#!/usr/bin/env python3
"""Builds the home page in English (/index.html) and Spanish (/es/index.html) from one template,
so the two stay in sync. Edit the text here, then run from the repo root:
    python3 scripts/build_home.py
Styles live in assets/home.css.
"""
import re

SITE = "https://cerqa.app"
APP_STORE = "https://apps.apple.com/{cc}/app/cerqa-app/id6762389261"
PLAY = ("https://play.google.com/store/apps/details?id=com.cerqa.app&amp;referrer="
        "utm_source%3Dcerqa.app%26utm_medium%3Dweb%26utm_campaign%3D{campaign}")

ICON_PEOPLE = '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>'
ICON_NAV = '<svg viewBox="0 0 24 24"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg>'
ICON_TRIP = '<svg viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm-7-8.5c-1.38 0-2.5 1.12-2.5 2.5 0 1.88 2.5 4.5 2.5 4.5s2.5-2.62 2.5-4.5c0-1.38-1.12-2.5-2.5-2.5z"/></svg>'

SHOTS = [  # (file, ios file) shown as iPhone + Android pairs
    ("01-home", "01-home"),
    ("02-group-sharing-map", "02-group-sharing-map"),
    ("04-shared-nav", "04-shared-nav"),
    ("08-group-nav", "08-group-nav"),
    ("06-trip-details", "06-trip-details"),
    ("10-compass", "10-compass"),
]

