# Prompt A — Admin audit via Claude in Chrome (signed-in browser)

Paste the block below into Claude in Chrome with the signed-in AFO tab open.

```text
I'm signed in to the Open Journal Systems (OJS) site at https://afo.birdlife.org.au/afo/index.php/afo/user
(Australian Field Ornithology, BirdLife Australia). We are auditing it so we can rebuild
it on another platform. Walk the admin interface and record everything below. Do not
change any settings — this is read-only. Produce a single structured markdown report
at the end.

1. SYSTEM
   - Go to Administration → System Information. Record: OJS version, PHP version,
     database driver + version, server info, and the full config summary shown.
   - Record the value of any "generator" info and admin version notices
     (e.g. "a new version is available").

2. SITE & JOURNAL SETUP
   - Settings → Journal: journal title, initials, path, ISSNs, publisher, contacts.
   - Settings → Journal → Sections: list every section name and its policies
     (peer-reviewed flag, indexed flag).
   - Settings → Website → Appearance: active theme, any custom CSS uploaded, logo files.
   - Settings → Website → Setup: navigation menus (every menu item + URL),
     sidebar blocks in use, homepage content settings.
   - Settings → Website → Plugins: list EVERY installed plugin and whether it is
     enabled or disabled. Note anything under the "generic", "import/export",
     "payment", "reports", and "OAI/metadata" categories specifically.
   - Static Pages plugin (if enabled): list every static page path and title.
   - Announcements: are they enabled, and how many exist?

3. USERS & ROLES
   - Users & Roles → Users: total user count (the list shows a total).
   - Roughly how many users hold each role: Journal Manager, Editor, Section Editor,
     Reviewer, Author, Reader. Exact numbers if visible, estimates otherwise.
   - Users & Roles → Site Access Options: registration open or closed? Reader
     registration required to view content?

4. EDITORIAL CONTENT & WORKFLOW STATE
   - Submissions: counts in each queue — My Queue / Unassigned / All Active / Archives.
     Break down active submissions by stage (Submission, Review, Copyediting,
     Production) if visible.
   - Issues → Back Issues: total number of published issues, the volume/number/year
     of the OLDEST and NEWEST published issue.
   - Issues → Future Issues: any issues in progress?
   - Approximate total published articles if any statistics page shows it
     (Statistics → Articles, or Publication statistics).

5. DISTRIBUTION & IDENTIFIERS
   - Settings → Distribution: DOI settings (is a DOI plugin/Crossref configured?
     what DOI prefix?), indexing/metadata settings, payments (is the payments
     module on?), access settings (fully open access? subscription?).
   - Tools → Import/Export: list every import/export plugin available
     (e.g. Native XML, Users XML, Crossref XML, PubMed, DOAJ, QuickSubmit).

6. EMAIL & TEMPLATES
   - Settings → Workflow → Emails: note whether email templates have been customised
     (any marked as modified), and the "from" address configured.

7. EXPORTS (do these last; download files, don't change anything)
   - Tools → Import/Export → Native XML Plugin → Export Issues: select ALL issues
     and export. Save the XML file.
   - Tools → Import/Export → Users XML Plugin: export users. Save the file.
     (Skip if it errors or times out — just note that.)

REPORT FORMAT: one markdown document titled "AFO OJS Admin Audit — <today's date>",
with sections matching the numbers above, every value written explicitly
("not visible" is an acceptable value — never guess). At the end include a
"Red flags for migration" list: anything old, customised, disabled-but-referenced,
or unusual you noticed along the way.
```

**Then:** save the report as `afo-audit/ADMIN-AUDIT.md` in this repo (or paste it back
into the Claude Code session) along with the two export XML files.
