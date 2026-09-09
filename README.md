# Crea y Monetiza Campus — landing de admisiones

Tres propuestas de diseño para la landing de admisiones del Campus.
Publicado en <https://web-crea-y-monetiza.perfectflow.cloud>.

## Qué hay aquí

La landing publicada es la propuesta **Perfil**, servida en la raíz del dominio.

Las otras tres direcciones (Prospecto, Expediente, Nocturno) siguen en el repo:
su hoja de estilo está en `css/` y su contenido en `contenido.py`. Para volver a
generarlas y compararlas, poner `BORRADORES = True` en `contenido.py` y
reconstruir: aparecen en `/propuesta-N/` con un índice en `/propuestas/`. Para
publicar otra, cambiar `PUBLICADA` a su clave.

## Cómo se edita

El texto **no** se toca en el HTML: los `index.html` se generan y cualquier cambio
hecho a mano se pierde en la siguiente build.

```
contenido.py     ← toda la copy vive aquí
construir.py     ← genera los cuatro index.html
css/base.css     ← tokens de marca, retícula, escala tipográfica, animación
css/p1|p2|p3.css ← la dirección visual de cada propuesta
js/campus.js     ← navegación, entradas al hacer scroll, video, formulario
```

Para regenerar tras editar contenido o estilos:

```bash
python3 construir.py
```

No necesita dependencias: solo Python 3.

Para verlo en local:

```bash
python3 -m http.server 8801
# http://localhost:8801/
```

## Regla que la build hace cumplir

La web pública **no muestra ninguna cifra económica** — ni precio, ni matrícula,
ni cuotas, ni planes de pago. Esa información se comunica solo, y en privado,
durante la entrevista de admisión.

`construir.py` revisa cada página antes de escribirla y **aborta la build** si
detecta cualquier término económico. Es la regla más fácil de romper sin darse
cuenta al editar copy más adelante, así que falla en vez de publicar el error.

## Pendiente de material del cliente

Marcado en pantalla con etiqueta amarilla, para que no se confunda un hueco con
una decisión de diseño:

- **Historias del Campus** (sección 15) — los tres casos con nombre, ciudad,
  punto de partida, qué trabajó y resultado comprobable, más el video o captura.
- **Capturas reales** de la plataforma Skool, del seguimiento y de la comunidad.
- **Retratos** de Pierina, Paola y Nathaly.
- **Recorte sin fondo de Pierina** para el hero de la propuesta 4: dejar el PNG
  con transparencia en `assets/pierina.png` y volver a construir. Conviene un
  plano de medio cuerpo, mirando ligeramente a la izquierda (queda a la derecha
  de la tarjeta) y de al menos 900px de alto. Mientras el archivo no exista, la
  build emite un hueco marcado en pantalla en vez de una imagen rota.
- **Fechas** de la próxima cohorte y estado de admisiones (sección 20).
- **Destino del formulario** de registro prioritario: la constante
  `ENDPOINT_REGISTRO` en `js/campus.js` está vacía. Mientras lo esté, el
  formulario valida y avisa en pantalla, pero no envía — preferible a que un
  lead real se pierda en silencio.

## Marca

Los colores y tipografías no son una interpretación: salen de las piezas que ya
existen (la carpeta y el pensum del Campus), con los mismos valores exactos.

- Vino `#500711` · Rosa `#F18BC4` · Azul `#98B7FD` · Amarillo `#F9FF80` · Crema `#F8F3EF`
- Anton (titulares) · Outfit (texto) · Caveat (manuscrita)
