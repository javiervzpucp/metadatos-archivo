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
            return re.sub(r'\s+', ' ', text.strip())
        return text

    def _normalize_date(self, date_str):
        try:
            date_str = date_str.lower().replace('.-', '-').replace('s/f.', 'fecha desconocida')
            if re.match(r'^\d{4}$', date_str):
                return f"{date_str}-01-01"
            return datetime.strptime(date_str, "%Y-%b-%d").strftime("%Y-%m-%d")
        except:
            return "fecha inválida"

    def process_excel(self, filepath):
        try:
            logger.info(f"📄 Procesando archivo: {filepath}")
            df = pd.read_excel(filepath, sheet_name=0, dtype=str)  # Usa primera hoja
            df = self._rename_columns(df)

            logger.info(f"🔧 Limpiando texto en columnas clave...")
            for col in ['descripcion', 'observaciones', 'palabras_clave', 'fecha_cronica', 'fecha_topica', 'folios']:
                if col in df.columns:
                    df[col] = df[col].apply(self._clean_text)

            if 'fecha_cronica' in df.columns:
                logger.info(f"📅 Normalizando fechas...")
                tqdm.pandas(desc="⏳ Normalizando fechas")
                df['fecha_cronica_iso'] = df['fecha_cronica'].progress_apply(self._normalize_date)

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
