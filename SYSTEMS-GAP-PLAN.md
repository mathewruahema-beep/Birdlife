# BirdLife systems gap register & remediation plan

Compiled **23 August 2026** from the nine system knowledge bases (audits 19 Jun – 20 Aug 2026),
the 20 Aug live connector survey, and this repo's dashboard findings. Figures are
point-in-time; re-verify before quoting externally. Named per-person MFA/access
weaknesses are deliberately excluded — they live in the confidential remediation export.

Rendered version (phone-friendly): https://claude.ai/code/artifact/629a76e7-00bf-4a20-bc6a-7585b5f0398c

---

## Deadline radar (as at 23 Aug)

| Date | Days | Item | Owner |
|---|---|---|---|
| 21 Aug | **past** | Vevox Dashboard SSO certificate expired — sign-in likely broken now; renew both certs | Keith / Andrew |
| 13 Jul | **past** | SF release update Transaction Security Policies, still 0% | Jonathon / Keith |
| 31 Aug | 8 | **Pardot hard cutover** — retain `AccountEngagementSync__c`, regression-test 13 triggers, close 4 open decisions | Jonathon / Karishma |
| 1 Sep | 9 | SF release updates: OAuth u/p retirement (**MoveData affected**), instanced URLs, Authorized Email Domains, Profile Filtering | Jonathon |
| 8 Sep | 16 | Second Vevox SSO certificate | Keith |
| 17 Sep | 25 | NetSuite orphaned OAuth2 cert (departed staff, zero activity) — confirm no dependency → revoke → monitor → delete | Claudia (CFO brief prepared) |
| 19 Sep | 27 | Quarterly enterprise-app review — last round's 129 decisions all blank; 18 apps unassigned | Mathew |

## The register

### Money — critical

1. **Unreconciled income detection built but switched off.** $671,117 / 2,878 records at
   3 Jul, then growing ~$87K/day. Zap 371228125 (SF↔NS ±3-day match, Tue/Fri email) is
   DRAFT. *Fix:* create NetSuite TBA credentials (integration record + consumer + token,
   Mathew, Administrator), test, second-person review, publish. Note: **NetSuite and
   Zapier connectors have disconnected from Claude — re-authenticate in claude.ai.*
2. **Bank recs 4 years stale.** 11104 NAT Operations (378 items) and 11103 NAT ABF
   Donations (120 items) last reconciled 31 Mar 2022. Mandatory BC precondition.
   *Fix:* dedicated Finance clear-down project with Claudia.
3. **Refund flow broken end-to-end.** Positive refund Payments, invalid StageName strings,
   Stripe `re_xxx` never synced, `Subscription_Member__c` never deactivated. *Fix:* add
   `Stripe_Refund_ID__c` on Payment + correct the mapping; Karishma's Week-4 gate —
   fix or formally accept, on record.
4. **WooCommerce Subscriptions unlicensed on ~A$11K/month live payments; Memberships
   inactive.** Gates all Blitzm membership work. *Fix:* purchase both licences — delegable
   procurement, this week.
5. **miniOrange: ~10% FLS sync failures + write-back gap; no prod duplicate keys.**
   *Fix:* FLS grant on every synced field, prod dup keys; `wc.py sync-check` gives daily
   detection once Woo keys land.
6. **Conga receipting: FY code hardcoded `'25f'`, EOFY button deleted, vendor degraded.**
   Never click "Regenerate Solution". *Fix:* patch FY code + rebuild button now; schedule
   the existing 10-week native replacement plan.
7. **NetSuite approvals effectively off.** Native routing disabled for all 7 transaction
   types; no-PO bills auto-approve under Bookkeeper-Branches; 4 role templates
   over-privileged. *Fix:* enable routing with Claudia; remediate templates; state in audit.

### Identity & access — critical

8. **No tenant-wide MFA; break-glass accounts never created.** ~8% MFA-capable, 116 users
   in 7 days with zero CA coverage, 237-account remediation all Pending. *Fix:* create
   break-glass first → tenant MFA CA report-only 7–14 days → enforce → work remediation
   groups per IT-SEC-001.
9. **WordPress public self-registration → Shop Manager.** One toggle; access to orders +
   customer data; 82,089 PII emails in DB. *Fix:* toggle today. Then: cull 25 admins per
   the decided list, enforce 2FA, remove WP File Manager + phpMyAdmin, update ACF-to-REST,
   stop the public debug log.
10. **Privileged-account sprawl.** 2 shared GA accounts of 6 GAs; 20 privileged Entra
    assignments; 9/14 SF sysadmins no MFA; 23 stale SF sysadmin accounts; bots as SA in CEO
    role node; 2 test accounts active with real credentials. *Fix:* test accounts off this
    week; retire shared GAs; deprovision; phishing-resistant MFA on admins; demote bots.
11. **Four leaked credentials unrotated:** old Woo API keys (routine prompts), miniOrange
    webhook access keys (3 docs), LearnUpon catch-hook URL (docs; runs under Keith's
    account), Raisely access token in a formula field. *Fix:* rotate all, scrub docs,
    new Woo keys as env vars per `woocommerce/README.md`.
12. **Device fleet unprotected.** Win 10 EOL unpatched; Tamper/LSA off; 0/19 ASR; no
    BitLocker/update rings/baselines; compliant-by-default misconfig; compliance not linked
    to CA; CVSS 9.6 Edge CVE on 109/115 devices; no Safe Links/Attachments; auto-forwarding
    allowed. *Fix:* Phase-3 Intune baseline programme (below).

### Data integrity

