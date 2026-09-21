# Crea y Monetiza Campus — propuesta 2

Segunda versión de la landing de admisiones. **Objetivo único: que una alumna
nueva entienda el Campus en una pasada y reserve.**

Es una web estática: se abre `index.html` y ya. No hay build ni dependencias.

```bash
cd "Crea y Monetiza - propuesta"
python3 -m http.server 8802
# http://localhost:8802/
```

---

## 1 · Qué cambia respecto a la primera versión

| | v1 | v2 |
|---|---|---|
| Entrada | Hero con titular + video + párrafo + 6 etiquetas + remate + 2 botones + 4 cifras, todo junto | **Telón**: una frase sola sobre vino. Al deslizar se levanta y aparece el hero, ya aligerado |
| Fondos | Pegatinas flotando sobre el color, colocadas al azar | **Papel**: grano real de la marca sobre hojas apiladas, y parches bordados cosidos a un borde |
| Secciones | 13 bloques con el mismo ritmo | 18 hojas con lengüeta, alternando crema, blanco, vino, rosa, azul y amarillo |
| Móvil | Retículas apretadas y listas larguísimas | Carriles horizontales, botón de admisión fijo, menú que se aparta al bajar |
| Prueba social | Ninguna | **4 secciones de alumnas** (1 en video + 3 escritas) |
| Navegación | 7 enlaces | 5 enlaces + botón |

---

## 2 · El telón

La primera pantalla no es la web: es la frase
**«Tu talento puede convertirse en una carrera profesional.»** sobre vino sólido.

Al primer gesto —rueda, dedo o tecla— la hoja se levanta en perspectiva, se
desenfoca y se va, y debajo aparece el hero. Funciona igual en móvil y en
escritorio porque **no depende del scroll de la página**: la página está
bloqueada y lo que avanza el telón es el gesto. Así ni las barras flotantes de
iOS ni el rebote del scroll descuadran la animación.

Detalles que importan:

- **Sin JavaScript no aparece.** Un telón que nadie puede retirar sería una
  página en blanco: la clase la pone un script en línea del `<head>`.
- **Si entras por un ancla** (`/#registro` desde un correo, por ejemplo) **no
  aparece**: quien viene a un sitio concreto no quiere una portada delante.
- **Se retira también con el teclado** (Tab, Enter, Esc, espacio, flecha abajo)
  y con el botón «Entrar al Campus».
- Con `prefers-reduced-motion` no se levanta: desaparece al primer gesto.
- El telón es `aria-hidden`: el `<h1>` real de la página vive en el hero, así
  que quien usa lector de pantalla nunca se queda atrapado en la portada.

Está en `css/cuaderno.css` (sección 01) y en `js/campus.js` (función `telon`).

---

## 3 · La dirección visual: el cuaderno del Campus

Todo sale de la carpeta de marca, no de una interpretación.

- **Las hojas.** Cada sección es una hoja de papel apilada sobre la anterior:
  esquinas superiores redondeadas y 34px de solape. No son bandas de color
  pegadas, es papel encima de papel.
- **Las lengüetas.** Cada hoja lleva su pestaña con número y nombre. Es el mismo
  objeto que ya tenía la carpeta del registro prioritario en la v1: repetirlo en
  toda la página es lo que ata el registro al resto en vez de dejarlo como una
  isla.
- **El grano.** Extraído de `Elementos Creativos/Fondos - Unicolor` de la marca,
  en un solo archivo de 5 KB (`assets/texturas/grano.webp`). Va en `overlay`
  sobre el color, no en `multiply`: el grano está centrado en gris medio, que en
  `overlay` es neutro, así que añade la variación del papel sin apagar la crema.
- **Los parches.** Estrella, rayo, medalla, logo y teclas salen de
  `Elementos Creativos/Parches` y `/Tecla`. Van **cosidos**: a la esquina del
  video, al borde de una franja, a la tarjeta de graduación. Ninguno flota.
- **El pespunte.** Los botones llevan una costura interior de puntos, la misma
  puntada que bordea los parches.
- Tipografías y colores, los de siempre: Anton, Outfit, Caveat · vino `#500711`,
  rosa `#F18BC4`, azul `#98B7FD`, amarillo `#F9FF80`, crema `#F8F3EF`.

---

