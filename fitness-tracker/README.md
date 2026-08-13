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

The **Kaupapa / Plan** tab carries the weekly training rhythm, the 4-day strength +
3-day active split, and the full session library from the spreadsheet.

## Using it on a Samsung phone

1. Open the page in **Samsung Internet** or **Chrome**.
2. Menu (⋮ or ≡) → **Add page to** → **Home screen** (Samsung Internet) or **Add to Home screen** (Chrome).
3. It opens like an app from then on.

## Data & backups

Entries are saved in the browser's local storage **on the phone itself** — nothing is
sent anywhere. Settings → **Backup (JSON)** saves a restore file; **Spreadsheet (CSV)**
exports all entries in a format that opens in Excel. Restoring a backup merges it with
whatever is already on the device.
