---
name: google-workspace-expert
description: "Expert operator knowledge for Google Workspace administration and for BirdLife Australia's tenant (C01muaswh) specifically: the admin model, how to read live state through the Directory API and console, the tenant's verified configuration, and the decision rules. Use for any Google Workspace admin, identity, 2SV, SSO, Drive sharing, Gmail security, OU, group, device, API access or posture task."
---

# Google Workspace, expert operator

## 0. The rule that comes first

Never assert a Workspace setting from memory. Read it live, then say what you read and when. Google changes console paths and defaults constantly, and this tenant has drifted from what earlier notes said. Baseline in section 3 was verified 11 September 2026; anything older than a month gets re-read before it is quoted to anyone.

## 1. The administration model

Five layers, in the order settings resolve:

1. **Customer** - the tenant. One customer ID (here `C01muaswh`), one edition, one set of domains. Edition caps what controls exist at all.
2. **Domains** - primary, secondary and alias. Secondary domains are separate user populations, not aliases.
3. **Organisational units** - a strict tree. A user is in exactly one OU. Settings inherit down and can be overridden per OU. **This is the only place most security settings can be scoped.**
4. **Groups** - can override service on/off and SSO profile assignment, but not most security settings. A group can only override one OU's setting per OU.
5. **User** - individual 2SV enrolment, admin roles, licences.

The practical consequence: when someone says "we have MFA", ask *at which OU*, because the root OU setting is what most of the tenant inherits, and a child OU can silently be weaker.

**Admin roles**: super admin is unscoped and total. Delegated roles (Groups, User Management, Help Desk, Services, Storage, Mobile, custom) are scoped to org units. Role assignments, not roles, are what to audit - a Help Desk Admin scoped to an OU can reset passwords for everyone in it.

## 2. How to read the tenant

### Directory API (fast, exact, use first)

Through the Zapier `GoogleWorkspaceAdminCLIAPI` connection (`google_workspace_admin_make_api_get_request`), authenticated as `mathew.hema.admin@birdlife.org.au`.

Works:
- `https://admin.googleapis.com/admin/directory/v1/users` with `customer=my_customer`, `maxResults=500`, and a `fields` mask. **Always use a fields mask** or the response blows the token budget. Useful mask: `nextPageToken,users(primaryEmail,suspended,isAdmin,isDelegatedAdmin,isEnrolledIn2Sv,isEnforcedIn2Sv,lastLoginTime,orgUnitPath,creationTime)`.
- `.../customer/my_customer/orgunits?type=all`
- `.../groups?customer=my_customer` with a fields mask
- `.../groups/{email}/members`
- `.../customer/my_customer/roles` and `.../roleassignments`
- Licensing API

Denied (Zapier scope gap, not an account gap): Reports API (usage and audit), Alert Center, user tokens, mobile devices, domains list.

When a user pull is too large for one tool result, it is written to a file - analyse it with a python script in bash rather than reading it back into context. `lastLoginTime` of `1970-01-01` means never signed in.

### Admin console (for everything the API cannot reach)

Sign in as the admin account, which lands on the `/u/2/` prefix. Verified paths:

| Setting | Path |
|---|---|
| 2-Step Verification | `/u/2/ac/security/2sv` |
| Password management | `/u/2/ac/security/passwordmanagement` |
| Login challenges | `/u/2/ac/managedsettings/352555445522/loginchallenge` |
| Account recovery / Passwordless / Advanced Protection | `/u/2/ac/managedsettings/352555445522/{accountrecovery,passwordless,titanium}` |
| SSO with Google as SAML IdP (certificates) | `/u/2/ac/security/ssocert` |
| SSO with third party IdP | `/u/2/ac/security/sso` |
| API controls | `/u/2/ac/owl` |
| Domain wide delegation | `/u/2/ac/owl/domainwidedelegation` |
| Google Cloud session control | `/u/2/ac/security/reauth/admin-tools` |
| Data protection / classification | `/u/2/ac/dp`, `/u/2/ac/dc` |
| Alert center | `/u/2/ac/ac` |
| Core service status | `/u/2/ac/appslist/core` |
| Drive and Docs settings | `/u/2/ac/appsettings/55656082996` (sharing: `/sharing`) |
| Gmail safety | `/u/2/ac/apps/gmail/safety` |
| Web and mobile apps | `/u/2/ac/apps/unified` |
| Devices | `/u/2/ac/devices/list`, settings `/u/2/ac/devices/settings/general` |
| Account settings | `/u/2/ac/accountsettings/profile` |
| Subscriptions | `/u/2/ac/billing/subscriptions` |

