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
a short code: 1, 2, 3 ... for "Every day", and the item id in capitals (R1, L2 ...) for the weekly groups.
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
    return s if len(s) <= n else s[:n - 1].rstrip() + '...'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def label(it):
    return it.get('short') or short(it['en'], 34)


def box(ok):
    return '[x]' if ok else '[ ]'


def of(n, total):
    return f'{n} of {total} done'


def week_range(day=None):
    day = day or now().date()
    s = day - dt.timedelta(days=day.weekday())
    return s, s + dt.timedelta(days=6)


# ---------------------------------------------------------------- views (plain text, no emoji)
def home_view(greet=False):
    dg = daily()
    today = done_set(period('daily'))
    week = done_set(period('week'))
    n_today = sum(it['id'] in today for it in dg['items'])
    wk_total = sum(len(g['items']) for g in weekly())
    wk_done = sum(1 for g in weekly() for it in g['items'] if it['id'] in week)
    t = now()
    ws, we = week_range()
    out = []
    if greet:
        out += ['<b>Good morning. It is 5:00.</b>', 'Get up, then write: <code>done 1</code>', '']
    out += [f'<b>TODAY</b>  {t:%A %d %B}', of(n_today, len(dg['items'])), '']
    for it in dg['items']:
        out.append(f'<code>{box(it["id"] in today)} {it["code"]:>2}</code>  {esc(label(it))}')
    if n_today == len(dg['items']):
        out += ['', '<b>All daily tasks are done. Well done.</b>']
    out += ['', f'<b>THIS WEEK</b>  {ws:%d %b} to {we:%d %b}', of(wk_done, wk_total), '']
    for g in weekly():
        if len(weekly()) > 1:
            out.append(f'{esc(g["title"])}:')
        for it in g['items']:
            out.append(f'<code>{box(it["id"] in week)} {it["code"]:>2}</code>  {esc(label(it))}')
    ex = weekly()[0]['items'][0]['code'] if weekly() else 'A1'
    out += ['', '<b>HOW TO USE</b>',
            f'Finished a task? Write <code>done 2</code> or <code>done 2 5 {ex}</code>',
            'Made a mistake? Write <code>undo 2</code>',
            'Or tap a task below.']
    kb = [[{'text': f'{box(it["id"] in today)} {it["code"]}  {label(it)}', 'callback_data': f't:{it["id"]}:home'}] for it in dg['items']]
    kb += [[{'text': f'{box(it["id"] in week)} {it["code"]}  {label(it)}', 'callback_data': f't:{it["id"]}:home'}] for g in weekly() for it in g['items']]
    kb.append([{'text': 'Today', 'callback_data': 'r:today'}, {'text': 'Week', 'callback_data': 'r:week'},
               {'text': 'Month', 'callback_data': 'r:month'}, {'text': 'Year', 'callback_data': 'r:year'}])
    kb.append([{'text': 'History', 'callback_data': 'h'}, {'text': 'Website', 'url': SITE_URL}])
    return '\n'.join(out), {'inline_keyboard': kb}


def group_view(gid):
    g = next((g for g in groups() if g['id'] == gid), None)
    if not g:
        return home_view()
    per = period(gid)
    ds = done_set(per)
    n = sum(it['id'] in ds for it in g['items'])
    if gid == 'daily':
        when = f'{now():%A %d %B}'
    else:
        ws, we = week_range()
        when = f'{ws:%d %b} to {we:%d %b}'
    out = [f'<b>{esc(g["title"]).upper()}</b>  {when}', f'<i>{esc(g["km"])}</i>', of(n, len(g['items'])), '']
    for it in g['items']:
        out += [f'<code>{box(it["id"] in ds)} {it["code"]}</code>  <b>{esc(label(it))}</b>',
                f'{esc(it["en"])}', f'<i>{esc(it["km"])}</i>', '']
    out += [f'Finished one? Write <code>done {g["items"][0]["code"]}</code> or tap it below.']
    kb = [[{'text': f'{box(it["id"] in ds)} {it["code"]}  {label(it)}', 'callback_data': f't:{it["id"]}:{gid}'}] for it in g['items']]
    kb.append([{'text': 'Back to today', 'callback_data': 'home'}, {'text': 'Week report', 'callback_data': 'r:week'}])
    return '\n'.join(out), {'inline_keyboard': kb}


