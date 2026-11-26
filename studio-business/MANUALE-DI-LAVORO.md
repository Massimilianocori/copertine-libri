# Manuale di lavoro: regole e obblighi (vincolante)

Massimiliano, 26/11/2026: «crea tutte le regole e obblighi di lavoro, segui il piano minuziosamente, ricontrolla il lavoro quando hai finito. Solo così evitiamo cazzate».

Questo manuale vale per me, per ogni agente e per ogni routine automatica. Se una regola qui e una in REGOLE-FISSE.md sembrano in conflitto, vale la più prudente e lo si scrive a Massimiliano.

## A. Prima di iniziare (obbligatorio)
1. Leggere REGOLE-FISSE.md, REGISTRO-RISCHI-ERRORI.md e PIANO-FATTURATO.md.
2. Scrivere la scheda in 10 punti (PIANO-OBBLIGATORIO.md) in `studio-business/schede/`. Nessuna scheda = nessun lavoro.
3. Il lavoro deve servire una tappa del piano o una regola (in € o visite misurate). Se non serve, non si fa.
4. Controllare: fermi in corso (Visa e BYF fino al 9/12), crediti Netlify, lavori già aperti da altri agenti sugli stessi file.
5. Decidere prima la misura del risultato (numero prima → dopo) e il criterio di stop.

## B. Durante il lavoro
1. Si fa solo quello che è nella scheda. Ogni deviazione si scrive nella scheda prima di farla.
2. Solo fonti ufficiali, lette davvero; mai aggirare anti-robot, blocchi geografici o errori di certificato; un dato non letto non si scrive.
3. Mai date false: «controllato il» = giorno della lettura vera.
4. Mai toccare URL, titoli in blocco, robots o noindex senza che la scheda e le regole lo permettano.
5. Gli agenti NON salvano e NON pubblicano: costruiscono, controllano, si fermano. Salvo e pubblico solo io, dopo la revisione.
6. Nessun dato personale nel repository; chiavi e password mai scritte né stampate.

## C. Prima di pubblicare (cancello: tutto deve essere sì)
1. Generatore senza errori; `verifica.py` del sito a 0 errori; `monetizzazione.py verifica` a 0 errori.
2. Misura prima → dopo scritta (pagine, link, date, numeri cambiati) e coerente con la scheda.
3. Nessuna data lastmod mossa senza un cambio vero del contenuto.
4. Controllo nel browser (Playwright) a 390 e 1.280 px: 0 errori, niente pagine rotte.
5. Revisione indipendente Fable con voto ≥ 8,5; correzioni applicate e ricontrollate.
6. `grep sd_live` vuoto; nessun dato personale nel diff; solo i file del lavoro nel commit (mai `git add -A`).
7. Una pubblicazione per sito al giorno; crediti Netlify sufficienti.

## D. Dopo la pubblicazione: ricontrollo obbligatorio
1. Le pagine cambiate rispondono 200 online e mostrano il cambio (controllo con curl o browser, non a memoria).
2. Sitemap online = repository.
3. IndexNow inviato; `salute.py` a 0 errori.
4. La scheda è spuntata punto per punto con le prove (comando, numero, commit).
5. Riga «Pubblicato il…» in DA-PUBBLICARE.md e data del controllo del risultato (3, 7, 14 giorni).
6. Se qualcosa non torna: si corregge subito, si scrive l'errore in REGISTRO-RISCHI-ERRORI.md con il controllo che ne impedisce il ritorno.

## E. Comunicazione con Massimiliano
1. Solo risultati verificati, con il numero o la prova. Niente «fatto» senza controllo.
2. Niente scuse e niente resoconti lunghi: cosa è online, cosa cambia in € o visite, cosa serve da lui (minuti, passi precisi).
3. Le decisioni di lavoro le prendo io con i dati (regola «DECISIONI IN BASE AL FATTURATO»); a lui chiedo solo spese, azioni sui suoi account e scelte che toccano il suo lavoro sui libri.
4. Un blocco che non posso superare si dice subito, una volta, con cosa serve.

## F. Controlli automatici che fanno rispettare il manuale
- `salute.py` ogni mattina (dati vecchi, routine saltate, date passate, promesse false, fonti ferme).
- `verifica.py` di ogni sito a ogni pubblicazione (cancello AdSense sulle parole uniche, link, dati contro le fonti).
- Indicatore del recupero ogni lunedì (visite Google ÷ picco).
- Rilettura di REGISTRO-RISCHI-ERRORI.md ogni lunedì.
