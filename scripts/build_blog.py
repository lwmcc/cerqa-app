#!/usr/bin/env python3
"""Builds the blog: /blog/ in English and /es/blog/ in Spanish, one post a week.

Each post answers something people search for (for example "share location between iPhone and Android")
and shows how Cerqa does it, with App Store and Google Play links. Posts live in scripts/blog/*.py, one
file per post with an EN and an ES version (see the first post for the shape). Run from the repo root:
    python3 scripts/build_blog.py
It writes the post pages, both blog indexes, the RSS feeds, and the blog part of sitemap.xml (between
the BLOG markers), so a new post only needs its file in scripts/blog/.

Writing rules: plain words, no em dashes, only claim what the shipped app does today, and link to other
cerqa.app pages where they help.
"""
import datetime
import glob
import html
import importlib.util
import json
import os
import re

from build_home import APP_STORE, PLAY, SITE, T, analytics

HERE = os.path.dirname(os.path.abspath(__file__))

UI = {
    "en": {
        "blog": "/blog/", "home": "/", "blog_name": "Cerqa Blog",
        "index_title": "Cerqa Blog | Location sharing, group trips and getting everyone there",
        "index_desc": "Guides for sharing your location with family and friends, road trips with a group, meeting up and getting everyone there, on iPhone and Android.",
        "index_h1": "The Cerqa Blog",
        "index_sub": "Guides for sharing where you are, driving together and getting everyone there. A new post every week.",
        "read": "Read", "min": "min read", "updated": "Updated",
        "cta_h": "Try Cerqa free", "cta_p": "On iPhone and Android, so the whole group can use it.",
        "more_h": "More from the blog", "faq_h": "Questions",
        "crumb_home": "Home", "other_lang": "Leer en español", "date_fmt": "%B %-d, %Y", "cc": "us",
    },
    "es": {
        "blog": "/es/blog/", "home": "/es/", "blog_name": "Blog de Cerqa",
        "index_title": "Blog de Cerqa | Compartir ubicación, viajes en grupo y que todos lleguen",
        "index_desc": "Guías para compartir tu ubicación con familia y amigos, viajar en carretera en grupo, encontrarse y que todos lleguen, en iPhone y Android.",
        "index_h1": "El blog de Cerqa",
        "index_sub": "Guías para compartir dónde estás, manejar juntos y que todos lleguen. Una entrada nueva cada semana.",
        "read": "Leer", "min": "min de lectura", "updated": "Actualizado",
        "cta_h": "Prueba Cerqa gratis", "cta_p": "En iPhone y Android, para que todo el grupo la use.",
        "more_h": "Más del blog", "faq_h": "Preguntas",
        "crumb_home": "Inicio", "other_lang": "Read in English", "date_fmt": "%d/%m/%Y", "cc": "mx",
    },
}

ES_MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
             "octubre", "noviembre", "diciembre"]


def nice_date(d, lang):
    if lang == "es":
        return f"{d.day} de {ES_MONTHS[d.month - 1]} de {d.year}"
    return d.strftime(UI["en"]["date_fmt"])


