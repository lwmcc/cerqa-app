#!/usr/bin/env python3
"""Quebec border wait pages in French (2026-11-21): /fr/temps-attente-frontiere/ and one page per
crossing (Lacolle, Stanstead, Saint-Armand/Philipsburg), both directions, same live data and
border.js as the English Canada pages (scripts/build_canada_border_pages.py, which holds the
crossing list in AREAS["montreal"] and the English twins).
Run from the repo root:  python3 scripts/build_quebec_border_pages.py   (QR codes need segno.)
Then add new pages to sitemap.xml.
"""
import importlib.util
import json
import os
import re
from urllib.parse import quote

_spec = importlib.util.spec_from_file_location("ca", os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_canada_border_pages.py"))
ca = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ca)
mx, SITE = ca.mx, ca.SITE

HUB = "/fr/temps-attente-frontiere/"
EN_HUB = ca.HUB
APP_STORE = "https://apps.apple.com/ca/app/cerqa-app/id6762389261?l=fr"

# French slug -> (English slug in ca.AREAS["montreal"], display name, place line)
NAMES = {
    "lacolle": ("lacolle-champlain", "Lacolle / Champlain (autoroute 15)", "Saint-Bernard-de-Lacolle, QC / Champlain, NY"),
    "stanstead": ("stanstead-derby-line", "Stanstead / Derby Line (autoroute 55)", "Stanstead, QC / Derby Line, VT"),
    "saint-armand-philipsburg": ("saint-armand-highgate", "Saint-Armand / Philipsburg (route 133)", "Saint-Armand, QC / Highgate Springs, VT"),
}
EN_TO_FR = {en: fr for fr, (en, _, _) in NAMES.items()}

CROSSINGS = {
    "lacolle": {
        "title": "Temps d'attente à Lacolle (frontière), en direct dans les deux sens",
        "h1": "Temps d'attente à la frontière de Lacolle",
        "desc": "Attente en direct à Lacolle vers le Canada (ASFC) et à Champlain vers les États-Unis (CBP), sur l'autoroute 15 / I-87 entre Montréal et New York. Comparez avec Stanstead et Saint-Armand.",
        "lead": "Temps d'attente en direct au poste de Saint-Bernard-de-Lacolle, entre le Québec et Champlain (New York), dans les deux sens.",
        "about": """<p>Lacolle est le principal poste entre Montréal et New York, là où l'autoroute 15 rejoint l'I-87, à environ 45 minutes au sud de Montréal. Le Canada l'appelle Saint-Bernard-de-Lacolle; du côté américain, c'est Champlain. Il est ouvert 24 heures et les files s'allongent pendant les longs week-ends.</p>
<p>Quand Lacolle est congestionné, Saint-Armand (route 133) vers le Vermont est l'option habituelle. Comparez-les ci-dessous.</p>""",
    },
    "stanstead": {
        "title": "Temps d'attente à Stanstead (frontière), en direct dans les deux sens",
        "h1": "Temps d'attente à la frontière de Stanstead",
        "desc": "Attente en direct à Stanstead vers le Canada (ASFC) et à Derby Line vers les États-Unis (CBP), sur l'autoroute 55 / I-91 entre les Cantons-de-l'Est et le Vermont.",
        "lead": "Temps d'attente en direct au poste entre Stanstead (Québec) et Derby Line (Vermont), dans les deux sens.",
        "about": """<p>Stanstead relie l'autoroute 55 à l'I-91 au Vermont, la route principale entre les Cantons-de-l'Est (Sherbrooke, Magog) et la Nouvelle-Angleterre. Il est ouvert 24 heures.</p>
<p>Depuis Montréal, Lacolle et Saint-Armand sont plus proches; comparez les trois ci-dessous.</p>""",
    },
    "saint-armand-philipsburg": {
        "title": "Temps d'attente à Saint-Armand / Philipsburg (frontière), en direct",
        "h1": "Temps d'attente à la frontière de Saint-Armand / Philipsburg",
        "desc": "Attente en direct à Saint-Armand/Philipsburg vers le Canada (ASFC) et à Highgate Springs vers les États-Unis (CBP), sur la route 133 / I-89 entre Montréal et le Vermont.",
        "lead": "Temps d'attente en direct au poste entre Saint-Armand (Philipsburg, Québec) et Highgate Springs (Vermont), dans les deux sens.",
        "about": """<p>Saint-Armand/Philipsburg est là où la route 133 rejoint l'I-89, la route de Montréal vers Burlington et le Vermont. Il est ouvert 24 heures.</p>
<p>C'est l'option habituelle quand Lacolle est congestionné. Comparez-les ci-dessous.</p>""",
    },
}

