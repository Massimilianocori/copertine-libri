# Higgsfield AI — verdetto finale, confermato dal video ufficiale

2026-09-16. Il video che Massimiliano aveva visto ("I Created 10+ Beauty Ads in 1 Hour — No
Agency Needed", canale ufficiale Higgsfield) è stato analizzato da Gemini (YouTube bloccato in
questo ambiente, vedi nota tecnica in fondo). **Conclusione: il video conferma il problema che
avevamo già trovato coi nostri test, non lo smentisce.**

---

## Il flusso corretto (per la cronaca)

Lo strumento giusto è **Marketing Studio → preset UGC**, non "Create Video" generico né
"Faceless" (che è solo immagini) — su questo la nostra ipotesi era corretta. Il flusso: si carica
1 foto isolata del prodotto + si sceglie un avatar (preset o generato da testo) + si scrive un
prompt breve con lo script — tutto nella stessa richiesta, un solo passaggio, nessun montaggio
esterno.

**Non usa Soul ID** (l'identità allenata da 20+ foto) né multi-immagine di riferimento — solo 1
immagine prodotto per generazione. La promessa di "9 riferimenti in una generazione" letta nei
blog Higgsfield non è quella dimostrata in questo video.

---

## Il punto che conta: la fedeltà del prodotto, testimoniata dal video stesso

`[VERIFICATO, fonte: analisi Gemini del video ufficiale Higgsfield]`

Nei formati **UGC con avatar che tiene/manipola il prodotto**:
> "il prodotto è parzialmente approssimato... i dettagli minuti (il monogramma, la scritta
> esatta dell'etichetta) tendono a fondersi con le dita o a risultare leggermente
> generici/sfocati rispetto alla grafica di partenza."

E sui difetti:
> "quando l'avatar rimuove il tappo o maneggia il tubetto, le dita e il collo del flacone
> mostrano lievi deformazioni plastiche (morphing) anziché un incastro meccanico rigido."
> "le scritte stampate sulle confezioni perdono nitidezza e definizione nei video rispetto ai
> render statici."

**Questo è esattamente il difetto che avevamo diagnosticato e aggirato su Veo** (deformazione
dell'oggetto durante la manipolazione manuale) — qui succede nel video promozionale ufficiale di
Higgsfield, fatto dal loro stesso team per mostrare il prodotto al meglio. Non è un problema che
abbiamo causato noi usando lo strumento sbagliato: è un limite reale e attuale della categoria di
modelli (Veo, Higgsfield, probabilmente altri), non risolto nemmeno nel caso ideale.

**Dove invece la fedeltà regge bene**: i formati **Hypermotion/TV Spot** (nessun avatar, nessuna
mano — il prodotto fluttua/appare via movimenti di camera) mostrano forma, colori e tappi dorati
coerenti con la foto di riferimento. Questo conferma anche l'altra metà della nostra strategia
già in uso: per il prodotto fedele senza mani, il product-only (quello che facciamo con Creatify)
è la strada affidabile — Higgsfield lo conferma sul proprio strumento equivalente.

---

## Verdetto

Non riapriamo l'abbonamento Higgsfield per questo caso d'uso specifico (avatar che manipola il
prodotto con le mani): il video che doveva mostrarcelo fatto bene mostra lo stesso identico
difetto. La soluzione resta quella già adottata: **avatar che parla senza manipolare il prodotto
da vicino (Veo) + demo del prodotto reale senza mani (Creatify) montati insieme**, come deciso in
`10-video-veo3-prompt-pronti.md` e discusso in chat il 2026-09-16.

Non c'è urgenza di testare Higgsfield per altri $9-20: il limite non è "abbiamo usato lo
strumento sbagliato", è un limite di modello condiviso dalla categoria.

---

## Nota tecnica

YouTube è bloccato dalla rete di questo ambiente (Claude Code, sessione cloud) — WebFetch ha
dato `EGRESS_BLOCKED` su youtu.be e youtube.com. L'analisi del video è stata ottenuta chiedendo a
Gemini (che ha accesso diretto a YouTube) un riassunto dettagliato con timestamp, poi incollata
qui per Claude. Non è una nostra osservazione diretta frame-per-frame come per i video Veo, ma un
resoconto di terzi — comunque sufficientemente dettagliato (timestamp, prompt testuali citati
parola per parola) da fidarcene per la decisione presa.
