# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 8 · Helm and namespaces'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes-08-helm/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: folder(34,18,92,66,YELLOW)+box(50,50,28,20,BLUE)+box(84,50,28,20,GREEN),
    'c02.svg': lambda: folder(6,28,46,38,GREEN,"dev")+folder(57,28,46,38,ORANGE,"stg")+folder(108,28,46,38,RED,"prod"),
    'c03.svg': lambda: folder(10,10,36,28,YELLOW)+gauge(92,74,46,.75,ORANGE),
    'c04.svg': lambda: doc(18,12,46,66,GREY)+doc(54,16,46,66,GREY)+doc(90,20,46,66,PURPLE),
    'c05.svg': lambda: package(80,46,1.4),
    'c06.svg': lambda: package(48,52,1.1)+doc(94,12,50,76,ORANGE,(0,1,1,2,1,1)),
    'c07.svg': lambda: panel(30,10,100,80)+text(80,30,"values.yaml",11,PURPLE)+slider(46,50,68,.6)+slider(46,70,68,.3,GREEN),
    'c08.svg': lambda: package(56,52,1.0)+arrow(112,80,112,18,GREEN,6),
    'c09.svg': lambda: package(50,52,1.0)+circ_arrow(118,48,18,BROWN,True),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
