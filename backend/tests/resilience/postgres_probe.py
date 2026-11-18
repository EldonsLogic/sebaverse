"""Actual PostgreSQL crash/replay/quota/concurrent-claim fixtures, native-gated only."""
import json,os,sys
from pathlib import Path
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import connection,connections,transaction
from django.utils import timezone
from modules.identity.models import Tenant,Membership,Learner,GuardianRelationship,ConsentRecord
from modules.identity.consent import withdraw_consent
from modules.access.models import Course,Enrollment,Entitlement,ScopedResource
from modules.usage.models import Budget
from modules.operations.models import Job,Attempt,UsageReceipt
from modules.operations.service import enqueue,claim,finish,failed,run_once,cancel,recover_expired,reconcile_not_billed,Conflict,QuotaExceeded,Denied
from modules.providers.contracts import Request,ProviderFailure
from modules.providers.mock import MockProvider,AlternateMockProvider


def main():
    assert os.environ.get('SEBAVERSE_TEST_POSTGRES')=='1' and connection.vendor=='postgresql'
    assert not connection.in_atomic_block
    now=timezone.now();users=get_user_model()
    actor=users.objects.create_user(username='fixture-worker-learner')
    guardian=users.objects.create_user(username='fixture-worker-guardian')
    tenant=Tenant.objects.create()
    Membership.objects.create(tenant=tenant,actor=actor,role='learner')
    Membership.objects.create(tenant=tenant,actor=guardian,role='guardian')
    learner=Learner.objects.create(tenant=tenant,actor=actor)
    relation=GuardianRelationship.objects.create(guardian=guardian,learner=learner,verified_at=now-timedelta(hours=1),verification_ref='fixture.review')
    consent=ConsentRecord.objects.create(relationship=relation,purpose='tutoring',notice_version='fixture.v1',notice_locale='ar-EG',evidence_ref='fixture.consent',granted_at=now-timedelta(hours=1),expires_at=now+timedelta(hours=1))
    course=Course.objects.create(tenant=tenant,edition_id='fixture.jobs',edition_version=1)
    enrollment=Enrollment.objects.create(learner=learner,course=course)
    Entitlement.objects.create(enrollment=enrollment,purpose='tutoring',starts_at=now-timedelta(hours=1),expires_at=now+timedelta(hours=1),remaining_units=999)
    resource=ScopedResource.objects.create(learner=learner,course=course,kind='job',purpose='tutoring',edition_id=course.edition_id,edition_version=1)
    budget=Budget.objects.create(learner=learner,course=course,purpose='tutoring',limit=10000)
    checks=[];request=Request(max_input=20,max_output=20)
    def add(key):return enqueue(actor,resource.pk,key,request)
    def state(job):return Job.objects.get(pk=job.pk)
    def expect(error,callback):
        try:callback()
        except error:return
        raise AssertionError('Expected failure '+error.__name__)
    # Once-only reservation and body mismatch.
    j=add('duplicate');assert add('duplicate').pk==j.pk
    budget.refresh_from_db();assert budget.reserved==40
    expect(Conflict,lambda:enqueue(actor,resource.pk,'duplicate',Request(max_output=21)))
    checks.append('idempotent-reserve')
    run_once(j.pk,MockProvider());assert state(j).status=='succeeded'
    a=Attempt.objects.get(job=j);receipt=MockProvider().generate(request,a.pk)
    finish(a.pk,receipt);budget.refresh_from_db();assert budget.spent==20 and budget.reserved==0
    checks.append('receipt-replay')
    # A crash after vendor response leaves a durable reservation, never a free replay.
    j=add('crash');a=claim(j.pk);late=MockProvider().generate(request,a.pk)
    Job.objects.filter(pk=j.pk).update(lease_until=now-timedelta(seconds=1))
    assert recover_expired(j.pk).status=='unknown'
    expect(Conflict,lambda:claim(j.pk))
    assert finish(a.pk,late).status=='cancelled'
    checks.append('crash-late-receipt-fence')
    # Cancellation before and during dispatch; late result bills only once and cannot apply.
    j=add('cancel-queued');cancel(actor,j.pk,MockProvider());assert state(j).reserved_units==0
    j=add('cancel-running');a=claim(j.pk);cancel(actor,j.pk,MockProvider())
    assert state(j).reserved_units==40
    assert finish(a.pk,MockProvider().generate(request,a.pk)).status=='cancelled'
    checks.append('cancel-and-late-accounting')
    # Unknown provider billing is held until explicit mock evidence reconciles it.
    j=add('unknown');a=claim(j.pk);failed(a.pk,ProviderFailure('timeout',True,'unknown'))
    assert state(j).status=='unknown' and state(j).reserved_units==40
    expect(Conflict,lambda:claim(j.pk))
    reconcile_not_billed(a.pk,'fixture.receipt.zero');reconcile_not_billed(a.pk,'fixture.receipt.zero')
    assert state(j).reserved_units==0
    checks.append('unknown-billing-reconciliation')
    # Bounded not-billed retries, no transaction over dispatch.
    j=add('retries')
    for n in range(3):
        a=claim(j.pk);failed(a.pk,ProviderFailure('unavailable',True,'not_billed'))
        if n<2:
            expect(Conflict,lambda:claim(j.pk))
            Job.objects.filter(pk=j.pk).update(due_at=now-timedelta(seconds=1))
    assert state(j).status=='failed' and state(j).attempts==3 and state(j).reserved_units==0
    checks.append('bounded-retries')
    # Revocation after enqueue blocks dispatch; after dispatch it blocks completion.
    j=add('revoke-before');ConsentRecord.objects.filter(pk=consent.pk).update(withdrawn_at=now)
    assert claim(j.pk) is None and state(j).status=='cancelled'
    ConsentRecord.objects.filter(pk=consent.pk).update(withdrawn_at=None)
    j=add('revoke-after');a=claim(j.pk);ConsentRecord.objects.filter(pk=consent.pk).update(withdrawn_at=now)
    assert finish(a.pk,MockProvider().generate(request,a.pk)).status=='cancelled'
    ConsentRecord.objects.filter(pk=consent.pk).update(withdrawn_at=None)
    checks.append('live-revocation')
    j=add('deadline');a=claim(j.pk)
    Job.objects.filter(pk=j.pk).update(deadline=now-timedelta(seconds=1),lease_until=now+timedelta(minutes=1))
    assert finish(a.pk,MockProvider().generate(request,a.pk)).status=='cancelled'
    checks.append('deadline-overrides-lease')
    first=add('swap-first');second=add('swap-second');one=claim(first.pk);two=claim(second.pk)
    swapped=MockProvider().generate(request,two.pk)
    expect(Conflict,lambda:finish(one.pk,swapped))
    assert state(first).reserved_units==40 and not UsageReceipt.objects.filter(attempt=one).exists()
    assert finish(two.pk,swapped).status=='succeeded'
    cancel(actor,first.pk,MockProvider());finish(one.pk,MockProvider().generate(request,one.pk))
    checks.append('receipt-dispatch-correlation')
    # Revocation remains a fence even if a new consent later restores ordinary access.
    j=add('revoke-regrant');a=claim(j.pk)
    withdraw_consent(guardian,consent.pk);withdraw_consent(guardian,consent.pk)
    ConsentRecord.objects.create(relationship=relation,purpose='tutoring',notice_version='fixture.v2',
        notice_locale='ar-EG',evidence_ref='fixture.regrant',granted_at=now-timedelta(minutes=1),expires_at=now+timedelta(hours=1))
    assert finish(a.pk,MockProvider().generate(request,a.pk)).status=='cancelled'
    checks.append('revocation-generation-regrant')
    j=add('changed-edition');a=claim(j.pk)
    ScopedResource.objects.filter(pk=resource.pk).update(edition_version=2)
    Course.objects.filter(pk=course.pk).update(edition_version=2)
    assert finish(a.pk,MockProvider().generate(request,a.pk)).status=='cancelled'
    ScopedResource.objects.filter(pk=resource.pk).update(edition_version=1)
    Course.objects.filter(pk=course.pk).update(edition_version=1)
    checks.append('pinned-job-scope')
    # Two real database connections contend for the same budget.
    budget.refresh_from_db();budget.limit=budget.spent+60;budget.save()
    barrier=Barrier(2)
    def reserve_worker(key):
        try:
            barrier.wait(timeout=10)
            try:return str(enqueue(users.objects.get(pk=actor.pk),resource.pk,key,request).pk)
            except QuotaExceeded:return 'quota'
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(reserve_worker,['race-a','race-b']))
    assert results.count('quota')==1
    race=Job.objects.get(pk=next(v for v in results if v!='quota'))
    budget.refresh_from_db();assert budget.reserved==40 and budget.spent+budget.reserved<=budget.limit
    checks.append('atomic-quota-race')
    # Two workers may observe a queued ID but only one gets a lease/fence.
    barrier=Barrier(2)
    def claim_worker(_):
        try:
            barrier.wait(timeout=10)
            try:return str(claim(race.pk,provider='mock-b').pk)
            except Conflict:return 'conflict'
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(claim_worker,[0,1]))
    assert results.count('conflict')==1
    attempt=Attempt.objects.get(pk=next(v for v in results if v!='conflict'))
    assert finish(attempt.pk,AlternateMockProvider().generate(request,attempt.pk)).status=='succeeded'
    checks.append('single-lease-race')
    # An unauthorized actor cannot cancel another actor's work.
    expect(Denied,lambda:cancel(guardian,race.pk,MockProvider()))
    checks.append('cancel-ownership')
    assert not connection.in_atomic_block
    print(json.dumps({'checks':checks,'count':len(checks),'provider_calls':'mock-only','transactions_over_dispatch':False}))


if __name__=='__main__':main()
