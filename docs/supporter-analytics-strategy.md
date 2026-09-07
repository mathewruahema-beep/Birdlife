# Supporter and Volunteer Analytics: where we are, what to fix, where to go

**Prepared for:** Mathew Hema, Senior Manager ICT
**Data read:** 7 September 2026, live from Salesforce Production, Ortto and Asana. Repo skills supplied the dated facts for Stripe, NetSuite, WordPress and Zapier.
**Status:** Assessment with decisions taken 7 Sep 2026 (section 9). Nothing in this paper has been changed in any system.

---

## Short answer

BirdLife holds more supporter data than almost any organisation its size: 482k contacts, 208k program participants, 690k Birdata survey records, 1.7M campaign memberships, 15.9M Ortto activities. What it does not hold is a single, agreed picture of one supporter across giving, membership, participation, volunteering and communications. Every team answers "who are our supporters" from its own system, and the answers disagree.

Three facts decide the next six months:

1. **Half the base is unreachable.** 31% of contacts have opted out of email and 53% are flagged inactive for Ortto. "Supporter at the heart" is, today, a statement about the half we can still talk to.
2. **Volunteering has no data home.** Volunteers for Salesforce holds zero jobs and zero hours, the Volunteer campaign type has zero members, and one contact in 482k carries a Better Impact ID. The Better Impact plan has 21 tasks, none assigned, none complete, and Phase 1 (August) is already overdue.
3. **The donor number depends on who you ask.** The custom "Last Gift Date (All Sources)" field, which Ortto uses for segmentation, says 9,642 people gave in the last year. Won Opportunities say 18,959. One of those numbers is wrong and every donor journey built on it inherits the error.

The recommendation is a three-stage process: **fix the definitions and identity plumbing first (no new tools, 90 days), then build the reporting layer on top of clean joins (Power BI, 90 to 180 days), then run a quarterly insight loop that feeds decisions in Fundraising, Participation and Supporter Care.** Buying an analytics tool before the first stage would produce prettier versions of the same disagreeing numbers.

---

## 1. The supporter in numbers today

All figures live at 7 Sep 2026 unless dated otherwise. Ask Zeus is excluded from supporter-facing Case counts.

### Who is in the base

| Measure | Figure | Read |
|---|---:|---|
| Contacts | 481,974 | The whole base, including duplicates |
| Household accounts | 475,416 | Almost one per contact: the NPSP household model is not grouping households |
| Contacts created in last 12 months | 49,833 | Growth of about 10% a year |
| New contacts with a Lead Source | 24 of 49,833 | We do not record where new supporters come from |
| Contacts with an email address | 461,857 (96%) | |
| Contacts opted out of email | 151,060 (31%) | |
| Contacts flagged Ortto Inactive | 253,719 (53%) | Excluded from the marketing sync |
| Contacts with no postcode | 142,412 (30%) | Branch and regional analysis is blind for a third of the base |
| Contacts with no email, phone, mobile or street | 4,825 | Unreachable by any channel |
| Contacts Plauti has flagged as duplicates | 200,441 | Nearly 42% of the base sits in a duplicate group |
| Contacts with any activity logged in 12 months | 25,880 (5%) | Tasks and events are not how staff record contact |

### Giving (won Opportunities, last 365 days)

| Record type | Count | Amount | Note |
|---|---:|---:|---|
| Donation | 40,841 | $6,302,043 | Prior year 34,036 / $5,663,590. Volume up 20%, income up 11%, average gift down from $166 to $154 |
| Bequest | 39 | $3,809,358 | 35% of income from 39 estates. Concentration risk, not a pipeline |
| Membership | 8,791 | $569,700 | Average $65 |
| Major Gift | 4 | $139,990 | Four records. Major giving is not being recorded under its own type |
| Distinct donors (primary contact) | 18,959 | | Prior year 15,061, up 26% |
| Contacts with Last Gift Date in 12 months | 9,642 | | Disagrees with the line above by a factor of two |
| Donation Opportunities with no Campaign | 0 | | Appeal attribution is complete. This is a genuine strength |

### Regular giving (Payments2Us Recurring Payments; NPSP Recurring Donations now hold 5 open records)

