# -*- coding: utf-8 -*-
"""Flat 2D object drawings for the 'Kubernetes basics' unit. Hand-authored SVG, no image model.
Run: python kubernetes-basics/draw.py"""
import io
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
NAVY, INK, WHITE, LINE, SOFT = '#1C2A4A', '#23262D', '#FFFFFF', '#C9CED8', '#EEF0F4'
BLUE, GREEN, PURPLE, ORANGE, BROWN, RED = '#0052A4', '#00A84D', '#996CAC', '#EF7C1C', '#CD7C2F', '#D7372B'
FONT = 'font-family="Gothic A1, Helvetica, Arial, sans-serif" font-weight="800" text-anchor="middle"'


def svg(name, body, vb='0 0 160 100'):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>\n'
    io.open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n').write(s)


def box(x, y, w, h, color):
    """A small shipping container."""
    ribs = ''.join(f'<rect x="{x + 4 + i * (w - 8) / 6:.1f}" y="{y + 4}" width="{(w - 8) / 12:.1f}" height="{h - 8}" fill="#000" opacity=".13"/>'
                   for i in range(6))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{color}"/>' + ribs


os.makedirs(OUT, exist_ok=True)

# c01 shipping container
svg('c01-container.svg', f'<rect x="16" y="84" width="128" height="5" rx="2.5" fill="{LINE}"/>' + box(24, 30, 112, 54, BLUE)
    + f'<rect x="24" y="30" width="112" height="6" fill="#003C7A"/>')

# c02 ship steering wheel (8 spokes)
spokes = ''.join(
    f'<line x1="{80 + 12 * math.cos(a):.1f}" y1="{50 + 12 * math.sin(a):.1f}" x2="{80 + 44 * math.cos(a):.1f}" y2="{50 + 44 * math.sin(a):.1f}" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/>'
    for a in (i * math.pi / 4 for i in range(8)))
svg('c02-wheel.svg', spokes + f'<circle cx="80" cy="50" r="32" fill="none" stroke="{BLUE}" stroke-width="7"/>'
    f'<circle cx="80" cy="50" r="11" fill="{BLUE}"/><circle cx="80" cy="50" r="4" fill="{WHITE}"/>')

# c03 three servers in a rack
rack = ''.join(f'<rect x="44" y="{14 + i * 25}" width="72" height="20" rx="3" fill="{NAVY}"/>'
               f'<circle cx="54" cy="{24 + i * 25}" r="3" fill="{GREEN}"/>'
               f'<rect x="64" y="{22 + i * 25}" width="40" height="4" rx="2" fill="#3B4A6E"/>' for i in range(3))
svg('c03-nodes.svg', rack + f'<rect x="38" y="90" width="84" height="4" rx="2" fill="{LINE}"/>')

# c04 pea pod with containers as peas
svg('c04-pod.svg',
    f'<path d="M18 52 Q40 22 80 24 Q122 26 142 48 Q122 76 80 76 Q40 76 18 52Z" fill="#6FB35A"/>'
    f'<path d="M24 52 Q46 30 80 32 Q116 34 136 50 Q116 68 80 68 Q44 68 24 52Z" fill="#B8E0A4"/>'
    + ''.join(f'<circle cx="{46 + i * 22}" cy="50" r="10" fill="{GREEN}"/>' for i in range(4))
    + f'<path d="M142 48 q8 -8 6 -18" stroke="#4E8A4F" stroke-width="3" fill="none" stroke-linecap="round"/>')

# c05 YAML document
lines = [(0, 34), (1, 40), (2, 30), (2, 36), (1, 26), (2, 38)]
svg('c05-yaml.svg',
    f'<path d="M46 8 H102 L118 24 V92 H46Z" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
    f'<path d="M102 8 V24 H118" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>'
    + ''.join(f'<rect x="{54 + ind * 8}" y="{30 + i * 10}" width="{w}" height="4" rx="2" fill="{PURPLE if ind == 0 else (INK if ind == 1 else LINE)}"/>'
              for i, (ind, w) in enumerate(lines)))

