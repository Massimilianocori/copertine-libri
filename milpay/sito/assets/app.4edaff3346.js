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
function viaggio(D, k, da, a) {
  function leggi(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); if (!m) return null; var t = Date.UTC(+m[1], +m[2] - 1, +m[3]);
    var d = new Date(t); return (d.getUTCFullYear() === +m[1] && d.getUTCMonth() === +m[2] - 1 && d.getUTCDate() === +m[3]) ? t : null; }
  var x = leggi(da), y = leggi(a); if (x === null || y === null) return {errore: 'data'};
  if (y < x) return {errore: 'ordine'};
  var n = Math.round((y - x) / 86400000) + 1; if (n > 183) return {errore: 'lungo'};
  var righe = [], tl = 0, tm = 0;
  for (var i = 0; i < n; i++) {
    var d = new Date(x + i * 86400000), mo = d.getUTCMonth() + 1, fy = String(mo >= 10 ? d.getUTCFullYear() + 1 : d.getUTCFullYear());
    var iso = d.toISOString().slice(0, 10), F = D.fy[fy];
    if (!F) return {errore: 'fuori', data: iso};
    var r = k === 'std' ? F.std : F.loc[k];
    if (!r) return {errore: 'non_listata', fy: fy, data: iso};
    var q = (i === 0 || i === n - 1) ? 0.75 : 1, m = r[1] * q, lo = i < n - 1 ? r[0][(mo + 2) % 12] : 0;
    righe.push({data: iso, fy: fy, alloggio: lo, mie: m, quota: q}); tl += lo; tm += m;
  }
  return {giorni: n, notti: n - 1, alloggio: tl, mie: tm, totale: tl + tm, righe: righe};
}
function miglia(D, giorno, scopo, mi) {
  var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(giorno || ''); mi = parseFloat(mi);
  if (!m || isNaN(mi)) return {errore: 'dati'};
  if (!(mi > 0 && mi <= 100000)) return {errore: 'miglia'};
  var p = null; for (var i = 0; i < D.periodi.length; i++) if (D.periodi[i].dal <= giorno && giorno <= D.periodi[i].al) p = D.periodi[i];
  if (!p) return {errore: 'fuori'};
  var r = p.tariffe[scopo]; if (r === undefined) return {errore: 'scopo'};
  var t = Math.floor(mi * 10 + 0.5), c = Math.floor((t * r + 50) / 100);
  return {tariffa: r / 10, decimi: t, centesimi: c, importo: c / 100, dal: p.dal, al: p.al};
}
if (typeof module !== 'undefined') module.exports = {calcola: calcola, viaggio: viaggio, miglia: miglia};
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
  function usd(x) { return '$' + x.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
  function escp(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  var MESI = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function giorno(iso) { var p = iso.split('-'); return MESI[+p[1] - 1] + ' ' + (+p[2]) + ', ' + p[0]; }
  var pd = document.querySelector('[data-pd]');
  if (pd) {
    var DP = JSON.parse(document.getElementById('dati-pd').textContent);
    var sl = pd.querySelector('select[name=l]'), da = pd.querySelector('input[name=da]'), a = pd.querySelector('input[name=a]'), op = pd.querySelector('[data-out]');
    var q0 = new URLSearchParams(location.search);
    if (q0.get('l') && (q0.get('l') === 'std' || DP.nomi[q0.get('l')])) sl.value = q0.get('l');
    if (q0.get('da')) da.value = q0.get('da'); if (q0.get('a')) a.value = q0.get('a');
    var pdAgg = function (scrivi) {
      var r = viaggio(DP, sl.value, da.value, a.value), h = '';
      if (r.errore) {
        var msg = {data: 'Enter both dates.', ordine: 'The last day is before the first day.', lungo: 'This calculator handles trips of up to 183 days.',
          fuori: 'We have GSA rates for October 1, 2025 to September 30, 2027 only (FY 2026 and FY 2027): ' + (r.data ? giorno(r.data) : '') + ' is outside.',
          non_listata: escp(DP.nomi[sl.value] || '') + ' is not listed as a separate GSA area in FY ' + r.fy + ' (from ' + (r.data ? giorno(r.data) : '') + '). For those dates check the county, or use the standard rate.'}[r.errore];
        h = '<p class="vuoto"><strong>' + msg + '</strong></p>';
      } else {
        h = '<div class="tot"><div class="main"><span>Maximum per diem for the trip</span><b>' + usd(r.totale) + '</b></div><div><span>Lodging, ' + r.notti + ' night' + (r.notti === 1 ? '' : 's') + ' (maximum)</span><b>' + usd(r.alloggio) +
          '</b></div><div><span>M&amp;IE, ' + r.giorni + ' day' + (r.giorni === 1 ? '' : 's') + '</span><b>' + usd(r.mie) + '</b></div></div>';
        if (r.giorni === 1) h += '<p>Same-day trip: no lodging, 75% of M&amp;IE, which GSA allows for one-day travel of more than 12 hours.</p>';
        h += '<div class="giorni-box"><table class="giorni"><thead><tr><th>Day</th><th>Lodging max</th><th>M&amp;IE</th></tr></thead><tbody>';
        r.righe.forEach(function (x) { h += '<tr><td>' + giorno(x.data) + ' <small>FY ' + x.fy + '</small></td><td>' + (x.alloggio ? usd(x.alloggio) : '–') + '</td><td>' + usd(x.mie) + (x.quota < 1 ? ' <small>(75%)</small>' : '') + '</td></tr>'; });
        h += '</tbody></table></div>';
        if (DP.pagine[sl.value]) h += '<p><a href="/' + DP.pagine[sl.value] + '">' + (sl.value === 'std' ? 'How per diem works →' : 'All rates for ' + escp(DP.nomi[sl.value]) + ' →') + '</a></p>';
      }
      op.innerHTML = h;
      if (scrivi && history.replaceState) { var q = new URLSearchParams(); q.set('l', sl.value); q.set('da', da.value); q.set('a', a.value); history.replaceState(null, '', location.pathname + '?' + q.toString()); }
    };
    pdAgg(false);
    [sl, da, a].forEach(function (el) { el.addEventListener('change', function () { pdAgg(true); }); el.addEventListener('input', function () { pdAgg(true); }); });
  }
  var km = document.querySelector('[data-km]');
  if (km) {
    var DK = JSON.parse(document.getElementById('dati-km').textContent);
    var kd = km.querySelector('input[name=data]'), ks = km.querySelector('select[name=scopo]'), kmi = km.querySelector('input[name=miglia]'), ko = km.querySelector('[data-out]');
    var q1 = new URLSearchParams(location.search);
    if (q1.get('data')) kd.value = q1.get('data'); if (q1.get('scopo') && DK.periodi[0].tariffe[q1.get('scopo')] !== undefined) ks.value = q1.get('scopo'); if (q1.get('miglia')) kmi.value = q1.get('miglia');
    var kmAgg = function (scrivi) {
      var r = miglia(DK, kd.value, ks.value, kmi.value), h;
      if (r.errore) h = '<p class="vuoto"><strong>' + {dati: 'Enter a date and a number of miles.', miglia: 'Enter between 0.1 and 100,000 miles.', fuori: 'We have the 2026 rates only (January 1 to December 31, 2026).', scopo: 'Choose a rate.'}[r.errore] + '</strong></p>';
      else h = '<div class="tot"><div class="main"><span>Amount</span><b>' + usd(r.importo) + '</b></div><div><span>Rate per mile</span><b>' + r.tariffa + '¢</b></div></div>' +
        '<p>' + (r.decimi / 10) + ' miles × ' + r.tariffa + '¢, rate in force ' + giorno(r.dal) + ' to ' + giorno(r.al) + '.</p>';
      ko.innerHTML = h;
      if (scrivi && history.replaceState) { var q = new URLSearchParams(); q.set('data', kd.value); q.set('scopo', ks.value); q.set('miglia', kmi.value); history.replaceState(null, '', location.pathname + '?' + q.toString()); }
    };
    kmAgg(false);
    [kd, ks, kmi].forEach(function (el) { el.addEventListener('change', function () { kmAgg(true); }); el.addEventListener('input', function () { kmAgg(true); }); });
  }
  var ce = document.querySelector('[data-cerca]');
  if (ce) {
    var qi = ce.querySelector('input[name=q]'), conta = ce.querySelector('[data-conta]'), voci = document.querySelectorAll('[data-elenco] li'), base = conta.textContent;
    var cerca = function () {
      var s = qi.value.trim().toLowerCase(), n = 0;
      voci.forEach(function (li) { var ok = s.length >= 2 && li.getAttribute('data-t').indexOf(s) >= 0 && n < 40; li.hidden = !ok; if (ok) n++; });
      conta.textContent = s.length < 2 ? base : (n ? n + (n === 40 ? '+' : '') + ' area' + (n === 1 ? '' : 's') + ' found.' : 'No GSA area matches: if the county is not listed either, the standard rate applies.');
    };
    qi.addEventListener('input', cerca);
  }
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
