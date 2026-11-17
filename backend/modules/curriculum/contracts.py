"""DEV-007: strict, subject-independent records and authored-bundle validation.

No database writes, grading, permission grants, plugins or model calls occur here.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from rest_framework import serializers as s


class Text(s.CharField):
    def __init__(self, **kwargs):
        super().__init__(trim_whitespace=False, max_length=kwargs.pop('max_length', 4000), **kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')
        return super().to_internal_value(data)


class Locale(Text):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', value):
            raise s.ValidationError('Invalid language tag.')
        return value


class Integer(s.IntegerField):
    def to_internal_value(self, data):
        if type(data) is not int:
            self.fail('invalid')
        return super().to_internal_value(data)


class Boolean(s.BooleanField):
    def to_internal_value(self, data):
        if type(data) is not bool:
            self.fail('invalid', input=data)
        return data


class Identifier(Text):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not re.fullmatch(r'[a-z][a-z0-9._-]{1,95}', value):
            raise s.ValidationError('Invalid stable identifier.')
        return value


def identifier(**kwargs):
    return Identifier(max_length=96, **kwargs)


class Strict(s.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise s.ValidationError('Expected an object.')
        unknown = set(data) - set(self.fields)
        if unknown:
            raise s.ValidationError({key: 'Unknown field.' for key in sorted(unknown, key=str)})
        return super().to_internal_value(data)


class Ref(Strict):
    id = identifier()
    version = Integer(min_value=1)


class Scope(Strict):
    type = s.ChoiceField(['shared_fixture', 'learner_private'])
    tenant_id = identifier(allow_null=True)
    learner_id = identifier(allow_null=True)

    def validate(self, value):
        private = value['type'] == 'learner_private'
        if any((value[key] is not None) != private for key in ('tenant_id', 'learner_id')):
            raise s.ValidationError('Private scope requires both IDs; shared scope cannot carry learner IDs.')
        return value


class Versioned(Strict):
    kind = Text(max_length=32)
    id = identifier()
    version = Integer(min_value=1)
    status = s.ChoiceField(['draft', 'approved', 'withdrawn'])
    reviewer_ref = identifier(allow_null=True)
    audience = Scope()

    def validate(self, value):
        if value['status'] == 'approved' and value['reviewer_ref'] is None:
            raise s.ValidationError('Approved metadata must retain a reviewer reference; it grants no authority.')
        return value


GRADERS = frozenset({'exact-set.v1', 'numeric.v1', 'choice.v1', 'human-review.v1'})
REPRESENTATIONS = ['text', 'bilingual-span', 'equation', 'table', 'image-region']
STRATEGIES = ['diagnose', 'explain', 'worked-example', 'guided-step', 'independent-practice', 'delayed-retrieval']


class Profile(Versioned):
    subject_tags = s.ListField(child=identifier(), min_length=1, max_length=12)
    instruction_locales = s.ListField(child=Locale(max_length=32), min_length=1, max_length=8)
    target_language = Locale(max_length=32, allow_null=True)
    representations = s.ListField(child=s.ChoiceField(REPRESENTATIONS), min_length=1, max_length=5)
    graders = s.ListField(child=s.ChoiceField(sorted(GRADERS)), min_length=1, max_length=4)
    strategies = s.ListField(child=s.ChoiceField(STRATEGIES), min_length=1, max_length=6)
    evidence_policy = s.ChoiceField(['evidence.proposed-v1'])
    retrieval_policy = s.ChoiceField(['retrieval.scoped-v1'])
    allowed_tools = s.ListField(child=s.ChoiceField(['none', 'numeric-check.v1']), min_length=1, max_length=2)


class CurriculumKey(Strict):
    country = Text(max_length=64, allow_null=True)
    system = Text(max_length=128, allow_null=True)
    authority = Text(max_length=128, allow_null=True)
    qualification = Text(max_length=128, allow_null=True)
    specification = Text(max_length=128, allow_null=True)
    academic_year = Text(max_length=32, allow_null=True)
    grade = Text(max_length=64, allow_null=True)
    subject = Text(max_length=128)
    term = Text(max_length=64, allow_null=True)
    language = Locale(max_length=32)


class Edition(Versioned):
    profile = Ref()
    collection = Ref()
    specification_id = identifier(allow_null=True)
    curriculum_key = CurriculumKey()
    supersedes = Ref(allow_null=True)

    def validate(self, value):
        value = super().validate(value)
        if value['specification_id'] is not None and any(v is None for v in value['curriculum_key'].values()):
            raise s.ValidationError('Official alignment requires a complete edition key; metadata is not content approval.')
        return value


class Permissions(Strict):
    process = Boolean()
    display = Boolean()
    derivatives = Boolean()
    redistribute = Boolean()
    train = Boolean()


class Rights(Versioned):
    source_ref = Text(max_length=512)
    owner_ref = identifier()
    artifact_sha256 = s.RegexField(r'\A[0-9a-f]{64}\Z')
    acquisition_date = s.DateField()
    permission_basis = Text(max_length=512)
    permissions = Permissions()
    expires_at = s.DateTimeField()
    territory = s.ListField(child=Text(max_length=64), min_length=1, max_length=20)
    restrictions = Text()


class Material(Versioned):
    rights = Ref()
    content = Text(max_length=20000)
    sha256 = s.RegexField(r'\A[0-9a-f]{64}\Z')
    media_type = s.ChoiceField(['text/plain'])
    anchors = s.ListField(child=identifier(), min_length=1, max_length=100)


class Collection(Versioned):
    materials = Ref(many=True, min_length=1, max_length=100)


class Source(Ref):
    anchor = identifier()


class Objective(Versioned):
    edition = Ref()
    description = Text()
    source = Source()


class Option(Strict):
    id = identifier()
    text = Text()


class Item(Versioned):
    edition = Ref()
    objectives = Ref(many=True, min_length=1, max_length=20)
    family_id = identifier()
    prompt = Text()
    options = Option(many=True, max_length=20)
    rubric = Ref()
    source = Source()


class Rubric(Versioned):
    grader_id = s.ChoiceField(sorted(GRADERS))
    visibility = s.ChoiceField(['assessment_only'])
    config = s.DictField()

    def validate(self, value):
        value = super().validate(value)
        config, grader = value['config'], value['grader_id']
        expected = {'exact-set.v1': {'accepted', 'case_sensitive'}, 'numeric.v1': {'expected', 'tolerance', 'unit'},
                    'choice.v1': {'correct_option'}, 'human-review.v1': {'criteria', 'reason'}}[grader]
        if set(config) != expected:
            raise s.ValidationError('Rubric has unsupported configuration fields.')
        if grader == 'exact-set.v1':
            if not isinstance(config['accepted'], list) or not 1 <= len(config['accepted']) <= 30 or any(not isinstance(x, str) or not x for x in config['accepted']) or type(config['case_sensitive']) is not bool:
                raise s.ValidationError('Exact-set rubric requires bounded nonempty text variants and a boolean.')
        elif grader == 'numeric.v1':
            try:
                if any(not isinstance(config[key], str) or len(config[key]) > 64 for key in ('expected', 'tolerance')):
                    raise ValueError()
                answer, tolerance = Decimal(config['expected']), Decimal(config['tolerance'])
                if not answer.is_finite() or not tolerance.is_finite() or tolerance < 0 or (config['unit'] is not None and not isinstance(config['unit'], str)):
                    raise ValueError()
            except (InvalidOperation, ValueError):
                raise s.ValidationError('Numeric rubric requires finite decimal strings and nonnegative tolerance.')
        elif grader == 'choice.v1':
            if not isinstance(config['correct_option'], str):
                raise s.ValidationError('Choice key must reference an option.')
        elif any(not isinstance(config[key], str) or not config[key] for key in expected):
            raise s.ValidationError('Human review requires criteria and a reason, never a guessed key.')
        return value


SERIALIZERS = {'profile': Profile, 'edition': Edition, 'rights': Rights, 'material': Material,
               'collection': Collection, 'objective': Objective, 'item': Item, 'rubric': Rubric}


class Bundle(Strict):
    schema_version = s.ChoiceField(['1.0'])
    fixture_only = Boolean()
    records = s.ListField(child=s.DictField(), min_length=1, max_length=500)


def canonical(record):
    """Stable content bytes; no hidden normalization of source text or notation."""
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def key(record):
    return record['kind'], record['id'], record['version']


def validate_bundle(data, previous=None, now=None):
    """Validate authored test data. This cannot publish content or authorize access."""
    envelope = Bundle(data=data)
    envelope.is_valid(raise_exception=True)
    if data['fixture_only'] is not True:
        raise s.ValidationError('Only authored fixture bundles are enabled in DEV-007.')
    rows = {}
    for record in data['records']:
        kind = record.get('kind')
        serializer = SERIALIZERS.get(kind) if isinstance(kind, str) else None
        if serializer is None:
            raise s.ValidationError('Unknown record kind; no executable adapters are accepted.')
        checked = serializer(data=record)
        checked.is_valid(raise_exception=True)
        identity = key(record)
        if identity in rows:
            raise s.ValidationError('Duplicate version identity.')
        if previous and identity in previous and canonical(record) != canonical(previous[identity]):
            raise s.ValidationError('Existing version is immutable; create a new version.')
        rows[identity] = record
    now = now or datetime.now(timezone.utc)

    def resolve(kind, ref, allow_withdrawn=False):
        identity = (kind, ref['id'], ref['version'])
        if identity not in rows:
            raise s.ValidationError('Missing exact version reference: ' + str(identity))
        if rows[identity]['status'] == 'withdrawn' and not allow_withdrawn:
            raise s.ValidationError('Referenced version is withdrawn; live access remains separate.')
        return rows[identity]

    def can_include(scope, other):
        return other['type'] == 'shared_fixture' or scope == other

    def material_scope(record, source):
        material = resolve('material', source)
        if source['anchor'] not in material['anchors'] or not can_include(record['audience'], material['audience']):
            raise s.ValidationError('Source anchor missing or source audience is incompatible.')
        edition = resolve('edition', record['edition'])
        collection = resolve('collection', edition['collection'])
        if source_key(source) not in {source_key(ref) for ref in collection['materials']}:
            raise s.ValidationError('Source is outside the pinned edition collection.')

    for record in rows.values():
        kind = record['kind']
        if kind == 'material':
            if hashlib.sha256(record['content'].encode('utf-8')).hexdigest() != record['sha256']:
                raise s.ValidationError('Original material hash mismatch.')
            if len(set(record['anchors'])) != len(record['anchors']):
                raise s.ValidationError('Duplicate material anchor.')
            rights = resolve('rights', record['rights'])
            expiry = s.DateTimeField().to_internal_value(rights['expires_at'])
            if rights['artifact_sha256'] != record['sha256'] or rights['audience'] != record['audience'] or expiry <= now or not all(rights['permissions'][p] for p in ('process', 'display')):
                raise s.ValidationError('Material rights expired, disallowed or have a different audience.')
        elif kind == 'collection':
            if len({source_key(ref) for ref in record['materials']}) != len(record['materials']):
                raise s.ValidationError('Duplicate collection source.')
            if any(not can_include(record['audience'], resolve('material', ref)['audience']) for ref in record['materials']):
                raise s.ValidationError('Collection would expose another private audience.')
        elif kind == 'edition':
            profile = resolve('profile', record['profile'])
            collection = resolve('collection', record['collection'])
            if not can_include(record['audience'], profile['audience']) or record['audience'] != collection['audience']:
                raise s.ValidationError('Edition profile/collection audience mismatch.')
            old = record['supersedes']
            if old is not None:
                resolve('edition', old, allow_withdrawn=True)
                if old['id'] != record['id'] or old['version'] >= record['version']:
                    raise s.ValidationError('Supersession must reference an earlier version of the same edition.')
        elif kind in ('objective', 'item'):
            edition = resolve('edition', record['edition'])
            if record['audience'] != edition['audience']:
                raise s.ValidationError('Learning record audience differs from its edition.')
            material_scope(record, record['source'])
            if kind == 'item':
                for ref in record['objectives']:
                    if resolve('objective', ref)['edition'] != record['edition']:
                        raise s.ValidationError('Item objective belongs to a different edition.')
                rubric = resolve('rubric', record['rubric'])
                profile = resolve('profile', edition['profile'])
                if rubric['audience'] != record['audience'] or rubric['grader_id'] not in profile['graders']:
                    raise s.ValidationError('Rubric audience/capability mismatch.')
                choices = [option['id'] for option in record['options']]
                if len(set(choices)) != len(choices) or (rubric['grader_id'] == 'choice.v1' and rubric['config']['correct_option'] not in choices):
                    raise s.ValidationError('Choice key is missing or options are duplicated.')
                if not resolve('rights', resolve('material', record['source'])['rights'])['permissions']['derivatives']:
                    raise s.ValidationError('Item derivation is not permitted by its source rights.')
    return rows


def source_key(ref):
    return ref['id'], ref['version']


def assessment_prompt(item):
    """Answer-free presentation DTO. Callers still need live server authorization."""
    return {field: item[field] for field in ('id', 'version', 'prompt', 'options', 'source')}
