"""AUTH-018: pure DB-free scoped lexical retrieval and live citation resolver.

Enforces server-derived ACL, pinned edition/profile/collection/material approval,
and live rights filtering BEFORE candidate ranking, excludes assessment rubrics
and answer keys completely, preserves original source text verbatim, and
re-verifies live authority on citation resolve.
No database, pgvector, network, or model calls occur here.
"""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import re

from rest_framework.exceptions import ValidationError

from modules.access import policy
from modules.curriculum.contracts import Bundle, SERIALIZERS, key, source_key


POLICY_VERSION = 'retrieval.scoped-preflight-v1'
_MAX_QUERY_CHARS = 500
_MAX_TOP_K = 10
_MAX_CONTEXT_CHARS = 20_000
_IDENTIFIER = re.compile(r'[a-z][a-z0-9._-]{1,95}')
_DIGEST = re.compile(r'[0-9a-f]{64}')
_ARABIC_DIACRITICS = re.compile(r'[\u064b-\u065f\u0670\u0640]')
# Arabic letters only (excludes Arabic punctuation such as ، ؛ ؟) plus Latin/German letters and digits.
_TOKEN_RE = re.compile(r'[\u0621-\u063a\u0641-\u064a\u0671-\u06d3\u06fa-\u06ff]+|[a-zäöüß0-9]+')
_ARABIC_TRANS = str.maketrans({
    'أ': 'ا',
    'إ': 'ا',
    'آ': 'ا',
    'ٱ': 'ا',
    'ة': 'ه',
    'ى': 'ي',
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
})
_STOPWORDS = frozenset({
    # Arabic function words (normalized forms)
    'في', 'من', 'الي', 'علي', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك', 'هو', 'هي', 'او', 'ثم', 'لا', 'ما',
    # English / German function words
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'der', 'die', 'das', 'und', 'ein', 'eine', 'in', 'to', 'of', 'is', 'on',
})


class RetrievalError(ValueError):
    """Fail-closed retrieval error with fixed reason code and zero leaked data."""


@dataclass(frozen=True)
class RetrievalScope:
    """Server-derived authorization and curriculum scope; never raw client input."""
    tenant_id: str
    learner_id: str
    edition_id: str
    edition_version: int
    role: str
    purpose: str
    actor_active: bool
    member_active: bool
    tenant_matches: bool
    learner_active: bool
    relationship_valid: bool
    consent_valid: bool
    enrollment_valid: bool
    entitlement_valid: bool
    course_active: bool
    edition_active: bool

    def to_access_scope(self, *, resource_active: bool = True, version_matches: bool = True, kind: str = 'material') -> policy.Scope:
        return policy.Scope(
            actor_active=self.actor_active,
            member_active=self.member_active,
            role=self.role,
            tenant_matches=self.tenant_matches,
            learner_active=self.learner_active,
            relationship_valid=self.relationship_valid,
            consent_valid=self.consent_valid,
            enrollment_valid=self.enrollment_valid,
            entitlement_valid=self.entitlement_valid,
            course_active=self.course_active,
            edition_active=self.edition_active,
            resource_active=resource_active,
            version_matches=version_matches,
            purpose=self.purpose,
            kind=kind,
        )


@dataclass(frozen=True)
class CitationRef:
    material_id: str
    material_version: int
    anchor: str
    chunk_index: int
    chunk_sha256: str


@dataclass(frozen=True)
class RetrievalHit:
    citation: CitationRef
    original_text: str
    score: float
    audience_type: str
    untrusted_data: bool = field(default=True, init=False)


@dataclass(frozen=True)
class RetrievalResponse:
    status: str
    hits: tuple[RetrievalHit, ...]
    abstention_reason: str | None
    cache_key: str
    edition_id: str
    edition_version: int
    candidate_count: int
    policy_version: str = field(default=POLICY_VERSION, init=False)


