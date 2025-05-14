# -*- coding: utf-8 -*-
"""
Pipeline completo para metadatos históricos:
- Extracción de palabras clave con LLM
- Clasificación semántica
- Matching con SKOS y generación de URIs
"""

import pandas as pd
import os
import re
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceEndpoint
from rapidfuzz import process, fuzz
from rdflib import Graph
from rdflib.namespace import SKOS

# Configuración
INPUT_FILE = "catalogo_completo_estandarizado.csv"
THESAURUS_FILE = "unesco-thesaurus.ttl"
OUTPUT_FILE = "catalogo_con_keywords_y_uris.csv"
BASE_URI_INTERNO = "http://ira.pucp.edu.pe/entidades/"

# Cargar API key
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Inicializar modelo LLM
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    huggingfacehub_api_token=HF_API_TOKEN,
    temperature=0.3,
    max_new_tokens=100
)

def is_valid_keyword(kw):
    kw = kw.strip()
    if len(kw) < 3:
        return False
    if kw.isdigit():
        year = int(kw)
        if year < 1400 or year > 2100:
            return False
    if re.match(r"[A-Z]?\d{2,}[-–]\w+", kw, re.IGNORECASE):
        return False
    return True

def clean_keywords_list(keywords):
    stop_terms = {"documento", "carta", "expediente", "escritura", "testimonio", "papel", "folio"}
    cleaned = []
    for kw in keywords:
        kw = kw.strip(" .,:;\"'()[]").strip()
        kw = kw.replace("  ", " ")
        if len(kw) > 0 and not kw.isupper():
            kw = kw.title()
        if kw.lower() not in stop_terms and len(kw) > 2:
            cleaned.append(kw)
    return cleaned

def extract_keywords_with_llm(texto_fuente):
    if not isinstance(texto_fuente, str) or not texto_fuente.strip():
        return []
    prompt = f"""Extrae únicamente las palabras clave del siguiente texto archivístico.
Incluye solo nombres de personas, lugares, instituciones o eventos históricos. 
No incluyas términos genéricos como 'documento', 'carta', 'escritura', ni frases completas.
Devuelve una lista separada por comas, sin explicaciones, y ordenada por relevancia (lo más importante primero). Solo muestra un máximo de 3 palabras clave.

Texto: {texto_fuente}
Palabras clave:"""
    try:
        response = llm.invoke(prompt).strip()
        raw_keywords = [kw.strip() for kw in response.split(",") if is_valid_keyword(kw.strip())]
        return clean_keywords_list(raw_keywords[:3])
    except Exception as e:
        print(f"⚠️ Error al usar LLM para texto: {e}")
        return []

def clasificar_keyword_llm(keyword):
    prompt = f"""Clasifica la siguiente palabra clave archivística según su tipo.
Posibles categorías: persona, lugar, institución, evento, otro.
Responde solo con una palabra: persona, lugar, institución, evento u otro.

Ejemplos:
- Nicolás de Piérola → persona
- Cusco → lugar
- Gobierno del Perú → institución
- Rebelión de Túpac Amaru → evento

Palabra clave: {keyword}
Tipo:"""
    try:
        tipo = llm.invoke(prompt).strip().lower()
        if tipo in {"persona", "lugar", "institución", "evento"}:
            return tipo
        else:
            return "otro"
    except Exception as e:
        print(f"⚠️ Error clasificando '{keyword}': {e}")
        return "otro"

def normalize_keyword(kw):
    return re.sub(r'\s+', ' ', kw.strip().lower())

def match_keyword_to_uri(keyword, tipo, thesaurus_dict, threshold=90):
    key_norm = normalize_keyword(keyword)
    if tipo in {"lugar", "evento", "concepto"}:
        if key_norm in thesaurus_dict:
            return thesaurus_dict[key_norm]
        match, score, _ = process.extractOne(key_norm, thesaurus_dict.keys(), scorer=fuzz.token_sort_ratio)
        if score >= threshold:
            return thesaurus_dict[match]
        return None
    elif tipo in {"persona", "institución"}:
        return BASE_URI_INTERNO + re.sub(r"[^a-z0-9]+", "_", key_norm).strip("_")
    return None

def main():
    print("🔍 Cargando catálogo...")
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    print("📉 Seleccionando muestra aleatoria de 100 documentos...")
    df = df.sample(n=100, random_state=42).copy()

    print("🧩 Combinando campos para análisis...")
    df["texto_fuente"] = df[["fecha_topica", "descripcion", "observaciones"]].fillna("").agg(" ".join, axis=1)

    print("🧠 Extrayendo keywords...")
    tqdm.pandas(desc="⏳ Extracción de keywords")
    df["keywords_extraidas"] = df["texto_fuente"].progress_apply(extract_keywords_with_llm)

    print("🏷️ Clasificando keywords únicas...")
    unicos = df["keywords_extraidas"].explode().dropna().unique().tolist()
    tipos = {kw: clasificar_keyword_llm(kw) for kw in tqdm(unicos, desc="📚 Clasificando")}

    df["tipo_keywords"] = df["keywords_extraidas"].apply(lambda kws: [tipos.get(kw, "otro") for kw in kws])

    print("📚 Cargando tesauro SKOS...")
    g = Graph()
    g.parse(THESAURUS_FILE, format="ttl")

    thesaurus_dict = {}
    for s, p, o in g.triples((None, SKOS.prefLabel, None)):
        if o.language == "es":
            thesaurus_dict[o.lower()] = str(s)
    for s, p, o in g.triples((None, SKOS.altLabel, None)):
        if o.language == "es":
            thesaurus_dict[o.lower()] = str(s)

    print("🔗 Aplicando matching con SKOS...")
    df["uri_keywords"] = df.apply(
        lambda row: [
            match_keyword_to_uri(kw, tipo, thesaurus_dict)
            for kw, tipo in zip(row["keywords_extraidas"], row["tipo_keywords"])
        ],
        axis=1
    )

    print(f"💾 Guardando en {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("✅ Proceso finalizado con éxito.")
    print(f"🔍 Documentos con al menos una URI: {(df['uri_keywords'].str.len() > 0).sum()} de {len(df)}")

if __name__ == "__main__":
    main()
