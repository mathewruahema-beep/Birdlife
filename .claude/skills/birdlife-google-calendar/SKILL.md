---
name: birdlife-google-calendar
description: Operator knowledge for the personal Google Calendar connected to this workspace — why BirdLife scheduling belongs in Outlook, and safe use of the Google calendar tools. Use only when the user explicitly directs a task at their personal Google Calendar. Trigger on "Google Calendar" specifically. For BirdLife meetings, availability and scheduling use the Microsoft 365 Outlook calendar tools instead.
---

# Personal Google Calendar — boundary skill

## What this connector actually is

**This is the personal Google account calendar (`mathew.rua.hema@gmail.com`), not the BirdLife work calendar.**

BirdLife scheduling lives in **Outlook / Exchange Online**, reached through `mcp__Microsoft_365__outlook_calendar_search`, `outlook_create_event`, `outlook_update_event`, `outlook_respond_to_event`, `outlook_find_available_time` and `find_meeting_availability`. Zoom also exposes calendar events with `source` values of `google`, `office365` or `zoom`.

**Default assumption: any BirdLife meeting request routes to Outlook, not here.**

## The work calendar shape, for context

Mathew's Outlook calendar is standup- and 1:1-dense, and he organises most of it: three Salesforce standups a week, a weekly ICT standup, recurring 1:1s (Keith, Renee, Andrew), plus vendor blocks (Alphasys ran 8 hours across two days). **Meeting prep and meeting follow-up are the two biggest invisible time sinks** — that is where calendar automation earns its keep, not in scheduling.

Timezone is **Australia/Sydney (AEST, UTC+10)**. Times the user gives are in that zone unless stated. Note the trap: NetSuite, Salesforce and most vendor systems here are also AEST, but Cloudflare, Zapier schedules and cron expressions are typically UTC. Convert explicitly and say which zone you used.

## Available tooling

`mcp__Google_Calendar__*`: `list_calendars`, `list_events`, `search_events`, `get_event`, `create_event`, `update_event`, `delete_event`, `respond_to_event`, `suggest_time`.

## Operating rules
1. **Route work scheduling to Outlook.** Only use Google Calendar on an explicit personal request.
2. **Never create or move a meeting involving other people without confirmation.** Calendar writes are visible to attendees immediately and cannot be quietly undone.
3. Do not surface personal calendar content in any BirdLife artefact.
4. Always state the timezone when quoting a time, and convert explicitly for anything scheduled (cron, Zapier, scheduled tasks).
5. Google Calendar is not on this project's approved connector list, and as a personal account that exclusion is correct.
