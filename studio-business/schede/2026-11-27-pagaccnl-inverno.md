# Scheda: Paga CCNL, pacchetto d'inverno (preavviso, tredicesima, quattordicesima) — 27/11/2026 (STRATEGIA-LAVORO n. 2)

1. Obiettivo: far risalire pagaccnl.com (124 → 33 pagine viste a settimana dal 21/11) con pagine che rispondono a ricerche di dicembre-gennaio; crescita del sito che porta la prova «annuncio di lavoro». Valore diretto piccolo (4/16/48 €/anno, ricerca-2026-11-27-idee-nuove.md idea 5), valore indiretto: visite al sito della prova Pro (centrale 2.800 €).
2. Dati: «quando arriva la tredicesima» 14.800/mese, «come si calcola la tredicesima» 9.900, «calcolo tredicesima» 8.100, «preavviso dimissioni» 12.100, «preavviso ccnl commercio» 4.400; i concorrenti partono dallo stipendio scritto a mano, nessuno da contratto e livello; sui giorni di preavviso del commercio i concorrenti non sono d'accordo (15/45 giorni).
3. Regole: due fonti al centesimo per ogni cifra (o testo del contratto per i giorni di preavviso, con articolo e frase citata); «verifica con il tuo consulente»; niente netto né stime fiscali; cancello AdSense; lastmod vero (dati/lastmod.json); forma editoriale.
4. Errori da evitare: regole più larghe del testo del contratto; giorni di preavviso presi da siti terzi; cifre inventate; pagine povere; date mosse senza motivo.
5. Variabili: rinnovi dei contratti; la tredicesima di dicembre 2026 arriva tardi per Google (vale per gennaio e per il 2027).
6. Non tocco: URL, titoli, cifre delle pagine esistenti; altri siti.
7. Misura: verifica.py 0 errori con controlli nuovi (JS = Python su ogni livello per la tredicesima; frasi citate = testo del contratto); revisione indipendente ≥ 8,5; pagine viste delle pagine nuove ogni lunedì.
8. Fatto: pagine preavviso e tredicesima per i 5 contratti + calcolo, online. Stop: se al 31/1/2027 le pagine nuove hanno meno di 20 visite in tutto, niente altre pagine di questo tipo.
9. Costo: agenti ~8 ore; 1 pubblicazione; nessuna spesa.
10. Dopo: controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE.

Chiusura: (da spuntare)

## Deviazioni e note di costruzione (27/11/2026, non pubblicato)
Fatto: 12 pagine (`/preavviso/` + 5, `/tredicesima/` + 5), calcolo della tredicesima, riquadro in 53 pagine livello e 5 pagine contratto, link nel piede. `verifica.py` 0 errori (anche `--browser`), `monetizzazione.py verifica ccnl` 0 errori. Niente commit, niente pubblicazione.
1. **Indennità sostitutiva, mese di 30 giorni.** Commercio, multiservizi e logistica non scrivono come passare dai giorni di calendario agli euro. Il conto «minimo ÷ 30 × giorni» è nostro ed è dichiarato in pagina, con la quota giornaliera del contratto citata come altro modo possibile. Metalmeccanici (mensilità scritte nel contratto) e lavoro domestico (trentesimi, chiarimento a verbale n. 2) usano la regola del testo.
2. **Ratei di 13ª e 14ª nell'indennità.** Commercio (art. 252) e logistica (artt. 18-19) li nominano. Li mostriamo solo nell'esempio svolto (× 14 ÷ 12), non nelle tabelle: le tabelle restano sul solo minimo.
3. **Logistica, driver e rider.** L'art. 36 non nomina la qualifica 1 (G, H) né le lettere I e L: per quei 6 livelli la pagina non dà giorni né euro e lo dice.
4. **Operai e impiegati.** Multiservizi e logistica distinguono per qualifica, non per livello. Le tabelle in euro degli operai coprono i livelli 1-5 (multiservizi) e 3S-6 (logistica), scelti dalle declaratorie; la pagina lo dichiara.
5. **Lavoro domestico.** Il preavviso non dipende dal livello ma da ore e anzianità: la tabella «per livello» è quella dell'indennità (convivente, 30 ore, 20 ore). La riduzione del 50% per le dimissioni nel testo sta solo dopo i rapporti da 25 ore: sotto le 25 ore la pagina non la applica. Vitto e alloggio: detti, non sommati.
6. **Testi vecchi.** Metalmeccanici e multiservizi: i soli testi completi che abbiamo sono del 2021 e del 2011. La pagina lo scrive in una nota («Quale testo leggiamo»). Da rifare quando il CNEL deposita i testi coordinati.
7. **Part time nel calcolo.** Solo in percentuale (come chiede la scheda), più «a ore» per colf e badanti. Le tabelle delle pagine usano 20, 24 e 30 ore, le stesse cifre delle pagine livello.
8. **Quattordicesima nel calcolo.** Usa gli stessi mesi scritti per la tredicesima; la pagina avverte che il periodo è diverso (luglio-giugno).
9. **Titoli.** Le frasi della scheda («preavviso dimissioni», «calcolo tredicesima») non sono nel file dei volumi del 13/11: i titoli nuovi non sono registrati in `titoli_misurati.json`. Nessuna FAQ con JSON-LD nelle pagine nuove (la regola delle FAQ chiede una frase misurata nel file).
10. **Date future.** Ogni blocco con cifre ha già il pezzo della prossima data. Con riga sospesa (logistica non viaggiante dal 1/1/2027, metalmeccanici dal 1/6/2027) le celle dicono «da aggiornare» e il calcolo non dà cifre, come lo strumento dell'annuncio.
11. **Trovato, non toccato.** Con `CCNL_OGGI` nel 2027 `verifica.py` dà 9 errori sulle pagine livello («manca il pezzo nascosto per la tabella del …»). C'erano già prima di questo lavoro (provato sul commit b59bb3ddf).
12. **Non fatto (punto 10 della scheda, dopo la pubblicazione):** controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE. Revisione indipendente ≥ 8,5: da fare.

