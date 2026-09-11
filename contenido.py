# -*- coding: utf-8 -*-
"""Fuente única de la copy de la landing.

Las tres propuestas rinden este mismo contenido: lo que cambia entre ellas es
el diseño, nunca el texto. Editar aquí y volver a ejecutar construir.py.

REGLA INNEGOCIABLE DEL CLIENTE: en esta landing no puede aparecer ninguna cifra
económica — ni precio, ni matrícula, ni cuotas, ni planes de pago, ni rangos.
Todo eso se comunica en privado durante la entrevista de admisión.
construir.py verifica esto antes de escribir los archivos.
"""

# La dirección pública, que hacen falta la canónica y las etiquetas para
# compartir en redes. Sin barra final: es como la sirve el dominio.
SITIO = "https://web-crea-y-monetiza.perfectflow.cloud"

MARCA = {
    "nombre": "Crea y Monetiza Campus",
    "dominio": "web-crea-y-monetiza.perfectflow.cloud",
    "descripcion": (
        "Formación integral de 6 meses para creadoras de contenido: marca personal, "
        "UGC profesional, negocio, inteligencia artificial y monetización."
    ),
}

# El ancla de cada entrada es también el id de la sección correspondiente.
# Las anclas tienen que existir como id de sección. Al fusionar bloques
# desaparecieron varias, así que la navegación se ajusta al mapa nuevo.
NAV = [
    ("Inicio", "inicio"),
    ("El Campus", "campus"),
    ("Tu recorrido", "recorrido"),
    ("Plan de estudios", "plan"),
    ("La Tesis", "tesis"),
    ("Experiencia", "experiencia"),
    # ("Mentoras", "mentoras"),  — la sección salió de la página; un enlace del
    # menú a un ancla que ya no existe deja al visitante en el mismo sitio sin
    # explicación.
    ("Admisiones", "admisiones"),
]

CTA_FIJO = "Iniciar admisión"

# El equipo se anuncia ya en el hero. Es el activo de confianza principal —los
# dos competidores directos ponen a la fundadora arriba del todo— y estaba
# enterrado en la sección 11.
EQUIPO_HERO = {
    "etiqueta": "Tu equipo",
    "personas": ["Pierina Alves", "Paola", "Nathaly"],
}

# 01
HERO = {
    "eyebrow": "Admisiones · Crea y Monetiza Campus",
    "titulo": "Tu talento puede convertirse en una carrera profesional.",
    "entrada": (
        "Bienvenida a Crea y Monetiza Campus, una formación integral para creadoras "
        "de contenido que quieren profesionalizar su talento, construir una marca con "
        "dirección y aprender a generar oportunidades reales dentro del mundo digital."
    ),
    "materias": [
        "Marca personal.",
        "Creación de contenido.",
        "UGC profesional.",
        "Negocio.",
        "Organización y productividad.",
        "Monetización.",
    ],
    "remate": "Todo dentro de una misma ruta formativa.",
    "cta_1": "Iniciar mi proceso de admisión",
    "cta_2": "Conocer el Campus",
    "cifras": [
        ("+270", "creadoras formadas"),
        ("6", "meses de recorrido"),
        # Con "+" porque ya son más de trece y siguen sumando: un número
        # cerrado quedaría desactualizado en cuanto se añada una.
        ("+10", "materias"),
        ("1:1", "acompañamiento cercano"),
    ],
}

# 02
CARTA = {
    "eyebrow": "Carta de bienvenida · Pierina Alves",
    "titulo": "Antes de entrar, quiero contarte por qué existe este Campus.",
    "parrafos": [
        "Durante años he creado contenido, trabajado con marcas, probado estrategias, "
        "cometido errores y acompañado a cientos de creadoras en su proceso.",
        "Y había algo que seguía viendo una y otra vez: mujeres con muchísimo talento "
        "intentando construir una carrera con información suelta.",
        "Un curso para aprender edición. Otro para entender redes. Tutoriales sobre UGC. "
        "Videos sobre cómo contactar marcas. Plantillas, prompts, consejos… pero ninguna "
        "ruta que conectara todo.",
        "Por eso nació Crea y Monetiza Campus.",
        "Quería construir un lugar donde una creadora pudiera formarse de manera integral "
        "y entender cómo pasar de tener talento y muchas ideas a tener estructura, criterio, "
        "herramientas y una dirección profesional.",
        "En este video quiero contarte de dónde viene el Campus, qué significa para mí y "
        "por qué hemos decidido construirlo de esta manera.",
    ],
    "video_id": "P2U3sFLbljE",
    "video_inicio": 8,
    "video_titulo": "Por qué nació Crea y Monetiza Campus",
    "cita": "Quería crear el lugar que yo habría necesitado cuando empecé.",
    "cita_autora": "Pierina Alves",
    "cta": "Continuar mi recorrido",

    # La carta llega cerrada y se abre al pulsar. Antes se leía como otro bloque
    # de texto largo; así se lee como lo que es, una carta de la rectora.
    "sobre_de": "De la rectora",
    "sobre_para": "Para la próxima creadora del Campus",
    "sobre_abrir": "Abrir la carta",
    "sobre_cerrar": "Cerrar la carta",

    # Quién firma. Los datos que faltan llegan de Pierina; hasta entonces van
    # entre corchetes y marcados en pantalla, nunca inventados.
    "trayectoria": {
        # El titular se retira: el bloque va pegado a la firma de la carta y se
        # entiende solo. Las creadoras acompañadas también, porque son las mismas
        # +270 que ya cuenta el hero.
        "cifras": [
            ("[años]", "años creando contenido"),
            ("+30", "marcas nacionales e internacionales de tecnología, belleza, "
                    "inteligencia artificial y bienestar."),
        ],
        "marcas_t": "Entre ellas se encuentran",
        "marcas": ["DJI", "CapCut", "FlexiSpot", "Higgsfield",
                   "Lovart.ai", "Pollo AI", "Musso", "Pantene"],
        "marcas_falta": "Faltan los nombres de las marcas",
    },
}

