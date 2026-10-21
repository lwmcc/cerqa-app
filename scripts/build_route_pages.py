#!/usr/bin/env python3
"""Builds the road trip route pages: /routes/ in English, and /es/rutas/ with Spanish versions of the
Mexico routes.

These are hand-written routes to test interest in Shared routes (Jira CAT-65) before building it in
the app: each page tracks views (GA4) and clicks on "I'd use this" (event route_interest).
Facts that change often (border hours, permits, advisories, fees) link to the official source.
Run from the repo root after editing:  python3 scripts/build_route_pages.py
Then add any new pages to sitemap.xml.
"""
import os

from build_border_pages import APP_STORE, PLAY, SITE, analytics

HUB = "/routes/"

GA = None

# Official links used across the Mexico routes.
L_ADVISORY = '<a href="https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/mexico-travel-advisory.html">US travel advisory for Mexico</a>'
L_BANJERCITO = '<a href="https://www.banjercito.com.mx/">Banjercito</a>'
L_INM = '<a href="https://www.gob.mx/inm">INM (Mexico immigration)</a>'
L_CBP_LUKEVILLE = '<a href="https://www.cbp.gov/contact/ports/lukeville">CBP Lukeville page</a>'
L_NPS_FEES = '<a href="https://www.nps.gov/grca/planyourvisit/fees.htm">Grand Canyon fees</a>'
L_BORDER = '<a href="/border-wait-times/">live border wait times</a>'
L_GAS_MX = '<a href="/gas-prices-mexico/">gas prices in Mexico</a>'

