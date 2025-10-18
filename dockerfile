FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen

WORKDIR /app

# Instalar dependencias del sistema necesarias para PySide6, OpenCV, PyZbar, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencias básicas
    build-essential \
    pkg-config \
    wget \
    curl \
    git \
    # Dependencias para PySide6/Qt
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-shm0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxcb-xtest0 \
    libxcb-xv0 \
    libxcb-xxf86vm0 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libegl1-mesa \
    libegl1 \
    libopengl0 \
    libgles2-mesa \
    libgles2 \
    # Dependencias para OpenCV
    libopencv-dev \
    python3-opencv \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    # Dependencias para PyZbar
    libzbar0 \
    libzbar-dev \
    # Dependencias para MongoDB
    libssl-dev \
    libffi-dev \
    # Dependencias adicionales para reportes y gráficos
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos primero para aprovechar cache de Docker
COPY Requisitos.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r Requisitos.txt

# Copiar el resto del código
COPY . .

# Crear directorio para reportes
RUN mkdir -p /app/report

# Hacer ejecutable el script de entrada
RUN chmod +x docker-entrypoint.sh

# Exponer puerto si es necesario
EXPOSE 8000

# Usar el script de entrada
ENTRYPOINT ["./docker-entrypoint.sh"]
