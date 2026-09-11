---
name: birdlife-conga
description: "Expert operator knowledge for Conga Composer 8 and Conga Batch in BirdLife Australia's Salesforce org (Zeus) - the 17 live scheduled batches behind every receipt and renewal reminder, the query and template inventory, the Composer parameter grammar, the live defects, and the S-Docs migration scope. Trigger on Conga, Composer, receipt, receipting, EOFY receipt, renewal reminder, merge template, CMQ-, CMT-, CET-, Conga Batch, S-Docs, document generation, or a supporter who did not get their receipt."
---

# BirdLife Australia — Conga Composer and Conga Batch

Conga is not a document tool at BirdLife. It is the **entire outbound supporter correspondence engine**: every donation receipt, every membership receipt, every EOFY tax receipt, and every membership renewal, expiry and cease reminder leaves the organisation through it. Seventeen scheduled batches fire between 02:30 PM and 09:15 PM AEST every day. If Conga stops, supporters stop being receipted and memberships silently lapse without warning. Nothing else in the estate covers this.

Read `birdlife-core` first for the precedence order and write tiers, and `birdlife-salesforce` for the org model. This skill is the layer beneath both for anything document-shaped.

**All figures verified live in production (birdlifeaustralia, AUS92) on 10 September 2026.** Re-verify anything older than 30 days using section 12.

---

## 1. Write tier — read this before touching anything

| Action | Tier | Rule |
|---|---|---|
| Reading Conga Solutions, Queries, Templates, Email Templates, Batch records | 1 | SOQL freely. Everything in this skill came from SOQL. |
| Editing a Conga **Query** SOQL body, a Conga **Email Template** body, a Batch schedule | 2 | These are *data* records, so the connector can technically write them. **Do not.** A wrong character in CMQ-0000 stops every donation receipt that night, silently. Prepare the exact new SOQL and hand it to Keith Tsui or Karishma Soni to paste and test in staging first. |
| Custom buttons, formula fields carrying Composer URLs, page layouts, the package itself | 3 | Metadata. Not reachable by this connector and not to be attempted. Produce the click path. |
| Re-generating a Conga Solution | **Never** | See defect D3. Regenerating the EOFY Batch solution overwrites the live button URL with a stale stored one. |

Conga failures are **silent and delayed**. A broken query returns zero rows, the batch reports a clean run, and nobody notices until a supporter complains weeks later. Treat every change as production-affecting even when it looks cosmetic.

---

## 2. Live inventory (10 Sep 2026)

| Object | API name | Count | Note |
|---|---|---|---|
| Conga Solution | `APXTConga4__Conga_Solution__c` | **10** | Only 3 are real; 5 are abandoned test solutions |
| Conga Template | `APXTConga4__Conga_Template__c` | **31** | CMT-00000 to CMT-00031, **CMT-00003 deleted** |
| Conga Query | `APXTConga4__Conga_Merge_Query__c` | **172** | ~30 in live use, the rest are 2022-23 membership sprint archaeology |
| Conga Email Template | `APXTConga4__Conga_Email_Template__c` | **35** | CET-00000 to CET-00037, **CET-00033/35/36 deleted** |
| Conga Batch (Conductor) | `APXT_BPM__Conductor__c` | **80** | **17 actively scheduled**, 1 stale, 62 dormant |
| Scheduled run history | `APXT_BPM__Scheduled_Conductor_History__c` | ~260-277/month | Confirms all 17 are firing |
| Document History | `APXTConga4__Document_History__c` | **0** | **Conga logs no document audit trail here. See defect D6.** |
| Composer Host Override | `APXTConga4__Composer_Host_Override__c` | 0 | Default Conga hosting |
| Solution Parameters | `APXTConga4__Conga_Solution_Parameter__c` | 0 | All parameters live in the formula-field URLs, not in Solution records |
| Solution↔Query junction | `APXTConga4__Conga_Solution_Query__c` | 0 | Same — the Solution records are near-empty shells |

**The single most important structural fact:** the Conga Solution records are almost empty. The real configuration lives in **Salesforce formula fields** on Opportunity, Contact and `AAkPay__Subscription__c` whose text value is the Composer URL. The Batch record names that field in `APXT_BPM__URL_Field_Name__c`, Conga evaluates it per record, and runs it. To read a solution you read the formula field's *value* on a real record (section 3), not the Solution record.

**Namespaces:** `APXTConga4` (Composer), `APXT_BPM` (Batch, internally "Conductor"), `APXT_CongaSign` (Conga Sign, installed, unused for receipting).

---

## 3. How to read a BirdLife Conga solution — the URL decode

This is the technique. Query the URL formula field on a live record:

```sql
SELECT Id, Donation_Receipt_Conga_Batch_EMAIL__c
FROM Opportunity
WHERE StageName='Closed Won' AND Amount>0 AND npsp__Primary_Contact__c!=null
ORDER BY CreatedDate DESC LIMIT 1
```

