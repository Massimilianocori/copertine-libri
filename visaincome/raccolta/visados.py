"""Rilegge le fonti ufficiali della sezione in spagnolo (/es/visados/) e portoghese (/pt/vistos/) "visti di lunga durata per nazionalità"
e scrive visaincome/dati/visados.json (dal 4/11/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/visados.py              # rilegge le fonti, controlla i frammenti e le impronte, legge i cambi, scrive il JSON
    python3 visaincome/raccolta/visados.py --domanda    # rifà anche l'autocompletamento di Google (hl=es gl=co/mx/ar/cl/pe, hl=pt gl=br)

Cosa c'è (solo fonti ufficiali; ogni cifra ha un frammento del testo ufficiale che lo script ritrova a ogni lancio):
- listini delle tasse dei consolati di Spagna (exteriores.gob.es): Bogotá (5/6/2024, con l'avviso di tasse nuove dal 1/10/2026), Santiago del Cile
  (dall'1/1/2026), Buenos Aires (dall'1/1/2026), Lima (2026, pubblicato il 12/6/2026), Città del Messico (pagina "Tasas para visados", dall'1/1/2026, e
  PDF del 16/12/2025), San Paolo (PDF stampato il 16/12/2025) e Brasília (1/1/2026);
- pagine del Consolato di Spagna a Buenos Aires sui visti nazionali (non lucrativo, nomadi digitali, studio): requisiti e documenti;
- Real Decreto 1155/2024 (BOE, testo consolidato): art. 62 (400% IPREM) e art. 35 (studio: 100% IPREM, familiari 75%/50%);
- Ministério dos Negócios Estrangeiros di Portogallo (vistos.mne.gov.pt): emolumenti (110 €), meios de subsistência (RMMG 920 €), residência (D7, D8,
  studenti, PB4 per il Brasile), CPLP, procura de trabalho (sospeso), tipo de visto;
- Decreto brasiliano 11.156/2022 (portale della Camera dei deputati): Accordo di mobilità CPLP in vigore per il Brasile dall'1/4/2022;
- tabelle dei diritti consolari italiani del IV trimestre 2026: Buenos Aires, Santiago del Cile, Città del Messico (testo) e San Paolo (PDF fatto
  di un'immagine: letto a vista il 4/11/2026, si controlla solo l'impronta SHA-256 del file: se cambia, lo script si ferma);
- cambi ufficiali dello stesso giorno: BCE (EUR/USD, EUR/MXN, EUR/BRL, file storico a 90 giorni), Colombia TRM (datos.gov.co), Argentina BCRA
  (api.bcra.gob.ar), Perù BCRP (serie PD04640PD), Cile SII (dólar observado). Le valute senza cambio BCE si convertono passando dal dollaro.
I mezzi per lo studio in Italia (10.179,85 € l'anno) restano in dati/studio_italia.json; SMI, IPREM e RMMG restano in dati/programmi.json
(il generatore controlla che coincidano con le cifre scritte qui nei frammenti).
Se un frammento manca o un'impronta cambia, il JSON NON viene scritto (esce con codice 1) finché qualcuno non rilegge la fonte.
Non letti (4/11/2026): listino 2026 del consolato di Bogotá (annunciato dal 1/10/2026, non pubblicato), tabelle italiane del IV trimestre 2026 di
Bogotá e Lima (ultime: II trimestre 2024 e IV trimestre 2025), planalto.gov.br (risponde "Acesso Negado").
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
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "visados.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
EXT = "https://www.exteriores.gob.es"
BA = EXT + "/Consulados/buenosaires/es/ServiciosConsulares/Paginas/index.aspx?scca=Visados&scco=Argentina&scd=40&scs=Visados+Nacionales+-+"
MNE = "https://vistos.mne.gov.pt/pt/vistos-nacionais/"

FONTI = {
    # ---- Spagna: listini dei consolati (data del listino = data scritta nel documento)
    "es_tasas_co": {"titolo": "Consulado General de España en Bogotá, Listado de tasas consulares – Sección de visados", "formato": "pdf", "paese": "colombia",
                    "url": EXT + "/DocumentosAuxiliaresSC/Colombia/BOGOT%C3%81%20(C)/TASAS%20DE%20VISADOS%20A%C3%91O%202024%20junio.pdf", "data_listino": "2024-06-05"},
    "es_tasas_co_aviso": {"titolo": "Consulado General de España en Bogotá, «Actualización tasas a partir de 1 de octubre 2026» (15/9/2026)", "formato": "html", "paese": "colombia",
                          "url": EXT + "/Consulados/bogota/es/Comunicacion/Noticias/Paginas/Articulos/ACTUALIZACI%c3%93N-TASAS-A-PARTIR-DE-1-DE-OCTUBRE-2026.aspx"},
    "es_tasas_cl": {"titolo": "Consulado General de España en Santiago de Chile, Listado de tasas consulares (a partir del 1 de enero de 2026)", "formato": "pdf", "paese": "chile",
                    "url": EXT + "/DocumentosAuxiliaresSC/Chile/SANTIAGO%20DE%20CHILE%20(C)/TASAS%20CONSULARES.pdf", "data_listino": "2026-01-01"},
    "es_tasas_ar": {"titolo": "Consulado General de España en Buenos Aires, Tasas consulares a partir del 01-01-2026", "formato": "pdf", "paese": "argentina",
                    "url": EXT + "/Consulados/buenosaires/es/ServiciosConsulares/PublishingImages/Paginas/Tasas-consulares/Hoja%20informativa%20tasas%20consulares%20a%201%20de%20enero%20de%202026.pdf",
                    "data_listino": "2026-01-01"},
    "es_tasas_pe": {"titolo": "Consulado General de España en Lima, Tasas consulares 2026 (publicado el 12/6/2026)", "formato": "pdf", "paese": "peru",
                    "url": EXT + "/DocumentosAuxiliaresSC/Per%c3%ba/LIMA%20%28C%29/Tasas%20consulares%202024.pdf", "data_listino": "2026-06-12"},
    "es_tasas_mx": {"titolo": "Consulado General de España en México, Tasas para visados (en vigor a partir del 1 de enero de 2026)", "formato": "html", "paese": "mexico",
                    "url": EXT + "/Consulados/mexico/es/ServiciosConsulares/Paginas/TasasVisados.aspx", "data_listino": "2026-01-01"},
    "es_tasas_mx_pdf": {"titolo": "Consulado General de España en México, Precios recaudación consular 2026 (impreso el 16/12/2025)", "formato": "pdf", "paese": "mexico",
                        "url": EXT + "/Consulados/mexico/es/ServiciosConsulares/Documents/TASAS%202026%20(DEFINITIVAS).pdf", "data_listino": "2025-12-16"},
    "es_tasas_br": {"titolo": "Consulado General de España en São Paulo, Precios recaudación consular (impreso el 16/12/2025)", "formato": "pdf", "paese": "brasil",
                    "url": EXT + "/Consulados/SAOPAULO/es/ServiciosConsulares/Documents/Tasas%20Consulares.pdf", "data_listino": "2025-12-16"},
    "es_tasas_br_bsb": {"titolo": "Embajada de España en Brasilia, Sección consular, Tasas consulares / Taxas consulares (01/01/2026)", "formato": "pdf", "paese": "brasil",
                        "url": EXT + "/DocumentosAuxiliaresSC/Brasil/BRASILIA%20(E)/tasasconsulares.pdf", "data_listino": "2026-01-01"},
    # ---- Spagna: requisiti (consolato di Buenos Aires) e regolamento
    "es_ba_nl": {"titolo": "Consulado General de España en Buenos Aires, Visado de residencia no lucrativa", "formato": "html", "url": BA + "Visado+de+residencia+no+lucrativa"},
    "es_ba_nd": {"titolo": "Consulado General de España en Buenos Aires, Visado de residencia para teletrabajo (nómada digital)", "formato": "html",
                 "url": BA + "Visado+de+residencia+para+teletrabajo+(n%C3%B3mada+digital)"},
    "es_ba_es": {"titolo": "Consulado General de España en Buenos Aires, Visado de estudios", "formato": "html", "url": BA + "Visado+de+estudios"},
    "es_rd1155": {"titolo": "Real Decreto 1155/2024, Reglamento de la Ley Orgánica 4/2000 (BOE, texto consolidado)", "formato": "html",
                  "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2024-24099"},
    # ---- Portogallo (MNE)
    "pt_emol": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Emolumentos", "formato": "html", "url": MNE + "informacao-geral/emolumentos"},
    "pt_meios": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Meios de subsistência", "formato": "html", "url": MNE + "documentacao-instrutoria/meios-de-subsistencia"},
    "pt_res": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Documentação instrutória – Residência", "formato": "html", "url": MNE + "documentacao-instrutoria/residencia"},
    "pt_cplp": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Documentação instrutória – CPLP", "formato": "html", "url": MNE + "documentacao-instrutoria/cplp"},
    "pt_proc": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Procura de Trabalho Qualificado", "formato": "html", "url": MNE + "documentacao-instrutoria/procura-de-trabalho"},
    "pt_tipo": {"titolo": "Ministério dos Negócios Estrangeiros, Vistos nacionais – Tipo de visto", "formato": "html", "url": MNE + "informacao-geral/tipo-de-visto"},
    "br_cplp": {"titolo": "Decreto nº 11.156, de 29 de julho de 2022 (promulga o Acordo sobre a Mobilidade CPLP), Câmara dos Deputados, Legislação Informatizada",
                "formato": "html", "url": "https://www2.camara.leg.br/legin/fed/decret/2022/decreto-11156-29-julho-2022-793054-publicacaooriginal-165820-pe.html"},
    # ---- Italia: tabelle dei diritti consolari, IV trimestre 2026
    "it_tab_ar": {"titolo": "Consolato Generale d'Italia a Buenos Aires, Tabella diritti consolari IV trimestre 2026", "formato": "pdf", "paese": "argentina",
                  "url": "https://consbuenosaires.esteri.it/wp-content/uploads/2026/09/IV-TRIM-2026-TABELLA-DIRITTI-CONSOLARI.pdf", "data_listino": "2026-10-01"},
    "it_tab_cl": {"titolo": "Ambasciata d'Italia a Santiago del Cile, Tabella delle principali percezioni consolari, IV trimestre 2026", "formato": "pdf", "paese": "chile",
                  "url": "https://ambsantiago.esteri.it/wp-content/uploads/2026/10/Tabella-Percezioni-IV-Trim-2026.pdf", "data_listino": "2026-10-01"},
    "it_tab_mx": {"titolo": "Ambasciata d'Italia a Città del Messico, Tabella diritti consolari IV trimestre 2026", "formato": "pdf", "paese": "mexico",
                  "url": "https://ambcittadelmessico.esteri.it/wp-content/uploads/2026/10/TABELLA-DIRITTI-CONSOLARI-IV-TRIM-2026.pdf", "data_listino": "2026-10-01"},
    "it_tab_br": {"titolo": "Consolato Generale d'Italia a San Paolo, Principali tariffe consolari in vigore dal 01 ottobre 2026 (firmata il 25/09/2026)", "formato": "immagine", "paese": "brasil",
                  "url": "https://conssanpaolo.esteri.it/wp-content/uploads/2026/10/Tabella-diritti-Consolari-IV-TRIM-2026.pdf", "data_listino": "2026-10-01",
                  "sha256_atteso": "91887e0acd1826aa6d59ee5f536a860c1553a6ff8eae36fd71ad3ba6333a787d"},
}

# ---------------------------------------------------------------- frasi lette a mano il 4/11/2026 (frammento = parole esatte, spazi normalizzati)
LETTURE = {
    # Spagna, tasse dei consolati
    "co_gratis_lista": {"fonte": "es_tasas_co", "frammento": "Visados Nacionales para ciudadanos de: Andorra, Chile, Colombia, Corea del Sur, Costa Rica, Croacia,"},
    "co_gratis": {"fonte": "es_tasas_co", "valore": 0, "valuta": "COP", "frammento": "Gratuito El Salvador, Honduras, Japón, Nicaragua, Panamá, Paraguay, San Marino. (Según acuerdos y convenios firmados)."},
    "co_fecha": {"fonte": "es_tasas_co", "frammento": "A partir de la fecha (05/06/2024)"},
    "co_aut": {"fonte": "es_tasas_co", "valore": 47400, "valuta": "COP", "frammento": "Autorización inicial de residencia temporal $47,400"},
    "co_aviso": {"fonte": "es_tasas_co_aviso", "frammento": "a partir del 1 de octubre de 2026, entrará en vigor una actualización de las tasas aplicables a los servicios consulares"},
    "cl_gratis": {"fonte": "es_tasas_cl", "valore": 0, "valuta": "CLP", "frammento": "Visados Nacionales para ciudadanos de los siguientes países: Andorra, CHILE, Colombia, Corea del Sur, Costa Rica, Croacia, El Salvador, Honduras, Japón, Nicaragua, Panamá, Gratuitos"},
    "cl_fecha": {"fonte": "es_tasas_cl", "frammento": "(A partir del 1º de Enero de 2026)"},
    "cl_aut": {"fonte": "es_tasas_cl", "valore": 11680, "valuta": "CLP", "frammento": "Autorización Inicial de Residencia Temporal $11.680.-"},
    "ar_visado": {"fonte": "es_tasas_ar", "valore": 152000, "valuta": "ARS", "frammento": "Visados Nacional 152.000 pesos"},
    "ar_fecha": {"fonte": "es_tasas_ar", "frammento": "TASAS CONSULARES a partir del 01-01-2026"},
    "ar_reciprocidad": {"fonte": "es_tasas_ar", "frammento": "Si el solicitante de visado es nacional de Australia, Canadá, Estados Unidos, Etiopía, Irlanda o Reino Unido"},
    "ar_bls": {"fonte": "es_tasas_ar", "frammento": "Las solicitudes de visado se presentan en el Centro de Solicitud"},
    "pe_visado": {"fonte": "es_tasas_pe", "valore": 352.10, "valuta": "PEN", "frammento": "Visado Nacional - Tasa general 352,10 soles"},
    "pe_fecha": {"fonte": "es_tasas_pe", "frammento": "Publicado el 12.06.2026"},
    "pe_titulo": {"fonte": "es_tasas_pe", "frammento": "TASAS CONSULARES 2026"},
    "pe_aut": {"fonte": "es_tasas_pe", "valore": 42.80, "valuta": "PEN", "frammento": "Residencia no lucrativa 42,80 soles"},
    "pe_bls": {"fonte": "es_tasas_pe", "valore": 66.10, "valuta": "PEN", "frammento": "La empresa BLS cobra una tarifa básica obligatoria de 66,10 soles"},
    "mx_visado": {"fonte": "es_tasas_mx", "valore": 1902, "valuta": "MXN", "frammento": "La tasa para solicitar todos los visados es de 1,902 MXN"},
    "mx_fecha": {"fonte": "es_tasas_mx", "frammento": "Tasas actualizadas en vigor a partir del 1 de enero de 2026."},
    "mx_nl": {"fonte": "es_tasas_mx", "valore": 231, "valuta": "MXN", "frammento": "residencia no lucrativa: 1,902 MXN + 231 MXN por la autorización inicial de residencia"},
    "mx_visado_pdf": {"fonte": "es_tasas_mx_pdf", "valore": 1902, "valuta": "MXN", "frammento": "14-Visado 1.902,00"},
    "br_visado": {"fonte": "es_tasas_br", "valore": 570, "valuta": "BRL", "frammento": "14-Visado 570,00"},
    "br_fecha": {"fonte": "es_tasas_br", "frammento": "Fecha de impresión: 16/12/2025"},
    "br_aut": {"fonte": "es_tasas_br", "valore": 69, "valuta": "BRL", "frammento": "Aut. Inicial residencia temporal 69,00"},
    "br_visado_bsb": {"fonte": "es_tasas_br_bsb", "valore": 570, "valuta": "BRL", "frammento": "Visados nacionales / Vistos: 570,00 R$"},
    "br_bsb_aut": {"fonte": "es_tasas_br_bsb", "valore": 69, "valuta": "BRL", "frammento": "Tasas de extranjería (MOD 790), residencia temporal / Taxas de Extranjería (MOD 790), residência temporária: 69,00 R$"},
    "br_bsb_orientativo": {"fonte": "es_tasas_br_bsb", "frammento": "La información ofrecida sólo tiene carácter orientativo y no es vinculante"},
    # Spagna, requisiti economici (BOE) e consolato di Buenos Aires
    "nl_400": {"fonte": "es_rd1155", "valore": 4.0, "frammento": "Para su sostenimiento, durante su residencia en España, una cantidad que represente mensualmente en euros el 400 % del IPREM, o su equivalente legal en moneda extranjera."},
    "nl_100": {"fonte": "es_rd1155", "valore": 1.0, "frammento": "Para el sostenimiento de cada uno de los familiares a su cargo, durante su residencia en España, una cantidad que represente mensualmente en euros el 100 % del IPREM"},
    "nl_un_ano": {"fonte": "es_rd1155", "valore": 1, "frammento": "La autorización inicial de residencia temporal no lucrativa tendrá la duración de un año."},
    "nl_ba_2400": {"fonte": "es_ba_nl", "valore": [2400, 28800, 600], "frammento": "Se deberá acreditar que el interesado cuenta con un mínimo de 2.400 euros por mes (12 meses) o un total de 28.800 euros. Por cada familiar a cargo se deberá acreditar un importe adicional de 600 euros por mes (12 meses)."},
    "nl_ba_trabajo": {"fonte": "es_ba_nl", "frammento": "deberá acreditar no ejercer actividades laborales, ni de manera presencial ni remota, ni por cuenta ajena o por cuenta propia"},
    "nl_ba_seguro": {"fonte": "es_ba_nl", "frammento": "Se deberá contratar una cobertura médica durante el primer año de residencia que cubra el 100% de los gastos médicos, sin copagos y sin carencias."},
    "nl_ba_penales": {"fonte": "es_ba_nl", "frammento": "certificado de antecedentes penales expedido por el país o países de residencia en los últimos 5 años"},
    "nl_ba_medico": {"fonte": "es_ba_nl", "frammento": "certificado médico que acredite que el solicitante no padece enfermedades que puedan tener repercusiones graves para la salud pública"},
    "nl_ba_pasaporte": {"fonte": "es_ba_nl", "frammento": "El pasaporte deberá tener una validez mínima de 1 año y dos páginas en blanco."},
    "nl_ba_ex01": {"fonte": "es_ba_nl", "frammento": "Impreso de solicitud de autorización de residencia no lucrativa."},
    "nl_ba_apostilla": {"fonte": "es_ba_nl", "frammento": "Todos los documentos extranjeros deben presentarse legalizados o apostillados"},
    "nl_ba_790": {"fonte": "es_ba_nl", "frammento": "modelo 790 código 052, epígrafe 2.1 ( autorización inicial de residencia temporal )"},
    "nd_200": {"fonte": "es_ba_nd", "valore": 2.0, "frammento": "Teletrabajador: cantidad que represente mensualmente el 200% del salario mínimo interprofesional (SMI)."},
    "nd_familia": {"fonte": "es_ba_nd", "valore": [0.75, 0.25], "frammento": "Familiares del teletrabajador: al menos el 75% del SMI por la primera persona reagrupada y, al menos, un 25% del SMI por cada miembro adicional."},
    "nd_titulo": {"fonte": "es_ba_nd", "frammento": "o bien probar una experiencia profesional mínima de tres años"},
    "nd_empresa": {"fonte": "es_ba_nd", "frammento": "la fecha de constitución de la empresa (no debe ser inferior a un año)"},
    "nd_antiguedad": {"fonte": "es_ba_nd", "frammento": "la antigüedad del trabajador en la empresa (no debe ser inferior a tres meses)"},
    "nd_20": {"fonte": "es_ba_nd", "frammento": "siempre que el porcentaje de dicho trabajo no sea superior al 20 % del total de su actividad"},
    "nd_seguro": {"fonte": "es_ba_nd", "frammento": "El seguro debe cubrir todos los riesgos asegurados por el sistema público de salud en España."},
    "nd_penales": {"fonte": "es_ba_nd", "frammento": "certificado de antecedentes penales expedido por el país o países de residencia en los últimos 2 años"},
    "est_100": {"fonte": "es_rd1155", "valore": 1.0, "frammento": "Para su sostenimiento, una cantidad que represente mensualmente el 100 % del IPREM, salvo que se acredite debidamente tener abonado de antemano el alojamiento por todo el tiempo de duración de la estancia."},
    "est_familia": {"fonte": "es_rd1155", "valore": [0.75, 0.50], "frammento": "una cantidad que represente mensualmente el 75 % del IPREM, para el primer familiar, y el 50 % del IPREM para cada una de las restantes personas"},
    "est_pasaporte": {"fonte": "es_rd1155", "frammento": "pasaporte o título de viaje en vigor, reconocido como válido en España, con una vigencia mínima de un año"},
    "est_ba_admision": {"fonte": "es_ba_es", "frammento": "documentos que acrediten la admisión y el pago de la matrícula"},
    "est_ba_90": {"fonte": "es_ba_es", "frammento": "La estancia por estudios de hasta 90 días no requiere visado de estudios."},
    # Portogallo (MNE)
    "pt_110": {"fonte": "pt_emol", "valore": 110, "valuta": "EUR", "frammento": "As taxas a pagar pelo tratamento administrativo de um pedido de visto nacional é de 110€."},
    "pt_isencao_bolsa": {"fonte": "pt_emol", "frammento": "A cidadãos estrangeiros que beneficiem de bolsas de estudo atribuídas pelo Estado Português"},
    "pt_rmmg": {"fonte": "pt_meios", "valore": 920, "valuta": "EUR", "frammento": "retribuição mínima mensal garantida que, em 2026, é de 920€"},
    "pt_escala": {"fonte": "pt_meios", "valore": [1.0, 0.5, 0.3], "frammento": "Primeiro adulto 100%; Segundo ou mais adultos 50%; Crianças e jovens com idade inferior a 18 anos e filhos maiores a cargo 30%."},
    "pt_estudo_12": {"fonte": "pt_meios", "valore": 12, "frammento": "assegurados por um período de 12 meses ou pelo número de meses de permanência do requerente, quando participe em programa de intercâmbio, podendo os rendimentos ser reduzidos a metade quando comprove ter assegurados, por qualquer forma, o alojamento ou até 90 % quando comprove ter também assegurada a alimentação"},
    "pt_d7_reformado": {"fonte": "pt_meios", "frammento": "No caso de cidadão estrangeiro reformado, através de documento comprovativo do respectivo rendimento, bem como da garantia do seu recebimento ou disponibilidade de outros rendimentos em território nacional"},
    "pt_d7_rendimentos": {"fonte": "pt_meios", "frammento": "No caso de cidadão estrangeiro que viva de rendimentos de bens móveis ou imóveis, da propriedade intelectual ou de aplicações financeiras, através de documento comprovativo da existência e montante de tais rendimentos, bem como da sua disponibilidade em Portugal."},
    "pt_d8_4": {"fonte": "pt_res", "valore": 4, "frammento": "Comprovativo de rendimentos médios mensais auferidos no exercício de atividade profissional subordinada ou independente nos últimos três meses de valor mínimo equivalente a quatro remunerações mínimas mensais garantidas"},
    "pt_d8_fiscal": {"fonte": "pt_res", "frammento": "Documento que ateste a sua residência fiscal."},
    "pt_seguro_pb4": {"fonte": "pt_res", "frammento": "como por exemplo no caso do Brasil (PB4) e Reino Unido (S1)"},
    "pt_seguro": {"fonte": "pt_res", "frammento": "Seguro de viagem válido, que permita cobrir as despesas necessárias por razões médicas, incluindo assistência médica urgente e eventual repatriamento"},
    "pt_registo": {"fonte": "pt_res", "frammento": "Certificado de registo criminal do país de origem ou do país onde o requerente resida há mais de um ano (os menores de 16 anos estão isentos da apresentação dos documentos relativos ao registo criminal), com Apostila de Haia (se aplicável) ou legalizado"},
    "pt_passaporte": {"fonte": "pt_res", "frammento": "Passaporte ou outro documento de viagem válido por mais 3 meses para além da duração da estada prevista"},
    "pt_est_admissao": {"fonte": "pt_res", "frammento": "Comprovativo em como preenche as condições de admissão ou foi aceite em instituição do ensino superior para frequência de um programa de estudos e que possui os recursos suficientes para a respetiva frequência."},
    "pt_est_lusofono": {"fonte": "pt_res", "frammento": "É dispensado da prova de meios de subsistência o requerente de visto de residência, nacional de Estado terceiro de língua oficial portuguesa , quando admitido em instituição de ensino superior."},
    "pt_est_91b": {"fonte": "pt_res", "frammento": "Os estudantes de ensino superior admitidos em instituição de ensino superior oficialmente reconhecido nos termos da legislação em vigor (Artigo 91º-B da LE) estão dispensados de apresentar seguro de saúde ou equivalente, de comprovar condições de admissão ou em como foi aceite em instituição de ensino superior, seguro de viagem ou meios de subsistência."},
    "pt_d7_reformados_doc": {"fonte": "pt_res", "frammento": "Documento comprovativo de montante da reforma."},
    "pt_familia_1563": {"fonte": "pt_res", "frammento": "determinado nos termos do n.º 2 do artigo 2.º da Portaria n.º 1563/2007, de 11 de dezembro"},
    "pt_cplp_regime": {"fonte": "pt_cplp", "frammento": "Regime de pedidos de visto aplicável aos nacionais de um Estado em que esteja em vigor o Acordo sobre a Mobilidade entre os Estados membros da Comunidade dos Países de Língua Portuguesa celebrado em Luanda a 17 de julho de 2021 (Acordo CPLP)"},
    "pt_cplp_dispensa": {"fonte": "pt_cplp", "frammento": "Os cidadãos da CPLP são dispensados da apresentação de meios de subsistência desde que apresentem:"},
    "pt_cplp_termo": {"fonte": "pt_cplp", "frammento": "Termo de responsabilidade com assinatura reconhecida, subscrito por cidadão português ou cidadão estrangeiro habilitado, com documento de residência em Portugal, que garanta a alimentação e alojamento ao requerente do visto"},
    "pt_cplp_irs": {"fonte": "pt_cplp", "frammento": "Declaração de IRS do subscritor (último ano); e Extrato bancário do subscritor (últimos 3 meses)."},
    "pt_cplp_ensino": {"fonte": "pt_cplp", "frammento": "Aos requerentes admitidos em instituição de ensino superior é dispensada a apresentação de meios de subsistência."},
    "pt_proc_suspenso": {"fonte": "pt_proc", "frammento": "PROCURA DE TRABALHO QUALIFICADO AINDA NÃO DISPONÍVEL NOS POSTOS CONSULARES PORTUGUESES A aguardar a necessária regulamentação do artigo 57.º-A da Lei de Estrangeiros."},
    "pt_tipo_suspenso": {"fonte": "pt_tipo", "frammento": "O Visto para Procura de Trabalho Qualificado (SUSPENSO)"},
    "pt_tipo_residencia": {"fonte": "pt_tipo", "frammento": "O visto de residência que permite a obtenção de autorização de residência é válido para duas entradas e por quatro meses"},
    "br_cplp_vigor": {"fonte": "br_cplp", "frammento": "Considerando que o Acordo entrou em vigor para a República Federativa do Brasil, no plano jurídico externo, em 1º de abril de 2022"},
    # Italia, visto per studio (diritti consolari del IV trimestre 2026)
    "it_ar": {"fonte": "it_tab_ar", "valore": 86100, "valuta": "ARS", "frammento": "Visto Nazionale per motivi di studio art. 29 50,00 86.100,00"},
    "it_ar_cambio": {"fonte": "it_tab_ar", "valore": 1720.2176, "frammento": "TASSO DI RAGGUAGLIO IV TRIMESTRE 2026 1 EURO PARI A: 1720,2176 ARS"},
    "it_ar_periodo": {"fonte": "it_tab_ar", "frammento": "IN VIGORE DAL 01/10 /2026 AL 31/12/2026"},
    "it_cl": {"fonte": "it_tab_cl", "valore": 54000, "valuta": "CLP", "frammento": "29d Visto di studio 54.000"},
    "it_cl_periodo": {"fonte": "it_tab_cl", "valore": 1067.96, "frammento": "IV trimestre 2026 dal 1° ottobre al 31 dicembre 2026 (1 Euro = 1.067,96 Pesos Cileni)"},
    "it_mx": {"fonte": "it_tab_mx", "valore": 1000, "valuta": "MXN", "frammento": "VISTO NAZIONALE PER MOTIVI DI STUDIO 50 1,000"},
    "it_mx_cambio": {"fonte": "it_tab_mx", "valore": 19.8501, "frammento": "TASSO DI RAGGUAGLIO: 19.8501"},
    "it_mx_periodo": {"fonte": "it_tab_mx", "frammento": "TABELLA DIRITTI CONSOLARI IV TRIMESTRE 2026"},
    # PDF di sola immagine: letto a vista il 4/11/2026 (riga "Visto nazionale per motivi di studio - tipo D", art. 29, tariffa 50,00 €;
    # contanti o PIX bancario 296,00; PIX con QR o POS 299,64; carta di debito 300,44; tasso di cambio 1 euro = R$ 5,90930000; San Paolo, 25/09/2026)
    "it_br": {"fonte": "it_tab_br", "valore": 296.00, "valuta": "BRL", "visiva": True,
              "frammento": "Visto nazionale per motivi di studio - tipo D | 29 | 50,00 | 296,00 | 299,64 | 300,44"},
    "it_br_cambio": {"fonte": "it_tab_br", "valore": 5.9093, "visiva": True, "frammento": "Tasso di cambio 1 Euro = R$ 5,90930000"},
}

# Paesi della sezione: valuta e fonte del cambio ufficiale (USD per le valute senza cambio BCE)
VALUTE = {"colombia": "COP", "mexico": "MXN", "argentina": "ARS", "chile": "CLP", "peru": "PEN", "brasil": "BRL"}
URL_CAMBI = {
    "ECB": "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml",
    "COP": "https://www.datos.gov.co/resource/32sa-8pi3.json?$order=vigenciadesde%20DESC&$limit=40",
    "ARS": "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD?fechadesde={da}&fechahasta={a}",
    "PEN": "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PD04640PD/json/{da}/{a}",
    "CLP": "https://www.sii.cl/valores_y_fechas/dolar/dolar{anno}.htm",
}
NOMI_CAMBI = {
    "ECB": "Banco Central Europeo, tipos de cambio de referencia del euro",
    "COP": "Superintendencia Financiera de Colombia, Tasa Representativa del Mercado (TRM), en datos.gov.co",
    "ARS": "Banco Central de la República Argentina, cotización del dólar (API de estadísticas cambiarias)",
    "PEN": "Banco Central de Reserva del Perú, tipo de cambio del sistema bancario SBS, venta (serie PD04640PD)",
    "CLP": "Servicio de Impuestos Internos de Chile, dólar observado",
}

QUERY = {
    "es": {"gl": ["co", "mx", "ar", "cl", "pe"],
           "q": ["visa no lucrativa españa para", "visa no lucrativa españa", "visa nomada digital españa para", "visa nomada digital españa",
                 "visa de estudiante españa para", "visa de estudiante españa", "cuanto cuesta la visa de estudiante para españa",
                 "visa d7 portugal para", "visa d7 portugal", "visa d8 portugal", "visa nomada digital portugal",
                 "visa de estudiante portugal para", "visa de estudiante portugal", "visa de estudiante italia para", "visa de estudiante italia"]},
    "pt": {"gl": ["br"],
           "q": ["visto d7 portugal", "visto d8 portugal", "visto nomade digital portugal", "visto de estudante portugal", "visto cplp portugal",
                 "visto de procura de trabalho portugal", "visto nao lucrativo espanha", "visto nomade digital espanha", "visto espanha estudante",
                 "visto de estudante espanha", "visto de estudante italia", "visto estudante italia"]},
}


def norm(t):
    t = re.sub(r"\s+", " ", t.replace(" ", " ").replace("​", " ")).strip()
    return re.sub(r" ([,.;:)])", r"\1", t)


def scarica(u, tentativi=3):
    for _ in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            st = getattr(e, "code", None)
            if st:
                return st, b""
            time.sleep(3)
    return None, b""


def testo_di(b, formato):
    """Testo normalizzato: PDF con pdftotext -layout (righe della tabella su una riga), HTML senza script e stili."""
    if formato == "pdf":
        return norm(subprocess.run(["pdftotext", "-layout", "-", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace"))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    return norm(H.unescape(re.sub(r"<[^>]+>", " ", t)))


def num(s):
    return float(str(s).replace(",", "."))


def cambi():
    """Cambi ufficiali dell'ultimo giorno in cui ci sono tutti (BCE, TRM, BCRA, BCRP, SII): EUR -> valuta."""
    oggi = date.today()
    st, b = scarica(URL_CAMBI["ECB"])
    if st != 200:
        raise SystemExit(f"cambi: BCE HTTP {st}")
    ns = {"e": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
    ecb = {}
    for c in ET.fromstring(b).iter("{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube"):
        if c.get("time"):
            ecb[c.get("time")] = {x.get("currency"): float(x.get("rate")) for x in c}
    da = (oggi - timedelta(days=20)).isoformat()
    # Colombia: TRM con vigenza da/a (si applica a ogni giorno dell'intervallo)
    st, bc = scarica(URL_CAMBI["COP"])
    trm = {}
    for r in json.loads(bc or b"[]"):
        d0, d1 = date.fromisoformat(r["vigenciadesde"][:10]), date.fromisoformat(r["vigenciahasta"][:10])
        while d0 <= d1:
            trm[d0.isoformat()] = float(r["valor"])
            d0 += timedelta(days=1)
    # Argentina
    st, ba = scarica(URL_CAMBI["ARS"].format(da=da, a=oggi.isoformat()))
    bcra = {r["fecha"]: float(r["detalle"][0]["tipoCotizacion"]) for r in json.loads(ba or b"{}").get("results", []) if r.get("detalle")}
    # Perù
    st, bp = scarica(URL_CAMBI["PEN"].format(da=da, a=oggi.isoformat()))
    mesi_en = {m: i + 1 for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
    bcrp = {}
    for p in json.loads(bp or b"{}").get("periods", []):
        g, m, a = p["name"].split(".")
        try:
            bcrp[date(2000 + int(a), mesi_en[m], int(g)).isoformat()] = float(p["values"][0])
        except (ValueError, KeyError):
            pass
    # Cile: tabella annuale del SII (righe = giorni, colonne = mesi)
    sii = {}
    for anno in sorted({oggi.year, (oggi - timedelta(days=20)).year}):
        st, bs = scarica(URL_CAMBI["CLP"].format(anno=anno))
        t = bs.decode("latin-1", "replace")
        tab = t[t.find('id="table_export"'):]
        tab = tab[:tab.find("</table>")]
        for riga in re.findall(r"<tr>(.*?)</tr>", tab, re.S):
            g = re.search(r"<th[^>]*>(\d+)</th>", riga)
            if not g:
                continue
            celle = re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)
            for m, c in enumerate(celle, start=1):
                c = H.unescape(c).replace("\xa0", "").strip()
                if c:
                    try:
                        sii[date(anno, m, int(g.group(1))).isoformat()] = float(c.replace(".", "").replace(",", "."))
                    except ValueError:
                        pass
    comuni = sorted(d for d in ecb if d in trm and d in bcra and d in bcrp and d in sii)
    if not comuni:
        raise SystemExit("cambi: nessun giorno con tutti i cambi ufficiali")
    d = comuni[-1]
    usd = ecb[d]["USD"]
    per_usd = {"COP": trm[d], "ARS": bcra[d], "PEN": bcrp[d], "CLP": sii[d]}
    tassi = {"USD": usd, "MXN": ecb[d]["MXN"], "BRL": ecb[d]["BRL"]}
    for v, x in per_usd.items():
        tassi[v] = round(usd * x, 4)
    return {"data": d, "eur_usd": usd, "per_usd": per_usd, "bce": {v: ecb[d][v] for v in ("USD", "MXN", "BRL")}, "tassi": tassi,
            "fonti": {k: {"nome": NOMI_CAMBI[k], "url": URL_CAMBI[k].split("?")[0].replace("{anno}", d[:4]).replace("/json/{da}/{a}", "")} for k in NOMI_CAMBI},
            "nota": "EUR -> COP/ARS/PEN/CLP = (dollari per euro della BCE) × (valuta per dollaro della fonte ufficiale del Paese), stesso giorno."}


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
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<co|mx|ar|cl|pe|br>&hl=<es|pt>&q=…",
            "query": out}


