from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.openai import ChatClientSettings
from ara import get_top_chunks

CHAT_MODEL = "qwen3-4b"
EMBED_MODEL = "qwen3-embedding-0.6b"

KURALLAR = (
    "/no_think Sen bir soru-cevap asistanisin. "
    "SADECE sana BAGLAM olarak verilen bilgiyi kullan. "
    "Sayilari, tarihleri ve sureleri baglamdan birebir aktar; asla cevirme veya tahmin etme. "
    "Eger cevap baglamda VARSA: once cevabi tam cumle olarak yaz, en sona kaynak dosya adini koseli parantezle ekle. Ornek: 'Projede SQLite kullanilir. [03_teknolojiler.txt]' "
    "Eger cevap baglamda YOKSA: kaynak gosterme ve SADECE sunu yaz: Bu bilgi elimde yok. "
    "Soruyla ayni dilde, kisa ve net cevap ver."
)

def modelleri_hazirla():
    config = Configuration(
        app_name="local-rag-assistant",
        model_cache_dir=r"C:\Users\oguzh\.foundry\cache\models",
    )
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps(names=["CUDAExecutionProvider"])

    embed_model = manager.catalog.get_model(EMBED_MODEL)
    for varyant in embed_model.variants:
        if "cpu" in varyant.id:
            embed_model.select_variant(varyant)
    embed_model.download()
    embed_model.load()

    chat_model = manager.catalog.get_model(CHAT_MODEL)
    for varyant in chat_model.variants:
        if "cuda" in varyant.id:
            chat_model.select_variant(varyant)
    chat_model.load()

    chat_client = chat_model.get_chat_client()
    
    return embed_model.get_embedding_client(), chat_client

def cevapla(embed_client, chat_client, soru):
    parcalar = get_top_chunks(embed_client, soru, k=3)

    baglam = "\n\n".join(
        f"[{kaynak}] {icerik}" for skor, kaynak, icerik in parcalar
    )

    cevap = chat_client.complete_chat(
        messages=[
            {"role": "system", "content": KURALLAR},
            {"role": "user", "content": f"BAGLAM:\n{baglam}\n\nSORU: {soru}"},
        ]
    )
    metin = cevap.choices[0].message.content
    if "</think>" in metin:
        metin = metin.split("</think>")[-1]
    metin = metin.replace("<think>", "").strip()
    return metin

def main():
    print("Modeller yukleniyor, biraz bekle...")
    embed_client, chat_client = modelleri_hazirla()
    print("Hazir! Sorunu yaz (cikmak icin: cikis)\n")

    while True:
        soru = input("SEN: ").strip()
        if soru.lower() in ("cikis", "exit", "q"):
            print("Gorusuruz!")
            break
        if not soru:
            continue
        try:
            print("BOT:", cevapla(embed_client, chat_client, soru))
        except Exception as hata:
            print("BOT: (Bir sorun olustu, tekrar dener misin?) Detay:", hata)
        print()

if __name__ == "__main__":
    main()