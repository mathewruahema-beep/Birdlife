# Memory: what happened, not how things work

The skills in `.claude/skills/` are long-term knowledge: how each system
works, its IDs, its traps. This directory is the other half of the brain:
**what happened, what was decided, what was learned, and what is still open.**
Without it every session starts with amnesia about history, and Mathew's
decisions live only in his head and in chat transcripts nobody re-reads.

Two kinds of file:

| Directory | Holds | One file per |
|---|---|---|
| `journal/` | Decisions, work done, lessons, open items, in date order | Day (`YYYY-MM-DD.md`) |
| `patterns/` | Resolved problems by system: symptom, cause, fix, how to verify | System |

Git is the store on purpose. It is versioned, greppable, readable by Andrew,
Keith and Nina without connector grants, and it carries no credentials by rule.
The console's artefact database and Claude's account memory are not the record;
a page is a mirror and an account is one person.

## Who writes here

- **Any session that changed something**: a record, a task, a routine, a
  skill, a document, or a decision Mathew made. The charter's session close
  rule in `CLAUDE.md` makes this mandatory, in the same commit as the change.
- **Routines** that produce a report or take an action append one line to the
  day's journal under "Done" (the routine name and the outcome), when they
  have repo write access. A routine that cannot write says so in its output.
- **The weekly OS audit** reads the journal since the last audit and reports
  gaps: commits without journal entries, fixes done without a learn step,
  facts that changed in prose but not in the facts file.

A session that only read and answered writes nothing.

## Journal entry format

```
# YYYY-MM-DD

## Decisions
- **<the decision in one line>.** Why, in one or two sentences. Decided by <name>. Source: <session, meeting, email, Case number>.

## Done
- <what changed, where, verified how>.

## Learned
- <a gotcha, a fact, a better way; and which skill or facts file now carries it>.
- <what Mathew would do differently, when he says so; the brain learns about its operator too>.

## Open
- <a question or decision waiting on someone, with the name and the date it is needed by>.
```

Rules for entries:

1. **Dated and sourced.** Every line says where it came from.
2. **Names, not roles.** "Nina" not "the team". Owner and date on anything open.
3. **No credentials, no donor or member PII, no card data.** A key that must be
   referenced is named by its first four characters, as the credential
   watchlist does.
4. **Security gaps stay in `birdlife-security`.** The journal may say "MFA
   remediation list reviewed"; the named accounts do not go here.
5. **Append, never rewrite history.** A wrong entry gets a dated correction
   below it, not an edit.
6. **Short.** One or two sentences a line. The skill is where detail goes.

## Pattern file format

One file per system (`salesforce.md`, `microsoft365.md`, `website.md`,
`money.md`, `claude-estate.md`, and so on, created when the first pattern
arrives). Each pattern:

```
### <Symptom as the requester would describe it>
- **Seen**: <date(s)>, <Case number or routine or session>
- **Cause**: <the actual mechanism>
- **Fix**: <what resolved it, tier, who ran it>
- **Verify**: <the re-read that proves it>
- **Doctrine**: <the skill section that now covers it, if any>
```

Patterns are episodic: a thing that happened and how it was closed. Doctrine
(the general rule) belongs in the skill; a pattern points at it.

## Reading the memory

- `INDEX.md` at the repo root maps every file in the brain.
- `grep -ri "<term>" memory/` finds any prior decision or pattern.
- The most recent journal files are the fastest way to catch up on a session
  that starts cold: read the last five days before doing estate or process
  work.
