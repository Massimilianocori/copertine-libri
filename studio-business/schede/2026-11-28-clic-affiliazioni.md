# Scheda: misura vera delle affiliazioni già accese (pannelli + contatore dei clic) — 28/11/2026

Da `ricerca-2026-11-27-sera-monetizzare-traffico.md` (1ª scelta) e dalla «mossa 0» di `ricerca-2026-11-26-sera-concorrenti.md`, decisa il 26/11 e non ancora fatta. Regola «OPPORTUNITÀ: realizzare entro 48 ore».

1. Obiettivo in €/visite e come contribuisce al piano: nessun euro diretto. Dà il numero che il piano scrive «manca» (PIANO-FATTURATO sez. 2.5: «Clic e vendite: mancano»). Con quel numero si decide: (a) se le affiliazioni accese valgono i 90-365 € l'anno stimati; (b) quali riquadri togliere prima della prossima domanda AdSense (tappa che sblocca il primo incasso); (c) se la decisione del 19/11 sulle affiliazioni nuove va riaperta («numeri veri»).

2. Dati che giustificano il lavoro:
   - 1.742 link di affiliazione su 1.361 pagine, 0 clic contati (conteggio di `rel="sponsored"` nelle cartelle `sito/`, 27/11): Before You Fly 606 link su 547 pagine, Visa Income 592 su 381, Cruise 257 su 257, EsameB1 220 su 110, Italy Strikes 62 su 61, Tourist Tax 5 su 5.
   - Incasso delle affiliazioni: 0 € (CRUSCOTTO sez. 2a).
   - Unico tasso vero: riquadro del libro, 6 clic su 441 visite in 7 giorni = 1,4 % (GoatCounter, 20-26/11).
   - Visite in 28 giorni (30/10-26/11): EsameB1 1.921, Visa 1.309, Before You Fly 1.029, Cruise 128, Tourist Tax 104, Italy Strikes 79.
   - Clic attesi nei pannelli dal giorno di accensione, se l'1,4 % vale: circa 50-75 (tabella 4.3 della ricerca).

