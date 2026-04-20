import pyperclip
from pynput import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import queue
import os
import re

try:
    from google import genai as google_genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False


# HATA SÖZLÜKLERİ - Basit Türkçe açıklamalar
HATA_SOZLUKLERI = {
    "csharp": {
        "CS1525": "Noktalı virgül (;) eksik veya yanlış yerde",
        "CS1002": "Satır sonunda noktalı virgül (;) eksik",
        "CS1513": "Kapanış süslü parantez (}) eksik",
        "CS1514": "Açılış süslü parantez ({) eksik",
        "CS0103": "Tanımlanmamış değişken kullanılmış",
        "CS0246": "Kütüphane/namespace bulunamadı",
        "CS0234": "Namespace içinde tip bulunamadı",
        "CS1061": "Olmayan metod/property çağrılmış",
        "CS0120": "Statik olmayan üyeye statik erişim",
        "CS0029": "Tip uyuşmazlığı",
        "CS0161": "Fonksiyon return değeri döndürmüyor",
        "CS0165": "Başlatılmamış değişken kullanılmış",
        "CS0019": "Operatör tip için geçersiz",
        "CS0106": "Erişim belirleyici yanlış",
        "CS0117": "Tip içinde tanımlı değil",
        "CS1001": "Tanımlayıcı (identifier) bekleniyor",
        "CS1026": "Kapanış parantezi ()) eksik",
        "CS1029": "Yanlış karakter",
        "CS1031": "Tür bekleniyor",
        "CS1043": "{ veya ; bekleniyor",
    },
    "python": {
        "SyntaxError": "Yazım hatası",
        "IndentationError": "Boşluk/indent hatası",
        "NameError": "Tanımlanmamış değişken/fonksiyon",
        "TypeError": "Tip uyuşmazlığı",
        "ValueError": "Geçersiz değer",
        "IndexError": "Dizi indeksi sınırlar dışında",
        "KeyError": "Sözlükte anahtar bulunamadı",
        "AttributeError": "Olmayan özellik/metod çağrısı",
        "ImportError": "Modül import edilemedi",
        "ModuleNotFoundError": "Modül bulunamadı",
        "ZeroDivisionError": "Sıfıra bölme hatası",
        "FileNotFoundError": "Dosya bulunamadı",
        "KeyboardInterrupt": "Program kullanıcı tarafından durduruldu",
    },
    "javascript": {
        "SyntaxError": "Yazım hatası",
        "ReferenceError": "Tanımlanmamış değişken",
        "TypeError": "Tip hatası",
        "RangeError": "Değer aralık dışında",
        "URIError": "URI hatası",
    },
    "typescript": {
        "SyntaxError": "Yazım hatası",
        "ReferenceError": "Tanımlanmamış değişken",
        "TypeError": "Tip hatası",
        "TS2304": "Tanımlanmamış isim",
        "TS2345": "Tip uyuşmazlığı",
        "TS2322": "Atama tip hatası",
    },
    "java": {
        "cannot find symbol": "Tanımlanmamış sembol",
        "expected": "Beklenen karakter eksik",
        "illegal start": "Geçersiz başlangıç",
        "class expected": "Sınıf bekleniyor",
        "variable might not have been initialized": "Değişken başlatılmamış",
    },
    "cpp": {
        "expected": "Beklenen karakter eksik",
        "undeclared": "Tanımlanmamış değişken",
        "was not declared": "Tanımlanmamış",
    },
}


# --- AYARLAR ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "qwen2.5:0.5b"  # Ana lokal model (F8) - CPU'da cok daha hizli
TEXT_MODEL_CANDIDATES = [
    "qwen2.5:0.5b",    # en hizli - CPU'da ~15 saniye
    "gemma3:1b",       # yedek
    MODEL_ADI,
]

CLOUD_MODEL_ADI = "gemini-3-flash-preview"  # Google Cloud Vertex AI modeli (F9)

KISAYOL_METIN = keyboard.Key.f8   # Lokal Ollama icin kisayol
KISAYOL_CLOUD = keyboard.Key.f9   # Google Cloud Gemini icin kisayol
KISAYOL_HATA = keyboard.Key.f10   # Kod hatasi aciklama kisayolu


