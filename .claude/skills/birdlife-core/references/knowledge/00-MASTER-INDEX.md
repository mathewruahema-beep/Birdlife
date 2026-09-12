# BirdLife Australia — ICT Knowledge Base Master Index

**Generated:** 2 August 2026 · **Owner:** Mathew Hema, ICT Manager
**Source:** full ingestion of 116 documents from the Birdlife OneDrive folder (121 files incl. images/artifacts; 3 corrupted, see below)

## Purpose — read this first (future Claude sessions)

This folder (`Birdlife\Claude\KnowledgeBase\`) is the assistant's persistent knowledge layer. At the start of any BirdLife session, read this index, then the digest for whichever system the task touches. Digests are dense, factual extractions — not summaries of opinion. Dates matter: check the "Current state" sections against today's date before treating anything as current.

## Digest map

| Digest file | Systems covered |
|---|---|
| `salesforce.md` | Salesforce org (prod + staging), ICT helpdesk, membership build, developer onboarding/handover, Conga-in-SF, Pardot decommissioning, Raisely flows, WooCommerce dataflow, Object Data Sync, duplicates/Plauti |
| `security.md` | Azure/M365 security programme, Essential Eight, Defender, Intune, MFA remediation, account hardening, elevated users, access reviews, Salesforce security |
| `people-systems.md` | Employment Hero (incl. Entra sync, payroll migration, TeamOrgChart), Culture Amp SSO, Google Workspace |
| `volunteer-membership-events.md` | Better Impact, Membership rebuild (Blitzm, miniOrange, Payments2Us), Humanitix, Taylor & Francis Emu journal |
| `finance-infra-web.md` | NetSuite (incl. OAuth2 certs, BC migration case), Fundraising dashboards & reconciliation, Conga audit, AWS Birdata middleware, Ortto RDS, WordPress health & cart-flood incident, Asana email rule, ABC2026 |

Companion documents in `Birdlife\Claude\`: `BirdLife_Claude_Connection_and_Knowledge_Plan.docx` (connection strategy, Track A/B) and the Digital Ecosystem Map (PPTX, six layers).

## Environment quick facts

- Salesforce prod: `birdlifeaustralia.lightning.force.com` (Enterprise, NFP Success Pack, instance AUS92) · staging sandbox `birdlifeaustralia--staging` · **70/70 full licences used — zero headroom** · 439 custom objects, ~4,600 reports
- WordPress: prod behind Cloudflare + WP Engine · staging `birdlifestage.wpengine.com`
- AWS account 499522613917 (Birdata middleware, EKS ×2) · Azure tenant + Entra ID · Google Workspace (partially federated: only 171 users on Entra SSO)
- Payroll: NetSuite + Infinet Cloud "ZonePayroll" (~128 staff) · HR: Employment Hero · Finance future state: Business Central (recommended, not yet decided)
- Connected to Claude today: M365, Asana, Confluence, Cloudflare, Zoom, Miro, Stripe, Zapier, NetSuite (needs re-auth), Gmail/GDrive/GCal, Azure+AWS via desktop bridge. Not yet: Salesforce, WordPress. Never: Bitwarden.

## CRITICAL FINDINGS — dated, ranked (as at 2 Aug 2026)

**Immediate (this week):**
1. **Pardot cutover window is open now** — target 15 Aug, hard stop 31 Aug. Blocking decisions unresolved: Ortto retention/billing upgrade (limit already reached — sync blocked), Leads sync scope, 238-vs-287 field discrepancy, uninstall approval.
2. **AWS EKS clusters (prod + staging) passed end of standard support 29 Jul 2026** — accruing extended-support fees, prod upgrade blocked by 2 unresolved insights, deprecated AL2 AMIs.
3. **Plaintext secrets in documentation** — miniOrange webhook access keys (prod `7cf2…`, staging `8d8f…`) printed in three docs; a live Zapier catch-hook URL in another. Rotate keys, scrub docs.
4. **Conga EOFY receipting** — FY code hardcoded `'25f'`, individual EOFY receipt button deleted, batch button URL mismatch. ~50–200 receipts/day depend on Conga.
5. **Salesforce Transaction Security Policies release update deadline passed 13 Jul unactioned**; four more security updates due 1 Sep 2026.

**This month:**
6. **Vevox SAML cert expires 21 Aug 2026** (SSO breakage); Vevox second cert 8 Sep.
7. **NetSuite OAuth2 M2M certificate expires 17 Sep 2026** — and it's orphaned (owners departed). Revoke/replace before expiry.
8. **Unreconciled SF↔NetSuite income $671K and growing ~$87K/day** (3 Jul figure); the exception-report Zap (ID 371228125) is still in draft — publish it.
9. **MFA posture**: tenant 7.9% MFA-capable; 237-account remediation list all "Pending" since 30 Jun; 9 of 14 active SF sysadmins no MFA; AWS root-level admin IAM user no MFA; Google Workspace 348 users no 2SV; Google SAML IdP signing cert EXPIRED.
10. **Refund/cancellation flow materially broken** (staging-verified: positive refund Payments, invalid "refunded" stage, subscriptions never cancelled in SF). Karishma's Week-4 decision gate.

**Structural (schedule):**
11. Windows 10 fleet past EOL, unpatched; Intune has no BitLocker/ASR/baseline policies; CVE-2026-12440 (9.6) exposed on 109/115 devices at review.
12. NetSuite bank recs 4+ years overdue (accounts 11104/11103, last done 31 Mar 2022) — mandatory precondition of BC migration.
13. Membership build: SF side entirely Not Built; 45/45 staging tests Not Tested; WooCommerce Memberships licence lapsed (plugin inactive) blocks Blitzm start; reminder-timing conflict (31/7/1 vs Keith's 10/37/60) must be escalated pre-build; Emu journal eligibility flag (`Active_BL_Member__c`) has no owner in the new build.
14. miniOrange sync failing ~10.4% on prod & staging (FLS on `npe01__Opportunity__c`) + UUID write-back bug → duplicate Opportunity risk.
15. WordPress: public self-registration defaults to **Shop Manager**; 25 admins, zero 2FA; ACF-to-REST-API v3.3.4 known-vulnerable; 31 outdated plugins; unlicensed WooCommerce Subscriptions on live payments (~A$11k/mo Stripe).
16. Employment Hero: default super fund blank / no ATO integration / no e-TFN (compliance exposure); Entra sync Logic App 403-failing (0 succeeded runs); Culture Amp sync contradiction (live-and-ungoverned vs not-yet-built) needs reconciling.
17. Helpdesk: ~3,600 unacknowledged "New" cases (1 Jul); dashboards live only in Mathew's private folder.
18. Knowledge-loss: Arun Nair's DocGen LWC spec + Developer Onboarding System Audit are the two corrupted files — content exists nowhere else; his Apex/Flows were never captured.

## Corrupted source files (recover from OneDrive version history or original author)

- `Salesforce/New Developer/BirdLife_DocGen_LWC_App_Specification.docx`
- `Salesforce/New Developer/BirdLife_Developer_Onboarding_System_Audit.docx`
- `Fundraising/BirdLife_Zapier_Salesforce_NetSuite_Integration_Guide.docx`

## Duplicates / stale versions to clean up

- `Security/MFA Remediation Plan — Birdlife Australia.xlsx` = byte-identical to `MFA Remediation User List.xlsx`
- Two near-duplicate Intune review docs; Defender E8 guide is a re-export of the Defender Security Review
- Dashboard Review 2026: three versions — `_Updated` (5 Jul) supersedes `_v2` and the original
- Membership Test Script v1.0 (30 Jun) superseded by Staging Test Script (31 Jul)
- `Claude/QUICK-REPLAY-GUIDE.txt` is non-BirdLife template content — delete
- Better Impact ActivityTemplates-Review superseded by -v2

## Maintenance

Refresh cycle: quarterly (per the Connection & Knowledge Plan), or immediately after any major system change. To refresh: re-run the ingestion over changed files, regenerate the affected digest, update this index's Critical Findings with current dates. Anything resolved should move to a "Closed" note in the relevant digest, not silently disappear.
