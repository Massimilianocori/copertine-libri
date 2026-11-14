// US Paycheck Calculator: conti in centesimi interi (nessun numero con la virgola), uguali a motore.py.
// busta(R, i)  -> ritenute del dipendente per un periodo di paga
// datore(R, stato, lordo, ytd, aliquota) -> imposte a carico del datore di lavoro sulla stessa paga
// R = dati-regole (JSON nella pagina): importi in centesimi, aliquote in millesimi di punto percentuale (6,2 % = 6200).
function idiv(a, b) { return (a - (a % b)) / b; }
function mezzo(num, den) { return num <= 0 ? 0 : idiv(2 * num + den, 2 * den); }   // num/den arrotondato al più vicino, .5 in su
function quota(x, rate) { return mezzo(x * rate, 100000); }                          // x centesimi × aliquota
function tra(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
function riga(tab, x) { var r = tab[0]; for (var k = 1; k < tab.length; k++) if (x >= tab[k][0]) r = tab[k]; return r; }

function federale(R, i) {
  var P = R.P[i.periodo];
  var g1 = i.step2 ? 0 : (i.fs === 'mfj' ? R.g1.mfj : R.g1.altro);
  var adj = Math.max(0, i.lordo * P + (i.a4 || 0) - (i.b4 || 0) - g1);            // righe 1c-1i
  var t = (i.step2 ? R.fed.step2 : R.fed.std)[i.fs], r = riga(t, adj);
  var anno100 = r[1] * 100 + (adj - r[0]) * r[2];                                  // riga 2g, in centesimi di centesimo
  var h2 = mezzo(anno100, 100 * P), b3 = mezzo(i.step3 || 0, P);                   // righe 2h e 3b, ognuna al centesimo come nel foglio
  return {adj: adj, da: r[0], base: r[1], pct: r[2], tentativo: h2, credito: b3, ritenuta: Math.max(0, h2 - b3) + (i.c4 || 0)};  // righe 3c e 4b
}

function statale(R, i) {
  var S = R.st[i.stato].it, o = {imposta: 0};
  if (!S) return o;
  if (S.m === 'il') {
    o.esenzioni = mezzo(((i.il1 || 0) * S.l1 + (i.il2 || 0) * S.l2), R.P[i.periodo]);
    o.imponibile = Math.max(0, i.lordo - o.esenzioni);
    o.imposta = quota(o.imponibile, S.r);
  } else if (S.m === 'nc') {
    var p = S.p[i.periodo][i.nc_fs === 'hoh' ? 'hoh' : 'single'];
    o.deduzione = p[0]; o.esenzioni = (i.nc_all || 0) * p[1];
    o.imponibile = Math.max(0, i.lordo - p[0] - o.esenzioni);
    o.imposta = mezzo(o.imponibile * S.r, 10000000) * 100;                        // al dollaro intero
  } else if (S.m === 'ca') {
    var fs = i.ca_fs || 'single', reg = i.ca_reg || 0, est = i.ca_est || 0;
    var col = fs === 'married' ? (reg >= 2 ? 'married2' : 'married01') : fs;
    o.soglia = S.es[i.periodo][col];
    if (i.lordo <= o.soglia) { o.esente = true; return o; }
    var ed = S.ed[i.periodo];
    o.stimate = est <= 0 ? 0 : (est <= 10 ? ed[est - 1] : est * ed[0]);
    o.deduzione = S.sd[i.periodo][col];
    o.imponibile = Math.max(0, i.lordo - o.stimate - o.deduzione);
    var t = S.tab[i.periodo][fs], r = t[0];
    for (var k = 1; k < t.length; k++) if (o.imponibile > t[k][0]) r = t[k];
    o.calcolata = r[1] + quota(o.imponibile - r[0], r[2]);
    var cr = S.cr[i.periodo];
    o.credito = reg <= 10 ? cr[reg] : reg * cr[1];
    o.imposta = Math.max(0, o.calcolata - o.credito);
  }
  return o;
}

function busta(R, i) {
  var ytd = i.ytd || 0, F = R.fica, f = federale(R, i), s = statale(R, i);
  var o = {lordo: i.lordo, fed: f.ritenuta, fedDettaglio: f, statoDettaglio: s, stato: s.imposta};
  o.ssImponibile = tra(F.ssBase - ytd, 0, i.lordo);
  o.ss = quota(o.ssImponibile, F.ss);
  o.medicare = quota(i.lordo, F.med);
  o.addlImponibile = Math.max(0, ytd + i.lordo - F.addlSoglia) - Math.max(0, ytd - F.addlSoglia);
  o.addl = quota(o.addlImponibile, F.addl);
  o.sdi = R.st[i.stato].sdi ? quota(i.lordo, R.st[i.stato].sdi) : 0;
  o.totale = o.fed + o.ss + o.medicare + o.addl + o.stato + o.sdi;
  o.netto = i.lordo - o.totale;
  return o;
}

function datore(R, stato, lordo, ytd, aliquota) {
  ytd = ytd || 0;
  var S = R.st[stato], F = R.fica, o = {lordo: lordo};
  o.ss = quota(tra(F.ssBase - ytd, 0, lordo), F.ss);
  o.medicare = quota(lordo, F.med);
  o.futaAliquota = R.futa.netta + (R.futa.rid[stato] || 0);
  o.futa = quota(tra(R.futa.base - ytd, 0, lordo), o.futaAliquota);
  o.sutaAliquota = (aliquota === undefined || aliquota === null) ? S.suta.nuovo : aliquota;
  o.suta = quota(tra(S.suta.base - ytd, 0, lordo), o.sutaAliquota);
  o.ett = S.ett ? quota(tra(S.ettBase - ytd, 0, lordo), S.ett) : 0;
  o.totale = o.ss + o.medicare + o.futa + o.suta + o.ett;
  o.costo = lordo + o.totale;
  return o;
}

// "1,234.56" -> centesimi interi; null se non è un importo valido
function centesimi(s) {
  s = String(s === undefined || s === null ? '' : s).replace(/[$,\s]/g, '');
  if (s === '') return 0;
  if (!/^\d{1,9}(\.\d{0,2})?$/.test(s)) return null;
  var p = s.split('.');
  return parseInt(p[0], 10) * 100 + (p[1] ? parseInt((p[1] + '0').slice(0, 2), 10) : 0);
}
// lordo del periodo da: importo per periodo, stipendio annuo, oppure paga oraria × ore del periodo
function lordoPeriodo(R, tipo, periodo, importo, ore) {
  if (importo === null) return null;
  if (tipo === 'anno') return mezzo(importo, R.P[periodo]);
  if (tipo === 'ora') { if (ore === null) return null; return mezzo(importo * ore, 100); }
  return importo;
}
if (typeof module !== 'undefined') module.exports = {busta: busta, datore: datore, centesimi: centesimi, lordoPeriodo: lordoPeriodo, mezzo: mezzo};

(function () {
  if (typeof document === 'undefined') return;
  var b = document.querySelector('[data-tema]');
  if (b) b.addEventListener('click', function () {
    var r = document.documentElement, scuro = r.getAttribute('data-theme') === 'dark' || (!r.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = scuro ? 'light' : 'dark'; r.setAttribute('data-theme', t); try { localStorage.setItem('pc-theme', t); } catch (e) {}
  });
  document.querySelectorAll('form[data-correzioni]').forEach(function (form) { form.addEventListener('submit', function (ev) { ev.preventDefault();
    var err = form.querySelector('[data-errore]'); err.hidden = true; if (!form.checkValidity()) { form.reportValidity(); return; }
    var bt = form.querySelector('button'); bt.disabled = true;
    fetch('/', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(new FormData(form)).toString()})
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; var ok = form.parentNode.querySelector('[data-ok]'); if (ok) ok.hidden = false; })
      .catch(function () { err.hidden = false; bt.disabled = false; });
  }); });
  var el = document.getElementById('dati-regole'); if (!el) return;
  var R = JSON.parse(el.textContent);
  function usd(c) { var neg = c < 0; c = Math.abs(c); var d = idiv(c, 100), r = c % 100; return (neg ? '−$' : '$') + d.toLocaleString('en-US') + '.' + (r < 10 ? '0' : '') + r; }
  function pct(m) { return (m / 1000).toFixed(3).replace(/0+$/, '').replace(/\.$/, '') + '%'; }
  function intero(v) { v = String(v || '').trim(); if (v === '') return 0; return /^\d{1,3}$/.test(v) ? parseInt(v, 10) : null; }
  var NOMI_P = {weekly: 'weekly', biweekly: 'biweekly', semimonthly: 'semimonthly', monthly: 'monthly'};

  document.querySelectorAll('[data-busta]').forEach(function (box) {
    var f = box.querySelector('form'), out = box.querySelector('[data-out]');
    function v(n) { return f.elements[n] ? f.elements[n].value : ''; }
    function agg() {
      var st = v('stato'), per = v('periodo'), tipo = v('tipo');
      box.querySelectorAll('[data-solo]').forEach(function (x) { x.hidden = x.getAttribute('data-solo').split(' ').indexOf(st) < 0; });
      box.querySelectorAll('[data-tipo]').forEach(function (x) { x.hidden = x.getAttribute('data-tipo') !== tipo; });
      var lab = box.querySelector('[data-lab-importo]');
      if (lab) lab.textContent = tipo === 'anno' ? 'Yearly salary before taxes ($)' : (tipo === 'ora' ? 'Hourly rate ($)' : 'Gross pay this pay period ($)');
      var ore = null; if (tipo === 'ora') { var o = String(v('ore')).trim(); ore = /^\d{1,3}(\.\d{0,2})?$/.test(o) ? centesimi(o) : null; }
      var lordo = lordoPeriodo(R, tipo, per, centesimi(v('importo')), ore);
      var i = {stato: st, periodo: per, lordo: lordo, ytd: centesimi(v('ytd')), fs: v('fs'), step2: f.elements.step2.checked,
        step3: centesimi(v('step3')), a4: centesimi(v('a4')), b4: centesimi(v('b4')), c4: centesimi(v('c4')),
        ca_fs: v('ca_fs'), ca_reg: intero(v('ca_reg')), ca_est: intero(v('ca_est')), il1: intero(v('il1')), il2: intero(v('il2')), nc_fs: v('nc_fs'), nc_all: intero(v('nc_all'))};
      var bad = null;
      ['lordo', 'ytd', 'step3', 'a4', 'b4', 'c4', 'ca_reg', 'ca_est', 'il1', 'il2', 'nc_all'].forEach(function (k) { if (i[k] === null) bad = k; });
      if (bad) { out.innerHTML = '<p class="errore">Check the amounts: use numbers only, for example 2500 or 2,500.00' + (tipo === 'ora' ? ', and hours such as 80' : '') + '. Allowances are whole numbers.</p>'; return; }
      if (i.lordo <= 0) { out.innerHTML = '<p><strong>Enter your gross pay</strong> to see the estimate.</p>'; return; }
      if (i.lordo > 100000000 || i.ytd > 5000000000) { out.innerHTML = '<p class="errore">This calculator handles pay of up to $1,000,000 per pay period.</p>'; return; }
      var r = busta(R, i), S = R.st[st], P = R.P[per];
      function tr(nome, c, nota, cls) { return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th scope="row">' + nome + (nota ? '<small>' + nota + '</small>' : '') + '</th><td>' + c + '</td></tr>'; }
      var h = '<div class="netto-box"><span>Estimated take-home pay, ' + NOMI_P[per] + '</span><b data-netto>' + usd(r.netto) + '</b><em>' + usd(r.totale) + ' withheld from ' + usd(r.lordo) + ' gross</em></div>';
      h += '<table class="righe"><tbody>' + tr('Gross pay', usd(r.lordo));
      h += tr('Federal income tax', '−' + usd(r.fed), 'IRS Pub. 15-T, ' + r.fedDettaglio.pct + '% bracket' + (i.step2 ? ', Step 2 box checked' : ''));
      h += tr('Social Security', '−' + usd(r.ss), pct(R.fica.ss) + (r.ssImponibile < r.lordo ? ' on ' + usd(r.ssImponibile) + ' (wage base reached)' : ''));
      h += tr('Medicare', '−' + usd(r.medicare), pct(R.fica.med));
      if (r.addl > 0) h += tr('Additional Medicare Tax', '−' + usd(r.addl), pct(R.fica.addl) + ' on ' + usd(r.addlImponibile) + ' above $200,000 this year');
      if (S.it) h += tr(S.nome + ' income tax', '−' + usd(r.stato), r.statoDettaglio.esente ? 'Below the low income exemption' : S.itNota);
      else h += tr(S.nome + ' income tax', '$0.00', 'No state income tax on wages');
      if (S.sdi) h += tr('California SDI', '−' + usd(r.sdi), pct(S.sdi) + ' of all wages');
      h += tr('Take-home pay', usd(r.netto), '', 'netto') + '</tbody></table>';
      h += '<p>About <strong>' + usd(r.netto * P) + '</strong> a year if every paycheck is like this one (× ' + P + '). ' + (i.ytd ? '' : 'Year-to-date pay is taken as $0: the Social Security wage base and Additional Medicare Tax are not reached. ') + '</p>';
      out.innerHTML = h;
    }
    f.addEventListener('input', agg); f.addEventListener('change', agg); agg();
  });

  document.querySelectorAll('[data-datore]').forEach(function (box) {
    var f = box.querySelector('form'), out = box.querySelector('[data-out]'), ultimo = null;
    function agg() {
      var st = f.elements.stato.value, S = R.st[st], ar = f.elements.aliquota;
      if (st !== ultimo) { ar.value = (S.suta.nuovo / 1000).toFixed(3).replace(/0+$/, '').replace(/\.$/, ''); ultimo = st; }
      var w = centesimi(f.elements.salario.value), a = String(ar.value).trim(), rate = /^\d{1,2}(\.\d{0,3})?$/.test(a) ? Math.round(parseFloat(a) * 1000) : null;
      if (w === null || rate === null) { out.innerHTML = '<p class="errore">Check the figures: wages such as 50000 and a rate such as 2.7.</p>'; return; }
      if (w <= 0) { out.innerHTML = '<p><strong>Enter the yearly wages</strong> to see the estimate.</p>'; return; }
      if (w > 10000000000) { out.innerHTML = '<p class="errore">This calculator handles wages of up to $100,000,000 a year.</p>'; return; }
      var r = datore(R, st, w, 0, rate);
      function tr(nome, c, nota, cls) { return '<tr' + (cls ? ' class="' + cls + '"' : '') + '><th scope="row">' + nome + (nota ? '<small>' + nota + '</small>' : '') + '</th><td>' + c + '</td></tr>'; }
      var h = '<div class="netto-box"><span>Estimated employer payroll taxes for the year</span><b data-tasse>' + usd(r.totale) + '</b><em>Wages plus taxes: ' + usd(r.costo) + '</em></div><table class="righe"><tbody>';
      h += tr('Social Security, employer share', usd(r.ss), pct(R.fica.ss) + ' up to $' + (R.fica.ssBase / 100).toLocaleString('en-US'));
      h += tr('Medicare, employer share', usd(r.medicare), pct(R.fica.med) + ' of all wages');
      h += tr('FUTA', usd(r.futa), pct(r.futaAliquota) + ' on the first $7,000' + (R.futa.rid[st] ? ' (0.6% + ' + pct(R.futa.rid[st]) + ' credit reduction)' : ' after the full credit'));
      h += tr(S.nome + ' ' + S.suta.nome, usd(r.suta), pct(r.sutaAliquota) + ' on the first $' + (S.suta.base / 100).toLocaleString('en-US'));
      if (S.ett) h += tr('California ETT', usd(r.ett), pct(S.ett) + ' on the first $' + (S.ettBase / 100).toLocaleString('en-US'));
      h += tr('Total employer taxes', usd(r.totale), (r.totale * 100 / w).toFixed(2) + '% of wages', 'netto') + '</tbody></table>';
      h += '<p>One employee, paid for the whole calendar year. Not included: workers’ compensation insurance, benefits, local taxes.</p>';
      out.innerHTML = h;
    }
    f.addEventListener('input', agg); f.addEventListener('change', agg); agg();
  });
})();
