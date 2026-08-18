from foundry_local_sdk import Configuration, FoundryLocalManager

CHAT_MODEL = "qwen3-4b"

def modeli_hazirla():
    config = Configuration(
        app_name="local-rag-assistant",
        model_cache_dir=r"C:\Users\oguzh\.foundry\cache\models",
    )
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance
    manager.download_and_register_eps(names=["CUDAExecutionProvider"])

    model = manager.catalog.get_model(CHAT_MODEL)
    for varyant in model.variants:
        if "cuda" in varyant.id:
            model.select_variant(varyant)
    model.download()
    model.load()
    return model.get_chat_client()

def sor(client, sistem_mesaji, kullanici_mesaji):
    cevap = client.complete_chat(
        messages=[
            {"role": "system", "content": sistem_mesaji},
            {"role": "user", "content": kullanici_mesaji},
        ]
    )
    metin = cevap.choices[0].message.content
    if "</think>" in metin:
        metin = metin.split("</think>")[-1]
    return metin.strip()

def main():
    client = modeli_hazirla()

    baglam = (
        "The internship program starts on July 1st and lasts 4 weeks. "
        "Interns come to the office 3 days a week. "
        "Each team gives a presentation at the end of the program."
    )

    kurallar = (
        "You are a question-answering assistant. "
        "Answer ONLY using the information given as CONTEXT. "
        "If the answer is not in the context, reply with EXACTLY this sentence: 'I do not have that information.' "
        "Answer in the same language as the question. Keep answers short."
    )

    print("=== DENEY 1: Kuralsiz, baglamsiz ===")
    print(sor(client, "Sen yardimsever bir asistansin.", "Stajyerlerin maasi ne kadar?"))
    print()

    print("=== DENEY 2: Kuralli + baglamli, cevap baglamda VAR ===")
    print(sor(client, kurallar, f"CONTEXT: {baglam}\n\nSORU: Staj programi ne zaman baslar?"))
    print()

    print("=== DENEY 3: Kuralli + baglamli, cevap baglamda YOK ===")
    print(sor(client, kurallar, f"CONTEXT: {baglam}\n\nSORU: Stajyerlerin maasi ne kadar?"))

if __name__ == "__main__":
    main()