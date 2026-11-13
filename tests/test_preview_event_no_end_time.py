"""An event with no end time keeps its banner up all day; the preview needs a button to see that.
Run: python3 -I tests/test_preview_event_no_end_time.py
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
EV = 'window.EVENTS=[{"id":"x1","title":"Open Mic Night","about":"","date":"2026-11-20","start":"19:00","where":"Lobby"}];'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context().new_page()
    pg.route("**/events.js", lambda r: r.fulfill(content_type="application/javascript", body=EV))
    pg.goto(base + "/admin.html"); pg.evaluate(f"localStorage.setItem('whojAdmin','{KEY}')")
    pg.goto(base + "/admin.html?v=preview"); pg.wait_for_selector(".cats button")
    pg.click(".cats button:has-text('Events')")
    m = [t.strip() for t in pg.eval_on_selector_all(".moments button", "e=>e.map(x=>x.textContent)")]
    ok = any("during the day" in x.lower() for x in m)
    if ok:
        pg.click(".moments button:has-text('During the day')"); pg.wait_for_timeout(1200)
        banner = pg.frame_locator("iframe").locator("#eventBanner").inner_text()
        ok = "Open Mic Night" in banner
        if not ok: print("FAIL: banner not shown:", repr(banner))
    else: print("FAIL: no 'During the day' button. Moments:", m)
    b.close()
print("PASS" if ok else "FAILED"); sys.exit(0 if ok else 1)
