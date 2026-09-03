---
name: birdlife-security
description: BirdLife Australia's security posture, deadline register and incident playbooks across the whole estate (Entra/M365, Salesforce, WordPress, NetSuite, Stripe, Zapier, Cloudflare, email authentication, and the Claude estate itself), anchored on ACSC Essential Eight with a SaaS/identity overlay. Use for any security question, posture read, admin or privilege review, MFA or Conditional Access work, certificate or credential expiry, phishing or compromise triage, leaked credential handling, access review, audit or board security reporting. Trigger on "security", "posture", "Essential Eight", "E8", "MFA", "admins", "sysadmin", "privileged", "phishing", "compromised", "breach", "leaked key", "certificate expiry", "access review", "Secure Score", "incident", or "what is due".
---

# BirdLife Australia: Security

This skill is the security lens over every other BirdLife skill. The system
skills hold the detail; this one holds the posture, the dates, the ratios and
the playbooks, so that a session at 2am has doctrine instead of guesswork.

**Everything in this file is CONFIDENTIAL.** Named accounts, gaps and dates do
not go into tickets, Teams chats, shared documents or any artefact that is not
the Security dashboard or the console's Security tab. Reports quote counts and
ratios, never names, unless the audience is Mathew or the ICT team directly.

## Framework anchor

**ACSC Essential Eight with a SaaS/identity overlay.** Target Maturity Level 1
in 12 weeks and ML2 in 12 months (programme set Jun 2026). The overlay matters
because most of BirdLife's real exposure (Salesforce, WordPress, Google
Workspace, 129 enterprise apps, five Stripe accounts) sits outside what E8 was
built to measure. Any posture statement names both halves.

| E8 control | Position (Jun 2026, re-verify) | The blocker |
|---|---|---|
| Patch applications | Below ML1 | Browser and OpenSSL CVEs on most of the fleet |
| Patch operating systems | ML1 partial | Windows 10 past EOL, Win 11 24H2 not started, no WUfB rings |
| Multi-factor authentication | Below ML1 (~8% capable) | No tenant-wide enforced CA MFA policy |
| Restrict admin privileges | Below ML1 | 6 Global Admins, 20 privileged assignments, LSA and Tamper Protection off, no PIM (P1 licence) |
| Application control | Below ML1 | 0 of 19 ASR rules |
| Restrict Office macros | Below ML1 | Macro ASR rules absent |
| User application hardening | Below ML1 | Email protection presets, WinRM, AutoPlay, Adobe JS, Chrome ADMX |
| Regular backups | Partial | BitLocker policy absent, no independent backup audit |

## Posture register by system

Numbers are point-in-time. State the date when quoting; re-read before
asserting anything is still true.

**Entra ID / Microsoft 365** (detail in `birdlife-microsoft365`)
- Entra ID P1 only. No risk-based CA, no PIM, no automated access reviews.
  "Turn on PIM" is a licence purchase (~A$2,500/yr), not a config change.
- 8 Conditional Access policies; **no tenant-wide enforced MFA**; the
  SharePoint external-sharing block is report-only. 116 users signed in over
  7 days with zero CA coverage.
- MFA-capable 203 of 2,561 (7.9%); remediation list of 237 accounts, all
  Pending since 30 Jun. Monthly MFA audit cadence is overdue.
- 6 Global Administrators against a recommendation of 4 to 5, two of them
  shared `.onmicrosoft.com` accounts. 20 privileged assignments (target 10).
- Break-glass accounts are documented as CA exclusions and **not yet created**.
- Secure Score 48.19%. Tamper Protection OFF, LSA Protection OFF, external
  auto-forwarding allowed, no Safe Links or Safe Attachments.
- 5,422 device vulnerabilities, 200 critical, 122 exploitable. Compliance is
  not linked to CA, so compliance state controls nothing.
- 129 enterprise apps, quarterly review, every decision field blank.

**Salesforce (Zeus)** (detail in `birdlife-salesforce`)
- Health Check 83%, but: 0 trusted IP ranges, 8 objects with public
  external access, guest profiles with Edit on 45 objects, "admins can log in
  as any user" enabled.
- **15% of internal users are System Administrators; target 5% or below.**
  9 of 14 active sysadmins lacked MFA at last read; 23 inactive sysadmin
  accounts not deprovisioned; birdbot1/5/6 hold System Administrator in the
  CEO role node. A phishing-resistant MFA CA policy for SF admins exists
  (15 Jun 2026) and covers only those who register.
- Release Updates 0% actioned. Transaction Security Policies overdue since
  13 Jul 2026. OAuth username-password retirement, instanced-URL retirement,
  Authorized Email Domains and Profile Filtering were due 1 Sep 2026: **now
  past**, verify what Salesforce did on the day and what MoveData did.