# Global degiskenler
root = None
gui_queue = queue.Queue()
kisayol_basildi = False
cloud_kisayol_basildi = False
hata_kisayol_basildi = False


# --- MENU SECENEKLERI VE PROMPT'LAR ---
ISLEMLER = {
    "📝 Gramer Düzelt": "Bu metni Türkçe yazım ve dil bilgisi kurallarına göre düzelt, resmi ve akıcı olsun. Sadece sonucu ver.",
    "🇬🇧 İngilizceye Çevir": "Bu metni İngilizceye çevir. Sadece çeviriyi ver.",
    "🇹🇷 Türkçeye Çevir": "Bu metni Türkçeye çevir. Sadece çeviriyi ver.",
    "📑 Özetle (Madde Madde)": "Bu metni analiz et ve en önemli noktaları madde madde özetle.",
    "💼 Daha Resmi Yap": "Bu metni kurumsal bir e-posta diline çevir, çok resmi olsun.",
    "🐍 Python Koduna Çevir": "Bu metindeki isteği yerine getiren bir Python kodu yaz. Sadece kodu ver.",
    "📧 Cevap Yaz (Mail)": "Bu gelen bir e-posta, buna kibar ve profesyonel bir cevap metni taslağı yaz.",
    "🎮 PS5 Oyun Skor + Acımasız Yorum": (
        "Seçili metni bir PS5 oyunu adı olarak ele al. Aşağıdaki formatta Türkçe cevap ver:\n"
        "1) Oyun: <ad>\n"
        "2) Topluluk Beğeni Skorları:\n"
        "- Metacritic User Score: <değer veya 'bilgi yok'>\n"
        "- OpenCritic / benzer eleştirmen ortalaması: <değer veya 'bilgi yok'>\n"
        "- Oyuncu yorumu ortalaması (PS Store vb.): <değer veya 'bilgi yok'>\n"
        "3) Hüküm: sadece 'IYI' veya 'KOTU'\n"
        "4) Acımasız Yorum: 2-4 cümle, net ve sert.\n"
        "Kurallar: Kesin bilmediğin puanı uydurma, onun yerine 'bilgi yok' yaz. "
        "Yorumu skorlarla tutarlı kur."
    ),
    "🐞 Kod Hatasını Açıkla": (
        "Bu metin bir kod hatası veya hata mesajı içeriyor. Lütfen şunları yap:\n"
        "1) Hatayı basit Türkçe ile açıkla (teknik terimleri açıkla)\n"
        "2) Olası çözüm önerisi ver (kısa ve net)\n"
        "3) Hangi programlama dili olduğunu belirt\n\n"
        "Format:\n"
        "🔴 Hata: [hata adı/tipi]\n"
        "📝 Açıklama: [Türkçe açıklama]\n"
        "💡 Çözüm: [öneri]\n"
        "🌐 Dil: [programlama dili]"
    ),
}


def get_available_text_model():
    """Metin islemede kullanilabilir modeli secer."""
    preferred_models = []
    for model in TEXT_MODEL_CANDIDATES:
        if model and model not in preferred_models:
            preferred_models.append(model)

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return MODEL_ADI

        models = response.json().get("models", [])
        installed_lower = {m.get("name", "").lower(): m.get("name", "") for m in models}

        for candidate in preferred_models:
            candidate_lower = candidate.lower()
            if candidate_lower in installed_lower:
                return installed_lower[candidate_lower]

            candidate_base = candidate_lower.split(":")[0]
            for installed_name_lower, installed_name in installed_lower.items():
                if installed_name_lower.startswith(candidate_base + ":"):
                    return installed_name
    except Exception:
        pass

    return MODEL_ADI


