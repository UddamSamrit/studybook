# -*- coding: utf-8 -*-
"""Build a to-do page from <folder>/todo.json (the same file the Telegram bot reads).

    python tools/build_todo.py english/todo

Writes <folder>/index.html (tick boxes, saved in this browser) and <folder>/page.json (so the book
page lists it). "Every day" tasks reset each day; the other groups reset each Monday, like the bot.
"""
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def e(s):
    return html.escape(s or '', quote=True)


def main():
    rel = sys.argv[1].strip('/')
    d = os.path.join(ROOT, rel)
    todo = json.load(io.open(os.path.join(d, 'todo.json'), encoding='utf-8'))
    up = '../' * (rel.count('/') + 1)
    byid = {it['id']: it for g in todo['groups'] for it in g.get('items', []) if 'id' in it}
    total = len(byid) - sum(1 for g in todo['groups'] if g.get('weekly') for it in g.get('items', []) if 'id' in it)
    groups = []
    for g in todo['groups']:
        kind = g.get('kind', 'checklist')
        num = f'{g["num"]}. ' if g.get('num') else ''
        head = f'    <h2>{num}{e(g["title"])} <span class="km" lang="km">{e(g.get("km", ""))}</span><span class="cnt"></span></h2>\n'
        body = ''
        if kind in ('priorities', 'checklist', 'schedule'):
            rows = []
            secs = g.get('sections') or [{'id': None}]
            for sec in secs:
                if sec['id']:
                    rows.append(f'      <li class="sec">{e(sec["title"])} ({e(sec["range"])})</li>\n')
                for it in g['items']:
                    if sec['id'] and it.get('section') != sec['id']:
                        continue
                    ref = 'ref' in it
                    t = byid.get(it['ref']) if ref else it
                    if not t:
                        continue
                    code = t.get('code') or t['id'].upper()
                    tm = f'<b class="tm">{e(it["time"])}</b> ' if it.get('time') else ''
                    link = ''
                    if t.get('link'):
                        ext = t['link'].startswith('http')
                        link = f' <a class="go" href="{e(t["link"])}"{" target=_blank rel=noopener" if ext else ""}>open</a>'
                    pr = ' data-prio="1"' if kind == 'priorities' else ''
                    rows.append(f'      <li><label><input type="checkbox" data-id="{e(t["id"])}"{" data-ref=1" if ref else ""}><span class="box" aria-hidden="true"></span>'
                                f'<span class="txt"><span class="en">{tm}<b class="code">{e(code)}</b> {e(t.get("short") or t["en"])}</span>'
                                f'<span class="km" lang="km">{e(t["km"])}</span></span></label>{link}</li>\n')
                    if kind == 'priorities':
                        rows.append(f'      <li class="note"><input type="text" data-note="{e(t["id"])}" placeholder="Write your {e(t["short"].lower())}"></li>\n')
            body = '    <div class="bar"><span></span></div>\n    <ul>\n' + ''.join(rows) + '    </ul>\n'
            if g.get('fields'):
                body += '    <ul class="notes">\n' + ''.join(
                    f'      <li><span>{e(f["label"])}</span><input type="text" data-note="{e(f["key"])}" placeholder="-"></li>\n' for f in g['fields']) + '    </ul>\n'
            if g.get('tracking'):
                body += '    <p class="sub">Time tracking</p>\n    <ul class="track">\n' + ''.join(
                    f'      <li><span>{e(t["label"])}</span><input type="number" min="0" max="{10 if t["unit"] == "/10" else 24}" step="0.5" data-note="track-{e(t["key"])}" placeholder="__"><span>{e(t["unit"])}'
                    + (f' (plan {t["plan"]:g}{e(t["unit"])})' if t.get('plan') else '') + '</span></li>\n' for t in g['tracking']) + '    </ul>\n'
        elif kind == 'notes':
            body = '    <ul class="notes">\n' + ''.join(
                f'      <li><span>{e(f["label"])}</span><input type="text" data-note="{e(f["key"])}" placeholder="-"></li>\n' for f in g['fields']) + '    </ul>\n'
        elif kind == 'list':
            body = '    <ul class="notes">\n' + ''.join(
                f'      <li><span>{i + 1}.</span><input type="text" data-note="{e(g["key"])}-{i}" placeholder="-"></li>\n' for i in range(g.get('slots', 3))) + '    </ul>\n'
        elif kind == 'progress':
            body = '    <p class="prog" id="prog"></p>\n'
        groups.append(f'  <section class="grp" data-group="{e(g["id"])}" data-weekly="{1 if g.get("weekly") else 0}" style="--c:{e(g.get("color", "#5A6C93"))}">\n'
                      + head + body + '  </section>\n')
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(todo["title"])} · Studybook</title>
<meta name="description" content="{e(todo["description"])}">
<meta name="theme-color" content="#1C2A4A">
<link rel="manifest" href="{up}manifest.webmanifest">
<link rel="icon" href="{up}icons/icon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@400;700;800&family=Noto+Sans+Khmer:wght@400;600&display=swap">
<style>
:root{{--bg:#F4F6FA;--card:#FFFFFF;--ink:#23262D;--mute:#5A6270;--line:#DDE1E8;--navy:#1C2A4A}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12151C;--card:#1B2029;--ink:#E8EAEE;--mute:#9AA3B2;--line:#2C3340}}}}
:root[data-theme="dark"]{{--bg:#12151C;--card:#1B2029;--ink:#E8EAEE;--mute:#9AA3B2;--line:#2C3340}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 "Gothic A1",system-ui,sans-serif}}
.km{{font-family:"Noto Sans Khmer","Gothic A1",sans-serif}}
header{{background:var(--navy);color:#fff;padding:18px 16px 16px}}
.wrap{{max-width:760px;margin:0 auto}}
header a.back{{color:#fff;opacity:.85;text-decoration:none;font-weight:700;font-size:.9rem}}
header h1{{margin:.3rem 0 .1rem;font-size:1.5rem;line-height:1.25}}
header p{{margin:0;opacity:.85}}
.total{{display:flex;align-items:center;gap:12px;margin-top:12px}}
.total .bar{{flex:1;background:rgba(255,255,255,.18)}}
.total .bar span{{background:#F5B700}}
main{{padding:16px}}
.note{{color:var(--mute);font-size:.9rem;margin:0 0 14px}}
.grp{{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--c);border-radius:12px;padding:14px 14px 6px;margin:0 0 14px}}
.grp h2{{font-size:1.05rem;margin:0 0 8px;display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}}
.grp h2 .km{{font-weight:400;color:var(--mute);font-size:.9rem}}
.grp h2 .cnt{{margin-left:auto;font-size:.85rem;color:var(--mute);font-weight:700}}
.bar{{height:6px;border-radius:3px;background:var(--line);overflow:hidden;margin-bottom:6px}}
.bar span{{display:block;height:100%;width:0;background:var(--c);transition:width .25s}}
ul{{list-style:none;margin:0;padding:0}}
li{{display:flex;align-items:flex-start;gap:8px;padding:10px 0;border-top:1px solid var(--line)}}
li:first-child{{border-top:0}}
label{{flex:1;display:flex;gap:12px;cursor:pointer;min-width:0}}
input[type=checkbox]{{position:absolute;opacity:0;width:1px;height:1px}}
.box{{flex:none;width:24px;height:24px;border:2px solid var(--c);border-radius:6px;margin-top:1px;display:grid;place-items:center}}
input:checked+.box{{background:var(--c)}}
input:checked+.box::after{{content:"";width:6px;height:11px;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg) translate(-1px,-1px)}}
input:focus-visible+.box{{outline:3px solid #F5B700;outline-offset:2px}}
.txt{{display:flex;flex-direction:column;min-width:0}}
.txt .km{{color:var(--mute);font-size:.88rem}}
input:checked~.txt .en{{text-decoration:line-through;color:var(--mute)}}
a.go{{flex:none;font-size:.85rem;font-weight:700;color:var(--c);text-decoration:none;border:1.5px solid var(--c);border-radius:999px;padding:2px 10px;margin-top:2px}}
footer{{color:var(--mute);font-size:.85rem;padding:0 16px 32px}}
li.sec{{display:block;font-weight:800;font-size:.85rem;color:var(--mute);text-transform:uppercase;letter-spacing:.04em;padding:12px 0 2px}}
.code{{font-family:ui-monospace,Menlo,monospace;font-size:.85rem;color:var(--c);margin-right:2px}}
.tm{{font-family:ui-monospace,Menlo,monospace;font-size:.85rem;color:var(--mute);font-weight:700}}
ul.notes li,ul.track li,li.note{{display:flex;align-items:center;gap:10px}}
ul.notes li span,ul.track li span:first-child{{flex:none;min-width:9.5em;color:var(--mute);font-size:.9rem}}
input[type=text],input[type=number]{{position:static;opacity:1;width:auto;height:auto;flex:1;min-width:0;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:8px 10px}}
input[type=number]{{flex:0 0 5.5em}}
li.note{{padding-top:0;border-top:0}}
.sub{{font-weight:800;font-size:.85rem;color:var(--mute);text-transform:uppercase;letter-spacing:.04em;margin:12px 0 0}}
.prog{{font-family:ui-monospace,Menlo,monospace;white-space:pre;margin:4px 0 10px}}
.foot{{text-align:center;font-weight:800;letter-spacing:.04em}}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="back" href="../">&larr; English</a>
  <h1>{e(todo["title"])}</h1>
  <p class="km" lang="km">{e(todo["title_km"])}</p>
  <div class="total"><div class="bar"><span id="totalBar"></span></div><b id="totalTxt">0/{total}</b></div>
</div></header>
<main class="wrap">
  <p class="note">Daily goal: <b>{e(todo.get("goal", ""))}</b>. Everything resets each morning, except the week goals, which reset each Monday. For history and reports, use the Telegram bot.</p>
{"".join(groups)}</main>
<footer class="wrap">{"".join(f'<p class="foot">{e(x)}</p>' for x in todo.get("footer", []))}<p>The same dashboard is in the Telegram bot, so both always match. Notes and ticks on this page are saved on this phone only.</p></footer>
<script>
(function(){{
  function pad(n){{return (n<10?'0':'')+n;}}
  var d=new Date(), day=d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
  var t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())); var dn=t.getUTCDay()||7; t.setUTCDate(t.getUTCDate()+4-dn);
  var y0=new Date(Date.UTC(t.getUTCFullYear(),0,1)), wk=t.getUTCFullYear()+'-W'+pad(Math.ceil(((t-y0)/864e5+1)/7));
  function key(w,id){{return 'todo:'+(w?wk:day)+':'+id;}}
  function get(k){{try{{return localStorage.getItem(k)==='1';}}catch(e){{return false;}}}}
  function put(k,v){{try{{v?localStorage.setItem(k,'1'):localStorage.removeItem(k);}}catch(e){{}}}}
  function count(){{
    var all=0, done=0;
    document.querySelectorAll('.grp').forEach(function(s){{
      var bs=s.querySelectorAll('input[type=checkbox]:not([data-ref])'), n=0;
      if(!bs.length)return;
      bs.forEach(function(b){{if(b.checked)n++;}});
      if(s.dataset.weekly!=='1'){{all+=bs.length; done+=n;}}
      s.querySelector('.cnt').textContent=n+'/'+bs.length;
      var bar=s.querySelector('.bar span'); if(bar)bar.style.width=(100*n/bs.length)+'%';
    }});
    document.getElementById('totalTxt').textContent=done+'/'+all;
    document.getElementById('totalBar').style.width=(100*done/all)+'%';
    var p=document.getElementById('prog');
    if(p)p.textContent='Total tasks:  '+all+'\\nCompleted:    '+done+'\\nPending:      '+(all-done)+'\\nCompletion:   '+Math.round(100*done/all)+'%';
  }}
  document.querySelectorAll('.grp').forEach(function(s){{
    var w=s.dataset.weekly==='1';
    s.querySelectorAll('input[type=checkbox]').forEach(function(b){{
      b.checked=get(key(w,b.dataset.id));
      b.addEventListener('change',function(){{
        put(key(w,b.dataset.id),b.checked);
        document.querySelectorAll('input[data-id="'+b.dataset.id+'"]').forEach(function(o){{o.checked=b.checked;}});
        count();
      }});
    }});
    s.querySelectorAll('input[data-note]').forEach(function(t){{
      var k='todo:'+day+':note:'+t.dataset.note;
      try{{t.value=localStorage.getItem(k)||'';}}catch(e){{}}
      t.addEventListener('input',function(){{try{{t.value?localStorage.setItem(k,t.value):localStorage.removeItem(k);}}catch(e){{}}}});
    }});
  }});
  count();
}})();
</script>
</body>
</html>
'''
    io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n').write(page)
    meta = {'title': todo['title'], 'title_km': todo['title_km'], 'description': todo['description'],
            'order': todo.get('order', 0), 'meta': f'{total} daily tasks in {len(todo["groups"])} sections'}
    io.open(os.path.join(d, 'page.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    print(f'{rel}/index.html: {total} daily tasks in {len(todo["groups"])} sections')


if __name__ == '__main__':
    main()
