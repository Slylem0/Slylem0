"""Draw assets/pisces.svg: my real contribution graph with two koi swimming
around it like the Pisces sign. Each koi is built from contribution-sized
squares: it starts as a head and grows one square for every few commits it
eats on its lap. Eaten days go dark and come back when the lap restarts.

Usage: python scripts/gen_pisces.py <data.json> <out.svg>
"""
import json
import math
import sys

DATA, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(DATA))
weeks = d["weeks"]

T = 24.0                                   # one lap (s)
W, H = 900, 250
CELL, GAP = 12, 3
STEP = CELL + GAP
GX = (W - len(weeks) * STEP + GAP) / 2
GY = 82
CX, CY = W / 2, GY + (7 * STEP - GAP) / 2
RX, RY = 350, 28

BG, BORDER, DIM, TEXT, FROST = "#2e3440", "#88c0d0", "#616e88", "#d8dee9", "#88c0d0"
LEVEL = ["#3b4252", "#3f5566", "#4f7090", "#6b93b5", "#88c0d0"]

STEPS = 2400


def raw(th):
    """The lap: an ellipse with a gentle swimming wave."""
    return (CX + RX * math.cos(th), CY + RY * math.sin(th) + 24 * math.sin(7 * th))


# Re-sample by arc length: animateMotion moves at constant speed along the path.
dense = [raw(2 * math.pi * i / 6000) for i in range(6001)]
cum = [0.0]
for i in range(6000):
    cum.append(cum[-1] + math.dist(dense[i], dense[i + 1]))
length = cum[-1]


def pos(u):
    """Point at fraction u of the lap's length."""
    target = (u % 1) * length
    lo, hi = 0, 6000
    while lo < hi:
        mid = (lo + hi) // 2
        if cum[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return dense[lo]


path_pts = [pos(i / 400) for i in range(400)]
PATH = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path_pts) + " Z"
speed = length / T
SPACING = 5.0                               # px between body segments
LAG = SPACING / speed                      # s between body segments

# Body profile, head first: segment widths (a koi is widest just behind the head).
PROFILE = [12, 15, 17, 18, 18, 17.5, 17, 16, 15, 14, 13, 12, 10.5, 9, 8, 7, 6, 5, 4.5, 4]
START = 4                                  # segments a koi is born with
FISH = [  # kohaku (white and red) and a dark koi with white marks: yin and yang
    {"phase": 0.0, "body": "#eceff4", "patch": "#bf616a", "fin": "#d08770", "eye": "#2e3440",
     "patches": {1, 2, 3, 7, 8, 9, 13, 14}},
    {"phase": T / 2, "body": "#15181e", "patch": "#eceff4", "fin": "#81a1c1", "eye": "#eceff4",
     "patches": {2, 3, 4, 10, 11}, "stroke": "#d8dee9"},
]

# When does each koi's head pass over each day with commits?
cells = []
for c, w in enumerate(weeks):
    for r, (date, n, lv) in enumerate(w):
        cells.append({"x": GX + c * STEP, "y": GY + r * STEP, "lv": lv, "n": n, "date": date, "eaten": None})


def head_at(phase, t):
    return pos(((t + phase) % T) / T)


for f in FISH:
    f["meals"] = []
for k in range(STEPS):
    t = T * k / STEPS
    for fi, f in enumerate(FISH):
        hx, hy = head_at(f["phase"], t)
        for cell in cells:
            if cell["lv"] and cell["eaten"] is None:
                if abs(cell["x"] + CELL / 2 - hx) < 9 and abs(cell["y"] + CELL / 2 - hy) < 9:
                    cell["eaten"] = (t, fi)
                    f["meals"].append(t)

# Growth: square i appears once the koi has eaten enough of its lap's food.
for f in FISH:
    meals = sorted(f["meals"])
    grow = len(PROFILE) - START
    per = max(1, len(meals) / grow) if meals else 1
    f["born"] = [0.0] * START + [meals[min(len(meals) - 1, int(per * (i + 1)) - 1)] if meals else 0.0
                                  for i in range(grow)]

END = 0.985
out = []
A = out.append


def window(t0, t1=None):
    """opacity on from t0 to t1 (or to the end of the lap)."""
    a, b = t0 / T, (t1 / T if t1 is not None else END)
    if a <= 0:
        return f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;{b:.4f};{END}" dur="{T}s" repeatCount="indefinite" calcMode="discrete"/>' if t1 is not None else ""
    return (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{a:.4f};{b:.4f}" '
            f'dur="{T}s" repeatCount="indefinite" calcMode="discrete"/>')


A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">')
A('<title id="t">Pisces koi over my contribution graph</title>')
A(f'<desc id="d">My GitHub contributions for the last year ({d["total"]} contributions) with two koi swimming '
  'around them like the Pisces sign. They grow as they eat the days with commits.</desc>')
