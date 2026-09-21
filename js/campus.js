/* ============================================================================
   campus.js — comportamiento de la propuesta 2.

   Orden: telón · navegación · entradas al hacer scroll · cifras · cinta ·
   video · carta · carriles · formulario.

   Todo lo que se mueve comprueba antes prefers-reduced-motion. El formulario
   es el de la primera versión, copiado sin cambios.
   ========================================================================== */
(function () {
  "use strict";

  var quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var movil  = window.matchMedia("(max-width: 699px)");

  /* ==================================================================== telón */

  /* La portada no depende del scroll real de la página: la página está
     bloqueada mientras el telón está puesto. Lo que hace avanzar el telón es
     el gesto —rueda, dedo o tecla—, y eso lo deja funcionar igual en móvil y
     en escritorio, donde el scroll fantasma de las barras de navegación de
     iOS habría descuadrado cualquier cálculo basado en scrollY. */
  function telon() {
    var el = document.getElementById("telon");
    var raiz = document.documentElement;
    if (!el || !raiz.classList.contains("telon-activo")) {
      if (el) el.remove();
      return;
    }

    var p = 0;
    var fuera = false;
    var umbral = Math.max(window.innerHeight * 0.85, 420);
    var y0 = 0;

    function pinta() {
      el.style.setProperty("--p", p.toFixed(4));
    }

    /* Al soltarse el telón, la cola del gesto sigue llegando: en un trackpad la
       inercia manda eventos hasta más de un segundo después de levantar los
       dedos. Para entonces el telón ya ha quitado sus oyentes y la página
       vuelve a poder desplazarse, así que esa cola la baja de varias pantallas
       de golpe y el recorrido empieza por la mitad en vez de por el hero.

       Se bloquea el desplazamiento en vez de cancelar los eventos: un scroll
       que viene del compositor no siempre se puede cancelar desde aquí, pero
       con la página bloqueada no hay nada que desplazar.

       Se suelta en cuanto el gesto para —150ms sin un solo evento— y nunca se
       queda enganchado: hay tope duro, y un empujón nuevo lo libera en el acto,
       porque la inercia solo decae y un evento más fuerte que el anterior ya no
       es inercia. */
    function amortiguaInercia() {
      var TOPE = 900;
      var QUIETO = 150;
      var arranque = Date.now();
      var ultimo = Infinity;
      var t = 0;
      var raizEl = document.documentElement;

      raizEl.classList.add("scroll-quieto");

      function suelta() {
        window.clearTimeout(t);
        raizEl.classList.remove("scroll-quieto");
        window.removeEventListener("wheel", vigila);
        window.removeEventListener("touchstart", suelta);
        window.removeEventListener("keydown", suelta);
      }

      function vigila(ev) {
        var d = Math.abs(ev.deltaY);
        if (d > ultimo + 1 || Date.now() - arranque > TOPE) { suelta(); return; }
        ultimo = d;
        window.clearTimeout(t);
        t = window.setTimeout(suelta, QUIETO);
      }

      window.addEventListener("wheel", vigila, { passive: true });
      /* Un dedo o una tecla son intención nueva: ahí sobra el amortiguador. */
      window.addEventListener("touchstart", suelta, { passive: true });
      window.addEventListener("keydown", suelta);
      t = window.setTimeout(suelta, QUIETO);
    }

    function retirar() {
      if (fuera) return;
      fuera = true;
      p = 1;
      pinta();
      raiz.classList.remove("telon-activo");
      el.classList.add("fuera");
      quita();
      window.scrollTo(0, 0);
      amortiguaInercia();
      /* El foco baja al contenido: quien navega con teclado no se queda
         atrapado en un botón que ya no está en pantalla. */
      var inicio = document.getElementById("inicio");
      if (inicio) {
        inicio.setAttribute("tabindex", "-1");
        inicio.focus({ preventScroll: true });
      }
      window.setTimeout(function () { el.remove(); }, 900);
    }

    function avanza(delta) {
      if (fuera) return;
      p = Math.min(1, Math.max(0, p + delta / umbral));
      pinta();
      if (p >= 0.995) retirar();
    }

    /* Si el gesto se queda a medias, el telón decide: pasado un tercio se va,
       antes vuelve a su sitio. Nunca se queda en un estado intermedio. */
    var vuelta;
    function resuelve() {
      window.clearTimeout(vuelta);
      vuelta = window.setTimeout(function () {
        if (fuera) return;
        if (p > 0.3) { retirar(); return; }
        el.style.transition = "transform .5s cubic-bezier(.22,.8,.28,1), opacity .5s, filter .5s";
        p = 0; pinta();
        window.setTimeout(function () { el.style.transition = ""; }, 520);
      }, 140);
    }

    function enRueda(ev) {
      ev.preventDefault();
      avanza(ev.deltaY);
      resuelve();
    }
    function enToque(ev) { y0 = ev.touches[0].clientY; }
    function enArrastre(ev) {
      var y = ev.touches[0].clientY;
      ev.preventDefault();
      avanza(y0 - y);
      y0 = y;
    }
    function enTecla(ev) {
      if (["ArrowDown", "PageDown", " ", "Enter", "Escape", "Tab"].indexOf(ev.key) > -1) {
        if (ev.key !== "Tab") ev.preventDefault();
        retirar();
      }
    }
    function quita() {
      window.removeEventListener("wheel", enRueda);
      window.removeEventListener("touchstart", enToque);
      window.removeEventListener("touchmove", enArrastre);
      window.removeEventListener("touchend", resuelve);
      window.removeEventListener("keydown", enTecla);
    }

    if (quieto) {
      /* Sin movimiento el telón no se levanta: se quita al primer gesto. */
      ["wheel", "touchstart", "keydown", "click"].forEach(function (e) {
        window.addEventListener(e, retirar, { once: true });
      });
    } else {
      window.addEventListener("wheel", enRueda, { passive: false });
      window.addEventListener("touchstart", enToque, { passive: true });
      window.addEventListener("touchmove", enArrastre, { passive: false });
      window.addEventListener("touchend", resuelve, { passive: true });
      window.addEventListener("keydown", enTecla);
    }

    var btn = document.getElementById("telon-saltar");
    if (btn) btn.addEventListener("click", retirar);

    /* Un ancla de la propia página (#registro desde el cierre, por ejemplo) no
       tiene sentido con el telón puesto. */
    window.addEventListener("hashchange", retirar);
  }

  /* =============================================================== navegación */

  function navegacion() {
    var nav = document.getElementById("nav");
    var avance = document.getElementById("avance");
    var cta = document.getElementById("cta-movil");
    var hero = document.getElementById("inicio");
    /* El botón flotante estorba justo donde ya hay una acción en pantalla:
       encima del formulario y encima del cierre. */
    var zonas = ["registro", "cierre"].map(function (id) {
      return document.getElementById(id);
    }).filter(Boolean);
    if (!nav) return;

    /* Arranca desde donde esté la página y no desde 0: al entrar por un ancla,
       con 0 el primer cálculo leía «ha bajado mucho» y escondía la barra antes
       de que nadie hubiera tocado nada. */
    var ultimo = window.scrollY;
    var pendiente = false;

    function pinta() {
      var y = window.scrollY;
      var alto = document.documentElement.scrollHeight - window.innerHeight;

      if (avance) avance.style.setProperty("--avance", (alto > 0 ? (y / alto) * 100 : 0) + "%");

      /* En móvil la barra se aparta al bajar y vuelve al subir. */
      if (movil.matches) {
        nav.classList.toggle("oculta", y > ultimo && y > 220);
      } else {
        nav.classList.remove("oculta");
      }
      ultimo = y;

      if (cta && hero) {
        var pasadoHero = y > hero.offsetHeight * 0.75;
        var estorba = zonas.some(function (z) {
          var r = z.getBoundingClientRect();
          return r.top < window.innerHeight && r.bottom > 0;
        });
        cta.classList.toggle("dentro", pasadoHero && !estorba);
      }
      pendiente = false;
    }

    window.addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      window.requestAnimationFrame(pinta);
    }, { passive: true });
    pinta();

    /* Enlace activo. */
    var enlaces = Array.prototype.slice.call(nav.querySelectorAll(".nav-links a"));
    var mapa = {};
    enlaces.forEach(function (a) {
      var s = document.querySelector(a.getAttribute("href"));
      if (s) mapa[s.id] = a;
    });
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        enlaces.forEach(function (a) { a.classList.remove("activo"); });
        if (mapa[e.target.id]) mapa[e.target.id].classList.add("activo");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(mapa).forEach(function (id) { obs.observe(document.getElementById(id)); });
  }

  /* ================================================== entradas al hacer scroll */

  /* Un solo motor y un solo ritmo para todo lo que entra, que es lo que hace
     que la página se lea como una pieza sincronizada y no como diez efectos
     sueltos. Tres trabajos, un mismo observador:

       1 · `.entra` → `.visible`, la entrada suelta de siempre.
       2 · el escalonado: a los hijos de cada retícula se les reparte
           `entra-d1..5` (70ms de paso) si no traen retardo propio.
       3 · los grupos con estado —el raíl que se traza, la checklist que se
           marca, los chips que encajan— llevan `.rv` puesta por el script y
           reciben `.dentro` al asomar.

     La regla que no se rompe: el estado escondido cuelga siempre de `.rv`, y
     `.rv` la pone este archivo. Si el script no carga, no hay `.rv`, no hay
     nada escondido y la página se lee entera. */

  var GRUPOS = ".linea, .activos, .vivo-rail, .tesis-piezas";

  function entradas() {
    var piezas = document.querySelectorAll(".entra");
    var grupos = document.querySelectorAll(GRUPOS);

    /* El escalonado se reparte antes de observar nada: así el retardo ya está
       puesto cuando la pieza entra. Solo a quien no traiga el suyo en el
       marcado, para no pisar los `--d` escritos a mano. */
    document.querySelectorAll(".rejilla, .etapas, .casos, .grad, .pasos, .si-no, .voz-rejilla, .videos-alumnas")
      .forEach(function (rejilla) {
        var hijos = rejilla.children, n = 0;
        for (var i = 0; i < hijos.length; i++) {
          var h = hijos[i];
          if (!h.classList.contains("entra") || h.style.getPropertyValue("--d")) continue;
          n++;
          h.classList.add("entra-d" + (n > 5 ? 5 : n));
        }
      });

    if (quieto || !("IntersectionObserver" in window)) {
      piezas.forEach(function (p) { p.classList.add("visible"); });
      return;
    }

    /* Los grupos arrancan escondidos solo ahora, con el script ya corriendo. */
    grupos.forEach(function (g) { g.classList.add("rv"); });

    var obs = new IntersectionObserver(function (lista) {
      lista.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add(e.target.matches(GRUPOS) ? "dentro" : "visible");
        obs.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    piezas.forEach(function (p) { obs.observe(p); });
    grupos.forEach(function (g) { obs.observe(g); });
  }

  /* ================================================== parallax de los parches */

  /* Los parches cosidos se mueven un poco menos que la página, solo en la
     primera pantalla y media: más abajo no se percibe y solo cuesta trabajo.
     Un rAF por gesto de scroll y el oyente pasivo, para no pelearse con el
     desplazamiento del navegador. */

  function parallax() {
    if (quieto) return;

    /* Solo los parches de la primera pantalla y media. El desfase se calcula
       contra `scrollY` absoluto, así que aplicado a un parche que vive a
       12.000px de scroll le metía 140px de desplazamiento y lo sacaba de su
       esquina: el de la Tesis y el de graduación acababan encima del texto. */
    var capas = [];
    document.querySelectorAll(".parche").forEach(function (p) {
      if (p.getBoundingClientRect().top + window.scrollY < window.innerHeight * 1.5) {
        capas.push(p);
      }
    });
    if (!capas.length) return;

    var pendiente = false;
    var fuera = false;
    window.addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      window.requestAnimationFrame(function () {
        pendiente = false;
        /* Pasado el tramo no basta con no pintar: hay que soltar el último
           valor, o el parche se queda congelado donde lo dejó el scroll. */
        if (window.scrollY > window.innerHeight * 1.5) {
          if (!fuera) {
            fuera = true;
            capas.forEach(function (c) { c.style.transform = ""; });
          }
          return;
        }
        fuera = false;
        for (var i = 0; i < capas.length; i++) {
          capas[i].style.transform =
            "translate3d(0," + window.scrollY * (0.04 + (i % 4) * 0.02) + "px,0)";
        }
      });
    }, { passive: true });
  }

  /* ===================================================================== cifras */

  function cifras() {
    var nums = document.querySelectorAll("[data-cuenta]");
    if (!nums.length || quieto || !("IntersectionObserver" in window)) return;

    var obs = new IntersectionObserver(function (lista) {
      lista.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        obs.unobserve(el);
        var fin = parseInt(el.dataset.cuenta, 10);
        var pre = el.dataset.pre || "";
        var t0 = performance.now();
        (function paso(t) {
          var k = Math.min(1, (t - t0) / 1100);
          var suave = 1 - Math.pow(1 - k, 3);
          el.textContent = pre + Math.round(fin * suave);
          if (k < 1) requestAnimationFrame(paso);
        })(t0);
      });
    }, { threshold: 0.5 });
    nums.forEach(function (n) { obs.observe(n); });
  }

  /* ====================================================================== cinta */

  /* Las seis materias, repetidas lo justo para que la cinta dé la vuelta sin
     costura: la animación desplaza exactamente la mitad de la pista. */
  var MATERIAS = [
    "Marca personal.",
    "Creación de contenido.",
    "UGC profesional.",
    "Negocio.",
    "Organización y productividad.",
    "Monetización."
  ];

  function cinta() {
    var pista = document.getElementById("cinta-pista");
    if (!pista) return;
    var mitad = "";
    for (var v = 0; v < 3; v++) {
      MATERIAS.forEach(function (m) {
        mitad += "<span>" + m + "</span><i aria-hidden=\"true\"></i>";
      });
    }
    pista.innerHTML = mitad + mitad;
  }

  /* ============================================================ el cortometraje */

  function video() {
    var fig = document.getElementById("cortometraje");
    if (!fig) return;
    var v = fig.querySelector("video");
    var btn = fig.querySelector(".sonido");
    if (!v) return;

    function arranca() {
      if (!v.src && v.dataset.src) v.src = v.dataset.src;
      var pr = v.play();
      if (pr && pr.catch) pr.catch(function () {});
    }

    /* El archivo pesa: no se descarga hasta que el hero está en pantalla. */
    var obs = new IntersectionObserver(function (lista) {
      lista.forEach(function (e) {
        if (e.isIntersecting) {
          arranca();
        } else if (!v.paused) {
          v.pause();
        }
      });
    }, { threshold: 0.25 });
    obs.observe(fig);

    /* Algunos navegadores rechazan el primer play() porque el archivo todavía
       no tiene datos, o porque la pestaña aún no ha recibido una interacción.
       Se reintenta cuando ya se puede pintar y al primer toque de la persona,
       en vez de dejar el video congelado en su primer fotograma. */
    v.addEventListener("canplay", function () {
      if (v.paused) arranca();
    });
    ["pointerdown", "keydown"].forEach(function (ev) {
      window.addEventListener(ev, function reintenta() {
        window.removeEventListener(ev, reintenta);
        if (v.paused && v.getBoundingClientRect().bottom > 0) arranca();
      }, { once: true });
    });

    if (btn) {
      btn.addEventListener("click", function () {
        v.muted = !v.muted;
        btn.setAttribute("aria-pressed", String(!v.muted));
        btn.setAttribute("aria-label", v.muted ? "Activar el sonido" : "Silenciar");
        if (!v.muted) {
          var pr = v.play();
          if (pr && pr.catch) pr.catch(function () {});
        }
      });
    }
  }

  /* ====================================================================== carta */

  /* El sobre llega cerrado, así que el estado que cuelga de una clase es el
     cerrado y no el abierto: sin script la carta se lee entera, que es lo que
     tiene que pasar si el archivo no carga.

     `sin-anim` se quita tras el primer pintado. Si no, el navegador anima el
     cierre inicial al cargar y se ve el gesto al revés. */
  function carta() {
    var sobre = document.getElementById("sobre");
    if (!sobre) return;
    var btn = sobre.querySelector(".sobre-btn");
    var cta = sobre.querySelector(".sobre-cta");

    /* rAF no se dispara en una pestaña oculta, y entonces el sobre se quedaba
       para siempre sin transiciones. El temporizador es el respaldo: quien
       llegue primero lo quita, y quitarlo dos veces no hace nada. */
    var suelta = function () { sobre.classList.remove("sin-anim"); };
    requestAnimationFrame(function () { requestAnimationFrame(suelta); });
    setTimeout(suelta, 120);

    btn.addEventListener("click", function () {
      var abierto = !sobre.classList.toggle("cerrada");
      btn.setAttribute("aria-expanded", String(abierto));
      cta.textContent = abierto ? cta.dataset.cerrar : cta.dataset.abrir;
    });
  }

  /* =================================================================== carriles */

  /* En móvil las tarjetas van en carril horizontal. Los puntos dicen cuántas
     hay y por cuál vas: sin ellos no se ve que haya más a la derecha. */
  function carriles() {
    document.querySelectorAll(".carril-pista[data-para]").forEach(function (pista) {
      var carril = document.getElementById(pista.dataset.para);
      if (!carril) return;
      var n = carril.children.length;
      pista.innerHTML = new Array(n + 1).join("<i></i>");
      var puntos = pista.querySelectorAll("i");
      puntos[0].classList.add("on");

      /* Si no hay nada que desplazar, los puntos mienten: dicen que hay más
         cuando ya se ve todo. Se comprueba al cargar y al cambiar el ancho,
         porque el carril deja de desplazarse justo al ensanchar la ventana. */
      var ajusta = function () {
        pista.hidden = carril.scrollWidth <= carril.clientWidth + 4;
      };
      ajusta();
      window.addEventListener("resize", ajusta, { passive: true });

      var pendiente = false;
      carril.addEventListener("scroll", function () {
        if (pendiente) return;
        pendiente = true;
        window.requestAnimationFrame(function () {
          var paso = carril.scrollWidth / n;
          var i = Math.min(n - 1, Math.round(carril.scrollLeft / paso));
          puntos.forEach(function (p, k) { p.classList.toggle("on", k === i); });
          pendiente = false;
        });
      }, { passive: true });
    });
  }

  /* ================================================================ formulario */

  /* Copiado sin cambios de la primera versión. Sigue pendiente la URL del
     webhook que recibe el registro prioritario: mientras esté vacía el
     formulario valida y avisa, pero no envía nada —preferible a que un lead
     real se pierda en silencio. */
  var ENDPOINT_REGISTRO = "";

  function formulario() {
    var form = document.getElementById("form-registro");
    if (!form) return;
    var msg = form.querySelector(".form-msg");
    var btn = form.querySelector("button[type=submit]");

    form.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      msg.className = "form-msg";
      msg.textContent = "";

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      var datos = Object.fromEntries(new FormData(form).entries());
      datos.origen = location.href;
      datos.enviado = new Date().toISOString();

      if (!ENDPOINT_REGISTRO) {
        msg.className = "form-msg err";
        msg.textContent =
          "Formulario de muestra: falta conectar el destino del registro. " +
          "Los datos no se han enviado.";
        console.info("[Campus] Registro sin endpoint. Datos capturados:", datos);
        return;
      }

      var textoBtn = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Enviando…";
      try {
        var res = await fetch(ENDPOINT_REGISTRO, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(datos)
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        form.reset();
        msg.className = "form-msg ok";
        msg.textContent = msg.dataset.ok;
      } catch (err) {
        msg.className = "form-msg err";
        msg.textContent = "No pudimos enviar tu registro. Vuelve a intentarlo en un momento.";
      } finally {
        btn.disabled = false;
        btn.textContent = textoBtn;
      }
    });
  }

  /* ====================================================== visor de capturas */

  /* Las capturas de resultados son anchas y con letra pequeña: en la página
     hacen de cartel y se leen de verdad aquí, ampliadas.

     Va sobre <dialog>, que ya trae el foco atrapado, el cierre con Esc y el
     fondo inerte. Lo que añade este código es la navegación entre las tres y
     devolver el foco al botón que abrió el visor. */

  function visorCapturas() {
    var dlg = document.getElementById("visor");
    if (!dlg || typeof dlg.showModal !== "function") return;

    /* Cada grupo se navega por separado: las dos capturas de una alumna son un
       grupo y las tres de la galería de resultados son otro. Mezclarlas en una
       sola lista dejaría las flechas saltando de un caso a otro sin sentido. */
    var grupos = Array.prototype.slice.call(
      document.querySelectorAll(".galeria, .ficha-capturas"));
    if (!grupos.length) return;

    var img = document.getElementById("visor-img");
    var pie = document.getElementById("visor-pie");
    var cuenta = document.getElementById("visor-cuenta");
    var lienzo = document.getElementById("visor-lienzo");
    var prev = dlg.querySelector('[data-visor="prev"]');
    var sig = dlg.querySelector('[data-visor="sig"]');

    var piezas = [];   // el grupo abierto ahora mismo
    var actual = 0;
    var abridor = null;

    function lee(boton) {
      var i = boton.querySelector("img");
      var f = boton.closest("figure");
      var cap = f && f.querySelector("figcaption");
      return {
        /* En la página va una versión ligera; el visor pide la grande, que es
           la única que se lee ampliada. */
        src: i.dataset.grande || i.getAttribute("src"),
        alt: i.getAttribute("alt") || "",
        pie: cap ? cap.innerHTML : ""
      };
    }

    function pinta(i) {
      actual = i;
      var p = piezas[i];
      img.src = p.src;
      img.alt = p.alt;
      pie.innerHTML = p.pie;
      cuenta.textContent = (i + 1) + " / " + piezas.length;
      prev.disabled = i === 0;
      sig.disabled = i === piezas.length - 1;
      /* Al cambiar de captura se vuelve al principio: si no, la siguiente
         aparecería empezada por la mitad allí donde se quedó la anterior. */
      lienzo.scrollLeft = 0;
      lienzo.scrollTop = 0;
    }

    grupos.forEach(function (grupo) {
      var botones = Array.prototype.slice.call(
        grupo.querySelectorAll(".prueba-abrir, .captura-abrir"));
      if (!botones.length) return;

      botones.forEach(function (b, i) {
        var f = b.closest("figure");
        var cap = f && f.querySelector("figcaption");
        b.setAttribute("aria-label",
          "Ampliar la captura" + (cap ? ": " + cap.textContent.trim() : ""));
        b.addEventListener("click", function () {
          piezas = botones.map(lee);
          abridor = b;
          pinta(i);
          dlg.showModal();
        });
      });
    });

    dlg.addEventListener("click", function (e) {
      var accion = e.target.closest("[data-visor]");
      if (accion) {
        var q = accion.dataset.visor;
        if (q === "cerrar") dlg.close();
        if (q === "prev" && actual > 0) pinta(actual - 1);
        if (q === "sig" && actual < piezas.length - 1) pinta(actual + 1);
        return;
      }
      /* Pulsar fuera cierra. El <dialog> ocupa toda la pantalla, así que
         «fuera» es el lienzo alrededor de la imagen, no el ::backdrop. */
      if (e.target === dlg || e.target === lienzo) dlg.close();
    });

    dlg.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft" && actual > 0) pinta(actual - 1);
      if (e.key === "ArrowRight" && actual < piezas.length - 1) pinta(actual + 1);
    });

    /* Esc lo cierra el navegador por su cuenta, así que devolver el foco va en
       `close` y no en cada salida. */
    dlg.addEventListener("close", function () {
      if (abridor) { abridor.focus(); abridor = null; }
    });
  }

  /* ================================================== la baraja de los casos */

  /* Las tres fichas se apilan al hacer scroll, pero solo si de verdad caben:
     una ficha clavada más alta que el hueco disponible nunca llega a enseñar su
     pie, y en el pie está la cita de la alumna, que es lo que mejor se lee de
     toda la ficha.

     Así que el tope de cada una se calcula: se la pega lo más arriba posible
     sin que se meta debajo de la barra, y si aun así no cabe entera, la baraja
     no se activa y las fichas se quedan en columna. Vale más leerlas seguidas
     que apiladas y a medias. */

  function baraja() {
    var caja = document.querySelector(".fichas");
    if (!caja) return;
    var fichas = Array.prototype.slice.call(caja.querySelectorAll(".ficha"));
    if (fichas.length < 2) return;

    /* La barra mide 67px; 70 le deja un respiro y además se esconde sola al
       bajar. Con 76 y 20 de margen, la baraja se apagaba por nueve píxeles en
       una ventana de 760 de alto, que es la de un portátil corriente. */
    var ALTO_BARRA = 70;
    var RESPIRO = 12;      // lo que se deja por debajo de la ficha

    function mide() {
      /* Por debajo de 900 no hay baraja: ahí las fichas son más altas que la
         pantalla y apilarlas solo taparía texto. */
      if (window.innerWidth < 900 || quieto) {
        caja.classList.remove("fichas--baraja");
        return;
      }

      /* Se mide con la baraja apagada: con las fichas clavadas, lo que devuelve
         getBoundingClientRect es la posición pegada, no la del flujo. */
      caja.classList.remove("fichas--baraja");

      var hueco = window.innerHeight - RESPIRO;
      var caben = true;
      var topes = fichas.map(function (f, i) {
        var alto = f.getBoundingClientRect().height;
        if (alto + ALTO_BARRA > hueco) caben = false;
        /* Lo más abajo que puede ir sin que se salga, con un escalón por ficha
           para que asome el canto de la anterior. */
        var tope = Math.min(ALTO_BARRA + 18 + i * 18, hueco - alto);
        return Math.max(ALTO_BARRA, Math.round(tope));
      });

      if (!caben) return;

      fichas.forEach(function (f, i) { f.style.setProperty("--tope", topes[i] + "px"); });
      caja.classList.add("fichas--baraja");
    }

    mide();
    /* Las fichas cambian de alto con el ancho y al cargar las capturas. */
    window.addEventListener("resize", mide, { passive: true });
    window.addEventListener("load", mide);
  }

  /* ====================================================================== arranque */

  function arranca() {
    telon();
    navegacion();
    entradas();
    cifras();
    cinta();
    video();
    carta();
    parallax();
    carriles();
    visorCapturas();
    baraja();
    formulario();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", arranca);
  } else {
    arranca();
  }
})();
