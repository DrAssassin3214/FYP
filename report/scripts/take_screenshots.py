"""Screenshots of the running GUI (ILLUSTRATIVE example loaded) at 1280 px width.
Usage: python report/scripts/take_screenshots.py PORT
Output: report/figures/fig5_screen_*.png.  The GUI must already be running (python -m gui --port PORT --no-browser)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

port = sys.argv[1]
out = Path(__file__).resolve().parents[1] / "figures"
base = f"http://127.0.0.1:{port}/"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 800})
    pg.emulate_media(reduced_motion="reduce")
    pg.add_init_script("try{localStorage.setItem('fyp-gui-theme','light')}catch(e){}")
    pg.goto(base); pg.wait_for_timeout(1500)
    pg.click('[data-action="example"]'); pg.wait_for_timeout(1500)
    for scr in ["case", "rules", "risks", "matrix", "evidence", "report"]:
        pg.goto(base + f"#/{scr}"); pg.wait_for_timeout(1200)
        pg.screenshot(path=str(out / f"fig5_screen_{scr}.png"), full_page=True)
    # analysis screen: load the ILLUSTRATIVE analysis example and run it
    pg.goto(base + "#/analysis"); pg.wait_for_timeout(1200)
    pg.click('[data-action="analysis-example"]'); pg.wait_for_timeout(1500)
    pg.screenshot(path=str(out / "fig5_screen_analysis_before.png"), full_page=True)
    pg.click('[data-action="analysis-run"]'); pg.wait_for_timeout(6000)
    pg.screenshot(path=str(out / "fig5_screen_analysis.png"), full_page=True)
    b.close()