def ollama_cevap_al(prompt):
    """Ollama API'den streaming modunda cevap al."""
    try:
        aktif_model = get_available_text_model()
        payload = {
            "model": aktif_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 400,
                "num_ctx": 1024,
            },
        }

        parcalar = []
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30) as response:
            if response.status_code != 200:
                err_msg = (
                    f"Ollama API Hatası: {response.status_code}\n"
                    f"Model: {aktif_model}\n"
                    f"Cevap: {response.text}"
                )
                print(f"❌ {err_msg}")
                gui_queue.put((messagebox.showerror, ("API Hatası", err_msg)))
                return None

            import json as _json
            for satir in response.iter_lines():
                if satir:
                    try:
                        veri = _json.loads(satir.decode("utf-8"))
                        parcalar.append(veri.get("response", ""))
                        if veri.get("done"):
                            break
                    except Exception:
                        continue

        return "".join(parcalar).strip()

    except requests.exceptions.ConnectionError:
        err_msg = (
            "Ollama'ya bağlanılamadı.\n"
            "Programın çalıştığından emin olun!\n"
            "(http://localhost:11434)"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Bağlantı Hatası", err_msg)))
        return None
    except Exception as e:
        err_msg = f"Beklenmeyen Hata: {e}"
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Hata", err_msg)))
        return None


def gemini_cevap_al(prompt):
    """Google Cloud Vertex AI - Gemini 3 Flash Preview ile cevap al."""
    if not GOOGLE_GENAI_AVAILABLE:
        err_msg = (
            "google-genai paketi kurulu degil.\n"
            "Terminalde su komutu calistirin:\n"
            "pip install --upgrade google-genai"
        )
        gui_queue.put((messagebox.showerror, ("Paket Eksik", err_msg)))
        return None

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "")

    if not project or use_vertex.upper() != "TRUE":
        err_msg = (
            "Google Cloud ortam degiskenleri ayarli degil!\n\n"
            "PowerShell'de su komutlari calistirin:\n"
            "$env:GOOGLE_CLOUD_PROJECT=\"YOUR_PROJECT_ID\"\n"
            "$env:GOOGLE_CLOUD_LOCATION=\"global\"\n"
            "$env:GOOGLE_GENAI_USE_VERTEXAI=\"True\"\n\n"
            "Ayrica 'gcloud auth application-default login' gerekli."
        )
        gui_queue.put((messagebox.showerror, ("Kimlik Hatası", err_msg)))
        return None

    try:
        client = google_genai.Client()
        response = client.models.generate_content(
            model=CLOUD_MODEL_ADI,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        err_msg = (
            f"Gemini API Hatası: {e}\n\n"
            "Kontrol listesi:\n"
            "- Billing acik mi?\n"
            "- Vertex AI API aktif mi? (aiplatform.googleapis.com)\n"
            "- IAM rolü: roles/aiplatform.user\n"
            "- gcloud auth application-default login yapildi mi?"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Gemini Hatası", err_msg)))
        return None


def hata_parser_basit(hata_metni, dil_kodu):
    """Basit regex/string parsing ile hata analizi yapar."""
    sonuclar = []
    
    # YENİ: Önce kritik kütüphane/bağımlılık hatalarını kontrol et
    kutuphane_raporu = kutuphane_cakismasi_analiz(hata_metni, dil_kodu)
    if kutuphane_raporu:
        return [{"tip": "kutuphane_raporu", "rapor": kutuphane_raporu}]
    
    # Pattern: dosya.cs(18,8): error CS1525: mesaj
    pattern = r'(\w+\.\w+)\((\d+),(\d+)\):\s*(?:error|warning)\s+(\w+):\s*(.+)'
    
    for satir in hata_metni.split('\n'):
        match = re.search(pattern, satir)
        if match:
            dosya, satir_no, kolon, hata_kodu, mesaj = match.groups()
            aciklama = hata_aciklama_bul(hata_kodu, mesaj, dil_kodu)
            sonuclar.append({
                'dosya': dosya,
                'satir': satir_no,
                'kolon': kolon,
                'hata_kodu': hata_kodu,
                'mesaj': mesaj.strip(),
                'aciklama': aciklama
            })
    
    return sonuclar


def kutuphane_cakismasi_analiz(hata_metni, dil_kodu):
    """
    Kritik kütüphane çakışmaları, eski sürüm kullanımı ve bağımlılık hatalarını analiz eder.
    Hocanın istediği 'silip tekrar yükle' raporunu üretir.
    """
    metin_lower = hata_metni.lower()
    
    # 1. PYTHON - Modül bulunamadı / Import hatası
    if dil_kodu == "python":
        # ModulNotFoundError veya ImportError
        if "modulenotfounderror" in metin_lower or "importerror" in metin_lower or "no module named" in metin_lower:
            # Hangi modül olduğunu bul
            modul_match = re.search(r"no module named ['\"]([^'\"]+)['\"]", metin_lower)
            if not modul_match:
                modul_match = re.search(r"modulenotfounderror: no module named ['\"]?([^'\"\s]+)['\"]?", metin_lower)
            
            modul_adi = modul_match.group(1) if modul_match else "[modül_adı]"
            
            return (
                f"⚠️ EKSİK KÜTÜPHANE TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"'{modul_adi}' kütüphanesi sistemde kurulu değil veya Python tarafından bulunamıyor.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Kodunuzda `import {modul_adi}` veya `from {modul_adi} import ...` şeklinde\n"
                f"bir kullanım var ancak bu kütüphane sanal ortamınızda (venv) yok.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. pip uninstall {modul_adi} -y\n"
                f"2. pip install {modul_adi} --upgrade\n\n"
                f"💡 EK NOT:\n"
                f"Eğer sanal ortam (venv) kullanıyorsanız, önce ortamı aktif edin:\n"
                f"   .venv\\Scripts\\activate"
            )
        
        # Sürüm çakışması - pip dependency resolver
        if "resolutionimpossible" in metin_lower or "cannot install" in metin_lower or "incompatible" in metin_lower:
            return (
                f"⚠️ KÜTÜPHANE SÜRÜM ÇAKIŞMASI TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"Projedeki kütüphanelerin sürümleri birbiriyle uyumsuz.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Bazı paketler belirli sürüm aralıklarında çalışırken, diğerleri\n"
                f"farklı sürümler gerektiriyor. pip çözümleyici bu çakışmayı çözemiyor.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. pip freeze > requirements_backup.txt\n"
                f"2. pip uninstall -r requirements.txt -y\n"
                f"3. pip cache purge\n"
                f"4. pip install -r requirements.txt\n\n"
                f"💡 EK NOT:\n"
                f"Eğer sorun devam ederse, requirements.txt'deki sürüm kısıtlamalarını\n"
                f"geçici olarak kaldırıp sadece paket adlarını bırakın."
            )
    
    # 2. JAVASCRIPT / TYPESCRIPT - npm/yarn çakışmaları
    if dil_kodu in ["javascript", "typescript"]:
        if "eresolve" in metin_lower or "peer dependency" in metin_lower or "conflict" in metin_lower:
            return (
                f"⚠️ NPM KÜTÜPHANE ÇAKIŞMASI TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"node_modules klasöründe paket sürümleri çakışıyor.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Bazı paketler aynı bağımlılığın farklı sürümlerini gerektiriyor.\n"
                f"npm/yarn bu çakışmayı çözemiyor.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. rm -rf node_modules package-lock.json\n"
                f"2. npm cache clean --force\n"
                f"3. npm install\n\n"
                f"💡 EK NOT:\n"
                f"Eğer sorun devam ederse '--legacy-peer-deps' flag'i deneyin:\n"
                f"   npm install --legacy-peer-deps"
            )
        
        if "cannot find module" in metin_lower or "module not found" in metin_lower:
            modul_match = re.search(r"cannot find module ['\"]([^'\"]+)['\"]", metin_lower)
            modul_adi = modul_match.group(1) if modul_match else "[modül_adı]"
            
            return (
                f"⚠️ EKSİK NPM PAKETİ TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"'{modul_adi}' paketi node_modules'da bulunamıyor.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Kodda bu paket import edilmiş ama kurulumu eksik veya\n"
                f"package.json'da tanımlı değil.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. npm uninstall {modul_adi}\n"
                f"2. npm install {modul_adi} --save\n\n"
                f"💡 EK NOT:\n"
                f"Eğer global paketse: npm install -g {modul_adi}"
            )
    
    # 3. C# - NuGet paket çakışmaları
    if dil_kodu == "csharp":
        if "nuget" in metin_lower or "package restore" in metin_lower or "unable to find" in metin_lower:
            return (
                f"⚠️ NUGET PAKET SORUNU TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"NuGet paketleri yüklenemiyor veya çakışıyor.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Proje dosyasındaki (csproj) paket referanslarında\n"
                f"sürüm uyumsuzluğu veya eksik paket var.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. dotnet clean\n"
                f"2. rmdir /s /q bin obj\n"
                f"3. dotnet restore --force\n"
                f"4. dotnet build\n\n"
                f"💡 EK NOT:\n"
                f"Eğer sorun devam ederse NuGet önbelleğini temizleyin:\n"
                f"   dotnet nuget locals all --clear"
            )
    
    # 4. JAVA - Maven/Gradle çakışmaları
    if dil_kodu == "java":
        if "maven" in metin_lower or "gradle" in metin_lower or "dependency" in metin_lower:
            return (
                f"⚠️ MAVEN/GRADLE BAĞIMLILIK SORUNU TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"Java bağımlılıklarında çakışma veya eksik kütüphane var.\n\n"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"pom.xml (Maven) veya build.gradle dosyasında tanımlı\n"
                f"paketler çakışıyor veya indirilemiyor.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"MAVEN için:\n"
                f"1. mvn clean\n"
                f"2. rmdir /s /q target\n"
                f"3. mvn dependency:purge-local-repository\n"
                f"4. mvn install\n\n"
                f"GRADLE için:\n"
                f"1. gradle clean\n"
                f"2. rmdir /s /q build .gradle\n"
                f"3. gradle build --refresh-dependencies"
            )
    
    return None


def hata_aciklama_bul(hata_kodu, hata_mesaji, dil_kodu):
    """Hata koduna veya mesajına göre basit Türkçe açıklama bulur."""
    
    # Önce hata koduna bak
    dil_sozlugu = HATA_SOZLUKLERI.get(dil_kodu, {})
    aciklama = dil_sozlugu.get(hata_kodu)
    if aciklama:
        return aciklama
    
    # Mesaj içeriğine göre bul
    mesaj_lower = hata_mesaji.lower()
    
    if 'unexpected symbol' in mesaj_lower or 'unexpected token' in mesaj_lower:
        return "Beklenmeyen karakter - noktalı virgül eksik olabilir"
    elif 'expected' in mesaj_lower:
        if ';' in mesaj_lower:
            return "Noktalı virgül (;) eksik"
        elif '}' in mesaj_lower:
            return "Kapanış süslü parantez (}) eksik"
        elif ')' in mesaj_lower:
            return "Kapanış parantezi ()) eksik"
        elif '{' in mesaj_lower:
            return "Açılış süslü parantez ({) eksik"
        elif '(' in mesaj_lower:
            return "Açılış parantezi (() eksik"
    elif 'does not exist' in mesaj_lower or 'not found' in mesaj_lower or 'undeclared' in mesaj_lower:
        return "Tanımlanmamış değişken/fonksiyon kullanılmış"
    elif 'cannot find' in mesaj_lower:
        return "Bulunamadı - yanlış isim veya eksik import"
    
    return "Sözdizimi hatası"


def hata_analiz_et(secili_metin, dil_kodu, kullan_cloud=False):
    """Basit parser ve çakışma analizi ile hata raporlama."""
    
    dil_isimleri = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "csharp": "C#",
        "cpp": "C/C++",
        "html": "HTML/CSS",
        "php": "PHP",
        "rust": "Rust",
        "go": "Go",
    }
    dil_adi = dil_isimleri.get(dil_kodu, dil_kodu)
    
    # Parser çalıştır (önce kritik kütüphane hatalarını kontrol eder)
    hatalar = hata_parser_basit(secili_metin, dil_kodu)
    
    # Eğer kütüphane raporu döndüyse, onu göster
    if hatalar and len(hatalar) > 0 and hatalar[0].get("tip") == "kutuphane_raporu":
        rapor = hatalar[0].get("rapor", "")
        cikti = f"🌐 Dil: {dil_adi}\n\n{rapor}"
        gui_queue.put((sonuc_penceresi_goster, (f"🐞 {dil_adi} Kritik Hata Raporu", cikti)))
        print(f"✅ {dil_adi} kritik hata analizi tamamlandı.")
        return
    
    # Normal syntax hataları
    if not hatalar:
        cikti = f"🌐 Dil: {dil_adi}\n\n"
        cikti += "⚠️ Hata formatı tanınamadı.\n"
        cikti += "📝 Seçili metin:\n"
        cikti += secili_metin[:200] + "..." if len(secili_metin) > 200 else secili_metin
    else:
        cikti = f"🌐 Dil: {dil_adi}\n"
        cikti += f"📊 {len(hatalar)} hata bulundu\n\n"
        
        for i, hata in enumerate(hatalar, 1):
            cikti += f"🔴 HATA #{i}\n"
            cikti += f"📍 {hata['dosya']} - Satır {hata['satir']}\n"
            cikti += f"❌ {hata['aciklama']}\n"
            cikti += f"💻 Kod: {hata['hata_kodu']}\n\n"
    
        cikti += "\n💡 İpucu: Belirtilen satırları kontrol edin."
    
    gui_queue.put((sonuc_penceresi_goster, (f"🐞 {dil_adi} Hata Analizi", cikti)))
    print(f"✅ {dil_adi} hata analizi tamamlandı.")


def ollama_hata_cevap_al(prompt):
    """Hata analizi için optimize edilmiş Ollama çağrısı - kısa ve öz."""
    try:
        aktif_model = get_available_text_model()
        payload = {
            "model": aktif_model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,      # Çok deterministik
                "top_p": 0.7,
                "num_predict": 180,      # Max 180 token (kısa cevap)
                "num_ctx": 1024,
            },
        }

        parcalar = []
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=30) as response:
            if response.status_code != 200:
                return None

            import json as _json
            for satir in response.iter_lines():
                if satir:
                    try:
                        veri = _json.loads(satir.decode("utf-8"))
                        parcalar.append(veri.get("response", ""))
                        if veri.get("done"):
                            break
                    except Exception:
                        continue

        return "".join(parcalar).strip()

    except Exception:
        return None