Live value, donation receipt by email (verified 10 Sep 2026):

```
&solmgr=1
&id=006RF00000fsazl
&queryid=[OppDonReceipt]0Q_010EAQ812325
&templateid=0T_000EAQ984028
&defaultpdf=1
&uf0=1
&mfts0=Receipt_Status__c&mftsvalue0=Receipted
&mfts1=Receipt_Date__c&mftsvalue1=TODAY
&sc0=1&sc1=SalesforceFile
&emailtoid=0035g00000L4S8f
&emailtemplateid=a2B5g000000CfhuEAC
&EmailFromID=0D25g000000oMle
&qmode=SendEmail
```

Parameter by parameter, as it behaves here:

| Parameter | BirdLife meaning |
|---|---|
| `solmgr=1` | Solution Manager marker. **Not documented in Conga's current parameter guide.** Do not attribute behaviour to it. |
| `id` | The master record. Resolves per record from the formula field. |
| `queryid=[OppDonReceipt]0Q_010...` | The **detail** query, aliased `OppDonReceipt`. That alias is the exact string the Word template uses in `{{TableStart:OppDonReceipt}}`. **`0Q_...` is a Conga Key, not a record Id** — Keys are org-portable external Ids, which is why these URLs survived the sandbox. |
| `templateid=0T_000EAQ984028` | Conga Key of **CMT-00000 Donation Receipt**. |
| `defaultpdf=1` | Sets PDF as the *default* output. It does **not** force PDF — only `FP0=1` does. Not used here, so a manual user can change format. |
| `uf0=1` | Enables Master Field to Set. Without it neither stamp below fires. |
| `mfts0/mftsvalue0` | On **successful merge only**, writes `Receipt_Status__c = 'Receipted'`. |
| `mfts1/mftsvalue1` | Writes `Receipt_Date__c = TODAY`. Literal `TODAY`, not `{!TEXT(TODAY())}` — **never mix the two styles in one solution.** |
| `sc0=1&sc1=SalesforceFile` | Saves the PDF as a Salesforce **File** (ContentVersion) on the master record. This is the only durable proof a receipt was produced. |
| `emailtoid` | Resolves to the Opportunity's `npsp__Primary_Contact__c`. Verified dynamic across three records — it is not hardcoded. |
| `emailtemplateid=a2B5g...` | **CET-00000**, a Conga Email Template (prefix `a2B`). |
| `EmailFromID=0D25g000000oMle` | Org-Wide Address **support@birdlife.org.au ("BirdLife Australia")**. Requires **View Setup and Configuration** on the running user. Mutually exclusive with `EmailReplyToId`. |
| `qmode=SendEmail` | Batch delivery mode. In Batch/Trigger `QMode` replaces `DS7` and is mandatory. |

The **print** variant is identical except it drops the three email parameters, adds `&APDF=1` (consolidate multiple PDFs into one file) and uses `qmode=Download`.

**The two-query pattern.** Every batch uses two different queries and confusing them is the most common diagnostic error here:
- The **master query**, on the Batch record's `APXT_BPM__Query_Id__c`, returns *which records to process*.
- The **detail query**, in the URL's `queryid`, supplies *the data the template merges*.

For donation receipts the master is **CMQ-0000** (`0Q_006EAQ023186`) and the detail is `0Q_010EAQ812325`. If receipts stop entirely, the master query is wrong. If receipts arrive with blank content, the detail query or FLS is wrong.

---

## 4. The 17 live scheduled batches

Times shown in AEST, as Salesforce stores UTC. Every one runs on the Conga refresh token described in section 9.

**Receipting (6)**

| Batch | Title | Master query | Schedule |
|---|---|---|---|
| 0008 | Donation Receipts - Email | CMQ-0000 | Daily 7:00 PM |
| 0014 | Donation Receipts - Print | CMQ-0012 | Thursday 8:00 PM |
| 0015 | Membership Receipts - Print | CMQ-0017 | Thursday 7:15 PM |
| 0016 | Membership Receipts - Email | CMQ-0018 | Daily 7:00 PM |
| 0039 | Photography Membership Receipts - Print | CMQ-0077 | Thursday 7:30 PM |
| 0040 | Photography Membership Receipts - Email | CMQ-0076 | Daily 2:30 PM |

**Renewal reminders, Sprint 7A — before expiry (7)**

| Batch | Title | Master query | Schedule |
|---|---|---|---|
| 0067 | NON-AR 10 day reminder - Email | CMQ-0143 | Daily 2:30 PM |
| 0068 | NON-AR 37 day reminder - Print (AU) | CMQ-0145 | Thursday 6:00 PM |
| 0069 | AUTO-RENEW CC 10 day - Email | CMQ-0144 | Weekdays 2:30 PM |
| 0070 | AUTO-RENEW 37 day - Print (AU) | CMQ-0146 | Thursday 6:15 PM |
| 0071 | AUTO-RENEW 60 day - Print (O/S) | CMQ-0147 | Thursday 6:30 PM |
| 0072 | NON-AR 60 day reminder - Print (O/S) | CMQ-0156 | Thursday 6:45 PM |
| 0073 | AUTO-RENEW DD 10 day - Email | CMQ-0159 | Weekdays 2:45 PM |

