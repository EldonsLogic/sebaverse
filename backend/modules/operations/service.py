"""Short locked transactions around mock dispatch, never across provider calls."""
from dataclasses import asdict
from datetime import timedelta
import re
from django.db import transaction, connection
from django.utils import timezone
from modules.access.service import authorized_resource
from modules.providers.contracts import Request, Receipt, ProviderFailure, validate_receipt
from modules.usage.models import Budget
from modules.identity.models import Learner
from .models import Job, Attempt, UsageReceipt
from .transitions import may_claim, may_finish, retry_delay


class Denied(ValueError): pass
class Conflict(ValueError): pass
class QuotaExceeded(ValueError): pass


def _locked(job_id):
    # Global lock order is budget then job, including replay, claim and cancellation.
    account_id=Job.objects.values_list('budget_id',flat=True).get(pk=job_id)
    budget=Budget.objects.select_for_update().get(pk=account_id)
    job=Job.objects.select_for_update().select_related('actor').get(pk=job_id)
    Learner.objects.select_for_update().get(pk=budget.learner_id)
    return budget,job


def _scope(resource):
    return {'learner':str(resource.learner_id),'course':str(resource.course_id),'purpose':resource.purpose,
            'edition':resource.edition_id,'version':resource.edition_version}


def _scope_live(job,budget):
    resource=authorized_resource(job.actor,job.resource_id)
    if resource is None or _scope(resource)!=job.scope or resource.learner_id!=budget.learner_id or resource.course_id!=budget.course_id or resource.purpose!=budget.purpose:
        return None
    return resource


def _release(budget,job):
    budget.reserved-=job.reserved_units
    job.reserved_units=0
    budget.save(update_fields=['reserved'])


@transaction.atomic
def enqueue(actor,resource_id,command_key,request):
    request.validate()
    if not isinstance(command_key,str) or not re.fullmatch(r'[a-zA-Z0-9._-]{1,96}',command_key):
        raise ValueError('Invalid command key')
    resource=authorized_resource(actor,resource_id)
    if resource is None:
        raise Denied('Current scope denied')
    budget=Budget.objects.select_for_update().get(learner=resource.learner,course=resource.course,purpose=resource.purpose)
    Learner.objects.select_for_update().get(pk=budget.learner_id)
    resource=authorized_resource(actor,resource_id)
    if resource is None or resource.learner_id!=budget.learner_id or resource.course_id!=budget.course_id or resource.purpose!=budget.purpose:
        raise Denied('Scope changed before reservation')
    digest=request.digest(resource_id)
    existing=Job.objects.filter(actor=actor,command_key=command_key).first()
    if existing:
        if existing.request_digest!=digest:
            raise Conflict('Command key reused with different body')
        return existing
    if budget.blocked or budget.limit-budget.spent-budget.reserved < request.reserve:
        raise QuotaExceeded('Hard synthetic quota')
    now=timezone.now()
    budget.reserved+=request.reserve
    budget.save(update_fields=['reserved'])
    return Job.objects.create(actor=actor,resource=resource,budget=budget,command_key=command_key,
        scope=_scope(resource),scope_generation=resource.learner.authorization_generation,request_digest=digest,request=asdict(request),reserved_units=request.reserve,due_at=now,
        deadline=now+timedelta(minutes=10))


@transaction.atomic
def claim(job_id,provider='mock-a'):
    if provider not in {'mock-a','mock-b'}:
        raise Denied('Unapproved provider')
    budget,job=_locked(job_id)
    now=timezone.now()
    if not may_claim(job.status,job.attempts,3,job.due_at<=now) or budget.blocked:
        raise Conflict('Job cannot be claimed')
    resource=_scope_live(job,budget)
    if job.cancelled or job.deadline<=now or resource is None or resource.learner.authorization_generation!=job.scope_generation:
        job.cancelled=True;job.status='cancelled';job.fence+=1
        _release(budget,job);job.save()
        return None
    job.status='running';job.fence+=1;job.attempts+=1;job.lease_until=now+timedelta(seconds=30)
    job.save()
    return Attempt.objects.create(job=job,fence=job.fence,provider=provider)


