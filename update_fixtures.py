import os
import json
import urllib.request
from datetime import datetime, timedelta

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("Missing API_KEY environment variable")

# Team IDs in API-Football for Greater Manchester & North West clubs
CLUBS = {
    "Manchester City": {"id": 50, "tier": "Premier League", "mins": 10},
    "Manchester United": {"id": 33, "tier": "Premier League", "mins": 15},
    "Bolton Wanderers": {"id": 68, "tier": "League One", "mins": 25},
    "Wigan Athletic": {"id": 61, "tier": "League One", "mins": 35},
    "Stockport County": {"id": 1359, "tier": "League One", "mins": 15},
    "Salford City": {"id": 1363, "tier": "League Two", "mins": 15},
    "Oldham Athletic": {"id": 1347, "tier": "National League", "mins": 20},
    "Rochdale": {"id": 1353, "tier": "National League", "mins": 25},
    "Altrincham": {"id": 1833, "tier": "National League", "mins": 20},
    "FC United of Manchester": {"id": 4682, "tier": "Northern Premier", "mins": 15},
}

today = datetime.utcnow().strftime("%Y-%m-%d")
end_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

fixtures_out = []
seen_ids = set()

for club_name, meta in CLUBS.items():
    url = f"https://v3.football.api-sports.io/fixtures?team={meta['id']}&from={today}&to={end_date}"
    req = urllib.request.Request(url, headers={"x-apisports-key": API_KEY})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            for item in data.get("response", []):
                fid = item["fixture"]["id"]
                if fid in seen_ids:
                    continue
                seen_ids.add(fid)
                
                home = item["teams"]["home"]["name"]
                away = item["teams"]["away"]["name"]
                is_home = item["teams"]["home"]["id"] == meta["id"]
                dt = datetime.fromisoformat(item["fixture"]["date"].replace("Z", "+00:00"))
                
                fixtures_out.append({
                    "id": fid,
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": dt.strftime("%H:%M"),
                    "home": home,
                    "away": away,
                    "competition": item["league"]["name"],
                    "venue": item["fixture"]["venue"]["name"] or "TBC",
                    "travelMins": meta["mins"] if is_home else 99,
                    "isLocal": is_home
                })
    except Exception as e:
        print(f"Error fetching {club_name}: {e}")

fixtures_out.sort(key=lambda x: (x["date"], x["time"]))

with open("fixtures.json", "w", encoding="utf-8") as f:
    json.dump(fixtures_out, f, indent=2)

print(f"Saved {len(fixtures_out)} fixtures.")
