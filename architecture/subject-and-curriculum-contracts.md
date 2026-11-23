# Subject and curriculum extension contracts

Selected technical design v1 · U11/U12 · R017–R045, R075, R094, R099. Content and assessment approval remains distinct from software configuration.

## Domain separation

EducationSystem → CurriculumSpecification → CurriculumEditionVersion → CourseOffering → Enrollment. Subject is an independent taxonomy, not a deployment. Custom/private courses may leave official specification null; they must not claim ministry alignment. An AcademicPeriod is metadata, not a hard-coded Egyptian semester enum. ObjectiveVersion maps to ConceptVersion through reviewed MappingVersion; equivalence across courses or subjects is explicit, never inferred mastery transfer.

SubjectProfileVersion specifies instruction language options, target language when relevant, representation capabilities, permitted action templates, grader configurations, prerequisite conventions and retrieval normalization. Values are schema-validated IDs from a reviewed registry, not Python paths, uploaded plugins or executable prompt instructions. Policy limits and safety rules are global constraints a profile cannot weaken. Copying a profile creates a new version; active sessions pin the old one until an explicit migration or withdrawal.

## Profile fields

| Field | Meaning / constraint |
|---|---|
| id/version/status/reviewer | Immutable published profile; draft/approved/withdrawn lifecycle |
| subject taxonomy | Language, mathematics, science etc. are tags, not conditionals in core |
| instruction_locales/target_language | Egyptian Arabic/MSA/English explanation independent of curriculum language |
| representations | text, bilingual span, equation AST, table, image region, later interactive manipulative |
| graders | reviewed exact-set, typed numeric, structured choice, rubric proposal with adjudication; optional restricted symbolic/language adapter |
| teaching strategies | diagnostic, explain, worked example, guided step, independent practice, delayed retrieval |
| evidence policy version | Independent/assisted/exposed/ambiguous semantics; profile thresholds remain educator-reviewed hypotheses |
| retrieval configuration | lexical normalization/embedding/rerank settings; may not broaden ACL or combine incompatible embedding spaces |
| allowed tools | Registry identifiers authorized independently by runtime; no generic shell/browser/code executor |
| accessibility | alternative representation and speech/text controls; never an inferred disability classification |

## Adding content or a subject

1. Create or choose a reviewed subject profile and permitted grader types.
2. Register source ownership, processing/display/derivative rights and publication scope.
3. Upload or import source versions through quarantine; capture original layout/page anchors.
4. Review extraction, mark uncertain regions and accept explicit mappings or custom objectives.
5. Create reviewed item families, answer/rubric versions and prerequisite edges.
6. Run profile/content checks and the subject's grounding/grading evaluation slice.
7. Publish a versioned manifest and enable a course offering; enrollments and grants remain separate.

A new science course using text/choice/table items needs no core schema change. Chemistry notation, proof grading or pronunciation assessment may need specialist tooling/rubrics; unsupported capabilities stay unavailable, never silently fall back to generic LLM certainty. Instructor configuration may select allowed variants, but not set arbitrary executable rules.

## Shared and private ingestion

Both paths retain material hash, original/normalized text, page/bounding box, source/rights record, parser and index versions. Built-in content requires publisher/educator approval for its intended audience. Private uploaded material can become ready for its permitted learner only after rights/processing and extraction-quality checks; this is not public curricular approval. User corrections create derived revisions with lineage. Source text, notes, answer keys and review comments have distinct audience policies.

A course may combine several authorized sources via an immutable CollectionManifestVersion. Retrieval resolves its explicit sources plus live grants; a session cannot accidentally search every uploaded book. Replacing one document creates a new collection version. A session pins curriculum/profile/collection/item versions; revocation is checked live even when versions are pinned.

## Subject-independence acceptance

Use three small authored fixtures: a language unit, a quantitative unit and a factual-science unit, plus a private worksheet overlay. Run the same upload/session/attempt/report commands for each. Add the third course via configuration/content after two exist, without editing identity, billing, tutoring state machine, database schema or report code. An unsupported grader produces a clear blocked capability, not a fake result. Two learners studying two subjects never mix evidence, source access or entitlements. Shared concept transfer requires an approved mapping and original evidence remains linked to its source edition.

This verifies extension boundaries, not quality for every global syllabus. The initial German use case R095 is retained as one example, not a platform dependency.

External review follow-up, 23 November 2026: [traceable contract proposals](external-review-2026-11-23.md) retain spoken-input versioning, mechanical item validation, explicit language policy and mixed-speech evaluation alongside account/UI proposals. These are scoped proposals; existing execution gates and selected defaults are unchanged.
