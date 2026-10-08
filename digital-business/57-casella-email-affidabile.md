# 57 — Casella email affidabile per l'outreach (studio dell'8/10/2026)

Problema: `hello@scrollcraft.design` è su Namecheap Private Email. Oggi (8/10) webmail inaccessibile ("Temporary Accessibility issue"). Da qui partono 40-50 email fredde al giorno verso agenzie USA (Gmail "Invia come" → `smtp.privateemail.com:587`). Se la casella si ferma, si ferma la vendita.

Fonti interne lette: `CLAUDE.md`, `ERRORI.md` (21, 26), `PROCEDURE.md` (righe 109-115, 132), `00-STATO-PROGETTO.md` (riga 27: le bozze create con il connettore Gmail partono da hello@ in automatico; riga 100: P.IVA iscritta al VIES).

Legenda: **[V]** verificato con fonte (URL). **[V debole]** fonte secondaria, forum o dato con date incerte. **[I]** mia ipotesi o deduzione.

---

## 1. Quanto è affidabile Namecheap Private Email

- [V] Incidenti Private Email sulla pagina di stato Namecheap: 15/8 webmail (~12 ore), 20/8 webmail, 21/8 gestione caselle, 10/9 webmail + IMAP/POP3 irraggiungibili, 15/9 webmail, 19/9 manutenzione, 3/10 webmail **e anche IMAP/SMTP** (risolto 14:29 UTC). https://www.namecheap.com/status-updates/temporary-issues-with-the-private-email-service-october-3-2026/ · https://www.namecheap.com/status-updates/?p=103703 · https://www.namecheap.com/status-updates/?p=103868
- [V debole] 13-14/8/2026: guasto grande (raffreddamento datacenter Phoenix), Private Email ferma circa 28 ore, né invio né ricezione. Fonte terza: https://blog.incidenthub.cloud/namecheap-outage-aug-13-2026 · pagina IncidentHub: https://incidenthub.cloud/status/namecheap/private-email
- [V debole] Gli incidenti del 28/9 e dell'8/10 li riporta Massimiliano. Nella ricerca non risultano ancora sulla pagina di stato.
- [V] Namecheap non pubblica uno SLA di uptime per Private Email (nessuno trovato).
- [I] Conto: almeno 8 incidenti in 8 settimane, uno al 3/10 che ha toccato anche l'invio SMTP. Il problema è strutturale, non un caso.
- [V] Nota positiva: in quasi tutti gli incidenti di webmail Namecheap scrive che la consegna della posta non è toccata (es. 15/9). La posta in arrivo non si perde: i server mittenti riprovano per ore o giorni.

## 2. Limiti di invio e regole sul cold email

| Servizio | Limite ufficiale | Cold email | Fonte |
|---|---|---|---|
| Namecheap Private Email (piani nuovi dal 2/6/2026: Launch/Expand/Scale) | 500/ora per casella; prova 20/ora; max 50 destinatari per email | Nessuna regola specifica trovata; Namecheap indaga le segnalazioni di spam e può sospendere | [V] https://www.namecheap.com/support/knowledgebase/article.aspx/10811/2306/new-email-sending-and-usage-limits-for-private-email/ · https://www.namecheap.com/support/knowledgebase/article.aspx/10184/5/how-does-namecheap-investigate-suspected-email-abusespam |
| Google Workspace | 2.000 email/giorno per utente; 2.000 destinatari esterni unici/giorno; in prova 500; finestra mobile di 24 ore | Vietato "unsolicited mass email ... solicitations"; le policy amministratore definiscono spam l'invio non richiesto a "significant numbers" di indirizzi senza rapporto. Chi manda spam può essere bloccato in invio in modo permanente | [V] https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace · https://workspace.google.com/terms/use_policy.html · https://workspace.google.com/intl/en_uk/terms/standard_program_policies/ |
| Zoho Mail | 50-500 email/ora verso l'esterno, **dinamico** in base alla reputazione; invio massivo non ammesso | Blocchi automatici; alcuni non sbloccabili dall'admin | [V] https://www.zoho.com/mail/help/adminconsole/rates-and-limits.html · https://www.zoho.com/mail/help/usage-policy.html |
| Microsoft 365 | ~10.000 destinatari/giorno per casella; tetto tenant 10.000 esterni/giorno con 1 licenza (prova 5.000) | Spam vietato dalle condizioni | [V] https://mc.merill.net/message/MC1023294 · [V debole] https://prospeo.io/s/office-365-sending-limits |

