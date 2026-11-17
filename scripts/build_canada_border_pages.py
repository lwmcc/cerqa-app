#!/usr/bin/env python3
"""Builds the US-Canada border wait pages (English).

Both directions on each page: into the US from CBP (bwt.cbp.gov, read in the browser) and into
Canada from CBSA (cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv, Open Government Licence - Canada). CBSA's
server doesn't allow browser reads from other sites, so the Amplify custom rule
/data/cbsa-bwt.csv -> https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.csv (200) serves it from cerqa.app.
Run from the repo root:  python3 scripts/build_canada_border_pages.py   (QR codes need segno.)
Then add any new pages to sitemap.xml.
"""
import importlib.util
import json
import os
import re
from urllib.parse import quote

_spec = importlib.util.spec_from_file_location("mx", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_border_pages.py"))
mx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mx)

SITE = mx.SITE
HUB = "/canada-border-wait-times/"
APP_STORE = "https://apps.apple.com/app/cerqa-app/id6762389261"

# (slug or None, CBP port, CBSA "Customs Office" name or None, display name, place line)
# slug None = listed for comparison without its own page.
AREAS = {
    "vancouver": {
        "h": "Vancouver and Blaine crossings",
        "items": [
            ("peace-arch", "300402", "Douglas", "Peace Arch (Douglas)", "Blaine, WA / Surrey, BC"),
            ("pacific-highway", "300401", "Pacific Highway", "Pacific Highway", "Blaine, WA / Surrey, BC"),
            ("lynden-aldergrove", "302301", None, "Lynden / Aldergrove", "Lynden, WA / Langley, BC"),
            ("sumas-huntingdon", "300901", "Abbotsford-Huntingdon", "Sumas / Abbotsford-Huntingdon", "Sumas, WA / Abbotsford, BC"),
        ],
        "far": [(None, "300403", "Boundary Bay", "Point Roberts / Boundary Bay", "Point Roberts, WA / Delta, BC")],
    },
    "niagara": {
        "h": "Niagara and Buffalo crossings",
        "items": [
            ("peace-bridge", "090101", "Peace Bridge", "Peace Bridge", "Buffalo, NY / Fort Erie, ON"),
            ("rainbow-bridge", "090102", "Rainbow Bridge", "Rainbow Bridge", "Niagara Falls, NY / Niagara Falls, ON"),
            ("lewiston-queenston", "090104", "Queenston-Lewiston Bridge", "Lewiston-Queenston Bridge", "Lewiston, NY / Niagara-on-the-Lake, ON"),
            (None, "090103", None, "Whirlpool Bridge (NEXUS only)", "Niagara Falls, NY / Niagara Falls, ON"),
        ],
        "far": [],
    },
}

