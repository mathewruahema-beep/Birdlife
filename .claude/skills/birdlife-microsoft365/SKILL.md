---
name: birdlife-microsoft365
description: Expert operator knowledge for BirdLife Australia's Microsoft 365 and Entra ID tenant — Conditional Access, MFA remediation, privileged accounts, Intune, Defender, Essential Eight posture, SharePoint/Teams/Outlook, onboarding and offboarding, and the Employment Hero to Entra sync. Use for any task involving mailboxes, distribution lists, Teams, SharePoint, OneDrive, Outlook rules, user provisioning, licence assignment, MFA resets, Conditional Access, device compliance, or Microsoft security posture. Trigger on "Entra", "Azure AD", "M365", "Intune", "Defender", "Conditional Access", "MFA", "Essential Eight", "new starter", "offboard", "shared mailbox", "distribution list", "SharePoint site", or a birdlife.org.au UPN.
---

# BirdLife Australia — Microsoft 365 / Entra ID

## Tenant identity — verified

| Fact | Value |
|---|---|
| Tenant | BIRDLIFE AUSTRALIA (birdlife.org.au) |
| Tenant ID | `2b431a7b-9a21-4b53-8943-4a10ff69970d` |
| Azure subscription (active) | BirdLife Australia Azure `f0b2d7cf-c6f1-4ab0-9c67-cc3dff6721cd` |
| Azure subscription (empty) | "Azure subscription 1" `82c42bb2-…` — pending cancellation |
| Trusted office public IP | `120.151.226.128/32` ("BirdLife Office - Trusted IP") |
| Mathew's object ID | `49d23f8b-4b95-4bda-a9ac-39261cfd4ae0` |
| Licence tier | **Entra ID P1 only. No P2.** |
| New-starter licence | M365 Business Premium |

**P1-only is the constraint that shapes everything.** No risk-based Conditional Access, no PIM, no automated Access Reviews. P2 was costed at ~A$2,500/yr for ~15 admins. Every time someone proposes "just turn on PIM", the answer is "that is a licence purchase, not a config change".

Directory snapshot (21 Jun 2026): **2,707 users** (roughly 2,700 are `#EXT#` guests — exclude them from any matching logic), 481 groups, 24 app registrations / 129 enterprise apps, 651 devices of which 499 (77%) unmanaged and 408 (63%) stale.

## Conditional Access — 8 policies and the hole in the middle

1. Per-user MFA (Microsoft) — ON
2. Block legacy authentication — ON
3. **"Block sharepoint access" — REPORT-ONLY.** External SharePoint/OneDrive sharing is effectively unrestricted.
4. High assurance – 4 hours — ON
5. Medium assurance – 8 hours — ON
6. Require MFA for non-trusted countries — ON
7. Salesforce Administrators – Phishing resistant MFA — ON (created 15 Jun 2026)
8. Standard assurance – 24 hours — ON

**There is NO tenant-wide enforced MFA policy.** 116 users signed in over a 7-day window with zero CA coverage. This is the single largest identity risk in the environment and it maps directly to Essential Eight MFA sitting below ML1.

**Change rule, non-negotiable:** every CA change deploys **Report-only for 7-14 days** with a documented rollback before enforcement. Break-glass accounts `breakglass01@` / `breakglass02@birdlife.org.au` are excluded from all CA policies — but the programme guide notes **they are not yet created**. Verify before relying on them.

Retired "Approved client app" grant (retired Mar 2026) may still be referenced; replace with "App protection policy".

## MFA posture and the remediation campaign

Baseline audit 23 Jun 2026: **203 of 2,561 (7.9%) MFA-capable**; ~183 internal. 1,300 of 6,500 sign-ins in 7 days were single-factor. SSPR 7 users (0.27%). Passwordless 46 (1.8%).

Remediation list re-exported 30 Jun 2026 — **237 accounts, all rows still "Pending"**:

