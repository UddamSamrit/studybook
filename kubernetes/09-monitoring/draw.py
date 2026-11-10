# -*- coding: utf-8 -*-
"""Flat 2D object drawings for 'K8s 9 · Monitoring and debugging'. Hand-authored SVG from tools/flat_icons.py, no image model.
Run: python kubernetes/09-monitoring/draw.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
from flat_icons import *  # noqa: E402,F401,F403

OUT = os.path.join(HERE, 'img')
PICS = {
    'c01.svg': lambda: chart(24,14,112,72,BLUE),
    'c02.svg': lambda: box(10,14,30,18,GREEN)+box(10,41,30,18,GREEN)+box(10,68,30,18,GREEN)+arrow(44,23,94,44,GREY,3)+arrow(44,50,94,50,GREY,3)+arrow(44,77,94,56,GREY,3)+cyl(124,28,42,44,ORANGE),
    'c03.svg': lambda: f'<rect x="16" y="10" width="128" height="80" rx="8" fill="{NAVY}"/>'+chart(24,18,56,32,GREEN,(.6,.4,.5,.2),False)+chart(84,18,52,32,ORANGE,(.3,.5,.4,.7),False)+chart(24,56,112,28,BLUE,(.5,.6,.3,.4,.2)),
    'c04.svg': lambda: bell(80,44,1.3),
    'c05.svg': lambda: doc(12,6,30,28,GREY,(0,))+doc(12,37,30,28,GREY,(0,))+doc(12,68,30,28,GREY,(0,))+arrow(46,20,86,40,GREY,3)+arrow(46,51,86,51,GREY,3)+arrow(46,82,86,62,GREY,3)+doc(94,14,54,74,BROWN),
    'c06.svg': lambda: box(8,40,30,20,BLUE)+box(65,12,30,20,GREEN)+box(65,68,30,20,PURPLE)+box(122,40,30,20,ORANGE)+f'<path d="M38 50 L65 22 M95 22 L122 50 M38 50 L65 78" stroke="{RED}" stroke-width="3" stroke-dasharray="5 4" fill="none"/>',
    'c07.svg': lambda: panel(20,10,120,80)+"".join(f'<circle cx="38" cy="{28+i*18}" r="5" fill="{[GREEN,GREEN,YELLOW,RED][i]}"/><rect x="50" y="{26+i*18}" width="{[70,56,64,50][i]}" height="4" rx="2" fill="{INK if i==3 else LINE}"/>' for i in range(4)),
    'c08.svg': lambda: terminal(14,10,104,80,[("#5A6C93",60),("#5A6C93",44),(RED,70),("#5A6C93",36)],False)+circ_arrow(134,30,11,ORANGE,True),
    'c09.svg': lambda: doc(36,8,62,84,BROWN,(0,2,2,0,2,2,2))+f'<g transform="translate(118 56) rotate(35)"><rect x="-5" y="-34" width="10" height="52" rx="2" fill="{YELLOW}"/><path d="M-5 18 L0 28 L5 18Z" fill="{INK}"/></g>',
}

for name, draw in PICS.items():
    save(OUT, name, draw())
print('drawn:', len(PICS))
