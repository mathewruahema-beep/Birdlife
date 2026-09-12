# ADR 0019: Birdata supporter feed goes to Salesforce, not to Ortto

Date: 7 September 2026
Status: Accepted (design), execution pending under IT-INT-004
Type: Integration design and data contract
Decider: Mathew Hema, Senior Manager ICT

## Context

Fundraising wants Ortto audiences and journeys built on Birdata activity. James Watmuff (Planticle) confirmed on 22 June 2026 that Birdata is MySQL on EC2 with no external database access, a daily DuckDB admin snapshot, and highly sensitive sighting data, and offered a scheduled job pushing user data to the Ortto API.

Verified live on 7 September 2026: Ortto already syncs 41 Contact fields and 89 event fields from Salesforce and carries no Birdata field. Salesforce already holds a purpose-built Birdata model (Interaction__c, 689,894 rows on 17,077 Contacts, plus Contact rollups) that is loaded by hand by Keith Tsui and last ran on 6 July 2026.

## Decision

1. Birdata pushes to Salesforce, not to Ortto. Ortto inherits the fields through the existing Salesforce sync. No Ortto API key is issued.
2. The feed carries aggregates only (six numbers per person: survey totals, last 365 days, last survey date, species count, primary state code, last logins). No survey rows, coordinates, site names or species names leave Birdata.
3. Identity is seeded once by an offline match on email plus first name plus last name (normalised), run in DuckDB on Mathew's laptop, and from then on the job matches on Birdata_User_Id__c, an external ID on Contact. The job never matches on email at run time and never creates a Contact.
4. The credential is a dedicated Salesforce integration user on the API-only profile, issued and rotated by Mathew. Birdata becomes an ADR 0006 Tier B connector; business data owner proposed as Caroline Scales, to be confirmed.
5. Interaction__c is archived to SharePoint and its rows deleted once the new feed has reconciled for one month, recovering about 1.3 GB of Salesforce data storage.

## Alternatives rejected

Birdata to Ortto direct (the vendor's offer): fastest, but creates a second identity-matching path, puts supporter data in a marketing tool that never reaches the CRM, and sends location data to Ortto. Working from the DuckDB snapshot as a permanent pipeline: sensitive data on a laptop, rebuilds what the vendor can do properly.

## Consequences

Keith stops the manual load and owns six new fields, the backfill, a weekly skipped-record review and the Ortto mapping. James builds to the aggregate contract, less work than survey rows. Jonathon Wilson signs the field list. The consent question (a Birdata account is not marketing consent) must close before any journey uses the fields; the NO_CONTACT population is not loaded anywhere until it does. Per-survey history is no longer held in Salesforce; Birdata remains the record of surveys.

## Records

IT-INT-004_Birdata_Supporter_Feed_Data_Contract.docx and IT-INT-004_Birdata_Email_Match.sql in OneDrive Birdlife\AWS. Seven Asana tasks prefixed "IT-INT-004 Birdata feed" in the IT Operations Project Plan. Reply draft to James Watmuff in Outlook Drafts.
