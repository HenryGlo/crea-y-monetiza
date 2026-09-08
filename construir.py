#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las tres propuestas de landing desde contenido.py.

    python3 construir.py

Las tres comparten el mismo marcado semántico y el mismo texto: lo que cambia es
la hoja de estilo. Así una corrección de copy se hace en un solo sitio y llega a
las tres, que es justo lo que hace falta mientras se elige dirección.
"""

import html
import os
import re
import sys

import contenido as C

RAIZ = os.path.dirname(os.path.abspath(__file__))

# El número de propuestas se decía a mano en el índice y en la cinta de cada
# página. Al añadir la cuarta quedaron todos desfasados, así que se deriva.
_NUM = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}
NUM_TXT = _NUM.get(len(C.PROPUESTAS), str(len(C.PROPUESTAS)))


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
EXCEPCIONES = ["Tu estructura de precios.", "Tarifas"]


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


# Pegatinas repartidas por la página. Cada sección lleva las suyas, colocadas
# desde CSS por la clase del hueco (d1 arriba-izquierda, d2 arriba-derecha,
# d3 abajo-izquierda, d4 abajo-derecha). Entran con un rebote al aparecer la
# sección y luego flotan, igual que las del hero.
DECORACION = {
    "campus":       [("estrella-rosa", "d2")],
    "perfil":       [("flor-amar", "d1")],
    "recorrido":    [("rayo-azul", "d2"), ("ovalo-rosa", "d3")],
    "plan":         [("flor-rosa", "d1")],
    "evaluacion":   [("estrella-amar", "d2")],
    "tesis":        [("flor-rosa", "d1"), ("estrella-azul", "d4")],
    "experiencia":  [("ovalo-amar", "d2")],
    "vivo":         [("rayo-rosa", "d1")],
    "mentoras":     [("estrella-rosa", "d4")],
    "oportunidades":[("ovalo-azul", "d2")],
    "incluye":      [("flor-amar", "d3")],
    "graduacion":   [("estrella-amar", "d1"), ("rayo-azul", "d4")],
    "registro":     [("flor-rosa", "d2")],
    "admisiones":   [("estrella-azul", "d1")],
    "faq":          [("ovalo-rosa", "d2")],
    "historias":    [("flor-azul", "d1")],
    "para-ti":      [("estrella-amar", "d4")],
    "cohorte":      [("rayo-amar", "d2")],
}


def decoracion(sid):
    piezas = DECORACION.get(sid, [])
    return "".join(
        f'<img class="deco {cls}" src="../assets/stickers/{n}.webp" alt="" '
        f'aria-hidden="true" loading="lazy" decoding="async">'
        for n, cls in piezas)


def seccion(sid, num, cuerpo, cls=""):
    return (f'<section id="{sid}" class="sec {cls}" data-num="{num}">'
            f'{decoracion(sid)}'
            f'<div class="wrap">{cuerpo}</div></section>')


def cinta(items, veces=3):
    """Cinta rodante. No añade contenido nuevo: repite las materias que ya
    están en el hero. Se duplica la tira porque el bucle es un desplazamiento
    del -50%: con una sola copia se vería el corte al reiniciar."""
    tira = "".join(
        f'<span>{e(x)}</span><span class="cinta-sep" aria-hidden="true">✳</span>'
        for x in items)
    return (f'<div class="cinta" aria-hidden="true"><div class="cinta-pista">'
            f'{tira * veces}{tira * veces}</div></div>')


def boton(texto, href, tipo="pri"):
    flecha = "→" if tipo == "pri" else "↓"
    return f'<a class="btn btn-{tipo}" href="{href}">{e(texto)} <span aria-hidden="true">{flecha}</span></a>'


# --------------------------------------------------------------------------
# Secciones
# --------------------------------------------------------------------------

def perfil_animado():
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
        persona = (f'<img class="pf-persona" src="../assets/{e(f["retrato"])}" '
                   f'alt="{e(f["retrato_alt"])}" loading="eager" decoding="async">')
    else:
        persona = ('<div class="pf-persona pf-persona-hueco pendiente" '
                   'role="img" aria-label="Falta el recorte de Pierina Alves">'
                   '<span>Recorte sin fondo<br>de Pierina</span></div>')

    return f"""<div class="pf">
  {persona}
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
        f'<img class="sticker {cls}" src="../assets/stickers/{n}.webp" alt="" '
        f'aria-hidden="true" loading="lazy" decoding="async">'
        for n, cls in piezas)


