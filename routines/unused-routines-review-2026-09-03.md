# Unused routines review, 3 September 2026

Live pull of `list_triggers` at 22:04 AEST on 3 September 2026, checked against
the routine register on branch `claude/os-for-claude-y12d5q` (`os/registers.md`,
last audited 2 September), the SharePoint heartbeat log
(`ICTMonitoring/General/_dashboard-run-log.txt`), Salesforce CaseComment
history, and the run sessions behind each trigger's last run. Read only: no
routine, connector or production record was changed by this review.

## Headline

15 triggers are live: 13 recurring and 2 one-shots. The register expects 12
recurring. The budget of 12 was breached today by a routine created outside the
register (AI Daily Ten).

Three routines are effectively unused: they fire on schedule, spend tokens,
and deliver nothing, because their core action stalls on an approval prompt in
an unattended session. Together they are the three most expensive prompts on
the account.

| Routine | Trigger | Evidence |
|---|---|---|
| ICT weekday dashboards and monitor (single job) | `trig_01HhAKnEe6PXAvo6EEq72BHo` | Heartbeat log last written 25 Aug 07:13 AEST. Seven weekday deep slots since (26, 27, 28, 31 Aug, 1, 2, 3 Sep) logged nothing. Today's 5:04pm slot has sat BLOCKED since 5:06pm on an approval for `mcp__Zapier__execute_zapier_write_action` (the website probe via Webhooks by Zapier, url learn.birdlife.org.au), 0 tokens used. Section 2 of the prompt runs that probe on every slot before anything else, so every slot halts there. |
| ICT overnight pre-draft (approve-first) | `trig_01EbMkfD4UcGUKLkUB1mNQ8V` | 2 Sep run ABANDONED, stuck on approval for `createSobjectRecord` (its only deliverable). Salesforce shows zero `[ASSISTANT DRAFT` comments between 24 Aug and 2 Sep across seven weekday fires. The three drafts dated 3 Sep 21:35 AEST were manual approvals in the stuck session; a fourth is still pending. Push notification is off, so the failures were silent. Step 5 also targets `console/index.html` and artifact `29a063d4`, both retired on 3 Sep per the register. |
| Dashboards weekend + weekly security (single job) | `trig_01CUkTdAFSisnzyU6pwgkH4k` | 29 Aug fire stalled for 4.5 days and closed on 3 Sep 21:32 AEST with 1,651 output tokens and 0.46 USD spent, which is a run that did nothing. The pending action is no longer visible. First merged-job fire is Sat 5 Sep 7:04am; the register's verification window stands, with lower confidence. |

Root cause for the first two is the same: the routine runs in `auto`
permission mode with only built-in tools pre-approved
(`preset:default`, Bash, Read, Edit, and so on). A connector write it needs
(Zapier action, Salesforce create) is held for a human who is not there. The
session then sits in REQUIRES_ACTION until it is abandoned.

## Verdict on every live trigger

