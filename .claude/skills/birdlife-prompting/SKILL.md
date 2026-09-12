---
name: birdlife-prompting
description: "Rewrite and challenge every BirdLife Australia prompt into the six-line frame (Outcome, Evidence, Tier, Deliver, People, Done) using the context of the system in play, routing to the right birdlife-* skills, verifying live before building and closing the loop."
---

# BirdLife prompting frame

This skill runs first on every BirdLife Australia request, before any system skill does work. It exists because the record since August 2026 shows four repeat costs: sessions that restart cold, deliverables that need a second pass, Tier 2 work that stalls between design and execution, and more output than a team of four can absorb. The human copy is `GoogleDrive\Claude\BirdLife_Prompt_Playbook.md` (ADR 0021). `birdlife-core` (in the birdlife-ict plugin) is the rulebook underneath; this skill applies it to the prompt itself.

## Step 1. Work out which system Mathew is looking at, and load its skill

Read the request, any pasted text, the connectors in use and the folder path. Match to this table and read the named skills before rewriting the prompt. Several rows can apply.

| Signal in the request | Skills to load |
|---|---|
| Case number 00137xxx, "ticket", Zeus queue, requester reply | birdlife-ict-assistant, birdlife-salesforce, email-voice |
| Contact, Opportunity, membership, donation, receipt, SOQL, Payments2Us, miniOrange, Raisely, duplicates, staging sandbox | birdlife-salesforce |
| Mailbox, licence, MFA, Conditional Access, Entra, Intune, Defender, SharePoint, Teams, birdlife.org.au UPN | birdlife-microsoft365, birdlife-security |
| New starter, leaver, role change, contractor, "still has access" | birdlife-people-lifecycle, birdlife-microsoft365, birdlife-salesforce, birdlife-security |
| GL code, journal, bank rec, reconciliation, SuiteQL, payroll, Business Central | birdlife-netsuite, birdlife-stripe when payments are involved |
| Charge, refund, payout, webhook, BECS, payment discrepancy | birdlife-stripe, birdlife-salesforce, birdlife-wordpress |
| Website, WooCommerce, plugin, WP Engine, Blitzm, membership rebuild | birdlife-wordpress, birdlife-salesforce |
| Zap, catch hook, connect X to Y, LearnUpon, Humanitix, Campaign Monitor | birdlife-zapier |
| DNS, SPF, DKIM, WAF, cache, Cloudflare | birdlife-cloudflare |
| Asana task, board, backlog, assign, due date | birdlife-asana |
| Security, posture, Essential Eight, admins, phishing, breach, certificate expiry, access review | birdlife-security |
| Report, brief, paper, status update, one-pager, "write this up", CEO or CFO or Board audience | birdlife-reporting, plus the Board Paper Word template |
| Email, reply, draft, forward, Case comment text | email-voice |
| Routine, scheduled task, dashboard, console, Jarvis, artefact, skill sync, "what is running" | birdlife-os |
| Programme highlight document or deck | birdlife-programme-pack |

If nothing matches, load birdlife-core alone and say the request does not map to a known system.

## Step 2. Rewrite the prompt into the frame

Using what the loaded skills know (the system's traps, its ADRs, its verification queries) and the live connector state, restate the request as exactly this block. Fill any line Mathew left out from that context and mark it (assumed).

```
OUTCOME   what is different at BirdLife when this is done, one sentence, no file names
EVIDENCE  what will be verified live first, naming the system and the figure and the query
TIER      1 execute / 2 prepare for Mathew to run / 3 design only
DELIVER   one primary deliverable and where it lands (Google Drive path and IT ID, artifact, Asana, Case)
PEOPLE    who is affected and what they must do differently, by name
DONE      the test that proves it worked: a query, a screenshot, a number, a date
```

## Step 3. Question it and make it better

Under the frame, add a short block headed "Challenges". Say plainly, against the record in the loaded skills and ADRs:

1. What is vague in the request and how you resolved it.
2. What in the request is wrong or stale (a figure that is older than 30 days, a fact the skill contradicts, a step the record shows fails, such as licence removal before mailbox conversion, or a duplicate Salesforce User record).
3. What the request as written would produce that is not needed yet, and the thinner version that lands something.
4. Where it asks for "all of" several deliverables, the decision-first alternative: three options, a recommendation, team hours by person, what breaks if wrong.

Then present the improved prompt as one block Mathew can approve with a word. If every line is clear and nothing was assumed or challenged, skip the pause and proceed. If one assumption changes the build, ask that one question, never more. If Mathew is clearly unattended, state the assumptions and proceed.

## Step 4. Execute under the doctrine

- Evidence before assertion: refresh every figure from the live connector using the skill's verification queries. If Mathew's number differs from live by more than 10%, say so and which layer was stale.
- Open by proving state, not describing it: check the two or three things that establish which phase the work is at, report, then act.
- Decide before building for anything longer than one session or touching money, identity, production Salesforce or a vendor. A decision is not made until the dated ADR exists.
- One session, one shippable thing. Thin slice first, widen after it is proven live.
- Tier 2 deliverables are the executable (exact PowerShell, click-path, proving SOQL) plus a named runner and a calendar slot or Asana task, never a design document. Say the tier out loud.
- Red-team before executing: three ways this goes wrong at BirdLife specifically, drawn from the loaded skill's recorded failures, and what prevents each. Knowingly accepted risks become an ADR of Type: Risk acceptance naming Mathew as acceptor.
- People impact is mandatory, naming Andrew Dunn (level 1), Keith Tsui (junior Salesforce developer), Nina Lewis (finance link), Karishma Soni (external Salesforce developer), staff, supporters or the Board as relevant. Where a team member can check the DONE test instead of Mathew, say who.

## Step 5. Close the loop before the session ends

When a decision was made, the estate changed, or a deliverable was produced, finish without being asked:

1. ADR written if a decision was made.
2. The affected birdlife-* skill updated with any durable fact learned; live figures go into verification queries as queries, never as values.
3. Every dated open item into Asana with an owner.
4. Deliverable filed to Mathew's Google Drive under the next free IT-xxx-nnn ID after checking existing IDs (IT-SEC-006 and IT-SF-005 were each used twice).
5. What in memory is now stale.
6. Three lines Mathew can send to the team.

## Style

Frank and logical. Challenge the request when the record says it will not work, and always give the workable path rather than a bare no. No em dashes. BirdLife documents use the Board Paper Word template. Deliverables are saved to Google Drive, not only sent in chat.