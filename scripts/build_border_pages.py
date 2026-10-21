#!/usr/bin/env python3
"""Builds the US-Mexico border wait pages (English + Spanish).

Static HTML: the crossing names, hours and explanations are in the page for search engines, and
assets/border.js fills in the live waits from CBP in the visitor's browser (no Cerqa server).
Run from the repo root after editing:  python3 scripts/build_border_pages.py
Then add any new pages to sitemap.xml.
"""
import os
import re

SITE = "https://cerqa.app"
EN_HUB = "/border-wait-times/"
ES_HUB = "/es/garitas/"
APP_STORE = "https://apps.apple.com/{cc}/app/cerqa-app/id6762389261"
PLAY = ("https://play.google.com/store/apps/details?id=com.cerqa.app&amp;referrer="
        "utm_source%3Dcerqa.app%26utm_medium%3Dweb%26utm_campaign%3D{campaign}")

# Hub groups: (CBP port number, name, Mexican city). Passenger crossings only.
GROUPS = [
    (("California", "California"), [
        ("250401", "San Ysidro", "Tijuana"),
        ("250407", "San Ysidro PedWest", "Tijuana"),
        ("250601", "Otay Mesa", "Tijuana"),
        ("250409", "Cross Border Xpress (CBX)", "Tijuana"),
        ("250501", "Tecate", "Tecate"),
        ("250302", "Calexico West", "Mexicali"),
        ("250301", "Calexico East", "Mexicali"),
        ("250201", "Andrade", "Los Algodones"),
    ]),
    (("Arizona", "Arizona"), [
        ("260801", "San Luis I", "San Luis Río Colorado"),
        ("260802", "San Luis II", "San Luis Río Colorado"),
        ("260201", "Lukeville", "Sonoyta"),
        ("260401", "Nogales DeConcini", "Nogales"),
        ("260402", "Nogales Mariposa", "Nogales"),
        ("260403", "Nogales Morley Gate", "Nogales"),
        ("260301", "Naco", "Naco"),
        ("260101", "Douglas", "Agua Prieta"),
    ]),
    (("New Mexico and West Texas", "Nuevo México y oeste de Texas"), [
        ("240601", "Columbus", "Puerto Palomas"),
        ("240801", "Santa Teresa", "San Jerónimo"),
        ("240201", "El Paso Bridge of the Americas", "Ciudad Juárez"),
        ("240202", "El Paso Paso del Norte", "Ciudad Juárez"),
        ("240203", "El Paso Ysleta", "Ciudad Juárez"),
        ("240204", "El Paso Stanton", "Ciudad Juárez"),
        ("240401", "Tornillo (Marcelino Serna)", "Guadalupe"),
        ("l24501", "Fort Hancock", "El Porvenir"),
        ("240301", "Presidio", "Ojinaga"),
    ]),
    (("Texas", "Texas"), [
        ("230201", "Del Rio", "Ciudad Acuña"),
        ("230301", "Eagle Pass Bridge I", "Piedras Negras"),
        ("230302", "Eagle Pass Bridge II", "Piedras Negras"),
        ("230401", "Laredo Bridge I", "Nuevo Laredo"),
        ("230402", "Laredo Bridge II", "Nuevo Laredo"),
        ("230403", "Laredo Colombia Solidarity", "Colombia, Nuevo León"),
        ("231001", "Roma", "Ciudad Miguel Alemán"),
        ("230701", "Rio Grande City", "Camargo"),
        ("230503", "Anzalduas", "Reynosa"),
        ("230501", "Hidalgo", "Reynosa"),
        ("230502", "Pharr", "Reynosa"),
        ("230902", "Donna", "Río Bravo"),
        ("230901", "Progreso", "Nuevo Progreso"),
        ("535503", "Los Indios", "Matamoros"),
        ("535502", "Brownsville Veterans", "Matamoros"),
        ("535504", "Brownsville Gateway", "Matamoros"),
        ("535501", "Brownsville B&M", "Matamoros"),
    ]),
]

