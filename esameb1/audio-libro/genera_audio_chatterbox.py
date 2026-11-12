"""Rende le 17 tracce del libro con Chatterbox Multilingual V3 (Resemble AI, MIT), voce clonata da due clip
sintetiche Kokoro-82M (Apache-2.0): voci/ref-F.flac (if_sara) e voci/ref-M.flac (im_nicola). Nessuna persona reale.
Stesse regole di lettura di genera_audio.py (Kokoro): ogni testo UNA volta, numeri degli elementi detti, pause uguali.
Ogni pezzo (frase o gruppo di frasi) viene ritrascritto con faster-whisper «small» e rigenerato se la somiglianza
con il testo è sotto SOGLIA (al massimo TENTATIVI volte; poi resta il migliore e finisce nel riepilogo).

Uso: python genera_audio_chatterbox.py TRACCE.txt CARTELLA_USCITA [numeri tracce...]
Ambiente (12/11/2026): Python 3.11, torch 2.6.0 CPU, chatterbox-tts dal GitHub (commit ab55923, serve per il modello
"v3"), faster-whisper 1.2.1, setuptools<81 (per il watermark Perth), ffmpeg con rubberband. Variabile THREADS = thread torch.
Le clip di riferimento sono state fatte con kokoro 0.9.4 (lang_code "i", speed 0.95) leggendo RIF_TESTO."""
import re, sys, json, subprocess, tempfile, os, time, difflib, unicodedata
from pathlib import Path
import numpy as np, soundfile as sf, librosa, torch

os.environ.setdefault("TQDM_DISABLE", "1")

torch.set_num_threads(int(os.environ.get("THREADS", "4")))
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel

QUI = Path(__file__).resolve().parent
RIF = {"F": QUI / "voci" / "ref-F.flac", "M": QUI / "voci" / "ref-M.flac"}
RIF_TESTO = ("Buongiorno a tutti. Oggi vi leggo alcune frasi in italiano, con calma e con una pronuncia chiara. "
             "Ascoltate bene e ripetete dopo di me.")
SOGLIA, TENTATIVI = 0.95, 4
MAX_CARATTERI = 200  # frasi raggruppate fino a ~200 caratteri per pezzo (oltre, il modello è meno stabile)

F, M, M2, F2 = "F", "M", "M2", "F2"  # M2/F2: stessa voce un po' più grave (due voci uguali nello stesso dialogo)
NARRATORE = M
VOCI = {"Impiegata": F, "Signor Okafor": M, "Uomo": M, "Donna": F, "Autista": M, "Responsabile": F, "Ahmed": M,
        "Maestra": F, "Mamma": F, "Vicina": F, "Giornalista": M, "Svetlana": F, "Lei": F, "Lui": M, "Segretaria": F,
        "Signora": F, "Commessa": F, "Luca": M, "Marco": M2, "Figlio": M, "Collega": F, "Lavoratore": M,
        "Infermiera": F, "Ragazzo": M, "Agente": M, "Impiegato": M, "Candidato": M, "Insegnante": F, "Papà": M}
VOCI_TRACCIA = {5: {"Cliente": F, "Farmacista": M, "Mamma": F2}, 11: {"Cliente": M, "Signora": F2}, 12: {"Cliente": M}, 14: {"Cliente": F, "Farmacista": F}}
VOCE_ELEMENTI = {1: [F], 2: [M], 4: [F, F, M, M], 6: [M, F], 7: [M, F], 8: [F], 10: [F, M, M, F],
                 13: [M, F, F, M, M, F], 16: [M, F, M, F, M, F, M], 17: [F, M, M, F, F]}
PAUSA = {4: 3, 5: 10, 6: 30, 11: 10, 14: 10}
PAUSA_DEFAULT = 5
PAUSA_BATTUTA = 0.6
PAUSA_FRASE = 0.3
PAUSA_DOPO_NUMERO = 1.2

