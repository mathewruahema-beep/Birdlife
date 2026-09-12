---
name: birdlife-gmail
description: Operator knowledge for the personal Gmail account connected to this workspace — why it is NOT BirdLife mail, the boundary between personal and work correspondence, and safe use. Use only for tasks the user explicitly directs at their personal Gmail. Trigger on "Gmail", "personal email", or an explicit reference to the gmail.com address. For BirdLife work email use the Microsoft 365 skill instead.
---

# Personal Gmail — boundary skill

## What this connector actually is

**This is `mathew.rua.hema@gmail.com`, a personal consumer Gmail account. It is not BirdLife mail.**

BirdLife work email is **Outlook / Exchange Online** under the birdlife.org.au tenant, reached through `mcp__Microsoft_365__outlook_*`. Those are the tools for anything work-related: triage, drafts, search, rules, calendar invitations, shared mailboxes.

Verified state of the connected Gmail: ~21,440 inbox messages, ~16,483 unread, and a large personal label taxonomy covering household, community, family, travel, telco, vehicle and volunteer-organisation correspondence.

**Default assumption: any BirdLife request routes to Microsoft 365, not here.** Only work in Gmail when Mathew explicitly asks for his personal mail.

## Why the boundary matters, not just as etiquette

Two real risks sit on this line:

1. **Work product in personal accounts.** The connected personal Google Drive already holds BirdLife documents including a CONFIDENTIAL security framework containing per-system weakness detail. Mail is the same failure mode. BirdLife has no retention, eDiscovery or access control over anything that lands here, and on departure or account compromise it is simply gone or exposed. If BirdLife correspondence turns up in this mailbox, flag it and recommend moving the thread to the work account.

2. **Personal content in work outputs.** This mailbox contains extensive personal life correspondence. None of it belongs in an ICT report, an Asana task, a Confluence page, a dashboard or a summary shared with anyone at BirdLife. Do not read across from it to characterise the user, and do not surface its content unprompted.

## Available tooling

`mcp__Gmail__*`: `search_threads`, `get_thread`, `get_message`, label management, and draft creation/update. Note there is **no send tool** — drafts only. That is the correct posture and matches the standing rule that agents draft and Mathew sends.

## Operating rules
1. **Route work email to Microsoft 365.** Only touch Gmail on an explicit personal request.
2. **Never send.** Draft only, as with all mail in this environment.
3. Do not summarise, categorise or index this mailbox's personal content into any BirdLife artefact.
4. If work correspondence appears here, recommend moving it to birdlife.org.au rather than acting on it in place.
5. Gmail is not on this project's approved connector list, and given it is a personal account, that exclusion is correct. Say so if governance comes up.
