"""Legge le fonti ufficiali su soldi, visto e borse regionali (DSU) per gli studenti internazionali in Italia e scrive
visaincome/dati/studio_italia.json (sezione "Study in Italy" del sito, dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/studio_italia.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/studio_italia.py --domanda    # rifà anche l'autocompletamento di Google (6 Paesi, circa 1 minuto)

Fonti (lette A MANO il 31/10/2026; ogni valore ha il FRAMMENTO del testo ufficiale da cui viene)
- MUR + MAECI, "Circolare recante le procedure per l'ingresso, il soggiorno, l'immatricolazione degli studenti internazionali
  ... valide per gli anni accademici 2026-2027 e 2027-2028" (PDF su Universitaly): mezzi economici 10.179,85 € l'anno, visto
  entro il 30/11/2026, permesso entro 8 giorni lavorativi, rinnovo 60 giorni prima, assicurazione sanitaria.
- MUR, D.D. n. 175 del 10/2/2026 (importi minimi delle borse 2026/27) e D.D. n. 176 del 10/2/2026 (limiti massimi ISEE e ISPE).
- MUR, D.M. n. 176 del 24/2/2026: elenco dei Paesi "particolarmente poveri" per il 2026/27.
- Poste Italiane (guida al permesso di soggiorno: 16 € marca, 30 € all'ufficio postale, 30,46 € per il documento) e Polizia di
  Stato (contributo: 40 € fino a un anno, 50 € da uno a due anni; D.M. 5/5/2017).
- Normattiva: art. 34 del D.lgs. 286/1998 (iscrizione volontaria al SSN degli studenti: almeno 700 € l'anno) e Allegato 1 del
  DPCM 159/2013 (scala di equivalenza ISEE). L'allegato si legge solo con il cookie di sessione della pagina dell'atto.
- Banca d'Italia, cambi medi annui 2024 e 2025 (valuta per 1 euro): sono quelli che i bandi usano per i redditi esteri.
- Bandi 2026/27 degli enti per il diritto allo studio (PDF ufficiali): ER.GO, DSU Toscana, DiSCo Lazio, Università degli Studi
  di Milano, Politecnico di Milano, Università di Padova, ERSU Palermo, ERSU Catania, ADISU Campania.
  Non letti (il 31/10/2026): EDISU Piemonte e ADISU Puglia (il server chiude la connessione), ARDiS FVG e Opera Universitaria
  Trento (sito raggiungibile, bando 2026/27 non trovato fra i file pubblicati): sono in NON_LETTI e il sito lo dice.

Regole
- Se un frammento non è più nel testo, la pagina è cambiata: il JSON NON viene aggiornato (esce con codice 1) finché qualcuno non
  rilegge la fonte e aggiorna LETTURE o ENTI. Nessuna cifra ricavata da noi entra come "letta".
- Controlli incrociati: limiti ISEE/ISPE di ogni bando ≤ limiti massimi del D.D. 176; importo base fuori sede di ogni bando ≥
  minimo del D.D. 175 (o importo + servizi, per DSU Toscana e DiSCo); +15% = base × 1,15 dove il bando lo scrive.
Nessun testo copiato per intero: si pubblicano fatti brevi (importi, date, condizioni) con il link alla fonte ufficiale.
"""
import hashlib
import html as H
import http.cookiejar
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "studio_italia.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

URL_DPCM = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:presidente.consiglio.ministri:decreto:2013-12-05;159"
URL_ALL1 = ("https://www.normattiva.it/atto/caricaArticolo?art.versione=3&art.idGruppo=0&art.flagTipoArticolo=1&art.codiceRedazionale=14G00009"
            "&art.idArticolo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=2014-01-24&art.progressivo=0&")

