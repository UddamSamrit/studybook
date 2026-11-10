# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 10 · Security and RBAC'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/10-security/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: idcard(12,26,66,48,BLUE)+arrow(84,50,104,50)+check(128,34,1)+cross(128,66,1),
    'c02.svg': lambda: panel(34,10,92,80)+check(54,30,.6)+check(54,50,.6)+cross(54,70,.6,GREY)+"".join(f'<rect x="70" y="{28+i*20}" width="{[44,36,40][i]}" height="4" rx="2" fill="{INK if i<2 else LINE}"/>' for i in range(3)),
    'c03.svg': lambda: idcard(8,28,58,44,BLUE)+f'<rect x="68" y="44" width="24" height="12" rx="6" fill="none" stroke="{GREY}" stroke-width="4"/>'+panel(96,24,56,52)+check(110,40,.45)+check(110,60,.45)+f'<rect x="120" y="38" width="24" height="4" rx="2" fill="{INK}"/><rect x="120" y="58" width="20" height="4" rx="2" fill="{INK}"/>',
    'c04.svg': lambda: idcard(14,26,64,48,PURPLE,True)+arrow(84,50,98,50)+box(104,36,44,28,GREEN),
    'c05.svg': lambda: f'<rect x="20" y="14" width="42" height="74" rx="3" fill="{BROWN}"/><circle cx="54" cy="52" r="3.5" fill="{YELLOW}"/>'+key(112,50,1.0),
    'c06.svg': lambda: f'<path d="M48 70 L42 34 L62 50 L80 26 L98 50 L118 34 L112 70Z" fill="{YELLOW}"/><rect x="48" y="72" width="64" height="10" rx="3" fill="{YELLOW}"/><line x1="36" y1="88" x2="124" y2="14" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>',
    'c07.svg': lambda: box(8,38,42,26,BLUE)+wall(70,26,4,RED)+box(110,38,42,26,GREEN),
    'c08.svg': lambda: box(12,30,72,44,BLUE)+magnifier(104,44,20),
    'c09.svg': lambda: circ_arrow(68,50,24,GREEN)+shield(126,50,.8),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
