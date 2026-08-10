from foundry_local_sdk import Configuration, FoundryLocalManager
import math

EMBED_MODEL = "qwen3-embedding-0.6b"

def kosinus_benzerligi(v1, v2):
    carpim_toplami = 0
    boy1 = 0
    boy2 = 0
    for a, b in zip(v1, v2):
        carpim_toplami += a * b
        boy1 += a * a
        boy2 += b * b
    return carpim_toplami / (math.sqrt(boy1) * math.sqrt(boy2))

def main():
    config = Configuration(
        app_name="local-rag-assistant",
        model_cache_dir=r"C:\Users\oguzh\.foundry\cache\models",
    )
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps(names=["CUDAExecutionProvider"])

    model = manager.catalog.get_model(EMBED_MODEL)
    if model is None:
        print(f"Model bulunamadi: {EMBED_MODEL}")
        return

    for varyant in model.variants:
        if "cuda" in varyant.id:
            model.select_variant(varyant)

    print("Embedding modeli indiriliyor (ilk seferde ~478 MB)...")
    model.download()
    print("Model yukleniyor...")
    model.load()

    client = model.get_embedding_client()

    cumleler = [
        "Kedim mama yemiyor, cok istahsiz.",
        "Bugun hava cok guzel, yuruyuse cikacagim.",
        "Python ile programlama ogreniyorum.",
        "Arabamin lastigi patladi, tamirciye gittim.",
        "Aksam yemeginde makarna pisirdim.",
    ]
    soru = "Evcil hayvanim hasta gibi, mamasina dokunmuyor."

    print("Cumleler haritaya yerlestiriliyor...")
    cevap = client.generate_embeddings(cumleler)
    cumle_vektorleri = [eleman.embedding for eleman in cevap.data]

    soru_vektoru = client.generate_embedding(soru).data[0].embedding

    print()
    print(f"SORU: {soru}")
    print()
    for cumle, vektor in zip(cumleler, cumle_vektorleri):
        skor = kosinus_benzerligi(soru_vektoru, vektor)
        print(f"  {skor:.3f}  {cumle}")

if __name__ == "__main__":
    main()