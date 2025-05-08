# -*- coding: utf-8 -*-
"""
Extracción de palabras clave con modelo LLM (Mixtral) desde un catálogo estandarizado.
Usa prompting para identificar personas, lugares, instituciones, eventos y tipos documentales.
"""

import pandas as pd
from tqdm import tqdm
import os
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
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    huggingfacehub_api_token=HF_API_TOKEN,
    temperature=0.3,
    max_new_tokens=100
)

def extract_keywords_with_llm(texto_fuente):
    if not isinstance(texto_fuente, str) or not texto_fuente.strip():
        return []

    prompt = f"""Extrae solo las palabras clave del siguiente texto archivístico. 
Incluye nombres de personas, lugares, instituciones, eventos históricos y tipos documentales. 
NO incluyas frases completas ni repitas el texto original. 
Devuelve el resultado como una lista de Python con comillas y comas, por ejemplo:

Texto: Lima Diploma de miembro de la Legión del Mérito Militar, expedido por el gobierno de Nicolás de Piérola en favor de José Mariano Alvizuri por su participación en el combate de Pacochas, el 29 de mayo de 1877.
Palabras clave: ["Lima", "Legión del Mérito Militar", "Nicolás de Piérola", "José Mariano Alvizuri", "combate de Pacochas", "1877", "Diploma"]

Texto: {texto_fuente}
Palabras clave:"""


    try:
        response = llm.invoke(prompt).strip()
        keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
        return keywords
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

    print("🧠 Extrayendo keywords con Mixtral...")
    tqdm.pandas(desc="⏳ Extrayendo con LLM")
    df["keywords_extraidas"] = df["texto_fuente"].progress_apply(extract_keywords_with_llm)

    print(f"💾 Guardando resultados en: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("✅ Proceso completado con éxito.")
    print(f"🟢 Documentos con al menos una keyword: {(df['keywords_extraidas'].str.len() > 0).sum()} de {len(df)}")

if __name__ == "__main__":
    main()