## 4 · La jerarquía

El orden responde a lo que se pregunta una alumna nueva, en ese orden: *¿qué es
esto? → ¿de quién es? → ¿en qué se diferencia? → ¿funciona? → ¿cómo es por
dentro? → ¿es para mí? → ¿cómo entro?*

```
00  Telón ....................... la promesa, sola
01  #inicio ..................... hero: video, entrada, dos botones, cifras
    Cinta ....................... las seis materias
02  #carta ...................... carta de Pierina + trayectoria + marcas
03  #campus ..................... qué es + curso grabado vs. formación
04  #alumnas .................... ALUMNAS · en video           ← pendiente
05  #formacion .................. los seis ejes
06  #recorrido .................. 6 meses · 2 etapas
07  #plan ....................... plan de estudios + entregables
08  #tesis ...................... La Tesis Creativa
09  #casos ...................... ALUMNAS · los tres casos reales
10  #experiencia ................ en vivo + mercado + oportunidades
11  #graduacion ................. graduación y certificado
12  #resultados ................. ALUMNAS · capturas de la comunidad
13  #admisiones ................. ¿es para ti? + proceso
14  #registro ................... REGISTRO PRIORITARIO (intacto)
15  #faq ........................ secretaría académica
16  #cierre ..................... último capítulo
```

`#resultados` entra en la posición 12, entre graduación y admisiones: es la
última prueba que se lee justo antes de decidir. Sustituye a la antigua ficha
`#cita`, que ya no existe —la frase de cada alumna vive ahora dentro de su
propia ficha en `#casos`—.

Menú: **Inicio · El Campus · Tu recorrido · Alumnas · Admisiones** + botón
«Iniciar admisión». Cinco enlaces en vez de siete; los tres bloques de alumnas
cuelgan de «Alumnas».

**Fusiones**, para dejar de contar lo mismo tres veces:

- *Plan de estudios* + *Aquí también se evalúa* → una sola sección: qué estudias
  y cómo se comprueba que lo aplicas son el mismo asunto en dos tiempos.
- *El Campus en directo* + *Experiencia profesional* + *Oportunidades* →
  `#experiencia`: las tres contaban qué pasa fuera de las clases.
- *¿Es para ti?* + *Proceso de admisión* → `#admisiones`.

**Fuera:** la sección de equipo, por decisión del cliente. Con ella salen de la
página las fichas de Pierina, Paola y Nathaly — es la única mención que había de
Paola y de Nathaly, y `assets/pierina-retrato.webp` queda sin usar.


## 5 · Las tres secciones de alumnas

Tres formatos, cada uno probando algo distinto: la cara y la voz, el caso
completo, y lo que se dicen entre ellas sin que nadie se lo pida. El mensaje de
cada alumna vive **dentro de su propia ficha**, junto a su evidencia.

| Sección | Qué es | Dónde está | Estado |
|---|---|---|---|
| `#alumnas` | galería horizontal de 3 videos | Justo después de la comparación, donde alguien se pregunta por primera vez si esto funciona | Completo |
| `#casos` | 3 fichas: foto, historia, capturas y frase | Después de la Tesis, cuando ya se entiende qué se construye | Casi completo |
| `#resultados` | 3 capturas de la comunidad, ampliables | Entre graduación y admisiones: la última prueba antes de decidir | Completo |

### `#resultados` · las capturas de la comunidad

Tres publicaciones que las alumnas escribieron dentro de la comunidad
contando sus propios números. No son testimonios pedidos: es lo que se cuentan
entre ellas, que es exactamente por lo que convencen.

Las capturas son anchas (1400px) y con letra pequeña, así que en la página
funcionan **como cartel** —se ve de qué van y el pie resume la cifra— y el
contenido real se lee en un **visor a pantalla completa** que se abre al
pulsarlas. Sin ese visor, en un teléfono no se leería ni una cifra y la
sección sería puro adorno.

El visor va sobre `<dialog>` nativo, que ya trae el foco atrapado, el cierre
con Esc y el fondo inerte. Dentro de él la captura **no se encoge para caber**:
se muestra a 900px de ancho como mínimo y el lienzo se desplaza con el dedo,
que es lo que la hace legible. Se navega entre las tres con las flechas o con
los botones ‹ ›.