**Renewal reminders, Sprint 7B — after expiry (4)**

| Batch | Title | Master query | Schedule |
|---|---|---|---|
| 0074 | Expiry Notification - Email | CMQ-0164 | Daily 2:45 AM |
| 0075 | Cease Notification - Email | CMQ-0163 | Daily 3:00 PM |
| 0076 | Cease Notification - Print | CMQ-0162 | Thursday 9:00 PM |
| 0077 | Expiry Notification - Print | CMQ-0161 | Thursday 9:15 PM |

**Not scheduled but live-relevant:** Batch-0013 (Payment Transactions, Finance) is explicitly disabled. Batch-0080 "Donation Receipts - Email Test" carries a stale next-run of 22 Jun 2026 and should be deleted. Batches 0001-0011 and 0017 are the EOFY family, launched manually each July. The remaining ~60 are 2022-23 membership sprint batches that have never run since and are pure migration noise.

All 17 firing is confirmed by run history averaging ~263 records/month, which matches 6 daily + 2 weekday + 9 weekly exactly. **Run counts dropped to 88 in Nov 2025, 100 in Dec and 135 in Jan 2026 before returning to normal.** Receipting volume did not drop in that window, so this looks like batches being paused rather than an outage, but it is unexplained and worth one question to Keith.

---

## 5. The receipting data model

The whole engine turns on three Opportunity fields and one Contact field.

| Field | Role |
|---|---|
| `Receipt_Status__c` (Opportunity) | The state machine. `Email receipt` / `Physical receipt` = queued. `Receipted` = done. Also `EOFY receipt`, `Pending receipt`, `No receipt required`. |
| `Receipt_Date__c` (Opportunity) | Stamped `TODAY` by MFTS on success. |
| `Regenerate_donation_receipt__c` (Opportunity) | Manual re-issue flag. Every receipting query ORs on it, so ticking it puts the record back in tonight's run **regardless of every other filter**. This is the supported way to reissue a receipt. |
| `Receipt_Preference__c` (Contact) | `Email` / `Print` / `Annual`. `Annual` means the supporter is deliberately excluded from per-gift receipts and picked up by EOFY instead. |

**How to reissue a receipt for a supporter (the answer to the most common ticket):** set `Regenerate_donation_receipt__c = TRUE` on the Opportunity. Email goes out in the 7:00 PM run; print is picked up Thursday. Do not attempt to run Conga manually.

Live volume, receipted Opportunities by month (`Receipt_Date__c`):

| Month | Count | | Month | Count |
|---|---|---|---|---|
| Sep 2025 | 2,153 | | Mar 2026 | 1,934 |
| Oct 2025 | 1,377 | | Apr 2026 | 1,076 |
| Nov 2025 | 3,413 | | May 2026 | 1,176 |
| Dec 2025 | 1,757 | | **Jun 2026** | **4,995** |
| Jan 2026 | 2,048 | | Jul 2026 | 955 |
| Feb 2026 | 1,148 | | Aug 2026 | 1,522 |

**23,554 receipted Opportunities in the 12 months to Aug 2026**, with a June EOFY peak of 4,995. This is receipts only. Renewal reminders run off `AAkPay__Subscription__c` and never touch `Receipt_Date__c`, which is why the S-Docs sizing of ~33,000 documents is larger and is the correct number for licensing.

---

## 6. The queries that matter

**CMQ-0000 — Donation receipts, email (Batch-0008, nightly).** The busiest query in the org.

```sql
SELECT Id, name, CreatedDate, RecordType.Name, StageName, Receipt_Status__c,
       Regenerate_donation_receipt__c
FROM Opportunity
WHERE (StageName='Closed Won' AND Amount > 0
  AND npsp__Primary_Contact__r.Email != null
  AND RecordType.Name IN ('Donation','Major Gift')
  AND IsRD__c = FALSE)
AND ((Receipt_Status__c = 'Email receipt'
      AND npsp__Primary_Contact__r.Receipt_Preference__c NOT IN ('Print','Annual')
      AND npsp__Primary_Contact__r.pi__pardot_hard_bounced__c != True)
     OR Regenerate_donation_receipt__c = TRUE)
```

Note `IsRD__c = FALSE` — recurring donation instalments are deliberately excluded from per-gift receipting and go to EOFY.

**CMQ-0012** is the print twin, keyed on `MailingStreet != null` and `Receipt_Status__c = 'Physical receipt'`.

**CMQ-0018 / CMQ-0017 — Membership receipts, email / print.** Same shape but `RecordType.Name IN ('Membership')` **plus a hardcoded membership-type whitelist**:

```
Membership_Option__c LIKE '%Wader%' OR '%Seabird%' OR '%Raptor%'
OR '%Full Member%' OR '%Concession%'
```

**Any membership type not on that list is never receipted by these batches.** Print variants carry `LIMIT 500`.

**CMQ-0076 / CMQ-0077 — Photography memberships.** Separate batches because Photography is not on the whitelist above. The **email** version additionally hardcodes `CreatedDate >= 2026-01-01T00:00:00Z`, so Photography memberships created before 2026 are permanently unreachable.

**CMQ-0143 to CMQ-0164 — the reminder engine.** All eleven run against `AAkPay__Subscription__c` (Payments2Us), sharing this shape:

```sql
SELECT Id FROM AAkPay__Subscription__c
WHERE AAkPay__Membership_Status__c != 'Cancelled'
  AND AAkPay__Membership_Status__c != 'Expired'
  AND (NOT AAkPay__Payment_Option_Name__c LIKE '%Lifetime%')
  AND (NOT AAkPay__Payment_Option_Name__c LIKE '%Complimentary%')
  AND (NOT AAkPay__Payment_Option_Name__c LIKE '%Legacy%')
  AND AAkPay__End_Date__c = Next_N_Days:10
  AND AAkPay__Automatic_Renewal__c = FALSE
  AND OK_to_Email_Reminder__c = TRUE
  AND Former_Gift_Membership__c = FALSE
  AND Renewal_Notification__c = FALSE
```

The suppression flags `Renewal_Notification__c`, `Expiry_Notification__c` and `Cease_Notification__c` are the idempotency guard: the Word template's **Master Field to Set** stamps them TRUE on success so a member is not reminded twice. That is why templates CMT-00027 to CMT-00030 carry `Master_Field_to_Set_1__c` values. Break that stamp and members get reminded every single day.

Windows in use: 10 days (email), 37 days (print AU), 60 days (print overseas), Cease at 30/37 days, Expiry at 60/67 days.

---

## 7. Templates and email templates

**Document templates in live use — only 5 of 31:**

| Template | Purpose | Conga Key |
|---|---|---|
| CMT-00000 | Donation Receipt | `0T_000EAQ984028` |
| CMT-00001 | EOFY Receipt | `0T_001EAQ630133` |
| CMT-00002 | Batch EOFY Receipt | `0T_003EAQ799020` |
| CMT-00005 | Membership Receipt | `0T_005EAG121769` |
| CMT-00027 to CMT-00030 | Membership reminder letters (renewal, expiry, cease) | various |

CMT-00006 to CMT-00026 are the 2022-23 membership sprint letters. Dead weight; do not migrate them.

**CMT-00028 carries an authoring warning worth preserving verbatim:** "The blank space that appears in the middle of the template on preview and a small 'd' by itself when downloaded has hidden code for IF STMTs. After downloading, select 'd', right click and select Toggle fields to see the content of the IF STMTs." Anyone editing that template without knowing this will delete the conditional logic.

**Email templates in live use:**

| Template | Subject | Note |
|---|---|---|
| **CET-00000** | "Thank You! BirdLife Australia Donation Receipt Enclosed" | **This is the live donation receipt cover email and it is the H5N1 Bird Flu variant**, swapped in 21 Jun 2026 for the bird flu emergency appeal. The standard text is parked in **CET-00037**. Nobody has decided when to revert. Raise this. |
| CET-00001 | EOFY Receipt cover email | Wildbird Protectors |
| CET-00002 | "BirdLife Membership Receipt" | |
| CET-00012 | Photography Membership Receipt | |
| CET-00027 to CET-00032 | Sprint 7A/7B reminder emails | Last edited 1-2 Sep 2026 |

**Conga email merge syntax as used here**, from CET-00027's live subject line:

```
Action required: {{AAKPAY__SUBSCRIPTION_FIRSTNAME}}, your
{{AAKPAY__SUBSCRIPTION_PAYMENT_FORM}} will lapse on
{{AAKPAY__SUBSCRIPTION_END_DATE \@ "d MMMM yyyy"}}. Renew online TODAY!
```

Double curly braces, dataset-prefixed field names, Word-style `\@ "format"` date pictures. Two constraints that bite: **detail data cannot go in a subject line**, and **IF statements do not work in email templates at all** — every conditional must be a separate template or a Salesforce formula field.

**How Conga sends.** Composer assembles the HTML but Salesforce transmits it. Batch uses `sendEmail(MassEmailMessage)`, so these count against **Salesforce mass email limits**, not the 5,000/day single-email cap. A June EOFY run of ~5,000 documents sits close enough to org limits to be worth checking before the next one.

---

## 8. EOFY receipting — the manual cursor, and why it breaks every year

EOFY is Contact-based, not Opportunity-based, and it is the most fragile thing Conga does here.

The driving field is `Contact.EOFY_Batch_Downloaded_Year__c`, a **manual batch cursor**. Live distribution:

