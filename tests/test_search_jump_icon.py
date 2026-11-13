"""Floating magnifying-glass button: upper right, below banners, jumps to the search box.
Run: python3 -I tests/test_search_jump_icon.py
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
    b = p.chromium.launch()
    for label, vp in [("desktop", {"width": 1280, "height": 800}), ("phone", {"width": 390, "height": 800})]:
        pg = b.new_context(viewport=vp).new_page()
        pg.goto(base + "/index.html"); pg.evaluate(f"localStorage.setItem('whojAdmin','{KEY}')")
        # a day with an event banner pinned at the top
        pg.goto(base + "/index.html?at=2026-11-17T20:00"); pg.wait_for_timeout(800)
        pg.evaluate("window.scrollTo(0, 2500)"); pg.wait_for_timeout(400)
        btn = pg.locator("#searchJump")
        check(f"{label}: search icon exists", btn.count() == 1)
        if btn.count() != 1: continue
        box = btn.bounding_box()
        check(f"{label}: icon is visible while scrolled down", btn.is_visible() and box is not None)
        check(f"{label}: icon is in the upper right", box["x"] + box["width"] > vp["width"] * 0.75 and box["y"] < vp["height"] * 0.4, box)
        stack_bottom = pg.evaluate("(()=>{const s=document.querySelector('.stack');return s?s.getBoundingClientRect().bottom:0})()")
        check(f"{label}: icon sits below the pinned banners", box["y"] >= stack_bottom - 1, f"icon top {box['y']} vs banners bottom {stack_bottom}")
        check(f"{label}: icon has an accessible name", bool(btn.get_attribute("aria-label")))
        btn.click(); pg.wait_for_timeout(900)
        check(f"{label}: tapping it puts the cursor in the search box", pg.evaluate("document.activeElement && document.activeElement.id") == "q")
        top = pg.evaluate("document.getElementById('q').getBoundingClientRect().top")
        check(f"{label}: search box is on screen below the banners", stack_bottom - 1 <= top < vp["height"], top)
    b.close()
sys.exit(1 if fails else 0)
