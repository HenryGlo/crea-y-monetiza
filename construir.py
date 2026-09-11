#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las tres propuestas de landing desde contenido.py.

    python3 construir.py

Las tres comparten el mismo marcado semántico y el mismo texto: lo que cambia es
la hoja de estilo. Así una corrección de copy se hace en un solo sitio y llega a
las tres, que es justo lo que hace falta mientras se elige dirección.
"""

import datetime
import hashlib
import html
import json
import os
import re
import sys

import contenido as C

RAIZ = os.path.dirname(os.path.abspath(__file__))

# El número de propuestas se decía a mano en el índice y en la cinta de cada
# página. Al añadir la cuarta quedaron todos desfasados, así que se deriva.
_NUM = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}
NUM_TXT = _NUM.get(len(C.PROPUESTAS), str(len(C.PROPUESTAS)))

# Prefijo de las rutas a css/, js/ y assets/. Es "" para la página publicada,
# que vive en la raíz, y "../" para los borradores en /propuesta-N/. Va como
# global del módulo porque lo necesitan funciones sueltas —las pegatinas, las
# teclas— a las que no tiene sentido arrastrarles el parámetro.
RAIZ_WEB = "../"


def version(*rutas):
    """Huella del contenido, para romper la caché al desplegar.

    GitHub Pages sirve css/ y js/ con caché larga: sin versión en la URL, quien
    ya visitó el sitio ejecuta los archivos viejos junto al HTML nuevo. Eso deja
    la página a medias —una regla que falta pinta un SVG en negro, un script
    viejo no aplica un tratamiento— y es invisible desde una ventana nueva, que
    es justo donde uno lo prueba.

    Va por hash del contenido y no por fecha a mano: se actualiza sola cuando el
    archivo cambia y no cambia cuando no cambia."""
    h = hashlib.sha1()
    for r in rutas:
        with open(os.path.join(RAIZ, r), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def e(t):
    """Escapa texto para HTML. Todo el contenido pasa por aquí."""
    return html.escape(str(t), quote=False)


def slug(t):
    t = re.sub(r"[^a-z0-9]+", "-", t.lower().replace("ó", "o").replace("í", "i")
               .replace("á", "a").replace("é", "e").replace("ú", "u").replace("ñ", "n"))
    return t.strip("-")


# --------------------------------------------------------------------------
# Guardia de precios
# --------------------------------------------------------------------------

# El cliente fue explícito dos veces: la web pública no muestra ninguna cifra
# económica. Esto no es un adorno, es la regla que más fácil se rompe al editar
# copy más adelante, así que la build falla en vez de publicar el error.
PROHIBIDO = [
    r"€", r"\$", r"\bEUR\b", r"\bUSD\b",
    r"\bprecio\b", r"\bprecios\b", r"\bcoste\b", r"\bcosto\b",
    r"\bmatr[ií]cula\b", r"\bcuotas?\b", r"\bpago\b", r"\bpagos\b",
    r"\bfinanciaci[oó]n\b", r"\bplazos\b", r"\binversi[oó]n\b",
    r"\bdescuento\b", r"\bbeca\b", r"\btarifa\b",
]
# "Tu estructura de precios" y "Tarifas" son materia de estudio, no el precio del
# Campus: son las únicas menciones que el cliente sí pidió mantener.
# Sin el punto final: ahora las fichas lo recortan y la excepción dejaba de
# coincidir, con lo que la build abortaba por una frase que sí está permitida.
# "formalizas tu matrícula" habla del acto de matricularse, no de lo que
# cuesta: la regla del cliente es no publicar cifras, y aquí no hay ninguna.
EXCEPCIONES = ["Tu estructura de precios", "Tarifas", "formalizas tu matrícula"]


def revisar_precios(pagina, nombre):
    texto = re.sub(r"<[^>]+>", " ", pagina)
    for exc in EXCEPCIONES:
        texto = texto.replace(exc, " ")
    fallos = []
    for pat in PROHIBIDO:
        for m in re.finditer(pat, texto, re.I):
            ctx = texto[max(0, m.start() - 60):m.end() + 60].strip()
            fallos.append(f"  {m.group(0)!r} → …{' '.join(ctx.split())}…")
    if fallos:
        print(f"\nABORTADO — {nombre} contiene información económica:", file=sys.stderr)
        print("\n".join(fallos), file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------
# Piezas comunes
# --------------------------------------------------------------------------

def logo_sprite():
    with open(os.path.join(RAIZ, "assets", "logo-sprite.svg"), encoding="utf-8") as f:
        return f.read()


def nav(activo="inicio"):
    links = "".join(
        f'<a href="#{a}"{" class=\"active\"" if a == activo else ""}>{e(t)}</a>'
        for t, a in C.NAV
    )
    return f"""<nav class="nav"><div class="nav-in">
  <svg class="iso" aria-hidden="true"><use href="#iso"/></svg>
  <span class="brand">Campus</span>
  <div class="nav-links">{links}</div>
  <a class="nav-cta" href="#admisiones">{e(C.CTA_FIJO)}</a>