| Priority | Population | Action |
|---|---|---|
| P1 CRITICAL | 5 staff with no MFA: `bnb.count`, `discovery.centre`, `emu.review`, `julia.hurley`, `website.logins` | Register or harden |
| — | 6 test accounts: Test, keith.stafftest, test101, test123, testbqcases, testcalendar2 | Disable/delete. test101 and test123 are **active with real credentials** |
| — | 4 service accounts: `birdbot4`, `sxiq.local`, `sxiq.text`, `wa.server` | Move to managed identity |
| — | 66 shared mailboxes | Convert + block sign-in |
| — | 4 room mailboxes | Block sign-in |
| — | 3 admin accounts: `mathew.hema.admin`, `ross.james.admin`, `sxiq.azure` | Verify phishing-resistant MFA |
| — | 16 users on SMS default | Migrate to Authenticator |
| P4 | 147 staff MFA-OK | No action |

MFA audit cadence is **monthly**. The baseline is overdue for re-run.

## Privileged accounts

**6 Global Administrators** (recommendation ≤4-5): `Office365.admin` and `admin.365` (shared, `.onmicrosoft.com`), `admin365.keith`, `mathew.hema`, `mathew.hema.admin`, `ross.james.admin`. **20 privileged role assignments total** (recommend ≤10). No PIM.

Pattern is named user + separate `.admin` account. The two shared `.onmicrosoft.com` GA accounts are the worst item on the list — shared credentials with the highest privilege in the tenant.

## No-MFA service account standard — IT-SEC-001 v1.0

Authored by Mathew Hema, issued 29-30 Jun 2026. Group-based, using group `CA-NoMFA-ServiceAccounts`:

- `CA-001-NoMFA-Block-LegacyAuth`
- `CA-002-NoMFA-Block-BrowserAccess`
- `CA-003` / `CA-003b` desktop-client + named-location pair, 30-day sign-in frequency
- `CA-004-NoMFA-Block-AdminApps`

Account standard: 20+ character vaulted password, password never expires, no admin roles, minimum licensing. The exception register is owned by the IT Manager and currently has **only `discovery.centre` populated** — site and owner fields blank. (`discovery.centre` had zero sign-ins in 30 days as at 29 Jun 2026 — likely dormant or running on a cached Office token.)

## Intune — what is missing matters more than what is there

138 enrolled devices, all Windows, corporate MDM. 26 non-compliant.

- **2 compliance policies**: Windows 10 (04/12/2025) and an **Android legacy Device Administrator policy (02/05/2021) — a deprecated model that hit EOL Dec 2024**.
- 17 configuration profiles (lock screen, EDR, Firewall, SmartScreen, LAPS ×2, web sign-in, Office updates).
- 1 antivirus policy.
- **ZERO of: BitLocker policies, App Protection/MAM, ASR rules, Windows Update rings, assigned security baselines** (8 available, none assigned).
- **"No compliance policy = Compliant" default misconfiguration is in place.**
- **Device compliance is not linked to Conditional Access** — so compliance status currently controls nothing.
- Majority of the fleet is **Windows 10, EOL 14 Oct 2025, unpatched.** Win 11 24H2 upgrade not started.

## Defender / Secure Score (21 Jun 2026)

**Secure Score 48.19% (554.2/1150)** — Identity 57.35%, Data 55.56%, Device 49.83%, Apps 37.34%.

115 devices in MDE. **5,422 vulnerabilities — 200 critical, 122 currently exploitable.** 126 outstanding recommended actions, 12 regressing.

**Tamper Protection OFF. LSA Protection OFF.** External email auto-forwarding allowed. **No Safe Attachments, no Safe Links, no custom anti-phishing.**

Named CVEs: **CVE-2026-12440 (Edge, CVSS 9.6) on 109 of 115 devices** — already 5 days past the Essential Eight 48-hour SLA at review. CVE-2023-36010 (Defender, 3 years old) on 114 devices. 17 OpenSSL CVEs on 100 devices.

