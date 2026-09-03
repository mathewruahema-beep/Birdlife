# Getting better with AI: a working guide

For Mathew Hema, Senior Manager ICT. Written 3 September 2026. Read time about ten
minutes. Every link was checked on the day of writing. A phone-readable copy is
published at https://claude.ai/code/artifact/3dd8818e-d1c8-4b81-877f-6945e62ddc1d
(private to Mathew; republish it from this file when the guide changes).

The thesis in one line: AI makes you faster only when you give it context, make it
verify, and give it somewhere to remember. Without those three it makes you
confidently wrong, faster. Everything below serves those three.

---

## 1. Where you actually are

You are ahead of most ICT managers. This repo already has a charter
([`CLAUDE.md`](../CLAUDE.md)), nine operator skills versioned in `.claude/skills/` (more on your claude.ai account), a
phone console, four scheduled routines and a three-tier honesty model for what the
assistant executes versus prepares. That is a real operating system, not a chatbot.

The honest gaps:

- **Usage is reactive.** Most sessions start from a ticket. The leverage is in the
  work you have not asked it to do yet: pre-drafting, pattern spotting, reporting.
- **Knowledge drifts.** The skills in the repo and the copies on your claude.ai
  account diverge. A gotcha fixed in one and not the other is a bug you will hit again.
- **Nothing is measured.** You cannot say how many cases per week the assistant
  closed, or how much time a routine saved. Without that number the Board and the
  CFO will treat this as a hobby.
- **Tier 2 is the ceiling.** Entra and Exchange admin work is still prepared, not
  executed. The plan to fix that is in
  [`entra-admin-connector.md`](entra-admin-connector.md). Until it lands, remote
  work stops at the point of admin action.

---

## 2. Five habits that make the difference

