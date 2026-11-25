# Revisione indipendente di STRATEGIA-RECUPERO.md

Fatta il 25/11/2026, sera. Ho letto il piano, la «Verifica del 25/11» e la tabella aggiunta «Tutti i siti della rete».

## Voto: 7,5 su 10

Il piano è prudente e ben documentato. Le citazioni sono quasi tutte vere. Le azioni di stanotte non fanno danni, se si rispettano le condizioni scritte sotto. Il voto scende per sei errori: una citazione usata a metà, una usata fuori contesto, l'azione 9 costruita su un presupposto sbagliato, un rischio concreto sul `lastmod`, troppe pagine toccate dalle azioni 5 e 6, e alcune conclusioni scritte come fatti.

Con le 8 correzioni della sezione 5 il piano arriva a 8,5.

## 1. Come ho controllato

- Ho scaricato 27 pagine citate e ho cercato ogni frase parola per parola. 72 frasi controllate.
- Ho controllato i 5 domini con richieste dirette: robots, sitemap, 301 dai vecchi indirizzi, 404, intestazioni.
- Ho letto `sito/` e `genera.py` dei 5 siti.
- Ho ricalcolato le visite da Google per sito in GoatCounter per il 20, 21, 22 e 24/11.

Non ho potuto controllare: la pagina di Search Engine Journal (risponde 403 alle richieste dirette; letta solo tramite un riassunto automatico); i dati di Search Console (schermate del titolare); le visite da Google dei giorni prima del 20/11 (il mio ricalcolo non è riuscito).

## 2. Citazioni

**Vere e usate bene: 66 su 72.** Tutte le frasi sullo spostamento, sul Cambio di indirizzo, su «Rilevata, non indicizzata», sugli aggiornamenti principali, sulle sitemap, su `lastmod`, sul noindex, sui contenuti in scala e su AdSense esistono nelle pagine indicate. Anche le due frasi di Mueller su Search Engine Roundtable e la pagina di stato di Google (aggiornamento dal 10/11 al 24/11, chiuso alle 14:03 UTC; aggiornamento di dicembre preannunciato il 24/11).

**Da correggere:**

| # | Dove | Problema | Correzione |
|---|---|---|---|
| Q1 | 1.2, «Budget di scansione» | Il piano dice che la guida vale solo per siti grandi e che «non è il nostro caso». La guida elenca tre casi. Il terzo è: «Sites with a large portion of their total URLs classified by Search Console as Discovered - currently not indexed». È esattamente il nostro caso. | Scrivere che la guida ci riguarda per il terzo caso. Rafforza il piano, non lo indebolisce. |
| Q2 | Azione 9 | «Try not to combine multiple moves» è citata a metà e con la fonte sbagliata. La frase intera è «Try not to combine multiple moves to a single location» e sta nella pagina del Cambio di indirizzo. Parla di più siti uniti in un solo dominio. Non parla di più siti spostati nello stesso periodo. | Togliere la citazione dall'azione 9. Resta valida «Change only one thing at a time». |
| Q3 | 1.2, podcast di luglio | Il piano dice che la domanda era su «discovered not indexed». Dal riassunto che ho letto, la domanda di Splitt riguardava lo stato «non indicizzata» in generale. Non verificato sulla pagina originale. | Scrivere «pagine non indicizzate» e segnare la citazione come non verificata. |
| Q4 | 1.2, Mueller | La risposta di Mueller è del 10/11 (Bluesky). L'articolo è dell'11/11. | Correggere la data. |
| Q5 | Azione 8 | Le frasi AdSense sono vere, ma sono sparse su tre pagine. «Don't place the ad code…» e «we may review all pages» stanno in answer/81904. «Building a high-quality site…» e «usually takes a few days» stanno in answer/10015918, non in 7299563. | Mettere ogni frase accanto alla sua pagina. |
| Q6 | Azione 7 | «Don't use noindex, as Google will still request…» è vera. Nella guida è un consiglio per chi vuole risparmiare scansione. | Nessun cambio di sostanza. Dire che vale come costo, non come divieto. |

**Sitemap dei vecchi indirizzi ospitata sul dominio nuovo: è valida.** La guida di Google lo dice in modo esplicito: una sitemap su un sito può contenere URL di altri siti, anche di domini diversi, se tutti i siti sono verificati. Si invia da Search Console. La guida allo spostamento chiede proprio due sitemap, vecchi e nuovi indirizzi, e dice che gli avvisi di reindirizzamento sono normali.

## 3. Logica e dati

**Confermato da me:**