# El cortometraje vertical que sustituye a la tarjeta de perfil en el hero.
# El archivo llega por Drive; hasta que esté en assets/ con este nombre, la
# página mantiene el perfil que se arma solo y señala el hueco.
HERO_VIDEO = {
    "archivo": "hero-cortometraje.mp4",
    "poster": "hero-cortometraje.webp",
    "titular": "Yo también estuve allí.",
    "texto": "Te aseguro que vale la pena creer en ti.",
    "alt": "Cortometraje de Pierina Alves sobre sus inicios como creadora",
    "nota_falta": "Aquí va el cortometraje vertical",
    # El navegador solo deja arrancar un video solo si va sin sonido, así que
    # empieza mudo y el sonido se activa desde aquí.
    "sonido_on": "Activar el sonido",
    "sonido_off": "Silenciar",
}

# 03
CAMPUS = {
    "eyebrow": "¿Qué es Crea y Monetiza Campus?",
    "titulo": "Aquí no vienes a ver clases, vienes a formarte.",
    "intro": [
        "Crear contenido puede convertirse en una profesión.",
        "Pero para construir una carrera necesitas mucho más que saber grabar un buen video.",
    ],
    "necesidades": [
        "Entender quién eres como creadora.",
        "Qué quieres comunicar.",
        "Cómo desarrollar una marca reconocible.",
        "Cómo crear contenido con intención.",
        "Cómo utilizar herramientas que hagan tu trabajo más eficiente.",
        "Cómo presentar tu talento profesionalmente.",
        "Cómo trabajar con marcas.",
        "Cómo negociar.",
        "Cómo monetizar.",
        "Y cómo construir oportunidades alrededor de todo eso.",
    ],
    "cierre": [
        "Eso es lo que conecta Crea y Monetiza Campus.",
        "Una formación integral donde aprendes, implementas, recibes acompañamiento y "
        "construyes los activos que necesitarás para desarrollar tu carrera como creadora.",
    ],
}

# 03b — Comparación. Esta copy NO viene del guion original: la escribió Nathaly
# en su propuesta y se incorpora tal cual, a petición del cliente. Si Pierina
# quiere ajustarla, se edita aquí.
COMPARACION = {
    "izq_kicker": "Lo habitual",
    "izq_titulo": "Un curso grabado",
    "izq": [
        "Compras el acceso y avanzas sola.",
        "Videos sueltos sin orden ni criterio de avance.",
        "Nadie revisa lo que haces ni te corrige.",
        "Terminas con apuntes, no con activos.",
        "El día que se acaba, se acaba todo.",
    ],
    "der_kicker": "El Campus",
    "der_titulo": "Una formación universitaria",
    "der": [
        "Un plan de estudios de 10 materias con orden, ejercicios y entregables.",
        "Dos etapas: primero te formas, después sales al mercado.",
        "Mentoras que revisan tu trabajo y te corrigen de verdad.",
        "Sales con portafolio, pitch, tarifas y sistema de contenido.",
        "Te gradúas y recibes tu certificado de creadora profesional.",
    ],
}

# 04
PERFIL = {
    "eyebrow": "En qué te estás formando",
    "titulo": "No estás aquí para convertirte en «una chica que hace videos». Estás aquí para convertirte en una creadora profesional.",
    "ejes": [
        ("Identidad", "Construyes una marca personal con una identidad clara, coherente y reconocible."),
        ("Estrategia", "Aprendes a tomar decisiones detrás de tu contenido y dejar de publicar sin dirección."),
        ("Creación", "Desarrollas criterio para conceptualizar, grabar, comunicar y producir piezas de contenido profesionales."),
        ("Posicionamiento", "Trabajas una presencia digital capaz de comunicar quién eres, qué haces y qué valor puedes aportar."),
        ("Negocio", "Aprendes a presentar tus servicios, estructurar propuestas, negociar y relacionarte profesionalmente con marcas."),
        ("Monetización", "Exploras diferentes caminos para transformar tus habilidades creativas y digitales en oportunidades."),
    ],
    "cierre": "Aquí no trabajamos únicamente tu contenido. Trabajamos la creadora profesional que hay detrás de él.",
}

