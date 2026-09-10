/* Comportamiento común de la landing.

   Regla que se aplica a todo lo de aquí: si el JS no llega a ejecutarse, o si el
   sistema pide movimiento reducido, la página se lee entera igual. Nada de lo
   que hay debajo decide si el contenido es visible; solo cómo aparece. */

(function () {
  "use strict";

  const quieto = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------- entradas al hacer scroll */

  function prepararEntradas() {
    if (quieto) return;
    /* Se marcan desde JS y no en el HTML a propósito: si el script falla, el
       marcado no lleva la clase que lo dejaría invisible. */
    const bloques = document.querySelectorAll(
      ".sec > .wrap > *, .cierre-final > .wrap > *, .card, .paso, .faq-item"
    );
    bloques.forEach(function (el) {
      if (el.closest(".hero")) return;
      el.classList.add("rv");
    });

    /* Los hijos de una misma retícula entran escalonados, no todos de golpe. */
    document.querySelectorAll(".grid, .pasos-grid").forEach(function (g) {
      Array.prototype.slice.call(g.children, 0, 5).forEach(function (hijo, i) {
        hijo.classList.add("rv-d" + (i + 1));
      });
    });

    const obs = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (en) {
          if (!en.isIntersecting) return;
          en.target.classList.add("dentro");
          obs.unobserve(en.target);
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.05 }
    );
    document.querySelectorAll(".rv").forEach(function (el) { obs.observe(el); });
  }

  /* ------------------------------------------------ sección activa en el menú */

  function navActiva() {
    const enlaces = {};
    document.querySelectorAll(".nav-links a").forEach(function (a) {
      enlaces[a.getAttribute("href").slice(1)] = a;
    });
    const objetivos = Object.keys(enlaces)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!objetivos.length) return;

    /* Gana la sección más alta de las que están en pantalla; con umbral único
       el resaltado parpadea al cruzar dos secciones a la vez. */
    const visibles = new Set();
    const obs = new IntersectionObserver(
      function (ents) {
        ents.forEach(function (en) {
          if (en.isIntersecting) visibles.add(en.target.id);
          else visibles.delete(en.target.id);
        });
        let arriba = null;
        objetivos.forEach(function (s) {
          if (visibles.has(s.id) && !arriba) arriba = s.id;
        });
        Object.keys(enlaces).forEach(function (id) {
          enlaces[id].classList.toggle("en-vista", id === arriba);
        });
      },
      { rootMargin: "-84px 0px -55% 0px" }
    );
    objetivos.forEach(function (s) { obs.observe(s); });
  }

  /* -------------------------------------------------- progreso y CTA flotante */

  function progresoYCta() {
    const nav = document.querySelector(".nav");
    const cta = document.querySelector(".cta-fijo");
    if (!nav) return;
    const barra = document.createElement("div");
    barra.className = "progreso";
    nav.appendChild(barra);

    const hero = document.querySelector(".hero");
    let pendiente = false;

    function pintar() {
      pendiente = false;
      const alto = document.documentElement.scrollHeight - innerHeight;
      const pct = alto > 0 ? (scrollY / alto) * 100 : 0;
      barra.style.width = pct + "%";
      if (cta && hero) {
        /* El botón flotante aparece recién cuando el hero (que ya tiene sus dos
           CTA) sale de pantalla, para no duplicar la misma llamada dos veces. */
        cta.classList.toggle("visible", scrollY > hero.offsetHeight * 0.85);
      }
    }
    addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(pintar);
    }, { passive: true });
    pintar();
  }

  /* --------------------------------------------------------- cifras del hero */

  function contadores() {
    if (quieto) return;
    const nodos = document.querySelectorAll(".cifra b");
    const obs = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        obs.unobserve(en.target);
        const el = en.target;
        const original = el.textContent;
        const m = original.match(/^(\D*)(\d+)(\D*)$/);
        /* "1:1" no es una cantidad que se pueda contar: se deja tal cual. */
        if (!m) return;
        const destino = parseInt(m[2], 10);
        const t0 = performance.now();
        /* 2,2s en vez de 0,9s. A novecientos milisegundos el número saltaba de
           cero a doscientos setenta antes de que diera tiempo a mirarlo: se
           veía un parpadeo, no un conteo. */
        const DURACION = 2200;
        (function paso(t) {
          const k = Math.min((t - t0) / DURACION, 1);
          const suave = 1 - Math.pow(1 - k, 3);
          el.textContent = m[1] + Math.round(destino * suave) + m[3];
          if (k < 1) requestAnimationFrame(paso);
          else el.textContent = original;
        })(t0);
      });
    }, { threshold: 0.6 });
    nodos.forEach(function (n) { obs.observe(n); });
  }

  /* ----------------------------------------------------------- video de YouTube */

  function video() {
    document.querySelectorAll(".video").forEach(function (caja) {
      const btn = caja.querySelector(".video-btn");
      if (!btn) return;
      btn.addEventListener("click", function () {
        const marco = document.createElement("iframe");
        marco.src = caja.dataset.src;
        marco.title = "Video de bienvenida de Pierina Alves";
        marco.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
        marco.allowFullscreen = true;
        caja.appendChild(marco);
        btn.remove();
      });
    });
  }

  /* ------------------------------------------------------- parallax del hero */

  function parallax() {
    if (quieto) return;
    const capas = document.querySelectorAll(".sticker");
    if (!capas.length) return;
    let pendiente = false;
    addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(function () {
        pendiente = false;
        if (scrollY > innerHeight * 1.2) return;
        capas.forEach(function (c, i) {
          c.style.transform = "translate3d(0," + scrollY * (0.12 + i * 0.08) + "px,0)";
        });
      });
    }, { passive: true });
  }

  /* ------------------------------------------------------------- formulario */

  /* TODO — pendiente del cliente: aquí va la URL del webhook (Activepieces,
     Mailjet o lo que use el Campus) que recibe el registro prioritario.
     Mientras esté vacío el formulario valida y avisa, pero no envía nada:
     preferible a que un lead real se pierda en silencio. */
  const ENDPOINT_REGISTRO = "";

  function formulario() {
    const form = document.getElementById("form-registro");
    if (!form) return;
    const msg = form.querySelector(".form-msg");
    const btn = form.querySelector("button[type=submit]");

    form.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      msg.className = "form-msg";
      msg.textContent = "";

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const datos = Object.fromEntries(new FormData(form).entries());
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

      const textoBtn = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Enviando…";
      try {
        const res = await fetch(ENDPOINT_REGISTRO, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(datos)
        });
        if (!res.ok) throw new Error("HTTP " + res.status);
        form.reset();
        msg.className = "form-msg ok";
        msg.textContent = msg.dataset.ok;
        confeti(btn);
      } catch (err) {
        msg.className = "form-msg err";
        msg.textContent = "No pudimos enviar tu registro. Vuelve a intentarlo en un momento.";
      } finally {
        btn.disabled = false;
        btn.textContent = textoBtn;
      }
    });
  }

  /* ------------------------------------------------- titulares palabra a palabra */

  function titularesPorPalabra() {
    if (quieto) return;
    /* Se parte por palabras y no por letras: por letras el lector de pantalla
       deletrea, y `text-wrap:balance` deja de funcionar al perder los espacios. */
    /* Todos los titulares de sección, no solo el hero: son los "textos
       principales" de la página y sin esto quedaban planos frente al primero.
       Los h3 de tarjeta quedan fuera a propósito — son sesenta y pico, y a ese
       tamaño el reflejo no se aprecia pero sí se paga. */
    document.querySelectorAll(".hero h1, .sec h2, .cierre-final h2, .tesis-nombre").forEach(function (h) {
      if (h.querySelector(".pal")) return;

      /* Los titulares con degradado recortado (background-clip:text) no se
         pueden partir: el color real lo pinta el fondo del propio elemento, y
         al meter cada palabra en su caja el degradado deja de alcanzarlas — el
         titular desaparece entero. Se les deja la entrada completa, sin
         escalonar, que sobre ese tratamiento se ve igual de bien. */
      var est = getComputedStyle(h);
      if ((est.webkitBackgroundClip || est.backgroundClip) === "text") {
        h.classList.add("entra-entero");
        return;
      }

      const palabras = h.textContent.trim().split(/\s+/);
      h.setAttribute("aria-label", h.textContent.trim());
      h.textContent = "";

      /* Lo que va entre comillas angulares se marca aparte: son frases que el
         titular cita para rechazarlas —«una chica que hace videos»— y en la
         página se escriben a mano y tachadas. Se detecta aquí, sobre las
         palabras ya partidas, en vez de con marcado propio: así cualquier
         titular que use « » recibe el tratamiento sin tocar el generador. */
      /* La frase citada va en su propio contenedor y en su propia línea. Suelta
         entre las demás palabras se partía por la mitad —"una" al final de una
         línea y "chica que hace videos" al principio de la siguiente— y perdía
         todo el gesto. En bloque cae entera y el tachado la cruza de una vez. */
      let cita = null;

      palabras.forEach(function (p, i) {
        const abre = p.indexOf("«") !== -1;
        const cierra = p.indexOf("»") !== -1;

        if (abre && !cita) {
          cita = document.createElement("span");
          cita.className = "mano";
          cita.setAttribute("aria-hidden", "true");
          h.appendChild(cita);
        }

        /* La puntuación que va detrás del cierre pertenece a la frase de
           fuera, no a la cita: en «…hace videos». el punto es del titular. Sin
           separarlo quedaba dentro del tachado, que es un error de lectura. */
        const limpio = p.replace(/[«»]/g, "");
        let dentro = limpio, fuera = "";
        if (cierra) {
          const corte = p.indexOf("»");
          dentro = p.slice(0, corte).replace(/«/g, "");
          fuera = p.slice(corte + 1);
        }

        const s = document.createElement("span");
        s.className = "pal" + (cita ? " pal-mano" : "");
        s.setAttribute("aria-hidden", "true");
        s.style.setProperty("--i", i);
        s.textContent = dentro;

        (cita || h).appendChild(s);
        (cita || h).appendChild(document.createTextNode(" "));

        if (cierra) {
          cita = null;
          /* Si detrás del cierre solo queda puntuación, se descarta: la cita va
             en su propia línea, así que el punto caía suelto al principio de la
             línea siguiente. El salto de línea ya cierra la frase. */
          if (fuera && !/^[.,;:!?]+$/.test(fuera)) {
            const post = document.createElement("span");
            post.className = "pal";
            post.setAttribute("aria-hidden", "true");
            post.style.setProperty("--i", i);
            post.textContent = fuera;
            h.appendChild(post);
            h.appendChild(document.createTextNode(" "));
          }
        }
      });
      h.classList.add("por-palabra");
    });

    const obs = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting) en.target.classList.add("entra");
      });
    }, { threshold: 0.15 });

    document.querySelectorAll(".por-palabra").forEach(function (h) {
      /* El del hero se anima solo desde CSS (ver .hero .por-palabra en
         base.css): ya está en pantalla al cargar y no debe depender de que
         una clase llegue a tiempo. */
      if (!h.closest(".hero")) obs.observe(h);
    });

    /* Antes se pausaba el reflejo en los titulares fuera de pantalla para no
       tener 188 palabras repintándose a la vez. Se quitó: el cliente pidió
       expresamente que no se detenga nunca, y era el único mecanismo capaz de
       detenerlo. Si el consumo llega a notarse en móvil, la vía correcta es
       reducir el número de titulares con reflejo, no pausarlos. */
  }

  /* --------------------------------------------- el perfil espera a estar a la vista */

  function montajePerfil() {
    const pf = document.querySelector(".pf");
    if (!pf || quieto) return;

    /* El montaje es CSS y arranca al cargar la página. En escritorio eso está
       bien porque la tarjeta ya se ve; en móvil quedó por debajo del pliegue y
       la escena terminaba antes de que nadie llegase a mirarla.

       Se pausa desde JS y se reanuda al entrar en pantalla. La pausa se añade
       desde aquí y no en el CSS a propósito: si el script no llega a
       ejecutarse, la animación corre como antes en vez de quedarse congelada e
       invisible. */
    /* Si ya se ve al cargar —el caso de escritorio— no se pausa nada: pausar
       para reanudar en el mismo instante solo añade una forma de fallar. */
    const caja = pf.getBoundingClientRect();
    if (caja.top < innerHeight * 0.8) return;

    pf.classList.add("pf-espera");

    function arrancar() {
      pf.classList.remove("pf-espera");
      clearTimeout(seguro);
      obs.disconnect();
    }

    const obs = new IntersectionObserver(function (ents) {
      if (ents[0].isIntersecting) arrancar();
    }, { threshold: 0.2 });
    obs.observe(pf);

    /* Red de seguridad. Una escena pausada que nunca arranca deja la tarjeta
       invisible, que es peor que la animación que se pierde: si en 6s el
       observador no ha avisado, se arranca igual. */
    const seguro = setTimeout(arrancar, 6000);
  }

  /* ------------------------------------------------------------ botones imantados */

  function imanes() {
    if (quieto || matchMedia("(pointer: coarse)").matches) return;
    document.querySelectorAll(".btn, .nav-cta, .cta-fijo").forEach(function (b) {
      b.addEventListener("pointermove", function (ev) {
        const r = b.getBoundingClientRect();
        /* Desplazamiento corto y proporcional: si el botón se va demasiado
           lejos del cursor, se vuelve difícil de pulsar. */
        const x = (ev.clientX - r.left - r.width / 2) * 0.22;
        const y = (ev.clientY - r.top - r.height / 2) * 0.3;
        b.style.transform = "translate(" + x + "px," + y + "px)";
      });
      b.addEventListener("pointerleave", function () { b.style.transform = ""; });
    });
  }

  /* ------------------------------------------------------------ tarjetas con relieve */

  function relieve() {
    if (quieto || matchMedia("(pointer: coarse)").matches) return;
    document.querySelectorAll(".card").forEach(function (c) {
      c.addEventListener("pointermove", function (ev) {
        const r = c.getBoundingClientRect();
        const px = (ev.clientX - r.left) / r.width - 0.5;
        const py = (ev.clientY - r.top) / r.height - 0.5;
        c.style.setProperty("--rx", (-py * 5).toFixed(2) + "deg");
        c.style.setProperty("--ry", (px * 5).toFixed(2) + "deg");
        /* Posición del brillo, para que la luz siga al cursor. */
        c.style.setProperty("--mx", ((px + 0.5) * 100).toFixed(1) + "%");
        c.style.setProperty("--my", ((py + 0.5) * 100).toFixed(1) + "%");
      });
      c.addEventListener("pointerleave", function () {
        c.style.removeProperty("--rx");
        c.style.removeProperty("--ry");
      });
    });
  }

  /* ------------------------------------------------------------- foco del cursor */

  function focoCursor() {
    if (quieto || matchMedia("(pointer: coarse)").matches) return;
    const hero = document.querySelector(".v-nocturno .hero, .v-perfil .hero");
    if (!hero) return;
    hero.addEventListener("pointermove", function (ev) {
      const r = hero.getBoundingClientRect();
      hero.style.setProperty("--fx", (((ev.clientX - r.left) / r.width) * 100).toFixed(1) + "%");
      hero.style.setProperty("--fy", (((ev.clientY - r.top) / r.height) * 100).toFixed(1) + "%");
    });
  }

  /* ------------------------------------------------------------------- confeti */

  function confeti(origen) {
    if (quieto) return;
    const colores = ["#F18BC4", "#98B7FD", "#F9FF80", "#500711"];
    const r = origen.getBoundingClientRect();
    const capa = document.createElement("div");
    capa.className = "confeti";
    for (let i = 0; i < 34; i++) {
      const p = document.createElement("i");
      p.style.setProperty("--c", colores[i % colores.length]);
      p.style.setProperty("--x", (Math.random() * 2 - 1).toFixed(2));
      p.style.setProperty("--r", Math.round(Math.random() * 360) + "deg");
      p.style.setProperty("--d", (Math.random() * 0.25).toFixed(2) + "s");
      capa.appendChild(p);
    }
    capa.style.left = r.left + r.width / 2 + "px";
    capa.style.top = r.top + scrollY + "px";
    document.body.appendChild(capa);
    setTimeout(function () { capa.remove(); }, 2200);
  }

  /* -------------------------------------------------- la vía del plan de estudios */

  function ruta() {
    const via = document.querySelector(".ruta");
    if (!via) return;
    if (quieto) { via.style.setProperty("--avance", 1); return; }

    const pasos = via.querySelectorAll(".ruta-paso");

    /* Cada materia enciende su nodo al entrar en pantalla. Se marca el paso
       entero y no la tarjeta, porque el nodo y la flecha son hermanos suyos. */
    const obsPaso = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("dentro");
        obsPaso.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -45% 0px" });
    pasos.forEach(function (p) { obsPaso.observe(p); });

    /* El trazo avanza con el scroll: 0 cuando el primer nodo llega al centro de
       la pantalla, 1 cuando lo alcanza el último. Referenciarlo a los nodos y no
       a la caja entera evita que el trazo vaya adelantado respecto a ellos. */
    let pendiente = false;
    function pintar() {
      pendiente = false;
      if (!pasos.length) return;
      const centro = scrollY + innerHeight / 2;
      const primero = pasos[0].getBoundingClientRect();
      const ultimo = pasos[pasos.length - 1].getBoundingClientRect();
      const y0 = primero.top + scrollY + primero.height / 2;
      const y1 = ultimo.top + scrollY + ultimo.height / 2;
      const k = y1 > y0 ? (centro - y0) / (y1 - y0) : 1;
      via.style.setProperty("--avance", Math.min(1, Math.max(0, k)).toFixed(3));
    }
    addEventListener("scroll", function () {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(pintar);
    }, { passive: true });
    addEventListener("resize", pintar, { passive: true });
    pintar();
  }

  function iniciar() {
    prepararEntradas();
    ruta();
    titularesPorPalabra();
    montajePerfil();
    imanes();
    relieve();
    focoCursor();
    navActiva();
    progresoYCta();
    contadores();
    video();
    parallax();
    formulario();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
