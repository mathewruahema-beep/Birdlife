# Automation Build: Regular Giving & Membership Renewal Recovery

**Status: BUILT, NOT ACTIVATED.** The flows in `force-app/main/default/flows/` are complete, deployable metadata with `<status>Draft</status>`. Deploying them changes nothing at runtime — no email is sent and no task is created until a human activates each flow, and the agreed path is **staging first**.

---

## 1. The process chosen, and why it is repeatable

When a Payments2Us recurring payment (regular-giving donation **or** membership auto-renewal) fails repeatedly, the managed package sets `AAkPay__Recurring_Payment_Status__c` to **"Suspended - Max retries exceeded"** and stops charging. From that moment the money simply stops.

The same event, with the same recovery steps, happens ~14 times every month:

| Evidence (production, 20 Aug 2026) | Value |
|---|---|
| RPs currently in "Suspended - Max retries exceeded" | **542** (A$4,082/month committed) |
| — of which BirdLife Memberships | 444 (A$2,678/mo) |
| — of which Direct Debit Donations (Wildbird RG) | 43 (A$1,310/mo) |
| New suspensions, last 90 days | 43 (~14/month), **all** with donor email on file |
| Tasks logged against any Recurring Payment, last 180 days | **0** |
| Active RPs with card expiring ≤ 60 days (phase 2) | 133 (A$786/mo) |

There is a welcome journey when a recurring payment starts (flow *"Recurring Payment: After insert, send Welcome to Wildbird Regular Giving Email"*) but **no journey when one dies**. Membership suspensions additionally threaten `Active_BL_Member__c` and therefore Emu journal access.

## 2. The pattern

This build follows the org's own established pattern (the Wildbird welcome flow): **record-triggered flow on `AAkPay__Recurring_Payment__c` → guardrail decision → donor email → internal work item → time-based escalation.** It is deliberately generic so it can be re-applied to gap #4 (NPSP `npe03__Recurring_Donation__c` status → Lapsed) and to the future `Membership__c` object after the Payments2Us decommission — only the trigger object and fields change.

```
[Status changes to Suspended - Max retries exceeded]
        │
        ├── Immediate path
        │     ├─ Guardrails: Contact exists · has Email · not Deceased · not Email Opt-Out
        │     ├─ YES → email donor (self-service payment-update link) → Task (owner, due +7d, High)
        │     └─ NO  → Task only, flagged "no email possible - phone/mail" (due +7d, High)
        │
        └── Scheduled path (+14 days)
              ├─ Re-fetch record (fresh values, not trigger-time values)
              ├─ still Suspended → escalation Task "phone the donor" (due +3d, High)
              └─ recovered/cancelled → end, no action
```

## 3. What was built (this package)

| Component | File | Trigger | Status |
|---|---|---|---|
| Flow: **RP aCU - Suspended Regular Giving Rescue** | `flows/RP_aCU_Suspended_Regular_Giving_Rescue.flow-meta.xml` | After save, status **changes to** "Suspended - Max retries exceeded" | Draft |
| Flow: **RP aCU - Card Expiry Reminder** (phase 2) | `flows/RP_aCU_Card_Expiry_Reminder.flow-meta.xml` | After save, `AAkPay__Expiry_Reminder__c` **changes to** true while status = Active (P2Us sets this flag automatically ~31 days before card expiry) | Draft |
| Manifest | `manifest/package.xml` | — | — |

Design decisions baked in:

- **`doesRequireRecordChangedToMeetCriteria` = true** on both flows — they fire only on the transition, never on unrelated edits to an already-suspended record, so deploying + activating cannot mass-email the 542-record backlog. The backlog is a deliberate, separate one-off campaign (see §6).
- **Donor email uses the P2Us self-service link** (`AAkPay__Email_Card_Update__c`, the URL-token card/bank-details update page) — the donor fixes their own payment method with zero staff licences and zero new credentials.
- **Tasks anchor to the Recurring Payment** (`WhatId`) and the Contact (`WhoId`), owned by the RP record owner — no new users, no licence impact.
- **Guardrails** exclude Deceased contacts and Email Opt-Outs, and route no-email records to a task-only path instead of silently dropping them.
- **The scheduled path re-queries the record** before escalating, so a donor who fixed their card in the meantime is never chased.
- Plain-text email bodies, sender defaults to the running user; switch to an org-wide address (e.g. supporter services) during staging configuration — flagged in §5.

