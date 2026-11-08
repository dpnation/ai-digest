#!/usr/bin/env python3
"""
Daily AI Digest builder.

Reads digest.json (written each morning by Dana's Claude scheduled task, which
curates AI newsletters from Gmail) and renders index.html in the dpnation style.
Also archives each day's JSON to archive/YYYY-MM-DD.json and links recent days.

Usage:  python3 build_digest.py            # builds from digest.json
"""

import datetime
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "digest.json"
ARCHIVE = ROOT / "archive"
OUT = ROOT / "index.html"

# Section keys used in digest.json -> (heading, icon). Order = page order.
SECTIONS = [
    ("workflows",   "🧩", "Workflows, Skills & Agents"),
    ("governance",  "🛡️", "AI Guardrails & Governance"),
    ("competitive", "🎯", "Competitive Intel & Orchestration Market"),
    ("measurement", "📊", "Measuring AI Impact"),
    ("enablement",  "🚀", "Enablement & Adoption"),
    ("landscape",   "🌐", "Frontier Labs & AI Landscape"),
]

esc = html.escape


def link(url: str | None, text: str) -> str:
    if url:
        return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'
    return esc(text)


def render_top(item: dict, n: int) -> str:
    also = item.get("also_in") or []
    also_html = f' <span class="also">also in {esc(", ".join(also))}</span>' if also else ""
    read = (f'<a href="{esc(item["url"])}" target="_blank" rel="noopener" class="read-more">Read more →</a>'
            if item.get("url") else "")
    return f"""
        <article class="top-card">
          <div class="top-num">0{n}</div>
          <div class="top-body">
            <div class="card-source">{esc(item.get("source", ""))}{also_html}</div>
            <h3 class="top-title">{link(item.get("url"), item["title"])}</h3>
            <p class="what">{esc(item.get("summary", ""))}</p>
            <p class="why"><span class="why-label">why it matters</span>{esc(item.get("why", ""))}</p>
            {read}
          </div>
        </article>"""


def render_card(item: dict) -> str:
    also = item.get("also_in") or []
    also_html = f' <span class="also">· also in {esc(", ".join(also))}</span>' if also else ""
    why = f'<p class="card-why">{esc(item["why"])}</p>' if item.get("why") else ""
    read = (f'<a href="{esc(item["url"])}" target="_blank" rel="noopener" class="read-more">Read more →</a>'
            if item.get("url") else "")
    return f"""
          <article class="card">
            <div class="card-source">{esc(item.get("source", ""))}{also_html}</div>
            <h3 class="card-title">{link(item.get("url"), item["title"])}</h3>
            <p class="card-summary">{esc(item.get("summary", ""))}</p>
            {why}
            {read}
          </article>"""


def render_try(t: dict | None) -> str:
    if not t:
        return ""
    return f"""
      <section class="try">
        <div class="try-label">🛠️ try this</div>
        <h3>{link(t.get("url"), t["title"])}</h3>
        <p>{esc(t.get("how", ""))}</p>
      </section>"""


def recent_archive(current: str, limit: int = 7) -> str:
    if not ARCHIVE.exists():
        return ""
    days = sorted((p.stem for p in ARCHIVE.glob("*.json")), reverse=True)
    days = [d for d in days if d != current][:limit]
    if not days:
        return ""
    links = " · ".join(f'<a href="archive/{d}.json">{d}</a>' for d in days)
    return f'<div class="archive">past days (raw data): {links}</div>'