T = {
    "en": {
        "path": "/", "alt": "/es/", "lang_link": "Español", "planner_nav": "Trip Planner", "cc": "us", "campaign": "home_en",
        "title": "Cerqa | Live location and group navigation for road trips",
        "desc": "Share live location, see everyone's arrival time and navigate together. Cerqa keeps family and friends together on road trips, meetups and group drives. Free on iPhone and Android.",
        "og_title": "Cerqa: get everyone there",
        "og_desc": "Live location, arrival times and group navigation for family and friends.",
        "og_locale": ("en_US", "es_MX"),
        "h1": "Get everyone there.",
        "sub": "See where everyone is, when they'll arrive, and navigate together. For road trips, meetups and every drive in between.",
        "fine": "Free on iPhone and Android. Works with Apple CarPlay.",
        "apple_badge": "/images/badges/app-store-en-us.svg", "google_badge": "/images/badges/google-play-en.png",
        "apple_alt": "Download on the App Store", "google_alt": "Get it on Google Play",
        "phones_alt": ("Group location sharing map on Android", "Group location sharing map on iPhone"),
        "benefits_h": "One map for the whole group",
        "benefits_p": "No more \"where are you?\" texts.",
        "benefits": [
            (ICON_PEOPLE, "See everyone, live", "Share your location with a friend or a group for an hour or a whole day, and see everyone on one map."),
            (ICON_NAV, "Arrive together", "Turn-by-turn directions with your group on the map. See who's ahead, who's behind and when everyone gets there."),
            (ICON_TRIP, "Plan the trip", "Stops, people and the group chat in one trip, from your phone or your computer."),
        ],
        "videos_h": "See it in motion",
        "videos_p": "Real screens from the app.",
        "videos": [
            ("group-navigation-pro", "Navigate with your group", "Directions with your whole group on the map, so you know who's ahead, behind or already there."),
            ("shared-trip-meet-up-android-group", "Share with a group", "Start a timed share, pick who's in, and agree on a place to meet."),
            ("cruise-mode", "Cruise", "Stop ideas along your drive, from scenic routes to attractions, one tap away."),
        ],
        "shots_h": "Built for iPhone and Android",
        "shots_p": "The same app on both, so the whole group can use it.",
        "shots": [
            ("Your trips, front and center", "Upcoming trips at a glance: where, when and who's going."),
            ("See everyone at once", "Friends show up live on the map as soon as they share."),
            ("Navigate while you share", "Turn-by-turn directions while your group keeps seeing where you are."),
            ("Never lose your group", "See friends on the road around you, ahead or behind."),
            ("Every stop, planned", "The route, the stops and who's going, then start in one tap."),
            ("Distance and direction", "Point your phone to find each friend and see how far away they are."),
        ],
        "tools_h": "Useful for the road",
        "tools_p": "Free pages you can use without the app.",
        "tools": [
            ("/border-wait-times/", "US-Mexico border wait times", "Live waits at every crossing into the US, from CBP: San Ysidro, Otay Mesa, CBX and more.", "See wait times"),
            ("/gas-prices-mexico/", "Gas prices in Mexico", "Today's average price by state and city, and the cheapest stations near you. Coming soon for stations in the United States.", "See gas prices"),
        ],
        "planner_h": "Plan trips from your computer",
        "planner_p": "Sign in at ride.cerqa.app to set up a trip with stops and invite your friends. Everyone you add sees it on the Home screen of the app.",
        "planner_link": "Open the trip planner",
        "planner_alt": "Creating a group trip with stops and a route on the Cerqa web trip planner",
        "carplay_h": "Apple CarPlay",
        "carplay_p": "Keep your group on your car's screen, hands free.",
        "plans_h": "Free and Pro",
        "plans_p": "Cerqa is free to use. Pro is for groups that travel together a lot.",
        "plans_cols": ("", "Free", "Pro"),
        "plans": [
            ("Share your location with friends and groups", True, True),
            ("Sharing time", "Up to 1 hour", "Up to 24 hours"),
            ("People per group", "Up to 5", "Up to 25"),
            ("Join trips you're invited to", True, True),
            ("Create trips", False, True),
            ("Navigate together as a group", False, True),
            ("Voice Co-Pilot", False, True),
            ("No ads", False, True),
        ],
        "plans_note": "You can upgrade to Pro in the app.",
        "final_h": "Your next trip starts here",
        "final_p": "Get Cerqa free and invite the people you travel with.",
        "footer": [("/feedback", "Feedback"), ("/support/", "Support"), ("/privacy/en/", "Privacy Policy"),
                   ("/terms/en/", "Terms of Service"), ("/border-wait-times/", "Border wait times"),
                   ("/gas-prices-mexico/", "Gas prices in Mexico")],
        "credits": 'Map data © <a href="https://www.mapbox.com/about/maps/">Mapbox</a>, © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Gas prices: Comisión Nacional de Energía (CNE). EV chargers: <a href="https://openchargemap.org">Open Charge Map</a> (CC BY 4.0). Border waits: U.S. Customs and Border Protection.',
        "ld_desc": "Live location sharing, arrival times and group navigation for family and friends.",
        "currency": "USD",
    },
    "es": {
        "path": "/es/", "alt": "/", "lang_link": "English", "planner_nav": "Planear viaje", "cc": "mx", "campaign": "home_es",
        "title": "Cerqa | Ubicación en vivo y navegación en grupo para viajes en carretera",
        "desc": "Comparte tu ubicación en vivo, ve a qué hora llega cada quien y naveguen juntos. Cerqa mantiene unidos a familia y amigos en viajes en carretera, reuniones y caravanas. Gratis en iPhone y Android.",
        "og_title": "Cerqa: que todos lleguen",
        "og_desc": "Ubicación en vivo, horas de llegada y navegación en grupo para familia y amigos.",
        "og_locale": ("es_MX", "en_US"),
        "h1": "Que todos lleguen.",
        "sub": "Ve dónde está cada quien, a qué hora llega, y naveguen juntos. Para viajes en carretera, reuniones y cualquier salida.",
        "fine": "Gratis en iPhone y Android. Funciona con Apple CarPlay.",
        "apple_badge": "/images/badges/app-store-es-mx.svg", "google_badge": "/images/badges/google-play-es.png",
        "apple_alt": "Descárgalo en el App Store", "google_alt": "Disponible en Google Play",
        "phones_alt": ("Mapa con la ubicación del grupo en Android", "Mapa con la ubicación del grupo en iPhone"),
        "benefits_h": "Un solo mapa para todo el grupo",
        "benefits_p": "Se acabaron los mensajes de \"¿dónde vienes?\".",
        "benefits": [
            (ICON_PEOPLE, "Ve a todos en vivo", "Comparte tu ubicación con un amigo o un grupo por una hora o un día entero, y ve a todos en un solo mapa."),
            (ICON_NAV, "Lleguen juntos", "Indicaciones paso a paso con tu grupo en el mapa. Ve quién va adelante, quién atrás y a qué hora llega cada quien."),
            (ICON_TRIP, "Planeen el viaje", "Paradas, invitados y el chat del grupo en un solo viaje, desde tu celular o tu computadora."),
        ],
        "videos_h": "Míralo en movimiento",
        "videos_p": "Pantallas reales de la app.",
        "videos": [
            ("group-navigation-pro", "Navega con tu grupo", "Indicaciones con todo tu grupo en el mapa: quién va adelante, quién atrás y quién ya llegó."),
            ("shared-trip-meet-up-android-group", "Comparte con un grupo", "Comparte por un tiempo, elige quién participa y pónganse de acuerdo dónde verse."),
            ("cruise-mode", "Cruise", "Ideas de paradas en el camino, de rutas escénicas a atracciones, a un toque."),
        ],
        "shots_h": "Para iPhone y Android",
        "shots_p": "La misma app en los dos, para que todo el grupo la use.",
        "shots": [
            ("Tus viajes, a la vista", "Tus próximos viajes de un vistazo: a dónde, cuándo y quién va."),
            ("Ve a todos a la vez", "Tus amigos aparecen en vivo en el mapa en cuanto comparten."),
            ("Navega mientras compartes", "Indicaciones paso a paso mientras tu grupo sigue viendo dónde estás."),
            ("No pierdas a tu grupo", "Ve a tus amigos en la carretera, adelante o atrás."),
            ("Cada parada, planeada", "La ruta, las paradas y quién va, y empieza con un toque."),
            ("Distancia y dirección", "Apunta tu teléfono para encontrar a cada amigo y ver qué tan lejos está."),
        ],
        "tools_h": "Útil para el camino",
        "tools_p": "Páginas gratis que puedes usar sin la app.",
        "tools": [
            ("/es/gasolina/", "Precio de la gasolina hoy", "Precio promedio por estado y ciudad, y las gasolineras más baratas. Próximamente también en Estados Unidos.", "Ver precios"),
            ("/es/garitas/", "Tiempos de espera en las garitas", "Espera en vivo para cruzar a EE. UU. en cada garita, según CBP: San Ysidro, Otay, CBX y más.", "Ver tiempos"),
        ],
        "planner_h": "Planea viajes desde tu computadora",
        "planner_p": "Entra a ride.cerqa.app para armar un viaje con paradas e invitar a tus amigos. Todos los que agregues lo ven en la pantalla de Inicio de la app.",
        "planner_link": "Abrir el planeador de viajes",
        "planner_alt": "Creando un viaje en grupo con paradas y ruta en el planeador web de Cerqa",
        "carplay_h": "Apple CarPlay",
        "carplay_p": "Tu grupo en la pantalla de tu auto, sin usar las manos.",
        "plans_h": "Gratis y Pro",
        "plans_p": "Cerqa es gratis. Pro es para grupos que viajan juntos seguido.",
        "plans_cols": ("", "Gratis", "Pro"),
        "plans": [
            ("Comparte tu ubicación con amigos y grupos", True, True),
            ("Tiempo para compartir", "Hasta 1 hora", "Hasta 24 horas"),
            ("Personas por grupo", "Hasta 5", "Hasta 25"),
            ("Únete a viajes a los que te invitan", True, True),
            ("Crea viajes", False, True),
            ("Naveguen juntos como grupo", False, True),
            ("Voice Co-Pilot", False, True),
            ("Sin anuncios", False, True),
        ],
        "plans_note": "Puedes cambiarte a Pro desde la app.",
        "final_h": "Tu próximo viaje empieza aquí",
        "final_p": "Descarga Cerqa gratis e invita a las personas con las que viajas.",
        "footer": [("/feedback", "Comentarios"), ("/support/", "Ayuda"), ("/privacy/es/", "Aviso de privacidad"),
                   ("/terms/es/", "Términos del servicio"), ("/es/garitas/", "Tiempos en garitas"),
                   ("/es/gasolina/", "Precio de la gasolina")],
        "credits": 'Datos del mapa © <a href="https://www.mapbox.com/about/maps/">Mapbox</a>, © <a href="https://www.openstreetmap.org/copyright">colaboradores de OpenStreetMap</a>. Precios de gasolina: Comisión Nacional de Energía (CNE). Cargadores eléctricos: <a href="https://openchargemap.org">Open Charge Map</a> (CC BY 4.0). Tiempos en garitas: Oficina de Aduanas y Protección Fronteriza de EE. UU. (CBP).',
        "ld_desc": "Ubicación en vivo, horas de llegada y navegación en grupo para familia y amigos.",
        "currency": "MXN",
    },
}


