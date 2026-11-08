# Daily AI Digest

A daily page of the AI news that matters for building AI workflows in product marketing.
Live at https://dpnation.github.io/ai-digest/

## How it works
1. Every morning a Claude scheduled task reads Dana's AI newsletters in Gmail, picks the relevant stories, and writes `digest.json`.
2. It runs `python3 build_digest.py`, which renders `index.html` in the dpnation style and saves a copy of the day's data to `archive/YYYY-MM-DD.json`.
3. It commits and pushes to `main`. GitHub Pages serves `index.html`.

No dependencies beyond Python 3.10+.

## digest.json shape
```json
{
  "date": "YYYY-MM-DD",
  "note": "optional one-liner, e.g. 'Slow news day.'",
  "stats": {"newsletters_scanned": 0, "read_in_full": 0},
  "top": [{"title": "", "url": "", "source": "", "also_in": [], "summary": "", "why": ""}],
  "try_this": {"title": "", "url": "", "how": ""},
  "sections": {
    "workflows": [], "governance": [], "competitive": [],
    "measurement": [], "enablement": [], "landscape": []
  }
}
```
Section items use the same fields as `top`. Empty sections are hidden.
