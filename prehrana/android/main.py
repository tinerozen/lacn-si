from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
import os
import math

# Set window size for testing (remove for mobile)
Window.size = (400, 600)

file_path = os.path.join(os.path.dirname(__file__), "data", "rating.txt")

class RestaurantRecommender:
    def __init__(self):
        self.restaurants = self.load_restaurants()
    
    def load_restaurants(self):
        restaurants = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    parts = line.strip().split("@")
                    if len(parts) >= 6:
                        name = parts[0].strip('"')
                        address = parts[1]
                        price_range = parts[2]
                        max_price = parts[3]
                        coords = parts[4]
                        rating = float(parts[5])
                        popularity = float(parts[6]) if len(parts) > 6 else 5.0
                        
                        # Parse coordinates
                        try:
                            lat, lon = coords.strip('()').split(',')
                            lat, lon = float(lat), float(lon)
                        except:
                            lat, lon = 0, 0
                        
                        # Parse price
                        try:
                            price = float(price_range.split()[0].replace(',', '.'))
                        except:
                            price = 5.0
                        
                        # Determine cuisine type from name
                        cuisine_type = self.determine_cuisine(name)
                        
                        restaurants.append({
                            'name': name,
                            'address': address,
                            'price': price,
                            'max_price': max_price,
                            'lat': lat,
                            'lon': lon,
                            'rating': rating,
                            'popularity': popularity,
                            'cuisine': cuisine_type
                        })
        except Exception as e:
            print(f"Error loading restaurants: {e}")
        
        return restaurants
    
    def determine_cuisine(self, name):
        """Determine cuisine type based on restaurant name"""
        name_lower = name.lower()
        if any(word in name_lower for word in ['pizza', 'pizzeria', 'laterna']):
            return 'Italian'
        elif any(word in name_lower for word in ['kitajska', 'shanghai']):
            return 'Chinese'
        elif any(word in name_lower for word in ['burek', 'okrepčevalnica']):
            return 'Fast Food'
        elif any(word in name_lower for word in ['menza', 'gostilnica', 'restavracija']):
            return 'Local'
        else:
            return 'Other'
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return float('inf')
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def recommend(self, max_price=10.0, min_rating=5.0, cuisine_preference=None, 
                  user_lat=46.0569, user_lon=14.5058, max_distance=5.0):
        """
        Recommend restaurants based on user preferences
        """
        if not self.restaurants:
            return []
        
        # Filter restaurants based on criteria
        filtered = []
        for restaurant in self.restaurants:
            # Price filter
            if restaurant['price'] > max_price:
                continue
            
            # Rating filter
            if restaurant['rating'] < min_rating:
                continue
            
            # Distance filter
            distance = self.calculate_distance(
                user_lat, user_lon, 
                restaurant['lat'], restaurant['lon']
            )
            if distance > max_distance:
                continue
            
            # Cuisine filter
            if cuisine_preference and cuisine_preference != 'Any':
                if restaurant['cuisine'] != cuisine_preference:
                    continue
            
            # Calculate score based on multiple factors
            score = self.calculate_score(
                restaurant, max_price, min_rating, 
                cuisine_preference, distance
            )
            restaurant['score'] = score
            restaurant['distance'] = distance
            filtered.append(restaurant)
        
        # Sort by score (higher is better)
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        return filtered[:5]  # Return top 5 recommendations
    
    def calculate_score(self, restaurant, max_price, min_rating, cuisine_preference, distance):
        """
        Calculate recommendation score based on multiple factors
        """
        score = 0.0
        
        # Rating factor (35% weight)
        rating_score = restaurant['rating'] / 10.0
        score += rating_score * 0.35
        
        # Price factor (25% weight) - lower price gets higher score
        price_score = 1.0 - (restaurant['price'] / max_price)
        score += price_score * 0.25
        
        # Popularity factor (20% weight)
        popularity_score = restaurant['popularity'] / 10.0
        score += popularity_score * 0.20
        
        # Distance factor (15% weight) - closer gets higher score
        if distance != float('inf'):
            distance_score = 1.0 - (distance / 5.0)  # Normalize to 5km max
            distance_score = max(0, distance_score)
            score += distance_score * 0.15
        
        # Cuisine preference bonus (5% weight)
        if cuisine_preference and cuisine_preference != 'Any':
            if restaurant['cuisine'] == cuisine_preference:
                score += 0.05
        
        return score

