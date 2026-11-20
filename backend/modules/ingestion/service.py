"""Private lifecycle broker. Unavailable/unreviewed adapters never publish content."""
from dataclasses import dataclass
from datetime import datetime
import hashlib,json,re,uuid
from django.db import transaction
from django.utils import timezone
from modules.access.service import authorized_resource
from modules.identity.models import Learner,Membership
from .models import Upload,UploadQuota,ReviewGrant
from .contracts import declaration,detect_type,canonical,validate_result,MAX_OUTPUT


class Denied(ValueError):pass
class Conflict(ValueError):pass
class QuotaExceeded(ValueError):pass


def scope(resource):
    return {'learner':str(resource.learner_id),'course':str(resource.course_id),'edition':resource.edition_id,
            'version':resource.edition_version,'purpose':resource.purpose}


def locked(upload_id):
    quota_id=Upload.objects.values_list('quota_id',flat=True).get(pk=upload_id)
    quota=UploadQuota.objects.select_for_update().get(pk=quota_id)
    upload=Upload.objects.select_for_update().select_related('actor').get(pk=upload_id)
    Learner.objects.select_for_update().get(pk=quota.learner_id)
    return quota,upload


def live(upload):
    resource=authorized_resource(upload.actor,upload.resource_id)
    return resource if resource is not None and scope(resource)==upload.scope and resource.learner.authorization_generation==upload.authorization_generation else None


@transaction.atomic
def allocate(actor,resource_id,command_key,data):
    data=declaration(data)
    if not isinstance(command_key,str) or not re.fullmatch('[a-zA-Z0-9._-]{1,96}',command_key):raise ValueError('Invalid command key')
    resource=authorized_resource(actor,resource_id)
    if resource is None or resource.kind!='file' or resource.purpose!='tutoring':raise Denied('Upload scope denied')
    quota=UploadQuota.objects.select_for_update().get(learner=resource.learner,course=resource.course)
    Learner.objects.select_for_update().get(pk=quota.learner_id)
    resource=authorized_resource(actor,resource_id)
    if resource is None or resource.kind!='file' or resource.purpose!='tutoring' or resource.learner_id!=quota.learner_id or resource.course_id!=quota.course_id:raise Denied('Upload scope changed')
    digest=hashlib.sha256(canonical({'resource':str(resource_id),**data})).hexdigest()
    existing=Upload.objects.filter(actor=actor,command_key=command_key).first()
    if existing:
        if existing.request_digest!=digest:raise Conflict('Upload key body mismatch')
        return existing
    if quota.limit_bytes-quota.used_bytes-quota.reserved_bytes<data['byte_count']:raise QuotaExceeded('Upload quota exceeded')
    quota.reserved_bytes+=data['byte_count'];quota.save()
    return Upload.objects.create(actor=actor,resource=resource,quota=quota,command_key=command_key,
        request_digest=digest,scope=scope(resource),authorization_generation=resource.learner.authorization_generation,
        declared_bytes=data['byte_count'],held_bytes=data['byte_count'],media_type=data['media_type'],rights_claim=data['rights_claim'])


def accept_bytes(actor,upload_id,chunks,store):
    with transaction.atomic():
        quota,upload=locked(upload_id)
        if upload.actor_id!=actor.pk or not actor.is_authenticated or not actor.is_active or live(upload) is None:raise Denied('Upload actor denied')
        if upload.status!='awaiting_bytes':raise Conflict('Upload cannot receive bytes')
        upload.status='receiving';upload.writer_active=True;upload.save();generation=upload.generation
    def checked_chunks():
        for chunk in chunks:
            current=Upload.objects.values('status','generation').get(pk=upload_id)
            if current['status']!='receiving' or current['generation']!=generation:raise Conflict('Upload cancelled while receiving')
            yield chunk
    try:
        info=store.put(str(upload.id),checked_chunks(),upload.declared_bytes)
        detect_type(info['prefix'],upload.media_type)
    except Exception:
        # PrivateObjects.put closes its descriptor before raising. Persist that fact
        # before fallible deletion; quota stays held until purge succeeds.
        with transaction.atomic():
            quota,current=locked(upload_id)
            current.writer_active=False
            if current.status=='receiving':current.status='failed'
            current.failure_code='invalid_upload';current.save()
        store.purge(str(upload.id))
        with transaction.atomic():
            quota,current=locked(upload_id)
            if current.status in ['failed','withdrawn']:
                quota.reserved_bytes-=current.held_bytes;current.held_bytes=0;quota.save()
                current.status='deleted' if current.status=='withdrawn' else 'failed';current.save()
        raise
    stale=False
    with transaction.atomic():
        quota,current=locked(upload_id)
        current.writer_active=False
        if current.status!='receiving' or current.generation!=generation or live(current) is None:
            stale=True
            if current.status=='receiving':current.status='withdrawn';current.generation+=1
            current.save()
        else:
            quota.reserved_bytes-=current.held_bytes;quota.used_bytes+=info['byte_count'];quota.save()
            current.held_bytes=0;current.stored_bytes=info['byte_count'];current.source_sha256=info['sha256'];current.status='quarantined';current.save()
    if stale:
        store.purge(str(upload.id))
        with transaction.atomic():
            quota,current=locked(upload_id)
            quota.reserved_bytes-=current.held_bytes;current.held_bytes=0;current.status='deleted';quota.save();current.save()
        raise Conflict('Upload changed while streaming')
    return current


