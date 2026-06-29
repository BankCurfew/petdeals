#!/usr/bin/env python3
"""Pull GA4 data (24h) → data/analytics/ga4-YYYY-MM-DD.json"""
import json, os
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
PROPERTY_ID = creds.get("GA4_PROPERTY_ID", "543407169")

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

def pull_ga4(token, start_date, end_date):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport"
    body = json.dumps({
        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
        "dimensions": [{"name": "pagePath"}, {"name": "eventName"}],
        "metrics": [
            {"name": "eventCount"},
            {"name": "activeUsers"},
            {"name": "screenPageViews"},
        ],
        "limit": 500,
    }).encode()
    req = Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"GA4 Pull: {yesterday} (24h)")
    token = get_access_token()
    print("Auth: OK")

    data = pull_ga4(token, yesterday, yesterday)
    rows = data.get("rows", [])
    print(f"Rows: {len(rows)}")

    output = {
        "pulled_at": datetime.now().isoformat(),
        "date": yesterday,
        "property_id": PROPERTY_ID,
        "total_rows": len(rows),
        "rows": rows,
    }

    outdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "analytics")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"ga4-{today}.json")
    with open(outfile, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved: {outfile}")

    for r in rows[:5]:
        dims = [d.get("value", "") for d in r.get("dimensionValues", [])]
        vals = [m.get("value", "0") for m in r.get("metricValues", [])]
        print(f"  {dims[0][:40]} | {dims[1] if len(dims)>1 else '?'} | count={vals[0]} users={vals[1] if len(vals)>1 else '?'}")

if __name__ == "__main__":
    main()
