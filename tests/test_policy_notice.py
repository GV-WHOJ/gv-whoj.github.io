"""Overnight access notice: shows in its date window, dismisses and stays dismissed, FAQ is near the top.
Run: python3 -I tests/test_policy_notice.py
"""
import functools, http.server, os, socketserver, threading
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

def open_at(ctx, when):
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(base + "/index.html"); pg.evaluate(f"localStorage.setItem('whojAdmin','{KEY}')")
    pg.goto(base + f"/index.html?at={when}"); pg.wait_for_timeout(600)
    return pg, errors

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, vp in [("desktop", {"width": 1280, "height": 800}), ("phone", {"width": 390, "height": 800})]:
        ctx = b.new_context(viewport=vp)
        n = lambda pg: pg.locator("#policyNotice")

        pg, errs = open_at(ctx, "2026-11-19T12:00")
        check(f"{label}: hidden the day before it starts showing", n(pg).is_hidden())

        pg, errs = open_at(ctx, "2026-11-21T12:00")
        check(f"{label}: shown before the policy starts", n(pg).is_visible())
        check(f"{label}: tag counts down to the start day", "starts mon, nov 30" in n(pg).locator(".ntag").inner_text().lower(), n(pg).locator(".ntag").inner_text())
        check(f"{label}: headline mentions 10pm → 6am", "10pm → 6am" in n(pg).locator("h2").inner_text())
        check(f"{label}: three points", n(pg).locator(".nitem").count() == 3)
        txt = n(pg).inner_text()
        check(f"{label}: says to have the GV ID ready and does not promise desk hours", "GV ID" in txt and "staffed" not in txt, txt)
        check(f"{label}: no sideways scrolling", pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"))
        check(f"{label}: page script has no errors", not errs, errs)
        dbox = n(pg).locator(".ndismiss").bounding_box(); lbox = n(pg).locator("a.nbtn").bounding_box()
        check(f"{label}: buttons are at least 44px tall", dbox["height"] >= 44 and lbox["height"] >= 44, (dbox, lbox))
        stack_top = pg.evaluate("document.getElementById('stack').getBoundingClientRect().top")
        check(f"{label}: sits above the pinned banners", n(pg).bounding_box()["y"] < stack_top + 1 or pg.evaluate("getComputedStyle(document.getElementById('stack')).display") == "none")

        check(f"{label}: search shortcut does not cover the notice at the top of the page", pg.evaluate("getComputedStyle(document.getElementById('searchJump')).visibility") == "hidden")
        pg.evaluate("window.scrollTo(0, 3000)"); pg.wait_for_timeout(400)
        check(f"{label}: search shortcut is back once the notice has scrolled away", pg.evaluate("getComputedStyle(document.getElementById('searchJump')).visibility") == "visible")
        pg.evaluate("window.scrollTo(0, 0)"); pg.wait_for_timeout(300)
        pg.locator("a.nbtn").click(); pg.wait_for_timeout(900)
        check(f"{label}: details link lands on the FAQ", pg.evaluate("location.hash") == "#overnight" and 0 <= pg.evaluate("document.getElementById('overnight').getBoundingClientRect().top") < vp["height"])

        pg, errs = open_at(ctx, "2026-12-01T12:00")
        check(f"{label}: tag says in effect once it starts", n(pg).is_visible() and "in effect now" in n(pg).locator(".ntag").inner_text().lower())

        n(pg).locator(".ndismiss").click(); pg.wait_for_timeout(200)
        check(f"{label}: dismiss hides it", n(pg).is_hidden())
        pg.reload(); pg.wait_for_timeout(500)
        check(f"{label}: stays dismissed after reload", n(pg).is_hidden())

        pg, errs = open_at(b.new_context(viewport=vp), "2026-12-15T12:00")
        check(f"{label}: hidden after its last day", n(pg).is_hidden())

        pg, errs = open_at(b.new_context(viewport=vp), "2026-11-21T12:00")
        order = pg.evaluate("[...document.querySelectorAll('#index a')].map(a => a.hash)")
        check(f"{label}: FAQ is the first item in the section index", order[:1] == ["#overnight"], order[:4])
        check(f"{label}: quick link row has it first", pg.evaluate("document.querySelector('.quick a').hash") == "#overnight")
        pg.fill("#q", "side door alarm"); pg.wait_for_timeout(200)
        check(f"{label}: search finds the FAQ", pg.evaluate("!document.getElementById('overnight').hidden"))
    b.close()
print("\nALL PASSED" if not fails else f"\n{len(fails)} FAILED: {fails}")
raise SystemExit(1 if fails else 0)
