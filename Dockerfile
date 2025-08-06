# 🐳 Python 3.9 slim image kullan
FROM python:3.9-slim

# 📁 Çalışma dizinini ayarla
WORKDIR /app

# 🔧 Sistem paketlerini güncelle ve gerekli paketleri kur
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 📦 Python gereksinimlerini kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Uygulama dosyalarını kopyala
COPY api_server.py .

# 👤 Root olmayan kullanıcı oluştur ve izinleri ayarla
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

USER appuser

# 🌐 Port'u aç
EXPOSE 8001
#
# 🚀 Uygulamayı başlat
CMD ["python", "-u", "api_server.py"]