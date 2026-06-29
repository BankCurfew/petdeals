#!/usr/bin/env python3
"""Pull Google Search Console data (7-day) → data/analytics/gsc-YYYY-MM-DD.json"""
import json, os, sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ENV = os.path.expanduser("~/.oracle/secrets/shopee-affiliate.env")
creds = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip()

CLIENT_ID = creds["GOOGLE_OAUTH_CLIENT_ID"]
CLIENT_SECRET = creds["GOOGLE_OAUTH_CLIENT_SECRET"]
REFRESH_TOKEN = creds["GOOGLE_REFRESH_TOKEN"]
SITE = "sc-domain:petzdeals.com"

def get_access_token():
    body = urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode()
    req = Request("https://oauth2.googleapis.com/token", data=body,
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())["access_token"]

def pull_gsc(token, start_date, end_date):
    url = f"https://www.googleapis.com/webmasters/v3/sites/{SITE}/searchAnalytics/query"
    body = json.dumps({
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page", "query"],
        "rowLimit": 1000,
    }).encode()
    req = Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")

    print(f"GSC Pull: {start} → {end}")
    token = get_access_token()
    print("Auth: OK")

    data = pull_gsc(token, start, end)
    rows = data.get("rows", [])
    print(f"Rows: {len(rows)}")

    output = {
        "pulled_at": datetime.now().isoformat(),
        "date_range": {"start": start, "end": end},
        "total_rows": len(rows),
        "rows": rows,
    }

    outdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "analytics")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"gsc-{today}.json")
    with open(outfile, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved: {outfile}")

    for r in rows[:5]:
        keys = r.get("keys", [])
        page = keys[0] if keys else "?"
        query = keys[1] if len(keys) > 1 else "?"
        print(f"  {page[:40]} | {query[:30]} | clicks={r.get('clicks',0)} imp={r.get('impressions',0)}")

if __name__ == "__main__":
    main()