ROUTES = [
    {
        "slug": "phoenix-to-san-diego",
        "title": "Phoenix to San Diego road trip on I-8",
        "h1": "Phoenix to San Diego on I-8",
        "desc": "Phoenix to San Diego by car on I-8: about 355 miles and 5.5 hours. Where to stop, where to get gas, the sand dunes, the mountain climb and tips for summer heat.",
        "facts": [("About 355 mi", "570 km"), ("About 5.5 h", "driving"), ("1 day", ""), ("US", "Arizona and California")],
        "lead": "The desert way to the coast: from the Valley across the Sonoran Desert, past sand dunes and over the mountains to the Pacific.",
        "days": [
            ("Phoenix to Gila Bend", "About 70 mi, 1 h", [
                "Take I-10 west, then AZ-85 south to I-8 in Gila Bend.",
                "<strong>Fill up in Gila Bend.</strong> The next 115 miles to Yuma have very few services.",
            ]),
            ("Gila Bend to Yuma", "About 115 mi, 1 h 45 min", [
                "Long, empty desert on I-8. Dateland, about halfway, has gas and its well-known date shakes.",
                "Yuma is the place for lunch. Yuma Territorial Prison State Historic Park sits right by the Colorado River.",
            ]),
            ("Yuma to El Centro", "About 60 mi, 1 h", [
                "Right after the Colorado River you enter California and pass an agriculture inspection station. Declare fruit and plants.",
                "West of the river, the Imperial Sand Dunes come right up to the freeway, with exits for the dune areas.",
                "From November to March, California is an hour behind Arizona. In summer the clocks match.",
            ]),
            ("El Centro to San Diego", "About 120 mi, 2 h", [
                "Fill up in El Centro. From below sea level, I-8 climbs to over 4,000 feet through the In-Ko-Pah Mountains, with strong side winds on the grade.",
                "Desert View Tower near Jacumba Hot Springs is a good stop to stretch and look back over the desert.",
                "You may pass a Border Patrol checkpoint on I-8. Have ID ready.",
                "Detour: Julian, for apple pie in the mountains. Take CA-79 from Descanso; it adds about an hour.",
            ]),
        ],
        "tips": [
            "In summer the desert often passes 110&deg;F. Leave early, carry water and check tires and coolant before you go.",
            "Two cars? Fill up together in Gila Bend and El Centro so nobody runs low in the empty stretches.",
        ],
    },
    {
        "slug": "grand-canyon-loop-from-phoenix",
        "title": "Grand Canyon loop from Phoenix: Sedona, South Rim and Page",
        "h1": "Grand Canyon loop from Phoenix",
        "desc": "A 4-day loop from Phoenix: Sedona, Grand Canyon South Rim, Desert View Drive, Horseshoe Bend and Antelope Canyon in Page. About 640 miles, with fees, gas and time zone tips.",
        "facts": [("About 640 mi", "1,030 km"), ("About 11 h", "driving"), ("4 days", ""), ("US", "Arizona")],
        "lead": "Red rocks, the canyon and slot canyons in one loop: north through Sedona, along the South Rim, up to Page and back down to the Valley.",
        "days": [
            ("Day 1: Phoenix to Sedona", "About 115 mi, 2 h", [
                "I-17 north, then AZ-179 into Sedona.",
                "On the way: Montezuma Castle National Monument, a few minutes off I-17.",
                "Many Sedona trailheads need a Red Rock Pass to park. Sleep in Sedona or Flagstaff.",
            ]),
            ("Day 2: Sedona to the Grand Canyon South Rim", "About 110 mi, 2.5 h", [
                "Drive up Oak Creek Canyon on AZ-89A to Flagstaff, then US-180 to the park.",
                "Entrance is $35 per car for 7 days, and cash isn't accepted. Since 2026, visitors who don't live in the US (16 and older) pay an extra $100 each. Check " + L_NPS_FEES + " before you go.",
                "Sleep in the park or in Tusayan, and book early.",
            ]),
            ("Day 3: South Rim to Page", "About 140 mi, 3 h", [
                "Go east on Desert View Drive (AZ-64), stopping at the viewpoints and the Desert View Watchtower, then down to Cameron and north on US-89.",
                "Fill up in Tusayan or Cameron. There are long stretches with few services and gaps in cell signal.",
                "In Page: Horseshoe Bend is a short walk from a paid parking lot. Antelope Canyon is only visited on guided tours run by Navajo companies, so book ahead.",
                "<strong>Time zones:</strong> Arizona doesn't use daylight saving time, but the Navajo Nation does, and phones can switch on their own. Check which time your tour uses.",
            ]),
            ("Day 4: Page to Phoenix", "About 275 mi, 4.5 h", [
                "US-89 south to Flagstaff, then I-17 down to Phoenix.",
                "Optional: the Sunset Crater and Wupatki loop just north of Flagstaff adds about an hour.",
            ]),
        ],
        "tips": [
            "Flagstaff and the South Rim are around 7,000 feet. From November to March, check for snow and road closures.",
            "Two cars? Agree on the next stop before Cameron. Cell service is spotty and it's easy to lose each other.",
        ],
    },
    {
        "slug": "phoenix-to-puerto-penasco",
        "title": "Phoenix to Puerto Peñasco (Rocky Point) by car",
        "h1": "Phoenix to Puerto Peñasco (Rocky Point)",
        "desc": "Driving from Phoenix to Rocky Point through Ajo, Organ Pipe and the Lukeville crossing: about 215 miles and 4 hours, plus what you need for Mexico (insurance, passport, permits).",
        "facts": [("About 215 mi", "345 km"), ("About 4 h", "plus the border"), ("1 day", ""), ("US and Mexico", "Arizona and Sonora")],
        "lead": "Arizona's beach: south through Ajo and Organ Pipe Cactus National Monument, across at Lukeville and Sonoyta, and down to the Sea of Cortez.",
        "before": [
            "<strong>Passport</strong> book or card for everyone to get back into the US. US citizens under 16 can use a birth certificate at land crossings.",
            "<strong>Mexican car insurance.</strong> US policies generally don't cover you in Mexico. Buy a Mexican policy before you cross.",
            "<strong>No vehicle permit needed.</strong> Puerto Peñasco is inside the Sonora free zone.",
            "<strong>Tourist permit (FMM):</strong> the rules for short trips have changed over the years. Check with " + L_INM + " or at the office in Sonoyta.",
            "<strong>Rental car?</strong> Make sure the company allows driving into Mexico.",
            "Lukeville isn't open 24 hours. Check the " + L_CBP_LUKEVILLE + " for current hours.",
        ],
        "days": [
            ("Phoenix to Ajo", "About 110 mi, 2 h", [
                "I-10 west to exit 112, then AZ-85 south through Gila Bend to Ajo.",
                "Ajo's Spanish-style plaza is a good break.",
            ]),
            ("Ajo to Lukeville", "About 37 mi, 45 min", [
                "Through Why and Organ Pipe Cactus National Monument. The visitor center is just off AZ-85.",
                "<strong>Fill up in Ajo or Why</strong> before the border.",
            ]),
            ("Sonoyta to Puerto Peñasco", "About 62 mi, 1 h", [
                "Cross at Lukeville into Sonoyta, then take Mexico Highway 8 south across the desert to the coast.",
                "Pesos and dollars are both widely used in Rocky Point.",
            ]),
        ],
        "tips": [
            "Coming home: lines at Lukeville get long on Sunday afternoons and after holiday weekends. Check the " + L_BORDER + " before you leave.",
            "There's a Border Patrol checkpoint on AZ-85 northbound. Have ID ready.",
            "Two cars? Cross together and agree where to meet in Sonoyta in case one gets pulled aside for inspection.",
        ],
    },
    {
        "slug": "tijuana-to-playa-del-carmen",
        "title": "Tijuana to Playa del Carmen by car in 7 days",
        "h1": "Tijuana to Playa del Carmen by car",
        "desc": "Driving across Mexico from Tijuana to Playa del Carmen in 7 days: about 2,700 miles through Hermosillo, Mazatlán, Guadalajara, Puebla, Villahermosa and Bacalar, with permits, tolls and gas tips.",
        "facts": [("About 2,700 mi", "4,350 km"), ("About 50 h", "driving"), ("7 days", ""), ("Mexico", "Baja California to Quintana Roo")],
        "lead": "Coast to coast across Mexico: the Sonoran Desert, the Pacific in Mazatlán, the highlands around Guadalajara and Puebla, then the Gulf and the Caribbean.",
        "before": [
            "<strong>Passport</strong> and a <strong>tourist permit (FMM)</strong>. See " + L_INM + ".",
            "<strong>Vehicle permit (TIP)</strong> from " + L_BANJERCITO + ": you need one as soon as you leave the border zone (in Sonora, the free zone). Get it online 10 to 60 days ahead or at a Banjercito office at the border. It takes a refundable deposit based on the car's year. Cancel it at the border on your way out to get the deposit back.",
            "<strong>Mexican car insurance.</strong> US policies generally don't cover you in Mexico.",
            "<strong>Pesos for tolls.</strong> Most of the way is on toll roads (cuotas). Many booths take cards, but not all, so carry cash.",
            "<strong>Safety:</strong> the route crosses states with different US travel advisory levels, and they change. Read the " + L_ADVISORY + " for each state before you go.",
        ],
        "days": [
            ("Day 1: Tijuana to Hermosillo", "About 550 mi (885 km), 10 h", [
                "Cross at Otay Mesa, San Ysidro or Tecate. Mexico Highway 2D east climbs La Rumorosa, a steep grade with wind and sometimes fog, to Mexicali.",
                "Then Highway 2 through San Luis Río Colorado and the Altar Desert to Sonoyta and Caborca, and south to Hermosillo.",
                "<strong>Fill up whenever you're at half a tank.</strong> Some desert stretches have long gaps between stations.",
            ]),
            ("Day 2: Hermosillo to Mazatlán", "About 535 mi (860 km), 10 h", [
                "Highway 15, four lanes most of the way: Guaymas, Ciudad Obregón, Navojoa, Los Mochis, Culiacán.",
                "Many toll booths today. Keep pesos handy.",
                "Carry your vehicle permit. You're outside the free zone now.",
            ]),
            ("Day 3: Mazatlán to Guadalajara", "About 305 mi (490 km), 5.5 h", [
                "Highway 15D through Tepic and into the mountains. A shorter day, with time for Mazatlán's malecón in the morning.",
            ]),
            ("Day 4: Guadalajara to Puebla", "About 405 mi (650 km), 7.5 h", [
                "Toll roads to Querétaro, then the Arco Norte around Mexico City, so you skip its traffic and driving restrictions.",
            ]),
            ("Day 5: Puebla to Villahermosa", "About 405 mi (650 km), 7.5 h", [
                "Highway 150D east past Pico de Orizaba, down the Cumbres de Maltrata grade (often foggy), through Córdoba and on to the Gulf.",
                "Detour: some drivers go through Veracruz city or Oaxaca instead. It's slower but has great stops.",
            ]),
            ("Day 6: Villahermosa to Bacalar", "About 335 mi (540 km), 6.5 h", [
                "Highway 186 east through Escárcega. Long stretches with few towns, so <strong>fill up in Escárcega</strong>.",
                "Bacalar's lagoon of seven colors is worth the night.",
            ]),
            ("Day 7: Bacalar to Playa del Carmen", "About 175 mi (280 km), 3.5 h", [
                "Highway 307 north through Felipe Carrillo Puerto and Tulum.",
                "Quintana Roo is an hour ahead of central Mexico all year.",
            ]),
        ],
        "tips": [
            "Most people driving across Mexico plan to arrive before dark.",
            "Military and National Guard checkpoints are routine. Slow down, be polite and have your papers ready.",
            "Watch for speed bumps (topes) entering every town, often unmarked.",
            "Gas stations are full service. Check that the pump starts at zero. Prices: " + L_GAS_MX + ".",
            "Roadside help: the Ángeles Verdes (Green Angels) answer at 078.",
            "Two cars? Agree on each day's gas stops and the hotel before you lose signal in the desert.",
        ],
    },
]

