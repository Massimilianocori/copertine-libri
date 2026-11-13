function calcola(D, g, c) {
  var r = D.righe[g]; if (!r) return null;
  var v = r[c]; if (v === null || v === undefined) return null;
  var tetto = null;
  if (D.tetto2.indexOf(g) >= 0 && v >= D.tetti.lvl2 - 0.001) tetto = D.tetti.lvl2;
  if (D.tetto5.indexOf(g) >= 0 && v >= D.tetti.lvl5 - 0.001) tetto = D.tetti.lvl5;
  var m = tetto === null ? v : Math.min(v, tetto);
  var pr = null;
  for (var j = c + 1; j < r.length; j++) {
    if (r[j] !== null) { var mj = r[j]; if (D.tetto2.indexOf(g) >= 0) mj = Math.min(mj, D.tetti.lvl2); if (D.tetto5.indexOf(g) >= 0) mj = Math.min(mj, D.tetti.lvl5);
      if (mj > m + 0.001) { pr = {col: j, mese: mj, piu: Math.round((mj - m) * 100) / 100}; break; } }
  }
  return {tabella: v, mese: m, anno: Math.round(m * 12 * 100) / 100, tetto: tetto, prossimo: pr};
}
if (typeof module !== 'undefined') module.exports = {calcola: calcola};
(function () {
  if (typeof document === 'undefined') return;
  var b = document.querySelector('[data-tema]');
  if (b) b.addEventListener('click', function () {
    var r = document.documentElement, scuro = r.getAttribute('data-theme') === 'dark' || (!r.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = scuro ? 'light' : 'dark'; r.setAttribute('data-theme', t); try { localStorage.setItem('mp-theme', t); } catch (e) {}
  });
  document.querySelectorAll('form[data-correzioni]').forEach(function (form) { form.addEventListener('submit', function (ev) { ev.preventDefault();
    var err = form.querySelector('[data-errore]'); err.hidden = true; if (!form.checkValidity()) { form.reportValidity(); return; }
    var bt = form.querySelector('button'); bt.disabled = true;
    fetch('/', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(new FormData(form)).toString()})
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; var ok = form.parentNode.querySelector('[data-ok]'); if (ok) ok.hidden = false; })
      .catch(function () { err.hidden = false; bt.disabled = false; });
  }); });
  var box = document.querySelector('[data-calc]'); if (!box) return;
  var D = JSON.parse(document.getElementById('dati-paga').textContent);
  var sg = box.querySelector('select[name=g]'), sy = box.querySelector('select[name=y]'), out = box.querySelector('[data-out]');
  function soldi(x) { return '$' + x.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function leggiUrl() {
    var q = new URLSearchParams(location.search);
    if (q.get('g') && D.righe[q.get('g')]) sg.value = q.get('g');
    var y = q.get('y'); if (y !== null && D.slug_col.indexOf(y) >= 0) sy.value = String(D.slug_col.indexOf(y));
  }
  function aggiorna(scrivi) {
    var g = sg.value, c = +sy.value, nome = D.nomi[g], res = calcola(D, g, c), h = '';
    if (!res) {
      var prima = D.righe[g].findIndex(function (x) { return x !== null; });
      h = '<p class="vuoto"><strong>No rate in the 2026 table for ' + esc(nome) + ' with ' + esc(D.colonne[c].toLowerCase()) + ' years of service.</strong> The ' + esc(nome) +
        ' row of the official table starts at “' + esc(D.colonne[prima]) + '”' + (D.righe[g].slice(prima).some(function (x) { return x === null; }) ? ' and has gaps' : '') + '.</p>';
    } else {
      h = '<div class="tot"><div class="main"><span>Monthly basic pay</span><b>' + soldi(res.mese) + '</b></div><div><span>Per year (× 12)</span><b>' + soldi(res.anno) + '</b></div></div>';
      if (res.tetto !== null) h += '<p><span class="cap">At the monthly limit.</span> By law basic pay for this grade cannot go above ' + soldi(res.tetto) + ' a month in 2026; the table already stops there.</p>';
      h += res.prossimo ? '<p><strong>Next step in the table:</strong> “' + esc(D.colonne[res.prossimo.col]) + '” years, ' + soldi(res.prossimo.mese) + ' a month (+' + soldi(res.prossimo.piu) + ').</p>'
        : '<p><strong>Top of the ' + esc(nome) + ' table:</strong> no higher rate at longer service in 2026.</p>';
      h += '<p><a href="/' + D.pagine[g] + '/">Full ' + esc(nome) + ' pay table →</a></p>';
    }
    out.innerHTML = h;
    if (scrivi && history.replaceState) { var q = new URLSearchParams(); q.set('g', g); q.set('y', D.slug_col[c]); history.replaceState(null, '', location.pathname + '?' + q.toString()); }
  }
  leggiUrl(); aggiorna(false);
  sg.addEventListener('change', function () { aggiorna(true); }); sy.addEventListener('change', function () { aggiorna(true); });
})();
