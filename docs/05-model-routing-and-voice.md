# Provider routing, Jev and multilingual voice

Current architecture note (U11/U12, 11 November 2026): architecture/technical-baseline.md selects the subject-independent technical baseline. German is one retained initial use case, not a design dependency; technical selection does not certify content/benchmarks or authorize execution. Detailed learning thresholds/provider models remain subject to evaluation.

Sources U1/U2/C1; G06; A09/A11. Jev introduction was opened 2026-11-10: https://jev-ai.org/docs/ . The vendor describes structured decisions with probabilities; educational calibration and local quality remain unmeasured.

## Provider-neutral boundary

Capabilities: generate/stream structured text, embed, transcribe, synthesize and optional realtime audio. Common request: scoped task, schema, language, model snapshot, max input/output/tool steps, timeout, cancellation ID, privacy class and spend reservation. Common result: content/tool proposals, finish reason, normalized error, actual token/audio/cache units, provider request ID, price version and raw usage receipt reference. Retain provider-specific capabilities explicitly; avoid a lowest-common-denominator abstraction that conceals data retention or audio billing.

Candidate matrix: OpenAI, Anthropic Claude, Google Gemini, Qwen/DeepSeek hosted endpoints, and at least one locally hosted open-weight model. Candidate status is not procurement approval. Each needs current model/weight license, minors/data/retention/training terms, processing location/transfer review, exact tariff/units, rate limits, Arabic/math quality and operational owner. Provider nationality is not a quality or privacy determination. No exact production model is locked here.

Route order: enforce legal/privacy/rights eligibility → required modality/schema/context capability → safety and task quality floor → availability/latency → cost budget. A cheaper model cannot bypass a quality/privacy gate. Start with a qualified default and one qualified fallback; choose deterministic task routes before learned routing. Tool calls, complex verification and uncertain grades may escalate within budget. Failure without eligible fallback returns a safe resumable message; it never sends data to an unapproved provider. Retry only retryable failures with bounded backoff and idempotency; provider calls may bill even when application retries.

## Jev-style experiment

Tasks: request routing, misconception hypothesis classification, next-action recommendation among allowed choices and parent-notification candidate tagging. Safety/authorization/grade/entitlement authority stays deterministic. No classifier may directly promote mastery, send a notification or broaden curriculum scope.

Compare explicit rules, a small conventional classifier where labels suffice, a small hosted/open-weight LLM and Jev on the same frozen inputs/labels. Proposed initial set: 300 educator-labeled cases across Egyptian Arabic/MSA/English, including ambiguous and adversarial inputs; independent held-out families and language/noise slices. Two reviewers adjudicate disagreements; low agreement means redefine the task rather than optimize to noisy labels. No raw identifying student chats required.

Metrics: macro-F1/per-class precision/recall, dangerous routing/false-alert errors, Brier/ECE/reliability plots where probabilities exist, abstention coverage-risk, latency p50/p95, billed cost/1,000 decisions and operator/review overhead. A vendor probability is not a calibrated mastery probability. Tune thresholds on validation only. Promote only if held-out quality is no worse than the approved baseline within a founder/educator-agreed margin, severe-error fixtures all pass and total cost/maintenance benefit is demonstrated. Thresholds and noninferiority margin are open decisions, not retrofitted to a winner. Run in shadow before use; retain deterministic fallback and record model/version/reason. Jev stays optional if terms, availability or results fail.

## Text and context economics

Separate static policy, curriculum retrieval, learner projection and session summary. Bound history and output; summarize checkpoints with source references and count the summary call. Retrieve only relevant current chunks. Use deterministic grading/tagging when valid and precompute reviewed explanations/items. Cache eligible static prefixes/content with versioned keys; measure provider-reported cached units instead of assuming savings. Log Arabic/English tokenization separately. Limit concurrency, retries, tools and total turn spend; reserve atomically before dispatch, reconcile receipts and release unused funds.

Quality-adjusted cost = all inference/audio/tool/parse/review cost divided by completed valid independent activities; long-term cost per retained skill requires actual delayed outcomes. Avoid rewarding a router for cheap failed lessons. Never suppress safety/deletion operations because tutoring quota is exhausted.

## Language and speech behavior

Language preference per activity, with switching mid-session and consistent Arabic/English academic terminology. MSA formal terms coexist with Egyptian conversational explanation. Evaluate dialect and code-switching separately; Arabic support labels do not establish child-speech quality. Bidi isolate formulas/English terms; screen readers receive sensible math alternatives.

Baseline candidate: push-to-talk → final transcript → bounded text tutor → TTS; show/edit/confirm transcript for critical numbers, units, operators and negation. Compare streaming cascade and native speech-to-speech under equivalent semantic workload. Native realtime voice must still produce inspectable assessment evidence; uncertain transcription cannot reduce mastery. Record connection/idle time when billed, distinguish input vs output audio and do not double count cascade speech on a native billed path.

Explicit mic consent and recording indicator, pause/mute, speed/read-aloud control, text fallback, reconnect checkpoint and session/minute caps. Barge-in cancels obsolete model/audio and prevents late grading. No voice cloning or identity inference. Raw audio is transient by default; diagnostic retention requires separate defined purpose/permission and expiry.

PoC: 60–100 voluntary adult native-speaker utterances initially, licensed/consented, spanning Egyptian Arabic/MSA/English, code-switching, noise and math. Later child audio requires appropriate pilot readiness. Measure WER/CER plus >=95% critical-entity fidelity candidate gate, educator intelligibility >=4/5, p95 end-of-speech→first-audio <1.5s on recorded profile and prompt cancellation. Report failures/denominators by language; these are targets, not results. Record actual receipts for matched cascade/realtime sessions before choosing quota or plan.

## Self-hosting decision

Compare hosted cost to GPU-hours + idle capacity + redundancy + storage/network + monitoring + engineer operations + model/weight/security maintenance. Use measured Arabic workload throughput, memory, batching and p95 concurrency; monthly student count alone cannot size GPUs. Benchmark at 100/1,000/10,000 active students with realistic exam peaks. Break-even requires eligible quality and utilization, not just low nominal GPU price. Local deployment stays future until measurements support it; no assumption that open weights are cost-free or legally unrestricted.
