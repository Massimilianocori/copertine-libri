#!/usr/bin/env python3
"""Previsione spese e incassi di BandiChiari per 12 mesi (ottobre 2026 - settembre 2027).

Tutti i numeri di crescita sono IPOTESI, non dati: si aggiornano con i dati veri ogni mese.
Uso: python3 bandichiari/previsione.py
"""
MESI = ["ott 26", "nov 26", "dic 26", "gen 27", "feb 27", "mar 27",
        "apr 27", "mag 27", "giu 27", "lug 27", "ago 27", "set 27"]

# Prezzi Studio e mix (70% mensile 49 €, 30% annuale 490 €)
PREZZO_MESE = 0.7 * 49 + 0.3 * 490 / 12           # ≈ 46,55 € al mese per studio
COMMISSIONI = 0.022                                 # Stripe ≈ 1,5% carta UE + 0,7% abbonamenti (+0,25 €/addebito)
COSTO_ADDEBITO = 0.25 * 0.7                          # 0,25 € a ogni addebito mensile

# Costi fissi
DOMINIO_EMAIL_ANNO = 40          # dominio .it + casella email
COMMERCIALISTA_MESE = 40         # servizio online per forfettari
INPS_COMMERCIANTI_ANNO = 2998    # minimo 2026 con riduzione 35% forfettari
ALIQ_SEPARATA = 0.2607           # Gestione Separata (stima 2026)
COEFF = 0.67                     # coefficiente di redditività forfettario (da confermare col codice ATECO)
IMPOSTA = 0.05                   # aliquota start-up primi 5 anni

SCENARI = {
    #               mese apertura P.IVA (0 = ottobre), nuovi studi al mese dopo l'apertura, disdette al mese
    "Pessimista":  dict(apertura=None, nuovi=0, churn=0.0),
    "Prudente":    dict(apertura=6, nuovi=1, churn=0.08),
    "Realistico":  dict(apertura=3, nuovi=3, churn=0.05),
    "Ottimista":   dict(apertura=2, nuovi=7, churn=0.04),
}


def simula(apertura, nuovi, churn, inps):
    studi, righe = 0.0, []
    for m, nome in enumerate(MESI):
        attiva = apertura is not None and m >= apertura
        if attiva:
            studi = studi * (1 - churn) + (3 if m == apertura else nuovi)  # i 3 studi in attesa partono subito
        incasso = studi * PREZZO_MESE if attiva else 0
        stripe = incasso * COMMISSIONI + studi * COSTO_ADDEBITO if attiva else 0
        fissi = DOMINIO_EMAIL_ANNO / 12 + (COMMERCIALISTA_MESE if attiva else 0)
        if not attiva:
            contributi = 0
        elif inps == "commercianti":
            contributi = INPS_COMMERCIANTI_ANNO / 12
        else:
            contributi = incasso * COEFF * ALIQ_SEPARATA
        tasse = max(0, incasso * COEFF - contributi) * IMPOSTA if attiva else 0
        netto = incasso - stripe - fissi - contributi - tasse
        righe.append(dict(mese=nome, studi=studi, incasso=incasso, spese=stripe + fissi + contributi + tasse, netto=netto))
    return righe


def eur(x):
    return f"{x:,.0f} €".replace(",", ".")


if __name__ == "__main__":
    for inps in ("commercianti", "separata"):
        print(f"\n=== INPS {inps.upper()} ===")
        print(f"{'Scenario':<12}{'studi a set 27':>15}{'incassi 12 mesi':>17}{'spese 12 mesi':>15}{'netto 12 mesi':>15}{'netto set 27':>14}{'peggior saldo':>15}")
        for nome, par in SCENARI.items():
            r = simula(inps=inps, **par)
            cum, minimo = 0, 0
            for x in r:
                cum += x["netto"]; minimo = min(minimo, cum)
            print(f"{nome:<12}{r[-1]['studi']:>15.0f}{eur(sum(x['incasso'] for x in r)):>17}"
                  f"{eur(sum(x['spese'] for x in r)):>15}{eur(cum):>15}{eur(r[-1]['netto']):>14}{eur(minimo):>15}")
    print("\nDettaglio mensile, scenario Realistico, INPS commercianti:")
    for x in simula(inps="commercianti", **SCENARI["Realistico"]):
        print(f"  {x['mese']}: studi {x['studi']:5.1f}  incasso {eur(x['incasso']):>8}  spese {eur(x['spese']):>8}  netto {eur(x['netto']):>8}")
