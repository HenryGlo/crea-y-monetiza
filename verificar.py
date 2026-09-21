#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revisa la propuesta antes de publicarla.

La regla innegociable del cliente sigue siendo la misma que en la primera
versión: en esta landing no puede aparecer ninguna cifra económica —ni precio,
ni matrícula, ni cuotas, ni planes de pago, ni rangos—. Todo eso se comunica en
privado durante la entrevista de admisión.

En la primera versión el HTML se generaba con Python y la comprobación vivía en
construir.py. Aquí el HTML se escribe a mano, así que la comprobación va en su
propio archivo y hay que ejecutarla:

    python3 verificar.py

Devuelve 0 si está limpio y 1 si encuentra algo, para poder encadenarlo a un
hook o a un despliegue.

Además comprueba que el bloque del registro prioritario sigue siendo idéntico
al de la web publicada, que es la otra cosa que no se puede romper sin darse
cuenta al editar.
"""

import os
import re
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(RAIZ), "crea-y-monetiza", "index.html")

# Los mismos patrones que hace cumplir la primera versión en construir.py.
# Van con límite de palabra a propósito: sin él, «vale la pena creer en ti»
# —que es copy del cortometraje— haría saltar la alarma.
PROHIBIDO = [
    r"€", r"\$", r"\bEUR\b", r"\bUSD\b",
    r"\bprecio\b", r"\bprecios\b", r"\bcoste\b", r"\bcosto\b",
    r"\bmatr[ií]cula\b", r"\bcuotas?\b", r"\bpago\b", r"\bpagos\b",
    r"\bfinanciaci[oó]n\b", r"\bplazos\b", r"\binversi[oó]n\b",
    r"\bdescuento\b", r"\bbeca\b", r"\btarifa\b",
]

# Términos del contenido real del Campus que contienen una palabra de la lista
# pero no comunican ninguna cifra: son materia de estudio, no el precio.
EXCEPCIONES = ["Tu estructura de precios", "Tarifas", "formalizas tu matrícula"]


def texto_visible(html):
    """El HTML sin marcado, comentarios ni scripts: lo que lee una persona."""
    sin = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    sin = re.sub(r"<(script|style)\b.*?</\1>", " ", sin, flags=re.S | re.I)
    sin = re.sub(r"<[^>]+>", " ", sin)
    return re.sub(r"\s+", " ", sin)


def revisar_precios(ruta):
    html = open(ruta, encoding="utf-8").read()
    plano = texto_visible(html)
    for exc in EXCEPCIONES:
        plano = plano.replace(exc, " ")

    fallos = []
    for patron in PROHIBIDO:
        for m in re.finditer(patron, plano, re.I):
            contexto = plano[max(0, m.start() - 60):m.end() + 60]
            fallos.append((m.group(0), " ".join(contexto.split())))
    return fallos


def revisar_registro(ruta):
    """El registro prioritario tiene que seguir siendo el de la primera versión."""
    if not os.path.exists(V1):
        return None  # no está la v1 al lado; no se puede comparar
    v1 = open(V1, encoding="utf-8").read()
    i = v1.find('<div class="sub reg" id="registro">')
    j = v1.find("    </div></div></section>", i)
    if i < 0 or j < 0:
        return None
    bloque = v1[i:j].rstrip()
    return bloque in open(ruta, encoding="utf-8").read()


def main():
    pagina = os.path.join(RAIZ, "index.html")
    ok = True

    fallos = revisar_precios(pagina)
    if fallos:
        ok = False
        print("✗ La página menciona condiciones económicas:")
        for termino, contexto in fallos:
            print("   · «%s» → …%s…" % (termino, contexto))
    else:
        print("✓ Sin cifras ni condiciones económicas.")

    intacto = revisar_registro(pagina)
    if intacto is None:
        print("· Registro prioritario: no se pudo comparar (falta la v1 al lado).")
    elif intacto:
        print("✓ Registro prioritario idéntico al de la web publicada.")
    else:
        ok = False
        print("✗ El bloque del registro prioritario ha cambiado respecto a la v1.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