3. Regole fisse che toccano questo lavoro:
   - Fermo su Visa Income e Before You Fly fino al 9/12: su questi due siti il contatore esce con la prima pubblicazione permessa dal 10/12, non prima.
   - Affiliazioni (19/11): nessun riquadro nuovo, nessun programma nuovo, nessun link spostato. Si aggiunge solo un attributo ai link che ci sono.
   - Nessun dato personale: l'evento GoatCounter non usa cookie e non porta dati della persona. Gli ID dei programmi non entrano nel nome dell'evento.
   - Date vere: nessun `lastmod` mosso (l'attributo non è contenuto).
   - Crediti Netlify: nessuna pubblicazione fatta apposta sui siti minori; il contatore esce con la prossima pubblicazione già prevista di ogni sito. Una pubblicazione per sito al giorno.
   - Gli agenti non salvano e non pubblicano.
   - Azioni sugli account di Massimiliano: i pannelli li legge solo lui.

4. Errori già fatti che questo lavoro rischia di ripetere, e come li evito:
   - «Lastmod mossi per un riquadro»: controllo che le date di sitemap prima e dopo siano uguali (diff della sitemap = 0 righe).
   - Decisioni prese su ipotesi e non su dati (19-23/11): nessun riquadro si toglie prima di 28 giorni di contatore e 200 visite sulle sue pagine.
   - Lavoro deciso e lasciato in un file (26/11): la scheda ha date e una riga in DA-PUBBLICARE.md.
   - Conteggio gonfiato dai nostri clic di prova: i clic di prova si fanno solo in locale (da localhost `count.js` non invia nulla) o si segnano e si tolgono, come per il Pass.

5. Variabili esterne e cosa succede se cambiano:
   - AdSense risponde durante la prova: la misura continua; se chiede meno promozione, i riquadri a 0 clic si tolgono subito anche prima dei 28 giorni, e lo si scrive qui.
   - Un programma chiude o cambia il link: l'evento resta legato al nome del programma, non all'URL.
   - Stagione: EsameB1 sale a gennaio-febbraio; le soglie sono in clic ogni 100 visite, non in clic assoluti, per la soglia di rete.
   - GoatCounter non risponde: si rilegge il giorno dopo; i pannelli restano la seconda fonte.

6. Cosa NON tocco: URL, titoli, testi, posizione e numero dei riquadri, `rel="sponsored noopener"`, riga di trasparenza, link del libro (hanno già il loro evento), robots, sitemap, `dati/affiliati.json` (nessun URL cambiato), Visa Income e Before You Fly fino al 10/12, i file delle prove in corso (Pass, sedi e scuole, Paga CCNL). Il link profondo di italki agli insegnanti dell'orale (ricerca del 26/11) NON è in questa scheda.

7. Come misuro che è fatto bene:
   - Nome dell'evento: `<dominio>/clic/aff-<programma>-<sezione>` (esempi: `esameb1.eu/clic/aff-italki-esempi`, `esameb1.eu/clic/aff-amazon-citta`, `cruise-health-scores.netlify.app/clic/aff-safetywing-navi`).
   - Prima → dopo, per sito: link `rel="sponsored"` con `data-goatcounter-click` da 0 a 220 (EsameB1), 257 (Cruise), 62 (Italy Strikes), 5 (Tourist Tax); numero di link e di pagine con link invariato.
   - `verifica.py` di ogni sito 0 errori, con un controllo nuovo: ogni link `rel="sponsored"` ha l'attributo e il nome segue lo schema; `monetizzazione.py verifica` 0 errori.
   - `salute.py` e `beforeyoufly/raccolta/visite.py` continuano a togliere gli eventi `/clic/` dalle visite (già così).
   - Playwright a 390 e 1.280 px: 0 errori; un clic di prova in locale non rompe il link (si apre il partner in una scheda nuova).
   - Revisione indipendente ≥ 8,5.

8. Criterio di «fatto» e criterio di stop:
   - Fatto: contatore online su EsameB1, Cruise, Italy Strikes e Tourist Tax; numeri dei 6 pannelli scritti in CRUSCOTTO sez. 7; riga della lettura del lunedì aggiunta. Visa e Before You Fly: online alla prima pubblicazione dal 10/12.
   - Soglia per programma e sezione: almeno 5 clic in 14 giorni → resta e sale più in alto nella pagina (lavoro a parte, con la sua scheda).
   - Stop per programma e sezione: 0 clic in 28 giorni con almeno 200 visite sulle sue pagine → il riquadro si toglie da quella sezione.
   - Soglia di rete al 26/12: almeno 1 clic ogni 100 visite sulle pagine con riquadro e almeno 1 vendita nei pannelli → conto vero per la decisione sulle affiliazioni, da portare a Massimiliano. Sotto 0,3 clic ogni 100 visite → le affiliazioni non si ripropongono fino a 50.000 visite al mese.
   - Date: partenza 28/11; prima lettura 12/12; verdetto 26/12 (EsameB1 e siti minori) e 7/1/2027 (Visa e Before You Fly, 28 giorni dal 10/12).

9. Costo: agenti circa 2-3 ore (4 generatori ora, 2 dal 10/12); 0 pubblicazioni Netlify in più; nessuna spesa. **Da Massimiliano: 10 minuti**, entro il 5/12, clic e vendite da 6 pannelli: italki (dal 30/10), Amazon.it `guideesami-21` (dal 30/10), Amazon UK e USA (dal 6/11), SafetyWing per campagna (dal 30/10), Wise su Partnerize (dal 14/11), Awin per inserzionista (dal 6/11).

10. Dopo la pubblicazione: una pagina per sito controllata online (l'attributo c'è, il link porta al partner); sitemap online = repository; IndexNow non serve (nessun contenuto cambiato); `salute.py` 0 errori; riga «Pubblicato il…» in DA-PUBBLICARE.md; lettura degli eventi `aff-*` ogni lunedì nel riassunto; controlli del risultato il 12/12, il 26/12 e il 7/1/2027.

Chiusura: (da spuntare)
