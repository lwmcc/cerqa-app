"""Week 3: school pickups. Searches: "school pickup app", "coordinate school pickups", "family location
sharing", "app para recoger a los niños de la escuela". Feature: Pick me up (1.19), family sharing.
Facts checked against the shipped app (2026-11-16): one person per request, optional "where to find you"
note, Now / In 15 / In 30 min, both share until the pickup, the driver gets "<name> needs a ride" with Go
or Can't, Go gives directions that follow the rider if they move. Accounts are 13 and up."""

POST = {
    "id": "school-pickups",
    "date": "2026-11-16",
    "image": "/images/blog/school-pickups.jpg",
    "en": {
        "slug": "make-school-pickups-easier",
        "title": "How to Make School Pickups Easier With Family Location Sharing | Cerqa",
        "h1": "How to Make School Pickups Easier With Family Location Sharing",
        "desc": "No more \"I'm here, where are you?\" in the school parking lot. Here is how to ask for a ride with one tap, watch the car arrive and walk straight to it, on iPhone and Android.",
        "image_alt": "Cerqa on iPhone and Android: a student asks for a ride from school and a parent sees the request",
        "body": """      <p>The bell rings. Your daughter grabs her backpack, walks out the front doors, and sends the same text she sends every day:</p>
      <p>"Are you here?"</p>
      <p>You're stuck behind a line of cars two blocks away. You reply at the next red light: "Almost. Where are you?" She answers: "Front entrance." But the front entrance is crowded, she can't see your car, and you can't see her. A few minutes later: "Which side are you on?"</p>
      <p>Meanwhile, your spouse texts too: "Are you getting her, or am I?"</p>
      <p>School pickups shouldn't take this many messages. Here's how to make them simpler, for the person waiting and for the person driving.</p>

      <h2>Why School Pickups Get Complicated</h2>
      <ul>
        <li><strong>Crowded lots and long lines.</strong> Dozens of cars arrive at the same time, and they all look alike from the curb.</li>
        <li><strong>Plans change during the day.</strong> Practice runs late, a club meeting gets canceled, or your teen wants a ride from a friend's house instead.</li>
        <li><strong>Two parents, one pickup.</strong> If nobody is sure who's going, both parents end up texting each other, and sometimes both show up.</li>
        <li><strong>Texting while driving.</strong> The person driving is the one who needs answers most, and the one who shouldn't be on the phone.</li>
      </ul>

      <h2>Ask for a Ride With Pick Me Up</h2>
      <p>With <strong>Cerqa</strong>, your teen doesn't have to send a string of texts. On the home screen, they tap <em>Pick me up</em>, choose who should pick them up, and tap <em>Ask for a ride</em>.</p>
      <p>They can add a short note about where to find them, like "Front entrance by the flagpole", and choose whether they need the ride now, in 15 minutes or in 30 minutes.</p>
      <p>The parent gets a simple request, like <em>"Ana needs a ride"</em>. One tap on <em>Go</em> starts directions straight to them. If the parent can't make it, they tap <em>Can't</em>, and your teen knows to ask someone else.</p>

      <h2>Watch the Car Arrive</h2>
      <p>Once the parent is on the way, you both share your location until the pickup. Your teen can see the car moving on the map and how far away it is, so there's no need to ask "how much longer?"</p>
      <p>And if they walk to a different spot, maybe from the front entrance to the gym or the side gate, the parent's directions follow them. Nobody has to explain where they moved.</p>
      <p>When the car pulls in, your teen can see exactly where it is in the lot and walk straight to it.</p>

      <h2>Everyday Family Sharing</h2>
      <p>School isn't the only pickup. There's practice, after-school jobs, friends' houses and late-night rides home.</p>
      <p>Cerqa lets your family share locations as a group, so everyone can see who's on the way and when they'll arrive. On the free plan, groups of up to 5 people can share for up to an hour at a time. With <a href="/#plans">Cerqa Pro</a>, you can share for up to 24 hours.</p>
      <p>It works between iPhone and Android phones, so a parent with an iPhone and a teen with an Android phone see each other on the same map. Here's more about <a href="/blog/share-location-between-iphone-and-android/">sharing your location between iPhone and Android</a>.</p>

      <h2>Privacy Stays in Your Hands</h2>
      <p>Your location goes only to the people you choose, and sharing always has an end. Either of you can stop sharing with one tap at any time. Cerqa isn't watching your family around the clock. It's there for the moments you need to find each other.</p>
      <p>Cerqa accounts are for ages 13 and up, so Pick me up is a great fit for teens with their own phones.</p>

      <h2>Tips for Smoother Pickups</h2>
      <ul>
        <li><strong>Pick a regular meeting spot.</strong> A landmark like the flagpole or the gym doors is easier to find than "out front".</li>
        <li><strong>Use the note.</strong> A few words about where you're waiting save a lot of back and forth.</li>
        <li><strong>Ask a little early.</strong> If practice ends at 5:00, ask for a ride in 15 minutes instead of waiting until you walk out.</li>
        <li><strong>Let the driver drive.</strong> The parent only needs to tap <em>Go</em>. Directions and the map do the rest.</li>
      </ul>
      <p><strong>Pickups don't need a dozen texts. One tap to ask, one tap to go, and everyone knows where everyone is.</strong></p>
""",
        "faq": [
            ("Is there an app that makes school pickups easier?", "Yes. With Cerqa, your teen taps Pick me up, chooses who should pick them up and adds a note about where to find them. The parent taps Go to get directions, and you both see each other on the map until the pickup."),
            ("Does it work between iPhone and Android?", "Yes. Cerqa works on iPhone and Android phones, so families with both see each other on the same map."),
            ("Is Pick me up free?", "Yes. Pick me up is free. Family groups of up to 5 people can also share their location for up to an hour at a time for free."),
            ("How old does my child need to be?", "Cerqa accounts are for ages 13 and up."),
            ("Does sharing stay on all the time?", "No. Sharing has an end, and either person can stop it with one tap."),
        ],
    },
    "es": {
        "slug": "recoger-a-los-ninos-de-la-escuela-mas-facil",
        "image": "/images/blog/school-pickups-es.jpg",
        "title": "Cómo hacer más fácil recoger a tus hijos de la escuela compartiendo la ubicación en familia | Cerqa",
        "h1": "Cómo hacer más fácil recoger a tus hijos de la escuela compartiendo la ubicación en familia",
        "desc": "Se acabó el \"ya llegué, ¿dónde estás?\" en el estacionamiento de la escuela. Así se pide un ride con un toque, se ve llegar el carro y se camina directo a él, en iPhone y Android.",
        "image_alt": "Cerqa en iPhone y Android: una estudiante pide que la recojan de la escuela y su papá ve la solicitud",
        "body": """      <p>Suena la campana. Tu hija toma su mochila, sale por la puerta principal y manda el mismo mensaje de todos los días:</p>
      <p>"¿Ya llegaste?"</p>
      <p>Tú vas en una fila de carros a dos cuadras. Contestas en el siguiente semáforo: "Casi. ¿Dónde estás?" Ella responde: "En la entrada principal." Pero la entrada está llena de gente, ella no ve tu carro y tú no la ves a ella. Unos minutos después: "¿De qué lado estás?"</p>
      <p>Mientras tanto, tu pareja también escribe: "¿Vas tú por ella o voy yo?"</p>
      <p>Recoger a los niños de la escuela no debería tomar tantos mensajes. Así puedes hacerlo más fácil, para quien espera y para quien maneja.</p>

      <h2>Por qué se complica recoger a los niños</h2>
      <ul>
        <li><strong>Estacionamientos llenos y filas largas.</strong> Llegan decenas de carros al mismo tiempo y desde la banqueta todos se ven iguales.</li>
        <li><strong>Los planes cambian durante el día.</strong> El entrenamiento se alarga, se cancela una reunión o tu hijo quiere que lo recojan en casa de un amigo.</li>
        <li><strong>Dos papás, una sola recogida.</strong> Si nadie sabe quién va, los dos terminan mandándose mensajes, y a veces llegan los dos.</li>
        <li><strong>Mensajes mientras manejas.</strong> Quien maneja es quien más necesita respuestas, y quien no debería usar el teléfono.</li>
      </ul>

      <h2>Pide que te recojan con Recógeme</h2>
      <p>Con <strong>Cerqa</strong>, tu hijo no tiene que mandar una cadena de mensajes. En la pantalla de inicio toca <em>Recógeme</em>, elige quién lo debe recoger y toca <em>Pedir que me recojan</em>.</p>
      <p>Puede agregar una nota corta sobre dónde encontrarlo, como "Entrada principal, junto al asta de la bandera", y elegir si necesita que lo recojan ahora, en 15 minutos o en 30 minutos.</p>
      <p>El papá o la mamá recibe una solicitud sencilla, como <em>"¿Recoges a Ana?"</em> Con un toque en <em>Voy</em> empiezan las indicaciones directo a él. Si no puede ir, toca <em>No puedo</em>, y tu hijo sabe que debe pedírselo a alguien más.</p>

      <h2>Mira cómo llega el carro</h2>
      <p>Cuando el papá o la mamá va en camino, los dos comparten su ubicación hasta la recogida. Tu hijo ve el carro moverse en el mapa y qué tan lejos está, así que no hace falta preguntar "¿cuánto te falta?"</p>
      <p>Y si camina a otro lugar, por ejemplo de la entrada principal al gimnasio o a la puerta lateral, las indicaciones lo siguen. Nadie tiene que explicar a dónde se movió.</p>
      <p>Cuando el carro entra, tu hijo ve exactamente dónde está en el estacionamiento y camina directo a él.</p>

      <h2>Compartir en familia todos los días</h2>
      <p>La escuela no es la única recogida. Están los entrenamientos, el trabajo después de clases, la casa de los amigos y los rides de noche.</p>
      <p>Cerqa permite que tu familia comparta la ubicación en grupo, para que todos vean quién va en camino y a qué hora llega. Con el plan gratis, los grupos de hasta 5 personas pueden compartir hasta una hora a la vez. Con <a href="/es/#plans">Cerqa Pro</a> puedes compartir hasta 24 horas.</p>
      <p>Funciona entre iPhone y Android, así que un papá con iPhone y un hijo con Android se ven en el mismo mapa. Aquí hay más sobre <a href="/es/blog/compartir-ubicacion-entre-iphone-y-android/">cómo compartir la ubicación entre iPhone y Android</a>.</p>

      <h2>Tu privacidad en tus manos</h2>
      <p>Tu ubicación solo la ven las personas que tú eliges, y compartir siempre tiene un final. Cualquiera de los dos puede dejar de compartir con un toque en cualquier momento. Cerqa no está vigilando a tu familia todo el día. Está para los momentos en que necesitan encontrarse.</p>
      <p>Las cuentas de Cerqa son para mayores de 13 años, así que Recógeme es ideal para adolescentes con su propio teléfono.</p>

      <h2>Consejos para recoger más fácil</h2>
      <ul>
        <li><strong>Elijan un punto de encuentro fijo.</strong> Un lugar como el asta de la bandera o la puerta del gimnasio es más fácil de encontrar que "afuera".</li>
        <li><strong>Usen la nota.</strong> Unas palabras sobre dónde esperas ahorran muchos mensajes.</li>
        <li><strong>Pidan un poco antes.</strong> Si el entrenamiento termina a las 5:00, pide que te recojan en 15 minutos en lugar de esperar a salir.</li>
        <li><strong>Que quien maneja solo maneje.</strong> Basta con tocar <em>Voy</em>. Las indicaciones y el mapa hacen el resto.</li>
      </ul>
      <p><strong>Recoger a los niños no necesita una docena de mensajes. Un toque para pedir, un toque en Voy, y todos saben dónde está cada quien.</strong></p>
""",
        "faq": [
            ("¿Hay una app que haga más fácil recoger a los niños de la escuela?", "Sí. Con Cerqa, tu hijo toca Recógeme, elige quién lo debe recoger y agrega una nota sobre dónde encontrarlo. El papá o la mamá toca Voy para recibir indicaciones, y los dos se ven en el mapa hasta la recogida."),
            ("¿Funciona entre iPhone y Android?", "Sí. Cerqa funciona en iPhone y en Android, así que las familias con los dos se ven en el mismo mapa."),
            ("¿Recógeme es gratis?", "Sí. Recógeme es gratis. Los grupos familiares de hasta 5 personas también pueden compartir su ubicación gratis hasta una hora a la vez."),
            ("¿Qué edad necesita tener mi hijo?", "Las cuentas de Cerqa son para mayores de 13 años."),
            ("¿Se comparte la ubicación todo el tiempo?", "No. Compartir tiene un final, y cualquiera de los dos puede detenerlo con un toque."),
        ],
    },
}