def s_hero(extra=""):
    h = C.HERO
    cifras = "".join(
        f'<div class="cifra"><b>{e(n)}</b><span>{e(t)}</span></div>'
        for n, t in h["cifras"])
    materias = "".join(f"<li>{e(m)}</li>" for m in h["materias"])
    return f"""<header id="inicio" class="hero">
  {stickers([("estrella-azul","s1"),("rayo-amar","s2"),("flor-rosa","s3"),("ovalo-azul","s4")])}
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


def s_carta():
    c = C.CARTA
    src = f'https://www.youtube-nocookie.com/embed/{c["video_id"]}?start={c["video_inicio"]}&autoplay=1&rel=0'
    # Fachada: la miniatura no carga nada de YouTube hasta que se pulsa, así el
    # visitante no queda expuesto a sus cookies solo por abrir la página.
    video = f"""<div class="video" data-src="{e(src)}">
      <button class="video-btn" type="button" aria-label="Reproducir el video de bienvenida">
        <span class="play" aria-hidden="true">▶</span>
        <span class="video-t">{e(c["video_titulo"])}</span>
      </button>
    </div>"""
    # La cita sobre un papel amarillo, no como texto suelto: es una nota suya
    # dentro de la página, y así se lee.
    cita = (f'<blockquote class="cita nota"><span>{e(c["cita"])}</span>'
            f'<cite>— {e(c["cita_autora"])}</cite></blockquote>')
    return seccion("carta", "02", f"""
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    <div class="carta-cuerpo">{parrafos(c["parrafos"])}</div>
    {video}
    {cita}
    <div class="ctas">{boton(c["cta"], "#campus", "sec")}</div>""", "carta")


def s_campus():
    c = C.CAMPUS
    return seccion("campus", "03", f"""
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    {parrafos(c["intro"], "lead")}
    {lista(c["necesidades"], "lista necesidades")}
    {parrafos(c["cierre"], "cierre")}""", "campus")


def s_perfil():
    p = C.PERFIL
    # Cada eje sobre una tecla. Los cuatro colores rotan; el icono es un signo
    # simple porque a este tamaño un pictograma detallado se pierde.
    teclas = ["vino", "rosa", "azul", "amar"]
    signos = ["✦", "✎", "◎", "⚡", "◆", "★"]
    ejes = "".join(
        f'<article class="card eje">'
        f'<span class="tecla" aria-hidden="true">'
        f'<img src="../assets/stickers/tecla-{teclas[(i-1) % 4]}.webp" alt="" loading="lazy" decoding="async">'
        f'<i>{signos[(i-1) % len(signos)]}</i></span>'
        f'<span class="eje-n">{i:02d}</span>'
        f'<h3>{e(t)}</h3><p>{e(d)}</p></article>'
        for i, (t, d) in enumerate(p["ejes"], 1))
    return seccion("perfil", "04", f"""
    {eyebrow(p["eyebrow"])}
    <h2>{e(p["titulo"])}</h2>
    <div class="grid grid-3">{ejes}</div>""", "perfil") + f"""
<div class="franja"><div class="wrap">
  <p>{e(p["cierre"])}</p>
  <img class="franja-sticker" src="../assets/stickers/rayo-azul.webp" alt="" aria-hidden="true" loading="lazy">
</div></div>"""


def s_recorrido():
    r = C.RECORRIDO
    etapas = ""
    for et in r["etapas"]:
        pasos = "".join(f"<li>{e(p)}</li>" for p in et["pasos"])
        intro = "".join(f"<p>{e(x)}</p>" for x in et["intro"].split("\n"))
        etapas += f"""<article class="card etapa" data-x="{e(et["n"].split()[-1])}">
      <p class="etapa-n">{e(et["n"])}</p>
      <p class="etapa-meses">{e(et["meses"])}</p>
      <h3>{e(et["titulo"])}</h3>
      {intro}
      <p class="lead-min">{e(et["lead"])}</p>
      <ol class="pasos">{pasos}</ol>
      <p class="cierre">{e(et["cierre"])}</p>
    </article>"""
    return seccion("recorrido", "05", f"""
    {eyebrow(r["eyebrow"])}
    <h2>{e(r["titulo"])}</h2>
    {parrafos(r["bajada"], "lead")}
    <div class="grid grid-2">{etapas}</div>""", "recorrido")


def s_plan():
    p = C.PLAN
    ms = ""
    for i, (t, d, sub) in enumerate(p["materias"], 1):
        cuerpo = f"<p>{e(d)}</p>" if d else ""
        if sub:
            cuerpo += '<ul class="temas">' + "".join(f"<li>{e(x)}</li>" for x in sub) + "</ul>"
        ms += f"""<li class="ruta-paso">
      <span class="ruta-nodo" aria-hidden="true">{i:02d}</span>
      <article class="card materia">
        <p class="materia-n">Materia {i:02d}</p>
        <h3>{e(t)}</h3>
        {cuerpo}
      </article>
    </li>"""
    return seccion("plan", "06", f"""
    {eyebrow(p["eyebrow"])}
    <h2>{e(p["titulo"])}</h2>
    <p class="lead">{e(p["bajada"])}</p>
    <ol class="ruta">{ms}</ol>
    {parrafos(p["cierre"], "cierre")}""", "plan")


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


def s_tesis():
    t = C.TESIS
    return seccion("tesis", "08", f"""
    {eyebrow(t["eyebrow"])}
    <h2>{e(t["titulo"])}</h2>
    <p class="lead-min">{e(t["lo_llamamos"])}</p>
    <p class="tesis-nombre">{e(t["nombre"])}</p>
    {parrafos(t["intro"])}
    <p class="lead-min">{e(t["lead"])}</p>
    {lista(t["integra"], "lista dos-col")}
    {parrafos(t["cierre"], "cierre")}""", "tesis")


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
                    f'<img class="cuaderno-foto" src="../assets/{e(foto)}" '
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
    <h2>{e(f["titulo"])}</h2>
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


def s_graduacion():
    g = C.GRADUACION
    bs = ""
    for t, ps, fecha in g["bloques"]:
        f = f'<p class="fecha">{e(fecha)}</p>' if fecha else ""
        bs += (f'<article class="card mini"><h3>{e(t)}</h3>{parrafos(ps)}{f}</article>')
    return seccion("graduacion", "16", f"""
    {eyebrow(g["eyebrow"])}
    <h2>{e(g["titulo"])}</h2>
    {parrafos(g["intro"], "lead")}
    <div class="grid grid-3">{bs}</div>
    <p class="cierre destacado">{e(g["cierre"])}</p>""", "graduacion")


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
    <div class="faq">{items}</div>""", "faq")


