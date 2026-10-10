# Strategia (10 ottobre 2026) — guadagno ed espansione partendo da dove siamo

Scritta da Claude su richiesta di Massimiliano. Vale finché non viene cambiata per iscritto qui (regola 5: le regole non si cambiano a metà). Dettagli e prove negli studi in `intelaiatura/` e in `REGOLE-FISSE.md`.

## 1. Da dove partiamo (fatti)
- Tre siti online a costo zero, aggiornati in automatico: EsameB1 (9/10), EsamiDiStato (10/10), Italy Strikes Today (10/10, registro letto due volte al giorno da GitHub Actions). Routine settimanale del lunedì. Verdetti a 45 giorni: 23-24/11/2026.
- Vincoli: zero costi fissi prima degli incassi; ogni attività commerciale costa ~3.000 €/anno di contributi quando si apre (il "cancello fiscale"); niente email a freddo; tutto il più automatico possibile; **no al lavoro da fotografo** (deciso il 10/10). Capitale: poche migliaia di euro, da usare solo come test con soglia scritta.
- Lezione dei tentativi passati (Etsy, orelab, Scrollcraft, BandiChiari): il problema non è mai stato il prodotto ma la distribuzione. Oggi la distribuzione è Google su domande che la gente fa ogni giorno e a cui nessuno risponde bene in inglese.

## 2. L'idea centrale: un pubblico solo, molti bisogni
**"L'Italia spiegata in inglese a chi ci viaggia o ci si trasferisce"**, poi l'Europa. È il pubblico giusto per tre motivi misurati negli studi: ha soldi (USA/UK/Canada/Australia, pubblicità che vale 3-4 volte quella italiana), ha bisogni che si comprano online (assicurazione, treni, transfer, eSIM, relocation, corsi di italiano), e le pagine che cerca ("today", "tomorrow", "calculator", "how to") non sono presidiate da chi scrive in inglese.
Invece di cercare un'idea nuova ogni volta, si costruiscono **più pagine per lo stesso pubblico** con lo stesso motore (`genera.py` + aggiornamento automatico), e ogni pagina nuova rende più preziose le altre (link interni, lista email unica, stessi partner).

I siti italiani (EsameB1, EsamiDiStato) restano come seconda linea: costano zero, e se passano il test diventano lead-gen per scuole e sedi con consenso separato (studio 8).

## 3. Come si guadagna, in ordine di arrivo
1. **Pubblicità** (AdSense dal giorno 20; Mediavine Journey a 1.000 sessioni Tier 1 in 30 giorni; Raptive a 25.000). Automatica. È il ricavo base di tutte le pagine.
2. **Affiliazione** (Omio, Welcome Pickups, SafetyWing/EKTA, Airalo; ItalianPod101 25 %): riquadro già pronto nel sito scioperi, compare appena arrivano i link. Automatica.
3. **Commissioni di servizio** (relocation: Smart Move Italy o altro partner con cifra scritta ≥ 150 €/cliente) dal sito "Retire / Move to Italy". Automatica dopo l'accordo.
4. **Lista email** (modulo avvisi su ogni sito): è il patrimonio che cresce anche quando la pubblicità rende poco. Fase 2 della visione di Massimiliano: avvisi completi/personalizzati a pagamento (da testare solo con ≥ 500 iscritti; nessun prezzo prima).
5. **Fase 3 (intermediazione)** solo se la fase 2 funziona: mettere in contatto chi viaggia o si trasferisce con chi vende il servizio, con quota da entrambe le parti. Non prima del 2027 inoltrato.

Il cancello fiscale si apre **una volta sola**, quando la somma dei ricavi attesi supera chiaramente i 3.000 €/anno; fino ad allora nessuna attivazione di pagamenti diretti (gli affiliati e AdSense pagano loro, al raggiungimento delle soglie).

