"""Compose assets/pond.gif: two git-koi koi in a pond, fed by my commits.

git-koi draws each koi as a 512x512 GIF of it swimming laps on a transparent
background. Here the second koi is the same swim turned 180 degrees, so the
pair always mirror each other like the Pisces sign. Under the pond sits my real
contribution graph; every recent day with commits sends a pellet up into the
water, and a pellet is eaten the moment a koi's body passes over it.

Usage: python scripts/gen_pond.py <data.json> <koi_a.gif> <koi_b.gif> <out.gif>
Needs Pillow and numpy.
"""
import json
import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence

DATA, KOI_A, KOI_B, OUT = sys.argv[1:5]
d = json.load(open(DATA))

W = 900
POND_H = 470
GRID_TOP = POND_H + 44
CELL, GAP = 12, 3
STEP = CELL + GAP
H = GRID_TOP + 7 * STEP + 40
KOI = 448                                  # koi square drawn at this size (from 512)
KX, KY = (W - KOI) // 2, (POND_H - KOI) // 2 + 8

BG = (27, 31, 39)                          # matches the terminal
WATER_TOP, WATER_BOTTOM = (24, 52, 66), (15, 32, 44)
RIM = (95, 170, 250)
TEXT, DIM = (216, 222, 233), (97, 110, 136)
LEVEL = [(46, 52, 64), (52, 84, 108), (66, 120, 160), (85, 150, 205), (95, 170, 250)]
PELLET = (235, 203, 139)


def frames(path):
    im = Image.open(path)
    out, durs = [], []
    for fr in ImageSequence.Iterator(im):
        out.append(fr.convert("RGBA").resize((KOI, KOI), Image.NEAREST))
        durs.append(fr.info.get("duration", 60))
    return out, durs


a, durs = frames(KOI_A)
b, _ = frames(KOI_B)
b = [f.rotate(180) for f in b]
n = min(len(a), len(b))

# --- static background: pond, lily pads, graph -------------------------------
base = Image.new("RGB", (W, H), BG)
dr = ImageDraw.Draw(base)
pond = Image.new("L", (W, POND_H), 0)
ImageDraw.Draw(pond).rounded_rectangle((14, 12, W - 15, POND_H - 6), radius=46, fill=255)
grad = Image.new("RGB", (W, POND_H))
gd = ImageDraw.Draw(grad)
for y in range(POND_H):
    t = y / POND_H
    gd.line((0, y, W, y), fill=tuple(int(WATER_TOP[i] + (WATER_BOTTOM[i] - WATER_TOP[i]) * t) for i in range(3)))
base.paste(grad, (0, 0), pond)
dr.rounded_rectangle((14, 12, W - 15, POND_H - 6), radius=46, outline=(52, 84, 108), width=2)

rnd = random.Random(7)
# a few stones on the pond floor
for _ in range(26):
    x, y = rnd.randint(40, W - 40), rnd.randint(40, POND_H - 30)
    if KX - 10 < x < KX + KOI + 10 and KY < y < KY + KOI:
        continue
    r = rnd.randint(4, 11)
    c = rnd.randint(30, 44)
    dr.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(c, c + 14, c + 22))


def lily(cx, cy, r, ang):
    pad = Image.new("RGBA", (r * 2 + 4, r * 2 + 4), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pad)
    pd.ellipse((2, 2, r * 2 + 2, r * 2 + 2), fill=(76, 122, 84, 255), outline=(58, 98, 66, 255), width=2)
    pd.pieslice((2, 2, r * 2 + 2, r * 2 + 2), -20, 20, fill=(0, 0, 0, 0))
    pd.line((r + 2, r + 2, r * 1.7 + 2, r + 2), fill=(58, 98, 66, 255), width=1)
    pad = pad.rotate(ang, resample=Image.BICUBIC)
    base.paste(pad, (cx - r - 2, cy - r - 2), pad)


lily(70, 70, 26, 30)
lily(118, 108, 16, 200)
lily(W - 86, POND_H - 80, 30, 120)
lily(W - 140, POND_H - 52, 17, 300)
lily(W - 70, 64, 14, 80)

try:
    font = ImageFont.truetype("DejaVuSansMono.ttf", 12)
    small = ImageFont.truetype("DejaVuSansMono.ttf", 11)
