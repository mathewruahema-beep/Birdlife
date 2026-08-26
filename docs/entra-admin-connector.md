# Entra admin connector — promoting Tier 2 to Tier 1

> **STATUS: DONE (26 Aug 2026).** `entra-admin-mcp` registered, all Graph
> permissions + `Exchange.ManageAsApp` admin-consented, Exchange Recipient
> Administrator assigned, certificate uploaded (thumbprint
> `23F3A8D1D5C1C1D03CE0E5DCC9AB8A153EEBCA39`, expires 26 Aug 2027 — renewal
> reminder Routine set for 26 Jul 2027), and verified end to end with app-only
> `Connect-MgGraph` + `Get-MgUser`. Remaining: point the local `entra-admin`
> server config at the app, and the follow-up hardening of scoping the
> Exchange role with a management scope. The plan below is kept as the record.

Goal: give the assistant an **approve-only write path into Entra ID and Exchange
Online**, so the Tier 2 playbooks (offboarding, onboarding, licences, MFA resets,
mailbox and distribution-list access) stop being "here's the PowerShell for an
admin to run" and become "reviewed, approved, executed, logged" in one sitting.

This stays inside the automation model already chosen: **the assistant prepares
and proposes; Mathew (or another GA) approves every write.** The connector changes
who types the command, not who decides.

## Where things stand

- A **read-only** Entra/Intune MCP server runs locally at `C:\azureintegration`
  (app `d8125f4d…`). It can look but not touch.
- A **write-tier `entra-admin` server exists but is blocked** on a separate app
  registration and admin consent. That consent is the single gate — everything
  below is the checklist for landing it properly.
- The connected Microsoft 365 connector is productivity-scoped (mail/calendar/
  SharePoint/Teams). It will never do tenant admin; don't try to widen it.

## Step 1 — App registration (portal, ~15 min, needs GA)

Tenant: `2b431a7b-9a21-4b53-8943-4a10ff69970d` (birdlife.org.au).

1. Entra admin center → App registrations → **New registration**
   - Name: `entra-admin-mcp` — single tenant, no redirect URI (daemon app).
2. **API permissions → Microsoft Graph → Application permissions** — least
   privilege, mapped to the playbooks it unlocks:

   | Permission | Unlocks |
   |---|---|
   | `User.ReadWrite.All` | Disable/enable accounts, revoke sessions, create starters, assign/reclaim licences |
   | `Group.ReadWrite.All` | Security & M365 group membership (add/remove on on/offboarding) |
   | `UserAuthenticationMethod.ReadWrite.All` | MFA method reset + require re-registration |
   | `Organization.Read.All` | Read licence SKUs before assigning |
   | `AuditLog.Read.All` | Check risky sign-ins before any security action |

   Do **not** add `Directory.ReadWrite.All` — it's broader than any playbook needs.
3. **Grant admin consent** for the tenant. This is the moment Tier 2 becomes Tier 1.
4. Credential: **certificate, not client secret** (self-signed is fine, 12-month
   validity). Store it in `kv-emphero-sync` or a dedicated vault — and unlike the
   EH-sync secrets, **record the expiry** (set a calendar reminder; the Graph
   secret for EH-sync expiring 2027-01-05 has no such reminder today — fix both).

## Step 2 — Exchange Online (the part Graph can't do)

Classic **distribution lists, mailbox-to-shared conversion, and mailbox
permissions are not manageable via Graph** — they need Exchange Online PowerShell:

1. On the same app registration add **Office 365 Exchange Online →
   `Exchange.ManageAsApp`** (application) and consent.
2. Assign the app the **Exchange Recipient Administrator** role (Entra → Roles →
   assign to the enterprise app). Recipient admin, not Exchange Administrator —
   it covers DLs, shared mailboxes and permissions without org-config rights.
3. The server then runs `Connect-ExchangeOnline -CertificateThumbprint … -AppId …
   -Organization birdlife.org.au` for: `Set-Mailbox -Type Shared`,
   `Add-MailboxPermission`, `Add-RecipientPermission`,
   `Add/Remove-DistributionGroupMember`.

## Step 3 — Wire it up and test

1. Point the `entra-admin` MCP server at the new app (app ID + certificate).
2. Smoke-test read: `GET /users/mathew.hema@birdlife.org.au` returns.
3. Smoke-test write on a **disposable target only** — and there's a ready-made
   one: the MFA audit lists active test accounts `test101` / `test123` that are
   flagged for disable/delete anyway. First real write = disable `test101`,
   verify `accountEnabled=False`, done. That's a test *and* a P1 remediation item.
4. Run one end-to-end offboarding on the next real leaver with Mathew approving
   each step, in the designed order: revoke sessions → disable account → mailbox
   to shared → reclaim licence → remove groups/DLs → 90-day delete reminder.

## Guardrails (unchanged by the connector)

- **Approve-only stays.** Every write is proposed with the exact call and target,
  and executed only on a go-ahead. No batch writes.
- **Never touch** `breakglass01@` / `breakglass02@` (verify they exist first —
  the programme guide says they may not yet), the GA accounts, or any CA policy
  via this path. Conditional Access changes keep their own report-only-first rule.
- Fields the EH sync owns (Job Title, Department, Manager, Office Location) are
  written upstream in Employment Hero, never directly — the native add-on
  overwrites, so a direct Entra write there just gets clobbered.
- Every action is logged back to the originating Ask Zeus Case as a CaseComment.

## What this unlocks, concretely

~20% of the Zeus queue is identity lifecycle (IAM 49 + Departing Staff 22 + New
User 16 of the last 425 cases). Today each of those tickets ends with a prepared
script waiting for an admin. With this consent landed, "Offboard <name> — last
day <date>" becomes a supervised five-minute conversation, offboarding stops
being ad hoc (there is currently **no offboarding checklist at all**), and
departed-staff licences get reclaimed the same day instead of whenever someone
remembers.