</div></nav>"""


def eyebrow(t):
    return f'<p class="eyebrow"><span class="dot"></span>{e(t)}</p>'


def lista(items, cls="lista"):
    lis = "".join(f"<li>{e(i)}</li>" for i in items)
    return f'<ul class="{cls}">{lis}</ul>'


def parrafos(ps, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{e(p)}</p>" for p in ps)


# Los óvalos y los círculos del juego de Nathaly no se usan: son parches
# bordados en blanco, pensados para llevar una palabra encima. Sueltos como
# adorno se leen como una mancha de color. Si alguna vez llevan texto, vuelven.
PLANTILLA_BIRRETE = '<span class="birrete" style="{estilo}"><svg viewBox="0 0 64 48" aria-hidden="true"><path class="b-tabla" d="M32 2 62 15 32 28 2 15z"/><path class="b-copa" d="M16 21v11c0 4 7 7 16 7s16-3 16-7V21l-16 7z"/><path class="b-borla" d="M56 19v13" stroke-width="2.6" fill="none" stroke-linecap="round"/><circle class="b-nudo" cx="56" cy="34" r="4"/></svg></span>'

def _aleatorio(semilla):
    """Generador determinista. Las posiciones tienen que ser siempre las mismas:
    con azar real, cada build movería las piezas y ninguna revisión de diseño
    sería comparable con la anterior."""
    x = semilla
    while True:
        x = (x * 1103515245 + 12345) % 2147483648
        yield x / 2147483648


def decoracion(sid):
    """El fondo de cada sección: dos piezas de la marca, enormes y casi
    imperceptibles, detrás del contenido.

    Van en todas las secciones y no en unas pocas, pero nunca con el mismo
    patrón: la semilla sale del propio nombre de la sección, así que cada una
    tiene su combinación de formas, colores, tamaños, posiciones y giros, y el
    fondo deja de ser un color plano sin repetirse nunca. Es determinista: la
    misma sección da siempre el mismo resultado y dos revisiones de diseño son
    comparables.

    A esta opacidad no compiten con la lectura; lo que hacen es que el color de
    la sección tenga algo debajo.

    Sustituye a la tabla de densidad que decidía qué secciones llevaban pieza y
    cuáles no: media página se había quedado sin fondo."""
    r = _aleatorio(sum(ord(c) * (i + 3) for i, c in enumerate(sid)) * 977)

    # Una estrella y un rayo: dos piezas de la misma familia en el mismo fondo
    # se leen como un error de repetición.
    familias = ["estrella", "rayo"]
    if next(r) > .5:
        familias.reverse()
    colores = ["rosa", "azul", "amar"]

    # Una a cada lado y en mitades distintas de la sección. Con el lado y la
    # altura al azar las dos caían a veces en el mismo sitio y la estrella se
    # montaba encima del rayo: son textura de fondo, y dos piezas superpuestas
    # se leen como una mancha.
    lados = ["left", "right"]
    if next(r) > .5:
        lados.reverse()

    piezas = []
    for i, familia in enumerate(familias):
        forma = f"{familia}-{colores[int(next(r) * len(colores))]}"
        alto = round(-8 + next(r) * 26) if i == 0 else round(48 + next(r) * 26)
        estilo = (f"{lados[i]}:{round(-8 + next(r) * 22)}%;"
                  f"top:{alto}%;"
                  f"width:clamp(200px,{round(26 + next(r) * 20)}vw,{round(360 + next(r) * 300)}px);"
                  # Sin giro: torcido, el rayo deja de leerse como un rayo y
                  # la estrella pierde su eje. Lo que cambia entre secciones es
                  # el sitio y el tamaño, no la inclinación.
                  f"--giro:0deg;"
                  f"animation-delay:{round(next(r) * -14, 1)}s;"
                  f"animation-duration:{round(14 + next(r) * 12)}s")
        piezas.append(f'<img class="deco deco-fondo" style="{estilo}" '
                      f'src="{RAIZ_WEB}assets/stickers/{forma}.webp" alt="" '
                      f'aria-hidden="true" loading="lazy" decoding="async">')
    return "".join(piezas)


# Tono de fondo de cada sección. A Pierina le gustan los colores y una sucesión
# de bloques sobre crema se leía plana; el cambio de tono también marca dónde
# empieza cada tema sin necesidad de un divisor.
TONOS = {
    "campus": "amar", "perfil": "rosa", "recorrido": "azul",
    "plan": "amar", "experiencia": "rosa", "mentoras": "azul",
    "mercado": "amar", "historias": "rosa", "graduacion": "azul",
    "admisiones": "amar", "faq": "azul", "carta": "rosa",
}


def seccion(sid, num, cuerpo, cls="", fuera=("", "")):
    """`fuera` son las piezas que van pegadas al borde de la sección y no dentro
    de la columna de texto: las ondas de un bloque a sangre, por ejemplo."""
    tono = TONOS.get(sid)
    if tono:
        cls = f"{cls} tono tono-{tono}".strip()
    return (f'<section id="{sid}" class="sec {cls}" data-num="{num}">'
            f'{decoracion(sid)}{fuera[0]}'
            f'<div class="wrap">{cuerpo}</div>{fuera[1]}</section>')


def cinta(items, veces=3):
    """Cinta rodante. No añade contenido nuevo: repite las materias que ya
    están en el hero. Se duplica la tira porque el bucle es un desplazamiento
    del -50%: con una sola copia se vería el corte al reiniciar."""
    tira = "".join(
        f'<span>{e(x)}</span><span class="cinta-sep" aria-hidden="true">✳</span>'
        for x in items)
    return (f'<div class="cinta" aria-hidden="true"><div class="cinta-pista">'
            f'{tira * veces}{tira * veces}</div></div>')


def boton(texto, href, tipo="pri", externo=False):
    flecha = "→" if tipo == "pri" else "↓"
    # Los enlaces que salen del sitio se abren aparte y con rel de seguridad.
    fuera = ' target="_blank" rel="noopener"' if externo else ""
    return (f'<a class="btn btn-{tipo}" href="{href}"{fuera}>{e(texto)} '
            f'<span aria-hidden="true">{flecha}</span></a>')


# --------------------------------------------------------------------------
# Secciones
# --------------------------------------------------------------------------

def hero_media(raiz="../"):
    """Lo que acompaña al titular del hero.

    El cortometraje vertical sustituye a la tarjeta de perfil que se armaba
    sola. Mientras el archivo no esté en assets/, va el marco vacío en su
    proporción con el texto que lo acompaña: así se ve ya la composición
    definitiva. Un <video> a una ruta inexistente deja un control roto justo en
    el hero, por eso el archivo se comprueba antes de emitirlo.

    Cuando aparezca con el nombre de contenido.py, el cambio ocurre solo, sin
    tocar código. perfil_animado() queda abajo sin usar, por si vuelve."""
    v = C.HERO_VIDEO
    texto = (f'<figcaption class="hero-video-txt">'
             f'<b>{e(v["titular"])}</b><span>{e(v["texto"])}</span></figcaption>')

    if not os.path.exists(os.path.join(RAIZ, "assets", v["archivo"])):
        return (f'<figure class="hero-media hero-video">'
                f'<div class="hero-hueco pendiente" data-nota="{e(v["nota_falta"])}"'
                f' role="img" aria-label="{e(v["alt"])}"></div>{texto}</figure>')

    poster = ""
    if os.path.exists(os.path.join(RAIZ, "assets", v["poster"])):
        poster = f' poster="{raiz}assets/{e(v["poster"])}"'

    # Silenciado y en bucle: es una pieza atmosférica, no algo que interrumpa a
    # quien llega. playsinline evita que iOS lo abra a pantalla completa solo.
    # Arranca mudo porque ningún navegador deja que un video empiece solo con
    # sonido: es una regla del navegador, no una decisión de diseño. El botón lo
    # enciende, que es el gesto de usuario que la regla pide.
    return f"""<figure class="hero-media hero-video">
  <video data-src="{raiz}assets/{e(v["archivo"])}"{poster}
         muted loop playsinline preload="none"
         aria-label="{e(v["alt"])}"></video>
  <button class="sonido" type="button" aria-pressed="false"
          data-on="{e(v["sonido_on"])}" data-off="{e(v["sonido_off"])}"
          aria-label="{e(v["sonido_on"])}">
    <span class="sonido-icono" aria-hidden="true"></span>
  </button>
  {texto}
</figure>"""


def perfil_animado(raiz="../"):
    """Perfil de creadora que se monta solo en el hero de la propuesta 4.

    El montaje es CSS puro con retardos escalonados: no depende de JS, así que
    ocurre igual si el script tarda o falla. Va marcado aria-hidden porque es
    una ilustración — lo que dice ya está en el titular y en el pie."""
    f = C.PERFIL_ANIMADO
    stats = "".join(
        f'<div class="pf-stat" style="--i:{i}"><b>{e(n)}</b><span>{e(t)}</span></div>'
        for i, (n, t) in enumerate(f["stats"]))
    etiquetas = "".join(
        f'<span class="pf-tag" style="--i:{i}">{e(x)}</span>'
        for i, x in enumerate(f["etiquetas"]))
    celdas = "".join(f'<i style="--i:{i}"></i>' for i in range(f["celdas"]))
    bio = "".join(f'<p class="pf-bio" style="--i:{i}">{e(x)}</p>'
                  for i, x in enumerate(f["bio"]))
    # La imagen solo se emite si el archivo está de verdad: un <img> a una ruta
    # inexistente deja el icono de imagen rota justo en el hero.
    # WebP pesa 62 KB contra 642 del PNG con el mismo recorte y transparencia.
    # Lo soporta todo navegador desde 2020, así que no hace falta alternativa.
    ruta = os.path.join(RAIZ, "assets", f["retrato"])
    if os.path.exists(ruta):
        persona = (f'<img class="pf-persona" src="{raiz}assets/{e(f["retrato"])}" '
                   f'alt="{e(f["retrato_alt"])}" loading="eager" decoding="async">')
    else:
        persona = ('<div class="pf-persona pf-persona-hueco pendiente" '
                   'role="img" aria-label="Falta el recorte de Pierina Alves">'
                   '<span>Recorte sin fondo<br>de Pierina</span></div>')

    return f"""<div class="pf">
  <div class="pf-marco" aria-hidden="true">
    <div class="pf-top">
      <span class="pf-avatar"></span>
      <div class="pf-id">
        <p class="pf-user">{e(f["usuario"])}<span class="pf-check">✓</span></p>
        <p class="pf-nombre">{e(f["nombre"])}</p>
      </div>
    </div>
    <div class="pf-stats">{stats}</div>
    <div class="pf-bios">{bio}</div>
    <div class="pf-tags">{etiquetas}</div>
    <div class="pf-grid">{celdas}</div>
  </div>
  <p class="pf-pie" aria-hidden="true">{e(f["pie"])}</p>
