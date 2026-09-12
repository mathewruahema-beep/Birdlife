# Patterns: the Claude estate (routines, skills, console)

Seeded 11 Sep 2026 from `os/registers.md`; doctrine in `birdlife-os` and
`os/README.md`.

### "The routine ran successfully and produced nothing"
- **Seen**: weekday dashboards job (heartbeat silent 25 Aug to 3 Sep), overnight pre-draft (zero drafts 24 Aug to 2 Sep), weekend job (29 Aug fire stalled 4.5 days)
- **Cause**: a connector write action was held for approval in an unattended auto-mode session; the run stalled at the approval and reported success. Earlier variant (Aug): routines with empty prompts.
- **Fix**: prompt reordered so the held action is last and cannot block the rest; the pre-draft prints its pack as text before writing. Pre-approving the tool or enabling push notifications is only possible in the Routines UI. Tier 1 for the prompt, Mathew in the UI for approvals.
- **Verify**: the output exists (heartbeat line in `_dashboard-run-log.txt`, a draft comment on a Case), not just the run status.
- **Doctrine**: `birdlife-os`, failure diagnosis; `os/README.md`, incident handling.

### "The dashboard did not update"
- **Seen**: repeatedly, Aug 2026
- **Cause**: most often the routine was created without connectors attached; connectors must be attached per routine in the UI.
- **Fix**: attach in claude.ai Routines; check `last_run` before anything else.
- **Verify**: next run's artifact timestamp and Teams file timestamp.
- **Doctrine**: `birdlife-os`, failure diagnosis.

### "The console tile says Add Salesforce-Production in Settings"
- **Seen**: 3 Sep 2026 console build
- **Cause**: the artifact `mcp` capability wants the connector display name with spaces; the hyphenated routine form is wrong.
- **Fix**: correct the name and republish to the same URL.
- **Verify**: tile loads data.
- **Doctrine**: `birdlife-os`, updating the console.

### "The DST fix would have skipped the main job"
- **Seen**: 3 Sep 2026 review
- **Cause**: the one-shot's prompt named six retired triggers and the weekday job's old cron.
- **Fix**: prompt rewritten against the current routine list. Estate changes must update dependent prompts in the same piece of work.
- **Verify**: the one-shot prompt lists exactly the triggers in the register.
- **Doctrine**: `os/README.md`, stale documentation is an incident.

### "A Cowork session made a change and the repo never saw it"
- **Seen**: 4 to 11 Sep 2026 (Zeus group rule, lens model, SC-300 baseline, WordPress rewrite, six new skills, three repo-inbox patches, the 3 Sep orphan-check patch)
- **Cause**: Cowork sessions on Mathew's machine had no GitHub connection, so they saved skills to the claude.ai account and patches to a Google Drive folder that syncs through his personal OneDrive; the tenant OneDrive the M365 connector reads never had it, and no repo session checked either place.
- **Fix**: pull the account skills from `/root/.claude/skills/synced/` (they are on disk in any repo session), then the Google Drive `Claude/repo-inbox` through the Google Drive connector, apply with `git am --3way`. Weekly audit step 8 now compares the live account list against the repo. Tier 1.
- **Verify**: the account skill list has nothing the repo lacks; the repo-inbox folder has no patch newer than the last journal entry that mentions it.
- **Doctrine**: `birdlife-os`, weekly audit steps 4 and 8; `memory/README.md`.
