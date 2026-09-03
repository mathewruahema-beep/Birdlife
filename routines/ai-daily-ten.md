# Routine: AI Daily Ten (weekdays 6:30am AEST)

**Status: live, created 3 September 2026.** Trigger `trig_01Y69zEQwQtn4HcGw9Esz8ua`,
first run 4 September 6:34am AEST. **One manual step remains:** attach the Gmail
connector to this routine in claude.ai, Routines (the API cannot attach
connectors for this organisation). Until that is done the routine reports
"Gmail unavailable" and changes nothing.

| Setting | Value |
|---|---|
| Schedule | `30 20 * * 0-4` UTC (weekdays 6:30am AEST; after the October DST change this is 7:30am AEDT until the DST fix routine adjusts it) |
| Session | fresh session per run |
| Connectors | Gmail (read-only use), plus the repo for the rep of the day |
| Notification | push on completion |
| Page | The AI Field Guide, daily block at the top: https://claude.ai/code/artifact/3dd8818e-d1c8-4b81-877f-6945e62ddc1d |
| Template | `dashboard/ai-field-guide.html` (whole page; the routine changes only the STAMP, REP, TEN and ARCHIVE marker blocks) |

## What it does

Reads the previous day's AI newsletters in Mathew's Gmail (TLDR, The Rundown,
The Neuron, AI for Work, The Deep View, Techpresso, One Useful Thing), extracts
ten hints an ICT manager can act on, each with a "Try today" line tied to
BirdLife's estate and a link to the original article, and republishes the field guide
at its existing URL, touching only the marker blocks. It also shows the AI rep of the day from
`docs/ai-practice/curriculum.md` and `log.md`, which absorbs the earlier
proposal in `ai-daily-rep-passport.md`.

## Hard rules in the prompt

Read-only on Gmail. Never fabricate a hint; fewer than ten is published as fewer.
Never repeat a hint from the five-day archive. Same artifact URL every day.
No em dashes.

## Check that proves it ran

The date in the page masthead equals today's Melbourne date, and the archive
gains one block per weekday.

## Kill switch

Disable the routine in claude.ai, Routines. Nothing else depends on it.

## Budget note

This is the thirteenth recurring routine against a cap of twelve. Decision for
Mathew: raise the cap to thirteen, or absorb this job into the overnight
pre-draft (whose last run was abandoned and needs attention anyway), or retire
one of the two Membership Build routines if their outcomes overlap.

## Register row (for os/registers.md when this lands)

| Routine | ID | Schedule | Outcome | Owner | Check |
|---|---|---|---|---|---|
| AI Daily Ten | trig_01Y69zEQwQtn4HcGw9Esz8ua | weekdays 20:30 UTC | Ten hints and rep of the day on the AI Field Guide | Mathew | Stamp date equals today |