| Routine | Trigger | Schedule (AEST) | Last run | Verdict |
|---|---|---|---|---|
| ICT weekday dashboards and monitor | `…HhAKnEe6PXAvo6EEq72BHo` | hourly 7:04am to 5:04pm | PENDING since 5:06pm today, blocked on Zapier approval | FAILING, firing but idle since 26 Aug |
| ICT overnight pre-draft | `…EbMkfD4UcGUKLkUB1mNQ8V` | weekdays 5:30am | ABANDONED 2 Sep, blocked on Salesforce create | FAILING, zero autonomous drafts since 24 Aug |
| Dashboards weekend + weekly security | `…CUkTdAFSisnzyU6pwgkH4k` | Sat, Sun 7:04am | "SUCCEEDED" after a 4.5 day stall, no output | UNVERIFIED, watch 5 to 6 Sep |
| AI Daily Ten (Gmail newsletters) | `…Y69zEQwQtn4HcGw9Esz8ua` | weekdays 6:34am | never, first fire tomorrow | UNREGISTERED, 13th recurring routine, Gmail not yet attached per its build session |
| Claude OS weekly audit | `…V3i4b5zekjZuuFTF6Ymu9G` | Mon 6:03am | never, first fire 7 Sep | WILL FAIL: prompt reads and commits `os/registers.md` on the default branch, which does not have an `os/` directory (it is on the unmerged `claude/os-for-claude-y12d5q`, 15 commits ahead) |
| Membership Build delivery briefing | `…F7wy1pGcauqCsgUxVU4b47` | Mon, Wed, Fri 7:08am | SUCCEEDED 3 Sep (manual test fire) | HEALTHY; register row is stale (says Friday only) |
| ICT Weekly Status Update | `…AsdSGs9WiwRUrmbRmSxtAZ` | Fri 2:05pm, persistent session | not recorded (persistent sessions do not log runs); session shows week ending 28 Aug delivered | HEALTHY, but the bound session has used 506k of 1M context tokens and 44.55 USD; it will hit the ceiling within weeks |
| Refund fix watch | `…VdzVKqN12nyemiu976mNca` | daily 8:15am | SUCCEEDED 3 Sep, 3 min | HEALTHY |
| Membership boards date sync | `…K4kh1m8foc2oYAv9Gs8xqo` | daily 7:37am | SUCCEEDED 3 Sep, 4 min | HEALTHY (Asana writes are passing the auto-mode check) |
| Offboarding detector | `…16nQBEZNDReT1DyrEbbqeSU` | daily 8:03am | SUCCEEDED 3 Sep, 3 min | HEALTHY by status; prompt depends on `entra-admin-cloud` tools that are not a connected connector, so the Entra half degrades silently |
| Onboarding detector | `…HiCsJkKpSUqPxq2xUpAbEo` | daily 8:38am | SUCCEEDED 3 Sep, 2 min | HEALTHY; same Salesforce queries as the offboarding detector 35 minutes earlier, consolidation candidate |
| Data feed and expiry monitor | `…Q6X1Xr1syjg7U5QGNwDSUg` | daily 9:08am | SUCCEEDED 3 Sep, 1 min | HEALTHY; prompt still reports the NetSuite OAuth2 certificate expiry as UNKNOWN every day although the register holds it (17 Sep 2026) |
| Stale case chaser (report-only) | `…S3ShSb7KSBA32LxFWaLaNa` | Mon 8:30am | SUCCEEDED 31 Aug, 2 min | OVERLAPPING: its 30-day and New-too-long checks duplicate the weekday deep slot and the pre-draft health flags; only the 14-day and 7-day stale rules are unique |
| DST fix (one-shot) | `…YY3yjtTASm7MvUCh8ceW11` | 5 Oct 2026 2pm | n/a | STALE: names 11 triggers, 6 of them retired; describes the weekday job's cron as `4 21-23 * * 0-4` when it is now `4 21-23,0-7 * * *`, so its own "skip if changed" rule will leave the main job an hour off after DST |
| Renew entra-admin-mcp certificate (one-shot) | `…Vp14cTKJCLnC7psjiRZnUC` | 26 Jul 2027 8am | n/a | HEALTHY; bound to session `session_01NtyDNj8Cb3CfjfSxpVywwX`, which must not be archived before then |

No ghost-registered rows: every trigger in the register is live.

## Decisions needed

1. Weekday dashboards job: pre-approve the Zapier action in the routine's
   tool allow list (Routines UI), or replace the two website probes with
   WebFetch and treat a blocked fetch as "unverified" rather than "down". Until
   one of these is done the job is 55 fires a week for nothing.
2. Overnight pre-draft: pre-approve `createSobjectRecord` for the routine, or
   downgrade it to report-only and let the console's approve cards do the
   writes. Either way, delete step 5 (the retired console snapshot) and turn
   the push notification on so a blocked run is visible.
3. AI Daily Ten: it is over budget and unregistered. Attach Gmail and retire
   one routine to hold at 12 (the stale case chaser is the obvious candidate),
   or pause it until a slot is freed.
4. Merge `claude/os-for-claude-y12d5q` into the default branch before Monday,
   or point the weekly audit at that branch. Otherwise the audit's first run
   cannot find the register it is meant to update.
5. Rewrite the DST fix prompt against the current 14 triggers (proposed text
   below) before 5 October.
6. Weekly status update: convert from a persistent session to fresh session
   per fire, carrying its own context in the prompt, before the bound session
   fills.
7. Small prompt fixes, approve as a batch: data feed monitor gets the NetSuite
   certificate date (17 Sep 2026); offboarding detector states what it cannot
   check without the Entra connector instead of implying it did.

## Proposed DST fix prompt (replaces the current one, not yet applied)

Sydney/Melbourne moved to AEDT (UTC+11) today. Call `list_triggers` first;
skip any trigger that is missing or whose cron already differs from the
"currently" value; never touch triggers not listed. Then `update_trigger`:

