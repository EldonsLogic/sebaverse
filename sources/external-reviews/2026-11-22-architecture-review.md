Architecture review · 22 November 2026

# Sebaverse, read against a working prototype

Two repositories, the same product, opposite ends of the problem. One has a skeleton and a conscience; the other has organs. Neither has heard a child speak.

**Reviewed** github.com/EldonsLogic/sebaverse @ `89ce415` **Against** the voice-tutor prototype

## 01 What each side actually is

|  | Sebaverse | Prototype |
| --- | --- | --- |
| Nature | Architecture, governance, foundation | Running vertical slice |
| Backend | Django/DRF, 8 modules, \~2,720 lines | FastAPI + Pipecat, \~1,900 lines |
| Frontend | 91-line shell, 4 routes, no state | Bilingual app, full flow |
| Tests | 618 backend | 480 |
| Documentation | 340 Markdown files, 104 requirements, 12 ADRs | 1 README |
| Provider calls | Mock only | Real cascade wired, never run |
| Tutoring runtime | **None** | Works on paper; never spoken aloud |
| Content | None | 26 lessons, 8 subjects, 2 languages |
| Accounts | Guardian/consent records, no child auth | Parent password, child PIN, lockout, reset |
| Deployment | None | None |

Strongest in Sebaverse

The ingestion, consent and purge work — 968 lines, lease fencing, scope generations. Genuinely hard, genuinely done, and the prototype has nothing like it.

Strongest in the prototype

The teaching loop exists, and it surfaced bugs no design review would have found. Those are the substance of this document.

## 02 The structural observation

104 requirements, 7 phases, 12 ADRs, 618 tests, and zero turns of tutoring.

The phase plan puts the grounded tutor at A3 and voice at A4; the current checkpoint is F3. Everything upstream is being hardened against a teaching loop whose shape is still a hypothesis.

This is a risk, not a style preference. Writing one lesson and grading one spoken answer produced four findings in an afternoon that the design documents do not anticipate. Each changes a contract currently treated as settled: transcript normalisation changes what `RubricVersion` must contain; the answer-leak failure changes what item review must mechanically check; the language-switching policy decides whether mixed-language synthesis sits on the critical path at all; and the code-switching result changes the segmenter and the voice ADR.

Recommendation

Pull a throwaway A3-lite slice ahead of completing F3: one subject, one authored lesson, one child, mic → transcript → bounded tutor → TTS → one graded attempt. Hardcode everything, then throw it away. The purpose is not to build the product. It is to falsify four contracts before they are hardened. In the prototype this took about a day.

## 03 Findings the design does not cover

### 3aTranscript normalisation is a versioned contract

The learning-intelligence doc specifies grading via reviewed rubric versions, deterministic exact-set and typed numeric. That is correct for typed input and insufficient for speech.

A spoken Egyptian Arabic answer arrives with diacritics, five alef forms, ta marbuta against ha, Arabic-Indic against Latin digits, filler words — and English words transliterated into Arabic script. A child answers an English maths question with “fifty”; a transcriber listening for `ar-EG` may return فيفتي. She is right. Mark her wrong once and she stops trusting the thing.

**Suggestion.** Add `TranscriptNormalizationVersion` alongside `RubricVersion`, referenced by `Attempt`. It must be versioned, because changing normalisation silently changes historical grades — exactly what the evidence ledger exists to prevent, and what the current model would not catch.

### 3bItem review needs a machine, not only an educator

Four of the prototype's check questions contained their own answers. A child who repeated the question back would have scored full marks. Two were Arabic substring collisions, essentially invisible to a reader:

- a question containing نصين whose answer was نص
- a question containing أربع whose answer was ربع

R043 is a human-review requirement. Human review does not catch these reliably. A test does, in milliseconds.

**Suggestion.** Add a mechanical validation stage that blocks publication, asserting that the item's own expected answer passes its own grader; that every acceptable answer does too; that an obvious non-answer fails; that the question text itself does *not* pass, with a per-item opt-out for comprehension items that legitimately contain their answer; and that the item's language matches its subject's instruction language.

### 3cLanguage-switching policy belongs on the subject profile

`SubjectProfileVersion` already carries instruction locales and target language — the right home. But the voice doc says language preference per activity, with switching mid-session.

