"""Rende le 17 tracce del libro con Kokoro-82M (voci italiane if_sara / im_nicola).
Uso: python render.py TRACCE.txt CARTELLA_USCITA [numeri tracce...]
Ogni traccia contiene tutto UNA volta (il lettore la ascolta due volte), con i numeri degli elementi detti
e le pause tra gli elementi."""
import re, sys, json, subprocess, tempfile, os
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro import KPipeline

SR = 24000
F, M, M2, F2 = "if_sara", "im_nicola", "im_nicola_b", "if_sara_b"  # M2/F2: stessa voce un po' più grave (due voci uguali nello stesso dialogo)
NARRATORE = M
VELOCITA = 0.9

VOCI = {"Impiegata": F, "Signor Okafor": M, "Uomo": M, "Donna": F, "Autista": M, "Responsabile": F, "Ahmed": M,
        "Maestra": F, "Mamma": F, "Vicina": F, "Giornalista": M, "Svetlana": F, "Lei": F, "Lui": M, "Segretaria": F,
        "Signora": F, "Commessa": F, "Luca": M, "Marco": M2, "Figlio": M, "Collega": F, "Lavoratore": M,
        "Infermiera": F, "Ragazzo": M, "Agente": M, "Impiegato": M, "Candidato": M, "Insegnante": F, "Papà": M}
VOCI_TRACCIA = {5: {"Cliente": F, "Farmacista": M, "Mamma": F2}, 11: {"Cliente": M, "Signora": F2}, 12: {"Cliente": M}, 14: {"Cliente": F, "Farmacista": F}}
# voce dei testi a una sola voce, elemento per elemento
VOCE_ELEMENTI = {1: [F], 2: [M], 4: [F, F, M, M], 6: [M, F], 7: [M, F], 8: [F], 10: [F, M, M, F],
                 13: [M, F, F, M, M, F], 16: [M, F, M, F, M, F, M], 17: [F, M, M, F, F]}
# pausa tra un elemento e l'altro (secondi)
PAUSA = {4: 3, 5: 10, 6: 30, 11: 10, 14: 10}
PAUSA_DEFAULT = 5
PAUSA_BATTUTA = 0.6
PAUSA_FRASE = 0.3
PAUSA_DOPO_NUMERO = 1.2

# testo → testo da pronunciare
TESTO = [("06 4427 1830", "zero sei, quarantaquattro ventisette, diciotto trenta"),
         ("Saidi", "Saìdi"), ("Kovač", "Kòvač"), ("Termoservice", "Termosèrvis"), ('"', "")]
# correzioni sui fonemi di espeak-ng
FONEMI = [("kwˈimdiʧɪ", "kwˈindiʧɪ"), ("kˈɔvak", "kˈɔvaʧ")]

P = KPipeline(lang_code="i", repo_id="hexgrad/Kokoro-82M")


def silenzio(s):
    return np.zeros(int(SR * s), dtype=np.float32)


def fonemi(testo):
    ps = P.g2p(testo)[0]
    for a, b in FONEMI:
        ps = ps.replace(a, b)
    return ps


def frasi(testo):
    return [x for x in re.split(r"(?<=[.!?])\s+", testo.strip()) if x]


def sintesi(testo, voce):
    for a, b in TESTO:
        testo = testo.replace(a, b)
    # gruppi di frasi fino a ~250 fonemi: prosodia naturale dentro il gruppo, mai oltre il limite del modello
    gruppi, cur = [], ""
    for fr in frasi(testo):
        prova = (cur + " " + fr).strip()
        if cur and len(fonemi(prova)) > 250:
            gruppi.append(cur)
            cur = fr
        else:
            cur = prova
    if cur:
        gruppi.append(cur)
    vera = {M2: M, F2: F}.get(voce, voce)
    pezzi = []
    for g in gruppi:
        ps = fonemi(g)
        audio = np.concatenate([r.audio.numpy() for r in P.generate_from_tokens(ps, voice=vera, speed=VELOCITA)])
        pezzi += [audio.astype(np.float32), silenzio(PAUSA_FRASE)]
        LOG.append({"voce": voce, "testo": g, "fonemi": ps})
    audio = np.concatenate(pezzi[:-1])
    if voce in (M2, F2):
        audio = grave(audio, 0.89 if voce == M2 else 0.92)
    return audio


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
    return len(audio) / SR, mp3.stat().st_size, [(e["numero"], [(v, t[:40]) for v, t in e["battute"]]) for e in els]


if __name__ == "__main__":
    BITRATE = os.environ.get("BITRATE", "64k")
    uscita = Path(sys.argv[2])
    uscita.mkdir(parents=True, exist_ok=True)
    scelte = {int(x) for x in sys.argv[3:]}
    riepilogo = {}
    for n, titolo, corpo in tracce(sys.argv[1]):
        if scelte and n not in scelte:
            continue
        LOG = []
        durata, peso, piano = rendi(n, titolo, corpo, uscita)
        riepilogo[n] = {"titolo": titolo, "durata": round(durata, 1), "byte": peso, "piano": piano}
        (uscita / f"traccia-{n:02d}.log.json").write_text(json.dumps(LOG, ensure_ascii=False, indent=1))
        print(f"{n:02d} {durata:6.1f} s {peso / 1e6:5.2f} MB  {titolo}", flush=True)
    (uscita / "riepilogo.json").write_text(json.dumps(riepilogo, ensure_ascii=False, indent=1))
