# BirdLife ICT Operations Dashboard

Reporting and data-flow monitoring for the **Ask Zeus** ICT helpdesk queue (Salesforce)
and the **IT Operations Project Plan** (Asana).

| | |
|---|---|
| Live dashboard | https://claude.ai/code/artifact/3aa92e1f-c8d7-4a91-95ad-c6dcd5db7606 |
| Refresh | Weekdays 08:00 AEST, automated |
| Salesforce org | `birdlifeaustralia.lightning.force.com` |
| Asana project | `1211042432693678` — IT Operations Project Plan |

---

## The problem this fixes

The ten Salesforce reports behind the two Zeus dashboards carry **no record-type
filter**. The `Case` object is shared across the whole organisation, so those reports
count all 19 record types — Powerful Owl, Swift Parrot Search, AOC, Conservation
Campaigns, General Enquiry, KBA, Birdata and the rest. Those are citizen-science and
enquiry queues owned by other teams.

Measured 6 August 2026:

| Measure | Unfiltered reports | Ask Zeus only | Inflation |
|---|---:|---:|---:|
| Open cases | 4,344 | 20 | 217× |
| Sitting in New | 3,787 | 8 | 473× |

Two conclusions in `BirdLife_Australia_ICT_Helpdesk_Dashboard_Technical_Documentation.docx`
(v1.0, 2 Jul 2026) are artefacts of this and should not be acted on:

- **"3,600 New cases reveals a significant acknowledgement bottleneck."** Eight of
  those New cases are Ask Zeus. There is no ICT acknowledgement bottleneck.
- **"MTTR by Agent — Angelica Fazio 6,300 closed, Alison Bolding 3,800 … a starting
  point for coaching or workload balancing."** Neither is on the ICT team. Ask Zeus
  owners are Andrew Dunn, Keith Tsui, Nina Lewis and Mathew Hema. Ask Zeus was 530 of
  the ~10,500 cases closed org-wide in the last 180 days.

`Ask Zeus` is a clean, already-existing discriminator. Applying it is the whole fix.

```
Name:          Ask Zeus
DeveloperName: Zeus          <-- note: NOT "Ask_Zeus"
Id:            012I80000004IPnIAM
SobjectType:   Case
```

---

## Salesforce admin tasks

These require the Salesforce UI — the API connector exposes record CRUD and SOQL,
not report or dashboard metadata, so they cannot be scripted from here.

### 1. Add the record-type filter to all ten reports — ~10 minutes

Highest-leverage change in this repo. Until it is done, both dashboards are
actively misleading.

For each report ID below: open
`https://birdlifeaustralia.lightning.force.com/lightning/r/Report/<ID>/view`
→ **Edit** → **Filters** tab → **Add Filter** → field `Record Type` → operator
`equals` → value `Ask Zeus` → **Apply** → **Save**.

| Report | ID |
|---|---|
| Helpdesk — Open Jobs by Status | `00ORF00000625cr2AA` |
| Helpdesk — Closed Jobs Last 2 Years by Month | `00ORF00000626In2AI` |
| Helpdesk — Cases by Agent (Top People) | `00ORF00000621Xj2AI` |
| Helpdesk — Cases by Type (Top Jobs) | `00ORF00000626lp2AA` |
| Helpdesk — SLA Time Spent by Agent | `00ORF00000627d32AA` |
| ICT — MTTR by Agent | `00ORF0000062ARF2A2` |
| ICT — Case Volume by Status | `00ORF0000062Aav2AE` |
| ICT — Top Categories by Technician | `00ORF0000062AxV2AU` |
| ICT — Backlog Trend by Month | `00ORF0000062BC12AM` |
| ICT — Case Origin Breakdown | `00ORF0000062BIT2A2` |

Sanity check when done: *Open Jobs by Status* should total **20**, not 4,344.

### 2. Require Type on close

65% of the open Ask Zeus queue (13 of 20) has no `Type`. Every category report is
computed over a field that is blank on two-thirds of live records, and triage has
nothing to sort on.

Fix it at the point of closure rather than backfilling 53,000 historical cases —
that is the moment the technician already knows the answer.

**Setup → Object Manager → Case → Validation Rules → New**

- Rule name: `Zeus_Type_Required_On_Close`
- Error condition formula:

```
AND(
  RecordType.DeveloperName = "Zeus",
  ISPICKVAL(Status, "Closed"),
  ISPICKVAL(Type, "")
)
```

- Error message: `Please set a Type before closing this case.`
- Error location: **Field** → `Type`

Scoped to `Zeus` so it never affects Powerful Owl, Birdata or any other team's cases.

### 3. Fix the MTTR report, and add real MTTR

The widget labelled *MTTR by Agent* is a **count of closed cases**, not a
resolution time. The technical doc concedes this in prose, but nobody reading the
dashboard sees the prose.