> **Antes de publicar:** son publicaciones de personas reales, con su nombre y
> su foto, sacadas de un espacio privado. Conviene tener su permiso por
> escrito para usarlas en una página pública.

### Las tres fichas

| Alumna | Texto | Foto | Capturas |
|---|---|---|---|
| Alfrelina Deluna | de `contenido.py` | ✓ | Tymo la busca · sus palabras al terminar |
| Carolina Campos | de `contenido.py` | ✓ | su primera colaboración pagada · la marca agradeciéndole |
| Adriana Ulloa | de `contenido.py` | ✓ | dos piezas de Bloomy Cakes con sus reproducciones |

Cada ficha lleva **una frase clave en negrita por campo**, para que el caso se
lea también en diagonal, y termina con la frase de la alumna en manuscrita.

Las capturas se eligieron por lo que prueban, no por lo que cuentan: una marca
buscándola, una colaboración cerrada, una marca dándole las gracias, un perfil
profesional montado desde cero. **En móvil la captura va delante del relato**:
es lo que para el pulgar y lo que hace que valga la pena leer lo de abajo.

Las fotos son recortes cuadrados centrados en la cara, y el marco es cuadrado
también: en círculo se comía las esquinas del recorte y la cara quedaba
descentrada.

María del Mar salió de la página por decisión del cliente. Su material sigue en
`~/Downloads/Maria del Mar - Captures.docx` por si vuelve; las recetas de sus
capturas se retiraron de `herramientas/capturas.py`.

### Las capturas

Las de Alfrelina, Carolina y María del Mar salen de los `.docx` que manda el
Campus. **No se publican tal cual**: llevan teléfonos, correos y perfiles de
terceros y, sobre todo, importes.

Qué se conserva y qué se tapa está declarado en `herramientas/capturas.py`, una
receta por captura, con las coordenadas en fracciones del lado. Para volver a
generarlas hay que descomprimir los `.docx` en `~/Downloads/_docx/<nombre>/` y:

```bash
python3 herramientas/capturas.py
```

**Ojo:** `verificar.py` solo lee texto, así que **no detecta una cifra dentro de
una imagen**. Cada captura nueva hay que mirarla a ojo antes de publicarla. La
regla del cliente —ninguna cifra económica en la página— vale igual para un
párrafo que para un pantallazo de un pago.

**Para completar lo que falta:**

- **Videos** (`#alumnas`): cambiar cada `<div class="video-hueco">` por un
  `<video>` o un `<iframe>`, y borrar la etiqueta `pendiente`.

## 6 · Qué texto se ha quitado, y por qué

No se ha reescrito nada: la copy es la de `contenido.py` de la primera versión.
Lo único que se ha retirado son repeticiones, tres:

1. **Las seis materias del hero.** Estaban como etiquetas dentro del hero y otra
   vez, palabra por palabra, en la cinta que se desliza justo debajo. Se quedan
   en la cinta.
2. **La cinta del cierre.** Repetía «Con estructura · Con formación · Con
   implementación · Con acompañamiento», que son exactamente los cuatro bloques
   que hay debajo en el pie. Se queda la lista del pie.
3. **La bajada de las historias** («Aquí queremos que conozcas algunos de los
   procesos…») aparecía dos veces al separar casos y videos. Se queda en
   `#voces-2`, que es de donde viene.

**Lo único escrito nuevo en toda la página** es el titular de `#alumnas`,
*«Las alumnas lo cuentan mejor.»*, porque esa sección no existía y necesitaba
uno. Está para cambiarlo.

Sigue sin publicarse, como en la v1 y por decisión del cliente: *Tu campus en un
solo lugar*, *Cuando formas parte del Campus no recibes solo clases*, la sección
de cohorte y los titulares retirados de equipo, mercado y graduación.

---

## 7 · El registro prioritario: intacto

- El HTML está copiado **carácter a carácter** de `crea-y-monetiza/index.html`.
- Sus estilos viven aparte, en `css/registro.css`, copiados tal cual de
  `crea-y-monetiza/css/base.css`. No se ha tocado ni un valor.
- El comportamiento del formulario en `js/campus.js` es el mismo.

`python3 verificar.py` lo comprueba comparando con la v1 y avisa si alguien lo
cambia sin querer. Si hay que tocar el registro, se toca en la v1 y se vuelve a
copiar aquí — no al revés.

