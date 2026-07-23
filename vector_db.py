import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from ingestion import DocumentIngestionPipeline

# Cargar variables de entorno (ej. GEMINI_API_KEY)
load_dotenv()

class VectorDatabaseManager:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.index_path = os.path.join(base_dir, "faiss_index")
        
        # Inicializar el modelo oficial de embeddings recomendado para el Challenge
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.db = None  # Cache de base de datos vectorial en memoria

    def build_and_save_index(self):
        print("Iniciando la construcción del índice vectorial...")
        
        # 1. Ejecutar el pipeline de ingesta para obtener los chunks
        pipeline = DocumentIngestionPipeline(base_dir=self.base_dir)
        chunks = pipeline.run()
        
        if not chunks:
            print("Error: No se generaron chunks para indexar.")
            return False

        print(f"Indexando {len(chunks)} chunks en base vectorial FAISS con control de tasa de cuota y auto-reintentos...")
        
        # 2. Crear e indexar en lotes con reintentos para evitar 429 RESOURCE_EXHAUSTED en Free Tier
        import time
        batch_size = 30
        db = None
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            print(f"-> Indexando lote {i // batch_size + 1} ({len(batch)} chunks)...")
            
            retries = 6
            success_batch = False
            while retries > 0 and not success_batch:
                try:
                    if db is None:
                        db = FAISS.from_documents(batch, self.embeddings)
                    else:
                        temp_db = FAISS.from_documents(batch, self.embeddings)
                        db.merge_from(temp_db)
                    success_batch = True
                except Exception as e:
                    error_msg = str(e)
                    if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                        print(f"Lote {i // batch_size + 1}: Limite de cuota alcanzado (429). Esperando 20 segundos para reintentar (Reintentos restantes: {retries - 1})...")
                        time.sleep(25)
                        retries -= 1
                    else:
                        print(f"Error fatal durante la indexacion del lote {i // batch_size + 1}: {e}")
                        return False
            
            if not success_batch:
                print("Error: No se pudo completar la indexacion tras multiples reintentos debido a limites de cuota de la API.")
                return False
            
            # Esperar brevemente entre lotes normales
            if i + batch_size < len(chunks):
                time.sleep(5)
        
        # 3. Guardar el índice localmente en disco
        if db:
            db.save_local(self.index_path)
            self.db = None  # Invalidar caché en memoria para forzar recarga
            print(f"Índice vectorial guardado exitosamente en: {self.index_path}")
            return True
        return False

    def load_vector_store(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"El índice vectorial no existe en: {self.index_path}. Ejecuta el script para construirlo primero.")
        
        # Cargar el índice local. Se requiere allow_dangerous_deserialization=True para archivos locales de confianza.
        return FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)

    def search(self, query, k=3, category_filter=None):
        if self.db is None:
            self.db = self.load_vector_store()
        
        # Configurar filtros por metadatos (HU 03 / HU 04)
        filter_dict = {}
        if category_filter:
            filter_dict["categoria"] = category_filter
            
        print(f"Ejecutando búsqueda semántica para: '{query}' | Filtro de categoría: {category_filter}...")
        
        # Búsqueda con similitud de coseno
        results = self.db.similarity_search(query, k=k, filter=filter_dict if filter_dict else None)
        return results

if __name__ == "__main__":
    manager = VectorDatabaseManager()
    
    # 1. Construir e indexar si no existe el índice, o si se desea reconstruir
    success = manager.build_and_save_index()
    
    if success:
        # 2. Realizar una búsqueda semántica de prueba para validación
        print("\n=== PRUEBA DE BÚSQUEDA VECTORIAL SEMÁNTICA ===")
        test_query = "¿Cuál es la política de reembolsos y plazos de devolución?"
        results = manager.search(test_query, k=2)
        
        for idx, doc in enumerate(results):
            print(f"\nResultado {idx + 1}:")
            print(f"- Archivo: {doc.metadata.get('archivo')}")
            print(f"- Categoría: {doc.metadata.get('categoria')}")
            print(f"- Responsable: {doc.metadata.get('responsable')}")
            print(f"- Página: {doc.metadata.get('pagina', 'N/A')}")
            print(f"- Contenido: {doc.page_content[:200]}...")
