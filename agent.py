import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from vector_db import VectorDatabaseManager

# Cargar variables de entorno
load_dotenv()

# Inicializar base de datos vectorial
db_manager = VectorDatabaseManager()

# Directorio de contactos corporativos para redirección
DIRECTORIO_CONTACTOS = """
Directorio de Contactos de BimBam Buy:
- Departamento de Devoluciones: devoluciones@bimbambuy.com (Ext. 201)
- Centro de Logística y Despacho: logistica@bimbambuy.com (Ext. 202)
- Departamento de Tesorería y Pagos: pagos@bimbambuy.com (Ext. 203)
- Área de Growth Marketing: marketing@bimbambuy.com (Ext. 204)
- Control de Calidad y Garantías: garantias@bimbambuy.com (Ext. 205)
- Área Jurídica y Compliance: legal@bimbambuy.com (Ext. 206)
- Soporte Técnico e Interno de TI: soporte@bimbambuy.com (Ext. 911)
"""

@tool
def buscar_documentos_corporativos(query: str) -> str:
    """Busca en la base de conocimiento de BimBam Buy información sobre devoluciones, reembolsos,
    tarifas de envío, tiempos de entrega, métodos de pago, garantías de productos, privacidad y soporte técnico de TI."""
    try:
        results = db_manager.search(query, k=4)
        if not results:
            return "No se encontraron documentos relevantes en la base de datos."
        
        formatted_docs = []
        for idx, doc in enumerate(results):
            meta = doc.metadata
            location = ""
            if "pagina" in meta:
                location = f"Página {meta['pagina']}"
            elif "fila" in meta:
                location = f"Fila {meta['fila']}"
            elif "indice" in meta:
                location = f"Registro {meta['indice']}"
            else:
                location = "Sección General"

            doc_str = (
                f"[Documento {idx+1}]\n"
                f"- Archivo: {meta.get('archivo')}\n"
                f"- Categoría: {meta.get('categoria')}\n"
                f"- Responsable: {meta.get('responsable')}\n"
                f"- Versión: {meta.get('version')}\n"
                f"- Ubicación: {location}\n"
                f"- Contenido:\n{doc.page_content}\n"
            )
            formatted_docs.append(doc_str)
        return "\n".join(formatted_docs)
    except Exception as e:
        return f"Error al buscar en la base vectorial: {e}"

# Definir herramientas accesibles por el agente
tools = [buscar_documentos_corporativos]

# Diseñar el prompt ReAct con memoria y directorio integrado (HU 05)
template = """Eres un asistente de Inteligencia Artificial corporativo para los colaboradores de la empresa BimBam Buy.
Tu objetivo es responder de manera clara y precisa a las dudas de los colaboradores utilizando ÚNICAMENTE la herramienta de búsqueda de documentos disponible.

Reglas de Oro del Comportamiento:
1. Responde con base única y exclusivamente en la información recuperada por la herramienta. No inventes datos, fechas, montos ni uses conocimiento previo.
2. Si la herramienta no devuelve información útil para responder a la consulta, di de forma directa y amigable: "No encontré esa información en los documentos corporativos disponibles." y sugiere que se pongan en contacto con el departamento responsable de esa área.
3. Al dar tu respuesta final, debes listar explícitamente en una sección llamada "Fuentes consultadas" los metadatos de los documentos que sustentan tu respuesta: archivo, categoría, responsable (owner), versión y ubicación (página, fila o registro).
4. Si la consulta involucra derivar con algún área, consulta el directorio de contactos provisto a continuación.

Directorio de Contactos Oficiales:
- Departamento de Devoluciones: devoluciones@bimbambuy.com (Ext. 201)
- Centro de Logística y Despacho: logistica@bimbambuy.com (Ext. 202)
- Departamento de Tesorería y Pagos: pagos@bimbambuy.com (Ext. 203)
- Área de Growth Marketing: marketing@bimbambuy.com (Ext. 204)
- Control de Calidad y Garantías: garantias@bimbambuy.com (Ext. 205)
- Área Jurídica y Compliance: legal@bimbambuy.com (Ext. 206)
- Soporte Técnico e Interno de TI: soporte@bimbambuy.com (Ext. 911)

Tienes acceso a las siguientes herramientas:

{tools}

Usa el siguiente formato estricto de razonamiento:

Question: la pregunta del colaborador que debes responder
Thought: siempre debes razonar sobre qué acción tomar
Action: la acción a ejecutar, debe ser una de [{tool_names}]
Action Input: el texto o consulta para la herramienta
Observation: el resultado de la herramienta
... (este proceso de Thought/Action/Action Input/Observation se puede repetir)
Thought: ¡Ahora sé la respuesta final!
Final Answer: tu respuesta final y detallada, formateada de manera premium e incluyendo siempre la sección de "Fuentes consultadas".

Historial de conversación:
{chat_history}

Pregunta del colaborador: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate(
    template=template,
    input_variables=["input", "tools", "tool_names", "agent_scratchpad", "chat_history"]
)

def get_agent_executor():
    # Instanciar el modelo LLM oficial para el Challenge (gemini-2.5-flash)
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.0,  # Temperatura baja para evitar alucinaciones
        max_output_tokens=1000,
        max_retries=12  # Reintentos automáticos para evitar fallos por cuota (429)
    )

    # Configurar memoria conversacional para mantener contexto del chat
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False  # ReAct estándar requiere strings, no objetos Message
    )

    # Crear agente ReAct
    agent = create_react_agent(llm, tools, prompt)

    # Orquestar el executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True  # Manejo automático de errores de formato de salida del LLM
    )
    return agent_executor

if __name__ == "__main__":
    print("Iniciando Agente Conversacional en modo consola de prueba...")
    agent_executor = get_agent_executor()
    print("Agente listo. Escribe 'salir' para terminar.")
    
    while True:
        user_input = input("\nColaborador: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break
        try:
            response = agent_executor.invoke({"input": user_input})
            print(f"\nAgente: {response['output']}")
        except Exception as e:
            print(f"\nError en el agente: {e}")