**Habit 1: State the outcome, not the task.** Weak: "look at case 139005". Strong:
"Case 139005: tell me the root cause, the fix, and draft the requester reply in my
voice. Done when the case can be closed with a reason." The pattern is
Context, Goal, Constraints, Done-when, Output shape. Anthropic's
[prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
and the
[prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
cover the mechanics. Ten minutes there pays back every day.

**Habit 2: Teach it once, in writing.** Every time you correct the assistant and do
not write it into a skill, you will correct it again next week. The rule is that a
correction becomes a skill edit the same day. How memory works is in
[How Claude remembers your project](https://code.claude.com/docs/en/memory) and how
skills work is in
[Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
Anthropic's
[context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
post explains why short, specific instructions beat long ones.

**Habit 3: Make it prove it.** Never accept "done". Ask for the re-query, the
record ID, the before and after. The assistant already re-queries Salesforce after
a write. Extend that to everything: "show me the SOQL you ran and the row count."
The [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
page calls this giving the agent a signal it can read. It is the single biggest
predictor of whether output is trustworthy.

**Habit 4: Delegate the recurring, keep the judgement.** Anything you do weekly
with the same shape belongs in a
[routine](https://code.claude.com/docs/en/routines): the stale-case chase, the
Monday status, the security posture read. A routine needs three things or it does
not go live: a named owner, a check that proves it ran correctly, and a way to
switch it off. Anthropic's
[Building effective agents](https://www.anthropic.com/research/building-effective-agents)
makes the case for simple workflows over clever agents. Believe it.

**Habit 5: Think with it, not through it.** The best use of AI for a manager is as a
sparring partner, not a typist. Before a decision, ask it to argue the other side,
run a pre-mortem, or list what the CFO will ask. Ethan Mollick's
[One Useful Thing](https://www.oneusefulthing.org/) and his book
[Co-Intelligence](https://www.penguinrandomhouse.com/books/741805/co-intelligence-by-ethan-mollick/)
are the best plain-language treatment of this. Keep the decision yours.

---

## 3. Working remote: the phone playbook

- **From anywhere:** open [claude.ai/code](https://claude.ai/code) on the phone and
  start a session on this repo. The charter and skills load automatically. Sessions
  keep running when you close the browser and you can watch them in the Claude
  mobile app. Details in
  [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web).
- **Quick triage:** the console artifact linked in
  [`using-the-assistant.md`](using-the-assistant.md) shows the live queue and the
  Asana board and can post and close from a phone.
- **Queue work from a locked-down machine:** open a GitHub issue on this repo and
  start a session from it.
- **While you sleep:** the routines in `routines/` run the dashboard refresh, the
  stale-case chase and the morning brief. Check their run status weekly in
  claude.ai under Routines, because a quiet routine and a broken routine look the same.
- **The honest limit:** account creation, licences, mailbox access and MFA resets
  still need an admin to run the prepared PowerShell. Remote work is real up to
  that line. Landing the Entra admin connector moves the line.

---

## 4. The rules you will be held to

You set the security bar for BirdLife, so your AI use has to clear it. These are
the documents an auditor, the Board or the OAIC would measure you against:

- [OAIC guidance on privacy and commercially available AI](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/guidance-on-privacy-and-the-use-of-commercially-available-ai-products).
  Two checklists: selecting a product and using it. Members' and donors' data is
  personal information under the APPs. Do not paste it into unmanaged tools.
- [Voluntary AI Safety Standard](https://www.industry.gov.au/publications/voluntary-ai-safety-standard)
  from the National AI Centre. Ten guardrails. Human oversight, record keeping and
  transparency are the three you already partly meet through the propose-then-write
  rule and the internal audit comment on every write.
- [ASD's Engaging with artificial intelligence](https://www.cyber.gov.au/business-government/secure-design/artificial-intelligence/engaging-with-artificial-intelligence).
  Sits alongside the
  [Essential Eight](https://www.cyber.gov.au/business-government/asds-cyber-security-frameworks/essential-eight/essential-eight-maturity-model)
  you already report on.
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/).
  Two entries matter to you directly. Prompt injection: a ticket body or an email
  can carry instructions aimed at the assistant, so it must never act on content
  from a requester without you seeing it. Excessive agency: every connector you
  attach widens what a mistaken session can do. Scope them, and keep the no-bulk,
  no-delete guardrails.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).
  Govern, Map, Measure, Manage. Useful as the skeleton for a one-page BirdLife AI
  use policy, which you do not yet have and will be asked for.

---

## 5. A thirty-day plan

| Week | Do this | Time |
|---|---|---|
| 1 | Take the Anthropic Academy intro course at [anthropic.skilljar.com](https://anthropic.skilljar.com/) and read the prompting best practices. Rewrite your five most-used prompts using the Context, Goal, Constraints, Done-when pattern. | 2 hrs |
| 2 | Read [best practices](https://code.claude.com/docs/en/best-practices) and [memory](https://code.claude.com/docs/en/memory). Pick the skill you correct most often and rewrite it. Re-sync the account copies. | 2 hrs |
| 3 | Build one reporting routine with an owner, a check and a kill switch. Candidate: the weekly ICT status draft in your voice. | 2 hrs |
| 4 | Read the OAIC checklists and write a one-page BirdLife AI use policy using the NIST four functions as headings. Put it to the CEO. | 3 hrs |
| Beyond | The ranked [learning ladder](ai-practice/learning-ladder.md): free courses this week, Copilot admin and agent skills this month, AI-900 this quarter, and the ISACA AAISM path for a security manager over twelve months. | see ladder |
| Ongoing | [One Useful Thing](https://www.oneusefulthing.org/) weekly. [Anthropic engineering blog](https://www.anthropic.com/engineering) monthly. The [Microsoft 365 Copilot administration path](https://learn.microsoft.com/en-us/training/paths/explore-microsoft-365-copilot-agent-administration/) before staff ask you for Copilot, because they will. | 30 min a week |

---

## 6. What this means for the people around you

- **Andrew, Keith and Nina** should be using the same skills, not routing through
  you. If you are the only person who can drive the assistant you have built a
  single point of failure with your own name on it. Share the console and the
  prompt playbook, and let them add gotchas to the skills.
- **Requesters** should see faster, clearer replies in a consistent voice. They do
  not need to know a draft was AI-assisted, but nothing goes out you have not read.
- **The CEO and Board** need one number and one page: time saved or cases closed
  per week, and the policy from week four. Bring both or expect the question.

---

## 7. The daily loop

Reading this once changes nothing. The loop is what compounds:

1. **Morning:** say `today's rep` in any session, on the phone or the desktop.
   The coach picks the next rep from
   [`ai-practice/curriculum.md`](ai-practice/curriculum.md) and ties it to a
   live case or task. Thirty reps, one per weekday, under thirty minutes each.
2. **During the day:** bring any decision with `think with me`. The coach runs
   a fixed frame: the decision in one line, facts versus assumptions versus
   unknowns, three options with who each lands on, the strongest case against,
   a recommendation with reversibility, and what evidence would change it.
3. **End of session:** say `coach me`. It quotes the prompts you actually wrote,
   shows the stronger version, names your weakest habit that day, and logs it.
4. **Friday:** say `weekly AI review`. Reps done, average score, streak, weakest
   habit, one proposed change.

Everything is recorded in [`ai-practice/log.md`](ai-practice/log.md) with a date,
a score and evidence. That log is the number the Board will ask for. The push
version, one sentence on the 7am Teams heartbeat, is proposed in
[`../routines/ai-daily-rep-passport.md`](../routines/ai-daily-rep-passport.md)
and waits on your go-ahead.

---

## 8. Five questions every Friday

1. What did I correct this week that is not yet written into a skill?
2. Which routine ran, and did I check its output, or just assume?
3. What did I accept without seeing the proof?
4. What recurring thing did I do by hand that should be a routine?
5. What decision did I make this week where I should have asked it to argue the other side?

---

## 9. Stop doing these

- Re-explaining context every session. If it is not in a skill, that is the fix.
- Accepting a summary when you needed a decision. Ask for the recommendation.
- Building more routines than you can supervise. Four you check beat ten you do not.
- Treating the console as finished. It is a tool that should change with the queue.
- Pasting PII into anything that is not a governed connector.
