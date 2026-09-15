#!/usr/bin/env python3
"""Genera l'overlay PNG trasparente per i campioni gratuiti (1080x1920).

Uso:  python3 genera-watermark.py
Serve solo per rigenerare il PNG se cambia il testo o il dominio.
Per applicarlo ai video si usa il PNG, non questo script — vedi
12-campione-gratuito.md.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
ACCENT = (198, 255, 58, 230)  # var(--accent) del sito
OUT = "sample-overlay-1080x1920.png"

# Il reticolo va disegnato su una tela sovradimensionata e poi ruotato e
# ritagliato: ruotare dopo il ritaglio lascerebbe angoli vuoti.
big = int(math.hypot(W, H)) + 200
layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
f_mark = ImageFont.truetype(BOLD, 58)
f_url = ImageFont.truetype(REG, 30)

for row, y in enumerate(range(0, big, 300)):
    offset = (row % 2) * 310  # righe alterne sfalsate: niente corridoi puliti
    for x in range(-620, big, 620):
        d.text((x + offset, y), "SAMPLE", font=f_mark, fill=(255, 255, 255, 44))
        d.text((x + offset + 3, y + 64), "scrollcraft.design", font=f_url,
               fill=(255, 255, 255, 38))

layer = layer.rotate(-30, resample=Image.BICUBIC)
wm = layer.crop(((big - W) // 2, (big - H) // 2,
                 (big - W) // 2 + W, (big - H) // 2 + H))

bar_h = 132
d = ImageDraw.Draw(wm)
d.rectangle([0, H - bar_h, W, H], fill=(0, 0, 0, 160))
d.rectangle([0, H - bar_h, W, H - bar_h + 3], fill=ACCENT)

f_line1 = ImageFont.truetype(BOLD, 37)
f_line2 = ImageFont.truetype(REG, 29)
line1 = "SAMPLE — not licensed for commercial use"
line2 = "Order the clean file at scrollcraft.design"
d.text(((W - d.textlength(line1, font=f_line1)) / 2, H - bar_h + 30),
       line1, font=f_line1, fill=(255, 255, 255, 245))
d.text(((W - d.textlength(line2, font=f_line2)) / 2, H - bar_h + 80),
       line2, font=f_line2, fill=(255, 255, 255, 165))

wm.save(OUT)
print("scritto", OUT, wm.size)