| Status | Count | Monthly value | Annualised |
|---|---:|---:|---:|
| Active | 5,327 | $44,982 | $539,780 |
| Expired | 7,043 | $45,254 nominal | Historic value no longer collected |
| Suspended, max retries exceeded | 565 | $4,277 | **$51,319 a year recoverable with a card-update campaign** |
| Cancelled and Cancelled AR | 941 | $5,285 | Cancellation reasons are a picklist; nobody reports on them |

The repo skill records 1,778 active NPSP Recurring Donations in June. Today there are 5 open. Either they were migrated to Payments2Us or closed in bulk. Nobody wrote down which, and that is itself a finding.

### Membership

| Measure | Figure |
|---|---:|
| Contacts with Active BirdLife Member flag | 7,640 |
| Active membership Recurring Payments (BirdLife Membership form) | 4,386 |
| Expired membership Recurring Payments | 3,215 |
| Members opted out of email | 631 (8%) |
| Members flagged Ortto Inactive | 839 (11%) |

Two membership truths already exist (the Contact flag and the Recurring Payment status), and the WooCommerce rebuild adds a third. The `Active_BL_Member__c` flag is maintained by Payments2Us, which is being decommissioned, and Emu journal access depends on it.

### Participation and citizen science

| Measure | Figure |
|---|---:|
| Program Engagements (Program Management Module) | 338,417 |
| Distinct people with a Program Engagement | 208,281 (43% of all contacts) |
| Aussie Bird Count engagements | 243,044 |
| Birdata survey submissions (all time) | 689,894 by 17,077 people |
| Birdata submissions, last 12 months | 77,225 by 4,090 people (19 surveys each) |
| Campaign Members, last 12 months | 184k Invited, 128k Participated, 92k Connected, 38k Responded, 27k Registered |
| Website Event registrations | 181,851 |
| LearnUpon course enrolments | 5,677 |
| Donors (Last Gift field) who also have a Program Engagement | 6,543 of 9,642 (68%) |
| Program participants who gave in the last year | 6,543 of 208,281 (3%) |

That last pair is the most valuable insight in this paper. Two-thirds of donors came through participation, yet only 3% of participants have given. The participation base is the fundraising pipeline and it is barely worked as one.

### Volunteering

| Measure | Figure |
|---|---:|
| Volunteers for Salesforce jobs / hours | 0 / 0 |
| Volunteer Campaign record type: campaigns / members | 2 / 0 |
| Contacts with a Better Impact ID | 1 |
| Ortto "Powerful Owl Volunteers" audience | 168 (created 7 Sep 2026) |
| Ortto "Migratory Shorebirds" volunteer audience | 14,546 subscribers; last update 44.6% open, 0.6% click |
| Better Impact implementation plan | 21 tasks, 0 assigned, 0 complete, Phase 1 overdue |

There is no data definition of a volunteer at BirdLife. The word covers Birdata surveyors, shorebird counters, branch committee members, event helpers and Powerful Owl monitors, and each lives in a different object, audience or spreadsheet.

### Communications (Ortto)

| Audience | Subscribers |
|---|---:|
| All subscribers | 233,087 |
| Engaged subscribers | 78,126 (34%) |
| Aussie Bird Count | 155,342 |
| News and updates (Bulletin) | 147,653 |
| Conservation Campaigns | 142,630 |
| Donations and Community Fundraising | 135,187 |
| Backyard Birds | 130,730 |
| Citizen Science and Birdata | 33,905 of 140,128 members |

Thirteen journeys are live: member, regular giver and new supporter welcomes, Aussie Bird Count registration, Birdata course, LMS follow-ups, bounce hygiene. Revenue attribution to won Opportunities works: the August major gift invitation (355 delivered) attributed 19 gifts and $221,719. This is the best-instrumented part of the estate and it runs on a 2.04M-record, 15.9M-activity Salesforce feed that has already hit its retention limit.

### Service (Cases, last 365 days, excluding Ask Zeus)

| Record type | Cases |
|---|---:|
| General Enquiry | 14,847 |
| Bird Week | 6,603 |
| Great Cocky Count | 1,867 |
| Birdata | 1,742 |
| eStore Enquiries | 1,737 |
| Conservation Campaigns, Powerful Owl, Participation, others | 3,356 |
| **Total supporter-facing** | **30,152** |

Status field history is not tracked, so time-to-first-response and time-to-resolve cannot be measured on any of these 30k conversations. The "3,600 in New" figure in the 1 July dashboard review is an org-wide backlog of supporter enquiries, not an ICT one.

