#!/usr/bin/env python3
"""Static site generator for Expat in Holland.

Reads data/articles.json and pre-renders real HTML so the content is present
in the served page (not injected by JS in the browser). This is what search
engines and the AdSense crawler actually read.

Outputs:
  index.html              homepage with every guide baked in, grouped by category
  guides/<id>.html        one static page per article (full body + Article JSON-LD)
  c/<Category>.html       one static page per category
  sitemap.xml             clean URLs for every page
  article.html            redirect shim: old ?id=X links -> /guides/X.html

Run after editing data/articles.json:
    python3 expat-site/build.py
"""

import json
import os
from datetime import datetime, timezone
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://expatinholland.com"
ADS_CLIENT = "ca-pub-4371405280920860"

# category id -> human label used in the nav
CATEGORIES = [
    ("Banking", "Banking"),
    ("Healthcare", "Healthcare"),
    ("Insurance", "Insurance"),
    ("Taxes", "Taxes"),
    ("Housing", "Housing"),
    ("Identity", "Identity & admin"),
    ("Telecoms", "Phone & internet"),
]
CAT_LABEL = dict(CATEGORIES)

# Themed photos per category (in /images/). Categories with several articles
# get a small pool so the same picture doesn't repeat on every page.
CAT_IMAGE = {
    "Banking": ["/images/cat-banking.jpg"],
    "Healthcare": ["/images/cat-healthcare.jpg"],
    "Insurance": ["/images/cat-insurance.jpg"],
    "Taxes": ["/images/cat-taxes.jpg"],
    "Housing": ["/images/cat-housing.jpg", "/images/cat-housing-2.jpg"],
    "Identity": ["/images/cat-identity.jpg"],
    "Telecoms": ["/images/cat-telecoms.jpg"],
}


def assign_images(articles):
    """Give each article an image: per-article `image` field wins, else a
    deterministic pick from its category pool (rotating for variety)."""
    counters = {}
    for a in articles:
        if a.get("image"):
            a["_image"] = a["image"]
            continue
        pool = CAT_IMAGE.get(a["category"], ["/images/cat-housing.jpg"])
        i = counters.get(a["category"], 0)
        a["_image"] = pool[i % len(pool)]
        counters[a["category"]] = i + 1


def img_of(a):
    return a.get("_image", "/images/cat-housing.jpg")

ADS_SCRIPT = (
    f'  <script async src="https://pagead2.googlesyndication.com/pagead/js/'
    f'adsbygoogle.js?client={ADS_CLIENT}" crossorigin="anonymous"></script>'
)


def fmt_date(iso):
    """2026-04-01 -> 'April 2026'."""
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%B %Y")
    except Exception:
        return iso


def head(title, desc, canonical, *, og_type="website", og_image="", extra=""):
    og_img_tags = ""
    if og_image:
        full = og_image if og_image.startswith("http") else SITE + og_image
        og_img_tags = (f'\n  <meta property="og:image" content="{full}">'
                       f'\n  <meta name="twitter:card" content="summary_large_image">')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">{og_img_tags}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Georgia&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
{ADS_SCRIPT}
{extra}</head>
<body>"""


def nav(active=""):
    links = ['<a href="/"{}>All guides</a>'.format(
        ' class="active"' if active == "home" else "")]
    for cid, label in CATEGORIES:
        cls = ' class="active"' if active == cid else ""
        links.append(f'<a href="/c/{cid}.html"{cls}>{escape(label)}</a>')
    links.append('<a href="/about.html"{}>About</a>'.format(
        ' class="active"' if active == "about" else ""))
    return f"""
<header class="site-header">
  <div class="header-inner">
    <div class="site-title"><a href="/">Expat in Holland</a></div>
    <div class="site-tagline">Practical guides for internationals in the Netherlands</div>
  </div>
</header>
<nav class="main-nav">
  <div class="nav-inner">
    {''.join(links)}
  </div>
</nav>"""


FOOTER = """
<footer class="site-footer">
  <div class="footer-inner">
    <span>&copy; 2026 Expat in Holland. Independent guides, no affiliation with any bank or insurer.</span>
    <div class="footer-links">
      <a href="/about.html">About</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
