---
name: birdlife-granola
description: Operator knowledge for BirdLife Australia's Granola meeting-notes workspace — scope of note access, overlap with Zoom and Teams transcripts, and safe handling of meeting content. Use for tasks about meeting notes, recaps, decisions taken in meetings, or turning discussion into actions. Trigger on "Granola", "meeting notes", "what did we decide", "recap the meeting", or a request to find what was said in a past meeting.
---

# BirdLife Australia — Granola

## Account — verified live

| Fact | Value |
|---|---|
| Account | mathew.hema@birdlife.org.au |
| Active workspace | **"Birdlife"**, id `2d77ba3f-a678-4cdc-bb99-f90773711453` |
| MCP note access scopes | **`personal` and `public` only** |

**The scope limit is the important fact.** You can read Mathew's own notes and notes shared publicly in the workspace. You cannot read other people's private notes. If a decision was captured only in someone else's private Granola note, it is not reachable from here — say so rather than reporting "no results".

## Where Granola fits, honestly

BirdLife now has **three** meeting-capture surfaces: Granola, Zoom recordings/transcripts/AI summaries, and Microsoft Teams transcripts. That is duplication, and it has a cost: a decision might exist in any of the three, so "search the meeting notes" is really three searches.

Granola's advantage is that it works regardless of platform and produces structured notes rather than raw transcript. Its limitation here is the scope restriction above.

**Practical search order for "what did we decide about X":**
1. Granola (`query_granola_meetings`, `list_meetings`, `get_meeting_transcript`) — fastest, already structured
2. Zoom (`search_meetings` with `has_summary` / `has_transcript`) — check `has_transcript_permission`
3. Teams — only where transcription was enabled, which is the known gap

If none of the three has it, the honest answer is that the decision was never captured, which is itself worth reporting.

## Available tooling

`mcp__Granola__*`: `query_granola_meetings` (start here), `list_meetings`, `get_meetings`, `get_meeting_transcript`, `list_meeting_folders`, `get_account_info`. All read-only.

## What meetings actually contain here

Mathew's meeting load is standup- and 1:1-dense: three Salesforce standups a week, a weekly ICT standup, recurring 1:1s (Keith, Renee, Andrew), and vendor blocks (Blitzm, Alphasys, S-Docs, miniOrange). That means meeting notes routinely contain:

- **Vendor commercial detail** — quotes, hours, rates (e.g. Blitzm's ~80-hour quote)
- **Staff performance and 1:1 content**
- **Donor and member data** discussed in fundraising contexts
- **Security weaknesses** discussed in ICT standups

Treat all four as confidential. Summarise for the intended audience; do not paste note or transcript content into Asana tasks, Confluence pages, emails or documents that go wider than the meeting.

## Operating rules
1. **Search Granola first** for meeting-decision questions — it is cheapest and structured.
2. **State the scope limit** when a search comes up empty. "Not found in the notes I can see" is different from "it was never discussed".
3. Never quote 1:1 content or vendor commercials outside the original audience.
4. When a note produces actions, put them in the Asana IT Operations Project Plan with an owner and date, or flag them as unassigned.
5. Granola is not on this project's approved connector list. Flag that in anything governance-facing.
