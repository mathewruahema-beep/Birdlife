#!/usr/bin/env bash
# AFO harvest — run this on your own machine (the Claude cloud session cannot
# reach afo.birdlife.org.au). From the repo root:
#
#   bash afo-audit/harvest-afo.sh
#
# Takes roughly 1-2 hours at the polite default rate. Safe to re-run;
# safe against production (read-only, sequential, rate-limited).
set -euo pipefail
cd "$(dirname "$0")/.."

pip3 install -q -r site-harvester/requirements.txt

echo "=== Pass 1: OAI-PMH metadata harvest (authoritative article list, ~2 min) ==="
python3 site-harvester/oai_harvest.py \
    "https://afo.birdlife.org.au/afo/index.php/afo/oai" \
    --out ./harvest/afo-oai

echo
echo "=== Pass 2: full site crawl (pages, PDFs, assets — the long one) ==="
python3 site-harvester/harvest.py \
    "https://afo.birdlife.org.au/afo/index.php/afo" \
    --out ./harvest/afo \
    --max-pages 8000 \
    --delay 0.5

echo
echo "=== Done. Review these, in order: ==="
echo "  harvest/afo-oai/articles.csv   <- every published article + per-year counts (printed above)"
echo "  harvest/afo/AUDIT.md           <- crawl summary + platform fingerprint"
echo "  harvest/afo/pages.csv          <- page inventory"
echo "  harvest/afo/raw/               <- offline mirror incl. galley PDFs"
echo
echo "Then commit the CSVs and AUDIT.md back to branch claude/website-audit-migration-6ymaha"
echo "(skip raw/ if it is huge - zip it somewhere safe instead):"
echo "  git checkout claude/website-audit-migration-6ymaha"
echo "  git add harvest/afo-oai/articles.csv harvest/afo/{AUDIT.md,manifest.json,pages.csv,assets.csv,redirect-map.csv}"
echo "  git commit -m 'Add AFO harvest results' && git push"
