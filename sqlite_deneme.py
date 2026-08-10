import sqlite3

def main():
    baglanti = sqlite3.connect("deneme.db")
    imlec = baglanti.cursor()

    imlec.execute("""
        CREATE TABLE IF NOT EXISTS belgeler (
            id INTEGER PRIMARY KEY,
            icerik TEXT
        )
    """)

    imlec.execute("DELETE FROM belgeler")

    imlec.execute("INSERT INTO belgeler (icerik) VALUES (?)", ("Kedim mama yemiyor.",))
    imlec.execute("INSERT INTO belgeler (icerik) VALUES (?)", ("Bugun hava cok guzel.",))
    imlec.execute("INSERT INTO belgeler (icerik) VALUES (?)", ("Python ogreniyorum.",))
    baglanti.commit()

    imlec.execute("SELECT id, icerik FROM belgeler")
    for satir in imlec.fetchall():
        print(satir)

    imlec.execute("SELECT id, icerik FROM belgeler WHERE icerik LIKE ?", ("%mama%",))
    print("Filtreli sonuc:", imlec.fetchall())

    baglanti.close()

if __name__ == "__main__":
    main()