# Spanish versions of the Mexico routes. "en" is the slug of the English page they mirror.
ES_HUB = "/es/rutas/"
L_ADVISORY_ES = '<a href="https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/mexico-travel-advisory.html">aviso de viaje de EE. UU. para México</a> (en inglés)'
L_INM_ES = '<a href="https://www.gob.mx/inm">INM</a>'
L_CBP_LUKEVILLE_ES = '<a href="https://www.cbp.gov/contact/ports/lukeville">página de CBP de Lukeville</a> (en inglés)'
L_BORDER_ES = '<a href="/es/garitas/">tiempos de espera en las garitas</a>'
L_GAS_MX_ES = '<a href="/es/gasolina/">precio de la gasolina</a>'

ES_ROUTES = [
    {
        "slug": "phoenix-a-puerto-penasco", "en": "phoenix-to-puerto-penasco",
        "title": "De Phoenix a Puerto Peñasco en auto",
        "h1": "De Phoenix a Puerto Peñasco",
        "desc": "Cómo llegar en auto de Phoenix a Puerto Peñasco por Ajo, Organ Pipe y la garita de Lukeville: unos 345 km y 4 horas, más lo que necesitas para entrar a México (seguro, pasaporte, permisos).",
        "facts": [("Unos 345 km", "215 millas"), ("Unas 4 h", "más la garita"), ("1 día", ""), ("EE. UU. y México", "Arizona y Sonora")],
        "lead": "La playa de Arizona: al sur por Ajo y el Monumento Nacional Organ Pipe Cactus, cruzando por Lukeville y Sonoyta, hasta el Mar de Cortés.",
        "before": [
            "<strong>Pasaporte</strong> o pasaporte en tarjeta para todos, para volver a Estados Unidos. Los ciudadanos de EE. UU. menores de 16 años pueden usar acta de nacimiento en cruces terrestres.",
            "<strong>Seguro de auto mexicano.</strong> Los seguros de EE. UU. normalmente no te cubren en México. Compra una póliza mexicana antes de cruzar.",
            "<strong>No necesitas permiso de importación del auto.</strong> Puerto Peñasco está dentro de la zona libre de Sonora.",
            "<strong>Permiso de turista (FMM):</strong> las reglas para viajes cortos han cambiado con los años. Consulta con el " + L_INM_ES + " o en la oficina de Sonoyta.",
            "<strong>¿Auto rentado?</strong> Confirma que la arrendadora permite manejarlo en México.",
            "Lukeville no abre las 24 horas. Revisa el horario actual en la " + L_CBP_LUKEVILLE_ES + ".",
        ],
        "days": [
            ("Phoenix a Ajo", "Unos 175 km, 2 h", [
                "I-10 al oeste hasta la salida 112, luego la AZ-85 al sur por Gila Bend hasta Ajo.",
                "La plaza de estilo español de Ajo es buena para un descanso.",
            ]),
            ("Ajo a Lukeville", "Unos 60 km, 45 min", [
                "Por Why y el Monumento Nacional Organ Pipe Cactus. El centro de visitantes está junto a la AZ-85.",
                "<strong>Carga gasolina en Ajo o Why</strong> antes de la frontera.",
            ]),
            ("Sonoyta a Puerto Peñasco", "Unos 100 km, 1 h", [
                "Cruza por Lukeville a Sonoyta y toma la carretera federal 8 al sur, por el desierto, hasta la costa.",
                "En Puerto Peñasco se usan pesos y dólares.",
            ]),
        ],
        "tips": [
            "De regreso: las filas en Lukeville crecen los domingos por la tarde y después de puentes. Revisa los " + L_BORDER_ES + " antes de salir.",
            "Hay un punto de revisión de la Patrulla Fronteriza en la AZ-85 rumbo al norte. Ten tu identificación a la mano.",
            "¿Van en dos autos? Crucen juntos y acuerden dónde verse en Sonoyta por si a uno lo pasan a revisión.",
        ],
    },
    {
        "slug": "tijuana-a-playa-del-carmen", "en": "tijuana-to-playa-del-carmen",
        "title": "De Tijuana a Playa del Carmen en auto en 7 días",
        "h1": "De Tijuana a Playa del Carmen en auto",
        "desc": "Cruzar México en auto de Tijuana a Playa del Carmen en 7 días: unos 4,350 km por Hermosillo, Mazatlán, Guadalajara, Puebla, Villahermosa y Bacalar, con permisos, casetas y gasolina.",
        "facts": [("Unos 4,350 km", "2,700 millas"), ("Unas 50 h", "manejando"), ("7 días", ""), ("México", "de Baja California a Quintana Roo")],
        "lead": "De costa a costa: el desierto de Sonora, el Pacífico en Mazatlán, el centro del país por Guadalajara y Puebla, y luego el Golfo y el Caribe.",
        "before": [
            "<strong>Pasaporte</strong> y <strong>permiso de turista (FMM)</strong> si no eres mexicano. Consulta con el " + L_INM_ES + ".",
            "<strong>Permiso de importación temporal del auto (TIP)</strong> de " + L_BANJERCITO + ", si el auto tiene placas extranjeras: lo necesitas en cuanto sales de la franja fronteriza (en Sonora, de la zona libre). Sácalo en línea de 10 a 60 días antes o en un módulo de Banjercito en la frontera. Pide un depósito reembolsable según el año del auto. Cancélalo en la frontera al salir para que te regresen el depósito.",
            "<strong>Seguro de auto mexicano.</strong> Los seguros de EE. UU. normalmente no te cubren en México.",
            "<strong>Efectivo para casetas.</strong> Casi todo el camino es por autopistas de cuota. Muchas casetas aceptan tarjeta, pero no todas.",
            "<strong>Seguridad:</strong> la ruta cruza estados con distintos niveles en el " + L_ADVISORY_ES + ", y cambian. Revísalo para cada estado antes de salir.",
        ],
        "days": [
            ("Día 1: Tijuana a Hermosillo", "Unos 885 km, 10 h", [
                "La 2D al este sube La Rumorosa, una cuesta empinada con viento y a veces neblina, hasta Mexicali.",
                "Luego la federal 2 por San Luis Río Colorado y el Desierto de Altar hasta Sonoyta y Caborca, y al sur a Hermosillo.",
                "<strong>Carga gasolina cuando llegues a medio tanque.</strong> En el desierto hay tramos largos sin gasolineras.",
            ]),
            ("Día 2: Hermosillo a Mazatlán", "Unos 860 km, 10 h", [
                "La 15, de cuatro carriles casi todo el camino: Guaymas, Ciudad Obregón, Navojoa, Los Mochis, Culiacán.",
                "Hoy pasas muchas casetas. Ten pesos a la mano.",
                "Si tu auto trae placas extranjeras, lleva el permiso del auto: ya saliste de la zona libre.",
            ]),
            ("Día 3: Mazatlán a Guadalajara", "Unos 490 km, 5.5 h", [
                "La 15D por Tepic y la sierra. Un día más corto, con tiempo para el malecón de Mazatlán en la mañana.",
            ]),
            ("Día 4: Guadalajara a Puebla", "Unos 650 km, 7.5 h", [
                "Autopistas de cuota hasta Querétaro y luego el Arco Norte, que rodea la Ciudad de México para evitar su tráfico y sus restricciones de circulación.",
            ]),
            ("Día 5: Puebla a Villahermosa", "Unos 650 km, 7.5 h", [
                "La 150D al este junto al Pico de Orizaba, bajando las Cumbres de Maltrata (con neblina seguido), por Córdoba y hasta el Golfo.",
                "Otra opción: hay quien pasa por el puerto de Veracruz u Oaxaca. Es más lento, pero con muy buenas paradas.",
            ]),
            ("Día 6: Villahermosa a Bacalar", "Unos 540 km, 6.5 h", [
                "La 186 al este por Escárcega. Tramos largos con pocos pueblos, así que <strong>carga gasolina en Escárcega</strong>.",
                "La laguna de los siete colores de Bacalar vale la noche.",
            ]),
            ("Día 7: Bacalar a Playa del Carmen", "Unos 280 km, 3.5 h", [
                "La 307 al norte por Felipe Carrillo Puerto y Tulum.",
                "Quintana Roo va una hora adelante del centro del país todo el año.",
            ]),
        ],
        "tips": [
            "Casi todos los que cruzan México en auto planean llegar antes de que oscurezca.",
            "Los retenes del Ejército y la Guardia Nacional son normales. Baja la velocidad, sé amable y ten tus papeles listos.",
            "Cuidado con los topes al entrar a cada pueblo; muchos no tienen señal.",
            "En las gasolineras te atienden. Fíjate que la bomba empiece en cero. Revisa el " + L_GAS_MX_ES + ".",
            "Ayuda en carretera: los Ángeles Verdes contestan en el 078.",
            "¿Van en dos autos? Acuerden las paradas de gasolina y el hotel de cada día antes de quedarse sin señal en el desierto.",
        ],
    },
]

