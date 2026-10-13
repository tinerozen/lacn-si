import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("lacn-si-1-firebase-adminsdk-fbsvc-b420610c07.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 📂 Preberi datoteko
with open("data/podatki2.txt", "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]


# 📤 Pošlji v Firestore
for line in lines:
    parts = line.split("@")
    print(parts)
    
    
    ime = parts[0][1:]
    naslov = parts[1]
    cena = float(parts[2].rsplit(" ")[0].replace(",","."))
    cena_brez = float(parts[3].rsplit(" ")[0].replace(",","."))
    lokacija = parts[4]


    doc = {
        "restavracija_ime": ime,
        "restavracija_naslov": naslov,
        "restavracija_cena": cena,
        "restavracija_cena_brez_subvencije": cena_brez,
        "restavracija_lokacija_string": lokacija,
        "restavracija_rating": 5.0

    }
    print(doc)

    db.collection("restavracije").add(doc)
    print(f"✅ Dodano: {ime}")

print("🎉 Uvoz končan!")