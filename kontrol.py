import sqlite3

baglanti = sqlite3.connect("rag.db")
sorgu = "SELECT icerik FROM parcalar WHERE kaynak = '02_takvim_ve_fazlar.txt'"
for (icerik,) in baglanti.execute(sorgu):
    print("-", icerik[:120])
baglanti.close()