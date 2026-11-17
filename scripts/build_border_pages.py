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
        "slug": "san-ysidro", "area": "tijuana", "port": "250401", "extra_ports": ["250407"],
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
        "slug": "otay-mesa", "area": "tijuana", "port": "250601",
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
        "slug": "cbx", "area": "tijuana", "port": "250409",
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
        "slug": "tecate", "area": "tijuana", "port": "250501",
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
    {
        "slug": "laredo-bridge-i", "area": "laredo", "port": "230401",
        "en": {
            "title": "Laredo Bridge I wait time, live",
            "h1": "Laredo Bridge I wait time",
            "desc": "Live Laredo Bridge I wait to enter the US from Nuevo Laredo: cars and walking, from CBP. Compare with Bridge II and Colombia right now.",
            "lead": "Live wait to enter the United States from Nuevo Laredo at Bridge I, from US Customs and Border Protection (CBP).",
            "about": """<p>Bridge I, also called the Gateway to the Americas Bridge, connects downtown Nuevo Laredo with downtown Laredo. It's the main bridge for people crossing on foot.</p>
<p>Car lanes at Bridge I are sometimes closed, so check the live wait above and compare it with Bridge II and Colombia.</p>""",
        },
        "es": {
            "title": "Puente 1 Nuevo Laredo: tiempo de espera en vivo",
            "h1": "Puente 1 de Nuevo Laredo: tiempo de espera",
            "desc": "Tiempo de espera en vivo en el Puente 1 para cruzar de Nuevo Laredo a Laredo: autos y peatones, datos de CBP. Compáralo con el Puente 2 y el Puente Colombia.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Nuevo Laredo por el Puente 1, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>El Puente Internacional 1 une el centro de Nuevo Laredo con el centro de Laredo, Texas. Es el puente principal para cruzar a pie.</p>
<p>A veces los carriles para autos del Puente 1 están cerrados, así que revisa la espera arriba y compárala con el Puente 2 y el Puente Colombia.</p>""",
        },
    },
    {
        "slug": "laredo-bridge-ii", "area": "laredo", "port": "230402",
        "en": {
            "title": "Laredo Bridge II wait time, live",
            "h1": "Laredo Bridge II wait time",
            "desc": "Live Laredo Bridge II (Juárez-Lincoln) wait to enter the US from Nuevo Laredo: general, SENTRI and Ready Lane, from CBP. Compare with Bridge I and Colombia.",
            "lead": "Live wait to enter the United States from Nuevo Laredo at Bridge II, from US Customs and Border Protection (CBP).",
            "about": """<p>Bridge II, the Juárez-Lincoln International Bridge, ends where I-35 begins in downtown Laredo, a few blocks east of Bridge I. It's for cars and buses; people on foot use Bridge I.</p>
<p>When Bridge II is backed up, many drivers compare it with the Colombia bridge northwest of the city.</p>""",
        },
        "es": {
            "title": "Puente 2 Nuevo Laredo: tiempo de espera en vivo",
            "h1": "Puente 2 de Nuevo Laredo: tiempo de espera",
            "desc": "Tiempo de espera en vivo en el Puente 2 (Juárez-Lincoln) para cruzar de Nuevo Laredo a Laredo: carril general, SENTRI y Ready Lane, datos de CBP. Compáralo con el Puente 1 y el Puente Colombia.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Nuevo Laredo por el Puente 2, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>El Puente 2, o Puente Internacional Juárez-Lincoln, llega al centro de Laredo donde empieza la I-35, a unas cuadras al este del Puente 1. Es para autos y autobuses; los peatones cruzan por el Puente 1.</p>
<p>Cuando el Puente 2 está lleno, mucha gente lo compara con el Puente Colombia, al noroeste de la ciudad.</p>""",
        },
    },
    {
        "slug": "laredo-colombia-solidarity", "area": "laredo", "port": "230403",
        "en": {
            "title": "Colombia Bridge wait time (Laredo), live",
            "h1": "Colombia Solidarity Bridge wait time",
            "desc": "Live Colombia Solidarity Bridge wait to enter the US from Colombia, Nuevo León, near Laredo: general, SENTRI and Ready Lane, from CBP. Hours and nearby bridges.",
            "lead": "Live wait to enter the United States from Colombia, Nuevo León, northwest of Laredo, from US Customs and Border Protection (CBP).",
            "about": """<p>The Colombia Solidarity Bridge connects Colombia, Nuevo León with the Laredo area, northwest of the city. It's the only crossing from the state of Nuevo León.</p>
<p>It isn't open overnight, so check the hours above. Drivers coming from Monterrey sometimes use it to skip city traffic in Nuevo Laredo, so compare the waits below before you choose.</p>""",
        },
        "es": {
            "title": "Puente Colombia: tiempo de espera en vivo",
            "h1": "Puente Colombia (Solidaridad): tiempo de espera",
            "desc": "Tiempo de espera en vivo en el Puente Colombia para cruzar de Colombia, Nuevo León a Laredo: carril general, SENTRI y Ready Lane, datos de CBP. Horario y puentes cercanos.",
            "lead": "Tiempo de espera en vivo para entrar a Estados Unidos desde Colombia, Nuevo León, al noroeste de Laredo, según la Oficina de Aduanas y Protección Fronteriza (CBP).",
            "about": """<p>El Puente Solidaridad Colombia une Colombia, Nuevo León con la zona de Laredo, Texas, al noroeste de la ciudad. Es el único cruce fronterizo del estado de Nuevo León.</p>
<p>No abre de noche, así que revisa el horario arriba. Mucha gente que viene de Monterrey lo usa para evitar el tráfico de Nuevo Laredo; compara las esperas abajo antes de decidir.</p>""",
        },
    },
    {
        "slug": "el-paso-bridge-of-the-americas", "area": "el_paso", "port": "240201",
        "en": {
            "title": 'Bridge of the Americas wait time (El Paso), live',
            "h1": 'Bridge of the Americas (BOTA) wait time',
            "desc": 'Live Bridge of the Americas wait to enter El Paso from Ciudad Juárez: cars, Ready Lane and walking, from CBP. Compare with Paso del Norte, Ysleta and Stanton.',
            "lead": 'Live wait to enter the United States from Ciudad Juárez at the Bridge of the Americas, from US Customs and Border Protection (CBP).',
            "about": """<p>The Bridge of the Americas, or BOTA, connects Ciudad Juárez with central El Paso near the Cordova area. It's the free bridge, so people in Juárez call it the Puente Libre. Cars and people on foot can cross, 24 hours.</p>
<p>Compare it with Paso del Norte and Ysleta below before you pick a line.</p>""",
        },
        "es": {
            "title": 'Puente Libre Juárez: tiempo de espera en vivo',
            "h1": 'Puente Libre (Córdova-Américas): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Libre para cruzar de Ciudad Juárez a El Paso: autos, Ready Lane y peatones, datos de CBP. Compáralo con el Santa Fe, Zaragoza y Lerdo.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Ciudad Juárez por el Puente Libre, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Libre, o Puente Córdova-de las Américas (BOTA en inglés), une Ciudad Juárez con el centro de El Paso. No cobra cuota, por eso le dicen el Libre. Cruzan autos y peatones, las 24 horas.</p>
<p>Compáralo abajo con el Santa Fe y el Zaragoza antes de formarte.</p>""",
        },
    },
    {
        "slug": "el-paso-paso-del-norte", "area": "el_paso", "port": "240202",
        "en": {
            "title": 'Paso del Norte bridge wait time (El Paso), live',
            "h1": 'Paso del Norte (PDN) wait time',
            "desc": 'Live Paso del Norte wait to enter El Paso from downtown Ciudad Juárez: cars, SENTRI, Ready Lane and walking, from CBP. Compare with BOTA, Ysleta and Stanton.',
            "lead": 'Live wait to enter the United States from downtown Ciudad Juárez at Paso del Norte, from US Customs and Border Protection (CBP).',
            "about": """<p>Paso del Norte connects downtown Ciudad Juárez with downtown El Paso. In Juárez it's called the Puente Santa Fe. It's the busiest bridge for people crossing on foot, and it only carries traffic into the US.</p>
<p>Cars and pedestrians can cross 24 hours.</p>""",
        },
        "es": {
            "title": 'Puente Santa Fe Juárez: tiempo de espera en vivo',
            "h1": 'Puente Santa Fe (Paso del Norte): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Santa Fe para cruzar del centro de Ciudad Juárez a El Paso: autos, SENTRI, Ready Lane y peatones, datos de CBP. Compáralo con el Libre, Zaragoza y Lerdo.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde el centro de Ciudad Juárez por el Puente Santa Fe, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Santa Fe (Paso del Norte en inglés) une el centro de Ciudad Juárez con el centro de El Paso. Es el puente con más gente cruzando a pie, y solo va hacia Estados Unidos.</p>
<p>Cruzan autos y peatones las 24 horas.</p>""",
        },
    },
    {
        "slug": "el-paso-ysleta", "area": "el_paso", "port": "240203",
        "en": {
            "title": 'Ysleta bridge wait time (El Paso), live',
            "h1": 'Ysleta (Zaragoza) bridge wait time',
            "desc": 'Live Ysleta wait to enter east El Paso from Ciudad Juárez: cars, SENTRI, Ready Lane and walking, from CBP. Compare with BOTA, Paso del Norte and Stanton.',
            "lead": 'Live wait to enter the United States from Ciudad Juárez at the Ysleta bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Ysleta bridge connects the east side of Ciudad Juárez with east El Paso. In Juárez it's called the Puente Zaragoza. It's open 24 hours for cars and people on foot.</p>
<p>For drivers headed to east El Paso or I-10 east, it can save a drive through downtown.</p>""",
        },
        "es": {
            "title": 'Puente Zaragoza Juárez: tiempo de espera en vivo',
            "h1": 'Puente Zaragoza (Ysleta): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Zaragoza para cruzar de Ciudad Juárez al este de El Paso: autos, SENTRI, Ready Lane y peatones, datos de CBP. Compáralo con el Libre, Santa Fe y Lerdo.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Ciudad Juárez por el Puente Zaragoza, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Zaragoza (Ysleta en inglés) une el oriente de Ciudad Juárez con el este de El Paso. Abre las 24 horas para autos y peatones.</p>
<p>Si vas al este de El Paso o a la I-10 hacia el este, te ahorra cruzar por el centro.</p>""",
        },
    },
    {
        "slug": "el-paso-stanton", "area": "el_paso", "port": "240204",
        "en": {
            "title": 'Stanton bridge wait time (El Paso), live',
            "h1": 'Stanton (Lerdo) bridge wait time',
            "desc": "Live Stanton bridge wait to enter El Paso from Ciudad Juárez, from CBP. Into the US it's SENTRI only. Hours and nearby bridges.",
            "lead": 'Live wait to enter the United States from Ciudad Juárez at the Stanton bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Stanton Street bridge connects downtown Ciudad Juárez with downtown El Paso. In Juárez it's called the Puente Lerdo. Going into the US, it's a SENTRI-only crossing, so everyone in the car needs a SENTRI card.</p>
<p>It isn't open overnight, so check the hours above.</p>""",
        },
        "es": {
            "title": 'Puente Lerdo Juárez: tiempo de espera en vivo',
            "h1": 'Puente Lerdo (Stanton): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Lerdo para cruzar de Ciudad Juárez a El Paso, datos de CBP. Hacia Estados Unidos es solo SENTRI. Horario y puentes cercanos.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Ciudad Juárez por el Puente Lerdo, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Lerdo (Stanton en inglés) une el centro de Ciudad Juárez con el centro de El Paso. Hacia Estados Unidos es solo para SENTRI, así que todos en el auto necesitan tarjeta SENTRI.</p>
<p>No abre de noche, así que revisa el horario arriba.</p>""",
        },
    },
    {
        "slug": "hidalgo", "area": "reynosa", "port": "230501",
        "en": {
            "title": 'Hidalgo bridge wait time (Reynosa to McAllen), live',
            "h1": 'Hidalgo bridge wait time',
            "desc": 'Live Hidalgo bridge wait to enter the US from Reynosa: cars, SENTRI, Ready Lane and walking, from CBP. Compare with Anzalduas and Pharr.',
            "lead": 'Live wait to enter the United States from Reynosa at the Hidalgo bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The McAllen-Hidalgo-Reynosa bridge connects downtown Reynosa with Hidalgo, a few miles south of McAllen. It's open 24 hours for cars and people on foot.</p>
<p>When the line is long, compare it with Anzalduas, west of the city.</p>""",
        },
        "es": {
            "title": 'Puente Reynosa-Hidalgo: tiempo de espera en vivo',
            "h1": 'Puente Reynosa-Hidalgo: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el puente Reynosa-Hidalgo para cruzar a McAllen: autos, SENTRI, Ready Lane y peatones, datos de CBP. Compáralo con Anzaldúas y Pharr.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Reynosa por el puente de Hidalgo, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El puente McAllen-Hidalgo-Reynosa une el centro de Reynosa con Hidalgo, Texas, a unos kilómetros al sur de McAllen. Abre las 24 horas para autos y peatones.</p>
<p>Cuando la fila está larga, compáralo con Anzaldúas, al poniente de la ciudad.</p>""",
        },
    },
    {
        "slug": "anzalduas", "area": "reynosa", "port": "230503",
        "en": {
            "title": 'Anzalduas bridge wait time (Reynosa), live',
            "h1": 'Anzalduas bridge wait time',
            "desc": 'Live Anzalduas bridge wait to enter the US from Reynosa: cars, SENTRI and Ready Lane, from CBP. Hours and nearby bridges.',
            "lead": 'Live wait to enter the United States from Reynosa at the Anzalduas bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Anzalduas International Bridge connects the west side of Reynosa with Mission and McAllen. It's for cars only, with no walking lanes.</p>
<p>It isn't open overnight, so check the hours above.</p>""",
        },
        "es": {
            "title": 'Puente Anzaldúas Reynosa: tiempo de espera en vivo',
            "h1": 'Puente Anzaldúas: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el puente Anzaldúas para cruzar de Reynosa a Mission y McAllen: autos, SENTRI y Ready Lane, datos de CBP. Horario y puentes cercanos.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Reynosa por el puente Anzaldúas, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Internacional Anzaldúas une el poniente de Reynosa con Mission y McAllen. Es solo para autos, sin carriles para peatones.</p>
<p>No abre de noche, así que revisa el horario arriba.</p>""",
        },
    },
    {
        "slug": "pharr", "area": "reynosa", "port": "230502",
        "en": {
            "title": 'Pharr bridge wait time (Reynosa), live',
            "h1": 'Pharr bridge wait time',
            "desc": 'Live Pharr bridge wait to enter the US from Reynosa, from CBP. Passenger lanes are often closed; compare with Hidalgo and Anzalduas.',
            "lead": 'Live wait to enter the United States from Reynosa at the Pharr bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Pharr-Reynosa bridge, east of Reynosa, is mostly used by trucks. Its passenger car lanes are often closed, so check the live wait above.</p>
<p>Most drivers in cars use Hidalgo or Anzalduas instead.</p>""",
        },
        "es": {
            "title": 'Puente Pharr Reynosa: tiempo de espera en vivo',
            "h1": 'Puente Pharr: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el puente Pharr para cruzar de Reynosa, datos de CBP. Los carriles para autos suelen estar cerrados; compáralo con Hidalgo y Anzaldúas.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Reynosa por el puente Pharr, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El puente Pharr-Reynosa, al oriente de Reynosa, lo usan sobre todo los camiones de carga. Los carriles para autos suelen estar cerrados, así que revisa la espera arriba.</p>
<p>La mayoría de quienes cruzan en auto usan Hidalgo o Anzaldúas.</p>""",
        },
    },
    {
        "slug": "brownsville-gateway", "area": "brownsville", "port": "535504",
        "en": {
            "title": 'Gateway bridge wait time (Brownsville), live',
            "h1": 'Brownsville Gateway bridge wait time',
            "desc": 'Live Gateway International Bridge wait to enter Brownsville from Matamoros: cars, Ready Lane and walking, from CBP. Compare with B&M and Veterans.',
            "lead": 'Live wait to enter the United States from downtown Matamoros at the Gateway bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Gateway International Bridge connects downtown Matamoros with downtown Brownsville. In Matamoros it's called the Puente Nuevo. It's open 24 hours for cars and people on foot.</p>
<p>Compare it with the B&amp;M bridge a few blocks away and with Veterans before you pick a line.</p>""",
        },
        "es": {
            "title": 'Puente Nuevo Matamoros: tiempo de espera en vivo',
            "h1": 'Puente Nuevo (Gateway), Matamoros: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Nuevo para cruzar de Matamoros a Brownsville: autos, Ready Lane y peatones, datos de CBP. Compáralo con el Puente Viejo y Los Tomates.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde el centro de Matamoros por el Puente Nuevo, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Nuevo (Gateway en inglés) une el centro de Matamoros con el centro de Brownsville. Abre las 24 horas para autos y peatones.</p>
<p>Compáralo con el Puente Viejo, a unas cuadras, y con Los Tomates antes de formarte.</p>""",
        },
    },
    {
        "slug": "brownsville-b-and-m", "area": "brownsville", "port": "535501",
        "en": {
            "title": 'B&M bridge wait time (Brownsville), live',
            "h1": 'Brownsville B&M bridge wait time',
            "desc": 'Live B&M bridge wait to enter Brownsville from Matamoros: cars, Ready Lane and walking, from CBP. Compare with Gateway and Veterans.',
            "lead": 'Live wait to enter the United States from Matamoros at the B&M bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The B&amp;M (Brownsville and Matamoros) bridge is a few blocks from the Gateway bridge, in downtown Brownsville. In Matamoros it's called the Puente Viejo. It's open 24 hours for cars and people on foot.</p>""",
        },
        "es": {
            "title": 'Puente Viejo Matamoros: tiempo de espera en vivo',
            "h1": 'Puente Viejo (B&M), Matamoros: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el Puente Viejo para cruzar de Matamoros a Brownsville: autos, Ready Lane y peatones, datos de CBP. Compáralo con el Puente Nuevo y Los Tomates.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Matamoros por el Puente Viejo, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El Puente Viejo (B&amp;M en inglés) está a unas cuadras del Puente Nuevo, en el centro de Brownsville. Abre las 24 horas para autos y peatones.</p>""",
        },
    },
    {
        "slug": "brownsville-veterans", "area": "brownsville", "port": "535502",
        "en": {
            "title": 'Veterans bridge wait time (Brownsville), live',
            "h1": 'Brownsville Veterans bridge wait time',
            "desc": 'Live Veterans International Bridge wait to enter Brownsville from Matamoros: cars, SENTRI, Ready Lane and walking, from CBP. Hours and nearby bridges.',
            "lead": 'Live wait to enter the United States from Matamoros at the Veterans bridge, from US Customs and Border Protection (CBP).',
            "about": """<p>The Veterans International Bridge, at Los Tomates, is east of downtown Brownsville and connects straight to the I-69E highway. It's the only Brownsville bridge with SENTRI lanes.</p>
<p>It isn't open overnight, so check the hours above.</p>""",
        },
        "es": {
            "title": 'Puente Los Tomates Matamoros: tiempo de espera en vivo',
            "h1": 'Puente Los Tomates (Veterans): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en el puente Los Tomates para cruzar de Matamoros a Brownsville: autos, SENTRI, Ready Lane y peatones, datos de CBP. Horario y puentes cercanos.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Matamoros por el puente Los Tomates, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>El puente Los Tomates (Veterans en inglés) está al oriente del centro de Brownsville y conecta directo con la carretera I-69E. Es el único puente de Brownsville con carriles SENTRI.</p>
<p>No abre de noche, así que revisa el horario arriba.</p>""",
        },
    },
    {
        "slug": "nogales-deconcini", "area": "nogales", "port": "260401",
        "en": {
            "title": 'Nogales DeConcini wait time, live',
            "h1": 'Nogales DeConcini wait time',
            "desc": 'Live DeConcini wait to enter Nogales, Arizona from Nogales, Sonora: cars, SENTRI and walking, from CBP. Compare with Mariposa and Morley Gate.',
            "lead": 'Live wait to enter the United States from downtown Nogales, Sonora at DeConcini, from US Customs and Border Protection (CBP).',
            "about": """<p>The DeConcini crossing connects downtown Nogales, Sonora with downtown Nogales, Arizona. It's open 24 hours for cars and people on foot.</p>
<p>Drivers often compare it with Mariposa on the west side of town.</p>""",
        },
        "es": {
            "title": 'Garita DeConcini Nogales: tiempo de espera en vivo',
            "h1": 'Garita DeConcini, Nogales: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en la garita DeConcini para cruzar de Nogales, Sonora a Nogales, Arizona: autos, SENTRI y peatones, datos de CBP. Compárala con Mariposa y Morley.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde el centro de Nogales, Sonora por la garita DeConcini, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>La garita DeConcini une el centro de Nogales, Sonora con el centro de Nogales, Arizona. Abre las 24 horas para autos y peatones.</p>
<p>Mucha gente la compara con Mariposa, al poniente de la ciudad.</p>""",
        },
    },
    {
        "slug": "nogales-mariposa", "area": "nogales", "port": "260402",
        "en": {
            "title": 'Nogales Mariposa wait time, live',
            "h1": 'Nogales Mariposa wait time',
            "desc": 'Live Mariposa wait to enter Nogales, Arizona from Nogales, Sonora: cars and walking, from CBP. Hours and nearby crossings.',
            "lead": 'Live wait to enter the United States from Nogales, Sonora at Mariposa, from US Customs and Border Protection (CBP).',
            "about": """<p>Mariposa is on the west side of Nogales and handles cars and trucks. It's a common choice for drivers who want to skip downtown.</p>
<p>It isn't open overnight, so check the hours above.</p>""",
        },
        "es": {
            "title": 'Garita Mariposa Nogales: tiempo de espera en vivo',
            "h1": 'Garita Mariposa, Nogales: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en la garita Mariposa para cruzar de Nogales, Sonora a Nogales, Arizona: autos y peatones, datos de CBP. Horario y garitas cercanas.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Nogales, Sonora por la garita Mariposa, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>La garita Mariposa está al poniente de Nogales y la usan autos y camiones. Mucha gente la escoge para no pasar por el centro.</p>
<p>No abre de noche, así que revisa el horario arriba.</p>""",
        },
    },
    {
        "slug": "nogales-morley-gate", "area": "nogales", "port": "260403",
        "en": {
            "title": 'Nogales Morley Gate wait time, live',
            "h1": 'Nogales Morley Gate wait time',
            "desc": 'Live Morley Gate walking wait to enter Nogales, Arizona from Nogales, Sonora, from CBP. Short hours; compare with DeConcini.',
            "lead": 'Live walking wait to enter the United States from downtown Nogales, Sonora at Morley Gate, from US Customs and Border Protection (CBP).',
            "about": """<p>Morley Gate is a walking-only crossing in downtown Nogales, close to DeConcini. It keeps short daytime hours, so check them above.</p>""",
        },
        "es": {
            "title": 'Garita Morley Nogales: tiempo de espera en vivo',
            "h1": 'Garita Morley, Nogales: tiempo de espera',
            "desc": 'Tiempo de espera en vivo a pie en la garita Morley para cruzar de Nogales, Sonora a Nogales, Arizona, datos de CBP. Horario corto; compárala con DeConcini.',
            "lead": 'Tiempo de espera en vivo a pie para entrar a Estados Unidos desde el centro de Nogales, Sonora por la garita Morley, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>La garita Morley es solo para peatones, en el centro de Nogales, cerca de DeConcini. Tiene un horario corto de día, así que revísalo arriba.</p>""",
        },
    },
    {
        "slug": "calexico-west", "area": "calexico", "port": "250302",
        "en": {
            "title": 'Calexico West wait time, live',
            "h1": 'Calexico West wait time',
            "desc": 'Live Calexico West wait to enter the US from downtown Mexicali: cars, SENTRI, Ready Lane and walking, from CBP. Compare with Calexico East.',
            "lead": 'Live wait to enter the United States from downtown Mexicali at Calexico West, from US Customs and Border Protection (CBP).',
            "about": """<p>Calexico West connects downtown Mexicali with downtown Calexico. In Mexicali it's called the Garita Centro. It's open 24 hours for cars and people on foot.</p>
<p>Compare it with Calexico East before you pick a line.</p>""",
        },
        "es": {
            "title": 'Garita Centro Mexicali: tiempo de espera en vivo',
            "h1": 'Garita Centro (Calexico West), Mexicali: tiempo de espera',
            "desc": 'Tiempo de espera en vivo en la Garita Centro para cruzar de Mexicali a Calexico: autos, SENTRI, Ready Lane y peatones, datos de CBP. Compárala con la garita Nuevo Mexicali.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde el centro de Mexicali por la Garita Centro, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>La Garita Centro (Calexico West en inglés) une el centro de Mexicali con el centro de Calexico. Abre las 24 horas para autos y peatones.</p>
<p>Compárala con la garita Nuevo Mexicali antes de formarte.</p>""",
        },
    },
    {
        "slug": "calexico-east", "area": "calexico", "port": "250301",
        "en": {
            "title": 'Calexico East wait time, live',
            "h1": 'Calexico East wait time',
            "desc": 'Live Calexico East wait to enter the US from Mexicali: cars, SENTRI, Ready Lane and walking, from CBP. Hours and nearby crossings.',
            "lead": 'Live wait to enter the United States from Mexicali at Calexico East, from US Customs and Border Protection (CBP).',
            "about": """<p>Calexico East is a few miles east of downtown, between the east side of Mexicali and Calexico. In Mexicali it's called the Garita Nuevo Mexicali. It handles cars, people on foot and trucks.</p>
<p>It isn't open overnight, so check the hours above.</p>""",
        },
        "es": {
            "title": 'Garita Nuevo Mexicali: tiempo de espera en vivo',
            "h1": 'Garita Nuevo Mexicali (Calexico East): tiempo de espera',
            "desc": 'Tiempo de espera en vivo en la garita Nuevo Mexicali para cruzar a Calexico: autos, SENTRI, Ready Lane y peatones, datos de CBP. Horario y garitas cercanas.',
            "lead": 'Tiempo de espera en vivo para entrar a Estados Unidos desde Mexicali por la garita Nuevo Mexicali, según la Oficina de Aduanas y Protección Fronteriza (CBP).',
            "about": """<p>La garita Nuevo Mexicali (Calexico East en inglés) está a unos kilómetros al oriente del centro, entre el oriente de Mexicali y Calexico. La usan autos, peatones y camiones.</p>
<p>No abre de noche, así que revisa el horario arriba.</p>""",
        },
    },
]