**3a.** Rename report `00ORF0000062ARF2A2` from `ICT — MTTR by Agent` to
`ICT — Closed Cases by Agent`. Update the widget title on dashboard
`01ZRF00000FcYsr2AF` to match.

**3b.** Add the field that makes real MTTR possible —
**Setup → Object Manager → Case → Fields & Relationships → New → Formula → Number**,
0 decimal places:

- Field label: `Days to Resolution`
- API name: `Days_to_Resolution__c`
- Formula:

```
IF(
  ISBLANK(ClosedDate),
  null,
  DATEVALUE(ClosedDate) - DATEVALUE(CreatedDate)
)
```

Then build `ICT — MTTR by Agent` properly: report type Cases, filter
`Record Type = Ask Zeus` **and** `Status = Closed`, group by `Case Owner`, and
summarise `Days to Resolution` by **Average**.

### 4. Also worth doing

Turn on **Field History Tracking** for `Status`
(Setup → Object Manager → Case → Fields & Relationships → Status → Set History
Tracking). This unlocks time-in-status, which is what a real SLA compliance
measure needs. There is already an Asana task for it — *Field History Tracking
setup*, assigned to Kate Rogerson, sitting in Backlog.

---

## The automated dashboard

Rather than a static HTML snapshot, the dashboard is regenerated from live data each
weekday morning and republished to a stable URL.

**Routine:** `ICT Dashboard — weekday refresh & data-flow check`
(`trig_0126KYAM3TAaZpBQKN8UeVdk`), cron `0 22 * * 0-4` UTC = weekdays 08:00 AEST.
Fresh session per run, read-only, push notification on completion.

### Why it replaced the old file

`birdlife_ict_dashboard.html` (Google Drive, 5 Aug 2026) was correctly scoped, but:

- It was a **static file claiming to be live** — "live from Salesforce and Asana" in
  the header, "Refreshed automatically" in the footer, hardcoded numbers, and no
  refresh mechanism of any kind.
- Its Asana panel covered **3 of 8 sections** (27 tasks). The project has 105
  incomplete tasks. 78 were invisible.

### Design principle: provenance is visible

Every panel on the dashboard states the filter it was computed under, and the footer
lists what is excluded. The defect in the original dashboards was never a wrong
number — it was an **unstated scope**. Making scope a visible design element is what
stops it recurring.

### Health checks run each morning

| Check | Threshold | At 6 Aug 2026 |
|---|---|---|
| Open cases with no Type | any | **13 of 20 (65%)** |
| New cases past first touch | 2 business days | **5 of 8**, oldest 21d |
| Open case ageing | 30 calendar days | **2** — 00133547 (69d), 00134670 (51d) |
| Asana Blocked, no movement | 14 days | **4**, all 21–22d |
| Asana overdue | past `due_on` | **4** (3 overdue since 2025) |
| Asana tasks in no section | any | **17** e-store subtasks |
| Asana unassigned | any | **5** |

### Known gap — connectors must be attached manually

The routine was created without connector grants: this organisation does not permit
attaching connectors through the API. **Until Salesforce Production and Asana are
attached to it, the routine will fire but will not be able to read any data.**

Fix: claude.ai → **Routines** → *ICT Dashboard — weekday refresh & data-flow check* →
add the **Salesforce Production** and **Asana** connectors. One-time.

---

## What the data says

Findings from the 6 August 2026 pull, beyond the scoping defect.

**Identity lifecycle is the automation target.** IAM (49) + Departing Staff (22) +
New User (16) = 87 of the last 425 cases — **20% of everything ICT handles**. Combined
with 96.5% email intake and no self-service channel, this is the clearest case for an
onboarding/offboarding playbook and a request form.

**Ask Zeus is single-channel.** 410 of 425 cases arrive by email, 15 internal. Zero
web, phone or portal. The Web (7,400) and Phone (6,900) volumes in the unfiltered
Case Origin report belong to other teams entirely.

**Nothing is reaching release.** *Ready for Deployment* and *Hypercare* are both
empty and have been throughout. Work moves from In Development straight to Done, or
to Blocked.

**Three Blocked items are decision debt, not technical work** — portal email
mismatch, Plauti bulk merge permissions, and duplicate management in Salesforce are
all explicitly "decision on responsibility". They need a call in a meeting, not
developer time.

**The join between systems is a spreadsheet column.** `ICT Priorities.xlsx` has
columns named *Asana Task* and *Zeus Case* — a human types the linkage in. At least
four divergent copies exist (Mathew's OneDrive, Justin Joseph's OneDrive, the ICT
Steering Group site, and a "- Copy" under Participation & Engagement). Worth
consolidating to one, or dropping in favour of the dashboard.

---

## Repository layout

```
README.md                     this file — findings and admin runbook
dashboard/ict-dashboard.html  dashboard source as published 6 Aug 2026
```

The HTML is kept for reference and as the design template the morning routine
rebuilds against. It is not itself the live artefact — the routine republishes to
the artifact URL each weekday.
