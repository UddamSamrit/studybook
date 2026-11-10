# -*- coding: utf-8 -*-
"""Flat 2D object drawings for the 'Introducing yourself' unit. Hand-authored SVG, no image model.
Run: python english/speaking/introducing-yourself/draw.py"""
import io
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
NAVY, INK, WHITE, LINE, SOFT = '#1C2A4A', '#23262D', '#FFFFFF', '#C9CED8', '#EEF0F4'
BLUE, GREEN, PURPLE, ORANGE, BROWN, RED, YELLOW = '#0052A4', '#00A84D', '#996CAC', '#EF7C1C', '#CD7C2F', '#D7372B', '#F5B700'
FONT = 'font-family="Gothic A1, Helvetica, Arial, sans-serif" font-weight="800" text-anchor="middle"'


def svg(name, body, vb='0 0 160 100'):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>\n'
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(s)


def bubble(x, y, w, h, fill, tail='left'):
    tx = x + 18 if tail == 'left' else x + w - 18
    d = -1 if tail == 'left' else 1
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
            f'<path d="M{tx} {y + h - 1} L{tx + d * 4} {y + h + 14} L{tx - d * 12} {y + h - 1}Z" fill="{fill}"/>')


os.makedirs(OUT, exist_ok=True)

# c01 speech bubble "Hi!"
svg('c01-hi.svg', bubble(30, 12, 100, 62, WHITE)
    + f'<text x="80" y="57" {FONT} font-size="34" fill="{BLUE}">Hi!</text>')

# c02 name tag
svg('c02-nametag.svg',
    f'<rect x="22" y="14" width="116" height="74" rx="8" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M22 22 A8 8 0 0 1 30 14 H130 A8 8 0 0 1 138 22 V38 H22Z" fill="{RED}"/>'
    f'<text x="80" y="32" {FONT} font-size="13" fill="{WHITE}">HELLO</text>'
    f'<text x="80" y="47" {FONT} font-size="7" fill="{WHITE}" opacity="0">.</text>'
    f'<path d="M40 66 q8 -12 16 0 t16 0 t16 0 t16 0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round"/>'
    f'<rect x="22" y="76" width="116" height="4" fill="{RED}"/>')

# c03 map pin
svg('c03-pin.svg',
    f'<ellipse cx="80" cy="90" rx="26" ry="6" fill="{LINE}"/>'
    f'<path d="M80 90 C70 72 54 58 54 38 A26 26 0 0 1 106 38 C106 58 90 72 80 90Z" fill="{GREEN}"/>'
    f'<circle cx="80" cy="38" r="10" fill="{WHITE}"/>')

# c04 small house
svg('c04-house.svg',
    f'<rect x="20" y="88" width="120" height="5" rx="2.5" fill="{LINE}"/>'
    f'<rect x="46" y="46" width="68" height="42" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M38 50 L80 14 L122 50Z" fill="{GREEN}"/>'
    f'<rect x="72" y="62" width="16" height="26" rx="2" fill="{NAVY}"/>'
    f'<rect x="52" y="56" width="13" height="13" rx="2" fill="{SOFT}" stroke="{LINE}" stroke-width="1.5"/>'
    f'<rect x="95" y="56" width="13" height="13" rx="2" fill="{SOFT}" stroke="{LINE}" stroke-width="1.5"/>')

# c05 laptop with code
svg('c05-laptop.svg',
    f'<rect x="38" y="12" width="84" height="56" rx="5" fill="{NAVY}"/>'
    f'<rect x="43" y="17" width="74" height="46" rx="2" fill="#2B3A5E"/>'
    f'<rect x="49" y="24" width="22" height="4" rx="2" fill="{PURPLE}"/><rect x="74" y="24" width="18" height="4" rx="2" fill="{WHITE}"/>'
    f'<rect x="55" y="33" width="30" height="4" rx="2" fill="{YELLOW}"/><rect x="88" y="33" width="14" height="4" rx="2" fill="{WHITE}"/>'
    f'<rect x="55" y="42" width="20" height="4" rx="2" fill="{GREEN}"/>'
    f'<rect x="49" y="51" width="12" height="4" rx="2" fill="{PURPLE}"/>'
    f'<path d="M24 72 H136 L130 84 H30Z" fill="{LINE}"/><rect x="70" y="74" width="20" height="3" rx="1.5" fill="#9AA3B2"/>')

