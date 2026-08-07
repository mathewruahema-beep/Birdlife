# Zeus Assist — an AI chat for resolving IT issues

A Claude-backed assistant for the *Ask Zeus* ICT queue, plus the practice around it.

| | |
|---|---|
| System prompt | [`instructions.md`](instructions.md) — the whole behaviour spec |
| Grounding | [`knowledge/`](knowledge/) — environment facts and runbooks |
| Acceptance tests | [`eval/scenarios.md`](eval/scenarios.md) — run before trusting it |
| API version | [`client/chat.py`](client/chat.py) — only if you need it embedded |

---

## Decide two things first

Most helpdesk AI projects fail because these were never separated.

### 1. Who is it for?

|  | **A — Technician assistant** | **B — Staff self-service** |
|---|---|---|
| Users | The four of you | ~150 staff |
| Value | Faster resolution, consistent replies | Ticket deflection |
| Risk if wrong | A technician spots it | A staff member acts on it |
| Effort | An afternoon | A project — hosting, SSO, guardrails, support |

**Start with A.** Not because B is wrong — the README's own finding is that there is
no self-service channel at all, and 20% of volume is repetitive identity work, so B is
where the actual saving lives. But A costs an afternoon and tells you whether the
model is any good at *your* cases before you put it in front of 150 people. If it
can't reproduce resolutions your team already found (test 10), B would have shipped a
confident wrong answer to the whole organisation.

Everything in this directory is A.

### 2. Claude Project or API?

| | **Claude Project** | **API (`client/chat.py`)** |
|---|---|---|
| Build | Paste `instructions.md`, upload `knowledge/` | Python, a key, somewhere to run it |
| Cost | Included in the Claude plan | Per token, plus hosting |
| Who can use it | Anyone you share the project with | Whatever you build |
| Embeddable | No | Yes — dashboard, Teams bot |

**Use the Project.** For four technicians it is the right tool, and the API buys you
nothing they need. Reach for `chat.py` only when you want the assistant somewhere
Claude isn't — inside `dashboard/ict-dashboard.html`, or behind a Teams bot.

Both read the same `instructions.md`, so the choice is reversible.

---

## Build it — Claude Project

1. **Claude → Projects → Create project.** Name it *Zeus Assist*.
2. **Custom instructions** — paste all of `instructions.md`.
3. **Project knowledge** — upload every file in `knowledge/`.
4. **Share** with the four ICT accounts. Don't share organisation-wide.
5. Run [`eval/scenarios.md`](eval/scenarios.md) before anyone relies on it.

Budget an hour for step 5 and the `TODO`s it exposes. That hour is the difference
between a useful assistant and a plausible one.

---

## Best practice — the parts that matter

### Use the work account, not a personal one

Put this on BirdLife's Claude Team or Enterprise workspace, under a work account —
not a personal plan, not a shared login. A workspace gives you admin control and
retention settings, and survives the person leaving. Confirm the current terms at
`anthropic.com/legal` and the privacy centre before rollout — that is the one thing
here worth verifying rather than taking from a README.

### Ground it, don't just prompt it

The instructions govern *behaviour*. The knowledge base governs *facts*. A model
without your facts writes confident, wrong, generic IT advice — the correct
Microsoft-documentation answer for a tenant that isn't yours.

The Case Type, Status and Origin values in `knowledge/01-environment.md` were read
from the live Salesforce org, not transcribed from documentation. The remaining
`TODO`s are facts only your team has. Fill them from the last five cases you closed
of that type. And when you don't know — **leave the `TODO`**. The instructions turn a
gap into *"I'm not certain, search for `<term>`"*, which is useful. A guess is not.

### Keep it advisory — no tools, no write access

Do not connect this to Salesforce or Entra with write access. Not in v1, and not in
v2 without a specific reason.

