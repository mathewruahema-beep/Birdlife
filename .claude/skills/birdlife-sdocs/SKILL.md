---
name: birdlife-sdocs
description: "Expert operator knowledge for configuring, administering and using S-Docs and S-Sign in BirdLife Australia's Salesforce org, and for replacing the live Conga Composer and Conga Batch receipting estate including the EOFY run."
---

# S-Docs at BirdLife Australia

Use for any task involving S-Docs, S-Sign, document generation, receipting templates, batch document runs, renewal notices, or the Conga replacement. Trigger on "S-Docs", "SDoc", "S-Sign", "e-Signature", "receipt template", "Conga", "Conga Batch", "EOFY receipts", "renewal reminder", "merge field", "named query", "Direct SOQL", "template editor", "batch generation", "doclist".

Read `birdlife-core` first for write authority and evidence rules, `birdlife-salesforce` for the Zeus org model, `birdlife-prompting` before acting on any request.

---

## 1. Verify before asserting

Never assume S-Docs is installed. Run these first:

```sql
-- Is the package present in this org?
SELECT QualifiedApiName, Label FROM EntityDefinition
WHERE QualifiedApiName LIKE 'SDOC%' OR QualifiedApiName LIKE 'SSign%'

-- Which org am I in?
SELECT Id, Name, InstanceName, IsSandbox FROM Organization

-- Templates, once installed
SELECT Id, Name, SDOC__Template_Format__c, SDOC__Related_To_Type__c,
       SDOC__Available_For_Use__c FROM SDOC__SDTemplate__c
```

**Verified state, 10 Sep 2026: S-Docs is installed in NEITHER org.** Zero SDOC or SSign entities in production and zero in staging (`00DBn00000CAloLMAT`). Production correctly runs entirely on Conga. Staging holds all 80 Conga Batch records, so it is a valid recent copy, but the trial recorded as installed on 9 Sep is gone.

**Most likely cause, and it matters.** The S-Docs knowledge base states you do *not* need to reinstall after a sandbox refresh, because a refresh copies production metadata including the package. Production has no S-Docs. So a refresh of staging from production *removes* a trial installed only in the sandbox. If staging was refreshed after 9 Sep, that is the explanation, and the fix is reinstall plus reactivation against the org ID.

One caveat before declaring it missing: `EntityDefinition` reflects the querying user's visibility. Confirm in Setup, Installed Packages. If it is listed there but the query returns nothing, that is an "Install for Admins Only" permissions state, not a missing package, and a far smaller fix.

---

## 2. Live evidence baseline (production, verified 10 Sep 2026)

| Measure | Value |
|---|---|
| Conga Batch records (`APXT_BPM__Conductor__c`) | 80 |
| Actively scheduled | 17 (plus 1 disabled: Payment Transactions, Finance) |
| Conga Solutions (`APXTConga4__Conga_Solution__c`) | 10 (5 real, 5 test) |
| Conga Merge Queries (`APXTConga4__Conga_Merge_Query__c`) | 170+ |
| Conga Templates (`APXTConga4__Conga_Template__c`) | 31, all auto-named CMT-000xx, no descriptions, no groups |
| Receipt PDFs generated, last 30 days | **1,424** |
| EOFY 2026 receipts generated | **2,911** |
| Packages | APXTConga4, APXT_BPM, CongaWorkflow, APXT_CongaSign |

Refresh these before quoting them. Queries in section 12.

**Rebuild the 17, retire the other 63.** Confirm with supporter care and finance that nothing live sits in the 63 before deleting.

**The template estate is undocumented.** 31 template records with system-generated names, no descriptions, no groups. Nobody can tell which template a batch uses without opening the button formula. Fix this in the rebuild: name S-Docs templates meaningfully and populate Description and Category, both of which S-Docs surfaces in the picker search and in the migration export filter.

**Stacked concurrency already exists.** Three routines fire at 14:30 and two at 19:00. Do not replicate that pattern in the Flow schedules.

---

## 3. Concept mapping

