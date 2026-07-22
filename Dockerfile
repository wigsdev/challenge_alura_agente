FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc en disco y buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar FAISS
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias primero (aprovechar cache de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto oficial de Streamlit
EXPOSE 8501

# Ejecutar el servidor Streamlit escuchando en todas las interfaces de red
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