</div>"""


def stickers(piezas):
    """Pegatinas del hero. Son PNG con volumen y no siluetas planas: el brillo y
    la sombra propios de cada pieza son justo lo que las hace parecer pegadas
    encima de la página en vez de dibujadas dentro."""
    return "".join(
        f'<img class="sticker {cls}" src="{RAIZ_WEB}assets/stickers/{n}.webp" alt="" '
        f'aria-hidden="true" loading="lazy" decoding="async">'
        for n, cls in piezas)


def s_hero(extra=""):
    h = C.HERO
    cifras = "".join(
        f'<div class="cifra"><b>{e(n)}</b><span>{e(t)}</span></div>'
        for n, t in h["cifras"])
    materias = "".join(f"<li>{e(m)}</li>" for m in h["materias"])
    return f"""<header id="inicio" class="hero">
  {stickers([("estrella-azul","s1"),("rayo-amar","s2"),("rayo-rosa","s3"),("estrella-rosa","s4")])}
  <div class="wrap">
    <svg class="logo" viewBox="0 0 863.98 253.56" role="img" aria-label="Crea y Monetiza Campus"><use href="#logo-full"/></svg>
    <p class="pill">{e(h["eyebrow"])}</p>
    <h1>{e(h["titulo"])}</h1>
    {extra}
    <p class="entrada">{e(h["entrada"])}</p>
    <ul class="materias-hero">{materias}</ul>
    <p class="remate">{e(h["remate"])}</p>
    <div class="ctas">
      {boton(h["cta_1"], "#admisiones", "pri")}
      {boton(h["cta_2"], "#campus", "sec")}
    </div>
    <div class="cifras">{cifras}</div>
  </div>
</header>"""


def equipo_hero():
    """NO SE USA: el bloque de equipo sale del hero por decisión del cliente.
    La función y su copy se quedan; vuelve llamándola de nuevo en s_hero().

    Las tres mentoras, anunciadas ya en el hero. Es el activo de confianza
    principal —los dos competidores directos del nicho ponen a la fundadora
    arriba del todo— y estaba enterrado en la sección once."""
    q = C.EQUIPO_HERO
    # Sin inicial dentro. Pierina y Paola comparten letra y salían dos círculos
    # con P, que se lee como un error antes que como dos personas. El nombre de
    # cada una ya está al lado; el círculo solo aporta el "son tres". Cuando
    # lleguen los retratos, entran aquí.
    caras = "".join(
        f'<span class="cara" title="{e(n)}"></span>' for n in q["personas"])
    nombres = " · ".join(q["personas"])
    return (f'<a class="equipo" href="#mentoras">'
            f'<span class="caras">{caras}</span>'
            f'<span class="equipo-txt"><b>{e(q["etiqueta"])}</b>'
            f'<i>{e(nombres)}</i></span></a>')


def forma_logo(ruta):
    """Ancho o cuadrado, según la proporción real del archivo.

    Un icono cuadrado y un logotipo con nombre puestos a la misma altura no
    pesan lo mismo: el ancho ocupa cinco veces más superficie y el cuadrado se
    ve diminuto al lado. La clase la decide el archivo, no el ojo, y así entra
    bien cualquier logotipo que se añada después."""
    try:
        if ruta.endswith(".svg"):
            cab = open(ruta, encoding="utf-8", errors="replace").read(2000)
            vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', cab)
            if not vb:
                return "ancho"
            an, al = float(vb.group(1)), float(vb.group(2))
        else:
            from PIL import Image
            with Image.open(ruta) as im:
                an, al = im.size
        if not al:
            return "ancho"
    except Exception:
        # Un logotipo mal medido se enseña igual, solo que al tamaño de siempre.
        return "ancho"

    razon = an / al
    if razon < 1.5:
        return "cuadrado"
    if razon < 2.6:
        return "medio"
    return "ancho"


def s_carta():
    """La carta llega cerrada dentro de su sobre y se abre al pulsar.

    El HTML se emite abierto y es campus.js quien lo cierra al arrancar: si el
    script falla o tarda, la carta se lee igual. Un desplegable que empieza
    cerrado en el HTML esconde el texto de quien no tiene JS.

    Debajo va quién firma: la trayectoria de Pierina. La carta pedía creer en
    ella, y hasta ahora la página no daba ni un dato sobre quién es."""
    c = C.CARTA
    t = c["trayectoria"]
    # El video sale de la carta por decisión del cliente. Los datos siguen en
    # contenido.py y la fachada que no cargaba nada de YouTube hasta pulsarla
    # está en el historial: vuelve poniéndola de nuevo aquí y en la hoja.
    # La cita sobre un papel amarillo, no como texto suelto: es una nota suya
    # dentro de la página, y así se lee.
    cita = (f'<blockquote class="cita nota"><span>{e(c["cita"])}</span>'
            f'<cite>— {e(c["cita_autora"])}</cite></blockquote>')
    # El recorte de Pierina acompaña a su propia carta. Estaba en el hero, donde
    # competía con la tarjeta del perfil; aquí es ella hablando en primera
    # persona y la foto es lo que le pone cara a ese texto.
    fp = C.PERFIL_ANIMADO
    retrato = ""
    if os.path.exists(os.path.join(RAIZ, "assets", fp["retrato"])):
        retrato = (f'<img class="carta-foto" src="{RAIZ_WEB}assets/{e(fp["retrato"])}" '
                   f'alt="{e(fp["retrato_alt"])}" loading="lazy" decoding="async">')

    # Las cifras entre corchetes son las que Pierina aún tiene que darnos: se
    # marcan en pantalla para que nadie las confunda con datos reales.
    cifras = "".join(
        f'<div class="cifra{" pendiente-min" if n.startswith("[") else ""}">'
        f'<b>{e(n)}</b><span>{e(txt)}</span></div>'
        for n, txt in t["cifras"])

    def logo_marca(nombre):
        """El logotipo de la marca si está en assets/marcas/, y su nombre escrito
        si no. Mismo criterio que el cortometraje y los retratos: el archivo
        manda, y hasta que llega la página no se rompe ni miente.

        El nombre del archivo sale del de la marca en minúsculas y sin signos,
        así que basta con dejarlo ahí para que entre."""
        slug = re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")
        for ext in ("svg", "webp", "png"):
            ruta = os.path.join(RAIZ, "assets", "marcas", f"{slug}.{ext}")
            if os.path.exists(ruta):
                return (f'<img src="{RAIZ_WEB}assets/marcas/{slug}.{ext}" '
                        f'alt="{e(nombre)}" data-forma="{forma_logo(ruta)}" '
                        f'loading="lazy" decoding="async">')
        return f"<span>{e(nombre)}</span>"

    if t["marcas"]:
        marcas = "".join(f"<li>{logo_marca(m)}</li>" for m in t["marcas"])
        marcas_cls = "marcas"
    else:
        # Seis huecos del tamaño de un logotipo: se ve la forma que tendrá la
        # fila sin afirmar ninguna marca que no esté confirmada.
        marcas = "".join('<li class="marca-hueca"></li>' for _ in range(6))
        marcas_cls = "marcas pendiente"
    # La etiqueta de lo que falta solo se emite cuando falta algo.
    falta = ("" if t["marcas"]
             else f' data-nota="{e(t["marcas_falta"])}"')

    return seccion("carta", "02", f"""
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>

    <div class="sobre">
      <span class="sobre-solapa" aria-hidden="true"></span>
      <svg class="sobre-sello" viewBox="0 0 265.42 268.17" aria-hidden="true"><use href="#iso"/></svg>

      <button class="sobre-btn" type="button" aria-expanded="true" aria-controls="carta-hoja">
        <span class="sobre-de"><b>{e(c["sobre_de"])}</b><i>{e(c["cita_autora"])}</i></span>
        <span class="sobre-para">{e(c["sobre_para"])}</span>
        <span class="sobre-cta" data-abrir="{e(c["sobre_abrir"])}"
              data-cerrar="{e(c["sobre_cerrar"])}">{e(c["sobre_cerrar"])}</span>
      </button>

      <div class="carta-hoja" id="carta-hoja">
        <div class="hoja-interior">
          <div class="carta-con-foto">
            <div class="carta-cuerpo">{parrafos(c["parrafos"])}</div>
            {retrato}
          </div>
          {cita}
        </div>
      </div>
    </div>

    <div class="trayectoria">
      <div class="cifras tray-cifras">{cifras}</div>
      <p class="tray-marcas-t">{e(t["marcas_t"])}</p>
      <ul class="{marcas_cls}"{falta}>{marcas}</ul>
    </div>

    <div class="ctas">{boton(c["cta"], "#campus", "sec")}</div>""", "carta")


def s_campus():
    c = C.CAMPUS
    return seccion("campus", "03", f"""
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    {parrafos(c["intro"], "lead")}
    {lista(c["necesidades"], "lista necesidades")}
    {parrafos(c["cierre"], "cierre")}
    {comparacion()}""", "campus")


def comparacion():
    """Lo habitual frente al Campus. Es el único bloque cuya copy no viene del
    guion original: la escribió Nathaly y se incorpora a petición del cliente."""
    c = C.COMPARACION
    izq = "".join(f"<li>{e(x)}</li>" for x in c["izq"])
    der = "".join(f"<li>{e(x)}</li>" for x in c["der"])
    return f"""<div class="comparar">
      <article class="comp comp-antes">
        <p class="kicker">{e(c["izq_kicker"])}</p>
        <h3>{e(c["izq_titulo"])}</h3>
        <ul>{izq}</ul>
      </article>
      <article class="comp comp-campus">
        <p class="kicker">{e(c["der_kicker"])}</p>
        <h3>{e(c["der_titulo"])}</h3>
        <ul>{der}</ul>
      </article>
    </div>"""


def s_perfil():
    p = C.PERFIL
    # Cada eje sobre una tecla. Los cuatro colores rotan; el icono es un signo
    # simple porque a este tamaño un pictograma detallado se pierde.
    teclas = ["vino", "rosa", "azul", "amar"]
    # Estrella y rayo alternos, que son las dos formas del juego de la marca.
    signos = ["★", "⚡"]
    ejes = "".join(
        f'<article class="card eje">'
        f'<span class="tecla" aria-hidden="true">'
        f'<img src="{RAIZ_WEB}assets/stickers/tecla-{teclas[(i-1) % 4]}.webp" alt="" loading="lazy" decoding="async">'
        f'<i>{signos[(i-1) % len(signos)]}</i></span>'
        f'<h3>{e(t)}</h3><p>{e(d)}</p></article>'
        for i, (t, d) in enumerate(p["ejes"], 1))
    return seccion("perfil", "04", f"""
    {eyebrow(p["eyebrow"])}
    <h2>{e(p["titulo"])}</h2>
    <div class="grid grid-3">{ejes}</div>""", "perfil") + f"""