---

## 8 · Antes de publicar

```bash
python3 verificar.py
```

Comprueba dos cosas:

1. **Que no aparece ninguna cifra ni condición económica** —ni precio, ni
   matrícula, ni cuotas, ni planes de pago—. Es la regla innegociable del
   cliente: eso se comunica solo, y en privado, durante la entrevista de
   admisión. Usa los mismos patrones que hacía cumplir `construir.py` en la v1.
2. **Que el registro prioritario sigue siendo el de la web publicada.**

Aquí **no hay `CNAME`** a propósito: la primera versión sí lo lleva y apunta a
`web-crea-y-monetiza.perfectflow.cloud`. Si esta carpeta se subiera con él,
se llevaría el dominio de la web que está publicada ahora mismo. Se añade el día
que esta propuesta la sustituya, no antes.

La página lleva `noindex` mientras sea una propuesta a puerta cerrada. Al
publicarla hay que cambiarlo, poner la URL canónica y devolver las etiquetas
para compartir en redes con rutas absolutas (están en el `<head>` con rutas
relativas, que sirven en local pero no al compartir un enlace).

---

## 9 · Pendiente de material

Marcado en pantalla con etiqueta amarilla o con texto entre corchetes, para que
no se confunda un hueco con una decisión de diseño:

- Los **videos de alumnas** ya están (tres, ver §5). La galería es horizontal,
  así que añadir un cuarto es meter otro `<figure class="video-alumna">`: no
  hay que tocar la retícula.

  Dos de los tres venían con franjas negras incrustadas —un clip casi cuadrado
  dentro de un lienzo 9:16—. Se recorta el negro al convertir y en la página se
  muestran enteros sobre su propio cartel difuminado, porque recortarlos a
  vertical les corta la cara: se mueven de encuadre.
- **Fechas de graduación** de cada cohorte → `[Fechas según calendario…]`.

También sin usar, a propósito: **`assets/fotos/pierina-ancha.webp`** (la foto
ancha que cerraba graduación) y **`assets/fotos/pierina-color-anterior.webp`**
(el retrato que había antes en la carta). Los dos se conservan en la carpeta
por si hay que volver atrás.
- **Destino del formulario**: la constante `ENDPOINT_REGISTRO` en
  `js/campus.js` está vacía. Mientras lo esté, el formulario valida y avisa en
  pantalla pero **no envía** — preferible a que un lead real se pierda en
  silencio.

### Lo que se pierde al borrar `#equipo`

La sección del equipo sale entera de la página a petición del cliente. Conviene
tenerlo apuntado porque no es solo maquetación:

- **Paola y Nathaly ya no aparecen en ningún sitio de la web.** Era su única
  mención. Si tienen que seguir estando, hay que decidir dónde: la carta de
  Pierina y el pie son los dos únicos sitios donde cabrían sin abrir otra
  sección.
- **Ya no hacen falta sus retratos**, que estaban pendientes de entrega.
- **`assets/pierina-retrato.webp` se queda sin usar.** No se borra: sigue en la
  carpeta por si el equipo vuelve o se quiere reutilizar en la carta.

### Los títulos, a dos o tres líneas

El cliente pidió titulares cortos de leer. En escritorio ninguno de los 19 `h2`
pasa de tres renglones (7 de uno, 7 de dos, 5 de tres): se consigue ensanchando
el renglón (`.cabecera h2{max-width:28ch}` y `.h2-largo{max-width:40ch}`), no
partiendo la frase en trozos.

A 375px los tres titulares más largos caen en cuatro renglones. Es el suelo
físico de un teléfono: bajarlos a tres exigiría un cuerpo tan pequeño que
dejarían de leerse como titulares. Si molestan, la salida no es CSS sino
acortar esas tres frases en la copy.

---

## 10 · Los archivos