@dataclass(frozen=True)
class ResolvedCitation:
    citation: CitationRef
    edition_id: str
    edition_version: int
    original_text: str
    audience_type: str
    untrusted_data: bool = field(default=True, init=False)


@dataclass(frozen=True)
class _Chunk:
    citation: CitationRef
    original_text: str
    tokens: tuple[str, ...]
    audience_type: str
    material_sha256: str


def normalize_search_text(text: str) -> str:
    """Normalize Arabic/Latin search text without mutating original source text."""
    if type(text) is not str:
        raise RetrievalError('invalid_query')
    stripped = _ARABIC_DIACRITICS.sub('', text)
    mapped = stripped.translate(_ARABIC_TRANS).lower()
    return ' '.join(mapped.split())


def _tokenize(text: str) -> tuple[str, ...]:
    normalized = normalize_search_text(text)
    tokens = []
    for tok in _TOKEN_RE.findall(normalized):
        if tok in _STOPWORDS:
            continue
        if len(tok) >= 2 or tok.isdigit():
            tokens.append(tok)
    return tuple(tokens)


def _validate_now(now: datetime) -> datetime:
    try:
        if type(now) is not datetime or now.utcoffset() is None:
            raise ValueError
        return now.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        raise RetrievalError('invalid_time') from None


def _validate_scope(scope: RetrievalScope, *, deny_code: str = 'access_denied') -> None:
    if not isinstance(scope, RetrievalScope):
        raise RetrievalError('invalid_scope')
    for value in (scope.tenant_id, scope.learner_id, scope.edition_id):
        if type(value) is not str or not _IDENTIFIER.fullmatch(value):
            raise RetrievalError('invalid_scope')
    if type(scope.edition_version) is not int or scope.edition_version < 1:
        raise RetrievalError('invalid_scope')
    if type(scope.role) is not str or type(scope.purpose) is not str:
        raise RetrievalError('invalid_scope')
    if not policy.allowed(scope.to_access_scope(kind='material')):
        raise RetrievalError(deny_code)


def _audience_allows(audience: dict, scope: RetrievalScope) -> bool:
    kind = audience.get('type')
    if kind == 'shared_fixture':
        return audience.get('tenant_id') is None and audience.get('learner_id') is None
    if kind == 'learner_private':
        return (
            audience.get('tenant_id') == scope.tenant_id
            and audience.get('learner_id') == scope.learner_id
        )
    return False


def _validate_record(record: dict, expected_kind: str) -> dict:
    if not isinstance(record, dict) or record.get('kind') != expected_kind:
        raise ValueError
    checked = SERIALIZERS[expected_kind](data=record)
    checked.is_valid(raise_exception=True)
    return record


def _index_bundle_records(bundle: dict) -> dict[tuple[str, str, int], dict]:
    """Validate bundle envelope and unique record identities without cross-tenant coupling."""
    envelope = Bundle(data=bundle)
    envelope.is_valid(raise_exception=True)
    if bundle['fixture_only'] is not True:
        raise ValueError
    rows: dict[tuple[str, str, int], dict] = {}
    for record in bundle['records']:
        if not isinstance(record, dict):
            raise ValueError
        kind = record.get('kind')
        rec_id = record.get('id')
        version = record.get('version')
        if (
            type(kind) is not str
            or kind not in SERIALIZERS
            or type(rec_id) is not str
            or type(version) is not int
            or version < 1
        ):
            raise ValueError
        identity = key(record)
        if identity in rows:
            raise ValueError
        rows[identity] = record
    return rows


