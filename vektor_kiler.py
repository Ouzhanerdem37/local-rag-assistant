import json
import sqlite3
import math

from foundry_local_sdk import Configuration, FoundryLocalManager

EMBED_MODEL = "qwen3-embedding-0.6b"

CUMLELER = [
    "Kedim mama yemiyor, cok istahsiz.",
    "Bugun hava cok guzel, yuruyuse cikacagim.",
    "Python ile programlama ogreniyorum.",
    "Arabamin lastigi patladi, tamirciye gittim.",
    "Aksam yemeginde makarna pisirdim.",
]

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
    model.download()
    model.load()
    return model.get_embedding_client()

def kileri_doldur(client, baglanti):
    imlec = baglanti.cursor()
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS belgeler (
            id INTEGER PRIMARY KEY,
            icerik TEXT,
            vektor TEXT
        )
    """)
    imlec.execute("DELETE FROM belgeler")

    cevap = client.generate_embeddings(CUMLELER)
    for cumle, eleman in zip(CUMLELER, cevap.data):
        vektor_yazisi = json.dumps(eleman.embedding)
        imlec.execute(
            "INSERT INTO belgeler (icerik, vektor) VALUES (?, ?)",
            (cumle, vektor_yazisi),
        )
    baglanti.commit()
    print(f"{len(CUMLELER)} cumle kilere yazildi.")

def ara(client, baglanti, soru):
    soru_vektoru = client.generate_embedding(soru).data[0].embedding

    imlec = baglanti.cursor()
    imlec.execute("SELECT icerik, vektor FROM belgeler")

    sonuclar = []
    for icerik, vektor_yazisi in imlec.fetchall():
        vektor = json.loads(vektor_yazisi)
        skor = kosinus_benzerligi(soru_vektoru, vektor)
        sonuclar.append((skor, icerik))

    sonuclar.sort(reverse=True)
    return sonuclar

def main():
    client = modeli_hazirla()
    baglanti = sqlite3.connect("kiler.db")

    kileri_doldur(client, baglanti)

    soru = "Evcil hayvanim hasta gibi, mamasina dokunmuyor."
    print()
    print(f"SORU: {soru}")
    for skor, icerik in ara(client, baglanti, soru):
        print(f"  {skor:.3f}  {icerik}")

    baglanti.close()

if __name__ == "__main__":
    main()