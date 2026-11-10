# Adaptive learning libraries and pilot recommendation

Audit date: 10 November 2026. Source inspection is pinned below. This is an engineering assessment, not evidence that any model improves Egyptian pupils' learning. No training with student data took place.

## Decision

Build a small, explicit learner-state and policy module. Start with teacher-tagged concepts, prerequisite edges, evidence-counted mastery rules, a short diagnostic, and a spaced-review scheduler. Use pyBKT as an offline benchmark and optional later estimator, not as a new server. Defer deep knowledge tracing and reinforcement-learning path selection until held-out Egyptian curriculum data demonstrates a worthwhile gain over the simple baseline. Keep the estimator replaceable behind `estimate(state, graded_attempt, model_version)`.

**Quarantine current EduStudio HEAD.** Its pinned workflow [`.github/workflows/exfil.yml`, lines 8–15](https://github.com/HFUT-LEC/EduStudio/blob/4acedad91be841a3c3c109944b4180997b8a7260/.github/workflows/exfil.yml#L8) reads `secrets.PYPI_API_TOKEN`, transforms it into reversed base64, and writes it to workflow output. This is a source-observed secret-exposure mechanism, not proof a token was present, a package was altered, or an attacker controls the project. Do not execute its workflows, install a current package, or recommend an earlier revision as safe without a provenance investigation. The commit subject is `ci: exfil`. No workflow was run during this audit.

## Pinned inventory

| Project | Source / exact commit | Declared license and version | Last commit date | Intended use |
|---|---|---|---|---|
| EduStudio | [HFUT-LEC/EduStudio](https://github.com/HFUT-LEC/EduStudio/tree/4acedad91be841a3c3c109944b4180997b8a7260), `4acedad91be841a3c3c109944b4180997b8a7260` | MIT; setup version v1.1.7 | 2026-10-27 | Research comparison only; quarantine pinned revision |
| pyKT | [pykt-team/pykt-toolkit](https://github.com/pykt-team/pykt-toolkit/tree/ccbaf37b07e3e7ff7b2415475b2faacb967d54ea), `ccbaf37b07e3e7ff7b2415475b2faacb967d54ea` | MIT; setup 0.0.38 | 2026-10-18 | Preferred later deep-KT benchmark harness, isolated environment |
| PyEdmine | [ZhijieXiong/pyedmine](https://github.com/ZhijieXiong/pyedmine/tree/31e434ae5b2d3bf9823044a4bd4582b184c0190b), `31e434ae5b2d3bf9823044a4bd4582b184c0190b` | MIT; metadata 1.0.0 | 2026-10-22 | Alternative research harness; do not add alongside pyKT |
| pyBKT | [CAHLR/pyBKT](https://github.com/CAHLR/pyBKT/tree/0f4ea412e18f6bcbd396fdf2be68fdd43aebebb6), `0f4ea412e18f6bcbd396fdf2be68fdd43aebebb6` | MIT; setup 1.5.0 | 2026-11-01 | Offline BKT fitting and regression oracle |
| py-irt | [nd-ball/py-irt](https://github.com/nd-ball/py-irt/tree/d4f4dbda1e591f2b2f471556b9664c6b2829131c), `d4f4dbda1e591f2b2f471556b9664c6b2829131c` | MIT; 0.8.3 | 2026-11-01 | Later offline item-bank calibration |
| py-fsrs | [open-spaced-repetition/py-fsrs](https://github.com/open-spaced-repetition/py-fsrs/tree/9446cb06605c597a063aeee49f7d188d42e34dc2), `9446cb06605c597a063aeee49f7d188d42e34dc2` | MIT; 6.3.2 | 2026-08-09 | Adopt scheduler after pilot integration tests |

Dates describe the fetched latest commit, not frequency of maintenance; shallow clones cannot establish long-term bus factor. Root licenses were inspected. Model papers, copied implementations, pretrained weights and datasets still need independent rights checks.

## Canonical PyEdmine verification

The [PyPI `edmine` package](https://pypi.org/project/edmine/) identifies author ZhijieXiong, Python >=3.9 and the author's homepage. That [documentation homepage](https://zhijiexiong.github.io/sub-page/pyedmine/document/site/index.html) links back to `ZhijieXiong/pyedmine`. The cloned `pyproject.toml` repeats that author, homepage and package name. This triangulates the canonical upstream rather than relying on a similarly named search result. Its release metadata says 1.0.0, while the fetched source is newer; package and repository parity was not verified.

## Source-level comparison

### EduStudio

Architecture: data templates, model templates, training templates and evaluation templates rather than a deployed adaptive tutor. [`edustudio/datatpl/KT/KTInterDataTPL.py:3`](https://github.com/HFUT-LEC/EduStudio/blob/4acedad91be841a3c3c109944b4180997b8a7260/edustudio/datatpl/KT/KTInterDataTPL.py#L3) specifies label conversion, ID remapping, sequence construction and random KT splitting. `CD/CDInterExtendsQDataTPL.py:3` generates a Q-matrix after filtering/remapping/splitting. `model/KT/__init__.py` imports DKT, AKT, SAKT, DeepIRT and others; `model/CD/__init__.py` imports IRT, MIRT, DINA, NCDM and graph-oriented variants. These are actual implementations, not conversational personalization.

[`model/CD/irt.py:40`](https://github.com/HFUT-LEC/EduStudio/blob/4acedad91be841a3c3c109944b4180997b8a7260/edustudio/model/CD/irt.py#L40) constructs student and exercise embeddings; `forward`, `get_main_loss`, `predict` are tensor-oriented integration points. Inputs need stable pupil/item IDs, correctness and a teacher-audited item-to-concept Q-matrix where required. Different models need extra graph/content/time features. New IDs need explicit fallback, not arbitrary embedding indices.

`setup.py:9–22,45–48` requires Python >=3.8 and loosely bounded Torch >=1.10, numpy/scipy/pandas/sklearn, tensorboard and networkx. This is not a reproducible lock. `evaltpl/prediction_evaltpl.py:10–44` offers AUC, accuracy and RMSE; interpretability/fairness evaluation modules also exist. `tests/test_run.py:4–22` trains KaNCD for two CPU epochs on FrcSub, which entails dataset/dependency preparation; not a self-contained unit test. Current CI provenance blocks execution regardless of those useful algorithms.

### pyKT

A PyTorch benchmark toolkit, not a student account system, event store or teaching policy. Pinned [`setup.py:5–25`](https://github.com/pykt-team/pykt-toolkit/blob/ccbaf37b07e3e7ff7b2415475b2faacb967d54ea/setup.py#L5) declares 0.0.38, Python >=3.5, numpy/pandas, Torch >=1.7, wandb and entmax. Treat old lower bounds as metadata, not proof current Python compatibility. Do not inherit these versions into the application.

[`pykt/models/dkt.py:7–33`](https://github.com/pykt-team/pykt-toolkit/blob/ccbaf37b07e3e7ff7b2415475b2faacb967d54ea/pykt/models/dkt.py#L7) embeds `concept_id + number_of_concepts * correctness`, runs an LSTM and emits sigmoid scores per concept. This needs ordered concept/response sequences and a trained vocabulary. `pykt/models/evaluate_model.py:48–204` dispatches model-specific signatures, applies next-response masks, and returns AUC/accuracy. It supports several model families but is not one universal production inference contract. Real-time use needs a custom adapter for history windows, vocabulary versions, CPU loading, timeout and cold-start fallback. Predicted correctness is not a validated mastery percentage or misconception diagnosis.

Additional pinned source: `pykt/preprocess/split_datasets.py:164–197` uses seeded row shuffles for train/test and folds; `main:599–615` builds the ID map on the whole dataset before splitting, then generates windows after the split. That is a transductive vocabulary assumption, not a clean unseen-item evaluation. `pykt/models/train_model.py:297–378` selects checkpoints on validation AUC and stops after ten non-improving epochs. Do not repeatedly inspect optional test scores while tuning. A bundled `tests/test_opera_integration_config.py`, `tests/check_dataset.py` and `tests/test.sh` exist, but no per-model test coverage was verified. Disable external experiment logging for learner data unless the destination, consent and redaction have been approved. The repository contains training/preprocessing/tests and documented benchmark protocols. Its [public issue list](https://github.com/pykt-team/pykt-toolkit/issues) remains a compatibility/support risk to review before adoption; issue counts are not evidence of defects in a specific model. Full clone downloads stalled; the partial clone pinned the commit and selected source blobs were inspected with `git show`, saved under `work/pykt-source/`; checkout remained incomplete and was not treated as a runnable installation. Full test execution was not achieved.

### PyEdmine

`edmine` separates datasets, model registry, trainers, metrics and environments. [`edmine/model/sequential_kt_model/DKT.py:16–115`](https://github.com/ZhijieXiong/pyedmine/blob/31e434ae5b2d3bf9823044a4bd4582b184c0190b/edmine/model/sequential_kt_model/DKT.py#L16) accepts `params` and `objects`, uses concept/correctness embeddings plus RNN/LSTM/GRU, and exposes `get_predict_score`, `get_predict_score_on_target_question`, and `get_knowledge_state`. It needs `question_seq`, `correctness_seq`, `mask_seq`, sequence lengths, and question-to-concept transfer/mask tables. The state is a model output, not an independently measured learning outcome.

Source includes DKT, DKVMN, AKT, SimpleKT, SparseKT, QIKT and other KT models; cognitive diagnosis IRT/MIRT/DINA/NCD; KG4EX exercise recommendation; and learning-path agents/trainers. The [documentation](https://zhijiexiong.github.io/sub-page/pyedmine/document/site/index.html) describes learning-path RL using a pretrained KT simulator. Optimizing that simulator is not proof of benefit with real pupils; do not enable online exploration with minors.

[`edmine/dataset/split_dataset.py:5–67`](https://github.com/ZhijieXiong/pyedmine/blob/31e434ae5b2d3bf9823044a4bd4582b184c0190b/edmine/dataset/split_dataset.py#L5) partitions sequences stratified by length/accuracy and uses folds. The CD split at lines 70–119 shuffles within each learner's interaction halves; that does not establish future-time generalization. Preserve raw student grouping before sequence expansion and use time-held-out tests. `metric/knowledge_tracing.py:13–37` computes AUC/accuracy/MAE/RMSE, but single-class/very small samples need explicit handling; cold-start uncertainty remains.

Packaging weakness: [`pyproject.toml`](https://github.com/ZhijieXiong/pyedmine/blob/31e434ae5b2d3bf9823044a4bd4582b184c0190b/pyproject.toml) lists no runtime dependencies although source imports Torch/numpy and README requires pandas/sklearn. It references `README4PYPI.md`, absent from this checkout. A dependable build/lock must be established before reuse. The MIT copyright names Stanford Future Data Systems although package ownership identifies the author; preserve notices and trace copied code before extraction. No `.github` CI or dedicated automated test suite was found; examples are not tests. Keep it a research alternative rather than the live application dependency.

### pyBKT

[`source-py/pyBKT/models/Model.py:22–46`](https://github.com/CAHLR/pyBKT/blob/0f4ea412e18f6bcbd396fdf2be68fdd43aebebb6/source-py/pyBKT/models/Model.py#L22) defines prior, learning, guessing, slipping and optional forgetting parameters; multilearn/multiprior/multipair/multigs variants. `fit:66`, `partial_fit:82`, `predict:115`, `evaluate:163` offer usable offline APIs with columns `order_id`, `skill_name`, `correct`, `user_id`. `partial_fit` refits model parameters; do not confuse it with a constant-time per-pupil posterior update.

Transparent per-concept latent state is preferable to deep KT at small N, but fitting all parameters separately on a handful of pupils is unstable and non-identifiable. Begin with fixed, reviewed priors and pooled parameters; communicate uncertainty. Runtime BKT updating can be a tiny pure domain function, cross-checked offline against pyBKT. The C++ backend includes Eigen/OpenMP; `setup.py:31–38` adds macOS OpenMP requirements. A Python backend exists. Tests cover backend parity, parameter recovery, one-attempt students and unseen classes. Do not load untrusted pickle models (`Model.py` imports pickle).

### py-irt

[`py_irt/models/one_param_logistic.py:47–86`](https://github.com/nd-ball/py-irt/blob/d4f4dbda1e591f2b2f471556b9664c6b2829131c/py_irt/models/one_param_logistic.py#L47) defines Bayesian 1PL ability minus difficulty with vague/hierarchical priors. Other source/tests cover 2PL/3PL/4PL and multidimensional variants. `pyproject.toml:10–22` requires Python >=3.10,<3.15 and Pyro/Torch/numpy/pandas/scipy/sklearn. This is an offline calibration dependency, not necessary for a logistic scoring formula at runtime. Need repeated, overlapping responses to anchor items, sufficient variation and a linked item bank. Generated one-off items cannot each receive credible calibrated difficulty from tiny samples. Prefer expert difficulty tiers initially; use held-out calibration before introducing 1PL. Additional discrimination/guessing parameters need more data, not just a more elaborate estimator.

### py-fsrs

[`fsrs/scheduler.py:142,236–262`](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/fsrs/scheduler.py#L236) exposes `Scheduler.review_card(card, rating, review_datetime, review_duration) -> (Card, ReviewLog)` and enforces UTC-aware review times. Store per-pupil review cards/logs and algorithm version. `pyproject.toml:7,20–21` declares 6.3.2, Python >=3.10 and typing-extensions; optimizer dependencies are optional and lazily loaded (`fsrs/__init__.py:16–26`). Default parameters work without local fitting; they are a starting schedule, not proof of Arabic curriculum retention. Preserve review evidence separately from mastery; successful recall of a fact does not certify conceptual transfer.

## Algorithm and operational comparison

| Approach | Data and cold start | Interpretability and online cost | Small pilot | Integration / evidence limits |
|---|---|---|---|---|
| Evidence-counted rules | Concept tags, graded unassisted attempts, item versions; explicit unknown state | Very high; constant work per concept | Best first baseline | Custom domain code; thresholds need teacher review; avoid pretending a heuristic is a calibrated probability |
| BKT | Ordered binary responses per skill; sensible prior/guess/slip/learn values; no local training required if fixed | High; scalar Bayesian update | Good with pooled/fixed priors | No automatic misconception semantics; noisy LLM grades bias posterior |
| 1PL IRT | Connected item/person response matrix, anchor items, repeated observations | High; cheap after offline calibration | Expert difficulty first | No learning-time dynamics; sparse new items have uncertain difficulty |
| Deep KT / graph KT | Many representative sequences, stable vocabularies and Q-matrix; graph/time/content features vary by model | Lower; CPU inference possible but history/caching and training add work | Defer | Public benchmark transfer to Egypt unproven; never set a universal minimum sample count |
| Prerequisite DAG | Expert-authored concept/edge versions, cycle checks, diagnostic evidence | High; simple graph traversal | Adopt | Graph structure does not estimate mastery; PostgreSQL tables suffice, no graph server required |
| FSRS | Repeated timestamped recall ratings; default parameters for new cards | Medium-high; cheap per-card scheduling | Adopt for revision | Review rating mappings and overload limits need validation; scheduler is not whole tutoring policy |
| RL learning paths | Trained simulator plus logged actions/rewards and off-policy support | Low; substantial evaluation complexity | Reject for pilot | Simulator exploitation and confounding; do not experiment freely on children |

No library removes the need for a curriculum ontology, validated items, misconception taxonomy, grading confidence, consent, learner authorization, or policy evaluation. One training harness is enough: pyKT for later deep-KT comparison, pyBKT for BKT, optional py-irt when the item bank supports calibration. Do not add EduStudio, pyKT and PyEdmine to the live backend together.

## Pilot state and policy contract

Record append-only `attempt_id`, pseudonymous learner, curriculum/year/version, item/version, concept tags, response timestamp, attempt number, hint exposure, score/rubric version, grader/model version, confidence and provenance. Exclude tutor-demonstrated answers from unassisted mastery evidence. Store misconception as a hypothesis with evidence, confidence, review status and expiry, not a permanent label.

Keep a transactional learner-state projection with `unknown/learning/provisional/secure`, evidence counts, last independent success, uncertainty and revision due date. Fix parameters/policy per release; include idempotency and out-of-order replay rules. The policy chooses prerequisite remediation, explanation, worked example, practice or revision using this state and an approved content set. An LLM can phrase instruction, but cannot silently edit the concept graph, grades, model parameters or entitlements.

BKT illustration: after a correct response, posterior `p* (1-slip) / [p*(1-slip)+(1-p)*guess]`; then apply learning transition `p_next = posterior + (1-posterior)*learn`. A wrong response uses `p*slip / [p*slip+(1-p)*(1-guess)]`. Keep guess/slip bounded, handle denominator guards, and version assumptions. These values describe a model belief, not a clinical or educational diagnosis.

## Evaluation and migration gates

1. Start with a teacher-reviewed concept map and 100–200 versioned questions for one narrow course unit. Use synthetic histories for system tests and consented real assessment only after privacy controls pass.
2. Establish simple rule/BKT/item-difficulty baselines. Use held-out pupils for new-pupil generalization and forward-time splits for continued pupils. Split before windowing and multi-concept expansion; prevent the same item clone or answer leak across folds. Fit vocabulary/scalers/item statistics on training only.
3. Report log loss, Brier score/calibration, AUC where both labels exist, and performance by language, concept, first-attempt/hinted status and history length. Bootstrap by pupil, not independent rows; with small N report wide uncertainty. Never interpret AUC alone as learning gain.
4. Validate educational utility with common anchor diagnostics and delayed retention/transfer tests, time-on-task, completion and teacher-reviewed misconception precision. Control grading bias and baseline ability. Parent satisfaction and tutor fluency are secondary signals.
5. Fit pooled BKT/1PL only when coverage supports identifiable parameters and confidence intervals. Trigger on coverage/learning curves, not a fixed enrollment target. Shadow estimates first, then bounded release with fallback.
6. Benchmark one deep model only after representative sequence coverage exists. Adopt only if it improves calibration and useful action selection without harming subgroup outcomes or latency/cost. Keep an immutable baseline, offline evaluation set, human approval, feature flag and immediate rollback. No automatic training on identifiable conversations and no self-modifying deployment.

## Execution record and limitations

Source clones were read only. No upstream instruction files were found in these adaptive repositories. No unknown setup scripts were executed. No packages, student data, GPU jobs or paid services were used.

- **PASS:** reviewed py-fsrs deterministic 13-review regression, reproducing upstream expected intervals `[0,2,11,46,163,498,0,0,2,4,7,12,21]`; Card dictionary round-trip serialization also passed. Python 3.11 ran directly from source with `PYTHONDONTWRITEBYTECODE=1`; existing typing-extensions was exposed on its import path. This verifies a narrow scheduler path, not the full suite.
- Default Python 3.9 failed FSRS import because pattern matching requires >=3.10; Python 3.11 initially lacked typing-extensions. These were environment mismatches, resolved for the smoke check without installing packages.
- Torch, numpy, pandas, Pyro and pytest are absent in the default interpreter. Full BKT/IRT/KT fitting and unit suites were not executed. No numerical claims about trained accuracy or latency are made.
- EduStudio execution intentionally withheld because of observed workflow secret exposure. No vulnerability database scan or complete transitive dependency audit was completed. No declared dependency should be treated as cleared solely because its license is MIT.

Final workspace note: the original full pyKT shallow clone completed after source review. The audit remains based on the same pinned selected files; no additional runtime/model suite was executed. Earlier incomplete-checkout observations above describe the inspection stage, not a permanent availability claim.
