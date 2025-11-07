# Usar imagen base con Python 3.11
FROM python:3.11-slim-bullseye

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements-production.txt .
RUN pip install --no-cache-dir -r requirements-production.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/raw/acm data/raw/sage data/processed

# Exponer puerto
EXPOSE 8080

# Variables de entorno
ENV ENVIRONMENT=production
ENV PORT=8080
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Comando de inicio
CMD ["gunicorn", "webui:app", "--bind", "0.0.0.0:8080", "--timeout", "600", "--workers", "2"]
