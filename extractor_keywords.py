# -*- coding: utf-8 -*-
"""
Extracción de palabras clave con KeyBERT desde un catálogo estandarizado.
Filtrado semántico usando spaCy: stopwords + validación POS (sustantivos, nombres propios).
"""

import pandas as pd
from keybert import KeyBERT
from tqdm import tqdm
import spacy

# Configuración
INPUT_FILE = "catalogo_completo_estandarizado.csv"
OUTPUT_FILE = "catalogo_con_keywords.csv"
TOP_N = 5
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Cargar modelo de spaCy para español
try:
    nlp = spacy.load("es_core_news_sm")
except:
    import os
    os.system("python -m spacy download es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

stopwords = nlp.Defaults.stop_words

def is_semantically_valid(phrase):
    """Usa spaCy para verificar que haya al menos un sustantivo o nombre propio."""
    doc = nlp(phrase)
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"}:
            return True
    return False

def extract_keywords_from_text(model, text, top_n=TOP_N):
    if not isinstance(text, str) or not text.strip():
        return []
    try:
        keywords = model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words=None,
            top_n=top_n,
            use_mmr=True,
            diversity=0.5
        )
        final_keywords = []
        for phrase, score in keywords:
            words = phrase.lower().split()
            if all(w in stopwords for w in words):
                continue
            if len(phrase.strip()) <= 2:
                continue
            if phrase.lower().startswith(tuple(stopwords)):
                continue
            if not is_semantically_valid(phrase):
                continue
            final_keywords.append(phrase)
        return final_keywords
    except Exception as e:
        print(f"⚠️ Error extrayendo keywords: {e}")
        return []

def main():
    print("🔍 Cargando catálogo...")
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    
    print("📉 Seleccionando muestra aleatoria de 100 documentos...")
    df = df.sample(n=100, random_state=42).copy()

    print("🔠 Inicializando modelo KeyBERT...")
    kw_model = KeyBERT(model=MODEL_NAME)

    print("🧩 Combinando campos 'descripcion' y 'observaciones'...")
    df["texto_fuente"] = df[["descripcion", "observaciones"]].fillna("").agg(" ".join, axis=1)

    print("🚀 Extrayendo palabras clave...")
    tqdm.pandas(desc="⏳ Extrayendo keywords mejoradas")
    df["keywords_extraidas"] = df["texto_fuente"].progress_apply(lambda x: extract_keywords_from_text(kw_model, x))

    print(f"💾 Guardando resultados en: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("✅ Proceso completado con éxito.")
    print(f"🟢 Documentos con al menos una keyword: {(df['keywords_extraidas'].str.len() > 0).sum()} de {len(df)}")

if __name__ == "__main__":
    main()
