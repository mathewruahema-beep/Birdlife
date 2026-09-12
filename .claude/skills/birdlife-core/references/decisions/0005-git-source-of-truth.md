# ADR 0005: Git is the source of truth; the plugin is a build artefact

- **Status:** Accepted
- **Date:** 8 August 2026
- **Decided by:** Mathew Hema

## Context
The entire ICT brain lived in one person's OneDrive folder. No version history usable for
review, no diffs, no pull requests, and no access for Andrew, Keith or Nina. The knowledge
base's own finding 17 flags that the ICT dashboards live only in Mathew's private folder
and treats that as a risk. The brain itself had the same problem one level up.

## Decision
A git repository is the single source of truth. The Cowork plugin is generated from it by
`scripts/build.sh` and is never edited directly.

## Rationale
- Diffs and pull requests give change review, which a governance artefact needs.
- History answers "when did we learn this and who from", which matters in an audit.
- Distribution stops depending on one person's file sync.
- Building the plugin from source removes the duplication that caused the original problem.
  There is exactly one copy of every fact, and packaging is mechanical.

## Consequences
The team needs a git workflow, which is a real adoption cost for a non-developer ICT team.
Mitigated by keeping everything as plain markdown and keeping the build to a single script.
Editing the installed plugin directly is now a defect, not a shortcut.