def analytics():
    s = open("index.html").read()
    return re.search(r"\s*<!-- Google Analytics 4.*?</script>", s, re.S).group(0)


def badges(t, campaign):
    return f"""<div class="store-badges">
      <a href="{APP_STORE.format(cc=t['cc'])}" target="_blank" rel="noopener"><img class="badge-apple" src="{t['apple_badge']}" alt="{t['apple_alt']}" width="156" height="52"></a>
      <a href="{PLAY.format(campaign=campaign)}" target="_blank" rel="noopener"><img class="badge-google" src="{t['google_badge']}" alt="{t['google_alt']}" width="175" height="52"></a>
    </div>"""


def cell(v):
    if v is True:
        return '<td class="c yes">✓</td>'
    if v is False:
        return '<td class="c no">–</td>'
    return f'<td class="c">{v}</td>'


def build(lang, ga):
    t = T[lang]
    benefits = "\n".join(f"""      <div class="benefit">
        <div class="benefit-icon">{icon}</div>
        <h3>{h}</h3>
        <p>{p}</p>
      </div>""" for icon, h, p in t["benefits"])
    videos = "\n".join(f"""      <div class="video-card">
        <div class="video-frame">
          <video muted loop playsinline preload="none" poster="/images/posters/{v}.jpg" data-src="/videos/{v}.mp4"></video>
        </div>
        <p class="feature-label">{h}</p>
        <p class="video-caption">{p}</p>
      </div>""" for v, h, p in t["videos"])
    shots = "\n".join(f"""      <figure class="shot">
        <div class="shot-pair">
          <img src="/images/screens/ios/{ios}.webp" width="560" height="1138" loading="lazy" alt="{h} (iPhone)">
          <img src="/images/screens/android/{android}.webp" width="560" height="1143" loading="lazy" alt="{h} (Android)">
        </div>
        <figcaption><h3>{h}</h3><p>{p}</p></figcaption>
      </figure>""" for (android, ios), (h, p) in zip(SHOTS, t["shots"]))
    tools = "\n".join(f"""      <a class="tool" href="{href}">
        <h3>{h}</h3>
        <p>{p}</p>
        <span class="go">{go} →</span>
      </a>""" for href, h, p, go in t["tools"])
    plan_rows = "\n".join(f"          <tr><td>{name}</td>{cell(free)}{cell(pro)}</tr>" for name, free, pro in t["plans"])
    other = "es" if lang == "en" else "en"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t['title']}</title>
  <meta name="description" content="{t['desc']}">
  <link rel="canonical" href="{SITE}{t['path']}">
  <link rel="alternate" hreflang="en" href="{SITE}/">
  <link rel="alternate" hreflang="es" href="{SITE}/es/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
  <link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
  <meta name="apple-itunes-app" content="app-id=6762389261">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cerqa">
  <meta property="og:url" content="{SITE}{t['path']}">
  <meta property="og:title" content="{t['og_title']}">
  <meta property="og:description" content="{t['og_desc']}">
  <meta property="og:image" content="{SITE}/images/social/cerqa-{lang}.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{t['og_locale'][0]}">
  <meta property="og:locale:alternate" content="{t['og_locale'][1]}">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"MobileApplication","name":"Cerqa","url":"{SITE}{t['path']}",
   "operatingSystem":"iOS, Android","applicationCategory":"TravelApplication",
   "description":"{t['ld_desc']}",
   "offers":{{"@type":"Offer","price":"0","priceCurrency":"{t['currency']}"}},
   "sameAs":["{APP_STORE.format(cc=t['cc'])}","https://play.google.com/store/apps/details?id=com.cerqa.app"]}}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/home.css">{ga}
