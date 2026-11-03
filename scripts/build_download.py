#!/usr/bin/env python3
"""Builds the download pages: /download/ (EN) and /es/descargar/ (ES). Every link the app shares for
"get Cerqa" lands here, so it says what Cerqa does in a line and that it's free, with no invite
needed (the old page still said "Invite Only", 2026-11-03). Shares the home page's nav, badges,
analytics and styles. Run from the repo root:
    python3 scripts/build_download.py
"""
import os

from build_home import SITE, T, analytics, badges

ICON_PIN = '<svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>'
ICON_CARS = '<svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>'

PAGES = {
    "en": {
        "path": "/download/", "alt": "/es/descargar/", "html_lang": "en", "og_locale": "en_US",
        "title": "Download Cerqa: free location sharing for iPhone and Android",
        "desc": "Get Cerqa free on iPhone and Android. Share your location with family and friends, see when everyone will arrive, and get there together. No invite needed.",
        "og_title": "Get Cerqa",
        "og_desc": "See who's on the way and when everyone will arrive. Free on iPhone and Android.",
        "og_image": "/images/social/cerqa-en.jpg",
        "h1": "Get Cerqa",
        "sub": "See who's on the way and when everyone will arrive. Share your location with family and friends, and get where you're going together.",
        "fine": "Free on iPhone and Android. No invite needed.",
        "phones_alt": ("Cerqa on an Android phone: friends on the map", "Cerqa on iPhone: friends on the map"),
        "benefits_h": "What you can do with Cerqa",
        "benefits": [
            (ICON_PIN, "Share your location", "With anyone on iPhone or Android, for a few minutes or the whole drive. Stop any time."),
            (ICON_CLOCK, "See when everyone arrives", "Live arrival times for everyone who's coming, so nobody has to ask \"where are you?\""),
            (ICON_CARS, "Get there together", "Make a plan, pick a place to meet, ask for a ride, or drive as a group with turn-by-turn directions."),
        ],
        "invite_h": "Got an invite from a friend?",
        "invite_p": "Open their link on your phone. Your invitation will be waiting when you open Cerqa.",
        "share_h": "Share Cerqa",
        "share_p": "Send this link to family and friends. They'll find Cerqa for iPhone and Android here.",
        "copy": "Copy", "copied": "Copied!",
        "more": "Learn more about Cerqa", "home": "/",
        "campaign": "download_en",
    },
    "es": {
        "path": "/es/descargar/", "alt": "/download/", "html_lang": "es", "og_locale": "es_MX",
        "title": "Descarga Cerqa: comparte tu ubicación gratis en iPhone y Android",
        "desc": "Descarga Cerqa gratis en iPhone y Android. Comparte tu ubicación con familia y amigos, mira cuándo llegará cada quien y lleguen juntos. No necesitas invitación.",
        "og_title": "Descarga Cerqa",
        "og_desc": "Mira quién va en camino y cuándo llegará cada quien. Gratis en iPhone y Android.",
        "og_image": "/images/social/cerqa-es.jpg",
        "h1": "Descarga Cerqa",
        "sub": "Mira quién va en camino y cuándo llegará cada quien. Comparte tu ubicación con familia y amigos, y lleguen juntos a donde van.",
        "fine": "Gratis en iPhone y Android. No necesitas invitación.",
        "phones_alt": ("Cerqa en Android: amigos en el mapa", "Cerqa en iPhone: amigos en el mapa"),
        "benefits_h": "Lo que puedes hacer con Cerqa",
        "benefits": [
            (ICON_PIN, "Comparte tu ubicación", "Con quien sea, en iPhone o Android, por unos minutos o todo el camino. Detenla cuando quieras."),
            (ICON_CLOCK, "Mira cuándo llega cada quien", "Horas de llegada en vivo de todos los que vienen, para que nadie tenga que preguntar \"¿dónde estás?\""),
            (ICON_CARS, "Lleguen juntos", "Hagan un plan, elijan dónde verse, pide que te recojan o manejen en grupo con indicaciones paso a paso."),
        ],
        "invite_h": "¿Un amigo te mandó una invitación?",
        "invite_p": "Abre su enlace en tu teléfono. Tu invitación estará ahí cuando abras Cerqa.",
        "share_h": "Comparte Cerqa",
        "share_p": "Manda este enlace a tu familia y amigos. Aquí encuentran Cerqa para iPhone y Android.",
        "copy": "Copiar", "copied": "¡Copiado!",
        "more": "Conoce más de Cerqa", "home": "/es/",
        "campaign": "download_es",
    },
}