# 05
RECORRIDO = {
    "eyebrow": "Tu plan académico",
    "titulo": "6 meses · 2 etapas",
    "bajada": [
        "Tres meses para construir tus bases.",
        "Tres meses para llevarlas al mercado con acompañamiento.",
    ],
    "etapas": [
        {
            "n": "Etapa 01",
            "meses": "Meses 1–3 · Formación",
            "titulo": "Construyes tus bases",
            "intro": "Comienzas con una ruta clara para entender qué necesitas trabajar, "
                     "qué debes priorizar y cómo avanzar dentro del Campus.",
            "lead": "Durante esta etapa:",
            "pasos": [
                "Realizas tu onboarding y diagnóstico inicial.",
                "Defines tus objetivos y tu ruta de trabajo.",
                "Comienzas tu formación a través del plan de estudios.",
                "Desarrollas ejercicios y entregables.",
                "Implementas lo aprendido en tu propio proyecto.",
                "Recibes acompañamiento y feedback.",
                "Evalúas tu progreso antes de pasar a la siguiente etapa.",
            ],
            "cierre": "Una marca personal que trasciende construye una base sólida.",
        },
        {
            "n": "Etapa 02",
            "meses": "Meses 4–6 · Implementación profesional",
            "titulo": "Sales al mercado",
            "intro": "En esta etapa empiezas a moverte como creadora profesional: "
                     "mostrar tu trabajo, conectar con marcas, detectar oportunidades "
                     "y comenzar a posicionarte dentro del mercado.",
            "lead": "Trabajarás sobre:",
            "pasos": [
                "Tu posicionamiento.", "Tu contenido.", "Tu portafolio.",
                "Tu propuesta profesional.", "Tu pitch.", "Tus conversaciones con marcas.",
                "Tus oportunidades.", "Tus negociaciones.",
                "Tu estrategia de monetización.", "Tu crecimiento.",
            ],
            "cierre": "Y durante todo este proceso seguirás contando con acompañamiento para "
                      "revisar, corregir y optimizar lo que estás implementando.",
        },
    ],
}

# 06
# El detalle del plan no se publica: es contenido exclusivo de las alumnas
# matriculadas. En la página quedan cómo está estructurado y la invitación a
# agendar la llamada de admisión.
PLAN = {
    "eyebrow": "Dentro del Campus",
    "titulo": "Tu plan de estudios.",
    "bajada": "Cada alumna accede a una formación estructurada por materias, clases, "
              "recursos y ejercicios diseñados para profesionalizar cada área de su "
              "carrera como creadora.",
    "exclusivo": "El plan de estudios es exclusivo para alumnas matriculadas en "
                 "Crea y Monetiza Campus.",

    "bloques": [
        ("Formación estructurada",
         "Materias organizadas para que sepas qué trabajar y en qué orden."),
        ("Clases + recursos",
         "Contenido formativo acompañado de herramientas, ejemplos y materiales de aplicación."),
        ("Ejercicios y entregables",
         "Cada bloque incluye trabajo práctico para llevar lo aprendido a tu propia realidad."),
        ("Contenido exclusivo del Campus",
         "El pensum completo se desbloquea una vez formalizas tu matrícula."),
    ],

    "cta_linea": "Conoce el proceso de admisión y da el primer paso para acceder a tu "
                 "formación completa dentro del Campus.",
    "cta_boton": "Desbloquear mi plan académico",
    # La llamada de admisión se agenda fuera del sitio.
    "cta_enlace": "https://calendly.com/encuentronl/45min",
}

# Duración de cada materia, por número de materia (1-10). El Campus tiene que
# confirmarlas; mientras estén vacías no se muestran.
DURACIONES = {
    1: "", 2: "", 3: "", 4: "", 5: "",
    6: "", 7: "", 8: "", 9: "", 10: "",
}

# 07
EVALUACION = {
    "eyebrow": "Aquí también se evalúa",
    "titulo": "No queremos que termines el Campus sabiendo más. Queremos que termines sabiendo hacer más.",
    "intro": [
        "Por eso tu progreso no se mide únicamente por las clases que has visto.",
        "Durante tu recorrido tendrás diferentes formas de poner en práctica lo aprendido.",
    ],
    "items": [
        ("Ejercicios", "Actividades diseñadas para aterrizar cada concepto a tu realidad."),
        ("Entregables", "Piezas concretas que tendrás que desarrollar durante tu formación."),
        ("Revisiones", "Espacios para recibir feedback y detectar qué necesitas mejorar."),
        ("Checkpoints", "Momentos específicos para revisar tu progreso y ajustar tu ruta."),
        ("Implementación", "Lo aprendido se aplica directamente a tu contenido, tu marca y tus activos profesionales."),
        ("Proyecto final", "El cierre de tu recorrido dentro del Campus."),
    ],
    "cierre": "Aquí no vienes a coleccionar clases terminadas. Vienes a construir evidencia de tu evolución.",
}