def build(d: dict) -> str:
    date = datetime.date.fromisoformat(d["date"])
    date_str = date.strftime("%B %-d, %Y")
    day_str = date.strftime("%A")

    top = d.get("top") or []
    sections = d.get("sections") or {}
    n_stories = len(top) + sum(len(sections.get(k, [])) for k, _, _ in SECTIONS)
    stats = d.get("stats") or {}
    scanned = stats.get("newsletters_scanned")

    top_html = "".join(render_top(it, i + 1) for i, it in enumerate(top))
    top_block = f"""
      <section class="topic-section">
        <h2 class="topic-heading">🔝 Top stories</h2>
        <div class="top-list">{top_html}
        </div>
      </section>""" if top else ""

    sec_html = ""
    for key, icon, heading in SECTIONS:
        items = sections.get(key) or []
        if not items:
            continue
        cards = "".join(render_card(it) for it in items)
        sec_html += f"""
      <section class="topic-section">
        <h2 class="topic-heading">{icon} {esc(heading)}</h2>
        <div class="cards-grid">{cards}
        </div>
      </section>"""

    slow = (f'<p class="slow">{esc(d["note"])}</p>' if d.get("note") else "")
    meta = f"{day_str}, {date_str} · {n_stories} stories"
    if scanned:
        meta += f" · {scanned} newsletters read"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Daily AI Digest — {date_str}</title>
  <link rel="icon" type="image/png" href="favicon.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    /* dpnation brand: Ink #0D0D0D, Canvas #F7F6F3, Mist #EBEBEB, Smoke #7A7A7A, Spark #FF8C69 */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: #F7F6F3; color: #0D0D0D; line-height: 1.6; }}
    a {{ color: inherit; }}

    header {{ background: #0D0D0D; color: #FFFFFF; padding: 2.25rem 2rem 1.75rem; border-bottom: 3px solid #FF8C69; }}
    .header-inner {{ max-width: 1100px; margin: 0 auto; }}
    .header-eyebrow {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.72rem; font-weight: 500;
                       letter-spacing: 0.14em; text-transform: lowercase; color: #FF8C69; margin-bottom: 0.5rem; }}
    header h1 {{ font-family: "Plus Jakarta Sans", "Inter", sans-serif; font-size: 2rem; font-weight: 800;
                 letter-spacing: -0.01em; margin-bottom: 0.3rem; }}
    .header-date {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.8rem; color: #EBEBEB; }}

    main {{ max-width: 1100px; margin: 2.25rem auto; padding: 0 1.5rem; }}
    .slow {{ font-size: 0.9rem; color: #7A7A7A; margin-bottom: 1.5rem; }}

    .topic-section {{ margin-bottom: 2.75rem; }}
    .topic-heading {{ font-family: "Plus Jakarta Sans", "Inter", sans-serif; font-size: 1.05rem; font-weight: 700;
                      border-bottom: 1px solid #EBEBEB; padding-bottom: 0.5rem; margin-bottom: 1.1rem; }}

    /* Top stories */
    .top-list {{ display: flex; flex-direction: column; gap: 1rem; }}
    .top-card {{ background: #FFFFFF; border: 1px solid #EBEBEB; border-left: 4px solid #FF8C69; border-radius: 8px;
                 padding: 1.25rem 1.4rem; display: flex; gap: 1.2rem; }}
    .top-num {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 1.4rem; font-weight: 500;
                color: #FF8C69; line-height: 1.2; }}
    .top-body {{ display: flex; flex-direction: column; gap: 0.45rem; flex: 1; }}
    .top-title {{ font-family: "Plus Jakarta Sans", "Inter", sans-serif; font-size: 1.15rem; font-weight: 700; line-height: 1.35; }}
    .top-title a, .card-title a, .try h3 a {{ text-decoration: none; }}
    .top-title a:hover, .card-title a:hover, .try h3 a:hover {{ color: #FF8C69; }}
    .what {{ font-size: 0.92rem; }}
    .why {{ font-size: 0.88rem; color: #3A3A3A; background: #F7F6F3; border-radius: 6px; padding: 0.55rem 0.75rem; }}
    .why-label, .try-label {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.66rem; letter-spacing: 0.08em;
                  text-transform: lowercase; color: #FF8C69; display: block; margin-bottom: 0.1rem; }}

    /* Try this */
    .try {{ background: #0D0D0D; color: #FFFFFF; border-radius: 8px; padding: 1.2rem 1.4rem; margin-bottom: 2.75rem; }}
    .try h3 {{ font-family: "Plus Jakarta Sans", "Inter", sans-serif; font-size: 1.02rem; margin-bottom: 0.3rem; }}
    .try p {{ font-size: 0.9rem; color: #EBEBEB; }}

    /* Cards */
    .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
    .card {{ background: #FFFFFF; border-radius: 8px; padding: 1.15rem 1.3rem 1rem; border: 1px solid #EBEBEB;
             display: flex; flex-direction: column; gap: 0.45rem;
             transition: box-shadow 0.15s ease, transform 0.15s ease, border-color 0.15s ease; }}
    .card:hover {{ box-shadow: 0 6px 18px rgba(13,13,13,0.08); border-color: #FF8C69; transform: translateY(-1px); }}
    .card-source {{ font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 0.68rem; font-weight: 500;
                    letter-spacing: 0.08em; text-transform: lowercase; color: #7A7A7A; }}
    .also {{ color: #A0A0A0; }}
    .card-title {{ font-family: "Plus Jakarta Sans", "Inter", sans-serif; font-size: 0.97rem; font-weight: 700; line-height: 1.4; }}
    .card-summary {{ font-size: 0.85rem; color: #4A4A4A; line-height: 1.55; }}
    .card-why {{ font-size: 0.82rem; color: #7A7A7A; line-height: 1.5; flex: 1; border-left: 2px solid #FF8C69; padding-left: 0.6rem; }}
    .read-more {{ font-size: 0.8rem; font-weight: 600; color: #0D0D0D; text-decoration: none;
                  border-bottom: 2px solid #FF8C69; align-self: flex-start; margin-top: auto; }}
    .read-more:hover {{ color: #FF8C69; }}

    footer {{ text-align: center; padding: 2rem 1rem; font-family: "JetBrains Mono", ui-monospace, monospace;
              font-size: 0.75rem; color: #7A7A7A; border-top: 1px solid #EBEBEB; margin-top: 1rem; }}
    footer a {{ color: #0D0D0D; text-decoration: none; border-bottom: 1px solid #FF8C69; }}
    .archive {{ margin-top: 0.6rem; }}

    @media (max-width: 600px) {{
      .cards-grid {{ grid-template-columns: 1fr; }}
      header h1 {{ font-size: 1.5rem; }}
      .top-card {{ flex-direction: column; gap: 0.4rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="header-eyebrow">dpnation · ai for pmm workflows</div>
      <h1>Daily AI Digest</h1>
      <div class="header-date">{meta}</div>
    </div>
  </header>

  <main>
    {slow}{top_block}{render_try(d.get("try_this"))}{sec_html}
  </main>

  <footer>
    curated daily by <a href="https://dpnation.com" target="_blank" rel="noopener">dpnation</a> · {date_str}
    {recent_archive(d["date"])}
  </footer>
</body>
</html>
"""


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    ARCHIVE.mkdir(exist_ok=True)
    shutil.copyfile(DATA, ARCHIVE / f"{d['date']}.json")
    OUT.write_text(build(d), encoding="utf-8")
    print(f"Built {OUT.name} for {d['date']}")


if __name__ == "__main__":
    main()
