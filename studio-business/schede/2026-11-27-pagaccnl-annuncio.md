# Scheda: prova di domanda «Paga CCNL per chi assume» — 27/11/2026 (PIANO-FATTURATO sez. 9, azione 3)

Massimiliano, 27/11: «falle andare bene»; «usa fable quando può migliorare qualcosa». Anticipata dal 10/12 a oggi.

1. Obiettivo: misurare se consulenti del lavoro, studi paghe, agenzie e uffici del personale userebbero uno strumento per la riga di retribuzione dell'annuncio (obbligo del D.Lgs. 96/2026, art. 5, dal 7/6/2026) e pagherebbero Pro 149 €/anno o API 49 €/mese. Centrale 2.800 € a 12 mesi, 9.200 € a 24 mesi se la prova passa (ricerca-2026-11-26-grandi-b2b.md, sez. 1.4).
2. Dati: obbligo per tutti i datori di lavoro, anche piccoli, senza regola transitoria; 456.000-575.000 ingressi al mese previsti (Excelsior 2025); concorrenti senza listino (ilCCNL.it) o 349-1.319 €/anno (Edotto, FiscoeTasse); nessuno strumento trovato che dia la riga pronta per l'annuncio da contratto e livello; pagaccnl.com: 5 contratti, 53 livelli, cifre verificate con due fonti, 44-113 visite a settimana.
3. Regole: NIENTE VENDITA (13/11): prezzi veri ma nessun pagamento, solo modulo «Avvisami all'apertura» e «Chiedi una chiave di prova», detto chiaro; niente contatti a freddo; niente dati personali nel repository (moduli Netlify); due fonti al centesimo per ogni cifra di paga, frase «verifica con il tuo consulente»; cancello AdSense del sito; forma editoriale; crediti Netlify (1 pubblicazione); nessun sito nuovo.
4. Errori da evitare: cifre di legge più larghe delle fonti (citare l'art. 5 com'è, non inventare sanzioni: l'importo non è stato trovato); pagine povere; lastmod mossi sulle pagine livello per un riquadro; promettere contratti che non abbiamo (dire 5 contratti oggi).
5. Variabili: rinnovi dei contratti (le cifre si aggiornano dalla raccolta esistente); Google sul dominio nuovo (home indicizzata il 26/11); circolari o interpelli sul D.Lgs. 96/2026.
6. Non tocco: URL, titoli, robots, tabelle e cifre delle pagine esistenti; altri siti.
7. Misura: eventi GoatCounter `pagaccnl.com/clic/annuncio-copia` (riga copiata), `pagaccnl.com/clic/pro-prezzo`, `pagaccnl.com/clic/api-chiave`; uso dello strumento (evento al calcolo); moduli Netlify «pro» e «api»; verifica.py 0 errori con controlli nuovi (riga dello strumento = cifre delle tabelle per tutti i 53 livelli, JS = Python); Playwright telefono e computer; revisione indipendente ≥ 8,5.
8. Fatto: strumento, guida, pagina «Per consulenti e aziende», pagina API con esempio JSON vero, online e misurati. Soglia al 15/1/2027: ≥ 300 usi e ≥ 10 email Pro, oppure ≥ 2 richieste di chiave API → si propone a Massimiliano costruzione e iscrizione. Stop al 31/1/2027: < 100 usi o < 3 email.
9. Costo: agenti ~6-8 ore; 1 pubblicazione Netlify; nessuna spesa.
10. Dopo: controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE.md, lettura ogni lunedì.

Chiusura: (da spuntare)

## Deviazioni scritte dall'agente che ha costruito (27/11/2026)

Costruito e non pubblicato (nessun commit, nessun push). `genera.py` + `verifica.py`: 0 errori, 0 avvisi; `verifica.py --browser`: 0 errori; `monetizzazione.py verifica ccnl`: 0 errori.

1. **Il lavoro domestico è escluso dal decreto.** Art. 2, comma 2: «ad esclusione dei contratti di lavoro domestico e dei contratti di lavoro intermittente». La ricerca del 26/11 diceva «tutti i datori di lavoro». Lo strumento dà la riga anche per colf e badanti (8 livelli), ma dice che è una scelta e non un obbligo; il riquadro delle pagine del lavoro domestico dice «l'obbligo non vale». Tolti questi, i livelli a cui l'obbligo si applica sono 45 su 53.
2. **Agenzie e piattaforme.** La ricerca diceva che l'art. 5 «vale anche per agenzie per il lavoro e piattaforme». Nel testo non c'è: il comma 2 nomina solo i «soggetti ai quali abbiano affidato la fase di selezione», e solo per il divieto di chiedere la retribuzione passata. La guida cita il comma com'è e non lo allarga.
3. **Testo ufficiale.** Normattiva e Gazzetta Ufficiale non si scaricano da questa macchina (connessione chiusa). Il testo è copiato da MioLegale (che riprende Normattiva, vigente al 24/10/2026); gli articoli 2, 5 e 13 sono stati poi riletti sulla pagina di Normattiva con un lettore di pagine, che ha confermato frase per frase art. 2 (5 frasi), art. 5 (10 frasi) e art. 13 comma 1, rubriche e numero dei commi. Non è un confronto fatto byte per byte da noi: resta da rifare a mano. ecnews.it, pmi.it e TeamSystem oggi non rispondono (reset o 403): non usati. Frammenti e impronta in `ccnl/dati/annuncio.json`.
4. **Sanzioni.** Nessun importo scritto. La guida cita l'art. 13 (rinvio all'art. 41 del codice delle pari opportunità per le discriminazioni accertate) e dice che un importo per l'annuncio senza retribuzione non è nelle fonti lette. «Nessuna regola transitoria» e «nessuna soglia di dipendenti» sono scritte come «nel testo letto non c'è».
5. **Part time in ore e in percentuale.** La scheda chiedeva la percentuale; ci sono tutte e due. Le ore danno le stesse cifre delle pagine livello.
6. **Mensilità non modificabili**: sono quelle del contratto (13 o 14), mostrate e usate per l'annuo.
7. **Date future.** Lo strumento contiene già i passi alle date note. Quando la pagina livello passa a «Cifra da aggiornare» (logistica non viaggiante dal 1/1/2027, metalmeccanici dal 1/6/2027) o il lavoro domestico resta sulla tabella dell'anno prima, lo strumento NON dà la riga e lo dice. Provato nel browser al 2/1 e al 2/2/2027.
8. **Evento del calcolo**: parte solo quando la riga è creata davvero (pulsante «Crea la riga»); ogni cambio di dati nasconde la riga, quindi un uso = un clic. La copia conta solo se riuscita.
9. **Aggiunte non chieste**: voce di menu «Per chi assume» (il menu largo ora si chiude sotto 1060 px invece di 900), colonna nel piede, riquadro anche in home, file fermo `/api/esempio.json`, due frasi in «Chi siamo». Il link dei riquadri porta contratto e livello (`?c=…&l=…`): `verifica.py` ora toglie la parte dopo `?` nel controllo dei link.
10. **Lastmod**: il sito non ha un'impronta per pagina; la sitemap dà a tutte le pagine la data `controllato_il` (12/11/2026), anche alle 4 nuove. Il riquadro non muove nessuna data.
11. **URL**: `/annuncio-di-lavoro/`, `/annuncio-di-lavoro/cosa-scrivere/`, `/per-consulenti-e-aziende/`, `/api/`. 67 pagine indicizzabili (erano 63). Parole di contenuto fuori dai moduli: 1.384, 1.827, 652, 837 (cancello a 400).
12. **Già rotto prima, non toccato**: con `CCNL_OGGI=2027-01-02` (e 2027-02-02, 2027-06-02) `verifica.py` dà 9 errori «manca il pezzo nascosto» sulle pagine livello anche sul codice di prima. I controlli nuovi a quelle date: 0 errori.
13. **Da fare dopo la pubblicazione**: accendere in Netlify le notifiche dei moduli `pro` e `api`; la revisione indipendente (punto 7 della scheda) non è stata fatta da questo agente.

