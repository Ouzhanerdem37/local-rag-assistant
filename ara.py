import json
import sqlite3
import math

from foundry_local_sdk import Configuration, FoundryLocalManager

EMBED_MODEL = "qwen3-embedding-0.6b"
DB_DOSYASI = "rag.db"

def kosinus_benzerligi(v1, v2):
    carpim_toplami = 0
    boy1 = 0
    boy2 = 0
    for a, b in zip(v1, v2):
        carpim_toplami += a * b
        boy1 += a * a
        boy2 += b * b
    return carpim_toplami / (math.sqrt(boy1) * math.sqrt(boy2))

def modeli_hazirla():
    config = Configuration(
        app_name="local-rag-assistant",
        model_cache_dir=r"C:\Users\oguzh\.foundry\cache\models",
    )
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps(names=["CUDAExecutionProvider"])

    model = manager.catalog.get_model(EMBED_MODEL)
    for varyant in model.variants:
        if "cuda" in varyant.id:
            model.select_variant(varyant)
    model.load()
    return model.get_embedding_client()

def get_top_chunks(client, soru, k=3):
    soru_vektoru = client.generate_embedding(soru).data[0].embedding

    baglanti = sqlite3.connect(DB_DOSYASI)
    imlec = baglanti.cursor()
    imlec.execute("SELECT kaynak, icerik, vektor FROM parcalar")

    sonuclar = []
    for kaynak, icerik, vektor_yazisi in imlec.fetchall():
        skor = kosinus_benzerligi(soru_vektoru, json.loads(vektor_yazisi))
        sonuclar.append((skor, kaynak, icerik))
    baglanti.close()

    sonuclar.sort(reverse=True)
    return sonuclar[:k]

def main():
    client = modeli_hazirla()

    sorular = [
        "Bu projede hangi veritabani kullaniliyor?",
        "Program kac hafta suruyor?",
        "Sunumda neler anlatilmali?",
    ]

    for soru in sorular:
        print(f"\nSORU: {soru}")
        for skor, kaynak, icerik in get_top_chunks(client, soru, k=3):
            ozet = icerik[:80].replace("\n", " ")
            print(f"  {skor:.3f}  [{kaynak}]  {ozet}...")

if __name__ == "__main__":
    main()