TEXT = {
    "en": {
        "hub": HUB, "home": "/", "crumb": "Road trip routes",
        "before": "Before you go", "route": "The route", "know": "Good to know",
        "written": "Written by the Cerqa team on {date} from public sources. Distances and times are rough driving estimates without stops. Rules, hours and fees change, so check the official links before you go. Drove it recently? <a href=\"{fb}\">Tell us what's changed</a>.",
        "int_h": "Drive this route with your group",
        "int_p": "We're thinking about letting you save routes like this in Cerqa, start them as a trip, and see everyone's live location and arrival time on the way. Would you use it?",
        "int_btn": "I'd use this", "stores": "Cerqa is free today:", "cc": "us",
        "footer": [("/feedback", "Feedback"), ("/support/", "Support"), ("/privacy/en/", "Privacy Policy"), ("/terms/en/", "Terms of Service")],
        "lang_name": "Español", "lang_attr": "es",
        "date": "October 21, 2026",
    },
    "es": {
        "hub": ES_HUB, "home": "/es/", "crumb": "Rutas en auto",
        "before": "Antes de salir", "route": "La ruta", "know": "Bueno saber",
        "written": "Escrito por el equipo de Cerqa el {date} con fuentes públicas. Las distancias y los tiempos son estimados de manejo sin paradas. Las reglas, los horarios y las cuotas cambian, así que revisa las ligas oficiales antes de salir. ¿La manejaste hace poco? <a href=\"{fb}\">Cuéntanos qué cambió</a>.",
        "int_h": "Maneja esta ruta con tu grupo",
        "int_p": "Estamos pensando en dejarte guardar rutas como esta en Cerqa, empezarlas como viaje y ver la ubicación en vivo y la hora de llegada de todos en el camino. ¿La usarías?",
        "int_btn": "Sí la usaría", "stores": "Cerqa es gratis hoy:", "cc": "mx",
        "footer": [("/feedback", "Comentarios"), ("/support/", "Ayuda"), ("/privacy/es/", "Aviso de privacidad"), ("/terms/es/", "Términos del servicio")],
        "lang_name": "English", "lang_attr": "en",
        "date": "21 de octubre de 2026",
    },
}
EN_TO_ES = {r["en"]: r["slug"] for r in ES_ROUTES}

