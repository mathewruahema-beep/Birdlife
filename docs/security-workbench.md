# Security Workbench

**https://claude.ai/code/artifact/0e4c1fb6-95ec-4dc3-a761-166281e79d42**

The working surface for IT security at BirdLife Australia. It is the
`birdlife-security` skill turned into a page: live Salesforce posture, the
deadline register with days remaining, incident playbooks that write the Tier 2
commands, a findings tracker where every line has an owner and a date, and a
report drafter. Source is `security/index.html` in this repo. Tell any assistant
session "update the security workbench" to change it.

**Status (3 Sep 2026):** the source in this repo carries the remediation layer
(approval cards, Audit tab, Asana task raising). The live artifact still runs the
read-only first build until it is republished with the manifest under "Updating"
below; the build session's permission mode refused a publish that grants write
tools. Any interactive session can do it: "republish the security workbench".

**Confidential.** The page names admin accounts from live reads and carries the
posture gaps from the doctrine. It is a private artifact. Do not share the link
outside the ICT team, and do not enable GitHub Pages for this repo.

## Tabs

| Tab | What it does | Data |
|---|---|---|
| Overview | Six tiles (sysadmins, admin ratio, stale users, dates past, open findings, security cases), what is due in 30 days, top open findings, the lines to hold | live + register |
| Salesforce | Active System Administrators with flags (service account, external domain, stale), Modify All Data permission-set assignments, failed logins in 24h grouped by status and source IP, setup audit trail with portal and Bird Bot noise removed, open Ask Zeus cases with security keywords, stale active users | live, refreshed every 5 min |
| Posture | Essential Eight control board and the per-system posture, each dated | doctrine (static, in the file) |
| Deadlines | The deadline register. Days remaining computed at open. "Record outcome" stores the verification evidence; rows are never deleted. New dates can be added | register + shared store |
| Playbooks | Phishing, compromised account, leaked credential, payment anomaly, website compromise. Each is a tiered checklist plus a generator that produces the exact Graph PowerShell, Exchange Online, SOQL or Cloudflare rule from a UPN, sender, amount or path. The compromised-account playbook can look the person up in Salesforce live (User + 30 days of LoginHistory) | doctrine + live |
| Findings | Add, re-own, re-date, note and close findings. P1 first. Owner and date are mandatory | shared store |
| Report | Drafts a team posture note, an exec brief (counts only, never names), a deadline chase list, or a full prompt for a Claude session, from the live snapshot, register and open findings, in Mathew's voice | live + store + on-page Claude |
| Audit | Every remediation approved on the page: who, when, reason, the change, what the re-read showed, and an Undo for reversible actions | shared store |

## Remediation with approval

Every "Remediate" button opens an approval card. The card shows the record, the
exact field change (from and to), the warnings that apply, and asks for a reason.
Approve arms the button for ten seconds; a second click confirms. The page then
writes one record, re-reads it, and reports "Verified" or "Did not stick" from the
re-read, never from the write response. The action, reason, approver and re-read
result go to the Audit tab and to the artifact's `actions` collection.

| Action | Where | Salesforce write | Undo |
|---|---|---|---|
| Freeze / unfreeze login | sysadmin list, stale list, compromised-account lookup | `UserLogin.IsFrozen` | yes |
| Deactivate / reactivate user | sysadmin list, stale list, lookup | `User.IsActive` | yes |
| Downgrade profile | sysadmin list | `User.ProfileId` to a profile with no Modify All Data and no Manage Users (default BirdLife Standard User) | yes, restores the previous profile |
| Remove permission set | Modify All Data list | delete `PermissionSetAssignment` | yes, re-creates it |
| Internal note | security-flagged cases | create `CaseComment` with `IsPublished = false` | no |
| Close case | security-flagged cases | `Case.Status = Closed` + `Case_Closed_Reason__c` (+ `Type` if blank) and an internal audit comment | no |
| Raise Asana task | any finding | Asana `create_tasks` into the IT Operations Project Plan with assignee, due date and section; the finding keeps the link | no |

Guards: the approving user's own account is never actionable; service and
integration accounts (birdbot, integration, readonly) carry a red warning because
freezing or downgrading them stops whatever signs in as them; one record per
approval; no bulk actions; nothing runs without a typed reason.

