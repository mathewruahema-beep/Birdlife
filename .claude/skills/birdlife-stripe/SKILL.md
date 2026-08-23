---
name: birdlife-stripe
description: Operator knowledge for BirdLife Australia's Stripe account — the eCommerce live account, how payments flow through WooCommerce into Salesforce and NetSuite, the refund traceability gap, BECS direct debit constraints for the membership migration, and safe use of the Stripe MCP. Use for any task about payments, charges, refunds, payouts, disputes, subscriptions, webhooks or payment reconciliation. Trigger on "Stripe", "charge", "refund", "payout", "webhook", "BECS", "direct debit", "card token", or a payment discrepancy.
---

# BirdLife Australia — Stripe

## Account — verified live

| Fact | Value |
|---|---|
| Account | **BirdLife Australia - eCommerce** |
| Account ID | `acct_1PaqQkEdZ08H7Yxq` |
| Mode | **livemode: true** |

**This is a live production account handling real donor and member money (~A$11,108.70/month in WooCommerce sales).** Every write is a real financial event. Treat `stripe_api_write` as requiring explicit human confirmation, every time, with no exceptions for "small" amounts.

A separate gateway "BirdLife MEMBERSHIP Facility" exists on the Payments2Us side in Salesforce. Confirm which facility a question refers to before answering.

## Where Stripe sits in the money chain

```
WooCommerce checkout (birdlife.org.au)
   → Stripe (card + BECS direct debit)
      → webhook creates Salesforce Opportunity + npe01__OppPayment__c
         → bank clears 1-3 business days later into NAT account 118636581
            → NetSuite, via a MANUAL MONTHLY CSV EXPORT from Salesforce
```

**There is no real-time Salesforce-to-NetSuite integration.** The 1-3 day bank clearing lag is why SF Close Date and NetSuite posting date never align, and it is the structural driver of the **$671,117 unreconciled income backlog growing ~$87K/day**.

Salesforce holds Stripe objects via the `stripeGC` managed package (Stripe Account, Connected Account, Event, Webhook Endpoint, Sync Log) and flow `[Stripe] aCU Opportunity - Get Balance Transaction`.

## The refund traceability gap — the thing to fix

**Stripe Refund IDs (`re_xxx`) are not synced into Salesforce.** Once a refund is issued, it is untraceable from the CRM side. Combined with the broken WooCommerce refund flow, the effect is:

- Refunds create a **new Payment with a positive amount** in Salesforce, so the ledger shows two positive payments.
- `TotalOrderAmount__c` is unchanged; OpportunityLineItems keep positive values.
- Opportunity StageName is set to the raw WooCommerce string `"refunded"` — not a valid picklist value.
- Partial refunds behave like full refunds.

**Recommended fix on record: add a `Stripe_Refund_ID__c` field on Payment and map it.** Until then, any refund investigation has to start in the Stripe dashboard and be matched back by amount and date, which is slow and error-prone. Say so rather than pretending Salesforce can answer refund questions.

WooCommerce volume for context: ~6,466 orders as at Jul 2026 — 6,331 completed, **70 refunded**, 60 failed.

## Membership migration constraints

- **Card tokens** may be reusable for migrated auto-renewal members. **Unconfirmed with Blitzm** — the new platform may force re-entry.
- **BECS direct debit members CANNOT be migrated.** They must set up a fresh mandate. This is a member-communication problem, not a technical one, and it needs to be in the transition messaging plan (open decision Q10).
- Existing WooCommerce subscriptions stay active 15 months so nobody loses access mid-transition.
- ICT turns off Payments2Us auto-renewals at cutover. **No double-charging across systems** is the hard requirement.

## Known open item

A Stripe support thread on the **payout webhook** was sitting in "they owe you" state as at Aug 2026. If payout data looks incomplete, that thread is the first place to look.

## Available tooling

`mcp__Stripe__*` provides `stripe_api_read`, `stripe_api_search`, `stripe_api_write`, `stripe_api_details`, account info and documentation search, plus an implementation planner.

**Discipline:**
1. `stripe_api_read` and `stripe_api_search` freely — they are safe.
2. `stripe_api_write` **never without explicit, specific human approval naming the object and amount.** Livemode means a mistaken refund or charge is real money out of a conservation charity.
3. Prefer answering reconciliation questions by reading Stripe and Salesforce and presenting the discrepancy, rather than "correcting" either side.
4. Card numbers, tokens and customer PII do not go into documents, tickets or chat summaries.

## Operating rules
1. State the account (`acct_1PaqQkEdZ08H7Yxq`, livemode) at the start of any payment investigation so there is no ambiguity.
2. Any figure quoted from Stripe should be paired with the Salesforce and NetSuite view, because the three rarely agree and the gap is the actual answer.
3. Never assert that a refund is reflected in Salesforce. Verify it.
