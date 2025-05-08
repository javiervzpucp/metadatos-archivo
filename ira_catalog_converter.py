# -*- coding: utf-8 -*-
"""
Conversor de catálogos históricos a formato estandarizado con normalización de fechas.
Extrae fecha_inicio y fecha_fin con regla o LLM, y convierte a ISO 8601.
"""

import pandas as pd
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import warnings

from langchain_community.llms import HuggingFaceEndpoint

warnings.simplefilter("ignore", category=FutureWarning)
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IRACatalogConverter:
    def __init__(self, data_folder="datos"):
        self.data_folder = data_folder
        self.column_map = {
            'signatura': 'signatura',
            'fecha crónica': 'fecha_cronica',
            'fecha tópica': 'fecha_topica',
            'descripción': 'descripcion',
            'palabras claves': 'palabras_clave',
            'folios': 'folios',
            'observaciones': 'observaciones'
        }

        # LLM para normalización de fechas complejas
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            huggingfacehub_api_token=os.getenv("HF_API_TOKEN"),
            temperature=0.3,
            max_new_tokens=100
        )

    def _rename_columns(self, df):
        return df.rename(columns=lambda c: self.column_map.get(c.strip().lower(), c.strip().lower().replace(" ", "_")))

    def _clean_text(self, text):
        if isinstance(text, str):
            return re.sub(r'\s+', ' ', text.strip().replace("..", "."))
        return text

    def _clean_fecha_topica(self, text):
        if isinstance(text, str):
            return text.strip().rstrip('.')
        return text

    def _to_iso(self, texto):
        """Convierte fechas como '1836-Mar.-14' a '1836-03-14'"""
        try:
            meses = {
                'ene.': '01', 'feb.': '02', 'mar.': '03', 'abr.': '04', 'may.': '05',
                'jun.': '06', 'jul.': '07', 'ago.': '08', 'sep.': '09', 'oct.': '10',
                'nov.': '11', 'dic.': '12'
            }
            for abbr, num in meses.items():
                texto = texto.lower().replace(abbr, num)
            texto = texto.replace('.', '').replace(' ', '')
            if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', texto):
                parts = texto.split('-')
                return '-'.join([parts[0]] + [p.zfill(2) for p in parts[1:]])
            return None
        except:
            return None

    def _extract_fecha_rango(self, texto_fecha):
        """Extrae fecha_inicio y fecha_fin. Usa regla con '/' o fallback con LLM."""
        if not isinstance(texto_fecha, str) or not texto_fecha.strip():
            return None, None

        texto_fecha = texto_fecha.strip()

        # Regla: separador explícito
        if '/' in texto_fecha:
            partes = texto_fecha.split('/')
            if len(partes) == 2:
                return partes[0].strip(), partes[1].strip()

        # Si solo hay una fecha legible, repítela como inicio
        if re.search(r"\d{4}", texto_fecha):
            return texto_fecha, None

        # Fallback con LLM
        prompt = f"""Extrae la fecha de inicio y la fecha de fin de este texto en español. 
Devuelve solo dos fechas en formato ISO 8601, separadas por coma.

Ejemplo:
Entrada: '1836-Mar.-14/1852-Ago.-20'
Salida: 1836-03-14,1852-08-20

Entrada: {texto_fecha}
Salida:"""
        try:
            response = self.llm.invoke(prompt).strip()
            fechas = [f.strip() for f in response.split(',') if re.match(r"\d{4}-\d{2}-\d{2}", f.strip())]
            return (fechas + [None, None])[:2]
        except Exception as e:
            logger.warning(f"⚠️ LLM no pudo interpretar fecha: '{texto_fecha}' → {str(e)}")
            return None, None

    def process_excel(self, filepath):
        try:
            logger.info(f"📄 Procesando archivo: {filepath}")
            df = pd.read_excel(filepath, sheet_name=0, dtype=str)
            df = self._rename_columns(df)

            logger.info(f"🔧 Limpiando texto en columnas clave...")
            for col in ['descripcion', 'observaciones', 'palabras_clave', 'fecha_cronica', 'fecha_topica', 'folios']:
                if col in df.columns:
                    df[col] = df[col].apply(self._clean_text)

            if 'fecha_topica' in df.columns:
                df['fecha_topica'] = df['fecha_topica'].apply(self._clean_fecha_topica)

            if 'fecha_cronica' in df.columns:
                logger.info("📆 Extrayendo fechas de inicio y fin...")
                tqdm.pandas(desc="⏳ Extrayendo fechas crónicas")
                fechas = df['fecha_cronica'].progress_apply(lambda x: pd.Series(self._extract_fecha_rango(x)))
                fechas.columns = ['fecha_inicio', 'fecha_fin']
                df = pd.concat([df, fechas], axis=1)

                logger.info("📆 Normalizando a formato ISO 8601...")
                df['fecha_inicio_iso'] = df['fecha_inicio'].apply(self._to_iso)
                df['fecha_fin_iso'] = df['fecha_fin'].apply(self._to_iso)

            df['__fuente__'] = os.path.basename(filepath)
            logger.info(f"✅ Procesamiento completo: {filepath} ({len(df)} filas)")
            return df

        except Exception as e:
            logger.error(f"❌ Error procesando {filepath}: {e}")
            return pd.DataFrame()

    def combine_excels(self):
        dataframes = []
        files = [f for f in os.listdir(self.data_folder) if f.endswith('.xlsx') or f.endswith('.xls')]

        for file in files:
            full_path = os.path.join(self.data_folder, file)
            df = self.process_excel(full_path)
            if not df.empty:
                dataframes.append(df)

        if not dataframes:
            logger.warning("⚠️ No se procesaron archivos con datos válidos.")
            return pd.DataFrame()

        logger.info("📦 Combinando catálogos con columnas comunes...")
        common_cols = list(set.intersection(*(set(df.columns) for df in dataframes)))
        return pd.concat([df[common_cols] for df in dataframes], ignore_index=True)
