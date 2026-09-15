#!/usr/bin/env python3
"""Genera gli overlay PNG trasparenti per i campioni gratuiti, uno per rapporto.

Uso:  python3 genera-watermark.py
Produce: sample-overlay-1080x1920.png (9:16), -1080x1350.png (4:5), -1080x1080.png (1:1).

Serve solo per rigenerare i PNG se cambia il testo o il dominio. Per applicarli ai
video si usano i PNG, non questo script — vedi 12-campione-gratuito.md.
"""
import math
from PIL import Image, ImageDraw, ImageFont

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
ACCENT = (198, 255, 58, 230)  # var(--accent) del sito
SIZES = [(1080, 1920), (1080, 1350), (1080, 1080)]


def build(W, H):
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

    f1 = ImageFont.truetype(BOLD, 37)
    f2 = ImageFont.truetype(REG, 29)
    l1 = "SAMPLE — not licensed for commercial use"
    l2 = "Order the clean file at scrollcraft.design"
    d.text(((W - d.textlength(l1, font=f1)) / 2, H - bar_h + 30), l1, font=f1,
           fill=(255, 255, 255, 245))
    d.text(((W - d.textlength(l2, font=f2)) / 2, H - bar_h + 80), l2, font=f2,
           fill=(255, 255, 255, 165))
    return wm


for W, H in SIZES:
    name = f"sample-overlay-{W}x{H}.png"
    build(W, H).save(name)
    print("scritto", name)