def load_posts():
    posts = []
    for path in sorted(glob.glob(os.path.join(HERE, "blog", "*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        p = mod.POST
        p["date"] = datetime.date.fromisoformat(p["date"])
        p["updated"] = datetime.date.fromisoformat(p.get("updated", p["date"].isoformat()))
        if p["date"] <= datetime.date.today() or os.environ.get("BLOG_DRAFTS"):
            posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def url(lang, slug=None):
    base = UI[lang]["blog"]
    return f"{base}{slug}/" if slug else base


def minutes(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return max(2, round(words / 220))


def badges(lang, campaign):
    t = T[lang]
    return f"""<div class="store-badges">
      <a href="{APP_STORE.format(cc=t['cc'])}" target="_blank" rel="noopener" data-store="apple"><img class="badge-apple" src="{t['apple_badge']}" alt="{t['apple_alt']}" width="156" height="52"></a>
      <a href="{PLAY.format(campaign=campaign)}" target="_blank" rel="noopener" data-store="google"><img class="badge-google" src="{t['google_badge']}" alt="{t['google_alt']}" width="175" height="52"></a>
    </div>"""


def head(lang, title, desc, path, alt_path, og_type, image, ld, ga):
    other = "es" if lang == "en" else "en"
    en_path, es_path = (path, alt_path) if lang == "en" else (alt_path, path)
    ld_tags = "\n".join(f'  <script type="application/ld+json">\n  {json.dumps(x, ensure_ascii=False)}\n  </script>' for x in ld)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{SITE}{path}">
  <link rel="alternate" hreflang="en" href="{SITE}{en_path}">
  <link rel="alternate" hreflang="es" href="{SITE}{es_path}">
  <link rel="alternate" hreflang="x-default" href="{SITE}{en_path}">
  <link rel="alternate" type="application/rss+xml" title="{UI[lang]['blog_name']}" href="{SITE}{UI[lang]['blog']}feed.xml">
  <link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
  <link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
  <meta name="apple-itunes-app" content="app-id=6762389261">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Cerqa">
  <meta property="og:url" content="{SITE}{path}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="{SITE}{image}">
  <meta property="og:locale" content="{'en_US' if lang == 'en' else 'es_MX'}">
  <meta property="og:locale:alternate" content="{'es_MX' if lang == 'en' else 'en_US'}">
  <meta name="twitter:card" content="summary_large_image">
{ld_tags}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/home.css">
  <link rel="stylesheet" href="/assets/blog.css">{ga}
</head>
<body>

  <nav class="site-nav">
    <a class="site-nav-brand" href="{UI[lang]['home']}"><img src="/images/icon/apple-touch-icon.png" alt="" width="32" height="32">Cerqa</a>
    <div class="site-nav-right">
      <a class="site-nav-lang" href="{UI[lang]['blog']}">Blog</a>
      <a class="site-nav-lang" href="{alt_path}" hreflang="{other}" lang="{other}">{T[lang]['lang_link']}</a>
    </div>
  </nav>
"""


def foot(lang):
    t = T[lang]
    return f"""
  <footer>
    <p>© 2026 Cerqa</p>
    {"".join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
    <p class="data-credits">{t['credits']}</p>
  </footer>
  <script>
    // Store badge taps on blog pages, so we can see which posts bring installs.
    document.querySelectorAll("a[data-store]").forEach(function (a) {{
      a.addEventListener("click", function () {{
        if (typeof gtag === "function") gtag("event", "store_click", {{store: a.dataset.store, page: location.pathname}});
      }});
    }});
  </script>
</body>
</html>
"""


def card(p, lang):
    v = p[lang]
    return f"""      <a class="post-card" href="{url(lang, v['slug'])}">
        <img src="{p['image']}" width="1200" height="630" loading="lazy" alt="{html.escape(v['image_alt'])}">
        <div class="post-card-text">
          <time datetime="{p['date'].isoformat()}">{nice_date(p['date'], lang)}</time>
          <h2>{v['h1']}</h2>
          <p>{v['desc']}</p>
          <span class="go">{UI[lang]['read']} →</span>
        </div>
      </a>"""


def build_post(p, lang, posts, ga):
    v, ui = p[lang], UI[lang]
    other = "es" if lang == "en" else "en"
    path, alt_path = url(lang, v["slug"]), url(other, p[other]["slug"])
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "headline": v["h1"], "description": v["desc"],
         "image": SITE + p["image"], "datePublished": p["date"].isoformat(), "dateModified": p["updated"].isoformat(),
         "inLanguage": lang, "mainEntityOfPage": SITE + path,
         "author": {"@type": "Organization", "name": "Cerqa", "url": SITE + "/"},
         "publisher": {"@type": "Organization", "name": "Cerqa", "url": SITE + "/",
                       "logo": {"@type": "ImageObject", "url": SITE + "/images/icon/apple-touch-icon.png"}}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["crumb_home"], "item": SITE + ui["home"]},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + ui["blog"]},
            {"@type": "ListItem", "position": 3, "name": v["h1"], "item": SITE + path}]},
    ]
    if v.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in v["faq"]]})
    faq = ""
    if v.get("faq"):
        faq = f"\n      <h2>{ui['faq_h']}</h2>\n" + "\n".join(
            f"      <details class=\"faq\"><summary>{q}</summary><p>{a}</p></details>" for q, a in v["faq"])
    more = [x for x in posts if x is not p][:3]
    more_html = ""
    if more:
        more_html = f"""
  <section class="section">
    <div class="section-header"><h2>{ui['more_h']}</h2></div>
    <div class="post-list">
{chr(10).join(card(x, lang) for x in more)}
    </div>
  </section>"""
    updated = ""
    if p["updated"] != p["date"]:
        updated = f' · {ui["updated"]} <time datetime="{p["updated"].isoformat()}">{nice_date(p["updated"], lang)}</time>'
    return head(lang, v["title"], v["desc"], path, alt_path, "article", p["image"], ld, ga) + f"""
  <article class="post">
    <p class="crumbs"><a href="{ui['home']}">{ui['crumb_home']}</a> › <a href="{ui['blog']}">Blog</a></p>
    <h1>{v['h1']}</h1>
    <p class="post-meta"><time datetime="{p['date'].isoformat()}">{nice_date(p['date'], lang)}</time>{updated} · {minutes(v['body'])} {ui['min']} · <a href="{alt_path}" hreflang="{other}" lang="{other}">{ui['other_lang']}</a></p>
    <img class="post-hero" src="{p['image']}" width="1200" height="630" alt="{html.escape(v['image_alt'])}">
    <div class="post-body">
{v['body']}{faq}
    </div>
  </article>

  <section class="final">
    <h2>{ui['cta_h']}</h2>
    <p>{ui['cta_p']}</p>
    {badges(lang, 'blog_' + lang + '_' + p['id'])}
  </section>{more_html}
""" + foot(lang)


def build_index(lang, posts, ga):
    ui = UI[lang]
    other = "es" if lang == "en" else "en"
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": ui["blog_name"], "url": SITE + ui["blog"],
           "inLanguage": lang, "publisher": {"@type": "Organization", "name": "Cerqa", "url": SITE + "/"},
           "blogPost": [{"@type": "BlogPosting", "headline": p[lang]["h1"], "url": SITE + url(lang, p[lang]["slug"]),
                         "datePublished": p["date"].isoformat()} for p in posts]}]
    image = posts[0]["image"] if posts else f"/images/social/cerqa-{lang}.jpg"
    return head(lang, ui["index_title"], ui["index_desc"], ui["blog"], UI[other]["blog"], "website", image, ld, ga) + f"""
  <header class="hero blog-hero">
    <h1>{ui['index_h1']}</h1>
    <p class="subtext">{ui['index_sub']}</p>
  </header>

  <section class="section">
    <div class="post-list">
{chr(10).join(card(p, lang) for p in posts)}
    </div>
  </section>

  <section class="final">
    <h2>{ui['cta_h']}</h2>
    <p>{ui['cta_p']}</p>
    {badges(lang, 'blog_' + lang + '_index')}
  </section>
""" + foot(lang)


def rss(lang, posts):
    ui = UI[lang]
    items = "\n".join(f"""    <item>
      <title>{html.escape(p[lang]['h1'])}</title>
      <link>{SITE}{url(lang, p[lang]['slug'])}</link>
      <guid>{SITE}{url(lang, p[lang]['slug'])}</guid>
      <pubDate>{datetime.datetime.combine(p['date'], datetime.time(15)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
      <description>{html.escape(p[lang]['desc'])}</description>
    </item>""" for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{ui['blog_name']}</title>
    <link>{SITE}{ui['blog']}</link>
    <description>{html.escape(ui['index_desc'])}</description>
    <language>{'en-us' if lang == 'en' else 'es-mx'}</language>
{items}
  </channel>
</rss>
"""


def sitemap(posts):
    def entry(loc, en, es, lastmod):
        return f"""  <url><loc>{SITE}{loc}</loc><lastmod>{lastmod}</lastmod>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>
    <xhtml:link rel="alternate" hreflang="es" href="{SITE}{es}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{en}"/>
  </url>"""
    newest = max((p["updated"] for p in posts), default=datetime.date.today()).isoformat()
    rows = [entry(url("en"), url("en"), url("es"), newest), entry(url("es"), url("en"), url("es"), newest)]
    for p in posts:
        en, es = url("en", p["en"]["slug"]), url("es", p["es"]["slug"])
        rows += [entry(en, en, es, p["updated"].isoformat()), entry(es, en, es, p["updated"].isoformat())]
    block = "  <!-- BLOG START (written by scripts/build_blog.py) -->\n" + "\n".join(rows) + "\n  <!-- BLOG END -->\n"
    s = open("sitemap.xml").read()
    if "<!-- BLOG START" in s:
        s = re.sub(r"  <!-- BLOG START.*?<!-- BLOG END -->\n", lambda m: block, s, flags=re.S)
    else:
        s = s.replace("</urlset>", block + "</urlset>")
    open("sitemap.xml", "w").write(s)


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print("wrote", path)


if __name__ == "__main__":
    ga = analytics()
    posts = load_posts()
    for lang in ("en", "es"):
        root = UI[lang]["blog"].strip("/")
        for p in posts:
            write(f"{root}/{p[lang]['slug']}/index.html", build_post(p, lang, posts, ga))
        write(f"{root}/index.html", build_index(lang, posts, ga))
        write(f"{root}/feed.xml", rss(lang, posts))
    sitemap(posts)
    print("sitemap.xml: blog part updated,", len(posts), "posts")