| Conga | S-Docs |
|---|---|
| Composer button | S-Docs button, or the Generate Documents LWC (prefer the LWC for supporter care) |
| Conga Solution | Template record plus button parameters |
| Merge Query | Get Records in a Flow, or a Direct SOQL related list |
| Conga Batch record | Scheduled Flow calling `SDOC__GenerateBatchInvocable`, or an S-Doc Job |
| Conga Batch schedule | Native Salesforce scheduled Flow |
| Conga email template | HTML template with the Email Settings tab |
| Conga Word or PDF template | WYSIWYG PDF template, or PDF-UPLOAD |
| Conga Trigger | Record-triggered Flow calling the SDK |
| Conga Sign | S-Sign, or drop |

There is no S-Docs feature shaped like Conga Batch. Batch is a Flow pattern: Get Records, loop, build collection variables of record IDs and template IDs, call the batch invocable.

---

## 4. Setup checklist

1. Install from the AppExchange into a sandbox. **S-Sign is a separate managed package not on the AppExchange** and needs a direct link from the S-Docs rep.
2. Object Manager, **SDoc Template**, Related to Type: add every object's API name as a picklist value. For BirdLife at minimum `Opportunity`, `Contact`, `AAkPay__Subscription__c`.
3. Object Manager, **SDoc Relationship**: create a lookup relationship for every object that will display documents.
4. Add the two LWCs (Create Document, Generated Documents) and/or buttons to page layouts.
5. Permission sets: **S-Docs Administrator** for template builders, **S-Docs User** for generators. A generating user also needs **Create and Read on SDoc Template**, not Read alone, or generation fails with misleading errors.
6. Templates referencing external images need a **Remote Site Setting** for that domain, or the logo silently fails in production.

---

## 5. Template formats

| Format | Built where | Best for | Hard limit |
|---|---|---|---|
| WYSIWYG editor | Salesforce | PDF, HTML email, DOC, XLS, PPT, CSV | None material |
| PDF-UPLOAD | Existing PDF, fields dragged on | Fixed-length forms | No related lists |
| DOCX / XLSX / PPTX | Word, Excel, PowerPoint | Teams that will not leave Office | **Cannot output PDF** |
| DOC-NEW | Section-based S-Docs editor | Word with section breaks, conditional sections | Word only |
| Component | Salesforce, single tab | Reusable blocks | Not standalone |

**Every BirdLife receipt must be PDF, so DOCX is never an option for them.** Build receipts in the WYSIWYG editor. Source code is available only in Template Editor formats, never in PDF-UPLOAD, DOCX, PPTX or XLSX.

---

## 6. Syntax reference

### Merge field attributes
Appended after a space inside the field:

| Purpose | Syntax |
|---|---|
| Number mask | `{{!Opportunity.amount #,###}}` |
| Date mask (Java pattern) | `{{!Opportunity.closedate M/d/yyyy}}` |
| Phone mask | `{{!Object.phone ###-###-####}}` |
| Boolean as tick box | `{{!Object.flag__c checkbox="true"}}` |
| Right to left | `{{!Object.name RTL="true"}}` |
| Translation Workbench picklist | `{{!Object.type translate="true"}}` |
| Rich text, formatting retained | `{{{Object.rtf__c}}}` (three braces) |

Only number, date and phone masks appear in the Insert Field wizard. The rest are typed.

### Special merge fields
`{{!DocumentID}}` (S-Doc ID such as SD-174, not a Salesforce ID) | `{{!DocumentName}}` | `{{!DocumentObject}}` | `{{!DocumentDate}}` | `{{!DocumentDateSOW}}` | `{{!DocumentDateEOW}}` | `{{!DocumentDateTime}}` | `{{!DocumentFormat}}` | `{{!ObjectId18}}` | `{{!ObjectId15}}` | `{{!PageNumber}}` and `{{!PageCount}}` (PDF only) | `{{!UserFirstName}}` | `{{!UserLastName}}` | `{{!UserName}}` | `{{!UserOrganizationName}}` | `{{!UserLoginName}}` | `{{!UserEmail}}` | `{{!UserDepartment}}` | `{{{!UserSignature}}}`

