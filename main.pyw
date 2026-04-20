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
import subprocess

try:
    from google import genai as google_genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False


# HATA SÖZLÜKLERİ - Basit Türkçe açıklamalar
HATA_SOZLUKLERI = {
    "csharp": {
        # Sozdizimi / noktali virgul / parantez
        "CS1002": "Satır sonunda noktalı virgül (;) eksik",
        "CS1003": "Sözdizimi hatası, beklenen karakter eksik",
        "CS1001": "Tanımlayıcı (identifier) bekleniyor",
        "CS1026": "Kapanış parantezi ()) eksik",
        "CS1513": "Kapanış süslü parantez (}) eksik",
        "CS1514": "Açılış süslü parantez ({) eksik",
        "CS1525": "Noktalı virgül (;) eksik veya yanlış yerde",
        "CS1519": "Geçersiz token (sınıf/yapı içinde yanlış sözdizimi)",
        "CS1520": "Metodun dönüş tipi (return type) eksik",
        "CS1528": "Bekleniyor: ; veya =",
        "CS1031": "Tür (type) bekleniyor",
        "CS1043": "{ veya ; bekleniyor",
        "CS1029": "Geçersiz ön-işleyici (preprocessor) yönergesi",
        # Isim / erisim hatalari
        "CS0103": "Tanımlanmamış değişken/fonksiyon kullanılmış",
        "CS0246": "Kütüphane/namespace bulunamadı (using eksik olabilir)",
        "CS0234": "Namespace içinde tip bulunamadı",
        "CS1061": "Olmayan metod veya property çağrılmış",
        "CS0117": "Tip içinde böyle bir üye tanımlı değil",
        "CS0122": "Koruma seviyesi yüzünden üyeye erişilemiyor (private/internal)",
        "CS0128": "Aynı isimde değişken zaten tanımlanmış",
        "CS0136": "Bu kapsamda aynı isim kullanılamaz (dış değişkenle çakışıyor)",
        "CS0108": "Üye üst sınıftaki üyeyi gizliyor (new anahtarı kullan)",
        # Tip uyusmazligi / donusum
        "CS0019": "Operatör verilen tiplere uygulanamaz",
        "CS0029": "Tip uyuşmazlığı (örtük dönüşüm yok)",
        "CS0266": "Örtük dönüşüm yok, açık cast gerekiyor",
        "CS1503": "Argüman tipi beklenen tipe uymuyor",
        "CS0411": "Jenerik tip argümanları çıkarılamadı",
        "CS0305": "Jenerik tip N adet tip argümanı istiyor",
        "CS0428": "Metod grubu delegate'e atanıyor, çağrı parantezi eksik olabilir",
        # Return / akis
        "CS0161": "Fonksiyon her yolda return yapmıyor",
        "CS0165": "Başlatılmamış (atanmamış) değişken kullanılmış",
        "CS0162": "Ulaşılamayan kod (unreachable) tespit edildi",
        "CS0168": "Değişken tanımlandı ama hiç kullanılmadı",
        "CS0219": "Değişkene atama yapıldı ama hiç okunmadı",
        # Sinif / miras
        "CS0106": "Erişim belirleyici bu üye için geçersiz",
        "CS0120": "Statik olmayan üyeye statik erişim (örnek gerekiyor)",
        "CS0050": "Erişim tutarsızlığı (metod imzası tipden daha gizli)",
        "CS0052": "Erişim tutarsızlığı (alanın tipi daha gizli)",
        "CS0506": "Virtual olmayan üye override edilemez",
        "CS0507": "Override ederken erişim seviyesi değiştirilemez",
        "CS0535": "Interface'in tüm üyeleri uygulanmamış",
        "CS0619": "Üye obsolete (kullanımdan kaldırıldı) olarak işaretli",
        "CS0660": "== tanımlı ama Equals override edilmemiş",
        "CS7036": "Zorunlu parametreye argüman verilmemiş",
        # Async
        "CS4033": "await yalnızca async metod içinde kullanılabilir",
        "CS4001": "'System.Void' await edilemez",
        # Foreach / indexleme
        "CS1579": "foreach için tip GetEnumerator uygulamıyor",
        "CS0021": "Bu tipe köşeli parantez ile indeks uygulanamaz",
        "CS0200": "Sadece okunur (read-only) property'ye atama yapılamaz",
    },
    "python": {
        "SyntaxError": "Yazım hatası",
        "IndentationError": "Boşluk/indent hatası",
        "TabError": "Tab ve boşluk karışmış",
        "NameError": "Tanımlanmamış değişken/fonksiyon",
        "UnboundLocalError": "Yerel değişken atanmadan kullanıldı",
        "TypeError": "Tip uyuşmazlığı",
        "ValueError": "Geçersiz değer",
        "IndexError": "Dizi indeksi sınırlar dışında",
        "KeyError": "Sözlükte anahtar bulunamadı",
        "AttributeError": "Olmayan özellik/metod çağrısı",
        "ImportError": "Modül import edilemedi",
        "ModuleNotFoundError": "Modül bulunamadı",
        "ZeroDivisionError": "Sıfıra bölme hatası",
        "FloatingPointError": "Kayan noktalı sayı aritmetik hatası",
        "FileNotFoundError": "Dosya bulunamadı",
        "FileExistsError": "Dosya zaten var",
        "PermissionError": "Dosya/kaynak için yetki yok",
        "IsADirectoryError": "Dosya yerine klasör verilmiş",
        "NotADirectoryError": "Klasör yerine dosya verilmiş",
        "OSError": "İşletim sistemi hatası (dosya/IO)",
        "IOError": "Girdi/Çıktı (IO) hatası",
        "EOFError": "Beklenmeyen dosya sonu (input bitti)",
        "KeyboardInterrupt": "Program kullanıcı tarafından durduruldu (Ctrl+C)",
        "RecursionError": "Çok fazla iç içe çağrı (özyineleme sınırı aşıldı)",
        "AssertionError": "assert ifadesi başarısız oldu",
        "UnicodeDecodeError": "Metin kodlaması (decode) uyuşmazlığı",
        "UnicodeEncodeError": "Metin kodlaması (encode) uyuşmazlığı",
        "UnicodeError": "Unicode işlem hatası",
        "OverflowError": "Sayı çok büyük, taşma oldu",
        "MemoryError": "Bellek yetersiz",
        "StopIteration": "Iterator bitti",
        "StopAsyncIteration": "Async iterator bitti",
        "RuntimeError": "Çalışma zamanı hatası",
        "NotImplementedError": "Bu metod henüz uygulanmamış",
        "ArithmeticError": "Aritmetik hata",
        "LookupError": "Arama hatası (index/key)",
        "ConnectionError": "Ağ bağlantı hatası",
        "ConnectionRefusedError": "Bağlantı reddedildi (port kapalı/servis çalışmıyor)",
        "ConnectionResetError": "Bağlantı karşı taraf tarafından kesildi",
        "ConnectionAbortedError": "Bağlantı iptal edildi",
        "TimeoutError": "İşlem zaman aşımına uğradı",
        "BrokenPipeError": "Pipe kırıldı (karşı taraf kapandı)",
        "ChildProcessError": "Alt süreç hatası",
        "BlockingIOError": "Non-blocking IO engellendi",
        "InterruptedError": "Sistem çağrısı kesildi",
        "JSONDecodeError": "Geçersiz JSON formatı",
        "GeneratorExit": "Generator kapatıldı",
        "SystemExit": "Program sys.exit() ile sonlandırıldı",
    },
    "javascript": {
        # Runtime hata tipleri
        "SyntaxError": "Yazım hatası",
        "ReferenceError": "Tanımlanmamış değişken",
        "TypeError": "Tip hatası (çoğunlukla 'is not a function' veya 'undefined of null')",
        "RangeError": "Değer aralık dışında (örn: sonsuz özyineleme, geçersiz dizi uzunluğu)",
        "URIError": "Bozuk URI (encodeURI/decodeURI hatası)",
        "EvalError": "eval() ile ilgili hata",
        "AggregateError": "Birden çok hata birleştirildi (Promise.any)",
        "InternalError": "JS motoru iç hatası (çoğunlukla stack overflow)",
        # Metin tabanli yaygin hatalar
        "is not a function": "Çağrılan şey fonksiyon değil (yanlış import veya yazım hatası)",
        "is not defined": "Değişken/fonksiyon tanımlı değil",
        "Cannot read property": "undefined veya null üzerinde property erişimi",
        "Cannot read properties of undefined": "undefined değerin property'si okunamaz",
        "Cannot read properties of null": "null değerin property'si okunamaz",
        "Maximum call stack size exceeded": "Sonsuz özyineleme (stack overflow)",
        "Unexpected token": "Beklenmeyen sözdizimi (noktalı virgül/parantez eksik olabilir)",
        "Unexpected end of input": "Beklenmeyen dosya sonu (parantez/süslü kapanmamış)",
        "Assignment to constant variable": "const değişkene yeniden atama yapılamaz",
        "Identifier has already been declared": "Aynı isimde değişken iki kez tanımlandı",
        # Node runtime
        "ERR_MODULE_NOT_FOUND": "Node modülü bulunamadı",
        "ERR_REQUIRE_ESM": "CommonJS 'require' ile ESM modülü yüklenemez",
        "EADDRINUSE": "Port zaten kullanımda",
        "ECONNREFUSED": "Bağlantı reddedildi (servis çalışmıyor olabilir)",
        "ENOTFOUND": "DNS çözümlemesi başarısız (host bulunamadı)",
        "ETIMEDOUT": "Bağlantı zaman aşımı",
        "EACCES": "İzin reddedildi (dosya/port için yetki yok)",
        "ENOENT": "Dosya veya klasör bulunamadı",
    },
    "typescript": {
        "SyntaxError": "Yazım hatası",
        "ReferenceError": "Tanımlanmamış değişken",
        "TypeError": "Tip hatası",
        # En yaygin TS kodlari
        "TS1005": "Beklenen karakter eksik (genellikle ; veya ,)",
        "TS1109": "İfade (expression) bekleniyor",
        "TS1128": "Bildirim veya ifade bekleniyor",
        "TS1155": "const/let bildirimi değer almalı",
        "TS1161": "Yorum sonlandırılmamış (*/ eksik)",
        "TS2300": "Çift tanımlama (aynı isim iki kez)",
        "TS2304": "Tanımlanmamış isim (import veya typing eksik olabilir)",
        "TS2305": "Modül bu ismi export etmiyor",
        "TS2307": "Modül bulunamadı (yanlış path veya paket kurulu değil)",
        "TS2322": "Atama tip hatası (değer türü hedef türle uyumsuz)",
        "TS2339": "Property bu tipte tanımlı değil",
        "TS2345": "Argüman tipi parametre tipine uygun değil",
        "TS2355": "Fonksiyon değer döndürmeli ama bazı yollarda döndürmüyor",
        "TS2451": "Blok kapsamlı değişken (let/const) yeniden tanımlanamaz",
        "TS2531": "Nesne null olabilir (null kontrolü ekle)",
        "TS2532": "Nesne undefined olabilir",
        "TS2533": "Nesne null ya da undefined olabilir",
        "TS2540": "Sadece okunur (readonly) property'ye atama yapılamaz",
        "TS2551": "Property yok (farklı bir isim kastediyor olabilirsin)",
        "TS2554": "Argüman sayısı eşleşmiyor",
        "TS2571": "'unknown' tipli nesneye doğrudan erişilemez",
        "TS2588": "const değişkene atama yapılamaz",
        "TS2693": "Sadece tip olarak kullanılabilir, değer olarak değil",
        "TS6133": "Değişken/import tanımlandı ama hiç kullanılmadı",
        "TS7006": "Parametre örtük olarak 'any' tipinde (noImplicitAny)",
        "TS7053": "Element örtük olarak 'any' tipinde (index signature yok)",
    },
    "java": {
        # Compile-time mesajlari (metin tabanli)
        "cannot find symbol": "Tanımlanmamış sembol (import eksik veya yazım hatası)",
        "package does not exist": "Paket bulunamadı (bağımlılık eksik olabilir)",
        "cannot resolve symbol": "Sembol çözümlenemedi",
        "expected": "Beklenen karakter eksik (genellikle ; veya })",
        "illegal start": "Geçersiz başlangıç (sözdizimi hatası)",
        "class expected": "Sınıf bekleniyor",
        "';' expected": "Noktalı virgül (;) eksik",
        "variable might not have been initialized": "Değişken başlatılmamış olabilir",
        "incompatible types": "Tip uyuşmazlığı",
        "missing return statement": "Metod return ifadesi içermiyor",
        "cannot be applied": "Metod bu argümanlara uygulanamaz (imza uyuşmuyor)",
        "unreachable statement": "Ulaşılamayan kod",
        "non-static method cannot be referenced": "Statik olmayan metoda statik erişim",
        "unchecked or unsafe operations": "Tip güvensiz işlem (cast uyarısı)",
        "bad operand types": "Operatör için geçersiz operand tipleri",
        # Runtime exception'lar
        "NullPointerException": "null üzerinde metod/alan erişimi",
        "ArrayIndexOutOfBoundsException": "Dizi indeksi sınırlar dışında",
        "StringIndexOutOfBoundsException": "String indeksi sınırlar dışında",
        "ClassCastException": "Geçersiz tür dönüşümü (cast)",
        "ArithmeticException": "Aritmetik hata (sıfıra bölme vb.)",
        "NumberFormatException": "Sayıya çevrilemeyen string",
        "IllegalArgumentException": "Geçersiz argüman",
        "IllegalStateException": "Nesne bu durumda bu işleme uygun değil",
        "ConcurrentModificationException": "Koleksiyon iterasyon sırasında değiştirildi",
        "UnsupportedOperationException": "Bu işlem desteklenmiyor",
        "ClassNotFoundException": "Sınıf classpath'te bulunamadı",
        "NoClassDefFoundError": "Sınıf tanımı yüklenemedi (runtime'da classpath sorunu)",
        "NoSuchMethodError": "Çağrılan metod yok (sürüm uyumsuzluğu)",
        "NoSuchFieldError": "Çağrılan alan yok",
        "OutOfMemoryError": "Java heap belleği tükendi",
        "StackOverflowError": "Sonsuz özyineleme (stack taştı)",
        "FileNotFoundException": "Dosya bulunamadı",
        "IOException": "Girdi/Çıktı (IO) hatası",
        "InterruptedException": "Thread kesildi",
    },
    "cpp": {
        # Sozdizimi
        "expected ';'": "Noktalı virgül (;) eksik",
        "expected '}'": "Kapanış süslü parantez (}) eksik",
        "expected '{'": "Açılış süslü parantez ({) eksik",
        "expected ')'": "Kapanış parantezi ()) eksik",
        "expected identifier": "Tanımlayıcı (isim) bekleniyor",
        "expected primary-expression": "Temel ifade bekleniyor",
        "expected": "Beklenen karakter eksik",
        "stray": "Geçersiz/hatalı karakter",
        # Isim / tanimlama
        "undeclared": "Tanımlanmamış değişken/fonksiyon",
        "was not declared in this scope": "Bu kapsamda tanımlı değil (include eksik olabilir)",
        "has not been declared": "Tanımlı değil",
        "no member named": "Bu sınıfta böyle bir üye yok",
        "has no member named": "Sınıfın böyle bir üyesi yok",
        "redefinition of": "Aynı şey iki kez tanımlandı",
        "redeclared as different kind": "Aynı isim farklı türde tekrar tanımlandı",
        # Tip / overload
        "cannot convert": "Tip dönüşümü yapılamaz",
        "invalid conversion": "Geçersiz tip dönüşümü",
        "no matching function": "Argümanlara uygun fonksiyon bulunamadı (overload yok)",
        "ambiguous overload": "Birden fazla uygun overload var (belirsiz)",
        "invalid use of": "Geçersiz kullanım (tip uyuşmazlığı)",
        "incomplete type": "Tam tanımlanmamış tip (forward declaration eksik)",
        # Linker
        "undefined reference": "Linker hatası: tanım bulunamadı (cpp dosyası derlenmedi/linklenmedi)",
        "multiple definition": "Aynı sembol birden fazla yerde tanımlı (header'da tanım var)",
        # Pointer / bellek (runtime isaretleri)
        "segmentation fault": "Segmentation fault — geçersiz bellek erişimi (çoğunlukla null/dangling pointer)",
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
    
    # Python traceback formatini ayrica dene (farkli bir format)
    if not sonuclar and dil_kodu == "python":
        sonuclar = python_traceback_parser(hata_metni)

    return sonuclar


def python_traceback_parser(hata_metni):
    """
    Python traceback formatini parse eder.
    Ornek:
        Traceback (most recent call last):
          File "app.py", line 12, in foo
            x = 1/0
        ZeroDivisionError: division by zero
    Cagri yigitinin en ic frame'i + son hata tipi+mesaj dondurulur.
    """
    sonuclar = []

    # Tum "File ..., line N, in ..." satirlarini topla (en son = hatanin oldugu yer)
    frame_pattern = r'File "([^"]+)", line (\d+)(?:, in (\S+))?'
    frames = re.findall(frame_pattern, hata_metni)

    # Son satirda "ErrorTipi: mesaj" formatini bul
    # Birden fazla satira yayilmis mesajlari da tolere et (son eslesen yeterli)
    hata_tipi_pattern = r'^([A-Z]\w*(?:Error|Exception|Warning|Interrupt)):\s*(.*)$'
    hata_tipi = None
    hata_mesaji = ""
    for satir in reversed(hata_metni.splitlines()):
        m = re.match(hata_tipi_pattern, satir.strip())
        if m:
            hata_tipi, hata_mesaji = m.group(1), m.group(2).strip()
            break

    # Hicbir sinyal yoksa bos don
    if not frames and not hata_tipi:
        return sonuclar

    # Varsayilan: son frame (hatanin gercek yeri)
    if frames:
        dosya, satir_no, fonk = frames[-1]
    else:
        dosya, satir_no, fonk = "?", "?", ""

    aciklama = hata_aciklama_bul(hata_tipi or "", hata_mesaji, "python")
    if aciklama == "Sözdizimi hatası" and hata_tipi:
        # Sozlukte yoksa en azindan hata tipini goster
        aciklama = f"{hata_tipi}: {hata_mesaji}" if hata_mesaji else hata_tipi

    sonuclar.append({
        'dosya': dosya,
        'satir': satir_no,
        'kolon': '-',
        'hata_kodu': hata_tipi or "Traceback",
        'mesaj': hata_mesaji,
        'aciklama': aciklama,
    })

    # Eger cagri yigini derinse kullaniciya ek bilgi ver
    if len(frames) > 1:
        dosya_zinciri = " -> ".join(f"{d}:{s}" for d, s, _ in frames)
        sonuclar[0]['cagri_yigini'] = dosya_zinciri

    return sonuclar


def cakisma_detay_cikar(hata_metni, dil_kodu):
    """
    Hata metninden cakisan paket isim + surum + kisit bilgilerini cikarir.
    Don: formatli string (rapora enjekte icin) veya bos string.
    """
    satirlar_cikti = []

    if dil_kodu == "python":
        # "X 1.2.3 requires Y<2,>=1" veya "X 1.2.3 depends on Y op V"
        # Kisit kismi: virgulle ayrilabilen operator+surum blogu
        pat_requires = re.compile(
            r'(?P<paket>[A-Za-z0-9_.\-]+)\s+'
            r'(?P<surum>\d[\w.\-+!]*)\s+'
            r'(?:requires|depends on)\s+'
            r'(?P<hedef>[A-Za-z0-9_.\-]+)\s*'
            r'(?P<kisit>[<>=!~]+[\w.\-+!]+(?:\s*,\s*[<>=!~]+[\w.\-+!]+)*(?:\s+and\s+[<>=!~]+[\w.\-+!]+)*)',
            re.IGNORECASE,
        )
        gorulen = set()
        for m in pat_requires.finditer(hata_metni):
            paket = m.group("paket")
            surum = m.group("surum")
            hedef = m.group("hedef")
            kisit = m.group("kisit").strip()
            key = (paket, surum, hedef, kisit)
            if key in gorulen:
                continue
            gorulen.add(key)
            satirlar_cikti.append(
                f"  • {paket} {surum}  →  ister:  {hedef} {kisit}"
            )

        # "but you have Y 1.2.3 which is incompatible"
        pat_have = re.compile(
            r'but you have\s+(?P<paket>[A-Za-z0-9_.\-]+)\s+'
            r'(?P<surum>\d[\w.\-+!]*)',
            re.IGNORECASE,
        )
        gorulen_kurulu = set()
        for m in pat_have.finditer(hata_metni):
            key = (m.group("paket"), m.group("surum"))
            if key in gorulen_kurulu:
                continue
            gorulen_kurulu.add(key)
            satirlar_cikti.append(
                f"  • Kurulu olan:  {key[0]} {key[1]}  (uyumsuz)"
            )

    elif dil_kodu in ("javascript", "typescript"):
        # NPM: "Found: X@1.2.3"  (surum aynı satırda biter, newline veya bosluk)
        pat_found = re.compile(r'Found:\s*(?P<paket>[@\w.\-\/]+)@(?P<surum>[^\s\n]+)')
        for m in pat_found.finditer(hata_metni):
            satirlar_cikti.append(
                f"  • Kurulu olan:  {m.group('paket')}@{m.group('surum')}"
            )

        # NPM: 'peer X@"..." from Y@1.2.3'
        pat_peer = re.compile(
            r'peer\s+(?P<paket>[@\w.\-\/]+)@["\']?(?P<kisit>[^"\'\n]+?)["\']?\s+from\s+'
            r'(?P<kaynak>[@\w.\-\/]+)@(?P<kaynak_surum>[^\s\n]+)',
            re.IGNORECASE,
        )
        for m in pat_peer.finditer(hata_metni):
            satirlar_cikti.append(
                f"  • {m.group('kaynak')}@{m.group('kaynak_surum')}  →  "
                f"ister:  {m.group('paket')}@{m.group('kisit').strip()}"
            )

    if not satirlar_cikti:
        return ""

    return (
        "🔎 TESPİT EDİLEN ÇAKIŞAN PAKETLER:\n"
        + "\n".join(satirlar_cikti)
        + "\n\n"
    )


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
                f"⚠️ EKSİK / UYUMSUZ KÜTÜPHANE TESPİT EDİLDİ (Python)\n"
                f"{'='*60}\n\n"
                f"📋 SORUN:\n"
                f"'{modul_adi}' kütüphanesi sistemde kurulu değil, yanlış sanal ortamda\n"
                f"aranıyor ya da farklı bir Python sürümüne kurulmuş olabilir. Program\n"
                f"çalışırken `import {modul_adi}` satırında durdu.\n\n"
                f"🔍 HATANIN OLASI KAYNAKLARI:\n"
                f"  1) Kütüphane hiç kurulmadı (pip install unutuldu).\n"
                f"  2) Sanal ortam (venv) aktif edilmeden program çalıştırıldı, bu yüzden\n"
                f"     global Python yorumlayıcısı kullanılıyor ve kütüphane orada yok.\n"
                f"  3) Kütüphanenin eski bir sürümü kuruldu; import yolu değişmiş olabilir\n"
                f"     (örn. eski 'sklearn' -> yeni 'scikit-learn').\n"
                f"  4) Başka bir kütüphaneyle sürüm çakışması var; pip sessizce eski bir\n"
                f"     sürüm bırakmış olabilir.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE' YÖNTEMİ:\n"
                f"Terminalde (PowerShell) sırayla çalıştırın:\n\n"
                f"  1. .venv\\Scripts\\activate          # sanal ortamı aktif et\n"
                f"  2. pip uninstall {modul_adi} -y\n"
                f"  3. pip cache purge                    # bozuk önbelleği temizle\n"
                f"  4. pip install {modul_adi} --upgrade --no-cache-dir\n\n"
                f"🔁 ALTERNATİF ÇÖZÜMLER:\n"
                f"  - Tüm bağımlılıkları sıfırla:\n"
                f"      pip freeze > eski_paketler.txt\n"
                f"      pip uninstall -r eski_paketler.txt -y\n"
                f"      pip install -r requirements.txt\n"
                f"  - Sanal ortamı komple baştan kur:\n"
                f"      rmdir /s /q .venv\n"
                f"      python -m venv .venv\n"
                f"      .venv\\Scripts\\activate\n"
                f"      pip install -r requirements.txt\n\n"
                f"💡 EK NOT:\n"
                f"  - Hangi Python'un kullanıldığını doğrulayın:  where python\n"
                f"  - Kütüphanenin kurulu olup olmadığını kontrol:  pip show {modul_adi}"
            )
        
        # Sürüm çakışması - pip dependency resolver
        if "resolutionimpossible" in metin_lower or "cannot install" in metin_lower or "incompatible" in metin_lower or "version conflict" in metin_lower:
            detay = cakisma_detay_cikar(hata_metni, "python")
            return (
                f"⚠️ KÜTÜPHANE SÜRÜM ÇAKIŞMASI TESPİT EDİLDİ (Python / pip)\n"
                f"{'='*60}\n\n"
                f"📋 SORUN:\n"
                f"Projede kullanılan paketlerin birbirinden istediği sürümler çelişiyor.\n"
                f"pip, tüm koşulları aynı anda karşılayan bir sürüm kümesi bulamıyor ve\n"
                f"kurulum yarıda kalıyor.\n\n"
                f"{detay}"
                f"🔍 HATANIN OLASI KAYNAKLARI:\n"
                f"  1) requirements.txt içinde eski bir paket, yeni bir paketin güncel\n"
                f"     sürümüyle uyumsuz (ör. numpy<1.20 iken pandas>=2.0 isteniyor).\n"
                f"  2) Global ortama daha önce kurulmuş eski sürümler takılıyor.\n"
                f"  3) pip'in kendi sürümü çok eski; yeni çözümleyiciyi kullanmıyor.\n"
                f"  4) İki bağımlılık aynı alt-paketin farklı sürümlerini zorluyor\n"
                f"     (transitive dependency conflict).\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE' YÖNTEMİ:\n"
                f"  1. python -m pip install --upgrade pip\n"
                f"  2. pip freeze > requirements_backup.txt       # yedek al\n"
                f"  3. pip uninstall -r requirements_backup.txt -y\n"
                f"  4. pip cache purge\n"
                f"  5. pip install -r requirements.txt\n\n"
                f"🔁 ALTERNATİF ÇÖZÜMLER:\n"
                f"  - Sürüm kısıtlarını gevşet: requirements.txt'de '==' yerine '>='\n"
                f"    kullan ya da sürümü tamamen kaldırıp sadece paket adını bırak.\n"
                f"  - Temiz bir sanal ortam kurun (en garantili yöntem):\n"
                f"      rmdir /s /q .venv\n"
                f"      python -m venv .venv && .venv\\Scripts\\activate\n"
                f"      pip install -r requirements.txt\n"
                f"  - Çakışan paketi yalıtın:\n"
                f"      pip install <paket> --ignore-installed\n\n"
                f"💡 EK NOT:\n"
                f"Genellikle bu hata iki kütüphanenin uyumsuzluğundan kaynaklanır;\n"
                f"hata mesajındaki 'requires X but you have Y' satırı çakışan paketi\n"
                f"açıkça gösterir."
            )
    
    # 2. JAVASCRIPT / TYPESCRIPT - npm/yarn çakışmaları
    if dil_kodu in ["javascript", "typescript"]:
        if "eresolve" in metin_lower or "peer dependency" in metin_lower or "conflict" in metin_lower:
            detay = cakisma_detay_cikar(hata_metni, "javascript")
            return (
                f"⚠️ NPM KÜTÜPHANE ÇAKIŞMASI TESPİT EDİLDİ\n"
                f"{'='*50}\n\n"
                f"📋 SORUN:\n"
                f"node_modules klasöründe paket sürümleri çakışıyor.\n\n"
                f"{detay}"
                f"🔍 HATANIN KAYNAĞI:\n"
                f"Bazı paketler aynı bağımlılığın farklı sürümlerini gerektiriyor.\n"
                f"npm/yarn bu çakışmayı çözemiyor.\n\n"
                f"🛠️ ÇÖZÜM - 'SİLİP TEKRAR YÜKLE':\n"
                f"Terminalde şu komutları sırayla çalıştırın:\n\n"
                f"1. Remove-Item -Recurse -Force node_modules, package-lock.json -ErrorAction SilentlyContinue\n"
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
        if ("maven" in metin_lower or "gradle" in metin_lower
                or "dependenc" in metin_lower   # "dependency" VE "dependencies" ikisini de yakalar
                or "could not resolve" in metin_lower
                or "failed to execute goal" in metin_lower):
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
            cikti += f"💻 Kod: {hata['hata_kodu']}\n"
            if hata.get('mesaj'):
                cikti += f"💬 Mesaj: {hata['mesaj']}\n"
            if hata.get('cagri_yigini'):
                cikti += f"🧭 Çağrı yığını: {hata['cagri_yigini']}\n"
            cikti += "\n"
    
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


def komutlari_cikart(icerik):
    """
    Rapordan 'SİLİP TEKRAR YÜKLE' bloku icindeki numarali komutlari cikarir.
    'ÇÖZÜM' basligindan sonra; 'ALTERNATİF', 'EK NOT', 💡 emoji gordugunde biter.
    """
    komutlar = []
    icinde = False
    for satir in icerik.splitlines():
        if "ÇÖZÜM" in satir:
            icinde = True
            continue
        if icinde:
            if ("ALTERNATİF" in satir or "EK NOT" in satir
                    or satir.lstrip().startswith("💡")
                    or satir.lstrip().startswith("🔁")
                    or satir.lstrip().startswith("🔍")):
                icinde = False
                continue
            # Numarali satir: "  1. pip uninstall pandas -y"
            m = re.match(r'^\s*\d+\.\s+(.+?)\s*(?:#.*)?$', satir)
            if m:
                cmd = m.group(1).strip()
                # "Terminalde ..." aciklama satirlarini atla
                if cmd and not cmd.lower().startswith(("terminalde", "sirayla", "maven:", "gradle:")):
                    komutlar.append(cmd)
    return komutlar


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

    def komutlari_calistir():
        komutlar = komutlari_cikart(icerik)
        if not komutlar:
            messagebox.showinfo(
                "Komut Bulunamadı",
                "Bu raporda çalıştırılabilir 'silip tekrar yükle' komutu yok.",
            )
            return
        ozet = "\n".join(f"  {i+1}. {k}" for i, k in enumerate(komutlar))
        onay = messagebox.askyesno(
            "Komutları Çalıştır?",
            f"Aşağıdaki {len(komutlar)} komut yeni bir PowerShell penceresinde\n"
            f"SIRAYLA çalıştırılacak. Pencere iş bitince kapanmayacak\n"
            f"(çıktıyı kontrol edebilmen için).\n\n"
            f"{ozet}\n\n"
            f"⚠️  Komutlar paketleri SİLİP yeniden kurar. Devam edilsin mi?",
        )
        if not onay:
            return
        # Her komut basarisiz olsa bile sonrakine gec -> ';' operatoru
        birlesik = " ; ".join(komutlar)
        try:
            subprocess.Popen(
                ["powershell", "-NoExit", "-Command", birlesik],
                creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
            )
        except Exception as e:
            messagebox.showerror("Çalıştırma Hatası", f"PowerShell başlatılamadı:\n{e}")

    # 'Komutları Calistir' butonu sadece rapor gercekten komut iceriyorsa gorunsun
    komut_sayisi = len(komutlari_cikart(icerik))
    if komut_sayisi > 0:
        tk.Button(
            alt_frame,
            text=f"🛠️ Komutları Çalıştır ({komut_sayisi})",
            command=komutlari_calistir,
            bg="#c85a1a",
            fg="white",
            activebackground="#e07030",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
        ).pack(side="left", padx=(8, 0))

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


def dil_otomatik_tespit(hata_metni):
    """
    Hata metninden programlama dilini otomatik tespit eder.
    Basit ama guclu sinyallere dayanir (skor bazli).
    Dondurur: dil_kodu (str) veya None (emin degilse).
    """
    if not hata_metni:
        return None

    metin = hata_metni.lower()
    skorlar = {
        "python": 0, "javascript": 0, "typescript": 0, "java": 0,
        "csharp": 0, "cpp": 0, "php": 0, "rust": 0, "go": 0, "html": 0,
    }

    # --- PYTHON (cok belirgin sinyaller) ---
    if "traceback (most recent call last)" in metin: skorlar["python"] += 10
    if "modulenotfounderror" in metin: skorlar["python"] += 8
    if "importerror" in metin: skorlar["python"] += 6
    if re.search(r'file "[^"]+\.py"', metin): skorlar["python"] += 6
    if "indentationError".lower() in metin: skorlar["python"] += 5
    if re.search(r'\b(pip|pip3)\b', metin): skorlar["python"] += 3
    if re.search(r'\b\w+error\b.*:', metin) and "python" not in skorlar: pass
    if "resolutionimpossible" in metin: skorlar["python"] += 7
    if re.search(r'line \d+, in ', metin): skorlar["python"] += 5

    # --- JAVASCRIPT / NODE ---
    if "npm err!" in metin: skorlar["javascript"] += 10
    if "node_modules" in metin: skorlar["javascript"] += 6
    if "eresolve" in metin: skorlar["javascript"] += 8
    if "cannot find module" in metin: skorlar["javascript"] += 7
    if "peer dependency" in metin: skorlar["javascript"] += 6
    if re.search(r'\.js[:\s]', metin): skorlar["javascript"] += 4
    if "at function.module._resolvefilename" in metin: skorlar["javascript"] += 6

    # --- TYPESCRIPT ---
    if re.search(r'\bts\d{4}\b', metin): skorlar["typescript"] += 10
    if re.search(r'\.ts[:\(]', metin): skorlar["typescript"] += 6
    if "tsc " in metin or " tsc:" in metin: skorlar["typescript"] += 5

    # --- C# ---
    if re.search(r'\bcs\d{4}\b', metin): skorlar["csharp"] += 10
    if re.search(r'\.cs\(\d+,\d+\)', metin): skorlar["csharp"] += 8
    if re.search(r'\bnu\d{4}\b', metin): skorlar["csharp"] += 9  # NuGet
    if "nuget" in metin: skorlar["csharp"] += 6
    if re.search(r'\bdotnet\b', metin): skorlar["csharp"] += 4

    # --- JAVA ---
    if "exception in thread" in metin: skorlar["java"] += 8
    if re.search(r'\.java:\d+', metin): skorlar["java"] += 7
    if "maven" in metin or "mvn " in metin: skorlar["java"] += 6
    if "gradle" in metin: skorlar["java"] += 6
    if "failed to execute goal" in metin: skorlar["java"] += 7
    if re.search(r'at (com|org|java)\.', metin): skorlar["java"] += 4

    # --- C / C++ ---
    if re.search(r'\.(cpp|cc|cxx|hpp|h)[:\s]', metin): skorlar["cpp"] += 7
    if "undeclared" in metin and "node_modules" not in metin: skorlar["cpp"] += 3
    if "was not declared" in metin: skorlar["cpp"] += 5
    if re.search(r'\bg\+\+\b|\bgcc\b', metin): skorlar["cpp"] += 5

    # --- RUST ---
    if re.search(r'error\[e\d+\]', metin): skorlar["rust"] += 10
    if "cargo" in metin: skorlar["rust"] += 5
    if re.search(r'\.rs:\d+', metin): skorlar["rust"] += 6

    # --- GO ---
    if re.search(r'\.go:\d+', metin): skorlar["go"] += 7
    if re.search(r'\bgo (build|run|get|mod)\b', metin): skorlar["go"] += 6

    # --- PHP ---
    if "php parse error" in metin or "php fatal error" in metin: skorlar["php"] += 10
    if re.search(r'\.php(:|\son\sline)', metin): skorlar["php"] += 6

    # En yuksek skorlu dili sec
    en_iyi = max(skorlar, key=skorlar.get)
    if skorlar[en_iyi] >= 6:  # esik: guven skoru
        return en_iyi
    return None


def hata_menu_goster():
    """F10 akisi: metni kopyala, dili otomatik tespit et, gerekirse menu goster."""
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

    # Dili otomatik tespit etmeyi dene
    otomatik_dil = dil_otomatik_tespit(secili_metin)
    if otomatik_dil:
        print(f"🔍 Dil otomatik tespit edildi: {otomatik_dil}")
        # Menuyu atla, direkt AI secim menusune gec
        hata_ai_menu_goster(secili_metin, otomatik_dil)
    else:
        # Emin degil → kullanici secsin
        print("❓ Dil otomatik tespit edilemedi, menü gösteriliyor.")
        dil_secim_menu_goster(secili_metin)


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
