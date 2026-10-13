import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

data = np.genfromtxt("data/studentska-prehrana.txt", delimiter="\",\"", encoding="utf-8", dtype=str)


def compute_value(row):
    geolocator = Nominatim(user_agent="studentska-prehrana")
    
    lokacija1 = geolocator.geocode(row[1])

    
    if lokacija1 == None:
        print(str((0, 0)))
        return str((0, 0))
    koordinate1 = (lokacija1.latitude, lokacija1.longitude)

    print(koordinate1)
    time.sleep(1.5)
    return str((lokacija1.latitude, lokacija1.longitude))


new_column = np.array([compute_value(row) for row in data])[:, np.newaxis]
data = np.hstack((data, new_column))



print(data)


np.savetxt("data/podatki.txt", data, fmt='%s', encoding="utf-8", delimiter="&")