The prototype started there and it was wrong. In an English-medium Egyptian school, maths is taught in English and the child answers in Arabic constantly. Following her ends the English lesson, muddies the progress data, and — decisively — makes every utterance a potential code-switch, putting the one unproven piece of the voice stack on the critical path for every subject instead of one.

**Suggestion.** Make it explicit and selectable per profile: `fixed`, `follow_learner`, `fixed_with_arabic_fallback`. Default to `fixed` — the only one that keeps every synthesized utterance single-language.

### 3dIntra-utterance code-switching is a distinct gate

The voice doc handles economics, cascade against realtime, WER and CER, critical-entity fidelity and barge-in carefully. It does not isolate the question that actually blocks the German opening scope:

Can the synthesiser speak a German word inside an Arabic sentence, or must the utterance be split into one call per language span?

These are different architectures. One streams; the other buffers the whole reply, emits a settings change and a speak call per span, and concatenates. The prototype handles both behind one contract — the model emits `[de]…[/de]`, a segmenter resolves it, one config value picks the mode — specifically so the answer could be deferred. It still has to be answered, and nobody has listened yet.

The one with a date on it

Promote this from an A4 comparative experiment to an A1 artifact. Four sentences, synthesized both ways, listened to by one person. It costs cents, and it determines the segmenter design, the subject profile's language policy, and whether German is viable as the opening scope at all. Deferring it means hardening A2 and A3 around an unknown.

### 3eChild authentication is missing from identity

The identity module has consent policy, guardian relationships and authorization generations — strong work on who may *authorize*. There is no design for how a seven-year-old gets in.

The prototype's answer held up: the parent signs in with email and password; the child never does. She taps her face and enters four digits. Three details are easy to miss.

- **Four digits is ten thousand guesses.** It needs its own lockout, counted per child rather than per session, so a new tab does not reset it.
- **Hash the PIN.** It is short, it is still a credential, and it is very often the family's phone lock.
- **Normalise Arabic-Indic digits.** The keypad shows ١٢٣٤; a laptop types 1234. Without folding, a child is locked out of her own account by the device she picked up.

### 3fA lightweight track sits above the curriculum chain

EducationSystem → CurriculumSpecification → CurriculumEditionVersion → CourseOffering → Enrollment is more correct than anything in the prototype and should stay. But rendering a subject grid should not require the full chain.

The prototype uses one `track` field on the child — her school type — mapped in a data file to a subject list. That is the entire mechanism, and it is what lets one platform serve a German school and a national-languages school with no branching anywhere.

| Track | Subjects |
| --- | --- |
| `nat-lang` | Arabic, Maths, Science, Social Studies, Religion, English |
| `german` | Arabic, Maths, Science, History, Religion, German |

**Suggestion.** Add a thin `TrackProfile` as a presentation and defaults layer: which school she attends, therefore which subjects she sees. Not a replacement for `CourseOffering` — the thing the UI reads, so A2 can show a working subject grid before A5 has real enrollments.

### 3gExtract the UI string table now, at 91 lines

`App.tsx` has Arabic strings inline and the shell is Arabic-only RTL. Most subjects are to be taught in English, so the interface will need both, with direction flipping. In the prototype that meant one string table with a column per language, `data-t` attributes on static markup, and a re-render on switch. At 91 lines it is an hour. At A5 it is a rewrite, done badly under pressure.

Two details worth copying. The interface language and the teaching language are independent — maths is English whichever way the buttons read, and conflating them is a tempting, costly mistake. And the PIN keypad stays left-to-right in both directions, because every phone dialler a child has used is laid out that way, Arabic ones included.

### 3hState the “browser never says who it is” invariant

The API contracts cover idempotency, stale workers, cancellation and billing uncertainty. One invariant deserves those words, because it is the one that fails quietly under pressure:

Every request touching a family's data resolves the parent from the session and the child from that same session. A `child_id` in a URL is only ever used to *ask about* a child, and is immediately resolved through a parent-scoped lookup. There is no lookup by id alone anywhere in the stack.

In the prototype this is one helper and five tests that put two families side by side and try to cross between them. The expensive failure in a multi-family product is never a crash; it is one family quietly reading another's data. The corollary for voice: the endpoint that spends money and listens to a child takes the child from the session and validates the requested subject against her track. The browser may name a lesson, never a learner.

