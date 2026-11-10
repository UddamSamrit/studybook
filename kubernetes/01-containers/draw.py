# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 1 · Containers and images'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/01-containers/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: terminal(10,22,66,50,[(GREEN,30),("#5A6C93",42)],False)+check(66,24,.9)+server(84,46,64,led=RED)+cross(142,40,.9)+ground(84),
    'c02.svg': lambda: box(18,26,124,56,BLUE)+pill(50,54,"app",WHITE,38,INK,10)+pill(92,54,"libs",WHITE,40,INK,10)+pill(126,54,"env",WHITE,26,INK,9),
    'c03.svg': lambda: doc(30,10,58,80,BLUE)+lock(116,56,1.2),
    'c04.svg': lambda: layers(80,4),
    'c05.svg': lambda: doc(50,8,60,84,BLUE,(0,0,0,0,0,0,0)),
    'c06.svg': lambda: tag(84,50,"v1.4",PURPLE,96),
    'c07.svg': lambda: cloud(104,38,1.3)+box(14,62,44,26,BLUE)+arrow(54,58,86,40),
    'c08.svg': lambda: doc(12,16,42,64,BLUE,(0,1,2,2,1))+arrow(60,48,84,48)+box(92,10,54,20,BLUE)+box(92,38,54,20,BLUE)+box(92,66,54,20,BLUE),
    'c09.svg': lambda: box(16,32,52,36,GREY)+arrow(76,50,94,50)+ghost(102,32,44,36),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
