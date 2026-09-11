---
name: birdlife-security
description: "BirdLife Australia's security posture, deadline register, identity capability baseline and incident playbooks across the whole estate (Entra/M365, Salesforce, WordPress, NetSuite, Stripe, Zapier, Cloudflare, email authentication, and the Claude estate itself), anchored on ACSC Essential Eight with a SaaS/identity overlay. Use for any security question, posture read, admin or privilege review, MFA or Conditional Access work, break-glass accounts, certificate or credential expiry, phishing or compromise triage, leaked credential handling, access review, enterprise app consent review, Entra licence decisions, audit or board security reporting. Trigger on \"security\", \"posture\", \"Essential Eight\", \"E8\", \"MFA\", \"admins\", \"sysadmin\", \"privileged\", \"PIM\", \"break-glass\", \"Conditional Access\", \"P1\", \"P2\", \"phishing\", \"compromised\", \"breach\", \"leaked key\", \"certificate expiry\", \"access review\", \"consent\", \"Secure Score\", \"incident\", or \"what is due\"."
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

## Identity capability baseline (SC-300)

SC-300 Microsoft Identity and Access Administrator completed 10 Sep 2026
(18 modules, 4 learning path trophies, all module assessments passed). The
syllabus is the reference frame for identity work here, so a gap is stated
against a recognised standard rather than against an internal opinion. Full
document: **IT-SEC-007**.

**The controlling insight: the licence is not the blocker.** Most of the
identity baseline, including both E8 controls where identity is decisive (MFA
and restrict admin privileges), is achievable on the Entra ID P1 licence
BirdLife already holds. P2 buys automation, just-in-time elevation and audit
evidence, not the baseline itself. Never let "we need P2" defer P1 work.

| SC-300 objective | Position | The next concrete step |
|---|---|---|
| Tenant config, branding, custom domains | Have | None |
| Entra roles and assignments | Gap | GA to 4, retire shared `.onmicrosoft.com` accounts, human owner per privileged assignment |
| Administrative units | Gap | Scope a Helpdesk Administrator unit for Andrew Dunn instead of tenant-wide power |
| Users, groups, group-based licensing | Gap | Move licence assignment to groups so joiner and leaver follow membership |
| Custom security attributes | Gap | Carry the IT-SEC-001 no-MFA service account register as attributes, not a document |
| External identities, cross-tenant access | Gap | Restrict guest access to most restrictive; configure inbound and outbound per partner tenant |
| Hybrid identity, Connect, PHS/PTA/SSO | Gap | Replace the expired Google Workspace SAML signing certificate or retire the federation |
| Tenant-wide MFA | Gap | Publish the CA policy in report-only, then enforce |
| Authentication methods policy, passkeys, TAP, CBA | Gap | Migrate off legacy per-user MFA; TAP for onboarding and recovery |
| SSPR, password protection, smart lockout | Gap | Password Protection in audit mode then enforce; confirm SSPR coverage before MFA enforcement |
| Conditional Access design and controls | Gap | Close out the report-only SharePoint external-sharing policy either way |
| Session controls, sign-in frequency, CAE | Gap | Enable CAE; sign-in frequency on privileged roles |
| Device-enforced restrictions | Gap | Compliance state is not linked to CA, so compliance controls nothing |
| ID Protection risk policies | Blocked by licence | P2 |
| Global Secure Access | Blocked by licence | Separate licensing, not near-term |
| Managed identities and service principals | Gap | Estate runs on stored secrets and certificates; see the deadline register |
| App registrations, API permissions, consent | Gap | Restrict user registration and consent, enable the admin consent workflow |
| Enterprise app integration and SSO | Gap | 129 apps, every decision field blank |
| Defender for Cloud Apps, OAuth app policies | Blocked by licence | Named blind spot, never claim coverage |
| Entitlement management, access packages, ToU | Blocked by licence | P2 |
| Access reviews | Blocked by licence | Keep the quarterly review manual but evidenced |
| Privileged Identity Management | Blocked by licence | Largest single gap; strongest P2 argument |
| **Break-glass / emergency access accounts** | **Gap, NOT blocked** | **Free, under an hour, highest priority. Must exist before tenant-wide MFA enforcement** |
| Sign-in, audit, provisioning log analysis | Gap | No diagnostic settings, so logs age out and cannot be queried with KQL |
| Workbooks, Identity Secure Score | Gap | Secure Score 48.19% (Jun 2026, re-verify); work improvement actions by points per hour |

