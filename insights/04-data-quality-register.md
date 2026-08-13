# Data Quality Register

Every known defect that corrupts a metric, in one place. Dashboard builders check
this register; each affected metric in the catalog cross-references a `DQ-##`.
A defect leaves this register only when the fix is verified, and the fix date is
annotated on any metric series it bent.

Status as at Aug 2026.

| ID | Defect | Corrupts | Workaround in the model | Fix (owner) |
|---|---|---|---|---|
| DQ-01 | miniOrange Woo→SF sync fails ~10.3–10.5% of attempts (FLS gap on `npe01__Opportunity__c`, both envs) | Fundraising income, order↔gift counts | Report Woo-vs-SF delta as a sync-integrity metric | Grant FLS to integration user on every synced field (ICT / Karishma) |
| DQ-02 | SF-Id write-back gap — paid orders left with "Salesforce UUID: None", next status change duplicates | Gift counts, duplicate rate | `sf_writeback_ok` flag on `fact_order`; exclude+count | Deliberate write-back test per mapping (test MO-05) |
| DQ-03 | Refund flow broken: refunds create **positive** Payments, invalid stage strings `"refunded"/"cancelled"`, Stripe `re_xxx` not synced, subscriptions never deactivated | Income, refund rate, member counts | Normalise to negative with `is_refund_defect`; refund truth from Stripe only | Karishma Week-4 decision gate: fix or formally accept. Add `Stripe_Refund_ID__c` |
| DQ-04 | SF number fields default 0 — `!= null` population reads are false (BetterImpact_ID__c: reads 479,613, truth **1**; `AAkPay__Member_Type__c` reads 100%, is 100% blank) | Any population/coverage metric | Mandatory `!= null AND != 0` or row sampling in every canonical query | Query discipline — enforced in `sql/extraction-queries.md` |
| DQ-05 | Regular giving split across NPSP Recurring Donations (1,778) and AAkPay Recurring Payments (392) | Regular-giving count & value | `fact_recurring_agreement` is a mandatory union | Converges when P2U decommissions — annotate the series break |
| DQ-06 | `Active_BL_Member__c` maintained by Payments2Us (decommissioning); Emu journal access depends on it; new `Membership__c` build has not taken it over | Active members, journal eligibility | Flag on every membership tile during migration | Membership rebuild scope (Blitzm/Karishma) — documented nowhere else, keep loud |
| DQ-07 | Major Donor dashboard tiles are independent queries — $9,089 gap, ~$37,500 confirmed double-counted | Major-gift income | Single shared query for related tiles | Rebuild tiles off `fact_gift` |
| DQ-08 | Unscoped Case reports count all 19 record types (4,344 vs 20 open) | Every ICT metric | `RecordType.DeveloperName = 'Zeus'` in every case query | Add filter to the 10 reports (runbook in root README) |
| DQ-09 | Duplicate supporters: Raisely/API writes bypass UI duplicate rules; historical dupes | Retention, donor counts, avg gift | Household grain + measured duplicate rate | Plauti daily merge job + merge discipline |
| DQ-10 | Raisely campaign → single SF Campaign; online gifts code to top-level appeal | Campaign attribution/ROI | `attribution_grain` column; tile caption | Donor Segment field proposal (Fundraising + MoveData) |
| DQ-11 | Conga receipting: CMQ-0008 hardcodes FY `'25f'`; EOFY contact button deleted; regenerate would break live batch | Receipting SLA, EOFY compliance | Treat receipting metrics as unreliable | Native-SF receipting rebuild, 10-week plan |
| DQ-12 | Staging↔production drift: Woo Members mapping, `Automatic_Renewal__c`, `npsp__Type__c`, dup-detection keys exist only in staging | Auto-renewal rate; sync integrity | State environment on any pre-cutover number | Production deploy re-mapping checklist |
| DQ-13 | NetSuite Class/Project ~67% inactive, no naming convention, `_NOT_SPECIFIED`/`GEN_OVERHEAD` live, some projects lack funders | Programme financials, dept splits | Show `unmapped %` on every org-unit split | FY2026-27 naming convention + cleanse (Finance) |
| DQ-14 | Asana hygiene: ~30 undated open tasks, 25-task block stale 6 months, unactioned auto-prompts | All flow/overdue metrics | Publish hygiene counts alongside flow metrics | Monday hygiene report ("close, delegate, or date it") |
| DQ-15 | EH↔NetSuite payroll dual-entry, no live link; EH→Entra Logic App failing (403); native EH add-on **overwrites, never merges** (blank EH field blanks Entra) | Headcount triangle, onboarding metrics | Triangle mismatch is the published metric | EH permission fix + token-persistence fix; scope add-on to Job Title/Dept/Manager/Location only |
| DQ-16 | Ortto retention limit reached; Lead not synced | Audience size, engagement | Caption the exclusions | Ortto plan decision (renewal 12 Aug 2027) |
| DQ-17 | Stripe payout webhook thread unresolved | Payout completeness | Cross-check payouts against NAB feed lines | Chase Stripe support thread |
| DQ-18 | SF↔NS reconciliation is a manual monthly CSV; 1–3 day bank lag; policy Option A (±3 business days) proposed 1 Aug 2026 | All finance vs fundraising comparisons | Date-basis disclosure on every finance number | Publish Zap `371228125`; needs NetSuite TBA credentials (don't exist yet) |
| DQ-19 | Bank accounts 11104 (378 unmatched) and 11103 (120) last reconciled 31 Mar 2022 | Cash position confidence; BC migration precondition | Ageing metric as standing control alarm | Finance backlog clear-down |
| DQ-20 | `Subscription__c` (unmanaged) name-collides with `AAkPay__Subscription__c`; contains 8 real + 421 test records | Any "subscription" query | Namespace-qualified queries only | Rationalise Keith's object during membership rebuild; reminder-timing conflict (31/7/1 vs Conga-wired 10/37/60) needs James Vilinsky's call |
| DQ-21 | LearnUpon webhook captures enrolment only, not completion; hook owned by keith.tsui's personal Zapier; URL leaked in docs | Training completion | Report enrolment as enrolment, never completion | Tick completion event; rotate hook; transfer ownership |
| DQ-22 | Case Status field-history tracking off | Time-to-acknowledge, time-in-status, SLA | Metric marked "not measurable yet" | Enable tracking (Asana task, Kate Rogerson) |
| DQ-23 | Pardot hard stop 31 Aug 2026 — engagement history lost at uninstall unless exported | Engagement time series | Export before cutover; annotate series break | Pardot decommission project |
| DQ-24 | Better Impact linkage empty (`BetterImpact_ID__c` = 1 contact) | All volunteer metrics | Volunteering reports readiness metrics only | BI implementation + ID backfill |

## Register discipline

- **New defect found while building a metric → add it here first**, then caveat
  the metric. Never ship a silently-corrected number.
- Fixes bend series: when DQ-03 is fixed, refund-inclusive income history changes
  meaning. Annotate the break on the chart, keep the old definition queryable.
- Quarterly review alongside the enterprise-app access review (next 19 Sep 2026).
