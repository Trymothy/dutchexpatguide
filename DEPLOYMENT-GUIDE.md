# Expat in Holland — Deployment Guide

This guide walks you through getting the static site at `/Users/trymtofte/website/expat-site/` from "files on a disk" to "live on the public internet, earning AdSense revenue." Total hands-on time is roughly 60–90 minutes, most of which is waiting for verifications.

## Step 0 — Domain availability (the answer first)

I checked all five domains on the candidate list. Findings (May 2026):

| Domain | Status | Notes |
|---|---|---|
| **expatinholland.com** | **TAKEN** | Active site for Buro Philip van den Hurk, a Dutch financial advisory firm. Not available. |
| **hollandexpat.com** | **TAKEN** | "Holland Verlof Service" — a Dutch rental agency. Not available. |
| **expatguide.nl** | **TAKEN** | Active 15-year-old expat directory. Not available. |
| **dutchexpatguide.com** | **PROBABLY AVAILABLE / PARKED** | Resolves but returns an empty response. No indexed content, no business presence. Most likely registered-but-unused or freshly available. **Verify at a registrar.** |
| **lifeinnl.com** | **PROBABLY AVAILABLE / PARKED** | Same pattern as above — resolves but empty. **Verify at a registrar.** |

### Recommendation, in priority order

1. **`dutchexpatguide.com`** — best brand fit. "Dutch" + "expat" + "guide" reads as authority, hits the keyword stack, generic enough for Pinterest and AdSense to love.
2. **`lifeinnl.com`** — short, memorable, brandable, but weaker SEO (no "expat" or "Netherlands" keyword in the domain itself).

### If both turn out to be unavailable at checkout

Backup list (check in this order at namecheap.com or cloudflare.com/products/registrar/):

- `netherlandsexpat.com`
- `expatlifenl.com`
- `livinginholland.com`
- `hollandexpatlife.com`
- `expatdutch.com`
- `nlexpatguide.com`

Avoid .nl unless you are willing to provide a Dutch address — SIDN requires NL registrants to designate a Dutch contact, which is an extra friction step. `.com` is the right call.

### Where to buy

