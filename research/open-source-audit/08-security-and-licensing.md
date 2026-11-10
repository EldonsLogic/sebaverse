# Security, child protection and licensing

10 November 2026. This is a source-based technical risk assessment and implementation checklist for this product, not legal advice, a penetration test or a compliance certification. “Not verified” is not synonymous with “absent.” Complete primary audits are in [02](02-deeptutor-audit.md) and [03](03-learnhouse-audit.md).

## Findings that change the recommendation

| Finding | Evidence / confidence | Product consequence |
|---|---|---|
| EduStudio pin includes a publishing-secret exposure workflow | High source confidence: [workflow lines 8–15](https://github.com/HFUT-LEC/EduStudio/blob/4acedad91be841a3c3c109944b4180997b8a7260/.github/workflows/exfil.yml#L8) reads `PYPI_API_TOKEN` and prints a reversible encoding | Quarantine this revision and do not run CI/install packages until provenance is independently established. No proof token existed, logs exposed it or release package was compromised. |
| LearnHouse exempts CSRF checks based on header presence on arbitrary paths | Confirmed narrow isolated function behavior: [csrf.py:214](https://github.com/learnhouse/learnhouse/blob/7dc39bc0e116437d564e4c7f96974397e913c338/apps/api/src/security/csrf.py#L214) | Restrict exemptions to exact verified webhook routes. Browser exploit chain not tested; CORS/preflight/SameSite influence feasibility. Medium hardening defect, not a demonstrated account takeover. |
| LearnHouse OSS paid-access helper falls back to allow when EE unavailable | High source confidence: [ee_hooks.py:113](https://github.com/learnhouse/learnhouse/blob/7dc39bc0e116437d564e4c7f96974397e913c338/apps/api/src/core/ee_hooks.py#L113) | Intentional free-tier behavior; not a bypass of its intended OSS policy. Build entitlements or license actual payment feature before selling access. |
| DeepTutor voice is authenticated shared infrastructure without per-user LLM grants | [voice.py](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/deeptutor/api/routers/voice.py), source verified | Add independent course/voice quotas and provider spend limits; authenticated alone is insufficient commercial authorization. |
| DeepTutor STT reads upload before 25MB limit; TTS lacks max text limit | Same pinned voice route | Enforce streaming/ingress size caps, concurrency, synthesis length and reservations. Runtime exploitability/load effect unmeasured. |
| Public LearnHouse profile/details fields unsuitable for child learning state | [users.py:92](https://github.com/learnhouse/learnhouse/blob/7dc39bc0e116437d564e4c7f96974397e913c338/apps/api/src/db/users.py#L92) | Separate private learner state and explicit projections; disable unnecessary public profiles/community features. |
| No verified end-to-end consent, retention and deletion system for this use | Both audits distinguish generic accounts from legal consent | Real-minor pilot blocked until owned controls and legal processing conditions are in place. |
| General agent tools and document/model inputs expand authority surface | DeepTutor tools/MCP/exec and both retrieval pipelines | Student-facing policy uses allowlisted typed tools; educational documents never grant tools or permissions. |

Findings were documented locally; no issues, messages or disclosures were sent to maintainers because the user did not authorize external communication.

## Existing controls versus required product controls

| Control | Observed existing implementations | Required work / release evidence |
|---|---|---|
| Authentication | DeepTutor bcrypt/token services; LearnHouse Argon2/JWT, account lockout fields and rate-limiting infrastructure | Staff MFA, reset/revocation tests, secure HttpOnly/SameSite cookies, CSRF and session expiry; no keys/tokens in browser storage where avoidable |
| RBAC and organization scope | LearnHouse org roles/principals and scoped AI/RAG; DeepTutor owner/session and guardian plumbing | Central object authorization, learner/guardian relationship checks on every operation and tool; deny by default; negative tests for guessed IDs and exports |
| Guardian relations | DeepTutor active relationship, permission and revocation checks | Real-world guardian verification, custody/dispute handling, scope and consent lifecycle; never equate invitation or email ownership with legal guardianship |
| Student data isolation | Identity and scope fields exist; no complete multi-tenant assurance established | Canonical `tenant_id/student_id`; mandatory scoped queries; private object keys; short-lived signed URLs; retrieval filters; optional RLS defense with connection-scope tests |
| Upload safety | LearnHouse extension/MIME/magic/ZIP size helpers; DeepTutor voice size guard | Ingress and per-student quotas, malware scan/quarantine, format allowlist, archive bomb protection, parser CPU/memory/time/egress limits, no macros/active content |
| Prompt injection | Both can retrieve contextual material; generic filtering insufficient | Separate system instructions from cited data, tool allowlist, no secrets in context, deny arbitrary URLs/exec, injection regression fixtures; never rely on a prompt-only defense |
| Tutoring safety | No target-specific child-safety evaluation established | Age-appropriate content controls in all languages, bullying/sexual/self-harm safeguards, factual uncertainty, emergency escalation design, educator/human review; no manipulative dependence or secrecy |
| Assessment integrity | Both question/assessment code exists | Keep answer keys out of prompts until appropriate; separate practice hints from independent evidence; grading confidence, appeals, rubric versions and cheating/answer-leak tests |
| Retention/deletion | LearnHouse SQL deletion and Redis TTL; DeepTutor persistent stores | Data map across SQL, files, vectors, summaries, jobs, traces, provider stores and backups; automatic deletion and proof; revocation cancels pending tasks/notifications |
| Encryption | No deployment encryption claim independently verified | TLS on external/internal sensitive links; encrypted DB/storage/backups; managed keys and rotation; least-privilege operator access |
| Secrets | Environment/config mechanisms exist; EduStudio workflow is an explicit concern | Secret manager/CI scopes; short-lived credentials; no secrets in prompts/logs; reviewed actions; rotation/incident playbook; no child uploads in CI |
| Abuse and economics | LearnHouse auth/AI rate limits and credit reservation; DeepTutor traffic-control seams | User/IP/concurrency limits, per-course caps, bounded tool/retry loops, reserve/finalize ledger, voice timeouts, anomaly alerts and circuit breakers |
| Audit trail | Session/tool traces and some platform events; LearnHouse audit_logs EE-only | Own security/consent/content/payment/policy audit log; pseudonymous IDs, access controls, retention, integrity and staff access review |
| Backup/recovery | Docker volumes do not demonstrate recovery | Encrypted offsite backups, timed restore drill, proposed pilot RPO24h/RTO4h, key recovery and deletion-reapplication rules |
| Observability | Logging, CI, tracing/usage hooks and Sentry dependency | Redact content/PII by default; no raw audio/transcripts in third-party traces; restricted diagnostic sampling; latency/cost/quality alerts |
| Supply chain | CI and manifests/locks exist; mutable tags/actions found | Stable version selection, hashes/digests, SBOM, license inventory, dependency scan, reviewed install hooks, signed provenance and update/rollback tests |
| WhatsApp privacy | No complete founder-specific implementation audited | Verified guardian recipient, opt-in/out, minimal template, link to authenticated portal; no grades, diagnoses or child chat on a lock screen by default |

Use separate staff, guardian and student projections. Guardians receive their authorized child's progress summary and its uncertainty, not automatically every private conversation. Define child safety escalation and access exceptions with educators/counsel; log access and provide a dispute path. Avoid collecting identity documents unless the approved verification process requires them, and minimize their retention.

## Threat scenarios to test

1. Student guesses another learner's session/document/item/guardian ID, including vector retrieval, resumable streams and downloads.
2. Uploaded textbook says to ignore instructions, reveal hidden prompts/answer keys or call an external endpoint. Retrieved content remains evidence and cannot change permissions.
3. Parent invitation token is forwarded, relationship revoked, phone number recycled, or custody disputed. Access stops based on current relationship, not stale JWT claims.
4. Expired subscription starts direct tutor/voice requests; concurrent requests race quota reservations; cancellation/retry duplicates charging or mastery updates.
5. Parser decompresses an archive bomb, downloads remote references, executes active content or consumes unbounded RAM. Quarantine worker has no learner database credentials or unrestricted network egress.
6. Logging/export/backup preserves deleted child data. Test deletion using traceable synthetic markers and reapply deletions after restore.
7. Misgraded hinted answer inflates mastery and skips a prerequisite. Evidence type and grader confidence must govern state updates.

## Egyptian legal review: current evidence and unresolved points

The translated [Law 151/2020 text in ILO's NATLEX archive](https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/111246/EGY111246%20Eng.pdf) identifies children's data as sensitive and requires guardian consent for its processing, with licensing and cross-border rules. Voice and identifiable learning histories can be personal data. A small pilot is not assumed exempt.

The [published translation of the law and executive regulations](https://eg.andersen.com/wp-content/uploads/2026/02/Law-No.-151-of-2020-1.pdf), including Article 15, differentiates under-15 and 15–18 consent mechanisms and refers to Center-approved procedures. It also addresses processing records and international transfers. English translations are aids; the official Arabic text controls. Do not infer that an ordinary checkbox or EU-hosted server is sufficient.

[Contemporary legal reporting](https://www.shandpartners.com/insights/briefings/telecoms-media-technology/the-issuance-of-the-executive-regulations-of-the-data-protection-law-and-the-establishment-of-the-data-protection-centre/) dates Decree 816/2025 to effect on 2 November 2025, with a one-year transition ending in early November 2026. At this audit date that reported window has elapsed. Confirm current licensing/permit processes, any extensions, DPO applicability, sensitive-child data permission, breach deadlines and foreign-processor requirements directly with Egyptian counsel/PDPC. No extension is assumed.

The [PDPC consent-guideline URL](https://pdpc.gov.eg/assets/pdf-data/Guidelines/DSConsent.pdf?csrt=11082648485996809314) was found, but direct retrieval returned no readable content; this audit does not claim to have verified the current official implementation guidance. Obtain it before real-student onboarding. Processor contracts, data flows and provider retention/training settings must be reviewed for **every** model, speech, hosting, trace and messaging vendor. Do not claim compliance from any repository README.

Operational legal work product needed: counsel-approved data map/processing purposes, guardian notice and verification method, consent and withdrawal evidence, processor/transfer register, retention/deletion schedule, incident contact procedure and required license/permit/DPO decisions. This list is a launch preparation task, not a determination that each formal obligation applies identically to every business structure.

## International applicability

GDPR is conditional on territorial scope and offering/monitoring behavior, not automatically applicable merely because software has EU users in theory. If applicable, assess Articles 3, 5, 8, 25, 28, 32 and 35, child consent ages by member state, DPIA, processor and transfer requirements. Source: [official GDPR text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng).

US COPPA may apply to a child-directed service or relevant knowledge of under-13 users in scope; it is not a universal worldwide age rule. The FTC states its rule was amended in 2025, so use the revised rule rather than old checklists. Source: [FTC guidance](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions). FERPA is a separate institutional/US educational-records question, not a general certification this Egyptian subscription product automatically needs.

For OpenAI specifically, [official data controls](https://developers.openai.com/api/docs/guides/your-data) distinguish training use, abuse monitoring and application-state retention. “API data not used for training by default” is not equivalent to zero retention. Verify supported endpoints, eligibility and under-18 contract requirements before sending child data. Equivalent review is needed for other providers; no vendor setting creates Egyptian legal authorization by itself.

## Licensing decision framework

| Component / use | Implication | Required decision |
|---|---|---|
| DeepTutor Apache-2.0 | Commercial/proprietary adaptation is generally permitted subject to license/notice/patent terms; trademarks and third-party code separate | Preserve license, applicable NOTICE and change notices; inspect dependency closure and optional parser licenses |
| LearnHouse AGPLv3 | Commercial charging is allowed; modified covered network software carries source-offer obligations | Accept copyleft scope or obtain sufficient commercial rights before incorporating/modifying |
| LearnHouse EE | Separate code/rights; public hooks are not a license to EE implementation | Written feature/license/hosting quote and exact terms; no audit of unavailable EE code claimed |
| Frappe LMS | AGPLv3 in inspected license | Same source-obligation analysis; not a permissive alternative |
| Moodle | GPLv3+ source; network use alone does not add AGPL section13 | Review distributed modified code and plugins; no blanket proprietary plugin exemption |
| Langfuse | MIT core with explicit EE path exclusions | Do not label whole tree MIT or assume EE features available |
| MIT/BSD/PostgreSQL components | Generally commercially usable with notices/conditions | Preserve licenses and transitive notices, review native libs/model weights separately |
| Curriculum, model weights, voices and datasets | Repository code license does not grant content/model/voice/data rights | Rights register per artifact; no unknown or noncommercial-only assets in paid product |

AGPL section 13 applies to modified covered versions interacting remotely; Corresponding Source scope and combined-work analysis depend on actual code/coupling. It does not automatically require publishing unrelated databases, customer data or every independent business service. Conversely, HTTP, separate containers or separate repositories are not automatic safe harbors. If AGPL code is copied into the monolith, hiding it behind an adapter does not remove its obligations. For conveying builds, sections 4–6 and installation/source requirements also matter. Preserve existing notices and provide a functional source offer for the deployed covered version. License text: [AGPLv3](https://opensource.org/license/agpl-3-0); pinned LearnHouse LICENSE is primary project evidence.

Apache-2.0 code can be used within an AGPL-covered combined work when conditions are satisfied; the permissive license does not erase the stronger combined-work obligations. Do not combine code until the exact integration and distribution/network model have been reviewed. Prefer clean interfaces and owned product schemas for maintainability, not as a claim of legal immunity.

## Dependency checks performed and remaining gaps

A public OSV query on 10 November covered eight exact LearnHouse manifest versions: FastAPI, SQLModel, Pydantic, redis, Alembic, Stripe, Sentry SDK and React. The response returned no vulnerability entries for those queries. See [dependency-check.json](evidence/dependency-check.json). This is a **limited manifest-version query**, not a resolved lockfile/container scan, package-existence verification or “no known vulnerabilities” certificate for the stack. Transitive dependencies, browser assets, OS libraries and optional tool/model dependencies were not cleared.

Before any build, resolve a reviewed minimal lock; verify package registry provenance, run OSV/pip-audit/npm equivalent against the actual resolution and scan the container/OS. Review install hooks without running them first. Pin action SHAs and image digests; record update ownership and patch windows. Dependabot/Renovate activity is useful but not sufficient evidence. The observed EduStudio workflow makes provenance a priority even where a vulnerability database reports nothing.
