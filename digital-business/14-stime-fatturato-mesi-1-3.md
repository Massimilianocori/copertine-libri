# Stime di fatturato — mesi 1-3, aggiornate al 2026-09-15

Rifatte dopo le scoperte di oggi: il riscaldamento email impone un ramp-up di 2-4 settimane
sull'outreach (non si può partire a pieno volume da subito), e i prezzi/costi sono quelli
effettivamente in vigore ora (`11-strategia-prezzi.md`). Protocollo: `[VERIFICATO]` con fonte,
`[IPOTESI]` altrimenti — qui quasi tutto è ipotesi, perché **non abbiamo ancora inviato una sola
email reale**: sono stime da ricalibrare sui primi dati veri, non previsioni certe.

---

## 1. Il vincolo che cambia tutto: il riscaldamento email

`[VERIFICATO]` Un dominio nuovo deve partire con 5-10 email/giorno e salire gradualmente in 2-4
settimane prima di poter mandare volumi pieni, pena finire in spam. Questo non è aggirabile con
nessuno strumento — decide il server di chi riceve, non noi.

**Volume di invio stimato, mese per mese `[IPOTESI]`**:

| Mese | Ritmo | Email inviate nel mese |
|---|---|---|
| 1 | Riscaldamento: 5→15/giorno crescente | ~300 |
| 2 | Riscaldamento completato: 20-25/giorno | ~650 |
| 3 | Regime: 25-30/giorno | ~800 |

Sostenere questo volume richiede una lista prospect molto più grande delle 34 attuali — va
alimentata con ricerca continua (altre nicchie adiacenti al men's grooming), altrimenti si esaurisce
prima di arrivare a regime.

---

## 2. Tassi di conversione — verificati, non inventati

`[VERIFICATO, fonte: Instantly/Woodpecker/Martal 2026]`:
- Tasso di risposta medio B2B: **3,4-5,8%** (liste piccole e mirate fanno meglio, fino al 5,8%)
- Tasso di chiusura (email → cliente pagante): **~0,2% medio**, cioè 1 cliente ogni 464 email
- Best-in-class con ICP stretto + offerta forte: **2-3%**

**La nostra posizione stimata `[IPOTESI]`**: lista piccola e mirata (favorevole) + campione gratuito
su misura come incentivo reale (differenziatore concreto, non nella media dei cold email generici)
→ ci posizioniamo sopra la media generica ma sotto il best-in-class, finché non abbiamo dati veri.

| Scenario | Tasso di risposta | Risposte → clienti paganti | Tasso di chiusura netto |
|---|---|---|---|
| Pessimistico | 4% | 10% | **0,4%** |
| Base | 6% | 18% | **1,1%** |
| Ottimistico | 8% | 25% | **2,0%** |

---

## 3. Mix di prodotto per i nuovi clienti `[IPOTESI, da ricalibrare]`

Un prospect contattato a freddo, alla prima chiusura, sceglie quasi sempre l'ingresso più basso, non
un abbonamento: **50% Singolo ($179), 35% Starter ($845), 15% Growth ($1.890/mese)**. Nessuno passa
a Scale al primo acquisto.

---

## 4. Le tre proiezioni

**Costi fissi mensili**: Netlify $9 (da valutare se tenere), Stripe ~2,9%+$0,30 a transazione.
Higgsfield ($15) è escluso: cancellazione già decisa.

### Mese 1 — ~300 email, ramp-up in corso

| Scenario | Nuovi clienti | Mix | Ricavo lordo | Costi | **Netto** |
|---|---|---|---|---|---|
| Pessimistico | ~1 | 1 Singolo | $179 | ~$14 | **~$165** |
| Base | ~3 | 2 Singolo + 1 Starter | $1.203 | ~$45 | **~$1.158** |
| Ottimistico | ~6 | 3 Singolo + 2 Starter + 1 Growth | $3.917 | ~$125 | **~$3.792** |

### Mese 2 — ~650 email, riscaldamento completato

| Scenario | Nuovi clienti | Ricavo nuovo | + Ricorrente da Growth mese 1 | **Netto totale** |
|---|---|---|---|---|
| Pessimistico | ~3 | ~$537 | +$0 (nessun Growth ancora) | **~$520** |
| Base | ~7 | ~$2.807 | +$1.890 (1 Growth da mese 1) | **~$4.550** |
| Ottimistico | ~13 | ~$8.483 | +$1.890 | **~$10.100** |

### Mese 3 — ~800 email, regime

`[CORRETTO 2026-09-16]` Il tetto di capacità usato in una versione precedente di questo file
(~25 ore/mese, ~$3.800/mese) era un residuo dell'ipotesi "side project part-time" e non riflette
la disponibilità reale: **~40 ore/settimana** (~173h/mese). Con la stessa ripartizione già usata
per lo scenario full-time (~65% produzione, resto outreach/admin) → **~112h/mese di produzione
effettiva**, a ~45 min/video → **~150 video/mese teorici**, scontati per iterazioni/tentativi
falliti a un tetto realistico di **~$12.000-17.000/mese**.

Con questo tetto corretto, **la produzione non è più il collo di bottiglia nei primi 3 mesi**,
nemmeno nello scenario ottimistico — resta la domanda (trovare abbastanza clienti) il vincolo
reale, non le ore disponibili.

| Scenario | Domanda stimata | **Ricavo realistico col tetto corretto (~$12-17k/mese)** |
|---|---|---|
| Pessimistico | ~$1.400 | ~$1.400 (ben sotto il tetto) |
| Base | ~$6.700 | ~$6.700 (sotto il tetto, nessun problema) |
| Ottimistico | ~$16.000 | ~$16.000 (dentro o al limite superiore del tetto — non più "fortemente limitato") |

---

## 5. La lettura onesta di questi numeri

- **Lo scenario pessimistico è il più probabile finché non abbiamo dati veri**: siamo un dominio
  nuovo, zero track record, zero recensioni. Aspettarsi lo scenario base o ottimistico al mese 1 è
  ottimismo non supportato da dati.
- **Il vincolo reale resta "trovare clienti", non "avere ore per servirli"** — corretto il tetto
  di capacità (~$12-17k/mese, non ~$3.800), anche lo scenario ottimistico del mese 3 rientra quasi
  del tutto nella produzione disponibile. Il problema di capacità tornerebbe rilevante solo oltre
  questi volumi, o se emerge la strada dei contatti diretti/warm intro discussa in sessione (che
  punta a riempire la capacità con pochi clienti di qualità invece che centinaia di email fredde).
- **Il numero da monitorare per primo non è il fatturato, è il tasso di risposta reale** dei primi
  100-150 email mandate — quello ci dice in quale scenario siamo, molto prima che si vedano i
  risultati in fatturato.
- Questi numeri **vanno ricalcolati dopo le prime 2 settimane di invii reali** — sono una stima di
  partenza, non un piano da seguire alla cieca.

## Fonti

- Instantly — Cold Email Reply Rate Benchmarks 2026: https://instantly.ai/blog/cold-email-reply-rate-benchmarks/
- Martal — B2B Cold Email Statistics 2026: https://martal.ca/b2b-cold-email-statistics-lb/
- Woodpecker — Cold Email Statistics (20M+ email inviate): https://woodpecker.co/blog/cold-email-statistics/
