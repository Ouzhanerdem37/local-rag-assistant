import json
import sqlite3
from pathlib import Path

from foundry_local_sdk import Configuration, FoundryLocalManager

EMBED_MODEL = "qwen3-embedding-0.6b"
DB_DOSYASI = "rag.db"
BELGE_KLASORU = "belgeler"

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

def parcala(metin):
    paragraflar = metin.split("\n\n")
    return [p.strip() for p in paragraflar if p.strip()]

def main():
    client = modeli_hazirla()

    baglanti = sqlite3.connect(DB_DOSYASI)
    imlec = baglanti.cursor()
    imlec.execute("""
        CREATE TABLE IF NOT EXISTS parcalar (
            id INTEGER PRIMARY KEY,
            kaynak TEXT,
            icerik TEXT,
            vektor TEXT
        )
    """)
    imlec.execute("DELETE FROM parcalar")

    toplam = 0
    for dosya in sorted(Path(BELGE_KLASORU).glob("*.txt")):
        metin = dosya.read_text(encoding="utf-8")
        parcalar = parcala(metin)

        cevap = client.generate_embeddings(parcalar)
        for parca, eleman in zip(parcalar, cevap.data):
            imlec.execute(
                "INSERT INTO parcalar (kaynak, icerik, vektor) VALUES (?, ?, ?)",
                (dosya.name, parca, json.dumps(eleman.embedding)),
            )

        toplam += len(parcalar)
        print(f"{dosya.name}: {len(parcalar)} parca")

    baglanti.commit()
    baglanti.close()
    print(f"Toplam {toplam} parca kilere yazildi.")

if __name__ == "__main__":
    main()