</footer>
</body>
</html>"""


def card(a):
    label = escape(CAT_LABEL.get(a['category'], a['category']))
    return f"""<div class="article-card">
    <a class="card-image" href="/guides/{a['id']}.html"><img src="{img_of(a)}" alt="{escape(a['title'])}" loading="lazy" width="600" height="168"></a>
    <span class="tag tag-{a['category']}">{label}</span>
    <div class="card-title"><a href="/guides/{a['id']}.html">{escape(a['title'])}</a></div>
    <div class="card-excerpt">{escape(a['excerpt'])}</div>
    <div class="card-meta">{escape(a['readTime'])} read</div>
  </div>"""


def grid_by_category(articles):
    """Render section headings + card grids grouped by category order."""
    html = ""
    for cid, label in CATEGORIES:
        items = [a for a in articles if a["category"] == cid]
        if not items:
            continue
        cards = "\n    ".join(card(a) for a in items)
        html += (f'\n      <h2 class="section-title">{escape(label)}</h2>'
                 f'\n      <div class="article-grid">{cards}</div>')
    return html


def render_index(articles):
    hero = articles[0]
    rest = articles[1:]
    desc = ("Independent, practical guides for expats living in the Netherlands. "
            "Banking, healthcare, taxes, housing, and more — written clearly, "
            "without jargon.")
    body = head(
        "Expat in Holland — Practical guides for internationals in the Netherlands",
        desc, f"{SITE}/", og_type="website", og_image=img_of(hero))
    body += nav("home")
    body += f"""
<div class="hero">
  <figure class="hero-figure"><img src="{img_of(hero)}" alt="{escape(hero['title'])}" width="1400" height="340"></figure>
  <div class="hero-inner">
    <div class="hero-label">{escape(CAT_LABEL.get(hero['category'], hero['category']))}</div>
    <h1 class="hero-title">{escape(hero['title'])}</h1>
    <p class="hero-excerpt">{escape(hero['excerpt'])}</p>
    <div class="hero-meta">{escape(hero['readTime'])} read</div>
    <a href="/guides/{hero['id']}.html" class="hero-read-link">Read the guide &rarr;</a>
  </div>
</div>
<div class="content-area">
  <div class="container">
    <div id="main-grid">{grid_by_category(rest)}
    </div>
  </div>
</div>"""
    body += FOOTER
    return body


def render_category(cid, label, articles):
    items = [a for a in articles if a["category"] == cid]
    desc = (f"{label} guides for expats in the Netherlands — practical, "
            f"independent, and jargon-free.")
    canonical = f"{SITE}/c/{cid}.html"
    body = head(f"{label} — Expat in Holland", desc, canonical)
    body += nav(cid)
    cards = "\n    ".join(card(a) for a in items)
    body += f"""
<div class="content-area">
  <div class="container">
    <h1 class="section-title">{escape(label)}</h1>
    <div class="article-grid">{cards}</div>
  </div>
</div>"""
    body += FOOTER
    return body


def render_article(a, articles):
    canonical = f"{SITE}/guides/{a['id']}.html"
    updated = fmt_date(a["publishedAt"])
    label = CAT_LABEL.get(a["category"], a["category"])

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["excerpt"],
        "image": SITE + img_of(a),
        "datePublished": a["publishedAt"],
        "dateModified": a["publishedAt"],
        "articleSection": label,
        "inLanguage": "en",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "author": {"@type": "Organization", "name": "Expat in Holland"},
        "publisher": {
            "@type": "Organization",
            "name": "Expat in Holland",
            "url": SITE,
        },
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": label,
             "item": f"{SITE}/c/{a['category']}.html"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": canonical},
        ],
    }
    ld_script = (
        f'  <script type="application/ld+json">{json.dumps(ld)}</script>\n'
        f'  <script type="application/ld+json">{json.dumps(breadcrumb)}</script>\n'
    )

    related = [x for x in articles
               if x["category"] == a["category"] and x["id"] != a["id"]][:5]
    related_html = "\n          ".join(
        f'<li><a href="/guides/{x["id"]}.html">{escape(x["title"])}</a></li>'
        for x in related) or "<li>No related guides yet.</li>"

    body = head(f"{a['title']} — Expat in Holland", a["excerpt"], canonical,
                og_type="article", og_image=img_of(a), extra=ld_script)
    body += nav(a["category"])
    body += f"""