# Crossings compared on each page: (slug, CBP port, name EN, name ES, Mexican city).
AREAS = {
    "tijuana": {
        "h": ("Tijuana crossings right now", "Garitas de Tijuana ahorita"),
        "items": [("san-ysidro", "250401", "San Ysidro", "San Ysidro", "Tijuana"),
                  ("otay-mesa", "250601", "Otay Mesa", "Otay", "Tijuana"),
                  ("cbx", "250409", "Cross Border Xpress (CBX)", "Cross Border Xpress (CBX)", "Tijuana"),
                  ("tecate", "250501", "Tecate", "Tecate", "Tecate")],
    },
    "el_paso": {
        "h": ("El Paso bridges right now", "Puentes de Ciudad Juárez ahorita"),
        "items": [("el-paso-bridge-of-the-americas", "240201", "Bridge of the Americas (BOTA)", "Puente Libre (Córdova-Américas)", "Ciudad Juárez"),
                  ("el-paso-paso-del-norte", "240202", "Paso del Norte", "Puente Santa Fe (Paso del Norte)", "Ciudad Juárez"),
                  ("el-paso-ysleta", "240203", "Ysleta", "Puente Zaragoza (Ysleta)", "Ciudad Juárez"),
                  ("el-paso-stanton", "240204", "Stanton (SENTRI only)", "Puente Lerdo (solo SENTRI)", "Ciudad Juárez"),
                  (None, "240401", "Tornillo (Marcelino Serna)", "Tornillo-Guadalupe", "Guadalupe"),
                  (None, "240801", "Santa Teresa", "Santa Teresa", "San Jerónimo")],
    },
    "reynosa": {
        "h": ("Reynosa bridges right now", "Puentes de Reynosa ahorita"),
        "items": [("hidalgo", "230501", "Hidalgo", "Reynosa-Hidalgo", "Reynosa"),
                  ("anzalduas", "230503", "Anzalduas", "Anzaldúas", "Reynosa"),
                  ("pharr", "230502", "Pharr", "Pharr", "Reynosa"),
                  (None, "230902", "Donna", "Donna", "Río Bravo"),
                  (None, "230901", "Progreso", "Progreso", "Nuevo Progreso")],
    },
    "brownsville": {
        "h": ("Brownsville bridges right now", "Puentes de Matamoros ahorita"),
        "items": [("brownsville-gateway", "535504", "Gateway", "Puente Nuevo (Gateway)", "Matamoros"),
                  ("brownsville-b-and-m", "535501", "B&amp;M", "Puente Viejo (B&amp;M)", "Matamoros"),
                  ("brownsville-veterans", "535502", "Veterans (Los Tomates)", "Los Tomates (Veterans)", "Matamoros"),
                  (None, "535503", "Los Indios", "Los Indios", "Matamoros"),
                  (None, "230901", "Progreso", "Progreso", "Nuevo Progreso")],
    },
    "nogales": {
        "h": ("Nogales crossings right now", "Garitas de Nogales ahorita"),
        "items": [("nogales-deconcini", "260401", "DeConcini", "DeConcini", "Nogales, Sonora"),
                  ("nogales-mariposa", "260402", "Mariposa", "Mariposa", "Nogales, Sonora"),
                  ("nogales-morley-gate", "260403", "Morley Gate (walking)", "Morley (peatones)", "Nogales, Sonora")],
    },
    "calexico": {
        "h": ("Mexicali crossings right now", "Garitas de Mexicali ahorita"),
        "items": [("calexico-west", "250302", "Calexico West", "Garita Centro (Calexico West)", "Mexicali"),
                  ("calexico-east", "250301", "Calexico East", "Nuevo Mexicali (Calexico East)", "Mexicali"),
                  (None, "250201", "Andrade", "Andrade", "Los Algodones")],
    },
    "laredo": {
        "h": ("Laredo bridges right now", "Puentes de Laredo ahorita"),
        "items": [("laredo-bridge-i", "230401", "Bridge I", "Puente 1", "Nuevo Laredo"),
                  ("laredo-bridge-ii", "230402", "Bridge II (Juárez-Lincoln)", "Puente 2 (Juárez-Lincoln)", "Nuevo Laredo"),
                  ("laredo-colombia-solidarity", "230403", "Colombia Solidarity", "Puente Colombia", "Colombia, Nuevo León")],
    },
}
LINE_WORDS = {
    "tijuana": ("la línea", "la garita"), "calexico": ("la línea", "la garita"), "nogales": ("la línea", "la garita"),
    "laredo": ("la fila", "el puente"), "el_paso": ("la fila", "el puente"), "reynosa": ("la fila", "el puente"),
    "brownsville": ("la fila", "el puente"),
}


