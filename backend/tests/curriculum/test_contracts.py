"""DEV-007: authored fixture contracts; no learner data, database or inference."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
from rest_framework.exceptions import ValidationError
from modules.curriculum.contracts import validate_bundle, canonical, assessment_prompt

ROOT = Path(__file__).resolve().parents[3]
NOW = datetime(2026, 11, 17, tzinfo=timezone.utc)


@pytest.fixture
def bundle():
    return json.loads((ROOT / 'evals/fixtures/curriculum-v1.json').read_text())


def find(bundle, kind, id=None, version=1):
    return next(r for r in bundle['records'] if r['kind'] == kind and r['version'] == version and (id is None or r['id'] == id))


def test_authored_multi_subject_versions_and_private_overlay_validate(bundle):
    rows = validate_bundle(bundle, now=NOW)
    assert len(rows) == 52
    assert len([r for r in rows.values() if r['kind'] == 'profile']) == 3
    assert len([r for r in rows.values() if r['kind'] == 'edition']) == 7
    assert all(r['status'] == 'draft' for r in rows.values())
    assert all(r['specification_id'] is None for r in rows.values() if r['kind'] == 'edition')


def test_third_subject_is_data_configuration_without_core_changes(bundle):
    first_two = copy.deepcopy(bundle)
    first_two['records'] = [r for r in first_two['records'] if not r['id'].endswith('.science')]
    before = validate_bundle(first_two, now=NOW)
    after = validate_bundle(bundle, previous=before, now=NOW)
    assert len(after) > len(before)
    assert all(canonical(after[k]) == canonical(value) for k, value in before.items())


def test_existing_version_cannot_be_relabelled_or_overwritten(bundle):
    original = validate_bundle(bundle, now=NOW)
    changed = copy.deepcopy(bundle)
    find(changed, 'item')['prompt'] = 'Changed without a new version'
    with pytest.raises(ValidationError, match='immutable'):
        validate_bundle(changed, previous=original, now=NOW)
    assert find(bundle, 'edition', version=2)['supersedes']['version'] == 1


@pytest.mark.parametrize('mutation', [
    lambda b: find(b, 'profile').update(allowed_tools=['shell']),
    lambda b: find(b, 'profile').update(graders=['python.eval']),
    lambda b: find(b, 'profile').update(evidence_policy='model.mastery'),
    lambda b: find(b, 'profile').update(retrieval_policy='all.uploads'),
    lambda b: find(b, 'profile').update(safety_policy='off'),
    lambda b: find(b, 'profile').update(instruction_locales=['not a locale']),
    lambda b: find(b, 'profile').update(version=True),
    lambda b: find(b, 'profile').update(version='1'),
    lambda b: find(b, 'profile').update(id=123),
    lambda b: find(b, 'profile').update(kind=['profile']),
])
def test_malformed_or_authority_expanding_configuration_rejected(bundle, mutation):
    mutation(bundle)
    with pytest.raises(ValidationError):
        validate_bundle(bundle, now=NOW)


@pytest.mark.parametrize('change', [
    {'expires_at': '2025-01-01T00:00:00Z'},
    {'artifact_sha256': '0' * 64},
    {'permissions': {'process': False, 'display': True, 'derivatives': True, 'redistribute': False, 'train': False}},
    {'permissions': {'process': True, 'display': False, 'derivatives': True, 'redistribute': False, 'train': False}},
    {'status': 'withdrawn'},
])
def test_source_rights_expiry_hash_and_processing_are_not_ignored(bundle, change):
    find(bundle, 'rights').update(change)
    with pytest.raises(ValidationError):
        validate_bundle(bundle, now=NOW)


def test_material_hash_and_anchor_preserve_original_source(bundle):
    find(bundle, 'material')['content'] += 'Altered source'
    with pytest.raises(ValidationError, match='hash'):
        validate_bundle(bundle, now=NOW)


def test_no_implicit_latest_reference_or_wrong_edition_objective(bundle):
    find(bundle, 'item')['objectives'][0]['version'] = 2
    with pytest.raises(ValidationError, match='different edition'):
        validate_bundle(bundle, now=NOW)
    find(bundle, 'item')['objectives'][0]['version'] = 99
    with pytest.raises(ValidationError, match='exact version'):
        validate_bundle(bundle, now=NOW)


def test_source_anchor_must_exist_in_the_pinned_collection(bundle):
    find(bundle, 'item')['source']['anchor'] = 'invented-anchor'
    with pytest.raises(ValidationError, match='anchor'):
        validate_bundle(bundle, now=NOW)


def test_shared_collection_cannot_include_a_private_overlay(bundle):
    find(bundle, 'collection')['materials'].append({'id': 'material.language.private', 'version': 1})
    with pytest.raises(ValidationError, match='private audience'):
        validate_bundle(bundle, now=NOW)


def test_private_overlay_cannot_be_assigned_to_another_learner(bundle):
    record = find(bundle, 'collection', 'collection.language.private')
    record['audience']['learner_id'] = 'fixture.other-learner'
    with pytest.raises(ValidationError):
        validate_bundle(bundle, now=NOW)


def test_custom_material_cannot_claim_official_alignment_without_complete_key(bundle):
    find(bundle, 'edition')['specification_id'] = 'claimed.ministry'
    with pytest.raises(ValidationError, match='complete edition key'):
        validate_bundle(bundle, now=NOW)


def test_answer_keys_remain_separate_from_assessment_presentation(bundle):
    validate_bundle(bundle, now=NOW)
    for item in [r for r in bundle['records'] if r['kind'] == 'item']:
        prompt = assessment_prompt(item)
        assert set(prompt) == {'id', 'version', 'prompt', 'options', 'source'}
        assert 'rubric' not in prompt and 'config' not in prompt and 'accepted' not in prompt


def test_ambiguous_open_response_requires_human_review_configuration(bundle):
    rubric = find(bundle, 'rubric', 'rubric.language.private')
    assert rubric['grader_id'] == 'human-review.v1'
    rubric['config']['accepted'] = ['guessed answer']
    with pytest.raises(ValidationError, match='unsupported configuration'):
        validate_bundle(bundle, now=NOW)


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity'])
def test_numeric_grader_never_accepts_nonfinite_keys(bundle, value):
    rubric = find(bundle, 'rubric', 'rubric.quantitative')
    rubric['config']['expected'] = value
    with pytest.raises(ValidationError, match='finite'):
        validate_bundle(bundle, now=NOW)


def test_unsupported_grader_does_not_fall_back_to_model_certainty(bundle):
    find(bundle, 'rubric', 'rubric.quantitative')['grader_id'] = 'symbolic.unreviewed'
    with pytest.raises(ValidationError):
        validate_bundle(bundle, now=NOW)


def test_derivative_rights_required_for_reviewed_item(bundle):
    find(bundle, 'rights')['permissions']['derivatives'] = False
    with pytest.raises(ValidationError, match='derivation'):
        validate_bundle(bundle, now=NOW)


def test_duplicate_identity_or_source_is_rejected(bundle):
    bundle['records'].append(copy.deepcopy(bundle['records'][0]))
    with pytest.raises(ValidationError, match='Duplicate version'):
        validate_bundle(bundle, now=NOW)


def test_fixture_validator_cannot_be_used_as_real_content_publisher(bundle):
    bundle['fixture_only'] = False
    with pytest.raises(ValidationError, match='Only authored fixture'):
        validate_bundle(bundle, now=NOW)
