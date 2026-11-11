# Verifica indipendente: sito polacco "codici ufficiali per le imprese" (PKD + KSeF), 11/11/2026

Idea verificata: un solo sito in polacco con (a) una pagina per codice PKD, con il passaggio PKD 2007 → PKD 2025 (scadenza 31/12/2026) e note su IVA, registratore di cassa e imposta forfettaria; (b) una pagina per codice di errore o di stato del KSeF. Fonti dell'idea: `fronti-2026-11-11-polonia.md` (idea 1) e `fronti-2026-11-11-mercati-nuovi.md` (idea 1). Stima del ricercatore: 110 / 1.950 / 18.600 €/anno.

## Verdetto: NO-GO come sito nuovo. Voto 4 su 10. Centrale rivisto: circa 175 €/anno (da 1.950).

Passano due prove su quattro. I dati sono ottimi e la domanda c'è, ma **il pagatore su cui poggiava la stima non ci accetta** e **il vuoto è più piccolo di quanto scritto**: il concorrente principale ha già il passaggio vecchio → nuovo per ogni codice. In più un dominio nuovo pubblicato il 1° dicembre non fa in tempo a prendere il picco di dicembre-febbraio.

| Prova | Esito | Perché |
|---|---|---|
| 1. Domanda reale | **SÌ** | autocomplete gl=pl pieno su quasi tutti i codici provati; ma la domanda principale per codice è l'aliquota forfettaria, non il passaggio |
| 2. Dati leggibili | **SÌ** per il PKD, **A METÀ** per il KSeF | PKD: 656 codici vecchi, 728 nuovi, 1.084 collegamenti estratti dal PDF ufficiale. KSeF: 75 codici ma descrizioni di 60 caratteri, nessun rimedio nella fonte |
| 3. Pagatore attivo a cui possiamo iscriverci | **NO (non dimostrato)** | Fakturownia esclude per regolamento chi non è polacco; wFirma è riservato ai propri clienti; resta iFirma, a cifra fissa una tantum |
| 4. Nessuno lo fa già meglio | **NO** | pkd.pl (inFakt) risponde già "codice vecchio → codici nuovi" per ogni codice e ha l'aliquota forfettaria con dati propri |

## 1. Dati (letti oggi con curl)

**PKD.** `klasyfikacje.stat.gov.pl/static/pkd_25/pdf/KlasyfikacjaPKD2025.pdf` risponde 200 (8,3 MB; 3,2 MB di testo con `pdftotext -layout`). Parte IV (riga 23.875 del testo) = passaggio 2007 → 2025; parte V = 2025 → 2007. Con una sola espressione regolare sulle righe che iniziano con un codice:

- 656 codici vecchi, 728 codici nuovi, **1.084 coppie vecchio → nuovo**;
- 471 codici vecchi hanno un solo codice nuovo, **185 si dividono** (119 in due, 29 in tre, 17 in quattro, 6 in cinque, 14 in sei o più);
- controlli a campione, tutti coerenti con il testo: 62.01.Z → 62.10.A, 62.10.B; 43.21.Z → 43.21.Z; 49.41.Z → 49.41.Z, 52.24.C; 56.10.A → 56.11.Z; 43.39.Z → sette codici (43.23.Z, 43.31.Z … 81.22.B); 96.02.Z → 96.21.Z, 96.22.Z; 70.22.Z → 70.20.Z; **47.91.Z → 37 codici** (il codice resta ma cambia significato);
- la colonna "**" segna il collegamento semplificato uno a uno, cioè quello usato per la riclassificazione d'ufficio (per 62.01.Z è 62.10.B): leggibile, ma su celle a più righe, da controllare riga per riga.

Limite vero: **non esiste una fonte ufficiale che leghi il codice PKD all'aliquota forfettaria, all'IVA o all'obbligo di registratore di cassa**. L'aliquota dipende dal tipo di ricavo (PKWiU), non dal PKD. È proprio la parte più cercata (vedi punto 3) ed è quella che non possiamo scrivere da un dato.

