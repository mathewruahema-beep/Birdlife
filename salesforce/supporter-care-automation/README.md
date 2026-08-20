# Supporter Care Automation — Build Package

**Status: BUILT, NOT DEPLOYED, NOT ACTIVE.** All three flows carry
`<status>Draft</status>` — even after deployment they cannot fire until someone
deliberately activates them. Nothing in this package has touched any Salesforce org.

Companion documentation: [`docs/supporter-care-process-and-automation-design.md`](../../docs/supporter-care-process-and-automation-design.md)
(process map, volumes, pattern rationale, benefits — all figures live-queried from
production on 20 Aug 2026).

## What's in the package

| Component | File | Purpose |
|---|---|---|
| `SC Case Intake - Acknowledge and Classify` | `force-app/main/default/flows/SC_Case_Intake_Acknowledge_Classify.flow-meta.xml` | Record-triggered (Case create, after save). Sends instant acknowledgement with case number; keyword-proposes Type + Sub Type for update-details / receipt / unsubscribe enquiries. Guards: General Enquiry record type only (looked up by DeveloperName — no hardcoded IDs), Origin Email/Web, supplied email present, not `Do_Not_Email__c`, not `IsEmailBounce__c` |
| `Update Supporter Details` | `force-app/main/default/flows/Update_Supporter_Details.flow-meta.xml` | Screen flow (Case quick action). Verifies matched Contact, pre-fills current values, warns on NPSP Recurring Donations AND Payments2Us Recurring Payments, routes address changes through the NPSP subflow, sends confirmation, stamps `SC_Additional_Enquiry_Type__c` + `Case_Closed_Reason__c='Closed - Email Sent'` — the existing **Auto close case** flow then closes the case (no new close logic) |
| `SC NPSP Address Change` | `force-app/main/default/flows/SC_NPSP_Address_Change.flow-meta.xml` | Reusable subflow. Creates a new `npsp__Address__c` on the Household Account with `npsp__Default_Address__c=true` — NPSP propagates to all household members; never edits `Contact.MailingAddress` directly |
| Case quick action | `post-activation/quickActions/Case.Update_Supporter_Details.quickAction-meta.xml` | Deployed **separately, after** the screen flow is activated (a Flow quick action can't deploy against an inactive flow) |

All picklist values used (`Closed - Email Sent`, `Update Contact Details`,
`Supporter Information`, `Donation`, `Receipt`, `Supporter Comms`, `Unsubscribe`)
and all object/field API names (`npe03__Recurring_Donation__c.npe03__Contact__c`,
`AAkPay__Recurring_Payment__c.AAkPay__Contact__c`, `npsp__Address__c` mailing
fields, `Do_Not_Email__c`, `IsEmailBounce__c`, `SC_Additional_Enquiry_Type__c`,
`Case_Closed_Reason__c`) were verified against production before authoring —
nothing is invented.

## Deployment (staging first — always)

```bash
cd salesforce/supporter-care-automation
sf org login web --alias staging --instance-url https://birdlifeaustralia--staging.sandbox.my.salesforce.com

# validate only (no deploy):
sf project deploy validate --manifest manifest/package.xml --target-org staging

# deploy the flows (they arrive as Draft — inactive):
sf project deploy start --manifest manifest/package.xml --target-org staging
```

After UAT sign-off, activate in this order (Setup → Flows):
1. `SC NPSP Address Change` (subflow must be active first)
2. `Update Supporter Details`
3. Deploy the quick action from `post-activation/` and add it to the General
   Enquiry Case page layout
4. `SC Case Intake - Acknowledge and Classify` **last** — it emails supporters,
   so activate only after the templates' wording is approved

## Pre-activation checklist

- [ ] Mathew signs off on scope
- [ ] Supporter Care lead (Lee Christian — natural pilot user) validates the
      manual-process description in the design doc
- [ ] Acknowledgement + confirmation email wording approved by Supporter Care
- [ ] Deliverability check from sandbox (sandboxes suppress/redirect email by
      default — Setup → Email Deliverability)
- [ ] Confirm the intake flow's send-from address; consider an org-wide email
      address for `supportercare@` rather than the running user
- [ ] Test cases: bounce case, Do-Not-Email case, no-contact case, household
      with two members (address must follow both), contact with active NPSP RD,
      contact with active Payments2Us recurring payment, email change on a
      contact with an open Plauti duplicate
- [ ] Two-week measured pilot with 2–3 agents before org-wide

## Known design decisions

- **Human-in-the-loop by design.** No flow writes supporter data from inbound
  email content; classification only *proposes* tags. Identity verification
  stays with the agent.
- **Deceased notices are excluded** — sensitive, separate process.
- Screen inputs pre-fill current Contact values, so a blank submit can only
  occur if an agent deliberately clears a field (LastName/Email are required).
- The intake flow's keyword classifier is deliberately simple; revisit once
  Sub Type tagging data improves (today 73% of cases are untagged).
- No changes to assignment rules, queues, record types, or the existing
  `Auto close case` flow.
- Licence impact: none. Runs as existing internal users.