</head>
<body>

  <nav class="site-nav">
    <a class="site-nav-brand" href="{t['path']}"><img src="/images/icon/apple-touch-icon.png" alt="" width="32" height="32">Cerqa</a>
    <div class="site-nav-right">
      <a class="site-nav-lang" href="{t['alt']}" hreflang="{other}" lang="{other}">{t['lang_link']}</a>
      <a class="site-nav-planner" href="https://ride.cerqa.app" target="_blank" rel="noopener">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>
        <span>{t['planner_nav']}</span>
      </a>
    </div>
  </nav>

  <header class="hero">
    <h1>{t['h1']}</h1>
    <p class="subtext">{t['sub']}</p>
    {badges(t, t['campaign'])}
    <p class="fine">{t['fine']}</p>
  </header>

  <div class="hero-phones">
    <div class="phone-wrap"><img src="/images/android/android-1.png" width="440" height="900" alt="{t['phones_alt'][0]}"></div>
    <div class="phone-wrap"><img src="/images/ios/ios-1.png" width="443" height="900" alt="{t['phones_alt'][1]}"></div>
  </div>

  <section class="section">
    <div class="section-header">
      <h2>{t['benefits_h']}</h2>
      <p>{t['benefits_p']}</p>
    </div>
    <div class="benefits">
{benefits}
    </div>
  </section>

  <section class="section">
    <div class="section-header">
      <h2>{t['videos_h']}</h2>
      <p>{t['videos_p']}</p>
    </div>
    <div class="videos-row">
{videos}
    </div>
  </section>

  <section class="section">
    <div class="section-header">
      <h2>{t['shots_h']}</h2>
      <p>{t['shots_p']}</p>
    </div>
    <div class="shots-grid">
{shots}
    </div>
  </section>

  <section class="section">
    <div class="section-header">
      <h2>{t['tools_h']}</h2>
      <p>{t['tools_p']}</p>
    </div>
    <div class="tools">
{tools}
    </div>
  </section>

  <section class="section">
    <div class="planner">
      <div class="browser-frame">
        <div class="browser-frame-bar"><span></span><span></span><span></span></div>
        <img src="/images/web/trip-planner-1.png" loading="lazy" alt="{t['planner_alt']}">
      </div>
      <div>
        <h2>{t['planner_h']}</h2>
        <p>{t['planner_p']}</p>
        <a class="link" href="https://ride.cerqa.app" target="_blank" rel="noopener">{t['planner_link']} →</a>
      </div>
    </div>
  </section>

  <section class="section carplay">
    <div class="section-header">
      <h2>{t['carplay_h']}</h2>
      <p>{t['carplay_p']}</p>
    </div>
    <video muted loop playsinline preload="none" poster="/images/posters/carplay-nav.jpg" data-src="/images/carplay/carplay-nav.mp4"></video>
  </section>

  <section class="section" id="plans">
    <div class="section-header">
      <h2>{t['plans_h']}</h2>
      <p>{t['plans_p']}</p>
    </div>
    <div class="plans">
      <table>
        <thead><tr><th>{t['plans_cols'][0]}</th><th class="c">{t['plans_cols'][1]}</th><th class="c pro">{t['plans_cols'][2]}</th></tr></thead>
        <tbody>
{plan_rows}
        </tbody>
      </table>
    </div>
    <p class="plans-note">{t['plans_note']}</p>
  </section>

  <section class="final">
    <h2>{t['final_h']}</h2>
    <p>{t['final_p']}</p>
    {badges(t, t['campaign'] + '_bottom')}
  </section>

  <footer>
    <p>© 2026 Cerqa</p>
    {"".join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
    <p class="data-credits">{t['credits']}</p>
  </footer>

  <script>
    // Videos load and play only while on screen.
    (function () {{
      var vids = document.querySelectorAll("video[data-src]");
      if (!("IntersectionObserver" in window)) {{
        vids.forEach(function (v) {{ v.src = v.dataset.src; }});
        return;
      }}
      var io = new IntersectionObserver(function (entries) {{
        entries.forEach(function (e) {{
          var v = e.target;
          if (e.isIntersecting) {{
            if (!v.src) v.src = v.dataset.src;
            var p = v.play(); if (p && p.catch) p.catch(function () {{}});
          }} else if (v.src) {{ v.pause(); }}
        }});
      }}, {{ rootMargin: "200px" }});
      vids.forEach(function (v) {{ io.observe(v); }});
    }})();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    ga = analytics()
    for lang, out in (("en", "index.html"), ("es", "es/index.html")):
        html = build(lang, ga)
        with open(out, "w") as f:
            f.write(html)
        print("wrote", out)