`{{!DocumentDate}}` is what rebuilds the date in BirdLife's receipt file names (section 11).

### Conditional logic: RENDER, not IF
```
<!--RENDER= {{!Opportunity.amount}} > '10000000' --> content <!-- ERENDER -->
```
Nesting uses `RENDER1`, `RENDER2` and so on, up to 5 levels, set with Render Level in the builder. Compound logic uses `&&` and `||` with parentheses. Use `CONTAINS` and `NOT CONTAINS` for substrings and multi-select picklists. Any merge field S-Docs supports can drive a condition, including a named query field.

### Switch statements (absent from the training, ideal for BirdLife)
Maps many values to many outputs from a JSON map held in a separate template, instead of thirty nested conditions.
```
<!--{{!
<switch>
<switchMap>Membership Tier Wording</switchMap>
<formula>{{!AAkPay__Subscription__c.AAkPay__Payment_Option_Name__c}} == '{{!SWITCH_KEY}}'</formula>
<outputForEachMatch>{{!SWITCH_VALUE}}</outputForEachMatch>
</switch>
}}-->
```
The switch map template holds JSON: `{"Full Member":"...","Concession":"...","Wader":"..."}`. Insert in Source view. Name matching is case sensitive. No trailing comma after the last value.

This is the right pattern for membership option wording, which currently drives a `LIKE '%Wader%' OR LIKE '%Seabird%' OR ...` chain in the Conga queries.

### Arithmetic (also absent from the training)
```
<MATH>( {{!Opportunity.Amount}} - {{!Opportunity.Fee__c}} )</MATH>
```
Standard Salesforce math operators. **Subtraction needs a space either side of the minus** or it reads as a negative number. Format with `format-number="#,###.##"`, dates with `type="date"`. Date functions: `DAYS(X)`, `MONTHS(X)`, `YEARS(X)`, `DaysBetween()`, `MonthsBetween()`, `YearsBetween()`. In DOCX use lowercase `<math>` in square brackets.

### Related lists
Wizard tabs: Select Related List and columns, Format Date Columns, Filters and Sort Order, Formatting and Styles. Insert adds only the header, carrying a commented `UNIQUEID:nnn` which is how you find it again in Source.

Column attributes: `format-date`, `format-number`, `format-phone`, `prefix`, `postfix`, `nullpostfix`, `type="rtf"` (required when prefix or postfix injects HTML such as `<br />`), `showcolumn` (conditional column). Filtering, limiting and sorting appear as `<where>`, `<limit>`, `<orderby>`, all SOQL, editable in the wizard or in Source. Set table width to 100 per cent rather than the default.

### Direct SOQL
Ticking Direct SOQL exposes every queryable object **and removes record context**, so an unfiltered list returns every record in the org. Reintroduce context in the WHERE clause: `AccountID = '{{!Account.ID}}'`. Left side is the lookup API name on the queried object, right side is a merge field resolved at generation. Both sides support relationship traversal four or more levels deep.

Use it for all records of a child object regardless of relationship, or for a grandchild object. Technique: select placeholder fields matching the column count, then fix field names in Source, so the column tags and CSS are generated for you.

Do not use the Available Related List section to edit an existing list. Find it in Source by its unique ID, or delete and re-insert.

### Class none
"Insert related list without table markup" strips CSS and header and returns raw data. Shape with prefix and postfix and `type="rtf"`. Best route for merging a run of images by building an `<img>` tag around each URL.

### Named queries
Method 1, single record: `<queryname>` names the variable, `<soql>` holds the query, limit it to 1. Method 2, multiple records: triggered by the presence of `<filter>` tags holding a WHERE clause **without** the word `where`; address records with `offset="2"` (zero indexed). Multiple filters, each with its own ID, let one named query serve several criteria. Filter IDs are not zero indexed because you define them.

Insert Field does not detect named query fields, so type them. Named query results can feed anything a merge field can feed, including conditional logic, an email To field and a signer email, and one named query can feed another's filter.

Use when the object is more than four lookups away, has no direct relationship, or you need a single child record such as a primary contact.

