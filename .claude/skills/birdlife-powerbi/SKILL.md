---
name: birdlife-powerbi
description: "Operator knowledge for Power BI and Fabric at BirdLife Australia: the unbuilt 2025 scoping backlog, the Zeus data model traps that make reports lie, the definitions to agree first, Copilot exposure risk, and the Fabric cost position."
---

# BirdLife Australia, Power BI and Fabric

## Capability gap, state this first

**There is no Power BI or Fabric MCP connector in this session.** No tool can list workspaces, read a semantic model, run a DAX query, publish a report, check a refresh, or read the Copilot tenant setting.

When someone asks you to build, publish, inspect or fix a Power BI report, say that immediately and offer the real paths: Power BI Desktop on Mathew's machine, the service at app.powerbi.com, or the Microsoft 365 admin centre for licensing and tenant settings. What a session **can** do is design the semantic model, write the DAX, write the source queries against the connected systems (Salesforce, NetSuite, Stripe, WordPress), and produce the exact click path. That is Tier 2 work. Never imply the report was built.

## Live state, verified 10 Sep 2026

| Fact | Value | Why it matters |
|---|---|---|
| Contacts in Zeus | 482,446 | Import mode is viable. This is not a Fabric-scale problem. |
| Won Opportunities | 642,564 | Refresh strategy matters. Incremental refresh, not full reload. |
| npe03__Recurring_Donation__c, total | 4,762 | See the recurring giving trap below. |
| npe03__Recurring_Donation__c, Open_Ended_Status = Open | **8** | The obvious filter returns 8 records. It is wrong. |
| Existing Power BI content in the tenant | none found in SharePoint search | Nothing to inherit and nothing to break. Greenfield. |
| Power BI or Fabric connector | not connected | See capability gap above. |

Re-run the verification queries below rather than trusting these values.

## The demand already exists, and it is the main risk

`2025 PowerBI scoping doc.docx` (Nadia Watson, OneDrive, last modified 6 Jun 2025) is a live requirements document gathering Power BI demand from six teams: Fundraising and Appeals, Advocacy and Campaigns, Marketing, Participation, LMS and Supporter Care.

It asks for, among other things: real time appeal segmentation and ROI, second and third gift rates, regular giving forecasting, ANOVA and regression on campaign data, GIS by federal electorate, roughly twenty named Aussie Bird Count and e-store dashboards across Google Analytics, Hotjar, Pardot, WooCommerce, NetSuite, Calameo and YouTube, Better Impact volunteer conversion tracking, and Zoom call metrics for Supporter Care.

**Fifteen months later none of it is built.** That is the pattern to name out loud, not repeat. The document is a demand register, not a plan. Treat it as evidence that:

1. The organisation genuinely wants this, so the business case is not the blocker.
2. The scope as written cannot be delivered by an ICT team of four, and attempting it is why nothing shipped.
3. Several requests (Pardot, Account Engagement) are already stale, since Pardot is being decommissioned to Ortto. Never build against a system on the decommission list.

When any of this comes up, the move is: acknowledge the register, pick **one** team and **one** question, ship it, then widen. Say the register will be worked down in order, not in parallel.

## The definitions problem, which is upstream of every dashboard

Four terms resolve differently across Zeus, NetSuite, WooCommerce and Ortto. Until they are agreed in writing, every report is arguable and will be argued with:

- **Active member.** WooCommerce subscription status, Salesforce membership record, or paid-within-12-months.
- **Active supporter.** Any Contact, any Contact with an engagement, or any Contact with a gift in a window.
- **Net donation income.** Gross, minus refunds, minus fees, and whether the non-tax-deductible portion is included. The scoping doc explicitly asks to filter this both ways, which means the model must carry both, not pick one.
- **Reporting period.** Financial year to 30 June, calendar year, or appeal period. Finance and Fundraising do not currently mean the same thing.

This is the analytics engineer role, and BirdLife does not have one. Mathew is it by default. The output is a one page definitions note signed off by Finance and Fundraising, dated, before modelling starts. One meeting, not a project.

## Data model traps in Zeus, verified

**Recurring giving is not in the NPSP recurring donation object.** 4,762 records exist but only 8 carry `npe03__Open_Ended_Status__c = 'Open'`. Anyone building a regular giving report on that filter reports 8 active regular givers and is wrong by orders of magnitude. Regular giving at BirdLife runs through **Payments2Us**. Confirm the live object and status field with `getObjectSchema` before writing a single measure, and record what you find here.

Other traps carried from `birdlife-salesforce`, all of which surface as wrong numbers in a visual:

- **Household account model (NPSP).** Contact to Account is not a simple lookup. Counting Accounts is not counting supporters, and rolling gifts to Account double counts across household members.
- **Duplicates.** The duplicate remediation programme (IT-SF-014, IT-SF-015) is live. Any supporter count is an over-count until dedupe completes. Say the number is an upper bound; do not present it as exact.
- **Two income paths.** Raisely and MoveData, and WooCommerce and miniOrange, both land Opportunities. A channel dimension has to be built deliberately or channel reporting is fiction.
- **Refund traceability.** Stripe refunds do not cleanly trace back to the originating Opportunity. Net income measures must state this limitation on the report page, not hide it.
- **Salesforce to NetSuite reconciliation is unresolved.** A Power BI report showing both side by side will surface the variance in front of the Board. That is a good thing if it is deliberate and briefed, and a career-limiting surprise if it is not. Brief the CFO before publishing anything showing both.

## Architecture, and the Fabric answer

Start with **Power BI Pro and import mode over the Salesforce connector**. At 482k Contacts and 642k Opportunities this is comfortably within import limits with incremental refresh, and the Pro licence is largely already held through the Microsoft 365 estate.

