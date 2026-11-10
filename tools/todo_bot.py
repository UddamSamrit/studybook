# -*- coding: utf-8 -*-
"""Telegram bot for the English to-do list: posts the list every morning, marks tasks done by text or
button, and reports what you finished today, this week, this month and this year.

    python tools/todo_bot.py            run the bot (long polling, never exits)
    python tools/todo_bot.py --once     post today's list to the group and exit

Settings come from ~/.studybook-bot/config.env (never from this public repo):

    TELEGRAM_BOT_TOKEN=123:ABC          from @BotFather
    TELEGRAM_CHAT_ID=-100...            the group the bot answers in
    TZ_NAME=Asia/Phnom_Penh             time zone for "today"
    MORNING_HOUR=5                      the bot posts the day's list at this hour
    TODO_URL=https://.../todo.json      optional: where the list lives (default: the live site)

The list is english/todo/todo.json on the site, so the page and the bot always match. Each task has
a short code: 1-5 for "Every day", R1, L1, S1, W1, K1, I1, G1 ... for the weekly groups.
"Every day" tasks reset each day; the other groups reset each Monday.

In the group:
    done 1 3 R2       mark tasks done (also: /done 1 3, or reply "1 3" to the bot's list)
    undo 2            take a tick back (also: /undo 2)
    /todo             today's list with tick buttons
    /today /week /month /year   what you finished in that period
    /history          the last 14 days and 6 weeks at a glance
    /log              the latest ticks, with who and when

Plain "done 1" messages reach the bot only if it is a group admin (Telegram privacy mode);
commands and replies to the bot always work. Every tick is kept in ~/.studybook-bot/history.db.
Standard library only.
"""
import datetime as dt
import io
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HOME = os.path.expanduser('~/.studybook-bot')
CFG = {}
for line in io.open(os.path.join(HOME, 'config.env'), encoding='utf-8'):
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.strip().split('=', 1)
        CFG[k] = v
TOKEN = CFG['TELEGRAM_BOT_TOKEN']
CHAT = int(CFG['TELEGRAM_CHAT_ID'])
TZ = ZoneInfo(CFG.get('TZ_NAME', 'Asia/Phnom_Penh'))
MORNING = int(CFG.get('MORNING_HOUR', '5'))
TODO_URL = CFG.get('TODO_URL', 'https://uddamsamrit.github.io/studybook/english/todo/todo.json')
SITE_URL = TODO_URL.rsplit('/', 1)[0] + '/'
API = f'https://api.telegram.org/bot{TOKEN}/'
CACHE = os.path.join(HOME, 'todo.json')

db = sqlite3.connect(os.path.join(HOME, 'history.db'))
db.executescript('''
CREATE TABLE IF NOT EXISTS state (period TEXT, item TEXT, done INTEGER, by TEXT, at TEXT, PRIMARY KEY (period, item));
CREATE TABLE IF NOT EXISTS events (at TEXT, period TEXT, item TEXT, done INTEGER, by TEXT);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
''')


