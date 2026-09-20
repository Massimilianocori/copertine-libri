# Scrollcraft — Stato del progetto (memoria persistente)

> Questo file è pensato per essere letto all'inizio di una NUOVA chat, per non dover rileggere centinaia di messaggi. Contiene fatti stabili, regole operative e stato corrente — non la cronologia della conversazione. Aggiornalo (o chiedi a Claude di aggiornarlo) ogni volta che cambia qualcosa di rilevante.

## Chi e cosa

- **Massimiliano Cori** (corimassimiliano@gmail.com), italiano, non tecnico.
- Business: **Scrollcraft** (scrollcraft.design) — produzione solista di video ad UGC generati con AI per brand DTC (e-commerce) americani.
- Repo di lavoro: `massimilianocori/copertine-libri`, branch `claude/digital-files-business-plan-f8y8gd`.
- Sito live: `digital-business/portfolio/index.html` (+ video `1.mp4`...`10.mp4`, logo, favicon, `privacy.html`).
- Altri documenti di piano nella cartella `digital-business/`: outreach kit, script video campione, comparativa business, piano ecommerce, lista prospect skincare, strategia prezzi, stime fatturato, ecc. (file numerati `01-...` a `17-...`).

## Email di outreach — configurazione tecnica

- Indirizzo mittente: **hello@scrollcraft.design**, configurato come alias "Send mail as" su Gmail tramite SMTP Namecheap Private Email (`smtp.privateemail.com`, porta 587 TLS). Funziona: le mail create con `mcp__Gmail__create_draft` / `send_message` partono automaticamente da questo indirizzo senza specificare nulla, verificato via campo `sender` nelle mail inviate.
- **ATTENZIONE**: prima della configurazione dell'alias (fino al 17/9), alcune email/bozze erano partite dall'indirizzo Gmail personale per errore. Se in Drafts compaiono bozze vecchie con sender `corimassimiliano@gmail.com`, sono quasi certamente residui duplicati di invii già fatti correttamente dopo — controllare nel tracker se il brand è già "Inviato" prima di rimandarle, altrimenti eliminarle.

## Tracker outreach (Google Sheet)

- Nome: **"Scrollcraft - Outreach Tracker"**, fileId: `1emO4s9g4xKBl79JU0NfmKpfkbSBjLAsqiKrFHdum6uk`.
- Colonne: Nicchia, Brand, Email, Oggetto, Stato, Data invio, Follow-up 1 (day 3), Follow-up 2 (day 7), Risposta, Note.
- **Claude non ha accesso in scrittura al foglio** (nessun tool di modifica celle disponibile) — ogni aggiornamento di stato ("Inviato", ecc.) va fatto manualmente da Massimiliano, oppure va segnalato a voce in chat.
- Nel foglio ci sono spesso **righe già ricercate ma non ancora trasformate in bozze** (stato "Da inviare" con email e hook già trovati) — prima di fare nuove ricerche da zero, controllare sempre queste righe: sono un backlog pronto all'uso.
- Righe con FLAG nelle note (es. VC-backed con piccoli round seed) sono da valutare caso per caso, non scartare automaticamente ma non sono la priorità.

## Criteri di selezione brand (outreach)

- Solo brand **founder-owned / bootstrapped / a conduzione familiare**. Scartare quelli con segnali chiari di funding VC/PE importante o agenzia marketing interna grande. Una ricerca mirata per candidato è sufficiente per questo controllo — non serve più di una.
- **Fascia prioritaria** (hook emotivo/storia di trasformazione personale forte → miglior tasso di risposta):
  - Integratori per animali (pet supplements)
  - Skincare bambini / eczema
  - Haircare (caduta capelli, ricrescita, danni)
  - Skincare/beauty femminile
- **Fascia secondaria**: grooming maschile, recovery gear (foam roller ecc.), igiene orale.
- **Fascia bassa priorità** (solo se non si arriva al target dalle prime due): elettroliti/idratazione, sport nutrition, pet care/grooming generico.
- **Da NON usare**: caffè/bevande specialty, gadget da cucina/casa (mancano di un hook "problema risolto" emotivo).
- Per ogni brand serve un **hook specifico e genuino**: una recensione cliente concreta su una trasformazione reale, una storia del fondatore, o un dettaglio di prodotto specifico — mai claim generici.

## Protocollo di ricerca email (importante — causa di un fallimento passato)

