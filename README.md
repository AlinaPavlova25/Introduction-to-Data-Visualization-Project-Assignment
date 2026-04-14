# AI Asistan - Metin İşleme ve Kod Hata Analizi

Windows için sistem çapında çalışan AI destekli metin işleme ve kod hata analizi aracı.

## Özellikler

### 1. Metin İşleme (F8 / F9)
Seçili metin üzerinde çeşitli AI işlemleri:
- 📝 Gramer Düzelt
- 🇬🇧 İngilizceye Çevir  
- 🇹🇷 Türkçeye Çevir
- 📑 Özetle (Madde Madde)
- 💼 Daha Resmi Yap
- 🐍 Python Koduna Çevir
- 📧 Cevap Yaz (Mail)
- 🎮 PS5 Oyun Skor + Acımasız Yorum
- 🐞 **Kod Hatasını Açıkla** (Yeni!)

**Kısayollar:**
- `F8` - Lokal Ollama AI ile işlem
- `F9` - Google Cloud Gemini AI ile işlem

### 2. Kod Hata Analizi (F10) - YENİ!

Derleme hatalarını anında Türkçe olarak açıklar. AI bekleme süresi olmadan, regex tabanlı parser ile çalışır.

**Desteklenen Diller:**
- 🐍 Python
- 📜 JavaScript
- 🔷 TypeScript
- ☕ Java
- 🔷 C#
- 🔧 C/C++
- 🌐 HTML/CSS
- 🐘 PHP
- 🦀 Rust
- 🎯 Go

**Kullanım:**
1. VS Code veya herhangi bir editörde hata mesajını seçin
2. `F10` tuşuna basın
3. Programlama dilini seçin
4. Hata anında analiz edilir ve Türkçe açıklama gösterilir

**Örnek Çıktı:**
```
🌐 Dil: C#
📊 2 hata bulundu

🔴 HATA #1
📍 main.cs - Satır 18
❌ Noktalı virgül (;) eksik veya yanlış yerde
💻 Kod: CS1525

🔴 HATA #2
📍 main.cs - Satır 33
❌ Satır sonunda noktalı virgül (;) eksik
💻 Kod: CS1002

💡 İpucu: Belirtilen satırları kontrol edin.
```

## Kurulum

### Gereksinimler
- Windows 10/11
- Python 3.12+
- Ollama (lokal AI için)
- Google Cloud hesabı (opsiyonel, Gemini için)

### Adımlar

1. **Ollama'yı kurun:**
   ```powershell
   # https://ollama.com/download adresinden indirin
   # Kurulumdan sonra:
   ollama pull qwen2.5:0.5b
   ```

2. **Projeyi klonlayın:**
   ```powershell
   git clone https://github.com/kullaniciadi/proje-adi.git
   cd proje-adi
   ```

3. **BASLAT.bat çalıştırın:**
   ```powershell
   .\BASLAT.bat
   ```
   
   Bu komut otomatik olarak:
   - Python sanal ortamı (.venv) oluşturur
   - Gerekli paketleri kurar
   - Uygulamayı arka planda başlatır

### Google Cloud Gemini (Opsiyonel)

F9 kısayolu ile Gemini kullanmak için:

```powershell
# gcloud CLI kurulumu
# https://cloud.google.com/sdk/docs/install

# Kimlik doğrulama
gcloud auth application-default login

# Ortam değişkenleri
$env:GOOGLE_CLOUD_PROJECT="proje-id"
$env:GOOGLE_CLOUD_LOCATION="global"
$env:GOOGLE_GENAI_USE_VERTEXAI="True"
```

## Proje Yapısı

```
.
├── main.pyw              # Ana uygulama
├── BASLAT.bat            # Başlatma scripti
├── kurulum.bat           # Kurulum scripti
├── requirements.txt      # Python bağımlılıkları
└── README.md            # Bu dosya
```

## Teknik Detaylar

### Hata Analizi Sistemi

F10 ile çalışan hata analizi, AI yerine **regex tabanlı parser** kullanır:

- **Hız:** Anında sonuç (AI bekleme süresi yok)
- **Doğruluk:** Hata kodu eşleştirme (CS1525 → "Noktalı virgül eksik")
- **Dil Desteği:** C#, Python, JS/TS, Java, C++ için özel hata sözlükleri

**Parser Mantığı:**
```python
# main.cs(18,8): error CS1525: Unexpected symbol `Console'
# ↓ parse ↓
# dosya: main.cs, satır: 18, hata_kodu: CS1525
# ↓ sözlük lookup ↓  
# "Noktalı virgül (;) eksik veya yanlış yerde"
```

### AI Modelleri

| Model | Kullanım | Hız |
|-------|----------|-----|
| `qwen2.5:0.5b` | Lokal (F8) | ~15 sn |
| `gemini-3-flash-preview` | Cloud (F9) | ~3 sn |

## Kullanılan Teknolojiler

- **Python 3.12** - Ana dil
- **Tkinter** - GUI menüleri
- **pynput** - Global kısayol dinleyici
- **pyautogui** - Klavye/mouse simülasyonu
- **requests** - Ollama API iletişimi
- **google-genai** - Gemini API (opsiyonel)

## Lisans

MIT License

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request açın

## Sorun Giderme

### Ollama bağlanamıyor
```powershell
# Ollama servisinin çalıştığından emin olun
ollama serve

# Modelin indirildiğini kontrol edin
ollama list
```

### Google Cloud 403 hatası
- Billing hesabının aktif olduğundan emin olun
- Vertex AI API'nin etkinleştirildiğini kontrol edin
- IAM rolü: `roles/aiplatform.user`

### F10 çalışmıyor
- Uygulamanın arka planda çalıştığını kontrol edin
- Başka bir uygulama F10'u kullanıyor olabilir
- Uygulamayı yeniden başlatın

## Yazar

- GitHub: [@kullaniciadi](https://github.com/kullaniciadi)

## Teşekkürler

- [Ollama](https://ollama.com/) - Lokal LLM çalıştırma
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Cloud AI