13. **People data maintained twice; syncs half-broken.** No EH↔NetSuite link (~128 staff
    duplicated — "biggest data-integrity risk in the landscape"). EH→Entra Logic App 0/2,
    blocked on EH 403 + token-persistence defect. Native EH add-on **overwrites** blanks
    into Entra. Legacy Zapier EH sync may still be a second writer. *Fix sequence:* EH
    permission → token persistence → re-run → scope add-on to Title/Dept/Manager/Location →
    confirm Zapier writer off → design EH↔NS on BLA###.
14. **Membership rebuild: SF side Not Built, 45/45 tests Not Tested.** `Active_BL_Member__c`
    landmine (journal access breaks at migration if unowned); reminder-timing conflict wired
    into Conga; BECS members need fresh mandates. *Fix:* staging evidence before acceptance;
    escalate reminder conflict to James Vilinsky; BECS comms into transition plan;
    assign `Active_BL_Member__c` takeover explicitly.
15. **SF→NS bridge is a manual monthly CSV**; date bases never align. *Fix:* exception Zap
    first; confirm Option A (+3-business-day window) adopted; API bridge only after the BC
    decision.

### Process & platform

16. **No offboarding checklist** in the org's biggest ticket category (identity = ~20% of
    cases, 96.5% email intake, no request form). Starter/leaver Power Automate flows already
    designed. *Fix:* implement under approve-only; gating step is admin consent for the
    write-tier app registration.
17. **Edge protection unused.** Cart-flood rule lives at WP Engine (Referer false-positives);
    `/wp-login.php` 50K hits/30d at 67% errors; Cloudflare WAF/rate-limits idle; two CF
    accounts undocumented. *Fix:* move cart + login controls to Cloudflare with an owner
    (dashboard work — MCP has no WAF tools); WP Engine bot mitigation meanwhile; consolidate
    accounts.
18. **Reporting scope + board hygiene + blocked automation.** Ten Zeus reports still
    unfiltered (runbook in README unexecuted); dashboard routine has no connectors attached;
    dashboards in a private folder; Case→Asana blocked on SPF
    (`include:_spf.salesforce.com` — security-reviewed change); ~30 undated Asana tasks;
    3 Blocked items are decision debt. *Fix:* run the runbook; attach connectors; shared
    folder; SPF via security review; "close, delegate, or date it" pass.
19. **Estate clutter.** NetSuite: 115/212 searches never run, ~67% Class/Project inactive,
    naming plan for FY26-27 unstarted. Zapier: 8 Outlook + 9 Excel connections unowned,
    2 Pardot connections stale after 31 Aug. Entra: 18 unassigned apps, 6-7 duplicate Asana
    registrations, an app named "Please remove after setup". *Fix:* fold into the 19 Sep
    review with recorded decisions; prune; treat NS cleanse as the BC precondition it is.

## The plan

### Phase 1 — while Mathew is away (this week, delegated)

| # | Action | Owner |
|---|---|---|
| 1 | Renew both Vevox SSO certs (one already expired) | Keith / Andrew |
| 2 | Turn off WP "Anyone can register" (or default → Subscriber) | Keith or Blitzm |
| 3 | Disable 2 live-credential test accounts; deactivate WP File Manager + phpMyAdmin | Keith |
| 4 | Drive Pardot cutover checklist to 31 Aug | Jonathon / Karishma |
| 5 | Review 1 Sep SF release updates; test MoveData against OAuth retirement | Jonathon |
| 6 | Purchase WooCommerce Subscriptions + Memberships licences | procurement / Nina |
| 7 | Rotate the four exposed credentials, scrub docs | Keith (hook), Blitzm (Woo + miniOrange) |
| 8 | From a phone: re-auth NetSuite + Zapier connectors; attach SF + Asana to the dashboard routine | Mathew, ~5 min |

### Phase 2 — first two weeks back (Sep)

1. NetSuite TBA credential → test → publish the exception Zap (second-person review).
2. Break-glass accounts → tenant MFA CA report-only → start 237-account remediation.
3. Retire shared GAs; deprovision 23 stale SF sysadmins; MFA on all admins.
4. EH permission fix → token persistence → EH→Entra re-run → scope native add-on → legacy writer off.
5. Woo integration live: keys as env vars, domain allowlisted, morning sync-check un-parked.
6. Hold the refund-flow decision gate with Karishma.
7. Salesforce report runbook; dashboards to shared folder; Status field-history on.
8. 19 Sep app review completed with recorded decisions; 18 unassigned apps decommissioned.

### Phase 3 — the quarter (Sep–Nov)

1. Intune baseline: compliant-by-default fix, compliance→CA, ASR audit→enforce, BitLocker,
   update rings, Win 11 wave, mail hardening. Target Essential Eight ML1.
2. On/offboarding flows live under approve-only (post admin-consent).
3. Finance: bank-rec clear-down; NetSuite approval routing on; role templates remediated.
4. Conga → native receipting phase 1 (FY code patched immediately).
5. Membership: execute all 45 staging tests before further acceptance; reminder conflict and
   BECS comms resolved.
6. Edge controls to Cloudflare WAF with named owner; consolidate the two accounts.
7. EH↔NetSuite payroll link designed on BLA### — prerequisite to any BC decision.

## Decision register (calls, not tasks)

| Decision | Context |
|---|---|
| Business Central migration | >$100K/yr saving is an unquoted vendor claim; preconditions are on this register regardless |
| Refund flow: fix or accept | Karishma Week-4 gate; recommend fix |
| Ortto retention upgrade | Cap reached, blocks expanded sync; tied to Pardot cutover |
| Entra P2 (~A$2.5K/yr) | Buys PIM/risk-CA/access reviews; decide after MFA baseline |
| Zapier WooCommerce paid extension | Only if Zaps need Woo triggers; direct REST covers reads |
| 3 Blocked Asana items | Portal email mismatch, Plauti merge permissions, dup-management ownership — need a meeting |
