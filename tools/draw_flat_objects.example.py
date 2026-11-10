# -*- coding: utf-8 -*-
"""Flat 2D object drawings for the funeral unit (Rex: "draw 2D flat object", 2026-11-05).
Hand-authored SVG, no image generation. Run: python korean-funeral-visit/draw.py"""
import io
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
NAVY, INK, WHITE, LINE = '#1C2A4A', '#23262D', '#FFFFFF', '#C9CED8'
GREEN, YELLOW, RED, SOUP = '#00A84D', '#F5B700', '#D7372B', '#C8472B'


def svg(name, body, vb='0 0 160 100'):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>\n'
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(s)


def ribbon(x, y, k=1.0):
    """Black mourning ribbon centred at x,y."""
    return (f'<g transform="translate({x} {y}) scale({k})" fill="{INK}">'
            f'<path d="M0 0 L-9 -7 Q-14 -4 -12 2 Q-9 6 0 0Z"/><path d="M0 0 L9 -7 Q14 -4 12 2 Q9 6 0 0Z"/>'
            f'<path d="M-1 1 L-7 15 L-4 14 L-2 17 L2 2Z"/><path d="M1 1 L7 15 L4 14 L2 17 L-2 2Z"/>'
            f'<circle r="2.6"/></g>')


def mum(cx, cy, r):
    """White chrysanthemum head: three rings of petals."""
    out = []
    for ring, (n, rr, w, ln) in enumerate([(18, r * .62, r * .2, r * .48), (14, r * .4, r * .18, r * .36), (10, r * .2, r * .14, r * .24)]):
        for i in range(n):
            a = 360 / n * i + ring * 9
            out.append(f'<ellipse cx="0" cy="{-rr:.1f}" rx="{w:.1f}" ry="{ln:.1f}" transform="translate({cx} {cy}) rotate({a:.1f})"/>')
    return (f'<g fill="{WHITE}" stroke="{LINE}" stroke-width=".9">{"".join(out)}</g>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .13:.1f}" fill="#EBDDA8"/>')


os.makedirs(OUT, exist_ok=True)

# 1. phone with a mourning notice
svg('c1-phone.svg',
    f'<rect x="56" y="4" width="48" height="92" rx="9" fill="{NAVY}"/>'
    f'<rect x="60" y="13" width="40" height="74" rx="3" fill="{WHITE}"/>'
    f'<rect x="74" y="8" width="12" height="2.4" rx="1.2" fill="#3B4A6E"/>'
    f'<rect x="63" y="30" width="34" height="26" rx="4" fill="#EEF0F4"/>'
    + ribbon(71, 40, .55) +
    f'<rect x="78" y="36" width="15" height="3" rx="1.5" fill="{INK}"/><rect x="78" y="42" width="12" height="3" rx="1.5" fill="{LINE}"/>'
    f'<rect x="66" y="49" width="27" height="3" rx="1.5" fill="{LINE}"/>'
    f'<rect x="63" y="62" width="34" height="5" rx="2.5" fill="#EEF0F4"/><rect x="63" y="71" width="24" height="5" rx="2.5" fill="#EEF0F4"/>')

# 2. message bubble with a ribbon
svg('c2-message.svg',
    f'<path d="M30 14 H130 A14 14 0 0 1 144 28 V62 A14 14 0 0 1 130 76 H62 L44 92 L47 76 H30 A14 14 0 0 1 16 62 V28 A14 14 0 0 1 30 14Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2.5"/>'
    + ribbon(44, 40, 1.15) +
    f'<rect x="66" y="31" width="58" height="6" rx="3" fill="{INK}"/><rect x="66" y="44" width="46" height="6" rx="3" fill="{LINE}"/>'
    f'<rect x="66" y="57" width="52" height="6" rx="3" fill="{LINE}"/>')

# 3. white condolence envelope, written 부의
svg('c3-envelope.svg',
    f'<rect x="50" y="6" width="60" height="88" rx="3" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M50 9 L80 30 L110 9" fill="none" stroke="{LINE}" stroke-width="2"/>'
    f'<text x="80" y="56" font-family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="17" font-weight="700" fill="{INK}" text-anchor="middle">부</text>'
    f'<text x="80" y="78" font-family="Malgun Gothic, Apple SD Gothic Neo, Noto Sans KR, sans-serif" font-size="17" font-weight="700" fill="{INK}" text-anchor="middle">의</text>')

# 4. open guestbook and pen
svg('c4-guestbook.svg',
    f'<path d="M80 22 Q52 14 20 20 V84 Q52 78 80 86Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M80 22 Q108 14 140 20 V84 Q108 78 80 86Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M80 22 V86" stroke="{NAVY}" stroke-width="2.5"/>'
    + ''.join(f'<path d="M28 {32 + i * 11} Q50 {28 + i * 11} 72 {33 + i * 11}" stroke="{LINE}" stroke-width="2" fill="none"/>' for i in range(5))
    + ''.join(f'<path d="M88 {33 + i * 11} Q110 {28 + i * 11} 132 {32 + i * 11}" stroke="{LINE}" stroke-width="2" fill="none"/>' for i in range(5))
    + f'<path d="M38 41 q6 -6 12 0 t12 0" stroke="{INK}" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
    f'<g transform="translate(120 52) rotate(-38)"><rect x="-4" y="-34" width="8" height="52" rx="3" fill="{NAVY}"/>'
    f'<path d="M-4 18 L0 28 L4 18Z" fill="{INK}"/><rect x="-4" y="-34" width="8" height="10" rx="3" fill="#3B4A6E"/></g>')