def faq(lang, c, name, area_h):
    """Short questions in the words people search ("¿cómo está la línea?"), plus FAQPage data."""
    import json
    line, word = LINE_WORDS[c["area"]]
    plain = re.sub(r"<[^>]+>", "", name).replace("&amp;", "&")
    if lang == "en":
        qa = [
            (f"How long is the line at {plain} right now?",
             f"The live wait at the top of this page is CBP's estimate for {plain}, by lane. It refreshes every 5 minutes on its own."),
            ("Which crossing is fastest right now?",
             f"Check \"{area_h}\" above. The crossing with the shortest regular car wait gets a green Fastest by car tag."),
            ("Are there wait times for going into Mexico?",
             "No. CBP only publishes waits for entering the United States."),
            ("Can my family see when I've crossed?",
             "Yes, with the free Cerqa app. You share your location for the trip, and they see where you are and when you'll arrive. Cerqa also shows border waits on the map."),
        ]
    else:
        qa = [
            (f"¿Cómo está {line} en {plain} ahorita?",
             f"El tiempo de espera de arriba es el estimado de CBP para {plain}, por carril. Se actualiza solo cada 5 minutos."),
            (f"¿Cuál {'garita' if word == 'la garita' else 'puente'} tiene menos espera ahorita?",
             f"Revisa «{area_h}» arriba. {'La garita' if word == 'la garita' else 'El puente'} con menos espera en el carril general para autos tiene la etiqueta verde Más rápido en auto."),
            ("¿Hay tiempos de espera para entrar a México?",
             "No. CBP solo publica los tiempos para entrar a Estados Unidos."),
            ("¿Mi familia puede ver cuando ya crucé?",
             "Sí, con la app gratis de Cerqa. Compartes tu ubicación durante el viaje y ven dónde vienes y a qué hora llegas. Cerqa también muestra los tiempos de la frontera en el mapa."),
        ]
    html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>" for q, a in qa)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    return (f'<h2>{TEXT[lang]["faq_h"]}</h2>\n<div class="prose faq">\n{html}\n</div>\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def share(lang, c, name):
    """WhatsApp share (wa.me opens the app on phones, WhatsApp Web on computers). border.js adds the live wait."""
    t = TEXT[lang]
    plain = re.sub(r"<[^>]+>", "", name).replace("&amp;", "&")
    url = f"{SITE}{hub_path(lang)}{c['slug']}/?utm_source=whatsapp&utm_medium=share&utm_campaign=border_share"
    from urllib.parse import quote
    href = "https://wa.me/?text=" + quote(f"{plain}: {url}")
    return (f'<div class="share-row"><a class="share-wa" href="{href}" target="_blank" rel="noopener" '
            f'data-share-name="{plain.replace(chr(34), "")}" data-share-url="{url}">{t["share"]}</a>'
            f'<button type="button" class="share-other" hidden>{t["share_other"]}</button></div>')


