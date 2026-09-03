---
name: birdlife-people-lifecycle
description: The joiner, mover and leaver process for BirdLife Australia staff and contractors across every system (Employment Hero, Entra ID/M365, Salesforce, NetSuite, Asana, WordPress, Zapier, Stripe, LearnUpon and the SaaS estate), including the order of operations, what a session executes versus prepares, the Salesforce licence and duplicate-user traps, and the departed-staff credential sweep. Use for any new starter, departing staff, role change, contractor onboarding, access request or "does X still have access" question, and for Ask Zeus Cases of Type New User or Departing Staff. Trigger on "onboard", "offboard", "new starter", "leaver", "departing", "last day", "starts Monday", "role change", "moved teams", "contractor access", "still has access", "deprovision", or "reclaim licence".
---

# BirdLife Australia: People lifecycle (joiner, mover, leaver)

Identity lifecycle is about 20% of the Ask Zeus queue and, per the M365 skill,
**there is no offboarding checklist in use today**. Leaver access removal is ad
hoc. This skill is the checklist, written so a session can run the parts it can
reach and prepare the rest for an admin with nothing forgotten.

The rule that outranks every other one here: **a leaver's access is removed
before anything else is tidied.** Convert, archive and reassign afterwards.

## The chain of record

| Order | System | Role in the chain | Join key |
|---|---|---|---|
| 1 | Employment Hero | Source of truth for people data and payroll | **BLA### worker code** (mandatory) |
| 2 | Entra ID / M365 | Identity, mail, licence, SSO into most SaaS | UPN `firstname.lastname@birdlife.org.au` |
| 3 | Salesforce | CRM and helpdesk users, 70 of 70 licences consumed | User `Username`; duplicates exist |
| 4 | NetSuite | Payroll (Infinet Cloud), ESS, finance roles | BLA### in the employee record |
| 5 | Asana | Work tracking, workspace `443963187362944` | Work email |
| 6 | WordPress | Website and WooCommerce admin/editor accounts | Work email; 25 admins today |
| 7 | Everything else | Zapier connections, Stripe dashboard users, Cloudflare, LearnUpon, Canva, Miro, Zoom, Google (GA4), Wrike, Smartsheet | Per app, mostly outside SSO |

Employment Hero rules that decide what arrives downstream: use "Add Employee"
and Start onboarding (never CSV Quick-add); capture the **personal** email at
invite (using the work email broke the invite loop); reactivate rehires, never
duplicate; company email in the standard format. The native EH→M365 add-on
**overwrites, never merges**: a blank EH field blanks the Entra field. Scope it
to Job Title, Department, Manager, Office Location only. The Logic App
employeeId sync is deployed and not working (EH 403). Until it works, BLA### is
keyed into Entra by hand.

## Tiers (what a session does itself)

- **Tier 1, execute after confirm:** Salesforce user reads, Case updates and
  closes, open-case reassignment, Asana task reassignment and comments,
  Outlook draft to the manager, checklists posted to the Case.
- **Tier 2, prepare for an admin:** every Entra/Exchange/Intune write (create,
  licence, groups, disable, mailbox conversion, session revoke, MFA reset),
  NetSuite user changes, WordPress admin removals, Zapier connection changes.
  Produce the exact command or click-path and post it on the Case.
- **Never unattended:** removing a person's access on a routine's say-so. A
  human confirms the last day and the name before any disable is run.

## Joiner

Trigger: Case Type `New User` (often from People and Culture) or an EH new
employee. Confirm start date, manager, role, location, and whether they need
Salesforce (because that is a licence decision, see below).

1. **Employment Hero** record exists with BLA###, personal email, manager.
   If not, the request goes back to P&C; nothing downstream is created first.
2. **Entra** (Tier 2): create user with the standard UPN, set manager,
   department, job title, employeeId = BLA###; assign **M365 Business
   Premium**; add to the department groups and DLs; require MFA registration
   at first sign-in (Authenticator, not SMS). Designed automation: create
   user, assign licence, notify IT and manager.
   ```
   Connect-MgGraph -Scopes "User.ReadWrite.All","Group.ReadWrite.All","Directory.ReadWrite.All"
   New-MgUser -DisplayName "First Last" -UserPrincipalName first.last@birdlife.org.au -MailNickname first.last -AccountEnabled -PasswordProfile @{Password="<vaulted temp>"; ForceChangePasswordNextSignIn=$true} -EmployeeId "BLA###" -Department "<dept>" -JobTitle "<title>"
   Set-MgUserLicense -UserId first.last@birdlife.org.au -AddLicenses @{SkuId="<Business Premium SKU>"} -RemoveLicenses @()
   ```
3. **Device** (Tier 2): Intune enrolment, compliance policy applies. Note
   the fleet is largely Windows 10 past EOL; a new starter should not receive
   a Windows 10 device.
4. **Salesforce** (Tier 1 read, Tier 1 write once approved): **70 of 70 full
   licences are consumed.** Before creating a user, name the licence being
   released (a leaver, or one of the 23 inactive sysadmin accounts). Check
   for an existing record first:
   `SELECT Id, Username, IsActive, Profile.Name FROM User WHERE Name = '<name>' OR Email = '<email>'`
   Reactivate rather than create a duplicate. Profile by role; System
   Administrator only with Mathew's explicit approval (ratio target 5%).
5. **NetSuite** (Tier 2): employee record with BLA###, role "Birdlife ESS
   Centre_No projects" unless finance; payroll set-up by Finance/Infinet.