# 08
TESIS = {
    "eyebrow": "Proyecto final",
    "titulo": "Toda creadora del Campus termina con un proyecto final.",
    "lo_llamamos": "Lo llamamos:",
    "nombre": "La Tesis Creativa",
    "intro": [
        "Durante tus meses dentro del Campus irás construyendo diferentes partes de tu carrera profesional.",
        "Al finalizar tendrás que conectarlas dentro de un proyecto que represente lo que has desarrollado.",
    ],
    "lead": "Tu proyecto podrá integrar:",
    "integra": [
        "Tu identidad de marca.", "Tu posicionamiento.", "Tu estrategia de contenido.",
        "Tus piezas creativas.", "Tu portafolio.", "Tu propuesta profesional.",
        "Tu estrategia de monetización.", "Tu plan de crecimiento.",
    ],
    "cierre": [
        "No puedes completar tu recorrido únicamente viendo clases.",
        "Queremos que cuando llegues al final puedas mirar todo lo que construiste durante "
        "estos meses y ver, de forma tangible, tu evolución como creadora.",
    ],
}

# 09 — NO SE PUBLICA. "Tu campus, en un solo lugar" se retiró de la página por
# decisión del cliente. La copy se conserva por si vuelve; no se borra material
# del cliente por una decisión de maquetación.
DIGITAL = {
    "eyebrow": "Dónde vives la experiencia",
    "titulo": "Tu campus, en un solo lugar.",
    "piezas": ["Clases.", "Recursos.", "Entregables.", "Comunidad.", "Actualizaciones.", "Sesiones."],
    "remate": "Todo forma parte de un mismo ecosistema.",
    "bloques": [
        {
            "kicker": "La plataforma",
            "titulo": "Skool",
            "texto": ["Aquí encontrarás tus clases, recursos, materiales, entregables y acceso a la comunidad."],
            "lista": [],
            "placeholder": "Captura real de la plataforma",
        },
        {
            "kicker": "Seguimiento",
            "titulo": "Cerca, durante todo el proceso.",
            "texto": [
                "No tienes que desaparecer durante semanas y volver cuando tengas una duda.",
                "El acompañamiento forma parte del recorrido.",
                "Tendrás espacios para comunicar tus avances, resolver bloqueos y saber cuál "
                "es el siguiente paso que necesitas ejecutar.",
            ],
            "lista": [],
            "placeholder": "Capturas reales de seguimiento",
        },
        {
            "kicker": "Comunidad",
            "titulo": "No estás recorriendo esto sola.",
            "texto": [
                "Formar parte del Campus también significa compartir el proceso con creadoras "
                "que están construyendo sus propios proyectos.",
                "Un espacio para:",
            ],
            "lista": [
                "Compartir avances.", "Resolver dudas.", "Celebrar resultados.", "Conectar.",
                "Aprender de otros procesos.", "Descubrir oportunidades.",
                "Y crecer rodeada de personas que entienden lo que estás construyendo.",
            ],
            "placeholder": "Captura real de la comunidad",
        },
    ],
}

# 10
VIVO = {
    "eyebrow": "El Campus también pasa en directo",
    "titulo": "Hay cosas que necesitan conversación, no otra clase grabada.",
    "bajada": "Durante tu recorrido tendrás acceso a diferentes espacios en vivo.",
    "items": [
        ("Masterclasses", "Sesiones especiales sobre temas estratégicos, herramientas, tendencias y oportunidades para creadoras."),
        ("Q&A", "Espacios para llevar preguntas concretas y resolverlas junto al equipo."),
        ("Revisiones", "Sesiones destinadas a analizar casos, procesos y aplicaciones reales."),
        ("Encuentros de comunidad", "Momentos para conectar con otras alumnas y vivir el Campus más allá de la plataforma."),
    ],
}

# 11
FACULTAD = {
    "eyebrow": "Tu equipo",
    # NO SE PUBLICA: retirado por decisión del cliente. La sección arranca en
    # "Cada área necesita una mirada diferente".
    "titulo": "No dependes de una sola persona.",
    "intro": [
        "Cada área necesita una mirada diferente.",
        "Por eso dentro del Campus encontrarás especialistas que acompañan diferentes "
        "partes de tu formación.",
    ],
    "personas": [
        {
            "nombre": "Pierina Alves",
            "rol": "Dirección del Campus · Estrategia y creación",
            "bio": [
                "Fundadora de Crea y Monetiza.",
                "Creadora de contenido y mentora especializada en estrategia, UGC, "
                "posicionamiento y monetización.",
                "Pierina dirige la visión del Campus y comparte el conocimiento y los sistemas "
                "que ha aplicado en su propia carrera y en los procesos de cientos de creadoras.",
            ],
        },
        {
            "nombre": "Paola",
            "rol": "Seguimiento e implementación",
            "bio": [
                "Acompaña el proceso de ejecución para ayudarte a mantener dirección, detectar "
                "bloqueos y convertir lo aprendido en acciones concretas.",
            ],
        },
        {
            "nombre": "Nathaly",
            "rol": "Inteligencia artificial aplicada, organización y productividad",
            "bio": [
                "Te ayuda a entender cómo incorporar inteligencia artificial a tu trabajo como "
                "creadora para investigar, organizar, producir y optimizar procesos sin sustituir "
                "tu criterio creativo.",
            ],
        },
    ],
    "cierre": "Y a lo largo del Campus podrás encontrar nuevas especialistas, invitadas y "
              "masterclasses en áreas específicas de tu desarrollo profesional.",
}

