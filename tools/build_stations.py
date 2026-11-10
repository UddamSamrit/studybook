# -*- coding: utf-8 -*-
"""Rewrite the homepage station list (index.html, <ol class="line">) from every */unit.json,
oldest first, so counts and numbering always match the units.

    python tools/build_stations.py

Each unit.json may carry "station_en" (one short line for the homepage); otherwise its description
is used. The newest unit gets the NEW tag (shown until opened, see index.html script).
"""
import glob
import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from romanize import romanize  # noqa: E402
import sitecfg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def e(s):
    return html.escape(s or '', quote=True)


def t(s):
    if not re.search('[가-힣]', s or ''):
        return e(s)
    return f'<span class="t-ko">{e(s)}</span><span class="t-ro" lang="ko-Latn">{e(romanize(s))}</span>'


def main():
    units = []
    for p in glob.glob(os.path.join(ROOT, '*', 'unit.json')):
        u = json.load(io.open(p, encoding='utf-8'))
        units.append(u)
    units.sort(key=lambda u: u.get('published', ''))
    stops = []
    for i, u in enumerate(units):
        cards = len(u['cards'])
        qs = sum(len(b['items']) for b in u['qa'] if b.get('kind') != 'surv')
        words = sum(len(g['items']) for g in u['vocab'])
        qlabel = u.get('qa_tab', {}).get('en', 'questions')
        qlabel = 'questions' if qlabel == 'Q&A' else qlabel
        new = '<span class="tag new" hidden>NEW</span>' if i == len(units) - 1 else ''
        stops.append(
            f'    <li class="stop" data-unit="{e(u["slug"])}" data-en="{e(u["title_en"])}">\n'
            f'      <a class="station" href="{e(u["slug"])}/">\n'
            f'        <span class="st-top"><span class="badge">{i + 1:02d}</span>{new}</span>\n'
            f'        <p class="st-ko" lang="{e(sitecfg.lang_of(u)["code"])}"><span class="mk">{t(u["title_ko"])}</span><span class="only-en">{e(u["title_en"])}</span></p>\n'
            f'        <p class="st-en">{t(u.get("station_en") or u.get("description", ""))}</p>\n'
            f'        <p class="st-meta"><span><b>{cards}</b> cards</span><span><b>{qs}</b> {e(qlabel)}</span>'
            f'<span><b>{words}</b> words</span></p>\n'
            f'      </a>\n'
            f'    </li>\n')
    p = os.path.join(ROOT, 'index.html')
    s = io.open(p, encoding='utf-8').read()
    s, n = re.subn(r'(<ol class="line" id="line">\n).*?(    <li class="stop next">)', lambda m: m.group(1) + ''.join(stops) + m.group(2), s, flags=re.S)
    assert n == 1, 'station list not found'
    if units:  # "Start here" points at the first unit until the learner opens one
        first = units[0]
        s = re.sub(r'(<a class="go" id="nowGo" href=")[^"]*', lambda m: m.group(1) + e(first['slug']) + '/', s, count=1)
        s = re.sub(r'<p class="title" id="nowTitle">.*?</p>',
                   lambda m: f'<p class="title" id="nowTitle">{t(first["title_ko"])}<span>{e(first["title_en"])}</span></p>', s, count=1)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print(f'index.html: {len(units)} stations:', ', '.join(u['slug'] for u in units))


if __name__ == '__main__':
    main()
