# BirdLife Australia — ICT environment

Grounding file for Zeus Assist. Upload to the Claude Project's knowledge, or let
`client/chat.py` inline it.

**Keep this file honest.** Anything in here the model will state as fact. If you are
not sure of a value, mark it `TODO` rather than guessing — a `TODO` produces "I don't
know, check X", a guess produces a confident wrong answer.

Last verified: 2026-08-07. The Case Type, Status and Origin values below were read
from the live Salesforce org on that date, not transcribed from documentation.

---

## Organisation

BirdLife Australia. Not-for-profit bird conservation. ~150 staff, multiple offices
plus a large volunteer and member base. ICT is a four-person team.

## The helpdesk queue

| | |
|---|---|
| System | Salesforce — `birdlifeaustralia.lightning.force.com` |
| Object | `Case` |
| Record type | **Ask Zeus** (`DeveloperName` = `Zeus`, Id `012I80000004IPnIAM`) |
| Volume | ~425 cases per quarter; 20 open at 6 Aug 2026 |
| Intake | 96.5% email, 3.5% internal. **No web form, no phone, no portal.** |

`Case` is shared across the whole organisation — 19 record types, including Powerful
Owl, Swift Parrot Search, AOC, Conservation Campaigns, General Enquiry, KBA and
Birdata. **Those are other teams' queues, not ICT.** Any figure not filtered to
record type `Ask Zeus` is wrong by roughly 200×.

**Case owners:** Mathew Hema, Andrew Dunn, Keith Tsui, Nina Lewis.
`Owner.Name = "Zeus"` is **not a person** — it is the unassigned intake queue.

### Case Type picklist — complete

Mandatory when closing. These are the **only** valid values. Volumes are the last
365 days (870 cases), measured 7 Aug 2026:

| Type | Cases | Notes |
|---|---:|---|
| Admin | 313 | Largest bucket — account admin, licences, config changes |
| Troubleshooting | 284 | Something broke and needs diagnosis |
| IAM | 82 | Identity & access: MFA, lockouts, permissions |
| New Feature | 57 | A request for something that doesn't exist yet |
| New User | 51 | Onboarding |
| Departing Staff | 40 | Offboarding |
| Purchase/Renew | 29 | Licence or hardware procurement |
| Spam | 1 | |
| *(blank)* | 13 | The gap the close-time validation rule fixes |

Identity lifecycle = IAM + New User + Departing Staff = **173 of 870, 20%**, holding
the same proportion over a full year as over the last 425 cases.

Admin and Troubleshooting together are 69% of volume and are both broad. When
choosing between them: *Troubleshooting* is "it was working and now it isn't";
*Admin* is "please change/grant/configure something".

### Case Status — complete

`New` → `In Progress` → `Waiting Response-External` → `Response Received` → `Closed`

Only those five values exist on Ask Zeus. `Waiting Response-External` means waiting
on the requester or a vendor — it stops the clock; `Response Received` means they
have replied and it is back with ICT.

### Origin

`Email` (842 of 870, 96.8%) and `Internal` (28). There is no Web, Phone or Portal
origin on Ask Zeus — those values in org-wide reports belong to other teams.

## The project board

| | |
|---|---|
| System | Asana |
| Project | `1211042432693678` — IT Operations Project Plan |
| Size | 105 incomplete tasks across 8 sections |

Sections include Backlog, In Development, **Ready for Deployment**, **Hypercare**,
Blocked, Done.

Ready for Deployment and Hypercare have been **empty throughout** — work moves from
In Development straight to Done, or to Blocked. If a user asks about release process,
that is the honest state of it.

## Systems in the estate

| System | Role | Notes |
|---|---|---|
| Microsoft 365 / Entra ID | Identity, mail, Teams, SharePoint, OneDrive, Intune, Defender | Primary identity plane |
| Salesforce ("Zeus") | CRM, supporter/member data, NPSP, and the ICT helpdesk | Payments2Us, Conga, Plauti dedupe |
| NetSuite OneWorld | Finance / ERP | Finance-owned, not ICT |
| WordPress on WP Engine | `birdlife.org.au`, WooCommerce shop & memberships | miniOrange syncs to Salesforce |
| Cloudflare | DNS, CDN and proxy in front of WP Engine | Two accounts |
| Stripe | Card payments via WooCommerce | |
| Zapier | Glue automation between SaaS apps | |
| Employment Hero | HR / payroll — **source of truth for staff records** | Syncs into Entra |

Identity flows **Employment Hero → Entra ID**. A wrong name, start date or
termination date is an HR-side correction, not an ICT one. Say this rather than
editing Entra by hand.

## Known open risks

The assistant may be asked about these. They are real and current:

- **WooCommerce API keys were exposed in plaintext** in scheduled routine prompts.
  They need rotating. Any request involving those keys should trigger the credential
  rule in the instructions.
- **Self-registration privilege flaw** on the WordPress site.
- **Expired plugin licences** on a site taking live payments.
- No self-service channel — every request arrives as an email a human reads.
