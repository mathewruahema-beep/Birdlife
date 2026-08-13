# Te Ara Hauora — personal fitness tracker

A single-file, phone-first wellbeing tracker built for daily use on a Samsung phone,
structured around **Te Whare Tapa Whā** (taha tinana, taha hinengaro, taha wairua, taha whānau).

Everything lives in `index.html` — no build step, no server, no accounts.

## What it tracks

- **Taumaha / Weight** — daily weigh-in with a goal line (90 kg) and a chart over 30 days / 90 days / 1 year / all time. Pre-loaded with 862 historical entries from the *Goals & Tracking* spreadsheet.
- **Wai / Water** — glass-at-a-time counter against a daily litres goal.
- **Kai / Food** — parakuihi, tina, hapa, paramanawa (breakfast, lunch, dinner, snacks).
- **Korikori / Exercise** — free-text log with one-tap chips (hīkoi, gym, golf, bike, pilates, boxing, basketball…) and the day's planned session shown from the weekly programme.
- **Rongoā / Medication** — morning and evening tick-offs plus an as-needed field (medication names editable in Settings).
- **Moe / Sleep & stress** — free-text nightly notes.
- **Te Whare Tapa Whā** — four daily tap-to-complete cornerstones, each with the day's suggestion from the Energy plan (karakia, whanaungatanga, hīkoi, whānau time…).

- **Portions & targets** (from *Food Log v2*) — hand-portion counters (protein palms, veg
  fists, carb cupped hands, fat thumbs, sugary/diet drinks) with live estimated kcal and
  protein against Mifflin-St Jeor targets computed from height, latest weight, age,
  activity factor and chosen loss rate, floored at BMR.
- **Peptides** — per-compound syringe-unit logging (Tesamorelin, Retatrutide, BPC/TB) with
  a vial dose calculator (mg ÷ ml → mg/ml; units ÷ 100 × concentration = dose), plus daily
  readings: waist (primary metric, target = height ÷ 2), resting HR, BP, appetite, energy,
  nausea, reflux, night wakings and side-effect notes.
- **Ngākau / Heart check** — daily gratitude, happiness rating (1–5), improvement and
  service notes, gathered into a browsable "kete" on the Review tab.
- **Wairua / Spiritual** — karakia, scriptures read, talks, Come Follow Me, calling
  contact and temple attendance, with the 2026 spiritual goals shown on the Plan tab.
- **Tuhinga / Journal** — free-text daily journal.
- **Arotake / Weekly review** — per-week days-logged, average kcal vs target, protein-hit
  days, sugary drinks, water, weight, waist, happiness, gratitude/service counts, and the
  Food Log v2 verdict rules ("Not enough days logged…", "OVER target…", "protein short…",
  "On track").

The **Kaupapa / Plan** tab carries the weekly training rhythm, the 4-day strength +
3-day active split, the full session library, the hand-portion guide with calibration
examples, and the peptide dose calculator.

## Offline use

Everything logs to local storage, so the page keeps working through connectivity drops
(an offline banner appears; Drive sync resumes automatically on the `online` event).
For a fully installable offline app, the folder ships `manifest.webmanifest`, `sw.js`
(stale-while-revalidate cache) and `icon.svg`: host the folder over HTTPS — e.g. GitHub
Pages (repo Settings → Pages → deploy from branch, then open
`/Birdlife/fitness-tracker/`) — and "Add to Home screen" installs it with offline cache.
The service worker only registers when served over http(s), so the claude.ai artifact
build is unaffected.

## Google Drive sync

When opened as a claude.ai artifact, the app syncs to the viewer's own Google Drive
connector (`create_file` / `search_files` / `download_file_content`):

- **Daily auto-sync** — once per day, on first load/edit while online, it writes both
  `te-ara-hauora-backup-YYYY-MM-DD.json` (full state) and
  `te-ara-hauora-log-YYYY-MM-DD.csv` (the complete day-by-day record, opens in Excel).
- **Manual** — Save to Drive / Restore from Drive buttons on the Review tab.

The data therefore lives outside the app in the user's Drive, and any Claude
conversation with Drive access can read it back for review. Outside claude.ai the
buttons hide and the local JSON/CSV backup in Settings remains.

## Using it on a Samsung phone

1. Open the page in **Samsung Internet** or **Chrome**.
2. Menu (⋮ or ≡) → **Add page to** → **Home screen** (Samsung Internet) or **Add to Home screen** (Chrome).
3. It opens like an app from then on.

## Data & backups

Entries are saved in the browser's local storage **on the phone itself** — nothing is
sent anywhere. Settings → **Backup (JSON)** saves a restore file; **Spreadsheet (CSV)**
exports all entries in a format that opens in Excel. Restoring a backup merges it with
whatever is already on the device.
