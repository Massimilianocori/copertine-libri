"""Rilegge le fonti ufficiali delle sezioni in spagnolo (/es/) e portoghese (/pt/) "¿Cuánto dinero necesito para entrar a Europa?" /
"Quanto dinheiro preciso para entrar na Europa?" e scrive visaincome/dati/entrar_europa.json (dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/entrar_europa.py              # rilegge le fonti, controlla i frammenti, scrive il JSON
    python3 visaincome/raccolta/entrar_europa.py --domanda    # rifà anche l'autocompletamento di Google (hl=es e hl=pt)

GLI IMPORTI per Stato NON stanno qui: vengono da dati/schengen_residenti.json (tabella della Commissione "Reference amounts",
PDF dell'8/6/2026, letta da raccolta/schengen_residenti.py). Qui ci sono solo i testi ufficiali nelle due lingue:
- Codice frontiere Schengen, Reg. (UE) 2016/399, testo consolidato del 12/10/2025 (art. 6 condizioni di ingresso, art. 14 respingimento,
  allegato I documenti giustificativi), in spagnolo, portoghese e inglese; nessuna parola sull'assicurazione (controllato: "seguro"/"insurance");
- Reg. (UE) 2018/1806, testo consolidato del 30/12/2025: allegato I (visto obbligatorio) e II (esenti) per i Paesi dell'America Latina e dei Caraibi;
- Codice dei visti, Reg. (CE) 810/2009, testo consolidato del 2/2/2020, art. 15 (assicurazione 30.000 EUR) in spagnolo e portoghese;
- Orden PRE/1282/2007 (mezzi economici per entrare in Spagna) e Orden PRE/1283/2007 (carta de invitación), BOE, testo consolidato;
- pagina ufficiale ETIAS (travel-europe.europa.eu) in spagnolo, portoghese e inglese, letta con Chromium (è un'app JavaScript): stato attuale;
- tabella della Commissione degli importi di riferimento (stesso PDF di schengen_residenti.json): intestazione "per day and per person",
  nota della Francia, righe di Liechtenstein e Cipro (non nei dati degli importi).
EUR-Lex risponde 202 vuoto al server: i testi UE si leggono dal Publications Office (CELLAR) risolvendo il CELEX per lingua; nelle pagine si linka EUR-Lex.
A ogni lancio lo script riscarica le fonti e controlla che ogni frammento sia ancora nel testo (spazi normalizzati): se un frammento manca,
il JSON NON viene scritto (esce con codice 1) finché qualcuno non rilegge la fonte e aggiorna LETTURE/PAESI.
Fonti non raggiungibili dal server il 31/10/2026: interior.gob.es (403), policia.es (pagina della carta de invitación 404), aima.gov.pt (nessuna risposta),
diariodarepublica.pt (solo JavaScript).
"""
import hashlib
import html as H
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "entrar_europa.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
CELLAR = "https://publications.europa.eu/resource/celex/"
EURLEX = "https://eur-lex.europa.eu/legal-content/{L}/TXT/?uri=CELEX:{c}"
LINGUE_UE = {"es": ("spa", "ES"), "pt": ("por", "PT"), "en": ("eng", "EN")}
CFS = "02016R0399-20251012"     # Codice frontiere Schengen, consolidato del 12/10/2025 (ultimo consolidato elencato da CELLAR il 31/10/2026)
VIS = "02018R1806-20251230"     # Regolamento sui visti (elenchi dei Paesi), consolidato del 30/12/2025
CV = "02009R0810-20200202"      # Codice dei visti, consolidato del 2/2/2020 (lo stesso di schengen_residenti.json)

