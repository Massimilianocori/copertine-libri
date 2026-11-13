# Verifica indipendente: prefissi telefonici USA (area codes), 13/11/2026

Idea 1 di `fronti-2026-11-13-scoperta-volumi.md` (ricercatore: COSTRUIRE, a 36 mesi 1.150 / 6.300 / 24.100 €/anno, 45 ore, 140 €/ora). Tutto riletto oggi dal server; dove un dato non è stato letto, è scritto. Cambio: 1 $ = 0,92 €. Ricerche di volume usate: circa 160.

## 1. Verdetto

- **RISERVA** (non COSTRUIRE). **Voto 4** su 10.
- **Stima rifatta a 36 mesi: 75 / 950 / 7.100 €/anno** (era 1.150 / 6.300 / 24.100). A 12 mesi: 15 / 190 / 1.400.
- **Resa: 21 €/ora** sulle 45 ore (era 140). Sotto l'asticella dei siti nuovi (5.000 € centrali).
- **I volumi sono veri, anzi più alti. Cade la quota**: quasi tutte le ricerche finiscono nel riquadro di Google, e il "vuoto" indicato dal ricercatore è già coperto da due concorrenti.

## 2. Volumi (campione casuale, non i prefissi famosi)

40 prefissi geografici USA estratti a sorte dai 378 in servizio (file NANPA di oggi, seme fisso), due forme ciascuno.

| Misura | Risultato |
|---|---|
| "NNN area code" | media 75.700 al mese, mediana 74.000 (da 2.400 per il 324 a 201.000 per il 209) |
| "area code NNN" | media 27.100, mediana 13.500; spesso è lo stesso gruppo della prima forma |
| Totale 378 prefissi | **circa 28,6 milioni al mese** (il ricercatore: 20 milioni, prudente) |
| Costo per clic | mediana 1,5 $; 12 prefissi su 40 a 0 $ |
| Prefissi nuovi (235, 324, 369, 679, 728, 948) | 2.400-18.100: dieci volte meno dei vecchi |

Attenzione: lo strumento raggruppa le varianti. "812 area code", "812 area code location", "812 country code", "indiana area code 812" danno tutte 74.000: è **un solo gruppo, non si sommano**.

**Intenzione (8 prefissi, 6 forme):**