Licenza: il PKD è l'allegato a un regolamento del Consiglio dei ministri (Dz.U. 2024 poz. 1936); gli atti normativi e i documenti ufficiali in Polonia non sono coperti da diritto d'autore (art. 4 della legge sul diritto d'autore: **non riletto oggi**, da confermare prima di qualsiasi costruzione).

**KSeF.** `api.ksef.mf.gov.pl/docs/v2/openapi.json` risponde 200 (652 KB, 63 percorsi, nessun campo licenza). Estratti **75 codici** distinti dalle tabelle delle descrizioni (il ricercatore ne contava 78). Le descrizioni sono in polacco ma brevissime: mediana **60 caratteri** per riga. Esempi: 445 = "Błąd weryfikacji, brak poprawnych faktur" e basta; 440 ha tre significati diversi secondo il contesto (duplicato, sessione annullata, operazione non permessa); 415 quattro; 450 dieci. **Nessun rimedio nella fonte**: i "passi per risolvere" andrebbero scritti da noi, in polacco, su un tema fiscale. Pagine da 60 caratteri di contenuto ufficiale sono pagine sottili.

## 2. Concorrenti (il punto decisivo)

Google.pl non è leggibile; la lettura delle pagine di ricerca di altri motori con curl è stata bloccata dalle regole dell'ambiente e non è stata aggirata. Metodo usato: ricerca web (indice americano, 4 ricerche) + lettura diretta delle pagine e delle sitemap dei concorrenti.

**Fatto nuovo rispetto al ricercatore: pkd.pl ha già il passaggio.** Il ricercatore ha scritto "passaggio assente (0 occorrenze di 2007)". Le pagine dei codici vecchi non sono nella sitemap, ma esistono: `pkd.pl/kod/62.01.z` risponde 200 con titolo "PKD 62.01.Z - nieaktualny kod" e il testo "Kod 62.01.Z jest nieaktualny. Został zastąpiony przez: 62.10.A …, 62.10.B …" con la descrizione di ogni codice nuovo. Verificato su 5 codici vecchi: 62.01.Z (2 nuovi), 43.39.Z (tutti e 7), 56.10.A (56.11.Z), 96.02.Z (96.21.Z, 96.22.Z), 70.22.Z (70.20.Z): **gli stessi collegamenti del PDF ufficiale**. Oggi quelle pagine hanno `noindex` e canonical verso la home, quindi non compaiono su Google: il vuoto esiste solo finché inFakt non toglie una riga di codice.

### PKD: chi dà che cosa (10 codici)

Codici letti: 62.01.Z → 62.10.B, 47.91.Z, 43.21.Z, 49.41.Z, 56.10.A → 56.11.Z, 43.39.Z → 43.31.Z, 74.20.Z, 96.02.Z → 96.21.Z, 68.20.Z, 85.59.B.

| | pkd.pl (inFakt; 679 pagine per codice 2025, sitemap di oggi) | pkd.com.pl (iFirma) | GUS `klasyfikacje.stat.gov.pl` | biznes.gov.pl | klasyfikacje.gofin.pl | Articoli (pit.pl, fakturowo.pl, studi legali) |
|---|---|---|---|---|---|---|
| Passaggio vecchio → nuovo | **Sì, 5 su 5 codici vecchi provati**, ma pagine non indicizzabili | No (pagine dei codici nuovi vuote: 365 caratteri) | Strumento ufficiale, applicazione JavaScript (non leggibile a curl) | Ricerca ufficiale, JavaScript; in CEIDG accanto al codice nuovo compare il vecchio | Chiavi di passaggio in PDF (parti IV e V) | Solo esempi sparsi; uno studio legale riporta un codice sbagliato |
| Aliquota forfettaria | **Sì, 10 su 10**, con la percentuale dei loro clienti per regime | No | No | No | No | Per categoria, non per codice |
| IVA | No (0 su 10) | Accenno generico (2 occorrenze per pagina) | No | No | No | No |
| Registratore di cassa, PKWiU | No (0 su 10) | No | No | No | No | No |
| "Comprende" | Sì, breve (1.500-2.600 caratteri a pagina) | **Sì, completo, per i codici 2007** (6.000-9.000 caratteri) | Sì | Sì | Sì | – |
| "Non comprende" | **No (0 su 10)** | Sì, per i codici 2007 | Sì | Sì | Sì | – |

Che cosa resta davvero libero: una pagina indicizzabile per ogni codice vecchio con "si divide in N, quale ti assegnano d'ufficio", la trappola dei codici che restano ma cambiano significato (47.91.Z), "non comprende" per i codici 2025. Che cosa NON possiamo dare meglio di loro: aliquota forfettaria, IVA e registratore di cassa per codice (nessuna fonte ufficiale; inFakt ha i dati dei propri clienti e i contabili).

`pkd2025.pl` esiste ma è un WordPress vuoto ("Hello world!", aprile 2025): qualcuno ha preso il nome, nessun contenuto.

### KSeF: chi dà che cosa (6 codici)

| Codice | Fonte ufficiale (openapi) | fakturowo.pl (aiuto) | wFirma (pagina errori, 27.600 caratteri) | Fakturownia (pagina errori e modalità offline, 20.700 caratteri) |
|---|---|---|---|---|
| 440 | 3 significati, senza rimedio | pagina dedicata con rimedio | citato una volta | citato 4 volte |
| 415 | 4 significati | pagina dedicata | assente | assente (la ricerca web la riporta in un'altra loro pagina) |
| 450 | 10 significati | assente nelle pagine lette | assente | **18 occorrenze, con rimedio** |
| 445 | una riga | assente | assente | assente |
| 21180 | 3 messaggi | assente | assente | assente |
| 21301 | 5 messaggi | assente | assente | assente |

I tre codici più cercati (440, 415, 450) sono già spiegati, con il rimedio, da chi vende il programma. La coda (445, 21xxx) è libera ma la fonte dà una riga sola e la cerca soprattutto chi programma un'integrazione, cioè chi non compra un programma di fatturazione.

**I pagatori sono anche i concorrenti**: inFakt possiede pkd.pl, iFirma possiede pkd.com.pl, wFirma e Fakturownia hanno le pagine sugli errori del KSeF. Il sito porterebbe traffico a chi ha già la stessa pagina.

## 3. Domanda (autocomplete Google gl=pl hl=pl, 31 domande, oggi)

- Per codice, 10 suggerimenti su 10: 62.01.z, 47.91.z, 43.21.z, 49.41.z, 43.39.z, 70.22.z, 68.20.z, 41.20.z; 9: 96.02.z, 73.11.z; 8: 62.10.b; 7: 56.10.a; 5: 86.90.a; 4: 01.11.z (i codici rari hanno poca domanda).
- **Che cosa chiedono**: su 10 suggerimenti per codice, 3-5 sono "jaki ryczałt / stawka ryczałtu", 1-2 "VAT", 1 "co obejmuje", 0-1 "kasa fiskalna", 1 "PKWiU", e **uno solo** riguarda il passaggio ("nowy kod", "2025", "nowe pkd"). La domanda dominante è quella a cui non abbiamo una fonte e a cui pkd.pl risponde già.
- Passaggio: "pkd 2007 na 2025" 10 (konwersja, kalkulator, klucz, mapowanie, wyszukiwarka), "nowe kody pkd" 10 (anche "2027", "do kiedy zmienić"), "konwerter pkd" 5, "stare pkd na nowe" 4, "zmiana pkd 2025 do kiedy" 3.
- KSeF: "ksef błąd" 10 e "ksef status 4" 10 (elenco di codici), ma **ogni codice da solo ha 1 suggerimento** ("ksef błąd 440" 1, 415 1, 450 1, 445 1; "ksef 21180" 3): domanda sottile per pagina.

**Stima delle visite (metodo dichiarato, non misura).** Non esiste un contatore di volumi leggibile. Ragionamento: sito nuovo, dominio nuovo, lingua nuova, tema fiscale; davanti ci sono un dominio a nome esatto (pkd.pl), due siti ufficiali e i portali fiscali. Con circa 1.400 pagine e una quota realistica di clic sulla coda lunga: prudente 500 visite al mese, centrale 3.000, ottimista 20.000 (media su 18 mesi). Il ricercatore usava 18.000 al mese centrali sommando i due siti: non c'è nessun elemento letto che lo sostenga.

**Stagionalità.** Scadenza 31/12/2026 (Dz.U. 2024 poz. 1936), riclassificazione d'ufficio dal 1/1/2027: picco dicembre-febbraio, poi la domanda sul passaggio cala ("nowe kody pkd 2027" esiste: un po' di coda resta). Un dominio pubblicato il 1° dicembre ha le prime pagine indicizzate in 2-4 settimane e traffico vero dopo mesi (lo schema della rete: "Avvio 0-30 giorni: prime pagine indicizzate"): **arriva dopo il picco**.

## 4. Soldi (pagine e regolamenti riletti oggi)

| Programma | Cifra | Possiamo iscriverci? (testo del regolamento) |
|---|---|---|
| **Fakturownia** | 30 % per 24 mesi; soglia 100 zł; fattura | **NO.** Regolamento: partecipazione "esclusivamente" per persone fisiche con attività registrata in Polonia **e cittadinanza polacca**, oppure enti con sede in Polonia; pagamento "solo in PLN e solo su conti di banche che operano in Polonia"; "non paga su conti esteri" |
| **wFirma** | 30 % di ogni pacchetto, senza limite di tempo; link valido 90 giorni; fattura ogni trimestre, pagata in 7 giorni | **Non dimostrato.** Il programma è "per i nostri clienti": si entra da dentro il conto wFirma scegliendo l'azienda da iscrivere, che viene verificata contro un regolamento **visibile solo dentro il sistema**; la fattura si emette dal sistema wFirma (campi PKWiU e aliquota forfettaria polacca). Esiste una pagina "program afiliacyjny" (registrazione con codice), stesso regolamento interno |
| **iFirma** | **una tantum**: 100 zł studio contabile, 50 zł contabilità online, 10 zł Faktura+; attribuzione con link o codice inserito entro 30 giorni dalla registrazione; fattura sopra 500 zł (sotto, fattura a parte), pagata in 14 giorni | **Forse.** Serve un conto gratuito iFirma e un'attività d'impresa; nessuna clausola "solo Polonia" nel testo letto; vale il diritto polacco. Da chiedere per email prima di contarci |
| AdSense | resa per 1.000 visite non leggibile: **assunzione 2,5-4 €** | Sì |

Conseguenza: la provvigione ricorrente del 30 % (su cui il ricercatore calcolava circa 40 € a cliente) **non è disponibile**. Resta al massimo iFirma: circa 50 zł ≈ 12 € a cliente, una volta sola.

**Formula:** €/anno = visite all'anno ÷ 1.000 × (resa pubblicità + resa affiliazione).

| Scenario | Visite/mese | Pubblicità €/1.000 | Affiliazione €/1.000 | €/anno |
|---|---|---|---|---|
| Prudente | 500 | 2,5 | 0 | **15** |
| Centrale | 3.000 | 3 | 1,85 (1 cliente iFirma ogni 6.500 visite × 12 €) | **circa 175** |
| Ottimista | 20.000 | 4 | 3 (1 cliente ogni 4.000 visite × 12 €) | **circa 1.680** |

Ore stimate per farlo bene: 50-70 (1.400 pagine in polacco, controllo riga per riga della tabella, due revisioni) → **circa 3 €/ora al centrale**, la resa più bassa della riserva.

## 5. Rischi

1. **Lingua e materia (il più grande insieme al pagatore).** Polacco non controllato da un madrelingua su un tema fiscale: la parte che possiamo scrivere senza rischio è solo il testo ufficiale, che GUS, biznes.gov.pl, gofin e pkd.com.pl pubblicano già.
2. **inFakt apre le pagine dei codici vecchi a Google** (togliere `noindex`): il vuoto si chiude in un giorno.
3. **Finestra**: picco dicembre-febbraio, dominio nuovo dal 1° dicembre.
4. **Accuratezza**: 185 codici divisi, celle su più righe; un errore manda un'impresa sul codice sbagliato.
5. **Manutenzione KSeF**: l'API cambia versione; ogni cambio va riletto.

## 6. Domini (RDAP, oggi; 404 = libero; controllo: pkd.pl 200)

| Nome | .com | .pl |
|---|---|---|
| kodyfirmowe | libero | libero |
| nowekodypkd | libero | libero |
| pkdksef | libero | libero |
| kodydlafirm | libero | registrato |

Non serve comprarli: verdetto NO-GO.

## Che cosa farebbe cambiare il verdetto

- una risposta scritta di iFirma o wFirma che accetta un'impresa italiana (partita IVA con VIES) e paga su IBAN estero, **e**
- un revisore madrelingua, **e**
- partenza su un dominio che ha già fiducia (non uno nuovo a dicembre).

Senza tutte e tre resta in riserva. Nessun piano di costruzione: non è un GO.

## Differenze rispetto al ricercatore

| Punto | Ricercatore | Verifica |
|---|---|---|
| Passaggio su pkd.pl | assente | presente per ogni codice vecchio provato (pagine non indicizzabili) |
| Fakturownia | "sì in linea di principio" | esclusa per regolamento |
| wFirma | "sì in linea di principio" | riservata ai clienti, regolamento non leggibile |
| Codici KSeF | 78 | 75, con mediana di 60 caratteri di testo |
| Centrale | 1.950 €/anno | circa 175 €/anno |
| Voto | 5,5 (PKD) e 5 (KSeF) | 4 |
