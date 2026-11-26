# Registro dei rischi e degli errori

Creato il 26/11/2026. Massimiliano: «il tuo lavoro deve tenere conto delle variabili, di Google, dei tuoi errori e li devi aggiustare».

Regola: ogni errore mio o ogni variabile esterna che costa visite o soldi entra qui il giorno stesso. Ogni riga ha la correzione fatta e il controllo automatico che impedisce di ripeterlo. Ogni lunedì si rilegge il registro e si aggiorna la colonna «stato».

## Errori miei

| Data | Errore | Danno misurato | Correzione | Controllo che lo impedisce | Stato |
|---|---|---|---|---|---|
| 8-13/11 | 3 domini cambiati insieme e centinaia di pagine toccate nella stessa settimana, senza piano dei rischi | Google da 701 a ~178 visite/settimana sui 3 siti | Strategia di recupero (8,6), sitemap a indice e vecchi indirizzi, link interni | Regola «CAMBI DI DOMINIO»: uno alla volta, piano dei rischi prima | in recupero, indicatore ogni lunedì |
| 19-23/11 | Calo attribuito alla stagione senza verificarlo | giorni persi | Regola «ERRORE DEL 19-23/11»: calo >30 % verificato lo stesso giorno | riassunto del lunedì, soglia −30 % | chiuso |
| ottobre-25/11 | Codice AdSense su pagine a modello quasi senza testo unico (filtro sulle parole totali) | BYF respinto per «Low value content» | Soglia sulle parole uniche nel generatore (26/11) | verifica.py di ogni sito, audit AdSense | correzioni in corso |
| 23/10-25/11 | Italy Strikes con data «aggiornato 23 ottobre» per un mese | fiducia e freschezza | data vera del controllo, fonte di riserva dichiarata | salute.py: fonte primaria ferma più di 3 giorni | chiuso |
| fino al 26/11 | 9 siti senza routine di aggiornamento | dati che invecchiano | routine nel calendario | salute.py: «routine saltata» | chiuso |
| fino al 26/11 | Previsione «37.035 €/anno» mostrata come previsto (era potenziale a 36 mesi) | aspettative sbagliate | riga del mattino = piano a 12 mesi sui dati veri | prompt del riassunto del mattino | chiuso |
| 25/11 | lastmod mosso dalla sola data di controllo (EsameB1, BYF) | segnali poco affidabili a Google | impronta senza le frasi di data | revisione indipendente su ogni pubblicazione | chiuso |
| 25/11 | Agente che salva e io che riprovo dopo il blocco | pubblicazione ferma una notte | gli agenti non salvano più, salvo io | regola nei brief | chiuso |

## Variabili esterne (non dipendono da noi, ma vanno seguite)

| Variabile | Come la misuro | Cosa faccio se cambia |
|---|---|---|
| Aggiornamenti di Google (core update, spam update) | Google Search Central Status; indicatore del lunedì (visite Google ÷ picco) | calo >30 %: verifica lo stesso giorno (tecnica, indicizzazione, posizioni) prima di cambiare qualcosa |
| Indicizzazione delle pagine | Controllo URL e foto di Search Console (28/11, 2/12, 9/12) | richieste di indicizzazione mirate; sfoltimento previsto il 2/12 se sotto il 30 % |
| Criteri AdSense | ADSENSE-AUDIT-2026-11-26.md; email di AdSense (Gmail in sola lettura) | correggere prima di chiedere la revisione; mai richiedere senza la lista dei criteri tutta verde |
| Domanda stagionale (esami, scioperi) | calendari ufficiali; picchi in Search Console | pagine fresche 2-3 giorni prima dei picchi (es. Italy Strikes il 2/12 per lo sciopero del 4/12) |
| Fonti ufficiali che cambiano formato o bloccano | salute.py, script di raccolta | non pubblicare dati non verificati; adattare lo script; data vera in pagina |
| Assistenti AI (ChatGPT) come fonte di visite | GoatCounter, provenienze | pagine con dato, fonte e data in apertura e file ufficiali |
| Costi (piano, Netlify, domini) | crediti Netlify, riassunto del lunedì | rete sotto il piano prudente per 2 mesi: proposta di taglio dei costi |