- I 301 dei 5 vecchi indirizzi portano alla stessa pagina del dominio nuovo. Anche `robots.txt` e `sitemap.xml`.
- Una pagina inesistente risponde 404 sui domini nuovi. Non ci sono falsi 200.
- `robots.txt` aperto. Nessun `X-Robots-Tag`. Le pagine rispondono 200 anche a Googlebot.
- Sitemap online: 1.553, 813, 207, 63, 21 URL. Nessuna pagina in noindex dentro. Ogni pagina in sitemap ha il canonical su se stessa.
- La pagina pubblicata è uguale a quella del repository.
- Link dalla home a pagine noindex: 11 (BYF), 2 (Visa), 7 (EsameB1). I numeri del piano sono giusti.
- Visite da Google del 21/11 e del 24/11: uguali alla tabella del piano.
- `lastmod` di BYF: 829 URL con 20/11 e 521 con 16/11. Giusto.

**Errori o punti deboli:**

- **L1. Paga CCNL e Payroll Tax non sono spostamenti.** I due siti sono nati l'11 e il 12/11 e sono andati sul dominio proprio il 13/11. I vecchi indirizzi netlify.app sono vissuti un giorno. Non c'è niente da trasferire. Il Cambio di indirizzo e la sitemap dei vecchi indirizzi lì non servono.
- **L2. «Payroll Tax regge» non è dimostrato.** Ha 2 e 4 visite da Google a settimana. Sono numeri troppo piccoli per dire qualcosa.
- **L3. Paga CCNL indebolisce l'ipotesi sul Cambio di indirizzo.** È un sito nuovo. Sale a 68 visite e poi cade il 21/11, senza nostre modifiche. Se lì non è stato inviato nessun Cambio di indirizzo, il crollo non dipende da quello strumento. Va controllato e scritto.
- **L4. La nuova tabella aiuta, ma prova meno di quanto sembra.** Calano solo i domini nuovi: questo rende meno probabile l'ipotesi I2 (solo aggiornamento di Google) e più probabile I1 (valutazione del dominio nuovo). Però i siti rimasti su netlify.app hanno 7–31 visite a settimana e Italy Strikes dipende dagli scioperi. Sono un confronto debole. Resta un'ipotesi. La prova vera è il controllo C3 sulla proprietà vecchia.
- **L5. I quattro domini nuovi mostrano lo stesso disegno:** salita subito dopo l'arrivo sul dominio nuovo, poi crollo dopo 7–10 giorni. Visa e BYF hanno la settimana migliore proprio dopo lo spostamento. Il piano non lo dice. È coerente con un dominio nuovo provato e poi rivalutato. Non ho trovato una fonte Google che lo descriva: è un'ipotesi.
- **L6. «EsameB1 tiene» è relativo.** È sceso da 217 a 92 a settimana (−58 %). Il piano lo attribuisce alla stagione, senza un dato.
- **L7. F3 è incompleto.** BYF ha pubblicato sezioni nuove anche il 19/11 e il 20/11 (compagnie per cani, animali, bagaglio da stiva, power bank). Sono altre modifiche di massa dopo il crollo.
- **L8. La «Verifica del 25/11» scrive ipotesi come fatti.** «Nessun guasto tecnico nostro» è confermato dai miei controlli. «Google le conosce ma non le scansiona perché giudica il sito poco prioritario» è un'ipotesi e va scritta così.
- **L9. Il `lastmod` vero esiste già su Visa** (`dati/lastmod.json`, dal 28/10). Il problema è su BYF (solo 35 voci hanno una data vera, le altre prendono la data di oggi) e su EsameB1 (tutte le 207 pagine prendono la data di oggi a ogni generazione). Il piano cita solo BYF.
- **L10. L'azione 6.4 è già fatta.** Privacy e contatti sono già nel piè di pagina e in sitemap su BYF, Visa ed EsameB1. BYF ha già la pagina Contact. Mancano davvero: «How we check» su BYF, «Contatti» su EsameB1, una pagina contatti su pagaccnl e payroll.
- **L11. Nella lista delle richieste manca la home di BYF.** È indicizzata, ma l'ultima scansione è dell'11/11. Dopo stanotte porta il blocco nuovo dei link.

Nota minore: Netlify aggiunge a tutte le pagine uno script con il suo distintivo. C'è su tutti i siti, anche su quelli che tengono. Non è la causa. Si può nascondere dalle impostazioni, senza urgenza.

## 4. Le azioni di stanotte

### Azione 3 — Sitemap: VIA, con tre condizioni

Corretta e sicura. Priorità giusta.