```
index.html              toda la página, con la copy dentro
css/base.css            tokens de marca, retícula, tipografía, componentes
css/cuaderno.css        la dirección visual: telón, hero, hojas y secciones
css/registro.css        el registro prioritario, copiado de la v1 · NO TOCAR
js/campus.js            telón, navegación, entradas, parallax, video, carta,
                        carriles, formulario
verificar.py            la comprobación de antes de publicar
propuesta-completa.html  la web entera en un archivo · generada, no editar
assets/capturas/        las capturas de las alumnas, ya recortadas y tapadas
herramientas/           utilidades que se ejecutan a mano (ver §5, §11 y §12)
herramientas/limpiar-medallas.py   regenera las medallas sin el damero (§11)
assets/texturas/        el grano de papel de la marca
assets/parches/         parches bordados, medallas y teclas
assets/stickers/        estrellas y rayos de la marca, traídos de la v1:
                        viñetas de lista, iconos del pie y adornos del plan
assets/fotos/           fotos de Pierina del banco
assets/marcas/          logotipos de las marcas con las que ha trabajado
assets/alumnas/         los testimonios en video (mp4 720x1280) con su cartel
assets/resultados/      las tres capturas de §5, en dos tamaños:
                        *-tarjeta.webp para la página, la grande para el visor
assets/fuentes/         las tipografías, servidas desde aquí (ver §13)
css/fuentes.css         GENERADO por herramientas/traer-fuentes.py
herramientas/optimizar-imagenes.py  reduce cada imagen a lo que se ve (§13)
herramientas/traer-fuentes.py       baja las tipografías de Google (§13)
herramientas/originales/sin-optimizar/   copia intacta de lo reducido
```

En `assets/parches/` y `assets/fotos/` hay más piezas de las que usa la página
ahora mismo: están convertidas y listas para las secciones que faltan por
rellenar. Son archivos sueltos, no se descargan si nadie los pide.

`assets/pierina-retrato.webp` quedó sin usar al borrar `#equipo` y se conserva
a propósito (ver §9).

---

## 11 · Las medallas, sin damero

Las siete medallas originales (`Elementos Creativos/Parches/medallas/*.png`)
**no tenían canal alfa**: el tablero de ajedrez estaba pintado en los píxeles
—alfa 255 en el 100% de la imagen—, y por eso «Alumna destacada» salía con
cuadros grises de fondo.

`herramientas/limpiar-medallas.py` las regenera: construye una máscara con los
grises del damero, inunda desde el borde **solo a través de esa máscara** —así
el blanco del propio diseño no se destruye— y guarda el resultado en
`assets/parches/medalla-N.webp` con el borde suavizado.

Solo hay que volver a ejecutarlo si llegan medallas nuevas con el mismo
problema:

```bash
python3 herramientas/limpiar-medallas.py
```

El resto de parches (estrella, rayo, círculo, logo, tecla) sí traían el alfa
correcto y no pasan por aquí.

---

---

---

## 12 · Dos formas de abrirla

**`propuesta-completa.html` — para mirarla y para mandarla.**
Un solo archivo con el CSS, el JavaScript y todas las imágenes dentro. Se abre
con doble clic desde cualquier carpeta, se puede mandar por WhatsApp o subir a
Drive, y se ve igual. Pesa 2,3 MB. Lo único que se queda fuera son **los tres
videos** —el cortometraje del hero y los dos testimonios de alumnas, que suman
más de 20 MB y en base64 crecerían otro tercio—: en su lugar se ve el fotograma
de portada de cada uno.

Por eso, para **ver los videos** hay que abrir `index.html` con sus carpetas al
lado, o la web ya publicada.

**`index.html` — para trabajar y para publicar.**
El de siempre, con `css/`, `js/` y `assets/` al lado. Este es el que se edita y
el que se sube al servidor.

Después de tocar el HTML, el CSS o el JS hay que regenerar el de un solo
archivo:

```bash
python3 herramientas/un-solo-archivo.py
```

### Si alguna vez lo ves como texto plano

Letras negras sobre blanco, sin colores ni tipografías, y un isotipo negro
gigante: eso es la página sin ninguna hoja de estilo. Pasa cuando se abre
`index.html` pero el navegador no llega a la carpeta `css/` — casi siempre
porque el archivo viajó solo, sin las carpetas que lo acompañan.

Dos salidas: abrir `propuesta-completa.html` en su lugar, o asegurarse de que
`index.html`, `css/`, `js/` y `assets/` están en la misma carpeta.

---

## 13 · Que cargue rápido (para la campaña)

La página se va a usar con tráfico de pago, así que lo que tarde en pintarse se
paga dos veces: en datos y en la gente que se va antes de verla. Lo que se hizo:

