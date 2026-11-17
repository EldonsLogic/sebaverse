# Curriculum contracts v1

DEV-007 implements a subject-independent fixture boundary. `curriculum-v1.schema.json` is generated from the runtime serializers by `tools/export_curriculum_schema.py`; `make test-contracts` checks parity and semantic tests. There are no new dependencies.

Records have stable IDs and explicit integer versions. Profiles describe reviewed capabilities; editions pin profiles and collections; collections pin materials; objectives and assessment items pin an edition and source anchor. Rubrics remain separate assessment-only records. References never select an implicit latest version. Existing version payloads are immutable when a previous bundle is supplied. Supersession retains the older edition rather than relabelling its evidence.

Materials bind their UTF-8 content hash to a rights record with owner, provenance, permission scope and expiry. Shared fixture records cannot reference private content. Private collections can combine shared fixture content with the same synthetic learner's overlay. These structural checks do not establish live authorization: future services must derive access from current server-side relationships, consent and grants.

The JSON Schema describes structure. Runtime validation additionally checks cross-record references, anchored provenance, permissions, hashes, scopes, capability registries and grader-specific configuration. Neither format grants publishing authority. This implementation accepts only fixture bundles; status and reviewer fields are metadata, not an approval workflow.

`evals/fixtures/curriculum-v1.json` contains 52 authored draft records: language, quantitative and science profiles, two editions per subject, and one private overlay. These are synthetic test materials, not official curricula or evidence of learning quality. `assessment_prompt` excludes the rubric reference and answer key; callers still need authorization and assessment-state controls before delivery.

Requirements R035, R036, R041, R042, R043, R075, R094 and R099 are supported only to this task's contract scope. Official syllabus mapping, reviewed publication, migrations of learner evidence, actual tenant access, ingestion and the R043 educator-reviewed bank of 100 clear plus 20 ambiguous/adversarial cases remain future work. The small authored fixture set does not satisfy that bank or the F3 exit gate.