```
2022  677     26a  498     26b  500     26c  500
26d   500     26e  500     26f  252     26hb   1
25a-25f  ~240 combined     test   1
```

The pattern is deliberate: staff label contacts in slices of 500 (`26a`, `26b`, … `26f`), then edit the master query to point at the next slice and re-launch. **This exists because Conga Batch caps distributed output at 1,000 records per run.** The FY26 run completed at `26f` with a 252-record tail.

**The live master query CMQ-0008 (Batch-0003, EOFY email) currently reads:**

```sql
SELECT Id, Name FROM Contact c
WHERE npsp__Deceased__c = False AND IsEmailBounced = False
  AND pi__pardot_hard_bounced__c = FALSE AND Email != ''
  AND Receipt_Preference__c != 'Print'
  AND Total_Wildbird_Gifts_Last_Financial_Year__c > 0
  AND DoNotEmailReason__c != 'BL Dummy Email'
  AND EOFY_Batch_Downloaded_Year__c = '26hb'
LIMIT 5000
```

**`'26hb'` matches exactly 1 contact.** It is a test value left in place after the 8 Jul 2026 edit. This is the same class of defect as the historic hardcoded `'25f'`: the query is a manual cursor with no guard, and it always ends the year pointing somewhere useless. **Before the July 2027 run, this value must be reset to the first FY27 slice.** Put it in Asana with a June 2027 due date, not in a document.

Note also the `LIMIT 5000` exceeds Conga's own 1,000-record distributed cap — the limit is theatre, the 500-record slicing is what actually controls the run.

---

## 9. Cross-system dependencies — what kills Conga from outside

**D-A. Pardot. The highest-consequence dependency in this skill.**
Seven Conga queries filter on `pi__pardot_hard_bounced__c`, including **CMQ-0000 (nightly donation receipts), CMQ-0018 (nightly membership receipts), CMQ-0076 (Photography), CMQ-0001 and CMQ-0008 (both EOFY masters), CMQ-0144 and CMQ-0162 (reminders)**. That field belongs to the `pi__` managed package, which is being decommissioned.

**9,484 Contacts currently carry `pi__pardot_hard_bounced__c = true`** and are suppressed by it.

Two failure modes, both bad:
- Uninstall `pi__` and the field vanishes. All seven queries throw and **receipting stops that night, silently**.
- Strip the filter without a replacement and 9,484 previously suppressed contacts start receiving email at hard-bounced addresses, damaging domain reputation for the whole tenant.

The fix is neither: create a non-namespaced `Email_Hard_Bounced__c` on Contact, backfill it from `pi__pardot_hard_bounced__c` **before** uninstall, repoint all seven queries, prove them, then uninstall. This must be sequenced into the Pardot decommission plan and it currently is not. **Cross-reference `birdlife-pardot-decommission`.**

**D-B. Payments2Us.**
Eleven of the seventeen live batches — the whole renewal reminder engine — run against `AAkPay__Subscription__c`. Payments2Us is being decommissioned as part of the membership rebuild. The reminders do not survive that migration on their own; the new `Membership__c` model must carry `End_Date`, `Cease_Date`, `Automatic_Renewal`, `Payment_Option_Name`, `OK_to_Email_Reminder`, `OK_to_Print_Reminder`, `Former_Gift_Membership` and the three notification suppression flags, or members stop being told their membership is ending. **Cross-reference `birdlife-membership-rebuild`.**

**D-C. The scheduled-batch refresh token — a single point of failure with a person's name on it.**
Conga Batch schedules run under a Salesforce refresh token created by whoever last clicked **Create Salesforce Token** on the Conga Batch Setup tab. Conga's own documentation: *"If that user revokes their Salesforce Refresh Token, all scheduled batches stop operating."* Deactivating that user during offboarding stops all 17 batches instantly and silently.

**Action:** identify the token holder, and if it is a named staff member, re-issue the token from a dedicated integration user. Add "check Conga Batch token holder" to the offboarding checklist. **Cross-reference `birdlife-people-lifecycle`.**

**D-D. Org session security.**
Conga requires **"Lock sessions to the IP address from which they originated" to be OFF**, permanently. This is a documented vendor requirement, not a misconfiguration, and it partly explains the org's zero trusted IP ranges. Record it as an accepted risk with a named acceptor rather than letting a future audit find it unexplained. Leaving Conga removes the constraint.

---

## 10. Live defects, verified 10 September 2026

