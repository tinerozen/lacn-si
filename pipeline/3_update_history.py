import os

# Imena datotek
rating_file = "data/FMF-rating.txt"
history_file = "data/zgodovina.txt"
default_date = "2025-01-01"  # Privzet datum za nove restavracije

# Preberi seznam restavracij iz rating.txt
rating_restaurants = set()
if os.path.exists(rating_file):
    with open(rating_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("@")
            if parts:
                restaurant_name = parts[0]  # Ime restavracije je pred prvim '@'
                rating_restaurants.add(restaurant_name)
else:
    print(f"Napaka: Datoteka {rating_file} ne obstaja!")
    exit()

# Preberi seznam iz zgodovina.txt
history_restaurants = {}
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("@")
            if len(parts) == 2:
                name, date = parts
                history_restaurants[name] = date

# Dodaj manjkajoče restavracije s privzetim datumom
new_entries = rating_restaurants - history_restaurants.keys()
if new_entries:
    with open(history_file, "a", encoding="utf-8") as f:
        for restaurant in sorted(new_entries):
            f.write(f"{restaurant}@{default_date}\n")
    print(f"Dodane nove restavracije: {', '.join(new_entries)}")
else:
    print("Ni novih restavracij za dodati.")
