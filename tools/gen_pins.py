"""Generate vertical 2:3 (1000x1500) Pinterest infographics for hollandexpatguide.com.

Every figure here is taken from the site's own published guides — see FIGURE SOURCES
comments per panel. If an article's numbers change, update them here too.
"""
import os

OUT_DIR = "/Users/trymtofte/website/expat-site/images"

W, H = 1000, 1500

# Site design tokens (mirrors expat-site/styles.css :root)
BG        = "#fafaf8"
CARD      = "#ffffff"
TEXT      = "#1a1a1a"
MUTED     = "#666666"
ACCENT    = "#1a5276"
ACCENT_LT = "#e8f0f7"
BORDER    = "#e0e0d8"
T_HOUSING = "#4a235a"
T_TAXES   = "#7d3c1a"
T_IDENT   = "#1a4a5a"
T_HEALTH  = "#1a6644"

SERIF = "Georgia, 'Times New Roman', serif"
UI    = "system-ui, -apple-system, sans-serif"

SITE_LABEL = "hollandexpatguide.com"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def wrap(text, max_chars):
    """Greedy word wrap -> list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


TITLE_SIZE = 56
TITLE_LEAD = 64


def header(title_lines, kicker, accent=ACCENT):
    """Big readable header — must survive Pinterest's small feed thumbnail.

    Height grows with the number of title lines so a 3-line title can never
    collide with the kicker. Returns (svg_fragment, header_height)."""
    top_pad, bottom_pad = 104, 74
    h = top_pad + TITLE_LEAD * (len(title_lines) - 1) + bottom_pad
    p = [f'<rect width="{W}" height="{h}" fill="{accent}"/>']
    y = top_pad
    for ln in title_lines:
        p.append(f'<text x="56" y="{y}" fill="#ffffff" font-family="{SERIF}" '
                 f'font-size="{TITLE_SIZE}" font-weight="700">{esc(ln)}</text>')
        y += TITLE_LEAD
    p.append(f'<text x="56" y="{h-26}" fill="#bcd4e6" font-family="{UI}" '
             f'font-size="24">{esc(kicker)}</text>')
    return "".join(p), h


def footer(note, y0=None):
    y0 = y0 if y0 is not None else H - 96
    return (f'<rect y="{y0}" width="{W}" height="{H-y0}" fill="{ACCENT}"/>'
            f'<text x="56" y="{y0+40}" fill="#ffffff" font-family="{UI}" font-size="20" '
            f'font-weight="600">{esc(note)}</text>'
            f'<text x="56" y="{y0+72}" fill="#bcd4e6" font-family="{UI}" '
            f'font-size="19">{esc(SITE_LABEL)}</text>')


def svg(body):
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>{body}</svg>')


def write(name, content):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote images/{name}")


# ---------------------------------------------------------------- pin 1
def pin_arrival():
    """FIGURE SOURCES: registering-at-gemeente-netherlands (5-day rule, BSN issue
    time), digid-expats-what-it-is-how-to-get (activation letter ~5 business days),
    health-insurance-netherlands-expats-complete-guide (4-month deadline + penalty),
    open-bank-account-netherlands-without-bsn."""
    steps = [
        ("1", "Register at your gemeente",
         "Within 5 days of arriving, if you're staying longer than 4 months.", T_IDENT),
        ("2", "Get your BSN",
         "Issued at the appointment, or mailed within 5-10 business days.", T_IDENT),
        ("3", "Activate DigiD",
         "Apply once you have a BSN; the activation letter arrives in about 5 business days.", T_IDENT),
        ("4", "Open a bank account",
         "Most Dutch banks want a BSN first. Some neobanks will open without one.", ACCENT),
        ("5", "Take out health insurance",
         "Mandatory within 4 months of arrival. Miss it and you're enrolled retroactively, with a penalty.", T_HEALTH),
    ]
    hdr, hh = header(["Your first weeks", "in the Netherlands"],
                     "The 5 things with actual deadlines")
    p = [hdr]
    FOOT = H - 96
    y = hh + 46
    ROW = (FOOT - 40 - y) // len(steps)
    # connecting spine
    p.append(f'<line x1="104" y1="{y+40}" x2="104" y2="{y + ROW*(len(steps)-1) + 40}" '
             f'stroke="{BORDER}" stroke-width="3"/>')
    for num, title, body, colour in steps:
        p.append(f'<circle cx="104" cy="{y+40}" r="34" fill="{colour}"/>')
        p.append(f'<text x="104" y="{y+52}" fill="#ffffff" font-family="{SERIF}" '
                 f'font-size="34" font-weight="700" text-anchor="middle">{num}</text>')
        p.append(f'<text x="168" y="{y+34}" fill="{TEXT}" font-family="{SERIF}" '
                 f'font-size="34" font-weight="700">{esc(title)}</text>')
        ty = y + 74
        for ln in wrap(body, 46):
            p.append(f'<text x="168" y="{ty}" fill="{MUTED}" font-family="{UI}" '
                     f'font-size="23">{esc(ln)}</text>')
            ty += 32
        y += ROW
    p.append(footer("Deadlines are strict — check each guide before you arrive."))
    return svg("".join(p))


# ---------------------------------------------------------------- pin 2
def pin_cost():
    """FIGURE SOURCES: cost-of-living-netherlands-expats-2026 — one-bedroom monthly
    rent ranges per city, plus the monthly essentials block."""
    cities = [
        ("Amsterdam (central)", 1800, 2400),
        ("Utrecht",             1400, 1900),
        ("The Hague",           1300, 1800),
        ("Amsterdam (outer)",   1200, 1700),
        ("Rotterdam",           1100, 1500),
        ("Eindhoven",           1000, 1500),
    ]
    lo_all = min(c[1] for c in cities)
    hi_all = max(c[2] for c in cities)
    BAR_X, BAR_W = 430, 400

    hdr, hh = header(["What it costs to", "live in the", "Netherlands"],
                     "One-bedroom rent per month, 2026", accent=T_HOUSING)
    p = [hdr]
    p.append(f'<text x="56" y="{hh+52}" fill="{TEXT}" font-family="{UI}" font-size="22" '
             f'font-weight="700" letter-spacing="1.5">FURNISHED ONE-BEDROOM, PER MONTH</text>')
    y = hh + 88
    ROW = 92
    for name, lo, hi in cities:
        mid = y + 34
        p.append(f'<text x="404" y="{mid+2}" fill="{TEXT}" font-family="{SERIF}" '
                 f'font-size="27" text-anchor="end">{esc(name)}</text>')
        x0 = BAR_X + (lo - lo_all) / (hi_all - lo_all) * BAR_W
        x1 = BAR_X + (hi - lo_all) / (hi_all - lo_all) * BAR_W
        p.append(f'<rect x="{BAR_X}" y="{mid-11}" width="{BAR_W}" height="22" rx="4" fill="{BORDER}" opacity="0.5"/>')
        p.append(f'<rect x="{x0:.0f}" y="{mid-11}" width="{max(10,x1-x0):.0f}" height="22" rx="4" fill="{T_HOUSING}"/>')
        p.append(f'<text x="{BAR_X+BAR_W+16}" y="{mid+8}" fill="{TEXT}" font-family="{UI}" '
                 f'font-size="22" font-weight="700">&#8364;{lo:,}-{hi:,}</text>'.replace(",", "."))
        y += ROW

    # essentials card — sized to meet the footer
    cy = y + 26
    card_h = (H - 96) - 34 - cy
    p.append(f'<rect x="56" y="{cy}" width="{W-112}" height="{card_h}" fill="{CARD}" stroke="{BORDER}" stroke-width="2"/>')
    p.append(f'<text x="88" y="{cy+58}" fill="{TEXT}" font-family="{UI}" font-size="22" '
             f'font-weight="700" letter-spacing="1.5">EVERY MONTH, ON TOP OF RENT</text>')
    items = [
        ("Health insurance (per adult)", "€135-165"),
        ("Gas, electricity & water", "€120-180"),
        ("Groceries (one adult)", "€250-400"),
        ("Fibre internet", "€40-55"),
        ("Mobile plan", "€15-30"),
        ("Regional transit pass", "€100-140"),
    ]
    iy = cy + 116
    step = (card_h - 176) // len(items)
    for label, val in items:
        p.append(f'<text x="88" y="{iy}" fill="{MUTED}" font-family="{UI}" font-size="25">{esc(label)}</text>')
        p.append(f'<text x="{W-88}" y="{iy}" fill="{TEXT}" font-family="{UI}" font-size="25" '
                 f'font-weight="700" text-anchor="end">{esc(val)}</text>')
        p.append(f'<line x1="88" y1="{iy+16}" x2="{W-88}" y2="{iy+16}" stroke="{BORDER}" stroke-width="1"/>')
        iy += step
    p.append(f'<text x="88" y="{iy+18}" fill="{MUTED}" font-family="{UI}" font-size="20" '
             f'font-style="italic">Plus a &#8364;385 annual health insurance deductible.</text>')
    p.append(footer("Ranges, not quotes — costs move. Full breakdown on the site."))
    return svg("".join(p))


# ---------------------------------------------------------------- pin 3
def pin_ruling():
    """FIGURE SOURCES: 30-percent-ruling-tapering-2026 — 2024 taper (30/20/10 across
    three 20-month blocks) vs the Belastingplan 2026 structure (30% for 30 months,
    then 25% for 30 months), and the 2026 salary thresholds."""
    BAR_X, BAR_W = 56, W - 112

    hdr, hh = header(["The 30% ruling", "changed again", "in 2026"],
                     "What expats actually get now", accent=T_TAXES)
    p = [hdr]

    def schedule(y, label, blocks, note):
        p.append(f'<text x="56" y="{y}" fill="{TEXT}" font-family="{UI}" font-size="22" '
                 f'font-weight="700" letter-spacing="1.5">{esc(label)}</text>')
        by = y + 26
        x = BAR_X
        for pct, months, shade in blocks:
            w = BAR_W * (months / 60)
            p.append(f'<rect x="{x:.0f}" y="{by}" width="{w:.0f}" height="104" fill="{shade}"/>')
            p.append(f'<text x="{x + w/2:.0f}" y="{by+50}" fill="#ffffff" font-family="{SERIF}" '
                     f'font-size="42" font-weight="700" text-anchor="middle">{pct}%</text>')
            p.append(f'<text x="{x + w/2:.0f}" y="{by+82}" fill="#ffffff" font-family="{UI}" '
                     f'font-size="21" text-anchor="middle" opacity="0.85">{months} months</text>')
            x += w
        p.append(f'<text x="56" y="{by+146}" fill="{MUTED}" font-family="{UI}" font-size="23">{esc(note)}</text>')

    y1 = hh + 56
    schedule(y1, "IF YOU APPLIED UNDER THE 2024 RULES",
             [(30, 20, "#a8571f"), (20, 20, "#c1834f"), (10, 20, "#dcb494")],
             "Averaged 20% across the five years.")

    y2 = y1 + 264
    schedule(y2, "IF YOU APPLY FROM 1 JANUARY 2026",
             [(30, 30, T_TAXES), (25, 30, "#a8571f")],
             "Averages 27.5% — the second half is no longer 20% then 10%.")

    # takeaway card
    cy = y2 + 218
    p.append(f'<rect x="56" y="{cy}" width="{W-112}" height="196" fill="{ACCENT_LT}" stroke="{BORDER}" stroke-width="2"/>')
    ty = cy + 62
    for ln in wrap("Already on the 2024 schedule? You stay on it unless you switch — "
                   "which is generally worth doing, and your payroll provider handles it.", 50):
        p.append(f'<text x="88" y="{ty}" fill="{TEXT}" font-family="{SERIF}" font-size="28">{esc(ln)}</text>')
        ty += 40

    # thresholds
    ty = cy + 268
    p.append(f'<text x="56" y="{ty}" fill="{TEXT}" font-family="{UI}" font-size="22" '
             f'font-weight="700" letter-spacing="1.5">2026 MINIMUM SALARY TO QUALIFY</text>')
    ty += 58
    for label, val in [("Standard", "€46.107"), ("Under 30 with a master's", "€35.048")]:
        p.append(f'<text x="56" y="{ty}" fill="{MUTED}" font-family="{UI}" font-size="25">{esc(label)}</text>')
        p.append(f'<text x="{W-56}" y="{ty}" fill="{TEXT}" font-family="{UI}" font-size="27" '
                 f'font-weight="700" text-anchor="end">{esc(val)}</text>')
        p.append(f'<line x1="56" y1="{ty+18}" x2="{W-56}" y2="{ty+18}" stroke="{BORDER}" stroke-width="1"/>')
        ty += 54
    p.append(f'<text x="56" y="{ty+8}" fill="{MUTED}" font-family="{UI}" font-size="20" '
             f'font-style="italic">Taxable salary after the 30% is deducted.</text>')

    p.append(footer("Thresholds are indexed yearly — verify before you rely on them."))
    return svg("".join(p))


def eur(n):
    """Dutch thousands separator: 1800 -> €1.800"""
    return "€" + f"{n:,}".replace(",", ".")


def chips(labels, y, fill, stroke, ink, size=22, x0=56):
    """Pill row that wraps within the canvas. Returns (svg, y_after)."""
    out, x, cy, h = [], x0, y, 50
    for label in labels:
        w = 22 + len(label) * (size * 0.573)
        if x + w > W - 56:
            x, cy = x0, cy + h + 12
        out.append(f'<rect x="{x:.0f}" y="{cy}" width="{w:.0f}" height="{h}" rx="25" '
                   f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<text x="{x + w/2:.0f}" y="{cy + 33}" fill="{ink}" font-family="{UI}" '
                   f'font-size="{size}" text-anchor="middle">{esc(label)}</text>')
        x += w + 12
    return "".join(out), cy + h


def stat_card(x, y, w, h, value, label, colour):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{colour}"/>'
            f'<text x="{x + w/2:.0f}" y="{y + h*0.52:.0f}" fill="#ffffff" font-family="{SERIF}" '
            f'font-size="52" font-weight="700" text-anchor="middle">{esc(value)}</text>'
            f'<text x="{x + w/2:.0f}" y="{y + h*0.78:.0f}" fill="#ffffff" font-family="{UI}" '
            f'font-size="21" text-anchor="middle" opacity="0.88">{esc(label)}</text>')


# ---------------------------------------------------------------- pin 4
def pin_health():
    """FIGURE SOURCES: health-insurance-netherlands-expats-complete-guide — basic
    premium range, mandatory eigen risico, voluntary deductible ceiling, zorgtoeslag
    income thresholds, and the four-month registration deadline."""
    hdr, hh = header(["Dutch health", "insurance: what", "you actually pay"],
                     "Mandatory basics, 2026", accent=T_HEALTH)
    p = [hdr]
    FOOT = H - 96

    y = hh + 48
    gap, cw = 24, (W - 112 - 24) / 2
    p.append(stat_card(56, y, cw, 196, "€135-165", "basic premium, per adult, per month", T_HEALTH))
    p.append(stat_card(56 + cw + gap, y, cw, 196, "€385", "mandatory annual deductible", "#155238"))

    # deadline band
    y += 196 + 36
    p.append(f'<rect x="56" y="{y}" width="{W-112}" height="116" fill="#fdf0e6" stroke="#e0c3a2" stroke-width="2"/>')
    p.append(f'<text x="88" y="{y+48}" fill="{T_TAXES}" font-family="{UI}" font-size="22" '
             f'font-weight="700" letter-spacing="1.2">THE DEADLINE THAT CARRIES A PENALTY</text>')
    p.append(f'<text x="88" y="{y+86}" fill="{TEXT}" font-family="{SERIF}" font-size="27">'
             f'Take out cover within 4 months of arriving.</text>')

    # what the standardised basic package covers — identical at every insurer
    y += 116 + 40
    p.append(f'<text x="56" y="{y}" fill="{TEXT}" font-family="{UI}" font-size="21" '
             f'font-weight="700" letter-spacing="1.4">BASIC COVER, IDENTICAL AT EVERY INSURER</text>')
    y += 30
    frag, y = chips(["GP visits", "Hospital treatment", "Prescriptions",
                     "Mental healthcare", "Maternity care", "Physiotherapy (limited)"],
                    y, "#eaf3ee", "#bcd9c8", T_HEALTH)
    p.append(frag)
    y += 40

    # detail rows, inside a card so the spacing reads as padding not drift
    card_h = (FOOT - 34) - y
    p.append(f'<rect x="56" y="{y}" width="{W-112}" height="{card_h}" fill="{CARD}" '
             f'stroke="{BORDER}" stroke-width="2"/>')
    p.append(f'<text x="88" y="{y+54}" fill="{TEXT}" font-family="{UI}" font-size="21" '
             f'font-weight="700" letter-spacing="1.4">THE REST OF THE NUMBERS</text>')
    rows = [
        ("Voluntary deductible, for a lower premium", "up to " + eur(885)),
        ("Supplementary dental cover", "€15-30 / month"),
        ("Zorgtoeslag limit, single (approx.)", eur(37000)),
        ("Zorgtoeslag limit, couple (approx.)", eur(47000)),
    ]
    ry = y + 116
    step = min(64, (card_h - 150) // len(rows))
    for label, val in rows:
        p.append(f'<text x="88" y="{ry}" fill="{MUTED}" font-family="{UI}" font-size="24">{esc(label)}</text>')
        p.append(f'<text x="{W-88}" y="{ry}" fill="{TEXT}" font-family="{UI}" font-size="25" '
                 f'font-weight="700" text-anchor="end">{esc(val)}</text>')
        p.append(f'<line x1="88" y1="{ry+18}" x2="{W-88}" y2="{ry+18}" stroke="{BORDER}" stroke-width="1"/>')
        ry += step

    p.append(footer("Premiums differ by insurer — compare before you sign."))
    return svg("".join(p))


# ---------------------------------------------------------------- pin 5
def pin_box3():
    """FIGURE SOURCES: box-3-wealth-tax-explained — 2026 deemed-return percentages
    per asset class, the 36% rate, the heffingsvrij vermogen, and the worked example."""
    hdr, hh = header(["Box 3: how Dutch", "wealth tax works", "in 2026"],
                     "You're taxed on an assumed return, not your real one", accent=T_TAXES)
    p = [hdr]

    y = hh + 48
    p.append(f'<text x="56" y="{y}" fill="{TEXT}" font-family="{UI}" font-size="22" '
             f'font-weight="700" letter-spacing="1.4">ASSUMED RETURN, BY ASSET TYPE</text>')
    y += 34
    rates = [("Savings & bank deposits", "1,44%", "#c1834f"),
             ("Investments & other assets", "6,04%", T_TAXES),
             ("Debts (subtracted)", "2,62%", "#9c9c9c")]
    for label, pct, colour in rates:
        p.append(f'<rect x="56" y="{y}" width="{W-112}" height="86" fill="{CARD}" stroke="{BORDER}" stroke-width="2"/>')
        p.append(f'<rect x="56" y="{y}" width="10" height="86" fill="{colour}"/>')
        p.append(f'<text x="92" y="{y+54}" fill="{TEXT}" font-family="{SERIF}" font-size="28">{esc(label)}</text>')
        p.append(f'<text x="{W-88}" y="{y+56}" fill="{colour}" font-family="{SERIF}" font-size="38" '
                 f'font-weight="700" text-anchor="end">{esc(pct)}</text>')
        y += 98

    y += 12
    gap, cw = 24, (W - 112 - 24) / 2
    p.append(stat_card(56, y, cw, 158, "36%", "tax on the assumed return", T_TAXES))
    p.append(stat_card(56 + cw + gap, y, cw, 158, eur(57684), "tax-free, per person", "#5d2e0c"))

    # worked example
    y += 158 + 34
    p.append(f'<rect x="56" y="{y}" width="{W-112}" height="206" fill="{ACCENT_LT}" stroke="{BORDER}" stroke-width="2"/>')
    p.append(f'<text x="88" y="{y+46}" fill="{TEXT}" font-family="{UI}" font-size="21" '
             f'font-weight="700" letter-spacing="1.4">WORKED EXAMPLE</text>')
    ex = [(eur(40000) + " savings + " + eur(100000) + " investments", ""),
          ("Assumed return after the allowance", eur(3910)),
          ("Tax actually owed", eur(1408))]
    ey = y + 92
    for label, val in ex:
        p.append(f'<text x="88" y="{ey}" fill="{MUTED if val else TEXT}" font-family="{UI}" '
                 f'font-size="23">{esc(label)}</text>')
        if val:
            p.append(f'<text x="{W-88}" y="{ey}" fill="{TEXT}" font-family="{UI}" font-size="25" '
                     f'font-weight="700" text-anchor="end">{esc(val)}</text>')
        ey += 44

    # what actually sits in Box 3
    y += 206 + 40
    p.append(f'<text x="56" y="{y}" fill="{TEXT}" font-family="{UI}" font-size="21" '
             f'font-weight="700" letter-spacing="1.4">WHAT COUNTS AS A BOX 3 ASSET</text>')
    frag, y = chips(["Savings", "Stocks & ETFs", "Crypto", "Second homes", "Loans receivable"],
                    y + 26, "#fdf0e6", "#e0c3a2", T_TAXES)
    p.append(frag)
    y += 34
    p.append(f'<text x="56" y="{y}" fill="{MUTED}" font-family="{UI}" font-size="21" '
             f'font-style="italic">Not your primary home, pension, or household possessions.</text>')

    p.append(footer("On the 30% ruling? Foreign assets may fall outside Box 3 entirely."))
    return svg("".join(p))


# ---------------------------------------------------------------- pin 6
def pin_cities():
    """FIGURE SOURCES: best-cities-for-expats-netherlands (positioning per city) and
    cost-of-living-netherlands-expats-2026 (one-bedroom rent ranges)."""
    hdr, hh = header(["Which Dutch city", "should you", "live in?"],
                     "Five cities, honestly compared")
    p = [hdr]
    FOOT = H - 96

    cities = [
        ("Amsterdam", "€1.800-2.400", "Most international, best culture — and the hardest housing market.", ACCENT),
        ("Utrecht", "€1.400-1.900", "Central, walkable, well connected. Amsterdam prices are catching up.", "#1a4a5a"),
        ("The Hague", "€1.300-1.800", "Government, courts and NGOs. Coastal, and quieter than Amsterdam.", "#1a6644"),
        ("Rotterdam", "€1.100-1.500", "Rents 30-40% below Amsterdam. Modern, and long overlooked.", "#4a235a"),
        ("Eindhoven", "€1.000-1.500", "Tech and ASML's Brainport. Best value of the major hubs.", "#7d3c1a"),
    ]

    y = hh + 40
    row = (FOOT - 30 - y) // len(cities)
    for name, rent, blurb, colour in cities:
        p.append(f'<rect x="56" y="{y}" width="{W-112}" height="{row-18}" fill="{CARD}" '
                 f'stroke="{BORDER}" stroke-width="2"/>')
        p.append(f'<rect x="56" y="{y}" width="10" height="{row-18}" fill="{colour}"/>')
        p.append(f'<text x="92" y="{y+52}" fill="{TEXT}" font-family="{SERIF}" font-size="34" '
                 f'font-weight="700">{esc(name)}</text>')
        p.append(f'<text x="{W-88}" y="{y+52}" fill="{colour}" font-family="{UI}" font-size="25" '
                 f'font-weight="700" text-anchor="end">{esc(rent)}</text>')
        ty = y + 92
        for ln in wrap(blurb, 52):
            p.append(f'<text x="92" y="{ty}" fill="{MUTED}" font-family="{UI}" font-size="22">{esc(ln)}</text>')
            ty += 30
        y += row

    p.append(footer("One-bedroom rent, per month. The right pick usually follows the job."))
    return svg("".join(p))


if __name__ == "__main__":
    write("pin-first-weeks-netherlands.svg", pin_arrival())
    write("pin-cost-of-living-netherlands.svg", pin_cost())
    write("pin-30-percent-ruling-2026.svg", pin_ruling())
    write("pin-health-insurance-netherlands.svg", pin_health())
    write("pin-box-3-wealth-tax.svg", pin_box3())
    write("pin-best-dutch-cities.svg", pin_cities())
    print("done")