**Las imágenes, al tamaño en que se ven.** Se midió en el navegador el ancho
real de cada imagen a 375, 768 y 1600px, y se redujo cada una a ese ancho por
dos (retina). Los parches bordados venían a 480px y no se ven a más de 56.

```bash
python3 herramientas/optimizar-imagenes.py          # --simular para no escribir
```

Parches, stickers, fotos y capturas: **951 KB → 418 KB (−56%)**. La herramienta
guarda el original en `herramientas/originales/sin-optimizar/` y siempre parte
de él, así que se puede volver a ejecutar sin degradar la imagen una y otra vez.

**Las capturas de resultados, en dos tamaños.** En la tarjeta se ven a 347px
pero el visor las amplía a 1400. Se sirve `*-tarjeta.webp` (720px) en la página
y la grande solo cuando alguien abre el visor: **240 KB que la mayoría ya no
descarga**. El enlace a la grande va en `data-grande` del `<img>`.

**Las tipografías, desde este dominio.** Antes se pedían a Google: dos dominios
ajenos que había que resolver y con los que había que abrir TLS *antes* de
poder pintar el primer titular.

```bash
python3 herramientas/traer-fuentes.py
```

Solo el subconjunto latino, que cubre el español entero. Google sirve una
**fuente variable por familia** —los cinco pesos de Outfit eran byte a byte el
mismo archivo—, así que se guarda una sola vez por familia y el `@font-face`
declara el rango de pesos: **315 KB → 116 KB**. Anton y Outfit van precargadas
porque son las que se leen en la primera pantalla; Caveat no, que pesa 74 KB y
no aparece hasta el remate del hero.

**Resultado medido** (en local, con la caché vacía):

| | antes | ahora |
|---|---|---|
| Primera pantalla | 806 KB | **467 KB** |
| Página entera | ~2,2 MB | **940 KB** |
| Dominios externos | 2 | **0** |
| `propuesta-completa.html` | 2,3 MB | **1,4 MB** |

Los tres videos siguen fuera del camino crítico: `preload="none"` y su cartel
en `poster`, así que no se descarga ni un byte de video hasta que alguien le da
al play.

**Lo que queda en manos del servidor**, y que no se puede hacer desde aquí:
activar **compresión** (gzip o brotli) y **caché larga** para `assets/`, `css/`
y `js/`. El CSS son 85 KB sin comprimir y se quedan en unos 18 con brotli. Sin
eso, la mitad del trabajo de arriba se pierde.

### Si se añaden imágenes nuevas

Hay que meterlas en la tabla de `optimizar-imagenes.py` con su ancho, o se
subirán a tamaño completo. Para saber el ancho, medirlo en el navegador —no
ponerlo a ojo—.

---

## 14 · Revisión de responsive y UX

Repaso completo a 360, 375, 414, 600, 768, 812, 860, 1024, 1280, 1440 y 1600px,
en vertical y en horizontal, y con el sobre y los desplegables abiertos (el peor
caso de maquetación). Lo que se encontró y se corrigió:

**El telón se pasaba de frenada.** Al levantarlo con un gesto fuerte, la página
bajaba cinco pantallas de golpe y el recorrido empezaba por la mitad. La causa:
el telón cancela la rueda mientras está puesto, pero al quitarse sus oyentes la
cola de inercia del mismo gesto —que en un trackpad llega hasta más de un
segundo después de levantar los dedos— caía ya sobre la página desbloqueada.

Ahora el desplazamiento se queda **bloqueado** hasta que el gesto para de verdad
(150ms sin un solo evento), y se suelta antes si llega un empujón nuevo, porque
la inercia solo decae. Se bloquea en vez de cancelar eventos: un scroll que
viene del compositor no siempre se puede cancelar desde el hilo principal, pero
con la página bloqueada no hay nada que desplazar. Medido: de **4.964px a 86px**.

**El telón no cabía en un teléfono en horizontal.** El cuerpo del titular salía
solo del ancho (11,2vw), y un móvil tumbado mide 812 de ancho por 375 de alto:
la última línea se cortaba y «Entrar al Campus» quedaba fuera de pantalla, sin
forma de llegar a él porque el telón no deja desplazar. Por debajo de 560px de
alto el cuerpo lo manda ahora la altura.