- Per ogni brand promettente, fare **almeno 2-3 ricerche mirate diverse** prima di rinunciare a trovare l'email (query tipo "[dominio] contact us", "[brand] customer service email", "[brand] press contact", ecc.).
- Se si trova il dominio ma non un'email esplicita, si può usare un pattern info@/hello@/support@ + dominio **solo se ci sono segnali di supporto** sul sito stesso (altre pagine che citano un formato email simile, contact page che menziona "email" senza darla, ecc.) — mai inventare senza alcun segnale.
- Non passare troppo tempo a verificare lo stato di funding oltre una ricerca ragionevole per brand.
- Se un candidato forte non ha email trovabile dopo sforzo reale, sostituirlo con un altro candidato piuttosto che lasciare un buco nel target giornaliero.

## Formato email di outreach (fisso, usato sempre)

```
Oggetto: [hook specifico in poche parole]

Hi [Brand] team,

[1-2 frasi che citano il dettaglio/hook specifico trovato]

I'm Massimiliano, I make short AI video ads for DTC brands — a few examples here: www.scrollcraft.design. Happy to build a free sample around it if useful.

Best,
Massimiliano
```

## Routine automatica giornaliera

- Trigger id: `trig_01FQTjpGhpFALewwcAE4ac8V`, nome "Scrollcraft daily outreach research + drafts" (ri-agganciato il 20/9, il precedente `trig_01FyXBJeb5FXSqyZMLTseYAJ` puntava a una sessione ormai chiusa ed è stato eliminato e ricreato — `update_trigger` non permette di cambiare la sessione agganciata, va rifatto con delete_trigger + create_trigger).
- Cron: `0 7 * * *` (UTC, le 07:00 ogni giorno).
- **È agganciato a UNA sessione specifica** (persistent_session_id = questa sessione: `session_01N4SsNUgx6UyDCxNf1LooSj`). Se si abbandona questa sessione/chat, la routine smette di funzionare finché non viene ri-agganciata (elimina il trigger e ricrealo con lo stesso nome/cron/prompt, dalla nuova sessione).
- Nota tecnica: `create_trigger` non passa i connector (Gmail/Drive) della sessione chiamante per questa organizzazione — è normale, il prompt del trigger include già il controllo che si ferma e segnala il problema se i tool non sono disponibili al risveglio, invece di fallire in silenzio.
- Obiettivo: 15 nuove bozze/giorno, seguendo i criteri sopra. **Non invia mai da sola** — crea solo bozze in Gmail Drafts, poi manda un messaggio di riepilogo chiedendo revisione/approvazione a Massimiliano.
- Limite noto della piattaforma: non è garantito che l'accesso ai connector (Gmail/Drive) sia sempre disponibile al momento dello scatto del trigger — il prompt del trigger include un controllo esplicito che si ferma e segnala il problema invece di fallire in silenzio.
- Storico: nei primi run reali la routine ha prodotto meno bozze del target (5/15, poi 9/15) — cause diagnosticate: abbandono troppo rapido della ricerca email su candidati validi, e limite ambientale (vedi sotto) sul recupero di contatti per domini piccoli. Il prompt del trigger è stato aggiornato con il protocollo di ricerca email più rigoroso sopra descritto per correggere questo.

## Limiti tecnici noti dell'ambiente (da tenere a mente)

- **WebFetch è bloccato** per domini piccoli/sconosciuti (es. shopsimpure.com, freedomjointdrop.com, piccoli negozi Shopify) — la ricerca contatti deve basarsi solo sugli snippet di `WebSearch`, mai su fetch diretto della pagina.
- **LibreOffice (`soffice`) e Poppler (`pdftoppm`) sono rotti in questo ambiente** — impossibile generare anteprime PDF/immagine di file .docx per verifica visiva. Verifica alternativa usata: integrità zip (`unzip -t`) + XML (`xmllint --noout`) in locale, poi upload su Google Drive e lettura di conferma con `read_file_content`/metadata (confronto dimensione byte).
- `npm install docx` va eseguito manualmente nella scratchpad prima di usare lo skill docx (nonostante la doc dello skill dica che è preinstallato).

## Upwork

- Partita IVA e registrazione VIES (Comunicazione operatore intracomunitario via Agenzia Entrate) completate — verificate anche sul checker ufficiale UE (ec.europa.eu/taxation_customs/vies/).
- Stato validazione VAT ID su Upwork: bloccato su "Invalid" nonostante VIES lo dia valido. Ticket #55547453: il supporto Upwork ha risposto il 19/9 (17:59 CET) confermando che il VAT risulta ancora "rejected" internamente e ha escalato per **verifica manuale**, con ETA dichiarata di 48h (quindi risposta attesa entro ~21/9 pomeriggio) — non ripresentare il VAT nel frattempo, aspettare la risposta sullo stesso ticket.
- Criteri di valutazione lavori Upwork usati finora: preferire fixed-price a hourly; guardare la **tariffa media oraria realmente pagata dal cliente** (storico reale), non il range dichiarato nell'annuncio — è il segnale vero; distinguere "AI video generation" da "traditional video editing" (skill mismatch); trattare "$0 spesi / 0% hire rate" come rischio reale ma talvolta da tentare comunque; preferire iniziare con una milestone/test a pagamento piccola invece di impegno hourly open-ended con clienti non verificati; **uno storico di tariffa media bassa predice un lowball futuro indipendentemente da come è scritto l'annuncio specifico** (intuizione corretta di Massimiliano, confermata).

