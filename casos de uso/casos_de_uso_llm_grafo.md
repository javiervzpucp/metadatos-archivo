
# Casos de Uso del Sistema de Metadatos Históricos Basado en LLM + Grafo

---

## 1. Archivos y bibliotecas patrimoniales

### Problema:
Muchos archivos (coloniales, notariales, judiciales, etc.) tienen:

- Descripciones mínimas, informales o heterogéneas.
- Nombres de personas y lugares sin normalizar.
- Imposibilidad de interconectar documentos por entidades comunes.

### Solución:
El sistema permite:

- Extraer automáticamente keywords significativas desde catálogos antiguos.
- Clasificarlas como *persona*, *lugar*, *evento* o *institución*.
- Vincularlas con un tesauro SKOS o generar URIs propias.
- Exportar esta estructura como un grafo RDF, listo para integrarse a sistemas como GraphDB, Protégé o Wikibase.

### Ejemplo real:
Un archivo de la Sección Colonial del Instituto Riva-Agüero contiene:

> “Testimonio de posesión de tierras en el valle de Majes, firmado por el gobernador Alonso del Río”.

**Resultado del sistema:**

- `keywords = ["Majes", "Alonso del Río", "posesión de tierras"]`
- `tipos = ["lugar", "persona", "evento"]`
- URIs generadas o enlazadas a SKOS

---

## 2. Catálogos históricos digitalizados

### Problema:
Muchos catálogos están digitalizados como Excel o PDFs pero carecen de:

- Normalización de campos.
- Palabras clave formales.
- Acceso temático, geográfico o cronológico estructurado.

### Solución:
- Estandariza automáticamente las columnas (`signatura`, `fecha`, `descripción`, etc.).
- Usa LLM + grafo para enriquecer el contenido con entidades formalizadas.
- Permite navegación por conceptos jerárquicos (ej. “Virreinato del Perú” → “Gobierno local” → “Arequipa”).

### Ejemplo:
Del catálogo:

> “Carta dirigida al corregidor de Cusco sobre conflicto de tierras, 1781.”

**El sistema sugiere:**

- `keywords: ["Cusco", "conflicto de tierras", "corregidor"]`
- Conexiones: `:conflicto_de_tierras → evento`, `:Cusco → lugar`, `:corregidor → institución`

---

## 3. Humanidades digitales y visualización de redes

### Aplicación:
- Visualizar redes históricas de documentos, personajes, lugares.
- Explorar coocurrencias y trayectorias en el tiempo.

### Ejemplo:
Visualización de un grafo donde:

- Nodos = documentos, personas, lugares.
- Aristas = menciones, autoría, localización.
- Puedes ver cómo “Túpac Amaru II” aparece en varios documentos conectados con *Cusco*, *Rebelión de 1780*, *Virreinato*.

**Técnica**: Grafo interactivo con `PyVis`, `D3.js` o `NetworkX`.

---

## 4. Investigadores en historia o archivística

### Necesidad:
- Localizar documentos rápidamente.
- Explorar contextos documentales por actor o tema.
- Generar corpus temáticos.

### Funcionalidad del sistema:
- Búsqueda semántica (no literal) por entidad:  
  > “documentos relacionados con autoridades locales en Arequipa entre 1820 y 1850”.
- Sugiere documentos con descripciones similares o entidades conectadas.

### Ejemplo:
Consulta:

> “Arequipa gobierno local 1834”

**Resultado:**

- Lugar: Arequipa  
- Año: 1834 (extraído de fecha crónica)  
- Entidad: Gobierno del Perú (institución relacionada)

---

## 5. Sistemas de recomendación o RAG (Retrieval-Augmented Generation)

### Aplicación:
- Integrar con un sistema tipo chatbot histórico.
- Responder preguntas complejas con evidencia documental.

### Ejemplo:
Consulta:

> “¿Qué documentos mencionan a Nicolás de Piérola en conflictos militares?”

**El sistema:**

- Busca en FAISS embeddings híbridos con esa combinación de entidades.
- Recupera documentos con esas palabras clave (persona: Nicolás de Piérola, evento: conflicto).
- Devuelve no solo el texto, sino la estructura semántica completa.

---

## 6. Normalización y preservación digital

### Problema:
Las entidades mencionadas en los archivos no siempre existen en Wikidata o GeoNames.

### Funcionalidad:
- Genera URIs persistentes propias (`http://ira.pucp.edu.pe/entidad/alonso_del_rio`)
- Permite extender tesauros y vincular nuevas entidades entre documentos.

### Ejemplo:
> “Juan de Olivares”, personaje mencionado en 3 documentos de 1745, no está en Wikidata.

**El sistema:**

- Crea `owl:sameAs` interno.
- Lo vincula a documentos y eventos relevantes.
- Puede exportarse a Wikibase o integrarse a Wikidata manualmente.

---

## 7. Interfaz pública o académica

### Aplicación:
- Crear un portal web para consulta de archivos anotados con el grafo semántico.

### Ejemplo:
Una interfaz basada en Streamlit:

- Buscador por personaje, lugar, institución o evento.
- Visualización del grafo del documento seleccionado.
- Descarga de los metadatos RDF para integración externa.
