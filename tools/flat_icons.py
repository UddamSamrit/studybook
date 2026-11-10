# -*- coding: utf-8 -*-
"""Shared flat 2D object pieces for unit pictures (viewBox 0 0 160 100, palette from DESIGN.md).

Each function returns an SVG fragment; a unit's draw.py combines a few of them per card and
calls save(). Standard library only."""
import io
import math
import os

NAVY, INK, WHITE, LINE, SOFT, GREY = '#1C2A4A', '#23262D', '#FFFFFF', '#C9CED8', '#EEF0F4', '#9AA3B2'
BLUE, GREEN, PURPLE, ORANGE, BROWN, RED, YELLOW = '#0052A4', '#00A84D', '#996CAC', '#EF7C1C', '#CD7C2F', '#D7372B', '#F5B700'
FONT = 'font-family="Gothic A1, Helvetica, Arial, sans-serif" font-weight="800" text-anchor="middle"'


def save(out_dir, name, body):
    os.makedirs(out_dir, exist_ok=True)
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 100">{body}</svg>\n'
    io.open(os.path.join(out_dir, name), 'w', encoding='utf-8', newline='\n').write(s)


def text(x, y, s, size=12, c=INK):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'<text x="{x}" y="{y}" {FONT} font-size="{size}" fill="{c}">{s}</text>'


def ground(y=90, x=14, w=132):
    return f'<rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{LINE}"/>'