def span(kind):
    t = now().date()
    if kind == 'today':
        return t, t, f'TODAY  {t:%A %d %B}'
    if kind == 'week':
        s, e = week_range(t)
        return s, t, f'THIS WEEK  {s:%d %b} to {e:%d %b}'
    if kind == 'month':
        return t.replace(day=1), t, f'THIS MONTH  {t:%B %Y}'
    return t.replace(month=1, day=1), t, f'THIS YEAR  {t:%Y}'


def report_view(kind):
    start, end, title = span(kind)
    rows = db.execute('SELECT period, item, at FROM state WHERE done=1 AND substr(at,1,10) BETWEEN ? AND ?',
                      (start.isoformat(), end.isoformat())).fetchall()
    first = db.execute("SELECT v FROM meta WHERE k='since'").fetchone()
    since = max(start, dt.date.fromisoformat(first[0])) if first else start  # don't count days before the bot started
    days = (end - since).days + 1
    dg = daily()
    daily_ids = {it['id'] for it in dg['items']}
    per_day, counts = {}, {}
    for per, item, at in rows:
        per_day[at[:10]] = per_day.get(at[:10], 0) + 1
        counts[item] = counts.get(item, 0) + 1
    daily_done = sum(c for i, c in counts.items() if i in daily_ids)
    possible = days * len(dg['items'])
    active = {r[0] for r in db.execute('SELECT DISTINCT substr(at,1,10) FROM state WHERE done=1')}
    streak, d = 0, end if end.isoformat() in active else end - dt.timedelta(days=1)
    while d.isoformat() in active:
        streak += 1
        d -= dt.timedelta(days=1)
    pct = round(100 * daily_done / possible) if possible else 0
    lines = [f'<b>{title}</b>', '',
             f'<code>Tasks done    {len(rows)}</code>',
             f'<code>Daily tasks   {daily_done} of {possible} ({pct}%)</code>',
             f'<code>Active days   {len(per_day)} of {days}</code>',
             f'<code>Streak        {streak} day{"s" if streak != 1 else ""}</code>']
    if kind in ('month', 'year') and per_day:
        best = max(per_day.items(), key=lambda x: x[1])
        lines.append(f'<code>Best day      {dt.date.fromisoformat(best[0]):%a %d %b} ({best[1]} tasks)</code>')
    if kind == 'week':
        wk = done_set(period('week'))
        lines += ['', '<b>Week goals</b>']
        lines += [f'<code>{box(it["id"] in wk)} {it["code"]:>2}</code>  {esc(label(it))}' for g in weekly() for it in g['items']]
    if kind == 'month' and per_day:
        lines += ['', '<b>Tasks per week</b>']
        d = start
        while d <= end:
            ws, we = week_range(d)
            n = sum(v for k, v in per_day.items() if max(ws, start).isoformat() <= k <= min(we, end).isoformat())
            lines.append(f'<code>{max(ws, start):%d %b} to {min(we, end):%d %b}   {n}</code>')
            d = we + dt.timedelta(days=1)
    if kind == 'year' and per_day:
        lines += ['', '<b>Tasks per month</b>']
        for m in range(1, end.month + 1):
            n = sum(v for k, v in per_day.items() if int(k[5:7]) == m)
            lines.append(f'<code>{dt.date(end.year, m, 1):%B}  {n}</code>')
    lines += ['', '<b>What you finished</b>']
    if not rows:
        lines.append('Nothing yet. When you finish a task, write <code>done 1</code>.')
    for g in groups():
        got = [(it, counts[it['id']]) for it in g['items'] if it['id'] in counts]
        if got:
            lines.append(f'{esc(g["title"])}:')
            lines += [f'<code>  {it["code"]:>2}</code>  {esc(label(it))}' + (f'  ({c} times)' if c > 1 else '') for it, c in got]
    kb = {'inline_keyboard': [[{'text': ('> ' if k == kind else '') + lab, 'callback_data': f'r:{k}'} for k, lab in
                               (('today', 'Today'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'))],
                              [{'text': 'Back to today', 'callback_data': 'home'}, {'text': 'History', 'callback_data': 'h'}]]}
    return '\n'.join(lines), kb


def history_view():
    dg = daily()
    today = now().date()
    lines = ['<b>HISTORY</b>', '', '<b>Daily tasks, last 14 days</b>']
    for i in range(14):
        day = today - dt.timedelta(days=i)
        ds = done_set(day.isoformat())
        got = [it['code'] for it in dg['items'] if it['id'] in ds]
        lines.append(f'<code>{day:%a %d %b}  {len(got)}/{len(dg["items"])}  {" ".join(got) if got else "-"}</code>')
    lines += ['', '<b>Week goals, last 6 weeks</b>']
    for i in range(6):
        day = today - dt.timedelta(weeks=i)
        ds = done_set(period('week', day))
        ws, _ = week_range(day)
        done_n = sum(it['id'] in ds for g in weekly() for it in g['items'])
        total = sum(len(g['items']) for g in weekly())
        lines.append(f'<code>Week of {ws:%d %b}  {done_n}/{total}</code>')
    first = db.execute('SELECT MIN(at), COUNT(*) FROM events WHERE done=1').fetchone()
    if first[0]:
        lines += ['', f'{first[1]} tasks ticked since {first[0][:10]}.']
    kb = {'inline_keyboard': [[{'text': 'Back to today', 'callback_data': 'home'}, {'text': 'Latest ticks', 'callback_data': 'log'}]]}
    return '\n'.join(lines), kb


def log_view(n=25):
    rows = db.execute('SELECT at, item, done, by FROM events ORDER BY at DESC LIMIT ?', (n,)).fetchall()
    lines = [f'<b>LATEST {len(rows)} TICKS</b>', '']
    for at, item, done, by in rows:
        _, it = by_id(item)
        lines.append(f'<code>{at[5:16].replace("T", " ")}  {"done" if done else "undo"}</code>  '
                     f'{esc(label(it) if it else item)}  ({esc(by)})')
    if not rows:
        lines.append('Nothing yet. When you finish a task, write <code>done 1</code>.')
    return '\n'.join(lines), {'inline_keyboard': [[{'text': 'Back to today', 'callback_data': 'home'}, {'text': 'History', 'callback_data': 'h'}]]}


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


def send_home(greet=False):
    text, kb = home_view(greet)
    return say(text, kb)


HELP = ('<b>HOW TO USE THIS BOT</b>\n\n'
        f'Every morning at {MORNING}:00 I send the list for the day.\n\n'
        '<b>Mark a task done</b>\n'
        '<code>done 2</code>  or  <code>done 2 5 R1</code>\n'
        'You can also reply to my list with the numbers, or tap a task.\n\n'
        '<b>Take a tick back</b>\n'
        '<code>undo 2</code>\n\n'
        '<b>See your progress</b>\n'
        '/todo  the list for today\n'
        '/today  /week  /month  /year  what you finished\n'
        '/history  the last 14 days and 6 weeks\n'
        '/log  the latest ticks\n\n'
        'Daily tasks ({daily}) start again each day. '
        'Weekly tasks ({weekly}) start again each Monday.')


def codes_hint():
    return f'1 to {len(daily()["items"])}, or ' + ', '.join(g['items'][0]['code'] for g in weekly()) + ' and so on'


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
        lines.append(f'<b>{"Done" if value else "Undone"}</b> ({esc(who)})')
        lines += [f'<code>{it["code"]:>3}</code>  {esc(label(it))}' for it in ok]
    if same:
        lines.append(('Already done: ' if value else 'Was not done: ') + ', '.join(it['code'] for it in same))
    if bad:
        lines.append('I do not know: ' + ', '.join(esc(b) for b in bad) + '. Use ' + codes_hint() + '.')
    if ok:
        today = done_set(period('daily'))
        total = len(daily()['items'])
        n = sum(it['id'] in today for it in daily()['items'])
        lines += ['', f'Today: {of(n, total)}.' + (' All daily tasks are done. Well done.' if n == total else '')]
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
    if head in ('/done', 'done'):
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
        return say(HELP.format(daily='1–' + str(len(daily()['items'])), weekly=', '.join(g['items'][0]['code'][0] for g in weekly())))


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
                note = ('Undone: ' if cur else 'Done: ') + label(it)
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
                send_home(greet=True)
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