1. **Primo avvio del registro `lastmod`.** Se il registro parte vuoto, tutte le pagine prendono la data di stanotte. È l'errore che vogliamo togliere. Partire dalle date della sitemap di oggi e dalle date dei dati (`letto_il`, `controllato_il`).
2. **Impronta solo sul testo principale.** I blocchi «Most used» e «Related», la data in alto e il piè di pagina devono restare fuori. Altrimenti le azioni 5 e 6 cambiano il `lastmod` di centinaia di pagine nella stessa notte.
3. **Sitemap dei vecchi indirizzi.** Solo gli URL che esistevano prima dell'8/11 (sitemap del commit precedente allo spostamento). Non le pagine nate dopo. File separato, inviato dalla proprietà nuova, fuori dall'indice delle sitemap. Aggiungere la riga `Sitemap:` anche in `robots.txt`: il robots del vecchio indirizzo rimanda già a quello nuovo. Solo per BYF, Visa ed EsameB1.

Consiglio: inviare in Search Console anche ogni sitemap di sezione, non solo l'indice. Così il filtro per sitemap funziona di sicuro.

Rischio residuo: basso. Effetto atteso: modesto. Il collo di bottiglia è la scansione del dominio nuovo, non la riscoperta dei vecchi indirizzi.

### Azione 5 — Link interni: VIA per i punti 1, 2 e 4. Punto 3 ridotto

- Punti 1, 2, 4 (blocco in home, pagine in evidenza negli indici, via i link a pagine noindex): sicuri. Toccano la home e una ventina di indici.
- Punto 3 («Related»): solo sulle 181 pagine con pochi link. Non su tutto il sito. Il blocco deve stare fuori dall'impronta del `lastmod`.
- Il piano stesso dice che l'effetto è piccolo. Non deve diventare una nuova ondata di pagine cambiate.

### Azione 6 — Pagine di fiducia: VIA, senza il punto 3 su tutte le pagine

- Nuove pagine «Who runs it», «How we check», «Contatti» di EsameB1: sicure.
- Punto 3 (data e fonte in alto «su ogni pagina»): farlo solo dove manca, e fuori dall'impronta. Se tocca centinaia di pagine, rimandarlo dopo il 9/12.
- EsameB1: sistemare prima il `lastmod` (L9). Oggi ogni pubblicazione cambia la data di tutte le 207 pagine.

### Azione 9 — pagaccnl e payroll: VIA solo per i controlli. FERMO per il resto

- Controlli C1–C3: sì.
- Cambio di indirizzo e sitemap dei vecchi indirizzi: no. Non c'è storia da trasferire (L1). Non fanno danno, ma non servono e aggiungono un'altra variabile.
- Aggiungere una pagina contatti può aspettare la stessa finestra del 9/12.

### C'è qualcosa che può fare danno stanotte?

Solo due cose, entrambe evitabili: il `lastmod` che salta alla data di stanotte su tutto il sito, e le azioni 5 e 6 che toccano centinaia di pagine. Con le condizioni sopra, no.

### Che cosa manca

- Richiesta di scansione della home di BYF dopo la pubblicazione (L11).
- Il controllo «è stato inviato un Cambio di indirizzo per pagaccnl?» (L3).
- Una riga chiara: stanotte si pubblicano tre azioni insieme. Sono additive, ma non si potrà dire quale ha funzionato. Va accettato e scritto.
- L'aggiornamento di dicembre può arrivare dentro i 14 giorni di misura. Il piano lo nota: bene.

## 5. Correzioni per arrivare a 8,5

1. Azione 9: togliere Cambio di indirizzo e sitemap dei vecchi indirizzi. Scrivere che i due siti sono nuovi, non spostati. Togliere «Payroll regge».
2. Azione 3: aggiungere le tre condizioni (registro avviato con le date vere, impronta solo sul testo principale, vecchi URL solo di prima dell'8/11). Dire che Visa ha già il `lastmod` vero e che EsameB1 no.
3. Azioni 5 e 6: limitare «Related» alle 181 pagine e il punto 6.3 alle pagine dove manca. Togliere il punto 6.4, già fatto.
4. Sezione 1.2: correggere la citazione sul budget di scansione (Q1). Togliere «Try not to combine multiple moves» dall'azione 9 (Q2).
5. Sezione 1.3: aggiungere la tabella di tutti i siti come elemento a favore di I1 e contro I2, con il limite dei numeri piccoli. Aggiungere il disegno «salita e poi crollo» dei quattro domini nuovi come ipotesi. Aggiungere il caso pagaccnl contro l'ipotesi sul Cambio di indirizzo.
6. «Verifica del 25/11»: riscrivere la conclusione come ipotesi. Tenere come fatto solo «nessun guasto tecnico trovato».
7. F3: aggiungere le pubblicazioni del 19 e del 20/11. Correggere le date e le fonti di Q3, Q4, Q5.
8. Sezione 5: mettere la home di BYF tra le richieste del giorno dopo la pubblicazione.