LANES_EN = """
<h2>Which lane can I use?</h2>
<div class="prose">
<ul>
<li><strong>General lanes</strong> are open to everyone.</li>
<li><strong>SENTRI</strong> lanes are only for trusted travelers. Everyone in the car needs a SENTRI card.</li>
<li><strong>Ready Lane</strong> is for travelers whose documents have an RFID chip, such as a passport card, a newer Border Crossing Card or an enhanced driver's license. Everyone in the car needs one.</li>
</ul>
</div>"""

LANES_ES = """
<h2>¿Qué carril puedo usar?</h2>
<div class="prose">
<ul>
<li><strong>Carriles generales:</strong> para todos.</li>
<li><strong>SENTRI:</strong> solo para viajeros confiables. Todos en el auto necesitan tarjeta SENTRI.</li>
<li><strong>Ready Lane:</strong> para quienes traen documentos con chip RFID, como pasaporte en tarjeta (passport card), visa láser reciente o licencia mejorada. Todos en el auto necesitan uno.</li>
</ul>
</div>"""

# Crossing pages. "nearby" lists other Tijuana-area crossings to compare.
CROSSINGS = [
    {
        "slug": "san-ysidro", "port": "250401", "extra_ports": ["250407"],
        "en": {
            "title": "San Ysidro border wait time, live",
            "h1": "San Ysidro border wait time",
            "desc": "Live San Ysidro wait to enter the US from Tijuana: general, SENTRI and Ready Lane for cars, plus walking, from CBP.",
            "lead": "Live wait to enter the United States from Tijuana, from US Customs and Border Protection (CBP).",
            "about": """<p>San Ysidro connects Tijuana with San Diego and is the busiest land border crossing in the Western Hemisphere. Car lanes are open 24 hours.</p>
<p>People on foot cross at PedEast or at PedWest, which keeps shorter hours. Both are shown below.</p>""",
            "extra_title": "Walking at PedWest",
        },
        "es": {
            "title": "Garita de San Ysidro: tiempo de espera en vivo",
            "h1": "Garita de San Ysidro: tiempo de espera",
            "desc": "Tiempo de espera en vivo en la garita de San Ysidro para cruzar de Tijuana a EE. UU.: carril general, SENTRI y Ready Lane, y peatones. Datos de CBP.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Tijuana, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>San Ysidro une Tijuana con San Diego y es el cruce fronterizo terrestre con más tráfico del continente. Los carriles para autos abren las 24 horas.</p>
<p>Los peatones cruzan por PedEast o por PedWest, que tiene un horario más corto. Abajo ves los dos.</p>""",
            "extra_title": "Peatones en PedWest",
        },
    },
    {
        "slug": "otay-mesa", "port": "250601",
        "en": {
            "title": "Otay Mesa border wait time, live",
            "h1": "Otay Mesa border wait time",
            "desc": "Live Otay Mesa wait to enter the US from Tijuana: general, SENTRI and Ready Lane for cars, plus walking, from CBP.",
            "lead": "Live wait to enter the United States from Tijuana at Otay Mesa, from US Customs and Border Protection (CBP).",
            "about": """<p>Otay Mesa is about 6 miles east of San Ysidro, near the Tijuana airport. The passenger crossing is open 24 hours, and trucks use a separate commercial crossing.</p>
<p>Many drivers check Otay Mesa and San Ysidro together and pick the shorter wait.</p>""",
        },
        "es": {
            "title": "Garita de Otay: tiempo de espera en vivo",
            "h1": "Garita de Otay: tiempo de espera",
            "desc": "Tiempo de espera en vivo en la garita de Otay para cruzar de Tijuana a EE. UU.: carril general, SENTRI y Ready Lane, y peatones. Datos de CBP.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Tijuana por Otay, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>La garita de Otay está a unos 10 km al este de San Ysidro, cerca del aeropuerto de Tijuana. El cruce de pasajeros abre las 24 horas y los camiones de carga usan un cruce comercial aparte.</p>
<p>Mucha gente revisa Otay y San Ysidro al mismo tiempo y escoge la que tenga menos espera.</p>""",
        },
    },
    {
        "slug": "cbx", "port": "250409",
        "en": {
            "title": "CBX wait time (Cross Border Xpress), live",
            "h1": "Cross Border Xpress (CBX) wait time",
            "desc": "Live CBX wait to walk from Tijuana airport into San Diego, from CBP. Who can use Cross Border Xpress and what you need.",
            "lead": "Live wait to walk from Tijuana International Airport into the United States, from US Customs and Border Protection (CBP).",
            "about": """<p>Cross Border Xpress is a walkway from Tijuana International Airport (TIJ) to a terminal on the San Diego side, in Otay Mesa. It's only for airline passengers: you need a boarding pass for a flight in or out of TIJ and a CBX ticket.</p>
<p>CBP reports a walking wait only, since there are no car lanes.</p>""",
        },
        "es": {
            "title": "CBX: tiempo de espera en vivo (Cross Border Xpress)",
            "h1": "Cross Border Xpress (CBX): tiempo de espera",
            "desc": "Tiempo de espera en vivo en CBX para cruzar a pie del aeropuerto de Tijuana a San Diego. Datos de CBP y quién puede usar Cross Border Xpress.",
            "lead": "Tiempo de espera en vivo para cruzar a pie del Aeropuerto Internacional de Tijuana a Estados Unidos, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>Cross Border Xpress es un puente peatonal que une el Aeropuerto Internacional de Tijuana (TIJ) con una terminal del lado de San Diego, en Otay Mesa. Es solo para pasajeros: necesitas pase de abordar de un vuelo que llegue o salga de TIJ y un boleto de CBX.</p>
<p>CBP solo reporta la espera a pie, porque no hay carriles para autos.</p>""",
        },
    },
    {
        "slug": "tecate", "port": "250501",
        "en": {
            "title": "Tecate border wait time, live",
            "h1": "Tecate border wait time",
            "desc": "Live Tecate wait to enter the US from Tecate, Baja California, from CBP. Hours, lanes and nearby Tijuana crossings.",
            "lead": "Live wait to enter the United States from Tecate, Baja California, from US Customs and Border Protection (CBP).",
            "about": """<p>Tecate is a smaller crossing about 30 miles east of Otay Mesa, between Tecate, Baja California and Tecate, California. It isn't open overnight, so check the hours below before you go.</p>
<p>When Tijuana crossings are busy, the drive to Tecate can be worth it.</p>""",
        },
        "es": {
            "title": "Garita de Tecate: tiempo de espera en vivo",
            "h1": "Garita de Tecate: tiempo de espera",
            "desc": "Tiempo de espera en vivo en la garita de Tecate para cruzar a EE. UU. Datos de CBP, horario, carriles y garitas cercanas de Tijuana.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Tecate, Baja California, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>Tecate es una garita más pequeña, a unos 50 km al este de Otay, entre Tecate, Baja California y Tecate, California. No abre de noche, así que revisa el horario abajo antes de salir.</p>
<p>Cuando las garitas de Tijuana están llenas, a veces vale la pena manejar a Tecate.</p>""",
        },
    },
]