FONTI = {
    **{f"cfs_{l}": {"titolo": {"es": "Reglamento (UE) 2016/399, Código de fronteras Schengen (texto consolidado del 12/10/2025)",
                               "pt": "Regulamento (UE) 2016/399, Código das Fronteiras Schengen (texto consolidado de 12/10/2025)",
                               "en": "Regulation (EU) 2016/399, Schengen Borders Code (consolidated text of 12/10/2025)"}[l],
                    "formato": "html", "celex": CFS, "lingua": l} for l in LINGUE_UE},
    **{f"vis_{l}": {"titolo": {"es": "Reglamento (UE) 2018/1806, lista de países sometidos y exentos de visado (texto consolidado del 30/12/2025)",
                               "pt": "Regulamento (UE) 2018/1806, lista dos países sujeitos e isentos de visto (texto consolidado de 30/12/2025)",
                               "en": "Regulation (EU) 2018/1806, visa list (consolidated text of 30/12/2025)"}[l],
                    "formato": "html", "celex": VIS, "lingua": l} for l in LINGUE_UE},
    **{f"cv_{l}": {"titolo": {"es": "Reglamento (CE) 810/2009, Código de visados (texto consolidado del 2/2/2020)",
                              "pt": "Regulamento (CE) 810/2009, Código de Vistos (texto consolidado de 2/2/2020)"}[l],
                   "formato": "html", "celex": CV, "lingua": l} for l in ("es", "pt")},
    "boe_medios": {"titolo": "Orden PRE/1282/2007, de 10 de mayo, sobre medios económicos cuya disposición habrán de acreditar los extranjeros para poder efectuar su entrada en España",
                   "formato": "html", "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-9608"},
    "boe_carta": {"titolo": "Orden PRE/1283/2007, de 10 de mayo, por la que se establecen los términos y requisitos para la expedición de la carta de invitación de particulares",
                  "formato": "html", "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2007-9609"},
    **{f"etias_{l}": {"titolo": {"es": "Unión Europea, sitio oficial de ETIAS", "pt": "União Europeia, sítio oficial do ETIAS", "en": "European Union, official ETIAS website"}[l],
                      "formato": "browser", "url": f"https://travel-europe.europa.eu/{l}/etias"} for l in LINGUE_UE},
    "riferimento": {"titolo": "European Commission, Reference amounts required for the crossing of the external border fixed by national authorities",
                    "formato": "pdf", "url": "https://home-affairs.ec.europa.eu/document/download/9bf9a98f-3bd1-4e14-9b39-c9087a08a32f_en?filename=Reference_amounts_table.pdf",
                    "pagina": "https://home-affairs.ec.europa.eu/policies/schengen/border-crossing_en"},
}

