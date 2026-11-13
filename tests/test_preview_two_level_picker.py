"""Admin Preview picker: pick a category, then a moment within it.
Run: python3 -I tests/test_preview_two_level_picker.py
"""
import functools, http.server, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "42a03c7096d17d62a3ef7b37940b86a07d4d6b1a069916d1091f759482be7d55"
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k): pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"
fails = []
def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))
    if not cond: fails.append(name)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context().new_page()
    pg.goto(base + "/admin.html"); pg.evaluate(f"localStorage.setItem('whojAdmin','{KEY}')")
    pg.goto(base + "/admin.html?v=preview"); pg.wait_for_timeout(1200)
    texts = lambda sel: [t.strip() for t in pg.eval_on_selector_all(sel, "e=>e.map(x=>x.textContent)")]
    cats = texts(".cats button")
    check("top row has Weekday, Saturday, Monday, Events", all(any(c.startswith(w) for c in cats) for w in ["Weekday", "Saturday", "Monday", "Events"]), cats)

    pg.click(".cats button:has-text('Weekday')"); m = texts(".moments button")
    check("Weekday shows exactly 4 moments", len(m) == 4, m)
    check("Weekday moments are duty ending / desk opens / desk closing / duty on",
          [any(k in x.lower() for x in m) for k in ["duty phone ending", "desk opens", "desk closing", "duty phone on"]] == [True] * 4, m)

    pg.click(".cats button:has-text('Saturday')"); m = texts(".moments button")
    check("Saturday shows exactly 3 moments", len(m) == 3, m)
    pg.click(".cats button:has-text('Monday')"); m = texts(".moments button")
    check("Monday shows exactly 1 moment", len(m) == 1, m)

    pg.click(".cats button:has-text('Events')")
    items = texts(".items button")
    check("Events lists each upcoming event as an item", any("HoobsGiving" in i for i in items), items)
    pg.click(".items button:has-text('HoobsGiving')"); m = texts(".moments button")
    check("An event shows Before and Happening now", len(m) == 2 and any("now" in x.lower() for x in m), m)
    pg.click(".moments button:has-text('now')"); pg.wait_for_timeout(1200)
    banner = pg.frame_locator("iframe").locator("#eventBanner").inner_text()
    check("Clicking Happening now shows that banner in the preview", "HoobsGiving" in banner, banner)
    check("Weekday-style moment buttons are gone while on Events", not any("duty phone" in x.lower() for x in texts(".moments button")))
    b.close()
sys.exit(1 if fails else 0)