def s_cierre():
    c = C.CIERRE
    return f"""<footer id="cierre" class="cierre-final">
  <div class="wrap">
    {eyebrow(c["eyebrow"])}
    <h2>{e(c["titulo"])}</h2>
    {parrafos(c["parrafos"])}
    {lista(c["con"], "lista con")}
    <svg class="logo-foot" viewBox="0 0 863.98 253.56" role="img" aria-label="{e(c["marca"])}"><use href="#logo-full"/></svg>
    <p class="claim">{e(c["claim"])}</p>
    <div class="ctas">
      {boton(c["cta_1"], "#admisiones", "pri")}
      <a class="btn btn-sec" href="#registro">{e(c["cta_2"])}</a>
    </div>
    <p class="firma">{e(c["firma"])}</p>
  </div>
</footer>"""


def s_cinta_1():
    return cinta(C.HERO["materias"])


def s_cinta_2():
    return cinta(C.CIERRE["con"])


SECCIONES = [s_hero, s_cinta_1, s_carta, s_campus, s_perfil, s_recorrido, s_plan, s_evaluacion,
             s_tesis, s_digital, s_vivo, s_facultad, s_mercado, s_oportunidades,
             s_experiencia, s_historias, s_graduacion, s_registro, s_es_para_ti,
             s_admisiones, s_cohorte, s_faq, s_cinta_2, s_cierre]


def pagina(prop):
    extra = perfil_animado() if prop.get("hero_extra") else ""
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
<meta name="robots" content="noindex, follow">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(C.MARCA["descripcion"])}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Outfit:wght@300;400;500;600;700;800;900&family=Caveat:wght@500;600;700&display=swap">
<link rel="stylesheet" href="../css/base.css">
<link rel="stylesheet" href="../css/{prop["clave"]}.css">
</head>
<body class="v-{prop["clave"]}">
{logo_sprite()}
<a class="saltar" href="#inicio">Saltar al contenido</a>
{nav()}
<main>
{cuerpo}
</main>
<a class="cta-fijo" href="#admisiones">{e(C.CTA_FIJO)} <span aria-hidden="true">→</span></a>
<div class="cambiar">
  <span>Propuesta {prop["n"]} · {e(prop["nombre"])}</span>
  <a href="../">Ver las {NUM_TXT}</a>
</div>
<script src="../js/campus.js"></script>
</body>
</html>"""


def indice():
    tarjetas = ""
    for i, p in enumerate(C.PROPUESTAS, 1):
        tarjetas += f"""<article class="p-card p-{p["clave"]}">
      <p class="p-n">Propuesta {i}</p>
      <h2>{e(p["nombre"])}</h2>
      <p>{e(p["resumen"])}</p>
      <a class="btn btn-pri" href="{p["slug"]}/">Abrir <span aria-hidden="true">→</span></a>
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Outfit:wght@300;400;500;600;700;800;900&family=Caveat:wght@500;600;700&display=swap">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/indice.css">
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


def main():
    # slug y número salen de la posición en la lista: el orden se cambia ahí y
    # solo ahí.
    for i, prop in enumerate(C.PROPUESTAS, 1):
        prop["slug"] = f"propuesta-{i}"
        prop["n"] = i

    for prop in C.PROPUESTAS:
        d = os.path.join(RAIZ, prop["slug"])
        os.makedirs(d, exist_ok=True)
        pg = pagina(prop)
        revisar_precios(pg, prop["slug"])
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(pg)
        print(f"  {prop['slug']}/index.html  ({len(pg) // 1024} KB)")

    idx = indice()
    revisar_precios(idx, "index")
    with open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8") as f:
        f.write(idx)
    print(f"  index.html  ({len(idx) // 1024} KB)")
    print("Sin cifras económicas en ninguna página.")


if __name__ == "__main__":
    main()
