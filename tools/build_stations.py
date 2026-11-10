# -*- coding: utf-8 -*-
"""Rebuild every homepage from the books and units on disk.

    python tools/build_stations.py

The site is a shelf of books. A book is a folder with a book.json (title, title_km, description,
order). Inside a book, a sub-folder with a book.json is a section (a book inside the book) and a
sub-folder with a unit.json is a unit, and one with a page.json is a plain page (like the to-do list,
made by build_todo.py). Books can nest as deep as needed:

    index.html                              the top-level books
    english/index.html                      English: Reading, Listening, Speaking, Writing
    english/speaking/index.html             the Speaking units
    english/speaking/<unit>/index.html      a unit page (render_unit.py)

Units that sit directly under the site root (no book) are listed on the root page too.
A book.json with "draft": true is left out (with everything inside it) until you remove the flag.
Each unit.json may carry "station_en" (one short line for the list); otherwise its description
is used. The newest unit of a book gets the NEW tag (shown until opened). Every page is made from
tools/hub_template.html, so all homepages share one design.
"""
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
TEMPLATE = os.path.join(ROOT, 'tools', 'hub_template.html')
CFG = sitecfg.load()


def e(s):
    return html.escape(s or '', quote=True)


def t(s):
    if not re.search('[가-힣]', s or ''):
        return e(s)
    return f'<span class="t-ko">{e(s)}</span><span class="t-ro" lang="ko-Latn">{e(romanize(s))}</span>'


def jload(p):
    return json.load(io.open(p, encoding='utf-8'))


def scan(rel):
    """The book at folder `rel` ('' = site root): its sections (books) and units, in order."""
    here = os.path.join(ROOT, rel)
    book = jload(os.path.join(here, 'book.json')) if rel else {'title': CFG.get('title', 'Studybook')}
    book['id'], book['books'], book['units'] = rel, [], []
    for name in sorted(os.listdir(here)):
        sub = os.path.join(rel, name) if rel else name
        if os.path.isfile(os.path.join(ROOT, sub, 'book.json')):
            if not jload(os.path.join(ROOT, sub, 'book.json')).get('draft'):  # "draft": true keeps a book off the site
                book['books'].append(scan(sub))
        elif os.path.isfile(os.path.join(ROOT, sub, 'page.json')):  # a plain page, e.g. a to-do list (build_todo.py)
            pg = jload(os.path.join(ROOT, sub, 'page.json'))
            pg.update(id=sub, books=[], units=[], page=True)
            book['books'].append(pg)
        elif os.path.isfile(os.path.join(ROOT, sub, 'unit.json')):
            book['units'].append(jload(os.path.join(ROOT, sub, 'unit.json')))
    book['books'].sort(key=lambda b: (b.get('order', 0), b['id']))
    book['units'].sort(key=lambda u: (u.get('published', ''), u.get('order', 0), u.get('slug', '')))
    return book


def counts(u):
    qs = sum(len(b['items']) for b in u['qa'] if b.get('kind') != 'surv')
    return len(u['cards']), qs, sum(len(g['items']) for g in u['vocab'])


def all_units(b):
    return b['units'] + [u for s in b['books'] for u in all_units(s)]


def stop(i, key, href, title, sub, line, meta, lang, new=False):
    tag = '<span class="tag new" hidden>NEW</span>' if new else ''
    return (f'    <li class="stop" data-unit="{e(key)}" data-en="{e(sub)}">\n'
            f'      <a class="station" href="{e(href)}">\n'
            f'        <span class="st-top"><span class="badge">{i + 1:02d}</span>{tag}</span>\n'
            f'        <p class="st-ko" lang="{e(lang)}"><span class="mk">{t(title)}</span><span class="only-en">{e(sub)}</span></p>\n'
            f'        <p class="st-en">{t(line)}</p>\n'
            f'        <p class="st-meta">{meta}</p>\n'
            f'      </a>\n'
            f'    </li>\n')


def book_stop(i, b, href):
    if b.get('page'):
        return stop(i, b['id'], href, b['title'], b.get('title_km', ''), b.get('description', ''), f'<span>{e(b.get("meta", ""))}</span>', CFG.get('lang', 'en'))
    us = all_units(b)
    if not us:
        meta = '<span>Coming soon</span>'
    else:
        meta = (f'<span><b>{len(us)}</b> unit{"s" if len(us) != 1 else ""}</span>'
                f'<span><b>{sum(counts(u)[0] for u in us)}</b> cards</span><span><b>{sum(counts(u)[2] for u in us)}</b> words</span>')
    if b['books']:
        meta = f'<span><b>{len(b["books"])}</b> sections</span>' + meta
    return stop(i, b['id'], href, b['title'], b.get('title_km', ''), b.get('description', ''), meta, CFG.get('lang', 'en'))


