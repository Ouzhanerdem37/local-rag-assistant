from foundry_local_sdk import Configuration, FoundryLocalManager

MODEL = "qwen2.5-0.5b"

def main():
    config = Configuration(
        app_name="local-rag-assistant",
        model_cache_dir=r"C:\Users\oguzh\.foundry\cache\models",
    )
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    sonuc = manager.download_and_register_eps(names=["CUDAExecutionProvider"])
    print("Motor kaydi:", sonuc.status)

    model = manager.catalog.get_model(MODEL)
    if model is None:
        print(f"Model bulunamadi: {MODEL}")
        return

    cuda_varyant = None
    for varyant in model.variants:
        if "cuda" in varyant.id:
            cuda_varyant = varyant

    if cuda_varyant is None:
        print("CUDA varyanti bulunamadi.")
        return

    model.select_variant(cuda_varyant)
    print("Secilen varyant:", cuda_varyant.id)

    print("Model indiriliyor (cache'te varsa atlanir)...")
    model.download()

    print("Model bellege yukleniyor...")
    model.load()

    client = model.get_chat_client()

    cevap = client.complete_chat(
        messages=[
            {"role": "user", "content": "Hello! Introduce yourself in two sentences."}
        ]
    )

    print(cevap.choices[0].message.content)

if __name__ == "__main__":
    main()