EXTRA_CSS = """
  <style>
    .dl-note{max-width:560px;margin:0 auto;text-align:center;padding:0 16px}
    .dl-note h2{font-size:22px;margin:0 0 8px}
    .dl-note p{margin:0;color:var(--muted,#5b6b82);line-height:1.5}
    .dl-share{display:flex;gap:8px;max-width:420px;margin:16px auto 0}
    .dl-share input{flex:1;min-width:0;padding:12px 14px;border:1px solid #cfd8e3;border-radius:12px;font:inherit;background:#fff;color:#1b2d4a}
    .dl-share button{padding:12px 18px;border:0;border-radius:12px;background:#1b2d4a;color:#fff;font:inherit;font-weight:600;cursor:pointer}
    @media (prefers-color-scheme: dark){.dl-share input{background:#152238;color:#e8eef6;border-color:#2b3d58}.dl-share button{background:#4f8cff}}
  </style>"""


def build(lang, ga):
    p, t = PAGES[lang], T[lang]
    url = SITE + p["path"]
    benefits = "\n".join(f"""      <div class="benefit">
        <div class="benefit-icon">{icon}</div>
        <h3>{h}</h3>
        <p>{d}</p>
      </div>""" for icon, h, d in p["benefits"])
    switch = ('<span aria-current="true">EN</span><a href="/es/descargar/" hreflang="es" lang="es" aria-label="Español">ES</a>'
              if lang == "en" else
              '<a href="/download/?lang=en" hreflang="en" lang="en" aria-label="English">EN</a><span aria-current="true">ES</span>')
    # The app shares /download/ in every language: a Spanish phone goes to the Spanish page once
    # (?lang=en, from the EN switch, stays in English).
    redirect = """
  <script>
    (function () {
      try {
        if (/[?&]lang=en/.test(location.search)) return;
        if (/^es\\b/i.test(navigator.language || "")) location.replace("/es/descargar/" + location.hash);
      } catch (e) {}
    })();
  </script>""" if lang == "en" else ""
    return f"""<!DOCTYPE html>
<html lang="{p['html_lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{p['title']}</title>
  <meta name="description" content="{p['desc']}">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="en" href="{SITE}/download/">
  <link rel="alternate" hreflang="es" href="{SITE}/es/descargar/">
  <link rel="alternate" hreflang="x-default" href="{SITE}/download/">{redirect}
  <link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
  <link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
  <meta name="apple-itunes-app" content="app-id=6762389261">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cerqa">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{p['og_title']}">
  <meta property="og:description" content="{p['og_desc']}">
  <meta property="og:image" content="{SITE}{p['og_image']}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{p['og_locale']}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/home.css">{EXTRA_CSS}{ga}
</head>
<body>

  <nav class="site-nav">
    <a class="site-nav-brand" href="{p['home']}"><img src="/images/icon/apple-touch-icon.png" alt="" width="32" height="32">Cerqa</a>
    <div class="site-nav-right">
      <a class="site-nav-lang" href="{p['home']}blog/">Blog</a>
      <div class="lang-switch" role="group" aria-label="Language">{switch}</div>
    </div>
  </nav>

  <header class="hero">
    <h1>{p['h1']}</h1>
    <p class="subtext">{p['sub']}</p>
    {badges(t, p['campaign'])}
    <p class="fine">{p['fine']} <a href="{p['home']}">{p['more']}</a></p>
  </header>

  <div class="hero-phones">
    <div class="phone-wrap"><img src="/images/android/android-1.png" width="440" height="900" alt="{p['phones_alt'][0]}"></div>
    <div class="phone-wrap"><img src="/images/ios/ios-1.png" width="443" height="900" alt="{p['phones_alt'][1]}"></div>
  </div>

  <section class="section">
    <div class="section-header">
      <h2>{p['benefits_h']}</h2>
    </div>
    <div class="benefits">
{benefits}
    </div>
  </section>

  <section class="section">
    <div class="dl-note">
      <h2>{p['invite_h']}</h2>
      <p>{p['invite_p']}</p>
    </div>
  </section>

  <section class="section">
    <div class="dl-note">
      <h2>{p['share_h']}</h2>
      <p>{p['share_p']}</p>
      <div class="dl-share">
        <input id="shareUrl" type="text" value="https://cerqa.app/download/" readonly aria-label="{p['share_h']}">
        <button id="copyBtn" type="button">{p['copy']}</button>
      </div>
    </div>
    {badges(t, p['campaign'] + '_bottom')}
  </section>

  <footer>
    <p>© 2026 Cerqa</p>
    {"".join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
  </footer>

  <script>
    document.getElementById("copyBtn").addEventListener("click", function () {{
      var input = document.getElementById("shareUrl"), btn = this;
      var done = function () {{ btn.textContent = "{p['copied']}"; setTimeout(function () {{ btn.textContent = "{p['copy']}"; }}, 2000); }};
      if (navigator.clipboard) navigator.clipboard.writeText(input.value).then(done, function () {{ input.select(); document.execCommand("copy"); done(); }});
      else {{ input.select(); document.execCommand("copy"); done(); }}
    }});
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    ga = analytics()
    for lang, out in (("en", "download/index.html"), ("es", "es/descargar/index.html")):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(build(lang, ga))
        print("wrote", out)
