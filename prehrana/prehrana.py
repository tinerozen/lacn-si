import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random as rd
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
from thefuzz import process

today_date = datetime.today().strftime("%Y-%m-%d")

zgodovina_fname = "data/zgodovina.txt"

data = np.genfromtxt("data/FMF-rating.txt", delimiter="@", encoding="utf-8", dtype=str)
zgodovina_import = np.genfromtxt(zgodovina_fname, delimiter="@", encoding="utf-8", dtype=str)

zgodovina = {}

for i in range(len(zgodovina_import[:,0])):
    visit_date = datetime.strptime(zgodovina_import[i,1], "%Y-%m-%d")
    zgodovina[zgodovina_import[i,0][1:]] = visit_date
    #print((datetime.today() - zgodovina[zgodovina_import[i,0][1:]]).days)


def razdalja(naslov, koordinate):
    geolocator = Nominatim(user_agent="studentska-prehrana")
    lokacija1 = geolocator.geocode(naslov)
    
    if not lokacija1:
        return None  # Če en naslov ni najden, vrni None
    
    koordinate1 = (lokacija1.latitude, lokacija1.longitude)
    
    return geodesic(koordinate1, koordinate).kilometers

slovar = {}


#   Oblika slovarja: Ime lokala: [zaporedna številka, naslov, cena doplačila, koordinate, razdalja od uporabnika, score, kvaliteta, količina, zadnji obisk pred]

for i in range(len(data[:,0])):



    slovar[data[i,0][1:]] = {"zaporednaštevilka": i, "naslov": str(data[i,1]), "cena": float(data[i,2].replace(",", ".")[0:3]), "koordinate":
                             (float(data[i,4].split()[0][1:-1]), float(data[i,4].split()[1][:-1])),
                              "razdalja_": 0, "score_ ":0, "kvaliteta": float(data[i,5]), "količina": float(data[i,6])}

    data[i,0] = data[i,0][1:]
    data[i,2] = float(data[i,2].replace(",", ".")[0:3])



for lokal in slovar.keys():

    slovar[lokal]["zadnji obisk pred"] = (datetime.today() - zgodovina[lokal]).days


lokacija = input("\nTvoja trenutna lokacija?: ")
print("")
geolocator = Nominatim(user_agent="studentska-prehrana")
lokacija1 = geolocator.geocode(lokacija)
koordinate = (lokacija1.latitude, lokacija1.longitude)

for lokal in slovar.keys():
    slovar[lokal]["razdalja_"] = geodesic(koordinate, slovar[lokal]["koordinate"]).kilometers

def score(vrstica):
    return 10*np.exp(-0.5*vrstica["razdalja_"]**4)+vrstica["kvaliteta"]+0.7*vrstica["količina"]+3/(1+vrstica["cena"]) - 8/(1+vrstica["zadnji obisk pred"]**2)

randomized_slovar = slovar.copy()

for lokal in slovar.keys():
    slovar[lokal]["score_"] = score(slovar[lokal])

sorted_slovar = dict(sorted(slovar.items(), reverse=True, key=lambda item: item[1]["score_"]))



console = Console()


razdalja_priporočila = round(sorted_slovar[list(sorted_slovar.keys())[0]]["razdalja_"], 1)

panel = Panel("\n[bold]" + list(sorted_slovar.keys())[0] + "[/bold]\n", title="Priporočena restavracija",
              subtitle=f"{razdalja_priporočila} km", expand=True)
console.print(panel, justify="center")

#console.print("Priporočena restavracija: [bold]" + list(sorted_slovar.keys())[0] + "[/bold]")
      #+ str(round(sorted_slovar[list(sorted_slovar.keys())[0]]["score_"], 3)))

print("")

console.print("Druga izbira: [bold]" + list(sorted_slovar.keys())[1] + "[/bold]   ")
      #+ str(round(sorted_slovar[ime]["score_"], 3)))

print("")

console.print("Wild card: " + rd.choice(list(sorted_slovar.keys())[2:7]))

print("")

#  ----------- CELOTEN SEZNAM -----------
# for ime in list(sorted_slovar.keys()):
#     print(ime + "   " + str(round(sorted_slovar[ime]["score_"], 3)))


obisk_b = input(f"\nAli zabeležim obisk {list(sorted_slovar.keys())[0]}?(y/n): ")


def popravi(vnos, zgodovina):
    best_match, score = process.extractOne(vnos, list(zgodovina.keys()))
    if score > 80:
        return best_match
    else:
        ponovni_vnos = input("Nisem razumel, lahko še enkrat: ")
        if ponovni_vnos == "None" or ponovni_vnos == "none": exit()
        return popravi(ponovni_vnos, zgodovina)

    

if obisk_b.lower() == "y":
    zgodovina[list(sorted_slovar.keys())[0]] = datetime.today()
    with open(zgodovina_fname, "w", encoding="utf-8") as f:
        for lokal in zgodovina.keys():
            date = zgodovina[lokal].strftime("%Y-%m-%d")
            f.write(f"\"{lokal}@{date}\n")
else:
    obiskana_rest = input("\nKatero restavracijo zabeležim?: ")
    if obiskana_rest == "None" or obiskana_rest == "none" or obiskana_rest == "Nobeno" or obiskana_rest == "nobeno":
        exit()
    

    obiskana_rest = popravi(obiskana_rest, zgodovina)


    zgodovina[obiskana_rest] = datetime.today()

    with open(zgodovina_fname, "w", encoding="utf-8") as f:
        for lokal in zgodovina.keys():
            date = zgodovina[lokal].strftime("%Y-%m-%d")
            f.write(f"\"{lokal}@{date}\n")
