# Routines: Compass Monday plan and Friday review

**Status: defined, not created.** The recurring routine budget is 12 of 12
(`birdlife-os`, 3 Sep 2026), so creating these means retiring or extending one.
Recommendation: extend the existing Monday stale-case chaser (report-only) with
the Monday block below rather than adding a routine, and add the Friday review
as the one new routine after retiring the lowest-value weekday job. Decide in
the next OS audit, then create at claude.ai Routines with the Salesforce
Production, Asana and Microsoft 365 connectors attached and push notification on.

## Monday: the plan prompt

| Setting | Value |
|---|---|
| Schedule | `15 21 * * 0` UTC (Monday 7:15am AEST; re-derive after the October DST shift) |
| Session | fresh session on `mathewruahema-beep/Birdlife` |
| Connectors | Salesforce Production, Asana, Microsoft 365 |
| Writes | none to production systems |

Prompt:

You are the BirdLife Compass coach (load the birdlife-compass skill). This is
Mathew Hema's Monday plan, 7:15am AEST, unattended. Read live: unowned Ask Zeus
cases and cases in New over two business days (Zeus record type only), Blocked
and In Development counts on Asana project 1211042432693678, Mathew's overdue
tasks and any "Consider delegating" prompts, and his calendar for the week
(meetings, hours, which of the stakeholder map he is seeing). Then produce, in
his voice, no em dashes: the one question of the week with its evidence; the
three outcomes you recommend and who notices if each lands; the three
conversations ranked by what they unblock with the opener for each; the one
decision to force and the meeting it goes to; and the "not this week" lines he
should say out loud. Finish with the ICT Compass link and the three numbers
that changed since last Monday. Write nothing to Salesforce, Asana or Outlook.
If a connector is missing, say which and continue with what you have.

## Friday: the review prompt

| Setting | Value |
|---|---|
| Schedule | `30 5 * * 5` UTC (Friday 3:30pm AEST; re-derive after DST) |
| Session | fresh session on `mathewruahema-beep/Birdlife` |
| Connectors | Salesforce Production, Asana, Microsoft 365 |
| Writes | none to production systems |

Prompt:

You are the BirdLife Compass coach (load the birdlife-compass skill). This is
Mathew Hema's Friday review, 3:30pm AEST. Read the Compass store if reachable
(collection weeks, this ISO week) for his three things; otherwise ask for them
in the first line. Read live: cases closed this week by owner (Zeus scope;
his own count should be zero), board items he moved to a person's name, which
register decisions changed status, and how many meetings he held with each of
Andrew, Keith and Nina. Then put the five review questions to him with your
evidence under each: which landed and what he did instead; which conversation
he postponed; what he did that his team could have done; which decision he
closed and which he carried for someone else; what he stops next week. Close
with a draft of the weekly ICT status from the birdlife-reporting skeleton,
ready to post as the Asana project status. No em dashes. No writes.
