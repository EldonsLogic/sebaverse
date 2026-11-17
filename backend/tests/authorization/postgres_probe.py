"""Actual isolated PostgreSQL probe, invoked only after the native CI pre-use gate.

Not collected as a DB-free pytest test. Every record is synthetic and rolled back.
"""
import json
import os
from pathlib import Path
import sys
from datetime import timedelta
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.test import Client
from django.utils import timezone
from modules.identity.models import Tenant, Membership, Learner, GuardianRelationship, ConsentRecord
from modules.access.models import Course, Enrollment, Entitlement, TeacherAssignment, ScopedResource
from modules.access.policy import KINDS


def main():
    assert os.environ.get('SEBAVERSE_TEST_POSTGRES') == '1'
    from django.db import connection
    assert connection.vendor == 'postgresql'
    now = timezone.now()
    users = get_user_model()
    counters = {'negative_scope_cases': 0, 'positive_cases': 0, 'revocation_cases': 0, 'constraint_cases': 0, 'actor_specific_negative_cases': 0}
    with transaction.atomic():
        actor = users.objects.create_user(username='fixture-learner')
        other = users.objects.create_user(username='fixture-other-learner')
        guardian = users.objects.create_user(username='fixture-guardian')
        unrelated = users.objects.create_user(username='fixture-other-guardian')
        teacher = users.objects.create_user(username='fixture-teacher')
        tenant, foreign = Tenant.objects.create(), Tenant.objects.create()
        for user, role in [(actor,'learner'),(other,'learner'),(guardian,'guardian'),(unrelated,'guardian'),(teacher,'teacher')]:
            Membership.objects.create(tenant=tenant, actor=user, role=role)
        learner = Learner.objects.create(tenant=tenant, actor=actor)
        Learner.objects.create(tenant=tenant, actor=other)
        relation = GuardianRelationship.objects.create(guardian=guardian, learner=learner,
            verified_at=now-timedelta(hours=1), verification_ref='fixture.verification')
        for purpose in ['tutoring', 'guardian_reporting', 'teacher_reporting']:
            ConsentRecord.objects.create(relationship=relation, purpose=purpose, notice_version='fixture.notice.v1',
                notice_locale='ar-EG', evidence_ref='fixture.consent', granted_at=now-timedelta(hours=1),
                expires_at=now+timedelta(hours=1))
        course = Course.objects.create(tenant=tenant, edition_id='fixture.edition', edition_version=1)
        other_course = Course.objects.create(tenant=tenant, edition_id='fixture.other-edition', edition_version=1)
        enrollment = Enrollment.objects.create(learner=learner, course=course)
        for purpose in ['tutoring','guardian_reporting','teacher_reporting']:
            Entitlement.objects.create(enrollment=enrollment, purpose=purpose, starts_at=now-timedelta(hours=1),
                expires_at=now+timedelta(hours=1), remaining_units=5)
        TeacherAssignment.objects.create(actor=teacher, learner=learner, course=course)
        for kind in sorted(KINDS):
            resource = ScopedResource.objects.create(learner=learner, course=course, kind=kind,
                purpose='tutoring', edition_id=course.edition_id, edition_version=1)
            path = '/api/v1/access/resources/'+str(resource.pk)+'/'
            def client(user=actor):
                c=Client(HTTP_HOST='localhost', enforce_csrf_checks=True)
                c.force_login(user)
                return c
            good=client().get(path)
            assert good.status_code == 200 and set(good.json()) == {'id','kind','edition_id','edition_version'}
            counters['positive_cases']+=1
            mutations = {
                'other_learner': lambda c: c.force_login(other),
                'other_tenant': lambda c: Course.objects.filter(pk=course.pk).update(tenant=foreign),
                'other_guardian': lambda c: c.force_login(unrelated),
                'revoked_membership': lambda c: Membership.objects.filter(actor=actor).update(active=False),
                'revoked_relationship': lambda c: GuardianRelationship.objects.filter(pk=relation.pk).update(revoked_at=now),
                'withdrawn_consent': lambda c: ConsentRecord.objects.filter(relationship=relation,purpose='tutoring').update(withdrawn_at=now),
                'expired_consent': lambda c: ConsentRecord.objects.filter(relationship=relation,purpose='tutoring').update(expires_at=now-timedelta(minutes=1)),
                'expired_entitlement': lambda c: Entitlement.objects.filter(enrollment=enrollment,purpose='tutoring').update(expires_at=now-timedelta(minutes=1)),
                'revoked_entitlement': lambda c: Entitlement.objects.filter(enrollment=enrollment,purpose='tutoring').update(revoked_at=now),
                'quota_exhausted': lambda c: Entitlement.objects.filter(enrollment=enrollment,purpose='tutoring').update(remaining_units=0),
                'wrong_course': lambda c: ScopedResource.objects.filter(pk=resource.pk).update(course=other_course),
                'wrong_version': lambda c: ScopedResource.objects.filter(pk=resource.pk).update(edition_version=2),
                'inactive_resource': lambda c: ScopedResource.objects.filter(pk=resource.pk).update(active=False),
                'expired_session': lambda c: expire(c),
                'inactive_actor': lambda c: users.objects.filter(pk=actor.pk).update(is_active=False),
            }
            for name, mutate in mutations.items():
                with transaction.atomic():
                    c=client();mutate(c)
                    response=c.get(path)
                    assert response.status_code in (401,404), (kind,name,response.status_code)
                    assert 'edition_id' not in response.json()
                    counters['negative_scope_cases']+=1
                    transaction.set_rollback(True)
            assert client().get('/api/v1/access/resources/'+str(uuid4())+'/').status_code == 404
            assert client().get(path+'?paid=true&role=guardian&consent=true').status_code == 400
            # Same authenticated session must lose access on the next call after withdrawal.
            with transaction.atomic():
                c=client();assert c.get(path).status_code==200
                ConsentRecord.objects.filter(relationship=relation,purpose='tutoring').update(withdrawn_at=now)
                assert c.get(path).status_code==404
                counters['revocation_cases']+=1
                transaction.set_rollback(True)
            for user,purpose in [(guardian,'guardian_reporting'),(teacher,'teacher_reporting')]:
                with transaction.atomic():
                    ScopedResource.objects.filter(pk=resource.pk).update(purpose=purpose)
                    assert client(user).get(path).status_code==200
                    counters['positive_cases']+=1
                    transaction.set_rollback(True)
        # Focused persisted guardian/teacher negatives verify live ORM filters, not just policy flags.
        report_resource = ScopedResource.objects.create(learner=learner, course=course, kind='material',
            purpose='guardian_reporting', edition_id=course.edition_id, edition_version=1)
        report_path='/api/v1/access/resources/'+str(report_resource.pk)+'/'
        second_relation=GuardianRelationship.objects.create(guardian=unrelated,learner=learner,
            verified_at=now-timedelta(hours=1),verification_ref='fixture.second-verification')
        ConsentRecord.objects.create(relationship=second_relation,purpose='guardian_reporting',
            notice_version='fixture.notice.v1',notice_locale='ar-EG',evidence_ref='fixture.second-consent',
            granted_at=now-timedelta(hours=1),expires_at=now+timedelta(hours=1))
        focused = [
            (guardian,'guardian_reporting',lambda: ConsentRecord.objects.filter(relationship=relation,purpose='guardian_reporting').update(withdrawn_at=now)),
            (teacher,'teacher_reporting',lambda: TeacherAssignment.objects.filter(actor=teacher).update(learner=Learner.objects.get(actor=other))),
            (teacher,'teacher_reporting',lambda: TeacherAssignment.objects.filter(actor=teacher).update(course=other_course)),
            (teacher,'teacher_reporting',lambda: TeacherAssignment.objects.filter(actor=teacher).update(active=False)),
            (guardian,'guardian_reporting',lambda: Membership.objects.filter(actor=guardian).update(active=False)),
            (guardian,'guardian_reporting',lambda: GuardianRelationship.objects.filter(pk=relation.pk).update(revoked_at=now)),
            (teacher,'teacher_reporting',lambda: ConsentRecord.objects.filter(relationship=relation,purpose='teacher_reporting').update(withdrawn_at=now)),
            (teacher,'teacher_reporting',lambda: Membership.objects.filter(actor=teacher).update(role='staff')),
        ]
        for user,purpose,mutate in focused:
            with transaction.atomic():
                ScopedResource.objects.filter(pk=report_resource.pk).update(purpose=purpose)
                c=client(user);assert c.get(report_path).status_code==200
                mutate()
                assert c.get(report_path).status_code==404
                counters['actor_specific_negative_cases']+=1
                transaction.set_rollback(True)
        # Failed writes prove actual database constraints, not only serializers.
        for write in [lambda: Membership.objects.create(tenant=tenant,actor=actor,role='learner'),
                      lambda: Course.objects.create(tenant=tenant,edition_id='fixture.bad',edition_version=0),
                      lambda: Membership.objects.create(tenant=foreign,actor=actor,role='model')]:
            try:
                with transaction.atomic(): write()
            except IntegrityError:
                counters['constraint_cases']+=1
            else:
                raise AssertionError('Expected database constraint rejection')
        transaction.set_rollback(True)
    assert counters == {'negative_scope_cases':120,'positive_cases':24,'revocation_cases':8,'constraint_cases':3,'actor_specific_negative_cases':8}
    print(json.dumps(counters))


def expire(client):
    session=client.session
    session.set_expiry(-1)
    session.save()


if __name__=='__main__':
    main()
