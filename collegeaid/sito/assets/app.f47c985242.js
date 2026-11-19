// US College Aid: tema chiaro/scuro, conto dei giorni alle scadenze, filtro della tabella degli Stati, calcolatori, modulo delle correzioni.
// Le pagine si leggono anche senza JavaScript (tabelle e date sono già nell'HTML). I calcolatori non hanno cifre scritte qui dentro:
// tassi, tetti e scaglioni arrivano dall'attributo data-regole della pagina, che genera.py scrive da dati/aiuti.json (fonti ufficiali).
// I conti sono in centesimi interi; i tassi in millesimi di punto percentuale (6,52 % = 6520).
var CA = (function () {
  function centesimi(testo) {            // "$27,000.50" -> 2700050 ; null se non è un numero
    var s = String(testo == null ? '' : testo).replace(/[$,\s]/g, '');
    if (!/^\d+(\.\d{0,2})?$/.test(s)) return null;
    var p = s.split('.');
    return parseInt(p[0], 10) * 100 + (p[1] ? parseInt((p[1] + '0').slice(0, 2), 10) : 0);
  }
  function millesimi(testo) {            // "6.52" -> 6520 ; null se non è un numero
    var s = String(testo == null ? '' : testo).replace(/[%\s]/g, '').replace(',', '.');
    if (!/^\d+(\.\d{0,3})?$/.test(s)) return null;
    var p = s.split('.');
    return parseInt(p[0], 10) * 1000 + (p[1] ? parseInt((p[1] + '00').slice(0, 3), 10) : 0);
  }
  function usd(c, senzaCent) {
    var neg = c < 0; c = Math.abs(c);
    var d = Math.floor(c / 100), r = c % 100;
    var s = String(d).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return (neg ? '−$' : '$') + s + (senzaCent && r === 0 ? '' : '.' + (r < 10 ? '0' : '') + r);
  }
  // Durata del piano standard per i prestiti dal 1/7/2026: dipende dal capitale (fasce della legge). saldo in centesimi.
  function anniStandard(saldo, fasce) {
    for (var i = 0; i < fasce.length; i++) if (fasce[i].sotto === null || saldo < fasce[i].sotto * 100) return fasce[i].anni;
    return fasce[fasce.length - 1].anni;
  }
  // Rata fissa di un prestito a tasso fisso: P·r / (1 − (1+r)^−n), r = tasso annuo / 12. Arrotondata al centesimo.
  function rata(saldo, tasso, mesi) {
    if (tasso === 0) return Math.round(saldo / mesi);
    var r = tasso / 1200000;
    return Math.round(saldo * r / (1 - Math.pow(1 + r, -mesi)));
  }
  function interesseMese(saldo, tasso) {   // interesse di un mese, arrotondato al centesimo (metà in su), con soli interi
    return Math.floor((saldo * tasso * 2 + 1200000) / 2400000);
  }
  // Piano di ammortamento: rata fissa, l'ultima rata chiude il saldo. Restituisce rata, mesi, totale pagato, interessi.
  function piano(saldo, tasso, mesi) {
    var p = rata(saldo, tasso, mesi), resto = saldo, pagato = 0, interessi = 0, n = 0;
    while (resto > 0 && n < mesi + 12) {
      var i = interesseMese(resto, tasso), dovuto = resto + i, paga = (n === mesi - 1 || dovuto < p) ? dovuto : p;
      resto = dovuto - paga; pagato += paga; interessi += i; n++;
    }
    return { rata: p, mesi: n, pagato: pagato, interessi: interessi };
  }
  // Repayment Assistance Plan: pagamento base annuo per scaglione di reddito (AGI), diviso 12, meno 50 $ per persona a carico, minimo 10 $.
  // reddito in dollari interi. Restituisce centesimi.
  function rapBaseAnno(reddito, rap) {
    for (var i = 0; i < rap.scaglioni.length; i++) {
      var s = rap.scaglioni[i];
      if (s.fino_a === null || reddito <= s.fino_a) return s.pc === null ? s.fisso_anno * 100 : reddito * s.pc;   // pc % di reddito in dollari = reddito·pc centesimi
    }
    return 0;
  }
  function rapPc(reddito, rap) {
    for (var i = 0; i < rap.scaglioni.length; i++) { var s = rap.scaglioni[i]; if (s.fino_a === null || reddito <= s.fino_a) return s.pc; }
    return null;
  }
  function rapMese(reddito, carico, rap) {
    var m = Math.round(rapBaseAnno(reddito, rap) / 12) - carico * rap.per_dipendente_mese * 100;
    return Math.max(m, rap.minimo_mese * 100);
  }
  // Un mese nel RAP: il pagamento va prima agli interessi; gli interessi non coperti non vengono addebitati;
  // se il capitale scende di meno di 50 $, il governo aggiunge la differenza fino a min(50 $, pagamento).
  function rapUnMese(pagamento, saldo, tasso, rap) {
    var i = interesseMese(saldo, tasso), paga = Math.min(pagamento, saldo + i);
    var aInteressi = Math.min(paga, i), aCapitale = paga - aInteressi, nonAddebitati = i - aInteressi;
    var soglia = rap.quota_capitale_mese * 100, aggiunta = 0;
    if (aCapitale < soglia) aggiunta = Math.max(0, Math.min(Math.min(soglia, paga) - aCapitale, saldo - aCapitale));
    return { interessi: i, aInteressi: aInteressi, aCapitale: aCapitale, nonAddebitati: nonAddebitati, aggiunta: aggiunta, nuovoSaldo: saldo - aCapitale - aggiunta };
  }
  // Quanto di un costo annuo coprono i tetti federali: studente dipendente (tetto annuo per anno di corso e tetto complessivo) e genitori (PLUS).
  // costo in centesimi per anno; anni di corso da 1 a 6. Restituisce le righe per anno e i totali.
  function buco(costo, anni, lim) {
    var righe = [], totS = 0, totG = 0, tot = { costo: 0, studente: 0, genitori: 0, resto: 0 };
    for (var a = 0; a < anni; a++) {
      var tettoAnno = lim.dipendente.anni[Math.min(a, lim.dipendente.anni.length - 1)].totale * 100;
      var s = Math.max(0, Math.min(tettoAnno, lim.dipendente.totale * 100 - totS, costo));
      var g = Math.max(0, Math.min(lim.genitori.anno * 100, lim.genitori.totale * 100 - totG, costo - s));
      totS += s; totG += g;
      var r = { anno: a + 1, costo: costo, studente: s, genitori: g, resto: costo - s - g };
      righe.push(r); tot.costo += costo; tot.studente += s; tot.genitori += g; tot.resto += r.resto;
    }
    return { righe: righe, totale: tot };
  }
  function giorniA(iso, oggi) {             // giorni interi tra oggi (ora locale) e la data iso
    var p = iso.split('-'), d = Date.UTC(+p[0], +p[1] - 1, +p[2]);
    var o = Date.UTC(oggi.getFullYear(), oggi.getMonth(), oggi.getDate());
    return Math.round((d - o) / 86400000);
  }
  function testoGiorni(n) {
    if (n > 1) return 'in ' + n + ' days';
    if (n === 1) return 'tomorrow';
    if (n === 0) return 'today';
    if (n === -1) return 'passed yesterday';
    return 'passed ' + (-n) + ' days ago';
  }
  return { centesimi: centesimi, millesimi: millesimi, usd: usd, anniStandard: anniStandard, rata: rata, interesseMese: interesseMese, piano: piano,
    rapBaseAnno: rapBaseAnno, rapPc: rapPc, rapMese: rapMese, rapUnMese: rapUnMese, buco: buco, giorniA: giorniA, testoGiorni: testoGiorni };
})();
if (typeof module !== 'undefined') module.exports = CA;

