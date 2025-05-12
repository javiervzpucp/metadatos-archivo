# -*- coding: utf-8 -*-
"""
Extracción de palabras clave con modelo LLM (Mistral) desde un catálogo estandarizado.
Filtra códigos, números irrelevantes y selecciona solo entidades históricas útiles.
"""

import pandas as pd
from tqdm import tqdm
import os
import re
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceEndpoint

# Configuración
INPUT_FILE = "catalogo_completo_estandarizado.csv"
OUTPUT_FILE = "catalogo_con_keywords.csv"

# Cargar variables de entorno (API Key)
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
    """Filtra códigos, números irrelevantes, y términos triviales."""
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
        keywords = [kw.strip() for kw in response.split(",") if is_valid_keyword(kw.strip())]
        return keywords[:3]
    except Exception as e:
        print(f"⚠️ Error al usar LLM para texto: {e}")
        return []

def main():
    print("🔍 Cargando catálogo...")
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    print("📉 Seleccionando muestra aleatoria de 100 documentos...")
    df = df.sample(n=100, random_state=42).copy()

    print("🧩 Combinando campos 'fecha_topica', 'descripcion' y 'observaciones'...")
    df["texto_fuente"] = df[["fecha_topica", "descripcion", "observaciones"]].fillna("").agg(" ".join, axis=1)

    print("🧠 Extrayendo keywords con LLM...")
    tqdm.pandas(desc="⏳ Extrayendo con LLM y filtrando")
    df["keywords_extraidas"] = df["texto_fuente"].progress_apply(extract_keywords_with_llm)

    print(f"💾 Guardando resultados en: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("✅ Proceso completado con éxito.")
    print(f"🟢 Documentos con al menos una keyword: {(df['keywords_extraidas'].str.len() > 0).sum()} de {len(df)}")

if __name__ == "__main__":
    main()
