FROM python:3.11-slim

WORKDIR /app

# Instalar Graphviz a nivel sistema
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Usar gunicorn apuntando al puerto que Render ponga en $PORT
CMD gunicorn --bind 0.0.0.0:$PORT app:app
