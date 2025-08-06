# 🔐 Environment variables'dan API key al
import openai
import json
import os
import glob
import time
from tqdm import tqdm
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# 🔐 OpenAI API Key (.env dosyasından)
openai.api_key = os.getenv("OPENAI_API_KEY")

# API key kontrol et
if not openai.api_key:
    print("❌ HATA: OPENAI_API_KEY environment variable bulunamadı!")
    print("   .env dosyasına OPENAI_API_KEY=your-key-here ekleyin.")
    exit(1)

# 📁 generated_questions klasöründeki JSON dosyalarını al
input_folder = "generated_questions"
json_files = sorted(glob.glob(os.path.join(input_folder, "konu_*.json")))

print(f"📊 Toplam {len(json_files)} JSON dosyası bulundu.")

# 📁 GPT response'ları için klasör oluştur
output_folder = "gpt_generated_questions"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 🔁 Her JSON dosyası için döngü - Progress bar ile
for i, json_file in enumerate(tqdm(json_files, desc="📚 JSON dosyaları işleniyor", unit="dosya")):

    # 📖 JSON dosyasını oku
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # JSON verisini string olarak format et
        json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"❌ JSON dosyası okunamadı: {e}")
        continue

    # 🔥 Prompt - JSON verisiyle birlikte
    prompt = f"""
Aşağıda bir matematik eğitimi için hazırlanmış soru-cevap JSON verisi bulunmaktadır. Bu JSON verisini analiz ederek, matematik eğitimi için değerlendirme ve geliştirme önerileri sunmanı istiyorum.



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

Çıktını JSON formatında ver:
''' JSON FALAN YAZMA SAKIN DİREKT OLARAK HATASIZ BİR ŞEKİLDE JSONA ÇEVİRİLEBİLİR OLMALIDIR RESPONSE
ÖRNEK BİR JSON ÇIKTISI BU ŞEKİLDEDİR:
[
  {{
    "type": "örnekli_soru",
    "instruction": "Asal çarpan nedir örnek verebilir misiniz?",
    "output": "Tabii! Örneğin 30 sayısını ele alalım. 30 = 2 × 3 × 5 şeklinde asal çarpanlara ayrılabilir. Yani asal çarpanları 2, 3 ve 5'tir."
  }},
  {{
    "type": "uygulamalı_soru",
    "instruction": "84 ve 90 sayılarının asal çarpanları nelerdir?",
    "output": "84 = 2 × 2 × 3 × 7 → asal çarpanlar: 2, 3, 7. 90 = 2 × 3 × 3 × 5 → asal çarpanlar: 2, 3, 5."
  }},
  {{
    "type": "yorum",
    "instruction": "Asal çarpanlar neden önemlidir?",
    "output": "Çünkü asal çarpanlar EKOK ve EBOB gibi konularda temel alınır. Ayrıca bir sayının yapısını anlamamıza yardımcı olur."
  }},
  {{
    "type": "hatalı_senaryo",
    "instruction": "60'ın asal çarpanları 4, 6 ve 10'dur. Doğru mu?",
    "output": "Hayır, bu yanlıştır. 4, 6 ve 10 asal sayılar değildir. 60'ın asal çarpanları sadece 2, 3 ve 5'tir."
  }}
]

İŞLEM YAPMAN GEREKEN JSON Verisi:
{json_content}
"""

    try:
        # ⏱️ İstek süresini ölç
        start_time = time.time()
        
        # 📡 GPT-4o API çağrısı
        response = openai.ChatCompletion.create(
            model="o3-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Sen, matematik eğitimi konusunda uzman bir analist ve değerlendiricisin. Matematik soru-cevap çiftlerini analiz ederek, eğitim kalitesi ve etkinliği hakkında detaylı değerlendirmeler yaparsın. Soruların kavramsal derinliğini, cevapların doğruluğunu ve genel eğitim değerini objektif bir şekilde değerlendirirsin."
                },
                {"role": "user", "content": prompt}
            ],
        )

        content = response["choices"][0]["message"]["content"].strip()
        
        # 🧹 GPT'nin bazen eklediği ```json ve ``` formatını temizle
        if content.startswith("```json"):
            content = content[7:]  # "```json" kısmını çıkar
        if content.startswith("```"):
            content = content[3:]   # "```" kısmını çıkar
        if content.endswith("```"):
            content = content[:-3]  # sondaki "```" kısmını çıkar
        
        content = content.strip()  # baştan-sondan boşlukları temizle
        
        # ⏱️ İstek süresini hesapla
        request_time = time.time() - start_time

        # ✅ Her JSON'dan gelen GPT response'u için ayrı dosya oluştur
        json_filename = os.path.basename(json_file).replace('.json', '')
        output_filename = os.path.join(output_folder, f"{json_filename}_generated.json")
        
        try:
            # JSON formatını doğrula
            analysis_data = json.loads(content)
            
            # Düzgün formatlı JSON olarak kaydet
            with open(output_filename, "w", encoding="utf-8") as out_f:
                json.dump(analysis_data, out_f, ensure_ascii=False, indent=2)
                
            # Progress bar ile süre ve dosya bilgisi göster
            tqdm.write(f"✅ {json_filename} - {request_time:.2f}sn - {len(analysis_data)} yeni çift")
            tqdm.write(f"💾 Dosya: {output_filename}")
            
        except json.JSONDecodeError:
            # JSON parse edilemezse ham içeriği kaydet
            with open(output_filename.replace('.json', '_raw.txt'), "w", encoding="utf-8") as out_f:
                out_f.write(content)
            tqdm.write(f"⚠️ {json_filename} - {request_time:.2f}sn - JSON hatası, ham kayıt: {output_filename.replace('.json', '_raw.txt')}")

    except Exception as e:
        tqdm.write(f"❌ HATA ({os.path.basename(json_file)}): {str(e)}")
        time.sleep(5)  # Hata varsa biraz bekle, sonra devam et
        continue

print("🎉 Tüm JSON dosyaları işlendi ve yeni sorular üretildi!")
print(f"📁 Sonuçlar '{output_folder}' klasöründe saklandı.")
