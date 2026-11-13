# EsameB1: universo delle parole chiave (13/11/2026)

**Metodo.** Strumento dei volumi (ricerche mensili medie, Italia salvo dove indicato), 270 interrogazioni: 40 semi, poi le «parole simili» in ordine di volume, poi semi mirati; estero con country=us/gb/ar/br/ua/ro. Raccolte 614 parole italiane (546 con volume) e 113 estere. Molte forme lunghe (città, date, costi: «esame b1 milano», «date esame cils 2026», «costo esame b1 cittadinanza») tornano 0: lo strumento non le conta, la domanda resta quella vista con i suggerimenti di Google e Search Console. Confronto con `esameb1/sito/sitemap.xml` (178 URL) e i titoli.

**Nota.** Varianti vicine hanno spesso lo stesso volume (es. «consulta la pratica cittadinanza» = «cittadinanza consulta pratica» = 4.400): si conta una volta per gruppo.

## Temi mancanti o deboli, per volume

| # | Tema (parola più cercata) | Volume/mese | Prima del 13/11 | Fonte ufficiale che risponde | Fatto il 13/11 |
|---|---|---|---|---|---|
| 1 | Ricongiungimento familiare (requisiti, procedura) | 9.900 | debole: solo `/reddito-ricongiungimento-familiare/` | Ministero, Sportello unico; art. 29 TU | no (prossimo) |
| 2 | Controllo / consulta pratica cittadinanza (K10) | 8.100 · 4.400 · 2.900 | debole: una riga in `/cittadinanza/` | Ministero «consulta la pratica» | **`/pratica-cittadinanza/`** |
| 3 | Requisiti cittadinanza italiana | 8.100 | debole: `/cittadinanza/` parla della domanda | L. 91/1992, DLCI art. 9, Vademecum 2025 | no (titolo/sezione di `/cittadinanza/` da rivedere) |
| 4 | Cittadinanza italiana per matrimonio | 5.400 (+ documenti 1.000, automatica 880, nuove regole 720) | mancante | L. 91/1992 art. 5, DLCI, Ministero | **`/cittadinanza-per-matrimonio/`** |
| 5 | Documenti cittadinanza italiana | 5.400 | debole: lista in `/cittadinanza/` | Ministero «invia la tua domanda» | in parte (matrimonio) |
| 6 | Giuramento cittadinanza | 2.900 (+ 1.600 «… italiana») | mancante | L. 91/1992 art. 10, Vademecum § 3.2, Prefetture | **`/pratica-cittadinanza/#giuramento`** |
| 7 | Permesso di soggiorno lungo periodo (carta di soggiorno) | 2.400 (+ requisiti 720, documenti 720, rinnovo 480, UE 390) | mancante in italiano (c'era solo /en/, /uk/, /ro/) | TU art. 9, Portale Immigrazione cod. 09, Poste | **`/carta-di-soggiorno/`** (hreflang con en/uk/ro) |
| 8 | Test di italiano A2 | 1.900 (+ esame italiano a2 1.300) | debole: sezione in `/esonero-test-italiano/` | Ministero «Test di conoscenza…», Prefettura di Lecco, DM 7/12/2021 | **`/test-italiano-a2/`** |
| 9 | Cittadinanza per residenza | 1.900 | coperto da `/cittadinanza/` | DLCI art. 9 | no |
| 10 | Verifica test di italiano (esito) | 1.600 (+ risultato prefettura 390) | mancante | Ministero (risultato sullo stesso sito) | **`/test-italiano-a2/#esito`** |
| 11 | Decreto cittadinanza | 1.600 | mancante | Vademecum § 3.2 (SEND) | **`/pratica-cittadinanza/#decreto`** |
| 12 | Test lingua italiana B1 cittadinanza online | 1.300 | debole: `/esempi/simulazione/` | enti certificatori | no (titolo da provare) |
| 13 | Test italiano A2 carta di soggiorno esempio | 880 (+ pdf 320) | mancante | Prefettura di Lecco (struttura prove) | **`/test-italiano-a2/#prove`** |
| 14 | Test italiano A2 online gratis | 720 | mancante | Ministero, DM 2021 | **FAQ `/test-italiano-a2/`** |
| 15 | Test lingua italiana B1 per cittadinanza dove farlo | 480 | coperto da home e città | enti | no |

Già coperti (nessuna azione): risultati CILS 1.900 e «online unistrasi riscils» 2.900 (`/risultati/cils/`), cils b1 cittadinanza 1.000, esame b1 italiano per cittadinanza 720, CVCL risultati 880 (`/risultati/celi/`), reddito per cittadinanza 590 (`/reddito-minimo-cittadinanza/`), decreto flussi 14.800 (`/decreto-flussi-click-day/`, titolo sul click day).

## Estero
- **Cittadinanza per matrimonio** è il tema estero più grande: Brasile «cidadania italiana por casamento» 1.600 (+ cônjuge 590), Argentina «ciudadanía italiana por matrimonio» 880, USA «italian citizenship by marriage» 880, Regno Unito 390. Candidato per `/en/` (e forse pt/es) se la pagina italiana prende impressioni.
- USA: «b1 italian test» 260, «italian b1 test» 210, «cils» 1.000. Ucraina/Romania: volumi minimi (≤ 70).

## Prossimi passi
1. Ricongiungimento familiare (9.900): pagina requisiti e procedura dallo Sportello unico e dall'art. 29 TU, collegata alla tabella del reddito.
2. «Requisiti cittadinanza italiana» (8.100): rivedere titolo e prima sezione di `/cittadinanza/`.
3. `/en/italian-citizenship-by-marriage/` se `/cittadinanza-per-matrimonio/` supera 100 impressioni in 30 giorni.
4. Misura a 30 giorni (Search Console): impressioni delle 4 pagine nuove sulle parole della tabella.
