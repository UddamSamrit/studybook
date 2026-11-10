# -*- coding: utf-8 -*-
"""Build every PNG icon and the link-share covers with headless Chromium.

    python tools/build_images.py            # or: set CHROME=path\\to\\chrome.exe first

Icons come from icons/icon.svg and icons/icon-maskable.svg. Apple icons use the full-bleed drawing
because iOS rounds the corners itself and paints transparency black. Maskable icons keep the drawing
inside Android's safe circle. Covers (og/<slug>.png, 1200x630) are what Facebook, Instagram DMs,
KakaoTalk and others show when a link is shared.
"""
import glob
import html
import io
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecfg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = sitecfg.load()
ANY = [48, 72, 96, 128, 144, 152, 192, 256, 384, 512, 1024]
MASK = [48, 72, 96, 128, 192, 384, 512]
APPLE = {120: 'apple-touch-icon-120.png', 152: 'apple-touch-icon-152.png', 167: 'apple-touch-icon-167.png',
         180: 'apple-touch-icon.png', 1024: 'apple-touch-icon-1024.png'}
FAV = {16: 'favicon-16.png', 32: 'favicon-32.png'}


def chrome():
    env = os.environ.get('CHROME')
    if env:
        return env
    pats = [os.path.expandvars(r'%LOCALAPPDATA%\ms-playwright\chromium_headless_shell-*\*\*.exe'),
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            os.path.expanduser('~/.cache/ms-playwright/chromium_headless_shell-*/*/*'),
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    for p in pats:
        hits = [h for h in sorted(glob.glob(p)) if 'headless' in os.path.basename(h) or 'chrome' in os.path.basename(h).lower()]
        if hits:
            return hits[-1]
    sys.exit('No Chromium found. Set CHROME to a Chrome or Chromium executable.')


def shot(exe, page, out, w, h, transparent=False, wait=0):
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(page)
    args = [exe, '--headless', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
            f'--window-size={w},{h}', f'--screenshot={out}', 'file:///' + f.name.replace(os.sep, '/')]
    if transparent:
        args.insert(1, '--default-background-color=00000000')
    if wait:
        args.insert(1, f'--virtual-time-budget={wait}')
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    os.unlink(f.name)


def icon_page(svg, n):
    svg = svg.replace('<svg ', f'<svg width="{n}" height="{n}" style="display:block" ', 1)
    return f'<!doctype html><html><body style="margin:0;background:transparent">{svg}</body></html>'


COVER = '''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@500;800&display=swap">
<style>
*{{box-sizing:border-box}}
body{{margin:0;width:1200px;height:630px;background:#1C2A4A;color:#fff;overflow:hidden;position:relative;
  font-family:'Gothic A1','Malgun Gothic',sans-serif}}
.line{{position:absolute;left:96px;top:0;bottom:0;width:16px;background:#00A84D}}
.dot{{position:absolute;left:68px;width:72px;height:72px;border-radius:50%;background:#fff;border:16px solid #00A84D}}
.here{{border-color:#F5B700}}
.body{{position:absolute;left:190px;top:0;right:{right}px;bottom:0;display:flex;flex-direction:column;justify-content:center}}
.brand{{font-size:30px;font-weight:500;color:#C4CCDD;margin:0 0 26px}}
h1{{margin:0;font-size:{size}px;font-weight:800;line-height:1.16;letter-spacing:-.015em;word-break:keep-all;overflow-wrap:anywhere;line-break:anywhere;text-wrap:balance}}
.en{{margin:22px 0 0;font-size:36px;font-weight:500;color:#fff;line-height:1.25}}
.meta{{margin:30px 0 0;font-size:27px;font-weight:500;color:#C4CCDD}}
.pic{{position:absolute;right:70px;top:135px;width:360px;height:360px;border-radius:50%;background:#F4F6F9;display:flex;
  align-items:center;justify-content:center;overflow:hidden}}
.pic img{{width:84%;height:84%;object-fit:contain}}
</style></head><body>
<div class="line"></div><div class="dot" style="top:150px"></div><div class="dot here" style="top:408px"></div>
<div class="body">{brand}<h1>{title}</h1><p class="en">{en}</p><p class="meta">{meta}</p></div>
{pic}
</body></html>'''


def cover_page(title, en, meta, img=None):
    pic = f'<div class="pic"><img src="file:///{img.replace(os.sep, "/")}" alt=""></div>' if img else ''
    size = 84 if len(title) <= 9 else 70
    brand = f'<p class="brand">{html.escape(CFG["title"])}</p>' if img else ''
    return COVER.format(title=html.escape(title), en=html.escape(en), meta=html.escape(meta), pic=pic, brand=brand,
                        right=470 if img else 90, size=size)


def main():
    exe = chrome()
    ic = os.path.join(ROOT, 'icons')
    plain = io.open(os.path.join(ic, 'icon.svg'), encoding='utf-8').read()
    full = io.open(os.path.join(ic, 'icon-maskable.svg'), encoding='utf-8').read()
    for n in ANY:
        shot(exe, icon_page(plain, n), os.path.join(ic, f'icon-{n}.png'), n, n, transparent=True)
    for n in MASK:
        shot(exe, icon_page(full, n), os.path.join(ic, f'icon-maskable-{n}.png'), n, n)
    for n, name in APPLE.items():
        shot(exe, icon_page(full, n), os.path.join(ic, name), n, n)
    for n, name in FAV.items():
        shot(exe, icon_page(plain, n), os.path.join(ic, name), n, n, transparent=True)

    og = os.path.join(ROOT, 'og')
    os.makedirs(og, exist_ok=True)
    units = [json.load(io.open(p, encoding='utf-8')) for p in glob.glob(os.path.join(ROOT, '*', 'unit.json'))]
    for u in units:
        cards = u['cards']
        words = sum(len(g['items']) for g in u['vocab'])
        # the unit's first big-picture tile says what it is about; the first card is often just an intro
        tiles = (u.get('explain') or {}).get('tiles') or []
        src = tiles[0]['img'] if tiles else cards[0]['img']
        img = os.path.join(ROOT, u['slug'], src.replace('/', os.sep))
        meta = f'{len(cards)} cards · {words} words'
        shot(exe, cover_page(u['title_ko'], u['title_en'], meta, img), os.path.join(og, u['slug'] + '.png'), 1200, 630, wait=5000)
    shot(exe, cover_page(CFG['title'], 'See it, hear it, say it',
                         f'{len(units)} units'), os.path.join(og, 'home.png'), 1200, 630, wait=5000)
    print(f'{len(ANY) + len(MASK) + len(APPLE) + len(FAV)} icons, {len(units) + 1} covers')


if __name__ == '__main__':
    main()
