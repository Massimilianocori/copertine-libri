# Scheda: prova di domanda «EsameB1 per le sedi e le scuole» — 27/11/2026 (PIANO-FATTURATO sez. 9, azione 2)

Massimiliano, 27/11: «falle andare bene». Anticipata dal 10/12 a oggi: EsameB1 non è fermo e la stagione d'esame è gennaio-febbraio.

1. Obiettivo: misurare se sedi d'esame private e scuole di italiano pagherebbero 199 €/anno (licenza del simulatore per la classe) o 29 €/mese (scheda in evidenza, una per città, segnata «sponsorizzato»). Centrale 2.600 € a 12 mesi, 7.500 € a 24 mesi se la prova passa (ricerca-2026-11-26-grandi-b2b.md, sez. 2.3).
2. Dati: 644 sedi d'esame e 129 CPIA già nel sito (94 pagine città); CILS 16.696 candidati B1 Cittadinanza in una sessione annuale; corsi di preparazione 80-180 €; nessuna piattaforma che vende licenze di simulazione B1 Cittadinanza alle scuole (ricerca del 26/11); Flo-Joe 245 £/anno per livello come riferimento; «simulazione esame b1 per cittadinanza italiana» 1.000-1.300 ricerche al mese.
3. Regole: NIENTE VENDITA (13/11): i prezzi sono veri ma il pulsante non vende, porta a un modulo onesto («in preparazione, nessun pagamento ora»); niente contatti a freddo (aspettiamo che le scuole scrivano); niente dati personali nel repository (le risposte restano nei moduli Netlify); cancello AdSense (≥110 parole proprie sulla pagina nuova, altrimenti niente script né affiliazioni); forma editoriale; schede delle sedi sempre ordinate dai dati ufficiali, mai mescolate con un posto a pagamento; nomi degli enti solo per descrivere, con «non affiliato»; crediti Netlify (1 pubblicazione).
4. Errori da evitare (REGISTRO-RISCHI-ERRORI.md): pagina povera con annunci; lastmod mosso su 94 pagine città per un pulsante (il pulsante va fuori dall'impronta, come i riquadri); testo più largo delle fonti; promesse non mantenibili (dire chiaro cosa c'è oggi: prova gratis da 24 domande; cosa è in preparazione: 6 simulazioni, codice classe, riepilogo per l'insegnante).
5. Variabili: revisione AdSense in corso; Google in recupero (la pagina si regge anche su ChatGPT e sui link interni); le scuole pubbliche e i CPIA comprano con il MEPA (fuori dalla prova, il testo lo dice).
6. Non tocco: titoli, URL, robots e ordine delle schede esistenti; riquadri del libro e del Pass; altri siti.
7. Misura: eventi GoatCounter `esameb1.eu/clic/sede-sei-tu` (pulsante sulle schede), `esameb1.eu/clic/scuole-licenza`, `esameb1.eu/clic/scuole-scheda`; moduli Netlify «scuole» (conteggio, mai copiati nel repo); verifica.py 0 errori con controllo nuovo sulla pagina e sui pulsanti; Playwright (telefono e computer); revisione indipendente ≥ 8,5.
8. Fatto: pagina online, pulsante su ogni scheda sede delle pagine città, modulo che arriva in Netlify, eventi che arrivano. Soglia al 28/2/2027: ≥ 8 scuole che scrivono e ≥ 3 che chiedono prezzo o ordine → si propone a Massimiliano costruzione e iscrizione. Stop: < 3 scuole al 28/2. Controllo intermedio 7/1.
9. Costo: agenti ~4-6 ore; 1 pubblicazione Netlify (~15 crediti); nessuna spesa.
10. Dopo: controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE.md, lettura ogni lunedì insieme al Pass.

Chiusura: (da spuntare)

## Deviazioni scritte dall'agente che ha costruito (27/11/2026)

1. **Le pagine città sono 87, non 94.** `dati/citta.json` ha 94 voci, ma le pagine generate in `/citta/` sono 87. Il pulsante è su tutte le 87 (619 schede). La pagina nuova scrive «87 pagine città», il numero vero.
2. **Niente simulazione dimostrativa nuova.** La ricerca (sez. 2.4) chiedeva «1 simulazione dimostrativa completa con audio». Non è stata costruita: la pagina indica come esempio la prova gratuita da 24 domande già online (senza audio) e lo dice.
3. **Link alla pagina da «Chi siamo», non dal piede.** Il piede è uguale in tutte le pagine: aggiungere una voce avrebbe cambiato tutti i file del sito. Con «Chi siamo» e la riga «Insegni…?» nella prova online cambiano 2 file.
4. **Il pulsante è fuori anche dalla misura delle parole proprie** (cancello AdSense), in `genera.py` e in `verifica.py`. Senza questa esclusione Caserta scendeva da 110 a 109 parole proprie e perdeva la pubblicità solo per il pulsante. Con l'esclusione l'elenco del cancello è identico a prima.
5. **Arrivando da una scheda l'interesse non è già scelto.** Solo la città è scritta nel modulo; la scuola sceglie da sola tra licenza, scheda e «solo gratis», così la misura non è spinta da noi. I due pulsanti «Mi interessa» invece scelgono la loro offerta.
6. **Campo nascosto `arrivo`** nel modulo (`scheda:<slug>` se la scuola arriva da una scheda): non è un dato personale, serve a contare da dove arrivano.
7. **«Candidati l'anno» è una scelta a fasce** (meno di 20, 20-50, 51-100, 101-300, più di 300, non lo so), non un numero libero.
8. **Prezzi scritti come «previsti»**, con la riga «il prezzo definitivo te lo scriviamo quando il servizio è pronto, prima di qualsiasi ordine». La pagina non dice se l'IVA è compresa: da decidere prima di rispondere alla prima scuola.
9. **Aggiunta gratuita di corso e date: oggi è solo il modulo.** La scheda sede non ha ancora un campo per corso e date; va costruito alla prima richiesta vera. La pagina promette il controllo su una pagina pubblica della sede, con fonte e data.
10. **Controllo del registro lastmod in `verifica.py`:** per le 4 pagine città sotto la soglia della pubblicità il confronto con `dati/lastmod.json` è saltato, perché già prima di oggi quelle pagine vengono ritoccate dopo la scrittura del registro. Resta il confronto «impronta con pulsante = impronta senza pulsante».
11. Non fatto, perché viene dopo la pubblicazione: controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE.md, prova che il modulo arrivi davvero in Netlify. Nessun commit e nessun push.

### Dopo la revisione indipendente (8,0): correzioni dello stesso giorno

12. **Numero delle sedi corretto.** La pagina scriveva «644 sedi in 87 pagine città»: le schede nelle pagine città sono 619, di 613 sedi diverse. Ora scrive «oltre 600», numero calcolato dalle pagine generate e ricontrollato in `verifica.py`, più «Se la tua sede non è in una pagina città, scrivici lo stesso».
13. **Audio detto chiaro.** La prova gratis è senza audio (dialogo da leggere, vero o falso, testo da completare) e la pagina lo dice; nella licenza «l'ascolto con audio è in preparazione».
14. **IVA:** la pagina dice che non è ancora deciso se i prezzi sono con o senza IVA. Resta da decidere prima di rispondere alla prima scuola.
15. **Promesse nuove da mantenere:** risposta entro 7 giorni a chi chiede corso e date; prima di un ordine della scheda in evidenza, le visite dell'ultimo mese della pagina città (dato GoatCounter).
16. **Schede «in provincia»:** il link porta `&provincia=1`; il modulo non scrive la città e il campo `arrivo` vale `provincia:<slug>`. Chi arriva da una scheda vede sopra il modulo una riga che indica la scelta gratuita; nessuna scelta è già fatta. «Solo aggiungere corso e date, gratis» è la prima scelta.
17. **Titolo H2 del gancio:** «Sei una sede d'esame? Aggiungi gratis il tuo corso e le tue date» (il pulsante sulle schede resta «Sei questa sede? Aggiungi corso e date»).
18. **Privacy:** base giuridica art. 6.1.b GDPR e tempi di cancellazione, uguali sotto il modulo.
19. **Titolo della pagina** senza il nome del sito ripetuto in fondo.
20. **Lastmod mossi al 27/11 perché il contenuto è cambiato davvero:** `chi-siamo/` (riga con il link), `privacy.html` (paragrafo sul modulo), `prova-b1-online/` (riga «Insegni…?»). Le 87 pagine città non si sono mosse.
21. **Da fare in `verifica.py`** (TODO datato nel codice): il registro lastmod è scritto prima del taglio delle affiliazioni nelle 4 pagine città sotto la soglia; lì il confronto con il registro è saltato.
