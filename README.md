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
- **Modelos de IA:** API de Google Gemini (`gemini-flash-latest` y `models/gemini-embedding-001`)
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

## ☁️ Despliegue en la Nube (OCI + Streamlit Cloud)

Debido a limitaciones temporales de disponibilidad de recursos gratuitos en las instancias de cómputo (VM.Standard.A1.Flex / VM.Standard.E2.1.Micro) de **Oracle Cloud Infrastructure (OCI)** en la región de Colombia Central, se optó por una **estrategia de despliegue híbrida** de nivel empresarial.

### 📐 Esquema de la Arquitectura Híbrida
```
[ OCI Object Storage ] --(Descarga Segura HTTP)--> [ App Streamlit Cloud ]
(Bucket: bimbam-buy-docs)                           (bimbambuy-agente)
                                                            |
                                                   [ Gemini API (LLM) ]
                                                   (gemini-flash-latest)
```

### 1. Almacenamiento en OCI Object Storage
Toda la documentación corporativa oficial (el corpus de 9 archivos en formatos PDF, CSV, JSON, MD y HTML) se encuentra alojada en la nube de **Oracle Cloud (OCI)**:
* **Espacio de Nombres (Namespace):** `axfpz54f6xyw`
* **Región de OCI:** `sa-bogota-1` (Colombia Central - Bogotá)
* **Nombre del Bucket:** `bimbam-buy-docs` (Acceso público de solo lectura)
* **Formato de URL de los Objetos:** `https://objectstorage.sa-bogota-1.oraclecloud.com/n/axfpz54f6xyw/b/bimbam-buy-docs/o/<nombre_archivo>`

### 2. Frontend y Orquestación en Streamlit Cloud
La interfaz interactiva y el motor RAG están alojados en **Streamlit Community Cloud** para garantizar alta disponibilidad y despliegue rápido.
* **URL de Producción:** [https://bimbambuy-agente.streamlit.app/](https://bimbambuy-agente.streamlit.app/)
* **CI/CD:** El despliegue se sincroniza automáticamente con cada `git push` a la rama `main` de este repositorio.

### 3. Optimizaciones para Cuotas Gratuitas de API (Mitigación de 429)
Para permitir que la aplicación funcione de manera estable con la API gratuita de Gemini, implementamos dos optimizaciones críticas:
* **Pre-Indexación Vectorial:** La base de datos vectorial FAISS se pre-compiló localmente y se subió en el repositorio (`faiss_index/`), evitando que el servidor en la nube consuma la cuota de embeddings en el arranque.
* **Manejo de Reintentos Exponenciales:** Tanto el Agente ReAct en `agent.py` (`max_retries=12`) como la interfaz en `app.py` tienen controladores que detectan errores de cuota (`RESOURCE_EXHAUSTED` / 429), pausando la ejecución 15 segundos y reintentando automáticamente en lugar de lanzar un error al usuario.

### 4. Alternativa de Despliegue Persistente en VM de OCI
Si deseas realizar el despliegue directo dentro de una máquina virtual (Compute Instance) de Linux en OCI, hemos dejado en la raíz los archivos de configuración listos para producción:
* **`Dockerfile`:** Para contenerizar la aplicación con Docker en OCI.
* **`alura-agente.service`:** Archivo de servicio Systemd para mantener el servicio activo e iniciarse automáticamente con el sistema operativo de la máquina virtual.