def _chunk_material(material: dict) -> list[_Chunk]:
    """Deterministically chunk one approved material across its declared anchors."""
    anchors = material['anchors']
    content = material['content']
    material_id = material['id']
    material_version = material['version']
    audience_type = material['audience']['type']
    material_sha = material['sha256']

    if len(anchors) == 1:
        segments = [content]
    else:
        raw_parts = [part for part in content.split('\n\n') if part]
        if len(raw_parts) == len(anchors):
            segments = raw_parts
        else:
            segments = [content]

    chunks: list[_Chunk] = []
    for idx, segment in enumerate(segments):
        anchor = anchors[idx] if idx < len(anchors) else anchors[0]
        digest = sha256(segment.encode('utf-8')).hexdigest()
        citation = CitationRef(
            material_id=material_id,
            material_version=material_version,
            anchor=anchor,
            chunk_index=idx,
            chunk_sha256=digest,
        )
        chunks.append(
            _Chunk(
                citation=citation,
                original_text=segment,
                tokens=_tokenize(segment),
                audience_type=audience_type,
                material_sha256=material_sha,
            )
        )
    return chunks


def _authorized_chunks(
    bundle: dict,
    scope: RetrievalScope,
    *,
    now: datetime,
    deny_code: str = 'access_denied',
) -> tuple[list[_Chunk], dict]:
    """Pre-filter strictly to the pinned edition's approved, live-rights materials."""
    try:
        rows = _index_bundle_records(bundle)
    except (ValidationError, ValueError, KeyError, TypeError, AttributeError):
        raise RetrievalError(deny_code if deny_code == 'citation_denied' else 'invalid_bundle') from None

    raw_edition = rows.get(('edition', scope.edition_id, scope.edition_version))
    if raw_edition is None:
        raise RetrievalError(deny_code)
    try:
        edition = _validate_record(raw_edition, 'edition')
    except (ValidationError, ValueError, KeyError, TypeError):
        raise RetrievalError(deny_code if deny_code == 'citation_denied' else 'invalid_bundle') from None
    if edition['status'] != 'approved' or not _audience_allows(edition['audience'], scope):
        raise RetrievalError(deny_code)

    raw_profile = rows.get(('profile', *source_key(edition['profile'])))
    if raw_profile is None:
        raise RetrievalError(deny_code)
    try:
        profile = _validate_record(raw_profile, 'profile')
    except (ValidationError, ValueError, KeyError, TypeError):
        raise RetrievalError(deny_code if deny_code == 'citation_denied' else 'invalid_bundle') from None
    if (
        profile['status'] != 'approved'
        or not _audience_allows(profile['audience'], scope)
        or (profile['audience']['type'] != 'shared_fixture' and profile['audience'] != edition['audience'])
    ):
        raise RetrievalError(deny_code)

    raw_collection = rows.get(('collection', *source_key(edition['collection'])))
    if raw_collection is None:
        raise RetrievalError(deny_code)
    try:
        collection = _validate_record(raw_collection, 'collection')
    except (ValidationError, ValueError, KeyError, TypeError):
        raise RetrievalError(deny_code if deny_code == 'citation_denied' else 'invalid_bundle') from None
    if (
        collection['status'] != 'approved'
        or collection['audience'] != edition['audience']
        or not _audience_allows(collection['audience'], scope)
    ):
        raise RetrievalError(deny_code)

    seen_materials: set[tuple[str, int]] = set()
    chunks: list[_Chunk] = []
    for mat_ref in collection['materials']:
        mat_key = source_key(mat_ref)
        if mat_key in seen_materials:
            continue
        seen_materials.add(mat_key)
        raw_material = rows.get(('material', *mat_key))
        if raw_material is None:
            continue
        try:
            material = _validate_record(raw_material, 'material')
        except (ValidationError, ValueError, KeyError, TypeError):
            continue
        if material['status'] != 'approved':
            continue
        if not _audience_allows(material['audience'], scope):
            continue
        if (
            material['audience']['type'] != 'shared_fixture'
            and material['audience'] != collection['audience']
        ):
            continue
        if len(set(material['anchors'])) != len(material['anchors']):
            continue
        if sha256(material['content'].encode('utf-8')).hexdigest() != material['sha256']:
            continue

        raw_rights = rows.get(('rights', *source_key(material['rights'])))
        if raw_rights is None:
            continue
        try:
            rights = _validate_record(raw_rights, 'rights')
            exp_raw = rights['expires_at']
            if type(exp_raw) is not str:
                continue
            exp_dt = datetime.fromisoformat(exp_raw)
            if exp_dt.utcoffset() is None:
                continue
            expiry = exp_dt.astimezone(timezone.utc)
        except (ValidationError, ValueError, KeyError, TypeError, OverflowError):
            continue
        if (
            rights['status'] != 'approved'
            or expiry <= now
            or not rights['permissions']['process']
            or not rights['permissions']['display']
            or rights['artifact_sha256'] != material['sha256']
            or rights['audience'] != material['audience']
        ):
            continue
        chunks.extend(_chunk_material(material))

    return chunks, edition


