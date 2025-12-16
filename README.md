# 🐟 LimiX – Version 2.1 (Current)  
## AI + IoT Smart Fish Farm with Disease Detection

### 📌 Overview
النسخة الأحدث من **Limix** — نظام متكامل يجمع بين **المراقبة البيئية**، **توصية نوع السمك**، و**كشف الأمراض** من صور الأسماك باستخدام **رؤية حاسوبية**.

### 🧠 المميزات الكاملة
#### 1. **المراقبة البيئية** (من الإصدار 1.0)
- pH, DO, Temperature, Turbidity, EC, Ammonia — تحديث كل 10 ثواني

#### 2. **توصية نوع السمك** (من الإصدار 2.0)
- تصنيف ذكي بناءً على جودة المياه

#### 3. **كشف الأمراض** (جديد في 2.1)
- ✅ **نموذج رؤية حاسوبية** (EfficientNet-B3)
- يصنّف الصورة إلى: `FreshFish` أو `InfectedFish`
- دقة عالية (تم اختبارها على صور واقعية)
- API مخصص: `POST /api/ai/health-check`

### 📡 البنية التقنية
- **Backend**: Flask (Python)
- **AI Models**: 
  - `fish_type_model.joblib` (Scikit-learn)
  - `fish_disease.pth` (PyTorch + EfficientNet-B3)
- **Cloud**: Firebase Realtime Database
- **Hardware**: ESP32 (في الانتظار للتكامل الكامل)
- **Mobile**: Flutter (قيد التطوير)

### 🚀 How to Use
```bash
# Install
pip install -r requirements.txt

# Run API only
python run.py api

# Run everything (simulator + listener + API)
python run.py all
