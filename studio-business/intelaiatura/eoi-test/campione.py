"""Sceglie i 30 controlli a mano e stampa, per ognuno, le righe della fonte da guardare.

Uso: python3 -I campione.py <date_estratte.json> <cartella_grezzi>
Campione: 2 date d'esame per ognuna delle 13 comunità lette (26) + 4 tappe, seme fisso 2026.
Il giudizio (giusta / sbagliata) si scrive a mano in controlli_30.json dopo aver letto la fonte.
"""
import json, os, random, re, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
cartella = sys.argv[2]
rnd = random.Random(2026)
comunita = sorted({r["comunita"] for r in d["esami"]})
campione = []
for c in comunita:
    rs = [r for r in d["esami"] if r["comunita"] == c]
    campione += [dict(r, genere="esame") for r in rnd.sample(rs, 2)]
campione += [dict(t, genere="tappa") for t in rnd.sample(d["tappe"], 4)]

MESI_ES = "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split()
MESI_CA = "gener febrer març abril maig juny juliol agost setembre octubre novembre desembre".split()

for i, r in enumerate(campione, 1):
    print(f"\n#{i} {r['genere']} {r['comunita']} | {r.get('convocatoria', r.get('tipo'))} | "
          f"{r.get('lingua', '')} {r.get('livello', '')} | {r['data']} {r.get('fine', '') or ''} {r.get('ora', '')} | {r['fonte']}")
    f = os.path.join(cartella, r["fonte"])
    f = f[:-4] + ".txt" if f.endswith(".pdf") else f
    t = open(f, encoding="utf-8", errors="ignore").read()
    if f.endswith(".html"):
        t = re.sub(r"<[^>]+>", " ", t)
    a, m, g = r["data"].split("-")
    pats = [f"{int(g)}/{int(m)}\\b", f"{g}/{m}/{a}", f"{g}-{m}-{a}", f"\\b{int(g)} de {MESI_ES[int(m)-1]}",
            f"\\b{int(g)} DE {MESI_ES[int(m)-1].upper()}", f"\\b{int(g)} de {MESI_CA[int(m)-1]}", f"\\b{int(g)} d'{MESI_CA[int(m)-1]}"]
    righe = t.splitlines()
    n = 0
    for j, riga in enumerate(righe):
        if any(re.search(p, riga, re.I) for p in pats):
            print(f"   {j:>4}: {riga.strip()[:150]}")
            n += 1
            if n >= 6:
                break
print(json.dumps(campione, ensure_ascii=False), file=open(os.path.join(os.path.dirname(sys.argv[1]), "campione_30.json"), "w", encoding="utf-8"))