# ---------------------------------------------------------------- frasi lette a mano il 31/10/2026 (frammento = parole esatte della fonte)
LETTURE = {
    # Código de fronteras Schengen, español
    "es_90_180": {"fonte": "cfs_es", "valore": [90, 180], "frammento": "una duración que no exceda de 90 días dentro de cualquier período de 180 días"},
    "es_pasaporte": {"fonte": "cfs_es", "valore": 3, "frammento": "seguirá siendo válido como mínimo tres meses después de la fecha prevista de partida del territorio de los Estados miembros"},
    "es_pasaporte_10": {"fonte": "cfs_es", "valore": 10, "frammento": "deberá haberse expedido dentro de los diez años anteriores"},
    "es_visado": {"fonte": "cfs_es", "frammento": "estar en posesión de un visado válido, cuando así lo exija el Reglamento"},
    "es_objeto": {"fonte": "cfs_es", "frammento": "estar en posesión de documentos que justifiquen el objeto y las condiciones de la estancia prevista y disponer de medios de subsistencia suficientes, tanto para el período de estancia previsto como para el regreso al país de origen"},
    "es_sis": {"fonte": "cfs_es", "frammento": "no estar inscrito como no admisible en el SIS"},
    "es_amenaza": {"fonte": "cfs_es", "frammento": "no suponer una amenaza para el orden público, la seguridad interior, la salud pública o las relaciones internacionales de ninguno de los Estados miembros"},
    "es_biometria": {"fonte": "cfs_es", "frammento": "facilitar los datos biométricos, de ser necesario"},
    "es_lista": {"fonte": "cfs_es", "frammento": "En el anexo I figura una lista no exhaustiva de documentos justificativos que la guardia de fronteras podrá pedir"},
    "es_medios": {"fonte": "cfs_es", "frammento": "La comprobación de los medios de subsistencia suficientes podrá basarse en el dinero efectivo, los cheques de viaje y las tarjetas de crédito que obren en poder del nacional de un tercer país."},
    "es_medios_precios": {"fonte": "cfs_es", "frammento": "se usarán como referencia los precios medios en el Estado o Estados miembros de que se trate del alojamiento y de la alimentación, en hospedaje económico multiplicado por el número de días de estancia"},
    "es_invitacion_medios": {"fonte": "cfs_es", "frammento": "también podrán constituir prueba de medios adecuados de subsistencia"},
    "es_toma_cargo": {"fonte": "cfs_es", "frammento": "Las declaraciones de invitación, cuando las prevea el Derecho interno, y las declaraciones de toma a cargo definidas por el Derecho interno, en caso de que el nacional de un tercer país se aloje en el domicilio de una persona de acogida"},
    "es_anexo_invitacion": {"fonte": "cfs_es", "frammento": "invitación de un particular si se hospeda en el domicilio de éste"},
    "es_anexo_hotel": {"fonte": "cfs_es", "frammento": "documento justificativo del establecimiento de hospedaje o cualquier otro documento pertinente que indique el alojamiento que se haya previsto"},
    "es_anexo_itinerario": {"fonte": "cfs_es", "frammento": "confirmación de la reserva de un viaje organizado o cualquier otro documento que indique los planes de viaje previstos"},
    "es_anexo_regreso": {"fonte": "cfs_es", "frammento": "billete de vuelta o de circuito turístico"},
    "es_anexo_negocios": {"fonte": "cfs_es", "frammento": "la invitación de una empresa o de una autoridad para participar en reuniones, conferencias o manifestaciones de carácter comercial, industrial o laboral"},
    "es_anexo_estudios": {"fonte": "cfs_es", "frammento": "documento de matrícula de un centro de enseñanza"},
    "es_denegacion": {"fonte": "cfs_es", "frammento": "Se negará la entrada en el territorio de los Estados miembros a los nacionales de terceros países que no cumplan todas las condiciones de entrada"},
    "es_motivada": {"fonte": "cfs_es", "frammento": "Solo podrá denegarse la entrada mediante una resolución motivada en la que se indiquen los motivos exactos de dicha denegación."},
    "es_recurso": {"fonte": "cfs_es", "frammento": "Las personas a las que se deniegue la entrada tendrán derecho a recurrir dicha resolución."},
    # Código das Fronteiras Schengen, português (texto oficial da UE, português europeu)
    "pt_90_180": {"fonte": "cfs_pt", "valore": [90, 180], "frammento": "de duração não superior a 90 dias em qualquer período de 180 dias"},
    "pt_passaporte": {"fonte": "cfs_pt", "valore": 3, "frammento": "ser válido pelo menos para os três meses seguintes à data prevista de partida do território dos Estados-Membros"},
    "pt_passaporte_10": {"fonte": "cfs_pt", "valore": 10, "frammento": "ter sido emitido há menos de 10 anos"},
    "pt_visto": {"fonte": "cfs_pt", "frammento": "Estar na posse de um visto válido, se tal for exigido"},
    "pt_objeto": {"fonte": "cfs_pt", "frammento": "Justificar o objetivo e as condições da estada prevista e dispor de meios de subsistência suficientes, tanto para a duração dessa estada como para o regresso ao país de origem"},
    "pt_sis": {"fonte": "cfs_pt", "frammento": "Não estar indicado no SIS para efeitos de não admissão"},
    "pt_ameaca": {"fonte": "cfs_pt", "frammento": "Não ser considerado suscetível de perturbar a ordem pública, a segurança interna, a saúde pública ou as relações internacionais de qualquer Estado-Membro"},
    "pt_biometria": {"fonte": "cfs_pt", "frammento": "Fornecer dados biométricos, se for necessário"},
    "pt_lista": {"fonte": "cfs_pt", "frammento": "Consta do anexo I uma lista não exaustiva dos documentos comprovativos que o guarda de fronteira pode solicitar"},
    "pt_meios": {"fonte": "cfs_pt", "frammento": "A verificação da suficiência de meios de subsistência pode basear-se no dinheiro líquido, nos cheques de viagem e nos cartões de crédito na posse do nacional de país terceiro."},
    "pt_meios_precos": {"fonte": "cfs_pt", "frammento": "com referência aos preços médios de alojamento e de alimentação, em condições económicas, no Estado-Membro ou Estados-Membros em causa, multiplicados pelo número de dias de estada"},
    "pt_convite_meios": {"fonte": "cfs_pt", "frammento": "podem igualmente constituir uma prova de meios de subsistência suficientes"},
    "pt_termo": {"fonte": "cfs_pt", "frammento": "As declarações de tomada a cargo, quando estejam previstas no direito nacional, e os termos de responsabilidade assinados por anfitriões, tal como definidos pelo direito nacional"},
    "pt_anexo_convite": {"fonte": "cfs_pt", "frammento": "convite do anfitrião, se for esse o caso"},
    "pt_anexo_hotel": {"fonte": "cfs_pt", "frammento": "documento comprovativo emitido pelo estabelecimento que fornece o alojamento, ou qualquer outro documento adequado que indique o alojamento previsto"},
    "pt_anexo_itinerario": {"fonte": "cfs_pt", "frammento": "confirmação da reserva de uma viagem organizada ou qualquer outro documento adequado que indique os planos de viagem"},
    "pt_anexo_regresso": {"fonte": "cfs_pt", "frammento": "bilhete de ida e volta ou bilhete de circuito turístico"},
    "pt_anexo_negocios": {"fonte": "cfs_pt", "frammento": "convite de uma empresa ou entidade para participar em encontros, conferências ou manifestações de caráter comercial, industrial ou profissional"},
    "pt_anexo_estudos": {"fonte": "cfs_pt", "frammento": "boletim de matrícula num estabelecimento de ensino"},
    "pt_recusa": {"fonte": "cfs_pt", "frammento": "A entrada nos territórios dos Estados-Membros é recusada a qualquer nacional de país terceiro que não preencha todas as condições de entrada"},
    "pt_fundamentada": {"fonte": "cfs_pt", "frammento": "A entrada só pode ser recusada por decisão fundamentada que indique as razões precisas da recusa"},
    "pt_recurso": {"fonte": "cfs_pt", "frammento": "As pessoas a quem tenha sido recusada a entrada têm direito de recurso."},
    # Código de visados / Código de Vistos, art. 15
    "es_seguro_visado": {"fonte": "cv_es", "frammento": "Los solicitantes de un visado uniforme para una o dos entradas deberán demostrar que poseen un seguro médico de viaje adecuado y válido"},
    "es_seguro_30000": {"fonte": "cv_es", "valore": 30000, "frammento": "La cobertura mínima será de 30 000 EUR."},
    "es_seguro_territorio": {"fonte": "cv_es", "frammento": "El seguro deberá ser válido en el territorio de los Estados miembros y cubrir todo el período de estancia o tránsito que la persona haya previsto."},
    "pt_seguro_visto": {"fonte": "cv_pt", "frammento": "Os requerentes de visto uniforme para uma ou duas entradas devem provar que possuem um seguro médico de viagem adequado e válido"},
    "pt_seguro_30000": {"fonte": "cv_pt", "valore": 30000, "frammento": "A cobertura do seguro deve ser, no mínimo, 30 000 EUR."},
    "pt_seguro_territorio": {"fonte": "cv_pt", "frammento": "O seguro deve ser válido em todo o território dos Estados-Membros e cobrir a totalidade da duração prevista de estada ou trânsito do interessado."},
    # Orden PRE/1282/2007 (España, medios económicos)
    "boe_requeridos": {"fonte": "boe_medios", "frammento": "si son requeridos para ello por los funcionarios encargados de efectuar el control de entrada de personas en territorio español"},
    "boe_10": {"fonte": "boe_medios", "valore": 0.10, "frammento": "el 10% del salario mínimo interprofesional bruto o su equivalente legal en moneda extranjera multiplicada por el número de días que pretendan permanecer en España y por el número de personas que viajen a su cargo"},
    "boe_90": {"fonte": "boe_medios", "valore": 0.90, "frammento": "Dicha cantidad será, en todo caso, de un mínimo que represente el 90% del salario mínimo interprofesional bruto vigente en cada momento o su equivalente legal en moneda extranjera por persona, con independencia del tiempo de estancia previsto."},
    "boe_dias": {"fonte": "boe_medios", "frammento": "el número de días resultantes desde la fecha de entrada en España hasta la fecha de salida que figure en el billete referido en la letra b) de este apartado, ambas fechas incluidas"},
    "boe_billete": {"fonte": "boe_medios", "frammento": "se acreditará disponer del billete o billetes nominativos, intransferibles y cerrados, en el medio de transporte que pretendan utilizar"},
    "boe_efectivo": {"fonte": "boe_medios", "frammento": "mediante exhibición de los mismos, en el caso de que los posean en efectivo, o mediante la presentación de cheques certificados, cheques de viaje, cartas de pago, o tarjetas de crédito, que deberán ir acompañadas del extracto de la cuenta bancaria o una libreta bancaria puesta al día"},
    "boe_no_cartas": {"fonte": "boe_medios", "frammento": "(no se admitirán cartas de entidades bancarias ni extractos bancarios de Internet)"},
    "boe_denegara": {"fonte": "boe_medios", "frammento": "se denegará su entrada en territorio español según lo establecido reglamentariamente"},
    "boe_reducir": {"fonte": "boe_medios", "frammento": "podrán permitir la entrada, reduciendo el tiempo de estancia en proporción a la cuantía de los recursos de que se dispongan"},
    # Orden PRE/1283/2007 (carta de invitación)
    "carta_alojamiento": {"fonte": "boe_carta", "frammento": "asumiendo el compromiso de costear, durante el período de estancia del beneficiario, todos los gastos relativos a su alojamiento"},
    "carta_frontera": {"fonte": "boe_carta", "frammento": "que podrá ser exigida en el puesto fronterizo español al extranjero que pretenda entrar en España y podrá ser aportada por éste ante el Consulado español, cuando se trate de nacionales de países sujetos al visado de estancia"},
    "carta_hospedaje": {"fonte": "boe_carta", "frammento": "En ningún caso, la carta de invitación suplirá la acreditación por el extranjero de los demás requisitos exigidos para la entrada, ya que únicamente justifica el requisito relativo al hospedaje."},
    "carta_comisaria": {"fonte": "boe_carta", "frammento": "deberá dirigir su solicitud a la Comisaría de Policía de su lugar de residencia, que será la competente para su tramitación y expedición"},
    "carta_quien": {"fonte": "boe_carta", "frammento": "ya sea ciudadano español, nacional de un Estado miembro de la Unión Europea o beneficiario del régimen comunitario o extranjero residente legal en España"},
    "carta_vivienda": {"fonte": "boe_carta", "frammento": "El invitante aportará documentación acreditativa de la disponibilidad de la vivienda (título de propiedad, contrato de arrendamiento u otros, de acuerdo con la legislación civil vigente)."},
    "carta_vinculo": {"fonte": "boe_carta", "frammento": "Relación o vínculo que mantiene con el invitado."},
    "carta_datos": {"fonte": "boe_carta", "frammento": "Nombre, apellidos, lugar y fecha de nacimiento, nacionalidad, lugar concreto de su residencia o domicilio y número de pasaporte del invitado."},
    "carta_periodo": {"fonte": "boe_carta", "frammento": "Período durante el cual está prevista la estancia del invitado, especificando, de manera aproximada, el primer y el último día de la misma."},
    "carta_varias": {"fonte": "boe_carta", "frammento": "la invitación podrá referirse a varias personas"},
    "carta_brevedad": {"fonte": "boe_carta", "frammento": "de cara a resolver en el sentido que proceda en relación con la misma con la mayor brevedad posible"},
    "carta_entrevista": {"fonte": "boe_carta", "frammento": "se podrá emplazar al solicitante para mantener una entrevista personal"},
    "carta_quince": {"fonte": "boe_carta", "valore": 15, "frammento": "que no podrá exceder de quince días"},
    "carta_tasa": {"fonte": "boe_carta", "frammento": "El abono de la tasa habrá de realizarse en el plazo de un mes desde la referida notificación, y el justificante de dicho abono deberá aportarse para recoger la Carta de invitación."},
    "carta_denegacion": {"fonte": "boe_carta", "frammento": "La denegación, en su caso, de la solicitud de Carta de invitación habrá de ser motivada"},
    "carta_modelo": {"fonte": "boe_carta", "frammento": "de acuerdo con el modelo establecido en el anexo de la presente Orden ministerial"},
    # ETIAS (sito ufficiale, 31/10/2026)
    "etias_es_estado": {"fonte": "etias_es", "frammento": "Actualmente, el sistema ETIAS no está en funcionamiento y no se están tramitando solicitudes de autorización de viaje."},
    "etias_es_fecha": {"fonte": "etias_es", "frammento": "La Unión Europea informará sobre la fecha concreta de inicio del ETIAS varios meses antes de su entrada en funcionamiento."},
    "etias_es_que": {"fonte": "etias_es", "valore": 30, "frammento": "ETIAS es la nueva autorización de viaje para que viajeros exentos de visa puedan viajar a 30 países europeos."},
    "etias_es_tasa": {"fonte": "etias_es", "valore": 20, "frammento": "Pague una tasa de solicitud de 20 EUR"},
    "etias_es_90": {"fonte": "etias_es", "valore": 90, "frammento": "La estancia es de hasta 90 días"},
    "etias_pt_estado": {"fonte": "etias_pt", "frammento": "O ETIAS não está atualmente em funcionamento e não são aceites pedidos de autorização de viagem neste momento."},
    "etias_pt_data": {"fonte": "etias_pt", "frammento": "A União Europeia informará sobre a data específica do início do ETIAS vários meses antes do seu lançamento."},
    "etias_pt_que": {"fonte": "etias_pt", "valore": 30, "frammento": "O ETIAS é a nova autorização de viagem para os viajantes isentos de visto que pretendam entrar em 30 países europeus."},
    "etias_pt_taxa": {"fonte": "etias_pt", "valore": 20, "frammento": "Pagar uma taxa de pedido de 20 EUR"},
    "etias_pt_90": {"fonte": "etias_pt", "valore": 90, "frammento": "Permanecer até 90 dias"},
    "etias_en_estado": {"fonte": "etias_en", "frammento": "ETIAS is currently not in operation and no applications for travel authorisations are collected at this point."},
    # tabella degli importi di riferimento (stesso PDF di schengen_residenti.json)
    "rif_persona": {"fonte": "riferimento", "frammento": "Minimum amount per day and per person"},
    "rif_francia": {"fonte": "riferimento", "frammento": "Where there is a hotel reservation for part of the stay, the amount required is € 65.00 for the period covered by the reservation and € 120.00 for the rest of the stay."},
    "rif_liechtenstein": {"fonte": "riferimento", "frammento": "Liechtenstein around CHF 100 around CHF 30 - students"},
    "rif_cipro": {"fonte": "riferimento", "frammento": "Cyprus on a case-by-case basis"},
}

