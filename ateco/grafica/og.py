"""Disegna grafica/og.png (1200×630, immagine di anteprima per la condivisione) da og.html con Playwright.
Uso: python3 ateco/grafica/og.py   (poi python3 ateco/genera.py la copia in sito/assets/)"""
from pathlib import Path
from playwright.sync_api import sync_playwright

QUI = Path(__file__).resolve().parent
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.route("**/*", lambda r: r.continue_() if r.request.url.startswith("file://") else r.abort())
    pg.goto((QUI / "og.html").as_uri())
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(QUI / "og.png"))
    b.close()
print(QUI / "og.png")
