#!/usr/bin/env python3
"""Builds the Mexico gas price pages from the CNE open data feeds.

Runs every night in GitHub Actions (.github/workflows/gas-pages.yml) and commits the pages, which
deploys cerqa.app. Run locally from the repo root:  python3 scripts/build_gas_pages.py
No dependencies beyond Python 3.9+. If a feed fails, nothing is written.

Pages:  /es/gasolina/ (all states) + /gas-prices-mexico/ (English), state pages for STATE_PAGES,
city pages for CITY_PAGES. Stations are placed in a state or municipality with the outlines in
scripts/data/mx_boundaries.json (geoBoundaries, CC BY 4.0).
"""
import base64
import datetime
import gzip
import json
import math
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

SITE = "https://cerqa.app"
FEED = "https://publicacionexterna.azurewebsites.net/publicaciones/"
FUELS = ["regular", "premium", "diesel"]
FUEL_ES = {"regular": "Magna", "premium": "Premium", "diesel": "Diésel"}
FUEL_EN = {"regular": "Regular (Magna)", "premium": "Premium", "diesel": "Diesel"}
VALID = (15.0, 40.0)  # pesos per liter; anything outside is a reporting error

# ADM1 name -> (display name, slug)
STATE_NAMES = {
    "Aguascalientes": "Aguascalientes", "Baja California": "Baja California", "Baja California Sur": "Baja California Sur",
    "Campeche": "Campeche", "Chiapas": "Chiapas", "Chihuahua": "Chihuahua", "Coahuila de Zaragoza": "Coahuila",
    "Colima": "Colima", "Distrito Federal": "Ciudad de México", "Durango": "Durango", "Guanajuato": "Guanajuato",
    "Guerrero": "Guerrero", "Hidalgo": "Hidalgo", "Jalisco": "Jalisco", "Mexico": "Estado de México",
    "Michoacan de Ocampo": "Michoacán", "Morelos": "Morelos", "Nayarit": "Nayarit", "Nuevo Leon": "Nuevo León",
    "Oaxaca": "Oaxaca", "Puebla": "Puebla", "Queretaro de Arteaga": "Querétaro", "Quintana Roo": "Quintana Roo",
    "San Luis Potosi": "San Luis Potosí", "Sinaloa": "Sinaloa", "Sonora": "Sonora", "Tabasco": "Tabasco",
    "Tamaulipas": "Tamaulipas", "Tlaxcala": "Tlaxcala", "Veracruz de Ignacio de la Llave": "Veracruz",
    "Yucatan": "Yucatán", "Zacatecas": "Zacatecas",
}
STATE_PAGES = {"Guanajuato": "guanajuato", "Queretaro de Arteaga": "queretaro"}
# (municipality as in the outlines, ADM1 state, page slug, display name)
CITY_PAGES = [
    ("León", "Guanajuato", "leon", "León"),
    ("Irapuato", "Guanajuato", "irapuato", "Irapuato"),
    ("Celaya", "Guanajuato", "celaya", "Celaya"),
    ("Salamanca", "Guanajuato", "salamanca", "Salamanca"),
    ("Silao de la Victoria", "Guanajuato", "silao", "Silao"),
    ("Guanajuato", "Guanajuato", "guanajuato-capital", "Guanajuato capital"),
    ("San Miguel de Allende", "Guanajuato", "san-miguel-de-allende", "San Miguel de Allende"),
    ("Querétaro", "Queretaro de Arteaga", "queretaro-ciudad", "Querétaro"),
]
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
          "octubre", "noviembre", "diciembre"]
APP_STORE = "https://apps.apple.com/{cc}/app/cerqa-app/id6762389261"
PLAY = ("https://play.google.com/store/apps/details?id=com.cerqa.app&amp;referrer="
        "utm_source%3Dcerqa.app%26utm_medium%3Dweb%26utm_campaign%3D{campaign}")


# ---------- data ----------