<div class="franja">
  <svg class="onda onda-arriba" viewBox="0 0 1200 90" preserveAspectRatio="none" aria-hidden="true" fill="#FBF7F4">
    <path d="M0 90V44c110-30 210 14 320 22s205-36 315-38 190 42 300 40 155-32 265-40v62z"/>
  </svg>
  <div class="wrap">
    <p>{e(p["cierre"])}</p>
    <img class="franja-sticker" src="{RAIZ_WEB}assets/stickers/rayo-azul.webp" alt="" aria-hidden="true" loading="lazy">
  </div>
  <svg class="onda onda-abajo" viewBox="0 0 1200 90" preserveAspectRatio="none" aria-hidden="true" fill="#FBF7F4">
    <path d="M0 90V44c110-30 210 14 320 22s205-36 315-38 190 42 300 40 155-32 265-40v62z"/>
  </svg>
</div>"""


def s_recorrido():
    r = C.RECORRIDO
    etapas = ""
    for et in r["etapas"]:
        # Sin desglose. El "durante esta etapa" con sus siete pasos y el
        # "trabajarás sobre" con sus diez convertían cada tarjeta en una lista
        # larga; la etapa se entiende con lo que la describe.
        intro = "".join(f"<p>{e(x)}</p>" for x in et["intro"].split("\n"))
        etapas += f"""<article class="card etapa" data-x="{e(et["n"].split()[-1])}">
      <p class="etapa-n">{e(et["n"])}</p>
      <p class="etapa-meses">{e(et["meses"])}</p>
      <h3>{e(et["titulo"])}</h3>
      {intro}
      <p class="cierre">{e(et["cierre"])}</p>
    </article>"""
    return seccion("recorrido", "05", f"""
    {eyebrow(r["eyebrow"])}
    <h2>{e(r["titulo"])}</h2>
    {parrafos(r["bajada"], "lead")}
    <div class="grid grid-2">{etapas}</div>""", "recorrido")


def s_plan():
    """El plan no se publica materia por materia: es contenido exclusivo de las
    alumnas matriculadas. La página cuenta cómo está estructurado y lleva a
    agendar la llamada de admisión, que es donde se ve completo.

    Con él se retiraron la ruta de nodos y las materias desplegables: eran la
    forma de leer un contenido que ya no está."""
    p = C.PLAN
    bloques = "".join(
        f'<article class="card mini"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
        for t, d in p["bloques"])
    return seccion("plan", "06", f"""
    {eyebrow(p["eyebrow"])}
    <h2>{e(p["titulo"])}</h2>
    <p class="lead">{e(p["bajada"])}</p>
    <p class="plan-exclusivo">{e(p["exclusivo"])}</p>
    <div class="grid grid-4">{bloques}</div>
    <p class="lead-min plan-invita">{e(p["cta_linea"])}</p>
    <div class="ctas">{boton(p["cta_boton"], p["cta_enlace"], "pri", externo=True)}</div>
    {bloque_evaluacion()}""", "plan")


def bloque_evaluacion():
    """Cómo se evalúa. Era la sección 07 y ahora cierra el plan de estudios:
    las dos responden "cómo aprendo", y separadas obligaban a leer dos veces lo
    mismo con otro titular."""
    v = C.EVALUACION
    # Los seis no son una lista de métodos sueltos: son el orden en que se
    # evalúa a lo largo del recorrido, de los primeros ejercicios al proyecto
    # final. En una retícula de fichas iguales ese orden no se leía; en línea
    # de tiempo, con el raíl trazándose al entrar en pantalla, se lee solo.
    items = "".join(
        f'<li class="hito" style="--i:{i}">'
        f'<span class="hito-nodo" aria-hidden="true">{i:02d}</span>'
        f'<div class="hito-caja"><b>{e(t)}</b><span>{e(d)}</span></div></li>'
        for i, (t, d) in enumerate(v["items"], 1))
    # Plegado: es información que se consulta, no que se lee de corrido, y
    # abierta ocupaba 600px al final del plan.
    # Deja de ir plegado. "No queremos que termines sabiendo más, queremos que
    # termines sabiendo hacer más" es de las frases que mejor separan al Campus
    # de un curso grabado, y escondida tras un acordeón no la leía nadie.
    #
    # Va en azul claro y no en vino: la Tesis, que viene justo después, ya es
    # vino a sangre, y dos bloques oscuros seguidos se leen como uno solo.
    return f"""</div></section>
