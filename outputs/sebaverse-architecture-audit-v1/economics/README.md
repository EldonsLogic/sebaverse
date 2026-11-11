# Editable economics and sensitivity model

All values in inputs.json are illustrative assumptions unless explicitly null/unknown. Historical research rates are preserved in A09, but are not revalidated procurement quotes here. No live invoice or measured quality result exists. Run `python3 tools/model_economics.py` from repository root to regenerate scenarios.json and sensitivity.md. This is a planning calculator, not product implementation.

## Model boundaries and equations

Per active learner, text = sessions × turns × [(uncached input × input rate + cached input × cached rate + output × output rate)/1,000,000]. Input tokens already include bounded history/retrieval; summary/grade calls beyond the explicit reserve must be added rather than forgotten. AI subtotal adds embeddings, parsing, tools and exactly one retry/auxiliary multiplier. Audio branch is either cascade(input minutes × STT + output minutes × TTS) or realtime(connected minutes × realtime rate plus measured backend usage); never both for the same audio session.

Total monthly cost = N_active × variable USD + fixed infrastructure + educator/support/ops + rights/content + messaging/other. EGP cost uses an explicit FX input. Net receipts = N_paid × price × (1-refund rate)/(1+price-inclusive tax rate) - payment fees. Contribution = net receipts - variable service costs; operating result additionally subtracts fixed costs and labor. Paid and active populations differ; p95 usage/exam season and inactive paid entitlements need separate scenarios. Semester receipts must fund every active month; EGP 300 per term is not EGP 300 recurring monthly revenue.

Unknown FX, payment/tax/WhatsApp/rightsholder/educator/vendor prices remain null. Default output deliberately withholds a full margin/EGP recommendation until required inputs are supplied. Setting unknown costs to zero would create false profitability. The generated costs are lower-bound partial service costs, not full COGS. Founder hypotheses are 300 EGP/month or 300–500 EGP/course/semester; no final selling price is selected.

## Baseline reproduced from audit assumptions

20 sessions × 20 turns × 2,000 input/600 output tokens, effective input/output $0.19/$0.95 per million, 25% auxiliary reserve. Assumed 400 connected voice minutes; cascade 40% input/60% output at placeholder $0.003/$0.015. Text AI $0.475, cascade AI $5.575, realtime example AI $25.475 per learner/month. These reproduce A09 arithmetic without endorsing model names/rates or educational quality. Fixed allowances 100/200/600/3000 USD at 20/100/1000/10000 active learners are not load-tested capacity plans.

Sensitivity varies usage, context, cache, voice minutes/rates, and model prices; scale scenarios include 100/1,000/10,000 learners. FX and paid/active/term-month sensitivities must be run when those inputs are chosen. Teacher review/support/licensing/messaging/payments/tax can outweigh text inference. Margin must include these and failed/cancelled calls. Cost per successful independent activity uses measured completion counts; delayed learning gain cannot be inferred from chat volume.

## GPU break-even worksheet

Set monthly GPU cost G (including idle/redundant hours), non-GPU hosting H, engineering/operations O, variable inference cost v and comparable qualified hosted cost h per activity. Break-even activities = (G+H+O)/(h-v), only when h>v and model quality/privacy/license gates pass. Check measured throughput and peak concurrency separately; a profitable average can still miss latency. inputs.json holds null placeholders until actual benchmarks/quotes exist. No self-hosting saving is asserted.

## Commercial experiment

Use existing interested prospects to compare willingness to buy a clearly scoped monthly plan versus a course/semester pack. Disclose text/page/voice limits and content coverage. Measure conversion, payment friction, active/paid ratio, support minutes, completed independent activities, refunds and exam-season use. Secure current processor/recurring-billing eligibility and Egyptian rate cards; retain manual prepaid fallback. Do not promise unlimited voice or treat acquisition/labor as free because the founder does the work.
