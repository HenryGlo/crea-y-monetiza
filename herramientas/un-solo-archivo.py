#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera «propuesta-completa.html»: la web entera en un único archivo.

Para qué: el index.html normal enlaza las hojas de estilo, el script y las
imágenes con rutas relativas. Eso está bien para trabajar y para publicar, pero
si el archivo viaja solo —se copia a otra carpeta, se manda por WhatsApp, se
sube a Drive— el navegador no encuentra nada y la página sale como texto plano
sobre fondo blanco.

Este archivo mete dentro del HTML el CSS, el JavaScript y todas las imágenes
(en base64), de modo que el resultado se abre bien en cualquier sitio, sin
carpetas al lado y sin servidor.

Fuera se quedan los videos: el cortometraje del hero y los testimonios de
alumnas suman más de 20 MB y meterlos dentro dejaría un archivo imposible de
mandar. En su lugar queda el fotograma de portada de cada uno, que es lo que se
ve hasta que el video arranca.

    python3 herramientas/un-solo-archivo.py

Hay que volver a ejecutarlo cada vez que se cambie el HTML, el CSS o el JS.
"""

import base64
import mimetypes
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "index.html")
SALIDA = os.path.join(RAIZ, "propuesta-completa.html")

# Los videos se quedan fuera: pesan más que todo lo demás junto. En base64
# crecen otro tercio, así que los 21 MB de los tres se convertirían en 28.
# Sus carteles sí entran, y son los que se ven en el archivo suelto.
FUERA = {
    "assets/hero-cortometraje.mp4",
    "assets/alumnas/andrea-lara.mp4",
    "assets/alumnas/tercero.mp4",
    "assets/alumnas/la-senal.mp4",
}


def leer(ruta):
    with open(os.path.join(RAIZ, ruta), encoding="utf-8") as f:
        return f.read()


def a_datos(ruta):
    """El archivo convertido en URL de datos, para que viaje dentro del HTML."""
    tipo, _ = mimetypes.guess_type(ruta)
    if tipo is None:
        tipo = "application/octet-stream"
    with open(os.path.join(RAIZ, ruta), "rb") as f:
        return "data:%s;base64,%s" % (tipo, base64.b64encode(f.read()).decode())


def main():
    if not os.path.exists(ENTRADA):
        sys.exit("No encuentro index.html")
    html = leer(ENTRADA)
    metidos, ausentes = 0, []

    # 1 · Las hojas de estilo, con sus propias rutas (../assets/…) ya resueltas.
    def hoja(m):
        nonlocal metidos
        ruta = m.group(1)
        css = leer(ruta)
        carpeta = os.path.dirname(ruta)

        def url_css(u):
            rel = u.group(1).strip("\"'")
            if rel.startswith(("data:", "http")):
                return u.group(0)
            destino = os.path.normpath(os.path.join(carpeta, rel))
            if not os.path.exists(os.path.join(RAIZ, destino)):
                ausentes.append(destino)
                return u.group(0)
            return 'url("%s")' % a_datos(destino)

        css = re.sub(r'url\(([^)]+)\)', url_css, css)
        metidos += 1
        return "<style>\n/* %s */\n%s\n</style>" % (ruta, css)

    html = re.sub(r'<link rel="stylesheet" href="(css/[^"]+)">', hoja, html)

    # Las precargas de las fuentes apuntan a archivos sueltos que en la versión
    # de un solo archivo no existen: se quitan para no dejar peticiones rotas.
    # Las fuentes en sí entran por el url() de css/fuentes.css, unas líneas más
    # arriba, igual que cualquier otra imagen.
    html = re.sub(r'\s*<link rel="preload" href="assets/fuentes/[^>]+>', "", html)

    # 2 · El script.
    def script(m):
        nonlocal metidos
        metidos += 1
        return "<script>\n%s\n</script>" % leer(m.group(1))

    html = re.sub(r'<script src="(js/[^"]+)"></script>', script, html)

    # 3 · Las imágenes y el resto de recursos del propio marcado.
    def recurso(m):
        nonlocal metidos
        attr, ruta = m.group(1), m.group(2)
        if ruta in FUERA or not os.path.exists(os.path.join(RAIZ, ruta)):
            return m.group(0)
        metidos += 1
        return '%s="%s"' % (attr, a_datos(ruta))

    html = re.sub(r'\b(src|href|poster|data-src)="((?:assets|favicon)[^"]*)"',
                  recurso, html)

    # Un aviso dentro del propio archivo, para quien lo abra dentro de un año.
    html = html.replace(
        "<head>",
        "<head>\n<!-- Archivo generado por herramientas/un-solo-archivo.py.\n"
        "     No editar a mano: los cambios se hacen en index.html y se vuelve\n"
        "     a generar. Lleva dentro el CSS, el JS y las imágenes. -->", 1)

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(html)

    print("propuesta-completa.html · %d recursos dentro · %.1f MB"
          % (metidos, os.path.getsize(SALIDA) / 1e6))
    if ausentes:
        print("No encontrados (se quedan como enlace):")
        for r in sorted(set(ausentes)):
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
