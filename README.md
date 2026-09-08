# Crea y Monetiza Campus — landing de admisiones

Tres propuestas de diseño para la landing de admisiones del Campus.
Publicado en <https://web-crea-y-monetiza.perfectflow.cloud>.

## Qué hay aquí

| Ruta | Qué es |
|---|---|
| `/` | Portada interna para comparar las tres. Desaparece al elegir dirección. |
| `/propuesta-1/` | **Prospecto** — continuidad con la carpeta y el pensum: crema, stickers, tarjetas. |
| `/propuesta-2/` | **Expediente** — institucional: retícula marcada, filetes, catálogo universitario. |
| `/propuesta-3/` | **Nocturno** — premium: vino a sangre, tipografía a gran escala, luz de color. |
| `/propuesta-4/` | **Perfil** — el hero monta en directo el perfil de una creadora y remata en que eso no pasa solo. |

Las cuatro llevan **exactamente la misma copy** y las mismas 22 secciones. Lo único
que cambia entre ellas es la hoja de estilo.

## Responsive

Verificado midiendo, no a ojo, en iPhone SE (375×667), iPhone 15 (393×852),
iPhone 15 Pro Max (430×932), iPad mini (768×1024) e iPad Pro (1024×1366).

El criterio: **el botón de admisión entra en el pliegue en las cuatro propuestas
y en los cinco tamaños**, y ninguna página produce scroll horizontal. En una
landing cuyo único trabajo es abrir una admisión, un hero que no enseña su botón
no cumple.

Se resuelve por estructura y no encogiendo tipografía hasta que quepa: en móvil
los botones se adelantan a la lista de materias con `order`, sin tocar el
marcado — en escritorio el orden del guion sí cabe entero. En la propuesta
Perfil la tarjeta del perfil pasa por detrás del botón en teléfonos (mide 637px
y por sí sola echaba el CTA fuera de pantalla) y vuelve delante en tablet.

## Movimiento

Cinta rodante entre secciones, titulares que entran palabra a palabra, tarjetas
con relieve que sigue al cursor, botones imantados con barrido de luz, stickers
flotando, cifras que suben al entrar en pantalla y confeti al confirmar el
registro. La propuesta 4 añade el montaje del perfil.

Todo se apaga por completo con `prefers-reduced-motion`, y nada de ello decide
si el contenido se puede leer: si el JS no llega a ejecutarse, la página se lee
entera igual. El titular del hero se anima desde CSS por ese motivo — no puede
quedar en blanco esperando a que una clase llegue.

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
