# Lačn.si

Scripts that recommend a place to eat from the Slovenian student meal-subsidy list (*študentska prehrana*). The recommendation uses distance, price, my own ratings and how long ago I last ate there.

This is the first, prototype version of Lačn.si (originally called *Prehrana*). It's plain Python, and all the data lives in `.txt` files. A FastAPI backend came later and is in [`server/`](server/). The code and comments are mostly in Slovenian.

Run everything from the repo root:

```bash
pip install -r requirements.txt
python prehrana.py
```

## Structure

```
prehrana.py                 CLI: asks for your location, prints a recommendation, a second choice
                            and a "wild card", then logs your visit to data/zgodovina.txt
gui.py                      Kivy window: type a location, get the top 5 by distance
gui_kivymd_prototype.py     KivyMD prototype with 5 hardcoded dummy restaurants

data/
  studentska-prehrana.txt   raw list (name, address, price, price without subsidy)
  podatki.txt               + coordinates, '&'-separated  (pipeline step 1)
  podatki2.txt              same, '@'-separated           (pipeline step 2)
  podatki2dumy.txt          two-line sample of podatki2.txt
  FMF-rating.txt            hand-rated subset (+ quality and quantity, 1–10)
  zgodovina.txt             last visit date per restaurant

pipeline/
  1_geocode.py              geocodes every address with Nominatim -> data/podatki.txt
  2_fix_separators.py       swaps the '&' separators for '@'       -> data/podatki2.txt
  3_update_history.py       adds new restaurants from FMF-rating.txt to zgodovina.txt
  upload_to_firebase.py     uploads podatki2.txt to Firestore (needs a service-account JSON, not included)

android/                    Kivy app meant for Android (see below)
experiments/
  Pridobivanje_ocen.ipynb   Google Places ratings (add your own API key), rich and thefuzz tests
  parse_latlng.py           parses a "LatLng(lat: .., lng: ..)" string

server/                     the later FastAPI backend (see below)
```

## Score (`prehrana.py`)

```
10*exp(-0.5*distance^4) + quality + 0.7*quantity + 3/(1+price) - 8/(1+days_since_last_visit^2)
```

## Android app

`android/main.py` lets you set max price, min rating, max distance and cuisine with sliders. It then shows the top 5 from `android/data/rating.txt`, scored as:

```
rating*0.35 + price_score*0.25 + popularity*0.20 + distance_score*0.15 + cuisine_bonus*0.05
```

`android/demo_algorithm.py` runs the same algorithm on sample data in the terminal.

```bash
cd android
python main.py                  # desktop
buildozer android debug         # build APK
```

## Later: the server

The idea later moved to a small FastAPI backend. It ranks restaurants by rating, distance and time since your last visit, and can read them from Firestore (the data that `pipeline/upload_to_firebase.py` uploads). It has its own requirements, Dockerfile and Procfile. See [`server/README.md`](server/README.md) for how to run it and what the endpoints are.