<section class="sec evaluacion-franja tono tono-azul" data-num="07"><div class="wrap">
      <p class="eyebrow"><span class="dot"></span>{e(v["eyebrow"])}</p>
      <h2 class="ev-titulo">{e(v["titulo"])}</h2>
      {parrafos(v["intro"], "lead")}
      <ol class="linea">{items}</ol>
      <p class="cierre destacado"><span class="lapiz">{e(v["cierre"])}</span></p>"""


def s_evaluacion():
    v = C.EVALUACION
    items = "".join(f'<article class="card mini"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
                    for t, d in v["items"])
    return seccion("evaluacion", "07", f"""
    {eyebrow(v["eyebrow"])}
    <h2>{e(v["titulo"])}</h2>
    {parrafos(v["intro"], "lead")}
    <div class="grid grid-3">{items}</div>
    <p class="cierre">{e(v["cierre"])}</p>""", "evaluacion")


ONDA_TRAZO = ("M0 90V44c110-30 210 14 320 22s205-36 315-38 190 42 300 40 "
              "155-32 265-40v62z")


def ondas():
    """Las dos ondas que muerden un bloque a sangre por arriba y por abajo.

    Van del color del fondo de la página, así que recortan el bloque en vez de
    dibujarse encima. Miden el doble de ancho y se desplazan un 50%: como el
    trazo se repite, el bucle empalma sin salto."""
    def svg(donde):
        return (f'<svg class="onda onda-{donde}" viewBox="0 0 1200 90" '
                f'preserveAspectRatio="none" aria-hidden="true">'
                f'<path d="{ONDA_TRAZO}"/></svg>')
    return svg("arriba"), svg("abajo")


def s_tesis():
    """El momento fuerte de la página. La Tesis Creativa es lo que de verdad
    separa al Campus de "otro curso más", así que se le da tratamiento de
    portada: sello giratorio, el nombre a tamaño de cartel con una copia
    fantasma detrás, y los ocho elementos que integra dispuestos como piezas que
    se juntan — que es literalmente lo que el proyecto hace."""
    t = C.TESIS

    # Sello de graduación: círculo de texto girando alrededor de una estrella.
    sello = f"""<div class="sello" aria-hidden="true">
      <svg viewBox="0 0 200 200">
        <defs><path id="aro" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs>
        <text class="sello-txt"><textPath href="#aro" startOffset="0%">
          {e(t["eyebrow"])} · {e(t["nombre"])} · {e(t["eyebrow"])} · {e(t["nombre"])} ·
        </textPath></text>
      </svg>
      <img class="sello-estrella" src="{RAIZ_WEB}assets/stickers/estrella-amar.webp" alt="">
    </div>"""

    # Las ocho partes que el proyecto integra, como piezas numeradas que se
    # juntan. En lista corrida eran ocho frases sueltas y no se veía el gesto.
    piezas = "".join(
        f'<li style="--n:{i}"><span>{i:02d}</span>{e(x.rstrip("."))}</li>'
        for i, x in enumerate(t["integra"], 1))

    return seccion("tesis", "08", f"""
    {sello}
    {eyebrow(t["eyebrow"])}
    <h2>{e(t["titulo"])}</h2>
    <p class="lead-min">{e(t["lo_llamamos"])}</p>
    <p class="tesis-nombre" data-texto="{e(t["nombre"])}">{e(t["nombre"])}</p>
    <div class="tesis-cuerpo">{parrafos(t["intro"])}</div>
    <p class="lead-min tesis-lead">{e(t["lead"])}</p>
    <ul class="tesis-piezas">{piezas}</ul>
    {parrafos(t["cierre"], "cierre")}""", "tesis", ondas())


def s_digital():
    d = C.DIGITAL
    piezas = "".join(f"<li>{e(x)}</li>" for x in d["piezas"])
    bloques = ""
    for b in d["bloques"]:
        extra = lista(b["lista"], "lista") if b["lista"] else ""
        bloques += f"""<article class="card bloque">
      <p class="kicker">{e(b["kicker"])}</p>
      <h3>{e(b["titulo"])}</h3>
      {parrafos(b["texto"])}
      {extra}
      <div class="ph" role="img" aria-label="{e(b["placeholder"])}"><span>{e(b["placeholder"])}</span></div>
    </article>"""
    return seccion("experiencia", "09", f"""
    {eyebrow(d["eyebrow"])}
    <h2>{e(d["titulo"])}</h2>
    <ul class="lista piezas">{piezas}</ul>
    <p class="remate">{e(d["remate"])}</p>
    <div class="grid grid-3">{bloques}</div>""", "digital")


def s_vivo():
    v = C.VIVO
    items = "".join(f'<article class="card mini"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
                    for t, d in v["items"])
    return seccion("vivo", "10", f"""
    {eyebrow(v["eyebrow"])}
    <h2>{e(v["titulo"])}</h2>
    <p class="lead">{e(v["bajada"])}</p>
    <div class="grid grid-4">{items}</div>""", "vivo")


def s_facultad():
    f = C.FACULTAD
    foto = C.PERFIL_ANIMADO.get("foto_pierina")
    tiene_foto = foto and os.path.exists(os.path.join(RAIZ, "assets", foto))

    def retrato(pers):
        """El retrato de Pierina va dentro de un cuaderno de espiral con su
        etiqueta: es lo que convierte una foto de equipo en una pieza de campus.
        Las demás mantienen el marcador hasta que lleguen sus fotos."""
        if pers["nombre"].startswith("Pierina") and tiene_foto:
            return (f'<div class="cuaderno">'
                    f'<img class="cuaderno-foto" src="{RAIZ_WEB}assets/{e(foto)}" '
                    f'alt="Retrato de {e(pers["nombre"])}" loading="lazy" decoding="async">'
                    f'<span class="etiqueta"><b>{e(pers["nombre"])}</b>'
                    f'<i>{e(pers["rol"].split("·")[0].strip())}</i></span></div>')
        return (f'<div class="retrato pendiente" role="img" '
                f'aria-label="Falta el retrato de {e(pers["nombre"])}">'
                f'<span>{e(pers["nombre"].split()[0])}</span></div>')

    ps = "".join(f"""<article class="card persona">
      {retrato(p)}
      <h3>{e(p["nombre"])}</h3>
      <p class="rol">{e(p["rol"])}</p>
      {parrafos(p["bio"])}
    </article>""" for p in f["personas"])
    return seccion("mentoras", "11", f"""
    {eyebrow(f["eyebrow"])}
    {parrafos(f["intro"], "lead")}
    <div class="grid grid-3">{ps}</div>
    <p class="cierre">{e(f["cierre"])}</p>""", "facultad")


def s_mercado():
    m = C.MERCADO
    return seccion("mercado", "12", f"""
    {eyebrow(m["eyebrow"])}
    <h2>{e(m["titulo"])}</h2>
    {parrafos(m["intro"], "lead")}
    <p class="lead-min">{e(m["lead"])}</p>
    {lista(m["items"], "lista dos-col")}""", "mercado")


def s_oportunidades():
    o = C.OPORTUNIDADES
    return seccion("oportunidades", "13", f"""
    {eyebrow(o["eyebrow"])}
    <h2>{e(o["titulo"])}</h2>
    <p class="lead">{e(o["intro"])}</p>
    {lista(o["items"], "lista chips")}
    {parrafos(o["cierre"], "cierre")}""", "oportunidades")


def s_experiencia():
    x = C.EXPERIENCIA
    items = "".join(f'<article class="card mini"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
                    for t, d in x["items"])
    return seccion("incluye", "14", f"""
    {eyebrow(x["eyebrow"])}
    <h2>{e(x["titulo"])}</h2>
    <div class="grid grid-3">{items}</div>""", "incluye")


def s_historias():
    h = C.HISTORIAS
    casos = ""
    for c in h["casos"]:
        campos = "".join(f'<div class="campo"><p class="kicker">{e(k)}</p><p>{e(v)}</p></div>'
                         for k, v in c["campos"])
        casos += f"""<article class="card caso pendiente">
      <p class="caso-n">{e(c["n"])}</p>
      <h3>{e(c["nombre"])}</h3>
      <p class="lugar">{e(c["lugar"])}</p>
      {campos}
      <div class="ph" role="img" aria-label="{e(c["media"])}"><span>{e(c["media"])}</span></div>
    </article>"""
    return seccion("historias", "15", f"""
    {eyebrow(h["eyebrow"])}
    <h2>{e(h["titulo"])}</h2>
    <p class="lead">{e(h["bajada"])}</p>
    <div class="grid grid-3">{casos}</div>""", "historias")


def birretes(n=6):
    """Los birretes que se lanzan al aire al llegar a la graduación.

    Van en SVG y no como imagen: hay que teñirlos con los colores de marca y
    girarlos, y a 40px una foto no aguanta el giro.

    Cada uno lleva su propia deriva, giro, altura y retardo, así que el
    lanzamiento se ve desordenado —como uno de verdad— con una sola animación."""
    piezas = []
    r = _aleatorio(20260909)
    for _ in range(n):
        deriva = round(-150 + next(r) * 300)
        giro = round(300 + next(r) * 420) * (1 if next(r) > .5 else -1)
        alto = round(330 + next(r) * 210)
        retardo = round(next(r) * 2.5, 2)
        salida = round(8 + next(r) * 84)
        estilo = (f"left:{salida}%;--deriva:{deriva}px;--giro-b:{giro}deg;"
                  f"--alto:{alto}px;animation-delay:{retardo}s")
        piezas.append(PLANTILLA_BIRRETE.format(estilo=estilo))
    return '<div class="birretes" aria-hidden="true">' + "".join(piezas) + "</div>"


def s_graduacion():
    g = C.GRADUACION
    bs = ""
    for t, ps, fecha in g["bloques"]:
        f = f'<p class="fecha">{e(fecha)}</p>' if fecha else ""
        bs += (f'<article class="card mini"><h3>{e(t)}</h3>{parrafos(ps)}{f}</article>')
    return seccion("graduacion", "16", f"""
    {birretes()}
    {eyebrow(g["eyebrow"])}
    <h2>{e(g["titulo"])}</h2>
    {parrafos(g["intro"], "lead")}
    <div class="grid grid-3">{bs}</div>
    """, "graduacion")


def s_registro():
    r = C.REGISTRO
    campos = "".join(f"""<label class="campo-f">
      <span>{e(lab)}</span>
      <input type="{tipo}" name="{n}" {"required" if req else ""} autocomplete="{'email' if tipo == 'email' else 'on'}">
    </label>""" for n, lab, tipo, req in r["campos"])
    opciones = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in r["punto_opciones"])
    return seccion("registro", "17", f"""
    {eyebrow(r["eyebrow"])}
    <h2>{e(r["titulo"])}</h2>
    {lista(r["items"], "lista chips")}
    <p class="lead">{e(r["bajada"])}</p>
    <form class="form" id="form-registro" novalidate>
      <p class="form-t">{e(r["form_titulo"])}</p>
      <div class="campos">{campos}</div>
      <label class="campo-f">
        <span>{e(r["punto_label"])}</span>
        <select name="punto" required><option value="">Selecciona una opción</option>{opciones}</select>
      </label>
      <label class="campo-f">
        <span>{e(r["objetivo_label"])}</span>
        <textarea name="objetivo" rows="4"></textarea>
      </label>
      <button class="btn btn-pri" type="submit">{e(r["boton"])} <span aria-hidden="true">→</span></button>
      <p class="form-msg" role="status" data-ok="{e(r["confirmacion"])}"></p>
    </form>""", "registro")


def s_es_para_ti():
    p = C.ES_PARA_TI
    return seccion("para-ti", "18", f"""
    {eyebrow(p["eyebrow"])}
    <div class="grid grid-2">
      <article class="card si"><h3>{e(p["si_titulo"])}</h3>{lista(p["si"], "lista check")}</article>
      <article class="card no"><h3>{e(p["no_titulo"])}</h3>{lista(p["no"], "lista cruz")}</article>
    </div>
    <p class="cierre">{e(p["cierre"])}</p>""", "para-ti")


def s_admisiones():
    a = C.ADMISIONES
    pasos = "".join(
        f'<li class="paso"><span class="paso-n">{i:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>'
        for i, (t, d) in enumerate(a["pasos"], 1))
    return seccion("admisiones", "19", f"""
    {eyebrow(a["eyebrow"])}
    <h2>{e(a["titulo"])}</h2>
    {parrafos(a["intro"], "lead")}
    {lista(a["queremos"], "lista")}
    <ol class="pasos-grid">{pasos}</ol>
    <p class="pregunta">{e(a["pregunta"])}</p>
    <div class="ctas">{boton(a["boton"], "#registro", "pri")}</div>
    <p class="nota">{e(a["nota"])}</p>""", "admisiones")


def s_cohorte():
    c = C.COHORTE
    datos = "".join(f'<div class="dato"><span>{e(k)}</span><b>{e(v)}</b></div>'
                    for k, v in c["datos"])
    return seccion("cohorte", "20", f"""
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    <div class="datos">{datos}</div>
    <p class="lead">{e(c["bajada"])}</p>
    <div class="ctas">{boton(c["boton"], "#registro", "pri")}</div>""", "cohorte")


def s_faq():
    f = C.FAQ
    items = "".join(f"""<details class="faq-item">
      <summary>{e(q)}</summary>
      <div class="faq-cuerpo">{parrafos(rs)}</div>
    </details>""" for q, rs in f["preguntas"])
    return seccion("faq", "21", f"""
    {eyebrow(f["eyebrow"])}
    <h2>{e(f["titulo"])}</h2>
    <div class="faq-lista">{items}</div>""", "faq")


def s_cierre():
    """La última pantalla, como una portada.

    El texto es el que aprobó el cliente y no se toca; lo que cambia es la
    composición. Va centrada sobre el vino, con el arco y el isotipo arriba, el
    titular a tamaño de cartel, una sola llamada en rosa y el registro debajo
    como enlace. A los lados, el carnet colgando y el sello.

    Las cuatro formas de recorrerlo bajan al pie en fila, cada una con su ficha
    de color: son el resumen de lo que hay dentro, no un argumento más que leer
    antes de decidir. Y el remate cierra la página entre dos filetes.

    Antes fue una columna centrada donde todo pesaba igual, y después dos
    paneles: el de papel se quedaba vacío al lado del vino."""
    c = C.CIERRE

    # Las cuatro van al pie con su ficha. La línea entre filetes que cierra la
    # página la ocupa el claim: antes llevaba "y con otras creadoras recorriendo
    # el mismo camino", que sale por decisión del cliente, y el claim estaba
    # repetido justo debajo del logo.
    piezas = ["estrella-amar", "rayo-azul", "estrella-rosa", "rayo-amar"]
    formas, remate = c["con"], c["claim"]
    # "Con estructura. Con formación. Con implementación. Con acompañamiento."
    # Cuatro etiquetas seguidas empezando por la misma palabra se leen como una
    # repetición, no como cuatro cosas distintas. El "Con" baja de tamaño y el
    # sustantivo se queda con el peso: no se toca una palabra del texto, pero lo
    # que se lee de un vistazo son las cuatro cosas.
    def partir(frase):
        cabeza, _, resto = frase.rstrip(".").partition(" ")
        return cabeza, resto or cabeza

    marcas = ""
    for i, x in enumerate(formas, 1):
        con, que = partir(x)
        marcas += (f'<li style="--n:{i}"><span class="con-punto">'
                   f'<img src="{RAIZ_WEB}assets/stickers/{piezas[i - 1]}.webp" alt="" '
                   f'aria-hidden="true" loading="lazy" decoding="async"></span>'
                   f'<b><i>{e(con)}</i>{e(que)}</b></li>')

    mano = "".join(f"<span>{e(x)}</span>" for x in c["mano"].split("\n"))

    # El arco que abre la composición, con el isotipo en su vértice.
    arco = f"""<div class="arco" aria-hidden="true">
      <svg viewBox="0 0 600 90" preserveAspectRatio="none">
        <path d="M2 88C90 26 240 4 300 4s210 22 298 84" fill="none"
              stroke="currentColor" stroke-width="1.5"/>
      </svg>
      <svg class="arco-iso" viewBox="0 0 265.42 268.17"><use href="#iso"/></svg>
    </div>"""

    return f"""<footer id="cierre" class="cierre-final">
  {carnet(c["carnet_rol"], c["carnet_palabras"])}
  <div class="cierre-lado">
    {sello_aro(c["sello"], "fin")}
    <p class="cierre-mano" aria-hidden="true">{mano}</p>
  </div>

  <div class="wrap cierre-centro">
    {arco}
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    {parrafos(c["parrafos"])}
    <div class="ctas">{boton(c["cta_1"], "#admisiones", "pri")}</div>
    <a class="enlace-sub" href="#registro">{e(c["cta_2"])}</a>

    <ul class="con-lista">{marcas}</ul>

    <p class="firma">{e(c["firma"])}</p>
    <p class="con-remate claim"><span>{e(remate)}</span></p>
    <svg class="logo-foot" viewBox="0 0 863.98 253.56" role="img" aria-label="{e(c["marca"])}"><use href="#logo-full"/></svg>
  </div>
