# ADR 0020: Salesforce and Outlook integration, add-in pilot with Einstein Activity Capture held

- **Status:** Accepted
- **Date:** 11 September 2026
- **Decision maker:** Mathew Hema, Senior Manager ICT
- **Type:** Solution decision, with an embedded risk acceptance
- **Supersedes:** nothing
- **Related:** IT-INT-004 (decision note and pilot runbook), IT-BCP-001 (DR and BC plan), IT-SEC-002 (privileged access capability ladder), ADR 0006 (connector scope)

## Context

BirdLife has never deployed any Salesforce to Outlook integration. Verified live in Zeus on 11 September 2026:

- Events created in the last 90 days: **0**. No supporter, donor, bequestor or partner meeting has been recorded in the CRM this quarter.
- EmailMessage last 90 days: 24,084 (5,574 incoming), almost all Email-to-Case on zeus@birdlife.org.au plus outbound receipting.
- Email Tasks last 90 days: 17,951, of which Keith Tsui 11,921 and Bird Bot 3,361 are process generated. Genuine human logging is about 2,669 across 68 active full licence users.
- Einstein Activity Capture: 100 permission set licences provisioned, **0 used**.
- No Salesforce Inbox connected app. The "Salesforce for Outlook" connected app present in the org is the default packaged artefact for the retired legacy desktop add-in.
- Active users on the Salesforce licence: 68, not the 70 of 70 carried in the knowledge base.

A hard external date applies. Microsoft begins disabling Exchange Web Services across Exchange Online on **1 October 2026**, auto-setting organisation level EwsEnabled to false for tenants that have not opted in, with full retirement on 1 April 2027. The Salesforce features that connect to Exchange have historically run on EWS and are moving to Microsoft Graph.

## Options considered

1. **Outlook Integration add-in only, five user pilot.** No licence cost, manual logging, data stays in Zeus objects, reversible in one action.
2. **Add-in plus Einstein Activity Capture.** Automatic capture, uses the free licences, but activity is stored outside Zeus objects, outside Veeam Backup for Salesforce and outside IT-BCP-001, with a limited retention horizon and whole mailbox scope by default.
3. **Helpdesk and Case side only.** Improve the existing Email-to-Case path. Lower risk, but does not address the zero Events finding.
4. **Whole of organisation rollout.** Fastest coverage, no pilot evidence, support load falls on Andrew Dunn with no runbook.

## Decision

**Option 1.** Deploy the Salesforce Outlook Integration add-in to five named users in Supporter Care and Fundraising for a fortnight, through a dedicated Entra security group, with manual logging only.

**Einstein Activity Capture stays off.** It becomes a separate decision after the pilot and after the tenant EWS position is settled, and not before 1 November 2026. That decision requires a written privacy position and exclusion rules, because capture applies to the whole connected mailbox by default and stores activity outside the Veeam backup and outside IT-BCP-001.

## Risk acceptance

Mathew Hema accepts, for the duration of the pilot, that the five pilot users operate in a tenant with **no tenant wide enforced Conditional Access MFA policy**. Mitigation is confirming MFA registration for all five before assignment, and deploying through a dedicated security group so access can be revoked in a single action.

## Consequences

- Keith Tsui executes the Salesforce Setup change, about one hour. Andrew Dunn takes first line support and runs the verification queries. Karishma Soni is not involved and this is not added to her twelve week plan.
- The five pilot users must change behaviour. If Events created stays at zero after a fortnight, the honest conclusion is that manual logging does not fit how the team works, and the choice narrows to automatic capture with its governance cost, or accepting that supporter meetings are not recorded.
- BirdLife now needs a tenant EWS position before 1 October 2026 regardless of this project. The EWS usage report in the Microsoft 365 admin centre is the input.
- Two knowledge base figures are corrected: Salesforce full licence consumption is 68 active users, not 70 of 70; and the "Salesforce for Outlook" connected app is not evidence of a prior deployment.

## Open items with owners

| Ref | Item | Owner | Due |
|---|---|---|---|
| D1 | Tenant EWS position: opt in with an allow list, or accept the 1 October auto-disable | Mathew Hema | 30 Sep 2026 |
| D2 | Einstein Activity Capture on or off, with a written privacy position and exclusion rules | Mathew Hema | After the pilot, not before 1 Nov 2026 |
| D3 | Whether to widen beyond the five pilot users | Mathew Hema | Day 14 of the pilot |
| D4 | Richard Cooling holds an active full Salesforce licence with no login since 14 Aug 2025. Reclaim or retain. | Mathew Hema | 30 Sep 2026 |
| D5 | Profile "Birdlife MARCOMMS (Ayla Only)" is named for an individual and is in live use. Rationalise or document. | Keith Tsui | Next configuration review |

## Verification

```
SELECT COUNT(Id) FROM Event
WHERE CreatedDate = LAST_N_DAYS:14
AND CreatedById IN ('005RF00000676wTYAQ','005RF0000069QUTYA2',
  '0055g00000DqUpxAAF','005RF000001v4CnYAI','005RF000003XS8fYAG')
```

Baseline 0. Target 5 or more at day fourteen. Checked by Andrew Dunn.