### Components
```
{{{{!TCSTANDARD}}}}
```
Four braces. Insert via parent template, Insert Field, Other Templates tab. PDF-Upload templates can act as components. Dynamic parameterised component references are supported.

For BirdLife: build the letterhead, footer, DGR tax-deductibility statement and ABN block as components once. Every receipt template references them, so a brand change is one edit.

### Apex from a template
S-Docs can call Apex classes from a template. Reserve for cases nothing else covers, and record it as an ADR, because it reintroduces the code dependency the Conga replacement is meant to remove.

### Template tabs
Output file name is on **Document Options** and accepts merge fields. The Preview button is on **Advanced Options**. International characters need the checkbox plus Unicode enforcement set to Strict. Header supports a different first page via "Use first page header for all pages".

### Runtime prompts
Button only, never the LWC. Types are checkbox, date and text. "Write this data back to Salesforce" accepts a merge field and is the only route by which generation-time user input reaches Salesforce. Use the `prefillRTP` parameter to pre-fill answers under one-click automation.

---

## 7. Button and URL parameters

All parameters are case sensitive. The ones that matter here:

| Parameter | Effect |
|---|---|
| `doclist=` | Comma-delimited template names or IDs to generate automatically |
| `oneclick=` | `True` (default) generates immediately, `False` pre-selects without generating |
| `sendemail=1` | Create and automatically send the email |
| `prepemail=1` | Create the email but do not send |
| `SetOrgWide=` | Set the From address to an org-wide address |
| `categoryfilter=` | Restrict the template picker to categories |
| `searchfilter=` | Restrict by name or description text |
| `additionalFields=` | Show extra template fields as filterable picker columns |
| `prefillRTP=` | Pre-fill runtime prompt answers for one-click automation |
| `previewFirst=True` | Do not create the file until the user confirms |
| `autodownload=` | Download after generation |
| `customRedirect=` | Send the user somewhere specific afterwards |
| `autoSSign=1` | Fire an S-Sign request automatically |
| `UIlanguage=` / `language=` | Translate the interface / the merge fields |

`doclist` is what breaks on an org move, because template IDs change. **Prefer template names over IDs in `doclist`** for anything that has to survive sandbox to production.

---

## 8. Automation

### Invocable Apex actions for Flow Builder

| Action | Apex name | Inputs | Output |
|---|---|---|---|
| Generate Document | `SDOC__GenerateDocumentInvocable` | Base record ID, template ID | `sdocId` |
| Generate Documents in Batch | `SDOC__GenerateBatchInvocable` | Collection of base record IDs, collection of template IDs, batch size | `jobId` |
| Combine Documents | `SDOC.CombinedDocumentHandler()` | Comma-delimited S-Doc file IDs, output name | Combined PDF |
| Generate S-Doc With Input | `SDOC__UserInputInvocable` | Base record ID, template ID, screen-flow input | `sdocId` |
| S-Docs Email | `SDOC_EmailInvocable` | Template, recipients, attachments | Send confirmation |
| Document Data Refresh | `SDOC_RefreshDocumentDataInvocable` | Generated document ID, record ID | `sdocId` |
| Prepare Envelope | `SDOC__PrepareEnvelopeInvocable` | Documents, materials, recipients | `envelopeId` |
| Seal Envelope | `SDOC__SealEnvelopeInvocable` | Envelope ID | `signingLink` |

Prepare and Seal Envelope must run in **separate transactions**. Combine Documents is Fall '25 or later. Batch collation options (not collated, or collate by base record) are Spring '25 v9.0 or later.

### Batch mode, and the number that matters
**The batch invocable defaults to a batch size of 5.** That is the single most important operational fact for BirdLife. At 2,911 EOFY documents a default batch size means roughly 583 queueable chunks. Size it deliberately against Salesforce governor limits and test at full EOFY volume in a sandbox before the first live EOFY.

Batch job progress is monitored in **Setup, Apex Jobs**, not inside S-Docs.