# testo → testo da pronunciare (prima dei numeri in lettere)
TESTO = [("06 4427 1830", "zero sei, quarantaquattro ventisette, diciotto trenta"), ("B1", "bi uno"),
         ("Saidi", "Saìdi"), ("Kovač", "KOVAC"), ("Termoservice", "Termosèrvis"), ('"', "")]
KOVAC = "Kòvaci"  # /ˈkɔvatʃi/: con «Kòvač» o «Kòvac» la trascrizione dà «Kovac» (c finale dura)

UNITA = "zero uno due tre quattro cinque sei sette otto nove dieci undici dodici tredici quattordici quindici sedici diciassette diciotto diciannove".split()
DECINE = {2: "venti", 3: "trenta", 4: "quaranta", 5: "cinquanta", 6: "sessanta", 7: "settanta", 8: "ottanta", 9: "novanta"}


def lettere(n):
    """Numero intero (0-9999) in lettere, italiano."""
    if n < 20:
        return UNITA[n]
    if n < 100:
        d, u = DECINE[n // 10], n % 10
        if u in (1, 8):
            d = d[:-1]
        s = d + (UNITA[u] if u else "")
    elif n < 1000:
        c, r = n // 100, n % 100
        s = "cento" if c == 1 else UNITA[c] + "cento"
        if r // 10 == 8:
            s = s[:-1]
        s += lettere(r) if r else ""
    else:
        m, r = n // 1000, n % 1000
        s = ("mille" if m == 1 else lettere(m) + "mila") + (lettere(r) if r else "")
    return s[:-3] + "tré" if n > 20 and s.endswith("tre") else s


def numeri_in_lettere(t):
    return re.sub(r"\d+", lambda m: ("zero " + lettere(int(m.group()[1:])) if len(m.group()) > 1 and m.group()[0] == "0" else lettere(int(m.group()))), t)


def da_dire(t):
    for a, b in TESTO:
        t = t.replace(a, b)
    return numeri_in_lettere(t).replace("KOVAC", KOVAC)


def normalizza(t):
    """Per il confronto con la trascrizione: minuscole, niente accenti né punteggiatura, numeri in lettere."""
    # numeri di telefono trascritti come «06-44-27-1830»: a coppie di cifre, come sono detti
    t = re.sub(r"\b0\d(?:[- ]\d{2,4})+\b", lambda m: " ".join(g[i:i + 2] for g in re.split(r"[- ]", m.group()) for i in range(0, len(g), 2)), t)
    t = re.sub(r"(\d)[.:,](\d)", r"\1 \2", t)
    t = numeri_in_lettere(t.replace("’", "'").replace("%", " per cento")).lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z]+", " ", t).split()


def confronto(t):
    """Testo di riferimento per il controllo: com'è detto, ma con le grafie normali dei nomi."""
    t = da_dire(t)
    for a, b in (("Termosèrvis", "Termoservice"), (KOVAC, "Kovac"), ("bi uno", "B1")):
        t = t.replace(a, b)
    return t


def somiglianza(rif, trascr):
    a, b = normalizza(rif), normalizza(trascr)
    parole = difflib.SequenceMatcher(None, a, b).ratio()
    lettere_ = difflib.SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    return max(parole, lettere_)


def silenzio(s):
    return np.zeros(int(SR * s), dtype=np.float32)


def frasi(testo):
    return [x for x in re.split(r"(?<=[.!?])\s+", testo.strip()) if x]


def gruppi(testo):
    out, cur = [], ""
    for fr in frasi(testo):
        prova = (cur + " " + fr).strip()
        if cur and len(prova) > MAX_CARATTERI:
            out.append(cur)
            cur = fr
        else:
            cur = prova
    return out + ([cur] if cur else [])


def taglia(a):
    """Toglie il silenzio iniziale e finale del pezzo (soglia -50 dB), lasciando 40 ms."""
    _, (i, j) = librosa.effects.trim(a, top_db=50, frame_length=512, hop_length=128)
    m = int(SR * 0.04)
    return a[max(0, i - m):min(len(a), j + m)]


