# Strategia volume outreach — oltre il limite di un solo dominio

2026-09-16. Il problema posto: 5-10 email/giorno da un dominio solo (il ritmo di riscaldamento di
`14-stime-fatturato-mesi-1-3.md`) non bastano a convertire abbastanza in fretta, e Massimiliano non
ha contatti diretti/caldi in USA (vive in Italia, mercato scelto è USA) — quindi la soluzione deve
venire tutta dal canale freddo, scalato bene.

Protocollo: `[VERIFICATO]` con fonte, `[IPOTESI]` altrimenti.

---

## 1. Il vincolo non è "quante email vogliamo mandare", è "quante ne regge UN dominio"

`[VERIFICATO, fonte: Mailpool/FirstSales/Reachly 2026]` Il limite di 5-15 email/giorno che
crescono in 2-4 settimane è per **dominio+mailbox singolo**, non un tetto assoluto dell'attività.
La pratica standard delle agenzie di cold outreach per scalare senza bruciare la reputazione è
**moltiplicare i domini e le caselle in parallelo**, non forzare il volume su uno solo:

- **2-3 mailbox per dominio**, ciascuna con nome realistico (`marco@`, non `sales@`)
- Ogni mailbox: **20-40 email/giorno** dopo il riscaldamento (3+ settimane minimo)
- Regola di dimensionamento: volume giornaliero target ÷ 100 = domini necessari (o ÷ 20-40 =
  mailbox necessarie)
- Ogni dominio nuovo richiede **la stessa configurazione già fatta oggi** su scrollcraft.design:
  MX + SPF + DKIM + DMARC, verificati con MXToolbox prima di mandare la prima email

## 2. Il piano concreto

`[IPOTESI, dimensionata sui numeri sopra]`

1. **Registrare 2 domini aggiuntivi** simili a scrollcraft.design (es. varianti come
   `tryscrollcraft.com`, `scrollcraft.agency` — nomi da verificare disponibilità), ~$10-15/anno
   l'uno. Puntano/reindirizzano al sito principale, non serve un sito diverso per ciascuno.
2. **Una mailbox Namecheap Private Email per dominio** (~$10-15/anno), configurata identica a
   quella di oggi (stesso processo: DKIM auto, SPF auto-verificato, DMARC `p=none` a mano).
3. **Riscaldamento in parallelo, non in sequenza**: i 3 domini (quello principale + 2 nuovi)
   partono tutti a 5-10/giorno nella stessa settimana, invece che aspettare che uno arrivi a
   regime prima di iniziare il prossimo.
4. **Risultato**: dal giorno 1, volume combinato ~15-30 email/giorno invece di 5-10; a regime
   (settimana 3-4), ~75-90/giorno invece di 25-30 — **triplica il piano di
   `14-stime-fatturato-mesi-1-3.md`** senza violare il limite di nessun singolo dominio.

**Nota costi/gestione**: farlo a mano su 3 domini è gestibile per ora (poche decine di email al
giorno in totale), ma se si scala oltre servirà uno strumento di cold email (Instantly, Smartlead,
~$30-97/mese) che gestisce rotazione e monitoraggio bounce/reply su più mailbox insieme — da
valutare solo se il volume manuale diventa ingestibile, non subito.

## 3. Canale parallelo che non dipende dal riscaldamento email: LinkedIn

`[IPOTESI]` LinkedIn ha un proprio limite indipendente (~20-25 richieste di connessione/giorno per
account) che si somma al volume email senza condividerne il rischio di reputazione — se un
prospect non risponde all'email, un secondo touchpoint su LinkedIn (messaggio diretto a
founder/marketing manager del brand) aumenta le probabilità di risposta senza costare volume email
aggiuntivo.

## 4. Canale da verificare: marketplace UGC (inbound, non soggetto a limiti di invio)

`[VERIFICATO, fonte: Billo/Stormy AI/Influencers Time 2026]` Piattaforme come **Billo, Insense,
JoinBrands** funzionano al contrario del cold outreach: il brand pubblica un brief già finanziato
e datato, i creator si candidano. Zero limite di invio, perché non si manda nulla a freddo — si
risponde a chi sta già cercando.

**Attenzione**: questi marketplace sono pensati per creator singoli che girano UGC reale, non per
agenzie che vendono produzione video AI — **non è garantito che il modello si adatti a
Scrollcraft senza modifiche**. Va verificato registrandosi e guardando che tipo di brief
pubblicano prima di investire tempo, non assunto che funzioni.

---

## 5. Priorità operativa

1. Registrare i 2 domini aggiuntivi e configurarne DNS/mailbox (stesso identico processo di oggi)
2. Far partire il riscaldamento dei 3 domini in parallelo questa settimana
3. In parallelo, aprire un profilo LinkedIn per Scrollcraft/Massimiliano e iniziare le prime
   richieste di connessione ai brand della lista prospect
4. Verificare l'idoneità dei marketplace UGC (Billo/Insense/JoinBrands) registrandosi e guardando
   3-5 brief reali prima di deciderne l'uso

## Fonti

- [Mailpool — The Mailbox Rotation Strategy](https://www.mailpool.ai/blog/the-mailbox-rotation-strategy-maximizing-deliverability-across-multiple-domains)
- [FirstSales — Email Domain Rotation: How Many Sending Domains](https://firstsales.io/blog/email-domain-rotation/)
- [Reachly — 7 Inbox Rotation Cold Email Strategies for 2026](https://www.reachly.co/blogs/inbox-rotation-cold-email)
- [Billo — Best UGC Platforms in 2026](https://billo.app/blog/ugc-platforms/)
- [Stormy AI — Sourcing High-ROI Creators: Billo, Insense, JoinBrands 2026](https://stormy.ai/blog/sourcing-high-roi-creators-billo-insense-joinbrands-comparison-2026)
