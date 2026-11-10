# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 5 · ConfigMaps and Secrets'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/05-config/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: box(14,30,80,44,BLUE)+pill(54,52,"pass=123",WHITE,66,INK,10)+cross(124,52,1.4),
    'c02.svg': lambda: panel(30,12,100,76)+slider(46,32,68,.3)+slider(46,50,68,.7,GREEN)+slider(46,68,68,.5,BLUE),
    'c03.svg': lambda: key(70,50,1.5)+lock(128,48,.9),
    'c04.svg': lambda: terminal(16,12,128,76,[(GREEN,64),(YELLOW,84),("#5A6C93",50)],False),
    'c05.svg': lambda: folder(12,30,56,42,YELLOW)+arrow(74,50,96,50)+box(102,34,46,32,BLUE),
    'c06.svg': lambda: box(12,22,54,32,BLUE)+pill(39,72,"staging",ORANGE,64)+box(94,22,54,32,BLUE)+pill(121,72,"prod",RED,64),
    'c07.svg': lambda: pill(80,24,"cGFzcw==",GREY,104,WHITE,13)+arrow(80,38,80,62)+pill(80,78,"pass",RED,64,WHITE,13),
    'c08.svg': lambda: shield(58,50,1.2,GREEN)+key(122,50,.9),
    'c09.svg': lambda: panel(14,20,62,60)+slider(24,40,42,.4)+slider(24,60,42,.8,GREEN)+circ_arrow(118,50,18),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