def strip_code_fence(text):
    if not text:
        return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines else []
        while lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def secili_metni_kopyala(max_deneme=4):
    sentinel = f"__AI_ASISTAN__{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    for _ in range(max_deneme):
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        metin = pyperclip.paste()
        if metin and metin.strip() and metin != sentinel:
            return metin
    return ""


def pencere_modunda_gosterilsin_mi(komut_adi):
    return "PS5 Oyun Skor" in komut_adi


def sonuc_penceresi_goster(baslik, icerik):
    pencere = tk.Toplevel(root)
    pencere.title(baslik)
    pencere.geometry("780x520")
    pencere.minsize(520, 320)
    pencere.attributes("-topmost", True)

    frame = tk.Frame(pencere, bg="#1f1f1f")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    text_alani = tk.Text(
        frame,
        wrap="word",
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        font=("Segoe UI", 10),
        padx=10,
        pady=10,
    )
    kaydirma = tk.Scrollbar(frame, command=text_alani.yview)
    text_alani.configure(yscrollcommand=kaydirma.set)

    text_alani.pack(side="left", fill="both", expand=True)
    kaydirma.pack(side="right", fill="y")

    text_alani.insert("1.0", icerik)
    text_alani.config(state="disabled")

    alt_frame = tk.Frame(pencere, bg="#1f1f1f")
    alt_frame.pack(fill="x", padx=10, pady=(0, 10))

    def panoya_kopyala():
        pyperclip.copy(icerik)

    tk.Button(
        alt_frame,
        text="Panoya Kopyala",
        command=panoya_kopyala,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left")

    tk.Button(
        alt_frame,
        text="Kapat",
        command=pencere.destroy,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="right")

    pencere.focus_force()
    pencere.lift()


def islemi_yap(komut_adi, secili_metin, kullan_cloud=False):
    prompt_emri = ISLEMLER[komut_adi]
    full_prompt = f"{prompt_emri}:\n\n'{secili_metin}'"

    kaynak = "☁️ Gemini Cloud" if kullan_cloud else "🖥️ Ollama Lokal"
    print(f"🤖 İşlem: {komut_adi} [{kaynak}]")
    print("⏳ İşleniyor...")

    if kullan_cloud:
        sonuc = gemini_cevap_al(full_prompt)
    else:
        sonuc = ollama_cevap_al(full_prompt)

    if not sonuc:
        print("❌ Sonuç alınamadı.")
        return

    sonuc = strip_code_fence(sonuc)
    if sonuc.startswith("'") and sonuc.endswith("'"):
        sonuc = sonuc[1:-1]

    if pencere_modunda_gosterilsin_mi(komut_adi):
        gui_queue.put((sonuc_penceresi_goster, (komut_adi, sonuc)))
        print("✅ Sonuç ayrı pencerede gösterildi.")
        return

    time.sleep(0.2)
    pyperclip.copy(sonuc)
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    print("✅ İşlem tamamlandı!")


def process_queue():
    """Kuyruktaki GUI islemlerini ana thread'de calistirir."""
    try:
        while True:
            try:
                task = gui_queue.get_nowait()
            except queue.Empty:
                break
            func, args = task
            func(*args)
    finally:
        if root:
            root.after(100, process_queue)


def menu_goster(kullan_cloud=False):
    """Metni kopyalar ve menuyu gosterir (ana thread)."""
    secili_metin = secili_metni_kopyala()
    if not secili_metin.strip():
        gui_queue.put(
            (
                messagebox.showwarning,
                (
                    "Secim Bulunamadi",
                    "Lutfen once metin secin, sonra kisayol ile menuyu acin.",
                ),
            )
        )
        return

    etiket = "☁️ Gemini Cloud" if kullan_cloud else "🖥️ Ollama Lokal"
    menu = tk.Menu(
        root,
        tearoff=0,
        bg="#2b2b2b",
        fg="white",
        activebackground="#4a4a4a",
        activeforeground="white",
        font=("Segoe UI", 10),
    )

    menu.add_command(
        label=f"── {etiket} ──",
        state="disabled",
        foreground="#888888",
    )

    def komut_olustur(k_adi, s_metin, cloud):
        def komut_calistir():
            threading.Thread(
                target=islemi_yap, args=(k_adi, s_metin, cloud), daemon=True
            ).start()
        return komut_calistir

    for baslik in ISLEMLER.keys():
        menu.add_command(
            label=baslik,
            command=komut_olustur(baslik, secili_metin, kullan_cloud),
        )

    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def dil_secim_menu_goster(secili_metin):
    """Hata analizi için programlama dili seçimi menüsü."""
    diller = {
        "🐍 Python": "python",
        "📜 JavaScript": "javascript",
        "🔷 TypeScript": "typescript",
        "☕ Java": "java",
        "🔷 C#": "csharp",
        "🔧 C/C++": "cpp",
        "🌐 HTML/CSS": "html",
        "🐘 PHP": "php",
        "🦀 Rust": "rust",
        "🎯 Go": "go",
    }
    
    menu = tk.Menu(
        root,
        tearoff=0,
        bg="#2b2b2b",
        fg="white",
        activebackground="#4a4a4a",
        activeforeground="white",
        font=("Segoe UI", 10),
    )

    menu.add_command(
        label="── Programlama Dili Seç ──",
        state="disabled",
        foreground="#888888",
    )

    def dil_secildi(dil_adi, dil_kodu):
        def handler():
            gui_queue.put((hata_ai_menu_goster, (secili_metin, dil_kodu)))
        return handler

    for dil_adi, dil_kodu in diller.items():
        menu.add_command(
            label=f"  {dil_adi}",
            command=dil_secildi(dil_adi, dil_kodu),
        )

    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def hata_ai_menu_goster(secili_metin, dil_kodu):
    """Dil seçildikten sonra Lokal/Cloud AI seçimi."""
    menu = tk.Menu(
        root,
        tearoff=0,
        bg="#2b2b2b",
        fg="white",
        activebackground="#4a4a4a",
        activeforeground="white",
        font=("Segoe UI", 10),
    )

    dil_isimleri = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "csharp": "C#",
        "cpp": "C/C++",
        "html": "HTML/CSS",
        "php": "PHP",
        "rust": "Rust",
        "go": "Go",
    }
    dil_adi = dil_isimleri.get(dil_kodu, dil_kodu.upper())

    menu.add_command(
        label=f"── 🐞 {dil_adi} Hatası ──",
        state="disabled",
        foreground="#888888",
    )

    def hata_analiz_cloud():
        threading.Thread(
            target=hata_analiz_et, args=(secili_metin, dil_kodu, True), daemon=True
        ).start()

    def hata_analiz_local():
        threading.Thread(
            target=hata_analiz_et, args=(secili_metin, dil_kodu, False), daemon=True
        ).start()

    menu.add_command(
        label="🖥️  Lokal AI ile Açıkla",
        command=hata_analiz_local,
    )
    menu.add_command(
        label="☁️  Cloud AI ile Açıkla",
        command=hata_analiz_cloud,
    )
    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def hata_menu_goster():
    """Hata analizi için önce dil seçimi menüsünü gösterir."""
    secili_metin = secili_metni_kopyala()
    if not secili_metin.strip():
        gui_queue.put(
            (
                messagebox.showwarning,
                (
                    "Seçim Bulunamadı",
                    "Lütfen önce hata mesajını veya kodunu seçin, sonra F10'a basın.",
                ),
            )
        )
        return

    # Önce dil seçimi menüsünü göster
    gui_queue.put((dil_secim_menu_goster, (secili_metin,)))
    menu.add_command(
        label="☁️  Cloud AI ile Açıkla",
        command=hata_analiz_cloud,
    )
    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def on_press(key):
    global kisayol_basildi, cloud_kisayol_basildi, hata_kisayol_basildi
    try:
        if key == KISAYOL_METIN and not kisayol_basildi:
            kisayol_basildi = True
            gui_queue.put((menu_goster, (False,)))
        elif key == KISAYOL_CLOUD and not cloud_kisayol_basildi:
            cloud_kisayol_basildi = True
            gui_queue.put((menu_goster, (True,)))
        elif key == KISAYOL_HATA and not hata_kisayol_basildi:
            hata_kisayol_basildi = True
            gui_queue.put((hata_menu_goster, ()))
    except AttributeError:
        pass