def log(*a):
    print(dt.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S'), *a, flush=True)


def api(method, **params):
    data = urllib.parse.urlencode({k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(API + method, data=data), timeout=70) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = json.load(e)
        if 'message is not modified' not in body.get('description', ''):
            log('api error', method, body.get('description'))
        return body


# ---------------------------------------------------------------- the list
_todo = {'at': 0, 'data': None}


def todo():
    """The list from the live site (refreshed every 10 minutes), else the last copy saved here."""
    if _todo['data'] and time.time() - _todo['at'] < 600:
        return _todo['data']
    try:
        with urllib.request.urlopen(TODO_URL + '?t=' + str(int(time.time())), timeout=20) as r:
            data = json.load(r)
        io.open(CACHE, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False))
    except Exception as e:  # offline or not deployed yet: keep the last good copy
        log('todo fetch failed, using cache:', e)
        data = json.load(io.open(CACHE, encoding='utf-8'))
    for g in data['groups']:  # short codes people can type: 1..5 for daily, R1, L2 ... for the rest
        for i, it in enumerate(g['items'], 1):
            it['code'] = str(i) if g['id'] == 'daily' else it['id'].upper()
    _todo.update(at=time.time(), data=data)
    return data


def groups():
    return todo()['groups']


def daily():
    return next(g for g in groups() if g['id'] == 'daily')


def weekly():
    return [g for g in groups() if g['id'] != 'daily']


def by_code(code):
    code = code.strip().upper().rstrip('.,')
    for g in groups():
        for it in g['items']:
            if it['code'] == code or it['id'].upper() == code:
                return g, it
    return None, None


def by_id(item_id):
    for g in groups():
        for it in g['items']:
            if it['id'] == item_id:
                return g, it
    return None, None


# ---------------------------------------------------------------- time and state
def now():
    return dt.datetime.now(TZ)


def period(group_id, day=None):
    day = day or now().date()
    if group_id == 'daily':
        return day.isoformat()
    y, w, _ = day.isocalendar()
    return f'{y}-W{w:02d}'


def done_set(per):
    return {r[0] for r in db.execute('SELECT item FROM state WHERE period=? AND done=1', (per,))}


def set_done(g, it, value, who):
    per = period(g['id'])
    cur = db.execute('SELECT done FROM state WHERE period=? AND item=?', (per, it['id'])).fetchone()
    if bool(cur and cur[0]) == bool(value):
        return False
    at = now().isoformat(timespec='seconds')
    db.execute('INSERT OR REPLACE INTO state VALUES (?,?,?,?,?)', (per, it['id'], 1 if value else 0, who, at))
    db.execute('INSERT INTO events VALUES (?,?,?,?,?)', (at, per, it['id'], 1 if value else 0, who))
    db.commit()
    return True


def short(s, n=44):
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------------------------------------------------------------- views
def home_view():
    dg = daily()
    today = done_set(period('daily'))
    week = done_set(period('week'))
    wk_total = sum(len(g['items']) for g in weekly())
    wk_done = sum(1 for g in weekly() for it in g['items'] if it['id'] in week)
    t = now()
    text = (f'<b>📚 English to-do · {t:%A %d %B}</b>\n'
            f'Today {sum(it["id"] in today for it in dg["items"])}/{len(dg["items"])} · This week {wk_done}/{wk_total}\n\n'
            f'<b>{esc(dg["title"])}</b> · <i>{esc(dg["km"])}</i>\n'
            + '\n'.join(f'{"✅" if it["id"] in today else "⬜"} <b>{it["code"]}</b>. {esc(it["en"])}' for it in dg['items'])
            + '\n\n<b>This week</b>\n'
            + '\n'.join(f'{"✅" if all(it["id"] in week for it in g["items"]) else "▫️"} {esc(g["title"])} '
                        f'{sum(it["id"] in week for it in g["items"])}/{len(g["items"])} · '
                        + ' '.join(('✓' if it['id'] in week else '') + it['code'] for it in g['items']) for g in weekly())
            + '\n\nWhen you finish one, write <code>done 1 3</code> or <code>done R2</code> '
              '(or reply to this message with the numbers). Tap a group to see its tasks.')
    kb = [[{'text': f'{"✅" if it["id"] in today else "⬜"} {it["code"]}. {short(it["en"])}', 'callback_data': f't:{it["id"]}:home'}] for it in dg['items']]
    row = []
    for g in weekly():
        n = sum(it['id'] in week for it in g['items'])
        row.append({'text': f'{g["title"]} {n}/{len(g["items"])}', 'callback_data': f'g:{g["id"]}'})
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([{'text': '📅 Today', 'callback_data': 'r:today'}, {'text': '🗓 Week', 'callback_data': 'r:week'},
               {'text': '📆 Month', 'callback_data': 'r:month'}, {'text': '🏆 Year', 'callback_data': 'r:year'}])
    kb.append([{'text': '📜 History', 'callback_data': 'h'}, {'text': '🌐 Site', 'url': SITE_URL}])
    return text, {'inline_keyboard': kb}


def group_view(gid):
    g = next((g for g in groups() if g['id'] == gid), None)
    if not g:
        return home_view()
    per = period(gid)
    ds = done_set(per)
    when = 'today' if gid == 'daily' else f'this week ({per})'
    text = (f'<b>{esc(g["title"])}</b> · {when}\n<i>{esc(g["km"])}</i>\n\n'
            + '\n\n'.join(f'{"✅" if it["id"] in ds else "⬜"} <b>{it["code"]}</b>. {esc(it["en"])}\n<i>{esc(it["km"])}</i>' for it in g['items'])
            + f'\n\nWrite <code>done {g["items"][0]["code"]}</code> when you finish one, or tap it below.')
    kb = [[{'text': f'{"✅" if it["id"] in ds else "⬜"} {it["code"]}. {short(it["en"])}', 'callback_data': f't:{it["id"]}:{gid}'}] for it in g['items']]
    kb.append([{'text': '⬅️ Back', 'callback_data': 'home'}, {'text': '🗓 This week', 'callback_data': 'r:week'}])
    return text, {'inline_keyboard': kb}


def span(kind):
    t = now().date()
    if kind == 'today':
        return t, t, f'Today · {t:%A %d %B}'
    if kind == 'week':
        s = t - dt.timedelta(days=t.weekday())
        return s, t, f'This week · {s:%d %b} – {s + dt.timedelta(days=6):%d %b}'
    if kind == 'month':
        s = t.replace(day=1)
        return s, t, f'This month · {t:%B %Y}'
    s = t.replace(month=1, day=1)
    return s, t, f'This year · {t:%Y}'


def report_view(kind):
    start, end, title = span(kind)
    rows = db.execute('SELECT period, item, at FROM state WHERE done=1 AND substr(at,1,10) BETWEEN ? AND ?',
                      (start.isoformat(), end.isoformat())).fetchall()
    first = db.execute("SELECT v FROM meta WHERE k='since'").fetchone()
    since = max(start, dt.date.fromisoformat(first[0])) if first else start  # don't count days before the bot started
    days = (end - since).days + 1
    dg = daily()
    daily_ids = {it['id'] for it in dg['items']}
    per_day = {}
    counts = {}
    for per, item, at in rows:
        per_day.setdefault(at[:10], 0)
        per_day[at[:10]] += 1
        counts[item] = counts.get(item, 0) + 1
    daily_done = sum(c for i, c in counts.items() if i in daily_ids)
    possible = days * len(dg['items'])
    # streak: days in a row, up to today (or yesterday if today is still empty), with at least one tick
    active = {r[0] for r in db.execute('SELECT DISTINCT substr(at,1,10) FROM state WHERE done=1')}
    streak, d = 0, end if end.isoformat() in active else end - dt.timedelta(days=1)
    while d.isoformat() in active:
        streak += 1
        d -= dt.timedelta(days=1)
    lines = [f'<b>✅ {title}</b>', '',
             f'Done: <b>{len(rows)}</b> task{"s" if len(rows) != 1 else ""} · active days {len(per_day)}/{days} · streak {streak} day{"s" if streak != 1 else ""}',
             f'Every day: {daily_done}/{possible} ({round(100 * daily_done / possible) if possible else 0}%)']
    if kind != 'today':
        if kind == 'week':
            weeks_done = done_set(period('week'))
            lines.append('Weekly groups: ' + ' · '.join(f'{g["title"]} {sum(it["id"] in weeks_done for it in g["items"])}/{len(g["items"])}' for g in weekly()))
        if kind in ('month', 'year') and per_day:
            best = max(per_day.items(), key=lambda x: x[1])
            lines.append(f'Best day: {dt.date.fromisoformat(best[0]):%a %d %b} with {best[1]} tasks')
    lines.append('')
    if not rows:
        lines.append('Nothing ticked yet. Write <code>done 1</code> when you finish a task.')
    for g in groups():
        got = [(it, counts[it['id']]) for it in g['items'] if it['id'] in counts]
        if not got:
            continue
        lines.append(f'<b>{esc(g["title"])}</b>')
        for it, c in got:
            lines.append(f'  ✅ {it["code"]}. {esc(short(it["en"], 60))}' + (f' <b>×{c}</b>' if c > 1 else ''))
    if kind in ('month', 'year') and per_day and kind == 'month':
        lines += ['', '<b>Days</b>']
        d = start
        cal = []
        while d <= end:
            n = per_day.get(d.isoformat(), 0)
            cal.append('🟩' if n >= 5 else '🟨' if n else '⬜')
            d += dt.timedelta(days=1)
        lines.append(''.join(cal) + '  (🟩 5+ · 🟨 some)')
    if kind == 'year' and per_day:
        lines += ['', '<b>Months</b>']
        for m in range(1, end.month + 1):
            n = sum(v for k, v in per_day.items() if int(k[5:7]) == m)
            lines.append(f'<code>{dt.date(end.year, m, 1):%b}</code> {"▇" * min(n // 5, 20)} {n}')
    kb = {'inline_keyboard': [[{'text': ('• ' if k == kind else '') + lab, 'callback_data': f'r:{k}'} for k, lab in
                               (('today', 'Today'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'))],
                              [{'text': '⬅️ To-do list', 'callback_data': 'home'}]]}
    return '\n'.join(lines), kb


def history_view():
    dg = daily()
    today = now().date()
    lines = ['<b>📜 History</b>', '', '<b>Every day</b> · last 14 days']
    for i in range(14):
        day = today - dt.timedelta(days=i)
        ds = done_set(day.isoformat())
        n = sum(it['id'] in ds for it in dg['items'])
        lines.append(f'<code>{day:%a %d %b}</code> {"".join("✅" if it["id"] in ds else "⬜" for it in dg["items"])} {n}/{len(dg["items"])}')
    lines += ['', '<b>Weekly groups</b> · last 6 weeks']
    for i in range(6):
        per = period('week', today - dt.timedelta(weeks=i))
        ds = done_set(per)
        lines.append(f'<code>{per}</code> ' + ' · '.join(f'{g["title"].split()[0]} {sum(it["id"] in ds for it in g["items"])}/{len(g["items"])}' for g in weekly()))
    first = db.execute('SELECT MIN(at), COUNT(*) FROM events WHERE done=1').fetchone()
    if first[0]:
        lines += ['', f'{first[1]} ticks since {first[0][:10]}.']
    kb = {'inline_keyboard': [[{'text': '⬅️ Back', 'callback_data': 'home'}, {'text': '🧾 Latest ticks', 'callback_data': 'log'}]]}
    return '\n'.join(lines), kb


def log_view(n=25):
    rows = db.execute('SELECT at, item, done, by FROM events ORDER BY at DESC LIMIT ?', (n,)).fetchall()
    lines = [f'<b>🧾 Latest {len(rows)} ticks</b>', '']
    for at, item, done, by in rows:
        _, it = by_id(item)
        lines.append(f'<code>{at[5:16].replace("T", " ")}</code> {"✅" if done else "↩️"} {esc(short(it["en"] if it else item, 38))} · {esc(by)}')
    if not rows:
        lines.append('No ticks yet. Write <code>done 1</code> when you finish a task.')
    return '\n'.join(lines), {'inline_keyboard': [[{'text': '⬅️ Back', 'callback_data': 'home'}, {'text': '📜 History', 'callback_data': 'h'}]]}


def view(name):
    if name == 'home':
        return home_view()
    if name == 'h':
        return history_view()
    if name == 'log':
        return log_view()
    if name.startswith('r:'):
        return report_view(name[2:])
    return group_view(name)


def say(text, kb=None, reply_to=None):
    p = dict(chat_id=CHAT, text=text, parse_mode='HTML', disable_web_page_preview=True)
    if kb:
        p['reply_markup'] = kb
    if reply_to:
        p['reply_to_message_id'] = reply_to
    return api('sendMessage', **p)


def send_home():
    text, kb = home_view()
    return say(text, kb)


HELP = ('<b>English to-do bot</b>\n\n'
        f'Every morning at {MORNING}:00 I post the day\'s list.\n\n'
        '<b>Mark done</b>: <code>done 1 3</code> or <code>done R2</code>, or reply to my list with the numbers, '
        'or tap a task. <code>undo 2</code> takes a tick back.\n\n'
        '/todo · today\'s list\n'
        '/today · /week · /month · /year · what you finished\n'
        '/history · last 14 days and 6 weeks\n'
        '/log · latest ticks, who and when\n\n'
        '"Every day" (1–5) resets each day. Other groups (R, L, S, W, K, I, G) reset each Monday.')


# ---------------------------------------------------------------- handling
def mark(codes, value, who, reply_to):
    ok, same, bad = [], [], []
    for c in codes:
        g, it = by_code(c)
        if not it:
            bad.append(c)
        elif set_done(g, it, value, who):
            ok.append(it)
        else:
            same.append(it)
    lines = []
    if ok:
        lines.append(('✅ Done' if value else '↩️ Undone') + f' ({who}):')
        lines += [f'  {it["code"]}. {esc(short(it["en"], 60))}' for it in ok]
    if same:
        lines.append(('Already done: ' if value else 'Was not done: ') + ' '.join(it['code'] for it in same))
    if bad:
        lines.append('Unknown: ' + ' '.join(esc(b) for b in bad) + ' · codes are 1–5, R1, L1, S1, W1, K1, I1, G1 …')
    if value and ok:
        today = done_set(period('daily'))
        n = sum(it['id'] in today for it in daily()['items'])
        lines.append(f'Today {n}/{len(daily()["items"])}' + (' 🎉 all daily tasks done!' if n == len(daily()['items']) else ''))
    say('\n'.join(lines) or 'Nothing to change.', reply_to=reply_to)


CODE = re.compile(r'^(?:\d{1,2}|[A-Za-z]\d{1,2})[.,]?$')


def handle_text(m):
    text = (m.get('text') or '').strip()
    if not text:
        return
    who = m['from'].get('first_name') or m['from'].get('username') or 'someone'
    words = text.split()
    head = words[0].split('@')[0].lower()
    rest = words[1:]
    to_bot = (m.get('reply_to_message') or {}).get('from', {}).get('is_bot')
    if head in ('/done', 'done', '✅'):
        return mark(rest, True, who, m['message_id']) if rest else say('Which task? For example <code>done 1 3</code>.', reply_to=m['message_id'])
    if head in ('/undo', 'undo'):
        return mark(rest, False, who, m['message_id']) if rest else say('Which task? For example <code>undo 2</code>.', reply_to=m['message_id'])
    if to_bot and words and all(CODE.match(w) for w in words):  # a reply to the list with just numbers
        return mark(words, True, who, m['message_id'])
    if head in ('/todo', '/start', '/list'):
        return send_home()
    if head in ('/today', '/week', '/month', '/year'):
        text, kb = report_view(head[1:])
        return say(text, kb)
    if head == '/history':
        text, kb = history_view()
        return say(text, kb)
    if head == '/log':
        text, kb = log_view()
        return say(text, kb)
    if head == '/help':
        return say(HELP)


def handle(u):
    if 'callback_query' in u:
        q = u['callback_query']
        msg = q.get('message') or {}
        if msg.get('chat', {}).get('id') != CHAT:
            return api('answerCallbackQuery', callback_query_id=q['id'], text='This bot only works in its group.')
        who = q['from'].get('first_name') or q['from'].get('username') or 'someone'
        data = q.get('data', '')
        note = ''
        target = data
        if data.startswith('t:'):
            _, item, target = data.split(':', 2)
            g, it = by_id(item)
            if it:
                cur = it['id'] in done_set(period(g['id']))
                set_done(g, it, not cur, who)
                note = ('↩️ Not done: ' if cur else '✅ Done: ') + short(it['en'], 60)
        elif data.startswith('g:'):
            target = data[2:]
        text, kb = view(target)
        api('editMessageText', chat_id=CHAT, message_id=msg['message_id'], text=text, parse_mode='HTML', reply_markup=kb, disable_web_page_preview=True)
        return api('answerCallbackQuery', callback_query_id=q['id'], text=note)
    m = u.get('message') or {}
    if m.get('chat', {}).get('id') == CHAT:
        handle_text(m)


def morning_due():
    t = now()
    last = db.execute("SELECT v FROM meta WHERE k='morning'").fetchone()
    if t.hour >= MORNING and (not last or last[0] != t.date().isoformat()):
        db.execute("INSERT OR REPLACE INTO meta VALUES ('morning', ?)", (t.date().isoformat(),))
        db.commit()
        return True
    return False


def main():
    if '--once' in sys.argv:
        r = send_home()
        print('sent' if r.get('ok') else r)
        return
    api('setMyCommands', commands=[
        {'command': 'todo', 'description': "Today's English to-do list"},
        {'command': 'done', 'description': 'Mark tasks done, e.g. /done 1 3 R2'},
        {'command': 'undo', 'description': 'Take a tick back, e.g. /undo 2'},
        {'command': 'today', 'description': 'What I finished today'},
        {'command': 'week', 'description': 'What I finished this week'},
        {'command': 'month', 'description': 'What I finished this month'},
        {'command': 'year', 'description': 'What I finished this year'},
        {'command': 'history', 'description': 'Last 14 days and 6 weeks'},
        {'command': 'log', 'description': 'Latest ticks: who and when'},
        {'command': 'help', 'description': 'How this bot works'}])
    db.execute("INSERT OR IGNORE INTO meta VALUES ('since', ?)", (now().date().isoformat(),))
    db.commit()
    offset = int((db.execute("SELECT v FROM meta WHERE k='offset'").fetchone() or ['0'])[0])
    log('bot running for chat', CHAT, 'morning list at', f'{MORNING}:00')
    while True:
        try:
            if morning_due():
                send_home()
            r = api('getUpdates', offset=offset, timeout=50, allowed_updates=['message', 'callback_query'])
            for u in r.get('result', []):
                offset = u['update_id'] + 1
                db.execute("INSERT OR REPLACE INTO meta VALUES ('offset', ?)", (str(offset),))
                db.commit()
                try:
                    handle(u)
                except Exception as e:
                    log('handle error', repr(e))
        except Exception as e:  # network drop, sleep, etc.: wait and carry on
            log('loop error', repr(e))
            time.sleep(10)


if __name__ == '__main__':
    main()