FONTI = {
    "circolare": {"url": "https://universitaly-private.cineca.it/uploads/universitaly-pubblico/Circolare_2026-2027_studenti_internazionali.pdf",
                  "editore": "Ministry of University and Research (MUR) and Ministry of Foreign Affairs",
                  "titolo": "Procedures for the entry, stay and enrolment of international students, academic years 2026-2027 and 2027-2028",
                  "pagina": "https://www.universitaly.it/it/studenti-stranieri"},
    "dd175": {"url": "https://www.mur.gov.it/sites/default/files/2026-03/Decreto%20Direttoriale%20n.%20175%20del%2010-02-2026.pdf",
              "editore": "MUR", "titolo": "Directorial Decree no. 175 of 10 February 2026 (minimum scholarship amounts 2026/27)", "data": "2026-02-10",
              "pagina": "https://www.mur.gov.it/it/atti-e-normativa/decreto-direttoriale-n-175-del-10-02-2026"},
    "dd176": {"url": "https://www.mur.gov.it/sites/default/files/2026-03/Decreto%20Direttoriale%20n.%20176%20del%2010-02-2026.pdf",
              "editore": "MUR", "titolo": "Directorial Decree no. 176 of 10 February 2026 (maximum ISEE and ISPE 2026/27)", "data": "2026-02-10",
              "pagina": "https://www.mur.gov.it/it/atti-e-normativa/decreto-direttoriale-n-176-del-10-02-2026"},
    "dm176": {"url": "https://www.mur.gov.it/sites/default/files/2026-03/Decreto%20Ministeriale%20n.%20176%20del%2024-2-2026.pdf",
              "editore": "MUR", "titolo": "Ministerial Decree no. 176 of 24 February 2026 (particularly poor countries 2026/27)", "data": "2026-02-24"},
    "poste": {"url": "https://www.poste.it/prodotti/guida-rilascio-e-rinnovo-permesso-di-soggiorno.html", "editore": "Poste Italiane",
              "titolo": "Residence permits: how to apply and what it costs"},
    "polizia": {"url": "https://www.poliziadistato.it/articolo/225", "editore": "Polizia di Stato", "titolo": "Il rilascio del permesso di soggiorno"},
    "ssn": {"url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1998-07-25;286~art34", "editore": "Normattiva",
            "titolo": "Legislative Decree 286/1998, art. 34 (voluntary registration with the National Health Service)"},
    "scala": {"url": URL_ALL1, "link": URL_DPCM, "editore": "Normattiva", "titolo": "DPCM 159/2013, Annex 1 (ISEE equivalence scale)", "cookie": True},
    # bandi 2026/27
    "ergo": {"url": "https://www.er-go.it/cosa-fare-per/bandi-di-concorso/leggi-il-bando/bando-di-concorso-benefici-dsu-a-a-2026_2027.pdf/@@download/file",
             "editore": "ER.GO", "titolo": "Bando di concorso benefici DSU a.a. 2026/2027",
             "pagina": "https://www.er-go.it/cosa-fare-per/bandi-di-concorso/leggi-il-bando"},
    "ergo_scad": {"url": "https://www.er-go.it/cosa-fare-per/bandi-di-concorso/leggi-il-bando/scadenze/@@download/file/scadenze.pdf",
                  "editore": "ER.GO", "titolo": "Scadenze 2026/2027"},
    "dsut": {"url": "https://www.dsu.toscana.it/documents/4390857/32478257/bando+borsa+alloggio+26-27.pdf/092c16da-95e8-1712-b1eb-f159d5e7743e?t=1784280597313",
             "editore": "DSU Toscana", "titolo": "Bando borsa di studio e posto alloggio 2026/2027", "pagina": "https://www.dsu.toscana.it/borsa-di-studio",
             "inglese": "https://www.dsu.toscana.it/documents/4390857/32478257/EN_bando+borsa+alloggio+2026-2027.pdf/eeffc852-e4e4-5539-dab2-9aebbd3c7a46?t=1786108838438"},
    "disco": {"url": "https://laziodisco.it/wp-content/uploads/2026/07/BANDO-DIRITTO-ALLO-STUDIO-26-27-con-EC.pdf", "editore": "DiSCo Lazio",
              "titolo": "Bando Diritto allo Studio 2026/2027", "pagina": "https://laziodisco.it/bando-diritto-allo-studio-2026-2027/",
              "inglese": "https://laziodisco.it/wp-content/uploads/2026/07/BANDO-DIRITTO-ALLO-STUDIO-ENG-26-27.pdf"},
    "unimi": {"url": "https://www.unimi.it/sites/default/files/2026-07/Bando_Borse_regionali%202026-27_IT_0.pdf", "editore": "Università degli Studi di Milano",
              "titolo": "Bando borse di studio regionali 2026/27", "pagina": "https://www.unimi.it/it/studiare/borse-premi-mense-e-alloggi/borse-di-studio-regionali"},
    "polimi": {"url": "https://www.polimi.it/fileadmin/user_upload/studenti/tasse-borse-agevolazioni-economiche/dsu/bando_2026-2027/Bando_Benefici_DSU_2026-2027.pdf",
               "editore": "Politecnico di Milano", "titolo": "Bando Diritto allo Studio a.a. 2026/2027",
               "pagina": "https://www.polimi.it/studenti/tasse-borse-e-agevolazioni/diritto-allo-studio"},
    "polimi_int": {"url": "https://www.polimi.it/fileadmin/user_upload/studenti/tasse-borse-agevolazioni-economiche/dsu/bando_2026-2027/Bando_integrativo_DSU_aa_26_27_.pdf",
                   "editore": "Politecnico di Milano", "titolo": "Bando integrativo DSU a.a. 2026/2027 (economic limits and amounts)"},
    "unipd": {"url": "https://wwwassets.unipd.it/sites/default/files/2026-07/Bando%20Borse%20Studio%202026-27.pdf", "editore": "Università di Padova",
              "titolo": "Concorso per l'assegnazione delle borse di studio regionali a.a. 2026/2027", "pagina": "https://www.unipd.it/borse-studio-alloggi",
              "inglese": "https://wwwassets.unipd.it/sites/default/files/2026-07/1.Bando%20Borse%20Studio%202026-27_ENG_0.pdf"},
    "palermo": {"url": "https://www.ersupalermo.it/wp-content/uploads/2026/06/Bando-di-Concorso-dellERSU-di-Palermo-a.a.-2026_2027.pdf", "editore": "ERSU Palermo",
                "titolo": "Bando di concorso a.a. 2026/2027",
                "pagina": "https://www.ersupalermo.it/2026/06/05/bando-di-concorso-per-lattribuzione-di-borse-di-studio-altri-contributi-economici-e-servizi-per-il-diritto-allo-studio-universitario/"},
    "catania": {"url": "https://www.ersucatania.it/wp-content/uploads/2026/06/Bando-ERSU-CT-2026-27-Delibera-45.pdf", "editore": "ERSU Catania",
                "titolo": "Bando di concorso a.a. 2026/2027", "pagina": "https://www.ersucatania.it/borsa-di-studio/"},
    "adisurc": {"url": "https://www.adisurcampania.it/sites/default/files/2026-07/Bando%20di%20Concorso%20a.a.%202026.27.pdf", "editore": "ADISU Campania (ADiSURC)",
                "titolo": "Bando di concorso borse di studio, posti alloggio e mobilità internazionale a.a. 2026/2027",
                "pagina": "https://www.adisurcampania.it/notizie/approvazione-bando-di-concorso-20262027",
                "inglese": "https://www.adisurcampania.it/sites/default/files/2026-07/Bando%20di%20Concorso%20a.a.%202026.27_ENG.pdf"},
}
URL_BDI = "https://tassidicambio.bancaditalia.it/terzevalute-wf-web/rest/v1.0/annualAverageRates?year={anno}&currencyIsoCode=EUR&lang=en"
PAGINA_BDI = "https://tassidicambio.bancaditalia.it/terzevalute-wf-ui-web/averageRates"
VALUTE_BDI = ["USD", "GBP", "INR", "PKR", "BDT", "NGN", "IRR", "NPR", "LKR", "EGP", "TRY", "MAD", "GHS", "KES", "ETB", "CNY", "VND",
              "IDR", "PHP", "UZS", "KZT", "AZN", "BRL", "MXN", "COP"]