def _build_cache_key(
    *,
    scope: RetrievalScope,
    edition: dict,
    authorized_chunks: list[_Chunk],
    query: str,
    top_k: int,
    max_context_chars: int,
) -> str:
    """Build an ACL- and version-scoped cache key; private scopes never share keys."""
    has_private = (
        edition['audience']['type'] == 'learner_private'
        or any(chunk.audience_type == 'learner_private' for chunk in authorized_chunks)
    )
    acl_partition = (
        f'learner_private:{scope.tenant_id}:{scope.learner_id}'
        if has_private
        else 'shared_fixture'
    )
    material_pins = sorted({
        (c.citation.material_id, c.citation.material_version, c.material_sha256)
        for c in authorized_chunks
    })
    payload = {
        'policy_version': POLICY_VERSION,
        'acl_partition': acl_partition,
        'role': scope.role,
        'purpose': scope.purpose,
        'edition_id': scope.edition_id,
        'edition_version': scope.edition_version,
        'language': edition['curriculum_key']['language'],
        'material_pins': material_pins,
        'normalized_query': normalize_search_text(query),
        'top_k': top_k,
        'max_context_chars': max_context_chars,
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return sha256(encoded).hexdigest()


def _bm25_scores(query_tokens: tuple[str, ...], chunks: list[_Chunk]) -> list[float]:
    """Compute deterministic BM25 strictly over the already-authorized chunk pool."""
    n_docs = len(chunks)
    if n_docs == 0 or not query_tokens:
        return [0.0] * n_docs

    k1 = 1.2
    b = 0.75
    doc_counters = [Counter(chunk.tokens) for chunk in chunks]
    doc_lens = [len(chunk.tokens) for chunk in chunks]
    avg_len = sum(doc_lens) / n_docs if n_docs else 1.0
    if avg_len <= 0:
        avg_len = 1.0

    unique_q = tuple(dict.fromkeys(query_tokens))
    df = {
        term: sum(1 for counter in doc_counters if counter.get(term, 0) > 0)
        for term in unique_q
    }

    scores: list[float] = []
    for counter, doc_len in zip(doc_counters, doc_lens):
        score = 0.0
        for term in unique_q:
            tf = counter.get(term, 0)
            if tf == 0:
                continue
            idf = math.log(1.0 + (n_docs - df[term] + 0.5) / (df[term] + 0.5))
            denom = tf + k1 * (1.0 - b + b * (doc_len / avg_len))
            score += idf * ((tf * (k1 + 1.0)) / denom)
        scores.append(round(score, 6))
    return scores


def retrieve_scoped(
    bundle: dict,
    scope: RetrievalScope,
    query: str,
    *,
    now: datetime,
    top_k: int = 5,
    max_context_chars: int = 4000,
) -> RetrievalResponse:
    """Retrieve bounded, ACL-filtered lexical evidence with exact citation refs."""
    now_utc = _validate_now(now)
    _validate_scope(scope, deny_code='access_denied')
    if type(query) is not str or not query.strip() or len(query) > _MAX_QUERY_CHARS:
        raise RetrievalError('invalid_query')
    if type(top_k) is not int or not 1 <= top_k <= _MAX_TOP_K:
        raise RetrievalError('invalid_query')
    if type(max_context_chars) is not int or not 1 <= max_context_chars <= _MAX_CONTEXT_CHARS:
        raise RetrievalError('invalid_query')

    authorized, edition = _authorized_chunks(bundle, scope, now=now_utc, deny_code='access_denied')
    cache_key = _build_cache_key(
        scope=scope,
        edition=edition,
        authorized_chunks=authorized,
        query=query,
        top_k=top_k,
        max_context_chars=max_context_chars,
    )

    query_tokens = _tokenize(query)
    if not query_tokens or not authorized:
        return RetrievalResponse(
            status='abstain',
            hits=(),
            abstention_reason='no_authorized_evidence',
            cache_key=cache_key,
            edition_id=scope.edition_id,
            edition_version=scope.edition_version,
            candidate_count=len(authorized),
        )

    scores = _bm25_scores(query_tokens, authorized)
    ranked = sorted(
        (
            (score, chunk)
            for score, chunk in zip(scores, authorized)
            if score > 0.0
        ),
        key=lambda pair: (
            -pair[0],
            pair[1].citation.material_id,
            pair[1].citation.material_version,
            pair[1].citation.anchor,
            pair[1].citation.chunk_index,
        ),
    )

    hits: list[RetrievalHit] = []
    used_chars = 0
    for score, chunk in ranked:
        if len(hits) >= top_k:
            break
        chunk_len = len(chunk.original_text)
        if used_chars + chunk_len > max_context_chars:
            continue
        hits.append(
            RetrievalHit(
                citation=chunk.citation,
                original_text=chunk.original_text,
                score=score,
                audience_type=chunk.audience_type,
            )
        )
        used_chars += chunk_len

    if not hits:
        reason = 'context_budget_exceeded' if ranked else 'no_authorized_evidence'
        return RetrievalResponse(
            status='abstain',
            hits=(),
            abstention_reason=reason,
            cache_key=cache_key,
            edition_id=scope.edition_id,
            edition_version=scope.edition_version,
            candidate_count=len(authorized),
        )

    return RetrievalResponse(
        status='grounded',
        hits=tuple(hits),
        abstention_reason=None,
        cache_key=cache_key,
        edition_id=scope.edition_id,
        edition_version=scope.edition_version,
        candidate_count=len(authorized),
    )


def resolve_citation(
    bundle: dict,
    scope: RetrievalScope,
    citation: CitationRef,
    *,
    now: datetime,
) -> ResolvedCitation:
    """Re-verify live server scope, approval, rights, and exact chunk hash."""
    now_utc = _validate_now(now)
    _validate_scope(scope, deny_code='citation_denied')
    if (
        not isinstance(citation, CitationRef)
        or type(citation.material_id) is not str
        or not _IDENTIFIER.fullmatch(citation.material_id)
        or type(citation.material_version) is not int
        or citation.material_version < 1
        or type(citation.anchor) is not str
        or not _IDENTIFIER.fullmatch(citation.anchor)
        or type(citation.chunk_index) is not int
        or citation.chunk_index < 0
        or type(citation.chunk_sha256) is not str
        or not _DIGEST.fullmatch(citation.chunk_sha256)
    ):
        raise RetrievalError('invalid_citation')

    authorized, _ = _authorized_chunks(bundle, scope, now=now_utc, deny_code='citation_denied')
    for chunk in authorized:
        if chunk.citation == citation:
            return ResolvedCitation(
                citation=chunk.citation,
                edition_id=scope.edition_id,
                edition_version=scope.edition_version,
                original_text=chunk.original_text,
                audience_type=chunk.audience_type,
            )
    raise RetrievalError('citation_not_found')
