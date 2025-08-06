from flask import Flask, jsonify, request
import openai
import json
import os
import glob
import time
from tqdm import tqdm
import threading
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = Flask(__name__)

# 🔐 OpenAI API Key (.env dosyasından)
openai.api_key = os.getenv("OPENAI_API_KEY")

# API key kontrol et
if not openai.api_key:
    print("❌ HATA: OPENAI_API_KEY environment variable bulunamadı!")
    print("   .env dosyasına OPENAI_API_KEY=your-key-here ekleyin.")
    exit(1)

print(f"✅ OpenAI API Key yüklendi: {openai.api_key[:8]}...{openai.api_key[-4:]}")

# 🌐 Global değişkenler
current_status = {
    "is_running": False,
    "current_file": "",
    "processed_count": 0,
    "total_count": 0,
    "start_time": None,
    "errors": [],
    "completed_files": [],
    "current_request_time": 0
}

def process_json_files():
    """JSON dosyalarını işleyen ana fonksiyon"""
    global current_status
    
    try:
        # 📁 Klasörleri kontrol et
        input_folder = "generated_questions"
        output_folder = "gpt_generated_questions"
        
        if not os.path.exists(input_folder):
            current_status["errors"].append(f"Input klasörü bulunamadı: {input_folder}")
            return
            
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # 📊 JSON dosyalarını al
        json_files = sorted(glob.glob(os.path.join(input_folder, "konu_*.json")))
        
        if not json_files:
            current_status["errors"].append("İşlenecek JSON dosyası bulunamadı")
            return
            
        current_status["total_count"] = len(json_files)
        current_status["is_running"] = True
        current_status["start_time"] = datetime.now()
        
        # 🔁 Her JSON dosyası için döngü
        for i, json_file in enumerate(json_files):
            if not current_status["is_running"]:  # Durdurulmuşsa çık
                break
                
            current_status["current_file"] = os.path.basename(json_file)
            current_status["processed_count"] = i
            
            # 📖 JSON dosyasını oku
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
                
            except Exception as e:
                error_msg = f"JSON dosyası okunamadı ({os.path.basename(json_file)}): {e}"
                current_status["errors"].append(error_msg)
                continue

            # 🔥 Prompt
            prompt = f"""
Aşağıda bir matematik eğitimi için hazırlanmış JSON formatında instruction-output verileri bulunmaktadır.

Her bir instruction-output çifti bir eğitim maddesini temsil eder. Bu verileri analiz ederek, aşağıdaki kurallara göre genişletilmiş eğitim verisi üretmeni istiyorum:

### 🎯 Görev Tanımı:
Her bir mevcut veri için, **ek olarak 4 adet yeni instruction-output çifti** üret:
0. UNUTMA HER BİR INSTRUCTION-OUTPUT SETI İÇİN 4 ADET YENİ INSTRUCTION OUPTUT CIFTI URETILMELDIR
1. **örnekli_soru**: Öğrencinin kavramı uygulamak için sorduğu bir örnek soruyu ve öğretmen benzeri açıklamalı cevabı.
2. **uygulamalı_soru**: Somut sayılarla işlem içeren bir soru ve adım adım çözüm.
3. **yorum**: Kavramın önemine, kullanımına ya da öğrencilerin sık yaptığı hatalara dair bir açıklama.
4. **hatalı_senaryo**: Öğrencinin yanlış anladığı veya kavramı hatalı kullandığı bir örnek ve buna verilen düzeltici açıklama.

### 🔧 Format:
Çıktını **JSON array** olarak ver. Her öğede aşağıdaki alanlar olacak:
- `type`: `"örnekli_soru"`, `"uygulamalı_soru"`, `"yorum"`, `"hatalı_senaryo"`
- `instruction`: Öğrencinin sorduğu veya düşündüğü doğal soru
- `output`: Matematik öğretmeni tarzında açıklayıcı cevap

### 📌 Notlar:
- Cevapların hedefi 8. sınıf öğrencisine uygun olmalı
- Öğretici, açıklayıcı ve örnekli anlatım tercih et
- Output kısmı asla çok kısa veya yüzeysel olmasın
- Asla var olan verileri kopyalama; özgün üret

''' JSON FALAN YAZMA SAKIN DİREKT OLARAK HATASIZ BİR ŞEKİLDE JSONA ÇEVİRİLEBİLİR OLMALIDIR RESPONSE
ÖRNEK BİR JSON ÇIKTISI BU ŞEKİLDEDİR:
[
  {{{{
    "type": "örnekli_soru",
    "instruction": "Asal çarpan nedir örnek verebilir misiniz?",
    "output": "Tabii! Örneğin 30 sayısını ele alalım. 30 = 2 × 3 × 5 şeklinde asal çarpanlara ayrılabilir. Yani asal çarpanları 2, 3 ve 5'tir."
  }}}},
  {{{{
    "type": "uygulamalı_soru",
    "instruction": "84 ve 90 sayılarının asal çarpanları nelerdir?",
    "output": "84 = 2 × 2 × 3 × 7 → asal çarpanlar: 2, 3, 7. 90 = 2 × 3 × 3 × 5 → asal çarpanlar: 2, 3, 5."
  }}}},
  {{{{
    "type": "yorum",
    "instruction": "Asal çarpanlar neden önemlidir?",
    "output": "Çünkü asal çarpanlar EKOK ve EBOB gibi konularda temel alınır. Ayrıca bir sayının yapısını anlamamıza yardımcı olur."
  }}}},
  {{{{
    "type": "hatalı_senaryo",
    "instruction": "60'ın asal çarpanları 4, 6 ve 10'dur. Doğru mu?",
    "output": "Hayır, bu yanlıştır. 4, 6 ve 10 asal sayılar değildir. 60'ın asal çarpanları sadece 2, 3 ve 5'tir."
  }}}}
]

İŞLEM YAPMAN GEREKEN JSON Verisi:
{json_content}
"""

            try:
                # ⏱️ İstek süresini ölç
                start_time = time.time()
                
                # 📡 API çağrısı
                response = openai.ChatCompletion.create(
                    model="o3-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Sen, matematik eğitimi konusunda uzman bir analist ve değerlendiricisin. Matematik soru-cevap çiftlerini analiz ederek, eğitim kalitesi ve etkinliği hakkında detaylı değerlendirmeler yaparsın. Soruların kavramsal derinliğini, cevapların doğruluğunu ve genel eğitim değerini objektif bir şekilde değerlendirirsin."
                        },
                        {"role": "user", "content": prompt}
                    ]
                )

                content = response["choices"][0]["message"]["content"].strip()
                
                # 🧹 Markdown formatını temizle
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                content = content.strip()
                
                # ⏱️ İstek süresini hesapla
                request_time = time.time() - start_time
                current_status["current_request_time"] = round(request_time, 2)

                # ✅ Dosyayı kaydet
                json_filename = os.path.basename(json_file).replace('.json', '')
                output_filename = os.path.join(output_folder, f"{json_filename}_generated.json")
                
                try:
                    # JSON formatını doğrula
                    analysis_data = json.loads(content)
                    
                    # Kaydet
                    with open(output_filename, "w", encoding="utf-8") as out_f:
                        json.dump(analysis_data, out_f, ensure_ascii=False, indent=2)
                        
                    current_status["completed_files"].append({
                        "file": json_filename,
                        "time": request_time,
                        "count": len(analysis_data),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except json.JSONDecodeError:
                    # JSON hatası varsa ham kaydet
                    with open(output_filename.replace('.json', '_raw.txt'), "w", encoding="utf-8") as out_f:
                        out_f.write(content)
                    current_status["errors"].append(f"JSON hatası: {json_filename}")

            except Exception as e:
                error_msg = f"API hatası ({os.path.basename(json_file)}): {str(e)}"
                current_status["errors"].append(error_msg)
                time.sleep(5)
                continue

    except Exception as e:
        current_status["errors"].append(f"Genel hata: {str(e)}")
    
    finally:
        current_status["is_running"] = False
        current_status["current_file"] = ""

@app.route('/')
def home():
    """Ana sayfa"""
    return jsonify({
        "message": "JSON İşleme API'si",
        "endpoints": {
            "/status": "Mevcut durumu göster",
            "/start": "İşlemi başlat",
            "/stop": "İşlemi durdur",
            "/logs": "Son logları göster"
        }
    })

@app.route('/status')
def get_status():
    """Mevcut durumu döndür"""
    status = current_status.copy()
    
    if status["start_time"]:
        elapsed = datetime.now() - status["start_time"]
        status["elapsed_time"] = str(elapsed).split('.')[0]  # Saniye kısmını çıkar
        
        if status["total_count"] > 0:
            progress_percent = (status["processed_count"] / status["total_count"]) * 100
            status["progress_percent"] = round(progress_percent, 2)
    
    return jsonify(status)

@app.route('/start', methods=['POST'])
def start_processing():
    """İşlemi başlat"""
    global current_status
    
    if current_status["is_running"]:
        return jsonify({
            "error": "İşlem zaten çalışıyor",
            "current_file": current_status["current_file"]
        }), 400
    
    # Status'u sıfırla
    current_status = {
        "is_running": False,
        "current_file": "",
        "processed_count": 0,
        "total_count": 0,
        "start_time": None,
        "errors": [],
        "completed_files": [],
        "current_request_time": 0
    }
    
    # Arka planda işlemi başlat
    thread = threading.Thread(target=process_json_files)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "message": "İşlem başlatıldı",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stop', methods=['POST'])
def stop_processing():
    """İşlemi durdur"""
    global current_status
    
    if not current_status["is_running"]:
        return jsonify({
            "error": "Çalışan işlem yok"
        }), 400
    
    current_status["is_running"] = False
    
    return jsonify({
        "message": "İşlem durduruldu",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/logs')
def get_logs():
    """Son logları döndür"""
    return jsonify({
        "errors": current_status["errors"][-10:],  # Son 10 hata
        "completed_files": current_status["completed_files"][-10:],  # Son 10 tamamlanan
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 JSON İşleme API'si başlatılıyor...")
    print("📡 Endpoints:")
    print("   GET  /         - Ana sayfa")
    print("   GET  /status   - Durum bilgisi") 
    print("   POST /start    - İşlemi başlat")
    print("   POST /stop     - İşlemi durdur")
    print("   GET  /logs     - Log bilgileri")
    print("\n🌐 API çalışıyor: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)