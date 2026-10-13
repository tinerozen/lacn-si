# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import math, os, json

from fastapi.middleware.cors import CORSMiddleware

# Optional Firestore / Firebase Admin (advanced)
firestore_db = None
try:
    from firebase_admin import credentials, initialize_app, firestore
    cred_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")  # put JSON string in env var for deployed apps
    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        initialize_app(cred)
        firestore_db = firestore.client()
except Exception:
    # no firestore configured
    firestore_db = None

app = FastAPI(title="Restaurant Recommender")

# Allow everybody for development; tighten this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class RestaurantIn(BaseModel):
    id: str
    name: Optional[str] = None
    lat: float
    lng: float
    rating: Optional[float] = 3.0
    last_visited: Optional[datetime] = None  # ISO8601 string accepted

class RecommendRequest(BaseModel):
    user_lat: float
    user_lng: float
    restaurants: Optional[List[RestaurantIn]] = None  # if omitted, server may read Firestore (see below)
    weights: Optional[Dict[str, float]] = Field(default_factory=lambda: {"wR": 0.5, "wD": 0.3, "wT": 0.2})
    max_distance_km: Optional[float] = 10.0
    top_k: Optional[int] = 20

class RestaurantOut(RestaurantIn):
    distance_km: float
    score: float

# --- Utilities ---
def haversine_km(lat1, lon1, lat2, lon2):
    # returns distance in kilometers
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def normalize_rating(rating):
    # rating assumed in [1,5] -> normalized 0..1
    return max(0.0, min(1.0, (rating - 1.0) / 4.0))

def days_since(dt: Optional[datetime]):
    if dt is None:
        return 30  # treat never-visited as old (max effect) - adjust if desired
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        # assume UTC if naive
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    return max(0, delta.days)

def compute_score(rating, distance_km, days_since_visit, weights, max_distance_km):
    R = normalize_rating(rating)
    D = min(distance_km / max_distance_km, 1.0)
    T = min(days_since_visit / 30.0, 1.0)
    wR = weights.get("wR", 0.5)
    wD = weights.get("wD", 0.3)
    wT = weights.get("wT", 0.2)
    score = wR * R + wD * (1 - D) + wT * T
    return round(score, 6)

def score_restaurants(req: RecommendRequest):
    # 1) If restaurants were not provided by the client, attempt to read from Firestore:
    restaurants = req.restaurants
    if not restaurants:
        if firestore_db is None:
            raise HTTPException(status_code=400, detail="No restaurants provided and Firestore not configured on server.")
        # Example: read all documents from 'restaurants' collection; adapt field names as needed
        docs = firestore_db.collection("restaurants").stream()
        restaurants = []
        for d in docs:
            data = d.to_dict()
            restaurants.append(RestaurantIn(
                id=d.id,
                name=data.get("name"),
                lat=float(data["lat"]),
                lng=float(data["lng"]),
                rating=float(data.get("rating", 3.0)),
                last_visited=data.get("lastVisited")  # if stored as Firestore Timestamp, pydantic will parse
            ))

    scored = []
    for r in restaurants:
        dist = haversine_km(req.user_lat, req.user_lng, r.lat, r.lng)
        ds = days_since(r.last_visited)
        sc = compute_score(r.rating or 3.0, dist, ds, req.weights or {}, req.max_distance_km or 10.0)
        out = RestaurantOut(**r.dict(), distance_km=round(dist, 4), score=sc)
        scored.append(out)

    # sort descending by score
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored

# --- Endpoints ---
@app.post("/calculate_score")
def calculate_score_endpoint(r: dict):
    """
    Quick test endpoint. Send JSON:
    { "rating": 4.2, "distance_km": 1.3, "last_visited": "2025-08-01T12:00:00Z", "weights": {"wR":0.5,"wD":0.3,"wT":0.2} }
    """
    rating = r.get("rating", 3.0)
    distance_km = r.get("distance_km", 0.0)
    last_visited = r.get("last_visited")
    weights = r.get("weights", {"wR":0.5,"wD":0.3,"wT":0.2})
    if last_visited:
        last_dt = datetime.fromisoformat(last_visited.replace("Z", "+00:00"))
    else:
        last_dt = None
    days = days_since(last_dt)
    sc = compute_score(rating, distance_km, days, weights, r.get("max_distance_km", 10.0))
    return {"score": sc, "days_since": days}

@app.post("/recommend_restaurants", response_model=List[RestaurantOut])
def recommend(req: RecommendRequest):
    scored = score_restaurants(req)
    return scored[: (req.top_k or 20)]



@app.post("/priporocajTopTri", response_model=List[RestaurantOut])
def recommend(req: RecommendRequest):
    scored = score_restaurants(req)

    prvaIzbira = scored[0]

    drugaIzbira = scored[1]

    tretjaIzbira = scored[2]

    return {"prvaIzbira": prvaIzbira, "drugaIzbira": drugaIzbira, "tretjaIzbira": tretjaIzbira}
