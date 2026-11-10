# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 6 · Volumes and StatefulSets'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes-06-storage/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: box(10,32,50,36,BLUE)+circ_arrow(86,50,14)+doc(108,22,44,54,GREY,(0,0,0,0))+cross(142,24,.7),
    'c02.svg': lambda: box(12,32,58,36,BLUE)+f'<path d="M72 50 H98" stroke="{GREY}" stroke-width="4" stroke-dasharray="4 3"/>'+cyl(122,28,42,44,GREEN),
    'c03.svg': lambda: cyl(80,20,64,58,GREEN,"50 GB"),
    'c04.svg': lambda: panel(16,26,82,48)+text(57,56,"10 GB?",15,PURPLE)+arrow(104,50,120,50)+cyl(138,32,28,36,GREEN),
    'c05.svg': lambda: gear(46,50,24,GREY)+arrow(78,50,102,50)+cyl(126,30,36,40,GREEN),
    'c06.svg': lambda: cyl(54,22,56,56,BLUE)+tag(118,50,"name",ORANGE,64),
    'c07.svg': lambda: cyl(42,24,48,50,BLUE,"db-0")+cyl(118,24,48,50,BLUE,"db-1"),
    'c08.svg': lambda: box(18,16,40,24,PURPLE)+f'<path d="M38 40 V56" stroke="{GREY}" stroke-width="3"/>'+cyl(38,58,32,22,GREEN)+arrow(70,48,94,48)+box(104,16,40,24,PURPLE)+f'<path d="M124 40 V56" stroke="{GREY}" stroke-width="3"/>'+cyl(124,58,32,22,GREEN),
    'c09.svg': lambda: cyl(46,24,46,50,GREEN)+arrow(78,50,102,50)+cyl(126,24,40,50,GREY,"copy"),
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