@transaction.atomic
def finish(attempt_id,receipt):
    reference=Attempt.objects.get(pk=attempt_id)
    budget,job=_locked(reference.job_id)
    attempt=Attempt.objects.select_for_update().get(pk=attempt_id)
    validate_receipt(receipt,Request(**job.request))
    # Enabled mocks echo the persisted dispatch nonce in their request ID.
    if receipt.request_id!='mock.'+str(attempt.id):
        raise Conflict('Receipt belongs to another dispatch')
    units=asdict(receipt)
    existing=UsageReceipt.objects.filter(attempt=attempt).first()
    if existing:
        if existing.units!=units:
            raise Conflict('Conflicting duplicate receipt')
        return job
    if attempt.state not in {'started','unknown'} or job.reserved_units < receipt.charge_units:
        raise Conflict('Attempt cannot settle')
    resource=_scope_live(job,budget)
    authorized=resource is not None and resource.learner.authorization_generation==job.scope_generation
    now=timezone.now()
    can_apply=may_finish(job.status,job.fence==attempt.fence,job.lease_until>now and job.deadline>now,authorized) and not job.cancelled
    UsageReceipt.objects.create(attempt=attempt,provider=attempt.provider,request_id=receipt.request_id,units=units)
    budget.reserved-=job.reserved_units;budget.spent+=receipt.charge_units
    job.reserved_units=0
    attempt.state='settled';attempt.receipt=units;attempt.save()
    # A late receipt reconciles usage but can never restore a cancelled/stale result.
    job.status='succeeded' if can_apply else 'cancelled'
    job.cancelled=not can_apply
    budget.save();job.save()
    return job


@transaction.atomic
def failed(attempt_id,error):
    reference=Attempt.objects.get(pk=attempt_id)
    budget,job=_locked(reference.job_id)
    attempt=Attempt.objects.select_for_update().get(pk=attempt_id)
    if attempt.state!='started':
        return job
    attempt.error_code=error.code
    if error.billing=='unknown':
        attempt.state='unknown'
        if job.status!='cancelled':job.status='unknown'
    else:
        attempt.state='not_billed'
        if job.status=='running' and job.fence==attempt.fence and not job.cancelled and error.safe_to_retry and job.attempts<3 and job.deadline>timezone.now():
            job.status='waiting_retry';job.due_at=timezone.now()+timedelta(seconds=retry_delay(job.attempts)+(int(job.id.hex[-1],16)%2))
        else:
            job.status='cancelled' if job.cancelled else 'failed'
            _release(budget,job)
    attempt.save();job.save()
    return job


@transaction.atomic
def recover_expired(job_id):
    budget,job=_locked(job_id)
    if job.status=='running' and job.lease_until<=timezone.now():
        # Dispatch may already have billed. Do not give a fresh worker free retries.
        job.status='unknown';job.fence+=1;job.save()
        Attempt.objects.filter(job=job,state='started').update(state='unknown')
    return job


def cancel(actor,job_id,adapter):
    if connection.in_atomic_block:
        raise Conflict('Cancellation dispatch requires a committed transaction boundary')
    with transaction.atomic():
        budget,job=_locked(job_id)
        if job.actor_id!=actor.pk or not actor.is_authenticated:
            raise Denied('Cannot cancel another actor work')
        if job.status in {'succeeded','failed','cancelled'}:
            return job
        running=Attempt.objects.filter(job=job,state__in=['started','unknown']).first()
        job.cancelled=True;job.status='cancelled';job.fence+=1
        if running is None:_release(budget,job)
        job.save()
    if running is not None:
        # Best effort only; cancellation acknowledgement does not prove zero billing.
        try:adapter.cancel(running.id)
        except Exception:pass
    return job


def run_once(job_id,adapter):
    if connection.in_atomic_block:
        raise Conflict('Provider dispatch requires a committed transaction boundary')
    attempt=claim(job_id,adapter.provider_id)
    if attempt is None:return Job.objects.get(pk=job_id)
    job=Job.objects.get(pk=job_id)
    try:
        receipt=adapter.generate(Request(**job.request),attempt.id)
        validate_receipt(receipt,Request(**job.request))
    except ProviderFailure as error:
        return failed(attempt.id,error)
    except Exception:
        return failed(attempt.id,ProviderFailure('invalid',False,'unknown'))
    return finish(attempt.id,receipt)


@transaction.atomic
def reconcile_not_billed(attempt_id,evidence_ref):
    """Internal mock reconciliation only, not a browser/provider probability assertion."""
    if not isinstance(evidence_ref,str) or not re.fullmatch(r'fixture\.receipt\.[a-z0-9._-]{1,64}',evidence_ref):
        raise ValueError('Reviewed mock evidence reference required')
    reference=Attempt.objects.get(pk=attempt_id)
    budget,job=_locked(reference.job_id)
    attempt=Attempt.objects.select_for_update().get(pk=attempt_id)
    if attempt.state=='not_billed' and attempt.receipt=={'evidence_ref':evidence_ref,'not_billed':True}:
        return job
    if attempt.state!='unknown':
        raise Conflict('Only unknown mock attempts can be reconciled')
    attempt.state='not_billed';attempt.receipt={'evidence_ref':evidence_ref,'not_billed':True};attempt.save()
    _release(budget,job)
    job.fence+=1;job.status='cancelled' if job.cancelled else 'failed';job.save()
    return job