1. `trig_01HhAKnEe6PXAvo6EEq72BHo` weekday dashboards, currently `4 21-23,0-7 * * *`, set `4 20-23,0-6 * * *`.
2. `trig_01CUkTdAFSisnzyU6pwgkH4k` weekend dashboards, currently `4 21 * * 5,6`, set `4 20 * * 5,6`.
3. `trig_01V3i4b5zekjZuuFTF6Ymu9G` OS weekly audit, currently `0 20 * * 0`, set `0 19 * * 0`.
4. `trig_01EbMkfD4UcGUKLkUB1mNQ8V` overnight pre-draft, currently `30 19 * * 0-4`, set `30 18 * * 0-4`.
5. `trig_01VdzVKqN12nyemiu976mNca` refund fix watch, currently `15 22 * * *`, set `15 21 * * *`.
6. `trig_01K4kh1m8foc2oYAv9Gs8xqo` membership date sync, currently `30 21 * * *`, set `30 20 * * *`.
7. `trig_016nQBEZNDReT1DyrEbbqeSU` offboarding detector, currently `0 22 * * *`, set `0 21 * * *`.
8. `trig_01HiCsJkKpSUqPxq2xUpAbEo` onboarding detector, currently `30 22 * * *`, set `30 21 * * *`.
9. `trig_01Q6X1Xr1syjg7U5QGNwDSUg` data feed monitor, currently `0 23 * * *`, set `0 22 * * *`.
10. `trig_01S3ShSb7KSBA32LxFWaLaNa` stale case chaser, currently `30 22 * * 0`, set `30 21 * * 0`.
11. `trig_01F7wy1pGcauqCsgUxVU4b47` membership briefing, currently `0 21 * * 0,2,4`, set `0 20 * * 0,2,4`.
12. `trig_01AsdSGs9WiwRUrmbRmSxtAZ` weekly status, currently `0 4 * * 5`, set `0 3 * * 5`.
13. `trig_01Y69zEQwQtn4HcGw9Esz8ua` AI Daily Ten, currently `30 20 * * 0-4`, set `30 19 * * 0-4`.

Confirm each update, then report exactly which triggers changed with new UTC
crons and local times. The reverts on the first Sunday of April 2027 are the
"currently" values above.

## Documentation drift found

- `README.md` (lines 164 and 255) and `docs/using-the-assistant.md` (line 47)
  on the default branch cite `trig_0126KYAM3TAaZpBQKN8UeVdk`, retired on
  13 August. Annotated in this commit; the full rewrite belongs to the merge of
  the OS branch, whose README still carries the same dead ID plus
  `trig_01QKqXyfwVoUwejxBbe15gX9` (retired 2 September).
- The register's Membership Build row (Friday only) lags today's change to
  Mon/Wed/Fri.
- The register's follow-up note said to "watch the first heartbeat line" on
  3 September. That line was never written. This review is the first record
  of it.

## Budget

13 recurring active against a cap of 12. Freeing paths, cheapest first:
retire the stale case chaser after folding its two rules into the weekday deep
slot (one slot), merge the onboarding and offboarding detectors into one daily
identity scan (one slot).

## Actions taken the same evening (on Mathew's instruction)

- Retired `trig_01CUkTdAFSisnzyU6pwgkH4k` (weekend dashboards and weekly security)
  and `trig_01AsdSGs9WiwRUrmbRmSxtAZ` (Friday weekly status update). Definitions,
  attached connector lists and the persistent session id are in
  `routines/routines-backup-2026-09-03b.json`. Recurring count is now 11 of 12.
- Weekday dashboards job: website probes moved from the Zapier webhook action to
  WebFetch; the Zapier Teams post moved to after the SharePoint push, heartbeat
  and monitoring dashboard so a held approval cannot take them down; weekend
  wording updated.
- Overnight pre-draft: prints the full draft pack as text before attempting the
  Salesforce writes; the retired console snapshot step (step 5) removed.
- Data feed monitor: NetSuite OAuth2 certificate now carries its real expiry,
  17 Sep 2026, with a 14-day warning window.
- DST fix one-shot: prompt rewritten against the 11 current recurring routines.
- Offboarding detector: no change needed; its prompt already says plainly when
  the Entra bridge is unreachable.
- OS branch `claude/os-for-claude-y12d5q` merged into this branch and the default
  branch so `os/registers.md` exists where routines run.

Still only possible in the Routines UI: pre-approve the Zapier action on the
weekday job, pre-approve createSobjectRecord on the pre-draft, turn on the
pre-draft push notification, attach Gmail to AI Daily Ten.
