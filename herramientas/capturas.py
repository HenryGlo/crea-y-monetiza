#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara las capturas de las alumnas para publicarlas.

Las capturas llegan en los .docx que manda el Campus, y tal cual no se pueden
publicar: llevan números de teléfono, correos y perfiles de terceros, y —lo más
delicado— importes concretos. La regla innegociable del cliente es que en esta
landing no aparezca ninguna cifra económica, y una captura de un pago es la
forma más literal de romperla. verificar.py solo lee texto, así que las imágenes
hay que revisarlas a mano: esto es lo que deja constancia de qué se tapó y por
qué.

Cada receta dice de dónde sale la captura, qué trozo se conserva y qué zonas se
cubren. Las coordenadas van en fracciones del lado (0 a 1) para que no dependan
del tamaño del archivo original.

    python3 herramientas/capturas.py

Salida: assets/capturas/<alumna>-<n>.webp, con las esquinas redondeadas.
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Hace falta Pillow: python3 -m pip install Pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESCARGAS = os.path.expanduser("~/Downloads")
DESTINO = os.path.join(RAIZ, "assets", "capturas")

VINO = (80, 7, 17)
ANCHO = 760          # ancho final; en la web nunca se ve a más de ~380 CSS px
RADIO = 0.035        # radio de esquina, en fracción del ancho

# ---------------------------------------------------------------------------
# Las recetas. "recorte" y "tapar" van en fracciones (izq, arriba, der, abajo).
# ---------------------------------------------------------------------------
RECETAS = [
    {
        "salida": "alfrelina-1",
        "doc": "Alfrelina - Captures", "imagen": "image3.jpg",
        "pie": "Tymo Beauty la busca para una colaboración",
        # El correo con el que la marca se presenta. Se conserva desde el asunto
        # hasta la descripción de la marca; más abajo el correo entra en tarifas.
        "recorte": (0.02, 0.125, 0.98, 0.895),
        "tapar": [],
    },
    {
        "salida": "alfrelina-2",
        "doc": "Alfrelina - Captures", "imagen": "image17.png",
        "pie": "Alfrelina, al terminar el programa",
        "recorte": (0.0, 0.055, 1.0, 0.905),
        "tapar": [],
    },
    {
        "salida": "carolina-1",
        "doc": "Carolina Campos - captures", "imagen": "image52.jpg",
        "pie": "Carolina, tras cerrar su primera colaboración pagada",
        "recorte": None,
        "tapar": [],
    },
    {
        "salida": "carolina-2",
        "doc": "Carolina Campos - captures", "imagen": "image41.jpg",
        "pie": "La marca, después de recibir su video",
        "recorte": None,
        "tapar": [],
    },
    {
        "salida": "adriana-1",
        "archivo": "adriana-taza.webp",
        "pie": "Una de sus piezas, 3,4 M de reproducciones",
        "recorte": None,
        "tapar": [],
    },
    {
        "salida": "adriana-2",
        "archivo": "adriana-batidora.webp",
        "pie": "Bloomy Cakes, contado con criterio",
        "recorte": None,
        "tapar": [],
    },
]


def esquinas_redondeadas(im, radio):
    """Devuelve la imagen con las esquinas recortadas en curva."""
    mascara = Image.new("L", im.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [(0, 0), (im.size[0] - 1, im.size[1] - 1)], radius=radio, fill=255)
    fuera = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fuera.paste(im, (0, 0), mascara)
    return fuera


ORIGINALES = os.path.join(RAIZ, "herramientas", "originales")


def preparar(receta):
    if receta.get("archivo"):
        # Capturas que no vienen de un .docx: se guardan en
        # herramientas/originales/ para que esto se pueda repetir.
        origen = os.path.join(ORIGINALES, receta["archivo"])
    else:
        origen = os.path.join(DESCARGAS, "_docx", receta["doc"],
                              "word", "media", receta["imagen"])
    if not os.path.exists(origen):
        return None, origen
    im = Image.open(origen).convert("RGB")
    w, h = im.size

    if receta["recorte"]:
        a, b, c, d = receta["recorte"]
        im = im.crop((int(a * w), int(b * h), int(c * w), int(d * h)))
        w, h = im.size

    # Las bandas se pintan antes de escalar: así el borde queda limpio.
    dibujo = ImageDraw.Draw(im)
    for a, b, c, d in receta["tapar"]:
        caja = [int(a * w), int(b * h), int(c * w), int(d * h)]
        r = max(4, int((caja[3] - caja[1]) * 0.22))
        dibujo.rounded_rectangle(caja, radius=r, fill=VINO)

    if w > ANCHO:
        im = im.resize((ANCHO, int(h * ANCHO / w)), Image.LANCZOS)

    im = esquinas_redondeadas(im, int(im.size[0] * RADIO))
    salida = os.path.join(DESTINO, receta["salida"] + ".webp")
    im.save(salida, "WEBP", quality=82, method=6)
    return salida, None


def main():
    os.makedirs(DESTINO, exist_ok=True)
    faltan = []
    for receta in RECETAS:
        salida, ausente = preparar(receta)
        if ausente:
            faltan.append(ausente)
            continue
        print("%-14s %8d bytes  · %s"
              % (receta["salida"], os.path.getsize(salida), receta["pie"]))
    if faltan:
        print("\nNo encontré los originales. Hay que descomprimir los .docx en "
              "~/Downloads/_docx/<nombre del documento>/ :")
        for f in faltan:
            print("  ", f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