@dataclass(frozen=True)
class RuntimeAssets:
    """Server-owned reviewed registry; caller/model cannot choose assets or flags."""
    records: tuple=()

    def permits(self,kind,asset_id,source_hash):
        return any(row.get('kind')==kind and row.get('id')==asset_id and row.get('reviewed') is True
                   and row.get('scope')=='authored_fixture_only' and source_hash in row.get('source_hashes',[]) for row in self.records)


DEFAULT_ASSETS=RuntimeAssets()


def _continue_dispatch(upload, generation, dispatch):
    """Check current authority under the caller's upload and learner locks."""
    if upload.status != 'processing' or upload.generation != generation or upload.dispatch_id != dispatch:
        return False
    if live(upload) is not None:
        return True
    upload.status = 'withdrawn'
    upload.generation += 1
    upload.save()
    return False


def process(upload_id,store,scanner,parser,assets=DEFAULT_ASSETS):
    with transaction.atomic():
        quota,upload=locked(upload_id)
        if upload.status!='quarantined' or upload.attempts>=3 or live(upload) is None:raise Conflict('Upload cannot be processed')
        scanner_id = scanner.asset_id
        if not assets.permits('scanner',scanner_id,upload.source_sha256):
            upload.failure_code='scanner_unavailable';upload.save();return upload
        upload.status='processing';upload.attempts+=1;upload.dispatch_id=uuid.uuid4();upload.save()
        generation,dispatch=upload.generation,upload.dispatch_id
    try:
        data=store.read(str(upload.id))
        if hashlib.sha256(data).hexdigest()!=upload.source_sha256:raise ValueError('Original hash drift')
        scan=scanner.scan(data)
        if type(scan) is not dict or set(scan)!={'asset_id','sha256','status'} or scan['asset_id']!=scanner_id or scan['sha256']!=upload.source_sha256 or scan['status']!='clean':raise ValueError('Scan did not clear')
        parser_id = parser.asset_id
        if not assets.permits('parser',parser_id,upload.source_sha256):raise ValueError('Parser not reviewed/available')
        expected={'object_id':str(upload.id),'source_sha256':upload.source_sha256,'generation':generation,
                  'dispatch_id':str(dispatch),'parser_id':parser_id,'media_type':upload.media_type}
        with transaction.atomic():
            _, current = locked(upload_id)
            if not _continue_dispatch(current, generation, dispatch):
                return current
        # The parser receives a copy of the primitive fields, so it cannot
        # modify the broker binding used to validate its result.
        result=validate_result(parser.parse(data,dict(expected)),expected)
        output=canonical(result)
    except Exception:
        with transaction.atomic():
            quota,current=locked(upload_id)
            if _continue_dispatch(current, generation, dispatch):
                current.status='quarantined';current.failure_code='scan_or_parse_failed';current.save()
            return current
    with transaction.atomic():
        quota,current=locked(upload_id)
        if not _continue_dispatch(current, generation, dispatch):
            return current
        # Charge source + derived bytes under the same quota lock; no amplification bypass.
        output_bytes=len(output)
        if quota.limit_bytes-quota.used_bytes-quota.reserved_bytes<output_bytes:
            current.status='quarantined';current.failure_code='output_quota_exceeded';current.save();return current
        try:
            store.put_manifest(str(upload.id),output)
        except Exception:
            # A retained partial file stays charged and cannot be retried over blindly.
            retained=store.path(str(upload.id),'manifest').exists()
            if retained:
                current.manifest_bytes=output_bytes;quota.used_bytes+=output_bytes;quota.save()
            current.status='failed' if retained else 'quarantined'
            current.failure_code='manifest_write_failed';current.save();return current
        current.manifest_bytes=output_bytes;quota.used_bytes+=output_bytes;quota.save()
        current.scan_id=scanner_id;current.parser_id=parser_id;current.manifest_sha256=hashlib.sha256(output).hexdigest()
        current.status='needs_review';current.failure_code='';current.save();return current