**Technique.** The console is an Angular app. `get_page_text` returns labels but not which option is selected. Use `javascript_tool` to read `aria-checked` on `[role="radio"],[role="checkbox"],[role="switch"]`, or take a screenshot. Nav items are not anchors on every page, but when they are, harvest real paths with:

```js
[...new Set([...document.querySelectorAll('a[href]')].map(e=>{const h=e.getAttribute('href')||'';return h.startsWith('/u/2/ac')?h.split('?')[0]+' :: '+(e.innerText||'').trim():null}).filter(Boolean))].join('\n')
```

Strip the nav chrome from `innerText` by slicing between `Privacy Policy` and `Main menu`. Clicking a `ref` from `find` often does not navigate in this console - prefer direct URLs. Extracting full `href` values including query strings can be blocked; use `a.pathname`.

## 3. BirdLife tenant baseline, verified 11 September 2026

**Edition**: Google Workspace for Nonprofits, free plan, all users licensed. No context aware access, no security investigation tool, no DLP, no Enterprise Plus charts. Hardening must use the controls that exist on this tier.

**Scale**: 383 accounts (328 active, 55 suspended), 11 domains, 27 OUs, 5 groups, 13 core services, 15 admin roles, 32 role assignments. 152 active accounts in `/Staff`; the other 176 are branches, programme communities and delegated mailboxes. Storage ~328 GB of 100 TB.

**Groups**: ICT Staff (5), Network Liaison Staff (5), Microsoft 365 SSO users / `sso-security-group-g@` (178), Survey Monkey (2), Classroom Teachers (0).

**Identity, the concentrated risk**:
- 2SV enforcement **Off** at the root OU. 313 of 328 active accounts have no second factor; 15 enrolled voluntarily; 8 enforced.
- Password policy: strong password **not** enforced, minimum 8 characters, reuse allowed, never expires.
- Entra SAML profile assigned to the `Microsoft 365 SSO users` group only. Root OU is set to None, so roughly 150 active accounts sign in with a Google password and nothing else.
- Google Cloud session control: no reauthentication policy set, 16 hour default session.

**Admins (8)**: super - `andrew.dunn@`, `keith.tsui@`, `mathew.hema.admin@`, `google@` (shared generic, also the tenant primary contact). Delegated - `christine.shaw@`, `fiona.cahill@`, `james.vilinsky@` (all /Staff, all 2SV), and **`test-user@wa.birdlife.org.au`, Branch user admin, no 2SV, last sign in 21 March 2023**. No break glass account, no privileged access review.

**Account contacts**: primary `google@birdlife.org.au`, secondary `amdunn1000@gmail.com`, a personal consumer address receiving tenant security and billing mail.

**SAML**: Google-as-IdP certificate `Google_2026-3-17-202127_SAML2_0` **expired 18 March 2026**, single certificate, and zero apps listed under Web and mobile apps.

**Drive**: external sharing on, anyone-with-link allowed, default new item private to owner, shared drive creation unrestricted, external members allowed on shared drives, download/print/copy enabled for viewers.

**Gmail safety**: all five spoofing and authentication protections **off**, all three attachment protections **off**, untrusted-link warning prompt **off**. Shortened URL and linked image scanning on. "Apply future recommended settings automatically" on.

**API access**: 0 restricted / 18 unrestricted Google services, 2 configured apps against 110 historically accessed, 0 pending review, no Marketplace apps. **Domain wide delegation: 3 clients** - GAM (`105856362628152449930`, 42+ scopes including `https://mail.google.com/`), Google Workspace Data Migration Service, and `gwmme-service-account@gwmme-1685490869766.iam.gserviceaccount.com`.

