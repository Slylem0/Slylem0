"""Generate assets/terminal.svg: an animated terminal for the profile README.

It mirrors my real setup: a Ghostty window tiled by Hyprland on Omarchy,
Nord colours, my starship prompt and my fastfetch layout (Omarchy logo plus
boxed sections). Animation is SMIL only, which GitHub renders inside <img>.

Usage: python gen_terminal.py <out.svg> <omarchy-logo.txt>
"""
import sys
from html import escape

OUT, LOGO = sys.argv[1], sys.argv[2]

T = 16.0                       # full cycle (s), then it starts over
W, LH, FS = 900, 19, 13
X0, Y0 = 28, 44
CW = 7.8                       # monospace cell width at FS 13 (JetBrains Mono)

N = {  # Nord
    'bg': '#2e3440', 'bg2': '#3b4252', 'border': '#88c0d0', 'text': '#d8dee9',
    'snow': '#eceff4', 'dim': '#616e88', 'frost': '#88c0d0', 'frost2': '#81a1c1',
    'frost3': '#5e81ac', 'green': '#a3be8c', 'yellow': '#ebcb8b', 'orange': '#d08770',
    'red': '#bf616a', 'purple': '#b48ead',
}
parts = []


def show(t, attr='opacity'):
    """Appears at second t and stays until the end of the cycle."""
    return (f'<animate attributeName="{attr}" values="0;1;0" keyTimes="0;{t / T:.4f};0.985" '
            f'dur="{T}s" repeatCount="indefinite" calcMode="discrete"/>')


def letter(ch, t):
    ch = escape(ch) if ch != ' ' else '&#160;'
    return f'<tspan fill-opacity="0">{ch}{show(t, "fill-opacity")}</tspan>'


def text(x, y, content, t, extra=''):
    parts.append(f'<text x="{x:.1f}" y="{y}" opacity="0" xml:space="preserve" {extra}>{content}{show(t)}</text>')


def span(s, color, bold=False):
    b = ' font-weight="700"' if bold else ''
    return f'<tspan fill="{color}"{b}>{escape(s)}</tspan>'


def prompt_spans(path='~'):
    # starship: user, dir, then the arrow
    return span('pablo ', N['snow'], True) + span(path + ' ', N['frost'], True) + span('❯ ', N['green'], True)


def prompt(line, t, cmd, step=0.06):
    y = Y0 + line * LH
    letters = ''.join(letter(ch, t + 0.3 + i * step) for i, ch in enumerate(cmd))
    parts.append(f'<text x="{X0}" y="{y}" opacity="0" xml:space="preserve">{prompt_spans()}'
                 f'<tspan fill="{N["text"]}">{letters}</tspan>{show(t)}</text>')
    return t + 0.3 + len(cmd) * step + 0.35


# 1. fastfetch -------------------------------------------------------------
line = 0
t = prompt(line, 0.4, 'fastfetch')

logo = [r.rstrip('\n') for r in open(LOGO, encoding='utf-8').read().splitlines() if r.strip()]
PX, PY = 4.0, 8.0               # one logo cell as a pixel block
lx, ly = X0 + 4, Y0 + (line + 1) * LH + 2
rects = []
for r, row in enumerate(logo):
    c = 0
    while c < len(row):
        if row[c] == '█':
            s = c
            while c < len(row) and row[c] == '█':
                c += 1
            rects.append(f'<rect x="{lx + s * PX:.1f}" y="{ly + r * PY:.1f}" width="{(c - s) * PX:.1f}" height="{PY:.1f}"/>')
        else:
            c += 1
logo_h = len(logo) * PY
parts.append(f'<g fill="{N["frost"]}" opacity="0">{"".join(rects)}{show(t)}</g>')