| Forma | Volume |
|---|---|
| "NNN area code location" / "where is NNN area code" | dentro il gruppo principale: è la domanda dominante ("dov'è") |
| "what area code is NNN" | 590-3.600 (circa 3 % del gruppo) |
| "NNN area code time zone" | 40-1.000 (sotto l'1 %) |
| "NNN area code scam", "who called me from NNN" | **0 su 8** |
| Sovrapposizioni e prefissi nuovi ("area code overlay" 320, "new area codes" 880, "new area code 2026" 0, "scam area codes" 590) | quasi nulla |

Teste: "area codes" 110.000, "area code lookup" 33.100, Stati 3.600-33.100 ("area codes by state" solo 1.300). Le ricerche con denaro dietro sono altre: "reverse phone lookup" e "phone number lookup" 823.000 l'una, e lì comandano i servizi di ricerca persone.

**Conseguenza:** la domanda misurata è "dov'è questo prefisso", cioè una riga di risposta. I due dati in più proposti (reclami FTC, prossime sovrapposizioni) **non hanno domanda misurabile**.

## 3. Quanti clic restano davvero

- Non ho letto la pagina dei risultati di Google (non si aggirano i blocchi). Ragiono su dati pubblici.
- SparkToro/Similarweb, gennaio-aprile 2026 (letto oggi): il **68 % delle ricerche Google USA finisce senza clic**; era 60 % nel 2024. Per una domanda da una riga con riquadro la quota senza clic è più alta della media.
- Il primo del settore, allareacodes.com (scheda pubblica Semrush, ottobre 2026): 3,3 milioni di visite, solo il 19 % da Google; "347 area code" e "929 area code" valgono lo 0,32 % del traffico l'una, circa 10.600 visite su 246.000 ricerche. **Il primo in classifica prende circa il 4 % delle ricerche.** Le cifre Semrush sono stime e sulla stessa scheda non tornano tra loro: ordine di grandezza, non misura.
- Un sito nuovo senza autorità, contro domini del 1996-2002, sta in prima pagina su pochi prefissi. La quota 0,2 % del ricercatore vorrebbe dire prendere un ventesimo del primo su tutti i 378 prefissi: non realistico a 36 mesi.

## 4. Dati

| Fonte | Letto oggi |
|---|---|
| NANPA, `reports.nanpa.com/public/npa_report.csv` | 200, 117 KB, data 13/11/2026. 378 prefissi geografici USA in servizio: confermato. Campi: Stato, data di servizio, sovrapposizioni, fuso |
| Licenza NANPA | **Non trovata.** `nanpa.com/terms`, `/terms-of-use`, `/legal`: 404. `nationalnanpa.com`: non raggiungibile. Sono fatti (negli USA non protetti), citando la fonte il rischio è basso ma **non c'è un permesso scritto** |
| FTC, API `api.ftc.gov/v0/dnc-complaints` | 200 con chiave dimostrativa (10 chiamate l'ora), 50 righe al massimo per pagina. La pagina della documentazione dice: "None of the information about the reported calls is verified". Il catalogo data.gov la indica come dominio pubblico (visto nel risultato di ricerca, pagina non aperta) |
| **Errore del ricercatore** | Il filtro `area_code` dell'API è il prefisso **di chi reclama**, non di chi chiama (provato su 804: escono chiamanti 978, 908, 804). Il prefisso del chiamante si ricava solo dal numero intero, riga per riga. L'API non dà il totale delle righe |
| Come si farebbe | File CSV giornalieri della FTC (circa 1,3 MB al giorno): si scaricano, si tengono le prime 3 cifre, si buttano i numeri. **Non scaricati**: `ftc.gov` risponde 404 a curl dal server. Fattibile senza pubblicare numeri, ma è un raccoglitore quotidiano in più |
| Limite di sostanza | I numeri dei chiamanti sono in gran parte **falsificati** (stesso prefisso della vittima). "Reclami dal prefisso 804" misura i numeri finti usati, non da dove arrivano le chiamate. Va scritto in pagina; come dato distintivo è debole. Nel campione le righe erano anche doppie |

## 5. Concorrenti (prefisso 804, letti oggi)

| Sito | Dominio dal | Che cosa c'è |
|---|---|---|
| allareacodes.com | 2002 | 403 anche oggi, non letto. 3,3 milioni di visite al mese, autorità 66, 6.300 domini che lo citano (Semrush) |
| areacodes.com | 1996 | 5.250 parole. **Anno di servizio, sovrapposizione 686, fuso, operatori per blocco, riquadro "Scam & Spam Alert", pagina "Who Called Me?", statistiche.** AdSense |
| areacodelocations.info | non letto | 5.240 parole. **"In service since June 24, 1973", complesso 804/686**, mappa, tutti i blocchi con operatore e data, "Phone number lookup — Sponsored". AdSense |
| zip-codes.com | 1998 | 3.150 parole, fuso, ora locale, popolazione, città e contee, aggiornato il 1/11/2026. AdSense |
| area-codes.com | 2002 | 1.300 parole, contee e città, vende la banca dati. AdPushup |
| Wikipedia | – | storia e date complete |

**Che cosa manca davvero a loro:** solo il conteggio dei reclami FTC. Data di servizio e sovrapposizione, che il ricercatore dava come vuoto, **ci sono già** in due siti. Non letti: worldpopulationreview (404), callersmart, whitepages, 411 (403).

## 6. Pagatore

- **Solo pubblicità.** Traffico da telefono, visita da 10 secondi, una pagina: 8-15 $ per 1.000 visite è già generoso. Il costo per clic di 1,5 $ non diventa resa per noi.
- **Affiliazioni di ricerca inversa** (BeenVerified, Spokeo, TruthFinder, Intelius): i programmi esistono (CJ, Impact, FlexOffers) ma **nessuna cifra letta su una pagina ufficiale**; gli elenchi di terzi si contraddicono (da 5 $ a "75 %" a vendita, con storni). Sono il vero pagatore del settore: areacodelocations ha già il loro riquadro sponsorizzato.
- **Restano escluse.** Vendono schede di persone: contro la nostra regola "nessun dato personale". Rischio legale vero: non sono agenzie ai sensi del Fair Credit Reporting Act e non si possono proporre per affitti, assunzioni o credito; la FTC ha sanzionato più volte il settore (Spokeo 2012; TruthFinder e Instant Checkmate 2023, 5,8 milioni di $) anche per abbonamenti poco chiari. Conferma della scelta del ricercatore.

## 7. Conti rifatti

Domanda 28,6 milioni al mese. Quota sulle ricerche (non sui clic).

| | Quota | Visite al mese | $ per 1.000 visite | €/anno |
|---|---|---|---|---|
| 36 mesi, prudente | 0,003 % | 860 | 8 | **75** |
| 36 mesi, centrale | 0,03 % | 8.600 | 10 | **950** |
| 36 mesi, ottimista | 0,15 % | 42.900 | 15 | **7.100** |
| 12 mesi | 0,0006 / 0,006 / 0,03 % | 170 / 1.700 / 8.600 | 8 / 10 / 15 | **15 / 190 / 1.400** |

Centrale: prima pagina su circa un prefisso su dieci, con un quindicesimo dei clic del primo. Ore: 45 per costruire, più circa 1 al mese (raccoglitore FTC, prefissi nuovi). **21 €/ora** al centrale, 158 all'ottimista.

## 8. Rischi

1. Riquadro e risposte automatiche di Google: la quota senza clic sale ogni anno (60 % → 68 % in due anni).
2. 378 pagine dallo stesso modello: rischio "contenuto di scarso valore" per AdSense, già visto sul sito gemello.
3. Dato distintivo debole (numeri falsificati, reclami non verificati) e senza domanda misurata.
4. Serve un dominio (spesa: sì di Massimiliano) oppure un indirizzo netlify.app che in questo settore parte ancora più indietro.
5. Nessun permesso scritto NANPA.

## 9. Che cosa fare

- **Non costruire** il sito e nemmeno la prova da 60 pagine: 15 ore sui 50 prefissi più cercati sono proprio dove i concorrenti sono più forti.
- **La soglia proposta (3.000 impressioni al mese) non prova nulla**: su circa 8 milioni di ricerche coperte dalle 60 pagine è lo 0,04 %, si passa anche in sesta pagina.
- **Si riapre solo così**, se avanzano ore: 20 pagine sui prefissi entrati in servizio dal 2022 (dove i concorrenti hanno poca storia), 6 ore, 60 giorni, soglia **almeno 150 clic al mese e posizione media sotto 12 su almeno 8 pagine**. Sotto soglia si chiude.
- Blocco "CAP per città" (idea 9): resta RISERVA, non ha più il sito a cui agganciarsi.
