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
function vaCombina(D, lista) {
  if (!Array.isArray(lista) || !lista.length || lista.length > 20) return {errore: 'lista'};
  for (var i = 0; i < lista.length; i++) { var x = lista[i]; if (typeof x !== 'number' || Math.floor(x) !== x || x < 10 || x > 100 || x % 10) return {errore: 'grado'}; }
  var o = lista.slice().sort(function (a, b) { return b - a; }), v = o[0], passi = [];
  for (var j = 1; j < o.length; j++) { if (v >= 95) break; var b = o[j], c = (v === 10 && b === 10) ? 19 : D.T[String(v)][b / 10 - 1]; passi.push([v, b, c]); v = c; }
  return {ordinati: o, passi: passi, valore: v, finale: Math.min(100, Math.floor((v + 5) / 10) * 10)};
}
function vaPaga(D, g, coniuge, aa, genitori, u18, scuola) {
  function ok(x, lo, hi) { return typeof x === 'number' && Math.floor(x) === x && x >= lo && x <= hi; }
  if (!ok(g, 10, 100) || g % 10) return {errore: 'grado'};
  if (!(ok(coniuge, 0, 1) && ok(aa, 0, 1) && ok(genitori, 0, 2) && ok(u18, 0, 12) && ok(scuola, 0, 12))) return {errore: 'dati'};
  var sg = String(g);
  if (g < 30) return {cent: D.base[sg], anno: D.base[sg] * 12, chiave: 'alone', base: D.base[sg], extra: [], senza_familiari: (coniuge || genitori || u18 || scuola) ? 1 : 0};
  if (scuola && !u18) return {errore: 'scuola'};
  var k = u18 ? ((coniuge ? 'child_spouse' : 'child') + (genitori ? '_p' + genitori : '')) : (coniuge ? 'spouse' + (genitori ? '_p' + genitori : '') : (genitori ? 'p' + genitori : 'alone'));
  var base = D.righe[k][sg], extra = [], tot = base;
  if (u18 > 1) extra.push(['child_u18', u18 - 1, D.agg.child_u18[sg]]);
  if (scuola) extra.push(['child_school', scuola, D.agg.child_school[sg]]);
  if (coniuge && aa) extra.push(['spouse_aa', 1, D.agg.spouse_aa[sg]]);
  extra.forEach(function (e) { tot += e[1] * e[2]; });
  return {cent: tot, anno: tot * 12, chiave: k, base: base, extra: extra, senza_familiari: 0};
}
if (typeof module !== 'undefined') module.exports = {calcola: calcola, viaggio: viaggio, miglia: miglia, vaCombina: vaCombina, vaPaga: vaPaga};
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
  var vb = document.querySelector('[data-va]');
  if (vb) {
    var DV = JSON.parse(document.getElementById('dati-va').textContent);
    var vg = vb.querySelector('select[name=g]'), vl = vb.querySelector('input[name=lista]'), vs = vb.querySelector('select[name=s]'), vp = vb.querySelector('select[name=p]'),
      vu = vb.querySelector('input[name=u]'), vc = vb.querySelector('input[name=c]'), vo = vb.querySelector('[data-out]');
    var NOMI = {alone: 'Veteran alone', spouse: 'Veteran with spouse', spouse_p1: 'Veteran with spouse and 1 parent', spouse_p2: 'Veteran with spouse and 2 parents', p1: 'Veteran with 1 parent', p2: 'Veteran with 2 parents',
      child: 'Veteran with 1 child', child_spouse: 'Veteran with spouse and 1 child', child_spouse_p1: 'Veteran with spouse, 1 child and 1 parent', child_spouse_p2: 'Veteran with spouse, 1 child and 2 parents',
      child_p1: 'Veteran with 1 child and 1 parent', child_p2: 'Veteran with 1 child and 2 parents'};
    var AGG = {child_u18: 'additional child under 18', child_school: 'child over 18 in school', spouse_aa: 'spouse receiving Aid and Attendance'};
    var cu = function (c) { return usd(c / 100); };
    var intero = function (el) { var t = el.value.trim(); if (t === '') return 0; return /^\d{1,2}$/.test(t) ? +t : -1; };
    var qv = new URLSearchParams(location.search);
    if (qv.get('g') && DV.base[qv.get('g')]) vg.value = qv.get('g');
    if (qv.get('r')) vl.value = qv.get('r').slice(0, 80);
    if (/^[012]$/.test(qv.get('s') || '')) vs.value = qv.get('s'); if (/^[012]$/.test(qv.get('p') || '')) vp.value = qv.get('p');
    if (/^\d{1,2}$/.test(qv.get('u') || '')) vu.value = qv.get('u'); if (/^\d{1,2}$/.test(qv.get('c') || '')) vc.value = qv.get('c');
    var vaAgg = function (scrivi) {
      var h = '', g = +vg.value, testo = vl.value.trim(), comb = null;
      if (testo !== '') {
        var parti = testo.split(/[\s,;+%]+/).filter(function (x) { return x !== ''; }), nums = parti.map(function (x) { return /^\d{1,3}$/.test(x) ? +x : NaN; });
        comb = vaCombina(DV, nums);
        if (comb.errore) { vo.innerHTML = '<p class="vuoto"><strong>Enter the single ratings as multiples of 10 between 10 and 100, separated by commas, for example 50, 30, 10.</strong> Or clear the field and pick the combined rating.</p>'; return; }
        g = comb.finale;
      }
      if (g < 10) { vo.innerHTML = '<p class="vuoto"><strong>These ratings combine to less than 10%.</strong></p>'; return; }
      var s = +vs.value, r = vaPaga(DV, g, s > 0 ? 1 : 0, s === 2 ? 1 : 0, +vp.value, intero(vu), intero(vc));
      if (r.errore === 'scuola') h = '<p class="vuoto"><strong>VA’s table lists the amount for a child over 18 in school only as an addition for a further child.</strong> We do not calculate a household whose only children are over 18 and in school: VA can tell you that amount.</p>';
      else if (r.errore) h = '<p class="vuoto"><strong>Enter whole numbers from 0 to 12 for the children.</strong></p>';
      else {
        h = '<div class="tot"><div class="main"><span>Monthly payment at ' + g + '%, ' + DV.anno + ' rates</span><b>' + cu(r.cent) + '</b></div><div><span>Per year (× 12)</span><b>' + cu(r.anno) + '</b></div></div>';
        if (comb) {
          h += '<p><strong>Combined rating: ' + comb.finale + '%.</strong> ' + (comb.passi.length ? 'Table I, in order of severity:' : 'One rating, nothing to combine.') + '</p>';
          if (comb.passi.length) { h += '<ol class="passi">'; comb.passi.forEach(function (p) { h += '<li>' + p[0] + ' and ' + p[1] + ' → ' + p[2] + '</li>'; });
            h += '<li>' + comb.valore + (comb.valore >= 95 && comb.passi.length < comb.ordinati.length - 1 ? ' is already 95 or more' : '') + ' → converted to ' + comb.finale + '%</li></ol>'; }
        }
        if (g < 30) h += '<p>' + (r.senza_familiari ? '<strong>Dependents do not change the rate at ' + g + '%.</strong> ' : '') + 'At 10% and 20% VA pays one rate, with or without dependents.</p>';
        else {
          h += '<p><strong>Basic rate:</strong> ' + escp(NOMI[r.chiave]) + ', ' + cu(r.base) + '.</p>';
          if (r.extra.length) { h += '<ol class="passi">'; r.extra.forEach(function (e) { h += '<li>+ ' + (e[1] > 1 ? e[1] + ' × ' : '') + cu(e[2]) + ' ' + AGG[e[0]] + '</li>'; }); h += '</ol>'; }
        }
        if (DV.pagine[String(g)] && location.pathname !== '/' + DV.pagine[String(g)]) h += '<p><a href="/' + DV.pagine[String(g)] + '">All ' + g + '% rates →</a></p>';
      }
      vo.innerHTML = h;
      if (scrivi && history.replaceState) { var q = new URLSearchParams(); if (testo !== '') q.set('r', testo); else q.set('g', vg.value); q.set('s', vs.value); q.set('p', vp.value); q.set('u', String(intero(vu))); q.set('c', String(intero(vc)));
        history.replaceState(null, '', location.pathname + '?' + q.toString()); }
    };
    vaAgg(false);
    [vg, vl, vs, vp, vu, vc].forEach(function (el) { el.addEventListener('change', function () { vaAgg(true); }); el.addEventListener('input', function () { vaAgg(true); }); });
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
