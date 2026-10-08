/* ============================================================
   Rispondoio — form di attivazione + calcolatore chiamate perse.
   Condiviso da index.html e dalle pagine per settore (per/…).

   Form: invio AJAX a Netlify Forms (form "attivazione"). Se il sito non è
   su Netlify (file locale, GitHub Pages…) l'invio fallisce e il modulo
   prepara un'email già compilata: la richiesta non si perde mai.

   API: window.RispondoioLead.open({ piano, fatturazione, settore })
   ============================================================ */
(function () {
  "use strict";

  var EMAIL = "io@rispondoio.net";
  var PREZZO_MINIMO = 79; // canone mensile del piano Basic (trimestrale), IVA esclusa

  function eur(n) {
    return "€ " + Math.round(n).toLocaleString("it-IT");
  }

  /* ---------------- Modale attivazione ---------------- */
  var overlay = document.getElementById("leadModal");
  var form = overlay ? overlay.querySelector("form.lead-form") : null;
  var lastFocus = null;

  function step(name) {
    overlay.querySelectorAll("[data-lead-step]").forEach(function (el) {
      el.hidden = el.getAttribute("data-lead-step") !== name;
    });
  }

  function setSelect(name, value) {
    if (!value) return;
    var sel = form.elements[name];
    if (!sel) return;
    for (var i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === value || sel.options[i].text === value) {
        sel.selectedIndex = i;
        return;
      }
    }
  }

  function open(opts) {
    if (!overlay) return;
    opts = opts || {};
    lastFocus = document.activeElement;
    step("form");
    setSelect("piano", opts.piano);
    setSelect("fatturazione", opts.fatturazione);
    setSelect("settore", opts.settore || document.body.getAttribute("data-settore"));
    form.elements.pagina.value = location.pathname + (opts.origine ? " · " + opts.origine : "");
    overlay.hidden = false;
    requestAnimationFrame(function () { overlay.classList.add("open"); });
    document.body.style.overflow = "hidden";
    setTimeout(function () {
      var first = form.elements.attivita;
      if (first) first.focus({ preventScroll: true });
    }, 60);
  }

  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.classList.remove("open");
    document.body.style.overflow = "";
    setTimeout(function () { overlay.hidden = true; }, 250);
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  function mailtoFrom(data) {
    var righe = [
      "Richiesta di attivazione Rispondoio",
      "",
      "Attività: " + (data.get("attivita") || ""),
      "Nome: " + (data.get("nome") || ""),
      "Settore: " + (data.get("settore") || ""),
      "Telefono: " + (data.get("telefono") || ""),
      "Email: " + (data.get("email") || ""),
      "Piano: " + (data.get("piano") || "") + " · " + (data.get("fatturazione") || ""),
      "Città: " + (data.get("citta") || ""),
      "Note: " + (data.get("note") || ""),
      "",
      "Pagina: " + (data.get("pagina") || "")
    ];
    return "mailto:" + EMAIL +
      "?subject=" + encodeURIComponent(data.get("subject") || "Richiesta Rispondoio") +
      "&body=" + encodeURIComponent(righe.join("\n"));
  }

  if (overlay && form) {
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay || e.target.closest("[data-lead-close]")) close();
    });
    addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      form.elements.subject.value =
        "Rispondoio · " + form.elements.piano.value + " · " + form.elements.attivita.value.trim();
      var data = new FormData(form);
      var btn = form.querySelector('[type="submit"]');
      btn.disabled = true;
      btn.textContent = "Invio in corso…";

      fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(data).toString()
      })
        .then(function (res) {
          if (!res.ok) throw new Error("HTTP " + res.status);
          form.reset();
          step("ok");
        })
        .catch(function () {
          overlay.querySelector("[data-lead-mailto]").href = mailtoFrom(data);
          step("mail");
        })
        .then(function () {
          btn.disabled = false;
          btn.textContent = "Invia la richiesta";
        });
    });
  }

  // Ogni elemento .js-lead apre il modulo con il piano indicato in data-plan.
  document.addEventListener("click", function (e) {
    var t = e.target.closest(".js-lead");
    if (!t) return;
    e.preventDefault();
    open({ piano: t.getAttribute("data-plan"), origine: t.getAttribute("data-origine") });
  });

  // Link diretto: …#attiva apre il modulo all'arrivo sulla pagina.
  if (overlay && location.hash === "#attiva") open({ origine: "link #attiva" });

  window.RispondoioLead = { open: open, close: close };

  /* ---------------- Calcolatore chiamate perse ---------------- */
  document.querySelectorAll("[data-roi]").forEach(function (box) {
    var inp = {
      perse: box.querySelector('[data-in="perse"]'),
      conv: box.querySelector('[data-in="conv"]'),
      valore: box.querySelector('[data-in="valore"]')
    };
    var out = {};
    ["perse", "conv", "mese", "anno", "cmp"].forEach(function (k) {
      out[k] = box.querySelector('[data-out="' + k + '"]');
    });

    // Valori iniziali dal data-attribute (diversi per ogni settore)
    ["perse", "conv", "valore"].forEach(function (k) {
      var v = box.getAttribute("data-" + k);
      if (v && inp[k]) inp[k].value = v;
    });

    function calc() {
      var perse = Math.max(0, +inp.perse.value || 0);
      var conv = Math.max(0, +inp.conv.value || 0) / 100;
      var valore = Math.max(0, +inp.valore.value || 0);
      var mese = perse * 4.33 * conv * valore;
      var arrotonda = function (n) { return Math.round(n / 10) * 10; };
      out.perse.textContent = perse;
      out.conv.textContent = Math.round(conv * 100) + "%";
      out.mese.textContent = eur(arrotonda(mese));
      out.anno.textContent = "circa " + eur(arrotonda(mese * 12)) + " l'anno";
      if (valore > 0) {
        var n = Math.max(1, Math.ceil(PREZZO_MINIMO / valore));
        out.cmp.innerHTML = "Rispondoio parte da <b>" + eur(PREZZO_MINIMO) + " al mese</b>: " +
          (n === 1 ? "si ripaga con <b>un solo cliente</b> recuperato."
                   : "si ripaga con <b>" + n + " clienti</b> recuperati.");
      }
    }
    Object.keys(inp).forEach(function (k) {
      if (inp[k]) inp[k].addEventListener("input", calc);
    });
    calc();
  });
})();
