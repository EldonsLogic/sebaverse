"""Export structural JSON Schema from the reviewed DRF contract fields."""
from pathlib import Path
import argparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from rest_framework import serializers as s
from django.core.validators import RegexValidator
from modules.curriculum.contracts import SERIALIZERS, Bundle, Identifier, Locale


def field_schema(field):
    if isinstance(field, s.ListSerializer):
        result = {'type': 'array', 'items': field_schema(field.child)}
    elif isinstance(field, s.Serializer):
        result = {'type': 'object', 'additionalProperties': False,
                  'properties': {name: field_schema(child) for name, child in field.fields.items()},
                  'required': [name for name, child in field.fields.items() if child.required]}
    elif isinstance(field, s.ListField):
        result = {'type': 'array', 'items': field_schema(field.child)}
    elif isinstance(field, s.ChoiceField):
        result = {'enum': list(field.choices)}
    elif isinstance(field, s.BooleanField):
        result = {'type': 'boolean'}
    elif isinstance(field, s.IntegerField):
        result = {'type': 'integer'}
        for attribute, name in [('min_value', 'minimum'), ('max_value', 'maximum')]:
            value = getattr(field, attribute, None)
            if value is not None:
                result[name] = value
    elif isinstance(field, s.DateTimeField):
        result = {'type': 'string', 'format': 'date-time'}
    elif isinstance(field, s.DateField):
        result = {'type': 'string', 'format': 'date'}
    elif isinstance(field, s.DictField):
        result = {'type': 'object'}
    elif isinstance(field, s.CharField):
        result = {'type': 'string', 'minLength': 0 if field.allow_blank else 1}
        if isinstance(field, Identifier):
            result['pattern'] = '^[a-z][a-z0-9._-]{1,95}$'
        elif isinstance(field, Locale):
            result['pattern'] = '^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$'
        else:
            for validator in field.validators:
                if isinstance(validator, RegexValidator):
                    result['pattern'] = validator.regex.pattern.replace(r'\A', '^').replace(r'\Z', '$')
    else:
        raise TypeError('Unsupported export field: ' + type(field).__name__)
    array = result.get('type') == 'array'
    for attribute, name in [('min_length', 'minItems' if array else 'minLength'),
                            ('max_length', 'maxItems' if array else 'maxLength')]:
        value = getattr(field, attribute, None)
        if value is not None:
            result[name] = value
    if field.allow_null:
        result = {'anyOf': [result, {'type': 'null'}]}
    return result


def build_schema():
    definitions = {}
    for kind, serializer in SERIALIZERS.items():
        value = field_schema(serializer())
        value['properties']['kind'] = {'const': kind}
        definitions[kind] = value
    schema = field_schema(Bundle())
    schema.update({'$schema': 'https://json-schema.org/draft/2020-12/schema',
                   '$id': 'urn:sebaverse:contracts:curriculum:1.0',
                   'title': 'Authored curriculum fixture bundle v1', '$defs': definitions,
                   '$comment': 'Structural export only. Python validation also enforces registry-dependent rubric config, exact reference graph, rights, scope and immutability. Neither validation grants publication/access authority.'})
    schema['properties']['fixture_only'] = {'const': True}
    schema['properties']['records']['items'] = {'oneOf': [{'$ref': '#/$defs/' + kind} for kind in SERIALIZERS]}
    return schema


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / 'contracts/curriculum-v1.schema.json'
    expected = json.dumps(build_schema(), indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if not target.exists() or target.read_text() != expected:
            raise SystemExit('Contract schema differs from current serializers; regenerate it.')
        print('Curriculum structural schema matches its runtime serializers.')
    else:
        target.write_text(expected)
        print('Wrote contracts/curriculum-v1.schema.json')


if __name__ == '__main__':
    main()