def pezzo(g, voce, seme):
    """Un gruppo di frasi: genera, ritrascrive, rigenera se serve. Ritorna l'audio migliore."""
    vera = {M2: M, F2: F}.get(voce, voce)
    MODELLO.conds = CONDS[vera]
    dire, rif = da_dire(g), confronto(g)
    migliore = None
    for k in range(TENTATIVI):
        torch.manual_seed(seme * 10 + k)
        t0 = time.time()
        a = MODELLO.generate(dire, language_id="it").squeeze().numpy().astype(np.float32)
        sec = time.time() - t0
        a = taglia(a)
        segs, _ = WHISPER.transcribe(librosa.resample(a, orig_sr=SR, target_sr=16000), language="it", beam_size=5)
        trascr = " ".join(s.text for s in segs).strip()
        s = somiglianza(rif, trascr)
        prova = {"voce": voce, "testo": g, "detto": dire, "tentativo": k + 1, "somiglianza": round(s, 3),
                 "trascrizione": trascr, "durata": round(len(a) / SR, 2), "secondi_cpu": round(sec, 1)}
        print(f"   [{voce} t{k + 1} {s:.3f} {len(a) / SR:4.1f}s/{sec:4.0f}s] {g[:60]}", flush=True)
        if migliore is None or s > migliore[0]["somiglianza"]:
            migliore = (prova, a)
        if s >= SOGLIA:
            break
    LOG.append(migliore[0])
    a = migliore[1]
    if voce in (M2, F2):
        a = grave(a, 0.89 if voce == M2 else 0.92)
    return a


def sintesi(testo, voce):
    pezzi = []
    for g in gruppi(testo):
        CONTATORE[0] += 1
        pezzi += [pezzo(g, voce, CONTATORE[0]), silenzio(PAUSA_FRASE)]
    return np.concatenate(pezzi[:-1])


