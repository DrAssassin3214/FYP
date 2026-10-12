"""Layout / accessibility smoke check of the running GUI (Playwright + Chromium).

    python -m gui --no-browser --port 8791      # in one shell
    python scripts/gui_layout_check.py 8791     # prints one line per screen and width; exit 1 on a finding

Checks, for each screen at 1280 / 800 / 375 px: horizontal scroll (scrollWidth > innerWidth), console errors, failed
requests, rail links without an accessible name.  Findings B-01, B-02 of docs/refine_round_1/lead_B.md.
"""
import os
import sys

from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8765"
SCREENS = ["case", "risks", "matrix", "rules", "evidence", "analysis", "report"]
WIDTHS = [1280, 800, 375]


def main() -> int:
    bad = 0
    with sync_playwright() as pw:
        exe = os.environ.get("CHROMIUM_PATH")            # e.g. /opt/pw-browsers/chromium-1194/chrome-linux/chrome
        b = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        for w in WIDTHS:
            ctx = b.new_context(viewport={"width": w, "height": 800})
            page = ctx.new_page()
            errors, failed = [], []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("requestfailed", lambda r: failed.append(r.url))
            page.goto(f"http://127.0.0.1:{PORT}/")
            page.wait_for_timeout(1800)
            for sc in SCREENS:
                page.evaluate(f"location.hash = '#/{sc}'")
                page.wait_for_timeout(500)
                m = page.evaluate("""() => ({sw: document.documentElement.scrollWidth, iw: window.innerWidth,
                    noname: [...document.querySelectorAll('#rail a, #rail button')].filter(e => !(e.getAttribute('aria-label') || '').trim() && !(e.innerText || '').trim().length || (getComputedStyle(e.querySelector('.nav-label')||e).display==='none' && !e.getAttribute('aria-label'))).length})""")
                flag = []
                if m["sw"] > m["iw"] + 1:
                    flag.append(f"HSCROLL {m['sw']}>{m['iw']}")
                if m["noname"]:
                    flag.append(f"{m['noname']} rail items without name")
                bad += bool(flag)
                print(f"{w:5d}px  {sc:9s} {'; '.join(flag) or 'ok'}")
            if errors or failed:
                bad += 1
                print(f"{w:5d}px  console errors: {errors[:3]} failed requests: {failed[:3]}")
            ctx.close()
        b.close()
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
