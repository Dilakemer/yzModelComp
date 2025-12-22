# 🧪 Hata Türleri AI Test Sistemi

Test otomasyonunda karşılaşılan hata türlerini yapay zeka modelleriyle analiz eden ve sonuçları veritabanında saklayan bir web uygulaması.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)

## 📋 Özellikler

- ✅ **12 Hata Kategorisi**: API, Otomasyon, Tarayıcı, Kodlama, Konfigürasyon, Veri, Veritabanı, Çevresel, Ağ, Performans, Güvenlik, Sürüm Uyumsuzluğu
- ✅ **AI Model Entegrasyonu**: Google Gemini ve Hugging Face modelleri
- ✅ **Soru Yönetimi**: Her kategori için test soruları ekleme/silme
- ✅ **Model Karşılaştırma**: Aynı soruyu birden fazla modelle test etme
- ✅ **Sonuç Kaydetme**: Tüm yanıtlar veritabanında saklanır
- ✅ **Modern Arayüz**: Karanlık tema, responsive tasarım

## 🚀 Kurulum

### 1. Gereksinimleri Yükleyin

```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Ayarlayın

`.env` dosyasını düzenleyin:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

**API Anahtarı Alma:**
- **Gemini**: [Google AI Studio](https://aistudio.google.com/apikey)
- **Hugging Face**: [HuggingFace Settings](https://huggingface.co/settings/tokens)
  - Token oluştururken "Make calls to Inference Providers" iznini açın

### 3. Veritabanını Oluşturun

```bash
python seed_data.py
```

### 4. Sunucuyu Başlatın

```bash
python main.py
```

Uygulama http://localhost:8000 adresinde çalışacaktır.

## 📁 Proje Yapısı

```
yz_lab/
├── main.py              # FastAPI ana uygulama
├── database.py          # SQLite veritabanı bağlantısı
├── models.py            # SQLAlchemy ORM modelleri
├── ai_services.py       # Gemini & HuggingFace API servisleri
├── seed_data.py         # Veritabanı başlangıç verileri
├── requirements.txt     # Python bağımlılıkları
├── .env                 # API anahtarları (gizli)
├── error_testing.db     # SQLite veritabanı
└── static/
    ├── index.html       # Ana sayfa
    ├── css/style.css    # Stiller
    └── js/app.js        # Frontend JavaScript
```

## 🤖 Desteklenen Modeller

### Google Gemini
| Model | RPM | TPM | RPD |
|-------|-----|-----|-----|
| gemini-2.5-flash-lite | 10 | 250K | 20 |
| gemini-2.5-flash | 5 | 250K | 20 |
| gemini-robotics-er-1.5-preview | 10 | 250K | 20 |

### Hugging Face (Açık Kaynak)
- Qwen/Qwen2.5-Coder-32B-Instruct
- meta-llama/Llama-3.2-3B-Instruct

## 📊 Veritabanı Şeması

```
┌─────────────────┐     ┌─────────────────┐
│ error_categories│     │   error_types   │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ category_id(FK) │
│ category_code   │     │ id (PK)         │
│ category_name   │     │ error_type      │
│ description     │     │ description     │
└─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐     ┌─────────────────┐
│    questions    │     │   ai_results    │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ question_id(FK) │
│ category_id(FK) │     │ id (PK)         │
│ question_text   │     │ model_name      │
│ created_at      │     │ model_provider  │
└─────────────────┘     │ response        │
                        │ response_time   │
                        │ tested_at       │
                        └─────────────────┘
```

## 🔧 API Endpoints

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/categories` | Tüm hata kategorileri |
| GET | `/api/categories/{id}` | Kategori detayı |
| GET | `/api/questions` | Tüm sorular |
| POST | `/api/questions` | Yeni soru ekle |
| DELETE | `/api/questions/{id}` | Soru sil |
| GET | `/api/models` | Mevcut AI modelleri |
| POST | `/api/test` | Tekil model testi |
| POST | `/api/test-all` | Tüm modellerle test |
| GET | `/api/results` | Test sonuçları |
| GET | `/api/stats` | İstatistikler |

## 📝 Kullanım

1. **Kategorileri Görüntüle**: Sol menüden "Kategoriler"e tıklayın
2. **Soru Ekle**: "Sorular" → "Yeni Soru Ekle" butonuna tıklayın
3. **Test Çalıştır**: "AI Testi" → Soru ve model seçin → "Testi Başlat"
4. **Sonuçları İncele**: "Sonuçlar" bölümünden tüm yanıtları görüntüleyin

## ⚠️ Bilinen Sorunlar

- **429 Hatası (Gemini)**: Günlük kota aşıldı. Birkaç dakika bekleyin veya farklı model deneyin.
- **404 Hatası**: Model bulunamadı. `ai_services.py` dosyasından model listesini güncelleyin.


