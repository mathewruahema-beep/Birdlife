---
name: birdlife-netsuite
description: Expert operator knowledge for BirdLife Australia's NetSuite OneWorld ERP — chart of accounts, subsidiary and segmentation model, saved searches, SuiteQL, the Salesforce-to-NetSuite reconciliation, Infinet Cloud/ZonePayroll, the bank reconciliation backlog, OAuth2 certificate risk, and the Business Central migration business case. Use for any task touching GL accounts, journals, vendor bills, bank recs, project or class codes, payroll data, expense reporting, financial reconciliation, or NetSuite reports and searches. Trigger on "NetSuite", "SuiteQL", "GL code", "chart of accounts", "bank rec", "reconciliation", "ZonePayroll", "Infinet", "Business Central", "BC migration", "unreconciled income", or an account number like 11104.
---

# BirdLife Australia — NetSuite

## Account identity — verified

| Fact | Value |
|---|---|
| Account ID | **3440597** (label "BirdLife Australia_090721") |
| Product | Oracle NetSuite OneWorld, release 2026.1, Australia edition |
| Data centre | AP Melbourne |
| Currency / FY | AUD, calendar fiscal year (Jan-Dec) |
| ABN | 75 149 124 774 |
| Subsidiaries (live) | id **2** "Birdlife Australia" · id **-1** "BirdLife Parent (Context)" |

**One operating subsidiary means no intercompany eliminations.** Anyone proposing consolidation logic is solving a problem BirdLife does not have.

Scope: GL, AR/AP, banking (60-90+ bank accounts), fixed assets, project/grant accounting, payroll, AASB 16 lease accounting, JB Were investment tracking (~$8.4M under management), GST/BAS.

## Chart of accounts — the numbers you will actually use

413 accounts, 5-digit blocks (10000 assets … 50000 expenses).

| Account | Meaning |
|---|---|
| **11103** | NAT ABF Donations |
| **11104** | NAT Operations |
| 11003-11159 | ~90 branch-suffixed bank accounts |
| 11200_x | AR by branch |
| 21101-21117 | AP by branch |
| **21103** | PAYG |
| 21124-21199 | NAB credit cards, one per staff member |
| **21304** | Unearned Revenue |
| 12300 / 12301 / 21600 / 22300 | AASB 16 lease accounting, 54 Wellington St Collingwood |
| 41001 / 41002 | Memberships |
| 44013 | Merchandise — **known GST issue, ~$7,224/yr** |
| 44023 | Subscriptions |
| 118636581 | NAT bank clearing account for donations |

## Segmentation — mostly dead weight

- **Department**: 86 active of 114
- **Class** (labelled "Class/Project"): **312 active of 952 — ~67% inactive**
- **Location/Branch**: 36 active of 38. **Three branch-code mismatches: MOR, BUN, SHI**
- **Project/Job**: ~281 active of 831 (~66% inactive); 279 active projects, 12-15 project types

**There is no enforced naming convention.** The Jul 2026 Project Codes Analysis proposes `[PROGRAM]_[FUNDER]_[TYPE]_[FYSTART FYEND]` from FY2026-27, documents 9 structural problems and a 10-step implementation plan. Placeholders `_NOT_SPECIFIED` and `GEN_OVERHEAD` are still active; some projects have no Customer (funder).

## Users and roles

**221 active user-role assignments across 52 roles.** ~160 employees sit on "Birdlife ESS Centre_No projects".

Admins: **BLA362 Mathew R Hema**, **BLA100 Claudia L Abad** (Finance Manager), **BLA058 Infinet Cloud Support**. External logins: Infinet Cloud, Fusion5, RSM Audit (role "CEO Hands-Off"), ICS Support.

**Segregation-of-duties risk:** four role templates carry excessive GL/bank/journal rights — BirdLife Accountant National Office, EP Configurator, EP Processor, and the Payroll Administrator/Processor family (×11). Flag these in any access review.

## Customisation and controls

**470 scripts, 450 from vendor bundles, only 20 custom** — 7 prefixed `F5:` (Fusion5) and 13 prefixed `SF:` (custom NAB bank-feed connector using PGP/SSH).

**7 workflows (5 custom)**, including Vendor Invoice Approval, which **auto-approves no-PO bills entered under the Bookkeeper-Branches role**.

