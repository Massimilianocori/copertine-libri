# Scheda: Italy Strikes, pagine per azienda e pagine per data degli scioperi nazionali — 27/11/2026

1. Obiettivo in €/visite e come contribuisce al piano: `PIANO-CRESCITA-SITI-MINORI-2026-11-27.md`, sezione 2, costruzioni 1 e 3 della tabella finale. Attese del piano: pagine azienda +20 (prudente) / +80 (centrale) visite a settimana nelle settimane con scioperi; pagine data +5 / +20. Con la stima centrale il sito passa da 34 a circa 115 visite a settimana, cioè sopra 300 al mese: soglia per chiedere dominio e AdSense. Deve essere pronto per la pubblicazione forzata del 2/12, prima dello sciopero generale del 4/12.
2. Dati che giustificano il lavoro: domanda misurata nel piano (ricerche al mese in Italia): sciopero trenitalia 110.000, atm 49.500, trenord 33.100, gtt 27.100, atac 12.100, actv 6.600, italo 6.600, tper 5.400, amt genova 4.400, cotral 4.400, anm 2.900, eav 2.900, ryanair 1.900, easyjet 1.300, autolinee toscane 1.000, amat palermo 720, amtab 480 (17 aziende, circa 270.000); «sciopero 15 dicembre» 390, «sciopero aerei 15 dicembre» 590. GoatCounter: picco il 19/11 (23 visite), il giorno prima dello sciopero del 20/11; le pagine in italiano rendono più di quelle in inglese. Oggi il sito non ha nessuna pagina per azienda né per data.
3. Regole fisse che toccano questo lavoro: PIANO OBBLIGATORIO (questa scheda prima del codice); NESSUN SITO OBSOLETO (date mostrate sempre vere; pagine generate per regola a ogni rigenerazione); DECISIONI CON I DATI; niente noindex di massa e nessun cambio di URL esistenti; fasce e orari solo se li scrive la fonte (registro MIT/CGSSE o pagina ufficiale dell'azienda), citati tra virgolette con link e data di lettura; nessuna stima; link alle aziende solo da `dati/link.json`; niente dati personali; nessun aggiramento di blocchi anti-bot (le pagine ufficiali che rifiutano il server restano «da leggere a mano»); niente nomi di modelli AI nei file; nessun commit né push; crediti Netlify: nessuna pubblicazione da questo lavoro (esce con quella già prevista del 2/12); CONTROLLI OBBLIGATORI punto 4 (genera → verifica 0 errori → monetizzazione 0 errori); attribuzione CGSSE/onData CC BY 4.0 invariata.
4. Errori già fatti che questo lavoro rischia di ripetere e come li evito:
   - 23/10-25/11, data «aggiornato» falsa per un mese → le pagine nuove usano la stessa riga di freschezza del sito (ora vera dell'ultimo controllo, registro MIT muto dichiarato); le frasi di risposta portano la data di generazione.
   - 25/11, lastmod mosso dalla sola data → non introduco un lastmod diverso da quello del sito (vedi punto 7: il sito non ha un registro di impronte; lo dichiaro).
   - Pagine a modello quasi senza testo unico (BYF, «Low value content») → ogni pagina azienda ha contenuto proprio: prossimo sciopero, scioperi generali che la riguardano, citazione ufficiale delle fasce se esiste, storico dell'azienda dall'archivio; le pagine senza scioperi dicono comunque storico, fasce e dove controllare.
   - Rischio 2 del piano, nomi scritti in modi diversi nel registro (es. «ATM» è anche l'azienda di Messina, «AMT» senza «Genova», «AMAT» anche a Taranto) → abbinamento per espressione regolare più vincolo di regione, in un file dati separato (`dati/aziende.json`), con controllo a mano delle 17 aziende sull'archivio e prove automatiche in `verifica.py`.
   - Cifre dalla stampa (Tourist Tax, Napoli) → nessun orario che non sia nel registro o in una pagina ufficiale letta oggi; ogni citazione ha URL, frammento esatto e data di lettura in `dati/fasce.json`.
5. Variabili esterne e cosa succede se cambiano durante il lavoro: registro MIT muto dal 23/10 (riserva CGSSE, finestra di 30 giorni) → la frase «nessuno sciopero» parla solo dei prossimi 30 giorni e la riga di freschezza dice la fonte; scioperi revocati tra una pubblicazione e l'altra → le liste si ridisegnano nel browser da `vista.json` (come nel resto del sito) e la frase di risposta si nasconde da sola se i dati sono cambiati; pagine ufficiali delle aziende che cambiano o tolgono l'avviso → le citazioni con data di sciopero scadono da sole dopo la data, le altre hanno la data di lettura e `verifica.py --rete` le ricontrolla; Google: pagine nuove su netlify.app, resa bassa già prevista dal piano.
6. Cosa NON tocco: URL, titoli e testi delle pagine esistenti (aggiungo solo blocchi di link); robots; `decidi_deploy.py`, `raccogli.py`, `fonte_cgsse.py`, workflow; `dati/operatori.json` (i nomi mostrati nelle schede restano quelli di oggi); altri siti; file di altri agenti (esameb1 ecc. sono modificati da altri: non li tocco); nessun noindex.
7. Come misuro che è fatto bene: `python3 italystrikes/genera.py` senza errori; `python3 italystrikes/verifica.py` 0 errori (ogni data e orario mostrato nelle pagine nuove è nei dati; ogni link ad azienda è in `link.json`; nessuna pagina afferma uno sciopero che non è nei dati; ogni pagina è in sitemap e collegata dall'interno); `python3 studio-business/strumenti/monetizzazione.py verifica italystrikes` 0 errori; Playwright a 390 e 1280 px su una pagina azienda e sulla pagina del 4/12 (nessuno scorrimento orizzontale, nessun errore in console); numeri prima → dopo: pagine del sito e voci di sitemap.
8. Criterio di «fatto» e criterio di stop: fatto = 17 pagine azienda + indice, pagine data (IT e EN) per gli scioperi nazionali dei prossimi 30 giorni, link da home, sezioni, città e aeroporti, sitemap, verifiche a 0 errori, schermate salvate. Stop = se un'azienda non si abbina in modo affidabile al registro la pagina non esce (meglio 15 pagine vere che 17 dubbie); se una citazione non si rilegge identica sulla pagina ufficiale non entra.
9. Costo: circa 10 ore previste dal piano (7 + 3); crediti Netlify 0 da questo lavoro (15 già previsti il 2/12); spese 0.
10. Dopo la pubblicazione (a cura di chi pubblica il 2/12): controllo online delle pagine nuove (200, sitemap = commit), IndexNow, `salute.py`, riga in `DA-PUBBLICARE.md`, rilettura delle citazioni delle fasce il 2/12 e il 3/12 (`verifica.py --rete`), controllo del risultato il 7/12 (GoatCounter, visite del 3-5/12 sulle pagine nuove) e il 18/12 (dopo gli scioperi del 14-17/12).

Chiusura: in fondo, dopo il lavoro.

## Chiusura (27/11/2026)

1. ✔ Costruite 17 pagine azienda + indice e le pagine per data di 4/12, 15/12, 16/12, 17/12 in italiano e inglese: pagine del sito da 121 a 147 (`genera.py`: «147 pagine»). Non pubblicato: esce con la pubblicazione del 2/12.
2. ✔ Le 17 aziende sono quelle della tabella della domanda misurata del piano.
3. ✔ Nessun noindex, nessun URL o titolo esistente cambiato; fasce solo da pagine ufficiali lette oggi (`dati/fasce.json`, 8 fonti, 12 frasi, tutte ritrovate identiche: `verifica.py --rete` 0 errori, 0 avvisi); link alle aziende solo da `dati/link.json` (9 voci nuove, lette oggi; easyJet rifiuta il server: stato «browser», nessun aggiramento); nessun dato personale; nessun commit né push.
4. ✔ Nomi ambigui: abbinamento con regione in `dati/aziende.json`, 25 prove fisse in `verifica.py` (ATM Messina, AMAT Taranto, AMT fuori Liguria, Trenitalia Tper, nota con «escluso») e 6 sul «può riguardare»; controllo a mano dei 74 scioperi dell'archivio: nessun abbinamento sbagliato. Data vera: riga di freschezza del sito + «Risposta scritta il 27 novembre 2026».
5. ✔ Revoche tra due pubblicazioni: prova Playwright con `vista.json` simulato (sciopero del 4/12 revocato) → risposta nascosta, avviso «i dati sono cambiati», schede con «Revocato»; orologio al 5/12 → «lo sciopero è passato».
6. ✔ Toccati solo `italystrikes/` e questa scheda. `decidi_deploy.py`, `raccogli.py`, `operatori.json`, workflow: invariati.
7. ✔ `python3 italystrikes/verifica.py`: 0 errori (prova contraria: una data, un orario e una risposta alterati a mano → 8 errori). `monetizzazione.py verifica italystrikes`: 0 errori. Playwright 390 e 1280 px su 8 pagine: larghezza di scorrimento = larghezza dello schermo, 0 errori in console. Schermate in scratchpad (`is-*.png`). Revisione indipendente ≥ 8,5: **da fare prima del 2/12** (non fatta qui).
8. ✔ Criterio di «fatto» raggiunto; nessuna azienda esclusa.
9. Crediti Netlify usati: 0.
10. ☐ Dopo la pubblicazione del 2/12 (a cura di chi pubblica): pagine nuove 200, IndexNow, `salute.py`, riga in `DA-PUBBLICARE.md`, `verifica.py --rete` il 2/12 e il 3/12, risultato il 7/12 e il 18/12.

## Deviazioni dal brief

- **17 aziende, non 16**: la tabella della domanda misurata ne elenca 17; fatte tutte.
- **Storico dal 10/10/2026, non dal 2014**: il piano dice che lo storico dal 2014 «è già nei dati», ma `dati/scioperi.json` parte dal 10/10/2026. Le pagine lo dichiarano. Lo storico lungo richiederebbe di importare l'archivio CGSSE di onData: lavoro a parte.
- **Fasce di garanzia**: disponibili da fonte ufficiale solo per Trenitalia, Trenord, Cotral (regole stabili) e, per il 4/12, Trenitalia, ACTV, AMT Genova, TPER, Autolinee Toscane. Le altre pagine dicono che non le riportiamo e rimandano alla pagina dell'azienda. Le frasi sono raccolte a mano in `dati/fasce.json`: non si aggiornano da sole, vanno rilette prima di ogni sciopero grande.
- **Sitemap**: il sito non ha un registro di impronte; `lastmod` = data di generazione per tutte le pagine, come già faceva. Non ne ho introdotto uno.
- **Pagine dei giorni passati**: restano online con «Concluso» (stessa regola delle pagine dei mesi), senza redirect.
- **Campi nuovi in `vista.json`** (`az`, `az_gen`) e tre aggiunte al JS comune (filtri `az:`/`azgen:`, finestra `day:`, controllo `data-firma`): servono perché gli elenchi delle pagine nuove si aggiornino nel browser come il resto del sito.
- **Link in più sulle pagine esistenti**: blocchi di link su home, sezioni, città, aeroporti, mesi e una voce nel piè di pagina italiano; in inglese home, mese e General strikes. Nessun testo esistente cambiato.
- **Notato, non toccato**: le pagine dei mesi passati si ridisegnano nel browser con i soli ultimi 35 giorni di dati, quindi ottobre 2026 mostra in pagina meno scioperi di quelli scritti nell'HTML. Non l'ho verificato nel browser e non rientra in questo lavoro.
- **«17 dicembre: treni»**: lo sciopero nazionale di quel giorno riguarda ditte in appalto («CONSORZIO STABILE IMPERO, GAM, PS SERVIZI»), che il sito già chiama «Sciopero nazionale treni». La pagina per data eredita quel nome: da valutare in revisione.

## Dopo la revisione indipendente (7/10), 27/11/2026: correzioni fatte

Tutte e 12 le richieste applicate; `genera.py` → 145 pagine (le due pagine del 17/12 non nascono più); `verifica.py --rete` 0 errori, 0 avvisi; `monetizzazione.py verifica italystrikes` 0 errori; Playwright 390/1280 su 10 pagine senza scorrimento orizzontale né errori; schermate rifatte.

1. Appalti ferroviari (cgsse-383453): niente pagina per data, scheda «Sciopero nazionale appalti ferroviari (ditte in appalto: i treni non sono nominati)», nessun «può riguardare». Prova fissa in `verifica.py`.
2. 16/12 (solo Italo): «Sciopera solo il personale di Italo: Trenitalia e Trenord non sono nominati…»; le fasce Trenitalia compaiono solo se Trenitalia è coinvolta. Uguale in inglese.
3. L'impronta (`firma`) comprende gli orari, in Python e nel JS. Prova fissa.
4. Pagine azienda: prima «Venerdì 4 dicembre 2026: sciopero generale nazionale che può riguardare anche ATM», poi «Nessuno sciopero proclamato solo per…».
5. Avvisi delle aziende con data e blocco «Cosa resta garantito / Cosa hanno comunicato» dentro una guardia `data-firma`: spariscono se lo sciopero cambia o passa; non nascono se quel giorno non c'è uno sciopero attivo. H1 con «(revocato)» quando tutti gli scioperi nazionali del giorno sono revocati.
6. Esclusioni: «INTERO SETTORE TRASPORTI» e le esclusioni scritte nella colonna degli orari («AD ESCLUSIONE DEL…»). Prove fisse per 8612 e cgsse-382981.
7. Sindacati del 4/12: nuovo `raccolta/adesioni.py` → `dati/adesioni.json` (scheda CGSSE 381488: proclamante anche Unicobas; aderenti Orsa, Usb e altri). Mostrati nelle pagine per data con il link alla scheda.
8. 15/12: «Sciopero 15 dicembre 2026: taxi in tutta Italia, controllori di volo a Bologna Marconi» e blocco Aerei. Uguale in inglese.
9. Cotral: avviso del 4/12 citato alla lettera (adesione USB e ORSA, fasce orarie). ATM: il 27/11 nessun avviso di sciopero nei suoi elenchi di notizie. ATAC: il sito rifiuta il server (403), non riletto.
10. Citazioni tagliate segnate con […]; aggiunte Genova-Casella (AMT) e Marconi Express (TPER).
11. Storico: colonna «Sindacati».
12. Inglese: «Who: Taxi drivers» per SERVIZIO TAXI (italiano: «Tassisti»).

## Deviazioni aggiunte

- **Punto 7 non è automatico**: `raccolta/adesioni.py` non è nel workflow (non ho toccato workflow né `raccogli.py`). Va lanciato a mano prima della pubblicazione del 2/12, oppure aggiunto al workflow. Le schede degli scioperi continuano a mostrare i sindacati del registro del Ministero (regola: i campi MIT non si sovrascrivono); l'elenco aggiornato è nel riquadro di risposta della pagina per data.
- **Punto 1**: etichetta messa in `leggi()` (titolo della scheda) e non in `SETT_TIT_IT`, per non allungare anche la riga «Chi». Lo sciopero resta nella pagina «Sciopero treni» con il nome nuovo.
- **Punto 8**: nome intero dell'aeroporto («Bologna Marconi») per non confondere gli scali di una stessa città.
- **Punto 9**: per ATM e ATAC nessun link a un avviso specifico: non esiste (ATM) o non è leggibile dal server (ATAC). Da rileggere a mano il 2-3/12.
- **Punto 5**: l'H1 non si può nascondere nel browser; cambia alla rigenerazione.
- **16/12, blocco Aerei**: compare per uno sciopero locale all'aeroporto di Bologna (La Lucente), con la sola regola generale.