### S-Docs Jobs (the closer analogue to Conga Batch)
Object: **S-Doc Job**. Required fields: `Object ID`, `Object API Name`, `Doclist`, `Send Email` (1 or 0), `Start Job` (boolean, must be true to begin). Optional: Incl. Attachments / Documents / Files with Email, Include All Related Files, Email From, Email Params. Status runs 0, 10, 20, 35, 40, 60, 80, 90, Completed, Error, with Status Details carrying the error text. Generated documents land in SDoc1, SDoc1 View, SDoc2 and so on.

Jobs are created by Flow, Process Builder or an Apex trigger, never manually.

**The knowledge base states automation is only available to S-Docs Unlimited Edition for an additional fee.** The quote says the per-document option includes "batch, automation". Get that confirmed in writing before signing.

### Custom settings that govern batch behaviour
Record name must be `SDocsSettings`.

| Setting | Why it matters |
|---|---|
| `SDJobs Batch Size` | Concurrent S-Doc Jobs. **45 is the vendor recommendation.** |
| `SD Jobs Fail If Template Error` | Halt the job on a document-level error. For receipting, decide deliberately: halt and investigate, or continue and reconcile. |
| `Allow Templates With Error to Generate` | Permits generation despite template errors. Leave off for receipting. |
| `SD Jobs Move to Top of Flex Queue` | Prioritise S-Docs in the async queue. Useful in the EOFY window. |
| `Process Job Splitters Concurrently` | Parallel queueable processing. |
| `Concurrent Master Wait Time` | Seconds between file-creation attempts, default 3. |
| `Send SDJobs Email as Future` | Routes job emails through future methods. |
| `Salesforce Home URL` | Base domain for image URLs. Must be corrected after any org move. |
| `Platform Encryption Enabled` | Shield compatibility. |
| `Don't Run SDTemplate Trigger` | Skips the template trigger during bulk template operations, useful during migration. |
| `ConnectedApp*` settings | S-Sign only. |

---

## 9. Migrating templates between orgs

Requires S-Docs 4.210 or higher, and S-Sign 2.78 or higher for S-Sign templates.

1. App Launcher, S-Docs, **S-Docs Setup**, "Migrate S-Docs & S-Sign Templates". On older versions append `/apex/SDOC__SDMigrate` to the org URL.
2. Set a SOQL export filter, for example `WHERE Document_Category__c='Receipting'`. Click Set Export Filters.
3. Optionally exclude attachments or specific fields. Generate Export Zip.
4. In the target org, upload the zip, optionally override field values, Start Import.

Carried across: template content and structure, attachments (DOCX and PDF), S-Sign data and settings, custom field values.

Needs fixing afterwards: anything referencing sandbox data, image URLs, related lists built against sandbox records, preview record IDs.

Individual import is fine under 15 templates. Data Loader is not recommended and creates duplicates.

**Categorise templates from day one.** The export filter is SOQL against template fields, so a Category of `Receipting`, `Renewal` or `EOFY` makes deployment a one-line filter rather than a hand-picked list.

---

## 10. Sandbox refresh runbook

You do **not** reinstall S-Docs after a refresh, provided the package exists in production. Three things break:

1. **Record ID references.** Preview IDs point at production records. Template IDs in `doclist`, Jobs and one-click buttons become invalid.
2. **URL and domain references.** `login.salesforce.com` becomes `test.salesforce.com`, production domains become sandbox domains.
3. **S-Sign site.** The production site URL stops working and must be deactivated and recreated.

Remediation: update `SDocsSettings` login and domain URLs and `ConnectedAppUserName`; add Remote Site Settings for the sandbox login and domain; set the Connected App callback to `https://test.salesforce.com/services/oauth2/callback`; recreate the S-Sign site and re-verify the guest user email against Organization-Wide Addresses.

**BirdLife caveat:** none of this applies while production has no S-Docs, because a refresh simply removes a sandbox-only trial install. Until production is licensed, treat every staging refresh as destroying the S-Docs environment and plan the rebuild window accordingly.

---

## 11. The BirdLife rebuild specification

### Output naming must be preserved
Live Conga output, read from ContentVersion on 10 Sep 2026:

