# Second Counsellor Desk

A single-page workload tool for Mathew Hema's calling as second counsellor in
the stake presidency. It is personal, not BirdLife work; it lives here because
this is the repository the Claude sessions are attached to.

`second-counsellor-desk.html` is the source of the published artifact. Publish
it with the Artifact tool and the capabilities below; a redeploy to the same
URL keeps the stored data.

## What it does

- **Workload**: tasks grouped Overdue / Today / This week / Later / No date,
  each tagged with an area (ward assignment, interviews, meetings, speaking,
  training, callings, temple, audit) and optionally a ward. Stored in the
  artifact database (`tasks/<id>`), with a browser-only fallback.
- **This Sunday**: where you are, in what role, what you are speaking on, which
  interviews are booked.
- **Assigned wards**: ward, bishop, last visit. Six weeks without a visit turns
  red.
- **Church mail**: a live Gmail search (default: stake, bishop, presidency,
  high council, ward, temple, conference, sustaining, interview, recommend in
  the last fourteen days) via the viewer's Gmail connector. One click opens the
  thread in Gmail; "Make task" pulls it onto the workload with a link back.
- **Next fourteen days**: Google Calendar events, church-related ones tagged.
- **Standing duties**: the recurring duties of a stake presidency counsellor
  from the General Handbook, with "Done today" rolling the next due date.
- **Doors**: Gmail, Leader and Clerk Resources, churchofjesuschrist.org, the
  stake calendar, Handbook 6, the Directory, and a second row of Handbook
  chapters, temple appointments, the Missionary Portal and Church Account.

## Capabilities the artifact declares

```json
{
  "db": {},
  "mcp": {
    "servers": [
      {"server": "Gmail", "tools": ["search_threads"]},
      {"server": "Google Calendar", "tools": ["list_events"]}
    ]
  }
}
```

The `mcp` grant means the page cannot be shared publicly. That is the right
setting for this tool.

## Confidentiality

The tool is hosted outside the Church's systems. Record that an interview
happened, never what was said. Confessions, worthiness detail and membership
council matters do not belong here (General Handbook 31.2).
