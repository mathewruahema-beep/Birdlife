# Microsoft 365 / Entra ID: facts

The lookup table for `birdlife-microsoft365`. **Edit this file first when a
value changes, then the prose.** Posture numbers are dated 19 to 30 Jun 2026
unless stated; re-verify before asserting. Named per-user weakness data is
CONFIDENTIAL and stays in the security skill and dashboard.

## Tenant

| Fact | Value |
|---|---|
| Tenant | BIRDLIFE AUSTRALIA, `birdlife.org.au` |
| Tenant ID | `2b431a7b-9a21-4b53-8943-4a10ff69970d` |
| Azure subscription (active) | BirdLife Australia Azure `f0b2d7cf-c6f1-4ab0-9c67-cc3dff6721cd` |
| Azure subscription (empty, pending cancellation) | "Azure subscription 1" `82c42bb2-…` |
| Trusted office public IP | `120.151.226.128/32` ("BirdLife Office - Trusted IP") |
| Mathew Hema object ID | `49d23f8b-4b95-4bda-a9ac-39261cfd4ae0` |
| Licence tier | Entra ID P1 only (P2 costed ~A$2,500/yr for ~15 admins) |
| New-starter licence | Microsoft 365 Business Premium |
| UPN format | `firstname.lastname@birdlife.org.au` |
| Break-glass accounts (documented, NOT yet created) | `breakglass01@`, `breakglass02@birdlife.org.au` |

Directory snapshot 21 Jun 2026: 2,707 users (~2,700 `#EXT#` guests), 481
groups, 24 app registrations, 129 enterprise apps, 651 devices (499 unmanaged,
408 stale).

## Conditional Access policies (8)

| # | Policy | State |
|---|---|---|
| 1 | Per-user MFA (Microsoft) | On |
| 2 | Block legacy authentication | On |
| 3 | Block sharepoint access | Report-only |
| 4 | High assurance, 4 hours | On |
| 5 | Medium assurance, 8 hours | On |
| 6 | Require MFA for non-trusted countries | On |
| 7 | Salesforce Administrators, phishing-resistant MFA (created 15 Jun 2026) | On |
| 8 | Standard assurance, 24 hours | On |

No tenant-wide enforced MFA policy. Change rule: report-only 7 to 14 days with
a written rollback before enforcement.

## IT-SEC-001 no-MFA service account standard (v1.0, 29 to 30 Jun 2026)

| Item | Value |
|---|---|
| Group | `CA-NoMFA-ServiceAccounts` |
| Policies | `CA-001-NoMFA-Block-LegacyAuth`, `CA-002-NoMFA-Block-BrowserAccess`, `CA-003` / `CA-003b` (desktop client + named location, 30-day sign-in frequency), `CA-004-NoMFA-Block-AdminApps` |
| Account standard | 20+ character vaulted password, never expires, no admin roles, minimum licensing |
| Exception register | only `discovery.centre` populated; site and owner blank |

## Privileged accounts

| Role | Accounts |
|---|---|
| Global Administrator (6) | `Office365.admin` and `admin.365` (shared, `.onmicrosoft.com`), `admin365.keith`, `mathew.hema`, `mathew.hema.admin`, `ross.james.admin` |
| Privileged role assignments | 20 total (target 10) |

## MFA remediation population (30 Jun 2026, 237 accounts, all Pending)

| Group | Accounts |
|---|---|
| P1 staff with no MFA | `bnb.count`, `discovery.centre`, `emu.review`, `julia.hurley`, `website.logins` |
| Test accounts | Test, keith.stafftest, test101, test123, testbqcases, testcalendar2 |
| Service accounts | `birdbot4`, `sxiq.local`, `sxiq.text`, `wa.server` |
| Shared mailboxes | 66 |
| Room mailboxes | 4 |
| Admin accounts to verify | `mathew.hema.admin`, `ross.james.admin`, `sxiq.azure` |
| SMS default | 16 users |
| MFA OK | 147 staff |

Baseline: 203 of 2,561 MFA-capable (7.9%); SSPR 7; passwordless 46.

## Intune and Defender (21 Jun 2026)