### Reference facts worth not re-deriving

- Entra roles are directory roles, separate from Azure RBAC. A Global Admin
  elevating to root scope Azure RBAC is an auditable event and should be alarmed.
- Method strength order: passkeys/FIDO2 and certificate-based auth are phishing
  resistant; Authenticator with number matching is strong; SMS and voice are
  weakest. Security questions are SSPR only, never MFA. Password cannot be disabled.
- Temporary Access Pass is the correct tool for onboarding and lost-device recovery.
- Password hash sync needs the least infrastructure, then pass-through auth,
  then federation. Microsoft's direction is away from AD FS.
- Security defaults and Conditional Access are mutually exclusive. Once any CA
  policy exists, coverage is entirely yours to prove.
- Application object is the global definition; service principal is the local
  instance that holds permissions. Delegated permissions act as the user,
  application permissions act with no user present.
- System-assigned managed identities live and die with their resource;
  user-assigned ones are independent and shareable. Either removes a stored secret.
- Deleted Entra users are recoverable for 30 days. Group-based licence changes
  apply within minutes of a membership change.
- Licence errors: CountViolation means buy or free licences; MutuallyExclusiveViolation
  means remove conflicting service plans; LicenseAssignmentAttributeConcurrencyException
  is transient and Entra retries it.

## Entra P1 against P2: the licence decision

**Available on P1 today and currently unused:** tenant-wide enforced CA MFA
with report-only staging and What If; Authentication methods policy, passkeys
and FIDO2, Temporary Access Pass, certificate-based auth, Windows Hello for
Business; SSPR, Entra Password Protection with a custom banned list, smart
lockout; named locations, device filters, session controls, sign-in frequency,
continuous access evaluation; break-glass accounts with sign-in alerting;
administrative units; group-based licensing; custom security attributes;
cross-tenant access settings; restricting user app registration and consent
plus the admin consent workflow; diagnostic settings to Log Analytics;
Identity Secure Score.

**Only P2 delivers:** PIM (eligible rather than standing assignment, time-boxed
and approved elevation, access reviews of directory roles); ID Protection user
and sign-in risk policies; automated access reviews; entitlement management and
access packages with external user lifecycle; workload identity risk.

**Standing position.** Do the P1 work first. Build the P2 case on access
reviews and audit evidence, not on PIM alone, because the recurring cost P2
removes is Mathew's own time running manual reviews and reconstructing evidence
for audit. The `~A$2,500/yr` figure in circulation is an estimate, not a
quotation: replace it with a current Microsoft nonprofit price against the real
licensed user count before it goes near a budget submission, and never quote it
as fact meanwhile. The decision is not made until a dated ADR exists, of type
Decision if P2 is purchased or Risk acceptance if BirdLife knowingly stays on P1.

## Posture register by system

Numbers are point-in-time. State the date when quoting; re-read before
asserting anything is still true.

**Entra ID / Microsoft 365** (detail in `birdlife-microsoft365`)
- Entra ID P1 only. No risk-based CA, no PIM, no automated access reviews.
  "Turn on PIM" is a licence purchase, not a config change. See the section above
  before repeating any price.
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
- Default tenant settings let any user register applications and consent to
  them. Consent phishing needs no password and is not stopped by MFA, so this
  sits behind the MFA work rather than in front of it.

