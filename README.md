# Local RAG Assistant

Microsoft Foundry Local ile **tamamen offline** çalışan, belge tabanlı soru-cevap asistanı. Kullanıcının sorusunu yerel embedding modeliyle vektöre çevirir, SQLite'ta saklanan belge parçaları arasından anlamca en yakınlarını bulur ve yerel dil modeline "cevabını sadece bu parçalara dayandır" talimatıyla iletir. İnternet bağlantısı olmadan çalışır; belgeler cihazdan dışarı çıkmaz.

> Bu proje, bir aylık yaz stajı programı kapsamında geliştirilmiştir.

## Nasıl Çalışır? (Mimari)

```
Kullanıcı sorusu
      │
      ▼
[Embedding modeli - CPU]  soruyu vektöre çevirir
      │
      ▼
[SQLite: rag.db]  34 belge parçası + vektörleri
      │  kosinüs benzerliği ile en yakın 3 parça seçilir
      ▼
[Sohbet modeli - GPU]  system prompt kuralları + bağlam + soru
      │  "sadece bağlamdan cevapla, yoksa 'Bu bilgi elimde yok' de"
      ▼
Cevap + kaynak dosya künyesi  →  ör: "Projede SQLite kullanılır. [03_teknolojiler.txt]"
```

**RAG (Retrieval-Augmented Generation):** Modele yeni bilgi "öğretilmez"; her soruda ilgili belge parçaları bulunup sorunun yanına eklenir. Model açık kitap sınavdaki öğrenci gibidir: doğru sayfa her seferinde önüne konur.

## Kullanılan Teknolojiler

| Bileşen | Seçim | Rolü |
|---|---|---|
| Yerel AI çalışma zamanı | Microsoft Foundry Local | Modelleri cihazda indirir ve çalıştırır |
| Sohbet modeli | qwen3-4b (GPU/CUDA) | Cevap üretimi |
| Embedding modeli | qwen3-embedding-0.6b (CPU) | Metin → anlam vektörü |
| Veri katmanı | SQLite (Python yerleşik) | Belge parçaları + vektörlerin kalıcı saklanması |
| SDK | foundry-local-sdk (Python) | Modellerle kod içinden iletişim |

## Kurulum

Gereksinimler: Windows 10/11, Python 3.10+, (önerilen) NVIDIA GPU.

```powershell
# 1. Foundry Local
winget install Microsoft.FoundryLocal

# 2. Depoyu klonla
git clone https://github.com/Ouzhanerdem37/local-rag-assistant.git
cd local-rag-assistant

# 3. Python bağımlılıkları
python -m pip install -r requirements.txt
```

Not: `main.py` ve `ara.py` içindeki `model_cache_dir` yolu kendi kullanıcı adınıza göre güncellenmelidir (`foundry cache location` komutu doğru yolu gösterir).

## Kullanım

```powershell
# 1. Belgeleri veritabanına yükle (belgeler/ klasörü değişince tekrar çalıştırılır)
python ingest.py

# 2. Botu başlat
python main.py
```

İlk çalıştırmada modeller indirilir (~3 GB, tek seferlik). `SEN:` satırına soru yazılır; `cikis` ile çıkılır.

```
SEN: Program kac hafta suruyor?
BOT: Program 4 hafta (yaklaşık bir ay) sürer. [02_takvim_ve_fazlar.txt]

SEN: Stajyerlere maas odeniyor mu?
BOT: Bu bilgi elimde yok.
```

Kendi belgelerinizle kullanmak için: `.txt` dosyalarınızı `belgeler/` klasörüne koyun (paragraflar boş satırla ayrılmış olmalı) ve `python ingest.py` çalıştırın.

## Dosya Yapısı

```
local-rag-assistant/
├── main.py                  # Bot: retrieval + LLM + sohbet döngüsü
├── ara.py                   # get_top_chunks(): anlam bazlı arama
├── ingest.py                # Belgeleri parçala, embedle, SQLite'a yaz
├── test_bot.py              # 10 soruluk otomatik test düzeneği
├── belgeler/                # Bilgi kaynağı (.txt, 6 dosya)
├── TEST_SONUCLARI_v1.md     # İlk test turu (ham hali)
├── TEST_SONUCLARI_final.md  # Son test turu (değerlendirmeli)
└── rag.db                   # Üretilen veritabanı (repoya dahil değil)
```