# 12
MERCADO = {
    "eyebrow": "Experiencia profesional",
    # NO SE PUBLICA: retirado por decisión del cliente. La sección arranca
    # directamente con "Aprender a crear contenido es solo una parte".
    "titulo": "En algún momento tienes que salir del aula.",
    "intro": [
        "Aprender a crear contenido es solo una parte.",
        "También necesitas aprender qué hacer con esas habilidades cuando llega el momento "
        "de presentarte profesionalmente.",
    ],
    "lead": "Durante tu recorrido trabajarás en:",
    "items": [
        "Tu portafolio.", "Tu propuesta.", "Tu pitch.", "Tu comunicación con marcas.",
        "Tu estructura de precios.", "Tu negociación.", "Tu seguimiento.",
        "Tu presencia profesional.", "Tu estrategia para encontrar oportunidades.",
    ],
}

# 13
OPORTUNIDADES = {
    "eyebrow": "Oportunidades",
    "titulo": "Saber crear es importante. Saber dónde buscar también.",
    "intro": "Dentro del Campus tendrás acceso a recursos diseñados para acercarte al mercado profesional.",
    # Cada recurso con su icono. Van aquí y no en el CSS porque son contenido:
    # el Campus puede cambiarlos sin tocar una hoja de estilo.
    "items": [
        ("🏷️", "Marcas."),
        ("🏢", "Agencias."),
        ("📱", "Plataformas UGC."),
        ("💸", "Oportunidades."),
        ("🤝", "Referencias."),
        ("🔎", "Recursos de prospección."),
    ],
    "cierre": [
        "Información que te ayude a entender dónde buscar y cómo presentarte.",
        "Porque una formación para creadoras no estaría completa si después de aprender no "
        "supieras cómo empezar a moverte profesionalmente.",
    ],
}

# 14 — NO SE PUBLICA. "Cuando formas parte del Campus, no recibes solo clases"
# se retiró: descartado por diseño, y su contenido ya se repetía por toda la
# página. La copy se conserva por si vuelve.
EXPERIENCIA = {
    "eyebrow": "Tu experiencia dentro del Campus",
    "titulo": "Cuando formas parte del Campus, no recibes solo clases.",
    "items": [
        ("10 materias", "Una formación integral para desarrollar diferentes áreas de tu carrera."),
        ("6 meses de recorrido", "Formación, implementación y acompañamiento."),
        ("Ruta de trabajo", "Una dirección clara para entender qué aprender, qué aplicar y qué priorizar."),
        ("Equipo de mentoras", "Especialistas en diferentes áreas de tu desarrollo."),
        ("Masterclasses en vivo", "Nuevas sesiones durante tu recorrido."),
        ("Clases grupales y Q&A", "Espacios para preguntas, implementación y casos reales."),
        ("Seguimiento", "Acompañamiento para revisar tu progreso."),
        ("Recursos y plantillas", "Herramientas listas para ayudarte a ejecutar."),
        ("Portafolio profesional", "Trabajas uno de tus principales activos para presentarte ante marcas."),
        ("Pitch para marcas", "Aprendes a comunicar tu valor de una manera más profesional."),
        ("Banco de oportunidades", "Recursos para ayudarte a encontrar posibles oportunidades."),
        ("Comunidad privada", "Una red de creadoras viviendo el mismo proceso."),
        ("Proyecto final", "Cierras tu recorrido integrando lo que has construido."),
        ("Graduación", "Celebramos oficialmente el final de tu experiencia dentro del Campus."),
        ("Certificado de finalización", "Recibes el reconocimiento correspondiente por haber completado tu recorrido en Crea y Monetiza Campus."),
    ],
}

# 15 — Los casos van con datos reales; hasta entonces quedan marcados como pendientes.
HISTORIAS = {
    "eyebrow": "Alumnas · Casos reales",
    "titulo": "Antes de ser un resultado, todas fueron una creadora intentándolo.",
    "bajada": "Aquí queremos que conozcas algunos de los procesos que han formado parte de Crea y Monetiza.",
    "casos": [
        {"n": "Caso 01", "nombre": "[Nombre de alumna]", "lugar": "[Ciudad · País]",
         "campos": [("Su punto de partida", "[Texto breve sobre dónde estaba antes.]"),
                    ("Qué trabajó", "[Texto breve.]"),
                    ("Su resultado", "[Resultado real y comprobable.]")],
         "media": "Video / captura / testimonio"},
        {"n": "Caso 02", "nombre": "[Nombre de alumna]", "lugar": "[Ciudad · País]",
         "campos": [("Su punto de partida", "[Texto breve sobre dónde estaba antes.]"),
                    ("Qué trabajó", "[Texto breve.]"),
                    ("Su resultado", "[Resultado real y comprobable.]")],
         "media": "Video / captura / testimonio"},
        {"n": "Caso 03", "nombre": "[Nombre de alumna]", "lugar": "[Ciudad · País]",
         "campos": [("Su punto de partida", "[Texto breve sobre dónde estaba antes.]"),
                    ("Qué trabajó", "[Texto breve.]"),
                    ("Su resultado", "[Resultado real y comprobable.]")],
         "media": "Video / captura / testimonio"},
    ],
}