PAGE_FOR_PORT = {it[1]: it[0] for a in AREAS.values() for it in a["items"] if it[0]}

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
        "this_page": "this page",
        "farther": "Farther away",
        "pickup": "<strong>Picking someone up on this side?</strong> If they have Cerqa, they can send you a live link while they drive. You'll see their arrival time in your browser, no app needed.",
        "pickup_link": "Get Cerqa",
        "qr": "Scan to download Cerqa",
        "download": "/download/",
        "all": "All border crossings",
        "about": "About this crossing",
        "source": 'Wait times: <a href="https://bwt.cbp.gov/">U.S. Customs and Border Protection</a>. They\'re CBP estimates, usually updated about once an hour, and can change quickly. The page refreshes on its own every 5 minutes.',
        "cta_h": "Border waits on your map",
        "cta_p": "Cerqa shows live border waits right on the map, plus where your family or friends are and when they'll arrive. Free on iPhone and Android.",
        "share": "Share on WhatsApp", "share_other": "Share",
        "faq_h": "Questions",
        "cc": "us",
        "footer": [("/feedback", "Feedback"), ("/support/", "Support"), ("/privacy/en/", "Privacy Policy"), ("/terms/en/", "Terms of Service"), ("https://www.facebook.com/profile.php?id=61594994114331", "Facebook")],
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
        "this_page": "esta página",
        "farther": "Más lejos",
        "pickup": "<strong>¿Vas a recoger a alguien de este lado?</strong> Si trae Cerqa, te puede mandar un enlace en vivo mientras maneja. Verás su hora de llegada en tu navegador, sin instalar nada.",
        "pickup_link": "Descarga Cerqa",
        "qr": "Escanea para descargar Cerqa",
        "download": "/es/descargar/",
        "all": "Todas las garitas",
        "about": "Sobre esta garita",
        "source": 'Tiempos de espera: <a href="https://bwt.cbp.gov/">Oficina de Aduanas y Protección Fronteriza de EE. UU. (CBP)</a>. Son estimados de CBP, normalmente se actualizan cada hora y pueden cambiar rápido. La página se actualiza sola cada 5 minutos.',
        "cta_h": "Los tiempos de la frontera en tu mapa",
        "cta_p": "Cerqa muestra los tiempos de espera de la frontera en el mapa, y dónde vienen tu familia o amigos y a qué hora llegan. Gratis en iPhone y Android.",
        "share": "Compartir por WhatsApp", "share_other": "Compartir",
        "faq_h": "Preguntas frecuentes",
        "cc": "mx",
        "footer": [("/es/comentarios/", "Comentarios"), ("/support/", "Ayuda"), ("/privacy/es/", "Aviso de privacidad"), ("/terms/es/", "Términos del servicio"), ("https://www.facebook.com/profile.php?id=61594994114331", "Facebook")],
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
<script src="/assets/store-gate.js" defer></script>
</body>
</html>
"""


def download_url(lang, campaign, medium):
    return f"{SITE}{TEXT[lang]['download']}?utm_source=cerqa.app&utm_medium={medium}&utm_campaign={campaign}"


def qr(lang, campaign):
    """QR code (SVG) to the download page, for visitors on a computer. Needs `pip install segno` to
    make new codes; without it, codes already in images/qr/ are reused."""
    rel = f"images/qr/{campaign}.svg"
    if not os.path.exists(rel):
        import segno
        os.makedirs("images/qr", exist_ok=True)
        segno.make(download_url(lang, campaign, "qr"), error="m").save(rel, scale=3, border=2, dark="#1b2d4a", light="#ffffff")
        # Add a viewBox so every code scales to the same size on the page, whatever its module count.
        svg = open(rel).read()
        w = re.search(r'<svg[^>]* width="(\d+)"', svg).group(1)
        open(rel, "w").write(svg.replace(f'width="{w}" height="{w}"', f'width="{w}" height="{w}" viewBox="0 0 {w} {w}"', 1))
    return "/" + rel


def cta(lang, campaign):
    t = TEXT[lang]
    return f"""<section class="app-cta">
  <div class="app-cta-text">
  <h2>{t['cta_h']}</h2>
  <p>{t['cta_p']}</p>
  <div class="stores">
    <a href="{APP_STORE.format(cc=t['cc'])}" target="_blank" rel="noopener">App Store</a>
    <a href="{PLAY.format(campaign=campaign)}" target="_blank" rel="noopener">Google Play</a>
  </div>
  </div>
  <figure class="app-cta-qr"><img src="{qr(lang, campaign)}" alt="" width="135" height="135"><figcaption>{t['qr']}</figcaption></figure>
