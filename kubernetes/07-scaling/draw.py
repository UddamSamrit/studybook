# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 7 · Scaling and health checks'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/07-scaling/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: chip(48,50,1.0,NAVY,"CPU")+ram(86,38,62,GREEN),
    'c02.svg': lambda: gauge(80,70,48,.6),
    'c03.svg': lambda: ram(30,20,100,GREEN)+cross(80,74,1.3),
    'c04.svg': lambda: heart(80,44,1.4,RED,True),
    'c05.svg': lambda: light(56,50,"green")+check(112,50,1.3),
    'c06.svg': lambda: light(32,50,"red")+arrow(54,50,92,50,GREY)+cross(74,26,.8)+box(102,38,44,26,GREY),
    'c07.svg': lambda: box(18,70,24,18,ORANGE)+box(50,56,24,18,ORANGE)+box(50,76,24,12,ORANGE)+box(82,42,24,14,ORANGE)+box(82,58,24,14,ORANGE)+box(82,74,24,14,ORANGE)+arrow(20,48,104,12)+chip(136,64,.55),
    'c08.svg': lambda: box(18,42,24,14,ORANGE)+box(18,58,24,14,ORANGE)+box(18,74,24,14,ORANGE)+box(50,56,24,18,ORANGE)+box(50,76,24,12,ORANGE)+box(82,70,24,18,ORANGE)+arrow(28,14,118,52),
    'c09.svg': lambda: rack(24,14,3,76)+f'<circle cx="128" cy="50" r="17" fill="{GREEN}"/><path d="M128 41 V59 M119 50 H137" stroke="{WHITE}" stroke-width="4" stroke-linecap="round"/>',
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
