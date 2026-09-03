# Pocket PT

A personal-trainer app for a phone, built as a single HTML page (`coach.html`) so it
runs in Samsung Internet or Chrome and can be added to the home screen. Everything is
stored in the phone's browser storage; nothing is uploaded.

Built for Mathew Hema (56, Māori male): the coach is demanding, the program follows
the evidence for men over 50, and the daily structure is Te Whare Tapa Whā. The look
is a HUD: arc-reactor cyan on near-black, gold secondary, translucent panels with corner
brackets, Orbitron for numbers and Rajdhani for the interface.

## Coach styles and voice

Three styles, cycled from the Coach tab. Every spoken line comes from a persona table and
is played through a delivery engine (base pace and pitch, sentence-to-sentence bounce,
real pauses between thoughts, a trailing-off drop on the last thought; an ellipsis in a
line is a longer beat):

- **Deadpan Kiwi**: unhurried and bouncy, warm, casually deadpan, te reo Māori woven in.
- **Gentle giant**: soft, slow, low, very polite, still not letting you off.
- **Straight coach**: plain.

Te reo words are respelled for the speech engine only (whānau is sent as far-no) so an
English voice pronounces them properly; the screen keeps the correct spelling. The app
prefers the phone's New Zealand English voice and ranks the network (neural) voices first.

## What it does

| Tab | What a trainer would do | What the app does |
|---|---|---|
| Today | Check in, call out slack, set the day's work | Coach's call built from this week's sessions, missed sessions, days since the last one, yesterday's steps and last night's sleep (from the watch). Weekly scoreboard (strength / Zone 2 minutes / intervals). Te Whare Tapa Whā habits: tinana, hinengaro, whānau, wairua. Spoken pep talk. |
| Train | Program, coaching cues, rest timing | 3-, 4- or 5-day programs for bodyweight, dumbbells or full gym, with power, balance and carry work built in. Guided session mode: the voice announces each exercise and cue, counts sets, runs the rest clock with a 10-second warning and 3-2-1 beeps. Live heart rate over Bluetooth (Chrome). |
| Move | Yoga, Pilates, stretching, and a way to grow it | Six built-in guided sessions (Morning Mobility, Pilates Core, Post-Lift Stretch, Evening Wind-Down, Desk Reset, Balance and Stability) over a 37-move library. The runner gives a get-into-position count, a timed hold with breathing prompts, automatic side switching, pause, +15 s and skip, and keeps the screen awake. Every session levels up with completions (holds ×1.25 at level 2, ×1.5 at level 3). A builder composes your own sessions from the library with per-move seconds, and you can add your own moves with a cue. Mobility is the fourth tile on the weekly scoreboard (target 3) and rest days recommend a session. |
| Fuel | Calories, macros, a day of eating, the rules | Mifflin-St Jeor maintenance, goal-adjusted target, protein at 1.8–2.0 g/kg split to 35–40 g per meal, creatine, fibre, alcohol and gout guidance, example day. |
| Progress | Track what matters | Weight trend chart, waist with risk bands (94 / 102 cm), training history, and the Samsung Health import (steps, sleep, resting heart rate, weight, workouts from the watch). |
| Coach | Accountability beyond the gym | Voice on/off, coach style toggle (Deadpan Kiwi or Straight coach), in-app voice picker with pace and pitch controls and a guide to installing the New Zealand English voice pack, health checks that go amber when due (heart health check, HbA1c, uric acid, bowel kit, prostate conversation, skin, dental), heart-rate zones for the watch, profile, backup. |

## Samsung Health and the Galaxy Watch

A web page cannot read Samsung Health directly. Two things work today:

1. **Import the export.** Samsung Health → ⋮ → Settings → Download personal data,
   then Progress → Import and pick the zip. Steps and sleep tick the habits and feed
   the streak; heart rate, weight and workouts land in Progress. Do it weekly.
2. **Live heart rate in a session** over Web Bluetooth in Chrome. Chest straps work as
   is; the Galaxy Watch needs a heart-rate broadcast app from the Galaxy Store.

Automatic sync with no export step needs a native Android app reading Health Connect
(Kotlin, Android Studio, sideload or Play Store). That is phase 2.

## Running it

Open `coach.html` in a browser, or publish it as a Claude artifact and add the URL to
the home screen. The page loads Archivo and Barlow from Google Fonts and JSZip from
cdnjs; everything else is inline.