# c06 open book with ABC
svg('c06-book.svg',
    f'<path d="M80 20 Q52 12 20 18 V84 Q52 78 80 86Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M80 20 Q108 12 140 18 V84 Q108 78 80 86Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M80 20 V86" stroke="{PURPLE}" stroke-width="3"/>'
    f'<text x="50" y="58" {FONT} font-size="24" fill="{PURPLE}">AB</text>'
    + ''.join(f'<path d="M90 {36 + i * 11} Q111 {32 + i * 11} 132 {36 + i * 11}" stroke="{LINE}" stroke-width="2.5" fill="none"/>' for i in range(4)))

# c07 headphones with a music note
svg('c07-headphones.svg',
    f'<path d="M44 62 V50 A36 36 0 0 1 116 50 V62" stroke="{NAVY}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    f'<rect x="32" y="54" width="22" height="34" rx="9" fill="{ORANGE}"/>'
    f'<rect x="106" y="54" width="22" height="34" rx="9" fill="{ORANGE}"/>'
    f'<path d="M80 38 V68" stroke="{INK}" stroke-width="4"/><path d="M80 38 L94 42 V50 L80 46Z" fill="{INK}"/>'
    f'<ellipse cx="74" cy="69" rx="7" ry="5.5" fill="{INK}"/>')

# c08 house with a heart (family time)
svg('c08-family.svg',
    f'<rect x="20" y="88" width="120" height="5" rx="2.5" fill="{LINE}"/>'
    f'<rect x="44" y="46" width="72" height="42" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M36 50 L80 12 L124 50Z" fill="{ORANGE}"/>'
    f'<path d="M80 80 C66 70 60 64 60 57 A8 8 0 0 1 80 54 A8 8 0 0 1 100 57 C100 64 94 70 80 80Z" fill="{RED}"/>')

# c09 two speech bubbles
svg('c09-chat.svg', bubble(14, 10, 78, 44, WHITE)
    + f'<rect x="28" y="24" width="48" height="5" rx="2.5" fill="{LINE}"/><rect x="28" y="35" width="34" height="5" rx="2.5" fill="{LINE}"/>'
    + bubble(66, 44, 80, 40, BROWN, tail='right')
    + f'<rect x="80" y="57" width="50" height="5" rx="2.5" fill="{WHITE}"/><rect x="80" y="68" width="30" height="5" rx="2.5" fill="{WHITE}"/>')


# c10 two coffee cups
def cup(x, color):
    return (f'<path d="M{x} 44 H{x + 40} L{x + 36} 84 H{x + 4}Z" fill="{color}"/>'
            f'<path d="M{x + 40} 52 A9 9 0 0 1 {x + 40} 70" stroke="{color}" stroke-width="5" fill="none"/>'
            f'<rect x="{x - 4}" y="38" width="48" height="8" rx="3" fill="{NAVY}"/>'
            f'<path d="M{x + 14} 30 q-5 -7 0 -14 M{x + 26} 30 q-5 -7 0 -14" stroke="{LINE}" stroke-width="3" fill="none" stroke-linecap="round"/>')


svg('c10-coffee.svg', f'<rect x="20" y="86" width="120" height="5" rx="2.5" fill="{LINE}"/>' + cup(30, BROWN) + cup(86, '#B5A27A'))

# x question mark in a bubble (ask back)
svg('x-question.svg', bubble(40, 10, 80, 66, WHITE)
    + f'<text x="80" y="62" {FONT} font-size="46" fill="{BROWN}">?</text>')

print('drawn:', sorted(os.listdir(OUT)))