# valore + fonte + frammento (testo normalizzato: spazi compattati, apostrofi e virgolette dritti)
LETTURE = {
    "mezzi": {"valore": 10179.85, "fonte": "circolare", "frammento": "Tali mezzi sono quantificati nell'importo di euro 10.179,85 annuali"},
    "mezzi_fonti": {"valore": True, "fonte": "circolare", "frammento": "deve provenire da fonti lecite e tracciabili e deve essere preferibilmente personale o, in alternativa, messa a disposizione dal nucleo familiare (parente fino al 4° grado)"},
    "mezzi_borsa": {"valore": True, "fonte": "circolare", "frammento": "in assenza di esplicita attestazione di attribuzione della borsa, non potrà essere considerata nel computo dei mezzi di sussistenza"},
    "alloggio": {"valore": True, "fonte": "circolare", "frammento": "La semplice candidatura o idoneità a un posto alloggio presso una residenza universitaria non costituisce documento valido"},
    "visto_scadenza": {"valore": "2026-11-30", "fonte": "circolare", "frammento": "le domande di visto dovranno essere presentate presso le Rappresentanze diplomatico-consolari competenti entro e non oltre il 30 novembre 2026"},
    "visto_scadenza_27": {"valore": "2027-10-31", "fonte": "circolare", "frammento": "il termine ultimo per la presentazione delle domande di visto è fissato al 31 ottobre 2027"},
    "permesso_giorni": {"valore": 8, "fonte": "circolare", "frammento": "Entro otto giorni lavorativi dall'arrivo in Italia con un visto di tipo D \"nazionale\" per STUDIO"},
    "rinnovo_giorni": {"valore": 60, "fonte": "circolare", "frammento": "il rinnovo del permesso di soggiorno per l'intero anno, almeno sessanta giorni prima della scadenza"},
    "assicurazione": {"valore": True, "fonte": "circolare", "frammento": "Una adeguata copertura assicurativa per cure mediche e ricoveri ospedalieri"},
    "assicurazione_polizza": {"valore": True, "fonte": "circolare", "frammento": "non dovranno comportare limitazioni od eccezioni alle tariffe stabilite per il ricovero ospedaliero urgente per tutta la sua durata"},
    "dsu_fs": {"valore": 7171.11, "fonte": "dd175", "frammento": "a) studenti fuori sede: b) studenti pendolari: c) studenti in sede: euro 7.171,11; euro 4.190,71; euro 2.890,16."},
    "dsu_pend": {"valore": 4190.71, "fonte": "dd175", "frammento": "euro 7.171,11; euro 4.190,71; euro 2.890,16."},
    "dsu_sede": {"valore": 2890.16, "fonte": "dd175", "frammento": "euro 7.171,11; euro 4.190,71; euro 2.890,16."},
    "dsu_istat": {"valore": 1.4, "fonte": "dd175", "frammento": "corrispondente al valore pari a +1,4%"},
    "isee_max": {"valore": 28339.88, "fonte": "dd176", "frammento": "limite massimo ISEE: euro 28.339,88"},
    "ispe_max": {"valore": 61608.48, "fonte": "dd176", "frammento": "limite massimo ISPE: euro 61.608,48"},
    "ps_marca": {"valore": 16, "fonte": "poste", "frammento": "16 euro per la marca da bollo"},
    "ps_poste": {"valore": 30, "fonte": "poste", "frammento": "30,00 euro all'operatore dell'ufficio postale, al momento della presentazione della domanda"},
    "ps_documento": {"valore": 30.46, "fonte": "poste", "frammento": "30,46 euro per la produzione di Permesso o Carta di Soggiorno cui va aggiunto l'eventuale contributo ove dovuto"},
    "ps_contributo_1": {"valore": 40, "fonte": "polizia", "frammento": "40,00 per i permessi di soggiorno di durata superiore a tre mesi e inferiore o pari a un anno"},
    "ps_contributo_2": {"valore": 50, "fonte": "polizia", "frammento": "euro 50,00 per i permessi di soggiorno di durata superiore a un anno e inferiore o pari a due anni"},
    "ps_dm": {"valore": "2017-05-05", "fonte": "polizia", "frammento": "Con decreto del Ministero dell'Economia e delle Finanze, di concerto con il Ministero dell'Interno, del 5 maggio 2017"},
    "ssn_studenti": {"valore": True, "fonte": "ssn", "frammento": "dagli stranieri soggiornanti in Italia titolari di permesso di soggiorno per motivi di studio"},
    "ssn_minimo": {"valore": 700, "fonte": "ssn", "frammento": "Il contributo non è in ogni caso inferiore a euro 700 annui nei casi di cui al comma 4, lettera a)"},
    "ssn_familiari": {"valore": True, "fonte": "ssn", "frammento": "Il contributo per gli stranieri indicati al comma 4, lettere a) e b) non è valido per i familiari a carico"},
    "ssn_adeguamento": {"valore": True, "fonte": "ssn", "frammento": "da adottare annualmente, gli importi minimi di cui al comma 3 e al comma 5 possono essere adeguati"},
    "scala": {"valore": {"1": 1.0, "2": 1.57, "3": 2.04, "4": 2.46, "5": 2.85, "oltre": 0.35}, "fonte": "scala",
              "frammento": "Numero componenti Parametro 1 1,00 2 1,57 3 2,04 4 2,46 5 2,85 Il parametro della scala di equivalenza è incrementato di 0,35 per ogni ulteriore componente"},
    "poveri_titolo": {"valore": True, "fonte": "dm176", "frammento": "Per l'anno accademico 2026/2027, sono da intendere particolarmente poveri"},
}

POVERI = ["Afghanistan", "Angola", "Bangladesh", "Benin", "Burkina Faso", "Burundi", "Cambodia", "Central African Republic", "Chad", "Comoros",
          "Democratic People's Republic of Korea", "Democratic Republic of the Congo", "Djibouti", "Eritrea", "Ethiopia", "Gambia", "Guinea",
          "Guinea-Bissau", "Haiti", "Kiribati", "Lao People's Democratic Republic", "Lesotho", "Liberia", "Madagascar", "Malawi", "Mali",
          "Mauritania", "Mozambique", "Myanmar", "Nepal", "Niger", "Rwanda", "Senegal", "Sierra Leone", "Solomon Islands", "Somalia",
          "South Sudan", "Sudan", "Syrian Arab Republic", "Tanzania", "Timor-Leste", "Togo", "Tuvalu", "Uganda", "Yemen", "Zambia"]

