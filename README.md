# Lačn.si

A small FastAPI backend that ranks restaurants by rating, distance and time since your last visit. It grew out of Prehrana.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

You can also use the `Dockerfile` (port 8000) or the `Procfile` (Heroku-style, `$PORT`).

### Firestore (optional)

If the `FIREBASE_SERVICE_ACCOUNT_JSON` env var holds a service-account JSON string, the server reads restaurants from the Firestore `restaurants` collection when the request doesn't include any.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/calculate_score` | Scores one restaurant (quick test) |
| POST | `/recommend_restaurants` | Returns the top `top_k` restaurants, sorted by score |
| POST | `/priporocajTopTri` | Same as above but returns only the top three (`prvaIzbira`, `drugaIzbira`, `tretjaIzbira`) |

Example body for `/recommend_restaurants`:

```json
{
  "user_lat": 46.05, "user_lng": 14.50,
  "restaurants": [
    {"id": "1", "name": "Menza FE", "lat": 46.0446, "lng": 14.4893, "rating": 4.2, "last_visited": "2025-08-01T12:00:00Z"}
  ]
}
```

## Score

```
score = wR * rating_norm + wD * (1 - distance / max_distance_km) + wT * min(days_since_visit / 30, 1)
```

Default weights are `wR=0.5, wD=0.3, wT=0.2`. A rating in 1–5 maps to 0–1. A restaurant you've never visited counts as 30 days.