**Salesforce (Zeus)** (detail in `birdlife-salesforce`)
- Health Check 83%, but: 0 trusted IP ranges, 8 objects with public
  external access, guest profiles with Edit on 45 objects, "admins can log in
  as any user" enabled.
- **Admin ratio target is 5% of active internal users or fewer.** Baselines,
  re-run the queries rather than quoting these: 15% (Jun 2026); 12.8% at 12
  active sysadmins over 94 active Standard users (10 Sep 2026). Inactive
  accounts still holding System Administrator: 23 (Jun 2026), 26 (10 Sep 2026)
  and growing. Stale active Standard users with no login in 30 days or never:
  37 of 94 (10 Sep 2026).
- 9 of 14 active sysadmins lacked MFA at the June read; birdbot1/5/6 hold
  System Administrator in the CEO role node. A phishing-resistant MFA CA policy
  for SF admins exists (15 Jun 2026) and covers only those who register.
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
- Salesforce has no PIM either. The SC-300 privileged access doctrine applies
  unchanged: fewer standing administrators, and a recorded reason for each one
  that remains.

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
| **Break-glass accounts created, excluded, alerted and tested** | **15 Sep 2026** | Entra | Mathew |
| Tenant-wide MFA Conditional Access, report-only start | 15 Sep 2026 | Entra | Mathew |
| NetSuite OAuth2 certificate (orphaned) | 17 Sep 2026 | NetSuite | Mathew / CFO |
| Enterprise app review, consent restrictions and admin consent workflow | 19 Sep 2026 | Entra | Mathew |
| SharePoint external-sharing CA policy: enforce or withdraw | 19 Sep 2026 | Entra | Mathew |
| Tenant-wide MFA Conditional Access, enforcement | 29 Sep 2026 | Entra | Mathew |
| Migrate off legacy per-user MFA to the Authentication methods policy | 30 Sep 2026 | Entra | Mathew |
| Global Administrators to 4; owner named per privileged assignment | 30 Sep 2026 | Entra | Mathew |
| Salesforce sysadmin reduction and inactive-admin deprovisioning | 15 Oct 2026 | Salesforce | Mathew / Keith |
| Entra diagnostic settings to Log Analytics | 31 Oct 2026 | Entra | Mathew |
| Helpdesk Administrator administrative unit scoped | 31 Oct 2026 | Entra | Mathew |
| Entra ID P2 quotation and dated ADR (purchase or risk acceptance) | 30 Nov 2026 | Entra | Mathew / CFO |
| Employment Hero sync Graph secret | 5 Jan 2027 | Entra / Key Vault | Mathew |
| Ortto renewal | 12 Aug 2027 | Ortto | Marketing / Mathew |
| entra-admin-mcp certificate | 26 Aug 2027 | Claude estate | Mathew |

Add a row the moment a new certificate, secret, licence or regulatory date is
learned. Rows never get deleted; passed items get a verified outcome.

## Ratios and thresholds to hold the line on

- Salesforce sysadmins: 5% of active internal users or fewer.
- Entra Global Administrators: 4 or fewer, none shared, all phishing-resistant.
- Privileged role assignments: 10 or fewer.
- Break-glass accounts: exactly 2, cloud-only, excluded from every CA policy,
  tested at least every 6 months and after any CA change.
- Stale accounts: no active account without a sign-in for 30 days unless on
  the no-MFA service-account register (IT-SEC-001) with owner and site filled.
- Critical CVE remediation: 48 hours (E8). Anything older is a named breach
  of the SLA in the report.
- Every CA change: report-only 7 to 14 days, written rollback, then enforce.

## Identity playbooks

Procedures, not incidents. All three are Tier 2: a session prepares the exact
steps, a human with Entra admin access executes them.

**Create and test break-glass accounts** (before any tenant-wide CA
enforcement, then every 6 months)
1. Two cloud-only accounts on `onmicrosoft.com`. Not named after any person,
   not synced from on-premises or Employment Hero, no mailbox.