# Parole che NON devono comparire nel Codice frontiere Schengen (assicurazione: le condizioni di ingresso non la chiedono). Se una compare,
# lo script si ferma: le pagine dicono "el Código de fronteras Schengen no menciona el seguro".
ASSENTI = {"cfs_en": ["insurance"], "cfs_es": ["seguro médico", "seguro de viaje", "seguro de enfermedad"], "cfs_pt": ["seguro médico", "seguro de viagem", "seguro de doença"]}

# Paesi dell'America Latina e dei Caraibi (e Spagna/Portogallo non servono): nome nelle tre lingue come scritto negli allegati del Reg. 2018/1806,
# allegato atteso (1 = visto obbligatorio, 2 = esenti), slug, aggettivo spagnolo e portoghese per i testi.
PAESI = [
    {"id": "argentina", "es": "Argentina", "pt": "Argentina", "en": "Argentina", "allegato": 2},
    {"id": "bolivia", "es": "Bolivia", "pt": "Bolívia", "en": "Bolivia", "allegato": 1},
    {"id": "brasil", "es": "Brasil", "pt": "Brasil", "en": "Brazil", "allegato": 2},
    {"id": "chile", "es": "Chile", "pt": "Chile", "en": "Chile", "allegato": 2},
    {"id": "colombia", "es": "Colombia", "pt": "Colômbia", "en": "Colombia", "allegato": 2},
    {"id": "costa-rica", "es": "Costa Rica", "pt": "Costa Rica", "en": "Costa Rica", "allegato": 2},
    {"id": "cuba", "es": "Cuba", "pt": "Cuba", "en": "Cuba", "allegato": 1},
    {"id": "ecuador", "es": "Ecuador", "pt": "Equador", "en": "Ecuador", "allegato": 1},
    {"id": "el-salvador", "es": "El Salvador", "pt": "Salvador", "en": "El Salvador", "allegato": 2},
    {"id": "guatemala", "es": "Guatemala", "pt": "Guatemala", "en": "Guatemala", "allegato": 2},
    {"id": "haiti", "es": "Haití", "pt": "Haiti", "en": "Haiti", "allegato": 1},
    {"id": "honduras", "es": "Honduras", "pt": "Honduras", "en": "Honduras", "allegato": 2},
    {"id": "mexico", "es": "México", "pt": "México", "en": "Mexico", "allegato": 2},
    {"id": "nicaragua", "es": "Nicaragua", "pt": "Nicarágua", "en": "Nicaragua", "allegato": 2},
    {"id": "panama", "es": "Panamá", "pt": "Panamá", "en": "Panama", "allegato": 2},
    {"id": "paraguay", "es": "Paraguay", "pt": "Paraguai", "en": "Paraguay", "allegato": 2},
    {"id": "peru", "es": "Perú", "pt": "Peru", "en": "Peru", "allegato": 2},
    {"id": "republica-dominicana", "es": "República Dominicana", "pt": "República Dominicana", "en": "Dominican Republic", "allegato": 1},
    {"id": "uruguay", "es": "Uruguay", "pt": "Uruguai", "en": "Uruguay", "allegato": 2},
    {"id": "venezuela", "es": "Venezuela", "pt": "Venezuela", "en": "Venezuela", "allegato": 2},
]
TITOLI_ALLEGATI = {
    "es": ("ANEXO I LISTA DE TERCEROS PAÍSES CUYOS NACIONALES ESTÁN SOMETIDOS A LA OBLIGACIÓN DE VISADO",
           "ANEXO II LISTA DE TERCEROS PAÍSES CUYOS NACIONALES ESTÁN EXENTOS DE LA OBLIGACIÓN DE VISADO", "ANEXO III"),
    "pt": ("ANEXO I LISTA DOS PAÍSES TERCEIROS CUJOS NACIONAIS ESTÃO SUJEITOS À OBRIGAÇÃO DE VISTO",
           "ANEXO II LISTA DOS PAÍSES TERCEIROS CUJOS NACIONAIS ESTÃO ISENTOS DA OBRIGAÇÃO DE VISTO", "ANEXO III"),
    "en": ("ANNEX I LIST OF THIRD COUNTRIES WHOSE NATIONALS ARE REQUIRED TO BE IN POSSESSION OF A VISA",
           "ANNEX II LIST OF THIRD COUNTRIES WHOSE NATIONALS ARE EXEMPT FROM THE REQUIREMENT", "ANNEX III"),
}

