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
SITE = "https://www.hollandexpatguide.com"
ADS_CLIENT = "ca-pub-4371405280920860"
PUBLISHER = "Expat in Holland"
# Date the guides were last checked against the official sources below.
# Bump this (or set a per-article "reviewed" field) when content is re-verified.
REVIEWED_DEFAULT = "2026-06-14"

# Authoritative sources shown at the foot of each guide. Verifiability is the
# single biggest "is this content trustworthy" signal for YMYL topics, so every
# guide cites the official Dutch government / regulator pages it is based on.
# A per-article "sources" field in the data overrides this mapping.
ART_SOURCES = {
    "best-bank-accounts-expats-netherlands-2026": [
        ("Dutch Banking Association (NVB) — English", "https://www.nvb.nl/"),
        ("De Nederlandsche Bank — central bank", "https://www.dnb.nl/en/"),
        ("Government.nl — banking", "https://www.government.nl/topics/new-in-the-netherlands"),
    ],
    "abn-amro-vs-ing-vs-rabobank": [
        ("ABN AMRO — personal banking (English)", "https://www.abnamro.nl/en/personal/index.html"),
        ("ING Netherlands", "https://www.ing.nl/"),
        ("Rabobank", "https://www.rabobank.nl/"),
    ],
    "open-bank-account-netherlands-without-bsn": [
        ("Government.nl — citizen service number (BSN)", "https://www.government.nl/topics/personal-data/citizen-service-number-bsn"),
        ("De Nederlandsche Bank — central bank", "https://www.dnb.nl/en/"),
        ("bunq — Dutch IBAN account", "https://www.bunq.com/"),
    ],
    "bunq-n26-revolut-netherlands": [
        ("bunq", "https://www.bunq.com/"),
        ("N26", "https://n26.com/en-eu"),
        ("Revolut", "https://www.revolut.com/"),
    ],
    "health-insurance-netherlands-expats-complete-guide": [
        ("Zorgverzekeringslijn — official help line (English)", "https://www.zorgverzekeringslijn.nl/english/"),
        ("Government.nl — health insurance", "https://www.government.nl/topics/health-insurance"),
        ("Zorgwijzer — compare insurers (English)", "https://www.zorgwijzer.nl/zorgvergelijker/english"),
    ],
    "30-percent-ruling-explained": [
        ("Belastingdienst — Tax Authority (English)", "https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/individuals"),
        ("Government.nl — income tax", "https://www.government.nl/topics/income-tax"),
        ("IND — coming to work in the Netherlands", "https://ind.nl/en"),
    ],
    "renting-apartment-amsterdam-expat": [
        ("Government.nl — housing", "https://www.government.nl/topics/housing"),
        ("Huurcommissie — Rent Tribunal (English)", "https://www.huurcommissie.nl/"),
        ("I amsterdam — official city guide", "https://www.iamsterdam.com/en"),
    ],
    "digid-expats-what-it-is-how-to-get": [
        ("DigiD — official site (English)", "https://www.digid.nl/en"),
        ("Logius — DigiD service owner", "https://www.logius.nl/diensten/digid"),
    ],
    "bsn-number-netherlands-how-to-get": [
        ("Government.nl — citizen service number (BSN)", "https://www.government.nl/topics/personal-data/citizen-service-number-bsn"),
        ("Government.nl — Personal Records Database (BRP)", "https://www.government.nl/topics/personal-data/personal-records-database-brp"),
    ],
    "filing-taxes-expat-netherlands-belastingdienst": [
        ("Belastingdienst — Tax Authority (English)", "https://www.belastingdienst.nl/wps/wcm/connect/en/home/home"),
        ("Government.nl — income tax", "https://www.government.nl/topics/income-tax"),
    ],
    "best-mobile-plans-netherlands-expats": [
        ("ACM ConsuWijzer — consumer authority", "https://www.consuwijzer.nl/"),
        ("Authority for Consumers & Markets (ACM)", "https://www.acm.nl/en"),
    ],
    "dutch-health-insurance-vs-private-insurance": [
        ("Zorgverzekeringslijn — official help line (English)", "https://www.zorgverzekeringslijn.nl/english/"),
        ("Government.nl — health insurance", "https://www.government.nl/topics/health-insurance"),
    ],
    "cost-of-living-netherlands-expats-2026": [
        ("Statistics Netherlands (CBS) — English", "https://www.cbs.nl/en-gb"),
        ("Nibud — National Institute for Family Finance", "https://www.nibud.nl/"),
    ],
    "exchange-foreign-driving-license-netherlands": [
        ("RDW — vehicle authority (English)", "https://www.rdw.nl/particulier"),
        ("Government.nl — driving licence", "https://www.government.nl/topics/driving-licence"),
    ],
    "internet-providers-netherlands-compared": [
        ("ACM ConsuWijzer — consumer authority", "https://www.consuwijzer.nl/"),
        ("Authority for Consumers & Markets (ACM)", "https://www.acm.nl/en"),
    ],
    "energy-providers-netherlands-compared": [
        ("ACM ConsuWijzer — consumer authority", "https://www.consuwijzer.nl/"),
        ("Authority for Consumers & Markets (ACM)", "https://www.acm.nl/en"),
    ],
    "30-percent-ruling-tapering-2026": [
        ("Belastingdienst — Tax Authority (English)", "https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/individuals"),
        ("Government.nl — income tax", "https://www.government.nl/topics/income-tax"),
    ],
    "box-3-wealth-tax-explained": [
        ("Belastingdienst — Tax Authority (English)", "https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/individuals"),
        ("Government.nl — income tax", "https://www.government.nl/topics/income-tax"),
    ],
    "mortgage-as-expat-netherlands": [
        ("Government.nl — housing", "https://www.government.nl/topics/housing"),
        ("AFM — financial markets authority (English)", "https://www.afm.nl/en"),
        ("Nibud — National Institute for Family Finance", "https://www.nibud.nl/"),
    ],
    "kinderopvangtoeslag-explained": [
        ("Government.nl — childcare benefit", "https://www.government.nl/topics/childcare/childcare-benefit"),
        ("Belastingdienst Toeslagen — benefits", "https://www.belastingdienst.nl/wps/wcm/connect/nl/toeslagen/toeslagen"),
    ],
    "best-cities-for-expats-netherlands": [
        ("Statistics Netherlands (CBS) — English", "https://www.cbs.nl/en-gb"),
        ("Government.nl — new in the Netherlands", "https://www.government.nl/topics/new-in-the-netherlands"),
    ],
    "registering-at-gemeente-netherlands": [
        ("Government.nl — Personal Records Database (BRP)", "https://www.government.nl/topics/personal-data/personal-records-database-brp"),
        ("Government.nl — citizen service number (BSN)", "https://www.government.nl/topics/personal-data/citizen-service-number-bsn"),
    ],
    "inburgering-integration-exam-netherlands": [
        ("Inburgeren.nl — official integration site (DUO)", "https://www.inburgeren.nl/"),
        ("DUO — Education Executive Agency", "https://duo.nl/particulier/"),
        ("Government.nl — new in the Netherlands", "https://www.government.nl/topics/new-in-the-netherlands"),
    ],
    "zzp-freelancer-registration-netherlands-expats": [
        ("KVK — Chamber of Commerce (English)", "https://www.kvk.nl/en/"),
        ("Business.gov.nl — government for entrepreneurs", "https://business.gov.nl/"),
        ("Belastingdienst — Tax Authority (English)", "https://www.belastingdienst.nl/wps/wcm/connect/en/home/home"),
    ],
    "parental-leave-netherlands-expats-guide": [
        ("Government.nl — parental leave", "https://business.gov.nl/coming-to-the-netherlands/"),
        ("UWV — Employee Insurance Agency (English)", "https://www.uwv.nl/en"),
        ("SVB — Social Insurance Bank (English)", "https://www.svb.nl/en"),
    ],
    "sick-leave-netherlands-expat-rights": [
        ("UWV — Employee Insurance Agency (English)", "https://www.uwv.nl/en"),
        ("Government.nl — illness and incapacity for work", "https://www.government.nl/topics/incapacity-for-work"),
        ("Netherlands Enterprise Agency — employing staff", "https://business.gov.nl/"),
    ],
    "dutch-citizenship-naturalisation-2026": [
        ("IND — Immigration and Naturalisation Service (English)", "https://ind.nl/en"),
        ("Government.nl — Dutch citizenship", "https://www.government.nl/topics/dutch-citizenship"),
        ("Rijksoverheid — naturalisatie", "https://www.rijksoverheid.nl/onderwerpen/nederlandse-nationaliteit"),
    ],
    "moving-to-netherlands-checklist": [
        ("Government.nl — new in the Netherlands", "https://www.government.nl/topics/new-in-the-netherlands"),
        ("Government.nl — citizen service number (BSN)", "https://www.government.nl/topics/personal-data/citizen-service-number-bsn"),
        ("Zorgverzekeringslijn — Dutch health insurance obligation", "https://www.zorgverzekeringslijn.nl/english/"),
    ],
    "aov-disability-insurance-self-employed-netherlands": [
        ("Netherlands Enterprise Agency — self-employed insurance", "https://business.gov.nl/"),
        ("UWV — Employee Insurance Agency (English)", "https://www.uwv.nl/en"),
        ("KVK — Chamber of Commerce (English)", "https://www.kvk.nl/en/"),
    ],
}