**Native Approval Routing is switched OFF for all 7 transaction types.** Control depends on manual status changes plus that one workflow. This is the weakest financial control in the system and it should be stated plainly in any audit conversation.

## Reporting

**212 saved searches — 115 have never been run, 46% are owned by the Fusion5 Support login, only 43 were run in 2026.** 34 saved custom reports including duplicates and searches literally named "test" and "test1".

Search owners of note: Cat Stewart, Stacy Gurrie, Bruce Potgieter. Branch bookkeeper roles: Sue Siwinski (BLA015), Graeme Sheppard (BLA089). Reporting PMs: Pamela M Fallow (BLA069), Jonathon C Wilson (BLA099).

Data volume: **587,260 GL journal lines back to Dec 2016**; vendor bills back to Jul 2017.

**Use `ns_listSavedSearches` and `ns_listAllReports` before building anything new.** Half the reporting estate is abandoned; adding to it without pruning makes the problem worse.

## SuiteQL — the fastest honest answer

`ns_runCustomSuiteQL` with `ns_getSuiteQLMetadata` is the right tool for reconciliation and analysis questions. Prefer it over saved searches for ad-hoc work: it leaves no artefacts behind in an already-cluttered saved-search library. Always scope to subsidiary id 2 unless you specifically want parent context.

## Integrations — there are essentially none

Only **2 formal integration records** (Default Web Services; SuiteCloud Development Integration) and **1 active access token**. A bundle audit (212 events, 7 bundles) confirms **no CRM, fundraising, donor or BI integration exists in NetSuite at all**.

- NAB bank feeds run through the custom `SF:` scripts.
- EFT payments through the Electronic Bank Payments bundle.
- **Payroll runs entirely in NetSuite** via Infinet Cloud Payroll ("ZonePayroll"), SuiteApp bundle `30500` v`26.3.03`, with STP reporting to the ATO. **~128 staff, one pay run.**
- **There is no live Employment Hero ↔ NetSuite link.** Employee and pay data is maintained twice. This is described in the knowledge base as the biggest data-integrity risk in the entire landscape. Match key for any future link is the **worker code BLA###**.

## Salesforce → NetSuite reconciliation

**The mechanism is a manual monthly CSV export from Salesforce imported by Finance. There is no real-time API integration.** Anyone who says "the systems are integrated" is wrong.

Flow: web orders (WooCommerce) → SF Opportunities → NS sales invoices. Donations → SF → NS bank deposits/income. Memberships → NS 41001/41002. Recurring donations and direct-debit batches → NS bank receipts. **SF GAU allocations map to NS GL codes.**

Structural timing gap: the Stripe webhook creates the SF Opportunity, but the bank clears **1-3 business days later** into account 118636581. SF Close Date and NS posting date never align. Proposed policy (Option A): SF Close Date plus a NetSuite +3-business-day month-end window, effective 1 Aug 2026.

**Unreconciled income as at 3 Jul 2026: $671,117.07 across 2,878 records — growing roughly $87K/day** (it went from $409,202 on 29-30 Jun to $671,117 on 3 Jul). Finance Net Income $6,234,694.64, of which reconciled $5,563,577.57.

**The exception report exists and is not running.** Zapier Zap ID **371228125** "Unreconciled Income Exception Report": Tue & Fri 12:00 AM AEST → SF Find Records (report `00ORF0000033T6z2AE`, unreconciled Opportunities, last 7 days) → NetSuite Find Records (account 3440597, TBA, ±3-business-day matching) → HTML exception table emailed to mathew.hema@birdlife.org.au. **Status: DRAFT, never published.** Publishing it is the single cheapest win in the finance stack.

Seven documented discrepancy causes: (1) close-date vs bank-posting-date lag; (2) memberships 41001 and subscriptions 44023 sit outside fundraising scope; (3) **Major Donor double counting — tiles are independent queries, $9,089 gap, ~$37,500 confirmed double-counted**; (4) GST on merchandise GL 44013 ~$7,224/yr; (5) unreconciled income; (6) no GL-to-programme mapping (now built, Section 7 of the Master Technical Guide); (7) Tax Appeal MD gifts intentionally excluded.

