#!/usr/bin/env python3
"""Builds the iPhone Duo landing page (/iphone-duo/index.html), English only for now. Shares the
home page's nav, badges, analytics and styles (assets/home.css). Run from the repo root:
    python3 scripts/build_duo.py

LAUNCH: while the Duo isn't out, the page says "Coming soon". When the Duo ships and the Duo
update is approved, set COMING_SOON = False here and in build_home.py, then rerun both.
"""
import os

from build_home import SITE, T, analytics, badges

COMING_SOON = True

PATH = "/iphone-duo/"
INNER = [  # (image, caption, line)
    ("inner-1", "See your whole crew, all at once", "Everyone live on one big map, with your group card beside it."),
    ("inner-2", "Who's close, who's running late", "Live arrival times on one side, the map on the other."),
    ("inner-3", "Drive together, turn by turn", "Directions on the map with your friends along the way."),
    ("inner-4", "Chat while you watch them arrive", "The group chat and the live map, side by side."),
]
OUTER = [
    ("outer-2", "Fold it and drive", "Turn-by-turn directions on the outer screen."),
    ("outer-1", "Your group, in your pocket", "Live locations, one hand."),
    ("outer-3", "Make plans in seconds", "See who's in and when."),
    ("outer-4", "Find a drive worth taking", "Scenic routes near you."),
]

ICON_FOLD = '<svg viewBox="0 0 24 24"><path d="M3 4h8v16H3zM13 4h8v16h-8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
ICON_RAIL = '<svg viewBox="0 0 24 24"><path d="M4 4h12v16H4zM18 4h2v16h-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'
ICON_CAR = '<svg viewBox="0 0 24 24"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>'

BENEFITS = [
    (ICON_FOLD, "Two screens, one app", "Open, your plans, chat and people sit in a panel beside a full map. Folded, the same app fits one hand."),
    (ICON_RAIL, "Made for the side rail", "Home, Map, Messages and Groups live in iPhone Duo's side rail, with sharing, Surprise me, Featured Drives and map layers a tap away."),
    (ICON_CAR, "The driver and the passenger", "Fold it for the driver's directions. Open it so a passenger can watch everyone and plan the next stop."),
]


def build(ga):
    t = T["en"]
    pill = "Coming soon to iPhone Duo" if COMING_SOON else "Now on iPhone Duo"
    fine = ("Free on iPhone today. Ready for iPhone Duo when it launches." if COMING_SOON
            else "Free on iPhone Duo, iPhone and Android.")
    inner = "\n".join(f"""      <figure class="duo-shot">
        <img src="/images/duo/{img}.webp" width="1400" height="1004" loading="lazy" alt="Cerqa on the open iPhone Duo: {h}">
        <figcaption><h3>{h}</h3><p>{p}</p></figcaption>
      </figure>""" for img, h, p in INNER)
    outer = "\n".join(f"""      <figure class="duo-shot">
        <img src="/images/duo/{img}.webp" width="700" height="968" loading="lazy" alt="Cerqa on the closed iPhone Duo: {h}">
        <figcaption><h3>{h}</h3><p>{p}</p></figcaption>
      </figure>""" for img, h, p in OUTER)
    benefits = "\n".join(f"""      <div class="benefit">
        <div class="benefit-icon">{icon}</div>
        <h3>{h}</h3>
        <p>{p}</p>
      </div>""" for icon, h, p in BENEFITS)
    title = "Cerqa on iPhone Duo | Live location and group navigation, unfolded"
    desc = ("Cerqa is made for iPhone Duo. Open it for a big map with your whole group beside it, "
            "fold it for turn-by-turn directions. " + ("Coming soon." if COMING_SOON else "Free on the App Store."))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{SITE}{PATH}">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
  <link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
  <meta name="apple-itunes-app" content="app-id=6762389261">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cerqa">
  <meta property="og:url" content="{SITE}{PATH}">
  <meta property="og:title" content="Cerqa on iPhone Duo">
  <meta property="og:description" content="Open it to see everyone. Fold it to drive.">
  <meta property="og:image" content="{SITE}/images/social/cerqa-iphone-duo.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/home.css">{ga}
</head>
<body>

  <nav class="site-nav">
    <a class="site-nav-brand" href="/"><img src="/images/icon/apple-touch-icon.png" alt="" width="32" height="32">Cerqa</a>
    <div class="site-nav-right">
      <a class="site-nav-lang" href="/">cerqa.app</a>
    </div>
  </nav>

  <header class="hero duo-hero">
    <span class="duo-pill">{pill}</span>
    <h1>Cerqa, unfolded.</h1>
    <p class="subtext">Open your iPhone Duo for a big map with your whole group beside it. Fold it to drive.</p>
    {badges(t, 'iphone_duo')}
    <p class="fine">{fine} <a href="/">Learn more about Cerqa</a></p>
  </header>

  <div class="duo-hero-image">
    <img src="/images/duo/inner-1.webp" width="1400" height="1004" alt="Cerqa on the open iPhone Duo, with the whole group live on the map">
  </div>

  <section class="section">
    <div class="section-header">
      <h2>Open it</h2>
      <p>Your people, plans and chat in one panel, with the live map right beside them.</p>
    </div>
    <div class="duo-grid duo-grid-inner">
{inner}
    </div>
  </section>

  <section class="section">
    <div class="section-header">
      <h2>Fold it</h2>
      <p>The outer screen is made for the drive.</p>
    </div>
    <div class="duo-grid duo-grid-outer">
{outer}
    </div>
  </section>

  <section class="section">
    <div class="section-header">
      <h2>Built for both screens</h2>
    </div>
    <div class="benefits">
{benefits}
    </div>
  </section>

  <section class="final">
    <h2>Get Cerqa free today</h2>
    <p>On iPhone now, {"and ready for iPhone Duo when it launches" if COMING_SOON else "iPhone Duo and Android"}.</p>
    {badges(t, 'iphone_duo_bottom')}
    <p class="duo-back"><a href="/">Back to cerqa.app</a></p>
  </section>

  <footer>
    <p>© 2026 Cerqa</p>
    {"".join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
    <p class="data-credits">{t['credits']}</p>
  </footer>
</body>
</html>
"""


if __name__ == "__main__":
    os.makedirs("iphone-duo", exist_ok=True)
    with open("iphone-duo/index.html", "w") as f:
        f.write(build(analytics()))
    print("wrote iphone-duo/index.html")