- Live posture reads (Zeus-scoped, from the console Security tab):
  - Sysadmins: `SELECT Id, Name, Username, LastLoginDate FROM User WHERE
    IsActive = true AND Profile.Name = 'System Administrator' ORDER BY
    LastLoginDate DESC NULLS LAST`
  - Inactive admins: same with `IsActive = false`
  - Stale users: `IsActive = true AND (LastLoginDate < LAST_N_DAYS:30 OR
    LastLoginDate = null)` counted against all active Standard users.
  - Admin ratio = sysadmins / active Standard-licence users.

**WordPress / WooCommerce** (detail in `birdlife-wordpress`)
- "Anyone can register" ENABLED with default role **Shop Manager**: public
  self-registration into order and customer data. One toggle. Fix today.
- 25 admin accounts, 2FA enforced on none, 20 never logged in; removal list
  agreed and not executed.
- WP File Manager and WP phpMyAdmin active (either is a full compromise path);
  ACF to REST API exposed; WP_DEBUG_LOG writing publicly; 82,089 logged
  emails with PII in the database.
- miniOrange SF→WP webhook access keys leaked in plaintext in three documents.
  Rotation unverified.
- WooCommerce "Read" API keys can write (enforcement gap). Keys were also
  exposed in deleted Claude routine prompts in Aug 2026; rotation **not
  verified done**.

**NetSuite** (detail in `birdlife-netsuite`)
- OAuth2 M2M certificate on the SuiteCloud Development Integration: linked to
  departed staff, zero activity, **expires 17 Sep 2026**. Revoke, monitor,
  delete, in that order, after confirming no scheduled job uses it.
- Native approval routing OFF for all 7 transaction types; a Bookkeeper-
  Branches workflow auto-approves no-PO bills. Weakest financial control.
- Four role templates with excessive GL/bank/journal rights (segregation of
  duties). External logins for Infinet, Fusion5, RSM, ICS.

**Stripe** (detail in `birdlife-stripe`)
- Five livemode accounts. Real donor money. `stripe_api_write` only with
  explicit human approval naming object and amount, never from a page or a
  routine.
- Refund IDs not synced to Salesforce: fraud or error investigation starts in
  Stripe, not the CRM.

**Zapier** (detail in `birdlife-zapier`)
- 17 connected apps, 8 Outlook and 9 Excel connections of unknown ownership.
- LearnUpon catch-hook URL in plaintext in documentation, owned by Keith's
  Zapier account. A webhook URL is a credential.
- The superseded EH→Azure AD manager-sync Zap may still be enabled: a second
  uncontrolled writer into Entra. Check and disable.

**Email authentication and edge** (detail in `birdlife-cloudflare`)
- DMARC `p=reject` but `pct=10`: 90% of spoofed mail is not rejected. Fix is
  `pct=100` after verifying every legitimate sender.
- SPF lacks `include:_spf.salesforce.com`; changing SPF is a domain-wide,
  reviewed, rollback-planned change.
- Cart-flood and `/wp-login.php` brute force (50k hits, 67% error) were
  mitigated at WP Engine, not Cloudflare. The edge controls BirdLife pays for
  are not being used for this.

**The Claude estate itself** (detail in `birdlife-os`)
- Connector credentials for every system above sit in the claude.ai account.
  No credentials in routine prompts, ever; a credential found in a prompt
  means pause the routine, rotate, then fix.
- Write-capable routines name their write surface and caps. The console's
  writes are one record at a time behind approval cards.
- entra-admin-mcp certificate expires 26 Aug 2027 (reminder routine live).

## Deadline register

Compute days remaining at read time. Anything past is a finding, not a date.

| Item | Date | System | Owner |
|---|---|---|---|
| Salesforce Transaction Security Policies release update | 13 Jul 2026 (OVERDUE) | Salesforce | Mathew |
| Vevox Dashboard SAML certificate | 21 Aug 2026 (passed, verify SSO) | Entra | Mathew |
| Pardot hard cutover; `pi__`/`sl_flow` uninstall approval | 31 Aug 2026 (passed, verify) | Salesforce | Karishma / Jonathon |
| Salesforce 1 Sep release updates (OAuth u/p retirement, instanced URLs, Authorized Email Domains, Profile Filtering) | 1 Sep 2026 (passed, verify MoveData) | Salesforce | Mathew |
| Vevox SAML certificate | 8 Sep 2026 | Entra | Mathew |
| Tenant-wide MFA Conditional Access target | 15 Sep 2026 | Entra | Mathew |
| NetSuite OAuth2 certificate (orphaned) | 17 Sep 2026 | NetSuite | Mathew / CFO |
| Enterprise app access review (quarterly) | 19 Sep 2026 | Entra | Mathew |
| Employment Hero sync Graph secret | 5 Jan 2027 | Entra / Key Vault | Mathew |
| Ortto renewal | 12 Aug 2027 | Ortto | Marketing / Mathew |
| entra-admin-mcp certificate | 26 Aug 2027 | Claude estate | Mathew |

