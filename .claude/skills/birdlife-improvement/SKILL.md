---
name: birdlife-improvement
description: The continuous-improvement loop for BirdLife Australia ICT: how a session or the console watches processes (queue patterns, board drift, money gaps, security posture, incidents, routine failures), turns what it sees into a ranked, owner-named fix on the console's Fixes tab, tracks the fix into Asana, verifies it landed, and writes the learning back into the skills so the next session starts smarter. Use for "what should we fix", "quick wins", "why does this keep happening", "propose a fix", "suggest improvements", "lessons learned", "post-incident review", "process review", "retro", or whenever a recurring problem, a workaround that became permanent, or a fixed issue should be captured as knowledge. Trigger on "fix", "fixes", "improve", "improvement", "quick win", "recurring", "again", "lesson", "learn", "retro", "post-mortem", "process", "workaround", "root cause".
---

# BirdLife Australia: the improvement loop

The organisation's problem is not a shortage of findings. It is that findings
sit in documents (the Jun 2026 security reviews, the Jul 2026 NetSuite
review, the WordPress health check) and nothing turns them into owned,
dated work, and nothing records what was learned when they are done. This
skill is the loop that fixes that: **observe, propose, decide, track, verify,
learn.** The console's **Fixes tab** is the working surface; the skills are
the memory; Asana is the tracker; the registers are the record.

## The loop

```
observe  →  propose  →  decide  →  track  →  verify  →  learn
 signals     fix card    Mathew    Asana     re-read    skill edit
 (live +     (ranked,    accepts/  task via  + status   + register
  skills)    owned)      dismisses approval  done       + Fixes seed
```

Every stage has a rule that stops the loop degrading into a to-do list:

1. **Observe from evidence, not memory.** A signal is a live read (queue,
   board, money, security snapshots, routine health) or a dated fact in a
   skill. "I think this is a problem" is not a signal.
2. **Propose in the fix format** (below), ranked Mathew's way: money first,
   then what blocks people, then risk, then everything else. Never propose
   more than three at once; the fourth is noise.
3. **Decide is Mathew's** (or the owner he names). A fix is proposed until a
   human accepts or dismisses it. Dismissed with a reason is a valid outcome
   and gets recorded.
4. **Track one fix, one task**, in Asana Backlog/Requests with owner and due
   date, behind an approval card. No bulk creation.
5. **Verify by re-read.** Done means the control is observed in the system
   (the policy is on, the account is disabled, the count moved), not that
   someone said so.
6. **Learn in the same piece of work.** The owning skill gets the outcome,
   the gotcha, the new ID or the changed process, committed with the fix.
   A fix that is done but not written down will be rediscovered in three
   months.

## The fix format (what the Fixes tab and `fix_propose` expect)

| Field | Rule |
|---|---|
| `id` | kebab-case, stable, never reused |
| `title` | imperative, one line, names the system ("Turn off public self-registration defaulting to Shop Manager") |
| `system` | the system of record it changes |
| `cat` | `money`, `process`, `security`, `data`, `estate` |
| `sev` | 1 critical (money leaking, breach path, hard deadline inside 14 days), 2 high, 3 medium |
| `tier` | 1 execute (console or session after approval), 2 prepare for an admin, 3 design for a developer |
| `effort` | `minutes`, `hours`, `project` |
| `owner` | a named person, never "the team" |
| `why` | one or two sentences of evidence with its date |
| `people` | who is affected and how; this is the sentence that gets the fix accepted |
| `steps` | two to six concrete steps, verifiable, in order |
| `src` | the skill or live read it came from; Jarvis additions carry `jarvis <date>` |

The **impact on people** line is mandatory because Mathew's own standard is
"I need an explanation and impact on people I am working with." A fix without
it is a technical preference, not a proposal.

## Where signals come from, and what each usually means