def unit_stop(i, u, href, new):
    cards, qs, words = counts(u)
    qlabel = u.get('qa_tab', {}).get('en', 'questions')
    qlabel = 'questions' if qlabel in ('Q&A', 'Interview') else qlabel
    meta = f'<span><b>{cards}</b> cards</span><span><b>{qs}</b> {e(qlabel)}</span><span><b>{words}</b> words</span>'
    return stop(i, u['slug'], href, u['title_ko'], u['title_en'], u.get('station_en') or u.get('description', ''),
                meta, sitecfg.lang_of(u)['code'], new)


def page(b, parent_title):
    rel = b['id']
    depth = rel.count('/') + 1 if rel else 0
    up = '../' * depth
    child = lambda key: key[len(rel) + 1:] if rel else key  # a key relative to this page
    stops = [book_stop(i, s, child(s['id']) + '/') for i, s in enumerate(b['books'])]
    n0 = len(stops)
    stops += [unit_stop(n0 + i, u, child(u['slug']) + '/', bool(rel) and i == len(b['units']) - 1) for i, u in enumerate(b['units'])]
    first = (b['books'][0]['id'], b['books'][0]['title'], b['books'][0].get('title_km', '')) if b['books'] else \
        (b['units'][0]['slug'], b['units'][0]['title_ko'], b['units'][0]['title_en']) if b['units'] else None

    s = io.open(TEMPLATE, encoding='utf-8').read()
    if depth:  # this page sits inside a book folder: point its own links back at the site root
        s = re.sub(r'((?:href|src)=")(?!https?:|#|mailto:|data:|/|\.\./)', lambda m: m.group(1) + up, s)
        s = s.replace('<h1>', f'<a class="books-back" href="../">&larr; {e(parent_title)}</a>\n      <h1>', 1)
        s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{e(b["title"])} · {e(CFG.get("title", ""))}</title>', s, count=1)
        s = re.sub(r'<h1>.*?</h1>', lambda m: f'<h1>{e(b["title"])}</h1>', s, count=1)
    head = ('All books', 'Tap a book to see what is inside') if not depth else \
        (f'{b["title"]} · {len(b["books"])} sections', 'Tap a section') if b['books'] and not b['units'] else \
        (f'{b["title"]} · {len(b["units"])} units', 'Tap a station to study')
    s = re.sub(r'<div class="line-h"><h2>.*?</h2><span>.*?</span></div>',
               lambda m: f'<div class="line-h"><h2>{e(head[0])}</h2><span>{e(head[1])}</span></div>', s, count=1)
    s = s.replace('</style>', '.books-back{display:inline-block;margin:0 0 .35rem;font-size:.9rem;font-weight:700;color:inherit;opacity:.85;text-decoration:none}\n</style>', 1)
    s = s.replace('<body>', f'<body data-path="{e(rel)}">', 1)
    s, n = re.subn(r'(<ol class="line" id="line">\n).*?(    <li class="stop next">)', lambda m: m.group(1) + ''.join(stops) + m.group(2), s, flags=re.S)
    assert n == 1, 'station list not found in hub_template.html'
    if not b['units'] and not b['books']:
        s = re.sub(r'(<p class="st-en">)Ask your AI for the next unit\.(</p>)', r'\1Coming soon: ask your AI for the first unit.\2', s)
    if first:  # "Start here" points at the first station until the learner opens a unit
        s = re.sub(r'(<a class="go" id="nowGo" href=")[^"]*', lambda m: m.group(1) + e(child(first[0]) + '/'), s, count=1)
        s = re.sub(r'<p class="title" id="nowTitle">.*?</p>',
                   lambda m: f'<p class="title" id="nowTitle">{t(first[1])}<span>{e(first[2])}</span></p>', s, count=1)
    # "You are here" works at every level: a unit inside a book lights up that book, and Continue opens the unit
    s = s.replace("if(s.dataset.unit===last)here=s;", "if(s.dataset.unit===last||(last&&last.indexOf(s.dataset.unit+'/')===0))here=s;")
    s = s.replace("var pos=get('sb:pos:'+here.dataset.unit,null);", "var pos=get('sb:pos:'+last,null);")
    s = s.replace("document.getElementById('nowGo').href=here.querySelector('a.station').getAttribute('href');",
                  "var P=document.body.dataset.path||'';document.getElementById('nowGo').href=(P?last.slice(P.length+1):last)+'/';")
    io.open(os.path.join(ROOT, rel, 'index.html'), 'w', encoding='utf-8', newline='\n').write(s)
    print(f'{(rel + "/") if rel else ""}index.html: {len(b["books"])} sections, {len(b["units"])} units')
    for sb in b['books']:
        if sb.get('page'):
            continue
        page(sb, b['title'] if depth else 'All books')


def main():
    page(scan(''), '')


if __name__ == '__main__':
    main()