# 16
GRADUACION = {
    "eyebrow": "El final de tu recorrido",
    "titulo": "Y sí. También te gradúas.",
    "intro": [
        "Completar tu recorrido significa haber avanzado por tu plan de estudios, "
        "desarrollado tus entregables y presentado tu Proyecto Final.",
        "Y queremos celebrar ese momento como corresponde.",
    ],
    "bloques": [
        ("Graduación presencial",
         ["Encuentros especiales en España para celebrar juntas el cierre del recorrido."],
         "[Fechas según calendario de cada cohorte]"),
        ("Graduación online",
         ["Si formas parte del Campus desde otro país y no puedes asistir presencialmente, "
          "podrás vivir también tu cierre de manera online."], ""),
        ("Certificado de finalización",
         ["Al completar los requisitos del Campus recibirás tu certificado de finalización "
          "de Crea y Monetiza Campus."], ""),
    ],
    # NO SE PUBLICA: retirada por decisión del cliente. Se conserva la copy.
    "cierre": "No celebramos que terminaste unas clases. Celebramos todo lo que fuiste capaz "
              "de construir mientras las aplicabas.",
}

# 17
REGISTRO = {
    "eyebrow": "Registro de interés",
    "titulo": "Acceso prioritario al Campus.",
    "bajada": "Sé de las primeras en enterarte de todo lo que pasa en el Campus.",
    "items": ["Nuevas convocatorias.", "Fechas de admisión.", "Masterclasses.", "Novedades.",
              "Eventos.", "Recursos.", "Actualizaciones del Campus."],

    # Cabecera del expediente. El formulario se presenta como un documento de la
    # oficina de admisiones, no como un bloque de campos sueltos.
    "oficina": "Oficina de admisiones",
    "form_titulo": "Registro prioritario",
    "form_sub": "Formulario de interés",
    "lema": "Más mujeres creando la vida que aman.",

    # Las mismas preguntas de siempre, agrupadas en tres pasos. Cada grupo cita
    # los campos por su nombre, así que reordenar aquí reordena el formulario.
    "grupos": [
        ("Sobre ti", "Cuéntanos un poco de ti.", ["nombre", "apellido", "email", "pais"]),
        ("Tu momento actual", "Queremos conocer tu contexto.", ["social", "punto"]),
        ("Hacia dónde vas", "Esto es solo el comienzo.", ["objetivo"]),
    ],

    "campos": [
        ("nombre", "Nombre", "text", True, "Tu nombre"),
        ("apellido", "Apellido", "text", True, "Tu apellido"),
        ("email", "Correo electrónico", "email", True, "tu@email.com"),
        ("pais", "País", "text", True, "Tu país"),
        ("social", "Instagram o TikTok", "text", True, "@tusuario"),
    ],
    "punto_label": "¿En qué punto estás actualmente?",
    "punto_opciones": [
        "Todavía no he empezado a crear contenido.",
        "Ya estoy creando contenido.",
        "Quiero empezar como creadora UGC.",
        "Ya he trabajado con marcas.",
        "Quiero profesionalizar mi marca personal.",
        "Ya monetizo, pero quiero crecer.",
    ],
    "objetivo_label": "¿Qué te gustaría conseguir profesionalmente con tu contenido durante los próximos 12 meses?",
    "boton": "Enviar mi registro",
    "confirmacion": "Registro recibido. Ahora sí: bienvenida al radar del Campus. 💌",
    "nota": "El registro prioritario no garantiza la admisión al Campus, pero te "
            "mantendrás informada de todas las novedades.",

    # El carnet que acompaña al expediente.
    "carnet_rol": "Estudiante del mañana",
    "carnet_palabras": ["Crea", "Aprende", "Conecta", "Monetiza"],
    "sello": "Crea y Monetiza Campus · Admisiones · Un futuro creativo es posible ·",
}

