# Usa una imagen ligera de Python
FROM python:3.11-slim

# Establecer carpeta de trabajo
WORKDIR /app

# Instalar Graphviz a nivel sistema (esto es CLAVE)
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Render define PORT, así que usamos esa variable
CMD gunicorn --bind 0.0.0.0:$PORT app:app
