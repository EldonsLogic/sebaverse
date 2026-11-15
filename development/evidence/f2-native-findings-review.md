# Native advisory review checkpoint —15 November2026

DEV-006; R054/R075/R078/R094/R097/R098. Observed evidence:actual Grype0.121.3 report from Linux run43596679254, DBv6.1.10.72 matches/33unique CVE IDs. This is a review register, **not approval**, an exploitability verdict or a finding suppression file. No row has been added to infra/security-reviewed-findings.json.

## Publisher evidence and bounded decisions

Ubuntu [USN-9065-1](https://ubuntu.com/security/notices/USN-9065-1), published12November2026, fixes the six matched libc6 advisories in Noble2.39-0ubuntu8.12; current scanned2.39-0ubuntu8.9 remains held. Authenticated candidate/dryrun evidence is preserved; the six-package companion transaction has not been installed or cleared.

The [OpenSSL10November2026 advisory](https://openssl-library.org/news/secadv/20261110.txt) excludes OpenSSL3.0 for CVE-2026-88822/88823/95691/95692. The scanned3.0.13-based distribution package therefore needs a source-version applicability decision rather than automatic acceptance of a generic scanner match. These are review candidates only:confirm distribution patch lineage before approving. CVE-2026-107496 affects3.0 under a CMS encryption path involving attacker-controlled certificate material; no global safety conclusion follows from planned local PostgreSQL usage.

[PostgreSQL18 libpq connection documentation](https://www.postgresql.org/docs/18/libpq-connect.html), relevant to identified libpq18.6, distinguishes SSL and GSS controls. Local synthetic configuration now explicitly disables GSS encryption and requires SCRAM-SHA-256;83 DB-free tests pass. Actual negotiated behavior remains untested. This does not approve Kerberos findings or prove every native code path unreachable.

All other applicability remains unknown until exact publisher/component/path review; the source URLs below are retained from actual scanner evidence. No blanket Medium/Low approval.

## Complete unique-ID register

Locator for each row:system-native-cves.json matches where vulnerability.id equals ID, preserved under development/evidence/f2-hardened-run-43596679254/. Repeated binary matches are grouped without dropping count or component.

| ID / publisher source | Severity | Packages and observed versions | Matches | Current disposition |
|---|---|---|---:|---|
| [CVE-2016-20013](https://ubuntu.com/security/CVE-2016-20013) | Negligible | libc6 2.39-0ubuntu8.9 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-100290](https://ubuntu.com/security/CVE-2026-100290) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-107161](https://ubuntu.com/security/CVE-2026-107161) | Medium | libsasl2-2 2.1.28+dfsg1-5ubuntu3.1 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-107496](https://ubuntu.com/security/CVE-2026-107496) | Medium | libssl3t64 3.0.13-0ubuntu3.16 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-107708](https://ubuntu.com/security/CVE-2026-107708) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-107778](https://ubuntu.com/security/CVE-2026-107778) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112314](https://ubuntu.com/security/CVE-2026-112314) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112315](https://ubuntu.com/security/CVE-2026-112315) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112316](https://ubuntu.com/security/CVE-2026-112316) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112317](https://ubuntu.com/security/CVE-2026-112317) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112318](https://ubuntu.com/security/CVE-2026-112318) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112319](https://ubuntu.com/security/CVE-2026-112319) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112320](https://ubuntu.com/security/CVE-2026-112320) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112321](https://ubuntu.com/security/CVE-2026-112321) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112322](https://ubuntu.com/security/CVE-2026-112322) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-112323](https://ubuntu.com/security/CVE-2026-112323) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-115819](https://ubuntu.com/security/CVE-2026-115819) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-119079](https://ubuntu.com/security/CVE-2026-119079) | Medium | libgssapi-krb5-2 1.20.1-6ubuntu2.10; libk5crypto3 1.20.1-6ubuntu2.10; libkrb5-3 1.20.1-6ubuntu2.10; libkrb5support0 1.20.1-6ubuntu2.10 | 4 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-18374](https://ubuntu.com/security/CVE-2026-18374) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
| [CVE-2026-67693](https://ubuntu.com/security/CVE-2026-67693) | Medium | libgnutls30t64 3.8.3-1.1ubuntu3.6 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-84243](https://ubuntu.com/security/CVE-2026-84243) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
| [CVE-2026-8674](https://ubuntu.com/security/CVE-2026-8674) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
| [CVE-2026-86805](https://ubuntu.com/security/CVE-2026-86805) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
| [CVE-2026-88647](https://ubuntu.com/security/CVE-2026-88647) | Medium | libgnutls30t64 3.8.3-1.1ubuntu3.6 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-88648](https://ubuntu.com/security/CVE-2026-88648) | Medium | libgnutls30t64 3.8.3-1.1ubuntu3.6 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-88822](https://ubuntu.com/security/CVE-2026-88822) | Medium | libssl3t64 3.0.13-0ubuntu3.16 | 1 | Publisher excludes upstream3.0; distribution-lineage review candidate, not approved |
| [CVE-2026-88823](https://ubuntu.com/security/CVE-2026-88823) | Medium | libssl3t64 3.0.13-0ubuntu3.16 | 1 | Publisher excludes upstream3.0; distribution-lineage review candidate, not approved |
| [CVE-2026-95184](https://ubuntu.com/security/CVE-2026-95184) | Medium | libgnutls30t64 3.8.3-1.1ubuntu3.6 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-95210](https://ubuntu.com/security/CVE-2026-95210) | Medium | libgnutls30t64 3.8.3-1.1ubuntu3.6 | 1 | Unapproved; exact applicability/mitigation review pending |
| [CVE-2026-95691](https://ubuntu.com/security/CVE-2026-95691) | Medium | libssl3t64 3.0.13-0ubuntu3.16 | 1 | Publisher excludes upstream3.0; distribution-lineage review candidate, not approved |
| [CVE-2026-95692](https://ubuntu.com/security/CVE-2026-95692) | Medium | libssl3t64 3.0.13-0ubuntu3.16 | 1 | Publisher excludes upstream3.0; distribution-lineage review candidate, not approved |
| [CVE-2026-95818](https://ubuntu.com/security/CVE-2026-95818) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
| [CVE-2026-97399](https://ubuntu.com/security/CVE-2026-97399) | Medium | libc6 2.39-0ubuntu8.9 | 1 | Patch exact reviewed transaction and rescan; held |
