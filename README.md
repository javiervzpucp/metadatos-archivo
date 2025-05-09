
# Sistema para Generación de Metadatos en Documentos Históricos

## Objetivo General

Construir un sistema que genere metadatos estructurados e interoperables a partir de catálogos históricos, utilizando estandarización, extracción con modelos de lenguaje, normalización semántica y construcción de grafos de conocimiento.

---

## FASE 1: Estandarización del Catálogo

**Entrada:** Archivos Excel o CSV con estructura variable.

**Acciones:**
- Homogeneizar nombres de columnas (`signatura`, `descripcion`, `fecha_cronica`, etc.).
- Separar `fecha_cronica` en `fecha_inicio` y `fecha_fin`.
- Normalizar campos de texto (quitar puntos, errores, espacios).
- Detectar y convertir fechas compuestas con reglas o LLM.

**Herramientas:**
- pandas
- re, datetime
- LLM (Mistral) para fechas complejas

**Resultado:**
Catálogo limpio y estructurado.

```
[doc_001]
 ├─ signatura: "Fondo123"
 ├─ fecha_cronica: "1836-Mar.-14/1852-Ago.-20"
 └─ descripcion: "Carta de..."
↓
[doc_001]
 ├─ fecha_inicio: 1836-03-14
 ├─ fecha_fin: 1852-08-20
 └─ descripcion normalizada
```

---

## FASE 2: Extracción de Palabras Clave con LLM

**Objetivo:** Identificar conceptos clave del contenido documental.

**Acciones:**
- Concatenar `fecha_topica`, `descripcion`, `observaciones`.
- Usar un LLM para extraer hasta 3 entidades clave:
  - personas
  - lugares
  - instituciones
  - eventos

**Ejemplo de Prompt:**

```
Extrae hasta 3 palabras clave del siguiente texto. Incluye solo nombres de personas, lugares, instituciones o eventos históricos. No incluyas términos genéricos.
```

**Resultado:**

```
["José Mariano Alvizuri", "Lima", "combate de Pacochas"]
```

```
[doc_001]
 └─ keywords: ["personaje", "evento", "lugar"]
```

---

## FASE 3: Normalización Semántica con Tesauro SKOS

**Objetivo:** Asociar keywords con conceptos normalizados.

**Acciones:**
- Consultar un tesauro SKOS con las keywords extraídas.
- Relacionar mediante `skos:prefLabel` o `skos:altLabel`.
- Obtener URIs de conceptos.

**Herramientas:**
- rdflib
- SPARQL

**Resultado:**

```
"combate de Pacochas" → <http://ira.pucp.edu.pe/tesauro/evento/combate_de_pacochas>
```

```
[doc_001]
 └─ subject → <tesauro:evento/combate_de_pacochas>
```

---

## FASE 4: Construcción del Grafo de Conocimiento

**Objetivo:** Modelar relaciones entre documentos, entidades y conceptos.

**Acciones:**
- Crear nodos RDF para documentos y entidades.
- Conectar mediante:
  - dc:subject
  - schema:location
  - prov:wasAssociatedWith
  - skos:broader, skos:related

**Herramientas:**
- rdflib
- NetworkX
- GraphDB / Neo4j (opcional)

**Resultado:**

```
[doc:001]
 ├─ mentions → José Mariano Alvizuri
 ├─ subject → combate de Pacochas
 ├─ location → Lima
 └─ linkedTo → Legión del Mérito Militar
```

---

## Usos del Grafo de Conocimiento

1. Búsqueda semántica mejorada.
2. Visualización de redes históricas.
3. Generación de líneas de tiempo.
4. Enriquecimiento con datos enlazados externos.
5. Control de autoridad automatizado.
6. Navegación facetada y jerárquica.

---

## Flujo General del Sistema

```
┌────────────┐
│ Excel/CSV  │
└─────┬──────┘
      ↓
[FASE 1: Estandarización]
      ↓
[FASE 2: Extracción con LLM]
      ↓
[FASE 3: Normalización con Tesauro SKOS]
      ↓
[FASE 4: Grafo de Conocimiento]
      ↓
Sistema interoperable de metadatos históricos
```

---
