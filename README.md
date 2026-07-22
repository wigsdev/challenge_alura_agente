# Challenge Alura Agente - Asistente Corporativo de IA (RAG)

Este repositorio contiene la implementación del **Challenge Alura Agente**, un asistente inteligente corporativo diseñado para responder consultas de los colaboradores a partir de múltiples formatos de documentos organizacionales (PDF, CSV, JSON, Markdown, HTML). 

La solución está construida bajo una arquitectura de **Generación Aumentada por Recuperación (RAG)** con control de estado y orquestada para su despliegue en la nube de **Oracle Cloud Infrastructure (OCI)**.

---

## 🏗️ Arquitectura de la Solución

El flujo operativo del agente se divide en tres fases principales:

```
[Documentos] -> [Ingesta / Chunking] -> [Embeddings] -> [Vector DB (FAISS/Chroma)]
                                                              | (Búsqueda)
[Usuario]    -> [Consulta] -> [Agente ReAct] -> [Retrieval] --+
                                    |
                             [Respuesta + Fuentes]
```

1. **Ingesta y Procesamiento (`ingestion.py`):** Carga y limpia dinámicamente los archivos de la base de conocimiento (`documentos/`), dividiéndolos en fragmentos lógicos (*chunks*) e inyectando metadatos para trazabilidad (fuente, página/línea, categoría).
2. **Capa Vectorial (`vector_db.py`):** Convierte los fragmentos en vectores densos utilizando embeddings (Google/Hugging Face) y los almacena localmente para realizar búsquedas semánticas basadas en similitud de coseno.
3. **Capa Conversacional y Agente (`agent.py` & `app.py`):** Un agente basado en el razonamiento de acción (ReAct) de LangChain que utiliza herramientas personalizadas (`@tool`) para interrogar la base vectorial. Cuenta con memoria conversacional e interactúa a través de una interfaz interactiva en Streamlit.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.10+
- **Orquestación de IA:** LangChain & LangGraph
- **Base de Datos Vectorial:** FAISS / Chroma
- **Modelos de IA:** API de Google Gemini (`gemini-2.5-flash` y `models/text-embedding-004`)
- **Interfaz Web:** Streamlit
- **Infraestructura Cloud:** Oracle Cloud Infrastructure (OCI)

---

## 🚀 Guía de Inicio Rápido (Local)

### 1. Clonar el repositorio
```bash
git clone https://github.com/wigsdev/challenge_alura_agente.git
cd challenge_alura_agente
```

### 2. Configurar el Entorno Virtual
```bash
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto a partir de `.env.example`:
```bash
GEMINI_API_KEY=tu_api_key_aqui
```

### 5. Ingesta de Documentos
Coloca tus documentos corporativos en la carpeta `documentos/` y ejecuta:
```bash
python ingestion.py
```

### 6. Ejecutar la Aplicación
```bash
streamlit run app.py
```

---

## ☁️ Despliegue en la Nube (OCI)

*(Próximamente: Evidencias de ejecución, diagramas de topología de red en OCI y pasos de despliegue persistente mediante Systemd).*