BX = lx + 56 * PX + 34          # info column
BOXW = 52                       # inner width in cells
sections = [
    ('Profile', [
        ('', 'Name', 'Pablo Nicolás Marín'),
        ('', 'Role', 'Cloud & Backend Builder'),
        ('', 'Study', 'Systems Engineering · Universidad del Valle'),
        ('', 'Cert', 'AWS Certified Cloud Practitioner'),
        ('', 'Club', 'AWS Student Builder Group Univalle'),
    ]),
    ('Software', [
        ('', 'OS', 'Omarchy (Arch Linux)'),
        ('', 'WM', 'Hyprland (Wayland)'),
        ('', 'Term', 'Ghostty · tmux · starship'),
        ('', 'Editor', 'Neovim (LazyVim)'),
        ('', 'Theme', 'Nord'),
    ]),
    ('Stack', [
        ('', 'Cloud', 'Lambda · DynamoDB · Bedrock · CDK · Amplify'),
        ('', 'Langs', 'TypeScript · Python · C++ · Go · Java'),
    ]),
]
row = line + 1
tt = t + 0.25
BW = W - BX - 34                # box width in px
for title, items in sections:
    top = Y0 + row * LH - 5     # box top edge sits on the title's middle
    bottom = Y0 + (row + len(items)) * LH + 9
    tw = len(title) * CW + 14
    tx = BX + (BW - tw) / 2
    box = (f'<rect x="{BX}" y="{top}" width="{BW}" height="{bottom - top}" rx="3" fill="none" stroke="{N["dim"]}"/>'
           f'<rect x="{tx:.1f}" y="{top - 8}" width="{tw:.1f}" height="16" fill="{N["bg"]}"/>'
           f'<text x="{tx + 7:.1f}" y="{top + 4}" fill="{N["frost3"]}">{escape(title)}</text>')
    parts.append(f'<g opacity="0">{box}{show(tt)}</g>')
    tt += 0.08
    row += 1
    for i, (_, k, v) in enumerate(items):
        content = span(f'{k:<7}', N['frost2'], True) + span(v, N['text'])
        text(BX + 16, Y0 + row * LH, content, tt)
        tt += 0.08
        row += 1
    row += 1
row -= 1
# Colour row, like fastfetch's palette module.
pal = [N['red'], N['orange'], N['yellow'], N['green'], N['frost'], N['frost3'], N['purple'], N['snow']]
row += 1
dots = ''.join(f'<circle cx="{BX + 14 + j * 20}" cy="{Y0 + row * LH - 4}" r="5.5" fill="{c}"/>' for j, c in enumerate(pal))
parts.append(f'<g opacity="0">{dots}{show(tt)}</g>')
tt += 0.4
info_bottom = Y0 + row * LH
logo_bottom = ly + logo_h
# center the logo against the info column
shift = ((info_bottom - (Y0 + (line + 1) * LH)) - logo_h) / 2
parts[1] = parts[1].replace('<g fill=', f'<g transform="translate(0 {shift:.1f})" fill=', 1)
line = row + 1
t = tt

# 2. what I'm on now -------------------------------------------------------
t = prompt(line, t, 'cat now.md')
now = [
    (N['frost'], '## now'),
    (N['text'], '- Shipping serverless backends on AWS from a Linux terminal in Buga, Colombia.'),
    (N['text'], '- Latest: SEE YOU SPACE BUILDER, my portfolio with Amazon Bedrock inside.'),
    (N['text'], '- Next: AWS Certified AI Practitioner.'),
]
for i, (c, s) in enumerate(now):
    line += 1
    text(X0, Y0 + line * LH, span(s, c, i == 0), t + i * 0.12)
t += len(now) * 0.12 + 0.6

# 3. idle prompt with a blinking block cursor ---------------------------------
line += 2
y = Y0 + line * LH
cursor = (f'<tspan fill="{N["snow"]}">█<animate attributeName="fill-opacity" values="1;0" '
          f'dur="1.06s" repeatCount="indefinite" calcMode="discrete"/></tspan>')
parts.append(f'<text x="{X0}" y="{y}" opacity="0" xml:space="preserve">{prompt_spans()}{cursor}{show(t)}</text>')

assert t < T * 0.9, f'animation ({t:.1f}s) does not fit the cycle ({T}s)'
H = int(y + 26)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Pablo Nicolás Marín (Slylem0) terminal</title>
<desc id="desc">Animated Ghostty terminal on Omarchy with the Nord theme: fastfetch prints the Omarchy logo with my profile, software and AWS stack, then cat now.md shows what I am working on.</desc>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="8" fill="{N['bg']}" stroke="{N['border']}" stroke-width="2"/>
<g font-family="'JetBrains Mono', 'JetBrainsMono Nerd Font', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace" font-size="{FS}" fill="{N['text']}">
{chr(10).join(parts)}
</g>
</svg>
'''
open(OUT, 'w', encoding='utf-8').write(svg)
print(f'{OUT}: {W}x{H}, cycle {T}s, animation {t:.1f}s')