---

## 2. The ecosystem: where supporter data lives and what does not flow

| Domain | System of record today | Feeds Salesforce? | Feeds Ortto? | Feeds analytics? | Gap |
|---|---|---|---|---|---|
| Identity and consent | Salesforce Contact | n/a | Yes (filtered) | Reports only | 200k in duplicate groups; 53% excluded from Ortto; no lead source; no household grouping |
| Giving | Salesforce NPSP + Payments2Us | n/a | Yes | Reports only | Two donor counts; Major Gift type unused; cancellation reasons unreported |
| Regular giving | Payments2Us Recurring Payment | n/a | Partly | No | NPSP RD history closed without a record of why |
| Membership | Payments2Us, moving to WooCommerce | miniOrange sync, ~10% failure | Yes | No | Three status sources at cutover; Emu access dependency |
| Participation | Salesforce PMM, Birdata (Interaction) | Native | Yes (PMM fields) | Reports only | Volunteer Interest flag not queryable by name; no participant-to-donor view |
| Volunteering | Nowhere (Better Impact planned) | Planned Phase 4 | Planned Phase 4 | No | No definition, no ID mapping, plan stalled |
| Communications | Ortto | Engagement summary not written back | n/a | Ortto reports | Retention limit reached; Lead not synced; 31% opted out |
| Service | Salesforce Case | n/a | No | Two private dashboards | No status history; 30k cases with no SLA measure |
| Commerce | WooCommerce, 5 Stripe accounts | miniOrange (orders only) | WooCommerce data source | No | Refunds untraceable in SF; no subscription mapping |
| Learning | LearnUpon | Enrolment package | Journeys | No | Completion not captured (catch-hook only on enrolment) |
| Web behaviour | GA4 | No | Ortto tracking code (ABC only) | No | GA4 reached only through a Zapier connection |
| Finance | NetSuite | Manual monthly CSV | No | Saved searches | $671k unreconciled at 3 Jul; no CRM, donor or BI integration in NetSuite |
| Analytics | 4,600 Salesforce reports; Claude department dashboards | | | | No warehouse, no metric dictionary, no owner per metric |