| Item | Value |
|---|---|
| Enrolled devices | 138, all Windows, corporate MDM; 26 non-compliant |
| Compliance policies | Windows 10 (4 Dec 2025); Android Device Administrator (2 May 2021, deprecated) |
| Configuration profiles | 17 |
| Absent | BitLocker, App Protection, ASR rules (0 of 19), Update rings, security baselines (8 available, 0 assigned) |
| Secure Score | 48.19% (554.2 / 1150): Identity 57.35, Data 55.56, Device 49.83, Apps 37.34 |
| Devices in MDE | 115 |
| Vulnerabilities | 5,422; 200 critical; 122 exploitable |
| Named CVEs | CVE-2026-12440 (Edge, CVSS 9.6) on 109 of 115; CVE-2023-36010 on 114; 17 OpenSSL CVEs on 100 |
| Off | Tamper Protection, LSA Protection; no Safe Links, Safe Attachments, custom anti-phishing; external auto-forwarding allowed |

## Employment Hero to Entra sync (Logic App)

| Component | Value |
|---|---|
| Logic App | `logic-emphero-entra-sync` (Consumption) |
| Resource group | `rg-emphero-entra-sync` |
| Key Vault | `kv-emphero-sync`, system-assigned managed identity, 5 secrets |
| App registration | `EmpHero-EmployeeID-Sync`, client ID `86345594-9286-40ae-85a8-f9c1c63e5482` |
| Graph permissions | `User.Read` delegated; `User.ReadWrite.All` application (consented) |
| Graph secret expiry | 5 Jan 2027 |
| Join key | EH `company_email` to Graph `mail` |
| Scope | one-way, `employeeId` only |
| Monitoring dashboard | `emphero-entra-sync-monitoring` |
| Status | deployed, 0 succeeded / 2 failed (EH 403, insufficient platform permission) |
| Deprecated resources to delete | Function App `func-emphero-entra-sync`, App Service plan `AustraliaEastPlan`, storage `stemphentrasync` |

Native EH to M365 add-on: connected; overwrites, never merges. Scope to Job
Title, Department, Manager, Office Location only. Employment Hero worker code
format `BLA###` (payroll and NetSuite join key).

## Local tooling

| Item | Value |
|---|---|
| Read-only Entra/Intune MCP | `C:\azureintegration`, app `d8125f4d` |
| Write-tier `entra-admin` server | exists; pending app registration and admin consent (plan: `docs/entra-admin-connector.md`) |
| entra-admin-mcp certificate | expires 26 Aug 2027; reminder routine `trig_01Vp14cTKJCLnC7psjiRZnUC` fires 25 Jul 2027 |

## Enterprise apps and dates

| Item | Value |
|---|---|
| Enterprise apps | 129, reviewed 21 Jun 2026, all decision fields blank |
| Next quarterly review | 19 Sep 2026 |
| No assigned principals | 18 apps |
| Immediate decommission | "Exclaimer Cloud AU Setup – Please remove after setup" |
| Duplicates | Asana 6 to 7, Zoom 3, Wrike 3, Exclaimer 3, Canva / Miro / Smartsheet 2 each |
| ADAL app | "P2P Server (2019)"; ADAL deadline passed Sep 2025 |
| Vevox Dashboard SAML cert | 21 Aug 2026 (passed; verify SSO) |
| Vevox SAML cert | 8 Sep 2026 |
| Tenant-wide MFA CA target | 15 Sep 2026 |
| TeamOrgChart+ | v2.1.20, org-wide (replaces Org Explorer) |

## Connector (`Microsoft 365`, productivity scope only)

Reads: `outlook_email_search`, `outlook_calendar_search`,
`find_meeting_availability`, `chat_message_search`, `teams_list_chats`,
`teams_list_channel_messages`, `sharepoint_search`, `get_me`. Drafts:
`outlook_create_reply_draft` (plain-text response `id: … webLink: …`),
`outlook_create_draft`. Sends exist (`outlook_send_draft`, `outlook_send_mail`,
`outlook_forward_mail`) and are used only when Mathew says "send" in that
session. Files: `sharepoint_upload_file`, `sharepoint_update_file` (dashboard
files with fixed names). Teams has no send API. Not exposed: Entra, Intune,
Defender, Conditional Access, licensing.

Teams channel dashboard files: `BirdLife-ICT-Operations-Dashboard.html`,
`BirdLife-ICT-Monitoring-Dashboard.html`, `BirdLife-Security-Dashboard.html`,
`_dashboard-run-log.txt`.
