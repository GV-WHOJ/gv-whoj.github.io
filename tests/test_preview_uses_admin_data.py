"""Admin Preview must show banners for events saved in Admin even when the
deployed events.js (what Pages serves) doesn't have them yet.
Run: python3 -I tests/test_preview_uses_admin_data.py
"""
import base64, functools, http.server, json, os, socketserver, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = "42a03c7096d17d62a3ef7b37940b86a07d4d6b1a069916d1091f759482be7d55"
API = "https://api.github.com/repos/GV-WHOJ/gv-whoj.github.io"

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k): pass
    def end_headers(self):
        self.send_header("Cache-Control", "no-store"); super().end_headers()
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"

def read(n): return open(os.path.join(ROOT, n)).read()
fresh = {"id": "fresh1", "title": "Fresh Event", "about": "Just saved in Admin", "date": "2026-11-14",
         "start": "10:00", "end": "11:00", "where": "Lobby"}
gh_events = read("events.js").rstrip().rstrip("];").rstrip() + ",\n" + json.dumps(fresh) + "\n];\n"

def api(route):
    u = route.request.url
    if "/contents/events.js" in u: body = {"sha": "e", "content": base64.b64encode(gh_events.encode()).decode()}
    elif "/contents/breaks.js" in u: body = {"sha": "b", "content": base64.b64encode(read("breaks.js").encode()).decode()}
    else: body = {"permissions": {"push": True}, "login": "t"}
    route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"}, body=json.dumps(body))

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context().new_page()
    pg.route("https://api.github.com/**", api)
    pg.goto(base + "/admin.html")
    pg.evaluate(f"localStorage.setItem('whojAdmin','{KEY}'); localStorage.setItem('whojGh','fake')")
    pg.goto(base + "/admin.html?v=preview"); pg.wait_for_selector("button.evc", timeout=8000)
    chip = pg.locator("button.evc", has_text="Fresh Event: happening now")
    assert chip.count() == 1, "chip for the freshly saved event is missing"
    chip.click(); pg.wait_for_timeout(1500)
    text = pg.frame_locator("iframe").locator("#eventBanner").inner_text()
    b.close()
if "Fresh Event" in text and "HAPPENING NOW" in text.upper():
    print("PASS"); sys.exit(0)
print("FAIL: iframe banner did not show the freshly saved event. Banner text: %r" % text); sys.exit(1)