# Allegato 1 del bando UNIMI: Paesi per cui l'Ateneo chiede i documenti esteri (agli altri dà d'ufficio la 1ª fascia)
UNIMI_ALL1 = ["ANDORRA", "ANTIGUA E BARBUDA", "ANTILLE OLAND.(P.B.)", "ARABIA SAUDITA", "ARUBA", "AUSTRALIA", "AUSTRIA", "BAHAMAS", "BAHREIN",
              "BARBADOS", "BELGIO", "BERMUDA", "BRUNEI", "BULGARIA", "CANADA", "CILE", "CIPRO", "CITTA' DEL VATICANO", "COREA DEL SUD", "COSTA RICA",
              "CROAZIA", "DANIMARCA", "EMIRATI ARABI UNITI", "ESTONIA", "FALKLAND", "FINLANDIA", "FRANCIA", "GERMANIA", "GIAPPONE", "GIBILTERRA",
              "GRECIA", "GUYANA", "HONG KONG", "IRLANDA", "ISLANDA", "ISOLE CAYMAN", "ISOLE TURCKS AND CAICOS", "ISOLE VERGINI", "ISRAELE", "KUWAIT",
              "LETTONIA", "LIECHTENSTEIN", "LITUANIA", "LUSSEMBURGO", "MACAO", "MALTA", "NAURU", "NORVEGIA", "NUOVA ZELANDA", "OMAN", "PAESI BASSI",
              "PALAU", "PANAMA", "POLINESIA FRANCESE", "POLONIA", "PORTOGALLO", "PRINCIPATO DI MONACO", "PUERTO RICO", "QATAR", "REGNO UNITO",
              "REPUBBLICA CECA", "REPUBBLICA DI SAN MARINO", "ROMANIA", "RUSSIA", "SAINT KITTS E NEVIS", "SEYCHELLES", "SINGAPORE", "SLOVACCHIA",
              "SLOVENIA", "SPAGNA", "STATI UNITI D' AMERICA", "SVEZIA", "SVIZZERA", "TAIWAN", "TRINIDAD E TOBAGO", "UNGHERIA", "URUGUAY"]

