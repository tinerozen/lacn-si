import numpy as np

str_pos = "LatLng(lat: 14.0, lng: 18.0)"

def convert_position_str(pos_str):
    lat = 0.0
    lng = 0.0
    sez = pos_str.rsplit(": ")
    lat = float(sez[1].rsplit(", ")[0])
    lng = float(sez[-1].rsplit(")")[0])
    return lat, lng

la, ln = convert_position_str(str_pos)

print(la)
print(ln)
