"""AUTH-018: DB-free scoped retrieval and citation preflight (DEV-012 sub-slice)."""

from .preflight import (
    POLICY_VERSION,
    CitationRef,
    ResolvedCitation,
    RetrievalError,
    RetrievalHit,
    RetrievalResponse,
    RetrievalScope,
    build_cache_key,
    normalize_search_text,
    resolve_citation,
    retrieve_scoped,
)

__all__ = [
    'POLICY_VERSION',
    'CitationRef',
    'ResolvedCitation',
    'RetrievalError',
    'RetrievalHit',
    'RetrievalResponse',
    'RetrievalScope',
    'build_cache_key',
    'normalize_search_text',
    'resolve_citation',
    'retrieve_scoped',
]
