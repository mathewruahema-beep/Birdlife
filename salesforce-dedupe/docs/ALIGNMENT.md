# Plauti ↔ Salesforce duplicate-rule alignment

Everything below was read from **production** (`birdlifeaustralia.my.salesforce.com`)
on **20 Aug 2026** via the API — not from documentation or memory. Plauti scenario
definitions come from the `dupcheck__scenarioData__c` snapshots the Duplicate Check
jobs store; native rules from the `DuplicateRule` object.

## 1. Live Plauti scenarios (the rule set this package mirrors)

| Scenario | Plauti Id | Object | Fields (method @ weight) | Threshold | Used by job |
|---|---|---|---|---|---|
| **Name and Email - Exact** | `a4pI80000008zqjIAA` | Contact | FirstName EQUAL@100 · LastName EQUAL@100 · Email EQUAL@100 | 75 (DEDUP) | **Clone: Daily Contact Merge** (also runs on INSERT) |
| Contact Fuzzy | `a4pI80000008yrnIAA` | Contact | LastName PERSON_NAME@100 · FirstName PERSON_NAME@90 · AllEmail__c COMPANY@80 · AllPhone__c COMPANY@60 | 75 (DEDUP50) | Clone: Contact Fuzzy |
| First Name and Email and Phone | `a4pI8000000BlplIAC` | Contact | FirstName FUZZY_PERSON@50 · AllEmail__c COMPANY@100 · AllPhone__c COMPANY@100 | 75 (DEDUP50) | Clone: First Name, Email and Phone |
| All Email | `a4pRF0000000CsPYAU` | Contact | AllEmail__c EMAIL_EXACT@90 | 75 (SEARCH; runs on INSERT/UPDATE/FLOW) | All Email, Clone: Contacts with Portal Users / Active Memberships / Active Programs / New Contacts |
| Email Exact | `a4pI80000009lj1IAA` | Contact | Email EQUAL@100 | 100 (SEARCH) | Clone: Active Members, Contacts with RGs |
| Mobile Match | `a4pI80000009s3lIAA` | Contact | AllPhone__c PHONE@100 | 75 (SEARCH) | Phone Match |
| Same Address Different Household | `a4pRF0000000ECfYAM` | Contact | MailingStreet EQUAL@85 · MailingState POSTAL_CODE@60 · AccountId NOT_EQUAL@100 | 75 (DEDUP) | Clone: Same Address not in Same Household |
| Account Name Match | `a4pI8000000AeVFIA0` | Account | Name EQUAL@90 · BillingPostalCode EQUAL@75 | 75 (SEARCH) | Weekly Account Merge |

Every Plauti **auto-process threshold** observed on jobs is **100** — Plauti only
auto-merges perfect scores. This package keeps that bar: only *Name and Email -
Exact* at score 100 is auto-merge eligible, everything else feeds Review.

Recent job outcomes (production, cumulative snapshots): Daily Contact Merge found
1,939 groups / 1,958 duplicates over 3,889 records at score 100; Contact Fuzzy
found 7,017 groups (avg 80); Same Address not in Same Household 16,404 groups
(avg 93) — the fuzzy and address books are *review* books, not auto-merge books.

## 2. Native Salesforce duplicate rules (as of 20 Aug 2026)

| Rule | Object | Active | Notes |
|---|---|---|---|
| NPSP Contact Personal Email Match | Contact | **Yes** | UI-side email matching; aligns with Plauti *Email Exact* |
| MoveData Contact Duplicate Rule | Contact | **Yes** | Governs the Raisely→MoveData API write path |
| MoveData Account Duplicate Rule | Account | **Yes** | Same, Account side |
| Org Account Duplicate Rule | Account | **Yes** | Organisation accounts |
| Household Duplicate Rule | Account | No | Deliberately off (NPSP household model) |
| Name and Household | Contact | No | Superseded by Plauti *Same Address Different Household* |
| Standard Lead↔Contact rules | Lead/Contact | No | Lead not in active use |

**Alignment verdict:** the native active rules are a *subset* of the Plauti rule
set (email-exact only). That is coherent — Plauti is the matching engine, native
rules are the last-line API/UI tripwire — but two gaps matter:

1. **API writes can bypass everything.** Raisely (MoveData) upserts on
   `Raisely_UUID__c` and the miniOrange WooCommerce sync upserts with stored
   record Ids. When the external Id/post-meta write-back is missing, they create
   contacts that only the *nightly* dedupe catches. Prevention belongs in the
   intake integrations (see the duplicate-sources board), detection stays here.
2. **Production miniOrange mappings have no duplicate-check keys** (staging has
   them). Until that is fixed, every WooCommerce "Salesforce UUID: None" order
   creates a fresh contact that this automation must mop up.

## 3. The manual SOP encoded in this package

From the BirdLife dedupe SOP (previously applied by hand in Plauti):

- Contacts require **≥ 2.5 points of identification**, Accounts **≥ 3**, before a
  merge — encoded as `Id_Points__c` per rule and the
  `Contact_Id_Points_Required__c` / `Account_Id_Points_Required__c` settings.
- **Portal-user records must be the merge master**; one active portal user per
  group, others need "Disable Customer User" first — encoded as guardrails
  (`PORTAL_USER_MASTER` / `MULTIPLE_PORTAL_USERS`).
- Financial records on duplicates → escalate — encoded as
  `MULTIPLE_ACTIVE_RECURRING` (blocks) and `HAS_FINANCIALS` (flags).
- Post-merge, check for duplicate active Recurring Donations / Recurring
  Payments / Subscriptions — encoded *pre*-merge: a group with two holders of
  active recurring giving never auto-merges.

## 4. What Plauti does that this package deliberately does not replace

- Real-time UI duplicate prevention (Plauti runs *Name and Email - Exact* on
  INSERT and *All Email* on INSERT/UPDATE/FLOW) — keep Plauti (or native rules)
  for point-of-entry blocking.
- Cross-object Lead→Contact conversion scenarios — Lead is inactive in this org.
- Frequent-word lists and Plauti's proprietary fuzzy internals — this engine's
  PERSON_NAME (exact / initial / edit-distance ≤ 1) is deliberately *stricter*
  than Plauti's, so anything Plauti would score that we cannot reproduce lands
  in Review, never in auto-merge.