6. **Asana** (Tier 1 via workspace admin, or prepare): invite to the
   workspace and the right team; never create a new team.
7. **Other SaaS**: only what the role needs, via SSO where the app supports
   it. Record any app outside SSO on the Case so the leaver sweep finds it.
8. **Close the Case** `Closed - Resolved`, Type `New User`, sub-type filled,
   with a checklist comment naming what was done and what the admin ran.

## Mover (role or team change)

1. EH updated first (title, department, manager). The add-on pushes those to
   Entra; check it did not blank anything.
2. Groups, DLs, SharePoint and Teams membership adjusted (Tier 2).
3. Salesforce profile, role node and public groups reviewed; remove what the
   old role needed. Case ownership: reassign open Zeus cases if they were a
   technician.
4. NetSuite roles reviewed against the four over-privileged templates.
5. Asana: move their tasks or reassign; the auto-generated "Consider
   delegating X's tasks" items are the signal that this was missed.

## Leaver

Trigger: Case Type `Departing Staff`, or the manager's email. **Confirm the
last day and the exact identity with a human before any step below.**

**On the last day, in this order (Tier 2, prepared as one script):**
1. Wait until after their final working hour (the designed flow uses a
   30-minute delay).
2. Revoke sessions: `Revoke-MgUserSignInSession -UserId <upn>`
3. Disable the account: `Update-MgUser -UserId <upn> -AccountEnabled:$false`
4. Convert the mailbox to shared and grant the manager access (Exchange
   Online): `Set-Mailbox <upn> -Type Shared`; `Add-MailboxPermission <upn>
   -User <manager> -AccessRights FullAccess`
5. Remove the licence: `Set-MgUserLicense -UserId <upn> -AddLicenses @()
   -RemoveLicenses @("<SKU>")`
6. Remove from all groups and DLs; remove any admin roles; wipe or retire the
   Intune device.
7. Set a 90-day deletion reminder (one-shot routine or Asana task with a
   date).

**Salesforce (Tier 1 after approval):**
1. Find every active User record for the person (duplicates exist):
   `SELECT Id, Username, IsActive, Profile.Name, LastLoginDate FROM User WHERE Name = '<name>' AND IsActive = true`
2. Reassign their open Zeus cases before deactivating:
   `SELECT Id, CaseNumber, Subject, Status FROM Case WHERE IsClosed = false AND RecordType.DeveloperName = 'Zeus' AND OwnerId IN (<ids>)`
   one at a time, each with an internal comment.
3. Reassign owned reports, dashboards and scheduled jobs (a private folder is
   lost with the user; Mathew's own Zeus dashboards sit in a private folder,
   the same risk applies to him).
4. Deactivate each record (`IsActive = false`). This releases a full licence:
   record who gets it.
5. If they were a sysadmin, note the new ratio.

**NetSuite (Tier 2):** inactivate the employee record and remove roles; Finance
handles final pay in Infinet. Check the person is not the linked entity on any
integration credential (Rachel Munt still is, on the OAuth2 certificate).

**Asana (Tier 1):** reassign or complete their open tasks, deprovision from the
workspace. Delegation prompts left unactioned are leaver debt.

**WordPress (Tier 2):** remove or demote the account; the current 25-admin list
includes people already agreed for removal.

**Zapier (Tier 2):** any connection they own (Outlook, Excel, LearnUpon
catch-hook on Keith's account) is re-owned or rebuilt before their account is
disabled, otherwise the Zap dies silently.

**Everything outside SSO:** Stripe dashboard users (five accounts), Cloudflare
account members, LearnUpon admin, Canva, Miro, Zoom, Wrike, Smartsheet, GA4,
Google Drive shares. Work from the joiner Case's list; if there is none, ask
the manager and record what you find.

**Close the Case** `Closed - Resolved`, Type `Departing Staff`, with the full
checklist and timestamps as an internal comment. That comment is the audit
trail the organisation currently lacks.

## Departed-staff credential sweep (run quarterly, and on every leaver)

Known items where departed people still hold a key or a role:
- NetSuite OAuth2 certificate linked to BLA216 Rachel Munt (departed), created
  by Matej Fucek (departed); expires 17 Sep 2026.
- Arun Nair (departed): BLAU DocGen framework in staging with uncaptured Apex
  and a corrupted specification. Knowledge loss, not access, but the
  permission sets remain.
- `ross.james.admin` is a Global Administrator in Entra and Ross James is on
  the WordPress removal list. **Verify Ross's employment status before the
  next GA review**; a departed GA is the single worst state this skill can
  find.
- 23 inactive Salesforce sysadmin accounts not deprovisioned, some five years
  stale.
- Test accounts `test101` and `test123` active with real credentials.

## Signals that the process is failing (raise them, do not step over them)

- Asana "Consider delegating X's tasks" prompts: someone left or moved and
  nobody reassigned.
- Salesforce cases owned by a deactivated or long-stale user.
- A Departing Staff case closed without a checklist comment.
- An Entra account with no sign-in for 30 days that is not on the IT-SEC-001
  service-account register.
- A licence request when the count is already 70 of 70 with no release named.

## Operating rules

1. **Confirm identity and last day with a human** before any disable.
2. **Access off first, tidy later.** Never let mailbox conversion or file
   handover delay the disable.
3. **Name the licence** released or consumed on every Salesforce user change.
4. **Never create a duplicate**: search Entra, Salesforce and EH first;
   reactivate.
5. **Tier 2 is prepared, not faked.** The script on the Case is the
   deliverable until the entra-admin connector is consented.
6. **The Case comment is the record.** Every step, who ran it, when.
