# -*- coding: utf-8 -*-
"""Build feed.xml (RSS 2.0) from every <unit>/unit.json, newest first, with each unit's full text in
content:encoded so an AI or feed reader can read the material without running the page.

    python tools/build_feed.py
"""
import glob
import html
import io
import json
import os
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecfg  # noqa: E402

CFG = sitecfg.load()
SITE = CFG['url']


def esc(s):
    return html.escape(s or '', quote=False)


def content(u):
    c = [f'<h2>{esc(u["title_ko"])} ({esc(u["title_en"])})</h2>', f'<p>{esc(u.get("description"))}</p>']
    ex = u.get('explain')
    if ex:
        c.append(f'<h3>{esc(ex.get("title"))}</h3><p>{esc(ex.get("why"))}</p><ul>'
                 + ''.join(f'<li>{esc(t["ko"])}: {esc(t["en"])}</li>' for t in ex['tiles']) + '</ul>')
    c.append(f'<h3>{esc(u.get("full_title", "Text"))}</h3>')
    for s in u['full']:
        c.append(f'<p><strong>{esc(s["title"])}</strong><br>{esc(s["ko"])}<br><em>{esc(s["en"])}</em></p>')
    c.append('<h3>Q&amp;A</h3>')
    for b in u['qa']:
        c.append(f'<p><strong>{esc(b["title"])}</strong></p>')
        for it in b['items']:
            if b.get('kind') == 'surv':
                c.append(f'<p>{esc(it["ko"])} ({esc(it.get("en"))})</p>')
            else:
                qen = f' ({esc(it["qen"])})' if it.get('qen') else ''
                aen = f' ({esc(it["aen"])})' if it.get('aen') else ''
                c.append(f'<p>Q. {esc(it["q"])}{qen}<br>A. {esc(it["a"])}{aen}</p>')
    n = sum(len(g['items']) for g in u['vocab'])
    c.append(f'<h3>Vocabulary ({n})</h3>')
    for g in u['vocab']:
        c.append(f'<p><strong>{esc(g["title"])}</strong><br>' + '<br>'.join(f'{esc(i["ko"])}: {esc(i["en"])}' for i in g['items']) + '</p>')
    return ''.join(c)


units = [json.load(io.open(p, encoding='utf-8')) for p in glob.glob(os.path.join(ROOT, '*', 'unit.json'))]
units.sort(key=lambda u: u.get('published', ''), reverse=True)
date = lambda u: format_datetime(datetime.strptime(u.get('published', '2026-01-01'), '%Y-%m-%d').replace(hour=12, tzinfo=timezone.utc))
items = []
for u in units:
    link = SITE + u['slug'] + '/'
    nq = sum(len(b['items']) for b in u['qa'] if b.get('kind') != 'surv')
    nv = sum(len(g['items']) for g in u['vocab'])
    desc = f'{u.get("description", "")} {len(u["cards"])} picture cards, {nq} questions, {nv} words.'
    items.append(f'<item>\n<title>{esc(u["title_ko"])} ({esc(u["title_en"])})</title>\n<link>{link}</link>\n'
                 f'<guid isPermaLink="true">{link}</guid>\n<pubDate>{date(u)}</pubDate>\n<description>{esc(desc)}</description>\n'
                 f'<content:encoded><![CDATA[{content(u)}]]></content:encoded>\n</item>')
feed = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
        f'<title>{esc(CFG["title"])}</title>\n'
        f'<link>{SITE}</link>\n<atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>\n'
        f'<description>{esc(CFG["description"])} Each item is a study unit with its full text (lines, Q&amp;A, vocabulary) so it can be read directly.</description>\n'
        f'<language>{esc(CFG["lang"])}</language>\n<lastBuildDate>{date(units[0])}</lastBuildDate>\n' + '\n'.join(items) + '\n</channel>\n</rss>\n')
io.open(os.path.join(ROOT, 'feed.xml'), 'w', encoding='utf-8', newline='\n').write(feed)
print(f'feed.xml: {len(units)} units')