## 4. Benefits

1. **Direct revenue recovery.** New suspensions run ~A$350/month of committed giving per quarter-cohort. Industry-typical recovery for a prompt email+call sequence is 30–50%; even 30% on the ongoing flow is roughly **A$5–7k/year protected**, compounding because every saved RP keeps paying.
2. **Membership retention & benefits integrity.** 82% of suspensions are membership auto-renewals — today these members silently lapse (and journal access via `Active_BL_Member__c` breaks) without anyone being told. Every suspension now produces a visible, owned work item.
3. **Phase 2 prevents failures instead of curing them.** 133 active RPs (A$786/mo) have cards expiring within 60 days; a pre-expiry nudge avoids the decline → retry → suspend cycle entirely.
4. **Zero incremental cost.** No new licences (70/70 consumed — this uses flows, tasks and existing self-service pages), no new integration, no managed-package modification.
5. **Auditability.** Tasks + flow interview logs give supporter care a measurable queue (recovery rate, time-to-contact) where today the number of follow-ups is provably zero.
6. **A reusable pattern.** The same skeleton ports to NPSP Lapsed recurring donations (78 today) and to the post-P2Us membership build, protecting the investment through the decommission.

## 5. Activation gate — must be cleared in staging BEFORE any activate

1. **Double-email check (most important).** Payments2Us has its own optional card-failure/expiry emails (`AAkPay__Resend_Card_Failure__c`, merchant-facility settings). Verify on the staging Merchant Facility / Payment Forms whether P2Us already emails on failure; if it does, either disable that or re-position this flow's email as the second touch. Never send the donor two failure emails.
2. **URL token coverage.** Confirm `AAkPay__Email_Card_Update__c` resolves to a working page for both card and BECS direct-debit RPs (link renders as `https://<token URL>`); where token generation is off, the email still reads correctly but the task is the primary channel.
3. **Sender address.** Point `emailSimple` at an org-wide verified address (supporter services) instead of the automated-process user default.
4. **Task routing.** Confirm RP record owners are the right owners (many old RPs may be owned by integration/admin users) — if not, retarget `OwnerId` to a queue agreed with Fundraising (V) before activation.
5. **Staging quirks.** Staging subscription periods are 1 day and SKUs are `-STAGING`; test with those, and remember all IDs differ from production.
6. **Regression scan.** `Recurring Payment aCU - Status Changed` (change logging) and the P2Us managed automation both fire on the same transition — confirm order-independence (this flow only reads the record and creates Task/email; it writes nothing back to the RP, so collision risk is minimal by design).
7. **Deliberately out of scope:** the 542-record backlog (run as a one-off segmented campaign — see §6), NPSP RD lapse handling (phase 3), and any change to P2Us retry settings.

## 6. Rollout plan

| Step | Environment | Action |
|---|---|---|
| 1 | Staging | `sf project deploy start -x manifest/package.xml -o <staging>` (flows arrive as Draft) |
| 2 | Staging | Clear §5 checklist; activate; force a test suspension (1-day subscription period makes this fast); verify email, task, +14d escalation (use Flow debug/time-travel) |
| 3 | Staging | Fundraising sign-off on email copy (V / Supporter Care) |
| 4 | Production | Deploy same manifest (still Draft — zero effect) |
| 5 | Production | Activate **Rescue** flow only; monitor 2 weeks (tasks created vs suspensions; interview failures) |
| 6 | Production | Activate **Card Expiry Reminder**; monitor |
| 7 | One-off | Backlog campaign for the existing 542: export segmented list (memberships vs RG, has-email vs not), run through supporter care as a called/emailed campaign — *not* through this flow |
| 8 | Reporting | Add "Suspensions this month / recovered / open rescue tasks" to the fundraising dashboard |

## 7. What this build deliberately does NOT do

- It does **not** touch any managed package metadata (AAkPay, NPSP, MoveData).
- It does **not** write to the Recurring Payment record at all — read-only trigger, so it cannot fight the managed package's own automation.
- It does **not** retry payments, change retry settings, or alter money movement in any way.
- It is **not activated** — deployed or not, nothing runs until the activation gate in §5 is signed off.