Use **Cloudflare Registrar** (https://domains.cloudflare.com) — at-cost pricing (~$10.44/yr for .com vs. $13–20 at Namecheap/GoDaddy), zero markup on renewal, free WHOIS privacy. The only catch is they don't take new TLD-launch pre-orders; standard .coms are fine.

Fallback if Cloudflare won't let you register from your jurisdiction: **Namecheap** (~$10.98/yr first year, ~$15/yr renewal). Avoid GoDaddy — their upsell flow is hostile and renewal pricing is opaque.

---

## Step 1 — Buy the domain (5 min)

1. Go to https://domains.cloudflare.com.
2. Sign in (or create a free Cloudflare account).
3. Search `dutchexpatguide.com`. If green-lit, add to cart.
4. Checkout. Choose 1-year registration (you can always renew). Total: ~$10.44.
5. Don't configure DNS yet — we'll come back after GitHub Pages is set up.

If `dutchexpatguide.com` shows as "registered" at this step, try `lifeinnl.com`, then work down the backup list.

**Important — keep track of the exact domain you bought.** The rest of this guide assumes `dutchexpatguide.com`. Wherever you see that name, mentally substitute the domain you actually purchased.

---

## Step 2 — Push the site to GitHub (10 min)

Run these commands in Terminal. They assume you have `gh` (GitHub CLI) installed. If you don't: `brew install gh`.

```bash
cd "/Users/trymtofte/website/expat-site"

# Initialize git
git init
git add .
git commit -m "Initial site"

# Sign into GitHub CLI if you haven't (one-time)
gh auth login

# Create a public repo and push (replace "trymtofte" with your GitHub username if different)
gh repo create dutchexpatguide --public --source=. --remote=origin --push
```

That's it — `git push` happens automatically with the `--push` flag.

**If you don't have GitHub CLI:** create a repo named `dutchexpatguide` manually at https://github.com/new (set to **Public**, do NOT initialize with README), then run:

```bash
cd "/Users/trymtofte/website/expat-site"
git init
git add .
git commit -m "Initial site"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dutchexpatguide.git
git push -u origin main
```

---

## Step 3 — Enable GitHub Pages (3 min)

1. Open https://github.com/YOUR_USERNAME/dutchexpatguide/settings/pages
2. Under **Source**, select **Deploy from a branch**.
3. Under **Branch**, select `main` and `/ (root)`. Click **Save**.
4. Wait ~60 seconds. The page will refresh with: *"Your site is live at `https://YOUR_USERNAME.github.io/dutchexpatguide/`"*.
5. Click that URL to confirm the site loads. **It will load with broken styles and JS** — that's because the site uses absolute paths (`/styles.css`, `/data/articles.json`). This is fine; once we add the custom domain, the absolute paths resolve correctly.

---

## Step 4 — Point your domain at GitHub Pages (10 min, then DNS waits 1–60 min)

### 4a — Tell GitHub the custom domain

1. In the GitHub Pages settings page (where you were in Step 3), find the **Custom domain** field.
2. Enter `dutchexpatguide.com` (no `https://`, no slash).
3. Click **Save**. GitHub creates a `CNAME` file in the repo automatically.
4. **Don't yet tick** "Enforce HTTPS" — we'll do that after DNS is wired up.

### 4b — Set up DNS at Cloudflare

1. In Cloudflare dashboard, click on `dutchexpatguide.com`.
2. Go to **DNS → Records**.
3. Add the following A records (apex domain → GitHub Pages IPs):

| Type | Name | Content | Proxy |
|---|---|---|---|
| A | @ | 185.199.108.153 | DNS only (grey cloud) |
| A | @ | 185.199.109.153 | DNS only (grey cloud) |
| A | @ | 185.199.110.153 | DNS only (grey cloud) |
| A | @ | 185.199.111.153 | DNS only (grey cloud) |
| CNAME | www | YOUR_USERNAME.github.io | DNS only (grey cloud) |

**Important:** all five records should be **DNS only** (grey cloud), not Proxied (orange cloud). The orange cloud breaks GitHub's automatic SSL provisioning. You can flip to Proxied later if you want Cloudflare's CDN — but only after step 4d succeeds.

### 4c — Wait for DNS propagation (1–60 min)

In Terminal, watch propagation:

```bash
dig +short dutchexpatguide.com
```

When this returns the four IPs above, DNS has propagated.

### 4d — Verify and enforce HTTPS

1. Back at GitHub Pages settings, you should now see "DNS check successful" next to the custom domain.
2. Wait another 5–10 minutes for GitHub to provision the Let's Encrypt cert.
3. Tick **Enforce HTTPS**. Done.
4. Open `https://dutchexpatguide.com` in a browser — site should load with full styling.

---

## Step 5 — Apply for Google AdSense (10 min hands-on, 1–14 days wait)

1. Go to https://adsense.google.com/start/ and sign in with your Google account.
2. Enter your site URL: `https://dutchexpatguide.com`.
3. Pick the country (Netherlands or wherever Trym files taxes — this determines payout currency).
4. Accept terms. Click **Start using AdSense**.
5. AdSense will give you a `<script>` tag (the "AdSense code"). **Copy it.** It looks like:
   ```html
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
   ```
6. Now embed that script — see Step 6.
7. Submit your site for review in the AdSense dashboard.
8. **AdSense approval typically takes 1–14 days.** They want to see: real content (we have 22+ articles after this session), privacy page (you have one), about page (you have one), contact page (you have one), traffic (any traffic — even a few visits from you and friends). The site is structurally well-prepared for approval.

---

## Step 6 — Insert the AdSense code into the HTML (3 min)

There are exactly four files with `<!-- ADSENSE CODE HERE -->` placeholders:

```bash
cd "/Users/trymtofte/website/expat-site"
grep -rn "ADSENSE CODE HERE" *.html
```

You should see matches in `index.html`, `article.html`, `about.html`, `privacy.html`, `contact.html`. For each, replace the placeholder line with your AdSense script.

The fastest way, after copying your AdSense script to clipboard:

```bash
# Replace YOUR-PUBLISHER-ID with what AdSense gave you (the ca-pub-XXXX part)
SCRIPT='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-YOUR-PUBLISHER-ID" crossorigin="anonymous"></script>'

# macOS sed quirk: requires the empty-string after -i
for f in index.html article.html about.html privacy.html contact.html; do
  sed -i '' "s|<!-- ADSENSE CODE HERE -->|$SCRIPT|" "$f"
done
```

Now commit and push:

```bash
git add .
git commit -m "Add AdSense script"
git push
```

GitHub Pages rebuilds in ~60 seconds.

### About the in-article ad slots

The `index.html` and `article.html` files also have `<!-- ADSENSE AD UNIT HERE -->` placeholders for actual ad units (the boxes that show ads, distinct from the script tag). Once AdSense approves your site, go to **AdSense → Ads → By ad unit → Display ads** and create an ad unit. Paste the resulting unit code into those placeholder slots. Don't worry about this on day one — the script tag alone is enough for approval.

---

## Step 7 — Submit sitemap to Google (5 min)

1. Open https://search.google.com/search-console.
2. Add `https://dutchexpatguide.com` as a new property (use "URL prefix" option).
3. Verify ownership: easiest method is **HTML tag** — Search Console gives you a meta tag; paste it into the `<head>` of `index.html`, commit, push, then click verify.
4. Once verified: **Sitemaps → Add a new sitemap → `sitemap.xml`**. Submit.
5. Google will index the site over the next 1–4 weeks.

---

## Step 8 — Bing and DuckDuckGo (3 min)

Bing's index also feeds DuckDuckGo and several other engines.

1. Go to https://www.bing.com/webmasters.
2. Sign in with a Microsoft account.
3. Import from Google Search Console (one click). Done.

---

## What to expect, financially

Realistic AdSense earnings projection for a niche site like this:

| Stage | Traffic/month | RPM (revenue per 1,000 pageviews) | Monthly revenue |
|---|---|---|---|
| Month 1–3 (just launched) | 100–500 | $1–3 | $0.10–$1.50 |
| Month 4–6 (Google starts indexing) | 1,000–3,000 | $3–8 | $3–24 |
| Month 7–12 (organic + Pinterest pickup) | 5,000–15,000 | $5–12 | $25–180 |
| Year 2 (mature, ranked) | 20,000–60,000 | $8–18 | $160–1,080 |

Netherlands-expat audience is high-quality from an advertiser's perspective (high income, English-speaking, location-targetable for Dutch financial/legal services), so RPMs trend toward the high end of the ranges above. Combined with the Gumroad ebook (~$11 average sale × ~1% conversion of organic visitors) and the weekly content task we're setting up, this site is realistically a $100–500/month asset by year two with effectively zero ongoing time investment.

---

## Pre-flight checklist before submitting to AdSense

- [ ] Custom domain works at `https://dutchexpatguide.com`
- [ ] HTTPS is enforced (no mixed content warnings)
- [ ] Privacy policy is present and accurate (you have `/privacy.html`)
- [ ] About page is present (you have `/about.html`)
- [ ] Contact page is present (you have `/contact.html`)
- [ ] At least 15 articles published (you have 22 after this session)
- [ ] Sitemap submitted to Google Search Console
- [ ] AdSense script tag is on every page

All of these are achieved by following this guide end-to-end.

---

## What could go wrong, in order of likelihood

1. **DNS doesn't propagate in 5 minutes.** Normal. Wait up to an hour, sometimes longer in some regions. `dig +short dutchexpatguide.com` is the truth — if it returns the right IPs, DNS is fine and any "site not found" is a browser or local DNS cache issue (try `ipconfig flushdns` on Mac).
2. **GitHub Pages says "DNS check failed"** even after `dig` returns right. GitHub caches DNS lookups for ~10 min. Wait, then click "Check" again.
3. **AdSense rejects on first review.** Most common reasons: "insufficient content" (we mitigate by adding 10 more articles), "navigation issues" (not a concern here), "page not found" errors (also not a concern). If rejected, fix what they cite and resubmit — there's no penalty for resubmission.
4. **Domain you wanted is gone.** Work down the backup list in Step 0. Update the `CNAME` file in the repo to match the new domain.

That's the whole deployment path. The site is production-ready as it stands; everything above is plumbing.
