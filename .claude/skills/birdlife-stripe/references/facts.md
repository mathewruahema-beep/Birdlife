# Stripe: facts

The lookup table for `birdlife-stripe`. **Edit this file first when a value
changes, then the prose.** All accounts are livemode: real donor money.

## Accounts (verified 3 Sep 2026)

| Account | Account ID | Salesforce counterpart |
|---|---|---|
| BirdLife Australia - eCommerce (primary, WooCommerce) | `acct_1PaqQkEdZ08H7Yxq` | miniOrange-synced Opportunities, `stripeGC` |
| Memberships | `acct_1DE94cH9l9pxYNgx` | `AAkPay__*` recurring payments, `Subscription__c` |
| Ausbirdfund | `acct_1DffVqH1WeNbvypj` | NPSP Opportunities, ABF GAU |
| BLP | `acct_1OKucyFMYRhNDz9n` | unmapped |
| eStore / AOC | `acct_1NfHuCCj2I4WmWMH` | unmapped |

Payments2Us gateway "BirdLife MEMBERSHIP Facility" is a separate facility on
the Salesforce side.

## Connector mechanics

| Item | Value |
|---|---|
| Account list | `list_available_accounts_or_orgs` |
| Read | `stripe_api_read({stripe_api_operation_id, parameters, stripe_context: <acct id>, livemode: true})` |
| Operation ids | `GetBalance`, `GetCharges`, `GetRefunds`, `GetPayouts`, `GetBalanceTransactions`, `GetCustomers` |
| Parameter lookup | `stripe_api_details` |
| Search | `stripe_api_search` (e.g. `amount:8400 AND created>1756684800`) |
| Balance shape | `{available:[{amount,currency}], pending:[...]}`, integer cents |
| Write | `stripe_api_write`: never from a page or routine; explicit human approval naming object and amount |
| Console | Money tab sums GetBalance across five accounts every four minutes while open |

## Money chain constants

| Item | Value |
|---|---|
| WooCommerce sales | ~A$11,108.70/month |
| Orders (Jul 2026) | ~6,466: 6,331 completed, 70 refunded, 60 failed |
| Bank clearing | 1 to 3 business days into NetSuite `118636581` |
| SF Stripe package | `stripeGC` (Account, Connected Account, Event, Webhook Endpoint, Sync Log); flow `[Stripe] aCU Opportunity - Get Balance Transaction` |
| Refund in SF | new positive Payment, `Paid = false`, Type `shop_order_refund`; StageName raw `refunded` |
| Recommended field | `Stripe_Refund_ID__c` on Payment |
| Open vendor thread | payout webhook, "they owe you" state (Aug 2026) |

## Membership migration constraints

Card tokens possibly reusable (unconfirmed with Blitzm). BECS direct debit
members cannot be migrated; fresh mandate required (open decision Q10).
Existing WooCommerce subscriptions stay active 15 months. Payments2Us
auto-renewals switched off at cutover.
