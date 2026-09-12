# ADR 0021: The brain lives in Mathew's personal git repository, with his Google Drive as the human copy

- **Status:** Accepted
- **Date:** 12 September 2026
- **Decided by:** Mathew Hema
- **Type:** Knowledge architecture and ownership. Extends ADR 0005 (git is the source of truth); supersedes every reference to OneDrive as a brain location and the repo-inbox pattern of 7 Sep 2026.

## Context

By 11 Sep 2026 the brain existed in four places: the git repository
`mathewruahema-beep/Birdlife` (Mathew's personal GitHub), the claude.ai account
skills (Mathew's personal account), a `Claude` folder that syncs through Mathew's
personal OneDrive and personal Google Drive, and Cowork memory. The BirdLife
tenant held none of it. For a week Cowork sessions without a GitHub connection
wrote skills to the account and patches to the folder, and no repo session read
either. Everything was pulled into the repository on 11 and 12 Sep.

Mathew's stated requirement: he retains the brain, in his personal storage, going
forward.

On 12 Sep the repository was found to be **public** on GitHub, with Pages enabled
and more than thirty branches, since its creation on 2 Aug 2026. It carries the
security posture, tenant identifiers and named privileged accounts.

## Decision

1. **The git repository is the executable brain.** Every Claude session (web,
   routine, desktop) loads `CLAUDE.md`, the skills and `memory/` from it. Nothing
   else is loaded at session start, so nothing else can be the brain.
2. **`GoogleDrive/Claude` in Mathew's personal Google account is the human-copy
   and backup layer.** Documents by IT identifier live there. A `git bundle` of
   the repository is written there weekly so the brain survives the loss of
   GitHub access. It is reached from sessions through the Google Drive connector.
3. **OneDrive is not a brain location** and the `repo-inbox` patch pattern is
   retired. Desktop and Cowork sessions commit from a local clone kept outside
   any cloud-synced folder, because syncing a `.git` directory corrupts it.
4. **Ownership is Mathew's, personally.** BirdLife Australia holds no copy unless
   a separate decision gives it one.
5. **The repository is made private immediately**, GitHub Pages disabled, and
   unrelated branches pruned. This is Mathew's action in the GitHub UI; the
   session cannot change visibility.

## Rationale

Google Drive cannot be loaded at session start and has no diff, history or
merge, so it cannot be the brain without recreating the week of drift this
decision closes. Git already satisfies the ownership requirement because the
repository is under Mathew's personal account. Naming Drive as the human copy
and backup makes what is already true into the rule.

## Consequences

- **Andrew Dunn, Keith Tsui, Nina Lewis:** inherit nothing unless Mathew grants
  them repository access. The delegation ladder (IT-SEC-002) has no path to the
  brain until he does.
- **BirdLife Australia:** its ICT operating knowledge, including the confidential
  security register, has no organisational home. That is a conversation under
  IT-GOV-002 (the AI policy) and Mathew's employment terms, recorded here as a
  known consequence, not decided here.
- **Public exposure, 2 Aug to 12 Sep 2026:** treated as a leaked-document
  incident under `birdlife-security`. Rotate anything credential-shaped in the
  history, then make private, then search for copies (forks, caches). Forks
  and stars were zero at the time of the finding.
- Every skill and document path that said `OneDrive Birdlife\Claude` now says
  `GoogleDrive\Claude`.

## Revisit when

Mathew leaves BirdLife, BirdLife adopts a policy requiring an organisational
copy, or the team is given repository access.

## Related

ADR 0004, ADR 0005, ADR 0006, ADR 0015, ADR 0016; IT-GOV-002; IT-SEC-002.
