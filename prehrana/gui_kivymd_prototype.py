from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import MDList, ThreeLineListItem
from kivy.uix.scrollview import ScrollView
import plyer
import math
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout

# Simulacija GPS-a za Windows, na Androidu uporabimo dejanski GPS
def get_location():
    try:
        loc = plyer.gps.get_location()
        return loc['lat'], loc['lon']
    except:
        return 46.0511, 14.5051  # Ljubljana

# Seznam restavracij
restaurants = [
    {"name": "Restavracija A", "address": "Trg republike 1", "price": 5, "coords": (46.0511, 14.5051)},
    {"name": "Restavracija B", "address": "Slovenska cesta 10", "price": 6, "coords": (46.0525, 14.5037)},
    {"name": "Restavracija C", "address": "Čopova ulica 5", "price": 4, "coords": (46.0530, 14.5055)},
    {"name": "Restavracija D", "address": "Tivolska cesta 12", "price": 7, "coords": (46.0580, 14.5012)},
    {"name": "Restavracija E", "address": "Dunajska cesta 20", "price": 5, "coords": (46.0650, 14.5100)},
]

def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

class MainScreen(Screen):
    def show_restaurants(self):
        user_lat, user_lon = get_location()
        sorted_restaurants = sorted(restaurants, key=lambda r: distance(user_lat, user_lon, r['coords'][0], r['coords'][1]))
        self.ids.restaurant_list.clear_widgets()
        for r in sorted_restaurants[:5]:
            item = ThreeLineListItem(text=r['name'], secondary_text=r['address'], tertiary_text=f"Cena: {r['price']} EUR")
            self.ids.restaurant_list.add_widget(item)

class RestaurantApp(MDApp):
    def build(self):
        return Builder.load_string('''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            title: "Restavracije"
        BoxLayout:
            orientation: "vertical"
            ScrollView:
                MDList:
                    id: restaurant_list
            MDRaisedButton:
                text: "Osveži"
                size_hint_y: None
                height: "48dp"
                on_release: root.show_restaurants()
''')

if __name__ == "__main__":
    RestaurantApp().run()