def _review_grant(actor,quota):
    grant=ReviewGrant.objects.filter(actor=actor,learner_id=quota.learner_id,course_id=quota.course_id,
        active=True,rights=True,extraction=True).first()
    member=Membership.objects.filter(actor=actor,actor__is_active=True,tenant_id=quota.learner.tenant_id,active=True,role__in=['staff','teacher']).exists()
    if grant is None or not member:raise Denied('Explicit scoped review grant required')
    return grant


def review_manifest(actor,upload_id,store):
    upload=Upload.objects.select_related('actor','quota').get(pk=upload_id)
    if not actor.is_authenticated or not actor.is_active or live(upload) is None:raise Denied('Reviewer denied')
    _review_grant(actor,upload.quota)
    if upload.status!='needs_review':raise Conflict('Extraction is not awaiting review')
    data=store.read(str(upload.id),'manifest',MAX_OUTPUT)
    if hashlib.sha256(data).hexdigest()!=upload.manifest_sha256:raise ValueError('Manifest hash drift')
    return validate_result(json.loads(data),{'object_id':str(upload.id),'source_sha256':upload.source_sha256,
        'generation':upload.generation,'dispatch_id':str(upload.dispatch_id),'parser_id':upload.parser_id,'media_type':upload.media_type})


@transaction.atomic
def approve(actor,upload_id,generation,source_hash,rights_evidence,rights_expires):
    quota,upload=locked(upload_id)
    if not actor.is_authenticated or not actor.is_active or live(upload) is None:raise Denied('Reviewer denied')
    grant=_review_grant(actor,quota)
    if upload.status!='needs_review' or upload.generation!=generation or upload.source_sha256!=source_hash:raise Conflict('Review is stale')
    if not isinstance(rights_evidence,str) or not re.fullmatch('[a-zA-Z0-9._-]{1,96}',rights_evidence) or not isinstance(rights_expires,datetime) or timezone.is_naive(rights_expires) or rights_expires<=timezone.now():raise ValueError('Reviewed rights reference/expiry required')
    upload.rights_evidence=rights_evidence;upload.rights_expires=rights_expires
    upload.rights_reviewer=grant;upload.extraction_reviewer=grant;upload.status='private_ready';upload.save()
    return upload


def resolve(actor,upload_id,store):
    upload=Upload.objects.select_related('actor').get(pk=upload_id)
    resource=authorized_resource(actor,upload.resource_id)
    if resource is None or scope(resource)!=upload.scope or resource.learner.authorization_generation!=upload.authorization_generation or upload.status!='private_ready' or not upload.rights_evidence or upload.rights_expires is None or upload.rights_expires<=timezone.now():raise Denied('Private source unavailable')
    data=store.read(str(upload.id),'manifest',MAX_OUTPUT)
    if hashlib.sha256(data).hexdigest()!=upload.manifest_sha256:raise ValueError('Manifest hash drift')
    return validate_result(json.loads(data),{'object_id':str(upload.id),'source_sha256':upload.source_sha256,
        'generation':upload.generation,'dispatch_id':str(upload.dispatch_id),'parser_id':upload.parser_id,'media_type':upload.media_type})


def withdraw(actor,upload_id,store):
    with transaction.atomic():
        quota,upload=locked(upload_id)
        if not actor.is_authenticated or not actor.is_active or upload.actor_id!=actor.pk:raise Denied('Cannot withdraw another actor upload')
        if upload.status=='deleted':return upload
        old=upload.status
        if old!='withdrawn':upload.status='withdrawn';upload.generation+=1
        upload.save()
        if upload.writer_active:
            # The receiver owns/has the open descriptor. Retain quota until it closes and acknowledges purge.
            return upload
    # Access is denied before I/O. Failed purge retains charged bytes until retry.
    store.purge(str(upload.id))
    with transaction.atomic():
        quota,current=locked(upload_id)
        if current.status=='withdrawn':
            quota.used_bytes-=current.stored_bytes+current.manifest_bytes;quota.reserved_bytes-=current.held_bytes
            current.stored_bytes=0;current.manifest_bytes=0;current.held_bytes=0;current.status='deleted';quota.save();current.save()
        return current
