# Quiet Storm, a baritone and bass voice coach

A single-file web app (`index.html`, no build, no dependencies) that measures a low
male voice with the microphone and coaches it toward the smooth R&B sound.

- **Assess**: a ten-minute baseline of seven numbers: lowest and highest clean note,
  pitch accuracy (cents), stability (cents SD on a held note), sustain (s), agility
  (% on target in a five-note scale) and breath (s of steady hiss). Reassess every
  14 days; progress charts compare against the first baseline.
- **Train**: laddering pattern exercises (scales, arpeggios, passaggio slides, low
  extension, chromatic), tone work (sustain, messa di voce), breath, and a Smooth
  category (legato slides, pentatonic runs, an original quiet-storm phrase, vibrato
  rate and width, quiet crooning).
- **Play**: Note Hunt, a timed ear game.
- **Coach**: frank feedback with a Firm or Brutal setting, and a daily plan built
  from the weakest numbers.

Pitch detection is a normalised autocorrelation (McLeod-style) at 2048 samples with
a 0.88 clarity gate, accurate to under a cent from A1 to A4 on synthetic tones. All
data lives in the browser's localStorage with copy-and-paste export and import.

## Running it

Open `index.html` in Chrome, Edge or Samsung Internet over HTTPS or as a local file
and allow the microphone. On a phone, use the browser menu's **Add to Home screen**.
The page is also published as a Claude artifact from the session that built it.