Positives worth stating in any board report: 0 risky sign-ins in the 7 days to 21 Jun; 19 attacks blocked in the prior two months; 0 users in the deleted-user bin.

## Essential Eight maturity (target ML1 in 12 weeks, ML2 in 12 months)

| Control | Current | Blocker |
|---|---|---|
| Patch Applications | **Below ML1** | Browser CVEs, OpenSSL |
| Patch Operating Systems | ML1 partial | Win 11 upgrade + WUfB not started |
| Multi-Factor Authentication | **Below ML1 (~8%)** | No tenant-wide CA MFA policy |
| Restrict Admin Privileges | **Below ML1** | LSA/Tamper off, 6 GAs, no PIM |
| Application Control | **Below ML1 (0/19 ASR rules)** | +14.82% Secure Score available here |
| Restrict Office Macros | **Below ML1** | Macro ASR rules |
| User Application Hardening | **Below ML1** | Email presets, WinRM, AutoPlay, Adobe JS, Chrome ADMX |
| Regular Backups | Partial ML1 | BitLocker + independent backup audit |

Anchor framework decision: **ACSC Essential Eight with a SaaS/identity overlay.** The overlay matters because most of BirdLife's real exposure (Salesforce, WordPress, Google Workspace, 129 enterprise apps) sits outside what E8 was designed to measure.

## Onboarding and offboarding

**Current state: there is no offboarding checklist at all.** Leaver access removal is ad hoc. This is the highest-value automation target in the environment.

Designed Power Automate leaver flow, in order:
1. 30-minute delay
2. Revoke sessions
3. Disable the account
4. Convert mailbox to shared
5. Remove the licence
6. Set a 90-day delete reminder

Designed starter flow: create Entra user → assign M365 Business Premium → notify IT and manager.

**Employment Hero is upstream for people data.** EH data rules that govern what arrives:
- **BLA### worker code is mandatory** — it is the payroll/NetSuite join key.
- Company Email format `firstname.lastname@birdlife.org.au`.
- Use "Add Employee"/Start onboarding, never CSV Quick-add.
- Capture the **personal** email at invite. Using the work email was the root cause of the broken invite loop.
- Reactivate rehires; never duplicate.

**Automation model Mathew has chosen: approve-only.** Unattended tasks detect and prepare; he approves the Entra writes. There is a local read-only Entra/Intune MCP server at `C:\azureintegration` (app `d8125f4d`).

**The write-tier app registration is LIVE (consented 26 Aug 2026): `entra-admin-mcp`** (client ID starts `bedc4239`). Graph application permissions consented: `User.ReadWrite.All`, `Group.ReadWrite.All`, `UserAuthenticationMethod.ReadWrite.All`, `Organization.Read.All`, `AuditLog.Read.All`, plus `Exchange.ManageAsApp` with the **Exchange Recipient Administrator** role. Credential: certificate only (thumbprint `23F3A8D1D5C1C1D03CE0E5DCC9AB8A153EEBCA39`, expires **26 Aug 2027** — renewal reminder Routine `trig_01Vp14cTKJCLnC7psjiRZnUC` fires 26 Jul 2027; no client secrets). Verified end to end with app-only `Connect-MgGraph` + `Get-MgUser`.

