# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 3 · Deployments and rollouts'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/03-deployments/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: doc(12,12,50,76,PURPLE)+"".join(box(74+i*26,34,22,18,PURPLE) for i in range(3))+pill(112,70,"x 3",NAVY,50),
    'c02.svg': lambda: box(12,40,36,24,PURPLE)+box(56,40,36,24,PURPLE)+ghost(100,40,36,24)+circ_arrow(118,22,10)+ground(72),
    'c03.svg': lambda: box(10,36,46,30,PURPLE)+tag(106,51,"app=web",ORANGE,92),
    'c04.svg': lambda: tag(42,50,"v1",GREY,56)+arrow(76,50,100,50)+tag(126,50,"v2",PURPLE,56),
    'c05.svg': lambda: "".join(box(12+i*36,28,30,24,PURPLE if i<2 else GREY) for i in range(4))+arrow(20,72,140,72,ORANGE),
    'c06.svg': lambda: globe(70,50,32,BLUE)+check(112,26,1.1),
    'c07.svg': lambda: f'<rect x="20" y="34" width="120" height="18" rx="9" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/><rect x="20" y="34" width="84" height="18" rx="9" fill="{PURPLE}"/>'+text(80,80,"70%",18,NAVY),
    'c08.svg': lambda: circ_arrow(80,46,26,BROWN,True)+pill(80,88,"v1",NAVY,44),
    'c09.svg': lambda: "".join(f'<rect x="{28+i*18}" y="{12+i*12}" width="72" height="50" rx="6" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'+text(64+i*18,44+i*12,f"v{i+1}",16,PURPLE) for i in range(3)),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