class RestaurantCard(BoxLayout):
    def __init__(self, restaurant, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.padding = dp(10)
        self.spacing = dp(5)
        
        # Restaurant name
        name_label = Label(
            text=restaurant['name'],
            size_hint_y=None, height=dp(25),
            font_size='16sp', bold=True,
            halign='left'
        )
        self.add_widget(name_label)
        
        # Details grid
        details_grid = GridLayout(cols=2, size_hint_y=None, height=dp(80))
        
        # Address
        details_grid.add_widget(Label(text='Address:', size_hint_y=None, height=dp(20), halign='left'))
        details_grid.add_widget(Label(text=restaurant['address'], size_hint_y=None, height=dp(20), halign='left'))
        
        # Price
        details_grid.add_widget(Label(text='Price:', size_hint_y=None, height=dp(20), halign='left'))
        details_grid.add_widget(Label(text=f"{restaurant['price']:.2f} EUR", size_hint_y=None, height=dp(20), halign='left'))
        
        # Rating
        details_grid.add_widget(Label(text='Rating:', size_hint_y=None, height=dp(20), halign='left'))
        details_grid.add_widget(Label(text=f"{restaurant['rating']:.1f}/10", size_hint_y=None, height=dp(20), halign='left'))
        
        # Distance
        if 'distance' in restaurant:
            details_grid.add_widget(Label(text='Distance:', size_hint_y=None, height=dp(20), halign='left'))
            details_grid.add_widget(Label(text=f"{restaurant['distance']:.1f} km", size_hint_y=None, height=dp(20), halign='left'))
        
        self.add_widget(details_grid)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recommender = RestaurantRecommender()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Title
        title = Label(
            text='🍽️ Restaurant Recommender',
            size_hint_y=None, height=dp(50),
            font_size='22sp', bold=True
        )
        main_layout.add_widget(title)
        
        # Preferences section
        preferences_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Price preference
        price_label = Label(text='💰 Maximum Price (EUR):', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(price_label)
        
        self.price_slider = Slider(min=1, max=15, value=10, step=0.5)
        self.price_slider.bind(value=self.on_price_change)
        preferences_layout.add_widget(self.price_slider)
        
        self.price_value = Label(text='10.0 EUR', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(self.price_value)
        
        # Rating preference
        rating_label = Label(text='⭐ Minimum Rating:', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(rating_label)
        
        self.rating_slider = Slider(min=1, max=10, value=5, step=0.5)
        self.rating_slider.bind(value=self.on_rating_change)
        preferences_layout.add_widget(self.rating_slider)
        
        self.rating_value = Label(text='5.0', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(self.rating_value)
        
        # Distance preference
        distance_label = Label(text='📍 Maximum Distance (km):', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(distance_label)
        
        self.distance_slider = Slider(min=1, max=10, value=5, step=0.5)
        self.distance_slider.bind(value=self.on_distance_change)
        preferences_layout.add_widget(self.distance_slider)
        
        self.distance_value = Label(text='5.0 km', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(self.distance_value)
        
        # Cuisine preference
        cuisine_label = Label(text='🍕 Cuisine Preference:', size_hint_y=None, height=dp(30))
        preferences_layout.add_widget(cuisine_label)
        
        self.cuisine_spinner = Spinner(
            text='Any',
            values=('Any', 'Italian', 'Chinese', 'Local', 'Fast Food', 'Other'),
            size_hint_y=None, height=dp(40)
        )
        preferences_layout.add_widget(self.cuisine_spinner)
        
        main_layout.add_widget(preferences_layout)
        
        # Recommend button
        recommend_btn = Button(
            text='🔍 Get Recommendations',
            size_hint_y=None, height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='16sp'
        )
        recommend_btn.bind(on_press=self.get_recommendations)
        main_layout.add_widget(recommend_btn)
        
        # Results section
        results_label = Label(
            text='Click "Get Recommendations" to see restaurant suggestions',
            size_hint_y=None, height=dp(30),
            font_size='14sp'
        )
        main_layout.add_widget(results_label)
        
        # Scrollable results area
        self.results_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        self.results_layout.size_hint_y = None
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.results_layout)
        main_layout.add_widget(scroll_view)
        
        self.add_widget(main_layout)
    
    def on_price_change(self, instance, value):
        self.price_value.text = f'{value:.1f} EUR'
    
    def on_rating_change(self, instance, value):
        self.rating_value.text = f'{value:.1f}'
    
    def on_distance_change(self, instance, value):
        self.distance_value.text = f'{value:.1f} km'
    
    def get_recommendations(self, instance):
        # Clear previous results
        self.results_layout.clear_widgets()
        
        max_price = self.price_slider.value
        min_rating = self.rating_slider.value
        max_distance = self.distance_slider.value
        cuisine_preference = self.cuisine_spinner.text
        
        # Default location (Ljubljana center)
        user_lat, user_lon = 46.0569, 14.5058
        
        recommendations = self.recommender.recommend(
            max_price=max_price,
            min_rating=min_rating,
            cuisine_preference=cuisine_preference,
            user_lat=user_lat,
            user_lon=user_lon,
            max_distance=max_distance
        )
        
        if not recommendations:
            no_results = Label(
                text='❌ No restaurants found matching your criteria.\nTry adjusting your preferences.',
                size_hint_y=None, height=dp(60),
                font_size='14sp'
            )
            self.results_layout.add_widget(no_results)
            return
        
        # Add results header
        header = Label(
            text=f'🎯 Top {len(recommendations)} Recommendations:',
            size_hint_y=None, height=dp(40),
            font_size='16sp', bold=True
        )
        self.results_layout.add_widget(header)
        
        # Add restaurant cards
        for i, restaurant in enumerate(recommendations, 1):
            # Create card container
            card_container = BoxLayout(orientation='vertical', spacing=dp(5))
            card_container.size_hint_y = None
            card_container.height = dp(140)
            
            # Add ranking
            ranking = Label(
                text=f'#{i} (Score: {restaurant["score"]:.2f})',
                size_hint_y=None, height=dp(25),
                font_size='14sp', bold=True,
                color=(0.2, 0.6, 1, 1)
            )
            card_container.add_widget(ranking)
            
            # Add restaurant card
            card = RestaurantCard(restaurant)
            card_container.add_widget(card)
            
            self.results_layout.add_widget(card_container)

class DetailsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20))
        
        title = Label(text='Restaurant Details', size_hint_y=None, height=dp(50))
        layout.add_widget(title)
        
        back_btn = Button(
            text='← Back to Home',
            size_hint_y=None, height=dp(50)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'home'

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DetailsScreen(name="details"))
        return sm

if __name__ == "__main__":
    MyApp().run() 