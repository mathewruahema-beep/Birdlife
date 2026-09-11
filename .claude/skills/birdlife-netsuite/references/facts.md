# NetSuite: facts

The lookup table for `birdlife-netsuite`. **Edit this file first when a value
changes, then the prose.** Financial figures are point in time; state the date.

## Account

| Fact | Value |
|---|---|
| Account ID | `3440597` (label "BirdLife Australia_090721") |
| Product | Oracle NetSuite OneWorld, release 2026.1, Australia edition |
| Data centre | AP Melbourne |
| Currency / fiscal year | AUD, calendar year |
| ABN | 75 149 124 774 |
| Subsidiaries | id `2` "Birdlife Australia" (operating); id `-1` "BirdLife Parent (Context)" |
| Payroll SuiteApp | Infinet Cloud Payroll (ZonePayroll), bundle `30500` v`26.3.03`, ~128 staff, one pay run |
| Integration records | Default Web Services; SuiteCloud Development Integration; 1 active access token |

## Chart of accounts (413 accounts)

| Account | Meaning |
|---|---|
| `11103` | NAT ABF Donations |
| `11104` | NAT Operations |
| `11003` to `11159` | ~90 branch-suffixed bank accounts |
| `11200_x` | AR by branch |
| `21101` to `21117` | AP by branch |
| `21103` | PAYG |
| `21124` to `21199` | NAB credit cards, one per staff member |
| `21304` | Unearned Revenue |
| `12300`, `12301`, `21600`, `22300` | AASB 16 lease accounting, 54 Wellington St Collingwood |
| `41001`, `41002` | Memberships |
| `44013` | Merchandise (GST issue, ~$7,224/yr) |
| `44023` | Subscriptions |
| `118636581` | NAT bank clearing account for donations |

## Segmentation

| Segment | Active / total |
|---|---|
| Department | 86 / 114 |
| Class (Class/Project) | 312 / 952 |
| Location/Branch | 36 / 38 (code mismatches MOR, BUN, SHI) |
| Project/Job | ~281 / 831 |

Proposed naming convention (Jul 2026): `[PROGRAM]_[FUNDER]_[TYPE]_[FYSTART FYEND]`
from FY2026-27. Placeholders still active: `_NOT_SPECIFIED`, `GEN_OVERHEAD`.

## Users and roles

| Item | Value |
|---|---|
| Active user-role assignments | 221 across 52 roles; ~160 on "Birdlife ESS Centre_No projects" |
| Admins | BLA362 Mathew R Hema; BLA100 Claudia L Abad; BLA058 Infinet Cloud Support |
| External logins | Infinet Cloud, Fusion5, RSM Audit ("CEO Hands-Off"), ICS Support |
| Over-privileged role templates | BirdLife Accountant National Office; EP Configurator; EP Processor; Payroll Administrator/Processor family (11) |
| Branch bookkeepers | Sue Siwinski (BLA015), Graeme Sheppard (BLA089) |
| Reporting PMs | Pamela M Fallow (BLA069), Jonathon C Wilson (BLA099) |

## Customisation

| Item | Value |
|---|---|
| Scripts | 470 (450 vendor, 20 custom: 7 `F5:` Fusion5, 13 `SF:` NAB bank feed, PGP/SSH) |
| Workflows | 7 (5 custom), incl. Vendor Invoice Approval (auto-approves no-PO bills under Bookkeeper-Branches) |
| Native approval routing | OFF for all 7 transaction types |
| Saved searches | 212; 115 never run; 46% owned by Fusion5 Support; 43 run in 2026 |
| Custom reports | 34 |
| GL journal lines | 587,260 back to Dec 2016; vendor bills back to Jul 2017 |

## Reconciliation figures

| Figure | Value | As of |
|---|---|---|
| Unreconciled income | $671,117.07 across 2,878 records, growing ~$87K/day | 3 Jul 2026 |
| Prior read | $409,202 | 29 to 30 Jun 2026 |
| Finance net income / reconciled | $6,234,694.64 / $5,563,577.57 | 3 Jul 2026 |
| Bank rec 11104 NAT Operations | 378 unmatched, last reconciled 31 Mar 2022 | Jul 2026 |
| Bank rec 11103 NAT ABF Donations | 120 unmatched, last reconciled 31 Mar 2022 | Jul 2026 |
| Major Donor double count | $9,089 gap, ~$37,500 confirmed | Jul 2026 |
| Bank clearing lag | 1 to 3 business days into `118636581` | standing |
| Proposed policy | SF Close Date plus NetSuite +3-business-day month-end window, from 1 Aug 2026 | Jul 2026 |
| Exception report Zap | ID `371228125`, DRAFT, never published (details in `birdlife-zapier`) | Aug 2026 |
| SF report feeding the Zap | `00ORF0000033T6z2AE` | Jul 2026 |

## OAuth2 certificate (orphaned)

| Fact | Value |
|---|---|
| Type | OAuth 2.0 client credentials (M2M) on SuiteCloud Development Integration |
| Certificate ID | `7SCEnbQf6XYE-nv-8z_q0oWmPNm3RM5aCWD7A2WSklo` |
| Created | 28 Oct 2024 |
| Valid | 17 Sep 2024 to 17 Sep 2026 |
| Linked entity / creator | BLA216 Rachel Munt (departed) / Matej Fucek (departed) |
| Activity | zero across SOAP, REST, RESTlets, AI Connector |
| Action | revoke, monitor, delete; briefed to CFO David Thompson 20 Jul 2026, no action yet |

Token-Based Auth credentials for Zapier do not exist yet (integration record,
consumer key/secret, token id/secret; user Mathew Hema, Administrator role).

## Connector (`NetSuite`)

`ns_runCustomSuiteQL` returns `{data:[...], totalResults, numberOfPages}`
(page when more than one). `SELECT id, name FROM subsidiary` returns two rows
and is the connectivity check. Tables: `transaction`, `transactionline`,
`transactionaccountingline` joined on `transaction.id`; `account.acctnumber`.
Also: `ns_getSuiteQLMetadata`, `ns_listSavedSearches`, `ns_listAllReports`,
`ns_runSavedSearch`, `ns_runReport`, `ns_getRecord`, `ns_createRecord`,
`ns_updateRecord` (writes never used from a page or routine).

## Business Central (advisory only)

BC list prices quoted: Team Member ~$8 to 10, Essentials $80, Premium $110 per
user per month. Claimed saving >$100k/yr is unquoted and unverified.