A(f'<defs><path id="lap" d="{PATH}"/></defs>')
A(f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>')
FAM = "font-family=\"'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace\""
FONT = FAM + ' font-size="13"'
SMALL = FAM + ' font-size="11"'
TINY = FAM + ' font-size="10"'
A(f'<text x="28" y="34" {FONT} fill="{TEXT}"><tspan fill="#eceff4" font-weight="700">pablo </tspan>'
  f'<tspan fill="{FROST}" font-weight="700">~ </tspan><tspan fill="#a3be8c" font-weight="700">❯ </tspan>git koi --pisces</text>')
A(f'<text x="{W - 28}" y="34" text-anchor="end" {FONT} fill="{DIM}">'
  f'<tspan fill="{TEXT}">{d["total"]}</tspan> contributions · streak <tspan fill="{TEXT}">{d["streak"]}</tspan>'
  f' · best <tspan fill="{TEXT}">{d["best"]}</tspan></text>')

# Month labels.
seen = None
for c, w in enumerate(weeks):
    m = w[0][0][5:7]
    if m != seen and c < len(weeks) - 2:
        seen = m
        name = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[int(m) - 1]
        A(f'<text x="{GX + c * STEP:.1f}" y="{GY - 8}" {TINY} fill="{DIM}">{name}</text>')

# Days. Eaten ones go dark until the lap restarts.
for cell in cells:
    col = LEVEL[cell["lv"]]
    anim = ""
    if cell["eaten"]:
        k = cell["eaten"][0] / T
        anim = (f'<animate attributeName="fill" values="{col};{LEVEL[0]};{col}" keyTimes="0;{k:.4f};{END}" '
                f'dur="{T}s" repeatCount="indefinite" calcMode="discrete"/>')
    A(f'<rect x="{cell["x"]:.1f}" y="{cell["y"]:.1f}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}">'
      f'<title>{cell["date"]}: {cell["n"]}</title>{anim}</rect>')


def motion(begin):
    return (f'<animateMotion dur="{T}s" begin="{-begin:.3f}s" repeatCount="indefinite" rotate="auto">'
            f'<mpath href="#lap"/></animateMotion>')


# Koi: tail-most squares first so the head is drawn on top.
for f in FISH:
    stroke = f' stroke="{f["stroke"]}" stroke-opacity="0.45" stroke-width="1"' if f.get("stroke") else ""
    n = len(PROFILE)
    for i in reversed(range(n)):
        s = PROFILE[i]
        begin = f["phase"] - i * LAG + T * 4          # keep begin positive for the offset math
        born = f["born"][i]
        nxt = f["born"][i + 1] if i + 1 < n else None
        col = f["patch"] if i in f["patches"] else f["body"]
        g = [f'<g opacity="{0 if born > 0 else 1}">{window(born) if born > 0 else ""}']
        g.append(f'<g>{motion(begin % T)}')
        # Tail fin: only on the last grown square.
        tail_vis = window(born, nxt) if nxt is not None else (window(born) if born > 0 else "")
        tail_init = 1 if born == 0 else 0
        # Tail fin: a flowing two-lobed fan, only on the last grown segment.
        k = max(s, 7)
        g.append(f'<g opacity="{tail_init}">{tail_vis}'
                 f'<path d="M0,0 C-6,{-k * 0.5} -12,{-k * 0.95} -19,{-k * 1.05} C-15,{-k * 0.45} -15,-2 -13,0 '
                 f'C-15,2 -15,{k * 0.45} -19,{k * 1.05} C-12,{k * 0.95} -6,{k * 0.5} 0,0 Z" '
                 f'fill="{f["fin"]}" opacity="0.85"/></g>')
        if i in (3, 11):  # pectoral and pelvic fins
            fl, fw = (9, 4.2) if i == 3 else (6, 3)
            for sgn in (-1, 1):
                cy = sgn * (s / 2 + fw * 0.6)
                g.append(f'<ellipse cx="-4" cy="{cy:.1f}" rx="{fl}" ry="{fw}" transform="rotate({sgn * 32} -4 {cy:.1f})" '
                         f'fill="{f["fin"]}" opacity="0.8"/>')
        rx = s * 0.62 if i else s * 0.55
        g.append(f'<ellipse cx="0" cy="0" rx="{rx:.1f}" ry="{s / 2:.1f}" fill="{col}"{stroke}/>')
        if i == 0:  # eyes
            g.append(f'<circle cx="2.5" cy="-3.6" r="1.5" fill="{f["eye"]}"/><circle cx="2.5" cy="3.6" r="1.5" fill="{f["eye"]}"/>')
        g.append('</g></g>')
        A("".join(g))

A(f'<text x="28" y="{H - 18}" {SMALL} fill="{DIM}">two koi, one per half of the year · they grow with every day of commits they eat</text>')
A(f'<text x="{W - 28}" y="{H - 18}" text-anchor="end" {SMALL} fill="{DIM}">updated {d["generated"]}</text>')
A('</svg>')
open(OUT, "w").write("\n".join(out))
eaten = sum(1 for c in cells if c["eaten"])
print(f"{OUT}: {W}x{H}, lap {T}s, {eaten} days eaten, meals {[len(f['meals']) for f in FISH]}")
