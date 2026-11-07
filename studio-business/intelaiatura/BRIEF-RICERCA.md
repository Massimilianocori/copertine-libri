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
`git add <tuoi file> && git commit -m "Ricerca <data>: <tema>" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01BzC8eDnqLFMycBfFEFEcZf"` e `git push -q origin ccr-b7fd6b9e-n096cr || (git pull -q --rebase --autostash origin ccr-b7fd6b9e-n096cr && git push -q origin ccr-b7fd6b9e-n096cr)`. Altri agenti lavorano in parallelo: niente `git add -A` né `git add .`; se ESPLORATE.md è in conflitto, tieni entrambe le parti.

Risposta finale (max 15 righe): le idee con voto, ognuna con la fonte esterna da cui è nata, la migliore, quelle che passano l'asticella.