- `BirdLife Australia Receipt - {Contact Name} - Donation ${Amount} {dd-MM-yyyy}.pdf`
- `BirdLife Membership Receipt (2) - {Contact Name} - Membership ${Amount} {dd-MM-yyyy}.pdf`
- `EOFY 2026 Receipt - {Contact Number}`

Rebuild these exactly on the **Document Options** tab, which accepts merge fields. Finance and supporter care search on these names. Changing the convention breaks how they find receipts, which is a people cost with no offsetting benefit.

Note the literal `(2)` in the membership receipt name. Almost certainly a duplicated Conga template never cleaned up. Confirm with supporter care and drop it if it is an artefact.

### The 17 scheduled routines

**Receipting (Opportunity based)**

| Batch | Title | Schedule | Query |
|---|---|---|---|
| 0008 | Donation Receipts, email | Daily 19:00 | CMQ-0000 |
| 0014 | Donation Receipts, print | Weekly Thu 20:00 | CMQ-0012 |
| 0016 | Membership Receipts, email | Daily 19:00 | CMQ-0018 |
| 0015 | Membership Receipts, print | Weekly Thu 19:15 | CMQ-0017 |
| 0040 | Photography Membership, email | Daily 14:30 | CMQ-0076 |
| 0039 | Photography Membership, print | Weekly Thu 19:30 | CMQ-0077 |

Email variants filter on `Receipt_Status__c = 'Email receipt'`, primary contact has an email, `Receipt_Preference__c NOT IN ('Print','Annual')` and not Pardot hard bounced. Print variants filter on `Receipt_Status__c = 'Physical receipt'`, primary contact has a MailingStreet, `Receipt_Preference__c NOT IN ('Email','Annual')`. All carry `OR Regenerate_donation_receipt__c = TRUE`, which is how staff force a reissue. **That escape hatch must survive the rebuild.** Print queries limit to 500. Donation queries also require `IsRD__c = FALSE` and RecordType in Donation or Major Gift.

**Renewal reminders (`AAkPay__Subscription__c` based)**

| Batch | Title | Schedule | Query | Window |
|---|---|---|---|---|
| 0067 | NON-AR 10 day reminder, email | Daily 14:30 | CMQ-0143 | End date next 10 days |
| 0069 | AUTO-RENEW credit card 10 day, email | Weekdays 14:30 | CMQ-0144 | Next 10 days, pay method Credit Card |
| 0073 | AUTO-RENEW direct debit 10 day, email | Weekdays 14:45 | CMQ-0159 | Next 10 days, pay method Direct Debit |
| 0068 | NON-AR 37 day, print, AU | Weekly Thu 18:00 | CMQ-0145 | Next 37 days, MailingCountry Australia |
| 0070 | AUTO-RENEW 37 day, print, AU | Weekly Thu 18:15 | CMQ-0146 | Next 37 days, Australia |
| 0071 | AUTO-RENEW 60 day, print, O/S | Weekly Thu 18:30 | CMQ-0147 | Next 60 days, not Australia |
| 0072 | NON-AR 60 day, print, O/S | Weekly Thu 18:45 | CMQ-0156 | Next 60 days, not Australia |

Common exclusions across all seven: status not Cancelled and not Expired, payment option not LIKE Lifetime, Complimentary or Legacy, `Former_Gift_Membership__c = FALSE`, `Renewal_Notification__c = FALSE`, plus the channel gate `OK_to_Email_Reminder__c` or `OK_to_Print_Reminder__c`.

**Cease and expiry notifications (`AAkPay__Subscription__c` based)**

| Batch | Title | Schedule | Query | Window |
|---|---|---|---|---|
| 0075 | Cease notification, email | Daily 15:00 | CMQ-0163 | Cease date next 30 days |
| 0076 | Cease notification, print | Weekly Thu 21:00 | CMQ-0162 | Next 37 days, AU, excl. SIG |
| 0074 | Expiry notification, email | Daily 02:45 | CMQ-0164 | Next 60 days |
| 0077 | Expiry notification, print | Weekly Thu 21:15 | CMQ-0161 | Next 67 days, AU |

