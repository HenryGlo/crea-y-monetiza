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
        (function paso(t) {
          const k = Math.min((t - t0) / 900, 1);
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
      } catch (err) {
        msg.className = "form-msg err";
        msg.textContent = "No pudimos enviar tu registro. Vuelve a intentarlo en un momento.";
      } finally {
        btn.disabled = false;
        btn.textContent = textoBtn;
      }
    });
  }

  function iniciar() {
    prepararEntradas();
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
