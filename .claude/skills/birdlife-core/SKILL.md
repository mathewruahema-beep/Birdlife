---
name: birdlife-core
description: The operating doctrine for every BirdLife Australia session, which layer of knowledge wins when two sources disagree, how to tell a live fact from a durable one, the write-authority tiers, and where to record something new. Read this FIRST in any BirdLife task before reaching for a system-specific skill. Trigger on any BirdLife Australia work at all, and specifically on "what do we know about", "is that still true", "where should this go", "who owns this", "check that figure", or any task that spans more than one BirdLife system.
---

# BirdLife ICT, Core Operating Doctrine

**Repo integration, 12 Sep 2026.** This skill was written for the August 2026
Cowork plugin and was pulled into the repository from Google Drive on 12 Sep
2026, after a month in which seven skills said "read birdlife-core first" and
no session on the repo could. `CLAUDE.md` is the kernel and wins on conflict;
this skill is the doctrine underneath it. The four layers map onto the repo as
follows: layer 1 is a live connector query; layer 2 is the `birdlife-*` skill
with its `references/facts.md` (dated baselines, never presented as current);
layer 3 is `references/knowledge/` here; layer 4 is `memory/journal/` (what was
decided and by whom) with `references/decisions/` as the ADR record, and Cowork
memory last. The decision log now runs 0001 to 0020; 0017 (autonomy levels) is
cited by 0018 and 0019 but was not found anywhere, and two ADRs carry the
number 0019 (Birdata supporter feed, 7 Sep; lens model, 8 Sep). Neither is
edited, per rule 3; the next ADR is 0021 and the collision is noted here.

This is the index and the rulebook. Every other `birdlife-*` skill assumes you have
read this one. It exists because BirdLife's knowledge is spread across four layers
that decay at very different speeds, and the failure mode is confidently repeating a
number that stopped being true weeks ago.

## Rule 1: the precedence order

When two sources disagree, this is the order. It is not negotiable.

1. **A live query through a connector.** Always wins.
2. **A system skill** (`birdlife-salesforce`, `birdlife-netsuite`, and so on).
3. **A knowledge digest** in `references/knowledge/`.
4. **Cowork memory**, Mathew's decisions and preferences only, never system state.

If you can query it, do not quote it. See `references/verification-queries.md` for
the exact query that refreshes each commonly-cited figure.

## Rule 2: classify the fact before you trust it

Four classes, four different half-lives. Most mistakes come from treating class 1 as
class 2.

| Class | Example | Half-life | Rule |
|---|---|---|---|
| **Live** | Case counts, licence headroom, unreconciled income, vulnerability counts | Days | Never assert from memory. Query it. |
| **Durable** | Join keys, integration topology, object model, why a decision was made | Years | Safe to quote. Still say where it came from. |
| **Decision** | "E8 with a SaaS overlay", "approve-only Entra writes" | Permanent once made | Never edit. Supersede with a new dated entry. Not made until the ADR exists. |
| **Open item** | Cert expiries, deadlines, blockers | Expires on a date | Does not belong in a document. Belongs in Asana with an owner. |

**Any figure carrying a date older than 30 days is a baseline, not a fact.** Present it
as "was X as at DATE, re-verify" or refresh it before speaking. Two worked examples,
both confirmed on 8 Aug 2026:

- Stored: "70/70 Salesforce full licences used, zero headroom." Live: **69/70**. One
  seat freed that morning by an offboarding. A team member reading the stored figure
  would have raised a purchase request that was not needed.
- Stored: "~3,600 cases in New (1 Jul 2026)." Live: **4,047**. The stored figure
  understated the backlog by 12% and hid five weeks of growth.

Neither digest was wrong when written. Both were wrong when read. That gap is the
whole reason this doctrine exists.

## Rule 3: write authority has three tiers

Inherited from `birdlife-ict-assistant`, and it applies to every system, not just the
helpdesk.

- **Tier 1, execute after confirming**: Salesforce data, Asana, M365 user-level mail
  and calendar, WordPress and WooCommerce reads, NetSuite reads, Cloudflare reads.
- **Tier 2, prepare and hand over**: Microsoft Entra, Exchange admin, Intune, Defender,
  Conditional Access, licence assignment. No admin connector exists. Produce the exact
  Graph PowerShell or click-path. Never claim to have executed.
- **Tier 3, design only**: Salesforce configuration (Metadata and Tooling API),
  WordPress plugin changes on production, anything touching money movement in Stripe.

Say which tier you are in, out loud, when it is not obvious. Going quiet or implying
success on a Tier 2 action is the worst thing you can do here.

## Rule 4: where a new fact goes

| What you learned | Where it goes |
|---|---|
| How a system behaves, durably | The relevant `birdlife-<system>` skill |
| Deep background, too long for a skill | `references/knowledge/<domain>.md` |
| A decision Mathew made, and why | `references/decisions/` as a new dated ADR. That ADR is the record. Memory is a convenience copy, never the only copy |
| Something with a due date and an owner | Asana, not a file |
| A current number | Nowhere. Write the query into `references/verification-queries.md` instead |

Never write the same fact in two layers. If it belongs in a skill, it does not also
belong in a digest. Duplication is how this estate got into trouble the first time.

## The estate in one screen

Durable structure only. Every count and dollar figure has deliberately been left out;
query them.

- **Salesforce "Zeus"** is the hub. NPSP/Household, Enterprise, instance AUS92, staging
  sandbox `birdlifeaustralia--staging`. Most other systems write into it, which makes it
  the best single place to observe the estate.
- **Microsoft 365 / Entra** is the identity root and the largest capability gap. P1
  licensing only. Read-only MCP at `C:\azureintegration`; the write tier is built but
  waits on a separate app registration and admin consent.
- **NetSuite OneWorld** is the ledger. Payroll via Infinet Cloud ZonePayroll. A Business
  Central migration is proposed, not decided.
- **WordPress on WP Engine behind Cloudflare** is the front door, with WooCommerce
  carrying membership and merchandise.
- **Stripe** takes the money; **Payments2Us**, **Raisely via MoveData** and **miniOrange**
  move it into Salesforce.
- **Employment Hero** is upstream of all people data. Its native M365 add-on **overwrites
  rather than merges**, so a blank field in EH blanks the Entra field. This is the single
  most dangerous behavioural fact in the estate.
- **Asana** carries project work; the **IT Operations Project Plan** is the main board.

## Blind spots, never claim coverage here

Entra, Exchange, Intune and Defender administration. Salesforce configuration metadata.
The run-health of external sync engines (miniOrange, MoveData, Zapier) as opposed to
their output. Zapier zap failures. The WordPress fleet beyond the main site. Ortto deep
sync. GA4, which no org-held Google account can reach.

When asked about these, say plainly what is connected and what is not, and name what
would be needed. An honest gap is more useful than a confident guess.

## Team

Mathew Hema (Senior Manager ICT), Andrew Dunn, Keith Tsui, Nina Lewis. Tickets arrive at
`zeus@birdlife.org.au` and land as Salesforce Cases on the "Ask Zeus" record type. Each
ICT staffer has **multiple active Salesforce User records**, resolve by query and ask
before reassigning.

## References

- `references/verification-queries.md`, the query that refreshes each volatile figure
- `references/fact-classification.md`, worked examples of the four classes
- `references/knowledge/`, the six deep digests, one per domain
- `references/decisions/`, the append-only decision log (ADRs 0001 to 0020; 0017 missing, 0019 used twice)