What this changes: in a session with the `entra-admin` server (Mathew's desktop), Entra/Exchange writes are **executable after his approval** — offboarding, onboarding, licences, MFA method resets, mailbox-to-shared, mailbox permissions, DLs. Sessions without that server (remote/mobile) still prepare the exact commands. Never use this identity on the break-glass accounts, GA accounts, or Conditional Access. Follow-up hardening on the list: scope the Exchange role with a management scope instead of tenant-wide.

## Employment Hero → Entra sync (Logic App)

| Component | Value |
|---|---|
| Logic App | `logic-emphero-entra-sync` (Consumption) |
| Resource group | `rg-emphero-entra-sync` |
| Key Vault | `kv-emphero-sync`, system-assigned managed identity, 5 secrets |
| App registration | `EmpHero-EmployeeID-Sync`, client ID `86345594-9286-40ae-85a8-f9c1c63e5482` |
| Graph permissions | `User.Read` delegated + `User.ReadWrite.All` application (admin-consented) |
| Graph secret expiry | **2027-01-05** |
| Join key | EH `company_email` ↔ Graph `mail` |
| Scope | One-way, **`employeeId` attribute only** |
| Monitoring | dashboard `emphero-entra-sync-monitoring` |

**Status: built, deployed, NOT working. 0 succeeded / 2 failed runs.** Blocker is a 403 — insufficient Employment Hero platform permission on Mathew's EH account. Needs Admin/Owner or org-wide view-employees.

Two design defects to fix when it is unblocked: the rotated EH refresh token is **not persisted back to Key Vault** (EH tokens rotate on each use, so the next run fails), and Key Vault secrets carry no expiry metadata.

**The native EH → M365 add-on is separately "Connected" and it OVERWRITES, never merges.** A blank field in Employment Hero blanks the corresponding Entra field. This is the most dangerous behavioural fact in the people-data chain. Scope it to Job Title, Department, Manager, Office Location — explicitly not Display Name, UPN or address.

Deprecated Azure resources pending deletion: Function App `func-emphero-entra-sync`, App Service plan `AustraliaEastPlan`, storage account `stemphentrasync`.

## Enterprise apps

All 129 reviewed 21 Jun 2026 — **every reviewer decision field is still blank; sign-off entirely outstanding. Next review due 19 Sep 2026** (quarterly).

- **18 apps with no assigned principals** → decommission candidates.
- "Exclaimer Cloud AU Setup – Please remove after setup" → immediate decommission.
- **Certificate expiries: Vevox Dashboard 21 Aug 2026, Vevox 8 Sep 2026.** SSO breaks on those dates.
- Duplicate registrations: Asana ×6-7, Zoom ×3, Wrike ×3, Exclaimer ×3, Canva/Miro/Smartsheet ×2.
- ADAL app "P2P Server (2019)" — ADAL deadline passed Sep 2025. Migrate to MSAL or delete.

## Available tooling in this session

`mcp__Microsoft_365__*` covers Outlook mail and calendar, SharePoint file operations, Teams chat listing, and `get_me`. It does **not** expose Entra directory administration, Intune, Defender, Conditional Access or licence assignment. For those, either use the local `C:\azureintegration` read-only MCP, Graph PowerShell, or the portal. **Do not promise Entra writes from this connector.**

## People

Mathew Hema (Senior Manager ICT; `mathew.hema` + `mathew.hema.admin`, both GA) · Keith Tsui (`admin365.keith`, GA) · Ross James (`ross.james.admin`, GA) · Andrew Dunn (TeamOrgChart admin; only fully-MFA SF sysadmin) · Kate Millar (CEO, org-tree root, intentionally no manager) · Caroline Scales.

Vendors: SXIQ (`sxiq.*` service accounts), Blitzm, Envision CP, Xecurify/miniOrange, Exclaimer, Vevox, TeamImprover (TeamOrgChart+ v2.1.20, deployed org-wide, replaces the blocked Org Explorer).

## Operating rules
1. **Report-only first** on every Conditional Access change, 7-14 days, with a written rollback.
2. **Never blank an Entra field** without checking whether the EH sync will overwrite it back, or vice versa.
3. **Entra writes: approve-then-execute** where the `entra-admin` server is present (desktop); prepare-and-hand-over everywhere else. Always propose the exact change first.
4. Named per-user security-weakness data (who lacks MFA, last logins) is **confidential**. Do not paste it into shared documents or tickets.
5. The security data here is dated 19-30 Jun 2026. Re-verify before asserting current state.