LANES = """<h2>Les voies</h2>
<div class="prose">
<ul>
<li><strong>Voies générales</strong> : ouvertes à tous.</li>
<li><strong>NEXUS</strong> : réservées aux membres NEXUS. Tous les occupants du véhicule doivent avoir une carte NEXUS.</li>
<li><strong>Ready Lane</strong> (vers les États-Unis) : pour les voyageurs dont les documents ont une puce RFID, comme une carte passeport, une carte NEXUS ou un permis de conduire Plus. Tous les occupants doivent en avoir une.</li>
</ul>
<p>L'ASFC publie un seul temps d'attente par poste pour les voyageurs qui entrent au Canada.</p>
</div>"""

SOURCE = ('Attente vers les États-Unis : <a href="https://bwt.cbp.gov/">U.S. Customs and Border Protection</a>. '
          'Attente vers le Canada : <a href="https://www.cbsa-asfc.gc.ca/bwt-taf/menu-fra.html">Agence des services frontaliers du Canada</a>; '
          'contient des informations visées par la <a href="https://ouvert.canada.ca/fr/licence-du-gouvernement-ouvert-canada">Licence du gouvernement ouvert – Canada</a>. '
          "Ce sont des estimations officielles qui peuvent changer rapidement. La page se met à jour toute seule toutes les 5 minutes.")

CTA_H = "Vous traversez en famille ou entre amis?"
CTA_P = "Cerqa montre la position en direct et l'heure d'arrivée de chacun sur une seule carte, pour que personne ne se perde de l'autre côté. Gratuit sur iPhone et Android."
PICKUP = ("<strong>Vous attendez quelqu'un de l'autre côté?</strong> S'il a Cerqa, il peut vous envoyer un lien en direct pendant qu'il roule. "
          "Vous voyez son heure d'arrivée dans votre navigateur, sans appli.")
AREA_H = "Postes de Montréal et du Québec"


def download_url(campaign, medium):
    return f"{SITE}/fr/telecharger/?utm_source=cerqa.app&utm_medium={medium}&utm_campaign={campaign}"


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
    play = mx.PLAY.format(campaign=campaign) + "&amp;hl=fr"
    return f"""<section class="app-cta">
  <div class="app-cta-text">
  <h2>{CTA_H}</h2>
  <p>{CTA_P}</p>
  <div class="stores">
    <a href="{APP_STORE}" target="_blank" rel="noopener">App Store</a>
    <a href="{play}" target="_blank" rel="noopener">Google Play</a>
  </div>
  </div>
  <figure class="app-cta-qr"><img src="{qr(campaign)}" alt="" width="135" height="135"><figcaption>Scannez pour télécharger Cerqa</figcaption></figure>
</section>"""


def items():
    for en_slug, port, cbsa, _, _ in ca.AREAS["montreal"]["items"]:
        fr = EN_TO_FR[en_slug]
        yield fr, port, cbsa, NAMES[fr][1], NAMES[fr][2]


def row(attr, val, name, place, slug, current):
    label = f'<a href="{HUB}{slug}/">{name}</a>' if not current else name + ' <span class="this-page">· cette page</span>'
    return (f'<li><span class="crossing-name">{label}<span class="crossing-sub">{place}</span></span>'
            f'<span class="crossing-wait" {attr}="{val}" data-mode="row">…</span></li>')


def compare(current=None):
    ca_rows = [row("data-cbsa", c, n, pl, s, s == current) for s, p, c, n, pl in items()]
    us_rows = [row("data-port", p, n, pl, s, s == current) for s, p, c, n, pl in items()]
    return f"""<h2>{AREA_H} : vers le Canada en ce moment</h2>
<ul class="crossing-list" data-fastest>
{chr(10).join(ca_rows)}
</ul>
<h2>{AREA_H} : vers les États-Unis en ce moment</h2>
<ul class="crossing-list" data-fastest>
{chr(10).join(us_rows)}
</ul>"""