**Do not propose Fabric.** Fabric requires an F SKU capacity charged by the hour on top of licensing. Nothing in the scoping register requires OneLake, Direct Lake, lakehouses or Data Factory that Pro plus a gateway cannot deliver. Fabric belongs in the ICT Strategy 2027-2029 as a costed option with a named trigger, most plausibly when Birdata or Aussie Bird Count app volumes need real-time, or when a genuine multi-source warehouse is funded. If Fabric is raised, the answer is not no, it is: here is the trigger, here is the cost, here is what we do until then.

Workspaces are the permission boundary. One workspace per domain (Fundraising, Finance, Participation), distributed through a **published app**, never through workspace access and never through per-item sharing. Workspace roles are admin, member, contributor and viewer. This also gives a clean line for the Essential Eight access review.

## Copilot exposure, decide before publishing

Copilot in Power BI is **on by default** at tenant level, and the standalone experience can query any semantic model the user can reach, not just the report they have open. At BirdLife that means an unprepped model reachable by a fundraising or marketing user becomes a natural language interface to 482,446 supporter records and their giving history.

Therefore, before the first publish:

1. Confirm the Copilot tenant setting in Admin portal, Tenant settings, and record it.
2. Decide Copilot scope by security group, not organisation-wide.
3. Run **Prep data for AI** on the semantic model, not the report: simplify the schema (hide every ID column), add verified answers for the questions leadership actually asks, and write AI instructions carrying BirdLife context (end of financial year income spike, Aussie Bird Count seasonality, what "member" means).
4. Mark the model **Approved for Copilot** in the service, previously called Prepped for AI.
5. Row-level security is mandatory the moment donor or supporter detail reaches a non-finance audience.

Treat Power BI workspace permissions as a data exposure control and pair the decision with `birdlife-security`.

## The build path, one slice at a time

| Step | What | Tier | Proof it worked |
|---|---|---|---|
| 1 | Definitions note agreed and signed by Finance and Fundraising | 1 | Dated one pager |
| 2 | Confirm Power BI Pro licence coverage and the Copilot tenant setting | 2 | Both recorded |
| 3 | Confirm the real Payments2Us recurring object and active status field | 1 | `getObjectSchema` output, recorded in this skill |
| 4 | One semantic model, star schema, over Salesforce membership and giving | 2 | Two independently built figures reconcile |
| 5 | One report, descriptive only, one audience | 2 | Numbers match a manual Salesforce report to within rounding |
| 6 | Publish to a domain workspace, distribute as an app | 2 | Named audience opens it, others cannot |
| 7 | Prep data for AI, then decide Copilot exposure | 2 | Model marked Approved for Copilot, decision recorded |

Only after step 7 does anything from the scoping register get picked up, one team at a time.

## Verification queries, run these before asserting anything

```sql
-- supporter base, upper bound until dedupe completes
SELECT COUNT(Id) FROM Contact

-- giving volume, sizes the refresh strategy
SELECT COUNT(Id) FROM Opportunity WHERE IsWon = true

-- the recurring giving trap, prove it before modelling
SELECT COUNT(Id) FROM npe03__Recurring_Donation__c
SELECT COUNT(Id) FROM npe03__Recurring_Donation__c WHERE npe03__Open_Ended_Status__c = 'Open'

-- income by channel, only valid once the channel dimension is agreed
SELECT COUNT(Id), SUM(Amount) FROM Opportunity WHERE IsWon = true AND CloseDate = THIS_FISCAL_YEAR
```

Never record a new figure in this skill. Record the query.

## People impact, state it in every recommendation

- **Keith Tsui**, junior Salesforce developer. Gains the most. Salesforce query and data model work transfers directly to semantic modelling and gives him a path beyond Case work. Costs roughly half a day a week during steps 3 and 4, out of his existing queue, not on top of it.
- **Nina Lewis**, finance link. Required at steps 1 and 5. Without Finance validating the numbers the report is an opinion. Agree the time with her; do not assume it.
- **Andrew Dunn**, level 1. Brought in at step 6 so "I cannot see the report" does not escalate every time.
- **Karishma Soni**, external Salesforce developer. Deliberately not required. Outsourcing this moves the capability out of the team.
- **Nadia Watson and the six requesting teams.** They get one report, not twenty. Say so up front. This is the single highest-value sentence in the engagement, because the alternative is the 2025 outcome.
- **Executive and Board.** No Fabric spend is committed. Any report showing Salesforce and NetSuite together is briefed to the CFO before it is published.

## Operating rules

1. **Declare the connector gap** the moment a build, publish or inspect request arrives. Design and DAX yes, execution no.
2. **Definitions before dashboards.** Refuse to model until the four terms are agreed, and say why.
3. **Never filter regular giving on `npe03__Open_Ended_Status__c = 'Open'`** without proving the count first. It returns 8.
4. **Never build against Pardot or Account Engagement.** It is being decommissioned to Ortto.
5. **Supporter counts are an upper bound** until duplicate remediation completes. Say so on the visual.
6. **Fabric is a costed future option, not this year's project.** Give the trigger and the cost, never a flat no.
7. **Copilot exposure is decided before the first publish**, by security group, with the model prepped and RLS in place.
8. **One session, one shippable slice.** The 2025 register is the evidence for why.
9. **Next learning step** is the Microsoft Learn path "Model and visualise data with Power BI", which covers the star schema and DAX gap. The foundation path does not.

Skill authored 10 Sep 2026 from the Microsoft Learn path "Get started with Microsoft data analytics" plus live verification against Zeus and SharePoint. Companion document: IT-CAP-001.