# category id -> human label used in the nav
CATEGORIES = [
    ("Banking", "Banking"),
    ("Healthcare", "Healthcare"),
    ("Insurance", "Insurance"),
    ("Taxes", "Taxes"),
    ("Housing", "Housing"),
    ("Identity", "Identity"),
    ("Telecoms", "Utilities"),
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
    """Give each article an image, in priority order:
      1. explicit `image` field in the data
      2. a per-article photo at images/<id>.jpg
      3. generated cover art at images/hero-<id>.svg — used where no unique
         photo exists, so two guides never share a picture
      4. a rotating pick from the category pool (last resort)."""
    counters = {}
    for a in articles:
        if a.get("image"):
            a["_image"] = a["image"]
            continue
        per_article = f"/images/{a['id']}.jpg"
        if os.path.exists(os.path.join(BASE, per_article.lstrip("/"))):
            a["_image"] = per_article
            continue
        generated = f"/images/hero-{a['id']}.svg"
        if os.path.exists(os.path.join(BASE, generated.lstrip("/"))):
            a["_image"] = generated
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


def re_tags(html):
    """Strip tags for plain-text schema fields."""
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


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
    about_cls = ' class="active"' if active == "about" else ""
    return f"""
<header class="site-header">
  <div class="header-inner">
    <div class="site-brand">
      <div class="site-title"><a href="/">Expat in Holland</a></div>
      <div class="site-tagline">Practical guides for internationals in the Netherlands</div>
    </div>
    <a href="/about.html" class="header-about"{about_cls}>About us</a>
  </div>
</header>
<nav class="main-nav" aria-label="Categories">
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
      <a href="/editorial-standards.html">Editorial standards</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
</footer>
</body>
</html>"""


def card(a):
    label = escape(CAT_LABEL.get(a['category'], a['category']))
    return f"""<article class="article-card cat-{a['category']}">
    <a class="card-image" href="/guides/{a['id']}.html" tabindex="-1" aria-hidden="true"><img src="{img_of(a)}" alt="" loading="lazy" width="600" height="168"></a>
    <div class="card-body">
      <span class="tag tag-{a['category']}">{label}</span>
      <h3 class="card-title"><a href="/guides/{a['id']}.html">{escape(a['title'])}</a></h3>
      <p class="card-excerpt">{escape(a['excerpt'])}</p>
      <div class="card-meta">{escape(a['readTime'])} read</div>
    </div>
  </article>"""


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
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": PUBLISHER,
        "url": SITE + "/",
        "logo": f"{SITE}/images/logo.png",
        "description": ("Independent guides to banking, tax, healthcare, housing and "
                        "Dutch administration for internationals in the Netherlands."),
        "publishingPrinciples": f"{SITE}/editorial-standards.html",
    }
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": PUBLISHER,
        "url": SITE + "/",
    }
    site_ld = (
        f'  <script type="application/ld+json">{json.dumps(org)}</script>\n'
        f'  <script type="application/ld+json">{json.dumps(website)}</script>\n'
    )
    body = head(
        "Expat in Holland — Practical guides for internationals in the Netherlands",
        desc, f"{SITE}/", og_type="website", og_image=img_of(hero), extra=site_ld)
    body += nav("home")
    body += f"""
<div class="container">
  <a class="hero cat-{hero['category']}" href="/guides/{hero['id']}.html">
    <img class="hero-img" src="{img_of(hero)}" alt="" width="1400" height="420">
    <div class="hero-overlay">
      <span class="tag tag-{hero['category']}">{escape(CAT_LABEL.get(hero['category'], hero['category']))}</span>
      <h1 class="hero-title">{escape(hero['title'])}</h1>
      <p class="hero-excerpt">{escape(hero['excerpt'])}</p>
      <span class="hero-read-link">Read the guide &rarr;</span>
    </div>
  </a>
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


def sources_of(a):
    """List of (label, url) authoritative sources for an article."""
    if a.get("sources"):
        return [(s["label"], s["url"]) for s in a["sources"]]
    return ART_SOURCES.get(a["id"], [])


def sources_html(a):
    src = sources_of(a)
    if not src:
        return ""
    items = "\n          ".join(
        f'<li><a href="{escape(url)}" target="_blank" rel="nofollow noopener">{escape(label)}</a></li>'
        for label, url in src)
    return f"""
      <section class="sources" aria-labelledby="sources-h">
        <h2 id="sources-h">Sources &amp; official references</h2>
        <p>This guide is based on the official Dutch government and regulator pages below. We link them so you can verify every figure at source — rules and amounts change, and the source always wins.</p>
        <ul>
          {items}
        </ul>
      </section>"""


def faq_html(a):
    faq = a.get("faq") or []
    if not faq:
        return ""
    rows = "\n        ".join(
        f'<details class="faq-item"><summary>{escape(q["q"])}</summary>'
        f'<div class="faq-a">{q["a"]}</div></details>'
        for q in faq)
    return f"""
      <section class="faq" aria-labelledby="faq-h">
        <h2 id="faq-h">Frequently asked questions</h2>
        {rows}
      </section>"""


def infographic_html(a):
    """Optional vertical 2:3 summary graphic, sized for Pinterest saves.

    Generated by tools/gen_pins.py from figures published in the guides
    themselves — keep the two in sync when a figure changes."""
    ig = a.get("infographic")
    if not ig:
        return ""
    caption = ig.get("caption", "")
    caption_html = f"\n          <figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f"""
      <figure class="infographic">
        <div class="infographic-label">The short version</div>
        <div class="infographic-frame">
          <img src="{escape(ig['src'])}" alt="{escape(ig['alt'])}"
               width="1000" height="1500">{caption_html}
        </div>
      </figure>"""


def body_with_infographic(a):
    """Place the summary graphic straight after the opening paragraph, where a
    reader deciding whether to read on will actually see it — rather than at
    the foot of the article."""
    ig = infographic_html(a)
    if not ig:
        return a["body"]
    split = a["body"].find("</p>")
    if split == -1:
        return a["body"] + ig
    cut = split + len("</p>")
    return a["body"][:cut] + ig + a["body"][cut:]


def byline_html(a):
    reviewed = fmt_date(a.get("reviewed", REVIEWED_DEFAULT))
    return (f'<div class="byline">By the <a href="/about.html">{escape(PUBLISHER)} '
            f'editorial team</a> &nbsp;&middot;&nbsp; '
            f'<a href="/editorial-standards.html">Reviewed {reviewed}</a> against official sources</div>')


def render_article(a, articles):
    canonical = f"{SITE}/guides/{a['id']}.html"
    updated = fmt_date(a["publishedAt"])
    reviewed_iso = a.get("reviewed", REVIEWED_DEFAULT)
    label = CAT_LABEL.get(a["category"], a["category"])

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["excerpt"],
        "image": SITE + img_of(a),
        "datePublished": a["publishedAt"],
        "dateModified": reviewed_iso,
        "articleSection": label,
        "inLanguage": "en",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "author": {
            "@type": "Organization",
            "name": f"{PUBLISHER} editorial team",
            "url": f"{SITE}/about.html",
        },
        "publisher": {
            "@type": "Organization",
            "name": PUBLISHER,
            "url": SITE,
            "logo": {"@type": "ImageObject", "url": f"{SITE}/images/logo.png"},
        },
        "citation": [url for _, url in sources_of(a)],
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
    schemas = [ld, breadcrumb]
    if a.get("faq"):
        schemas.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q["q"],
                 "acceptedAnswer": {"@type": "Answer",
                                    "text": re_tags(q["a"])}}
                for q in a["faq"]
            ],
        })
    ld_script = "".join(
        f'  <script type="application/ld+json">{json.dumps(s)}</script>\n'
        for s in schemas)

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
      <figure class="article-hero">
        <img src="{img_of(a)}" alt="{escape(a['title'])}" width="1400" height="360">
        <span class="tag tag-{a['category']} hero-tag">{escape(label)}</span>
      </figure>
      <div class="article-header">
        <h1 class="article-title">{escape(a['title'])}</h1>
        <div class="article-meta">{escape(a['readTime'])} read &nbsp;&middot;&nbsp; Last updated {updated}</div>
        {byline_html(a)}
      </div>
      <div class="article-body">{body_with_infographic(a)}</div>
{faq_html(a)}
{sources_html(a)}
      <div style="margin-top:40px; padding-top:24px; border-top:1px solid var(--border); font-family:var(--font-ui); font-size:13px; color:var(--text-muted);">
        <strong>Was this guide helpful?</strong> We try to keep all information up to date, but rules change. Always verify critical financial, tax, or legal information directly with the relevant authority before making decisions. See our <a href="/editorial-standards.html">editorial standards</a> for how we research and review these guides.
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
          <li><a href="https://www.government.nl/topics/new-in-the-netherlands" target="_blank" rel="noopener">Government expat guide</a></li>
          <li><a href="https://www.ind.nl/en" target="_blank" rel="noopener">Immigration (IND)</a></li>
          <li><a href="https://www.zorgwijzer.nl/zorgvergelijker/english" target="_blank" rel="noopener">Health insurance compare</a></li>
          <li><a href="https://www.uwv.nl/en" target="_blank" rel="noopener">Work &amp; benefits (UWV)</a></li>
        </ul>
      </div>
    </aside>
  </div>
</div>"""
    body += FOOTER
    return body