# Enti letti il 31/10/2026. Ogni valore: importo/data + fonte (chiave di FONTI) + frammento.
# fs: borsa massima per fuori sede (la cifra più alta della tabella per la generalità degli studenti) e fino a quale ISEE vale;
# fs_base: importo base (100%) per fuori sede; servizi: valore dei servizi compresi o aggiunti (pasti, alloggio) se il bando li scrive.
# metodo: chi calcola la condizione economica di chi ha redditi all'estero: "caf" (CAF convenzionato), "ente" (l'ente dai documenti).
# poveri: frammento del bando sugli studenti dei Paesi particolarmente poveri (UNIMI e Padova non ne parlano: niente campo).
ENTI = [
    {"id": "er-go", "nome": "ER.GO", "nome_lungo": "ER.GO, Emilia-Romagna regional agency for the right to higher education", "regione": "Emilia-Romagna",
     "citta": ["Bologna", "Modena", "Reggio Emilia", "Parma", "Ferrara"], "universita": "Universities of Bologna, Modena and Reggio Emilia, Parma and Ferrara",
     "fonti": ["ergo", "ergo_scad"], "metodo": "ente",
     "isee": {"valore": 25000.0, "fonte": "ergo", "frammento": "Soglia ISEE Soglia ISPE Borsa di studio € 25.000,00 € 50.000,00"},
     "ispe": {"valore": 50000.0, "fonte": "ergo", "frammento": "Soglia ISEE Soglia ISPE Borsa di studio € 25.000,00 € 50.000,00"},
     "fs": {"valore": 8246.78, "fino_isee": 12500.0, "fonte": "ergo", "frammento": "fino a € 12.500,00 8.246,78 comprensivo della quota eventualmente convertita in servizio ristorativo"},
     "fs_base": {"valore": 7171.11, "fino_isee": 16666.67, "fonte": "ergo", "frammento": "fino a 16.666,67 7.171,11 comprensivo della quota eventualmente convertita in servizio ristorativo"},
     "scadenza": {"valore": "2026-08-24", "ora": "16:00", "aperta_dal": "2026-06-23", "fonte": "ergo_scad",
                  "frammento": "Borsa di studio per: - studenti matricole ed anni successivi di tutti i corsi Dal 23 giugno al 24 agosto 2026 fino alle ore 16.00 del giorno di scadenza"},
     "poveri": {"fonte": "ergo", "frammento": "che risultano \"particolarmente poveri\" (Tabella A), devono produrre una certificazione della Rappresentanza italiana"},
     "estero": {"fonte": "ergo", "frammento": "presentare la documentazione delle condizioni economiche e patrimoniali rilasciata dalle autorità competenti per il territorio in cui i redditi sono stati prodotti e dove sono posseduti i patrimoni. Non vengono accettate in nessun caso autocertificazioni o autodichiarazioni."},
     "estero_cambio": {"fonte": "ergo", "frammento": "convertiti in euro sulla base del tasso medio di cambio delle valute estere dell'anno 2025, calcolato dalla Banca d'Italia"},
     "anno_redditi": 2025,
     "chiavi": ["er.go", "ergo", "bologna", "unibo", "modena", "parma", "ferrara"]},
    {"id": "dsu-toscana", "nome": "DSU Toscana", "nome_lungo": "DSU Toscana, Tuscany regional agency for the right to study", "regione": "Tuscany",
     "citta": ["Florence", "Pisa", "Siena"], "universita": "Universities of Florence, Pisa and Siena, and other Tuscan institutions",
     "fonti": ["dsut"], "metodo": "ente",
     "isee": {"valore": 27000.0, "fonte": "dsut", "frammento": "non devono superare le soglie limite sotto riportate: ISEE € 27.000,00 ISPE € 60.000,00"},
     "ispe": {"valore": 60000.0, "fonte": "dsut", "frammento": "non devono superare le soglie limite sotto riportate: ISEE € 27.000,00 ISPE € 60.000,00"},
     "fs": {"valore": 3338.0, "fino_isee": 13500.0, "fonte": "dsut", "frammento": "Studenti fuori sede da € 0,00 € 2385 € 3880 € 3338 a € 13.500,00 n. 1 pasto giornaliero gratuito n. 1 pasto giornaliero gratuito n. 2 pasti giornalieri e posto alloggio gratuiti"},
     "servizi": {"valore": 4910.0, "mensa": 1760.0, "alloggio": 3150.0, "fonte": "dsut", "frammento": "Mensa €940 €940 € 1.760 Alloggio Non previsto Non previsto € 3.150"},
     "scadenza": {"valore": "2026-09-07", "ora": "13:00", "aperta_dal": "2026-07-20", "fonte": "dsut", "frammento": "dal 20 luglio 2026 alle ore 13.00 (ora italiana) del 7 settembre 2026"},
     "poveri": {"fonte": "dsut", "frammento": "8.3.3 Studenti extra Unione Europea provenienti dai paesi particolarmente poveri e in via di sviluppo"},
     "estero": {"fonte": "dsut", "frammento": "I fabbricati posseduti all'estero sono valutati convenzionalmente € 500,00 al metro quadro."},
     "estero_cambio": {"fonte": "dsut", "frammento": "I redditi e/o il patrimonio mobiliare all'estero sono valutati sulla base del tasso di cambio medio dell'Euro nell'anno 2025"},
     "anno_redditi": 2025,
     "chiavi": ["toscana", "tuscany", "florence", "firenze", "pisa", "siena", "unifi", "unipi"]},
    {"id": "disco-lazio", "nome": "DiSCo Lazio", "nome_lungo": "DiSCo, Lazio regional agency for the right to study", "regione": "Lazio",
     "citta": ["Rome", "Viterbo", "Cassino"], "universita": "Sapienza, Tor Vergata, Roma Tre and other universities in Lazio",
     "fonti": ["disco"], "metodo": "caf",
     "isee": {"valore": 28339.88, "fonte": "disco", "frammento": "ISEE /ISEEUP: € 28.339,88 • Indicatore Situazione Patrimoniale Equivalente ISPE/ISPEUP: € 61.608,48"},
     "ispe": {"valore": 61608.48, "fonte": "disco", "frammento": "ISEE /ISEEUP: € 28.339,88 • Indicatore Situazione Patrimoniale Equivalente ISPE/ISPEUP: € 61.608,48"},
     "fs": {"valore": 7556.78, "fino_isee": 14169.94, "fonte": "disco", "frammento": "Tabella 6 LIVELLO ISEE Minore o uguale a € 14.169,94"},
     "fs_cifra": {"fonte": "disco", "frammento": "STUDENTE FUORI SEDE STUDENTE PENDOLARE STUDENTE IN SEDE € 7.556,78 (115%)"},
     "servizi": {"valore": 600.0, "mensa": 600.0, "alloggio": 0, "fonte": "disco", "frammento": "+ 2 pasti giornalieri gratuiti (corrispondente a € 600 complessivi)"},
     "scadenza": {"valore": "2026-07-22", "ora": "12:00", "aperta_dal": "2026-06-10", "fonte": "disco", "frammento": "Dal 10 giugno al 22 luglio 2026 ore 12.00 Compilazione e trasmissione della domanda di partecipazione (prima fase)."},
     "poveri": {"fonte": "disco", "frammento": "Per gli studenti internazionali provenienti da uno dei Paesi particolarmente poveri individuati dal D.M. 24 febbraio 2026 n. 176"},
     "estero": {"fonte": "disco", "frammento": "l'ISEEUP deve essere sottoscritto entro il 10 dicembre 2026 presso uno dei CAF convenzionati con DiSCo"},
     "estero_scadenza": "2026-12-10",
     "estero_cambio": {"fonte": "disco", "frammento": "si applica il tasso di cambio definito dalla Banca d'Italia"},
     "anno_redditi": 2024,
     "chiavi": ["disco", "lazio", "rome", "roma", "sapienza", "tor vergata"]},
    {"id": "university-of-milan", "nome": "University of Milan (UniMi)", "nome_lungo": "Università degli Studi di Milano (regional scholarships of Lombardy)", "regione": "Lombardy",
     "citta": ["Milan"], "universita": "Università degli Studi di Milano", "fonti": ["unimi"], "metodo": "ente",
     "isee": {"valore": 26887.93, "fonte": "unimi", "frammento": "(ISEE Università) non sia superiore a € 26.887,93"},
     "ispe": {"valore": 58452.06, "fonte": "unimi", "frammento": "(ISPE) non sia superiore a € 58.452,06"},
     "fs": {"valore": 7419.0, "fino_isee": 13443.97, "fonte": "unimi", "frammento": "1ª Fascia € 7.419,00 più un pasto giornaliero gratuito € 8.248,00"},
     "fs_fascia": {"fonte": "unimi", "frammento": "Prima fascia: ISEE da € 0,00 a € 13.443,97"},
     "servizi": {"valore": 829.0, "mensa": 829.0, "alloggio": 0, "fonte": "unimi", "frammento": "1ª Fascia € 7.419,00 più un pasto giornaliero gratuito € 8.248,00"},
     "scadenza": {"valore": "2026-09-30", "ora": "", "fonte": "unimi", "frammento": "La domanda di Borsa di Studio deve essere presentata entro il 30 settembre 2026."},
     "estero": {"fonte": "unimi", "frammento": "Agli studenti provenienti da Paesi non presenti nell'allegato 1 sarà attribuita d'ufficio la 1ª fascia di reddito"},
     "estero_regola": {"fonte": "unimi", "frammento": "20% della somma dei patrimoni mobiliare ed immobiliare posseduti da ogni singolo componente il nucleo familiare alla data del 31/12/2025; per il calcolo del patrimonio immobiliare sono considerati esclusivamente i fabbricati, che saranno valutati a € 500,00 al mq"},
     "anno_redditi": 2025, "allegato1": True,
     "chiavi": ["milan", "unimi", "university of milan", "statale"]},
    {"id": "politecnico-di-milano", "nome": "Politecnico di Milano", "nome_lungo": "Politecnico di Milano (regional scholarships of Lombardy)", "regione": "Lombardy",
     "citta": ["Milan", "Como", "Lecco", "Cremona", "Mantua", "Piacenza"], "universita": "Politecnico di Milano", "fonti": ["polimi", "polimi_int"], "metodo": "caf",
     "isee": {"valore": 26887.93, "fonte": "polimi_int", "frammento": "non superiore a € 26.887,93"},
     "ispe": {"valore": 58452.06, "fonte": "polimi_int", "frammento": "non superiore a € 58.452,06"},
     "fs": {"valore": 7419.0, "fino_isee": 13443.97, "fonte": "polimi_int", "frammento": "€ 7.419,00 + un pasto giornaliero gratuito per un totale di € 8.248,00"},
     "fs_fascia": {"fonte": "polimi_int", "frammento": "1ª fascia Da €0,00 a € 13.443,97"},
     "servizi": {"valore": 829.0, "mensa": 829.0, "alloggio": 0, "fonte": "polimi_int", "frammento": "€ 7.419,00 + un pasto giornaliero gratuito per un totale di € 8.248,00"},
     "scadenza": {"valore": "2026-08-05", "ora": "12:00", "fonte": "polimi", "frammento": "5 agosto 2026 per gli studenti che si iscrivono ai PRIMI ANNI di tutti i corsi di studio"},
     "poveri": {"fonte": "polimi", "frammento": "gli studenti provenienti da Paesi particolarmente poveri 10 potranno consegnare al CAF convenzionato"},
     "estero": {"fonte": "polimi", "frammento": "Per ottenere l'ISEEU parificato, ci si deve esclusivamente rivolgere al CAF convenzionato con il Politecnico di Milano"},
     "anno_redditi": None,
     "chiavi": ["polimi", "politecnico"]},
    {"id": "university-of-padua", "nome": "University of Padua", "nome_lungo": "Università di Padova (regional scholarships of Veneto)", "regione": "Veneto",
     "citta": ["Padua"], "universita": "Università di Padova", "fonti": ["unipd"], "metodo": "caf",
     "isee": {"valore": 26306.25, "fonte": "unipd", "frammento": "non deve superare il limite di 26.306,25"},
     "ispe": {"valore": 43125.94, "fonte": "unipd", "frammento": "non deve superare il limite di 43.125,94 Euro"},
     "fs": {"valore": 8246.0, "fino_isee": 13153.11, "fonte": "unipd", "frammento": "Fuori sede Pendolare In sede 8.246,00 Euro 4.819,00 Euro 3.323,00 Euro 7.171,11 Euro"},
     "fs_fascia": {"fonte": "unipd", "frammento": "una maggiorazione del 15% della borsa di studio per gli studenti con ISEE inferiore o uguale a 13.153,11 Euro"},
     "scadenza": {"valore": "2026-09-30", "ora": "", "fonte": "unipd", "frammento": "Per poter concorrere alla borsa di studio è necessario, ENTRO IL 30 SETTEMBRE 2026, compiere tutti i seguenti passaggi"},
     "estero": {"fonte": "unipd", "frammento": "Il rilascio dell'ISEE Parificato deve essere richiesto esclusivamente al CAF convenzionato con l'Ateneo"},
     "anno_redditi": None,
     "chiavi": ["padova", "padua", "unipd", "esu"]},
    {"id": "ersu-palermo", "nome": "ERSU Palermo", "nome_lungo": "ERSU Palermo, regional agency for the right to university study", "regione": "Sicily",
     "citta": ["Palermo", "Agrigento", "Trapani", "Caltanissetta"], "universita": "University of Palermo and other institutions in western Sicily",
     "fonti": ["palermo"], "metodo": "caf",
     "isee": {"valore": 23000.0, "fonte": "palermo", "frammento": "ISEE – Indicatore della Situazione Economica Equivalente € 23.000,00 ISPE – Indicatore della Situazione Patrimoniale Equivalente € 52.500,00"},
     "ispe": {"valore": 52500.0, "fonte": "palermo", "frammento": "ISEE – Indicatore della Situazione Economica Equivalente € 23.000,00 ISPE – Indicatore della Situazione Patrimoniale Equivalente € 52.500,00"},
     "fs": {"valore": 8246.78, "fino_isee": 11499.99, "fonte": "palermo", "frammento": "Importo complessivo base gradualmente ridotto sino alla metà € 8.246,78 € 7.171,11"},
     "fs_fascia": {"fonte": "palermo", "frammento": "(Fascia ISEE 0: da € 0,00 a € 11.499,99)"},
     "scadenza": {"valore": "2026-07-22", "ora": "14:00", "aperta_dal": "2026-06-05", "fonte": "palermo", "frammento": "Entro le ore 14:00 di MERCOLEDÌ 22 LUGLIO 2026 Scadenza compilazione online della richiesta di partecipazione al concorso"},
     "poveri": {"fonte": "palermo", "frammento": "Soggetti stranieri provenienti da paesi particolarmente poveri (D.M. n. 166/2026): permesso di soggiorno in corso di validità o copia dell'avvenuto versamento per il suo rilascio/rinnovo e certificazione della Rappresentanza italiana nel paese di provenienza"},
     "estero": {"fonte": "palermo", "frammento": "Lo studente internazionale è tenuto a presentare l'ISEEU/ISPEU parificato calcolato da un CAF italiano"},
     "estero_scadenza": "2026-11-30",
     "estero_scad_fr": {"fonte": "palermo", "frammento": "ENTRO LE ORE 14:00 DI LUNEDI' 30 NOVEMBRE 2026 ed essere inserito nelle graduatorie di assegnazione delle borse di studio"},
     "anno_redditi": None,
     "chiavi": ["palermo", "unipa", "sicily"]},
    {"id": "ersu-catania", "nome": "ERSU Catania", "nome_lungo": "ERSU Catania, regional agency for the right to university study", "regione": "Sicily",
     "citta": ["Catania", "Enna", "Ragusa", "Siracusa"], "universita": "University of Catania and other institutions in eastern Sicily",
     "fonti": ["catania"], "metodo": "caf",
     "isee": {"valore": 25000.0, "fonte": "catania", "frammento": "ISEE - Indicatore della Situazione Economica Equivalente € 25.00,00 ISPE - Indicatore della Situazione Patrimoniale Equivalente € 60.000,00",
              "nota": "the PDF prints the ISEE limit as \"€ 25.00,00\"; the bando's own bands (half = €12,500, top band up to €25,000) confirm €25,000"},
     "isee_conferma": {"fonte": "catania", "frammento": "(fino a € 12.500,00) Importo base incrementato del 15% € 8.246,78"},
     "ispe": {"valore": 60000.0, "fonte": "catania", "frammento": "ISPE - Indicatore della Situazione Patrimoniale Equivalente € 60.000,00"},
     "fs": {"valore": 8246.78, "fino_isee": 12500.0, "fonte": "catania", "frammento": "(fino a € 12.500,00) Importo base incrementato del 15% € 8.246,78"},
     "scadenza": {"valore": "2026-08-10", "ora": "14:00", "aperta_dal": "2026-06-24", "fonte": "catania", "frammento": "Entro il 10 agosto 2026 ore 14:00 Scadenza compilazione on-line della richiesta di partecipazione al Concorso"},
     "poveri": {"fonte": "catania", "frammento": "provenienti da paesi poveri (D.M. n. 176/2026) - Fotocopia del permesso di soggiorno in corso di validità (o copia dell'avvenuto versamento per il suo rinnovo) e Certificazione della Rappresentanza italiana nel paese di provenienza"},
     "estero": {"fonte": "catania", "frammento": "Lo studente internazionale è tenuto a presentare il calcolo dell'ISEEU/ISPEU parificato rivolgendosi al CAF individuato dall'ERSU di Catania"},
     "estero_scadenza": "2026-11-30",
     "estero_scad_fr": {"fonte": "catania", "frammento": "Entro le ore 14:00 del 30 novembre 2026 Scadenza regolarizzazione richiesta di partecipazione al concorso"},
     "anno_redditi": None,
     "chiavi": ["catania", "unict", "sicily"]},
    {"id": "adisu-campania", "nome": "ADISU Campania", "nome_lungo": "ADiSURC, Campania regional agency for the right to university study", "regione": "Campania",
     "citta": ["Naples", "Salerno", "Caserta", "Benevento"], "universita": "Federico II, L'Orientale, Parthenope, Vanvitelli, Salerno, Sannio and Suor Orsola Benincasa",
     "fonti": ["adisurc"], "metodo": "caf",
     "isee": {"valore": 25500.0, "fonte": "adisurc", "frammento": "non deve superare il limite di € 25.500,00 (venticinquemilacinquecento/00)"},
     "ispe": {"valore": 54000.0, "fonte": "adisurc", "frammento": "non deve superare il limite di € 54.000,00 (cinquantaquattromila/00)"},
     "fs": {"valore": 7171.11, "fino_isee": 17000.0, "fonte": "adisurc", "frammento": "− € 7.171,11 per studente \"fuori sede\"."},
     "fs_fascia": {"fonte": "adisurc", "frammento": "incrementato del 15% nel caso in cui il valore l'indicatore della situazione economica equivalente (ISEE) sia inferiore o uguale alla metà della soglia limite, fissata in € 25.500,00."},
     "scadenza": {"valore": "2026-09-10", "ora": "12:00", "aperta_dal": "2026-07-24", "fonte": "adisurc", "frammento": "Scadenza per la partecipazione alle ore 12:00 del giorno 10 settembre 2026"},
     "poveri": {"fonte": "adisurc", "frammento": "una certificazione della Rappresentanza italiana nel Paese di provenienza che attesti che lo studente non appartiene ad una famiglia notoriamente di alto reddito ed elevato livello sociale"},
     "estero": {"fonte": "adisurc", "frammento": "entro e non oltre il 31/03/2027, a pena di esclusione, deve trasmettere all'ADiSURC copia dell'ISEE UNIVERSITARIO PARIFICATO (ISEEUP), compilata presso un CAF"},
     "estero_scadenza": "2027-03-31",
     "anno_redditi": 2024,
     "chiavi": ["adisurc", "campania", "naples", "napoli", "federico"]},
]

