#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recorta el tablero de ajedrez que las medallas traen pintado encima.

Las siete medallas de la carpeta de marca
(«🎨 BRANDING COMPLETO/Elementos Creativos/Parches/medallas/») se exportaron mal:
no tienen canal alfa —el alfa es 255 en el 100% de los píxeles— y el damero gris
que debería indicar transparencia está pintado dentro de la imagen. Por eso
«Alumna destacada» salía en la web con los cuadros de fondo.

Lo que hace este archivo: inunda desde el borde, pasando solo por los grises del
damero, y pone a cero el alfa de lo inundado. Como el relleno arranca del borde y
solo atraviesa esos dos grises, el blanco que sí forma parte del diseño —el
interior de la medalla— no se toca.

    python3 herramientas/limpiar-medallas.py

Solo hay que volver a ejecutarlo si llegan medallas nuevas.
"""

import os
import sys
from collections import deque

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Hace falta Pillow: python3 -m pip install Pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(
    os.path.dirname(RAIZ),
    "🎨 BRANDING COMPLETO", "Elementos Creativos", "Parches", "medallas",
)
DESTINO = os.path.join(RAIZ, "assets", "parches")

# Los dos grises del damero. Se miden, no se adivinan: son los dos colores más
# repetidos de la imagen después del propio diseño.
DAMERO = [(236, 236, 236), (254, 254, 254), (242, 242, 242), (243, 243, 243)]
TOLERANCIA = 7
LADO = 480


def es_damero(px):
    r, g, b = px[:3]
    # El damero es gris: los tres canales casi iguales. Con esto, un rosa claro
    # del diseño nunca entra aunque su luminosidad se parezca.
    if abs(r - g) > 4 or abs(g - b) > 4 or abs(r - b) > 4:
        return False
    return any(abs(r - c[0]) <= TOLERANCIA for c in DAMERO)


def limpiar(ruta):
    im = Image.open(ruta).convert("RGBA")
    im.thumbnail((LADO, LADO), Image.LANCZOS)
    w, h = im.size
    px = im.load()

    fuera = bytearray(w * h)          # 1 = es fondo, se vuelve transparente
    cola = deque()

    def empuja(x, y):
        i = y * w + x
        if fuera[i] or not es_damero(px[x, y]):
            return
        fuera[i] = 1
        cola.append((x, y))

    for x in range(w):
        empuja(x, 0)
        empuja(x, h - 1)
    for y in range(h):
        empuja(0, y)
        empuja(w - 1, y)

    while cola:
        x, y = cola.popleft()
        if x > 0:     empuja(x - 1, y)
        if x < w - 1: empuja(x + 1, y)
        if y > 0:     empuja(x, y - 1)
        if y < h - 1: empuja(x, y + 1)

    # La máscara se difumina un pelo antes de aplicarse: un recorte a pixel duro
    # deja el borde dentado, y el borde bordado de la medalla es justo lo que
    # hace que se lea como un parche.
    alfa = Image.frombytes("L", (w, h), bytes(255 if not v else 0 for v in fuera))
    alfa = alfa.filter(ImageFilter.GaussianBlur(0.6))
    im.putalpha(alfa)
    return im


def main():
    if not os.path.isdir(ORIGEN):
        sys.exit("No encuentro la carpeta de marca:\n  " + ORIGEN)
    os.makedirs(DESTINO, exist_ok=True)

    for n in range(1, 8):
        entrada = os.path.join(ORIGEN, "%d.png" % n)
        if not os.path.exists(entrada):
            continue
        im = limpiar(entrada)
        salida = os.path.join(DESTINO, "medalla-%d.webp" % n)
        im.save(salida, "WEBP", quality=80, method=6)
        esquina = im.getpixel((1, 1))[3]
        print("medalla-%d.webp  %sx%s  %d bytes  alfa en la esquina: %d"
              % (n, im.size[0], im.size[1], os.path.getsize(salida), esquina))


if __name__ == "__main__":
    main()
