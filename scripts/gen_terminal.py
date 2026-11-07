"""Generate assets/terminal.svg: my profile as a Claude Code session in my kitty.

Same look as my real setup: the darker background I switch to while Claude
runs, the "Omarchy vivo" colours, the blue prompt rules, my status line and
Clawd in the corner. Commits and stats are real and redrawn every night.
Animation is SMIL only, which GitHub renders inside <img>.

Usage: python scripts/gen_terminal.py <data.json> <out.svg>
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from html import escape

DATA, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(DATA))

W, LH, FS = 900, 21, 13.5
X0, XT = 26, 50                 # bullet column, text column
T = 22.0
C = {  # Omarchy vivo (my Claude Code theme) on the dark kitty background
    'bg': '#1b1f27', 'band': '#26354b', 'blue': '#5faafa', 'text': '#d8dee9', 'snow': '#eceff4',
    'dim': '#7b8394', 'subtle': '#4c566a', 'green': '#a3be8c', 'yellow': '#ebcb8b', 'red': '#bf616a',
    'frost': '#88c0d0', 'purple': '#b48ead', 'orange': '#d5795a', 'auto': '#d5967a',
}
parts = []


def show(t):
    return (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{t / T:.4f};0.985" '
            f'dur="{T}s" repeatCount="indefinite" calcMode="discrete"/>')


def sp(s, color, bold=False):
    b = ' font-weight="700"' if bold else ''
    return f'<tspan fill="{color}"{b}>{escape(s)}</tspan>'


def line_at(y, content, t, x=XT):
    parts.append(f'<text x="{x}" y="{y}" opacity="0" xml:space="preserve">{content}{show(t)}</text>')


y = 40
t = 0.3

# 1. my message, on the highlighted band ---------------------------------------
q = 'who is pablo?'
letters = ''.join(
    f'<tspan fill-opacity="0">{escape(ch) if ch != " " else "&#160;"}'
    f'<animate attributeName="fill-opacity" values="0;1;0" keyTimes="0;{(t + 0.2 + i * 0.07) / T:.4f};0.985" '
    f'dur="{T}s" repeatCount="indefinite" calcMode="discrete"/></tspan>' for i, ch in enumerate(q))
parts.append(f'<g opacity="0"><rect x="14" y="{y - 15}" width="{W - 28}" height="24" rx="3" fill="{C["band"]}"/>'
             f'<text x="{X0}" y="{y + 1}" xml:space="preserve">{sp("❯ ", C["dim"])}<tspan fill="{C["text"]}">{letters}</tspan></text>'
             f'{show(t)}</g>')
t += 0.2 + len(q) * 0.07 + 0.7
y += 2 * LH


def tool(name, arg):
    global y, t
    parts.append(f'<g opacity="0"><circle cx="{X0 + 4}" cy="{y - 4.5}" r="4" fill="{C["green"]}"/>'
                 f'<text x="{XT - 8}" y="{y}" xml:space="preserve">{sp(name, C["snow"], True)}{sp("(" + arg + ")", C["text"])}</text>{show(t)}</g>')
    y += LH
    t += 0.45


def out_lines(rows, step=0.09):
    global y, t
    for i, content in enumerate(rows):
        if i == 0:
            line_at(y, sp('⎿', C['dim']), t, XT - 4)
        line_at(y, content, t, XT + 18)
        y += LH
        t += step
    y += LH * 0.6
    t += 0.35


# 2. fastfetch ----------------------------------------------------------------------
tool('Bash', 'fastfetch')
K = lambda k: sp(f'{k:<9}', C['blue'], True)
out_lines([
    K('name') + sp('Pablo Nicolás Marín', C['text']),
    K('role') + sp('Cloud & Backend Builder · Buga, Colombia', C['text']),
    K('study') + sp('Systems Engineering · Universidad del Valle', C['text']),
    K('cert') + sp('AWS Certified Cloud Practitioner', C['text']),
    K('club') + sp('AWS Student Builder Group Univalle · Partnerships & Academy Lead', C['text']),
    K('stack') + sp('Lambda · DynamoDB · Bedrock · CDK · Amplify · TypeScript · Python · C++ · Go', C['text']),
    K('setup') + sp('Omarchy · Hyprland · kitty · Neovim · Nord', C['text']),
])

# 3. the answer -----------------------------------------------------------------------
parts.append(f'<g opacity="0"><circle cx="{X0 + 4}" cy="{y - 4.5}" r="4" fill="{C["snow"]}"/>{show(t)}</g>')
answer = [
    sp('Pablo builds ', C['text']) + sp('serverless backends on AWS', C['snow'], True)
    + sp(' and ', C['text']) + sp('AI agents on Amazon Bedrock', C['snow'], True) + sp(',', C['text']),
    sp('straight from a Linux terminal. Latest: ', C['text']) + sp('SEE YOU SPACE BUILDER', C['blue'], True)
    + sp(', a portfolio with a secret', C['text']),
    sp('tiling desktop and three AI cores that vote. Next stop: ', C['text'])
    + sp('AWS Certified AI Practitioner', C['snow'], True) + sp('.', C['text']),
]
for i, a in enumerate(answer):
    line_at(y, a, t + i * 0.25, XT - 8)
    y += LH
t += len(answer) * 0.25 + 0.5
y += LH * 0.6

# 4. latest commits (real) ---------------------------------------------------------------
tool('Bash', f'gh search commits --author {d["login"]} --limit 3')
MON = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
rows = []
for c in d['commits'][:3]:
    msg = c['msg'] if len(c['msg']) <= 60 else c['msg'][:59] + '…'
    when = f"{MON[int(c['date'][5:7]) - 1]} {c['date'][8:10]}"
    rows.append(sp(c['sha'] + '  ', C['yellow']) + sp(f"{c['repo'][:15]:<16}", C['frost'], True)
                + sp(f'{msg:<61}', C['text']) + sp(when, C['dim']))
out_lines(rows)

# 5. the "done" line, like Claude Code prints after a turn -----------------------------
now = datetime.now(timezone(timedelta(hours=-5)))
line_at(y, sp('✻ ', C['dim']) + sp(f'Crunched {d["total"]} contributions · done {now.strftime("%I:%M %p").lstrip("0")}', C['dim']), t, X0)
t += 0.5
y += LH * 1.5

# 6. prompt box with blinking cursor ----------------------------------------------------
top, bottom = y - 15, y + LH - 2
cursor = (f'<rect x="{X0 + 17}" y="{y - 13}" width="9" height="17" fill="none" stroke="{C["snow"]}" stroke-width="1.4">'
          f'<animate attributeName="opacity" values="1;0" dur="1.06s" repeatCount="indefinite" calcMode="discrete"/></rect>')
parts.append(f'<g opacity="0"><line x1="14" y1="{top}" x2="{W - 14}" y2="{top}" stroke="{C["blue"]}" stroke-width="1.5"/>'
             f'<text x="{X0}" y="{y + 1}">{sp("❯", C["dim"])}</text>{cursor}'
             f'<line x1="14" y1="{bottom}" x2="{W - 14}" y2="{bottom}" stroke="{C["blue"]}" stroke-width="1.5"/>{show(t)}</g>')
y = bottom + LH + 6

# 7. status line + Clawd ------------------------------------------------------------------
days = [n for w in d['weeks'] for _, n, _ in w]
active = sum(1 for n in days if n)
fill = round(16 * active / max(1, len(days)))
bar = sp('━' * max(1, fill), C['green']) + sp('╌' * (16 - fill), C['subtle'])
s1 = (sp(d['login'], C['blue'], True) + sp('  ·  active days ', C['dim']) + bar
      + sp(f' {round(100 * active / max(1, len(days)))}% {active}/{len(days)}', C['text']) + sp('  ·  ', C['dim'])
      + sp(f'{d["total"]}', C['snow'], True) + sp(' contributions', C['dim']))
s2 = (sp('streak ', C['dim']) + sp(str(d['streak']), C['green'], True) + sp('  ·  best ', C['dim'])
      + sp(str(d['best']), C['yellow'], True) + sp('  ·  repos ', C['dim']) + sp(str(d['repos']), C['text'])
      + sp('  ·  followers ', C['dim']) + sp(str(d['followers']), C['text']) + sp('  ·  ', C['dim'])
      + sp('+commits ', C['green']) + sp('-bugs', C['red']))
line_at(y, s1, t, XT)
line_at(y + LH, s2, t, XT)
line_at(y + 2 * LH + 10, sp('▸▸ ', C['yellow']) + sp('auto mode on', C['yellow']) + sp(' (shift+tab to cycle)', C['dim']), t, XT)

# Clawd, from the same block characters my status line uses, as 2x2 sub-pixels.
QUAD = {'█': 'abcd', '▐': 'bd', '▌': 'ac', '▛': 'abc', '▜': 'abd', '▙': 'acd', '▟': 'bcd',
        '▝': 'b', '▘': 'a', '▗': 'd', '▖': 'c', '▀': 'ab', '▄': 'cd', ' ': '', '^': ''}
PX, PY = 6.0, 10.5


def clawd(rows, ox, oy):
    rects = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            for q in QUAD.get(ch, ''):
                dx, dy = (q in 'bd'), (q in 'cd')
                rects.append(f'<rect x="{ox + (2 * c + dx) * PX:.1f}" y="{oy + (2 * r + dy) * PY:.1f}" '
                             f'width="{PX + 0.3:.1f}" height="{PY + 0.3:.1f}"/>')
    return ''.join(rects)


cx, cy = W - 9 * 2 * PX - 60, y - 16
open_eyes = clawd([' ▐▛███▜▌ ', '▝▜█████▛▘', '  ▘▘ ▝▝  '], cx, cy)
closed = clawd([' ▐▀███▀▌ ', '▝▜█████▛▘', '  ▘▘ ▝▝  '], cx, cy)
blink = 'values="1;1;0;1" keyTimes="0;0.9;0.93;0.97" dur="4s" repeatCount="indefinite" calcMode="discrete"'
parts.append(f'<g opacity="0" fill="{C["orange"]}" shape-rendering="crispEdges">'
             f'<g><animate attributeName="opacity" {blink}/>{open_eyes}</g>'
             f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;0" keyTimes="0;0.9;0.93;0.97" dur="4s" repeatCount="indefinite" calcMode="discrete"/>{closed}</g>'
             f'{show(t)}</g>')
parts.append(f'<text x="{cx - 14}" y="{cy + 10}" text-anchor="end" opacity="0" fill="{C["dim"]}">zZz{show(t)}</text>')

assert t < T * 0.9, f'animation ({t:.1f}s) does not fit the cycle ({T}s)'
H = int(y + 2 * LH + 34)
FONT = "'JetBrains Mono', 'JetBrainsMono Nerd Font', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
clock = now.strftime('%H:%M')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Pablo Nicolás Marín (Slylem0)</title>
<desc id="desc">A Claude Code session in my terminal: I ask "who is pablo?", it runs fastfetch with my profile and stack, answers, lists my three latest commits, and my status line shows my real GitHub stats with Clawd in the corner.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#1d2330"/><stop offset="0.55" stop-color="{C['bg']}"/><stop offset="1" stop-color="#1a2232"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="10" fill="url(#bg)"/>
<text x="{W - 40}" y="{H * 0.62:.0f}" text-anchor="end" font-family="{FONT}" font-size="150" font-weight="300" fill="#8fa8c8" opacity="0.05">{clock}</text>
<g font-family="{FONT}" font-size="{FS}" fill="{C['text']}">
{chr(10).join(parts)}
</g>
</svg>
'''
open(OUT, 'w', encoding='utf-8').write(svg)
print(f'{OUT}: {W}x{H}, cycle {T}s, animation {t:.1f}s')