**Zonas de toque por debajo de 44px.** El botón de la barra, los dos «Ver el
detalle de la etapa» y «Entrar al registro prioritario» medían entre 23 y 37px
de alto. Crece la caja, no la letra.

**34 imágenes sin `width`/`height`.** Sin medidas declaradas, la maqueta salta
al cargar cada imagen. Ahora las llevan todas, incluidos los tres logotipos SVG.

**Dos adornos encima del texto en móvil y tablet.** La estrella de la Tesis y la
de la franja de perfil pisaban la primera línea del titular por unos píxeles.

**Un 404 en cada visita.** El navegador pide `/favicon.ico` por su cuenta aunque
haya un SVG declarado. Añadido.

### Cómo se comprobó

No a ojo: con un recorrido por el DOM que compara los rectángulos **reales de
las líneas de texto** (`Range.getClientRects()`) contra los adornos y las
lengüetas. Dos avisos para quien lo repita:

- La caja de un `h2` centrado llega hasta el borde de la sección aunque las
  letras no: comparar cajas da falsos positivos. Hay que comparar el texto.
- Un `<details>` cerrado y el sobre plegado **siguen devolviendo medidas** en
  Chromium. Para saber si algo se pinta de verdad, `el.checkVisibility({...})`.

### Lo que se dejó como está

- **Etiquetas de 11–11,5px** (los rótulos en mayúscula, los meses de cada etapa,
  los números de los chips). Son rótulos con interletrado ancho, no texto
  corrido, y forman un sistema coherente en toda la página.
- **Las fichas de casos no se apilan en móvil.** Miden hasta 1.246px en una
  pantalla de 812, así que no llegarían a clavarse nunca y lo único que se
  conseguiría es tapar texto. La baraja va de 900px de ancho para arriba, y
  solo si además caben de alto (ver §15).

---

## 15 · La baraja de los casos

Las tres fichas de `#casos` se apilan al hacer scroll: cada una se clava y la
siguiente sube y se le monta encima. Tiene dos condiciones que hay que
respetar, porque saltárselas se come contenido —pasó, y se corrigió—:

**1 · La ficha tiene que caber entera.** Clavada por arriba con un tope fijo de
94px, la primera ficha —832px de alto— pedía 926 en una ventana de 900: su cita
de cierre, que es lo último y lo que mejor se lee de la ficha, **no llegaba
nunca a pantalla**.

Ahora el tope de cada ficha lo calcula `baraja()` en `js/campus.js` con la
altura real y la de la ventana, y si aun así alguna no cabe, **desactiva la
baraja** y las deja en columna. Vale más leerlas seguidas que apiladas y a
medias.

**2 · Tiene que haber un rato para leerla.** La ficha de abajo tapa desde el pie
hacia arriba, y en el pie está la cita: es lo primero que desaparece. Ese rato
es exactamente el margen entre fichas, que pasó de 54px a `clamp(150px,24vh,
260px)`. Medido a 1440×900: cada cita se ve entera y sin tapar durante 420, 440
y 820px de scroll —unas cuatro vueltas de rueda— cuando antes eran 0.

### Para que cupieran, las capturas se ampliaron

La ficha era alta por las capturas: 437px de alto contra los 278 de la columna
de texto de al lado. Ahora en escritorio se recortan por el pie
(`object-position:50% 0`) a unos 200–260px, y **se pueden ampliar**: cada una es
un botón que abre el mismo visor de §5.

Es mejor que antes, no un recorte a secas: dentro de la ficha se veían a 225px
de ancho, donde no se lee una sola línea de lo que prueban. Ahora la ficha
enseña el cartel y el detalle se lee a pantalla completa.

El visor navega **por grupos**: las dos capturas de una alumna son un grupo y
las tres de la galería de resultados son otro. Con una sola lista, las flechas
saltaban de un caso a otro sin sentido.

### Si se retocan las fichas

Cualquier cosa que las haga más altas —un campo más, una cita más larga— puede
dejarlas sin caber y apagar la baraja sin avisar. Para comprobarlo, en la
consola del navegador:

```js
document.querySelector('.fichas').classList.contains('fichas--baraja')
```

Si sale `false` en una ventana de escritorio normal, es que alguna ficha se ha
pasado de alto.