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
    total = sum(len(g['items']) for g in todo['groups'])
    groups = []
    for g in todo['groups']:
        items = []
        for it in g['items']:
            link = ''
            if it.get('link'):
                ext = it['link'].startswith('http')
                link = f' <a class="go" href="{e(it["link"])}"{" target=_blank rel=noopener" if ext else ""}>open</a>'
            items.append(f'      <li><label><input type="checkbox" data-id="{e(it["id"])}"><span class="box" aria-hidden="true"></span>'
                         f'<span class="txt"><span class="en">{e(it["en"])}</span><span class="km" lang="km">{e(it["km"])}</span></span></label>{link}</li>\n')
        groups.append(f'  <section class="grp" data-group="{e(g["id"])}" style="--c:{e(g["color"])}">\n'
                      f'    <h2>{e(g["title"])} <span class="km" lang="km">{e(g["km"])}</span><span class="cnt"></span></h2>\n'
                      f'    <div class="bar"><span></span></div>\n'
                      f'    <ul>\n{"".join(items)}    </ul>\n  </section>\n')
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
input{{position:absolute;opacity:0;width:1px;height:1px}}
.box{{flex:none;width:24px;height:24px;border:2px solid var(--c);border-radius:6px;margin-top:1px;display:grid;place-items:center}}
input:checked+.box{{background:var(--c)}}
input:checked+.box::after{{content:"";width:6px;height:11px;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg) translate(-1px,-1px)}}
input:focus-visible+.box{{outline:3px solid #F5B700;outline-offset:2px}}
.txt{{display:flex;flex-direction:column;min-width:0}}
.txt .km{{color:var(--mute);font-size:.88rem}}
input:checked~.txt .en{{text-decoration:line-through;color:var(--mute)}}
a.go{{flex:none;font-size:.85rem;font-weight:700;color:var(--c);text-decoration:none;border:1.5px solid var(--c);border-radius:999px;padding:2px 10px;margin-top:2px}}
footer{{color:var(--mute);font-size:.85rem;padding:0 16px 32px}}
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
  <p class="note">"Every day" resets each morning; the other groups reset each Monday. Ticks are saved on this phone. To tick together and keep history, use <b>/todo</b> in the Telegram group.</p>
{"".join(groups)}</main>
<footer class="wrap">The same list is in the Telegram bot, so both always match.</footer>
<script>
(function(){{
  function pad(n){{return (n<10?'0':'')+n;}}
  var d=new Date(), day=d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
  var t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())); var dn=t.getUTCDay()||7; t.setUTCDate(t.getUTCDate()+4-dn);
  var y0=new Date(Date.UTC(t.getUTCFullYear(),0,1)), wk=t.getUTCFullYear()+'-W'+pad(Math.ceil(((t-y0)/864e5+1)/7));
  function key(g,id){{return 'todo:'+(g==='daily'?day:wk)+':'+id;}}
  function get(k){{try{{return localStorage.getItem(k)==='1';}}catch(e){{return false;}}}}
  function put(k,v){{try{{v?localStorage.setItem(k,'1'):localStorage.removeItem(k);}}catch(e){{}}}}
  var all=0, done=0;
  function count(){{
    all=0; done=0;
    document.querySelectorAll('.grp').forEach(function(s){{
      var bs=s.querySelectorAll('input'), n=0; bs.forEach(function(b){{if(b.checked)n++;}});
      all+=bs.length; done+=n;
      s.querySelector('.cnt').textContent=n+'/'+bs.length;
      s.querySelector('.bar span').style.width=(100*n/bs.length)+'%';
    }});
    document.getElementById('totalTxt').textContent=done+'/'+all;
    document.getElementById('totalBar').style.width=(100*done/all)+'%';
  }}
  document.querySelectorAll('.grp').forEach(function(s){{
    var g=s.dataset.group;
    s.querySelectorAll('input').forEach(function(b){{
      b.checked=get(key(g,b.dataset.id));
      b.addEventListener('change',function(){{put(key(g,b.dataset.id),b.checked);count();}});
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
            'order': todo.get('order', 0), 'meta': f'{total} tasks · {len(todo["groups"])} groups'}
    io.open(os.path.join(d, 'page.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(meta, ensure_ascii=False, indent=1) + '\n')
    print(f'{rel}/index.html: {total} tasks in {len(todo["groups"])} groups')


if __name__ == '__main__':
    main()
