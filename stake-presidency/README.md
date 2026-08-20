# Stake Presidency Assistant

A single-file, fully private planner for stake presidency work.

| | |
|---|---|
| Live tool | https://claude.ai/code/artifact/d690ae08-c63a-4367-aba3-4e7ffd36669f |
| Source | `stake-presidency/index.html` — no build step, no dependencies |
| Data | Browser `localStorage` only. Nothing is sent to any server. |

## What it tracks

- **Dashboard** — the next four Sundays (with uncovered Sundays flagged), callings
  in motion, interviews in the next fortnight, open action items with overdue
  flags, and upcoming ward conferences.
- **Sundays** — who is visiting, presiding or speaking in which unit each week.
- **Callings** — a pipeline from *Recommended → Approved → Call extended →
  Sustained → Set apart → Recorded*, with a one-click "Advance" per calling.
- **Interviews** — temple recommend, calling, missionary, patriarchal blessing
  and youth interviews, with a "Mark held" toggle.
- **Action items** — assignments out of presidency meeting, with owner, due
  date and overdue flagging.
- **Units** — the wards and branches of the stake, their leaders and ward
  conference dates (conference dates feed the dashboard automatically).

## Privacy and backup

Names of members, interview schedules and calling deliberations are sensitive.
The tool therefore keeps everything in the browser it is used in — there is no
account, no sync, and no network traffic beyond loading two Google Fonts.

**Settings & backup** (top right) holds the stake name, the presidency /
high-council name list that powers the autocomplete fields, and a copy/paste
backup: *Copy backup* puts the full dataset on the clipboard as JSON; pasting
that text back and pressing *Restore* loads it on any device. Because storage
is per-browser, copy a backup periodically — clearing browser data clears the
tool's data too.

The same file can also be opened directly from disk (`index.html`) if a
non-hosted copy is preferred.
