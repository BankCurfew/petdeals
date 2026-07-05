#!/usr/bin/env python3
"""Update seasons.json — compute auto-active flags and populate matchingProducts from products.json.
Run daily as part of the promo loop or before build."""
import json, os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SEASONS_PATH = os.path.join(DATA_DIR, "seasons.json")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def match_products_by_category(products, categories):
    """Match products whose category overlaps with campaign categories."""
    matched = []
    for p in products:
        cat = p.get("category", "")
        if any(c in cat for c in categories):
            matched.append(p.get("slug", ""))
    return [s for s in matched if s]


def match_products_with_discount(products):
    """Match products that have a priceMax (discount available)."""
    matched = []
    for p in products:
        if p.get("priceMax") and str(p["priceMax"]).strip():
            matched.append(p.get("slug", ""))
    return [s for s in matched if s]


def main():
    today = datetime.now()
    seasons = load_json(SEASONS_PATH)
    products = load_json(PRODUCTS_PATH)
    if not isinstance(products, list):
        products = products.get("products", [])

    all_categories = list({p.get("category", "") for p in products if p.get("category")})
    discounted = match_products_with_discount(products)

    # Update campaigns — auto-active by date range
    for c in seasons.get("campaigns", []):
        start = datetime.strptime(c["startDate"], "%Y-%m-%d")
        end = datetime.strptime(c["endDate"], "%Y-%m-%d")
        if today < start:
            c["active"] = False
            c["status"] = "upcoming"
        elif today > end:
            c["active"] = False
            c["status"] = "past"
        else:
            c["active"] = True
            c["status"] = "active"

        c["matchingProducts"] = discounted[:50]

    # Update recurring — auto-active by day of month
    for r in seasons.get("recurring", []):
        dom = r["dayOfMonth"]
        dur = r.get("durationDays", 3)
        active_start = dom
        active_end = dom + dur - 1
        r["active"] = active_start <= today.day <= active_end

        cats = r.get("categories", all_categories)
        r["matchingProducts"] = match_products_by_category(products, cats)[:50]

    # Update seasonal — auto-active by month range
    for s in seasons.get("seasonal", []):
        sm = s["startMonth"]
        em = s["endMonth"]
        if sm <= em:
            s["active"] = sm <= today.month <= em
        else:
            s["active"] = today.month >= sm or today.month <= em

        cats = s.get("categories", all_categories)
        s["matchingProducts"] = match_products_by_category(products, cats)[:50]

    seasons["updatedAt"] = today.strftime("%Y-%m-%d")
    save_json(SEASONS_PATH, seasons)

    # Summary
    active_campaigns = [c["slug"] for c in seasons.get("campaigns", []) if c.get("active")]
    active_recurring = [r["slug"] for r in seasons.get("recurring", []) if r.get("active")]
    active_seasonal = [s["slug"] for s in seasons.get("seasonal", []) if s.get("active")]

    print(f"Seasons updated: {today.strftime('%Y-%m-%d')}")
    print(f"  Campaigns: {len(seasons['campaigns'])} ({len(active_campaigns)} active: {active_campaigns})")
    print(f"  Recurring: {len(seasons['recurring'])} ({len(active_recurring)} active: {active_recurring})")
    print(f"  Seasonal:  {len(seasons['seasonal'])} ({len(active_seasonal)} active: {active_seasonal})")
    print(f"  Discounted products: {len(discounted)}")


if __name__ == "__main__":
    main()