2. Global Administrator permanently on both. This is the one place a permanent
   assignment is correct, because the account exists for when nothing else
   works.
3. Long random passphrases, each split so no single person holds a whole
   credential, stored under physical control in separate locations. Record
   where, in a document that is not itself in the tenant.
4. Exclude from **every** CA policy, verified policy by policy, not by trusting
   a group.
5. Sign-in alert on both so any use is noticed the same day.
6. Test now, before they are needed. Record the date. Retest every 6 months and
   after any CA change.

Failure mode this prevents: BirdLife has one administrator with tenant-wide
identity control. Enforcing MFA without a tested route back in turns a routine
misconfiguration into an outage nobody in the organisation can resolve.

**Conditional Access, report-only to enforced** (every new or changed policy)
1. Confirm break-glass accounts exist, are excluded from this policy and have
   been tested. If not, stop here.
2. Model with What If for a representative user per population, including a
   guest and a service account.
3. Report-only for 7 to 14 days. Under seven days misses weekly and
   fortnightly business processes.
4. Review report-only results daily for the first three days. The question is
   who would have been blocked that you did not expect.
5. Write the rollback before enforcing: which policy, which switch, who can
   flip it, how long it takes. One page.
6. Tell affected people what changes and when. Andrew Dunn is briefed before
   the users, because he fields the calls.
7. Enforce. Watch sign-in logs for the first working day. Record the
   enforcement date against the policy.

**Enterprise application and consent review** (quarterly, and on any new app)
1. Close the front door first: restrict user app registration, restrict user
   consent to low-impact permissions from verified publishers or turn it off,
   enable the admin consent workflow so requests reach ICT.
2. Export the app list with owner, permissions, delegated versus application
   level, and last sign-in.
3. Triage by blast radius, not alphabetically: application-level Graph
   permissions first, then tenant-wide mail or file read, then anything with
   no sign-in in 90 days.
4. Record a decision against every app: keep with named owner, keep with
   reduced permissions, or remove. A blank decision field is the finding.
5. Remove what nobody owns. No owner and no sign-in means unmonitored, not
   unused.
6. Register the review date and the count reviewed. Report the ratio to the
   Board, never the app names.

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
5. Continuous access evaluation is not enabled, so session revocation does not
   take effect until the token expires. Say so rather than implying the
   attacker is locked out at the moment you revoke.

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

## Verification, Tier 2

No administrative connector to Entra exists. Every Entra figure in this file is
a baseline to refresh, not a fact to quote. These are the refresh commands for
an administrator to run; they belong here as commands, never as stored values.

```
Get-MgIdentityConditionalAccessPolicy | Select-Object DisplayName, State
Get-MgDirectoryRoleMember -DirectoryRoleId (Get-MgDirectoryRole -Filter "DisplayName eq 'Global Administrator'").Id
Get-MgReportAuthenticationMethodUserRegistrationDetail -All | Where-Object { -not $_.IsMfaCapable } | Measure-Object
Get-MgServicePrincipal -All | Where-Object { $_.Tags -contains 'WindowsAzureActiveDirectoryIntegratedApp' } | Measure-Object
```

## Reporting cadence

- **Console Security tab**: live admin list, stale counts, deadline board.
  Open it before any security conversation.
- **Security dashboard artefact** (Sunday refresh via the weekend routine):
  the deep view, confidential, `ff6c82e3-38d4-41de-b872-606521972498`.
- **Monthly**: MFA audit re-run; Zapier connection ownership; admin counts.
- **Quarterly**: enterprise app and consent review (next 19 Sep 2026);
  Salesforce sysadmin and inactive-user review; NetSuite role review.
- **Every second quarter**: break-glass account test, date recorded.
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
8. **The licence is not the blocker.** Before saying a control needs P2, check
   it against the P1 list above. Deferring free work behind a purchase order is
   the failure mode that section exists to prevent.