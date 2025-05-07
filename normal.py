# -*- coding: utf-8 -*-
"""
Created on Wed May  7 17:38:06 2025

@author: jveraz
"""

from ira_catalog_converter import IRACatalogConverter

converter = IRACatalogConverter(data_folder="datos")
df = converter.combine_excels()
df.to_csv("catalogo_completo_estandarizado.csv", index=False, encoding="utf-8-sig")


# Vista previa
print(df.head())
