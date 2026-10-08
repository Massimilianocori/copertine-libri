/* BandiChiari — ricerca bandi + modulo di iscrizione */
(function () {
  "use strict";

  /* ---------- Ricerca: filtra le card già presenti nella pagina ---------- */
  var finder = document.querySelector("[data-finder]");
  if (finder) {
    var sel = {
      regione: finder.querySelector('[name="f-regione"]'),
      finanzia: finder.querySelector('[name="f-finanzia"]'),
      benef: finder.querySelector('[name="f-benef"]')
    };
    var cards = Array.prototype.slice.call(finder.querySelectorAll(".card"));
    var count = finder.querySelector("[data-count]");
    var empty = finder.querySelector("[data-empty]");

    var filtra = function () {
      var r = sel.regione.value, f = sel.finanzia.value, b = sel.benef.value, n = 0;
      cards.forEach(function (c) {
        var reg = c.getAttribute("data-regioni").split("|");
        var ok = (!r || reg.indexOf("tutte") > -1 || reg.indexOf(r) > -1) &&
                 (!f || c.getAttribute("data-finanzia").split("|").indexOf(f) > -1) &&
                 (!b || c.getAttribute("data-benef").split("|").indexOf(b) > -1);
        c.hidden = !ok;
        if (ok) n++;
      });
      count.innerHTML = "<b>" + n + "</b> " + (n === 1 ? "bando trovato" : "bandi trovati") +
        (r ? " per " + r : "") + ".";
      empty.hidden = n > 0;
      try { localStorage.setItem("bc-filtri", JSON.stringify({ r: r, f: f, b: b })); } catch (e) {}
    };
    try {
      var salvati = JSON.parse(localStorage.getItem("bc-filtri") || "null");
      if (salvati && !finder.hasAttribute("data-fisso")) {
        sel.regione.value = salvati.r || ""; sel.finanzia.value = salvati.f || ""; sel.benef.value = salvati.b || "";
      }
    } catch (e) {}
    Object.keys(sel).forEach(function (k) { sel[k].addEventListener("change", filtra); });
    filtra();
  }

  /* ---------- Moduli (Netlify Forms; piano Studio → Stripe) ---------- */
  var regioneUrl = new URLSearchParams(location.search).get("regione");
  document.querySelectorAll("form[name=iscrizione], form[name=studio]").forEach(function (form) {
    var box = form.closest("[data-form-box]");
    // ?regione=Lombardia (dai link delle pagine regionali) precompila la regione
    if (regioneUrl && form.elements.regione) form.elements.regione.value = regioneUrl;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var data = new FormData(form);
      var btn = form.querySelector('[type="submit"]');
      var testo = btn.textContent;
      btn.disabled = true; btn.textContent = "Invio in corso…";
      fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(data).toString()
      }).then(function (res) {
        if (!res.ok) throw new Error(res.status);
        var link = data.get("piano") && form.getAttribute("data-stripe-" + data.get("piano"));
        if (link) {
          location.href = link + (link.indexOf("?") > -1 ? "&" : "?") +
            "prefilled_email=" + encodeURIComponent(data.get("email"));
          return;
        }
        box.querySelector("[data-step=form]").hidden = true;
        box.querySelector("[data-step=ok]").hidden = false;
      }).catch(function () {
        btn.disabled = false; btn.textContent = testo;
        box.querySelector("[data-errore]").hidden = false;
      });
    });
  });
})();