### Secondo giro, dopo la revisione indipendente (8,3) — 27/11/2026

Applicate le 13 correzioni chieste e il `lastmod` per pagina. `verifica.py` 0 errori, `--browser` 0 errori, `monetizzazione.py verifica ccnl` 0 errori. Ancora nessun commit.

14. **Retribuzione offerta (punto 9)**: solo per i contratti a cui il decreto si applica; per il lavoro domestico il campo è nascosto. Offerta uguale al minimo = riga normale; più bassa = rifiutata con il minimo scritto nel messaggio. Con la fascia la riga completa dice «Importo: fascia dal minimo del contratto in vigore dal … alla retribuzione offerta dall'azienda».
15. **Art. 12 e art. 6 (punti 5 e 10)**: citato il primo periodo dei due commi, copiato dalla copia di MioLegale. Questi due frammenti NON sono stati riletti frase per frase su Normattiva come gli articoli 2, 5 e 13 (è scritto in `annuncio.json`, `nota_frammenti`).
16. **«livello» minuscolo (punto 11)**: applicato anche dentro la riga («Inquadramento: livello C3…», «quadro»).
17. **«due fonti (testo depositato o tabella ministeriale, e una seconda fonte firmataria)» (punto 12)**: scritto come chiesto in strumento, Pro e API. Per il lavoro domestico la seconda fonte è la copia depositata al CNEL, non una parte firmataria: le pagine del contratto lo dicono già, la frase nuova è un po' più stretta del vero per quel contratto.
18. **Evento in più (punto 13)**: `pagaccnl.com/clic/api-prezzo`, pulsante della scheda API nella pagina Pro. Da aggiungere alla lettura del lunedì.
19. **Privacy**: i dati dei due moduli si cancellano entro il 31/3/2027 se non apriamo. È un impegno scritto in pagina: va messo in agenda.
20. **Lastmod per pagina**: registro `ccnl/dati/lastmod.json`, stesso metodo di Visa Income (titolo, descrizione, JSON-LD, `<main>`), fuori dall'impronta le date di controllo e di lettura delle fonti, i nomi dei file in `/assets/` e il riquadro dell'annuncio. Primo avvio fatto dalle pagine generate con il codice dell'ultimo commit: 61 pagine restano al 12/11/2026, 6 al 27/11/2026 (le 4 nuove più «Chi siamo» e «Privacy», che oggi hanno testo nuovo). NON usate le date di `git log` (14/11 e 25/11) proposte dal piano visite: l'istruzione del coordinatore era di tenere il 12/11. Con `CCNL_OGGI` il registro non si riscrive.