<div class="container">
  <div class="page-layout">
    <main>
      <nav class="breadcrumb" aria-label="Breadcrumb" style="font-family:var(--font-ui);font-size:13px;color:var(--text-muted);margin:18px 0 8px;">
        <a href="/">Home</a> &rsaquo; <a href="/c/{a['category']}.html">{escape(label)}</a>
      </nav>
      <figure class="article-hero"><img src="{img_of(a)}" alt="{escape(a['title'])}" width="1400" height="360"></figure>
      <div class="article-header">
        <div class="article-tag"><span class="tag tag-{a['category']}">{escape(label)}</span></div>
        <h1 class="article-title">{escape(a['title'])}</h1>
        <div class="article-meta">{escape(a['readTime'])} read &nbsp;&middot;&nbsp; Last updated {updated}</div>
      </div>
      <div class="article-body">{a['body']}</div>
      <div style="margin-top:40px; padding-top:24px; border-top:1px solid var(--border); font-family:var(--font-ui); font-size:13px; color:var(--text-muted);">
        <strong>Was this guide helpful?</strong> We try to keep all information up to date, but rules change. Always verify critical financial, tax, or legal information directly with the relevant authority before making decisions.
        <br><br><a href="/">&larr; Back to all guides</a>
      </div>
    </main>
    <aside class="sidebar">
      <div class="widget">
        <div class="widget-title">More {escape(label)} guides</div>
        <ul>
          {related_html}
        </ul>
      </div>
      <div class="widget">
        <div class="widget-title">Useful links</div>
        <ul>
          <li><a href="https://www.belastingdienst.nl/wps/wcm/connect/en/home/home" target="_blank" rel="noopener">Tax Authority (English)</a></li>
          <li><a href="https://www.government.nl/topics/living-and-working-in-the-netherlands" target="_blank" rel="noopener">Government expat guide</a></li>
          <li><a href="https://www.ind.nl/en" target="_blank" rel="noopener">Immigration (IND)</a></li>
          <li><a href="https://www.zorgwijzer.nl/zorgvergelijker/english" target="_blank" rel="noopener">Health insurance compare</a></li>
          <li><a href="https://www.werk.nl/en/" target="_blank" rel="noopener">Work in the Netherlands</a></li>
        </ul>
      </div>
    </aside>
  </div>
</div>"""
    body += FOOTER
    return body


def render_redirect_shim():
    """Keep old article.html?id=X links working -> /guides/X.html."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="robots" content="noindex">
  <title>Redirecting…</title>
  <script>
    var id = new URLSearchParams(location.search).get('id');
    location.replace(id ? '/guides/' + id + '.html' : '/');
  </script>
  <link rel="canonical" href="{SITE}/">
</head>
<body>
  <p>Redirecting… If nothing happens, <a href="/">go to the homepage</a>.</p>
</body>
</html>"""


def render_sitemap(articles):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [
        (f"{SITE}/", "weekly", "1.0"),
        (f"{SITE}/about.html", "monthly", "0.5"),
        (f"{SITE}/privacy.html", "monthly", "0.3"),
        (f"{SITE}/contact.html", "monthly", "0.4"),
    ]
    for cid, _ in CATEGORIES:
        if any(a["category"] == cid for a in articles):
            urls.append((f"{SITE}/c/{cid}.html", "weekly", "0.6"))
    for a in articles:
        urls.append((f"{SITE}/guides/{a['id']}.html", "monthly", "0.8"))

    rows = "\n".join(
        f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        for loc, cf, pr in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{rows}\n</urlset>\n")


def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote {path}")


def main():
    with open(os.path.join(BASE, "data", "articles.json"), encoding="utf-8") as f:
        articles = json.load(f)
    print(f"Building {len(articles)} articles…")
    assign_images(articles)

    write("index.html", render_index(articles))
    for a in articles:
        write(f"guides/{a['id']}.html", render_article(a, articles))
    for cid, label in CATEGORIES:
        if any(a["category"] == cid for a in articles):
            write(f"c/{cid}.html", render_category(cid, label, articles))
    write("article.html", render_redirect_shim())
    write("sitemap.xml", render_sitemap(articles))
    print("Done.")


if __name__ == "__main__":
    main()
