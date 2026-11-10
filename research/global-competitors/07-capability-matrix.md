# Capability and feedback-loop matrix

Research cut-off: 10 November 2026. Read alongside [competitor profiles](02-competitor-deep-dives.md) and the [source register](11-sources-and-evidence.md). This is a comparison of public evidence, not a hands-on product benchmark. Source IDs Wxx/Axx resolve in the register.

**Legend:** D = documented implementation/behavior, high confidence in the bounded disclosure; V = vendor-described capability, medium confidence in implementation; P-hist = historical technical disclosure, high confidence historically and uncertain current deployment; U = not established in reviewed evidence. A cell marked U does not mean the feature is absent. Dates, populations and regional offers remain material. Pricing is an advertised offer, not a checked purchase.

| Capability | Eedi | CENTURY | Khanmigo / Khan Academy | Synthesis Tutor | Duolingo | Squirrel AI |
|---|---|---|---|---|---|---|
| Initial diagnosis | V: distractors W01 | D: topic diagnostic W08 | U: placement; levels W15 | V: placement A01 | P-hist: ability prediction A05 | V: foundation diagnosis A13 |
| Misconception specificity | V: authored graph W01 | V: gap targeting W08 | U: taxonomy | U: taxonomy | U: taxonomy | D: worked-step analysis A15 |
| Named tracing algorithm | U | U: KT family | D: level rules W15 | U | P-hist: IRT/LSTM A05 | U |
| Prerequisite relations | V: graph W01 | V: content graph W06 | D: prerequisite context W16 | U: graph | U: graph semantics | V: knowledge graph A13 |
| Next activity | V: targeted intervention W01 | V: predicted success W06 | D: review W15 | V: micro-checks A02 | P-hist: prediction A05 | V: matched practice A13 |
| Forgetting/revision | U: schedule | V: Memory Boost W10 | D: challenges W15 | U: schedule | P-hist: HLR A06 | U: schedule |
| Contradictory performance | U: policy | U: policy | D: mixed unchanged W15 | U: policy | P-hist: history updates A05 | V: repeat-error response A13 |
| Across-session state | V: predictions W01 | D: dashboard W09 | D: history context W16 | V: summaries A01 | D: memory A08 | V: reassessment A13 |
| Conversational teaching | V: constrained W01 | U: general dialogue | D: workflows W16 | V: interactive A02 | D: staged calls A08 | D: VATE branch A15 |
| Long-term conversational memory | U | U | U: full design | U | D: fact list A08 | U |
| Student material uploads/grounding | U | U | U: authorized textbook pipeline | U | U | U: rights/pipeline |
| Verified mathematical tools | U | U | D: SymPy/NumPy W16 | U | U | U |
| Voice turn-taking | U | U | D: read-aloud W19 | V: read-aloud A02 | D: push-to-talk A09 | U |
| Interruption/latency evidence | U | U | D: latency experiments W16 | U | D: turn control A09 | U |
| Arabic text | U | U | D: offered, limited QA W20 | U | U: tutor scope | U |
| Egyptian Arabic voice/code-switching | U | U | U | U | U | U |
| Parent visibility | U: current scope | U: exact parent access | D: flag routing W18 | V: emails A01 | U: tutor-parent workflow | U: exact access |
| Teacher/classroom workflow | V: DQR W05 | D: assignments W07 | V: tools W13 | V: sales A01 | U: tutor-classroom integration | V: supervisor A13 |
| Exam/curriculum coverage | U: Egypt mapping | V: UK/IB W11 | V: broad subjects W13 | V: K–5 A01 | U: school exam mapping | V: US PreK–5 A14 |
| Consumer price/access | U: current tariff | V: from £8.33 annual-equivalent W11 | D: $4/month, US W14 | V: overlapping offers A01 | D: tier transition A04 | V: regional quote A14 |
| Learning-outcome evidence | D: supervised RCT W02 | V: usage associations W12 | D: proxy experiments W16 | U: product trial A03 | V: speaking study A12 | P-hist: narrow trials A16/A17 |
| Public reproducible component | U: commercial data rights W04 | U: core code | D: disclosed tool pattern W16 | U: core code | D: MIT HLR A07 | D: paper pattern A15 |

The matrix does not award an overall winner. Strong publication evidence for a tool or workflow does not establish superior learning outcomes. A smaller public surface may reflect limited disclosure. Regional curriculum fit requires checking subject, grade, specification and academic year rather than matching a broad brand label.

## Three separate feedback loops

Here **individual** means updating a student's instructional state; **system** means improving shared content, prompts or selection policies under version control; **model** means changing trained parameters. A memory entry is an individual-loop update, not model training. Human review of output is a system-loop input, not evidence that it is used to train weights.

| Provider | Individual adaptation evidence | System-improvement evidence | Model-improvement evidence | Disclosure boundary |
|---|---|---|---|---|
| Eedi | V: diagnosis W01 | D: trials/review W02/W03 | U: Eedi weight updates | Training data/permissions U |
| CENTURY | V: recommendations W06 | V: accumulated interactions W07 | V: in-house training W07 | Cadence/rollback U |
| Khanmigo | D: learner context W16 | D: controlled experiments W16 | U: proprietary fine-tuning | Prompt/model selection ≠ weight update |
| Synthesis | V: micro-assessment A02 | V: quality review A02 | U | Review-to-training path U |
| Duolingo | P-hist: learner-state updates A05 | D: A/B tests A10; review A11 | P-hist: learned predictors A05/A06 | Current retraining governance U |
| Squirrel AI | V: reassessment A13 | D: approved diagnosis reuse A15 | U: current deployed training | Cache updates ≠ weight update |

None of these bounded disclosures establishes that autonomous online self-training is required, safe or educationally superior. For a small pilot, keep the three loops separately permissioned and evaluated; compare any added algorithmic complexity with a transparent baseline using independent answers and delayed retention. This is an original recommendation, not a claim about a competitor's internal policy.

## How to use this matrix in architecture planning

Promote a V/P-hist item to a pilot requirement only after defining a measurable local behavior. For example, “misconception diagnosis” needs a labeled set of student explanations and follow-up probes; “Arabic voice” needs dialect, code-switching, background-noise, turn-taking and mathematical-terminology evaluation. Vendor scale and model names cannot substitute for those tests.

Maintain separate fields for disclosure confidence, pilot value and observed performance. Record source/content/model versions and access region when updating a cell. Procurement or a later authorized product walkthrough should resolve U cells with explicit tasks, observations and limitations rather than guesses about hidden architecture.