## Politica trademark/endorsement sui video del portfolio pubblico

- Un video "spec ad" fatto su misura per un brand specifico, mandato in privato a QUEL brand come pitch, è a basso rischio.
- Lo STESSO asset mostrato sul portfolio pubblico per attirare ALTRI clienti è un uso diverso e più rischioso (rischio di endorsement/affiliazione implicita).
- Soluzione adottata: **due versioni** dello stesso video — una col branding reale del cliente (solo per outreach privato diretto a quel cliente), una de-brandizzata con end card generica Scrollcraft (per il portfolio pubblico su scrollcraft.design). Sfondo end card generica: beige del sito (`#F1EFE7` / `--bg2`), non nero, per leggibilità.

## Outlier.ai

- Massimiliano si è iscritto come valutatore per Outlier.ai (piattaforma di training/valutazione AI).
- Gli è stato preparato e consegnato un CV adattato (reframed per enfatizzare esperienza pratica con AI generativa nel business Scrollcraft, mantenendo tutti i fatti veri) — caricato su Google Drive come **"CV Massimiliano Cori - Outlier.docx"** (fileId `11Ki01V1kMHDYR99WF_E7T585Sw2JMlCQ`) e consegnato anche come file in chat.
- Consiglio dato: fare prima lo screening/test di competenza in **italiano** (madrelingua, unico disponibile al momento), poi eventualmente quello in inglese quando sarà sbloccato (più volume di progetti ma più competizione).
- Le istruzioni/interfaccia della piattaforma sono in inglese; i contenuti specifici del test di una competenza linguistica (es. italiano) sono verosimilmente nella lingua testata.
- **Aggiornamento 20/9**: verifica d'identità **approvata** da Outlier (email di conferma ricevuta). Esito del test di screening in italiano ancora da verificare — nessuna email di risultato trovata finora.

## Cose in sospeso / da verificare

- [x] Le 15 bozze outreach del 20/9 confermate presenti in Gmail Drafts (verificato 20/9) — ancora in attesa di revisione/invio manuale da parte di Massimiliano.
- [x] Trigger daily outreach ri-agganciato il 20/9 a questa sessione (`trig_01FQTjpGhpFALewwcAE4ac8V` → `session_01N4SsNUgx6UyDCxNf1LooSj`).
- [x] **20/9 — svuotato il backlog "Da inviare" del tracker**: 21 bozze aggiuntive create da righe già ricercate in giorni precedenti (email/hook già trovati, mai trasformati in draft): Organic Muscle, SuperGreen Tonik, Cure Hydration, Arrival Wellness, Dog is Human, stubble & 'stache, Four Leaf Rover, Bernie's Best, Under the Weather Pet, VitaHound, Pawstruck, Kin+Kind, Nutra Thrive, Finn, Swolverine, NutraBio Labs, Hoist Hydration, Elete Electrolytes, Pacific Shaving Company, RAD Roller, Mountaineer Brand. Totale bozze in attesa di revisione ora: **36** (15 giornaliere + 21 backlog).
- [ ] **Priorità massima per fatturare**: revisionare e inviare i 36 draft in Gmail — è il collo di bottiglia attuale, non la ricerca. Claude non invia automaticamente senza autorizzazione esplicita (policy ripetuta nel prompt del trigger).
- [ ] Aggiornare manualmente il tracker Google Sheet con le 15+21 bozze del 20/9 (non ancora presenti, ultimo aggiornamento foglio: 18/9) e per ogni invio effettivo (Claude non può scrivere sul foglio).
- [ ] Risposta ticket Upwork VAT ID: escalato per verifica manuale il 19/9, ETA 48h (~21/9) — ricontrollare la mail/il ticket #55547453.
- [ ] Verificare risultato del test di screening Outlier in italiano (identità già approvata il 20/9).
- [ ] La routine daily outreach scatterà di nuovo domani (21/9, 07:00 UTC) — controllare risultato ed eventualmente completare manualmente se sotto le 15 bozze target (c'è backlog pronto nel tracker, vedi sopra).
- [ ] Se si apre una nuova chat "leggera": ricordarsi di ri-agganciare il trigger `trig_01FQTjpGhpFALewwcAE4ac8V` alla nuova sessione (delete_trigger + create_trigger, vedi sezione Routine sopra), altrimenti la routine giornaliera si ferma.