STYLE = """<style>
.route-facts { display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 8px; padding: 0; list-style: none; }
.route-facts li { background: #fff; border: 1px solid #dde5ee; border-radius: 12px; padding: 10px 14px; min-width: 120px; }
.route-facts strong { display: block; font-size: 17px; }
.route-facts span { font-size: 13px; color: #6b7a8d; }
.route-days { list-style: none; padding: 0; margin: 0; }
.route-day { background: #fff; border: 1px solid #dde5ee; border-radius: 16px; padding: 16px 20px; margin: 0 0 12px; box-shadow: 0 6px 24px rgba(27,45,74,0.06); }
.route-day h3 { font-size: 17px; margin: 0; }
.route-day .leg { font-size: 14px; color: #6b7a8d; margin: 2px 0 8px; }
.route-day ul, .route-list { margin: 0; padding-left: 20px; }
.route-day li, .route-list li { margin: 4px 0; }
.route-written { font-size: 13px; color: #6b7a8d; margin: 24px 0 0; }
.route-interest { background: #fff; border: 1px solid #dde5ee; border-radius: 16px; padding: 20px; margin: 40px 0 0; }
.route-interest h2 { margin: 0 0 6px; }
.route-interest p { margin: 0 0 14px; color: #4b5b73; }
.route-interest .btn { display: inline-block; background: #465D91; color: #fff; font-weight: 700; padding: 10px 18px; border-radius: 999px; text-decoration: none; }
.route-interest .stores { margin-top: 14px; font-size: 14px; }
.route-interest .stores a { margin-right: 14px; font-weight: 600; }
.route-cards { list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }
.route-cards a { display: block; background: #fff; border: 1px solid #dde5ee; border-radius: 16px; padding: 16px 20px; text-decoration: none; color: inherit; }
.route-cards strong { display: block; font-size: 17px; color: #1b2d4a; }
.route-cards span { font-size: 14px; color: #6b7a8d; }
</style>"""