</section>"""


def pickup(lang, campaign):
    t = TEXT[lang]
    return (f'<p class="pickup">{t["pickup"]} <a href="{download_url(lang, campaign, "web").replace("&", "&amp;")}">{t["pickup_link"]}</a></p>')


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
{'<p style="margin-top:12px"><a href="/canada-border-wait-times/">US-Canada border wait times (both directions)</a></p>' if lang == 'en' else ''}
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
    area = AREAS[c["area"]]
    lis, far = [], []
    for s, p, n_en, n_es, city in area["items"]:
        if s is None:  # farther crossings: listed for comparison, never badged as fastest
            far.append(crossing_li(lang, p, n_en if lang == "en" else n_es, city, link=False))
            continue
        name = n_en if lang == "en" else n_es
        if s == c["slug"]:
            name = f'{name} <span class="this-page">· {t["this_page"]}</span>'
        lis.append(crossing_li(lang, p, name, city, link=(s != c["slug"])))
    nearby = "\n".join(lis)
    farther = (f'<h3 class="farther">{t["farther"]}</h3>\n<ul class="crossing-list">\n' + "\n".join(far) + "\n</ul>") if far else ""
    campaign = f"border_{c['slug'].replace('-', '_')}_{lang}"
    me = next(it for it in area["items"] if it[0] == c["slug"])
    my_name = me[2] if lang == "en" else me[3]
    area_h = area['h'][0 if lang == 'en' else 1]
    body = f"""<p class="crumbs"><a href="{hub_path(lang)}">{t['crumb']}</a></p>