## Tasarım Kararları

**Model seçimi — A/B testiyle:** İlk denenen qwen2.5-0.5b, talimat takibinde başarısız oldu: bağlamda olmayan sorulara uydurma cevaplar üretti (ör. var olmayan bir maaş için "900 TL"). Aynı 3 deneylik test qwen3-4b ile tekrarlandığında model, bağlam dışı soruyu doğru şekilde reddetti. Türkçe desteği daha güçlü olduğu için Phi ailesi yerine Qwen tercih edildi.

**Embedding CPU'da, sohbet modeli GPU'da:** İki model birden GPU'ya yüklendiğinde bellek yetmedi ("bad allocation"). Embedding modeli küçük olduğu ve soru başına tek cümlelik iş yaptığı için CPU'ya taşındı; GPU ağır işe (cevap üretimi) ayrıldı.

**Uydurma (hallucination) kontrolü — system prompt ile:** Kurallar koşullu yazıldı: cevap bağlamda varsa "cevap + kaynak künyesi", yoksa yalnızca "Bu bilgi elimde yok." Çelişkili kuralların (ör. "sadece şu cümleyi yaz" + "künye zorunlu") modeli tutarsızlaştırdığı testle gözlendi ve düzeltildi.

**Belge kalitesi = cevap kalitesi:** "Program kaç hafta sürüyor?" sorusuna model ısrarla "52 hafta" diyordu. Teşhis: kaynak belgede süre yalnızca "ay" birimindeydi ve model birim çevirisinde hata yapıyordu. Belge "4 hafta (yaklaşık bir ay)" olarak netleştirilince sorun kalıcı çözüldü.

**Basit vektör arama (harici vektör DB yok):** 34 parçalık koleksiyonda tüm vektörleri okuyup kosinüs benzerliğini Python'da hesaplamak yeterli ve hızlıdır. Büyük koleksiyonlarda özel vektör veritabanı gerekir; bu bilinçli bir kapsam kararıdır.

## Test Sonuçları

10 soruluk test seti üç kategoride koşuldu: cevaplanabilir (5), cevaplanamaz (3), uç durum (2). Son turda **8/10 başarı**. Süreçte yakalanan ve çözülen hatalar: birim çevirisi uydurması ("52 hafta"), çelişkili kural kaynaklı eksik cevaplar, `<think>` bloğu sızıntısı. Ayrıntı: `TEST_SONUCLARI_final.md`.

## Bilinen Sınırlılıklar

- **Üretim oynaklığı:** 4B parametreli model, aynı soruya turdan tura farklı biçimde cevap verebiliyor; nadiren reddetmesi gereken soruya uydurma cevap ürettiği gözlendi. Çekirdek davranışlar (doğru cevap + reddetme) büyük oranda kararlı; biçim detayları (künye yerleşimi) oynak.
- **Künye güvenilirliği:** Model kaynak dosya adını da üretir — nadiren harf hatası yapabilir ("03_teknoloZiler.txt" gibi).
- **Türkçe akıcılık:** 4B modelin Türkçesi anlaşılır ancak büyük modellerin gerisinde; doğruluk testlerinde sorun çıkarmadı.
- Sohbet geçmişi tutulmaz (her soru bağımsızdır); tek seferde tek kullanıcı içindir.

## Kaynaklar

- [Foundry Local dokümantasyonu](https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local)
- [Tutorial: Build a RAG application (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/foundry-local/tutorials/tutorial-build-rag-app)
- [Building Your First Local RAG Application with Foundry Local (Tech Community)](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/building-your-first-local-rag-application-with-foundry-local/4501968)
- [SQLite](https://sqlite.org/index.html)
- [Prompt engineering techniques (Microsoft Learn)](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/prompt-engineering)