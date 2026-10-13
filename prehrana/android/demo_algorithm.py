#!/usr/bin/env python3
"""
Demo script showing how the restaurant recommendation algorithm works
"""

import math

class RestaurantRecommender:
    def __init__(self):
        # Sample restaurant data
        self.restaurants = [
            {
                'name': 'Restavracija Menza IJS',
                'address': 'Jamova cesta 39, 1000 Ljubljana',
                'price': 4.10,
                'lat': 46.0421851,
                'lon': 14.4891359,
                'rating': 7.0,
                'popularity': 7.0,
                'cuisine': 'Local'
            },
            {
                'name': 'Pizzeria Laterna',
                'address': 'Tržaška 79a, 1000 Ljubljana',
                'price': 4.90,
                'lat': 46.0474461,
                'lon': 14.4952444,
                'rating': 8.0,
                'popularity': 9.0,
                'cuisine': 'Italian'
            },
            {
                'name': 'Kitajska restavracija Leteča zvezda',
                'address': 'Cesta v mestni log 55, 1000 Ljubljana',
                'price': 4.62,
                'lat': 46.0363814,
                'lon': 14.4898423,
                'rating': 6.0,
                'popularity': 5.0,
                'cuisine': 'Chinese'
            },
            {
                'name': 'Burek Olimpija Rimska',
                'address': 'Rimska cesta 13, 1000 Ljubljana',
                'price': 0.70,
                'lat': 46.0474028,
                'lon': 14.4998954,
                'rating': 6.0,
                'popularity': 7.0,
                'cuisine': 'Fast Food'
            },
            {
                'name': 'Gostilnica Meta in Bazilika',
                'address': 'Snežniška ulica 1, 1000 Ljubljana',
                'price': 4.90,
                'lat': 46.0475751,
                'lon': 14.4978493,
                'rating': 8.0,
                'popularity': 8.0,
                'cuisine': 'Local'
            }
        ]
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def calculate_score(self, restaurant, max_price, min_rating, cuisine_preference, distance):
        """Calculate recommendation score based on multiple factors"""
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
    
    def recommend(self, max_price=10.0, min_rating=5.0, cuisine_preference=None, 
                  user_lat=46.0569, user_lon=14.5058, max_distance=5.0):
        """Recommend restaurants based on user preferences"""
        
        print(f"\n🔍 Searching for restaurants with criteria:")
        print(f"   💰 Max Price: {max_price} EUR")
        print(f"   ⭐ Min Rating: {min_rating}/10")
        print(f"   📍 Max Distance: {max_distance} km")
        print(f"   🍕 Cuisine: {cuisine_preference}")
        print(f"   📍 User Location: ({user_lat}, {user_lon})")
        print("-" * 60)
        
        # Filter and score restaurants
        filtered = []
        for restaurant in self.restaurants:
            # Price filter
            if restaurant['price'] > max_price:
                print(f"❌ {restaurant['name']} - Too expensive (€{restaurant['price']:.2f})")
                continue
            
            # Rating filter
            if restaurant['rating'] < min_rating:
                print(f"❌ {restaurant['name']} - Rating too low ({restaurant['rating']:.1f}/10)")
                continue
            
            # Distance filter
            distance = self.calculate_distance(
                user_lat, user_lon, 
                restaurant['lat'], restaurant['lon']
            )
            if distance > max_distance:
                print(f"❌ {restaurant['name']} - Too far ({distance:.1f} km)")
                continue
            
            # Cuisine filter
            if cuisine_preference and cuisine_preference != 'Any':
                if restaurant['cuisine'] != cuisine_preference:
                    print(f"❌ {restaurant['name']} - Wrong cuisine ({restaurant['cuisine']})")
                    continue
            
            # Calculate score
            score = self.calculate_score(
                restaurant, max_price, min_rating, 
                cuisine_preference, distance
            )
            restaurant['score'] = score
            restaurant['distance'] = distance
            filtered.append(restaurant)
            
            print(f"✅ {restaurant['name']} - Score: {score:.3f}")
        
        # Sort by score
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        return filtered

