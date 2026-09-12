# BirdLife Australia, ICT Brain

The structured operational knowledge of BirdLife Australia's ICT function, in a form both
people and Claude can use.

This repository is the **source of truth**. The installable Cowork plugin is built from
it. Never edit the installed plugin directly.

## What is in here

```
skills/          19 Claude skills. birdlife-core is the doctrine; the rest are per-system.
knowledge/       6 deep digests, distilled from 116 source documents.
decisions/       Append-only decision log (ADRs). Never edited, only superseded.
registers/       Open items awaiting an owner in Asana.
scripts/         build.sh, assembles the plugin from this repo.
dist/            Build output. Not committed.
```

## Quick start

**To use it:** install `dist/birdlife-ict.plugin` in Claude Cowork. All 19 skills load and
trigger automatically.

**To change it:** edit the markdown here, open a pull request, rebuild.

```bash
./scripts/build.sh
```

## The four layers, and which one wins

| Layer | Holds | Precedence |
|-------|-------|-----------|
| Live connector query | Anything countable right now | **1, always wins** |
| `skills/` | How each system behaves, durably | 2 |
| `knowledge/` | Deep background, too long for a skill | 3 |
| Cowork memory | Mathew's decisions and preferences | 4 |

Full doctrine in `skills/birdlife-core/SKILL.md`. Read it before anything else.

## The rule that matters most

**If a connector can answer it, do not write it down.**

Every volatile figure in this repository has been paired with the query that refreshes it,
in `skills/birdlife-core/references/verification-queries.md`. Two examples, both confirmed
on 8 August 2026:

| Stored | Live | Effect of trusting the stored value |
|--------|------|--------------------------------------|
| Salesforce licences 70/70, no headroom | 69/70 | An unnecessary purchase request |
| ~3,600 cases in New (1 Jul) | 4,047 | Backlog understated by 12% |

Neither was wrong when written. Both were wrong when read. That is the problem this
structure exists to solve.

## Skills

**Doctrine**

- `birdlife-core`, precedence, fact classification, write-authority tiers, estate map

**Operational**

- `birdlife-ict-assistant`, the helpdesk workflow, Case and Asana mechanics
- `birdlife-salesforce`, `birdlife-microsoft365`, `birdlife-netsuite`, `birdlife-wordpress`,
  `birdlife-asana`, `birdlife-stripe`, `birdlife-cloudflare`, `birdlife-zapier`

**Supporting**

- `birdlife-atlassian`, `birdlife-canva`, `birdlife-gmail`, `birdlife-google-calendar`,
  `birdlife-google-workspace`, `birdlife-granola`, `birdlife-microsoft-learn`,
  `birdlife-miro`, `birdlife-spotify`

Nine of these were written and then left sitting unused in OneDrive, never installed. They
are live from this build onward.

## Write authority

Stated explicitly because getting it wrong is expensive.

- **Tier 1, execute after confirming**, Salesforce data, Asana, M365 user-level mail and
  calendar, reads across WordPress, NetSuite and Cloudflare
- **Tier 2, prepare and hand over**, Entra, Exchange admin, Intune, Defender, Conditional
  Access, licence assignment. No admin connector exists.
- **Tier 3, design only**, Salesforce configuration, production WordPress plugin changes,
  Stripe money movement

## Maintenance

Weekly, ten minutes: run the verification queries, update any baseline that has moved.

Quarterly: re-read each skill against reality, close resolved findings into the relevant
digest rather than deleting them, and confirm every open item still has an owner.

On any material system change: update the affected skill in the same week. A skill that
lags reality is worse than no skill.

Full process in `GOVERNANCE.md`.

## Owner

Mathew Hema, Senior Manager ICT. Contributors: Andrew Dunn, Keith Tsui, Nina Lewis.
