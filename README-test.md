# 🚀 JSON İşleme API'si

Bu API, matematik eğitimi JSON dosyalarını otomatik olarak işleyerek genişletilmiş soru-cevap setleri üretir.

## 📋 Özellikler

- 🔄 **7/24 Çalışma**: Sunucuda sürekli çalışabilir
- 📊 **Progress Tracking**: Real-time durum takibi
- 🌐 **REST API**: HTTP endpoints ile kontrol
- ⚡ **Background Processing**: Arka planda işleme
- 📝 **Logging**: Detaylı log kayıtları
- 🛑 **Start/Stop Control**: İşlemi başlatma/durdurma

## 🛠️ Kurulum

### Windows:
```bash
run_server.bat
```

### Linux/Mac:
```bash
chmod +x run_server.sh
./run_server.sh
```

### Manuel Kurulum:
```bash
# Sanal ortam oluştur
python -m venv venv

# Aktifleştir (Windows)
venv\Scripts\activate
# Aktifleştir (Linux/Mac)
source venv/bin/activate

# Gereksinimleri kur
pip install -r requirements.txt

# API'yi başlat
python api_server.py
```

## 📁 Klasör Yapısı

```
📦 Proje
├── 📂 generated_questions/          # Input JSON dosyaları
│   ├── konu_001_sorular.json
│   ├── konu_002_sorular.json
│   └── ...
├── 📂 gpt_generated_questions/      # Çıktı dosyaları
│   ├── konu_001_sorular_generated.json
│   └── ...
├── api_server.py                    # Ana API dosyası
├── requirements.txt                 # Python gereksinimleri
└── README.md                       # Bu dosya
```

## 📡 API Endpoints

### 🏠 Ana Sayfa
```http
GET http://localhost:5000/
```

### 📊 Durum Kontrolü
```http
GET http://localhost:5000/status
```

**Response:**
```json
{
  "is_running": true,
  "current_file": "konu_045_sorular.json",
  "processed_count": 44,
  "total_count": 324,
  "progress_percent": 13.58,
  "elapsed_time": "0:12:34",
  "current_request_time": 3.45,
  "errors": [],
  "completed_files": [...]
}
```

### ▶️ İşlemi Başlat
```http
POST http://localhost:5000/start
```

### ⏹️ İşlemi Durdur
```http
POST http://localhost:5000/stop
```

### 📋 Log Kayıtları
```http
GET http://localhost:5000/logs
```

## 🔧 Kullanım

1. **Klasörleri Hazırla**: `generated_questions/` klasörüne JSON dosyalarını koy
2. **API'yi Başlat**: `python api_server.py`
3. **İşlemi Başlat**: POST isteği gönder `/start` endpoint'ine
4. **Durumu Takip Et**: GET isteği ile `/status` kontrolü
5. **Sonuçları Al**: `gpt_generated_questions/` klasöründen çıktıları al

## 🌐 Curl Örnekleri

```bash
# Durum kontrolü
curl http://localhost:5000/status

# İşlemi başlat
curl -X POST http://localhost:5000/start

# İşlemi durdur
curl -X POST http://localhost:5000/stop

# Logları al
curl http://localhost:5000/logs
```

## 🔑 API Key Ayarı

`api_server.py` dosyasındaki API key'i güncelle:
```python
openai.api_key = "your-openai-api-key-here"
```

## 📝 Log Formatı

API aşağıdaki bilgileri takip eder:
- ✅ **Başarılı İşlemler**: Dosya adı, süre, üretilen soru sayısı
- ❌ **Hatalar**: Hata mesajları ve hangi dosyada oluştuğu
- 📊 **Progress**: Kaç dosyanın işlendiği, kalan süre tahmini

## 🚀 Sunucuda Çalıştırma

### PM2 ile (Önerilen):
```bash
# PM2 kur
npm install -g pm2

# API'yi başlat
pm2 start api_server.py --name "json-api" --interpreter python

# Durumu kontrol et
pm2 status

# Logları takip et
pm2 logs json-api
```

### Screen ile:
```bash
# Screen oturumu başlat
screen -S json-api

# API'yi çalıştır
python api_server.py

# Ctrl+A+D ile detach et
```

## ⚡ Performans

- **Model**: o3-mini (hızlı ve ekonomik)
- **Ortalama İstek Süresi**: 3-5 saniye
- **Günlük Kapasite**: ~17.280 dosya (saniyede 1 dosya varsayımı)
- **Memory Usage**: ~100-200MB

## 🛠️ Troubleshooting

### "generated_questions klasörü bulunamadı"
- `generated_questions/` klasörü oluştur
- JSON dosyalarını içine koy

### "OpenAI API hatası"
- API key'i kontrol et
- İnternet bağlantısını kontrol et
- Rate limit kontrolü yap

### "Port 5000 kullanımda"
- `api_server.py` içinde port numarasını değiştir
- Veya çalışan process'i durdur

## 🐳 Docker ile Çalıştırma

### Hızlı Başlangıç:
```bash
# Windows
docker-run.bat

# Linux/Mac
chmod +x docker-run.sh
./docker-run.sh
```

### Manuel Docker Kurulumu:
```bash
# Image'ı build et
docker-compose build

# Container'ı başlat
docker-compose up -d

# Durumu kontrol et
docker-compose ps

# Logları takip et
docker-compose logs -f

# Durdur
docker-compose down
```

### Docker Avantajları:
- ✅ **Kolay Deploy**: Tek komutla her yerde çalışır
- ✅ **İzolasyon**: Sistem bağımsız çalışma
- ✅ **Auto-restart**: Container otomatik yeniden başlar
- ✅ **Health Check**: Otomatik sağlık kontrolü
- ✅ **Log Management**: Otomatik log rotasyonu

## 📞 İletişim

API çalışırken terminal'de detaylı bilgiler görüntülenir. Sorun yaşanırsa `/logs` endpoint'ine bakın.