# c06 three identical replicas and the number 3
svg('c06-replicas.svg', ''.join(box(18 + i * 38, 44, 32, 26, PURPLE) for i in range(3))
    + f'<circle cx="138" cy="34" r="14" fill="{NAVY}"/><text x="138" y="40" {FONT} font-size="17" fill="{WHITE}">3</text>'
    + f'<rect x="14" y="76" width="112" height="4" rx="2" fill="{LINE}"/>')

# c07 signpost pointing to three boxes
svg('c07-sign.svg',
    f'<rect x="32" y="20" width="6" height="72" rx="2" fill="#9AA3B2"/>'
    f'<path d="M20 22 H70 L80 32 L70 42 H20Z" fill="{PURPLE}"/>'
    f'<rect x="28" y="30" width="34" height="4" rx="2" fill="{WHITE}"/>'
    + ''.join(box(92, 18 + i * 24, 40, 18, '#B79BC5') for i in range(3))
    + f'<path d="M80 32 C86 32 86 27 90 27 M80 32 H90 M80 32 C86 32 86 75 90 75 M80 32 C86 32 86 51 90 51" stroke="{LINE}" stroke-width="2" fill="none"/>'
    + f'<rect x="20" y="90" width="30" height="4" rx="2" fill="{LINE}"/>')

# c08 scale up: arrow over growing stacks
svg('c08-scale.svg',
    box(20, 70, 24, 18, ORANGE)
    + box(54, 56, 24, 18, ORANGE) + box(54, 76, 24, 12, ORANGE)
    + box(88, 42, 24, 14, ORANGE) + box(88, 58, 24, 14, ORANGE) + box(88, 74, 24, 14, ORANGE)
    + f'<path d="M22 50 L104 14" stroke="{NAVY}" stroke-width="5" stroke-linecap="round"/>'
    f'<path d="M96 8 L112 11 L102 24Z" fill="{NAVY}"/>'
    f'<rect x="14" y="90" width="130" height="4" rx="2" fill="{LINE}"/>')

# c09 self-heal: cracked box, circular arrow, new box
svg('c09-heal.svg',
    box(14, 40, 42, 30, '#B9BEC8')
    + f'<path d="M32 40 L28 52 L36 58 L30 70" stroke="{WHITE}" stroke-width="3" fill="none"/>'
    + f'<path d="M66 62 A16 16 0 1 1 94 60" stroke="{ORANGE}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    f'<path d="M86 56 L98 66 L100 52Z" fill="{ORANGE}"/>'
    + box(104, 40, 42, 30, GREEN)
    + f'<rect x="10" y="78" width="140" height="4" rx="2" fill="{LINE}"/>')

# c10 magnifying glass over log lines
svg('c10-logs.svg',
    f'<rect x="20" y="10" width="92" height="80" rx="6" fill="{NAVY}"/>'
    + ''.join(f'<rect x="28" y="{20 + i * 11}" width="{[60, 44, 70, 38, 56, 30][i]}" height="4" rx="2" fill="{RED if i == 3 else "#5A6C93"}"/>' for i in range(6))
    + f'<circle cx="104" cy="54" r="22" fill="{WHITE}" fill-opacity=".25" stroke="{BROWN}" stroke-width="7"/>'
    f'<path d="M120 70 L140 90" stroke="{BROWN}" stroke-width="10" stroke-linecap="round"/>')

# c11 roll back: curved arrow pointing left over a version tag
svg('c11-rollback.svg',
    f'<path d="M118 70 A38 38 0 0 0 48 40" stroke="{BROWN}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    f'<path d="M34 34 L56 28 L50 50Z" fill="{BROWN}"/>'
    f'<rect x="58" y="62" width="44" height="22" rx="11" fill="{NAVY}"/>'
    f'<text x="80" y="78" {FONT} font-size="12" fill="{WHITE}">v1</text>')

print('drawn:', sorted(os.listdir(OUT)))
