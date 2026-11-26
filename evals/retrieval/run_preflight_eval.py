"""AUTH-018: synthetic-fixture retrieval & citation preflight evaluation harness.

Engineering check only over authored synthetic fixtures; does NOT measure real
curricula, OCR fidelity, pgvector/hybrid ranking, or student learning efficacy.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))

from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(USE_TZ=True, REST_FRAMEWORK={})

from modules.retrieval.preflight import (  # noqa: E402
    CitationRef,
    RetrievalError,
    RetrievalScope,
    resolve_citation,
    retrieve_scoped,
)

NOW = datetime(2026, 11, 26, tzinfo=timezone.utc)


def _approved_fixture_bundle() -> dict:
    bundle = json.loads((ROOT / 'evals/fixtures/curriculum-v1.json').read_text(encoding='utf-8'))
    for record in bundle['records']:
        record['status'] = 'approved'
        record['reviewer_ref'] = 'reviewer.synthetic-eval'
    return bundle


def _scope(
    *,
    edition_id: str,
    edition_version: int = 1,
    tenant_id: str = 'fixture.tenant-a',
    learner_id: str = 'fixture.learner-a',
    consent_valid: bool = True,
) -> RetrievalScope:
    return RetrievalScope(
        tenant_id=tenant_id,
        learner_id=learner_id,
        edition_id=edition_id,
        edition_version=edition_version,
        role='learner',
        purpose='tutoring',
        actor_active=True,
        member_active=True,
        tenant_matches=True,
        learner_active=True,
        relationship_valid=True,
        consent_valid=consent_valid,
        enrollment_valid=True,
        entitlement_valid=True,
        course_active=True,
        edition_active=True,
    )


def run_eval() -> dict:
    bundle = _approved_fixture_bundle()

    answerable_cases = [
        ('language:v1', 'de', 'edition.language', 1, 'الفعل الموضع الثاني Deutsch', 'material.language'),
        ('language:v2', 'de', 'edition.language', 2, 'إصدار اختبار ثان Deutsch', 'material.language'),
        ('quantitative:v1', 'ar', 'edition.quantitative', 1, 'تساوي الطرفين نطرح بالتعويض', 'material.quantitative'),
        ('science:v1', 'ar', 'edition.science', 1, 'انصهار الثلج؟ الحالة الصلبة السائلة', 'material.science'),
        ('language.private:v1', 'de', 'edition.language.private', 1, 'تتعلمه ورقة اختبار خاصة', 'material.language.private'),
    ]

    unanswerable_cases = [
        ('language:v1', 'de', 'edition.language', 1, 'انصهار الثلج الحالة الصلبة'),
        ('quantitative:v1', 'ar', 'edition.quantitative', 1, 'خوارزمية التشفير الكمومي'),
        ('science:v1', 'ar', 'edition.science', 1, 'Heute lerne ich Deutsch'),
    ]

    by_bucket: dict[str, dict[str, int]] = {}
    answerable_hits = 0
    abstention_hits = 0
    fabricated_citations = 0
    unauthorized_access = 0

    for subject, lang, edition_id, version, query, expected_material in answerable_cases:
        key_name = f'{subject}:{lang}'
        by_bucket.setdefault(key_name, {'answerable': 0, 'recall_at_5': 0, 'unanswerable': 0, 'abstained': 0})
        by_bucket[key_name]['answerable'] += 1

        scope = _scope(edition_id=edition_id, edition_version=version)
        res = retrieve_scoped(bundle, scope, query, now=NOW, top_k=5)
        matched_ids = [h.citation.material_id for h in res.hits]
        if res.status == 'grounded' and expected_material in matched_ids:
            answerable_hits += 1
            by_bucket[key_name]['recall_at_5'] += 1
        for hit in res.hits:
            try:
                resolve_citation(bundle, scope, hit.citation, now=NOW)
            except RetrievalError:
                fabricated_citations += 1

    for subject, lang, edition_id, version, query in unanswerable_cases:
        key_name = f'{subject}:{lang}'
        by_bucket.setdefault(key_name, {'answerable': 0, 'recall_at_5': 0, 'unanswerable': 0, 'abstained': 0})
        by_bucket[key_name]['unanswerable'] += 1

        scope = _scope(edition_id=edition_id, edition_version=version)
        res = retrieve_scoped(bundle, scope, query, now=NOW, top_k=5)
        if res.status == 'abstain' and res.hits == ():
            abstention_hits += 1
            by_bucket[key_name]['abstained'] += 1

    # Negative security checks: cross-learner, cross-tenant, revoked consent, fabricated citation
    negative_scopes = [
        _scope(edition_id='edition.language.private', learner_id='fixture.learner-b'),
        _scope(edition_id='edition.language.private', tenant_id='fixture.tenant-b'),
        _scope(edition_id='edition.language', consent_valid=False),
    ]
    for neg_scope in negative_scopes:
        try:
            retrieve_scoped(bundle, neg_scope, 'ورقة اختبار خاصة', now=NOW)
            unauthorized_access += 1
        except RetrievalError:
            pass

    fake_citation = CitationRef(
        material_id='material.language',
        material_version=1,
        anchor='invented-anchor',
        chunk_index=0,
        chunk_sha256='0' * 64,
    )
    try:
        resolve_citation(bundle, _scope(edition_id='edition.language'), fake_citation, now=NOW)
        fabricated_citations += 1
    except RetrievalError:
        pass

    # Answer-key exclusion check (querying rubric key text directly)
    rubric_res = retrieve_scoped(bundle, _scope(edition_id='edition.science'), 'physical correct_option', now=NOW)
    if rubric_res.hits:
        unauthorized_access += 1

    # Post-retrieval withdrawal check
    valid_scope = _scope(edition_id='edition.language')
    valid_res = retrieve_scoped(bundle, valid_scope, 'Deutsch', now=NOW)
    withdrawn_bundle = copy.deepcopy(bundle)
    for r in withdrawn_bundle['records']:
        if r['kind'] == 'material' and r['id'] == 'material.language' and r['version'] == 1:
            r['status'] = 'withdrawn'
    try:
        resolve_citation(withdrawn_bundle, valid_scope, valid_res.hits[0].citation, now=NOW)
        unauthorized_access += 1
    except RetrievalError:
        pass

    recall_at_5 = round(answerable_hits / len(answerable_cases), 4)
    abstention_accuracy = round(abstention_hits / len(unanswerable_cases), 4)

    return {
        'scope': 'AUTH-018 synthetic-fixture preflight only',
        'recall_at_5': recall_at_5,
        'abstention_accuracy': abstention_accuracy,
        'fabricated_citations': fabricated_citations,
        'unauthorized_access': unauthorized_access,
        'by_subject_language': by_bucket,
        'pass': (
            recall_at_5 >= 0.90
            and abstention_accuracy >= 0.90
            and fabricated_citations == 0
            and unauthorized_access == 0
        ),
        'note': 'Synthetic-fixture engineering check only; not a real-curriculum or learning-efficacy claim.',
    }


if __name__ == '__main__':
    report = run_eval()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report['pass'] else 1)