<h1>{x['h1']}</h1>
<p class="lead">{x['lead']}</p>
<div class="wait-card" data-port="{c['port']}" data-mode="detail"><p class="wait-loading">{t['loading']}</p></div>
<noscript><p class="note">{t['noscript']}</p></noscript>
{share(lang, c, my_name)}
{pickup(lang, campaign)}
{extra}
<h2>{area['h'][0 if lang == 'en' else 1]}</h2>
<ul class="crossing-list" data-fastest>
{nearby}
</ul>
{farther}
<p style="margin-top:12px"><a href="{hub_path(lang)}">{t['all']}</a></p>
<p class="note">{t['southbound']}</p>
<h2>{t['about']}</h2>
<div class="prose">{x['about']}</div>
{LANES_EN if lang == 'en' else LANES_ES}
{faq(lang, c, my_name, area_h)}
{cta(lang, campaign)}
<p class="source">{t['source']}</p>"""
    path = f"{hub_path(lang)}{c['slug']}/"
    alt = f"{hub_path('es' if lang == 'en' else 'en')}{c['slug']}/"
    desc = x["desc"]
    if lang == "es":
        line, _ = LINE_WORDS[c["area"]]
        desc = f"¿Cómo está {line}? " + desc
    return path, page(lang, path, alt, x["title"], desc, body, f"cerqa-{lang}.jpg")


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