def demo_recommendations():
    """Demonstrate the recommendation algorithm with different scenarios"""
    
    recommender = RestaurantRecommender()
    
    # Scenario 1: Budget-conscious user
    print("=" * 60)
    print("SCENARIO 1: Budget-conscious user (max €3, any cuisine)")
    print("=" * 60)
    
    recommendations = recommender.recommend(
        max_price=3.0,
        min_rating=5.0,
        cuisine_preference='Any',
        max_distance=5.0
    )
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for i, restaurant in enumerate(recommendations, 1):
        print(f"{i}. {restaurant['name']}")
        print(f"   📍 {restaurant['address']}")
        print(f"   💰 €{restaurant['price']:.2f} | ⭐ {restaurant['rating']:.1f}/10 | 📍 {restaurant['distance']:.1f}km")
        print(f"   🍕 {restaurant['cuisine']} | 🎯 Score: {restaurant['score']:.3f}")
        print()
    
    # Scenario 2: Italian food lover
    print("=" * 60)
    print("SCENARIO 2: Italian food lover (any price, high rating)")
    print("=" * 60)
    
    recommendations = recommender.recommend(
        max_price=15.0,
        min_rating=7.0,
        cuisine_preference='Italian',
        max_distance=5.0
    )
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for i, restaurant in enumerate(recommendations, 1):
        print(f"{i}. {restaurant['name']}")
        print(f"   📍 {restaurant['address']}")
        print(f"   💰 €{restaurant['price']:.2f} | ⭐ {restaurant['rating']:.1f}/10 | 📍 {restaurant['distance']:.1f}km")
        print(f"   🍕 {restaurant['cuisine']} | 🎯 Score: {restaurant['score']:.3f}")
        print()
    
    # Scenario 3: Quality seeker
    print("=" * 60)
    print("SCENARIO 3: Quality seeker (high rating, any cuisine)")
    print("=" * 60)
    
    recommendations = recommender.recommend(
        max_price=10.0,
        min_rating=8.0,
        cuisine_preference='Any',
        max_distance=3.0
    )
    
    print(f"\n🎯 TOP RECOMMENDATIONS:")
    for i, restaurant in enumerate(recommendations, 1):
        print(f"{i}. {restaurant['name']}")
        print(f"   📍 {restaurant['address']}")
        print(f"   💰 €{restaurant['price']:.2f} | ⭐ {restaurant['rating']:.1f}/10 | 📍 {restaurant['distance']:.1f}km")
        print(f"   🍕 {restaurant['cuisine']} | 🎯 Score: {restaurant['score']:.3f}")
        print()

def explain_algorithm():
    """Explain how the scoring algorithm works"""
    print("=" * 60)
    print("ALGORITHM EXPLANATION")
    print("=" * 60)
    
    print("""
The recommendation algorithm uses a weighted scoring system:

🎯 SCORING FORMULA:
Score = (Rating × 0.35) + (Price_Score × 0.25) + (Popularity × 0.20) + (Distance_Score × 0.15) + (Cuisine_Bonus × 0.05)

📊 FACTOR BREAKDOWN:
• Rating (35%): Restaurant rating divided by 10
• Price (25%): 1 - (restaurant_price / max_price) - lower prices get higher scores
• Popularity (20%): Restaurant popularity divided by 10
• Distance (15%): 1 - (distance / max_distance) - closer restaurants get higher scores
• Cuisine Bonus (5%): +0.05 if cuisine matches user preference

🔍 FILTERING PROCESS:
1. Price filter: Remove restaurants above budget
2. Rating filter: Remove restaurants below minimum rating
3. Distance filter: Remove restaurants too far away
4. Cuisine filter: Remove restaurants with wrong cuisine type
5. Score calculation: Calculate weighted score for remaining restaurants
6. Ranking: Sort by score (highest first)

📈 EXAMPLE CALCULATION:
For "Pizzeria Laterna" with Italian preference:
• Rating: 8.0/10 × 0.35 = 0.280
• Price: (1 - 4.90/10) × 0.25 = 0.128
• Popularity: 9.0/10 × 0.20 = 0.180
• Distance: (1 - 2.1/5) × 0.15 = 0.087
• Cuisine Bonus: 0.05 (Italian match)
• Total Score: 0.725
""")

if __name__ == "__main__":
    explain_algorithm()
    demo_recommendations() 