Gates: `Cease_Notification__c = FALSE` or `Expiry_Notification__c = FALSE`, `Special_Interest_Group__c = FALSE` on two of them, print limits 500.

### The EOFY run
Not on a schedule. Fired manually in the June to July window. 2,911 documents in 2026.

- **CMQ-0001**, print. Contact, not deceased, has MailingStreet, and (Print preference OR IsEmailBounced OR Pardot hard bounced OR no Email), `Total_Wildbird_Gifts_Last_Financial_Year__c > 0`, LIMIT 200.
- **CMQ-0008**, email. Contact, not deceased, not bounced on either channel, has Email, not Print preference, gifts last FY > 0, `DoNotEmailReason__c != 'BL Dummy Email'`, `EOFY_Batch_Downloaded_Year__c = '<year code>'`, LIMIT 5000.
- **CMQ-0010**, manual print. MailingStreet not null, not major gift donor, not Do_Not_Mail, `Total_RG_Gifts_Last_Financial_Year__c > 0`, not already downloaded this calendar year, LIMIT 200.
- **CMQ-0172 / CMQ-0173**, test batches against hard-coded contact IDs. Do not migrate.

`EOFY_Batch_Downloaded_Year__c` is the anti-duplicate marker. Whatever replaces it must be written back **after** a successful send, not before, or a failed run silently suppresses the reissue.

### The Pardot dependency
`pi__pardot_hard_bounced__c` appears in CMQ-0000 (daily donation receipts), CMQ-0008 (EOFY email), CMQ-0018 and CMQ-0076 (membership receipts), CMQ-0144 (auto-renew credit card reminders) and CMQ-0162 (cease print). Pardot is being decommissioned for Ortto. Get the Ortto bounce equivalent from marketing **before** the S-Docs queries are written. See `birdlife-pardot-decommission`.

### Build sequence
1. Fix the environment. Nothing else can start.
2. Build the four components: letterhead, footer, DGR statement, ABN block.
3. Build one template end to end (donation receipt, PDF, WYSIWYG) and validate the output file name against the live convention.
4. Build one Flow end to end for batch 0008 with a deliberate batch size.
5. Run it in parallel with Conga for one full weekly cycle and reconcile document counts.
6. Then the remaining receipting, then renewals, then cease and expiry.
7. EOFY last, tested at full 2,911 document volume before June.
8. Retire the 63 unscheduled Conga Batch records once supporter care and finance confirm none are live.

---

## 12. Queries to refresh the evidence

```sql
-- Scheduled routines
SELECT Name, APXT_BPM__Title__c, APXT_BPM__Schedule_Description__c,
       APXT_BPM__Next_Run_Date__c, APXT_BPM__Query_Id__c, APXT_BPM__URL_Field_Name__c
FROM APXT_BPM__Conductor__c WHERE APXT_BPM__Schedule_Description__c != null
ORDER BY APXT_BPM__Next_Run_Date__c NULLS LAST

-- Record selection behind a routine
SELECT Name, APXTConga4__Description__c, APXTConga4__Query__c
FROM APXTConga4__Conga_Merge_Query__c WHERE Id = '<query id>'

-- Live output volume, last 30 days
SELECT COUNT(Id) FROM ContentVersion WHERE IsLatest = true AND FileExtension = 'pdf'
AND (Title LIKE 'BirdLife Australia Receipt%' OR Title LIKE 'BirdLife Membership Receipt%')
AND CreatedDate = LAST_N_DAYS:30

-- EOFY volume
SELECT COUNT(Id) FROM ContentVersion WHERE IsLatest = true AND Title LIKE 'EOFY 2026 Receipt%'
```

---

## 13. Commercial watch-list

Quote from Sarah, 9 Sep 2026, USD, 25 per cent NFP discount claimed:
- Option 1: USD 0.45 per document on 35,000 a year, unlimited users, batch, automation, Experience Cloud.
- Option 2: USD 275 per user per year for 12 seats, manual generation and templates only.
- 12-month initial term, extra 5 per cent for 3 years.

