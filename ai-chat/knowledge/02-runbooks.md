# Runbooks — the three case types that are 20% of the queue

Grounding file for Zeus Assist.

IAM (49) + Departing Staff (22) + New User (16) = 87 of the last 425 cases. If the
assistant is good at nothing else, it should be good at these.

**These are skeletons, deliberately.** Every `TODO` is a step only your team can
fill in — the exact group name, the exact licence SKU, the exact approver. Fill them
from the last five cases you closed of each type, not from memory. An unfilled
`TODO` makes the assistant say "check with the team"; a plausible invention makes it
send a technician down a path that does not exist.

---

## New User (onboarding)

Trigger: People & Culture confirm a start date. The record originates in **Employment
Hero** and syncs to Entra ID — the account should not be hand-created unless the sync
has failed.

1. Confirm the person exists in Employment Hero with the correct legal name, start
   date and manager. If not, **stop** — that is a P&C correction, not an ICT one.
2. Confirm the Entra account has appeared from the sync. If it has not after
   `TODO — expected sync interval`, that is a sync fault, not an onboarding task.
3. UPN / email format: `TODO — confirm convention, e.g. firstname.lastname@birdlife.org.au`
4. Licence: `TODO — which SKU by role`. Check availability before promising a date.
5. Groups and distribution lists by role/team: `TODO — list the role→group mapping`
6. MFA registration — send the enrolment instructions with the welcome mail.
7. Hardware: `TODO — device build/Intune enrolment steps, and who orders`
8. Applications beyond M365 — Salesforce, NetSuite, WordPress, Asana as required by
   role. **Each has a separate owner and its own approval.** Salesforce licences in
   particular are not free; check before assigning.

Close as Type `New User`.

---

## Departing Staff (offboarding)

Highest-risk case type in the queue. Getting this wrong leaves a live account for
someone who has left.

Trigger: termination date in Employment Hero. **Do not act on a verbal heads-up** —
confirm the HR record first, and confirm the actual last working day, which is often
not the date first mentioned.

1. **On the last working day, at the agreed time** — block sign-in and revoke active
   sessions/refresh tokens. Blocking sign-in alone does not kill a live session.
2. Reset the password and remove the MFA methods.
3. Mailbox: `TODO — convert to shared, or delegate to manager? Confirm the standard
   and the retention period.`
4. Forwarding or auto-reply, if the manager has asked for one.
5. OneDrive contents — transfer to the manager before the account is removed.
   `TODO — retention window before deletion.`
6. Remove from distribution lists, Teams, and shared mailbox permissions.
7. **Non-M365 systems** — Salesforce, NetSuite, WordPress/WP Engine, Asana,
   Cloudflare, Stripe, Zapier. These do not offboard themselves and are the usual
   miss. Reclaim the licence where one is attached.
8. Any privileged/admin role, and any shared or service credential the person knew —
   rotate it.
9. Hardware return: `TODO — who chases, and what happens if it is not returned`

Close as Type `Departing Staff`. Note in the resolution which non-M365 systems were
covered, so the next person can see what was checked.

---

## IAM (access, MFA, lockouts) — the biggest single bucket

Most common sub-cases and the first thing to check:

| Symptom | First check |
|---|---|
| Can't sign in | Is the account blocked or the password expired, or is it a Conditional Access block? These look identical to the user. |
| MFA prompt loop | Device compliance / Conditional Access, not the MFA method itself |
| New phone, lost authenticator | Requires identity verification **before** you reset the method — `TODO — what is the approved verification standard?` |
| "I need access to X" | Who owns X? ICT does not own most of them. Route, don't grant. |
| Guest/external access | `TODO — is external sharing permitted, and who approves?` |

**Rules that hold regardless of the sub-case:**

- Verify identity before resetting an authentication factor. A help desk that resets
  MFA on an emailed request is the single most exploited path into an organisation —
  and 96.5% of this queue arrives by email.
- Never fix a Conditional Access block by excluding the user from the policy.
  Find why the policy fired.
- Never grant a standing privileged role to solve a one-off task.
- Access to Salesforce, NetSuite and the website is **owned by those systems' owners**,
  not by ICT. ICT provisions identity; it does not decide entitlement.

Close as Type `IAM`.

---

## The pattern worth naming

All three of these are the same underlying process — identity lifecycle — handled as
individual emails. A request form and a documented playbook removes the class. A
faster answer to each individual ticket does not. The assistant should say this when
it is relevant, and then stop saying it.
