---
name: birdlife-miro
description: Operator knowledge for BirdLife Australia's Miro workspace — the empty-spaces state, what the connector can build (diagrams, canvases, tables, prototypes), and where Miro fits for ICT architecture and process mapping work. Use for tasks about whiteboards, architecture diagrams, process maps, workshop boards, journey maps, or visual planning. Trigger on "Miro", "board", "whiteboard", "diagram", "process map", "architecture diagram", "workshop", or a request to map or visualise a system or process.
---

# BirdLife Australia — Miro

## Workspace identity — verified live

| Fact | Value |
|---|---|
| Org ID | `3458764569241611977` |
| Team ID | `3458764569241611978` |
| Mathew's user ID | `3458764665396343632` |
| Workspace ID | `0` |
| **Spaces** | **none — `space_list` returns empty** |

**No Spaces exist.** Boards, if any, sit directly at team level. That means there is no organising structure yet, which is an opportunity rather than a problem: the first thing to establish is a Space convention (by programme, by project, or by system) before board count makes it painful.

Entra holds **2 duplicate Miro enterprise-app registrations** — consolidate in the app access review.

## What Miro is genuinely good for here

BirdLife's ICT landscape is unusually tangled: 15+ SaaS platforms, a 424-object Salesforce org, integrations that run through miniOrange, MoveData, Zapier and manual CSV, and a Digital Ecosystem Map that currently lives as a PowerPoint with six layers. That PPTX is the single most-referenced artefact in the environment and it is not editable collaboratively.

**Highest-value Miro use cases, in order:**
1. **Rebuild the Digital Ecosystem Map as a live board.** Six layers already defined: Digital Experience, Marketing/Acquisition, Internal Workplace, Integration/Identity/Automation, Core Platform (Salesforce), Finance/HR/Data/Infrastructure. A board can be updated as systems change; a deck cannot.
2. **Data flow diagrams** for the money chain (WooCommerce → Stripe → Salesforce → NetSuite) and the people chain (Employment Hero → Entra → Culture Amp / TeamOrgChart). Both are currently described in prose across multiple documents and understood by one person.
3. **Membership cutover runbook** as a swimlane — Blitzm, miniOrange, Salesforce developer and end-to-end responsibilities, matching the 45-test staging script structure.
4. **Workshop boards** for branch and stakeholder sessions, where the alternative is a Word decision log with unanswered rows.

## Available tooling

`mcp__Miro__*` is unusually capable. Beyond board CRUD and sharing:
- **`diagram_create_mermaid` / `diagram_update_mermaid`** — generate diagrams from Mermaid source. Call `diagram_get_mermaid_instructions` first for the supported subset.
- **`canvas_create_from_svg` / `canvas_read_as_svg` / `canvas_update_from_svg`** — round-trip SVG. `canvas_get_canvas_composer_skill` returns Miro's own composition guidance; read it before hand-authoring canvas SVG.
- `table_create`, `table_sync_rows`, `table_list_rows` — structured data on a board, useful for decision logs and RAID.
- `doc_create` / `doc_update`, `code_widget_*`, `image_*`, `prototype_*`, `section_*`
- `comment_create` / `comment_reply` / `comment_resolve` for review cycles
- `context_get` and `context_explore` to orient before acting

**Mermaid is the fastest honest path** for architecture and flow diagrams. Author the logic as Mermaid, push it, then adjust visually.

## Operating rules
1. **Call `diagram_get_mermaid_instructions` or `canvas_get_canvas_composer_skill` before authoring** — do not guess the supported syntax.
2. Create a Space structure before creating the fifth board.
3. Diagrams that describe integrations must state their as-at date. This environment changes monthly and a stale architecture diagram is worse than none.
4. Do not put credentials, webhook URLs, tenant IDs or per-user security detail on a board. Boards get shared with vendors.
5. If a diagram will be reused or presented, deliver it as a rendered artefact as well as a Miro link, so it survives access changes.
