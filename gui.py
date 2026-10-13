import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from threading import Thread

class RestaurantFinder(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.geolocator = Nominatim(user_agent="studentska-prehrana")

        # Text input for location
        self.location_input = TextInput(hint_text="Vnesi svojo lokacijo", multiline=False)
        self.add_widget(self.location_input)

        # Search button
        self.search_button = Button(text="Najdi Restavracije")
        self.search_button.bind(on_press=self.find_restaurants)
        self.add_widget(self.search_button)

        # Label for results
        self.results_label = Label(text="Rezultati bodo prikazani tukaj")
        self.add_widget(self.results_label)

        # Load data
        self.data = np.genfromtxt("data/podatki2.txt", delimiter="@", encoding="utf-8", dtype=str)
        self.restaurants = {}

        for i in range(len(self.data[:, 0])):
            name = self.data[i, 0][1:]
            address = str(self.data[i, 1])
            price = float(self.data[i, 2].replace(",", ".")[0:3])
            coordinates = (
                float(self.data[i, 4].split()[0][1:-1]),
                float(self.data[i, 4].split()[1][:-1])
            )
            self.restaurants[name] = [i, address, price, coordinates, 0, 0]

    def find_restaurants(self, instance):
        user_location = self.location_input.text
        if not user_location:
            self.results_label.text = "Vnesi lokacijo!"
            return

        # Run geolocation in a separate thread
        Thread(target=self.calculate_distances, args=(user_location,)).start()

    def calculate_distances(self, user_location):
        try:
            location = self.geolocator.geocode(user_location)
            if not location:
                self.results_label.text = "Lokacija ni najdena!"
                return

            user_coordinates = (location.latitude, location.longitude)

            for name, data in self.restaurants.items():
                data[4] = geodesic(user_coordinates, data[3]).kilometers
                data[5] = 5 * np.exp(-2 * data[4]**2)

            # Sort by score
            sorted_restaurants = sorted(self.restaurants.items(), key=lambda x: x[1][5], reverse=True)

            # Display top 5 results
            self.results_label.text = "\n".join([f"{name}: {round(data[5], 3)}" for name, data in sorted_restaurants[:5]])

        except Exception as e:
            self.results_label.text = f"Napaka: {str(e)}"

class RestaurantApp(App):
    def build(self):
        return RestaurantFinder()

if __name__ == "__main__":
    RestaurantApp().run()