TIJUANA_AREA = [("san-ysidro", "250401", "San Ysidro"), ("otay-mesa", "250601", "Otay Mesa"),
                ("cbx", "250409", "Cross Border Xpress (CBX)"), ("tecate", "250501", "Tecate")]
PAGE_FOR_PORT = {port: slug for slug, port, _ in TIJUANA_AREA}

TEXT = {
    "en": {
        "hub_title": "US-Mexico border wait times, live",
        "hub_h1": "US-Mexico border wait times",
        "hub_desc": "Live wait times at every US-Mexico border crossing into the US, from CBP: San Ysidro, Otay Mesa, CBX, Calexico, Nogales, El Paso, Laredo and more.",
        "hub_lead": "Live waits to enter the United States at every crossing from Mexico, from US Customs and Border Protection (CBP). The number shown is the general car lane, or the walking wait where there are no car lanes.",
        "crumb": "Border wait times",
        "lang_name": "Español", "lang_attr": "es",
        "loading": "Loading live wait from CBP…",
        "noscript": "Turn on JavaScript to see the live wait.",
        "southbound": "These are waits to enter the United States. No official wait times are published for going into Mexico.",
        "nearby": "Other Tijuana crossings",
        "all": "All border crossings",
        "about": "About this crossing",
        "source": 'Wait times: <a href="https://bwt.cbp.gov/">U.S. Customs and Border Protection</a>. They\'re CBP estimates, usually updated about once an hour, and can change quickly. The page refreshes on its own every 5 minutes.',
        "cta_h": "Crossing with family or friends?",
        "cta_p": "Cerqa shows everyone's live location and arrival time on one map, so nobody gets lost on the other side.",
        "cc": "us",
        "footer": [("/feedback", "Feedback"), ("/support/", "Support"), ("/privacy/en/", "Privacy Policy"), ("/terms/en/", "Terms of Service")],
        "home": "/",
    },
    "es": {
        "hub_title": "Tiempos de espera en las garitas, en vivo",
        "hub_h1": "Tiempos de espera en las garitas",
        "hub_desc": "Tiempos de espera en vivo en todas las garitas para cruzar de México a EE. UU., según CBP: San Ysidro, Otay, CBX, Calexico, Nogales, Ciudad Juárez, Nuevo Laredo y más.",
        "hub_lead": "Tiempos de espera en vivo para entrar a Estados Unidos en cada garita de la frontera, según la Oficina de Aduanas y Protección Fronteriza (CBP). El número es el carril general para autos, o la espera a pie donde no hay carriles para autos.",
        "crumb": "Garitas",
        "lang_name": "English", "lang_attr": "en",
        "loading": "Cargando el tiempo de espera de CBP…",
        "noscript": "Activa JavaScript para ver el tiempo de espera en vivo.",
        "southbound": "Estos son los tiempos para entrar a Estados Unidos. No hay tiempos oficiales publicados para entrar a México.",
        "nearby": "Otras garitas de Tijuana",
        "all": "Todas las garitas",
        "about": "Sobre esta garita",
        "source": 'Tiempos de espera: <a href="https://bwt.cbp.gov/">Oficina de Aduanas y Protección Fronteriza de EE. UU. (CBP)</a>. Son estimados de CBP, normalmente se actualizan cada hora y pueden cambiar rápido. La página se actualiza sola cada 5 minutos.',
        "cta_h": "¿Cruzas con familia o amigos?",
        "cta_p": "Cerqa muestra la ubicación en vivo y la hora de llegada de todos en un solo mapa, para que nadie se pierda del otro lado.",
        "cc": "mx",
        "footer": [("/es/comentarios/", "Comentarios"), ("/support/", "Ayuda"), ("/privacy/es/", "Aviso de privacidad"), ("/terms/es/", "Términos del servicio")],
        "home": "/es/",
    },
}


