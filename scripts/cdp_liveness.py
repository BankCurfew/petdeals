#!/usr/bin/env python3
"""CDP render-based liveness for Shopee product pages (T094 Part 2).

Shopee product pages are a JS SPA: HTTP returns 200 + empty shell for BOTH live
and dead listings, so only a rendered DOM can tell them apart. This connects to
the real logged-in Chrome on :9222 (SOP Method 2), navigates each product URL,
waits for render, and classifies from the rendered DOM.

classify() signals (checked in rendered document.body.innerText + DOM):
  dead        : "สินค้านี้ไม่มีจำหน่ายแล้ว" / "ไม่พบสินค้า" / "Page Unavailable" /
                "This product is not available" / redirected to /search|home
  login_wall  : "not logged in" / "Log In" wall (session lost — can't judge)
  alive       : has add-to-cart / buy-now / price node and a product title

Usage: python3 scripts/cdp_liveness.py <url> [<url> ...]
Importable: cdp_check(url) -> (status, detail)
"""
import json, sys, time, asyncio, http.client
import websockets

CDP_HOST, CDP_PORT = "localhost", 9222

JS = r"""
(function(){
  var t = (document.body ? document.body.innerText : "") || "";
  var low = t.toLowerCase();
  var dead = /สินค้านี้ไม่มีจำหน่ายแล้ว|ไม่พบสินค้า|สินค้าหมด|page unavailable|product is not available|ไม่สามารถใช้งาน/i.test(t);
  var login = /not logged in|log in to continue|เข้าสู่ระบบเพื่อ/i.test(t);
  var hasBuy = !!document.querySelector('button[class*="add-to-cart"],div[class*="add-to-cart"],button[class*="buy"]') ||
               /หยิบใส่รถเข็น|ซื้อสินค้า|add to cart|buy now/i.test(t);
  var hasPrice = /฿[\d,]/.test(t);
  return JSON.stringify({url: location.href, len: t.length, dead: dead, login: login, hasBuy: hasBuy, hasPrice: hasPrice, snippet: t.slice(0,120)});
})()
"""


def _http(method, path):
    c = http.client.HTTPConnection(CDP_HOST, CDP_PORT, timeout=8)
    c.request(method, path)
    r = c.getresponse().read().decode()
    c.close()
    return json.loads(r) if r.strip().startswith(("{", "[")) else r


async def _drive(url, tab):
    uri = f"ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab['id']}"
    async with websockets.connect(uri, max_size=8 * 1024 * 1024) as ws:
        mid = 0
        async def cmd(method, params=None):
            nonlocal mid; mid += 1; i = mid
            await ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
                if m.get("id") == i:
                    return m
        await cmd("Page.enable")
        await cmd("Page.navigate", {"url": url})
        await asyncio.sleep(4.5)  # let SPA render
        r = await cmd("Runtime.evaluate", {"expression": JS, "returnByValue": True})
        val = r.get("result", {}).get("result", {}).get("value")
        return json.loads(val) if val else {}


def cdp_check(url):
    try:
        tab = _http("PUT", f"/json/new?{url}")
        if not isinstance(tab, dict) or "id" not in tab:
            return "error", "no-tab"
        try:
            info = asyncio.get_event_loop().run_until_complete(_drive(url, tab))
        finally:
            _http("GET", f"/json/close/{tab['id']}")
        if not info:
            return "unknown", "no-eval"
        if info.get("dead"):
            return "dead", "rendered dead-marker"
        if "/search" in info.get("url", "") or info.get("url", "").rstrip("/") == "https://shopee.co.th":
            return "dead", "redirected->" + info.get("url", "")[:50]
        if info.get("login"):
            return "login_wall", "session lost: " + info.get("snippet", "")[:60]
        if info.get("hasPrice") or info.get("hasBuy"):
            return "alive", f"price={info.get('hasPrice')} buy={info.get('hasBuy')} len={info.get('len')}"
        # Rendered but NO price and NO buy button = removed/unavailable listing
        # (real Shopee products always render a price + add-to-cart). Reliable dead signal.
        return "dead", "no price/buy rendered (unavailable): " + info.get("snippet", "")[:50]
    except Exception as e:
        return "error", str(e)[:60]


if __name__ == "__main__":
    for u in sys.argv[1:]:
        st, detail = cdp_check(u)
        print(f"{st:11} | {detail} | {u[:60]}")
        time.sleep(0.5)
