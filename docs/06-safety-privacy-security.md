# Child safety, privacy and security plan

Source basis: U1/U2, G05/G10, A08 and preserved pinned audit evidence. This is a proposed control design and legal-review work plan; it does not certify compliance or assert current licensing deadlines. The regulator home page was opened in this session and had no readable text. Current official Arabic rules/processes and qualified Egyptian advice are required before processing real minors' data.

## Governance and consent

Create a processing register per purpose: tutoring, assessment, guardian reporting, billing, support, safeguarding, product evaluation and optional training. Record minimal fields, recipients/processors, storage/processing/transfer locations, legal basis/permissions, retention, deletion and owner. Counsel resolves current Law 151/2020/regulations, sensitive child/voice data, age-specific consent/assent mechanisms, licenses/permits, DPO applicability, transfer and breach duties. EU/US expansion triggers separate jurisdiction assessment; do not impose a universal COPPA age rule or claim GDPR/FERPA certification.

ConsentRecord stores notice/version/language/purpose, verified relationship method, actor, time and withdrawal. Child notice is understandable and explains AI uncertainty and reporting. A checked box, paid account or family relationship does not establish a complete lawful processing route. Invitation acceptance does not by itself verify legal guardianship; define custody disputes, recycled phone numbers and revoked links. Founder owns operations, educator owns pedagogical review, safeguarding reviewer/counsel roles must be appointed before pilot.

Processor register covers every LLM, embedding, speech, hosting, trace, messaging and payment service, with current contract, retention/training settings and transfer route. Provider API not-training-by-default is not zero retention. No training on child data by default; research/model improvement needs separate rights/purpose/review. An unapproved fallback never receives data.

## Safeguarding behavior

Age-appropriate explanations and refusal/redirect patterns in all three languages; no sexualized content, manipulative dependence, secrecy requests or shaming. For credible harm, use a human-owned escalation protocol with minimal facts, severity, authorized recipient, response hours and fallback. Do not promise 24/7 emergency monitoring or automatic unrestricted parent disclosure. Define exceptions/access with counsel and educators. Test adversarial self-harm, bullying, sexual exploitation, abuse disclosure and unsafe advice scenarios with reviewed expected behavior; no operational helpline numbers are invented in the product specification.

Guardian progress visibility covers evidence, uncertainty, next steps and usage, with a defined appeal/export/delete route. Sensitive chat/incident access is separately scoped/audited. WhatsApp defaults to a minimal notification with an authenticated portal link; no diagnosis/grade/chat snippet on a lock screen. Verify recipient, opt-in, quiet hours, deduplication, opt-out and revocation before sending.

## Security threat/control matrix

| Threat | Required control | Evidence before pilot |
|---|---|---|
| Cross-child/tenant guessed IDs, streams, vectors, exports | Deny-by-default server-derived object scopes; private assets; current grants | At least 100 negative cases across tenants, guardians and revocation; zero leaks |
| Malicious uploaded instructions or files | Quarantine, format/signature/malware checks; bounded parser with restricted network/credentials | 30 injection cases plus oversize, archive bomb and malicious filename fixtures |
| Model tool/grade/permission escalation | Typed allowlisted tools, deterministic authority and schemas | No arbitrary exec/network/role/grade mutation from prompts |
| Account theft or CSRF | Staff MFA, secure cookie/session lifecycle, exact webhook exemption, reset/revocation/rate limits | Auth/session/webhook negative tests; reviewed browser security settings |
| Unbounded spend/concurrent quota race | Atomic reserve/finalize, provider caps, retry/tool/audio limits | Race/cancel/crash receipts reconciled without double charges |
| Raw expression execution in grading | Typed restricted math AST, domain/units, process resource limits | Malformed/complex expressions fail safely |
| Sensitive logs/vendor traces/backups | Pseudonymous metrics, no raw child content by default, encryption and least privilege | Synthetic-marker deletion trace, access review and restore drill |
| Compromised dependencies/actions | Reviewed minimal locks, SBOM, license/provenance/secret scans, pinned actions/images | Resolve actual deployed dependency tree; no blanket approval from old limited OSV queries |
| Stale guardian access/jobs after revocation | Recheck live relationship and cancel queued reports/streams | Forwarded invitation, recycled number and revoked link scenarios |

## Retention and deletion

Proposed defaults for review: raw audio transient/no routine retention; exceptional consented diagnostic sample expires in seven days; full chat limited to a short configurable window (candidate 30 days); minimal learning evidence retained during active enrollment plus an agreed closure period; billing/legal records separated and retained only as required. These are proposals, not legal deadlines. G3 must approve a purpose-by-purpose schedule; code must not invent one.

Deletion workflow: verify authority/scope → immediate access revocation → queued purge of DB objects, files/page images, chunks/vectors, summaries/caches, jobs, traces and processor stores → record minimal deletion receipt → backups expire per documented schedule; replay deletion after restore. Do not promise immediate physical erasure from immutable backups. Derived analysis/training datasets must honor scope and assess re-identification; aggregate small cohorts can remain identifying.

## Incidents and recovery

Runbook: triage severity → contain affected topic/provider/account/data path → preserve minimal authorized evidence → appoint owner → evaluate counsel-defined notification duties → correct/replay and verify → controlled restore/rollback → postmortem/regression. Secrets rotate through secret manager, never prompts/logs. Proposed pilot RPO <=24h/RTO <=4h needs timed restore proof. Test backup-key recovery and deletion reapplication. Real-student use is blocked by unresolved critical authorization/consent/rights/safety defects regardless of average quality or cheap costs.

## Licensing adoption gates

A08 gives reported source findings: DeepTutor Apache-2.0 notice/dependency obligations; LearnHouse AGPL plus separate EE scope; Frappe AGPL; Moodle GPL; Langfuse core/EE separation; content/model/dataset/voice rights independent of code. AGPL combined-work/source obligations depend on actual modification/integration; HTTP/container separation is not automatic clearance. Source offer requirements do not mean publishing children's data. Check deployed artifacts and obtain legal resolution for contested scope. EduStudio exact audited pin remains quarantined; compromise beyond observed workflow mechanism is not established. No external disclosure/messages were sent or are authorized by this planning deliverable.
