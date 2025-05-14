
# Proyecto de Innovación: Sistema Graph-RAG para Archivos Históricos

## Título del Proyecto
**Sistema Graph-RAG para la Generación Inteligente y Recuperación Semántica de Metadatos en Archivos Históricos**

---

## Resumen Ejecutivo
Este proyecto propone el desarrollo de un sistema inteligente para la generación, clasificación y recuperación de metadatos en documentos históricos mediante la integración de modelos de lenguaje (LLM), tesauros controlados y grafos de conocimiento. A través de una arquitectura de tipo Graph-RAG (Retrieval-Augmented Generation basada en grafos), se construye una infraestructura capaz de extraer entidades clave, relacionarlas semánticamente y permitir búsquedas e inferencias complejas, todo desde catálogos históricos digitalizados.

---

## Problema Detectado
Los archivos históricos —notariales, judiciales, coloniales— suelen carecer de metadatos estructurados, dificultando:
- La recuperación por entidades, temas o cronología.
- La reutilización del conocimiento archivístico.
- La preservación semántica a largo plazo.

Muchos catálogos existen solo como archivos Excel o PDF con descripciones informales y sin normalización.

---

## Solución Propuesta
Desarrollar un sistema completo compuesto por:

### 1. **Extracción automática de keywords**
- Uso de LLMs como Mistral/Mixtral para extraer entidades desde descripciones archivísticas.
- Clasificación automática en tipos: persona, lugar, evento, institución, documento.

### 2. **Alineamiento con tesauros SKOS y URIs**
- Normalización semántica a partir de vocabularios (como el Thesaurus UNESCO).
- Generación automática de URIs si no existen referencias externas.

### 3. **Construcción de grafo de conocimiento**
- Representación RDF de documentos y sus entidades.
- Exportación en formato interoperable (TTL), listo para GraphDB, Wikibase o Neo4j.

### 4. **Embedding híbrido (texto + grafo)**
- Creación de vectores con SentenceTransformers + Node2Vec.
- Integración en un índice FAISS para recuperación semántica.

### 5. **Módulo Graph-RAG**
- Combinación de búsqueda semántica y respuestas generadas por LLM.
- Interfaz de consulta y recomendación para usuarios finales.

---

## Casos de Uso
- Archivos nacionales, museos y bibliotecas patrimoniales.
- Proyectos de historia digital.
- Chatbots históricos y sistemas RAG explicables.
- Normalización y visualización de redes documentales.

---

## Resultados Esperados
- Un prototipo funcional y validado con catálogos reales.
- Un paquete tecnológico con scripts, modelos y ontologías.
- Un grafo interoperable enlazado con fuentes externas.
- Un índice FAISS para búsquedas avanzadas.
- Posible registro de software ante INDECOPI y validación con socios estratégicos.

---

## Nivel de madurez tecnológica (TRL)
**TRL 6**: Prototipo completo validado en entorno relevante, con posibilidad de despliegue inicial en entornos reales institucionales.

---

## Potencial de transferencia
El sistema puede ser transferido a:
- Archivos nacionales o regionales.
- Repositorios institucionales universitarios.
- Empresas de gestión documental o tecnología archivística.
- Sistemas de historia pública digital.

---

## Equipo propuesto
- Especialistas en IA y grafos semánticos.
- Expertos en archivística y humanidades digitales.
- Colaboradores institucionales con acceso a catálogos reales.

