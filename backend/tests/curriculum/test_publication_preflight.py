"""AUTH-016 preflight tests using separately supplied authored fixture snapshots."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import traceback

import pytest
from django.utils import timezone as django_timezone

from modules.curriculum.contracts import validate_bundle
from modules.curriculum.publication_preflight import PreflightError, validate_publication_preflight

SUBJECTS = ('language', 'quantitative', 'science')
RELEASE_VERSION = 2
PRIVATE_MARKER = 'authored-private-diagnostic-marker'
NOW = datetime(2026, 11, 17, tzinfo=timezone.utc)


@pytest.fixture
def bundle():
    fixture = Path(__file__).resolve().parents[3] / 'evals' / 'fixtures' / 'curriculum-v1.json'
    return json.loads(fixture.read_text(encoding='utf-8'))


def find(snapshot, kind, record_id, version):
    return next(row for row in snapshot['records']
                if (row['kind'], row['id'], row['version']) == (kind, record_id, version))


def pin(record):
    payload = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return {
        'kind': record['kind'],
        'id': record['id'],
        'version': record['version'],
        'sha256': hashlib.sha256(payload).hexdigest(),
    }


def selected_pins(snapshot):
    # The release fixture selects version 2 and its profile v1. It retains
    # edition v1 and its dependencies only as historical validation context.
    return [
        pin(row) for row in snapshot['records']
        if row['kind'] == 'profile' or row['version'] == RELEASE_VERSION
    ]


@pytest.fixture
def release(bundle):
    records = deepcopy([row for row in bundle['records'] if row['audience']['type'] == 'shared_fixture'])
    inventory = {**bundle, 'records': records}
    for row in records:
        if row['kind'] == 'profile' or row['version'] == RELEASE_VERSION:
            row.update(status='approved', reviewer_ref='fixture.educator')
    assert len(validate_bundle(inventory, now=NOW)) == 45
    return deepcopy(inventory), {'schema_version': '1.0', 'records': selected_pins(inventory)}, inventory


def preflight(candidate, manifest, inventory, now=NOW):
    return validate_publication_preflight(candidate, manifest, inventory_bundle=inventory, now=now)


@pytest.mark.parametrize('omit_subject', [False, True])
def test_omission_from_both_candidate_artifacts_still_fails_trusted_coverage(release, omit_subject):
    candidate, manifest, inventory = release
    if omit_subject:
        candidate['records'] = [row for row in candidate['records'] if not row['id'].endswith('.science')]
    else:
        candidate['records'].remove(find(candidate, 'item', 'item.science', RELEASE_VERSION))
    manifest['records'] = [row for row in manifest['records'] if not row['id'].endswith('.science')]
    assert validate_bundle(candidate, now=NOW)
    assert selected_pins(inventory) != manifest['records']

    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)


def test_adding_a_self_consistent_but_unreviewed_item_fails_independent_coverage(release):
    candidate, manifest, inventory = release
    item = deepcopy(find(candidate, 'item', 'item.science', RELEASE_VERSION))
    item['id'] = 'item.science.extra'
    candidate['records'].append(item)
    manifest['records'].append(pin(item))
    assert validate_bundle(candidate, now=NOW)

    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)


def test_candidate_cannot_be_used_as_its_own_inventory(release):
    candidate, manifest, _ = release
    with pytest.raises(PreflightError):
        preflight(candidate, manifest, candidate)


@pytest.mark.parametrize('fault', ['empty', 'missing', 'duplicate', 'extra', 'stale', 'hash', 'bad-version'])
def test_manifest_requires_exact_versioned_pins(release, fault):
    candidate, manifest, inventory = release
    rows = manifest['records']
    if fault == 'empty':
        rows.clear()
    elif fault == 'missing':
        rows.pop()
    elif fault == 'duplicate':
        rows.append(deepcopy(rows[0]))
    elif fault == 'extra':
        rows.append(pin(find(inventory, 'rights', 'rights.language', 1)))
    elif fault == 'stale':
        current = next(index for index, row in enumerate(rows) if row['id'] == 'rubric.language')
        rows[current] = pin(find(inventory, 'rubric', 'rubric.language', 1))
    elif fault == 'hash':
        rows[0]['sha256'] = '0' * 64
    else:
        rows[0]['version'] = True  # bool == 1 must not pass exact version checks.

    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)


@pytest.mark.parametrize('changed', ['item', 'rubric', 'source-and-rights', 'draft-history'])
def test_self_consistent_candidate_cannot_overwrite_reviewed_versions(release, changed):
    candidate, manifest, inventory = release
    if changed == 'item':
        find(candidate, 'item', 'item.language', RELEASE_VERSION)['prompt'] = PRIVATE_MARKER
    elif changed == 'rubric':
        find(candidate, 'rubric', 'rubric.language', RELEASE_VERSION)['config']['accepted'] = [PRIVATE_MARKER]
    elif changed == 'draft-history':
        find(candidate, 'item', 'item.language', 1)['prompt'] = PRIVATE_MARKER
    else:
        source = find(candidate, 'material', 'material.language', RELEASE_VERSION)
        source['content'] = PRIVATE_MARKER
        source['sha256'] = hashlib.sha256(source['content'].encode('utf-8')).hexdigest()
        find(candidate, 'rights', 'rights.language', RELEASE_VERSION)['artifact_sha256'] = source['sha256']
    manifest['records'] = selected_pins(candidate)
    assert validate_bundle(candidate, now=NOW)

    with pytest.raises(PreflightError) as rejected:
        preflight(candidate, manifest, inventory)
    assert PRIVATE_MARKER not in ''.join(traceback.format_exception(rejected.value))


def test_source_bytes_must_match_claimed_hash_before_candidate_comparison(release):
    candidate, manifest, inventory = release
    find(candidate, 'material', 'material.language', RELEASE_VERSION)['content'] = PRIVATE_MARKER

    with pytest.raises(PreflightError) as rejected:
        preflight(candidate, manifest, inventory)
    assert PRIVATE_MARKER not in ''.join(traceback.format_exception(rejected.value))


def test_extra_manifest_pin_fields_are_rejected_without_exposing_values(release):
    candidate, manifest, inventory = release
    manifest['records'][0]['unexpected_value'] = PRIVATE_MARKER

    with pytest.raises(PreflightError) as rejected:
        preflight(candidate, manifest, inventory)
    assert PRIVATE_MARKER not in ''.join(traceback.format_exception(rejected.value))


def test_additional_collection_source_and_its_rights_must_be_pinned(release):
    _, manifest, inventory = release
    collection = find(inventory, 'collection', 'collection.language', RELEASE_VERSION)
    collection['materials'].append({'id': 'material.language', 'version': 1})
    additional_source = find(inventory, 'material', 'material.language', 1)
    additional_rights = find(inventory, 'rights', 'rights.language', 1)
    for row in (additional_source, additional_rights):
        row.update(status='approved', reviewer_ref='fixture.educator')
    candidate = deepcopy(inventory)
    manifest['records'] = selected_pins(inventory)

    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)
    manifest['records'].append(pin(additional_source))
    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)

    manifest['records'].append(pin(additional_rights))
    assert preflight(candidate, manifest, inventory).status == 'structure_valid_assessment_held'


def test_rights_expiration_at_decision_time_blocks_unchanged_inputs(release):
    candidate, manifest, inventory = release
    rights = find(inventory, 'rights', 'rights.language', RELEASE_VERSION)
    expiry = datetime.fromisoformat(rights['expires_at'])
    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory, now=expiry)


@pytest.mark.parametrize('ambient_zone', ['UTC', 'Africa/Cairo'])
def test_naive_rights_expiry_is_rejected_under_every_ambient_zone(release, ambient_zone):
    _, manifest, inventory = release
    rights = find(inventory, 'rights', 'rights.language', RELEASE_VERSION)
    rights['expires_at'] = '2026-11-24T12:00:00'
    manifest['records'] = selected_pins(inventory)
    now = datetime(2026, 11, 24, 11, tzinfo=timezone.utc)

    with django_timezone.override(ambient_zone), pytest.raises(PreflightError, match='^invalid_inventory$'):
        preflight(deepcopy(inventory), manifest, inventory, now=now)


@pytest.mark.parametrize('ambient_zone', ['UTC', 'Africa/Cairo'])
@pytest.mark.parametrize('expires_at', ['2026-11-24T10:15:00Z', '2026-11-24T12:15:00+02:00'])
def test_explicit_rights_expiry_uses_absolute_instant(release, ambient_zone, expires_at):
    _, manifest, inventory = release
    rights = find(inventory, 'rights', 'rights.language', RELEASE_VERSION)
    rights['expires_at'] = expires_at
    manifest['records'] = selected_pins(inventory)
    candidate = deepcopy(inventory)
    expiry = datetime(2026, 11, 24, 10, 15, tzinfo=timezone.utc)

    with django_timezone.override(ambient_zone):
        before = preflight(candidate, manifest, inventory, now=expiry - timedelta(seconds=1))
        assert before.status == 'structure_valid_assessment_held'
        with pytest.raises(PreflightError, match='^invalid_inventory$'):
            preflight(candidate, manifest, inventory, now=expiry)


@pytest.mark.parametrize('fault', [
    'draft-objective', 'withdrawn-source', 'wrong-permission', 'unknown-grader', 'single-option',
])
def test_matching_invalid_inputs_cannot_pass_by_agreement(release, fault):
    _, manifest, inventory = release
    if fault == 'draft-objective':
        find(inventory, 'objective', 'objective.language', RELEASE_VERSION).update(status='draft', reviewer_ref=None)
        assert validate_bundle(inventory, now=NOW)
    elif fault == 'withdrawn-source':
        find(inventory, 'material', 'material.language', RELEASE_VERSION)['status'] = 'withdrawn'
    elif fault == 'wrong-permission':
        find(inventory, 'rights', 'rights.language', RELEASE_VERSION)['permissions']['derivatives'] = False
    elif fault == 'unknown-grader':
        find(inventory, 'rubric', 'rubric.language', RELEASE_VERSION)['grader_id'] = 'unchecked.grader'
    else:
        item = find(inventory, 'item', 'item.science', RELEASE_VERSION)
        rubric = find(inventory, 'rubric', 'rubric.science', RELEASE_VERSION)
        item['options'] = [option for option in item['options'] if option['id'] == rubric['config']['correct_option']]
        assert len(item['options']) == 1
        assert validate_bundle(inventory, now=NOW)
    manifest['records'] = selected_pins(inventory)

    with pytest.raises(PreflightError):
        preflight(deepcopy(inventory), manifest, inventory)


def test_private_overlay_is_excluded_even_when_existing_fixture_schema_accepts_it(bundle, release):
    candidate, manifest, inventory = release
    candidate['records'].extend(row for row in bundle['records'] if row['audience']['type'] == 'learner_private')
    assert validate_bundle(candidate, now=NOW)

    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)


def test_fixture_only_flag_cannot_be_forged_with_truthy_nonboolean(release):
    candidate, manifest, inventory = release
    candidate['fixture_only'] = 1
    with pytest.raises(PreflightError):
        preflight(candidate, manifest, inventory)


def test_exact_three_subject_release_returns_holds_without_changing_input_or_exposing_payload(release):
    candidate, manifest, inventory = release
    original = deepcopy(release)
    candidate['records'].reverse()
    manifest['records'].reverse()
    original[0]['records'].reverse()
    original[1]['records'].reverse()

    result = preflight(candidate, manifest, inventory)

    assert result.status == 'structure_valid_assessment_held'
    assert isinstance(result.assessment_holds, tuple)
    assert set(asdict(result)) == {'status', 'assessment_holds'}
    assert {(hold.item_id, hold.item_version) for hold in result.assessment_holds} == {
        (f'item.{subject}', RELEASE_VERSION) for subject in SUBJECTS
    }
    assert all(hold.reasons == ('actual_grader_review_required', 'educator_review_required')
               for hold in result.assessment_holds)
    assert all(set(asdict(hold)) == {'item_id', 'item_version', 'reasons'} for hold in result.assessment_holds)
    with pytest.raises(FrozenInstanceError):
        result.status = 'approved'
    assert (candidate, manifest, inventory) == original


def test_human_review_mode_stays_held_without_inventing_an_automated_grade(release):
    _, manifest, inventory = release
    rubric = find(inventory, 'rubric', 'rubric.language', RELEASE_VERSION)
    rubric.update(grader_id='human-review.v1', config={'criteria': 'Review meaning', 'reason': 'Authored ambiguity'})
    manifest['records'] = selected_pins(inventory)

    result = preflight(deepcopy(inventory), manifest, inventory)

    assert next(hold for hold in result.assessment_holds if hold.item_id == 'item.language').reasons == (
        'human_review_only', 'educator_review_required',
    )
    assert result.status == 'structure_valid_assessment_held'