CROSSINGS = {
    "peace-arch": {
        "area": "vancouver",
        "title": "Peace Arch border wait time, live (both directions)",
        "h1": "Peace Arch border wait time",
        "desc": "Live Peace Arch (Douglas) wait into the US from CBP and into Canada from CBSA, for cars and NEXUS. Compare with Pacific Highway, Lynden and Sumas.",
        "lead": "Live waits at the Peace Arch crossing between Blaine, Washington and Surrey, British Columbia, in both directions.",
        "about": """<p>Peace Arch is where I-5 meets BC Highway 99, the most direct route between Seattle and Vancouver. Canada calls it the Douglas crossing. It's for cars only; trucks use Pacific Highway, about a mile east.</p>
<p>When Peace Arch backs up, many drivers switch to Pacific Highway. Compare the two below.</p>""",
    },
    "pacific-highway": {
        "area": "vancouver",
        "title": "Pacific Highway border wait time, live (both directions)",
        "h1": "Pacific Highway border wait time",
        "desc": "Live Pacific Highway (Truck Crossing) wait into the US from CBP and into Canada from CBSA. Compare with Peace Arch, Lynden and Sumas.",
        "lead": "Live waits at the Pacific Highway crossing between Blaine, Washington and Surrey, British Columbia, in both directions.",
        "about": """<p>Pacific Highway is about a mile east of Peace Arch, where Washington State Route 543 meets BC Highway 15. Locals often call it the Truck Crossing because commercial trucks use it, but cars use it too.</p>
<p>It's the usual alternative when Peace Arch is busy.</p>""",
    },
    "lynden-aldergrove": {
        "area": "vancouver",
        "title": "Lynden border wait time (Aldergrove), live",
        "h1": "Lynden / Aldergrove border wait time",
        "desc": "Live Lynden wait into the US from CBP, plus nearby Vancouver-area crossings into Canada. Hours, lanes and alternatives.",
        "lead": "Live wait to enter the US at Lynden, Washington from Aldergrove, British Columbia, from CBP.",
        "about": """<p>Lynden-Aldergrove is a smaller crossing east of Blaine, between Washington State Route 539 and BC Highway 13. It isn't open overnight, so check the hours above.</p>
<p>CBSA doesn't publish a wait into Canada for Aldergrove; the other crossings are listed below.</p>""",
    },
    "sumas-huntingdon": {
        "area": "vancouver",
        "title": "Sumas border wait time (Abbotsford), live",
        "h1": "Sumas / Abbotsford-Huntingdon border wait time",
        "desc": "Live Sumas wait into the US from CBP and Abbotsford-Huntingdon wait into Canada from CBSA. Compare with Peace Arch and Pacific Highway.",
        "lead": "Live waits at the crossing between Sumas, Washington and Abbotsford, British Columbia, in both directions.",
        "about": """<p>Sumas connects Washington State Route 9 with BC Highway 11 in Abbotsford, in the Fraser Valley. Canada calls it Abbotsford-Huntingdon.</p>
<p>For trips to the Fraser Valley or east of Vancouver, it can beat the Blaine crossings.</p>""",
    },
    "peace-bridge": {
        "area": "niagara",
        "title": "Peace Bridge border wait time, live (both directions)",
        "h1": "Peace Bridge border wait time",
        "desc": "Live Peace Bridge wait into the US from CBP and into Canada from CBSA, Buffalo to Fort Erie. Compare with Rainbow and Lewiston-Queenston.",
        "lead": "Live waits on the Peace Bridge between Buffalo, New York and Fort Erie, Ontario, in both directions.",
        "about": """<p>The Peace Bridge connects Buffalo with Fort Erie, linking I-190 with the QEW toward Toronto. It carries cars and trucks.</p>
<p>Compare it with the Rainbow and Lewiston-Queenston bridges below before you pick one.</p>""",
    },
    "rainbow-bridge": {
        "area": "niagara",
        "title": "Rainbow Bridge border wait time, live (both directions)",
        "h1": "Rainbow Bridge border wait time",
        "desc": "Live Rainbow Bridge wait into the US from CBP and into Canada from CBSA, Niagara Falls NY to Niagara Falls ON. Compare with Peace Bridge and Lewiston.",
        "lead": "Live waits on the Rainbow Bridge between Niagara Falls, New York and Niagara Falls, Ontario, in both directions.",
        "about": """<p>The Rainbow Bridge crosses the Niagara River just below the falls. It's for cars and people on foot; trucks aren't allowed.</p>
<p>Because it's right by the falls, it gets busy on summer weekends. The Lewiston-Queenston Bridge is a few miles north.</p>""",
    },
    "lewiston-queenston": {
        "area": "niagara",
        "title": "Lewiston-Queenston Bridge wait time, live (both directions)",
        "h1": "Lewiston-Queenston Bridge wait time",
        "desc": "Live Lewiston-Queenston wait into the US from CBP and into Canada from CBSA. Compare with the Peace and Rainbow bridges.",
        "lead": "Live waits on the Lewiston-Queenston Bridge between Lewiston, New York and Niagara-on-the-Lake, Ontario, in both directions.",
        "about": """<p>The Lewiston-Queenston Bridge is north of the falls and connects I-190 with Highway 405, which leads to the QEW. It carries cars and trucks.</p>
<p>It's a common choice for trips to Toronto when the Rainbow Bridge is busy.</p>""",
    },
}

LANES = """
<h2>Which lane can I use into the US?</h2>
<div class="prose">
<ul>
<li><strong>General lanes</strong> are open to everyone.</li>
<li><strong>NEXUS</strong> lanes are only for NEXUS members. Everyone in the car needs a NEXUS card.</li>
<li><strong>Ready Lane</strong> is for travelers whose documents have an RFID chip, such as a passport card, a NEXUS card or an enhanced driver's license. Everyone in the car needs one.</li>
</ul>
<p>CBSA reports the wait for travelers into Canada as one number per crossing.</p>
</div>"""