# 18
ES_PARA_TI = {
    "eyebrow": "Antes de aplicar",
    "si_titulo": "El Campus puede ser para ti si…",
    "si": [
        "Te encanta crear y quieres empezar a verlo como una carrera.",
        "Ya creas contenido, pero sientes que necesitas estructura.",
        "Quieres desarrollar una marca personal profesional.",
        "Te interesa aprender UGC.",
        "Quieres trabajar con marcas.",
        "Necesitas mejorar la forma en la que presentas tu trabajo.",
        "Quieres aprender a monetizar tus habilidades.",
        "Buscas acompañamiento durante tu implementación.",
        "Quieres formar parte de una comunidad que también se toma esto en serio.",
        "Estás dispuesta a aprender, aplicar y recibir feedback.",
    ],
    "no_titulo": "Probablemente no es para ti si…",
    "no": [
        "Buscas resultados sin ejecutar.",
        "Quieres comprar otra formación para dejarla guardada.",
        "No estás dispuesta a aplicar lo aprendido.",
        "No quieres recibir feedback.",
        "Buscas una fórmula rápida que haga el trabajo por ti.",
    ],
    "cierre": "Nos importa mucho quién entra al Campus porque queremos construir una comunidad "
              "de creadoras que realmente quieran profesionalizarse.",
}

# 19
ADMISIONES = {
    "eyebrow": "Proceso de admisión",
    "titulo": "Tu entrada al Campus empieza aquí.",
    "intro": ["Antes de incorporarte queremos conocerte."],
    "queremos": [
        "Entender dónde estás.",
        "Qué quieres conseguir.",
        "Qué has intentado hasta ahora.",
        "Y confirmar que Crea y Monetiza Campus tiene sentido para el momento profesional "
        "en el que te encuentras.",
    ],
    "pasos": [
        ("Envía tu solicitud", "Completa tu información y cuéntanos brevemente sobre ti y tus objetivos."),
        ("Agenda tu entrevista", "Tendrás una conversación con nuestro equipo para conocer tu situación actual y hacia dónde quieres avanzar."),
        ("Evaluamos tu perfil", "Revisamos si el Campus encaja con tus objetivos y si podemos acompañarte en el punto en el que te encuentras."),
        ("Recibes los siguientes pasos", "Si tu perfil encaja con la formación y hay disponibilidad para incorporarte, durante la llamada conocerás todos los detalles de acceso."),
    ],
    # NO SE PUBLICA: retirada por decisión del cliente. El botón de admisión se
    # queda; lo que se va es la pregunta.
    "pregunta": "¿Quieres formar parte de la próxima generación de creadoras del Campus?",
    "boton": "Iniciar mi proceso de admisión",
    "nota": "Completar el proceso de admisión no garantiza automáticamente una plaza.",
}

# 20
# NO SE PUBLICA: la sección de cohorte se retiró por decisión del cliente. El
# registro prioritario, que era su desenlace, vive ahora por su cuenta.
COHORTE = {
    "eyebrow": "Admisiones",
    "titulo": "Cada generación empieza su recorrido en conjunto.",
    "datos": [
        ("Próxima cohorte", "[Fecha / mes]"),
        ("Estado de admisiones", "[Abiertas / Próximamente / Lista prioritaria]"),
        ("Registro prioritario", "Abierto"),
    ],
    "bajada": "Si quieres recibir las próximas fechas y novedades antes que el resto, puedes "
              "entrar al registro prioritario.",
    "boton": "Quiero recibir las próximas fechas",
}

# 21
FAQ = {
    "eyebrow": "Preguntas frecuentes",
    "titulo": "Secretaría académica",
    "preguntas": [
        ("¿Necesito experiencia previa?",
         ["No necesitas tener una carrera consolidada como creadora para aplicar.",
          "Dentro del proceso de admisión evaluaremos tu punto de partida para entender si el Campus encaja contigo."]),
        ("¿Necesito tener muchos seguidores?",
         ["No.",
          "La formación trabaja tus habilidades, posicionamiento, estrategia y profesionalización. "
          "Tu número de seguidores no determina por sí solo tu capacidad para construir oportunidades."]),
        ("¿Puedo formar parte si vivo fuera de España?",
         ["Sí.", "El Campus está diseñado para recibir creadoras desde diferentes países."]),
        ("¿El Campus es online?",
         ["La formación y el acompañamiento principal se desarrollan online para que puedas avanzar desde donde estés.",
          "Además, pueden existir experiencias y encuentros presenciales vinculados al Campus."]),
        ("¿Cuánto dura?",
         ["Tu recorrido principal dentro del Campus tiene una duración de 6 meses."]),
        ("¿Tengo que hacer entregables?",
         ["Sí.",
          "Queremos que apliques lo aprendido durante el proceso, por eso diferentes materias "
          "incluyen ejercicios, implementación y entregables."]),
        ("¿Tengo que presentar un proyecto final?",
         ["Sí.",
          "Al finalizar tu recorrido desarrollarás tu Proyecto de Graduación, donde integrarás "
          "diferentes elementos que has construido durante tu formación."]),
        ("¿Hay acompañamiento?",
         ["Sí.", "El acompañamiento y seguimiento forman parte de la experiencia del Campus."]),
        ("¿Recibiré un certificado?",
         ["Al completar los requisitos del recorrido recibirás tu título como "
          "Creadora Profesional."]),
        ("¿Qué es el Banco de Oportunidades?",
         ["Es un espacio de recursos relacionados con marcas, agencias, plataformas y "
          "oportunidades que pueden ayudarte durante tu etapa de profesionalización."]),
        ("¿Cómo puedo entrar?",
         ["El primer paso es completar tu proceso de admisión y agendar una entrevista con nuestro equipo."]),
        ("¿Dónde puedo conocer las condiciones de acceso?",
         ["Todas las condiciones de incorporación se explican durante la entrevista de admisión "
          "una vez que conocemos tu situación y confirmamos que el Campus puede encajar contigo."]),
        ("¿Qué pasa si las admisiones están cerradas?",
         ["Puedes entrar al registro prioritario para recibir directamente las próximas fechas, "
          "convocatorias y novedades."]),
    ],
}