Add a row the moment a new certificate, secret, licence or regulatory date is
learned. Rows never get deleted; passed items get a verified outcome.

## Ratios and thresholds to hold the line on

- Salesforce sysadmins: 5% of active internal users or fewer.
- Entra Global Administrators: 4 or fewer, none shared, all phishing-resistant.
- Privileged role assignments: 10 or fewer.
- Stale accounts: no active account without a sign-in for 30 days unless on
  the no-MFA service-account register (IT-SEC-001) with owner and site filled.
- Critical CVE remediation: 48 hours (E8). Anything older is a named breach
  of the SLA in the report.
- Every CA change: report-only 7 to 14 days, written rollback, then enforce.

## Incident playbooks

Severity first, then containment, then comms. A session prepares; a human
executes anything Tier 2 (Entra/Exchange admin) or anything that removes a
person's access. Never destroy evidence: no deleting mail, logs, records or
Zaps during triage.

**Phishing report (a Case with Type Troubleshooting or sub-type Phishing Email)**
1. Read the message headers from the Case, not a forwarded copy.
2. Check whether anyone else received it (Exchange message trace: Tier 2,
   prepare the query). Mathew's own habit: "I ran a trace and these are the
   people who received it."
3. If credentials were entered: treat as compromised account (below).
4. Reply to the requester in Mathew's voice (email-voice, register A or B):
   thank them, say what was done, say whether to delete.
5. Close `Closed - Resolved`, set sub-type, note the sender domain for the
   pattern report.

**Compromised or suspected compromised account**
1. Prepare, do not run: revoke sessions, reset password, reset MFA methods,
   review sign-in logs for 30 days, check inbox rules and forwarding
   (auto-forwarding is allowed tenant-wide, so check it every time).
2. If the account holds any admin role, escalate to Mathew immediately.
3. If it has Salesforce access, check `LoginHistory` and recent record edits.
4. Document the timeline in the Case with an internal comment.

**Leaked credential (key, token, webhook URL, password in a document or prompt)**
1. Rotate first, investigate second. Rotation is the only step that closes
   the exposure.
2. Then scrub the document, then search for copies (SharePoint search,
   Teams, Asana, routine prompts, repo history).
3. Register it in `os/registers.md` credential watchlist with status
   "rotation not verified" until someone confirms.
4. Standing examples: WooCommerce keys in routine prompts (Aug 2026),
   miniOrange webhook keys in three documents, LearnUpon catch-hook URL,
   Raisely access token in a formula field.

**Payment anomaly (unexpected refunds, charges, payouts)**
1. Identify which of the five Stripe accounts. Read, never write.
2. Match to Salesforce by amount and date (refund IDs are not synced).
3. Hand to Nina Lewis (reconciliation) and the CFO for any money decision.
4. Card numbers, tokens and customer PII stay out of the write-up.

**Website compromise or flood**
1. WP Engine error rate and `/cart`, `/wp-login.php` hit counts first.
2. Containment lives in WP Engine Web Rules today; propose the Cloudflare
   WAF or rate limit as the durable control and name an owner.
3. If admin compromise is suspected, the Shop Manager self-registration and
   the 25 admin accounts are the first things to check.

**Regulatory note.** BirdLife handles donor and member personal information
under the Australian Privacy Act; a breach that is likely to cause serious harm
triggers Notifiable Data Breach assessment (30 days). Say so early rather than
late; the CEO (Kate Millar) and the Board hear it from Mathew, not from a
technician.

## Reporting cadence

- **Console Security tab**: live admin list, stale counts, deadline board.
  Open it before any security conversation.
- **Security dashboard artefact** (Sunday refresh via the weekend routine):
  the deep view, confidential, `ff6c82e3-38d4-41de-b872-606521972498`.
- **Monthly**: MFA audit re-run; Zapier connection ownership; admin counts.
- **Quarterly**: enterprise app review (next 19 Sep 2026); Salesforce
  sysadmin and inactive-user review; NetSuite role review.
- **Board or exec**: ratios and trend, not names; positives stated (0 risky
  sign-ins, 19 attacks blocked, 0 deleted-user bin) alongside the gaps.

## Operating rules

1. **Confidential by default.** Names and gaps stay in this skill, the
   Security dashboard and the console tab.
2. **Read live before asserting.** Every number here has a date; a posture
   claim without a fresh read is a guess.
3. **Prepare Tier 2, never fake it.** Entra, Exchange, Intune and Defender
   changes are produced as exact PowerShell or click-paths for an admin.
4. **Rotate before you investigate** a leaked credential.
5. **Report-only first** for every Conditional Access change.
6. **One finding, one owner, one date.** A security report line without an
   owner and a date is a wish, not a plan.
7. **Never quote a saving or a maturity level as achieved** until the
   verifying evidence (policy state, sign-in data, scan) is in hand.