## Bank reconciliation — the standing red flag

**11104 NAT Operations: 378 unmatched items. 11103 NAT ABF Donations: 120 unmatched items. Both last reconciled 31 March 2022.** Over four years.

This is an urgent control risk independent of any migration decision, and it is a **mandatory precondition of the Business Central migration**. Do not let a BC conversation proceed as though this can be cleared during cutover.

## OAuth2 certificate — orphaned credential, dated expiry

| Fact | Value |
|---|---|
| Type | OAuth 2.0 Client Credentials (M2M) on SuiteCloud Development Integration |
| Certificate ID | `7SCEnbQf6XYE-nv-8z_q0oWmPNm3RM5aCWD7A2WSklo` |
| Created | 28 Oct 2024 |
| Valid | 17 Sep 2024 → **expires 17 Sep 2026** |
| Revoked | No |
| Linked entity | BLA216 Rachel Munt — **departed** |
| Created by | Matej Fucek — **departed** |
| Activity | **Zero recorded activity across SOAP, REST, RESTlets and AI Connector** |

The integration record has been unchanged since 25 Jul 2024. Recommended sequence: confirm with IT and the NetSuite partner that no infrequent scheduled job depends on it, then **revoke first, monitor, then delete**. Prepared for CFO David Thompson 20 Jul 2026. **No action taken yet.**

For the Zapier path a second credential set is needed and does not exist: **Token-Based Auth** — integration record plus consumer key/secret and token ID/secret, user Mathew Hema, Administrator role.

## Business Central migration — advisory, not decided

Two consultant documents recommend migrating to Microsoft Dynamics 365 Business Central: the BC Migration Business Case (Jul 2026, status "Pre-Implementation Advisory") and the NetSuite System Review (10 Jul 2026).

Claimed saving **>$100k/yr** on licensing (BC tiers: Team Member ~$8-10, Essentials $80, Premium $110 per user per month, against 160 employees / 221 role assignments). **That saving is unverified — there is no vendor quote on file and no signed decision.** Treat the number as a vendor-side claim until quoted.

Conditions attached to the recommendation: vendor-backed licensing quote; finance and payroll team interviews; Class/Project data cleanse; early Infinet Cloud and Fusion5 engagement for payroll; remediation of the 4 flagged role templates; full volume extraction; rebuild of only confirmed-active searches and reports; rebuild of the 20 custom scripts and 5 workflows as BC extensions.

Recommended shape: **Employment Hero as the payroll platform under BC**, phased not big-bang, **no historical transaction migration** (archive to SharePoint), Power BI from day one.

Pre-migration cleanup list: clear and document credit cards 21124-21199 and Unearned Revenue 21304; cleanse Class/Project; clear the bank rec backlog.

## Mathew's three stated NetSuite goals

1. Salesforce-to-NetSuite reconciliation
2. An Employment Hero payroll integration process
3. Expense reporting out of NetSuite

Note that **Expense Categories are empty in Employment Hero** and NetSuite's expense role templates are among the four flagged for excessive rights. Any expense reporting design has to resolve both.

## People

Mathew Hema (BLA362, admin) · Claudia L Abad (BLA100, Finance Manager) · David Thompson (CFO) · Rachel Munt (BLA216, departed) · Matej Fucek (departed) · Cat Stewart · Stacy Gurrie · Bruce Potgieter · Sue Siwinski (BLA015) · Graeme Sheppard (BLA089) · Pamela M Fallow (BLA069) · Jonathon C Wilson (BLA099). Credit-card holders named in the audit: Jessica Rooke, Darren Quin, James Johnson.

Partners: Infinet Cloud (payroll), Fusion5 (implementation, owns 46% of saved searches), RSM (audit), JB Were, NAB.

## Operating rules
1. **Scope every query to subsidiary id 2** unless parent context is genuinely wanted.
2. **Use SuiteQL for analysis; do not add saved searches** to a library where 115 of 212 have never been run.
3. **Never quote the >$100k BC saving as fact** — it is an unquoted vendor claim.
4. Reconciliation questions must state the SF-vs-NS date basis being used, because the two never align.
5. NetSuite is not on this project's originally approved connector list. It was added Aug 2026. Flag that when writing anything governance-facing.
