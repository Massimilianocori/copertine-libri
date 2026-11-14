**14/11/2026 notte: limiti ricaricati (Fable disponibile, 0 % usato; reset settimanale mercoledì 21:00).** Ricercatori e revisori indipendenti tornano su Fable.

**13/11/2026: seodata Unlimited attivo** (pagato da Massimiliano 4,99 $ + IVA; rinnovo già disdetto: attivo fino al 13/12/2026, poi si torna a 500 ricerche al mese): ricerche di volume SENZA limite. Misurare sempre i volumi veri, senza risparmiare chiamate (resta il divieto di stampare o scrivere la chiave).

> **Volumi di ricerca veri (dal 12/11/2026 sera):** usare `https://api.seodata.dev/v1/keyword?q=<frase>&country=<it|us|gb|de|fr|es…>` (volume medio mensile Google Ads, CPC, frasi simili). Chiave del conto gratuito di Massimiliano (500 ricerche al mese): sta SOLO nel file `/root/.config/seodata/key` del contenitore, fuori dal repository; si passa come `-H "Authorization: Bearer $(cat /root/.config/seodata/key)"`. Mai stamparla, mai scriverla in file del repository, nei commit o nei messaggi. Se il file manca (contenitore nuovo), usare le 20 ricerche gratuite al giorno senza chiave e dirlo. Budget: al massimo ~60 ricerche per ricercatore.

> **Dal 12/11/2026 sera (Massimiliano):** la concorrenza non scarta più un'idea. La prova "nessuno fa meglio" diventa la stima della quota che possiamo prendere (3-15 % con concorrenti forti) × la domanda. Il limite "senza vuoto dimostrato voto massimo 5" NON vale più: il voto dipende dagli euro attesi con quella quota.

# Brief comune per i ricercatori (aggiornato il 7/11/2026)

Repository: /home/user/copertine-libri, branch ccr-b7fd6b9e-n096cr. Lavori per Massimiliano Cori (fotografo, partita IVA forfettaria). Obiettivo unico: fatturato. Massimiliano può metterci ore sue (scritte in numero) e il suo mestiere di fotografo.

**Regola anti-ancoraggio (7/11, Massimiliano: "gira e rigira vai sempre a finire nelle stesse nicchie").** NON partire dai nostri siti né dai modelli che abbiamo già (esami, visti, tasse, viaggi, regole per Stato/Paese, pannelli solari). Le idee devono nascere da FONTI ESTERNE di ciò che cresce o vende adesso, lette con curl, per esempio:
- elenchi "in crescita": Google Trends (pagine pubbliche leggibili), Exploding Topics, classifiche "Movers & Shakers" e "Best Sellers" dei marketplace (Amazon, Etsy, eBay), Product Hunt, App Store/Play top chart pubblici;
- le reti di affiliazione: categorie e programmi con EPC o commissione per cliente più alti (Awin, Impact, CJ, PartnerStack), programmi nuovi del 2026;
- regole e obblighi nuovi con data (EUR-Lex, Federal Register, gazzette nazionali) che creano un acquisto obbligato;
- domande ricorrenti nei forum pubblici (Reddit tramite le pagine pubbliche, Stack Exchange) senza una buona risposta su Google.
Ogni idea deve citare la fonte esterna da cui è nata. Un'idea che somiglia a una riga di ESPLORATE.md si scarta (cerca prima le parole chiave).

Leggi prima: `.claude/skills/rete-siti/SKILL.md`, `studio-business/REGOLE-FISSE.md` (tutte le regole, in particolare quelle del 5-7/11), la fine di `studio-business/intelaiatura/ESPLORATE.md`.

Per ogni idea: domanda reale (autocomplete Google nel Paese giusto: suggestqueries.google.com/complete/search?client=firefox&gl=XX&hl=YY&q=..., con il numero di suggerimenti), composizione dei risultati, chi paga con la cifra letta sulla pagina del programma, stima prudente/centrale/ottimista €/anno a 18 mesi con le assunzioni, ore (agenti e Massimiliano), rischi, voto severo 1-10. Dove va: sezione di un sito esistente o sito/prodotto nuovo (asticella: voto ≥ 7 e ≥ 5.000 €/anno centrali; segnala anche ottimista ≥ 10.000 €).

Vincoli: spese solo con il sì di Massimiliano; niente email a freddo, niente social; nessun dato personale; non aggirare blocchi anti-bot o geo-blocchi; nessun nome di modello AI nei file. NON modificare i siti: solo ricerca.

Consegna: il tuo file in `studio-business/intelaiatura/` (nome indicato nel compito), poi le tue righe in fondo a `studio-business/intelaiatura/ESPLORATE.md`. Commit SOLO dei tuoi file con:
`git add <tuoi file> && git commit -m "Ricerca <data>: <tema>" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01BzC8eDnqLFMycBfFEFEcZf"` e `git fetch -q origin ccr-b7fd6b9e-n096cr`, se il remoto è avanti `git merge -q --no-edit origin/ccr-b7fd6b9e-n096cr` (MAI rebase, stash o autostash), poi `timeout 120 git push -q origin HEAD:ccr-b7fd6b9e-n096cr`. Altri agenti lavorano in parallelo: niente `git add -A` né `git add .`; se ESPLORATE.md è in conflitto, tieni entrambe le parti.

Risposta finale (max 15 righe): le idee con voto, ognuna con la fonte esterna da cui è nata, la migliore, quelle che passano l'asticella.

**Obbligo dal 10/11/2026:** prima di stimare, leggere le pagine dei 3 concorrenti più probabili su 5 esempi concreti e scrivere cosa manca a loro. Senza un vuoto dimostrato il voto massimo è 5. (Tre idee ridimensionate dalla verifica il 10/11: furti di dati, libri di testo, filtri caldaia.)

## Correzioni di metodo (14/11/2026, dopo la notte con voti massimi 6 e 5)
1. **Concorrenti prima del voto:** per ogni idea che supera i filtri di domanda e pagatore, leggere davvero i primi risultati (pagine dei concorrenti raggiungibili, loro data, profondità, fonti) prima di dare il voto; niente quote stimate a occhio sulle idee finaliste.
2. **Fonte bloccata ≠ idea bocciata:** se un dato ufficiale dà 403 o JavaScript, cercare un'altra via legittima (file scaricabile, API ufficiale, pagina gemella, ente diverso) e segnare l'idea «DA RIPROVARE», non NO.
3. **Fuori dall'inglese:** ogni giro grande copre almeno un mercato in spagnolo, tedesco, francese o portoghese, dove la concorrenza è più debole.
4. **Prima chi paga:** partire dai programmi con compenso scritto ≥ 50 $ ad azione e cercare la domanda collegata; è stato l'unico metodo che ha dato idee sopra 5.