| # | Defect | Evidence | Impact |
|---|---|---|---|
| **D1** | **EOFY master query points at a dead cursor.** CMQ-0008 filters `EOFY_Batch_Downloaded_Year__c = '26hb'`, which matches 1 contact. | Live query + Contact group-by | Next EOFY email run produces 1 document unless reset. Not urgent until June 2027, but it will be forgotten. |
| **D2** | **Individual EOFY Receipt button is broken.** The "EOFY Receipt" Solution (weblink `00b0p000001BG5b`) is joined to **CMT-00031 "EOFY Template Test"**, a test template. | `APXTConga4__Conga_Solution_Template__c` junction, live | Supporter Care cannot produce a one-off EOFY receipt on request. Every such request escalates to ICT. Longest-standing user-facing defect here. |
| **D3** | **Never click "Regenerate Solution" on EOFY Batch Receipts.** The Solution's stored URL differs from the live button URL. | Carried from the Jul 2026 audit, structurally unchanged | Regenerating overwrites the working button and breaks the July run. |
| **D4** | **Membership receipt whitelist excludes real membership types.** CMQ-0017/0018 only match Wader, Seabird, Raptor, Full Member, Concession. | Live query text | Family, Student and other types are never receipted by the membership batches. **112 Photography Opportunities sit unreceipted**, and CMQ-0076's `CreatedDate >= 2026-01-01` makes the pre-2026 ones permanently unreachable. |
| **D5** | **364 Closed Won Opportunities with Amount > 0 are stuck in a queued receipt status**, oldest from Apr 2022. Only 20 satisfy tonight's donation query. | Live aggregate | Real supporters who gave and were never receipted. A tax and trust problem, not a technical one. Needs triage by Nina Lewis with Supporter Care. |
| **D6** | **No document audit trail.** `APXTConga4__Document_History__c` holds **0 records** in production. | Live count | You cannot prove from Salesforce which receipts Conga generated. The only evidence is `Receipt_Date__c` plus the saved Salesforce File. Design the S-Docs replacement to log properly. |
| **D7** | **Live donation receipt email is still the H5N1 Bird Flu variant** (CET-00000, swapped 21 Jun 2026). Standard text parked in CET-00037. | Live template descriptions | Every donor receipt for nearly three months has carried emergency appeal framing. Fundraising should decide, not ICT by default. |
| **D8** | **Stale test batch.** Batch-0080 "Donation Receipts - Email Test" carries a next-run date of 22 Jun 2026 against the production donation formula field. | Live batch record | Low risk today, but a test batch pointed at production receipting should not exist. Delete it. |
| **D9** | **62 dormant batches and ~140 unused queries.** | Live counts | Pure migration cost and audit noise. Archive before the S-Docs build, not during. |

D1, D2, D5 and D7 are the four that reach a human being. Lead with those.

---

## 11. Conga Composer mechanics — the vendor layer

Verified against `documentation.conga.com` on 10 September 2026.

**Product status.** Composer for Salesforce is **current and actively developed**; latest release **8.298, 13 June 2026**, adding PKCE and refresh token rotation for Salesforce Summer '26. **There is no announced end of life for Composer 8 or Conga Batch.** Composer 7, Mail Merge and Quick Merge died in Aug 2022; the **Solution Migration Tool was retired 22 May 2026** and replaced by Conga Keys. Conga Batch is **included with Composer, not separately licensed**. Conga publishes no list price; a ~2024 third-party figure of US$6/user/month exists but is unverified, and **there is no evidence of per-document pricing** — which is worth remembering when comparing to the S-Docs per-document quote.

**Formatting rules that cause most malformed-URL failures.** No spaces (use `+`), no quote marks, **URL max 1,750 characters**, parameters order-independent and case-insensitive in name but not in value. A raw `&` in field data breaks the merge: `Ben&Jerry's` fails, `Ben & Jerry's` passes. Wrap field references in `URLENCODE()`.

**Parameters you will actually meet here.**

*Data:* `id` (master), `QueryId` (`[Alias]` prefix names the dataset; alias must be 2-20 alphanumeric characters, unique, and not `Master`, `Org` or `ReportData`), `ReportId`, `pv0`-`pv5` filter values (master record Id is auto-passed into `pv0`).

*Template:* `TemplateId` (record Ids or Conga Keys, comma-separated, merged in listed order). **Never put dashes, slashes or underscores in a template alias** — it produces `Template Id/s do not exist`. Use `OFN` for filenames (2-80 chars, no `: # " \ / > <`).

*Output:* `DefaultPDF` sets the default only; **`FP0=1` is what actually forces PDF**. `APDF` consolidates multiple PDFs. PDF security is `PS0`-`PS4`, `PSPW` — leave `PS4` (screen reader access) permissive or you make receipts inaccessible.

*Save-back:* `SC0=1` plus `SC1=SalesforceFile|Attachments|Chatter|Content|Documents`. `SC1=Content` defaults to the **Private Library** and `Documents` to **My Personal Documents** — both silently hide the output.

*Field updates:* `UF0=1` enables, then up to three `MFTS0/1/2` + `MFTSValue0/1/2` pairs, written **only on successful merge**. `MFTSId0/1/2` targets a record other than the master. Checkbox values must be `TRUE`; date `TODAY` or `{!TEXT(TODAY())}` but **never both styles in one solution**. Does not work with Global Merge solutions.