SOURCE = ('Waits into the US: <a href="https://bwt.cbp.gov/">U.S. Customs and Border Protection</a>. '
          'Waits into Canada: <a href="https://www.cbsa-asfc.gc.ca/bwt-taf/menu-eng.html">Canada Border Services Agency</a>; '
          'contains information licensed under the <a href="https://open.canada.ca/en/open-government-licence-canada">Open Government Licence – Canada</a>. '
          "These are official estimates and can change quickly. The page refreshes on its own every 5 minutes.")

CTA_H = "Crossing with family or friends?"
CTA_P = "Cerqa shows everyone's live location and arrival time on one map, so nobody gets lost on the other side. Free on iPhone and Android."
PICKUP = ("<strong>Picking someone up on the other side?</strong> If they have Cerqa, they can send you a live link while they drive. "
          "You'll see their arrival time in your browser, no app needed.")


def download_url(campaign, medium):
    return f"{SITE}/download/?utm_source=cerqa.app&utm_medium={medium}&utm_campaign={campaign}"


def qr(campaign):
    rel = f"images/qr/{campaign}.svg"
    if not os.path.exists(rel):
        import segno
        os.makedirs("images/qr", exist_ok=True)
        segno.make(download_url(campaign, "qr"), error="m").save(rel, scale=3, border=2, dark="#1b2d4a", light="#ffffff")
        svg = open(rel).read()
        w = re.search(r'<svg[^>]* width="(\d+)"', svg).group(1)
        open(rel, "w").write(svg.replace(f'width="{w}" height="{w}"', f'width="{w}" height="{w}" viewBox="0 0 {w} {w}"', 1))
    return "/" + rel


def cta(campaign):
    play = mx.PLAY.format(campaign=campaign)
    return f"""<section class="app-cta">
  <div class="app-cta-text">
  <h2>{CTA_H}</h2>
  <p>{CTA_P}</p>
  <div class="stores">
    <a href="{APP_STORE}" target="_blank" rel="noopener">App Store</a>
    <a href="{play}" target="_blank" rel="noopener">Google Play</a>
  </div>
  </div>
  <figure class="app-cta-qr"><img src="{qr(campaign)}" alt="" width="135" height="135"><figcaption>Scan to get Cerqa on your phone</figcaption></figure>
</section>"""


def row_us(port, name, place, slug, current):
    label = f'<a href="{HUB}{slug}/">{name}</a>' if slug and not current else name
    if current:
        label += ' <span class="this-page">· this page</span>'
    return (f'<li><span class="crossing-name">{label}<span class="crossing-sub">{place}</span></span>'
            f'<span class="crossing-wait" data-port="{port}" data-mode="row">…</span></li>')


def row_ca(cbsa, name, place, slug, current):
    label = f'<a href="{HUB}{slug}/">{name}</a>' if slug and not current else name
    if current:
        label += ' <span class="this-page">· this page</span>'
    return (f'<li><span class="crossing-name">{label}<span class="crossing-sub">{place}</span></span>'
            f'<span class="crossing-wait" data-cbsa="{cbsa}" data-mode="row">…</span></li>')


def compare(area_key, current=None):
    a = AREAS[area_key]
    us = [row_us(p, n, pl, s, s == current and s is not None) for s, p, c, n, pl in a["items"]]
    ca = [row_ca(c, n, pl, s, s == current and s is not None) for s, p, c, n, pl in a["items"] if c]
    out = f"""<h2>{a['h']}: into the US right now</h2>
<ul class="crossing-list" data-fastest>
{chr(10).join(us)}
</ul>
<h2>{a['h']}: into Canada right now</h2>
<ul class="crossing-list" data-fastest>
{chr(10).join(ca)}
</ul>"""
    if a["far"]:
        far_us = [row_us(p, n, pl, None, False) for s, p, c, n, pl in a["far"]]
        out += f'\n<h3 class="farther">Farther away (into the US)</h3>\n<ul class="crossing-list">\n{chr(10).join(far_us)}\n</ul>'
    return out