The value is in diagnosis and drafting, which needs no access at all. Write access
adds a category of failure — an assistant that closes the wrong case, resets the
wrong account — in exchange for keystrokes. Read-only access is a defensible later
step, once the tests pass consistently. Write is not.

The other reason: 96.8% of this queue arrives by **email**, which is unauthenticated.
An assistant that could act on the contents of an email is an assistant that acts on
anything a sender writes.

### Never paste credentials or supporter data

Two hard rules for whoever uses it:

- **No secrets.** No passwords, API keys, tokens, client secrets, connection strings.
  This is not hypothetical here — live WooCommerce keys sat in plaintext in a
  scheduled prompt and still need rotating.
- **No member, donor or supporter records.** Names, emails, addresses, donation
  history. BirdLife holds personal information under the Privacy Act 1988, and
  sending it offshore engages the cross-border disclosure obligations in APP 8. A
  staff name in a ticket is ordinarily fine and unavoidable; a supporter extract is
  not. If a case genuinely needs record data, describe the shape of the problem, not
  the records.

Put both rules in the workspace onboarding note, not just in the system prompt — the
prompt catches mistakes, the note prevents them.

### Test it against cases you have already closed

This is the step that separates the two outcomes, and it is the step everyone skips.
[`eval/scenarios.md`](eval/scenarios.md) is ten prompts. Nine check behaviour — does
it refuse to disable MFA, does it stop on a pasted key, does it invent a Salesforce
path. The tenth checks competence: give it three real closed cases, symptom only, and
see whether it lands where your technician landed.

Re-run the ten after any edit to the prompt or knowledge base. Prompt changes have
side effects — a rule added to fix tone routinely breaks a refusal.

### Keep the prompt in git

`instructions.md` lives here, not in the browser. Edit here, re-paste there. The
moment someone tweaks the project instructions directly, you have two versions, no
history, and no way to tell which behaviour came from which change.

### Decide the review loop before launch, not after

Pick one, write it down:

- Anything the assistant drafts that goes to a requester gets read by a human first.
  (Non-negotiable while it is advisory.)
- One person skims a sample of conversations weekly for the first month.
- Wrong answers get logged as a `TODO` filled or a rule added — not as a shrug.

### Measure whether it worked

Decide now, so you can answer in six weeks:

- Handle time on IAM / New User / Departing Staff cases, before and after.
- Consistency — do four technicians now close the same case type the same way?
- `Type` completeness on close. Currently blank on 13 of the last 870 cases and 65%
  of the *open* queue. If the assistant emits a Type every time and that number
  falls, the reporting problem quietly fixes itself alongside the coaching one.

Baseline them this week, while "before" is still measurable.

---

## Notes on the API path

`client/chat.py` is deliberately small, but three details in it are load-bearing:

- **Prompt caching.** The system prompt plus knowledge base is ~5k tokens and goes on
  every turn. One `cache_control` breakpoint makes turns after the first cheap. It
  only works if the cached prefix is byte-identical every turn — never interpolate a
  timestamp or ticket number into `instructions.md` or `knowledge/` at runtime.
- **Refusal handling.** Claude Opus 5 can decline a request outright and return a
  successful response with empty content. That is live here, not hypothetical: this
  assistant gets asked about phishing and credential compromise weekly, and benign
  security work occasionally trips the classifier. The script checks `stop_reason`
  before reading content, and opts into a server-side fallback so a declined request
  is re-run rather than coming back blank.
- **`max_tokens` covers thinking too.** Opus 5 thinks by default; a tight cap
  truncates the answer mid-sentence. It is set generously on purpose.

---

## What this does not fix

It makes each ticket faster. It does not reduce the number of tickets.

The README's finding stands: identity lifecycle is 20% of volume, intake is
single-channel email, and there is no request form. A faster answer to a
new-starter email is still an email a technician has to read. **The self-service
channel and the onboarding playbook are the larger win** — this assistant is the
cheap step that proves the ground before you build them, and the knowledge base you
write here is most of the content those need anyway.
