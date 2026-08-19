from main import modelleri_hazirla, cevapla

TEST_SORULARI = [
    ("Cevaplanabilir", "Bu projede hangi veritabani kullaniliyor?"),
    ("Cevaplanabilir", "Program kac hafta suruyor?"),
    ("Cevaplanabilir", "Final sunumunda neler anlatilmali?"),
    ("Cevaplanabilir", "Bu projede embedding ne ise yariyor?"),
    ("Cevaplanabilir", "Foundry Local nedir?"),
    ("Cevaplanamaz", "Stajyerlere maas odeniyor mu?"),
    ("Cevaplanamaz", "Programa toplam kac ogrenci katiliyor?"),
    ("Cevaplanamaz", "Ofis hangi sehirde?"),
    ("Uc durum", "Merhaba, nasilsin?"),
    ("Uc durum", "asdfgh qwerty"),
]

def main():
    print("Modeller yukleniyor...")
    embed_client, chat_client = modelleri_hazirla()
    print(f"{len(TEST_SORULARI)} soru test edilecek.\n")

    satirlar = ["# Test Sonuclari\n"]
    for i, (kategori, soru) in enumerate(TEST_SORULARI, start=1):
        print(f"[{i}/{len(TEST_SORULARI)}] {soru}")
        try:
            cevap = cevapla(embed_client, chat_client, soru)
        except Exception as hata:
            cevap = f"HATA: {hata}"

        satirlar.append(f"## Soru {i} ({kategori})")
        satirlar.append(f"**Soru:** {soru}")
        satirlar.append(f"**Cevap:** {cevap}")
        satirlar.append("**Degerlendirme:** [ ] Basarili  [ ] Basarisiz — Not: ")
        satirlar.append("")

    with open("TEST_SONUCLARI.md", "w", encoding="utf-8") as dosya:
        dosya.write("\n".join(satirlar))

    print("\nBitti! Sonuclar TEST_SONUCLARI.md dosyasina yazildi.")

if __name__ == "__main__":
    main()