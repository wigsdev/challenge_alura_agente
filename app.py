import streamlit as st
import os
from agent import get_agent_executor

# Configuración de página con título e icono representativo
st.set_page_config(
    page_title="Asistente BimBam Buy",
    page_icon="🛍️",
    layout="wide"
)

# Estilo CSS Premium personalizado (Glassmorphism, gradientes y tipografía moderna)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Degradado premium para el título principal */
    .title-gradient {
        background: linear-gradient(90deg, #00e676 0%, #00b0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #8a99ad;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Estilo de Tarjetas del Panel Lateral */
    .sidebar-card {
        background-color: #131a2c;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #1f2a45;
        margin-bottom: 1rem;
    }
    
    .sidebar-card h4 {
        color: #00e676;
        margin-top: 0;
        font-size: 1rem;
    }

    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 1rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar historial de conversación y ejecutor del agente en el estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = get_agent_executor()

if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = {}

# Barra Lateral (Sidebar) con información y controles
with st.sidebar:
    st.markdown('<div class="sidebar-card"><h4>🤖 BimBam Buy Agente</h4><p style="font-size:0.9rem; color:#8a99ad; margin:0;">Asistente inteligente oficial de atención interna para colaboradores corporativos.</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-card"><h4>📁 Base de Conocimiento</h4><p style="font-size:0.9rem; color:#8a99ad; margin:0; font-weight:600;">🟢 Estado: Conectado</p><p style="font-size:0.8rem; color:#8a99ad; margin:5px 0 0 0;">Indexados: 142 chunks vectoriales (PDF, CSV, JSON, MD, HTML)</p></div>', unsafe_allow_html=True)

    # Botón para limpiar conversación e historial
    if st.button("🗑️ Reiniciar Conversación", use_container_width=True):
        st.session_state.messages = []
        # Reiniciar ejecutor para borrar memoria interna
        st.session_state.agent_executor = get_agent_executor()
        st.rerun()

    st.markdown("<br><hr style='border-color:#1f2a45;'><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8rem; color:#8a99ad;'>Desarrollado para el Challenge Alura Agente © 2026</p>", unsafe_allow_html=True)

# Sección Principal del Dashboard
st.markdown('<h1 class="title-gradient">Asistente Corporativo BimBam Buy</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interroga de manera inteligente los manuales, políticas y guías de servicio oficiales.</p>', unsafe_allow_html=True)

# Mostrar el historial de conversación en la interfaz
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Ofrecer opciones de feedback interactivo en respuestas del agente (HU 06)
        if message["role"] == "assistant":
            col1, col2, col3 = st.columns([0.05, 0.05, 0.9])
            feedback_key = f"feedback_{idx}"
            
            with col1:
                if st.button("👍", key=f"up_{idx}"):
                    st.session_state.feedbacks[feedback_key] = "positivo"
            with col2:
                if st.button("👎", key=f"down_{idx}"):
                    st.session_state.feedbacks[feedback_key] = "negativo"
                    
            if feedback_key in st.session_state.feedbacks:
                status = st.session_state.feedbacks[feedback_key]
                col3.markdown(f"<span style='font-size:0.8rem; color:#8a99ad;'>Feedback registrado: <b>{status}</b></span>", unsafe_allow_html=True)

# Entrada de texto del usuario (Chat Input)
if prompt := st.chat_input("¿En qué puedo ayudarte hoy? (ej. plazos de devolución, tarifas de envío...)"):
    # Agregar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar la respuesta del asistente mediante el agente ReAct
    with st.chat_message("assistant"):
        with st.spinner("Buscando en manuales corporativos..."):
            try:
                # Invocar al agente pasándole la consulta
                result = st.session_state.agent_executor.invoke({"input": prompt})
                output_text = result["output"]
            except Exception as e:
                output_text = f"Ocurrió un error al procesar tu consulta: {e}"
                
            st.markdown(output_text)
            
            # Guardar la respuesta en el estado de sesión
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
    # Forzar el redibujado para renderizar botones de feedback de la nueva respuesta
    st.rerun()
