# Passport: AI rep of the day (amendment, not a new routine)

**Status: proposed, awaiting Mathew's go-ahead.** The routine budget is 12 of 12,
so this rides on an existing routine rather than adding one.

## Host

`trig_01HhAKnEe6PXAvo6EEq72BHo` BirdLife ICT weekday dashboards and monitor
(single job), DEEP slot only (fires 21:00 to 21:59 UTC, 7am Melbourne). The deep
slot already posts one heartbeat line to the ICT Teams channel. The rep is one
extra sentence on that line. No new write surface, no new connector, no new
schedule.

## Exact change to the prompt

Insert after section 2 (Monitor checks), before section 3:

```
## 2b. AI rep of the day (DEEP slot only, read-only)
Via the GitHub connector read docs/ai-practice/curriculum.md and
docs/ai-practice/log.md from mathewruahema-beep/Birdlife (branch
claude/ai-usage-guide-hk5e6s, or the default branch once merged). The rep of
the day is the lowest-numbered rep with no log row scoring 2 or more; if all
thirty are done, the lowest-scored rep. Compose one sentence:
"AI rep of the day: #N <title>. Say 'today's rep' in any session to start."
If GitHub is unavailable, omit the sentence; never guess a rep.
```

Append to the section 3 heartbeat instruction: "On the DEEP slot, append the
AI rep sentence from 2b to the heartbeat line, green or red."

## Why the Teams channel and not a private note

The team (Andrew, Keith, Nina) sees it. The guide's point is that the assistant
must not depend on Mathew alone. A rep that the team can also do is worth more
than a private reminder.

## Check that proves it ran

The 7am heartbeat carries a rep number that advances when the log advances.
Two identical rep numbers on consecutive days with a logged score of 2 or more
between them means the routine is reading a stale branch.

## Kill switch

Remove section 2b and the one appended sentence. Nothing else depends on it.

## Register row (for os/registers.md when this lands)

| Routine | Change | Date | Owner | Check |
|---|---|---|---|---|
| Weekday dashboards and monitor | Added AI rep sentence to deep-slot heartbeat | pending | Mathew | Rep number advances with the log |