# 22
CIERRE = {
    "eyebrow": "Tu próximo capítulo",
    "titulo": "Tu carrera como creadora no empieza cuando una marca te descubre. Empieza cuando decides tomártela en serio.",
    "parrafos": [
        "Puedes seguir aprendiendo cada parte por separado.",
        "O puedes construirlas dentro de una ruta.",
    ],
    # "Y con otras creadoras recorriendo el mismo camino" se retira del cierre
    # por decisión del cliente; su sitio lo ocupa el claim.
    "con": ["Con estructura.", "Con formación.", "Con implementación.", "Con acompañamiento."],
    "marca": "Crea y Monetiza Campus",
    "claim": "Formación integral para la nueva generación de creadoras.",
    "cta_1": "Iniciar mi proceso de admisión",
    "cta_2": "Entrar al registro prioritario",
    "firma": "Tu contenido puede ser el comienzo de algo mucho más grande.",

    # Los adornos del cierre. Es la última pantalla de la página: se le da
    # tratamiento de despedida y no de pie de página.
    "mano": "Misma pasión.\nNuevas posibilidades.",
    "carnet_rol": "Creadora en progreso",
    "carnet_palabras": ["Ideas", "Formación", "Acción", "Libertad"],
    "sello": "Admisiones abiertas · Creadoras de un futuro real ·",
}

# Datos del perfil que se arma solo en el hero de la propuesta 4.
# Es un perfil genérico de creadora, no una réplica de una red concreta: sin
# logos ni marcas de terceros, lo que además lo deja envejecer mejor.
PERFIL_ANIMADO = {
    "usuario": "@tu.marca",
    "nombre": "Creadora profesional",
    "bio": ["Marca personal · UGC · Contenido", "Formándome en Crea y Monetiza Campus"],
    "stats": [("128", "publicaciones"), ("24.7K", "seguidores"), ("312", "siguiendo")],
    "etiquetas": ["Portafolio", "Pitch", "Marcas", "Tarifas"],
    # nueve celdas de la retícula, cada una con su color de la paleta
    "celdas": 9,
    "pie": "Tu perfil no se arma solo. Aquí aprendes a construirlo.",

    # Recorte sin fondo de Pierina, que entra deslizándose desde la derecha
    # cuando el perfil ya terminó de montarse. El archivo va en assets/ con ese
    # nombre; construir.py comprueba si existe y, si no, deja un hueco marcado
    # en pantalla en vez de una imagen rota.
    "retrato": "pierina.webp",
    # Foto de Pierina para el marco de cuaderno de la sección de mentoras.
    "foto_pierina": "pierina-retrato.webp",
    "retrato_alt": "Pierina Alves, directora de Crea y Monetiza Campus",
}

# Las propuestas comparten contenido; solo cambian nombre, resumen y hoja de
# estilo. El orden de esta lista es el orden en que se presentan: la primera es
# la que se enseña primero. El nombre del archivo CSS y la clase del body salen
# de "clave", no de la posición, para que reordenar aquí no obligue a renombrar
# nada — que es justo lo que pasaba cuando iban como p1/p2/p3.
# La propuesta que se publica en la raíz del dominio. Las demás se siguen
# generando en /propuesta-N/ solo si BORRADORES está activo: sirven para
# comparar mientras se decide, y se apagan al publicar.
PUBLICADA = "perfil"
BORRADORES = False

PROPUESTAS = [
    {
        "clave": "perfil",
        "nombre": "Perfil",
        "resumen": "El hero monta en directo el perfil de una creadora — avatar, cifras que suben, "
                   "retícula que se llena — y Pierina entra a presentarlo. Es la promesa del Campus "
                   "contada en un segundo, sin explicarla.",
        "hero_extra": True,
    },
    {
        "clave": "prospecto",
        "nombre": "Prospecto",
        "resumen": "Continuidad directa con las piezas que ya existen: crema, stickers, Anton y "
                   "tarjetas redondeadas. La más reconocible para quien ya vio la carpeta o el pensum.",
    },
    {
        "clave": "expediente",
        "nombre": "Expediente",
        "resumen": "Registro institucional: retícula marcada, secciones numeradas como un catálogo "
                   "universitario, mucho blanco y el rosa reservado para acentuar. Transmite seriedad académica.",
    },
    {
        "clave": "nocturno",
        "nombre": "Nocturno",
        "resumen": "Vino a sangre completa, tipografía a gran escala y acentos en rosa y azul sobre "
                   "oscuro. El registro más premium y cinematográfico de los cuatro.",
    },
]