</footer>"""


def s_cinta_1():
    return cinta(C.HERO["materias"])


def s_cinta_2():
    return cinta(C.CIERRE["con"])


def s_experiencia_unificada():
    """Solo las sesiones en vivo.

    Se retiraron los otros dos bloques que llevaba fusionados:

    - "Tu campus, en un solo lugar" (Skool, seguimiento, comunidad), que además
      esperaba tres capturas que nunca llegaron.
    - "Cuando formas parte del Campus, no recibes solo clases", los quince
      puntos de lo que incluye. Descartado por diseño, y su contenido ya se
      repetía por toda la página.

    La copy de los dos sigue en contenido.py, en DIGITAL y EXPERIENCIA: no se
    borra material del cliente por una decisión de maquetación. Si vuelven,
    están ahí.

    Conserva el id "experiencia" para no romper el enlace del menú."""
    v = C.VIVO
    items = "".join(f'<article class="card mini"><h3>{e(t)}</h3><p>{e(d)}</p></article>'
                    for t, d in v["items"])
    return seccion("experiencia", "09", f"""
    {eyebrow(v["eyebrow"])}
    <h2>{e(v["titulo"])}</h2>
    <p class="lead">{e(v["bajada"])}</p>
    <div class="grid grid-4">{items}</div>""", "vivo")


def s_mercado_unificado():
    """Del campus al mercado + banco de oportunidades. Las dos responden "qué
    pasa cuando salgo"; la segunda era el detalle de la primera.

    Los nueve puntos de "trabajarás en" no son un temario: son los activos con
    los que la creadora sale del Campus. Como viñetas de texto se leían como una
    lista más; numerados y en fichas se leen como un inventario de lo que se
    lleva puesto.

    Los recursos del banco llevan icono. La lista de seis palabras sueltas era
    lo más plano de la página."""
    m, o = C.MERCADO, C.OPORTUNIDADES

    activos = "".join(
        f'<li style="--n:{i}"><i class="tic" aria-hidden="true">✓</i>'
        f'<span>{e(x.rstrip("."))}</span></li>'
        for i, x in enumerate(m["items"], 1))

    recursos = "".join(
        f'<li style="--n:{i}"><i aria-hidden="true">{ico}</i>'
        f'<span>{e(txt.rstrip("."))}</span></li>'
        for i, (ico, txt) in enumerate(o["items"], 1))

    return seccion("mercado", "12", f"""
    {eyebrow(m["eyebrow"])}
    {parrafos(m["intro"], "lead")}
    <p class="lead-min">{e(m["lead"])}</p>
    <ul class="activos">{activos}</ul>

    <div class="sub">
      <h3>{e(o["titulo"])}</h3>
      <p class="lead">{e(o["intro"])}</p>
      <ul class="recursos">{recursos}</ul>
      {parrafos(o["cierre"], "cierre")}
    </div>""", "mercado")


def sello_aro(texto, ident):
    """Sello circular: el texto gira alrededor del isotipo. El id del arco tiene
    que ser único por página, así que lo pone quien llama.

    textLength fuerza al texto a ocupar la circunferencia entera (2·pi·76 = 478):
    sin él, cada sello dejaba un hueco distinto según lo largo de su frase y el
    aro se leía como un arco cortado."""
    return f"""<div class="sello-aro" aria-hidden="true">
      <svg viewBox="0 0 200 200">
        <defs><path id="aro-{ident}" d="M100,100 m-76,0 a76,76 0 1,1 152,0 a76,76 0 1,1 -152,0"/></defs>
        <text class="aro-txt" textLength="478" lengthAdjust="spacing">
          <textPath href="#aro-{ident}" startOffset="0%">{e(texto)}</textPath>
        </text>
      </svg>
      <svg class="aro-iso" viewBox="0 0 265.42 268.17"><use href="#iso"/></svg>
    </div>"""


def carnet(rol, palabras):
    """El carnet de estudiante colgando de su cinta. Es el objeto que resume de
    qué va todo esto: entrar al Campus es recibir uno."""
    pals = "".join(f"<li>{e(x)}</li>" for x in palabras)
    return f"""<div class="carnet" aria-hidden="true">
      <span class="carnet-cinta"></span>
      <span class="carnet-clip"></span>
      <div class="carnet-tarjeta">
        <svg class="carnet-iso" viewBox="0 0 265.42 268.17"><use href="#iso"/></svg>
        <p class="carnet-marca">Crea y Monetiza<b>Campus</b></p>
        <p class="carnet-rol">{e(rol)}</p>
        <ul class="carnet-pals">{pals}</ul>
      </div>
    </div>"""


def s_admisiones_unificada():
    """¿Es para ti? + proceso + registro prioritario. Las tres son el mismo
    momento —decidir si entras— y estaban repartidas con otras secciones en
    medio, obligando a subir y bajar para decidir.

    El registro se presenta como un expediente de la oficina de admisiones: las
    mismas preguntas de siempre, agrupadas en tres pasos numerados. Sueltas, once
    campos seguidos se leen como un trámite; por pasos se ve dónde empiezas y
    cuánto falta.

    Se retiraron el bloque de cohorte y la pregunta de cierre por decisión del
    cliente; la copy de ambos sigue en contenido.py."""
    p, a, r = C.ES_PARA_TI, C.ADMISIONES, C.REGISTRO

    pasos = "".join(
        f'<li class="paso"><span class="paso-n">{i:02d}</span><h3>{e(t)}</h3><p>{e(dd)}</p></li>'
        for i, (t, dd) in enumerate(a["pasos"], 1))

    # Cada campo se arma por su nombre para que los grupos puedan citarlos.
    campos = {n: f"""<label class="campo-f">
      <span>{e(lab)}</span>
      <input type="{tipo}" name="{n}" placeholder="{e(ph)}" {"required" if req else ""}
             autocomplete="{'email' if tipo == 'email' else 'on'}">
    </label>""" for n, lab, tipo, req, ph in r["campos"]}

    opciones = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in r["punto_opciones"])
    campos["punto"] = f"""<label class="campo-f">
      <span>{e(r["punto_label"])}</span>
      <select name="punto" required><option value="">Selecciona una opción</option>{opciones}</select>
    </label>"""
    campos["objetivo"] = f"""<label class="campo-f ancho">
      <span>{e(r["objetivo_label"])}</span>
      <textarea name="objetivo" rows="4" placeholder="Cuéntanos tu visión…"></textarea>
    </label>"""

    # Con <fieldset>/<legend> el navegador impone su propio modelo de caja y la
    # retícula se rompe; el grupo se anuncia con role/aria-label, que da la misma
    # agrupación al lector de pantalla sin pelearse con el layout.
    grupos = "".join(f"""<div class="grupo-f g{i}" role="group" aria-label="{e(t)}">
      <div class="grupo-cab">
        <span class="grupo-n" aria-hidden="true">{i:02d}</span>
        <span class="grupo-txt"><b>{e(t)}</b><i>{e(d)}</i></span>
      </div>
      <div class="grupo-campos">{"".join(campos[k] for k in claves)}</div>
    </div>""" for i, (t, d, claves) in enumerate(r["grupos"], 1))

    return seccion("admisiones", "17", f"""
    {eyebrow(p["eyebrow"])}
    <h2>{e(a["titulo"])}</h2>

    <div class="grid grid-2">
      <article class="card si"><h3>{e(p["si_titulo"])}</h3>{lista(p["si"], "lista check")}</article>
      <article class="card no"><h3>{e(p["no_titulo"])}</h3>{lista(p["no"], "lista cruz")}</article>
    </div>
    <p class="cierre">{e(p["cierre"])}</p>

    <div class="sub">
      <h3>{e(a["eyebrow"])}</h3>
      {parrafos(a["intro"], "lead")}
      {lista(a["queremos"], "lista")}
      <ol class="pasos-grid">{pasos}</ol>
      <p class="nota">{e(a["nota"])}</p>
    </div>

    <div class="sub reg" id="registro">
      <h3 class="reg-t">{e(r["titulo"])}</h3>
      <p class="reg-baja">{e(r["bajada"])}</p>
      {lista(r["items"], "lista chips")}

      <div class="expediente">
        {carnet(r["carnet_rol"], r["carnet_palabras"])}
        {sello_aro(r["sello"], "reg")}
        <div class="carpeta">
          <span class="carpeta-lengueta" aria-hidden="true"></span>
          <div class="carpeta-hoja">
            <header class="exp-cab">
              <div class="exp-titulos">
                <p class="exp-of">{e(r["oficina"])}</p>
                <p class="exp-t">{e(r["form_titulo"])}</p>
                <p class="exp-sub">{e(r["form_sub"])}</p>
              </div>
              <p class="exp-lema"><b>Crea y Monetiza Campus</b><i>{e(r["lema"])}</i></p>
            </header>

            <form class="form" id="form-registro" novalidate>
              {grupos}
              <div class="exp-pie">
                <button class="btn btn-pri" type="submit">{e(r["boton"])} <span aria-hidden="true">→</span></button>
                <p class="form-msg" role="status" data-ok="{e(r["confirmacion"])}"></p>
                <p class="exp-nota">{e(r["nota"])}</p>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>""", "admisiones")


# Quince bloques donde antes había veintidós. No se quitó contenido: se
# fusionaron las secciones que respondían la misma pregunta y se plegó lo
# secundario. Los competidores directos del nicho tienen entre cuatro y cinco.
SECCIONES = [s_hero, s_cinta_1, s_carta, s_campus, s_perfil, s_recorrido,
             s_plan, s_tesis, s_experiencia_unificada,
             # s_facultad — la sección "Tu equipo" sale de la página por
             # decisión del cliente. La función y su copy siguen intactas:
             # vuelve descomentándola aquí y devolviendo su entrada al NAV.
             s_mercado_unificado, s_graduacion,
             # s_historias sale mientras Pierina reúne los casos, las capturas y
             # la aprobación de las alumnas. La función sigue abajo intacta:
             # vuelve descomentándola aquí.
             s_admisiones_unificada, s_faq, s_cinta_2, s_cierre]


def cinta_propuestas(prop):
    """Cinta para saltar entre propuestas. No forma parte de la landing: solo
    existe mientras se compara, y desaparece en la versión publicada."""
    if prop["clave"] == C.PUBLICADA:
        return ""
    return (f'<div class="cambiar"><span>Propuesta {prop["n"]} · {e(prop["nombre"])}</span>'
            f'<a href="../">Ver las {NUM_TXT}</a></div>')


def datos_estructurados():
    """Lo que Google necesita para entender qué es esto, en JSON-LD.

    Van tres cosas: la escuela, la propia página y el cuestionario de la
    secretaría académica. El último es el que más rinde: las preguntas
    frecuentes pueden salir desplegadas en el buscador, y aquí son trece
    respuestas reales ya escritas."""
    preguntas = [{
        "@type": "Question",
        "name": q,
        "acceptedAnswer": {"@type": "Answer", "text": " ".join(rs)},
    } for q, rs in C.FAQ["preguntas"]]

    datos = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "EducationalOrganization",
                "@id": f"{C.SITIO}/#campus",
                "name": C.MARCA["nombre"],
                "description": C.MARCA["descripcion"],
                "url": f"{C.SITIO}/",
                "logo": f"{C.SITIO}/assets/icono-apple.png",
                "image": f"{C.SITIO}/assets/compartir.png",
                "inLanguage": "es",
            },
            {
                "@type": "WebSite",
                "@id": f"{C.SITIO}/#sitio",
                "url": f"{C.SITIO}/",
                "name": C.MARCA["nombre"],
                "publisher": {"@id": f"{C.SITIO}/#campus"},
                "inLanguage": "es",
            },
            {"@type": "FAQPage", "mainEntity": preguntas},
        ],
    }
    # ensure_ascii=False para que las tildes viajen como tales, y sin barras
    # escapadas, que es como lo espera el validador de Google.
    crudo = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    # Dentro de un <script> no puede aparecer la secuencia que lo cerraría.
    crudo = crudo.replace("</", "<\\/")
    return f'<script type="application/ld+json">{crudo}</script>'


def pagina(prop):
    raiz = RAIZ_WEB
    v_base = version("css/base.css")
    v_tema = version(f"css/{prop['clave']}.css")
    v_js = version("js/campus.js")
    extra = hero_media(RAIZ_WEB) if prop.get("hero_extra") else ""
    cuerpo = "\n".join(
        (s(extra) if s is s_hero else s()) for s in SECCIONES)
    titulo = f'{C.MARCA["nombre"]} — Admisiones'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(C.MARCA["descripcion"])}">
<!-- La página llevaba noindex desde que era una propuesta a puerta cerrada.
     Ya es la web pública, así que se indexa. -->
<meta name="robots" content="index, follow">
<link rel="canonical" href="{C.SITIO}/">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(C.MARCA["descripcion"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{C.SITIO}/">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="{e(C.MARCA["nombre"])}">
<meta property="og:image" content="{C.SITIO}/assets/compartir.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}">
<meta name="twitter:description" content="{e(C.MARCA["descripcion"])}">
<meta name="twitter:image" content="{C.SITIO}/assets/compartir.png">
<meta name="theme-color" content="#500711">
<link rel="icon" href="{raiz}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{raiz}assets/icono-apple.png">
{datos_estructurados()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Outfit:wght@400;600;700;800&family=Caveat:wght@700&display=swap">
<link rel="stylesheet" href="{raiz}css/base.css?v={v_base}">
<link rel="stylesheet" href="{raiz}css/{prop["clave"]}.css?v={v_tema}">
</head>
<body class="v-{prop["clave"]}">
{logo_sprite()}
<a class="saltar" href="#inicio">Saltar al contenido</a>
{nav()}
<main>
{cuerpo}
</main>
<a class="cta-fijo" href="#admisiones">{e(C.CTA_FIJO)} <span aria-hidden="true">→</span></a>
{cinta_propuestas(prop)}
<script src="{raiz}js/campus.js?v={v_js}"></script>
</body>
</html>"""