def render_editorial_standards():
    canonical = f"{SITE}/editorial-standards.html"
    desc = ("How Expat in Holland researches, sources, reviews and corrects its "
            "guides for internationals in the Netherlands.")
    body = head("Editorial standards — Expat in Holland", desc, canonical)
    body += nav()
    body += f"""
<div class="container">
  <div class="static-page">
    <h1>Editorial standards</h1>
    <p>Expat in Holland publishes guides on money, tax, healthcare, housing and Dutch
    administration — decisions where getting it wrong has real consequences. This page
    explains how we research, write, review and correct our content, so you can judge
    how much to trust it.</p>

    <h2>Who writes these guides</h2>
    <p>Our guides are written and edited by the Expat in Holland editorial team — people
    who have themselves moved to, registered in, and dealt with the bureaucracy of the
    Netherlands as internationals. We write from first-hand experience of the same
    processes our readers are going through: opening a bank account without a BSN,
    registering at the gemeente, choosing a health insurer, applying the 30% ruling.</p>

    <h2>How we research and source</h2>
    <p>Every guide is built on primary, official sources — the Dutch government
    (Rijksoverheid / Government.nl), the Tax Authority (Belastingdienst), the immigration
    service (IND), DUO, the RDW, the consumer authority (ACM/ConsuWijzer) and the relevant
    regulators. We link those sources at the foot of each guide so you can verify every
    figure yourself. Where a figure changes year to year — tax thresholds, the 30% ruling,
    insurance premiums — we cite the source and date rather than asking you to take our
    word for it.</p>

    <h2>Review and "last verified" dates</h2>
    <p>Each guide shows a "Reviewed" date. That is the last time we checked the content
    against the official sources, not just the day it was first published. When Dutch rules
    change — and in tax and immigration they change often — we update the affected guides
    and move the date forward.</p>

    <h2>Independence and how we are funded</h2>
    <p>We are independent. We have no affiliation with any bank, insurer, estate agent,
    energy company or government body, and we do not accept payment to recommend one
    provider over another. The site is funded by advertising, which is kept separate from
    our editorial recommendations. A bank or insurer cannot pay to be rated more highly.</p>

    <h2>Accuracy, limitations and corrections</h2>
    <p>We work hard to be accurate, but our guides are general information, not personalised
    legal, tax or financial advice. For decisions that matter, verify with the official
    source we link or a qualified professional. If you spot something that is wrong or out
    of date, please <a href="/contact.html">tell us</a> — we take corrections seriously and
    will fix genuine errors quickly.</p>
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
        (f"{SITE}/editorial-standards.html", "monthly", "0.5"),
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
    write("editorial-standards.html", render_editorial_standards())
    write("article.html", render_redirect_shim())
    write("sitemap.xml", render_sitemap(articles))
    write("ads.txt", f"google.com, {ADS_CLIENT.replace('ca-','')}, DIRECT, f08c47fec0942fa0\n")
    print("Done.")


if __name__ == "__main__":
    main()
