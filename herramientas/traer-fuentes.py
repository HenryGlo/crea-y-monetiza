#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descarga las tipografías de Google y las deja servidas desde la propia web.

Por qué: pedirlas a fonts.googleapis.com mete dos dominios ajenos en el camino
crítico —resolver DNS, abrir TLS, bajar un CSS y solo entonces empezar a bajar
las fuentes—. En un móvil con datos eso son varias décimas de segundo antes de
que se pinte el primer titular, y en una campaña de pago ese retraso se paga en
gente que se va. Servidas desde el mismo dominio, el navegador ya tiene la
conexión abierta y puede además precargarlas.

Se queda solo el subconjunto `latin`: el español entra entero ahí (á é í ó ú ñ
ü ¿ ¡ están todos por debajo de U+00FF). Los subconjuntos cirílico, griego y
vietnamita que sirve Google no pintan nada en esta página.

    python3 herramientas/traer-fuentes.py

Genera assets/fuentes/*.woff2 y css/fuentes.css. Hay que volver a ejecutarlo
solo si cambian las familias o los pesos.
"""

import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "assets", "fuentes")
HOJA = os.path.join(RAIZ, "css", "fuentes.css")

PETICION = ("https://fonts.googleapis.com/css2"
            "?family=Anton&family=Outfit:wght@400;500;600;700;800"
            "&family=Caveat:wght@600;700&display=swap")

# Con un navegador moderno en la cabecera, Google devuelve woff2; con otro,
# formatos antiguos que pesan el doble.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# El bloque `latin` es el último de cada familia/peso y se reconoce por este
# rango, que es el que incluye el ASCII y los acentos del español.
LATIN = "U+0000-00FF"


def baja(url):
    pet = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(pet, timeout=30) as r:
        return r.read()


def main():
    os.makedirs(DESTINO, exist_ok=True)
    css = baja(PETICION).decode("utf-8")

    bloques = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)

    # Google sirve UNA fuente variable por familia y la ofrece bajo cada peso
    # pedido: los cinco archivos de Outfit son byte a byte el mismo. Guardarlos
    # cinco veces serían 160 KB para 32 KB de tipografía, así que se agrupa por
    # familia y el @font-face declara el rango de pesos que cubre.
    familias = {}
    for cuerpo in bloques:
        if LATIN not in cuerpo:
            continue
        familia = re.search(r"font-family:\s*'([^']+)'", cuerpo).group(1)
        peso = int(re.search(r"font-weight:\s*(\d+)", cuerpo).group(1))
        estilo = re.search(r"font-style:\s*(\w+)", cuerpo).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", cuerpo).group(1)
        f = familias.setdefault(familia, {"pesos": [], "estilo": estilo, "urls": {}})
        f["pesos"].append(peso)
        f["urls"][peso] = url

    reglas, bajados = [], 0
    for familia, datos in familias.items():
        pesos = sorted(datos["pesos"])
        nombre = "%s.woff2" % familia.lower().replace(" ", "-")
        ruta = os.path.join(DESTINO, nombre)
        if not os.path.exists(ruta):
            with open(ruta, "wb") as f:
                f.write(baja(datos["urls"][pesos[0]]))
            bajados += 1
        rango = str(pesos[0]) if len(pesos) == 1 else "%d %d" % (pesos[0], pesos[-1])
        reglas.append(
            "@font-face{\n"
            "  font-family:'%s';\n"
            "  font-style:%s;\n"
            "  font-weight:%s;\n"
            "  font-display:swap;\n"
            "  src:url('../assets/fuentes/%s') format('woff2');\n"
            "}" % (familia, datos["estilo"], rango, nombre))

    cabecera = (
        "/* ============================================================================\n"
        "   fuentes.css — GENERADO por herramientas/traer-fuentes.py. No editar a mano.\n"
        "\n"
        "   Las tipografías se sirven desde este mismo dominio en vez de pedírselas a\n"
        "   Google: así no hay que resolver dos dominios ajenos ni abrir dos conexiones\n"
        "   TLS antes de poder pintar el primer titular.\n"
        "\n"
        "   Solo el subconjunto latino, que es el que cubre el español entero.\n"
        "   `font-display:swap` para que el texto se lea desde el primer momento con la\n"
        "   tipografía del sistema y cambie al cargar la de marca.\n"
        "   ========================================================================== */\n\n")

    with open(HOJA, "w", encoding="utf-8") as f:
        f.write(cabecera + "\n".join(reglas) + "\n")

    total = sum(os.path.getsize(os.path.join(DESTINO, n))
                for n in os.listdir(DESTINO) if n.endswith(".woff2"))
    print("%d fuentes (%d nuevas) · %.0f KB · css/fuentes.css"
          % (len(reglas), bajados, total / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
