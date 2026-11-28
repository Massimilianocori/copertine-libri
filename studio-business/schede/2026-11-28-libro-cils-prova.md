# Scheda: libro KDP «CILS B1 Cittadinanza», prova di domanda sulle pagine CILS — 28/11/2026

Da `ricerca-2026-11-28-grandi-opportunita.md`, scelta 2.

1. Obiettivo in €/visite e come contribuisce al piano: decidere entro il 20/12 se scrivere un secondo libro KDP solo sul CILS. Stima 380 € prudente / 1.700 € centrale l'anno (diritti d'autore: nessun nodo fiscale nuovo). Canale n. 1 del piano (libri venduti dal sito).
2. Dati che giustificano il lavoro (GoatCounter 21-27/11 e seodata, letti il 28/11): `/esempi/cils` 84 visite a settimana contro CELI 8 e PLIDA 7; pagine CILS insieme 96 a settimana; `/esempi/` 204 su 426 visite del sito, 115 da ChatGPT; «cils b1 cittadinanza» 1.000 ricerche al mese, clic 1,45 €; Amazon libri suggerisce «cils b1 cittadinanza»; Percorso CILS 7-14 copie al giorno con lamentele su audio e formato (BookBeam 6/11). Libro 1: 6 clic a settimana, 2 copie.
3. Regole fisse: niente vendita diretta (il riquadro non vende, raccoglie solo l'interesse con il modulo «avvisami» che c'è già); nessun dato personale nel repository; libri nuovi solo con BookBeam (≥ 3 indipendenti che vendono); una pubblicazione Netlify al giorno per sito; revisione indipendente ≥ 8,5; cancello AdSense delle pagine.
4. Errori già fatti che rischio di ripetere: promettere una data d'uscita non sicura (il testo dice «in preparazione», senza data); riquadri fuori dall'impronta del lastmod (nessuna data mossa); prova che nessuno vede (la pagina del Pass ha 1 visita a settimana: qui il riquadro sta sulle pagine che hanno già le visite).
5. Variabili esterne: esame CILS del 3/12 (dopo, le visite a `/esempi/cils` possono scendere: la soglia è in numero assoluto e si legge anche il tasso); revisione AdSense in corso su esameb1.eu; Google in recupero o no.
6. Cosa NON tocco: URL, titoli, robots, il riquadro del libro 1, il riquadro del Pass, gli altri siti.
7. Come misuro: evento GoatCounter `esameb1.eu/clic/libro-cils` e iscrizioni del modulo; visite alle 3 pagine nello stesso periodo; verifica.py 0 errori; Playwright a 390 e 1280 px; revisione ≥ 8,5.
8. Criterio di «fatto» e di stop: prova dal 30/11 al 20/12. **Si scrive il libro** se ≥ 10 clic o iscrizioni E la foto BookBeam mostra ≥ 3 indipendenti sotto il n. 20.000; uscita entro il 15/1/2027. **Stop** se < 4 clic al 20/12 o la foto non regge. Fra 4 e 9: si prolunga al 10/1 e si decide con le copie del libro 1.
9. Costo: 2-3 ore per il riquadro e una pubblicazione Netlify; 5 minuti di Massimiliano (1 foto BookBeam «cils b1 cittadinanza» su amazon.it); 0 €. Se passa: 15-20 ore per il libro, 2 ore sue.
10. Dopo la pubblicazione: controllo online, IndexNow, salute.py, riga in DA-PUBBLICARE.md; lettura dei numeri ogni lunedì; esito il 21/12.

Chiusura: [ ] riquadro online (data, commit) · [ ] evento arrivato · [ ] foto BookBeam ricevuta · [ ] esito del 21/12 con i numeri.

## Deviazioni (costruzione del 28/11/2026, non ancora pubblicato né in git)