*Email:* `EmailToId`, `EmailAdditionalTo`, `EmailCC`, `EmailBCC`, `EmailSubject` (overrides the template subject), `EmailTemplateId` (Salesforce or Conga), `CongaEmailTemplateId`/`CETId` (Conga only), `EmailFromID` (Org-Wide Address, `0D2` prefix, needs View Setup and Configuration, mutually exclusive with `EmailReplyToId`). **`OrgWideEmailFrom` is not a real parameter.** `EmailBody` is undocumented legacy — do not use it.

*Batch delivery:* `QMode` replaces `DS7` and is mandatory. Values include `SendEmail`, `Download` (Batch only), `Attachments`, `SalesforceFile`, `Chatter`, `Content`, `GenerateLink`.

**Limits.** Conga's own pages contradict each other on row limits (2,500 vs 25,000 rows per query; 5 MB vs 10 MB data cap; 50 vs 100 queries per solution) and never state which applies to which edition. **Design to the conservative numbers.** Firm limits that do hold: **consolidated batch output 200 records per run, distributed output 1,000 records per run**, aggregate queries 1,000 rows, `GROUP BY` 200 rows, 3 query variables of 50 rows each, 20 templates per operation (Business) or 40 (Enterprise). There is **no auto-chunking** — the 500-record EOFY slicing exists precisely because of this.

**Word template syntax.** Two conventions both work: text-based `{{FIELD_NAME}}` and traditional Word `«FIELD_NAME»`. Detail regions are `{{TableStart:Alias}}` … `{{TableEnd:Alias}}` where **Alias must exactly match the URL's `[Alias]`** — mismatched pairs produce `Something's wrong with your template (bad mojo)`. Nesting is supported. IF statements must be **real Word merge fields** (Ctrl+F9), take the form `{IF "expr1" op "expr2" "true" "false"}` with spaces around the operator and everything quoted, need the `\* MERGEFORMAT` switch deleted, use `"True"` not `"TRUE"` for checkboxes, and **cannot hide table rows** (use `TableHide` or filter the query instead).

**Top errors and what they mean here.**

| Error | Most likely cause at BirdLife |
|---|---|
| `INVALID SESSION ID or SERVER URL` | Org 24-hour API limit hit (check Setup → Company Information → API Requests Last 24 Hours), or IP session locking was re-enabled, or the running profile lost API Enabled |
| `Template Id/s do not exist` | Special character in a template alias |
| `Template Id is Invalid` | Stale Id after a sandbox refresh — the reason Conga Keys are used here |
| `REQUEST LIMIT EXCEEDED` | Too many batches overlapping. Keep 15 minutes between schedules |
| `SINGLE_EMAIL_LIMIT_EXCEEDED` | EOFY run against the 5,000/day cap |
| `REQUIRED FIELD MISSING Missing body` | Bad `CETId` or an empty email template body |
| `Something's wrong with your template (bad mojo)` | Mismatched TableStart/TableEnd alias |
| Scheduled batch simply not firing | **The refresh token. Check this first.** See D-C |
| Output contains blank fields | FLS on the running user, or a wrong dataset alias |

Errors surface only on the **Conga Batch Dashboard** tab, never in Apex debug logs. Failure is per-record, not all-or-nothing, and **there is no automatic retry and no supported re-run-failures-only mechanism**. The MFTS stamp is what makes re-running safe.

---

## 12. Verification queries

Never quote a figure from this skill without refreshing it.

```sql
-- Live scheduled batches and their next run
SELECT Name, APXT_BPM__Title__c, APXT_BPM__Query_Id__c,
       APXT_BPM__URL_Field_Name__c, APXT_BPM__Next_Run_Date__c,
       APXT_BPM__Schedule_Description__c
FROM APXT_BPM__Conductor__c
WHERE APXT_BPM__Next_Run_Date__c != null ORDER BY Name

-- Did the batches actually run last night?
SELECT APXT_BPM__Conga_Conductor__r.Name, Name, CreatedDate
FROM APXT_BPM__Scheduled_Conductor_History__c
WHERE CreatedDate = LAST_N_DAYS:2 ORDER BY CreatedDate DESC

-- Receipting backlog: who gave and was never receipted
SELECT Receipt_Status__c, COUNT(Id), MIN(CreatedDate), MAX(CreatedDate)
FROM Opportunity
WHERE Receipt_Status__c IN ('Physical receipt','Email receipt','Pending receipt')
  AND StageName='Closed Won' AND Amount>0
GROUP BY Receipt_Status__c

-- Monthly receipting volume (the S-Docs sizing number)
SELECT CALENDAR_YEAR(Receipt_Date__c), CALENDAR_MONTH(Receipt_Date__c), COUNT(Id)
FROM Opportunity WHERE Receipt_Date__c = LAST_N_MONTHS:12
GROUP BY CALENDAR_YEAR(Receipt_Date__c), CALENDAR_MONTH(Receipt_Date__c)

-- Pardot blast radius before uninstall
SELECT COUNT(Id) FROM Contact WHERE pi__pardot_hard_bounced__c = true

-- EOFY cursor state
SELECT EOFY_Batch_Downloaded_Year__c, COUNT(Id) FROM Contact
WHERE EOFY_Batch_Downloaded_Year__c != null
GROUP BY EOFY_Batch_Downloaded_Year__c ORDER BY COUNT(Id) DESC

-- Read any solution's real configuration (substitute the formula field)
SELECT Id, Donation_Receipt_Conga_Batch_EMAIL__c FROM Opportunity
WHERE StageName='Closed Won' AND Amount>0 AND npsp__Primary_Contact__c!=null
ORDER BY CreatedDate DESC LIMIT 1

-- Which queries break when Pardot is uninstalled
SELECT Name, APXTConga4__Name__c, APXTConga4__Query__c
FROM APXTConga4__Conga_Merge_Query__c ORDER BY Name
-- then filter locally for 'pi__'
```