## Secondo giro dopo la revisione indipendente (27/11/2026, voto 8,2; non pubblicato)
Applicati tutti e 10 i punti. `genera.py`, `verifica.py`, `verifica.py --browser`, `monetizzazione.py verifica ccnl`: 0 errori. Deviazioni e limiti:
1. **Quattordicesima (blocco 1).** Fatto come chiesto per commercio e logistica, con la tabella del minimo previsto al 30 giugno 2027 (tabelle già firmate). Per il multiservizi l'art. 21 non dice «al 30 giugno»: la pagina lo scrive e l'etichetta del calcolo è «(prima di luglio il minimo può cambiare)» invece di «(quella vera usa il minimo al 30 giugno)».
2. **Testi vecchi (blocco 2).** Verificato sui file prima di scrivere. Il rinnovo intermedio del multiservizi nei nostri documenti si chiama «CCNL 8 giugno 2021»: la pagina usa quella data. Il controllo sui due rinnovi è stato fatto a mano su una lettura ottica completa già presente fuori dal progetto (stesso file, stessa impronta): rifarla dentro `_grezzi` chiede ore di macchina, quindi `verifica.py` ricontrolla solo le pagine che abbiamo (2, 6, 13 dell'ipotesi multiservizi).
3. **Ratei (punto 4).** Colonna «con i ratei» = importo × 14 ÷ 12. È la lettura più semplice di «comprensiva dei ratei di 13a e 14a»: la formula è scritta in pagina. Le tabelle del commercio ora hanno 8 colonne e sul telefono scorrono di lato.
4. **«Letto il» (punto 5).** La data del 27 novembre vale per il testo del contratto (e per la pag. 6 dell'ipotesi multiservizi); le tabelle dei minimi restano «Letto il 12 novembre 2026», perché quelle non le abbiamo rilette oggi.
5. **Metà dei termini (punto 8).** Il numero tra parentesi c'è solo quando è intero. «La metà di 15 giorni» e «la metà di 2 mesi e 15 giorni» restano senza numero: il contratto non dice come arrotondare.
6. **Ferie e malattia (punto 10).** Solo frasi dei testi. Per la malattia nel multiservizi, nella logistica e nei metalmeccanici la pagina dice che le regole stanno negli articoli sulla malattia, che non riportiamo. Per il commercio dice che gli artt. 251, 252 e 256 non ne parlano.
7. **Procedura online (punto 10).** Fonte unica: la pagina «Dimissioni volontarie» del Ministero del Lavoro, letta il 27/11/2026. Nessuna norma citata oltre a quello che dice la pagina.

## Terzo giro (27/11/2026, voto 8,8; non pubblicato)
Applicati i 4 punti; tutti i controlli a 0 errori. Deviazioni:
1. Tabelle dell'indennità sul telefono: per non scorrere di lato a 390 px la colonna «Minimo» è nascosta sotto i 700 px (sul computer le colonne sono 5). La fascia di mezzo è «Oltre 5, fino a 10» e non «5–10 anni», per restare sulle parole del contratto.
2. Commercio, ferie e malattia: la sezione resta, con la frase dell'art. 190 sulla malattia; sulle ferie non c'è una frase e la pagina lo dice.
3. Anche le tabelle di colf e badanti hanno intestazioni più corte («Chi convive», «A ore, 30 ore»).

