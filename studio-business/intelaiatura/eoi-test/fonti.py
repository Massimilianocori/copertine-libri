"""Fonti ufficiali per le 17 comunità autonome (test EOI, 31/10/2026).

Ogni voce: chiave file, comunità, URL, formato, ruolo.
ruolo = "esami" (calendario delle prove scritte), "tappe" (iscrizioni, liste, risultati),
        "controllo" (documento letto per capire chi fissa le date, senza date d'esame).
"""

FONTI = [
    # Madrid
    ("mad_bocm_2026.pdf", "Madrid", "https://bocm.es/boletin/CM_Orden_BOCM/2026/03/25/BOCM-20260325-12.PDF", "PDF BOCM", "esami+tappe"),
    # País Vasco
    ("pv_cal_2027.pdf", "País Vasco", "https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/Calendario-Examenes-Anexo-II2026_2027-definitivo-1.pdf", "PDF Departamento", "esami"),
    ("pv_cal_2026.pdf", "País Vasco", "https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/2025-2026/4c-Calendario-examenes-2025_2026.pdf", "PDF Departamento", "esami"),
    ("pv_res_2027.pdf", "País Vasco", "https://www.euskadi.eus/contenidos/informacion/eoi_matricula_libre/es_def/adjuntos/RESOLUCIoN-MATRICULA-LIBRE-EE.OO.II_-2026-2027.pdf", "PDF Departamento", "tappe"),
    # Cataluña
    ("cat_calendari_2027.html", "Cataluña", "https://educacio.gencat.cat/ca/serveis-tramits/proves/proves-lliures-obtencio-titols/convocat-ordinaria-idiomes/calendari/", "HTML Departament", "esami+tappe"),
    # Andalucía
    ("and_boja46_2026.pdf", "Andalucía", "https://www.juntadeandalucia.es/boja/2026/46/BOJA26-046-00026-3164-01_00334384.pdf", "PDF BOJA", "esami+tappe"),
    # Comunitat Valenciana
    ("val_dogv_2026.pdf", "Comunitat Valenciana", "https://dogv.gva.es/datos/2026/02/05/pdf/2026_3622_es.pdf", "PDF DOGV", "esami+tappe"),
    # Canarias
    ("can_apendice2_2026.pdf", "Canarias", "https://www.gobiernodecanarias.org/cmsgob1/export/sites/educacion/web/_galerias/descargas/otros/apendice-2-pruebas-certificacion-aspirantes-libres-escolarizados-25-26.pdf", "PDF BOC (apéndice)", "esami"),
    ("can_apendice1_2026.pdf", "Canarias", "https://www.gobiernodecanarias.org/cmsgob1/export/sites/educacion/web/_galerias/descargas/otros/apendice-1-preubas-certificacion-aspirantes-libres-escolarizados-25-26.pdf", "PDF BOC (apéndice)", "tappe"),
    ("can_pagina_2026.html", "Canarias", "https://www.gobiernodecanarias.org/educacion/web/idiomas/pruebas/pruebas_certificacion/pruebas_certificacion_idiomas_eoi/", "HTML Consejería", "tappe"),
    # Región de Murcia
    ("mur_borm181_2026.pdf", "Región de Murcia", "https://www.borm.es/services/anuncio/ano/2026/numero/181/pdf?id=840845", "PDF BORM", "esami+tappe"),
    # Illes Balears
    ("bal_boib17_2026.pdf", "Illes Balears", "https://www.caib.es/eboibfront/pdf/ca/2026/17/1211874", "PDF BOIB", "esami"),
    ("bal_boib14_2026.pdf", "Illes Balears", "https://www.caib.es/eboibfront/pdf/ca/2026/14/1211310", "PDF BOIB", "tappe"),
    # Aragón
    ("ara_anexo2_2026.pdf", "Aragón", "https://aplicaciones.aragon.es/seda_core/rest/getModelByKey?childServiceId=1189&key=Calendariodepruebasdecertificacinconvocat", "PDF Departamento (anexo BOA)", "esami"),
    ("ara_anexo3_2026.pdf", "Aragón", "https://aplicaciones.aragon.es/seda_core/rest/getModelByKey?childServiceId=1189&key=Calendariopruebasdecertificacinconvocatori", "PDF Departamento (anexo BOA)", "esami"),
    ("ara_anexo5_2026.pdf", "Aragón", "https://aplicaciones.aragon.es/seda_core/rest/getModelByKey?childServiceId=1189&key=Calendariodelprocesodepruebaslibres", "PDF Departamento (anexo BOA)", "tappe"),
    # Castilla y León
    ("cyl_bocyl_2026.pdf", "Castilla y León", "https://bocyl.jcyl.es/boletines/2026/02/24/pdf/BOCYL-D-24022026-37-28.pdf", "PDF BOCYL", "esami"),
    # Castilla-La Mancha
    ("clm_docm_2026.pdf", "Castilla-La Mancha", "https://docm.jccm.es/docm/descargarArchivo.do?ruta=2026%2F02%2F11%2Fpdf%2F2026_727.pdf&tipo=rutaDocm", "PDF DOCM", "esami"),
    # Navarra
    ("nav_anexo2_2027.pdf", "Navarra", "https://www.educacion.navarra.es/documents/27590/0/ANEXO+2%C2%BA+calendario+ex+escritos+26-27.pdf/3755a7a2-075b-3b76-97d7-917214618cb2", "PDF Departamento", "esami"),
    # Principado de Asturias
    ("ast_bopa_2026.pdf", "Principado de Asturias", "https://www.asturias.es/bopa/2026/02/11/2026-00845.pdf", "PDF BOPA", "esami+tappe"),
    # Extremadura (nessun calendario unico: la Junta rinvia a ogni EOI)
    ("ext_doe21_2026.pdf", "Extremadura", "https://doe.juntaex.es/pdfs/doe/2026/210o/26060238.pdf", "PDF DOE", "controllo"),
    ("ext_tramite.html", "Extremadura", "https://www.juntaex.es/w/0648923", "HTML Junta", "controllo"),
    # Galicia (Instrución 1/2026, anexos IV e V: sito Xunta non raggiungibile dal server)
    ("gal_coruna_ord_2026.pdf", "Galicia", "https://centros.edu.xunta.gal/eoicoruna/sites/centros.edu.xunta.gal.eoicoruna/files/2026-02/CALENDARIO%20PROBAS%20WEB%20ORDINARIA_25-26%20SIN%20AULAS.pdf", "PDF (copia di una EOI)", "esami"),
    ("gal_portal.html", "Galicia", "https://www.edu.xunta.gal/portal/eoi", "HTML Consellería", "controllo"),
    # Cantabria (BOC 26/2/2026, CVE-2026-1414)
    ("cant_boc_2026.html", "Cantabria", "https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=431682", "HTML BOC", "esami"),
    ("cant_guia.html", "Cantabria", "https://www.educantabria.es/en/guia-informativa", "HTML Consejería", "controllo"),
    # La Rioja (guide 2025-26 con calendario; sito non raggiungibile dal server)
    ("rio_guia_b2_2026.pdf", "La Rioja", "https://larioja.org/edu-orden-academica/es/ensenanzas-regimen-especial/escuelas-oficiales-idiomas.ficheros/1696030-GU_A_B2_2025_26.pdf", "PDF Consejería", "esami"),
]

# Popolazione al 1/1/2025, INE, Cifras de Población (tabella 56940, dato definitivo),
# letta dall'API JSON dell'INE il 31/10/2026.
POPOLAZIONE = {
    "Andalucía": 8676713, "Aragón": 1364621, "Principado de Asturias": 1015128,
    "Illes Balears": 1249844, "Canarias": 2258866, "Cantabria": 593623,
    "Castilla y León": 2401221, "Castilla-La Mancha": 2126378, "Cataluña": 8124126,
    "Comunitat Valenciana": 5425182, "Extremadura": 1053345, "Galicia": 2714741,
    "Madrid": 7113886, "Región de Murcia": 1586989, "Navarra": 683854,
    "País Vasco": 2242343, "La Rioja": 326803,
}
SPAGNA_TOTALE = 49128297  # con Ceuta (83.567) e Melilla (87.067)