def fetch(name):
    req = urllib.request.Request(FEED + name, headers={"Accept-Encoding": "gzip", "User-Agent": "cerqa.app gas pages"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return ET.fromstring(data.decode("utf-8-sig"))


def pretty_name(raw):
    """Same rules as the app's prettyStationName: drop SA DE CV etc., title case."""
    s = re.sub(r"[,.]?\s+(S\.?\s?A\.?\s?P\.?\s?I\.?|S\.?\s?A\.?|S\.?\s?DE\s?R\.?\s?L\.?|S\.?\s?C\.?|A\.?\s?C\.?)(\s+DE\s+C\.?\s?V\.?)?\.?$", "",
               raw.strip(), flags=re.I).strip()
    small = {"de", "del", "la", "las", "los", "y", "el"}
    words = [w if w in small else w[:1].upper() + w[1:] for w in s.lower().split()]
    out = " ".join(words)
    return out[:1].upper() + out[1:]


def location_link(lat, lng, name):
    """cerqa.app/location?p=CODE, the same code the app builds (LocationLink, kind g = gas station)."""
    payload = f"g|{round(lat, 5)}|{round(lng, 5)}|{name}"
    return SITE + "/location?p=" + base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")


def inside(x, y, polys):
    for poly in polys:
        if _in_ring(x, y, poly[0]) and not any(_in_ring(x, y, hole) for hole in poly[1:]):
            return True
    return False


def _in_ring(x, y, ring):
    c = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def locate(x, y, areas):
    for a in areas:
        b = a["bbox"]
        if b[0] <= x <= b[2] and b[1] <= y <= b[3] and inside(x, y, a["polys"]):
            return a
    return None


def load_stations():
    places = fetch("places")
    prices = fetch("prices")
    by_id = {}
    for p in prices.findall("place"):
        fuels = {}
        for g in p.findall("gas_price"):
            try:
                v = float(g.text)
            except (TypeError, ValueError):
                continue
            if VALID[0] <= v <= VALID[1]:
                fuels[g.get("type")] = v
        if fuels:
            by_id[p.get("place_id")] = fuels
    geo = json.load(open(os.path.join(os.path.dirname(__file__), "data", "mx_boundaries.json")))
    stations = []
    for p in places.findall("place"):
        pid = p.get("place_id")
        if pid not in by_id:
            continue
        try:
            x = float(p.find("location/x").text)
            y = float(p.find("location/y").text)
        except (AttributeError, TypeError, ValueError):
            continue
        st = locate(x, y, geo["states"])
        if not st:
            continue
        mu = locate(x, y, [m for m in geo["municipalities"] if m["state"] == st["name"]]) \
            if st["name"] in STATE_PAGES else None
        name = pretty_name(p.findtext("name") or "")
        stations.append({"id": pid, "name": name, "lat": y, "lng": x, "state": st["name"],
                         "muni": mu["name"] if mu else None, "prices": by_id[pid]})
    match_brands(stations)
    if len(stations) < 5000:
        sys.exit(f"Only {len(stations)} stations matched; feed looks wrong, not writing pages.")
    return stations, geo


def match_brands(stations):
    """Nearest branded OpenStreetMap station within 120 m (scripts/data/osm_fuel_brands.json)."""
    path = os.path.join(os.path.dirname(__file__), "data", "osm_fuel_brands.json")
    grid = {}
    for lat, lng, brand in json.load(open(path))["stations"]:
        grid.setdefault((round(lat, 2), round(lng, 2)), []).append((lat, lng, brand))
    for s in stations:
        best, best_d = None, 120.0
        for dy in (-0.01, 0, 0.01):
            for dx in (-0.01, 0, 0.01):
                for lat, lng, brand in grid.get((round(s["lat"] + dy, 2), round(s["lng"] + dx, 2)), ()):
                    d = math.hypot((lat - s["lat"]) * 111_320, (lng - s["lng"]) * 111_320 * math.cos(math.radians(lat)))
                    if d <= best_d:
                        best, best_d = brand, d
        s["brand"] = best


def stats(stations, fuel):
    v = [s["prices"][fuel] for s in stations if fuel in s["prices"]]
    if not v:
        return None
    return {"n": len(v), "avg": sum(v) / len(v), "min": min(v), "max": max(v)}


def money(v):
    return f"${v:,.2f}"


# ---------- html ----------

def analytics():
    s = open("index.html").read()
    return re.search(r"\s*<!-- Google Analytics 4.*?</script>", s, re.S).group(0)


def page(lang, path, title, desc, body, alt_path=None):
    alts = ""
    if alt_path:
        en, es = (path, alt_path) if lang == "en" else (alt_path, path)
        alts = (f'\n<link rel="alternate" hreflang="en" href="{SITE}{en}">'
                f'\n<link rel="alternate" hreflang="es" href="{SITE}{es}">'
                f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{en}">')
    nav_lang = (f'<a class="site-nav-lang" href="{alt_path}" hreflang="{"es" if lang == "en" else "en"}">'
                f'{"Español" if lang == "en" else "English"}</a>') if alt_path else ""
    footer = ([("/feedback", "Feedback"), ("/support/", "Support"), ("/privacy/en/", "Privacy Policy"),
               ("/terms/en/", "Terms of Service")] if lang == "en" else
              [("/es/comentarios/", "Comentarios"), ("/support/", "Ayuda"), ("/privacy/es/", "Aviso de privacidad"),
               ("/terms/es/", "Términos del servicio")])
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Cerqa</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">{alts}
<link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
<link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
<meta name="apple-itunes-app" content="app-id=6762389261">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Cerqa">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/social/cerqa-{lang}.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/border.css">{GA}
</head>
<body>
<nav class="site-nav">
  <a class="site-nav-brand" href="{"/" if lang == "en" else "/es/"}">Cerqa</a>
  {nav_lang}
</nav>
<main>
{body}
</main>
<footer>
  <p>© 2026 Cerqa</p>
  {" ".join(f'<a href="{h}">{n}</a>' for h, n in footer)}
</footer>
</body>
</html>
"""


def summary_cards(st_list, lang):
    names = FUEL_EN if lang == "en" else FUEL_ES
    avg = "average" if lang == "en" else "promedio"
    rng = "lowest {0} · highest {1}" if lang == "en" else "más bajo {0} · más alto {1}"
    cards = []
    for f in FUELS:
        s = stats(st_list, f)
        if not s:
            continue
        cards.append(f"""<div class="fuel-card">
  <div class="fuel-name">{names[f]}</div>
  <div class="fuel-price">{money(s['avg'])}<span>/L {avg}</span></div>
  <div class="fuel-range">{rng.format(money(s['min']), money(s['max']))}</div>
</div>""")
    return '<div class="fuel-cards">' + "\n".join(cards) + "</div>"


def station_table(rows, fuel, lang, show_muni=False):
    names = FUEL_EN if lang == "en" else FUEL_ES
    rows = sorted([s for s in rows if fuel in s["prices"]], key=lambda s: s["prices"][fuel])
    head = ("<th>#</th><th>" + ("Station" if lang == "en" else "Gasolinera") + "</th>" +
            ("<th>" + ("Municipality" if lang == "en" else "Municipio") + "</th>" if show_muni else "") +
            "".join(f'<th class="num">{names[f].split(" ")[0]}</th>' for f in FUELS))
    body = []
    for i, s in enumerate(rows, 1):
        cells = "".join(
            f'<td class="num{" hl" if f == fuel else ""}">{money(s["prices"][f]) if f in s["prices"] else "–"}</td>'
            for f in FUELS)
        muni = f"<td>{s['muni'] or ''}</td>" if show_muni else ""
        link = location_link(s["lat"], s["lng"], s["name"])
        label = (f'<a href="{link}"><strong>{s["brand"]}</strong></a><span class="station-legal">{s["name"]}</span>'
                 if s.get("brand") else f'<a href="{link}">{s["name"]}</a>')
        body.append(f'<tr><td class="rank">{i}</td><td>{label}</td>{muni}{cells}</tr>')
    return f'<div class="table-wrap"><table class="price-table"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def area_table(groups, lang, first_col, link_for):
    names = FUEL_EN if lang == "en" else FUEL_ES
    head = (f"<th>{first_col}</th><th class=\"num\">{'Stations' if lang == 'en' else 'Gasolineras'}</th>" +
            "".join(f'<th class="num">{names[f].split(" ")[0]}</th>' for f in FUELS))
    body = []
    for label, key, rows in groups:
        if not rows:
            continue
        link = link_for(key)
        name = f'<a href="{link}">{label}</a>' if link else label
        cells = "".join(f'<td class="num">{money(stats(rows, f)["avg"]) if stats(rows, f) else "–"}</td>' for f in FUELS)
        body.append(f'<tr><td>{name}</td><td class="num">{len(rows)}</td>{cells}</tr>')
    return f'<div class="table-wrap"><table class="price-table"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def cta(lang, campaign):
    h = "Road trip with family or friends?" if lang == "en" else "¿Viajan en varios autos?"
    p = ("Cerqa shows everyone's live location and arrival time on one map, so the whole group gets there together."
         if lang == "en" else
         "Cerqa muestra la ubicación en vivo y la hora de llegada de todos en un solo mapa, para que todo el grupo llegue junto.")
    return f"""<section class="app-cta">
  <h2>{h}</h2>
  <p>{p}</p>
  <div class="stores">
    <a href="{APP_STORE.format(cc='us' if lang == 'en' else 'mx')}" target="_blank" rel="noopener">App Store</a>
    <a href="{PLAY.format(campaign=campaign)}" target="_blank" rel="noopener">Google Play</a>
  </div>
</section>"""


def source(lang):
    if lang == "en":
        return ('<p class="source">Prices: what each station reported to Mexico\'s Comisión Nacional de Energía (CNE), open data. '
                'Prices can change during the day, so check at the pump. Brands: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. '
                'Municipal and state boundaries: <a href="https://www.geoboundaries.org/">geoBoundaries</a> (CC BY 4.0).</p>')
    return ('<p class="source">Precios: los que cada gasolinera reportó a la Comisión Nacional de Energía (CNE), datos abiertos. '
            'Pueden cambiar durante el día, confirma el precio en la bomba. Marcas: © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a>. '
            'Límites municipales y estatales: <a href="https://www.geoboundaries.org/">geoBoundaries</a> (CC BY 4.0).</p>')


def es_date(d):
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


ES_HUB = "/es/gasolina/"
EN_HUB = "/gas-prices-mexico/"


def state_path(adm1):
    return f"{ES_HUB}{STATE_PAGES[adm1]}/" if adm1 in STATE_PAGES else None


def city_path(adm1, slug):
    return f"{ES_HUB}{STATE_PAGES[adm1]}/{slug}/"


def city_links(lang, exclude=None):
    items = [f'<li><a href="{city_path(st, slug)}">{label}</a></li>' for _, st, slug, label in CITY_PAGES if slug != exclude]
    return '<ul class="link-list">' + "".join(items) + "</ul>"


def build(stations, today):
    pages = {}
    by_state = {}
    for s in stations:
        by_state.setdefault(s["state"], []).append(s)
    date_es = es_date(today)
    date_en = today.strftime("%B %-d, %Y")

    # National, Spanish
    groups = sorted(((STATE_NAMES[k], k, v) for k, v in by_state.items()), key=lambda g: g[0])
    body = f"""<h1>Precio de la gasolina hoy en México</h1>
<p class="lead">Precio promedio de Magna, Premium y Diésel en cada estado, con los precios que {len(stations):,} gasolineras reportaron a la Comisión Nacional de Energía (CNE). Actualizado el {date_es}.</p>
{summary_cards(stations, "es")}
<p class="note">Próximamente: precios de gasolina en estaciones de Estados Unidos.</p>
<h2>¿Por qué Cerqa muestra precios de gasolina?</h2>
<p>Para que sepas cuánto costará tu viaje antes de salir. Cerqa usa los precios de hoy y el rendimiento de tu auto para calcular la gasolina de tu ruta, suma las casetas y divide el total entre todos cuando viajan juntos.</p>
<h2>Precio promedio por estado</h2>
{area_table(groups, "es", "Estado", state_path)}
<h2>Precios por ciudad</h2>
{city_links("es")}
{cta("es", "gas_mx_es")}
{source("es")}"""
    pages[ES_HUB] = page("es", ES_HUB, "Precio de la gasolina hoy en México, por estado",
                         f"Precio promedio de la gasolina Magna, Premium y Diésel hoy en cada estado de México, con datos de la CNE. Actualizado el {date_es}.",
                         body, EN_HUB)

    # National, English
    body = f"""<h1>Gas prices in Mexico today</h1>
<p class="lead">Average price of Regular (Magna), Premium and Diesel in every Mexican state, in pesos per liter, from what {len(stations):,} stations reported to Mexico's energy regulator (CNE). Updated {date_en}.</p>
{summary_cards(stations, "en")}
<p class="note">Coming soon: gas prices at stations in the United States.</p>
<h2>Why Cerqa shows gas prices</h2>
<p>So you know what a trip will cost before you leave. Cerqa uses today's prices and your car's mileage to estimate the fuel for your route, adds the tolls, and splits the total per person when you travel together.</p>
<h2>Average price by state</h2>
{area_table(groups, "en", "State", state_path)}
<h2>Prices by city (in Spanish)</h2>
{city_links("en")}
{cta("en", "gas_mx_en")}
{source("en")}"""
    pages[EN_HUB] = page("en", EN_HUB, "Gas prices in Mexico today, by state",
                         f"Average price of Regular (Magna), Premium and Diesel today in every Mexican state, in pesos per liter, from CNE data. Updated {date_en}.",
                         body, ES_HUB)

    # State pages
    for adm1, slug in STATE_PAGES.items():
        rows = by_state.get(adm1, [])
        name = STATE_NAMES[adm1]
        by_muni = {}
        for s in rows:
            if s["muni"]:
                by_muni.setdefault(s["muni"], []).append(s)
        city_for = {m: city_path(st, sl) for m, st, sl, _ in CITY_PAGES if st == adm1}
        mgroups = sorted(((m, m, v) for m, v in by_muni.items()), key=lambda g: g[0])
        body = f"""<p class="crumbs"><a href="{ES_HUB}">Gasolina en México</a></p>
<h1>Precio de la gasolina en {name} hoy</h1>
<p class="lead">Precios que {len(rows)} gasolineras de {name} reportaron a la Comisión Nacional de Energía (CNE). Actualizado el {date_es}.</p>
{summary_cards(rows, "es")}
<h2>Las 15 gasolineras con la Magna más barata en {name}</h2>
{station_table(sorted(rows, key=lambda s: s["prices"].get("regular", 99))[:15], "regular", "es", show_muni=True)}
<h2>Precio promedio por municipio</h2>
{area_table(mgroups, "es", "Municipio", lambda m: city_for.get(m))}
{cta("es", f"gas_{slug}_es")}
{source("es")}"""
        p = state_path(adm1)
        pages[p] = page("es", p, f"Precio de la gasolina en {name} hoy",
                        f"Precio de la gasolina Magna, Premium y Diésel hoy en {name}: promedio, las gasolineras más baratas y el precio por municipio. Datos de la CNE, {date_es}.",
                        body)

    # City pages
    for muni, adm1, slug, label in CITY_PAGES:
        rows = [s for s in by_state.get(adm1, []) if s["muni"] == muni]
        if not rows:
            continue
        sname = STATE_NAMES[adm1]
        cheapest = sorted(rows, key=lambda s: s["prices"].get("regular", 99))[:15]
        diesel = sorted([s for s in rows if "diesel" in s["prices"]], key=lambda s: s["prices"]["diesel"])[:10]
        place = label if label == sname else f"{label}, {sname}"
        body = f"""<p class="crumbs"><a href="{ES_HUB}">Gasolina en México</a> › <a href="{state_path(adm1)}">{sname}</a></p>
<h1>Precio de la gasolina en {label} hoy</h1>
<p class="lead">Precios que {len(rows)} gasolineras de {place} reportaron a la Comisión Nacional de Energía (CNE). Actualizado el {date_es}.</p>
{summary_cards(rows, "es")}
<h2>Las {len(cheapest)} gasolineras con la Magna más barata en {label}</h2>
{station_table(cheapest, "regular", "es")}
{f'<h2>Diésel más barato en {label}</h2>' + station_table(diesel, "diesel", "es") if diesel else ""}
<p class="note">Toca una gasolinera para abrirla en Cerqa con su ubicación.</p>
<h2>Otras ciudades</h2>
{city_links("es", exclude=slug)}
{cta("es", f"gas_{slug.replace('-', '_')}_es")}
{source("es")}"""
        p = city_path(adm1, slug)
        pages[p] = page("es", p, f"Precio de la gasolina en {label} hoy",
                        f"Precio de la gasolina Magna, Premium y Diésel hoy en {place}: promedio y las gasolineras más baratas. Datos de la CNE, {date_es}.",
                        body)
    return pages


def update_sitemap(paths, today):
    p = "sitemap.xml"
    s = open(p).read()
    d = today.isoformat()
    for path in paths:
        url = SITE + path
        if f"<loc>{url}</loc>" in s:
            s = re.sub(rf"(<loc>{re.escape(url)}</loc><lastmod>)[^<]*", rf"\g<1>{d}", s)
        else:
            alt = ""
            if path in (ES_HUB, EN_HUB):
                alt = (f'\n    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{EN_HUB}"/>'
                       f'\n    <xhtml:link rel="alternate" hreflang="es" href="{SITE}{ES_HUB}"/>'
                       f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{EN_HUB}"/>')
            s = s.replace("</urlset>", f"  <url><loc>{url}</loc><lastmod>{d}</lastmod>{alt}\n  </url>\n</urlset>")
    open(p, "w").write(s)


if __name__ == "__main__":
    GA = analytics()
    today = datetime.datetime.now(ZoneInfo("America/Mexico_City")).date()
    stations, _ = load_stations()
    pages = build(stations, today)
    for path, html in pages.items():
        out = path.strip("/") + "/index.html"
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(html)
        print("wrote", out)
    update_sitemap(list(pages), today)
    print(f"{len(stations)} stations")
