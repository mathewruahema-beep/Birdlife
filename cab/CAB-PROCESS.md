# BirdLife Australia — Change Advisory Board (CAB) Process

**Version 1.0 — August 2026**
**Owner:** Mathew Hema (CAB Chair) · **Review:** every 6 months

---

## 1. Why a CAB

The ICT estate is small but the blast radius is not. A single WordPress plugin
update sits in front of live donations; an SPF record change can silence
Salesforce Case intake; a NetSuite segment edit flows into every financial
report. Today the Asana board shows work moving from *In Development* straight
to *Done* — *Ready for Deployment* and *Hypercare* have been empty throughout —
which means changes reach production with no gate, no shared record of what
changed, and no agreed rollback.

The CAB exists to fix exactly that, with the minimum ceremony a four-person
ICT team can sustain:

- **Every production change is recorded** before (or, for emergencies,
  immediately after) it happens.
- **Risk decides the level of scrutiny** — most changes should pass with a
  peer's async thumbs-up, not a meeting.
- **The organisation gets a voice** on changes that touch its money, its
  members, or its public face.
- **We learn from failures** through a lightweight post-implementation review.

The CAB is a service to the organisation, not a brake on ICT. If the process
is slowing safe work down, the process is wrong — raise it at any CAB meeting.

## 2. Scope

A **change** is any modification to a production system's configuration, code,
data structure, integrations, or access model. In scope:

| Domain | Examples |
|---|---|
| Salesforce ("Zeus") | validation rules, flows, record types, permission sets, managed package upgrades (Payments2Us, Conga, Plauti), report/dashboard changes relied on by others |
| Website / WooCommerce | plugin installs & updates, theme changes, checkout or membership changes, WP Engine environment changes, miniOrange sync settings |
| NetSuite | chart of accounts, segments, saved searches used in close, roles, Infinet/ZonePayroll config, integrations |
| Microsoft 365 / Entra | Conditional Access, MFA policy, mail flow rules, distribution list restructures, Intune policy, licence model changes |
| Cloudflare / DNS | any DNS record (especially SPF/DKIM/MX), WAF, caching rules, Workers |
| Stripe / payments | webhook endpoints, API key rotation, payout or dispute settings |
| Integrations & automation | Zapier zaps touching production data, Raisely/MoveData, Ortto sync, scheduled routines |
| Identity lifecycle | changes to the onboarding/offboarding process itself (not individual joiners/leavers) |

**Out of scope** (business as usual, no change record needed): password/MFA
resets for individuals, single-user licence assignments, routine content
edits on the website, individual record fixes in Salesforce, running existing
reports, restarting a service with no config change.

If unsure, log it. A change record costs two minutes; an unrecorded outage
costs a day of archaeology.

## 3. Change types

| Type | Definition | Approval path |
|---|---|---|
| **Standard** | Pre-approved, repeatable, low-risk, documented procedure (see §8 catalogue) | None — log it in the register as Standard; it is auto-approved |
| **Normal** | Everything else, assessed by risk score (§4) | Low → one peer, async · Medium → CAB async or next meeting · High → CAB meeting |
| **Emergency** | Needed *now* to restore service or close an active security hole | Verbal/chat OK from CAB Chair (or any other CAB member if Chair unavailable), do the work, log it same day, retrospective review at next CAB |

## 4. Risk assessment

Score every Normal change as **Impact × Likelihood**. The requester scores it;
the approver sanity-checks it.

**Impact — if this change goes wrong, what breaks?**

| Score | Level | Meaning at BirdLife |
|---|---|---|
| 3 | High | Donations/payments flow, membership joins/renewals, org-wide sign-in (Conditional Access, MFA), DNS/SPF/mail flow, financial data integrity in NetSuite, public website availability |
| 2 | Medium | One team's system or workflow degraded; a workaround exists; internal-only impact |
| 1 | Low | Single user or cosmetic; trivially reversed |

**Likelihood — how likely is it to go wrong?**

| Score | Level | Meaning |
|---|---|---|
| 3 | High | Novel change, no test environment available, vendor-dependent, or touches undocumented config |
| 2 | Medium | Some complexity or dependencies; partially tested |
| 1 | Low | Well-understood, tested in staging/sandbox, rollback rehearsed or trivial |

**Risk = Impact × Likelihood**

| Score | Risk | Who approves | How |
|---|---|---|---|
| 1–2 | **Low** | Any one other CAB member | Async in the tool — no meeting |
| 3–4 | **Medium** | CAB Chair + one member | Async, or next CAB meeting if anyone asks |
| 6–9 | **High** | CAB meeting | Quorum of 3 incl. Chair; affected business stakeholder invited; tested rollback plan mandatory |