def main():
    oggi = date.today().isoformat()
    errori, testi, fonti = [], {}, {}
    for k, F in FONTI.items():
        st, b = scarica(F["url"])
        if st != 200 or not b:
            errori.append(f"{k}: HTTP {st} ({F['url']})")
            continue
        sha = hashlib.sha256(b).hexdigest()
        if F["formato"] == "immagine":
            if sha != F["sha256_atteso"]:
                errori.append(f"{k}: il PDF (immagine) è cambiato (SHA-256 {sha}): rileggerlo a vista e aggiornare LETTURE e sha256_atteso")
            testi[k] = ""
        else:
            testi[k] = testo_di(b, F["formato"])
        fonti[k] = {**F, "http": 200, "letto_il": oggi, "byte": len(b), "sha256": sha}
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    for k, L in LETTURE.items():
        if L.get("visiva"):
            continue
        if norm(L["frammento"]) not in testi[L["fonte"]]:
            errori.append(f"frammento non trovato ({k}, {L['fonte']}): {L['frammento']!r}")
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not domanda:
        sys.exit("ERRORE: nessuna domanda salvata: lanciare con --domanda")
    dati = {
        "_nota": "Generato da raccolta/visados.py: non modificare a mano.",
        "letto_il": oggi,
        "fonti": fonti,
        "letture": LETTURE,
        "valute": VALUTE,
        "cambi": cambi(),
        "domanda": domanda,
    }
    cont = {k: dati[k] for k in ("fonti", "letture", "valute", "cambi")}
    dati["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(LETTURE)} frasi, cambi del {dati['cambi']['data']}, "
          f"domanda del {domanda['data']} ({len(domanda['query'])} ricerche).")


if __name__ == "__main__":
    main()