---

## 13. The S-Docs migration inventory

Everything above doubles as the migration scope. Conga's configuration is **data, not metadata**, so no normal deployment moves any of it and Conga's own sandbox-to-production guidance is entirely manual re-creation. Conga provides no export tool; the Solution Migration Tool was retired in May 2026.

**What must be rebuilt, in order of difficulty:**

| Component | Live count | In scope | Extractable? |
|---|---|---|---|
| Conga Queries | 172 | **~30** | Yes, trivially — SOQL is plain text on the record |
| Conga Email Templates | 35 | **~10** | Yes — HTML in a rich text field |
| Word document templates | 31 | **5** | Files only. Layout is portable Office; every merge field, TableStart/TableEnd, IF field and Master Field to Set is Conga-specific syntax S-Docs will not read. **This is the real work.** |
| Composer URLs / formula fields | ~20 formula fields | all live ones | Yes, via Metadata API `WebLink` / formula field retrieve. Fastest way to inventory every parameter |
| Conga Batch schedules | 80 | **17** | Records exportable; the schedule itself must be rebuilt |
| Solution records | 10 | 3 | Near-empty, low value |

**Sequencing that avoids an outage:**
1. Fix the Pardot dependency (D-A) **first**. It is due now regardless of S-Docs, and migrating a query that references a field about to vanish wastes the work twice.
2. Move the token off any named person (D-C) before anyone else is offboarded.
3. Migrate **donation receipts only** as the thin slice: one query, one template, one email template, one nightly batch. Run S-Docs and Conga in parallel with S-Docs writing to a different field until the counts match for two weeks.
4. Then membership receipts, then EOFY (which needs the 500-record cursor replaced with real pagination, not reproduced), then the reminder engine — and **the reminder engine should wait for the membership rebuild**, because rebuilding it on `AAkPay__Subscription__c` means rebuilding it twice.
5. Archive the 62 dormant batches and ~140 unused queries **before** the build so nobody migrates dead weight.
6. Uninstall Conga last, and note that doing so lifts the IP-session-locking constraint (D-D), which is a security win worth claiming in the board paper.

**One correction to carry into vendor conversations:** Conga is not end-of-life and Composer 8 is actively released. The case for S-Docs rests on cost, the defect list above and the native Salesforce rendering, not on Conga dying. Arguing EOL will not survive contact with anyone who checks.

---

## 14. People

| Person | Their stake in Conga |
|---|---|
| **Keith Tsui** | Modified most live batches and queries; last edited the EOFY master query 8 Jul 2026. First call for any query change. Owns the fix for D1. |
| **Karishma Soni** | External Salesforce developer; the right hands for the S-Docs template rebuild. |
| **Nina Lewis** | Finance link. Owns triage of D5, the 364 unreceipted gifts, with Supporter Care. |
| **Andrew Dunn** | Level 1. Can run the verification queries in section 12 and check the Conga Batch Dashboard each morning without needing Mathew. Give him the nightly check. |
| **Fiona Mainey** | Built most 2022-23 membership sprint batches. Historical context only. |
| **Bird Bot** | Owner of record on most batches. An automation identity, not a person. |
| **Fundraising** | Owns the CET-00000 bird flu wording decision (D7), not ICT. |

---

## 15. Operating rules

1. **Read the formula field, not the Solution record.** The Solution records are empty shells. The configuration is in the URL.
2. **Distinguish master query from detail query** before diagnosing. No documents means the master query; blank documents means the detail query or FLS.
3. **Never edit a live Conga Query through the connector.** Prepare the SOQL, hand it over, prove it in staging.
4. **Reissue a receipt by setting `Regenerate_donation_receipt__c = TRUE`**, never by running Conga manually.
5. **Check the refresh token first** when a scheduled batch has not fired. It is the most likely cause and the least obvious.
6. **Assume every figure here is a baseline.** Re-run section 12 before quoting anything to Finance, the Board or a vendor.
7. **State the tier out loud** on any Conga change, and say plainly that Conga failures are silent so the DONE test must be a query, never an assumption.