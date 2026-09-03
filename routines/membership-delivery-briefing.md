# Routine: Membership Build delivery briefing (Mon/Wed/Fri 7am AEST)

**Status: live.** Trigger `trig_01F7wy1pGcauqCsgUxVU4b47`, updated 3 Sep 2026 from the
former "Membership Build: Friday status update draft" (created 2 Sep 2026, never fired)
rather than creating a 13th routine. One job per outcome: the Friday status draft is now
the Friday variant of this routine. Recurring routine budget stays at 12 of 12.

| Setting | Value |
|---|---|
| Schedule | `0 21 * * 0,2,4` UTC = Monday, Wednesday, Friday 7:00am AEST. After the 5 Oct DST shift this fires 8:00am AEDT; fold it into the standing DST fix one-shot if 7am matters. |
| Session | fresh session per run, this environment |
| Connectors needed | Asana (read), Salesforce Staging (read), Salesforce Production (read), Microsoft 365 (Outlook read). Attach in claude.ai → Routines; the assistant cannot attach connectors. |
| Notification | push on completion (email off) |
| Writes | none to Asana, Salesforce or Outlook. The only write is republishing the Membership Delivery Desk artifact with the new briefing block. |
| Output | a sub-300-word delivery briefing (SendUserMessage + written into the Desk's Today tab); on Fridays also the weekly status draft ending "Post as written, or changes?" |

## What the briefing contains

Short answer (programme colour and the one reason) · Moved since last run · Late, by
owner, with what each holds · The tightest critical-chain link and any date inversion ·
Today's three conversations (the first is always whoever holds the critical path) ·
Decisions due with owner and date · a two-line run report naming which connectors
answered.

Evidence sources per run: Asana board (tasks, dependencies, comments on the 4 to 6 most
consequential items), Salesforce staging (does `Membership__c` exist yet; are order line
items still Postage at 0; MEM- product count), Salesforce production (raw WooCommerce
StageName strings still being written), Outlook read of the UAT Website and Membership
threads for vendor commitments.

## Prompt

The full prompt is stored on the trigger. Re-read it with `list_triggers` before editing;
change it with `update_trigger` (never delete and recreate, that loses run history).
Hard rules baked in: Asana read only, no email, no status posting, no credentials, never
fabricate a figure, say which connector was missing.

## Register note

`os/registers.md` lives on the `claude/os-for-claude-y12d5q` branch, not on this one.
When that branch and this one meet, add the row: routine trig_01F7wy1pGcauqCsgUxVU4b47,
renamed 3 Sep 2026, cron `0 21 * * 0,2,4`, outcome "Membership Build delivery briefing +
Friday status draft", owner Mathew, artefact c79983b4-5375-48b1-8d73-f405c4838f95.