Measured volume 1 Sep 2025 to 31 Aug 2026: about 33,000 documents, roughly 80 per cent email with PDF and 20 per cent print PDF. Corroborated by 1,424 receipts in 30 days and 2,911 EOFY receipts. Option 1 is the only viable model because batch is the entire use case.

Still unanswered by the vendor, chase in writing:
1. Are failed merges billed?
2. Is there banding or step-down, and how is the June to July peak treated?
3. What is the overage rate?
4. Does the per-document option include S-Docs Jobs and the batch invocable, given the knowledge base restricts automation to Unlimited Edition?
5. Can batches run as an API-only integration user with the S-Docs permission set, and does that consume a seat?

---

## 14. Traps

1. **Batch size defaults to 5.** Size it deliberately or EOFY will crawl.
2. **Template IDs break on any org move.** Use template names in `doclist`.
3. **DOCX cannot produce PDF.** Ever.
4. **Live edit does not write back to Salesforce.** Only runtime prompts do.
5. **Refresh before live edit.** A data refresh discards live edits.
6. **Runtime prompts are button-only.** Use `prefillRTP` for one-click automation.
7. **Files-stored documents carry no S-Docs actions.** Email, edit, refresh and versions only work from the S-Docs LWC or related list.
8. **Direct SOQL removes record context.** Always re-add the WHERE clause.
9. **External images need a Remote Site Setting.**
10. **Subtraction in `<MATH>` needs spaces around the minus.**
11. **Parameters are case sensitive.**
12. **Generation needs Create and Read on SDoc Template**, not Read alone.
13. **Automation may be an Unlimited Edition add-on.** Confirm before signing.

---

## 15. e-Signature: two products

| | S-Docs e-Signature | S-Sign |
|---|---|---|
| Install | Base package | Separate package, direct link |
| Templates | Not required | Required, PDF or PDF-UPLOAD only |
| Config store | **Custom Metadata Types** | Remote site `https://api.sendgrid.com`, Salesforce Site, 6 Visualforce pages, licence keys |
| Licences | Permission sets (Signer, Requester) | Requesters licensed **twice**: S-Sign licence page **and** Installed Packages, Manage Licenses. Signers need none. |
| Source | PDF uploaded from the device | Generated from a template |

S-Sign Visualforce pages for the site: `SDOC.SDTemplateHTML`, `SSign.SSCreateSig`, `SSign.SSMultiSign`, `SSign.SSTemplatePDF`, `SSign.SSViewEnvlncl`, `SSign.SS`. Also tick Lightning Web Security in Session Settings and clear Lightning Features for Guest Users on the site.

Envelope lookup field naming for custom objects: object API name with `_c` appended, so `Expense__c` becomes a field named `Expense_c`.

Setting the same signing order number does **not** produce concurrent signing.

**BirdLife position: buy neither in phase one.** Receipting needs no signature. Revisit only for bequest forms or volunteer agreements, which are templated and repeatable, so S-Sign not e-Signature.

---

## 16. End-user behaviour to teach staff

- Live edit changes the **document only**, never a Salesforce field.
- Always Refresh Data **before** live editing; a refresh discards live edits.
- Versions are created on each save of an edited document; any version can be downloaded.
- Emails sent via S-Docs are logged in the record **Activity feed**.
- Documents linked into standard Files carry **no** S-Docs actions.
- The template picker searches both name and description, so populate both.

---

## 17. People impact, to state in every recommendation

- **Supporter care** move from a Conga button that loads a separate page to a component that keeps them on the supporter record. Genuine improvement to their day. Sell it that way. End-user course only, roughly two hours.
- **Finance and Peggy** notice nothing if the rebuild is correct and everything if a schedule is missed. Run both systems in parallel for at least one full weekly cycle and reconcile counts before switching off any Conga schedule.
- **Keith Tsui** carries the build and cannot start until the environment is fixed. Both admin courses, roughly a full day.
- **Marketing** own the Ortto bounce field and are on the critical path, whether or not they know it yet.