def indice():
    tarjetas = ""
    for i, p in enumerate(C.PROPUESTAS, 1):
        tarjetas += f"""<article class="p-card p-{p["clave"]}">
      <p class="p-n">Propuesta {i}</p>
      <h2>{e(p["nombre"])}</h2>
      <p>{e(p["resumen"])}</p>
      <a class="btn btn-pri" href="../{p["slug"]}/">Abrir <span aria-hidden="true">→</span></a>
    </article>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crea y Monetiza Campus — {NUM_TXT.capitalize()} propuestas de landing</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Outfit:wght@400;600;700;800&family=Caveat:wght@700&display=swap">
<link rel="stylesheet" href="../css/base.css">
<link rel="stylesheet" href="../css/indice.css">
</head>
<body class="v-indice">
{logo_sprite()}
<div class="wrap idx">
  <svg class="logo" viewBox="0 0 863.98 253.56" role="img" aria-label="Crea y Monetiza Campus"><use href="#logo-full"/></svg>
  <p class="pill">Landing de admisiones · {NUM_TXT.capitalize()} direcciones</p>
  <h1>Mismo contenido, {NUM_TXT} diseños.</h1>
  <p class="lead">{NUM_TXT.capitalize()} llevan exactamente la misma copy y las mismas 22 secciones.
  Lo único que cambia es la dirección visual, para que la decisión sea sobre diseño
  y no sobre texto.</p>
  <div class="p-grid">{tarjetas}</div>
  <p class="nota-idx">{NUM_TXT.capitalize()} omiten por completo cualquier cifra económica: eso se
  comunica solo, y en privado, durante la entrevista de admisión. La build lo verifica
  antes de escribir cada página.</p>
</div>
</body>
</html>"""


