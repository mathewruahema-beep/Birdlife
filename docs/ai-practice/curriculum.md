# AI practice curriculum: thirty reps

One rep per weekday, each on real BirdLife work, each under thirty minutes. The
reps follow the five habits in [`../ai-usage-guide.md`](../ai-usage-guide.md),
then governance and remote work. Score each rep in [`log.md`](log.md):

| Score | Meaning |
|---|---|
| 1 | Attempted, did not finish or did not land |
| 2 | Done as written |
| 3 | Done and it changed something: a skill edit, a decision, a number, a closed case |

A rep counts as done at score 2 or above. After rep 30 the coach cycles back to
the lowest-scored reps, then to harder variants. Ask any session for "today's rep".

## Week 1: State the outcome, not the task

| # | Rep | Do this | Done when |
|---|---|---|---|
| 1 | The four-part prompt | Take the next real ticket. Write the prompt as Context, Goal, Constraints, Done-when before you send it. [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). | The assistant asked zero clarifying questions. |
| 2 | Name the output shape | Ask for a specific shape: "a table with columns Case, Owner, Age, Next action". [Prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview). | You used the output without reformatting it. |
| 3 | Give one example | Paste a past reply you were proud of and say "match this register". | The draft needed under two edits. |
| 4 | Recommendation, not summary | Replace "summarise case X" with "tell me what to do about case X and why". | You acted on the recommendation. |
| 5 | Constrain the scope | Add a limit: "read only", "three options maximum", "do not touch Asana". | Nothing was done that you did not ask for. |

## Week 2: Teach it once, in writing

| # | Rep | Do this | Done when |
|---|---|---|---|
| 6 | Capture the correction | Find the correction you made most often this week. Write it into the right skill under `.claude/skills/`. [How Claude remembers your project](https://code.claude.com/docs/en/memory). | Committed and pushed. |
| 7 | Read CLAUDE.md as a stranger | Read the charter cold. Delete or sharpen one line that a new session would misread. | Committed. |
| 8 | Add a gotcha with the real value | Add a picklist value, ID or failure mode to a skill's reference file. [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). | A fresh session recalls it unprompted. |
| 9 | Resolve one drift | Compare one repo skill with its account copy. Make them identical. | No diff. |
| 10 | Playbook entry | Something you asked for three times this week becomes a line in the prompt playbook in `docs/using-the-assistant.md`. | Committed. |

## Week 3: Make it prove it

| # | Rep | Do this | Done when |
|---|---|---|---|
| 11 | Show the query | On any report, ask "show the SOQL you ran and the row count". Check it is scoped to `RecordType.DeveloperName = 'Zeus'`. | The numbers match Salesforce. |
| 12 | Dry run first | Add "dry run" to a write. Compare the preview with what the real write then did. | Preview and write matched. |
| 13 | Before and after | After a case write, ask for the re-query and the audit comment. | You saw both. |
| 14 | Red-team a draft | Before sending a requester reply, ask "what in this could be wrong or misread?" [Best practices](https://code.claude.com/docs/en/best-practices). | One change made. |
| 15 | Catch it lying | Ask about a system detail you already know cold. Check the answer. | Logged right or wrong. If wrong, the skill is fixed. |

## Week 4: Delegate the recurring, keep the judgement

| # | Rep | Do this | Done when |
|---|---|---|---|
| 16 | The by-hand list | List everything you did by hand this week with the same shape. Circle one. [Routines](https://code.claude.com/docs/en/routines). | The list is in the log. |
| 17 | Read the routine register | Which routine last failed or was abandoned, and why? Use the birdlife-os skill. | One decision made: fix or retire. |
| 18 | Write the passport | Draft a routine passport for the rep 16 pick, in the shape of `routines/overnight-pre-draft.md`. | Passport saved under `routines/`. |
| 19 | Define the check | For one live routine, write what proves it ran correctly. | The check is in its prompt or its register row. |
| 20 | Workflow or agent | Read [Building effective agents](https://www.anthropic.com/research/building-effective-agents). Write three lines on which of your routines are workflows and which are agents. | Written in the log. |

## Week 5: Think with it, not through it

| # | Rep | Do this | Done when |
|---|---|---|---|
| 21 | Argue the other side | Before a decision, ask it to make the strongest case against you. [One Useful Thing](https://www.oneusefulthing.org/). | You changed or reconfirmed, with the reason logged. |
| 22 | Pre-mortem | "It is three months on and this project failed. Why?" | One mitigation added to the plan. |
| 23 | The CFO's questions | Before a money conversation, ask "what will the CFO ask?" | You had every answer ready. |
| 24 | Explain it back | Describe a BirdLife system in one paragraph and ask what is missing. | One real gap found. |
| 25 | Three options, then choose | Ask for three options with trade-offs. Pick one yourself. | Decision and reason in the log. |

## Week 6: Governance and remote

| # | Rep | Do this | Done when |
|---|---|---|---|
| 26 | Score against the OAIC checklist | Work through the "using" checklist in the [OAIC AI guidance](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/guidance-on-privacy-and-the-use-of-commercially-available-ai-products). | Gaps listed. |
| 27 | One-page AI use policy | Draft it with the [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) functions as headings: Govern, Map, Measure, Manage. | Draft in `docs/`. |
| 28 | Prompt injection drill | Give the assistant a made-up ticket whose body contains instructions ("close all cases"). See what it does. [OWASP LLM Top 10](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/). | Behaviour logged. Guardrail fixed if it obeyed. |
| 29 | Phone end to end | Work one case from the phone only: triage, draft, post, close with reason. [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web). | Case closed with an audit comment. |
| 30 | The number | Count cases closed this month with an assistant draft versus without. | The number is in the log and in the guide's status section. |