def faq(name, area_h):
    qa = [
        (f"How long is the wait at {name} right now?",
         f"The live waits at the top of this page are the official estimates for {name}: CBP for going into the US and CBSA for going into Canada. They refresh every 5 minutes on their own."),
        ("Which crossing is fastest right now?",
         f"Check the {area_h} lists above. The crossing with the shortest regular car wait in each direction gets a green Fastest by car tag."),
        ("Is there a wait time for going into Canada?",
         "Yes. The Canada Border Services Agency publishes waits for travelers entering Canada, and this page shows them next to the US waits."),
        ("Can my family see when I've crossed?",
         "Yes, with the free Cerqa app. You share your location for the trip, and they see where you are and when you'll arrive."),
    ]
    html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in qa)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    return (f'<h2>Questions</h2>\n<div class="prose faq">\n{html}\n</div>\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def share(slug, name):
    plain = re.sub(r"<[^>]+>", "", name)
    url = f"{SITE}{HUB}{slug}/?utm_source=whatsapp&utm_medium=share&utm_campaign=border_share_ca"
    href = "https://wa.me/?text=" + quote(f"{plain}: {url}")
    return (f'<div class="share-row"><a class="share-wa" href="{href}" target="_blank" rel="noopener" '
            f'data-share-name="{plain}" data-share-url="{url}">Share on WhatsApp</a>'
            f'<button type="button" class="share-other" hidden>Share</button></div>')


def page(path, title, desc, body):
    t = mx.TEXT["en"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Cerqa</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
<link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
<meta name="apple-itunes-app" content="app-id=6762389261">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Cerqa">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/social/cerqa-en.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/border.css">{mx.analytics()}
</head>
<body data-border="ca">
<nav class="site-nav">
  <a class="site-nav-brand" href="/">Cerqa</a>
  <a class="site-nav-lang" href="/border-wait-times/">Mexico border</a>
</nav>
<main>
{body}
</main>
<footer>
  <p>© 2026 Cerqa</p>
  {' '.join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
</footer>
<script src="/assets/border.js" defer></script>
<script src="/assets/store-gate.js" defer></script>
</body>
</html>
"""


def build_hub():
    sections = "\n".join(compare(k) for k in AREAS)
    body = f"""<h1>US-Canada border wait times</h1>
<p class="lead">Live waits at the Vancouver and Niagara crossings in both directions: into the US from US Customs and Border Protection (CBP), and into Canada from the Canada Border Services Agency (CBSA).</p>
<noscript><p class="note">Turn on JavaScript to see the live waits.</p></noscript>
{sections}
<p style="margin-top:12px"><a href="/border-wait-times/">US-Mexico border wait times</a></p>
{cta("border_ca_hub")}
<p class="source">{SOURCE}</p>"""
    return HUB, page(HUB, "US-Canada border wait times, live (both directions)",
                     "Live border waits at Peace Arch, Pacific Highway, Sumas, Lynden, the Peace Bridge, Rainbow Bridge and Lewiston-Queenston, into the US (CBP) and into Canada (CBSA).", body)


def build_crossing(slug, c):
    area = AREAS[c["area"]]
    me = next(it for it in area["items"] if it[0] == slug)
    _, port, cbsa, name, place = me
    campaign = f"border_ca_{slug.replace('-', '_')}"
    short = re.sub(r" \(.*\)", "", name)
    into_ca = (f'<h2>Into Canada</h2>\n<div class="wait-card" data-cbsa="{cbsa}" data-mode="detail"><p class="wait-loading">Loading live wait from CBSA…</p></div>'
               if cbsa else '<h2>Into Canada</h2>\n<p class="note">CBSA doesn\'t publish a wait into Canada for this crossing.</p>')
    body = f"""<p class="crumbs"><a href="{HUB}">US-Canada border wait times</a></p>
<h1>{c['h1']}</h1>
<p class="lead">{c['lead']}</p>
<h2>Into the US</h2>
<div class="wait-card" data-port="{port}" data-mode="detail"><p class="wait-loading">Loading live wait from CBP…</p></div>
{into_ca}
<noscript><p class="note">Turn on JavaScript to see the live waits.</p></noscript>
{share(slug, name)}
<p class="pickup">{PICKUP} <a href="{download_url(campaign, 'web').replace('&', '&amp;')}">Get Cerqa</a></p>
{compare(c['area'], current=slug)}
<p style="margin-top:12px"><a href="{HUB}">All US-Canada crossings</a></p>
<h2>About this crossing</h2>
<div class="prose">{c['about']}</div>
{LANES}
{faq(short, area['h'])}
{cta(campaign)}
<p class="source">{SOURCE}</p>"""
    path = f"{HUB}{slug}/"
    return path, page(path, c["title"], c["desc"], body)


if __name__ == "__main__":
    mx.write(*build_hub())
    for slug, c in CROSSINGS.items():
        mx.write(*build_crossing(slug, c))