def on_release(key):
    global kisayol_basildi, cloud_kisayol_basildi, hata_kisayol_basildi
    try:
        if key == KISAYOL_METIN:
            kisayol_basildi = False
        elif key == KISAYOL_CLOUD:
            cloud_kisayol_basildi = False
        elif key == KISAYOL_HATA:
            hata_kisayol_basildi = False
    except AttributeError:
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Asistan - Metin İşleme")
    print("=" * 60)
    aktif_text_model = get_available_text_model()
    print(f"📦 Lokal Model (F8): {aktif_text_model}")
    print(f"☁️  Cloud Model  (F9): {CLOUD_MODEL_ADI} [Vertex AI]")
    print()
    print("🔧 Kullanım:")
    print("   F8  - Lokal Ollama ile AI işlemi")
    print("   F9  - Google Cloud Gemini 3 ile AI işlemi")
    print("   F10 - Kod hatasını AI ile açıkla")
    print()
    print("⚠️ Programı kapatmak için bu pencereyi kapatın veya Ctrl+C yapın.")
    print("=" * 60)

    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code == 200:
            print("✅ Ollama bağlantısı başarılı!")
        else:
            print("⚠️ Ollama'ya bağlanılamadı, servisi kontrol edin!")
    except Exception:
        print("⚠️ Ollama çalışmıyor olabilir! 'ollama serve' ile başlatın.")

    if GOOGLE_GENAI_AVAILABLE:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        if project:
            print(f"✅ Google Cloud projesi: {project}")
        else:
            print("⚠️ GOOGLE_CLOUD_PROJECT ayarlı değil — F9 çalışmayacak.")
    else:
        print("⚠️ google-genai kurulu değil — F9 çalışmayacak.")

    print()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    root = tk.Tk()
    root.withdraw()
    root.after(100, process_queue)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Kapatılıyor...")
