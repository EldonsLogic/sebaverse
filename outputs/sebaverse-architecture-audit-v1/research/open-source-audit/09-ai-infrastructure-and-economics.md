# AI infrastructure and operating economics

Cost date: 10 November 2026. USD/month unless stated otherwise. These are transparent scenarios, not quotes, measured bills or a final EGP selling price. Quality and legal processing conditions take priority over the cheapest model.

## Verified price inputs versus assumptions

The [official OpenAI pricing page](https://developers.openai.com/api/docs/pricing) was opened during research. Standard text input/output prices per million tokens: GPT-6 Luna $0.10/$0.50; GPT-6.1 Terra $1/$5; GPT-6.1 Sol $2/$10. Cached input: $0.01/$0.05/$0.10 respectively. GPT-Live-1 is $0.05 per session minute, billed per second; backend model and tool usage is additional. Realtime audio token pricing is different and must not be substituted for session-minute pricing. Availability and account limits were not tested. Rate cards can change.

For comparison, older [mini TTS](https://developers.openai.com/api/docs/models/gpt-4o-mini-tts) and [mini transcription](https://developers.openai.com/api/docs/models/gpt-4o-mini-transcribe) model pages are now marked deprecated. Do not choose them simply because historical tutorials quote low per-minute prices. A current cascade must obtain fresh supported-model prices and benchmark dialect quality.

**Explicit planning assumptions:** cascade STT $0.003 per input minute and TTS $0.015 per output minute are placeholders, not verified current supported-vendor quotes. Hosting, storage, monitoring, embeddings and routine parsing below are allowances, not verified vendor prices. We did not purchase anything or test billable calls.

## Usage definition and formula

One active learner: 20 sessions/month, 20 tutor turns/session. Each turn includes 2,000 billable input tokens (history, retrieved context and instructions included) and 600 output tokens. Thus 800,000 input and 240,000 output tokens per month. A budget router sends 90% of these token volumes to Luna and 10% to Terra. This is an economic assumption, not evidence the mixture meets Arabic tutoring quality. Effective rates: $0.19 input / $0.95 output per million.

Base text spend = `800000 * 0.19 / 1e6 + 240000 * 0.95 / 1e6 = $0.38` per learner. Add 25% AI reserve for bounded retries, grading and small auxiliary calls: **$0.475**. If auxiliary calls exceed that reserve, meter them explicitly rather than hiding them.

Text-heavy case: the text workload above, without sustained audio. Voice-heavy case: the same semantic tutoring workload plus 400 connected voice minutes/month, with 40% student audio and 60% synthesized tutor audio for the cascade. This equalizes teaching workload; audio model backend token usage may differ in real sessions and must be measured.

- Cascade planning estimate = `0.475 + 1.25*(160*0.003 + 240*0.015)` = **$5.575/student/month**. Conditional on unverified cascade rates.
- GPT-Live planning estimate = `0.475 + 1.25*(400*0.05)` = **$25.475/student/month**. Uses verified session-minute rate and assumed backend text volume. Do not charge an additional STT/TTS cascade for the same Live audio. Silence, interruptions and idle connections still affect connected duration.

General equation: `N * [sessions * turns * ((input_tokens*input_rate + output_tokens*output_rate)/1e6) + audio_cost + tools] * retry_reserve + fixed_infrastructure + non_AI_costs`. Cache uses a separate cached token term. Apply the reserve once. Annual/semester costs depend on active months, exam peaks and promised quotas, not simply enrolled accounts.

## Monthly scenarios

Fixed assumptions include modest application/worker compute, managed database or equivalent, storage/backup and basic monitoring: $100 pilot, $200 at 100, $600 at 1,000, $3,000 at 10,000. They assume ordinary traffic and no always-on self-hosted GPU. They are capacity/budget placeholders, not load-tested sizing.

| Active students | Fixed allowance | Text AI | Text total | Cascade AI* | Cascade total* | Live AI | Live total |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | $100.00 | $9.50 | $109.50 | $111.50 | $211.50 | $509.50 | $609.50 |
| 100 | $200.00 | $47.50 | $247.50 | $557.50 | $757.50 | $2,547.50 | $2,747.50 |
| 1000 | $600.00 | $475.00 | $1,075.00 | $5,575.00 | $6,175.00 | $25,475.00 | $26,075.00 |
| 10000 | $3,000.00 | $4,750.00 | $7,750.00 | $55,750.00 | $58,750.00 | $254,750.00 | $257,750.00 |

*Cascade values use unverified rate assumptions. Totals exclude tax, payment gateway fees, chargebacks, WhatsApp, curriculum licensing/authoring, educator grading/review, customer support, legal/security review, salaries and acquisition. At 10,000 students a solo operator likely needs operational support; that labor is not represented by a compute allowance. Reserve and infrastructure allowances are not gross-margin guarantees.

Scenario inputs and recomputed values are also in [cost-scenarios.json](evidence/cost-scenarios.json). These calculations are reproducible arithmetic, not a performance test.

## Sensitivity and limits

| Change from baseline | Text AI/student/month | Consequence |
|---|---:|---|
| 90% Luna / 10% Terra baseline | $0.475 | Quality must pass; routing should use task type/confidence, not random percentage |
| All Luna | $0.250 | Lowest cost only if correctness and safety hold |
| All Terra | $2.500 | Stronger model candidate; not an established learning-quality result |
| All Sol | $5.000 | Premium review/routing can dominate spend |
| Twice the sessions | $0.950 | Linear if context/turns unchanged; voice minutes also double |
| 8,000 input / 1,000 output per turn | $1.235 | History and retrieval growth materially increase spend |
| Half input tokens cached at matching blended cached rates | $0.387 | About 19% saving; no assumed output saving, cache-write fees excluded |
| 10% extra tool calls at $0.01 each over 400 turns | +$0.500 with reserve | Web search and agent loops can cost more than baseline text |
| Voice 100 / 400 / 800 Live minutes | Audio $6.25 / $25 / $50 with reserve | Connected-minute quota is essential |
| Cascade speech prices double | $10.675 total AI | Text savings do little to offset voice-heavy costs |

The cache row assumes eligible automatic cached input, no paid cache-write option, 400k uncached and 400k cached input at blended $0.19/$0.014, plus 240k output at $0.95, then 25% reserve. Caching must be isolated by privacy/scope; never reuse personalized output across learners. Arabic tokenization and long system/context prompts require measurement; do not infer token counts from English word counts.

**Growing histories:** replaying all earlier messages makes total session input grow approximately quadratically with turn count. Bound context, use source-linked summaries, retrieve limited curriculum passages and account for summarization calls. Cache static curriculum prompts where safe; do not count savings until provider usage receipts confirm them.

## Recommended infrastructure choices

| Concern | Pilot decision | Scale trigger / fallback |
|---|---|---|
| LLM inference | Hosted provider behind `generate/stream/usage` adapter | Benchmark at least two providers; no self-hosted GPU before utilization economics and legal review |
| Routing | One qualified default plus explicit fallback/review route | Preserve model/version and route reason; budget never overrides safety |
| Retrieval / embeddings | Postgres lexical search + pgvector when measured useful; versioned multilingual embeddings | Record dimension/model, backfill new index before switch; no mixed embedding spaces |
| Vector storage | Same Postgres, tenant/course filters | Index/partition after filtered recall/latency benchmark; export original chunks to avoid lock-in |
| STT/TTS | Current supported models selected by Egyptian Arabic benchmark | Cascade offers separate control and transcripts; actual supported pricing pending |
| Continuous voice | Optional P1 experiment; short-lived credentials, session cap and disconnect | Pipecat if transport/turn-taking needs justify worker; compare Live and cascade using actual receipts |
| Document processing | Docling in restricted asynchronous worker; teacher approval | OCR fallback only on failed benchmark pages; page limits and curriculum deduplication |
| Caching | Bounded in-process cache initially; static content/version keys | Add external cache only with multi-worker invalidation need |
| Session memory | Bounded conversation context; source-linked summaries; Postgres authoritative evidence | DeepTutor memory is a design reference; no opaque autonomous student dossier |
| Metering | Append-only usage ledger by learner/course/session/request/provider/model | Reconcile reservations and provider receipts, record failed/cancelled calls |
| Entitlements | Course/semester grant plus server-side token/minute/page quotas | Signed idempotent payment webhooks, reversals and expiry; no browser trust |
| Jobs | Postgres jobs + transactional outbox, same app worker | Celery only when scheduling/concurrency and retries exceed simple worker needs |
| Monitoring | Structured logs + OTel, cost/latency/error/grounding dashboards | Langfuse optional after redaction and footprint assessment |

## Admission and spend controls

Reserve a maximum spend amount transactionally before dispatch; scope reservations to student/course/billing period. Enforce hard concurrency and tool-step limits, maximum history/output tokens, parsed pages, audio duration and retry counts. Finalize actual receipt and release remainder. Expire orphan reservations; reconcile at least daily against vendor reports. Provider limits and app limits both matter. Stop or degrade gracefully on cap; never silently charge an unapproved upgrade.

Use soft warnings and hard provider/app monthly caps. Keep grading and deletion operational during a tutoring quota stop. A payment success does not bypass guardian-consent requirements. Track p50/p95 input/output/audio usage and cost per **completed independent learning activity**, not only per chat. Version price tables to explain historical bills.

WhatsApp country/category/template fees were **not verified** because Meta's official rate page required login. Do not assume current free service windows or generic global prices. Model `notifications_per_student * delivered_message_price + provider_fee` separately. Four monthly parent summaries per learner imply 80 / 400 / 4,000 / 40,000 outbound messages across these scenarios. Obtain the Egyptian rate card and template classification before budgeting.

[Paymob's portal](https://wizard.paymob.com/) says feature selection does not activate recurring billing; account enablement remains necessary. Merchant acceptance, fees and settlement are unresolved commercial inputs. Start with prepaid course/semester entitlements if recurring collection is unavailable. No gateway transaction fee or exchange rate is invented here.

## EGP pricing decision framework

Let current treasury conversion be `FX` EGP/USD and non-AI cost per active learner be `L`. Approximate cost base = `USD total/N * FX + L + payment/tax allowances`. A target contribution margin `g` requires net receipts at least `cost/(1-g)`; this is not a recommended selling price. Run FX +20% and usage p95/exam-season scenarios, specify fair-use quotas by course/semester, and distinguish registered from active/paid learners. Validate willingness to pay in separate competitive/customer research before setting prices.