# Enti cercati il 31/10/2026 senza un bando 2026/27 leggibile: il sito lo dice e non pubblica cifre.
NON_LETTI = [
    {"nome": "EDISU Piemonte (Turin)", "url": "https://www.edisu.piemonte.it/", "motivo": "the server closed the connection when we tried to read it"},
    {"nome": "ADISU Puglia (Bari, Foggia, Lecce)", "url": "https://www.adisupuglia.it/", "motivo": "the server closed the connection when we tried to read it"},
    {"nome": "ARDiS Friuli Venezia Giulia (Trieste, Udine)", "url": "https://www.ardis.fvg.it/", "motivo": "the website opened, but we did not find the 2026/27 call among its published files"},
    {"nome": "Opera Universitaria (Trento)", "url": "https://www.operauni.tn.it/it/borse-di-studio/", "motivo": "the website opened, but we did not find the 2026/27 call among its published files"},
]

GL = ["us", "in", "pk", "ng", "bd", "ir"]
QUERY = ["dsu scholarship italy", "dsu scholarship", "isee parificato", "isee for international students", "italy student visa bank balance",
         "italy student visa bank statement", "italy student visa funds", "italy student visa health insurance", "particularly poor countries",
         "disco lazio scholarship", "er.go scholarship", "dsu toscana", "unimi dsu", "polimi dsu", "padova regional scholarship", "ersu palermo",
         "ersu catania", "adisurc", "iscrizione volontaria ssn", "regional scholarship italy"]


