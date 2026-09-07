# ICT Manager Weekly Review, Monday 7 September 2026

IT-GOV-003 | Owner: Mathew Hema | Classification: CONFIDENTIAL (names deadlines and admin counts) | Week 1, so no direction of travel yet

Evidence pulled live at about 3pm AEST on 7 September 2026: Salesforce production (four SOQL queries, Zeus-scoped), Asana IT Operations Project Plan (112 incomplete tasks per get_project; the first search capped at 100 and a second search on Mathew and Keith picked up the remaining 12, all Mathew's), the scheduled task list (12 entries), the security deadline register in the birdlife-security skill. Entra, Intune and Defender figures could not be verified live; they are marked Tier 2.

## Scorecard

| Measure | This week | Target | Read |
|---|---|---|---|
| Zeus Cases open | 18 (New 6, In Progress 6, Waiting Response-External 4, Response Received 2) | New at 0 by Friday | Healthy. The queue is small and moving |
| Zeus Cases closed, last 30 days | 79 | Steady or rising | About 18 a week against 18 open. Roughly one week of work in the queue |
| Open Zeus Cases raised last 30 days, by owner | Andrew 7, Keith 3, Zeus queue 2, Nina 2, Supporter Care 1 | Zeus queue at 0 | Two sit unowned in the queue |
| Asana open tasks | 112 | Falling | 235 ever created, 123 done |
| Asana tasks with no due date | 85 of 112 | Falling every week | This is the board the team works from. Three quarters of it has no date |
| Asana overdue | 8 (three from 2025 on Sean Hellend, one on Keith from 31 Aug, four on Caroline and Merryn from 20 Aug to 1 Sep) | 0 | Five of the eight belong to people outside ICT who have been put on the ICT board |
| Blocked on a Mathew decision | 3, each blocked since at least 5 August (33 days) | 0 older than 14 days | Portal email mismatch, Plauti bulk merge permissions, Duplicate Management in Salesforce. All three titles end "decision on responsibility" |
| Tasks assigned to Mathew | 31 open, 30 with no date | Falling | The manager holds the most tasks on the board and the least dates. Fifteen of them are the January 2026 Salesforce migration block last touched in a bulk edit |
| Scheduled tasks | 10 recurring plus 2 one-shots, all last runs succeeded (6 to 7 Sep) | 12 budget | At budget. No new routine can be added without retiring one |
| Salesforce active System Administrators | 12 | 5 percent of active internal users | Down from 14 in the June baseline. Ratio still to be computed against active Standard users |

Deadlines inside 14 days, from the register (Tier 2 unless stated):

| Item | Date | Days | Owner | Verified live? |
|---|---|---|---|---|
| Vevox SAML certificate | 8 Sep | 1 | Mathew | No. Entra, Tier 2 |
| Tenant-wide MFA Conditional Access target | 15 Sep | 8 | Mathew | No. Entra, Tier 2 |
| NetSuite OAuth2 M2M certificate (orphaned) | 17 Sep | 10 | Mathew / CFO | No. NetSuite integration record, not queried this week |
| Enterprise application access review | 19 Sep | 12 | Mathew | No. Entra, Tier 2 |

Passed and still unverified: Salesforce Transaction Security Policies (13 Jul), Vevox first certificate (21 Aug), Pardot hard stop (31 Aug), the four Salesforce 1 September release updates including the OAuth change that affects MoveData. Four passed dates with no recorded outcome is itself the finding.

## Where the team's work sits (Asana, 112 open)

Mathew 31 open (1 dated, 3 in Blocked), Keith 21 (3 dated, 1 overdue), Nina 18 (0 dated, 5 in Blocked), Andrew 14 (5 dated, all 4 December), unassigned 8, people outside ICT 21 (Caroline Scales 11, Merryn Pryor 5, Sean Hellend 3, James Vilinsky 2 in Blocked, Zoë Woodford 1, Sonia Sanchez 1).

Three things are wrong with this picture. First, the manager holds 28 percent of the board personally, which is the opposite of what IT-SEC-002 is trying to build. Second, a fifth of the ICT board is other teams' Spring Cocky Count and event work, dated, while ICT's own work is undated; the board reports the wrong team's progress. Third, Nina holds five Blocked items and none of them is blocked on Nina.

## The learning this week

**Check the scope of a number before you carry it.** The birdlife-core doctrine, the open-items list of 8 August and the story told to the Executive Director all carried "4,047 Cases in New" as the ICT helpdesk backlog. Live today the org holds 4,612 open Cases and 18 of them are Zeus. The other 4,594 are programme queues: Powerful Owl 1,155, General Enquiry 925, Swift Parrot Search 636, AOC 501, Conservation Campaigns 477 and thirteen more. The query was never scoped to the record type, so a number that was true was also not about ICT. The habit that replaces it: every count that leaves this team carries its scope clause in the same sentence ("18 Zeus Cases open", not "18 Cases open"), and the verification query in the doctrine gets the WHERE clause added this week. The upside is real: the ICT backlog story is over, and the conversation with the ED becomes who owns the 4,594.

## Delegations this week (IT-SEC-002: cleanup before privilege, evidence before promotion)

| Who | Task | DONE test they run themselves | By |
|---|---|---|---|
| Andrew Dunn | Own the Zeus queue this week: take the two unowned Cases, move the six New to In Progress or close with a reason | The first SOQL in the skill returns New 0 and no Owner named "Zeus" | Fri 11 Sep |
| Keith Tsui | Date, close or hand back every one of his 21 open Asana tasks. "Close, delegate or date it", no fourth option | Asana search on Keith, completed false, project 1211042432693678, returns 0 undated | Wed 9 Sep |
| Nina Lewis | For the three "decision on responsibility" items, write a half-page each: options, recommendation, who does the work after the decision | Three comments on the three tasks, then a 15-minute slot with Mathew booked | Thu 10 Sep |

Karishma: no change this week.

## Mathew's own three

1. Tomorrow, 8 Sep: confirm the Vevox SAML certificate was renewed, or renew it. Record the outcome on the register row. Tier 2, Entra.
2. By Thu 10 Sep: make the three decisions Nina has prepared, in one sitting, and move the tasks out of Blocked. 33 days blocked is the manager's queue, not the team's.
3. By Fri 11 Sep: your own 30 undated Asana tasks, starting with the 15 January migration tasks that have not been touched since July: close, hand to Keith or Karishma with a date, or date them yourself. Same rule you are asking Keith to follow.

Also this week, because the dates do not wait: NetSuite OAuth2 certificate (17 Sep) needs the "no scheduled job uses it" check before revocation, and the enterprise application access review (19 Sep) needs the 129 reviewer decision fields filled, which was blank last quarter.

## Decisions needed

1. **Correct the doctrine.** Add `RecordType.DeveloperName = 'Zeus'` to the helpdesk backlog query in birdlife-core verification-queries.md and record the 8 August figure as org-wide. Recommendation: do it this week; the console's Security tab already scopes correctly, the doctrine file does not.
2. **Where the weekly review runs.** The routine budget is 12 of 12. Options: (a) run this review inside the existing "Claude OS weekly audit" routine (Sunday 20:00 UTC, Monday 6am AEST) as a second section, no new routine; (b) retire one routine to make room; (c) run it on demand in a Monday session. Recommendation: (a). Cost: one prompt edit with update_trigger. If wrong: the audit prompt grows and the run takes longer; reversible.
3. **Other teams' work on the ICT board.** 21 of the 112 tasks are Spring Cocky Count and event tasks owned outside ICT. Options: move them to the Citizen Science team board with a link, or keep them and accept the board reports mixed ownership. Recommendation: move, because the board is the team's standup surface. Ask Caroline first; do not move silently.

## Three lines for the team

Zeus queue is 18 open and moving, about a week's work; Andrew owns it this week and the target is zero in New by Friday.
The Asana board has 85 undated tasks and that ends this week: close it, hand it back, or put a date on it, no fourth option. Keith by Wednesday, Mathew by Friday.
Nina is preparing the three decisions that have been blocked on me since August; I will make all three on Thursday.