except OSError:
    font = small = ImageFont.load_default()

weeks = d["weeks"]
GX = (W - len(weeks) * STEP + GAP) // 2
dr.text((GX, GRID_TOP - 26), f"{d['total']} contributions in the last year", font=font, fill=TEXT)
dr.text((W - GX, GRID_TOP - 26), f"streak {d['streak']} · best {d['best']}", font=font, fill=DIM, anchor="ra")
cells = {}
for c, w in enumerate(weeks):
    for r, (date, cnt, lv) in enumerate(w):
        x, y = GX + c * STEP, GRID_TOP + r * STEP
        dr.rounded_rectangle((x, y, x + CELL, y + CELL), radius=2, fill=LEVEL[lv])
        cells[date] = (x + CELL / 2, y + CELL / 2, cnt, lv)
dr.text((GX, H - 22), "the koi eat my commits: every recent day with commits sends food up into the pond",
        font=small, fill=DIM)

# --- food: one pellet per recent day with commits -----------------------------
active = [k for k in sorted(cells) if cells[k][2] > 0][-18:]
# where each pellet settles: spread over the area the koi actually swim through
swim = np.zeros((KOI, KOI), bool)
for f in a[:n] + b[:n]:
    swim |= np.array(f.split()[3]) > 0
ys, xs = np.nonzero(swim)
pellets = []
for i, date in enumerate(active):
    j = rnd.randrange(len(xs))
    px, py = KX + int(xs[j]), KY + int(ys[j])
    sx, sy = cells[date][:2]
    start = int(i * n / (len(active) + 2))          # staggered launches
    pellets.append({"from": (sx, sy), "to": (px, py), "start": start, "rise": 14, "eaten": None})


def alpha_at(fr, x, y):
    lx, ly = x - KX, y - KY
    if 0 <= lx < KOI and 0 <= ly < KOI:
        return fr.getpixel((int(lx), int(ly)))[3] > 0
    return False


for p in pellets:
    land = p["start"] + p["rise"]
    for k in range(land, land + n):
        fi = k % n
        if alpha_at(a[fi], *p["to"]) or alpha_at(b[fi], *p["to"]):
            p["eaten"] = k
            break

# --- frames ------------------------------------------------------------------
TOTAL = n * 2                                # two swim loops so every pellet gets eaten
out = []
for k in range(TOTAL):
    fr = base.copy()
    over = ImageDraw.Draw(fr, "RGBA")
    # ripples
    for rc in range(3):
        ph = ((k / TOTAL) + rc / 3) % 1
        cx, cy = [(220, 150), (690, 300), (420, 390)][rc]
        rr = 6 + ph * 46
        over.ellipse((cx - rr, cy - rr * 0.45, cx + rr, cy + rr * 0.45), outline=(140, 190, 230, int(70 * (1 - ph))), width=1)
    for p in pellets:
        if k < p["start"] or (p["eaten"] is not None and k >= p["eaten"]):
            continue
        t = min(1.0, (k - p["start"]) / p["rise"])
        (x0, y0), (x1, y1) = p["from"], p["to"]
        e = 1 - (1 - t) ** 3
        x, y = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
        r = 3.2 if t >= 1 else 2.4
        glow = int(110 * (0.6 + 0.4 * math.sin(k / 3 + x)))
        over.ellipse((x - r - 3, y - r - 3, x + r + 3, y + r + 3), fill=PELLET + (glow // 3,))
        over.ellipse((x - r, y - r, x + r, y + r), fill=PELLET + (255,))
    fi = k % n
    fr.paste(b[fi], (KX, KY), b[fi])
    fr.paste(a[fi], (KX, KY), a[fi])
    out.append(fr)

sheet = Image.new("RGB", (W, H * 3))
for i, k in enumerate((0, TOTAL // 3, 2 * TOTAL // 3)):
    sheet.paste(out[k], (0, H * i))
pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in out]
q[0].save(OUT, save_all=True, append_images=q[1:], duration=[durs[k % n] for k in range(TOTAL)],
          loop=0, optimize=True, disposal=1)
eaten = sum(1 for p in pellets if p["eaten"] is not None)
print(f"{OUT}: {W}x{H}, {TOTAL} frames, {len(pellets)} pellets, {eaten} eaten")
