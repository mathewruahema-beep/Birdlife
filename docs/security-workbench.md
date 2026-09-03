# Security Workbench

**https://claude.ai/code/artifact/0e4c1fb6-95ec-4dc3-a761-166281e79d42**

The working surface for IT security at BirdLife Australia. It is the
`birdlife-security` skill turned into a page: live Salesforce posture, the
deadline register with days remaining, incident playbooks that write the Tier 2
commands, a findings tracker where every line has an owner and a date, and a
report drafter. Source is `security/index.html` in this repo. Tell any assistant
session "update the security workbench" to change it.

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

## What it can and cannot do

- **Reads only.** The page never writes to any BirdLife system. Its one connector
  call is `soqlQuery` on Salesforce Production, with the viewer's own credentials.
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
   tools: ["soqlQuery"]}]`, `db: {}`, `sample: {}`. Omitting `capabilities`
   carries the stored manifest forward.
3. Never declare a connector tool this page has not been observed calling.
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