(function () {
  if (typeof document === 'undefined') return;
  var b = document.querySelector('[data-tema]');
  if (b) b.addEventListener('click', function () {
    var r = document.documentElement, scuro = r.getAttribute('data-theme') === 'dark' || (!r.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = scuro ? 'light' : 'dark'; r.setAttribute('data-theme', t); try { localStorage.setItem('ca-theme', t); } catch (e) {}
  });
  document.querySelectorAll('form[data-correzioni]').forEach(function (form) { form.addEventListener('submit', function (ev) { ev.preventDefault();
    var err = form.querySelector('[data-errore]'); err.hidden = true; if (!form.checkValidity()) { form.reportValidity(); return; }
    var bt = form.querySelector('button'); bt.disabled = true;
    fetch('/', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(new FormData(form)).toString()})
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; var ok = form.parentNode.querySelector('[data-ok]'); if (ok) ok.hidden = false; })
      .catch(function () { err.hidden = false; bt.disabled = false; });
  }); });

  // Conto dei giorni: la data scritta nella pagina è quella ufficiale; qui si aggiunge solo «in N days» con l'orologio di chi legge.
  var oggi = new Date();
  document.querySelectorAll('[data-giorni]').forEach(function (el) {
    var n = CA.giorniA(el.getAttribute('data-giorni'), oggi);
    el.textContent = CA.testoGiorni(n); el.hidden = false;
    if (n < 0) el.classList.add('passata');
  });

  // Tabella delle scadenze per Stato: ricerca per nome e filtro per tipo di scadenza.
  document.querySelectorAll('[data-scadenze]').forEach(function (box) {
    var righe = Array.prototype.slice.call(box.querySelectorAll('tbody tr')), cerca = box.querySelector('[data-cerca]'), tipo = box.querySelector('[data-tipo]');
    var stato = box.querySelector('[data-stato]'), vuoto = box.querySelector('[data-vuoto]');
    function agg() {
      var q = (cerca.value || '').trim().toLowerCase(), t = tipo.value, n = 0;
      righe.forEach(function (tr) {
        var ok = (!q || tr.getAttribute('data-nome').indexOf(q) >= 0) && (!t || tr.getAttribute('data-tipo') === t);
        tr.hidden = !ok; if (ok) n++;
      });
      vuoto.hidden = n > 0;
      stato.textContent = 'Showing ' + n + ' of ' + righe.length + ' states and territories.';
    }
    cerca.addEventListener('input', agg); tipo.addEventListener('change', agg);
    box.querySelector('[data-filtri]').hidden = false; agg();
  });

  function regole(el) { return JSON.parse(el.getAttribute('data-regole')); }
  function scrivi(box, nome, testo) { var e = box.querySelector('[data-o="' + nome + '"]'); if (e) e.textContent = testo; }
  function errore(box, msg) {
    var e = box.querySelector('[data-errore]'), o = box.querySelector('[data-uscita]');
    e.textContent = msg || ''; e.hidden = !msg; o.hidden = !!msg;
  }
  function ascolta(box, fn) {
    box.querySelectorAll('input,select').forEach(function (i) { i.addEventListener('input', fn); i.addEventListener('change', fn); });
    var f = box.querySelector('form'); if (f) f.addEventListener('submit', function (ev) { ev.preventDefault(); fn(); });
    fn();
  }

  // Calcolatore della rata (piano standard)
  document.querySelectorAll('[data-calc="rata"]').forEach(function (box) {
    var R = regole(box), saldoI = box.querySelector('[name=saldo]'), tipoI = box.querySelector('[name=tipo]'), tassoI = box.querySelector('[name=tasso]'), pianoI = box.querySelector('[name=piano]');
    tipoI.addEventListener('change', function () { if (tipoI.value) tassoI.value = tipoI.value; });
    ascolta(box, function () {
      var saldo = CA.centesimi(saldoI.value), tasso = CA.millesimi(tassoI.value);
      if (saldo === null || saldo < 100 || saldo > 100000000) return errore(box, 'Enter a loan balance between $1 and $1,000,000.');
      if (tasso === null || tasso > 20000) return errore(box, 'Enter an interest rate between 0 and 20 percent, for example 6.52.');
      var anni = pianoI.value === 'nuovo' ? CA.anniStandard(saldo, R.fasce) : 10, p = CA.piano(saldo, tasso, anni * 12);
      if (!p) return errore(box, 'These numbers do not produce a repayment schedule.');
      errore(box, '');
      scrivi(box, 'rata', CA.usd(p.rata)); scrivi(box, 'anni', anni + ' years (' + p.mesi + ' payments)');
      scrivi(box, 'pagato', CA.usd(p.pagato)); scrivi(box, 'interessi', CA.usd(p.interessi));
      scrivi(box, 'perche', pianoI.value === 'nuovo'
        ? 'A balance of ' + CA.usd(saldo, true) + ' falls in the ' + anni + '-year band of the standard plan for loans made on or after July 1, 2026.'
        : 'Fixed payment over 10 years, the standard plan for borrowers whose loans were all made before July 1, 2026.');
    });
  });

  // Calcolatore del Repayment Assistance Plan
  document.querySelectorAll('[data-calc="rap"]').forEach(function (box) {
    var R = regole(box), redI = box.querySelector('[name=reddito]'), carI = box.querySelector('[name=carico]'), saldoI = box.querySelector('[name=saldo]'), tassoI = box.querySelector('[name=tasso]');
    ascolta(box, function () {
      var red = CA.centesimi(redI.value), car = parseInt(carI.value, 10);
      if (red === null || red > 1000000000) return errore(box, 'Enter your adjusted gross income in dollars, for example 45,000.');
      if (isNaN(car) || car < 0 || car > 15) return errore(box, 'Enter the number of dependents, from 0 to 15.');
      var dollari = Math.floor(red / 100), base = CA.rapBaseAnno(dollari, R.rap), pc = CA.rapPc(dollari, R.rap), m = CA.rapMese(dollari, car, R.rap);
      var saldo = saldoI.value.trim() ? CA.centesimi(saldoI.value) : 0, tasso = CA.millesimi(tassoI.value);
      if (saldo === null || saldo > 100000000) return errore(box, 'Enter the loan balance in dollars, or leave it empty.');
      if (saldo > 0 && (tasso === null || tasso > 20000)) return errore(box, 'Enter an interest rate between 0 and 20 percent, for example 6.52.');
      errore(box, '');
      scrivi(box, 'rata', CA.usd(m));
      scrivi(box, 'base', pc === null ? CA.usd(base, true) + ' a year (flat amount)' : CA.usd(base) + ' a year (' + pc + '% of ' + CA.usd(dollari * 100, true) + ')');
      scrivi(box, 'dodici', CA.usd(Math.round(base / 12)));
      scrivi(box, 'carico', car ? '− ' + CA.usd(car * R.rap.per_dipendente_mese * 100, true) : '$0');
      scrivi(box, 'minimo', m === R.rap.minimo_mese * 100 && Math.round(base / 12) - car * R.rap.per_dipendente_mese * 100 < m ? 'The result is below $' + R.rap.minimo_mese + ', so the $' + R.rap.minimo_mese + ' minimum applies.' : '');
      var mese = box.querySelector('[data-mese]');
      if (saldo > 0) {
        var u = CA.rapUnMese(m, saldo, tasso, R.rap);
        scrivi(box, 'interessi', CA.usd(u.interessi)); scrivi(box, 'ainteressi', CA.usd(u.aInteressi)); scrivi(box, 'acapitale', CA.usd(u.aCapitale));
        scrivi(box, 'nonaddebitati', CA.usd(u.nonAddebitati)); scrivi(box, 'aggiunta', CA.usd(u.aggiunta)); scrivi(box, 'nuovosaldo', CA.usd(u.nuovoSaldo));
        mese.hidden = false;
      } else mese.hidden = true;
    });
  });

  // Calcolatore di quanto coprono i tetti federali (studente dipendente + genitori)
  document.querySelectorAll('[data-calc="buco"]').forEach(function (box) {
    var R = regole(box), costoI = box.querySelector('[name=costo]'), anniI = box.querySelector('[name=anni]'), corpo = box.querySelector('[data-righe]');
    ascolta(box, function () {
      var costo = CA.centesimi(costoI.value), anni = parseInt(anniI.value, 10);
      if (costo === null || costo > 50000000) return errore(box, 'Enter the yearly cost in dollars, for example 32,000.');
      errore(box, '');
      var r = CA.buco(costo, anni, R.limiti), h = '';
      r.righe.forEach(function (x) {
        h += '<tr><th scope="row">Year ' + x.anno + '</th><td class="n">' + CA.usd(x.costo, true) + '</td><td class="n">' + CA.usd(x.studente, true) + '</td><td class="n">' + CA.usd(x.genitori, true) + '</td><td class="n forte">' + CA.usd(x.resto, true) + '</td></tr>';
      });
      corpo.innerHTML = h;
      scrivi(box, 'resto', CA.usd(r.totale.resto, true)); scrivi(box, 'costo', CA.usd(r.totale.costo, true));
      scrivi(box, 'studente', CA.usd(r.totale.studente, true)); scrivi(box, 'genitori', CA.usd(r.totale.genitori, true));
      scrivi(box, 'frase', r.totale.resto > 0
        ? 'Over ' + anni + (anni === 1 ? ' year' : ' years') + ', the federal limits leave ' + CA.usd(r.totale.resto, true) + ' to cover in other ways.'
        : 'Over ' + anni + (anni === 1 ? ' year' : ' years') + ', the federal limits are enough to cover this cost in full.');
    });
  });
})();