def grave(audio, quanto):
    with tempfile.TemporaryDirectory() as t:
        a, b = os.path.join(t, "a.wav"), os.path.join(t, "b.wav")
        sf.write(a, audio, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", f"rubberband=pitch={quanto}:formant=preserved", b], check=True)
        return sf.read(b, dtype="float32")[0]


NUMERI = {"1": "uno", "2": "due", "3": "tre", "4": "quattro"}


def tracce(file):
    blocchi = re.split(r"^=== Traccia (\d+) · (.+?) ===\s*$", Path(file).read_text(encoding="utf-8"), flags=re.M)
    for i in range(1, len(blocchi), 3):
        yield int(blocchi[i]), blocchi[i + 1].strip(), blocchi[i + 2]


def elementi(n, corpo):
    """Lista di elementi: {"numero": "Dialogo 6" o None, "battute": [(voce o None, testo)]}."""
    voci = {**VOCI, **VOCI_TRACCIA.get(n, {})}
    out, cur = [], None
    for riga in corpo.splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("Istruzioni per chi legge"):
            continue
        m = re.match(r"^(Dialogo|Testo|Messaggio|Notizia) (\w+)\.?(?:\s+(.*))?$", riga)
        if m and (m.group(3) is None or n == 4):
            cur = {"numero": f"{m.group(1)} {m.group(2)}", "battute": []}
            out.append(cur)
            if m.group(3):
                cur["battute"].append((None, m.group(3)))
            continue
        if cur is None:
            cur = {"numero": None, "battute": []}
            out.append(cur)
        m = re.match(r"^([A-ZÀ-Ü][\w'à ]{0,20}): (.+)$", riga)
        if m and m.group(1) in voci:
            cur["battute"].append((voci[m.group(1)], m.group(2)))
        elif m and not m.group(1)[0].islower() and len(m.group(1).split()) <= 2 and m.group(1) not in ("Mi raccomando", "Attenzione"):
            raise SystemExit(f"traccia {n}: interlocutore senza voce: {m.group(1)}")
        else:
            cur["battute"].append((None, riga))
    for k, e in enumerate(out):  # voce dei testi a una sola voce
        e["battute"] = [(v or VOCE_ELEMENTI[n][min(k, len(VOCE_ELEMENTI[n]) - 1)], t) for v, t in e["battute"]]
    return out


def rendi(n, titolo, corpo, uscita):
    parti = [silenzio(0.7)]
    els = elementi(n, corpo)
    for k, e in enumerate(els):
        if k:
            parti.append(silenzio(PAUSA.get(n, PAUSA_DEFAULT)))
        if e["numero"]:
            tipo, num = e["numero"].split()
            parti += [sintesi(f"{tipo} {NUMERI.get(num, num)}.", NARRATORE), silenzio(PAUSA_DOPO_NUMERO)]
        for j, (v, t) in enumerate(e["battute"]):
            if j:
                parti.append(silenzio(PAUSA_BATTUTA))
            parti.append(sintesi(t, v))
    parti.append(silenzio(1.0))
    audio = np.concatenate(parti)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.89  # picco a -1 dBFS
    wav = uscita / f"traccia-{n:02d}.wav"
    sf.write(wav, audio, SR, subtype="PCM_16")
    mp3 = uscita / f"traccia-{n:02d}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "1", "-codec:a", "libmp3lame", "-b:a", BITRATE,
                    "-id3v2_version", "3", "-metadata", f"title=Traccia {n:02d} · {titolo.replace(' (da leggere ad alta voce)', '')}",
                    "-metadata", "album=Esame B1 Cittadinanza Italiana", "-metadata", "artist=Guide EsameB1",
                    "-metadata", f"track={n}/17", "-metadata", "comment=Voce sintetica. esameb1.eu/audio-libro",
                    str(mp3)], check=True)
    wav.unlink()
    return len(audio) / SR, mp3.stat().st_size


if __name__ == "__main__":
    BITRATE = os.environ.get("BITRATE", "64k")
    uscita = Path(sys.argv[2])
    uscita.mkdir(parents=True, exist_ok=True)
    scelte = {int(x) for x in sys.argv[3:]}
    MODELLO = ChatterboxMultilingualTTS.from_pretrained(device="cpu", t3_model="v3")
    SR = MODELLO.sr
    CONDS = {}
    for g, f in RIF.items():
        MODELLO.prepare_conditionals(str(f), exaggeration=0.5)
        CONDS[g] = MODELLO.conds
    WHISPER = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=int(os.environ.get("THREADS", "4")))
    for n, titolo, corpo in tracce(sys.argv[1]):
        if scelte and n not in scelte:
            continue
        LOG, CONTATORE = [], [n * 1000]  # semi riproducibili per traccia
        t0 = time.time()
        durata, peso = rendi(n, titolo, corpo, uscita)
        sotto = [x for x in LOG if x["somiglianza"] < SOGLIA]
        rifatti = [x for x in LOG if x["tentativo"] > 1]
        (uscita / f"traccia-{n:02d}.log.json").write_text(json.dumps(LOG, ensure_ascii=False, indent=1))
        (uscita / f"traccia-{n:02d}.riepilogo.json").write_text(json.dumps(
            {"numero": n, "titolo": titolo, "durata": round(durata, 1), "byte": peso, "pezzi": len(LOG),
             "rigenerati": len(rifatti), "sotto_soglia": sotto, "minuti_cpu": round((time.time() - t0) / 60, 1)}, ensure_ascii=False, indent=1))
        print(f"{n:02d} {durata:6.1f} s {peso / 1e6:5.2f} MB  pezzi {len(LOG)} rigenerati {len(rifatti)} sotto soglia {len(sotto)}  "
              f"{(time.time() - t0) / 60:.1f} min  {titolo}", flush=True)
