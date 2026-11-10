# -*- coding: utf-8 -*-
"""Start a brand-new, empty studybook site in a folder (standard library only).

    python <skill>/templates/new_site.py <folder> --lang ja --title "My Japanese Studybook" [--support Khmer]

Copies the builders (tools/), the shared styles and script (assets/), the app files (manifest,
service worker, offline page, icons) and the homepage, then writes site.json with the title and
study language. The web address is filled in later from the git remote (see tools/sitecfg.py), so
the site never points at anybody else's. Existing files are never overwritten.
"""
import argparse
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sitecfg import LANGS  # noqa: E402

TOOLS = ['sitecfg.py', 'render_unit.py', 'gen_audio.py', 'build_stations.py', 'build_feed.py', 'build_images.py',
         'romanize.py', 'draw_flat_objects.example.py']


def put(path, text):
    if os.path.exists(path):
        print('  kept   ', os.path.relpath(path))
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print('  wrote  ', os.path.relpath(path))


def copy(src, dst):
    if os.path.isdir(src):
        for name in os.listdir(src):
            copy(os.path.join(src, name), os.path.join(dst, name))
        return
    if os.path.exists(dst):
        print('  kept   ', os.path.relpath(dst))
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    print('  copied ', os.path.relpath(dst))


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def hub(title, short, desc, code, support):
    s = io.open(os.path.join(HERE, 'hub_index.html'), encoding='utf-8').read()
    ko = code == 'ko'
    name = LANGS.get(code, {}).get('name', code)
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + esc(desc).replace('\\', r'\\'), s, count=1)
    s = re.sub(r'(<meta name="apple-mobile-web-app-title" content=")[^"]*', r'\g<1>' + esc(short).replace('\\', r'\\'), s, count=1)
    s = re.sub(r'<h1>.*?</h1>', f'<h1>{esc(title)}</h1>', s, count=1)
    # no sample units: the station list starts empty and build_stations.py fills it
    s = re.sub(r'(<ol class="line" id="line">\n).*?(    <li class="stop next">)', r'\1\2', s, count=1, flags=re.S)
    s = re.sub(r'<p class="title" id="nowTitle">.*?</p>', '<p class="title" id="nowTitle">Your first unit<span>is on its way</span></p>', s, count=1)
    s = re.sub(r'(<a class="go" id="nowGo" href=")[^"]*', r'\1./', s, count=1)
    s = s.replace('The next unit is built with <code>/teach-me</code>.', 'Ask your AI for the next unit.')
    if not ko:
        s = s.replace('<html lang="ko">', f'<html lang="{code}" data-ui="en">', 1)
        s = s.replace('앱 설치', 'Install app').replace('계속하기 · Continue', 'Continue').replace('노선도 · All stations', 'All stations')
        s = s.replace('다음 역', 'Next stop').replace(' lang="ko"', f' lang="{code}"')
        s = re.sub(r'<div class="script" role="group" aria-label="Show text in">.*?</div>',
                   '<div class="script" role="group" aria-label="Show text in">'
                   f'<button type="button" data-set="en" aria-pressed="false">{esc(support)}</button>'
                   f'<button type="button" data-set="ko" aria-pressed="true" lang="{code}">{esc(name)}</button></div>', s, count=1)
    return s


def main():
    ap = argparse.ArgumentParser(description='Start an empty studybook site.')
    ap.add_argument('folder')
    ap.add_argument('--lang', default='ko', help='study language code: ' + ', '.join(LANGS))
    ap.add_argument('--title', default='')
    ap.add_argument('--support', default='English', help='the language translations are written in, e.g. English, Khmer')
    a = ap.parse_args()
    if a.lang not in LANGS:
        print(f'note: {a.lang} has no preset voice; set "voice" in site.json (an edge-tts voice name, see: edge-tts --list-voices)')
    info = LANGS.get(a.lang, {'name': a.lang, 'en': a.lang})
    title = a.title or f'My {info["en"]} Studybook'
    short = 'Studybook'
    desc = f'{info["en"]} study units: picture cards with native audio, Q&A, vocabulary and full text.'
    root = os.path.abspath(a.folder)
    os.makedirs(root, exist_ok=True)
    print(f'New studybook in {root}')
    for f in TOOLS:
        copy(os.path.join(HERE, f), os.path.join(root, 'tools', f))
    copy(os.path.join(HERE, 'assets'), os.path.join(root, 'assets'))
    copy(os.path.join(HERE, 'pwa'), root)
    copy(os.path.join(HERE, 'DESIGN.example.md'), os.path.join(root, 'DESIGN.md'))
    put(os.path.join(root, 'index.html'), hub(title, short, desc, a.lang, a.support))
    put(os.path.join(root, '.nojekyll'), '')
    put(os.path.join(root, '.gitignore'), '__pycache__/\n*.pyc\n.DS_Store\n')
    site = {'title': title, 'short': short, 'description': desc, 'lang': a.lang, 'support': a.support, 'url': ''}
    if a.lang not in LANGS:
        site['voice'] = ''
    put(os.path.join(root, 'site.json'), json.dumps(site, ensure_ascii=False, indent=1) + '\n')
    m = os.path.join(root, 'manifest.webmanifest')
    if os.path.exists(m):
        mf = json.load(io.open(m, encoding='utf-8'))
        if 'Rex' in mf.get('description', '') or mf.get('name', '').startswith('다라봇'):
            mf.update(name=title, short_name=short, description=desc, lang=a.lang, id='./')
            io.open(m, 'w', encoding='utf-8', newline='\n').write(json.dumps(mf, ensure_ascii=False, indent=2) + '\n')
    print('Done. Next: write <unit-slug>/unit.json, then build it (see references/02).')


if __name__ == '__main__':
    main()