- **Pagine e posto del riquadro.** Solo `/esempi/cils/`, `/ente/cils/`, `/risultati/cils/`. Non è in alto (lì restano il riquadro del libro 1 e quello del Pass): sta dopo i file ufficiali in `/esempi/cils/`, dopo «Come prepararti» in `/ente/cils/`, dopo «Se non hai superato l'esame» in `/risultati/cils/`. Se al primo lunedì i clic sono zero, la prima cosa da provare è spostarlo più in alto.
- **Un pulsante, poi il modulo.** Come per il Pass: il pulsante «Avvisami quando esce» conta il clic (`esameb1.eu/clic/libro-cils`) e apre il modulo. Così si leggono due numeri separati: clic e iscrizioni.
- **Modulo.** È il modulo Netlify «avvisami» che c'è già, con il campo nascosto `fonte=libro-cils` per distinguere queste iscrizioni. Si scrive solo l'email; in più c'è la casella del consenso (obbligatoria, come nel Pass). Niente città, niente ente.
- **Date scritte nel riquadro.** Nessuna data di uscita e nessun prezzo («non sono decisi»). Ci sono solo due date, che riguardano i dati: «decidiamo entro il 10 gennaio 2027» (lo stop della scheda è il 20/12, prolungabile al 10/1: ho scritto la più lontana, per non dover cambiare il testo) e «se non lo facciamo, cancelliamo la tua email entro il 15 gennaio 2027». **Impegno da rispettare:** se l'esito è «stop», le iscrizioni con `fonte=libro-cils` vanno cancellate da Netlify entro il 15/1/2027.
- **«Con audio».** Il testo dice «libro di sole prove CILS B1 Cittadinanza, con audio», come nella ricerca. Se il libro si fa senza audio, il testo va cambiato prima.
- **Informativa privacy non toccata.** Il registro del lastmod non doveva cambiare, quindi `privacy.html` è rimasta com'è: il testo sui dati sta tutto nel riquadro. L'informativa ha già il paragrafo «Libro in arrivo» (solo email, una sola email, poi cancellata), ma non dice «se il libro non si fa». Consiglio: aggiungere una riga sul libro CILS alla prossima modifica dell'informativa (la data di `privacy.html` cambierà, ed è giusto).
- **Fuori dalle misure.** Il riquadro è fuori dall'impronta del lastmod (`dati/lastmod.json` identico) e dalle due misure delle parole della pubblicità (`dati/cancello_pubblicita.json` identico). Rispetto a prima cambiano solo le 3 pagine, e solo per il riquadro; titoli, URL, description invariati.
- **Controlli.** `verifica.py` ha il nuovo `controlli_libro_cils` (riquadro solo sulle 3 pagine, evento una volta sola su un pulsante, campi del modulo, frasi oneste, nessun prezzo, date ammesse, impronta, parole): 0 errori. `monetizzazione.py verifica esameb1`: 0 errori. Playwright a 390 e 1280 px sulle 3 pagine: nessuno scorrimento orizzontale, 0 errori in console, il clic manda l'evento `esameb1.eu/clic/libro-cils`, l'invio manda solo `email`, `consenso`, `fonte=libro-cils` e `source`. Prova fatta in locale: l'arrivo vero dell'evento su GoatCounter e la prima iscrizione su Netlify si controllano dopo la pubblicazione.
- **Non fatto qui:** commit, pubblicazione, IndexNow, riga in DA-PUBBLICARE.md, revisione indipendente, foto BookBeam.

### Dopo la revisione indipendente (8,7) — 28/11/2026
- Tolto «con audio» (non deciso). Frase d'apertura ora «Pensiamo di fare un libro…» con «decidiamo entro il 10 gennaio 2027 se farlo»; conferma «Ti scriviamo se e quando il libro esce».
- privacy.html: aggiunto il paragrafo del riquadro CILS (una sola email se esce; se non lo facciamo, email cancellate entro il 15/1/2027 senza scrivere). Lastmod mosso solo su privacy.html (contenuto cambiato davvero).
- Impegno: se l'esito è «stop», cancellare in Netlify le iscrizioni `fonte=libro-cils` entro il 15/1/2027 (promemoria in agenda).