# 5. one white chrysanthemum
svg('c5-flower.svg',
    f'<path d="M80 50 Q76 72 82 98" stroke="#4E8A4F" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    f'<path d="M79 76 Q62 66 56 74 Q66 82 79 76Z" fill="#5F9C5E"/><path d="M81 86 Q98 76 104 84 Q94 92 81 86Z" fill="#5F9C5E"/>'
    + mum(80, 38, 34))

# 6. chief mourner's armband
svg('c6-armband.svg',
    f'<ellipse cx="28" cy="50" rx="10" ry="22" fill="#111317"/>'
    f'<rect x="28" y="28" width="104" height="44" fill="{INK}"/>'
    f'<ellipse cx="132" cy="50" rx="10" ry="22" fill="#3A3E47"/>'
    f'<rect x="28" y="40" width="104" height="4.5" fill="{WHITE}"/><rect x="28" y="55" width="104" height="4.5" fill="{WHITE}"/>')

# 7. bowl of yukgaejang with a spoon
svg('c7-bowl.svg',
    f'<g transform="translate(118 30) rotate(32)"><rect x="-3" y="-30" width="6" height="44" rx="3" fill="#9AA3B2"/>'
    f'<ellipse cx="0" cy="18" rx="9" ry="12" fill="#9AA3B2"/></g>'
    f'<path d="M22 46 Q24 90 80 92 Q136 90 138 46Z" fill="#EEF0F4" stroke="{LINE}" stroke-width="2"/>'
    f'<ellipse cx="80" cy="46" rx="58" ry="14" fill="{SOUP}"/>'
    f'<ellipse cx="80" cy="46" rx="58" ry="14" fill="none" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M48 44 l14 3 M70 41 l12 4 M92 47 l14 -3 M60 50 l10 -2 M102 41 l10 3" stroke="#6FA552" stroke-width="3" stroke-linecap="round"/>'
    f'<rect x="80" y="48" width="12" height="4" rx="2" fill="#7A3B22"/><rect x="56" y="40" width="10" height="4" rx="2" fill="#7A3B22"/>'
    f'<rect x="64" y="96" width="32" height="3" rx="1.5" fill="{LINE}"/>')

# x1. calendar: three days
svg('x-calendar.svg',
    f'<rect x="38" y="12" width="84" height="80" rx="8" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M38 20 A8 8 0 0 1 46 12 H114 A8 8 0 0 1 122 20 V32 H38Z" fill="{NAVY}"/>'
    f'<rect x="56" y="6" width="6" height="14" rx="3" fill="#3B4A6E"/><rect x="98" y="6" width="6" height="14" rx="3" fill="#3B4A6E"/>'
    + ''.join(f'<rect x="{48 + i * 23}" y="46" width="17" height="17" rx="4" fill="{NAVY if i < 3 else "#EEF0F4"}"/>' for i in range(3))
    + ''.join(f'<rect x="{48 + i * 23}" y="68" width="17" height="14" rx="4" fill="#EEF0F4"/>' for i in range(3)))

# x2. dark suit jacket, white shirt, black tie
svg('x-jacket.svg',
    f'<path d="M80 14 L54 18 Q38 24 36 40 L32 96 H128 L124 40 Q122 24 106 18Z" fill="{INK}"/>'
    f'<path d="M66 16 L80 46 L94 16Z" fill="{WHITE}"/>'
    f'<path d="M77 22 H83 L85 50 L80 58 L75 50Z" fill="#0B0C0F"/>'
    f'<path d="M66 16 L58 30 L72 40 L80 58 Z M94 16 L102 30 L88 40 L80 58Z" fill="#33373F"/>'
    f'<circle cx="80" cy="70" r="2.4" fill="#4A4F59"/><circle cx="80" cy="82" r="2.4" fill="#4A4F59"/>')

# x3. a deep bow (pictogram)
svg('x-bow.svg',
    f'<rect x="20" y="84" width="120" height="6" rx="3" fill="{LINE}"/>'
    f'<circle cx="54" cy="72" r="9" fill="{NAVY}"/>'
    f'<path d="M64 68 Q84 52 104 60 L108 84 H96 L94 72 Q82 72 66 80Z" fill="{NAVY}"/>'
    f'<path d="M62 78 L52 84 H62Z" fill="{NAVY}"/>'
    f'<text x="122" y="40" font-family="Malgun Gothic, Apple SD Gothic Neo, sans-serif" font-size="22" font-weight="800" fill="{"#EF7C1C"}" text-anchor="middle">2</text>')
print('drawn:', sorted(os.listdir(OUT)))
