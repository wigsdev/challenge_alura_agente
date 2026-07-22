import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DocumentIngestionPipeline:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.docs_dir = os.path.join(base_dir, "documentos")
        self.bimbam_dir = os.path.join(self.docs_dir, "bimbam_buy")
        self.inventory_path = os.path.join(self.docs_dir, "inventario_documentos.json")
        
        # Configurar fragmentador de texto
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_inventory(self):
        if not os.path.exists(self.inventory_path):
            raise FileNotFoundError(f"Inventario no encontrado en: {self.inventory_path}")
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clean_text(self, text):
        if not text:
            return ""
        # Limpieza básica de espacios y saltos de línea repetidos
        lines = [line.strip() for line in text.splitlines()]
        cleaned = " ".join([line for line in lines if line])
        return cleaned

    def parse_pdf(self, filepath, doc_meta):
        documents = []
        try:
            reader = PdfReader(filepath)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                cleaned_text = self.clean_text(text)
                if cleaned_text:
                    # Inyectar metadatos específicos por página
                    meta = doc_meta.copy()
                    meta["pagina"] = page_num + 1
                    meta["source"] = filepath
                    documents.append(Document(page_content=cleaned_text, metadata=meta))
        except Exception as e:
            print(f"Error al procesar PDF {filepath}: {e}")
        return documents

    def parse_markdown(self, filepath, doc_meta):
        documents = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            # Mantenemos los títulos en MD ya que proveen estructura lógica
            meta = doc_meta.copy()
            meta["source"] = filepath
            documents.append(Document(page_content=text, metadata=meta))
        except Exception as e:
            print(f"Error al procesar Markdown {filepath}: {e}")
        return documents

    def parse_csv(self, filepath, doc_meta):
        documents = []
        try:
            df = pd.read_csv(filepath)
            # Conversión de filas en descripciones semánticas legibles
            for idx, row in df.iterrows():
                row_str = ", ".join([f"{col}: {val}" for col, val in row.items()])
                content = f"Registro de tarifas {idx + 1}: {row_str}"
                meta = doc_meta.copy()
                meta["fila"] = idx + 1
                meta["source"] = filepath
                documents.append(Document(page_content=content, metadata=meta))
        except Exception as e:
            print(f"Error al procesar CSV {filepath}: {e}")
        return documents

    def parse_json(self, filepath, doc_meta):
        documents = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Estructurar pares de Pregunta/Respuesta para conservar semántica
            for idx, item in enumerate(data):
                pregunta = item.get("pregunta", "")
                respuesta = item.get("respuesta", "")
                content = f"Pregunta: {pregunta} | Respuesta: {respuesta}"
                meta = doc_meta.copy()
                meta["indice"] = idx + 1
                meta["source"] = filepath
                documents.append(Document(page_content=content, metadata=meta))
        except Exception as e:
            print(f"Error al procesar JSON {filepath}: {e}")
        return documents

    def parse_html(self, filepath, doc_meta):
        documents = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            # Extraer contenido de texto omitiendo scripts y estilos
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            cleaned_text = self.clean_text(text)
            if cleaned_text:
                meta = doc_meta.copy()
                meta["source"] = filepath
                documents.append(Document(page_content=cleaned_text, metadata=meta))
        except Exception as e:
            print(f"Error al procesar HTML {filepath}: {e}")
        return documents

    def run(self):
        print("Iniciando pipeline de ingesta y extracción de contenido...")
        inventory = self.load_inventory()
        all_chunks = []

        for doc in inventory:
            filename = doc["archivo"]
            formato = doc["formato"]
            filepath = os.path.join(self.bimbam_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"Advertencia: El archivo {filename} no existe en la ruta {filepath}")
                continue

            print(f"Procesando archivo [{formato}]: {filename}...")
            
            # Preparar metadatos base del inventario (HU 01)
            doc_meta = {
                "archivo": doc["archivo"],
                "categoria": doc["categoria"],
                "responsable": doc["responsable"],
                "version": doc["version"],
                "estado": doc["estado"]
            }

            # Extracción por formato (HU 02)
            parsed_docs = []
            if formato == "PDF":
                parsed_docs = self.parse_pdf(filepath, doc_meta)
            elif formato == "Markdown":
                parsed_docs = self.parse_markdown(filepath, doc_meta)
            elif formato == "CSV":
                parsed_docs = self.parse_csv(filepath, doc_meta)
            elif formato == "JSON":
                parsed_docs = self.parse_json(filepath, doc_meta)
            elif formato == "HTML":
                parsed_docs = self.parse_html(filepath, doc_meta)
            else:
                print(f"Formato no soportado: {formato}")
                continue

            # Fragmentación (Chunking) y acumulación
            # Formatos pre-estructurados fila por fila o QA no requieren chunking por tamaño fijo
            if formato in ["CSV", "JSON"]:
                # Cada registro es un chunk semántico completo
                all_chunks.extend(parsed_docs)
                print(f"-> Generados {len(parsed_docs)} chunks estructurados directos.")
            else:
                # Fragmentamos PDFs, Markdown e HTMLs
                chunks = self.text_splitter.split_documents(parsed_docs)
                all_chunks.extend(chunks)
                print(f"-> Fragmentado en {len(chunks)} chunks de texto.")

        print(f"\nProceso concluido con éxito. Total de chunks generados: {len(all_chunks)}")
        return all_chunks

if __name__ == "__main__":
    pipeline = DocumentIngestionPipeline()
    chunks = pipeline.run()
    if chunks:
        print("\nEjemplo de Chunk Indexado:")
        print(f"Contenido: {chunks[0].page_content[:200]}...")
        print(f"Metadatos: {chunks[0].metadata}")
