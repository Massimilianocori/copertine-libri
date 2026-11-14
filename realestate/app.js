// Real Estate Exam Pass Rates: tema chiaro/scuro, tabelle delle scuole (ordine, ricerca, filtri), modulo delle correzioni.
// Le tabelle sono già complete nell'HTML (ordinate per numero di esami): senza JavaScript si leggono lo stesso.
// Regola dell'ordinamento per percentuale: prima le scuole con almeno SOGLIA esami, poi quelle sotto la soglia (riga di stacco),
// in fondo quelle senza esami. Una percentuale su pochi esami non viene mai messa in testa a una classifica.
(function () {
  if (typeof document === 'undefined') return;
  var b = document.querySelector('[data-tema]');
  if (b) b.addEventListener('click', function () {
    var r = document.documentElement, scuro = r.getAttribute('data-theme') === 'dark' || (!r.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = scuro ? 'light' : 'dark'; r.setAttribute('data-theme', t); try { localStorage.setItem('re-theme', t); } catch (e) {}
  });
  document.querySelectorAll('form[data-correzioni]').forEach(function (form) { form.addEventListener('submit', function (ev) { ev.preventDefault();
    var err = form.querySelector('[data-errore]'); err.hidden = true; if (!form.checkValidity()) { form.reportValidity(); return; }
    var bt = form.querySelector('button'); bt.disabled = true;
    fetch('/', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(new FormData(form)).toString()})
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; var ok = form.parentNode.querySelector('[data-ok]'); if (ok) ok.hidden = false; })
      .catch(function () { err.hidden = false; bt.disabled = false; });
  }); });

  document.querySelectorAll('[data-tabella]').forEach(function (box) {
    var tab = box.querySelector('table'), corpo = tab.tBodies[0], soglia = parseInt(box.getAttribute('data-soglia'), 10);
    var righe = Array.prototype.slice.call(corpo.querySelectorAll('tr[data-nome]'));
    var cerca = box.querySelector('[data-cerca]'), ordina = box.querySelector('[data-ordina]'), minimo = box.querySelector('[data-min]'), formato = box.querySelector('[data-formato]');
    var stato = box.querySelector('[data-stato]'), vuoto = box.querySelector('[data-vuoto]'), bottoni = Array.prototype.slice.call(tab.querySelectorAll('.ord'));
    var colonne = tab.tHead.rows[tab.tHead.rows.length - 1].cells.length, verso = 'giu';
    var stacco = document.createElement('tr'); stacco.className = 'stacco';
    stacco.innerHTML = '<td colspan="' + colonne + '">Fewer than ' + soglia + ' exams: too few to compare. One or two results move these percentages a lot.</td>';
    function num(tr, k) { return parseInt(tr.getAttribute('data-n-' + k), 10) || 0; }
    function tasso(tr, k) { var n = num(tr, k); return n ? (parseInt(tr.getAttribute('data-p-' + k), 10) || 0) / n : -1; }
    function agg() {
      var q = (cerca.value || '').trim().toLowerCase(), chiave = ordina.value, solo = minimo && minimo.checked, f = formato ? formato.value : '';
      var primaria = box.getAttribute('data-primaria'), perTasso = chiave.indexOf('r:') === 0, k = perTasso ? chiave.slice(2) : primaria, su = verso === 'su' ? -1 : 1;
      var viste = righe.filter(function (tr) {
        if (q && tr.getAttribute('data-nome').indexOf(q) < 0) return false;
        if (f && (' ' + tr.getAttribute('data-formati') + ' ').indexOf(' ' + f + ' ') < 0) return false;
        if (solo && num(tr, perTasso ? k : primaria) < soglia) return false;
        return true;
      });
      function gruppo(tr) { var n = num(tr, k); return n >= soglia ? 0 : n > 0 ? 1 : 2; }
      viste.sort(function (a, c) {
        if (chiave === 'nome') return su * a.getAttribute('data-nome').localeCompare(c.getAttribute('data-nome'));
        if (perTasso) return (gruppo(a) - gruppo(c)) || su * (tasso(c, k) - tasso(a, k)) || (num(c, k) - num(a, k)) || a.getAttribute('data-nome').localeCompare(c.getAttribute('data-nome'));
        return su * (num(c, primaria) - num(a, primaria)) || a.getAttribute('data-nome').localeCompare(c.getAttribute('data-nome'));
      });
      righe.forEach(function (tr) { if (tr.parentNode) tr.parentNode.removeChild(tr); });
      if (stacco.parentNode) stacco.parentNode.removeChild(stacco);
      var messo = false;
      viste.forEach(function (tr) {
        if (perTasso && !messo && gruppo(tr) > 0 && viste.length && gruppo(viste[0]) === 0) { corpo.appendChild(stacco); messo = true; }
        corpo.appendChild(tr);
      });
      vuoto.hidden = viste.length > 0;
      var testo = 'Showing ' + viste.length + ' of ' + righe.length + ' schools';
      if (perTasso) testo += ', highest pass rate first among schools with at least ' + soglia + ' exams; smaller samples are listed after them';
      else if (chiave === 'nome') testo += ', by name';
      else testo += ', most exams first';
      stato.textContent = testo + '.';
      bottoni.forEach(function (bt) { var on = bt.getAttribute('data-ord') === chiave; bt.setAttribute('aria-pressed', on ? 'true' : 'false'); bt.setAttribute('data-verso', on ? verso : 'giu'); });
    }
    bottoni.forEach(function (bt) { bt.addEventListener('click', function () {
      var c = bt.getAttribute('data-ord');
      if (ordina.value === c) verso = verso === 'giu' ? 'su' : 'giu'; else { ordina.value = c; verso = 'giu'; }
      agg();
    }); });
    cerca.addEventListener('input', agg);
    ordina.addEventListener('change', function () { verso = 'giu'; agg(); });
    if (minimo) minimo.addEventListener('change', agg);
    if (formato) formato.addEventListener('change', agg);
    box.querySelector('[data-strumenti]').hidden = false;
    agg();
  });
})();
