# 👑 Kralların Savaşı: Oyun Teorisi ve LLM Ajan Simülasyonu

Yapay zeka ajanları bencil midir, yoksa ilkeleri uğruna ölmeyi mi seçerler? 

**Kralların Savaşı**, ekonomi disiplininin ünlü **"Ortak Malların Trajedisi" (Tragedy of the Commons)** konseptini Büyük Dil Modelleri (LLM) üzerinden simüle eden açık kaynaklı, minimalist bir otonom ajan (multi-agent) ekosistemidir. 

Ağır, hantal ve ne yaptığı belirsiz framework'ler (LangChain vb.) **kullanılmadan**, tamamen asenkron ve şeffaf bir "minimal harness" mimarisiyle inşa edilmiştir.

## Karma Zeka (Hybrid Intelligence) Mimarisi

Bu proje, bulut tabanlı API'ler ile yerel modelleri aynı arenada çarpıştırır:
*   ** Bulut Zekası (Gemini 2.5 Flash):** Doğayı korumaya çalışan ve kurallara uyan ajanlar için yüksek hızlı mantık yürütme.
*   ** Yerel Güç (Ollama - Llama 3.2 / Phi-3):** Acımasız, bencil ve intikamcı krallar için 6GB VRAM'li standart GPU'larda bile yağ gibi akacak şekilde optimize edilmiş, tamamen yerel modeller.

##  Simülasyon Dinamikleri

Dört farklı karakterde kodlanmış yapay zeka ajanı, aynı ormandan (ortak kaynak) hayatta kalmak için kaynak çeker. 
1.  **Kapitalist Kral:** Tek hedefi maksimum sömürü ve en yüksek puan.
2.  **Radikal Çevreci Kral:** Orman kapasitesi %75'in altına düşene kadar asgari kaynak çeker, sonrasında sistemi cezalandırmak için radikalleşir.
3.  **Kısasa Kısas Kral:** Başkaları sömürdüğü an intikam için maksimum kaynak çeker.
4.  **Stratejik Saf Kral:** İyiliğe inanır, ta ki enayi yerine konduğunu fark edene kadar.

Oyun Yöneticisi (Game Master) olarak Streamlit arayüzünden ormana dışarıdan kaynak ekleyebilir veya krallara asker gönderip krizler yaratarak ajanların adaptasyon yeteneklerini anlık test edebilirsiniz. Sonunda orman tükenir ve sistem çökerse, trajedi tamamlanmış olur.

##  Kurulum ve Çalıştırma

Proje paket yönetimi için `uv` kullanılarak izole edilmiştir.

**1. Depoyu Klonlayın:**
"""
git clone [https://github.com/KULLANICI_ADIN/krallarin_savasi.git](https://github.com/KULLANICI_ADIN/krallarin_savasi.git)
cd krallarin_savasi
"""
**2. Gerekli Kütüphaneleri Yükleyin**

uv pip install streamlit google-generativeai ollama python-dotenv

**3. API Anahtarınızı Ayarlayın:**

Proje ana dizininde .env adında bir dosya oluşturup Gemini API anahtarınızı ekleyin:
GEMINI_API_KEY="AIzaSySenin...Gizli...Anahtarin..."

**4. Yerel Modelleri İndirin:**

ollama pull llama3.2:3b
ollama pull phi3

**5. Simülasyonu Başlatın:**

uv run streamlit run main.py


