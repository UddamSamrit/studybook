# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 11 · CI/CD and GitOps'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes-11-production/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: branch(24,66)+pill(80,22,"push",NAVY,64,WHITE,12),
    'c02.svg': lambda: check(34,50,1.3)+arrow(58,50,86,50)+box(94,34,54,32,BLUE),
    'c03.svg': lambda: box(6,38,36,24,BLUE)+arrow(46,50,62,50)+pill(92,50,"staging",ORANGE,56,WHITE,10)+text(140,54,"prod",11,GREY),
    'c04.svg': lambda: text(80,40,"Git",30,ORANGE)+branch(24,74),
    'c05.svg': lambda: pill(34,50,"Git",ORANGE,52,WHITE,13)+arrow(64,42,96,42,GREEN,4)+arrow(96,58,64,58,GREEN,4)+rack(104,18,3,46),
    'c06.svg': lambda: branch(24,66,PURPLE)+check(126,26,.9),
    'c07.svg': lambda: bird(58,50,1.0)+arrow(96,50,114,50,GREY,3)+box(118,40,34,20,GREEN),
    'c08.svg': lambda: chart(12,14,82,72,RED,(.2,.3,.25,.6,.85),False)+circ_arrow(126,48,18,BROWN,True),
    'c09.svg': lambda: trophy(80,48,1.3),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