## 4. Espansione: lo stesso motore, più Paesi e più strumenti
Ordine deciso dalla domanda misurata (autocomplete USA del 10/10: "france/germany/spain/greece strike today", "europe strikes today" hanno lo stesso schema dell'Italia):
1. **Italia** (fatto): scioperi; poi satelliti **codice fiscale calculator for foreigners** e **ZTL fines by city** (domanda confermata, 2-4 ore ciascuno, stesso pubblico).
2. **Retire / Move to Italy** (sito EN, motore EsameB1): comuni flat tax 7 %, requisiti visto, calcolatore reddito, modulo partner. Si costruisce solo con la commissione scritta.
3. **Francia** → hub **"Europe strikes today"**: test tecnico delle fonti (SNCF, RATP, DGAC/aviazione civile) prima di costruire; passa solo con ≥ 3 fonti ufficiali leggibili in automatico. Poi Germania, Spagna, Grecia, una alla volta, ognuna dopo che la precedente è indicizzata.
4. **Versione italiana degli scioperi** ("sciopero domani [città]", domanda 4-8 volte quella inglese) solo se il test del sito inglese fallisce sulla quota Tier 1 ma Google indicizza.
Regola della catena: **una costruzione nuova ogni 2-3 settimane, mai due insieme; ogni nuova pagina deve avere fonte ufficiale unica o ≤ 3 fonti leggibili in automatico; tutto ciò che non passa il test a 45 giorni si chiude e si scrive perché.**

## 5. Calendario
| Quando | Cosa | Chi |
|---|---|---|
| 10-23/10 | Iscrizioni affiliati, candidatura Smart Move Italy (`DA-FARE-MASSIMILIANO.md`). Domanda fiscale **rinviata al primo pagamento in arrivo** (decisione di Massimiliano del 10/10) | Massimiliano (1,5 ore in tutto) |
| 10-23/10 | Riquadro affiliati online al primo deploy utile; satelliti codice fiscale + ZTL pronti; test tecnico fonti Francia | Claude |
| 23/10 | Lettura Search Console (indicizzazione dei tre siti) → decisione: Francia dentro il sito scioperi oppure "Retire/Move to Italy" per primo (dipende dalla risposta di Smart Move Italy) | Claude propone, Massimiliano dice sì/no |
| ~30/10 | Richiesta AdSense per Italy Strikes Today (se ≥ 20 pagine indicizzate) | Massimiliano (10 min) |
| 23-24/11 | Verdetti a 45 giorni dei tre siti; chiusura di ciò che non passa; eventuale test annunci ≤ 50-100 € sul sito che passa (sì esplicito) | Claude + Massimiliano |
| dic 2026 - feb 2027 | Costruzione Francia (+ Germania/Spagna se la Francia indicizza); Retire/Move to Italy; versione IT scioperi se serve | Claude |
| mar-giu 2027 | Stagione alta dei viaggi: picco scioperi (marzo è il picco storico su Trends); richiesta Journey a 1.000 sessioni Tier 1; primi pagamenti affiliati/AdSense → apertura del cancello fiscale se i ricavi attesi > 3.000 €/anno | Claude + professionista |
| giu 2027 | Revisione della strategia con i numeri di 8 mesi | insieme |

## 6. Numeri prudenti (da non vendere a nessuno come promessa)
- 12 mesi (ott 2027): **500-2.000 €** complessivi (pubblicità + affiliati + 0-2 commissioni relocation), con 1-2 siti chiusi e 4-6 pagine/siti attivi.
- 18-24 mesi: **5-10k €/anno** se l'hub europeo indicizza e passa Journey; sotto i 3k €/anno il cancello fiscale resta chiuso e si continua a costo zero.
- Probabilità onesta: alta che il sistema renda qualcosa, media che superi i 5k €/anno, bassa che arrivi a un reddito pieno. È la somma di molte pagine piccole, non un colpo solo.

## 7. Soldi: come si usano
- **Riserva 3.000 €** per il cancello fiscale: non si tocca per altro.
- **Test annunci**: ≤ 50-100 € per sito, solo dopo l'approvazione AdSense o un accordo partner scritto, con soglia (RPM ≥ 6 $, costo per lead ≤ 1/5 della commissione) e sì esplicito sull'importo.
- **Nessun acquisto** (siti, macchine, abbonamenti, directory): la domanda fiscale è rinviata al primo pagamento in arrivo, quindi il sito-test ≤ 3.000 $ (studio 9) resta fermo fino ad allora. Quando arriva il primo pagamento (AdSense, affiliati o partner) si fa la consulenza gratuita PRIMA di incassarlo.
- Crediti Netlify: max 6 pubblicazioni/mese per sito; se la banda cresce, piano Personal (9 $/mese) pagato dai ricavi, non prima.

## 8. Cosa fa chi
- **Claude**: costruzione, aggiornamenti automatici, lettura settimanale dei numeri, proposte con prove, test tecnici prima di ogni costruzione, chiusure.
- **Massimiliano**: le 2 ore di iscrizioni/candidature/domanda fiscale ora; i 10 minuti di Netlify/Search Console/AdSense per ogni sito nuovo; i sì/no sulle spese e sulle costruzioni. Nessun lavoro continuativo.

## 9. Cosa farebbe cambiare strategia (e va scritto qui prima)
- Google non indicizza nessuno dei tre siti entro il 24/11 → il canale "Google su pagine quotidiane" non funziona per noi: si ferma la catena e si riparte dallo studio (KDP/diritti d'autore resta l'unica alternativa automatica a costo zero).
- Risposta fiscale "tutto commerciale, 3.000 €/anno da subito" → nessun ricavo attivato prima di 3.000 €/anno di run-rate; si continua a costruire la lista e il traffico.
- Un partner paga ≥ 300 €/cliente con cifra scritta → "Retire / Move to Italy" passa davanti a tutto il resto.
