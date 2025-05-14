# -*- coding: utf-8 -*-
"""
Created on Mon May 12 18:33:08 2025

@author: jveraz
"""

# -*- coding: utf-8 -*-
"""
FASE 4: Construcción del grafo RDF a partir del catálogo anotado con keywords y URIs.
Cada documento se representa como un nodo :Documento, vinculado a sus entidades.
"""

import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, SKOS, OWL

# Configuración
INPUT_FILE = "catalogo_con_keywords_y_uris.csv"
OUTPUT_TTL = "catalogo_grafo.ttl"
BASE = "http://ira.pucp.edu.pe/"
CATALOGO = Namespace(BASE + "catalogo/")
ENTIDAD = Namespace(BASE + "entidad/")
VOCAB = Namespace(BASE + "vocab/")

# Cargar CSV
df = pd.read_csv(INPUT_FILE)

# Inicializar grafo
g = Graph()
g.bind("skos", SKOS)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("ira", CATALOGO)
g.bind("ent", ENTIDAD)
g.bind("voc", VOCAB)

def format_id(text):
    """Genera una URI válida para una entidad a partir de un string."""
    return URIRef(ENTIDAD + text.strip().lower()
                  .replace(" ", "_")
                  .replace(",", "")
                  .replace(".", "")
                  .replace("'", "")
                  .replace("’", "")
                  .replace("–", "-"))

for idx, row in df.iterrows():
    doc_id = f"doc_{idx+1:03}"
    doc_uri = URIRef(CATALOGO + doc_id)

    # Nodo Documento
    g.add((doc_uri, RDF.type, VOCAB.Documento))
    g.add((doc_uri, VOCAB.signatura, Literal(row.get("signatura", f"SIN_SIGNATURA_{idx}"))))

    # Parsear columnas que contienen listas
    try:
        keywords = eval(row["keywords_extraidas"])
        tipos = eval(row["tipo_keywords"])
        uris = eval(row["uri_keywords"])
    except:
        continue  # saltar fila malformada

    for kw, tipo, uri in zip(keywords, tipos, uris):
        if not kw:
            continue
        entidad_uri = format_id(kw)

        # Nodo Entidad
        g.add((entidad_uri, RDF.type, VOCAB[tipo.capitalize() if tipo else "Entidad"]))
        g.add((entidad_uri, SKOS.prefLabel, Literal(kw, lang="es")))
        if uri and isinstance(uri, str) and uri.startswith("http"):
            g.add((entidad_uri, OWL.sameAs, URIRef(uri)))

        # Relación Documento → Entidad
        g.add((doc_uri, VOCAB.tienePalabraClave, entidad_uri))

# Guardar como Turtle
g.serialize(destination=OUTPUT_TTL, format="turtle")
print(f"✅ Grafo guardado en {OUTPUT_TTL} con {len(g)} triples.")
