# Asana: facts

The lookup table for `birdlife-asana`. **Edit this file first when a value
changes, then the prose.** Live task memberships override any section name
here if a section was renamed; `get_project` is the check.

## Workspace

| Fact | Value | Verified |
|---|---|---|
| Workspace gid | `443963187362944` | Aug 2026 |
| Mathew Hema user gid | `1210202992538499` (mathew.hema@birdlife.org.au) | Aug 2026 |
| IT Operations Project Plan project gid | `1211042432693678` | Aug 2026 |
| Task link pattern | `https://app.asana.com/1/443963187362944/project/1211042432693678/task/<gid>` | Sep 2026 |
| Better Impact board | "ICT Better Impact Implementation", private to the ICT Manager | Aug 2026 |

## IT Operations Project Plan sections

| Section | gid |
|---|---|
| Backlog/Requests | `1216556543715194` |
| Scoping/Requirements Gathering | `1216556543715193` |
| In Development/Progress | `1216556543715191` |
| Awaiting Response | `1217146608838572` |
| Blocked | `1216556543715197` |
| Ready for Deployment | `1216556543715188` |
| Hypercare | `1211042432693693` |
| Done | `1211051239943465` |
| Meeting agenda (Marketing+ICT) | `1214293208933456` (agenda, not a work state) |

## Team gids (verified Aug 2026)

| Team | gid |
|---|---|
| Advocacy/Policy | `1210433663470343` |
| Beach-nesting Birds | `1207819728138563` |
| Black-cockatoos | `1207418217121010` |
| Campaign Management | `1205098136351778` |
| Citizen Science | `1204255684549550` |
| Coastal and Wetland Birds | `1207947394108072` |
| Comms and Engagement | `1204164938395809` |
| eCommerce | `1211041491719670` |
| Finance (duplicate teams, cleanup item) | `1211135286171472`, `1213223677662621` |
| Finance & Business Improvement | `1213223677662598` |
| Fundraising and Marketing | `1204407434526263` |
| Global Authentication (login.birdlife.org.au) | `1204617145641439` |
| Glossy Black-Cockatoo | `1207321314790331` |
| Grasswrens | `1207489426903543` |
| 2024 Nature Laws Project | `1206587228062563` |
| Advanced Tier | `1211029269244275` |

Untidy defaults to archive: "BirdLife's first team", "Caroline's first team".

## API shapes

| Call | Shape |
|---|---|
| `search_tasks({projects_any, completed:false, limit, opt_fields})` | `{data:[...]}`; sections at `memberships[].section.{gid,name}` |
| `update_tasks(tasks=[...])` | per-task `succeeded` / `failed`; check `failed` |
| Section move | `add_projects: [{project_id, section_id}]` |
| Complete | `{task, completed: true}` |
| `add_comment(task_id, text)` | human-authored story |
| `create_tasks(default_project, tasks=[{name, notes, section_id, assignee}])` | response shape not yet observed; verify by re-read |

## Board reading thresholds

| Rule | Value |
|---|---|
| Attention | Blocked, Awaiting Response, due date passed, or no due date outside Backlog |
| Stale | `modified_at` older than 30 days and not Done |
| In Development stale question | 14+ days |
| Hygiene report buckets | untouched 30 / 60 / 90+ days |

## Related facts held elsewhere

| Item | Where |
|---|---|
| Case-to-Asana email rule SPF blocker (`include:_spf.salesforce.com`) | `birdlife-cloudflare/references/facts.md` |
| Zapier Asana connection (41 actions, 1 connection) | `birdlife-zapier/references/facts.md` |
| Entra duplicate Asana enterprise apps (6 to 7), review 19 Sep 2026 | `birdlife-microsoft365/references/facts.md` |
