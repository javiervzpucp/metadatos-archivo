# -*- coding: utf-8 -*-
"""
Conversor de catálogos históricos a formato estandarizado con ayuda de IA (Mixtral)
Inspirado en el conversor ISAD(G) de jveraz
"""

import pandas as pd
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
import warnings

warnings.simplefilter("ignore", category=FutureWarning)

# Configurar entorno y logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IRACatalogConverter:
    def __init__(self):
        self.column_map = {
            'signatura': 'signatura',
            'fecha crónica': 'fecha_cronica',
            'fecha tópica': 'fecha_topica',
            'descripción': 'descripcion',
            'palabras claves': 'palabras_clave',
            'folios': 'folios',
            'observaciones': 'observaciones'
        }

        # LLM Hugging Face (Mixtral)
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            huggingfacehub_api_token=os.getenv("HF_API_TOKEN"),
            temperature=0.3,
            max_new_tokens=80
        )

    def _rename_columns(self, df):
        return df.rename(columns=lambda c: self.column_map.get(c.strip().lower(), c.strip().lower().replace(" ", "_")))

    def _clean_text(self, text):
        if isinstance(text, str):
            return re.sub(r'\s+', ' ', text.strip())
        return text

    def _normalize_date_llm(self, raw_date):
        prompt = f"""Convierte esta fecha histórica al formato ISO 8601. Si no es posible, responde 'fecha inválida'.
Fecha original: {raw_date}
ISO:"""
        try:
            result = self.llm.invoke(prompt).strip()
            if re.match(r"\d{4}-\d{2}-\d{2}", result):
                return result
        except Exception as e:
            logger.warning(f"LLM error: {e}")
        return "fecha inválida"

    def _normalize_date(self, date_str):
        try:
            date_str = date_str.lower().replace('.-', '-').replace('s/f.', 'fecha desconocida')
            if re.match(r'^\d{4}$', date_str):
                return f"{date_str}-01-01"
            return datetime.strptime(date_str, "%Y-%b-%d").strftime("%Y-%m-%d")
        except:
            return self._normalize_date_llm(date_str)

    def process_excel(self, filepath, sheet_name=None):
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)
            df = self._rename_columns(df)

            for col in ['descripcion', 'observaciones', 'palabras_clave', 'fecha_cronica', 'fecha_topica', 'folios']:
                if col in df.columns:
                    df[col] = df[col].apply(self._clean_text)

            if 'fecha_cronica' in df.columns:
                df['fecha_cronica_iso'] = df['fecha_cronica'].apply(self._normalize_date)

            df['__fuente__'] = os.path.basename(filepath)
            return df

        except Exception as e:
            logger.error(f"Error procesando {filepath}: {e}")
            return pd.DataFrame()

    def combine_excels(self, file_sheet_list):
        dataframes = []
        for file_path, sheet in file_sheet_list:
            df = self.process_excel(file_path, sheet)
            if not df.empty:
                dataframes.append(df)

        common_cols = list(set.intersection(*(set(df.columns) for df in dataframes)))
        return pd.concat([df[common_cols] for df in dataframes], ignore_index=True)
