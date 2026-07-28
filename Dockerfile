# Utilizar una imagen base oficial de Python ligera
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y forzar salida en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto por defecto de la aplicación
EXPOSE 8503

# Comando para ejecutar la aplicación Streamlit configurando el puerto y escuchando en todas las interfaces
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8503", "--server.address", "0.0.0.0"]