## 04 What runs the other way

Stated plainly, because the comparison is not one-directional and most of these are real gaps in the prototype.

| Sebaverse has | Prototype has | Why it matters |
| --- | --- | --- |
| Evidence ledger with correction lineage, replayable projections | Attempts appended, no lineage | A regraded item cannot retroactively fix history |
| Usage reservation, call attempts, receipts; atomic reserve before dispatch | **No cost control at all** | A child could talk for an hour; nothing stops it |
| Rights records on every material | None | Fine for family use; illegal at pilot scale |
| Consent records, guardian verification, revocation cancelling queued work | A PIN and nothing else | Under-13 data handling is a legal gate |
| Item families, exposure rules, independent-family counts | Linear lessons, identical on repeat | “Mastery” is two correct answers to the same question |
| Retention policy for audio and transcripts | Flagged, not designed | Becomes legal the moment a family that is not yours signs up |
| Release manifests pinning sessions to versions | Lessons reloaded from disk mid-session | An edit mid-lesson changes the lesson under the child |

The usage-receipt design is the one to port in the other direction first. The prototype has no spend ceiling, and that is the difference between a family project and a product.

## 05 Proposed register entries

Framed as register entries, since that is the repository's working unit. None appear covered by R001–R104 as written, though several sit close to an existing requirement.

| ID | Title | Nearest | Phase |
| --- | --- | --- | --- |
| R105 | Versioned transcript normalisation for spoken answers | R020, R043 | A2 / A3 |
| R106 | Mechanical item self-validation before publication | R043 | A3 |
| R107 | Per-subject language-switching policy, `fixed` default | R013–R017 | A2 |
| R108 | Intra-utterance code-switching synthesis gate | R016 | **A1** |
| R109 | Child PIN credential: lockout, hashing, digit normalisation | R053 | A2 |
| R110 | Track profile — school type to subject presentation | R036 | A2 |
| R111 | Bilingual interface with direction switching | R054 | A2 |
| R112 | Content tests parametrised over the live content folder | R032, R043 | A3 |

R108 is the only one with urgency. Everything else can wait for its phase.

## 06 Where the two would merge

The prototype is not a candidate to become the product. Django/DRF with PostgreSQL and the modular monolith is the right call under ADR-001, and FastAPI with SQLite is not a serious alternative at pilot scale. The prototype's value is as evidence and as a source of contracts.

1. **Keep** the architecture, data model, phase gates and governance unchanged.
2. **Port four contracts** into A2 before F3 completes: transcript normalisation, item self-validation, the language-switching field, child PIN credentials.
3. **Run R108** within two weeks as an A1 artifact under the existing spend cap. The prototype's probe script does exactly this and lifts as-is; it is provider-specific, the method is not.
4. **Run the A3-lite throwaway slice**, scoped to falsifying those contracts, explicitly not to producing product code.
5. **Use the 26 lessons as authored fixtures** for A3. They already span language, quantitative and factual-science content in two instruction languages — precisely what A3's exit criterion asks for. Right shape for fixtures, wrong shape for a pilot, which is fine.
6. **Port the usage-receipt design** into the prototype if it is ever shown to anyone outside the family.

## 07 Two things to push back on

**The documentation-to-runtime ratio is itself a risk.** 340 Markdown files against a 91-line UI shell is not caution; past a point it is a way of deferring the moment the design meets a child. The governance is good and nearly all of it should stay. But every contract hardened before A3 is hardened against an untested hypothesis, and four are already known to be wrong.

**The German opening scope rests on an unanswered question.** German is the only subject in the whole design where two languages must be spoken inside one utterance. If the synthesiser cannot do it cleanly, German needs the split path, with its own latency and billing profile — which changes the opening scope's cost model. Settling it now is cheaper than discovering it at A4.

**Limits of this review.** The architecture was read and the source sampled at one commit. The 618 backend tests were not run; the 402 files under `development/` were not reviewed; the ingestion and cleanup logic was not audited in depth, and from reading it appears to be the most carefully built part of the repository. The research packs and economics model were not examined. Nothing here is a security or compliance judgment.

The comparison is honest about one thing above all: neither codebase has yet taught anybody anything.