# ---------------------------------------------------------------- domanda (autocompletamento Google)
QUERY = {
    "es": {"gl": ["es", "mx", "co", "ar", "pe", "ve"],
           "q": ["cuanto dinero necesito para entrar a", "cuánto dinero necesito para entrar a españa", "cuanto dinero necesito para entrar a europa",
                 "cuanto dinero necesito para entrar a italia", "cuanto dinero necesito para entrar a francia", "cuanto dinero necesito para entrar a alemania",
                 "cuanto dinero necesito para entrar a suiza", "cuanto dinero necesito para entrar a portugal", "cuanto dinero hay que llevar a europa",
                 "carta de invitación españa", "requisitos para entrar a europa desde", "requisitos para entrar a españa", "requisitos para entrar a europa",
                 "seguro de viaje obligatorio para europa", "seguro de viaje para europa", "etias", "etias para"]},
    "pt": {"gl": ["br", "pt"],
           "q": ["quanto dinheiro precisa para entrar na", "quanto dinheiro precisa para entrar na europa", "quanto dinheiro precisa para entrar em portugal",
                 "quanto dinheiro levar para portugal", "quanto dinheiro levar para portugal imigração", "requisitos para entrar em portugal",
                 "requisitos para entrar na europa", "seguro viagem obrigatório europa", "seguro viagem obrigatório", "carta convite espanha", "carta convite",
                 "etias", "imigração portugal"]},
}