def page(lang, path, title, desc, body, alt_path=None):
    t = TEXT[lang]
    alt_links, lang_nav = "", ""
    if alt_path:
        en_path, es_path = (path, alt_path) if lang == "en" else (alt_path, path)
        alt_links = (f'\n<link rel="alternate" hreflang="en" href="{SITE}{en_path}">'
                     f'\n<link rel="alternate" hreflang="es" href="{SITE}{es_path}">'
                     f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{en_path}">')
        lang_nav = f'\n  <a class="site-nav-lang" href="{alt_path}" hreflang="{t["lang_attr"]}" lang="{t["lang_attr"]}">{t["lang_name"]}</a>'
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Cerqa</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{path}">{alt_links}
<link rel="icon" type="image/png" sizes="32x32" href="/images/icon/favicon-32.png">
<link rel="apple-touch-icon" href="/images/icon/apple-touch-icon.png">
<meta name="apple-itunes-app" content="app-id=6762389261">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Cerqa">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/social/cerqa-{lang}.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/border.css">
{STYLE}{GA}
</head>
<body>
<nav class="site-nav">
  <a class="site-nav-brand" href="{t['home']}">Cerqa</a>{lang_nav}
</nav>
<main>
{body}
</main>
<footer>
  <p>© 2026 Cerqa</p>
  {' '.join(f'<a href="{h}">{n}</a>' for h, n in t['footer'])}
</footer>
</body>
</html>
"""


def interest(lang, slug):
    # The click is the signal for CAT-65; the feedback page lets people say more.
    t = TEXT[lang]
    track = f"if(typeof gtag==='function')gtag('event','route_interest',{{route:'{slug}',lang:'{lang}'}})"
    return f"""<section class="route-interest">
  <h2>{t['int_h']}</h2>
  <p>{t['int_p']}</p>
  <a class="btn" href="/feedback?topic=routes&amp;route={slug}" onclick="{track}">{t['int_btn']}</a>
  <div class="stores">{t['stores']}
    <a href="{APP_STORE.format(cc=t['cc'])}" target="_blank" rel="noopener">App Store</a>
    <a href="{PLAY.format(campaign='route_' + slug.replace('-', '_'))}" target="_blank" rel="noopener">Google Play</a>
  </div>
</section>"""


def build_route(lang, r):
    t = TEXT[lang]
    facts = "\n".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in r["facts"])
    before = ""
    if r.get("before"):
        before = f"<h2>{t['before']}</h2>\n<ul class=\"route-list\">\n" + "\n".join(f"<li>{x}</li>" for x in r["before"]) + "\n</ul>"
    days = "\n".join(
        f"""<li class="route-day"><h3>{h}</h3><p class="leg">{leg}</p>
<ul>{''.join(f'<li>{x}</li>' for x in items)}</ul></li>""" for h, leg, items in r["days"])
    tips = "\n".join(f"<li>{x}</li>" for x in r["tips"])
    fb = f"/feedback?topic=routes&amp;route={r['slug']}"
    body = f"""<p class="crumbs"><a href="{t['hub']}">{t['crumb']}</a></p>
<h1>{r['h1']}</h1>
<p class="lead">{r['lead']}</p>
<ul class="route-facts">
{facts}
</ul>
{before}
<h2>{t['route']}</h2>
<ol class="route-days">
{days}
</ol>
<h2>{t['know']}</h2>
<ul class="route-list">
{tips}
</ul>
<p class="route-written">{t['written'].format(date=t['date'], fb=fb)}</p>
{interest(lang, r['slug'])}"""
    path = f"{t['hub']}{r['slug']}/"
    if lang == "es":
        alt = f"{HUB}{r['en']}/"
    else:
        alt = f"{ES_HUB}{EN_TO_ES[r['slug']]}/" if r["slug"] in EN_TO_ES else None
    return path, page(lang, path, r["title"], r["desc"], body, alt)


def build_hub(lang):
    t = TEXT[lang]
    routes = ROUTES if lang == "en" else ES_ROUTES
    cards = "\n".join(
        f"""<li><a href="{t['hub']}{r['slug']}/"><strong>{r['h1']}</strong><span>{r['facts'][0][0]}, {r['facts'][2][0]}. {r['lead']}</span></a></li>"""
        for r in routes)
    if lang == "en":
        h1, lead = "Road trip routes", "Routes across the US and Mexico, day by day: where to stop, where to fill up and what to bring."
        title, desc = ("Road trip routes in the US and Mexico",
                       "Day-by-day road trip routes in the US and Mexico: Phoenix to San Diego, a Grand Canyon loop, Phoenix to Rocky Point and Tijuana to Playa del Carmen.")
    else:
        h1, lead = "Rutas en auto", "Rutas por México, día por día: dónde parar, dónde cargar gasolina y qué llevar."
        title, desc = ("Rutas en auto por México",
                       "Rutas en auto día por día: de Tijuana a Playa del Carmen cruzando México y de Phoenix a Puerto Peñasco.")
    body = f"""<h1>{h1}</h1>
<p class="lead">{lead}</p>
<ul class="route-cards">
{cards}
</ul>
{interest(lang, 'hub')}"""
    alt = ES_HUB if lang == "en" else HUB
    return t["hub"], page(lang, t["hub"], title, desc, body, alt)


def write(path, html):
    out = path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(html)
    print("wrote", out)


if __name__ == "__main__":
    GA = analytics()
    write(*build_hub("en"))
    for r in ROUTES:
        write(*build_route("en", r))
    write(*build_hub("es"))
    for r in ES_ROUTES:
        write(*build_route("es", r))
