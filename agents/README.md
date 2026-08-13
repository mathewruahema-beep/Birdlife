# Agents pending approval

Four agents built 13 August 2026, all created as **disabled** routines. Nothing runs
until each is reviewed, its connectors are attached in the claude.ai Routines UI
(org policy blocks attaching connectors via API), and it is enabled.

| Agent | Definition | Schedule (Melbourne) | Writes to | Trigger ID |
|---|---|---|---|---|
| Zeus triage & first-touch drafter | [zeus-triage-drafter.md](zeus-triage-drafter.md) | Hourly 8am–5pm weekdays | Internal CaseComments only | `trig_01EpSqssk6qvoFRg2UNoEH5o` |
| Identity lifecycle pack-to-plan | [identity-pack-to-plan.md](identity-pack-to-plan.md) | Daily 9:10am | Asana only | `trig_01FXchh6R9btpstDt6fSaLsM` |
| Unreconciled income exception report | [unreconciled-income.md](unreconciled-income.md) | Weekdays 7:30am | One Gmail draft only | `trig_01QC85zSvXoEWHTEzkip9ajp` |
| Meeting actions collector | [meeting-actions-asana.md](meeting-actions-asana.md) | Weekdays 4:30pm | One Gmail draft only | `trig_014XfhCxMe3nwBgAeGAACp8B` |

## Review order suggestion

1. **Unreconciled income** — read-only everywhere, but blocked until the NetSuite
   connector is re-authorised. Zero risk, needs the auth fixed first.
2. **Meeting actions** — read-only, one draft; the main question is comfort with
   the agent reading meeting content.
3. **Zeus triage** — the only agent that writes into Salesforce (internal comments);
   review the draft-reply voice and the comment format.
4. **Pack-to-plan** — writes Asana tasks; review the subtask checklists against the
   real runbooks before enabling.

## Shared ground rules

Every prompt embeds the same posture as the existing detectors: hard no-write rules
outside the named surface, draft-don't-send, dedup guards against repeat writes,
plain-language reports, and an explicit closing statement of what was and wasn't
touched. Connector outages are reported as outages, not task failures.
