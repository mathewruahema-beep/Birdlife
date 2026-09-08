# ADR 0019: The BirdLife OS lens model, and the gate for promoting Entra writes to Tier 1

- **Status:** Proposed (lens model Accepted 8 Sep 2026; the Entra promotion gate awaits Mathew's word)
- **Date:** 8 September 2026
- **Decided by:** Mathew Hema

## Context
Mathew asked for a "BirdLife OS" he can use across the digital ecosystem through
lenses, acting first as IT Admin in all systems. A Claude OS already exists
(birdlife-os skill, the BirdLife Australia console, the registers). Building a
second one would be skill sprawl.

A live probe of every connector on 8 Sep 2026 (IT-GOV-004, section 3) found that
the entra-admin-cloud connector on the desktop bridge answers Microsoft Graph reads
under Mathew's admin identity and exposes write tools (disable and enable account,
set licences, set manager, add and remove group member, revoke sessions, create
user, temporary access pass, delete auth method). ADR 0002 still records Entra
writes as "pending a separate app registration and admin consent". The record and
the estate disagree.

## Decision
1. The OS gains a lens model: IT Admin (live), Security, Finance link, Manager, and
   Board and Exec (stubs). A lens fixes who is acting, which systems, the write tier
   per action, the standing questions and the outputs. A lens can narrow authority,
   never raise it. The IT Admin capability matrix in IT-GOV-004 is the record of what
   each connector can do and at what tier; it is re-verified live at the Monday OS
   audit and any row older than 30 days is a baseline, not a fact.
2. Extend, do not replace: the lens lives in the birdlife-os skill and the console
   (Lens tab, active lens prepended to every Jarvis turn), not in a new artefact.
3. Entra promotion gate (Proposed): Entra stays Tier 2 (prepare and hand over) until
   ONE reversible write has been executed through the connector behind an approval
   card with a written rollback and a re-read proof. On that proof, four actions move
   to Tier 1 with approval: disable_user_account, revoke_user_sessions, licence
   removal via set_user_licenses, and remove_user_from_group. create_user,
   create_temporary_access_pass, delete_auth_method and any enable_user_account stay
   Tier 2 and require an Ask Zeus Case number in the approval card. Mail-enabled
   group removal still needs Exchange PowerShell (IT-SEC-004). One user per
   approval, never a list.

## Rationale
The approve-then-write charter (ADR 0002) was written when no write path existed.
The write path now exists on Mathew's own machine under his admin identity with CA
policy CA-005 in front of it. Keeping the policy while the capability sits unused
gives the slowest possible offboarding (the Finn Saurine case ran 19 days) with none
of the safety of a tested gate. Proving one write first, then promoting four narrow
and reversible actions, is the staged path ADR 0017 (autonomy levels) calls for.

## Consequences
- Andrew Dunn and Keith Tsui: no change until the gate passes; then the offboarding
  detector's approval pack can be executed by Mathew in the same session, and the
  leaver latency drops from days to the time it takes to tap Approve.
- Nina Lewis: none.
- Staff: an approved disable is deliberate, logged and reversible; a mistaken one is
  undone by enable_user_account in the same session.
- ADR 0002 is not edited (rule: supersede, never edit); this ADR supersedes its
  "current enabling state" section once the gate passes.
- IT-GOV-004 findings F2 to F6 (shared Zapier Teams credential, AWS bridge without
  credentials, GitHub not connected, Raisely token privilege unknown, three
  overlapping Salesforce read paths) are open items for Asana, not for this ADR.

## Revisit when
The first proven Entra write lands, or the entra-admin connector is rehosted or
its certificate renewed (one-shot trig_01Vp14cTKJCLnC7psjiRZnUC, 25 Jul 2027).

## Related
ADR 0002, ADR 0007, ADR 0010, ADR 0015, ADR 0016, ADR 0017; IT-SEC-002; IT-SEC-004; IT-GOV-004.
