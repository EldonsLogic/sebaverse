# Curriculum, uploads and RAG

Current architecture note (U11/U12, 11 November 2026): architecture/technical-baseline.md selects the subject-independent technical baseline. German is one retained initial use case, not a design dependency; technical selection does not certify content/benchmarks or authorize execution. Detailed learning thresholds/provider models remain subject to evaluation.

Sources: U1/U2; G04/G06/G08; A05/A09/A12. Proposed pipeline and gates below. RAG provides candidate evidence; citations do not prove an answer is correct.

## Identity and rights

CurriculumKey: country/system, authority or awarding body, qualification, syllabus/specification, academic year, grade, subject, term and language. Each edition is immutable with publication/effective dates, source authority, approval and supersession. Canonical concepts map many-to-many to versioned objectives with mapping confidence/reviewer; no automatic transfer of mastery certification between systems. American curricula require institution/course standards; IGCSE requires awarding body/specification; IB needs programme/subject/version.

RightsRecord: artifact hash, owner/source URL, acquisition date, license or permission document, allowed processing/display/derivatives/distribution/training, territory, audience, expiry, reviewer and restrictions. Public ministry download is not a commercial license. An uploader declaration is evidence of a claim, not automatic clearance. Built-in sources require explicit review before publication. Private uploads remain private; shared/public/training promotion requires separate authority. Copyright takedown suspends access and derived chunks while preserving minimal decision audit under an approved retention policy.

## Ingestion and version lifecycle

1. Authenticate and resolve uploader/child relationship, purpose, quota and rights declaration. Allocate random object ID, never a user-controlled storage path. Accept scoped types only; proposed PoC baseline PDF and images, DOCX later after parser threat review.
2. Stream ingress under byte/page limits; inspect type/signature; quarantine malware, active content and archives; bound CPU/RAM/time and disable unneeded egress. Parser has no production learner DB credentials.
3. Hash/deduplicate within permitted scope. Preserve immutable original and page images when rights permit. Scan for personal information; private materials cannot join public caches.
4. Parse layout/OCR with Arabic reading order, columns, tables, diagrams, formulas, numerals and language spans. Record parser/OCR/model version and page/bounding boxes. Low-quality notation triggers human review or cleaned source; no silent formula guessing.
5. Extract candidate hierarchy and objectives. Built-in: educator approves source/edition/objective mapping. Uploaded: label as private custom material, match to known objectives with confidence, allow user correction; unmapped topics stay custom, not falsely official.
6. Chunk by semantic section with page anchors and equation/table boundaries. Each chunk links source version, ACL, rights, objective mappings, extraction confidence and checksum. Preserve original plus normalized search text; Arabic normalization never overwrites original notation.
7. Compare lexical, dense and hybrid retrieval. Index only approved chunks; embeddings record provider/model/dimension/version. Re-embed into a new index before atomic switch; never mix spaces.
8. Review sampled extraction/mapping/retrieval; publish immutable manifest. UI states: uploaded, quarantined, processing, needs_review, ready, failed, superseded, withdrawn. User sees actionable failures and quota impact.

Edition changes require a diff of sources/objectives/items, approval and migration mapping. Active sessions stay pinned unless safety withdrawal forces an explicit restart. Old evidence retains its edition and is reinterpreted only through a reviewed migration. Revoked rights/consent invalidate cache/index access immediately; deleting the original alone is insufficient.

## Retrieval contract

Server derives scope from learner, guardian relationship, tenant, course grant, chosen curriculum edition and purpose. Apply ACL/edition/approval/rights filters before candidate ranking and again when resolving citations. Avoid postfilter-only designs that leak metadata. Query rewrite may propose search terms but cannot broaden authority. Rerank within allowed set; bounded top-k and context tokens. Conflicting/low-confidence/unanswerable evidence triggers clarification/abstention, not invented sources.

Answer citation contains exact source version/page/anchor/chunk. A citation resolver enforces current access without exposing signed permanent links. Generated statements are checked for source support and mathematical correctness; the orchestrator can request a reviewed tool. Documents are untrusted data and never grant tools, alter roles, reveal answer keys or direct external fetches. No arbitrary browsing/exec from uploaded instructions.

Cache keys include ACL scope, curriculum/item/source/index/prompt versions, language and query normalization. Shared cache only for authorized nonpersonal public/owned content; personal answers are isolated. Deletion/revocation invalidates derived caches and pending jobs. Source updates invalidate relevant response caches; stale content is not silently served.

## Evaluation protocol

PoC corpus: 20–30 authorized pages across digital/scanned Arabic, bilingual two-column text, tables/formulas/diagrams. Build 100 teacher-labeled questions with answerable, unanswerable, conflicting, wrong-edition and private-source cases; include 30 injection documents and two-tenant isolation fixtures. Annotate expected evidence page, objective, answerability and critical notation.

Proposed gates from A11: recall@5 >=90% on answerable items, supported factual claims >=90%, fabricated citations zero, appropriate abstention >=90%; report each language, corpus type and edition separately with counts and uncertainty. Zero unauthorized retrieval/citation access across all negative fixtures. Measure OCR critical-symbol fidelity, retrieval nDCG/MRR, latency and full parse/index/query costs. Small datasets give engineering confidence only; they do not prove all curricula work.

Unknowns: first content-rights route, source quality, OCR provider/model rights, exact page quotas, review workload and future curriculum authority integrations. Resolve at G1/G3 rather than invent licensed coverage.
