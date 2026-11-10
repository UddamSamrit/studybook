# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 4 · Services and Ingress'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes-04-services/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: box(14,38,48,30,GREEN)+pill(38,22,"10.1.4.7",GREY,60,WHITE,9)+arrow(68,53,92,53)+box(98,38,48,30,GREEN)+pill(122,22,"10.1.9.2",GREY,60,WHITE,9),
    'c02.svg': lambda: signpost(32,"web",BLUE)+"".join(box(98,18+i*24,46,18,GREEN) for i in range(3)),
    'c03.svg': lambda: tag(50,26,"app=web",ORANGE,90)+box(18,58,36,24,GREEN)+box(62,58,36,24,GREEN)+box(106,58,36,24,GREEN),
    'c04.svg': lambda: f'<rect x="12" y="10" width="136" height="80" rx="14" fill="{SOFT}" stroke="{BLUE}" stroke-width="3" stroke-dasharray="8 5"/>'+box(26,42,42,26,GREEN)+box(76,42,42,26,GREEN)+lock(132,32,.7),
    'c05.svg': lambda: globe(36,50,26)+arrow(68,50,94,50)+rack(100,24,2,48),
    'c06.svg': lambda: globe(22,50,16)+f'<path d="M40 50 C70 50 66 20 96 20 M40 50 H96 M40 50 C70 50 66 80 96 80" stroke="{ORANGE}" stroke-width="4" fill="none"/>'+pill(124,20,"/api",BLUE,50)+pill(124,50,"/web",GREEN,50)+pill(124,80,"/docs",PURPLE,50),
    'c07.svg': lambda: lock(52,56,1.6,GREEN)+pill(114,50,"https",GREEN,64,WHITE,13),
    'c08.svg': lambda: box(10,40,46,28,BLUE)+arrow(60,54,96,54)+box(104,40,46,28,GREEN)+pill(80,26,"api",NAVY,44),
    'c09.svg': lambda: book(80,50,BLUE)+text(50,54,"api",15,NAVY)+text(110,54,"10.0.3.1",10,GREEN),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