- [V] Su Namecheap il limite reale osservato il 6/10 era ~20/ora (era ancora in prova: 20/ora/casella, coincide). ERRORI 26.
- [V debole] Utenti Zoho riferiscono blocchi dopo 6-8 email. https://help.zoho.com/portal/en/community/topic/reason-for-the-block-mail-rate-exceeded-limit · https://help.zoho.com/portal/en/community/topic/cold-emails-not-allowed
- [V debole] Prassi del settore: 20-30 (max 40-50) email fredde al giorno per casella. Noi siamo nel limite alto. https://mailshake.com/blog/secondary-domains-the-essential-guide-for-safe-scaling/ · https://mailreach.co/blog/google-workspace-email-sending-limits
- [I] Tutti e quattro vietano lo spam con parole simili. Il rischio di sospensione dipende da reclami e rimbalzi, non dal fornitore. 40-50 email singole e personalizzate al giorno, con rimbalzi bassi (Apollo verifica), sono lontane da "mass email". Rischio basso, non zero.

## 3. Affidabilità degli altri

- [V] Google Workspace: SLA scritto 99,9% al mese (~44 minuti di fermo al mese), con crediti se mancato. https://workspace.google.com/terms/sla-20250130/
- [V debole] Google ha avuto incidenti (es. errori estesi su Gmail e Docs per ~3 ore), ma rari. Elenco date non verificato. https://statusgator.com/services/google-workspace/outage-history?page=4
- [I] Microsoft 365: SLA 99,9% anch'esso. Ma il nostro flusso passa da Gmail ("Invia come" + connettore Gmail della routine). Microsoft sta togliendo l'accesso SMTP con password semplice: "Invia come" da Gmail rischierebbe di smettere di funzionare. Non verificato in questa ricerca.
- [I] Zoho: limiti dinamici e blocchi segnalati a basso volume. Inadatto al nostro uso.

## 4. Prezzi per 1 casella