| Signal | Read it from | Typical fix category |
|---|---|---|
| Same sub-type recurring in the Zeus queue | `SELECT SC_Additional_Enquiry_Type__c, COUNT(Id) FROM Case WHERE RecordType.DeveloperName='Zeus' AND CreatedDate = LAST_N_DAYS:90 GROUP BY SC_Additional_Enquiry_Type__c` | process or automation |
| Cases ageing in New | console Today tab; New vs In Progress ratio | process (acknowledgement) |
| Board items Blocked or Awaiting Response over 14 days | console Projects tab | process (chase, decide, or kill) |
| Asana "Consider delegating X's tasks" prompts | board | people lifecycle miss |
| Lens gap between Stripe, Salesforce, NetSuite | console Money tab | money |
| Sysadmin ratio, never-logged-in admins, overdue deadline | console Security tab | security |
| A routine failed, ran idle, or overlaps another | `list_triggers` vs `os/registers.md` | estate |
| An incident (phishing, outage, wrong charge) | the Case, the vendor thread | security or process, always with a learn step |
| A workaround the team does by hand every week | inbox and Teams themes, standups | process or automation |
| A fact in a skill dated more than 90 days ago | the skill file | data (re-verify) |

## Working the Fixes tab (console)

- **Tiles**: critical open, quick wins (minutes and high impact), in
  progress, done percentage, Jarvis-suggested count. Tap a tile to filter.
- **Filters**: text search, category chips, severity, tier, status, sort
  (Mathew's ranking, quickest first, by system). Reset restores the defaults.
- **Card**: severity pill, title, system, tier, effort; expand for why,
  impact on people, steps, owner, source. Status dropdown per card.
- **Actions**: *prepare with jarvis* (exact commands in order, verification,
  a one-line message to the owner in Mathew's voice), *track in asana*
  (one task, approval card, verified), *draft the nudge* (register B message
  to the owner), *copy runbook*, *mark done*, *remove suggestion* (Jarvis
  additions only).
- **Ask Jarvis for new fixes**: Jarvis reads the live snapshots and the
  catalogue, proposes at most three that are not already listed, adds them
  tagged `jarvis`, and names the one to do first.
- **Persistence**: status and Jarvis additions are stored in that browser
  only. The durable record is the Asana task and the skill edit. This is
  deliberate: a page must never be the system of record.

Jarvis tools: `fixes_catalog` (read, with filters), `fix_propose` (add),
`fix_status` (progress), `fix_track` (Asana task, approval card, one per
call, verified by re-read, sets status accepted).

## The learn step, in detail (this is the part everyone skips)

When a fix reaches done, in the same session:

1. **Owning skill**: record the outcome where the finding lived. The
   security posture register gets the new number and date; the WordPress
   skill loses the "anyone can register" finding and gains "fixed 3 Sep,
   verified by ..."; a new ID or gotcha goes in the observed-behaviour
   section.
2. **Registers**: credential watchlist row closed with who verified; deadline
   register row gets its outcome; connector or routine register if the estate
   changed.
3. **Fixes seed**: remove the item from `FIXES_SEED` in
   `os/claude-os-overview.html` (or leave it with status done if it should
   stay visible for a fortnight), and republish.
4. **Pattern check**: ask whether the fix is a symptom. Two fixes in the same
   place (two leaked keys, two departed admins) is a process fix, and that
   becomes the next proposal.
5. **Commit** with the fix described; push; the account skill copy is
   re-uploaded at the next sync.

For an incident, the learn step is a short post-incident note in the
`birdlife-security` skill under the relevant playbook: what happened, what
detected it, what would have detected it sooner, what changed.

## Cadence

- **Daily**: Jarvis "Quick wins" chip when opening the console; do one.
- **Weekly (Monday, with the OS audit)**: review the Fixes tab: anything
  accepted but not tracked, tracked but not moving, done but not learned.
  Ask Jarvis for new fixes once.
- **Monthly**: re-verify any fact in the skills older than 90 days that a
  fix depends on; retire dismissed fixes older than 60 days from the seed.
- **Per incident**: propose, track and learn within the week.

## Operating rules

1. **Evidence first.** No fix without a dated signal.
2. **Three at a time.** More is a list nobody reads.
3. **Impact on people or it is not a proposal.**
4. **One task per approval.** Never bulk-create.
5. **Done is observed, not announced.**
6. **Learn in the same commit.** The skill is the memory; the page is a
   mirror.
7. **Tier honesty.** A tier 2 or 3 fix is prepared, and the preparation is
   the deliverable; never mark it done because the script was written.