Not on the page, still Tier 2: Entra, Exchange, Intune and Defender changes come
out of the Playbooks tab as command blocks for an admin to run.

## What it can and cannot do

- **Writes only behind approval.** The page's Salesforce calls are `soqlQuery`,
  `getUserInfo`, `updateSobjectRecord`, `createSobjectRecord` and
  `deleteSobjectRecord`, plus Asana `create_tasks`, all with the viewer's own
  connector credentials. The write shapes come from the connectors' published
  schemas (the build session could not execute a write to observe one); every
  outcome is verified by an observed read, so a wrong shape shows as a failed card,
  never as a silent success.
- **Tier 2 is prepared, not executed.** Every Entra, Exchange, Intune and Cloudflare
  action comes out as a command block with a Copy button for an admin to run.
- **Findings and deadline outcomes** are stored in the artifact's database. Any
  assistant session can read them back (`read_db` on collections `findings` and
  `deadlines`) to build a report or chase list. When the page is opened outside
  claude.ai the store is not available and it falls back to browser-local storage,
  and says so on the Findings tab.
- **Posture numbers on the Posture tab are dated.** They come from the skill, not a
  live read. Re-verify before asserting any of them.

## Live queries (Zeus-scoped where Cases are involved)

| Read | SOQL |
|---|---|
| Sysadmins | `SELECT Id, Name, Username, LastLoginDate, UserRole.Name, UserType FROM User WHERE IsActive = true AND Profile.Name = 'System Administrator' ORDER BY LastLoginDate DESC NULLS LAST` |
| Inactive sysadmins | same with `IsActive = false`, `COUNT(Id)` |
| Active Standard users | `SELECT COUNT(Id) FROM User WHERE IsActive = true AND UserType = 'Standard'` |
| Stale users | `IsActive = true AND UserType = 'Standard' AND (LastLoginDate < LAST_N_DAYS:30 OR LastLoginDate = null)` |
| Modify All Data | `PermissionSetAssignment WHERE PermissionSet.PermissionsModifyAllData = true AND PermissionSet.IsOwnedByProfile = false AND Assignee.IsActive = true` |
| Failed logins | `LoginHistory WHERE LoginTime = LAST_N_DAYS:1 LIMIT 300`, filtered on the page because `Status` cannot be filtered in SOQL |
| Setup changes | `SetupAuditTrail WHERE CreatedDate = LAST_N_DAYS:7 LIMIT 150`, filtered on the page because `Section` cannot be filtered in SOQL |
| Security cases | `Case WHERE RecordType.DeveloperName = 'Zeus' AND IsClosed = false AND Subject LIKE` phishing, suspicious, scam, hack, compromise, password, MFA, spam, security, access |

Admin ratio = active sysadmins / active Standard users. The line is 5%.

## Updating

1. Edit `security/index.html`.
2. Republish with the Artifact tool passing `url` = the address above and the
   capabilities manifest: `mcp.servers` = `[{server: "Salesforce Production",
   tools: ["soqlQuery", "getUserInfo", "updateSobjectRecord",
   "createSobjectRecord", "deleteSobjectRecord"]}, {server: "Asana", tools:
   ["create_tasks"]}]`, `db: {}`, `sample: {}`. Omitting `capabilities` carries
   the stored manifest forward.
3. Never declare a connector tool the page does not call. If a tool's shape has
   not been observed in the publishing session, say so when publishing.
4. Commit and push the source in the same session.

## Seeded findings

Fourteen findings were seeded on 3 Sep 2026 from the doctrine and the live
Salesforce read (ids `f-seed-01` to `f-seed-14`), each with an owner and a due
date. The due dates were set at build time and need Mathew's confirmation; that
is noted on each finding.

## First-open checklist for Mathew

1. Open the link from the claude.ai app so the Salesforce connector, the shared
   store and on-page drafting are granted. The first Salesforce read asks for
   consent once.
2. On the Salesforce tab, confirm the sysadmin list matches what you expect. Two
   vendor-domain accounts and three birdbot accounts hold System Administrator.
3. On the Deadlines tab, record outcomes for the four dates that have passed
   (Transaction Security Policies, Vevox Dashboard SAML, Pardot cutover, the
   1 Sep Salesforce retirements).
4. On the Findings tab, re-own or re-date anything you disagree with.