Two hard rules regardless of score:

1. **Anything touching payments, donations, or member joins in production is
   minimum Medium** — even a "routine" plugin update. The expired-licence and
   cart-flood history is why.
2. **A change with no rollback plan is not approvable.** "Restore from WP
   Engine backup" is a valid rollback plan; "should be fine" is not.

## 5. Roles

| Role | Who | Does |
|---|---|---|
| CAB Chair | Mathew Hema | Runs meetings, tie-breaks, approves emergencies, owns this process |
| CAB members | Andrew Dunn, Keith Tsui, Nina Lewis | Assess and approve changes, take Change Owner roles |
| Change Requester | Anyone (ICT or business) | Raises the request, scores risk, proposes schedule and rollback |
| Change Owner | An ICT team member | Implements, verifies, closes with an outcome. Defaults to the requester if they're in ICT |
| Business stakeholders | e.g. Finance lead for NetSuite, Fundraising lead for Salesforce/website | Invited for High-risk changes to their domain; can veto scheduling into their critical periods |

Quorum for a CAB meeting decision: **3 of 4** ICT members including the Chair
(or the Chair's delegate).

## 6. Cadence and flow

- **CAB meeting: fortnightly, 30 minutes**, appended to an existing ICT
  catch-up. Standing agenda: (1) emergency changes since last meeting —
  retrospective review; (2) High-risk requests; (3) Medium requests anyone
  escalated; (4) failed/rolled-back changes — lessons; (5) freeze-window
  lookahead.
- **Between meetings**, Low and Medium changes move by async approval in the
  Flightpath tool. Don't hold a safe change for a fortnight.
- **Change lifecycle:**

```
Submitted → In review → Approved → Scheduled → Implemented → Closed (with outcome)
                     ↘ Rejected / Deferred
Emergency: do the work → log as Implemented (retro flag) → reviewed & Closed at next CAB
```

- **Closing a change records one of four outcomes:** Successful · Successful
  with issues · Rolled back · Failed. Rolled back and Failed changes get a
  short PIR: what happened, what we'd do differently, whether a standard
  procedure or freeze rule should change.

## 7. Change freeze windows

No Medium or High changes to the affected domain during these windows without
CAB-meeting approval. Standard and Low changes allowed with extra care;
emergencies always allowed.

| Window | When | Protects |
|---|---|---|
| EOFY receipting | 15 Jun – 15 Jul | Salesforce receipting, NetSuite close, payments |
| Aussie Backyard Bird Count / Bird Week | ~2 weeks mid-October (confirm dates annually) | Website, Birdata-adjacent load, donations |
| Year-end giving | 1 Dec – 5 Jan | Website, donations, payments, email |

The Flightpath tool warns automatically when a planned date lands in a freeze
window. Windows are reviewed at the first CAB of each calendar year.

## 8. Standard change catalogue (v1)

Pre-approved procedures — log as Standard, then just do them:

1. WordPress **minor/patch** plugin updates on **staging** (production
   promotion of the same update is a Normal change, min. Medium if the plugin
   touches checkout).
2. Salesforce report/dashboard changes that only add filters or rename
   labels, on reports owned by ICT.
3. Adding a member to an existing distribution list or shared mailbox.
4. Creating a Zapier zap that only **reads** production data.
5. DNS TTL reductions ahead of a planned change.
6. Certificate/credential rotation following the documented runbook.

Additions to this catalogue are approved at a CAB meeting: a change must have
run cleanly as a Normal change at least twice first.

## 9. Where the record lives

- **Flightpath tool** (`cab/cab-tool.html`, published as a shared artifact) —
  the change register, risk scoring, approvals log, and CAB agenda. The page
  itself is the record: every submission and decision publishes a new version
  attributed to the person who made it.
- **Asana** — implementation work for Approved changes is tracked as tasks;
  *Ready for Deployment* now means "change approved & scheduled", *Hypercare*
  means "implemented, in verification before Close". This gives those two
  empty sections their job.
- **Zeus (Salesforce)** — where a change originates from a helpdesk case,
  record the case number on the change request so the requester can be told
  the outcome.

## 10. Metrics the CAB watches

Reviewed quarterly from the register:

- **Change success rate** — Closed-Successful ÷ all Closed. Target ≥ 90%.
- **Emergency ratio** — Emergency ÷ all changes. Target < 15%; a rising ratio
  means planning is failing upstream.
- **Rolled back / Failed count** — each one gets a PIR; two in the same domain
  in a quarter triggers a deeper look.
- **Unrecorded changes discovered** — anything found changed in production
  with no register entry. Target: zero; each one is a process conversation,
  not a blame exercise.
