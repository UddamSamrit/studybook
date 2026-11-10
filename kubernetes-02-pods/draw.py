# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 2 · Pods and kubectl'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes-02-pods/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: gear(62,52,28,BLUE)+gear(112,36,18,PURPLE),
    'c02.svg': lambda: rack(24,14,3,76)+box(112,16,34,16,GREEN)+box(112,41,34,16,GREEN)+box(112,66,34,16,GREEN),
    'c03.svg': lambda: box(64,6,32,20,GREEN)+arrow(80,30,42,58)+arrow(80,30,118,58)+server(10,66,62)+server(88,66,62),
    'c04.svg': lambda: terminal(12,18,74,62)+arrow(92,48,112,48)+gear(134,48,16,BLUE),
    'c05.svg': lambda: "".join(box(18,14+i*26,40,18,GREEN)+pill(108,23+i*26,"Running",GREEN,76) for i in range(3)),
    'c06.svg': lambda: doc(12,12,52,76,PURPLE)+arrow(70,50,98,50)+rack(104,16,3,44),
    'c07.svg': lambda: pill(80,22,"Pending",YELLOW,88,INK,12)+arrow(80,36,80,62)+pill(80,78,"Running",GREEN,88,WHITE,12),
    'c08.svg': lambda: box(14,30,60,40,GREY)+magnifier(104,44,20),
    'c09.svg': lambda: terminal(14,10,104,80,[("#5A6C93",60),("#5A6C93",44),(RED,70),("#5A6C93",36)],False)+magnifier(120,60,16),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