**Devices**: mobile management Custom, password requirements Basic, all devices user owned and auto-Approved, no managed Chrome browsers, no network profiles or certificates.

**Alerting**: Alert Center collecting, nothing triaged. All alerts Not started with no assignee, including a High severity super admin password reset for `ross.james@birdlife.org.au` (11 May 2026; account since suspended) and user-reported phishing to 12 June 2026. Six month retention.

**Dormancy**: 78 active accounts have never signed in, 69 have not signed in in over a year, 84 not in over six months. 56 accounts created in the last 12 months.

## 4. The two Google contexts, do not confuse them

1. The **BirdLife tenant** above.
2. The connected Google Drive, Gmail and Calendar MCP connectors, which authenticate as whichever account was last connected. Check before assuming. When they point at `mathew.hema.admin@`, that mailbox and Drive are empty. When they point at the personal `mathew.rua.hema@gmail.com`, they reach a personal consumer account that has held BirdLife work product, which is a data governance finding, not a convenience. Organisational documents belong in SharePoint or the BirdLife tenant.

The first-party Google connectors carry **no admin scopes**. Admin work goes through the Zapier Directory API connection or the console.

## 5. Decision rules

- **Before proposing consolidation onto Microsoft 365**, answer what happens to the 176 non-staff accounts. They are branch and programme communities, they are not M365 licensed, and they are the reason Workspace persists.
- **Scope every change to an OU and name it.** "Turn on 2SV" is not a plan. "Enforce at /Staff with a two week enrolment window, then branches" is.
- **Sequence identity changes one at a time.** 2SV first, password policy second. Users absorb one change; two at once produces a helpdesk spike and workarounds.
- **Branch and volunteer accounts are not staff accounts.** Dormancy cleanup outside /Staff needs the branch coordinator's confirmation first. Some accounts are legitimately used once a season.
- **Domain wide delegation outranks almost everything else.** A DWD client with `https://mail.google.com/` is a standing, non expiring, unattended key to every mailbox. Know who holds it before touching anything else.
- **Gmail spoofing protections are free on this edition.** There is no cost argument for leaving them off at a charity that solicits donations.
- **Google Workspace is outside the Azure and M365 security programme.** It is the gap the SaaS overlay in the Security Framework exists to close. Report on it separately or it disappears.
- **Never promise an admin action the tooling cannot perform.** Directory reads and user/group/role writes work through Zapier. Security settings, sharing policy, Gmail safety, SSO and DWD are console-only.

## 6. Standing remediation queue

Ordered by risk reduction per hour, with the people impact that has to be stated alongside each:

1. Remove `test-user@wa.birdlife.org.au` and its role assignment. Nobody is affected.
2. Enable the Gmail spoofing and attachment protections. Warn branch coordinators; poorly configured branch senders may land in spam for a fortnight.
3. Move the tenant primary and secondary contacts off `google@` and off the personal Gmail address. Agree with Andrew Dunn first.
4. Inventory then revoke the GAM domain wide delegation; remove the two migration clients. Ask Andrew and Keith whether GAM scripts are running before revoking.
5. Enforce 2SV in stages: admins and ICT Staff, then /Staff, then branches. Two week enrolment window, allow trusted devices. Federated users see nothing; the ~150 Google password users need enrolment support and branch volunteers are the group most likely to be locked out.
6. Password policy: strong, minimum 12, no reuse, enforce at next sign in. After 2SV, not with it.
7. Resolve the expired Google SAML IdP certificate: find the relying parties, then reissue or retire.
8. Restrict the 18 unrestricted Google services, or move to allowlisting with a stated request path.
9. Constrain Drive: disable user shared drive creation, review anyone-with-link.
10. Name an Alert Center triage owner with a five business day SLA into the Ask Zeus queue.
11. Dormant account cleanup, branch coordinators consulted first.

## 7. Known blind spots

- Reports API and audit log history are not reachable through the current connection. Getting that scope granted is the single biggest capability gain available.
- Shared drive inventory and per drive external membership have not been enumerated.
- All section 3 settings were read at the **root OU**. Child OU overrides have not been spot checked; /Staff and /wa.birdlife.org.au are the two to check first.
- Who holds the GAM private key is unknown. Ask, do not infer.