def escribir(ruta, contenido, etiqueta):
    revisar_precios(contenido, etiqueta)
    os.makedirs(os.path.dirname(ruta) or RAIZ, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"  {os.path.relpath(ruta, RAIZ)}  ({len(contenido) // 1024} KB)")


def main():
    global RAIZ_WEB

    # slug y número salen de la posición en la lista: el orden se cambia ahí y
    # solo ahí.
    for i, prop in enumerate(C.PROPUESTAS, 1):
        prop["slug"] = f"propuesta-{i}"
        prop["n"] = i

    publicada = next((p for p in C.PROPUESTAS if p["clave"] == C.PUBLICADA), None)
    if publicada is None:
        print(f"ABORTADO — PUBLICADA={C.PUBLICADA!r} no existe en PROPUESTAS", file=sys.stderr)
        sys.exit(1)

    # La elegida va en la raíz: es la que sirve el dominio.
    RAIZ_WEB = ""
    escribir(os.path.join(RAIZ, "index.html"), pagina(publicada), "index")

    if C.BORRADORES:
        RAIZ_WEB = "../"
        for prop in C.PROPUESTAS:
            escribir(os.path.join(RAIZ, prop["slug"], "index.html"),
                     pagina(prop), prop["slug"])
        escribir(os.path.join(RAIZ, "propuestas", "index.html"), indice(), "indice")
    else:
        # Se borran los borradores para que no queden servidos por el dominio.
        import shutil
        for prop in C.PROPUESTAS:
            d = os.path.join(RAIZ, prop["slug"])
            if os.path.isdir(d):
                shutil.rmtree(d)
                print(f"  retirado {prop['slug']}/")
        d = os.path.join(RAIZ, "propuestas")
        if os.path.isdir(d):
            shutil.rmtree(d)

    # Las dos piezas que piden los buscadores y que no son HTML.
    escribir(os.path.join(RAIZ, "robots.txt"),
             "User-agent: *\nAllow: /\n\n"
             f"Sitemap: {C.SITIO}/sitemap.xml\n", "robots")
    escribir(os.path.join(RAIZ, "sitemap.xml"),
             '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             f"  <url>\n    <loc>{C.SITIO}/</loc>\n"
             f"    <lastmod>{datetime.date.today().isoformat()}</lastmod>\n"
             "    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n"
             "  </url>\n</urlset>\n", "sitemap")

    print(f"Publicada: {publicada['nombre']}. Sin cifras económicas.")


if __name__ == "__main__":
    main()
