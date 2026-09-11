# Zapier: facts

The lookup table for `birdlife-zapier`. **Edit this file first when a value
changes, then the prose.** Never record a webhook URL or a `selected_api`
value here; both are credentials or internal identifiers.

## Connected apps (verified live, Aug 2026)

| App | Actions | Connections | Named connection |
|---|---|---|---|
| Salesforce | 41 | 3 | |
| Asana | 41 | 1 | |
| Microsoft Outlook | 44 | 8 | |
| Award Force | 33 | 1 | |
| Microsoft Teams | 30 | 3 | |
| Content Workflow (Bynder) | 24 | 1 | |
| Microsoft Excel | 22 | 9 | |
| Storage by Zapier | 16 | 1 | |
| Pardot | 12 | 2 | decommissioned 31 Aug 2026; remove |
| BugHerd | 10 | 1 | |
| LearnUpon | 8 | 1 | |
| Campaign Monitor | 7 | 1 | Campaign Monitor |
| Raisely | 6 | 1 | BirdLife Australia |
| Ortto | 6 | 1 | birdlife |
| Google Analytics 4 | 3 | 2 | mathew.hema.admin@birdlife.org.au |
| Humanitix | 1 | 1 | mathew.hema@birdlife.org.au |
| Webhooks by Zapier | 1 | 0 | |

## Zap 371228125 "Unreconciled Income Exception Report" (DRAFT)

| Step | Detail |
|---|---|
| Trigger | Schedule, Tue and Fri 12:00 AM AEST |
| 1 | Salesforce Find Records, report `00ORF0000033T6z2AE`, unreconciled Opportunities, last 7 days |
| 2 | NetSuite Find Records, account `3440597`, Token-Based Auth (credentials do not exist yet), ±3 business days |
| 3 | HTML exception table emailed to mathew.hema@birdlife.org.au |

## Other automations

| Item | Value |
|---|---|
| LearnUpon | `learn.birdlife.org.au`, Webhooks v2 catch-hook, only "Course enrolment" ticked; Zapier account keith.tsui@birdlife.org.au; URL in plaintext docs (rotate) |
| EH Certification write-back | needs Employment Hero Platinum tier (not held) |
| Superseded EH to Azure AD manager sync | Entra app `EH-OrgSync-Zapier` (`User.ReadWrite.All`), PUT manager `$ref`; ~4 tasks per employee; usage 142 of 2,000 monthly; check it is disabled |
| Failure routing (designed) | Zap Manager error to Salesforce Case, Type `System Notification`, Zeus record type |

## Connector mechanics

`inspect_zapier_actions` with no arguments enumerates apps;
`list_zapier_connections` needs `selected_api`; `discover_zapier_actions`,
`enable_zapier_action`, `disable_zapier_action`,
`execute_zapier_read_action`, `execute_zapier_write_action`. In unattended
routines a Zapier write action is held for approval and stalls the run (3 Sep
2026 finding); pre-approve it in the Routines UI or avoid it.