def box(x, y, w, h, c=BLUE):
    """Shipping container (the picture for a container / pod)."""
    n = max(3, int(w // 9))
    ribs = ''.join(f'<rect x="{x + 4 + i * (w - 8) / n:.1f}" y="{y + 3}" width="{(w - 8) / n / 2:.1f}" height="{h - 6}" fill="#000" opacity=".13"/>'
                   for i in range(n))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{c}"/>' + ribs


def ghost(x, y, w, h):
    """Dashed outline: something that is gone or not there yet."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="none" stroke="{GREY}" stroke-width="2" stroke-dasharray="5 4"/>'


def server(x, y, w=72, c=NAVY, led=GREEN):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="3" fill="{c}"/>'
            f'<circle cx="{x + 10}" cy="{y + 10}" r="3" fill="{led}"/>'
            f'<rect x="{x + 20}" y="{y + 8}" width="{w * .55:.0f}" height="4" rx="2" fill="#3B4A6E"/>')


def rack(x=44, y=14, n=3, w=72, leds=None):
    leds = leds or [GREEN] * n
    return ''.join(server(x, y + i * 25, w, led=leds[i]) for i in range(n))


def doc(x, y, w=56, h=78, c=PURPLE, lines=(0, 1, 2, 2, 1, 2)):
    widths = [34, 40, 30, 36, 26, 38, 30, 34]
    rows = ''.join(f'<rect x="{x + 8 + ind * 7}" y="{y + 20 + i * 9}" width="{min(widths[i % 8], w - 18 - ind * 7)}" height="4" rx="2" '
                   f'fill="{c if ind == 0 else (INK if ind == 1 else LINE)}"/>' for i, ind in enumerate(lines) if 20 + i * 9 < h - 6)
    return (f'<path d="M{x} {y} H{x + w - 14} L{x + w} {y + 14} V{y + h} H{x}Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M{x + w - 14} {y} V{y + 14} H{x + w}" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>' + rows)


def terminal(x=24, y=12, w=112, h=76, lines=None, prompt=True):
    lines = lines or [(GREEN, 50), ('#5A6C93', 70), ('#5A6C93', 40)]
    rows = ''.join(f'<rect x="{x + 10}" y="{y + 24 + i * 11}" width="{wd}" height="4" rx="2" fill="{c}"/>' for i, (c, wd) in enumerate(lines))
    p = f'<path d="M{x + 10} {y + h - 18} l6 4 l-6 4" stroke="{GREEN}" stroke-width="2.5" fill="none"/><rect x="{x + 20}" y="{y + h - 16}" width="8" height="4" fill="{WHITE}"/>' if prompt else ''
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{NAVY}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="13" rx="7" fill="#2B3A5E"/><rect x="{x}" y="{y + 7}" width="{w}" height="6" fill="#2B3A5E"/>'
            + ''.join(f'<circle cx="{x + 9 + i * 8}" cy="{y + 6.5}" r="2.5" fill="{cc}"/>' for i, cc in enumerate([RED, YELLOW, GREEN]))
            + rows + p)


def arrow(x1, y1, x2, y2, c=NAVY, w=5):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - 10 * math.cos(a), y2 - 10 * math.sin(a)
    l = (bx + 7 * math.cos(a + math.pi / 2), by + 7 * math.sin(a + math.pi / 2))
    r = (bx + 7 * math.cos(a - math.pi / 2), by + 7 * math.sin(a - math.pi / 2))
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{x2} {y2} L{l[0]:.1f} {l[1]:.1f} L{r[0]:.1f} {r[1]:.1f}Z" fill="{c}"/>')


def circ_arrow(cx, cy, r=16, c=ORANGE, back=False):
    """Curved arrow: restart (clockwise) or roll back (back=True)."""
    if back:
        return (f'<path d="M{cx + r} {cy + r * .6} A{r} {r} 0 1 0 {cx - r * .7} {cy - r * .7}" stroke="{c}" stroke-width="6" fill="none" stroke-linecap="round"/>'
                f'<path d="M{cx - r * 1.15:.1f} {cy - r * 1.2:.1f} L{cx - r * .2:.1f} {cy - r * 1.05:.1f} L{cx - r * .95:.1f} {cy - r * .2:.1f}Z" fill="{c}"/>')
    return (f'<path d="M{cx - r} {cy + r * .3} A{r} {r} 0 1 1 {cx + r * .8} {cy + r * .6}" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M{cx + r * .3:.1f} {cy + r * .4:.1f} L{cx + r * 1.15:.1f} {cy + r * 1.1:.1f} L{cx + r * 1.25:.1f} {cy + r * .05:.1f}Z" fill="{c}"/>')


def cloud(cx, cy, s=1.0, c=SOFT, stroke=LINE):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M-34 14 A16 16 0 0 1 -26 -12 A22 22 0 0 1 14 -18 A18 18 0 0 1 34 14Z" '
            f'fill="{c}" stroke="{stroke}" stroke-width="2"/></g>')


def lock(cx, cy, s=1.0, c=NAVY, open_=False):
    shackle = f'M-9 -4 V-12 A9 9 0 0 1 9 -12 V{-14 if open_ else -4}'
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="{shackle}" stroke="{GREY}" stroke-width="5" fill="none"/>'
            f'<rect x="-15" y="-5" width="30" height="24" rx="4" fill="{c}"/><circle cx="0" cy="5" r="3.5" fill="{WHITE}"/>'
            f'<rect x="-1.5" y="6" width="3" height="7" fill="{WHITE}"/></g>')


def key(cx, cy, s=1.0, c=YELLOW):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><circle cx="-18" cy="0" r="12" fill="{c}"/><circle cx="-18" cy="0" r="5" fill="{WHITE}"/>'
            f'<rect x="-8" y="-3.5" width="34" height="7" rx="2" fill="{c}"/><rect x="16" y="2" width="5" height="9" fill="{c}"/>'
            f'<rect x="8" y="2" width="5" height="7" fill="{c}"/></g>')


def gear(cx, cy, r=24, c=GREY):
    teeth = ''.join(f'<rect x="{-r * .18:.1f}" y="{-r * 1.18:.1f}" width="{r * .36:.1f}" height="{r * .4:.1f}" rx="2" transform="rotate({i * 45})" fill="{c}"/>' for i in range(8))
    return f'<g transform="translate({cx} {cy})">{teeth}<circle r="{r * .88:.1f}" fill="{c}"/><circle r="{r * .38:.1f}" fill="{WHITE}"/></g>'


def cyl(cx, cy, w=44, h=50, c=BLUE, label=''):
    rx, ry = w / 2, w / 7
    lab = text(cx, cy + h / 2 + 4, label, 11, WHITE) if label else ''
    return (f'<path d="M{cx - rx} {cy} V{cy + h} A{rx} {ry} 0 0 0 {cx + rx} {cy + h} V{cy}Z" fill="{c}"/>'
            f'<path d="M{cx - rx} {cy + h / 2} A{rx} {ry} 0 0 0 {cx + rx} {cy + h / 2}" stroke="#000" stroke-opacity=".15" stroke-width="2" fill="none"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}"/><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" fill-opacity=".25"/>' + lab)


def tag(cx, cy, label='v2', c=PURPLE, w=58):
    return (f'<path d="M{cx - w / 2} {cy - 14} H{cx + w / 2 - 12} L{cx + w / 2} {cy} L{cx + w / 2 - 12} {cy + 14} H{cx - w / 2}Z" fill="{c}"/>'
            f'<circle cx="{cx + w / 2 - 12}" cy="{cy}" r="3" fill="{WHITE}"/>' + text(cx - 5, cy + 5, label, 14, WHITE))


def pill(cx, cy, label, c=GREEN, w=64, fg=WHITE, size=11):
    return f'<rect x="{cx - w / 2}" y="{cy - 10}" width="{w}" height="20" rx="10" fill="{c}"/>' + text(cx, cy + 4, label, size, fg)


def check(cx, cy, s=1.0, c=GREEN):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><circle r="13" fill="{c}"/>'
            f'<path d="M-6 0 L-1.5 5 L7 -5" stroke="{WHITE}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')


def cross(cx, cy, s=1.0, c=RED):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><circle r="13" fill="{c}"/>'
            f'<path d="M-5 -5 L5 5 M5 -5 L-5 5" stroke="{WHITE}" stroke-width="3.5" stroke-linecap="round"/></g>')


def heart(cx, cy, s=1.0, c=RED, pulse=False):
    p = (f'<path d="M-22 0 H-9 L-5 -9 L0 9 L4 -4 L7 0 H22" stroke="{WHITE}" stroke-width="3" fill="none" stroke-linejoin="round"/>' if pulse else '')
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M0 26 C-22 10 -30 0 -30 -10 A15 15 0 0 1 0 -16 A15 15 0 0 1 30 -10 C30 0 22 10 0 26Z" fill="{c}"/>{p}</g>')


def bell(cx, cy, s=1.0, c=YELLOW):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M-22 16 Q-16 10 -16 -4 A16 16 0 0 1 16 -4 Q16 10 22 16Z" fill="{c}"/>'
            f'<rect x="-24" y="15" width="48" height="5" rx="2.5" fill="{c}"/><circle cy="24" r="5" fill="{BROWN}"/><circle cy="-22" r="3.5" fill="{c}"/>'
            f'<path d="M-30 -14 q-6 8 0 16 M30 -14 q6 8 0 16" stroke="{c}" stroke-width="3" fill="none" stroke-linecap="round"/></g>')


def folder(x, y, w=60, h=44, c=YELLOW, label=''):
    lab = text(x + w / 2, y + h / 2 + 8, label, 11, INK) if label else ''
    return (f'<path d="M{x} {y + 4} A4 4 0 0 1 {x + 4} {y} H{x + w * .38:.0f} L{x + w * .46:.0f} {y + 7} H{x + w - 4} A4 4 0 0 1 {x + w} {y + 11} V{y + h - 4} '
            f'A4 4 0 0 1 {x + w - 4} {y + h} H{x + 4} A4 4 0 0 1 {x} {y + h - 4}Z" fill="{c}"/>'
            f'<rect x="{x}" y="{y + 12}" width="{w}" height="{h - 12}" rx="4" fill="#fff" fill-opacity=".25"/>' + lab)


def chart(x=24, y=14, w=112, h=72, c=BLUE, pts=(.7, .55, .62, .4, .45, .25, .3), fill=True):
    n = len(pts) - 1
    path = ' '.join(f'{"M" if i == 0 else "L"}{x + 8 + i * (w - 16) / n:.1f} {y + 6 + p * (h - 14):.1f}' for i, p in enumerate(pts))
    area = (f'<path d="{path} L{x + w - 8} {y + h - 8} L{x + 8} {y + h - 8}Z" fill="{c}" fill-opacity=".15"/>' if fill else '')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>' + area
            + f'<path d="{path}" stroke="{c}" stroke-width="3.5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')


def magnifier(cx, cy, r=18, c=BROWN):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{WHITE}" fill-opacity=".35" stroke="{c}" stroke-width="6"/>'
            f'<path d="M{cx + r * .72:.1f} {cy + r * .72:.1f} L{cx + r * 1.6:.1f} {cy + r * 1.6:.1f}" stroke="{c}" stroke-width="9" stroke-linecap="round"/>')


def shield(cx, cy, s=1.0, c=GREEN, mark=True):
    m = f'<path d="M-9 0 L-2 7 L10 -7" stroke="{WHITE}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' if mark else ''
    return f'<g transform="translate({cx} {cy}) scale({s})"><path d="M0 -32 L28 -22 V0 C28 18 14 28 0 34 C-14 28 -28 18 -28 0 V-22Z" fill="{c}"/>{m}</g>'


def chip(cx, cy, s=1.0, c=NAVY, label='CPU'):
    pins = ''.join(f'<rect x="{-20 + i * 9}" y="-30" width="4" height="8" fill="{GREY}"/><rect x="{-20 + i * 9}" y="22" width="4" height="8" fill="{GREY}"/>'
                   f'<rect x="-30" y="{-20 + i * 9}" width="8" height="4" fill="{GREY}"/><rect x="22" y="{-20 + i * 9}" width="8" height="4" fill="{GREY}"/>' for i in range(5))
    return (f'<g transform="translate({cx} {cy}) scale({s})">{pins}<rect x="-23" y="-23" width="46" height="46" rx="5" fill="{c}"/>'
            + text(0, 5, label, 12, WHITE) + '</g>')


def ram(x, y, w=100, c=GREEN):
    cells = ''.join(f'<rect x="{x + 8 + i * (w - 16) / 5:.1f}" y="{y + 6}" width="{(w - 16) / 5 - 4:.1f}" height="14" rx="1" fill="{INK}"/>' for i in range(5))
    teeth = ''.join(f'<rect x="{x + 6 + i * 6}" y="{y + 26}" width="3" height="5" fill="{YELLOW}"/>' for i in range(int((w - 12) / 6)))
    return f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="2" fill="{c}"/>' + cells + teeth


def globe(cx, cy, r=26, c=BLUE):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r * .45:.1f}" ry="{r}" fill="none" stroke="{WHITE}" stroke-width="2.5" opacity=".7"/>'
            f'<path d="M{cx - r} {cy} H{cx + r} M{cx - r * .87:.1f} {cy - r * .5:.1f} H{cx + r * .87:.1f} M{cx - r * .87:.1f} {cy + r * .5:.1f} H{cx + r * .87:.1f}" stroke="{WHITE}" stroke-width="2.5" opacity=".7"/>')


def package(cx, cy, s=1.0, c=BROWN):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M-30 -14 L0 -28 L30 -14 L0 0Z" fill="#E09A55"/>'
            f'<path d="M-30 -14 L0 0 V32 L-30 18Z" fill="{c}"/><path d="M30 -14 L0 0 V32 L30 18Z" fill="#A9611F"/>'
            f'<path d="M-15 -21 L15 -7 V8" stroke="{YELLOW}" stroke-width="5" fill="none"/></g>')


def bird(cx, cy, s=1.0, c=YELLOW):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><ellipse cx="0" cy="6" rx="24" ry="18" fill="{c}"/><circle cx="18" cy="-14" r="13" fill="{c}"/>'
            f'<path d="M30 -16 L40 -12 L30 -9Z" fill="{ORANGE}"/><circle cx="21" cy="-16" r="2.5" fill="{INK}"/>'
            f'<path d="M-6 0 Q4 -6 12 4 Q2 14 -10 10Z" fill="#E0A800"/><path d="M-22 6 L-38 0 L-32 12Z" fill="#E0A800"/>'
            f'<path d="M-4 24 V32 M6 24 V32" stroke="{BROWN}" stroke-width="3" stroke-linecap="round"/></g>')


def trophy(cx, cy, s=1.0, c=YELLOW):
    return (f'<g transform="translate({cx} {cy}) scale({s})"><path d="M-22 -30 H22 V-10 A22 22 0 0 1 -22 -10Z" fill="{c}"/>'
            f'<path d="M-22 -24 H-32 V-16 A12 12 0 0 0 -18 -6 M22 -24 H32 V-16 A12 12 0 0 1 18 -6" stroke="{c}" stroke-width="5" fill="none"/>'
            f'<rect x="-5" y="10" width="10" height="12" fill="{c}"/><rect x="-18" y="22" width="36" height="9" rx="2" fill="{BROWN}"/>'
            f'<path d="M0 -24 L3 -17 L10 -17 L4.5 -12.5 L6.5 -5.5 L0 -9.5 L-6.5 -5.5 L-4.5 -12.5 L-10 -17 L-3 -17Z" fill="{WHITE}"/></g>')


def idcard(x, y, w=70, h=48, c=BLUE, robot=False):
    face = (f'<rect x="{x + 8}" y="{y + 12}" width="22" height="20" rx="4" fill="{GREY}"/><circle cx="{x + 15}" cy="{y + 21}" r="2.5" fill="{WHITE}"/>'
            f'<circle cx="{x + 23}" cy="{y + 21}" r="2.5" fill="{WHITE}"/><rect x="{x + 17}" y="{y + 6}" width="4" height="6" fill="{GREY}"/>' if robot else
            f'<circle cx="{x + 19}" cy="{y + 18}" r="7" fill="{GREY}"/><path d="M{x + 7} {y + 36} A12 10 0 0 1 {x + 31} {y + 36}Z" fill="{GREY}"/>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{x}" y="{y + h - 8}" width="{w}" height="8" rx="3" fill="{c}"/>' + face
            + f'<rect x="{x + 38}" y="{y + 12}" width="{w - 46}" height="4" rx="2" fill="{INK}"/><rect x="{x + 38}" y="{y + 22}" width="{w - 52}" height="4" rx="2" fill="{LINE}"/>')


def branch(x, y, c=ORANGE):
    """Git branch: a main line and a branch that merges back."""
    return (f'<path d="M{x} {y} H{x + 110}" stroke="{NAVY}" stroke-width="5"/>'
            f'<path d="M{x + 22} {y} C{x + 34} {y - 26} {x + 70} {y - 26} {x + 86} {y}" stroke="{c}" stroke-width="5" fill="none"/>'
            + ''.join(f'<circle cx="{x + px}" cy="{y}" r="7" fill="{NAVY}"/>' for px in (0, 22, 86, 110))
            + f'<circle cx="{x + 54}" cy="{y - 20}" r="7" fill="{c}"/>')


def slider(x, y, w, pos, c=PURPLE):
    return (f'<rect x="{x}" y="{y - 2}" width="{w}" height="4" rx="2" fill="{LINE}"/><rect x="{x}" y="{y - 2}" width="{w * pos:.0f}" height="4" rx="2" fill="{c}"/>'
            f'<circle cx="{x + w * pos:.0f}" cy="{y}" r="7" fill="{WHITE}" stroke="{c}" stroke-width="3"/>')


def gauge(cx, cy, r=36, val=.8, c=ORANGE):
    a = math.pi * (1 - val)
    nx, ny = cx + (r - 8) * math.cos(a), cy - (r - 8) * math.sin(a)
    return (f'<path d="M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}" stroke="{LINE}" stroke-width="10" fill="none"/>'
            f'<path d="M{cx + r * math.cos(math.pi * .3):.1f} {cy - r * math.sin(math.pi * .3):.1f} A{r} {r} 0 0 1 {cx + r} {cy}" stroke="{RED}" stroke-width="10" fill="none"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="6" fill="{NAVY}"/>')


def light(cx, cy, on='green'):
    cols = {'red': RED, 'yellow': YELLOW, 'green': GREEN}
    return (f'<rect x="{cx - 14}" y="{cy - 40}" width="28" height="80" rx="8" fill="{NAVY}"/>'
            + ''.join(f'<circle cx="{cx}" cy="{cy - 24 + i * 24}" r="9" fill="{cols[k] if k == on else "#3B4A6E"}"/>' for i, k in enumerate(['red', 'yellow', 'green'])))


def book(cx, cy, c=BLUE):
    return (f'<path d="M{cx} {cy - 30} Q{cx - 28} {cy - 38} {cx - 60} {cy - 32} V{cy + 34} Q{cx - 28} {cy + 28} {cx} {cy + 36}Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M{cx} {cy - 30} Q{cx + 28} {cy - 38} {cx + 60} {cy - 32} V{cy + 34} Q{cx + 28} {cy + 28} {cx} {cy + 36}Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M{cx} {cy - 30} V{cy + 36}" stroke="{c}" stroke-width="3"/>')


def wall(x, y, n=4, c=RED):
    return ''.join(f'<rect x="{x + (8 if r % 2 else 0)}" y="{y + r * 12}" width="16" height="10" rx="1" fill="{c}"/>'
                   f'<rect x="{x + (8 if r % 2 else 0)}" y="{y + r * 12 + 11}" width="0" height="0"/>' for r in range(n))


def layers(cx=80, n=4, cols=(BLUE, GREEN, PURPLE, ORANGE)):
    """Image layers stacked like flat tiles."""
    out = []
    for i in range(n):
        y = 74 - i * 16
        out.append(f'<path d="M{cx - 46} {y} L{cx} {y - 14} L{cx + 46} {y} L{cx} {y + 14}Z" fill="{cols[i % len(cols)]}" stroke="{WHITE}" stroke-width="2"/>')
    return ''.join(out)


def signpost(x=32, label='web', c=BLUE):
    return (f'<rect x="{x}" y="20" width="6" height="72" rx="2" fill="{GREY}"/>'
            f'<path d="M{x - 12} 22 H{x + 38} L{x + 48} 32 L{x + 38} 42 H{x - 12}Z" fill="{c}"/>' + text(x + 16, 37, label, 12, WHITE)
            + f'<rect x="{x - 12}" y="90" width="30" height="4" rx="2" fill="{LINE}"/>')


def panel(x=30, y=10, w=100, h=80):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