def norm(t):
    t = re.sub(r"\s+", " ", t.replace(" ", " ").replace(" ", " ")).strip()
    return re.sub(r" ([,.;:)])", r"\1", t)


def scarica(u, accetta=None, lingua=None):
    h = dict(UA)
    if accetta:
        h["Accept"] = accetta
    if lingua:
        h["Accept-Language"] = lingua
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=120)
            return r.status, r.read(), r.geturl()
        except Exception as e:  # noqa: BLE001
            st = getattr(e, "code", None)
            if st:
                return st, b"", u
            time.sleep(3)
    return None, b"", u


def risolvi_celex(celex, lingua3):
    """CELLAR risponde 303 verso la manifestazione nella lingua chiesta (indirizzo http): si segue a mano in https."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    op = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(CELLAR + celex, headers={**UA, "Accept": "application/xhtml+xml", "Accept-Language": lingua3})
    try:
        op.open(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303) and e.headers.get("Location"):
            return e.headers["Location"].replace("http://", "https://", 1)
    return None


def testo_di(b, formato):
    if formato == "pdf":
        return norm(subprocess.run(["pdftotext", "-raw", "-", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace"))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    return norm(H.unescape(re.sub(r"<[^>]+>", " ", t)))


def leggi_browser(urls):
    r = subprocess.run(["node", str(RADICE / "raccolta" / "browser.js")] + urls, capture_output=True, text=True, timeout=600)
    return json.loads(r.stdout or "{}")


def autocompleta(q, gl, hl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": hl, "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for hl, Q in QUERY.items():
        for gl in Q["gl"]:
            for q in Q["q"]:
                out[f"{hl}-{gl}|{q}"] = autocompleta(q, gl, hl)
                time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<es|mx|co|ar|pe|ve|br|pt>&hl=<es|pt>&q=…",
            "query": out}


def main():
    oggi = date.today().isoformat()
    errori, testi, fonti = [], {}, {}
    browser = [F["url"] for F in FONTI.values() if F["formato"] == "browser"]
    letti = leggi_browser(browser)
    for k, F in FONTI.items():
        if F["formato"] == "browser":
            r = letti.get(F["url"], {})
            if r.get("http") != 200 or not r.get("testo"):
                errori.append(f"{k}: HTTP {r.get('http')} ({F['url']})")
                continue
            b = r["testo"].encode("utf-8")
            tx = norm(r["testo"])
            meta = {"url": F["url"], "pubblico": F["url"]}
        else:
            if "celex" in F:
                l3, L2 = LINGUE_UE[F["lingua"]]
                u = risolvi_celex(F["celex"], l3)
                if not u:
                    errori.append(f"{k}: CELEX {F['celex']} non risolto ({l3})")
                    continue
                st, b, _ = scarica(u, "application/xhtml+xml", l3)
                meta = {"url": u, "pubblico": EURLEX.format(L=L2, c=F["celex"])}
            else:
                st, b, _ = scarica(F["url"])
                meta = {"url": F["url"], "pubblico": F["url"]}
            if st != 200 or not b:
                errori.append(f"{k}: HTTP {st} ({meta['url']})")
                continue
            tx = testo_di(b, F["formato"])
        testi[k] = tx
        fonti[k] = {**{c: F[c] for c in F}, **meta, "http": 200, "letto_il": oggi, "byte": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    for k, L in LETTURE.items():
        if norm(L["frammento"]) not in testi[L["fonte"]]:
            errori.append(f"frammento non trovato ({k}, {L['fonte']}): {L['frammento']!r}")
    for k, parole in ASSENTI.items():
        for p in parole:
            if p.lower() in testi[k].lower():
                errori.append(f"{k}: compare «{p}»: rileggere il Codice frontiere e le pagine sull'assicurazione")
    # allegati del Reg. 2018/1806: ogni Paese nell'allegato atteso e non nell'altro (parola intera)
    for l, (t1, t2, t3) in TITOLI_ALLEGATI.items():
        tx = testi[f"vis_{l}"]
        i1, i2 = tx.find(t1), tx.find(t2)
        i3 = tx.find(t3, i2 + 1)
        if min(i1, i2, i3) < 0:
            errori.append(f"vis_{l}: titoli degli allegati non trovati")
            continue
        a1, a2 = tx[i1:i2], tx[i2:i3]
        for P in PAESI:
            n = P[l]
            dentro = [bool(re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", a)) for a in (a1, a2)]
            if dentro != [P["allegato"] == 1, P["allegato"] == 2]:
                errori.append(f"vis_{l}: {n} non solo nell'allegato {P['allegato']} (allegato I: {dentro[0]}, allegato II: {dentro[1]})")
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not domanda:
        sys.exit("ERRORE: nessuna domanda salvata: lanciare con --domanda")
    dati = {
        "_nota": "Generato da raccolta/entrar_europa.py: non modificare a mano. Gli importi per Stato sono in dati/schengen_residenti.json.",
        "letto_il": oggi,
        "fonti": fonti,
        "letture": LETTURE,
        "assenti": ASSENTI,
        "paesi": PAESI,
        "domanda": domanda,
    }
    cont = {k: dati[k] for k in ("fonti", "letture", "assenti", "paesi")}
    dati["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(LETTURE)} frasi, {len(PAESI)} Paesi negli allegati del Reg. 2018/1806, "
          f"domanda del {domanda['data']} ({len(domanda['query'])} ricerche).")


if __name__ == "__main__":
    main()
