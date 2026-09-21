#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deja cada imagen al tamaño en que de verdad se ve en pantalla.

Por qué: la página se estaba sirviendo con imágenes mucho más grandes de lo que
llegan a mostrarse. Los parches bordados venían a 480px de ancho y no se ven a
más de 56. Eso son cientos de kilobytes que el navegador descarga, descomprime
y tira, y en una campaña de pago se paga dos veces: en datos y en la gente que
se va antes de que cargue.

Los anchos de abajo no están puestos a ojo: se midieron en el navegador el
ancho máximo real de cada imagen a 375, 768 y 1600px, y se guardó el mayor
multiplicado por dos, que es lo que pide una pantalla retina. Si el diseño
cambia de tamaños, hay que volver a medir y actualizar la tabla.

El original de todo lo que se reduce se guarda en `herramientas/originales/`,
así que el proceso es reversible y se puede volver a ejecutar sin degradar la
imagen una y otra vez: siempre parte del original, nunca del ya reducido.

    python3 herramientas/optimizar-imagenes.py
    python3 herramientas/optimizar-imagenes.py --simular   (no escribe nada)
"""

import os
import shutil
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINALES = os.path.join(RAIZ, "herramientas", "originales", "sin-optimizar")

# ancho máximo medido en pantalla × 2 (retina). Ver la explicación de arriba.
OBJETIVOS = {
    "assets/parches/logo-1.webp": 210,
    "assets/parches/logo-2.webp": 210,
    "assets/parches/estrella-1.webp": 210,
    "assets/parches/estrella-2.webp": 180,
    "assets/parches/estrella-3.webp": 210,
    "assets/parches/medalla-1.webp": 200,
    "assets/parches/tecla-1.webp": 120,
    "assets/parches/tecla-2.webp": 120,
    "assets/parches/tecla-3.webp": 120,
    "assets/parches/tecla-4.webp": 120,
    "assets/stickers/rayo-amar.webp": 140,
    "assets/stickers/rayo-rosa.webp": 140,
    "assets/stickers/rayo-azul.webp": 140,
    "assets/stickers/estrella-amar.webp": 90,
    "assets/stickers/estrella-rosa.webp": 90,
    "assets/stickers/estrella-azul.webp": 90,
    "assets/fotos/alfrelina.webp": 210,
    "assets/fotos/carolina.webp": 210,
    "assets/fotos/adriana.webp": 210,
    "assets/capturas/alfrelina-1.webp": 650,
    "assets/capturas/alfrelina-2.webp": 650,
    "assets/capturas/carolina-1.webp": 650,
    "assets/capturas/carolina-2.webp": 650,
    "assets/capturas/adriana-1.webp": 650,
    "assets/capturas/adriana-2.webp": 650,
}

# Las capturas de resultados son un caso aparte: en la página se ven a 347px,
# pero el visor las amplía y ahí hacen falta los 1400 enteros. Se guardan las
# dos: la pequeña para la tarjeta y la grande solo cuando alguien la abre.
DOBLES = {
    "assets/resultados/marce.webp": 720,
    "assets/resultados/angela.webp": 720,
    "assets/resultados/stephany.webp": 720,
}


def original(rel):
    """La copia intacta; la primera vez se crea desde el archivo actual."""
    guardado = os.path.join(ORIGINALES, rel)
    actual = os.path.join(RAIZ, rel)
    if not os.path.exists(guardado):
        os.makedirs(os.path.dirname(guardado), exist_ok=True)
        shutil.copy2(actual, guardado)
    return guardado


def kb(ruta):
    return os.path.getsize(ruta) / 1024


def main():
    simular = "--simular" in sys.argv
    antes = despues = 0
    filas = []

    for rel, ancho in sorted(OBJETIVOS.items()):
        destino = os.path.join(RAIZ, rel)
        if not os.path.exists(destino):
            print("· no está, se salta:", rel)
            continue
        fuente = original(rel)
        im = Image.open(fuente)
        if im.width <= ancho:
            continue
        peso_antes = kb(destino)
        nueva = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
        if not simular:
            nueva.save(destino, "WEBP", quality=82, method=6)
        antes += peso_antes
        despues += kb(destino) if not simular else peso_antes
        filas.append((rel, im.width, ancho, peso_antes, kb(destino)))

    # las capturas de resultados, en dos tamaños
    for rel, ancho in sorted(DOBLES.items()):
        destino = os.path.join(RAIZ, rel)
        if not os.path.exists(destino):
            continue
        fuente = original(rel)
        im = Image.open(fuente)
        chica = destino.replace(".webp", "-tarjeta.webp")
        if not simular:
            # la grande se restaura del original, por si una pasada anterior
            # la dejó reducida
            Image.open(fuente).save(destino, "WEBP", quality=82, method=6)
            im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS) \
              .save(chica, "WEBP", quality=80, method=6)
            filas.append((os.path.relpath(chica, RAIZ), im.width, ancho,
                          kb(destino), kb(chica)))

    print("%-44s %11s %9s" % ("archivo", "ancho", "peso"))
    for rel, w0, w1, k0, k1 in filas:
        print("%-44s %5d→%-5d %4.0f→%-4.0f KB" % (rel, w0, w1, k0, k1))
    if antes:
        print("\nParches, fotos y capturas: %.0f KB → %.0f KB (−%.0f%%)"
              % (antes, despues, 100 * (1 - despues / antes)))
    if simular:
        print("(simulación: no se ha escrito nada)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