| Servizio | Prezzo | Fonte |
|---|---|---|
| Namecheap Private Email Launch | $14,88/anno (~€13), forse prezzo di 2 anni; piano di Massimiliano da verificare | [V] https://www.namecheap.com/support/knowledgebase/article.aspx/10789/2306/new-private-email-plans-comparison/ |
| Google Workspace Business Starter | **€8,10/mese flessibile** (disdetta quando si vuole) o €6,80/mese annuale (vincolo 12 mesi) | [V] https://workspace.google.com/intl/it/pricing · https://knowledge.workspace.google.com/admin/billing/compare-flexible-and-annual-fixed-term-payment-plans?hl=it |
| Microsoft 365 Business Basic | €6,07/mese annuale (prezzo prima dell'aumento di luglio 2026) | [V debole] https://www.microsoft.com/it-it/microsoft-365/exchange/compare-microsoft-exchange-online-plans |
| Zoho Mail Lite | ~$1-1,25/mese (prezzo EUR non trovato) | [V debole] https://www.capterra.com/p/174694/Zoho-Mail/pricing/ |

- [V debole] Forfettario con P.IVA nel VIES: la fattura di Google Ireland arriva senza IVA. Va integrata (TD17) e si versa il 22% con F24, non detraibile. Dal D.Lgs. 81/2025 il versamento sarebbe trimestrale. Da confermare col commercialista. https://flextax.it/commercialisti-online/come-devo-comportarmi-per-lintegrazione-delliva-sullacquisto-di-un-servizio-da-google-ireland/ · https://focus.namirial.com/it/regime-forfettario-e-reverse-charge/
- [I] Costo reale Workspace flessibile: €8,10 + 22% = **€9,88/mese, ~€119/anno**. Differenza con Namecheap: ~€105/anno.
- [I] Un giorno di outreach perso = 40-50 contatti in meno. Basta un cliente in più all'anno per ripagare la differenza molte volte.

## 5. Cosa comporta il cambio verso Google Workspace

DNS su Namecheap (Domain List → Manage → Advanced DNS; il DNS è separato da Private Email e funziona anche oggi).

- [V] **MX**: togliere gli MX di Private Email; mettere un solo MX `smtp.google.com`, priorità 1, host `@` (account Workspace creati dopo aprile 2023). Su Namecheap usare "Custom MX". https://support.google.com/googlecloud/answer/11237746?hl=en · https://www.namecheap.com/support/knowledgebase/article.aspx/322/2237/how-can-i-set-up-mx-records-for-my-domain/
- [I] **SPF**: durante il passaggio, un solo record TXT con entrambi: `v=spf1 include:spf.privateemail.com include:_spf.google.com ~all`. Dopo 2 settimane si toglie `spf.privateemail.com`. (Copiare il valore Namecheap esatto dal record attuale prima di modificarlo.)
- [V debole] **DKIM**: si genera la chiave in Admin console (Gmail → Autentica email), si aggiunge il TXT `google._domainkey`, poi "Avvia autenticazione". Il vecchio `privateemail._domainkey` si lascia finché Private Email è attiva.
- [I] **DMARC**: non cambia. Passa con SPF e DKIM allineati su `scrollcraft.design`.
- [V] **Verifica dominio**: record TXT `google-site-verification` richiesto da Google in fase di attivazione.
- [V debole] **Gmail "Invia come"**: si tiene nel Gmail personale (la routine e il connettore Gmail restano uguali). Si cambia solo il server: `smtp.gmail.com:587`, utente `hello@scrollcraft.design`, password = **password per le app** (serve la verifica in 2 passaggi sull'account Workspace). https://connect.ucsb.edu/training-support/connect-user-guides/google-workspace-email/app-passwords-to-send-mail-as
- [I] **Inoltro**: nel Gmail Workspace di hello@ si attiva l'inoltro a `corimassimiliano@gmail.com` (codice di conferma arriva al Gmail personale).
- [V] **Vecchia posta**: Google Data Migration Service copia via IMAP dalla casella Namecheap, gratis, senza cancellare l'origine. https://knowledge.workspace.google.com/kb/how-to-set-up-data-migration-service-to-migrate-emails-000007279
- [V] **Fermo**: i record Namecheap valgono in ~30 minuti; Google avvisa fino a 48 ore. In quella finestra la posta arriva a volte a Namecheap, a volte a Google. https://www.namecheap.com/support/knowledgebase/article.aspx/322/2237/how-can-i-set-up-mx-records-for-my-domain/
- [I] Fermo reale per noi: **zero**, se Private Email resta attiva (è già pagata) e i due inoltri portano tutto al Gmail personale.
- [I] **Reputazione**: Gmail misura soprattutto la reputazione del dominio firmato DKIM (`scrollcraft.design`), che resta la stessa. Cambiano solo gli IP: da quelli condivisi Namecheap a quelli Google, di solito migliori. Rischio basso se SPF e DKIM sono a posto prima del primo invio.
- [V debole] In prova (14 giorni) il limite è 500/giorno: basta per 50. https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace
- [V debole] Alcune fonti dicono che un account nuovo ha limiti ridotti finché non ha pagato $100. Non confermato da Google. Per 50/giorno non conta. https://expandi.io/blog/email-warmup/

## 6. Alternativa: tenere Private Email e aggiungere un secondo dominio di invio

- [V debole] È prassi comune: dominio simile (es. `getscrollcraft.com`), 2-3 caselle per dominio, 20-30 email al giorno per casella, **14-21 giorni di riscaldamento** prima di usarlo. https://mailshake.com/blog/secondary-domains-the-essential-guide-for-safe-scaling/ · https://emailbison.com/blogs/cold-email-secondary-domains
- [V debole] Costi tipici: dominio ~$10-15/anno [I, prezzo .com Namecheap non verificato oggi] + casella (Namecheap ~$15/anno, Google €8,10/mese) + strumento di riscaldamento $15-29/mese (utilità contestata). https://www.smartlead.ai/blog/email-warmup-service-cost
- [I] Perché non ora: **non risolve il problema** (se è su Namecheap, cade insieme); ferma o divide l'outreach per 2-3 settimane; il dominio principale ha già la storia d'invio. Ha senso solo quando si vuole salire oltre ~50 al giorno o se la reputazione di `scrollcraft.design` peggiora.

---

## 7. RACCOMANDAZIONE

**Passare `hello@scrollcraft.design` a Google Workspace Business Starter, piano flessibile (€8,10/mese + IVA in reverse charge ≈ €9,88), subito: si attiva oggi e il cambio MX si fa stasera dopo il giro di invii. Private Email resta attiva fino a scadenza come riserva, poi non si rinnova.**

Motivo: Namecheap ha avuto ~8 incidenti in 8 settimane, uno anche sull'invio SMTP, e non ha SLA. Google ha SLA 99,9%, limiti larghi (2.000/giorno, niente blocco a 20/ora) e il nostro flusso resta in Gmail. Zoho e Microsoft sono scartati (§2-3). Il secondo dominio non risolve i guasti (§6).

### Passi di Massimiliano (~40 minuti, oggi)

1. workspace.google.com → "Inizia" → Business Starter, 1 utente, dominio esistente `scrollcraft.design`, utente `hello`. Dati fiscali: P.IVA (fattura senza IVA da Google Ireland). Scegliere piano **flessibile**.
2. Attivare la verifica in 2 passaggi su `hello@scrollcraft.design` e creare una **password per le app** (myaccount.google.com → Sicurezza). Tenerla per il punto 6.
3. Namecheap → Advanced DNS: aggiungere il TXT di verifica che mostra Google. Non toccare ancora gli MX. Avvisarmi: controllo io che sia visibile.
4. Admin console Google → Gmail → Autentica email → Genera nuovo record (2048 bit) → incollare in Namecheap il TXT `google._domainkey`. Dopo 1 ora: "Avvia autenticazione".
5. **Stasera, a giro finito**, in Namecheap: Mail Settings → Custom MX → un solo record `@` → `smtp.google.com` priorità 1. Aggiornare l'SPF come al §5 (con il valore che gli preparo io).
6. Gmail personale → Impostazioni → Account e importazione → "Invia messaggio come" → hello@ → Modifica info → server `smtp.gmail.com`, porta 587, TLS, utente `hello@scrollcraft.design`, password per le app.
7. Gmail di hello@ (Workspace) → Impostazioni → Inoltro → `corimassimiliano@gmail.com`.
8. (Facoltativo, 10 minuti) Admin console → Migrazione dati → IMAP `mail.privateemail.com` per copiare la vecchia posta.
9. Fra 30 giorni, se tutto va: si può passare al piano annuale (€6,80) e non rinnovare Private Email. Avvisare il commercialista della fattura Google Ireland (integrazione IVA).

### Cosa faccio io (costo zero)

- Prima del punto 5: controllo DNS pubblico di TXT verifica, DKIM `google._domainkey`, MX attuali; preparo il record SPF esatto.
- Dopo il punto 5: controllo propagazione MX e SPF.
- Dopo il punto 6: chiedo un'email di prova a Gmail e leggo gli header (`spf=pass`, `dkim=pass` con `d=scrollcraft.design`, `dmarc=pass`), come da ERRORI 21.
- Dopo il punto 7: verifico che il codice di conferma inoltro e un'email di prova in arrivo compaiano nel Gmail personale.
- Primo giro su Google: stessi tetti giornalieri (25/30/40 → 50) e stessa distanza (1 email ogni 3-4 minuti) finché un giro completo non passa senza errori; poi aggiorno `PROCEDURE.md` ed `ERRORI.md` 26.
- Tengo d'occhio `from:mailer-daemon` e i rimbalzi per i primi 7 giorni.
- Fra 2 settimane: tolgo `spf.privateemail.com` dall'SPF (lo propongo, lo fa Massimiliano).

## 8. Rischi

- [I] **Sospensione Google per cold email**: rischio basso a 40-50 email personalizzate al giorno. Riduzione: niente liste comprate, verifica Apollo prima dell'invio, rimbalzi sotto 2%, riga per non ricevere altre email, stop immediato a chi chiede di non essere contattato, mai oltre 50/giorno da questa casella.
- [I] **Unico punto di guasto**: tutto il business su una casella. Se un giorno si vuole salire oltre 50/giorno, allora secondo dominio (§6), con uno studio nuovo.
- [I] **Errori DNS al cambio** (SPF doppio, DKIM mancante): mitigato dai miei controlli prima e dopo ogni passo e dalla prova degli header prima del primo invio vero.
- [I] **Posta divisa nelle prime 48 ore**: nessuna perdita finché Private Email e il suo inoltro restano attivi.
- [V debole] **IVA**: costo +22% non detraibile e un adempimento in più (integrazione fattura, F24). Da confermare col commercialista.
- [I] **Spesa doppia per qualche mese**: Private Email già pagata (~€13/anno) va persa. Trascurabile.