The pattern: Salesforce is the hub for identity, giving and participation; Ortto is the only place engagement and revenue attribution meet; volunteering, learning completion, web behaviour and finance sit outside the join entirely. Every cross-domain question (does volunteering predict giving; do members renew after a Birdata course; which branch's supporters churn) is answered today by export, spreadsheet and memory.

---

## 3. Maturity: where we are on a recognised scale

Scored against the Data Orchard Data Maturity Framework, the nonprofit-sector standard with five stages: Unaware, Emerging, Learning, Developing, Mastering. Evidence is from this read.

| Theme | Stage | Evidence |
|---|---|---|
| Uses (what data is used for) | Learning | Ortto journeys and appeal attribution are real. Cross-domain questions are not asked because they cannot be answered |
| Data (quality, coverage, identity) | Emerging | 42% in duplicate groups, 30% no postcode, two donor counts, no lead source, no volunteer record |
| Analysis | Emerging | 4,600 reports, none governed; dashboards in private folders; one scoping defect inflated ICT numbers 200 times for a month before anyone noticed |
| Leadership | Learning | ICT is asking the question. No named data owner for supporter, donor, member or volunteer definitions |
| Culture | Emerging | Priorities tracked in four divergent copies of a spreadsheet; findings sit in documents and are not converted to owned work |
| Tools | Developing | Salesforce NPSP, PMM, Ortto, Plauti, Payments2Us and Stripe are capable platforms. The problem is the joins between them, not the platforms |
| Skills | Learning | Salesforce developer capacity is contracted (Karishma Soni, 12 weeks); analytics skill sits with individuals, not a role |

Overall: **Emerging moving to Learning.** Realistic 12-month target: Developing across Data, Analysis and Leadership. Mastering is not a 12-month goal and should not be promised.

---

## 4. The gaps, ranked the way Mathew ranks (money, then what blocks people, then risk, then the rest)

| # | Gap | Evidence (7 Sep 2026) | Impact on people | Owner | Effort |
|---|---|---|---|---|---|
| 1 | 565 regular gifts suspended after failed retries | $4,277/month, $51k/year | Regular givers who intended to give are silently lapsed; Fundraising loses income it already won | Fundraising (V) with Keith | Hours |
| 2 | Donor count disagrees by 2x between the Last Gift field and Opportunities | 9,642 vs 18,959 | Ortto donor journeys, lapsed-donor audiences and welcome sequences target the wrong people | Keith / Karishma | Hours to diagnose, days to fix |
| 3 | Better Impact rollout will create a second supporter database with no key to Salesforce | 1 contact has a BI ID; SF sync is Phase 4, after branches are loaded in Phase 3 | Branch volunteers will be entered twice, matched by hand, and never linked to their giving or participation history | Mathew, James Vilinsky | Re-sequence now, before the 8 Sep import |
| 4 | Half the base is invisible to Ortto | 253,719 Ortto Inactive; retention limit reached | Any supporter in that half receives nothing, including members (839) and last-year donors (1,348) | Mathew, Inna Kersman | Days |
| 5 | Branch and SIG membership lists blocked | Asana task Blocked, assigned James Vilinsky | Ten branches cannot see or contact their own members; the single most requested Participation capability | James Vilinsky, Mathew | Decision, then days |
| 6 | No lead source on new contacts | 24 of 49,833 | Nobody can say which channel or program recruits supporters who stay | Keith (forms), Marketing | Hours per form |
| 7 | No status history on 30k supporter Cases | Field history off; existing Asana task (Kate Rogerson, Backlog) | Supporter Care cannot show response times to the Exec or fix the queue that is measured as "3,600 in New" | Kate Rogerson | Minutes to enable, months of data to accrue |
| 8 | Duplicate management decision outstanding | 200,441 in duplicate groups; Asana task Blocked | Supporters get two receipts, two welcomes, or none; every count above is inflated | Mathew to decide responsibility | Decision |
| 9 | 30% of contacts have no postcode | 142,412; 558 of last-year donors | Regional and branch analysis excludes a third of the base | Supporter Care, forms | Ongoing |
| 10 | Three membership truths at cutover | Contact flag, P2Us RP status, WooCommerce subscription | Members lose journal access or get renewal reminders from two systems | Membership project (Blitzm, Karishma) | Design decision in the current build |
| 11 | Volunteer Interest cannot be counted | Field synced to Ortto but not queryable under the expected API name | Participation cannot size its own volunteer pool | Keith | Minutes to find the field |
| 12 | Learning completion not captured | LearnUpon hook fires on enrolment only | Code of Conduct completion for new volunteers cannot be evidenced | Keith, Isis St Pierre | Hours |

Items 3, 5 and 8 are decisions, not technical work. They belong in one meeting with Mathew, James Vilinsky and Micah Demmert.

---

## 5. Insights we can produce now, from data already held

These need no new tools. Each one names the source and the decision it informs.

| Question | Source | Answer today | Decision it drives |
|---|---|---|---|
| Are participants becoming donors? | PMM engagement joined to Last Gift Date | 68% of donors are participants; 3% of participants are donors | Fundraising builds a participant-to-donor journey in Ortto, starting with Aussie Bird Count registrants (155k audience) |
| Which regular gifts can be recovered? | Recurring Payment status = Suspended | 565 records, $51k/year | Card-update campaign this month |
| Why do regular givers cancel? | Cancellation Reason picklist on 941 records | Not yet reported | First report tells Fundraising whether it is price, trust or process |
| Is membership growing or churning? | Membership RP Active vs Expired | 4,386 active, 3,215 expired | Sets the renewal target for the WooCommerce rebuild |
| Who are the active citizen scientists? | Birdata Interaction, last 365 days | 4,090 people, 19 surveys each | The core volunteer cohort to seed Better Impact with, and the group to ask first about giving |
| Where are our supporters? | Contact postcode against branch regions | Blind for 30% | Branch lists (gap 5) once postcode capture is fixed |
| Does email still work? | Ortto campaign reports | Open rates 44 to 74%, click 0.6 to 17% | Fine on opens, weak on clicks for volunteer updates: content and call-to-action review |
| What is the appeal return? | Ortto attribution to won Opportunities | Major gift EDM: 355 sent, 19 gifts, $221,719 | Keep instrumenting every send with an Opportunity goal |
| How much bequest dependency? | Opportunity record type | 35% of income from 39 estates | Board-level risk disclosure and a bequest pipeline measure |
| What do supporters contact us about? | Case record type and subject | 30k cases, half General Enquiry | Sub-type General Enquiry so self-service content can be built for the top ten |

---

## 6. The analytical data process (the operating model)

A process, not a project. Six stages, each with a rule that stops it degrading.

```
DEFINE  -->  CAPTURE  -->  JOIN  -->  CHECK  -->  ANALYSE  -->  ACT  -->  LEARN
metric       forms and    supporter  monthly     the ten      owner    write the
dictionary   integrations ID in      quality     questions    named,   answer into
and owners   carry the    every      scorecard   above, then  dated    the skill and
             source       system                 the next ten          the dictionary
```

**Define.** One metric dictionary, versioned in this repo, with a named owner for each definition. The first seven entries: supporter, member, donor, regular giver, volunteer, participant, reachable. Nothing gets reported that is not in the dictionary. Owners: Fundraising for donor and regular giver; Participation (James Vilinsky) for volunteer and participant; Membership for member; ICT for reachable and supporter.

**Capture.** Every entry point (Gravity Forms, Raisely, WooCommerce, Ortto forms, Birdata, Better Impact, Humanitix) writes a Lead Source and a consent state. The web form audit already in progress (Caroline Scales) is the vehicle.

**Join.** The Salesforce Contact ID (the `C-` supporter number) is the key. It travels into Ortto (already), Better Impact (add to the UserData.xlsx export in Phase 2), WooCommerce (miniOrange), LearnUpon and Birdata. A record in any system without a supporter ID is a data quality failure, counted monthly.

**Check.** A monthly supporter data quality scorecard, produced by the weekday routine and published to the department dashboards: duplicate groups, postcode coverage, opt-out rate, Ortto-inactive share, records without supporter ID, donor-count reconciliation (the 9,642 vs 18,959 test), regular gifts suspended. Each line has an owner and moves or does not.

**Analyse.** The ten questions in section 5 answered quarterly, then the next ten. Analysis is written up in Mathew's report register (decision first, number with date, owner and date on every action, provenance line).

**Act.** Every insight becomes one Asana task with an owner and a date, through the console's Fixes tab, one at a time. Insight without an owner is a slide.

**Learn.** When a fix lands, the owning skill in this repo gets the outcome and the dictionary gets the corrected definition. That is how the next session and the next analyst start smarter.

### Supporter lifecycle model (the spine every metric hangs on)

| Stage | Signal in data | System |
|---|---|---|
| Aware | Ortto subscriber, web event, campaign member Invited | Ortto, Salesforce |
| Participate | Program Engagement, Birdata survey, event registration, course enrolment | Salesforce PMM, Birdata, LearnUpon |
| Support | First won Opportunity, membership purchase | Salesforce, WooCommerce |
| Sustain | Active recurring payment, membership renewal, second gift | Payments2Us, then WooCommerce |
| Volunteer and advocate | Better Impact status Active, campaign member Responded on advocacy | Better Impact, Salesforce |
| Lapse | Expired RP, no gift in 13 months, unsubscribed, Ortto inactive | Salesforce, Ortto |
| Reactivate | Gift or engagement after lapse | Salesforce |

Every stage transition is an event that already exists in a system. The future-state warehouse stores those transitions per supporter ID; that table alone answers most of section 5 without a data scientist.

---

## 7. What to do better: 30, 90 and 180 days

### Next 30 days (no tools, decisions and plumbing)

| Action | Owner | By | Impact on people |
|---|---|---|---|
| Convene one decision meeting: volunteer definition, Better Impact sequencing, duplicate ownership, branch list release | Mathew with James Vilinsky, Micah Demmert | 18 Sep | Unblocks three Blocked Asana tasks and ten branches |
| Add Salesforce Contact ID to the Better Impact UserData.xlsx export before the first bulk import | Mathew, Keith | Before 8 Sep import (or delay the import) | Stops a second identity silo before it is created |
| Diagnose the donor-count gap (Last Gift Date vs Opportunities) and fix the rollup | Keith, Karishma | 25 Sep | Donor journeys target the right people |
| Run the suspended regular gift recovery (565 records) | Fundraising (V) with Keith | 30 Sep | $51k/year of intended gifts resumes |
| Turn on Case Status field history (existing task) | Kate Rogerson | 15 Sep | Supporter Care can measure response time from October |
| Ortto Inactive review: why 253,719, and the retention upgrade decision | Mathew, Inna Kersman | 30 Sep | Members and donors currently unreachable can be reached |
| Publish the first seven dictionary definitions | Mathew (draft), owners sign | 30 Sep | Every report after this uses the same words |

### 30 to 90 days (make the data trustworthy)

- Lead Source on every form and integration (web form audit output).
- Duplicate management: run the Plauti merge under the decided ownership; report duplicate groups monthly.
- Postcode capture made mandatory on all forms; back-fill from Birdata and WooCommerce where the supporter ID matches.
- Monthly supporter data quality scorecard live on the department dashboards.
- Membership rebuild: decide the single membership status source and the `Active_BL_Member__c` successor before the Salesforce side is built.
- Better Impact Phase 2 and 3 with supporter ID carried on every import; Phase 4 sync designed against that key.
- Cancellation-reason and regular-giving attrition report to Fundraising, quarterly.

### 90 to 180 days (the reporting layer)

- Stand up Power BI on the Microsoft 365 tenant BirdLife already runs, with a small Azure SQL or Fabric store fed nightly from Salesforce, Ortto exports, Better Impact API, Stripe and NetSuite saved searches. Rationale: it sits inside the identity and security estate ICT already governs, nonprofit pricing exists, and the NetSuite review already recommended Power BI from day one under Business Central.
- First three models: Supporter 360 (one row per supporter ID with lifecycle stage), Giving (gifts, regular giving, attrition), Participation and Volunteering (engagements, surveys, Better Impact hours).
- Retire the unscoped Salesforce dashboards and the four copies of ICT Priorities.xlsx into the new layer.
- Quarterly insight review with Fundraising, Participation and Supporter Care, run off the ten questions.

Indicative cost, unquoted and to be verified: Power BI Pro under nonprofit licensing is low tens of dollars per builder per month; a small Fabric or Azure SQL footprint is low hundreds per month; the larger cost is people time, roughly 0.5 FTE of analyst or developer capacity for six months. Salesforce's own analytics products (CRM Analytics, Data Cloud) would answer the same questions at several times the cost and would not reach NetSuite, Better Impact or Stripe.

---

## 8. Future state (12 to 18 months)

**One supporter, one ID, many systems.** Salesforce remains the system of record for identity, consent, giving and participation. Better Impact owns volunteer management and writes status and hours summary back against the supporter ID. Ortto owns engagement and writes an engagement score back. WooCommerce and Stripe own commerce; membership status has one truth in Salesforce. NetSuite (or Business Central) owns finance and receives reconciled income by supporter segment, not a monthly CSV.

**A governed metric layer.** The dictionary, the owners, the monthly scorecard and the quarterly review are routine, not effort. Numbers on the Board paper are the same numbers on the Fundraising dashboard, because they come from the same model.

**Supporter-facing outcomes.** Branches see and contact their own members. A citizen scientist who logs 19 surveys a year is thanked, invited to volunteer, and asked to give, in that order and not all at once. A regular giver whose card fails is contacted within a week, not lost into "Suspended". A member renewing through the new site gets one reminder schedule, keeps journal access, and is recognised as the same person who counted birds in October.

**Analytics as a service inside ICT.** The Claude routines already refresh nine department dashboards each weekday. In the future state they read from the warehouse rather than hand-built queries, and the insight loop in section 6 is run by ICT with named business owners deciding.

**What this is not.** It is not a data science program, it is not a new CRM, and it does not require replacing Salesforce, Ortto or Better Impact. The estate is capable. The work is definitions, keys, quality and one reporting layer.

---

## 9. Decisions taken (Mathew Hema, 7 September 2026)

| Decision | Outcome | What it still needs, and where I push back |
|---|---|---|
| Volunteer system | **Better Impact is the system of choice for volunteers.** | The decision names the system, not the key. Assumption recorded here: the Salesforce Contact ID travels on every Better Impact import from the first one, and a volunteer is defined as "a person with an Active status in Better Impact" from cutover. Until then Birdata surveyors and shorebird counters are participants, not volunteers. The first bulk import is due 8 Sep; if the ID column is not in the UserData export, delay the import rather than load 10 branches without a key. The Salesforce sync task moves from Phase 4 to a design item in Phase 2. |
| Duplicate management | **Owned by Supporter Care.** | Supporter Care owns the outcome; ICT still owns the controls. The Blocked "Plauti bulk merge permissions" item has to be granted to the named Supporter Care owner, and the API paths (Raisely via MoveData, miniOrange) bypass Plauti entirely, so ICT keeps duplicate rules on those integrations. Name the person, not the team, before the task leaves Blocked. Merge order matters: Portal User records are the master, financial records on blank duplicates escalate. |
| Ortto retention and Lead | **Retention upgrade funded. Lead does not sync.** | Confirmed safe: Lead holds 6 records ever, none created in the last year. Lead sync is closed. The retention upgrade unblocks the Ortto Inactive review (253,719 excluded); that review is still owed by 30 Sep and Marketing needs to state the rule that will replace the current filter. |
| Reporting layer | **Power BI.** | Power BI sits on the Microsoft tenant ICT already governs. Two constraints to settle in the design: Salesforce has 70 of 70 full licences consumed, so the Power BI connection either reuses an existing integration user or a licence is freed first; and the store (Azure SQL or Fabric) needs a quote. Business Central timing decides whether the finance feed is built once or twice. |
| Participant-to-donor journey | **Owned by Marketing.** | Inna Kersman builds journeys today, so this lands with her. Dependency stated plainly: the journey must not launch on the "Last Gift Date" field until the 9,642 vs 18,959 donor-count gap is fixed, or it will invite existing donors to give for the first time. Fundraising sets the ask and the segment; Marketing owns the build and the measure. |

### What these decisions unblock, and the tasks they become

Each line is one Asana task, created one at a time behind an approval, per the charter.

| Task | Project / section | Owner | Due |
|---|---|---|---|
| Add Salesforce Contact ID to the Better Impact UserData export; block the 8 Sep import until it is present | ICT Better Impact Implementation, Phase 2 | Mathew Hema | 8 Sep 2026 |
| Move "Salesforce Integration with Better Impact" from Blocked to In Development as a Phase 2 design item keyed on Contact ID | IT Operations Project Plan | Mathew Hema | 18 Sep 2026 |
| Write the volunteer definition into the metric dictionary (Better Impact Active status) and confirm with James Vilinsky | IT Operations Project Plan, Backlog/Requests | Mathew Hema | 30 Sep 2026 |
| Grant Plauti bulk merge permission to the named Supporter Care owner; move "Duplicate Management, decision on responsibility" out of Blocked | IT Operations Project Plan | Mathew Hema, then Keith Tsui | 18 Sep 2026 |
| Diagnose and fix the Last Gift Date rollup (9,642 vs 18,959) | IT Operations Project Plan, In Development | Keith Tsui, Karishma Soni | 25 Sep 2026 |
| Ortto Inactive rule review after the retention upgrade lands | IT Operations Project Plan, Backlog/Requests | Mathew Hema, Inna Kersman | 30 Sep 2026 |
| Power BI design note: licence path for the Salesforce connection, store choice, first three models | IT Operations Project Plan, Backlog/Requests | Mathew Hema | 31 Oct 2026 |
| Participant-to-donor journey brief: segment, ask, measure; blocked on the rollup fix | Marketing and Sales, Requests | Inna Kersman | 30 Sep 2026 |

## 9a. Decisions still open

1. **The named person in Supporter Care who owns duplicates.** A team cannot hold a Plauti permission.
2. **Whether the 8 Sep Better Impact import proceeds without the Contact ID column.** Recommendation: it does not.
3. **The Salesforce licence path for Power BI** (reuse an integration user or free a licence).
4. **Business Central timing**, which decides whether the finance feed into Power BI is built once or twice.

---

## Provenance

Read on 7 Sep 2026 between 01:30 and 03:00 UTC via the Salesforce Production connector (SOQL on Contact, Account, Opportunity, `npe03__Recurring_Donation__c`, `AAkPay__Recurring_Payment__c`, `pmdm__ProgramEngagement__c`, `Interaction__c`, `WebsiteEvent__c`, CampaignMember, Campaign, Case, `dupcheck__dc3Duplicate__c`, LearnUpon enrolments, Volunteers for Salesforce objects), the Ortto connector (schema, audiences, journeys, campaign reports) and the Asana connector (Better Impact Implementation project, task searches). Stripe, NetSuite, WordPress and Zapier facts are from the repo skills, dated June to September 2026, and were not re-read live. Not readable from here: Better Impact itself (no connector), production WooCommerce, GA4, Entra posture. Contact counts include duplicates; no de-duplicated figures exist until decision 2 is made.