def faq(name):
    qa = [
        (f"Quel est le temps d'attente à {name} en ce moment?",
         f"Les temps en haut de cette page sont les estimations officielles pour {name} : l'ASFC pour entrer au Canada et la CBP pour entrer aux États-Unis. Ils se mettent à jour tout seuls toutes les 5 minutes."),
        ("Quel poste est le plus rapide en ce moment?",
         "Regardez les listes ci-dessus. Le poste avec la plus courte attente en voiture dans chaque sens porte l'étiquette verte Le plus rapide en voiture."),
        ("Y a-t-il un temps d'attente pour entrer aux États-Unis?",
         "Oui. La U.S. Customs and Border Protection publie l'attente pour entrer aux États-Unis, et cette page l'affiche à côté de l'attente vers le Canada."),
        ("Ma famille peut-elle voir quand j'ai traversé?",
         "Oui, avec l'appli gratuite Cerqa. Vous partagez votre position pour le trajet, et vos proches voient où vous êtes et quand vous arriverez."),
    ]
    html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in qa)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "fr", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    return (f'<h2>Questions</h2>\n<div class="prose faq">\n{html}\n</div>\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def share(slug, name):
    plain = re.sub(r"<[^>]+>", "", name)
    url = f"{SITE}{HUB}{slug}/?utm_source=whatsapp&utm_medium=share&utm_campaign=border_share_qc"
    href = "https://wa.me/?text=" + quote(f"{plain} : {url}")
    return (f'<div class="share-row"><a class="share-wa" href="{href}" target="_blank" rel="noopener" '
            f'data-share-name="{plain}" data-share-url="{url}">Partager sur WhatsApp</a>'
            f'<button type="button" class="share-other" hidden>Partager</button></div>')


def page(path, en_path, title, desc, body):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Cerqa</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="fr" href="{SITE}{path}">
<link rel="alternate" hreflang="fr-CA" href="{SITE}{path}">
<link rel="alternate" hreflang="en" href="{SITE}{en_path}">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
<link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
<meta name="apple-itunes-app" content="app-id=6762389261">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Cerqa">
<meta property="og:locale" content="fr_CA">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/social/cerqa-fr.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/border.css">{mx.analytics()}
</head>
<body data-border="ca">
<nav class="site-nav">
  <a class="site-nav-brand" href="/fr/">Cerqa</a>
  <a class="site-nav-lang" href="{en_path}" hreflang="en" lang="en">English</a>
</nav>
<main>
{body}
</main>
<footer>
  <p>© 2026 Cerqa</p>
  <a href="/fr/">Accueil</a> <a href="/privacy/fr/">Confidentialité</a> <a href="/terms/fr/">Conditions</a>
</footer>
<script src="/assets/border.js" defer></script>
<script src="/assets/store-gate.js" defer></script>
</body>
</html>
"""


def build_hub():
    body = f"""<h1>Temps d'attente à la frontière Québec–États-Unis</h1>
<p class="lead">Attente en direct aux postes de Lacolle, Stanstead et Saint-Armand dans les deux sens : vers le Canada selon l'Agence des services frontaliers du Canada (ASFC), et vers les États-Unis selon la U.S. Customs and Border Protection (CBP).</p>
<noscript><p class="note">Activez JavaScript pour voir les temps en direct.</p></noscript>
{compare()}
<p style="margin-top:12px"><a href="{EN_HUB}" hreflang="en" lang="en">All US-Canada crossings (English)</a></p>
{cta("border_qc_hub")}
<p class="source">{SOURCE}</p>"""
    return HUB, page(HUB, EN_HUB, "Temps d'attente à la frontière Québec–États-Unis, en direct",
                     "Attente en direct à Lacolle, Stanstead et Saint-Armand/Philipsburg, vers le Canada (ASFC) et vers les États-Unis (CBP).", body)


def build_crossing(slug, c):
    en_slug, name, place = NAMES[slug]
    _, port, cbsa, _, _ = next(it for it in ca.AREAS["montreal"]["items"] if it[0] == en_slug)
    campaign = f"border_qc_{slug.replace('-', '_')}"
    short = re.sub(r" \(.*\)", "", name)
    body = f"""<p class="crumbs"><a href="{HUB}">Frontière Québec–États-Unis</a></p>
<h1>{c['h1']}</h1>
<p class="lead">{c['lead']}</p>
<h2>Vers le Canada</h2>
<div class="wait-card" data-cbsa="{cbsa}" data-mode="detail"><p class="wait-loading">Chargement de l'attente (ASFC)…</p></div>
<h2>Vers les États-Unis</h2>
<div class="wait-card" data-port="{port}" data-mode="detail"><p class="wait-loading">Chargement de l'attente (CBP)…</p></div>
<noscript><p class="note">Activez JavaScript pour voir les temps en direct.</p></noscript>
{share(slug, name)}
<p class="pickup">{PICKUP} <a href="{download_url(campaign, 'web').replace('&', '&amp;')}">Obtenir Cerqa</a></p>
{compare(current=slug)}
<p style="margin-top:12px"><a href="{HUB}">Tous les postes du Québec</a></p>
<h2>À propos de ce poste</h2>
<div class="prose">{c['about']}</div>
{LANES}
{faq(short)}
{cta(campaign)}
<p class="source">{SOURCE}</p>"""
    path = f"{HUB}{slug}/"
    return path, page(path, f"{EN_HUB}{en_slug}/", c["title"], c["desc"], body)


if __name__ == "__main__":
    mx.write(*build_hub())
    for slug, c in CROSSINGS.items():
        mx.write(*build_crossing(slug, c))
