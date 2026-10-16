import secrets
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

EMAIL = "23f2004447@ds.study.iitm.ac.in"          # <-- put YOUR logged-in email here
API_KEY = "ak_vn6dtekpvwp1212tpuzjbqz7"

app = FastAPI()

# Allow any website to call us (needed so the browser can verify the endpoint).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analytics")
async def analytics(request: Request):
    # 1) The doorman: check the API key FIRST, before touching the body.
    given_key = request.headers.get("x-api-key", "")
    if not secrets.compare_digest(given_key, API_KEY):
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    # 2) Read the events safely.
    try:
        body = await request.json()
        events = body["events"]
    except Exception:
        return JSONResponse({"detail": "Bad request"}, status_code=400)

    # 3) Do the math.
    users = set()
    positive_totals = defaultdict(float)   # user -> sum of their positive amounts
    revenue = 0.0

    for e in events:
        user = e["user"]
        amount = float(e["amount"])
        users.add(user)
        if amount > 0:
            revenue += amount
            positive_totals[user] += amount

    top_user = max(positive_totals, key=positive_totals.get) if positive_totals else None

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": round(revenue, 2),
        "top_user": top_user,
    }