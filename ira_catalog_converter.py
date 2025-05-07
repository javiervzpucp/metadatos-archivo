# -*- coding: utf-8 -*-
"""
Conversor de catálogos históricos a formato estandarizado con registro de avance.
Asume archivos Excel en carpeta 'datos/' y usa la primera hoja.
"""

import pandas as pd
import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import warnings

warnings.simplefilter("ignore", category=FutureWarning)
load_dotenv()

# Configuración del logger
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

    def _extract_fecha_rango(self, texto_fecha):
        """Extrae fecha de inicio y fin si es un rango (ej. '1836-Mar.-14/1852-Ago.-20')"""
        if not isinstance(texto_fecha, str) or '/' not in texto_fecha:
            return None, None
        partes = texto_fecha.split('/')
        if len(partes) != 2:
            return None, None
        return partes[0].strip(), partes[1].strip()

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
                tqdm.pandas(desc="⏳ Extrayendo rangos de fechas")
                df[['fecha_inicio', 'fecha_fin']] = df['fecha_cronica'].progress_apply(
                    lambda x: pd.Series(self._extract_fecha_rango(x))
                )

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