def analytics():
    s = open("index.html").read()
    m = re.search(r"\s*<!-- Google Analytics 4.*?</script>", s, re.S)
    return m.group(0)


GA = None


def page(lang, path, alt_path, title, desc, body, og_image):
    t = TEXT[lang]
    en_path, es_path = (path, alt_path) if lang == "en" else (alt_path, path)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Cerqa</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">
<link rel="alternate" hreflang="en" href="{SITE}{en_path}">
<link rel="alternate" hreflang="es" href="{SITE}{es_path}">
<link rel="alternate" hreflang="x-default" href="{SITE}{en_path}">
<link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
<link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
<meta name="apple-itunes-app" content="app-id=6762389261">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Cerqa">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/social/{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/border.css">{GA}
</head>
<body>
<nav class="site-nav">
  <a class="site-nav-brand" href="{t['home']}">Cerqa</a>
  <a class="site-nav-lang" href="{alt_path}" hreflang="{t['lang_attr']}" lang="{t['lang_attr']}">{t['lang_name']}</a>
</nav>
<main>
{body}
</main>
<footer>
  <p>© 2026 Cerqa</p>
  {' '.join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
</footer>
<script src="/assets/border.js" defer></script>
</body>
</html>
"""


def cta(lang, campaign):
    t = TEXT[lang]
    return f"""<section class="app-cta">
  <h2>{t['cta_h']}</h2>
  <p>{t['cta_p']}</p>
  <div class="stores">
    <a href="{APP_STORE.format(cc=t['cc'])}" target="_blank" rel="noopener">App Store</a>
    <a href="{PLAY.format(campaign=campaign)}" target="_blank" rel="noopener">Google Play</a>
  </div>
</section>"""


def hub_path(lang):
    return EN_HUB if lang == "en" else ES_HUB


def crossing_li(lang, port, name, city, link=True):
    slug = PAGE_FOR_PORT.get(port)
    label = f'<a href="{hub_path(lang)}{slug}/">{name}</a>' if (slug and link) else name
    return (f'<li><span class="crossing-name">{label}<span class="crossing-sub">{city}</span></span>'
            f'<span class="crossing-wait" data-port="{port}" data-mode="row">…</span></li>')


def build_hub(lang):
    t = TEXT[lang]
    sections = []
    for (en_name, es_name), items in GROUPS:
        lis = "\n".join(crossing_li(lang, p, n, c) for p, n, c in items)
        sections.append(f"<h2>{en_name if lang == 'en' else es_name}</h2>\n<ul class=\"crossing-list\">\n{lis}\n</ul>")
    body = f"""<h1>{t['hub_h1']}</h1>
<p class="lead">{t['hub_lead']}</p>
<noscript><p class="note">{t['noscript']}</p></noscript>
{chr(10).join(sections)}
<p class="note">{t['southbound']}</p>
{cta(lang, f"border_hub_{lang}")}
<p class="source">{t['source']}</p>"""
    path = hub_path(lang)
    alt = hub_path("es" if lang == "en" else "en")
    return path, page(lang, path, alt, t["hub_title"], t["hub_desc"], body, f"cerqa-{lang}.jpg")


def build_crossing(lang, c):
    t = TEXT[lang]
    x = c[lang]
    extra = ""
    for port in c.get("extra_ports", []):
        extra += f"""<h2>{x['extra_title']}</h2>
<div class="wait-card" data-port="{port}" data-mode="detail"><p class="wait-loading">{t['loading']}</p></div>"""
    nearby = "\n".join(crossing_li(lang, p, n, "Tijuana" if s != "tecate" else "Tecate")
                       for s, p, n in TIJUANA_AREA if s != c["slug"])
    body = f"""<p class="crumbs"><a href="{hub_path(lang)}">{t['crumb']}</a></p>
<h1>{x['h1']}</h1>
<p class="lead">{x['lead']}</p>
<div class="wait-card" data-port="{c['port']}" data-mode="detail"><p class="wait-loading">{t['loading']}</p></div>
<noscript><p class="note">{t['noscript']}</p></noscript>
{extra}
<p class="note">{t['southbound']}</p>
<h2>{t['about']}</h2>
<div class="prose">{x['about']}</div>
{LANES_EN if lang == 'en' else LANES_ES}
<h2>{t['nearby']}</h2>
<ul class="crossing-list">
{nearby}
</ul>
<p style="margin-top:12px"><a href="{hub_path(lang)}">{t['all']}</a></p>
{cta(lang, f"border_{c['slug'].replace('-', '_')}_{lang}")}
<p class="source">{t['source']}</p>"""
    path = f"{hub_path(lang)}{c['slug']}/"
    alt = f"{hub_path('es' if lang == 'en' else 'en')}{c['slug']}/"
    return path, page(lang, path, alt, x["title"], x["desc"], body, f"cerqa-{lang}.jpg")


def write(path, html):
    out = path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(html)
    print("wrote", out)


if __name__ == "__main__":
    GA = analytics()
    for lang in ("en", "es"):
        write(*build_hub(lang))
        for c in CROSSINGS:
            write(*build_crossing(lang, c))