def norm(t):
    t = H.unescape(t).replace(" ", " ").replace(" ", " ").replace("­", "")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"(?:\s*\.){4,}", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def scarica(u, opener=None):
    try:
        r = (opener.open if opener else urllib.request.urlopen)(urllib.request.Request(u, headers=UA), timeout=120)
        return r.status, r.read()
    except Exception as e:  # noqa: BLE001
        return getattr(e, "code", 0) or 0, b""


def testo_di(b):
    if b[:4] == b"%PDF":
        t = subprocess.run(["pdftotext", "-", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace")
        info = subprocess.run(["pdfinfo", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace")
        m = re.search(r"ModDate:\s*(.+)", info) or re.search(r"CreationDate:\s*(.+)", info)
        data = ""
        if m:
            try:
                data = datetime.strptime(m.group(1).strip(), "%a %b %d %H:%M:%S %Y %Z").date().isoformat()
            except ValueError:
                data = ""
        return norm(t), data, "pdf"
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", s)
    return norm(re.sub(r"<[^>]+>", " ", s)), "", "html"


def leggi(f):
    """-> (meta, testo). Per l'allegato del DPCM serve prima il cookie della pagina dell'atto su Normattiva."""
    opener = None
    if f.get("cookie"):
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        scarica(f["link"], opener)
    st, b = scarica(f["url"], opener)
    if st != 200 or not b:
        return {"url": f["url"], "http": st}, ""
    t, data, tipo = testo_di(b)
    return {"url": f["url"], "http": st, "formato": tipo, "data_file": data, "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest()}, t


def cambi_bdi(anno):
    try:
        r = urllib.request.urlopen(urllib.request.Request(URL_BDI.format(anno=anno), headers={**UA, "Accept": "application/json"}), timeout=60)
        st, b = r.status, r.read()
    except Exception as e:  # noqa: BLE001
        st, b = getattr(e, "code", 0) or 0, b""
    if st != 200:
        return None, f"Banca d'Italia {anno}: HTTP {st}"
    try:
        d = json.loads(b.decode("utf-8"))
    except ValueError:
        return None, f"Banca d'Italia {anno}: risposta non JSON"
    tassi = {x["isoCode"]: float(x["avgRate"]) for x in d.get("rates", []) if x.get("exchangeConventionCode") == "C" and int(x.get("year", 0)) == anno}
    manca = [v for v in VALUTE_BDI if v not in tassi]
    if manca:
        return None, f"Banca d'Italia {anno}: mancano {manca}"
    return {v: tassi[v] for v in VALUTE_BDI}, ""


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for q in QUERY:
        for gl in GL:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.25)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl={us,in,pk,ng,bd,ir}&hl=en&q=…",
            "query": out}


def main():
    oggi = date.today().isoformat()
    errori = []
    fonti, testi = {}, {}
    for k, f in FONTI.items():
        meta, t = leggi(f)
        if not t:
            errori.append(f"fonte {k}: non leggibile (HTTP {meta['http']}): {f['url']}")
        meta.update({kk: f[kk] for kk in ("editore", "titolo", "pagina", "inglese", "link") if kk in f})
        meta["data"] = f.get("data", meta.get("data_file", ""))
        meta["letto_il"] = oggi
        fonti[k], testi[k] = meta, t
        if "inglese" in f:
            st, _ = scarica(f["inglese"])
            meta["inglese_http"] = st
            if st != 200:
                errori.append(f"fonte {k}: versione inglese non leggibile (HTTP {st})")
    for k, v in LETTURE.items():
        if v["frammento"] not in testi.get(v["fonte"], ""):
            errori.append(f"{k}: frammento non trovato in {v['fonte']}: {v['frammento'][:110]!r}")
    # elenco dei Paesi particolarmente poveri: ogni nome nel tratto dell'elenco, e nient'altro
    t = testi.get("dm176", "")
    tratto = t.split("seguente elenco:", 1)[-1].split("2. Ai fini", 1)[0]
    for p in POVERI:
        if p not in tratto:
            errori.append(f"DM 176: {p} non nell'elenco")
    resto = tratto
    for p in sorted(POVERI, key=len, reverse=True):
        resto = resto.replace(p, " ")
    if re.sub(r"[\s\d]", "", resto):
        errori.append(f"DM 176: nell'elenco c'è testo non riconosciuto: {resto.strip()[:120]!r}")
    tu = testi.get("unimi", "")
    all1 = tu.split("NAZIONI DI PRODUZIONE DEL REDDITO", 1)[-1].split("Allegato 2", 1)[0]
    for p in UNIMI_ALL1:
        if p not in all1:
            errori.append(f"UNIMI allegato 1: {p} non trovato")
    for E in ENTI:
        for campo in ("isee", "ispe", "fs", "fs_base", "fs_cifra", "fs_fascia", "servizi", "scadenza", "estero", "estero_cambio", "estero_regola",
                      "estero_scad_fr", "isee_conferma", "poveri"):
            v = E.get(campo)
            if v and v["frammento"] not in testi.get(v["fonte"], ""):
                errori.append(f"{E['id']} {campo}: frammento non trovato in {v['fonte']}: {v['frammento'][:110]!r}")
    # controlli incrociati
    L = {k: v["valore"] for k, v in LETTURE.items()}
    for E in ENTI:
        if E["isee"]["valore"] > L["isee_max"] or E["ispe"]["valore"] > L["ispe_max"]:
            errori.append(f"{E['id']}: limiti ISEE/ISPE sopra i massimi del D.D. 176/2026")
        totale = E["fs"]["valore"] + (E["servizi"]["valore"] if E.get("servizi") and E["id"] in ("dsu-toscana", "disco-lazio") else 0)
        if totale < L["dsu_fs"] - 0.01:
            errori.append(f"{E['id']}: borsa fuori sede massima ({totale}) sotto il minimo nazionale {L['dsu_fs']}")
        if E["fs"]["fino_isee"] >= E["isee"]["valore"]:
            errori.append(f"{E['id']}: fascia della borsa massima oltre il limite ISEE")
    for E in ENTI:
        if E["id"] in ("er-go", "ersu-palermo", "ersu-catania") and round(L["dsu_fs"] * 1.15, 2) != E["fs"]["valore"]:
            errori.append(f"{E['id']}: +15% non coerente ({E['fs']['valore']} ≠ {round(L['dsu_fs'] * 1.15, 2)})")
    cambi = {}
    for anno in (2024, 2025):
        c, e = cambi_bdi(anno)
        if e:
            errori.append(e)
        cambi[str(anno)] = c
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom:
        errori.append("domanda: nessun dato di autocompletamento (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    letture = {k: {"valore": v["valore"], "fonte": v["fonte"], "frammento": v["frammento"]} for k, v in LETTURE.items()}
    contenuto = {"letture": letture, "fonti": fonti, "enti": ENTI, "non_letti": NON_LETTI, "poveri": POVERI, "unimi_allegato1": UNIMI_ALL1,
                 "cambi_bdi": {"pagina": PAGINA_BDI, "api": URL_BDI, "convenzione": "foreign currency amount for 1 euro", "anni": cambi}}
    uscita = {"_nota": "Generato da raccolta/studio_italia.py: non modificare a mano (i valori letti a mano stanno in LETTURE ed ENTI dentro lo script). "
                       "Fonti: MUR, Universitaly, Poste Italiane, Polizia di Stato, Normattiva, Banca d'Italia, bandi 2026/27 degli enti per il diritto allo studio.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} valori, {len(ENTI)} enti letti, {len(NON_LETTI)} non letti; "
          f"mezzi per il visto {L['mezzi']} €; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
