# -*- coding: utf-8 -*-
"""Telegram bot: a daily productivity dashboard you fill in by writing short messages.

    python tools/todo_bot.py            run the bot (long polling, never exits)
    python tools/todo_bot.py --once     post today's dashboard to the group and exit

Settings come from ~/.studybook-bot/config.env (never from this public repo):

    TELEGRAM_BOT_TOKEN=123:ABC          from @BotFather
    TELEGRAM_CHAT_ID=-100...            the group the bot answers in
    TZ_NAME=Asia/Phnom_Penh             time zone for "today"
    MORNING_HOUR=5                      the dashboard is posted at this hour
    EVENING_TIME=21:30                  the end-of-day review reminder is posted at this time
    TODO_URL=https://.../todo.json      optional: where the list lives (default: the live site)

The dashboard is english/todo/todo.json on the site (the page and the bot always match). It has
10 sections: top 3 priorities, work, learning, personal projects, follow-up, blockers, achievements,
daily progress, a timed plan with time tracking, and an end-of-day review, plus goals for the week.

What you write in the group (plain text, or reply to the bot):
    done W1 L2 T1         tick tasks          doing W1     mark in progress      undo W1   untick
    p1 Finish login API   set a priority      goal ...     set the daily goal
    follow / waiting / review / issue / reason / next / well / improve / tomorrow <text>
    win <text>            add an achievement  clear <word> remove what you wrote today
    work 7.5  learn 1.5  deep 4  focus 8      time tracking for today
    /todo  /today /week /month /year  /history  /log  /help

Plain messages reach the bot only if it is a group admin (Telegram privacy mode); commands and
replies to the bot always work. Everything is kept in ~/.studybook-bot/history.db.
Standard library only. No emoji in any message.
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
EVENING = CFG.get('EVENING_TIME', '21:30')
TODO_URL = CFG.get('TODO_URL', 'https://uddamsamrit.github.io/studybook/english/todo/todo.json')
SITE_URL = TODO_URL.rsplit('/', 1)[0] + '/'
API = f'https://api.telegram.org/bot{TOKEN}/'
CACHE = os.path.join(HOME, 'todo.json')

db = sqlite3.connect(os.path.join(HOME, 'history.db'))
db.executescript('''
CREATE TABLE IF NOT EXISTS state (period TEXT, item TEXT, done INTEGER, by TEXT, at TEXT, PRIMARY KEY (period, item));
CREATE TABLE IF NOT EXISTS events (at TEXT, period TEXT, item TEXT, done INTEGER, by TEXT);
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS track (day TEXT, key TEXT, value REAL, by TEXT, at TEXT, PRIMARY KEY (day, key));
CREATE TABLE IF NOT EXISTS notes (day TEXT, key TEXT, idx INTEGER, text TEXT, by TEXT, at TEXT, PRIMARY KEY (day, key, idx));
''')
DONE, DOING = 1, 2


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


# ---------------------------------------------------------------- the dashboard definition
_todo = {'at': 0, 'data': None}


def todo():
    """The dashboard from the live site (refreshed every 10 minutes), else the last copy saved here."""
    if _todo['data'] and time.time() - _todo['at'] < 600:
        return _todo['data']
    try:
        with urllib.request.urlopen(TODO_URL + '?t=' + str(int(time.time())), timeout=20) as r:
            data = json.load(r)
        io.open(CACHE, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False))
    except Exception as e:  # offline or not deployed yet: keep the last good copy
        log('todo fetch failed, using cache:', e)
        data = json.load(io.open(CACHE, encoding='utf-8'))
    items = {}
    for g in data['groups']:
        for it in g.get('items', []):
            if 'id' in it:
                it['code'] = it.get('code') or it['id'].upper()
                it['group'] = g['id']
                items[it['id']] = it
    for g in data['groups']:  # schedule lines can point at a task from another section
        for it in g.get('items', []):
            if 'ref' in it and it['ref'] in items:
                it['target'] = items[it['ref']]
    data['_items'] = items
    _todo.update(at=time.time(), data=data)
    return data


def groups():
    return todo()['groups']


def group(gid):
    return next((g for g in groups() if g['id'] == gid), None)


def tasks(g):
    """The tickable tasks of a group (schedule lines that point elsewhere are not counted twice)."""
    return [it for it in g.get('items', []) if 'id' in it]


def daily_tasks():
    return [it for g in groups() if not g.get('weekly') for it in tasks(g)]


def weekly_tasks():
    return [it for g in groups() if g.get('weekly') for it in tasks(g)]


def by_code(code):
    code = code.strip().upper().rstrip('.,')
    for it in todo()['_items'].values():
        if it['code'] == code:
            return it
    return None


def note_fields():
    return {f['key']: f for g in groups() if g.get('kind') == 'notes' for f in g['fields']}


def list_keys():
    return {g['key']: g for g in groups() if g.get('kind') == 'list'}


def tracking():
    return next((g.get('tracking', []) for g in groups() if g.get('tracking')), [])


# ---------------------------------------------------------------- time and state
def now():
    return dt.datetime.now(TZ)


def today_iso():
    return now().date().isoformat()


def week_key(day=None):
    y, w, _ = (day or now().date()).isocalendar()
    return f'{y}-W{w:02d}'


def week_range(day=None):
    day = day or now().date()
    s = day - dt.timedelta(days=day.weekday())
    return s, s + dt.timedelta(days=6)


def period_of(it, day=None):
    g = group(it['group'])
    return week_key(day) if g and g.get('weekly') else (day or now().date()).isoformat()


def status(it, day=None):
    r = db.execute('SELECT done FROM state WHERE period=? AND item=?', (period_of(it, day), it['id'])).fetchone()
    return r[0] if r else 0


def set_status(it, value, who):
    per = period_of(it)
    if status(it) == value:
        return False
    at = now().isoformat(timespec='seconds')
    db.execute('INSERT OR REPLACE INTO state VALUES (?,?,?,?,?)', (per, it['id'], value, who, at))
    db.execute('INSERT INTO events VALUES (?,?,?,?,?)', (at, per, it['id'], value, who))
    db.commit()
    return True


def note(key, idx=0, day=None):
    r = db.execute('SELECT text FROM notes WHERE day=? AND key=? AND idx=?', (day or today_iso(), key, idx)).fetchone()
    return r[0] if r else None


def notes_list(key, day=None):
    return [r[0] for r in db.execute('SELECT text FROM notes WHERE day=? AND key=? ORDER BY idx', (day or today_iso(), key))]


def set_note(key, text, who, append=False):
    day = today_iso()
    idx = 0
    if append:
        top = db.execute('SELECT MAX(idx) FROM notes WHERE day=? AND key=?', (day, key)).fetchone()[0]
        idx = 0 if top is None else top + 1
    db.execute('INSERT OR REPLACE INTO notes VALUES (?,?,?,?,?,?)', (day, key, idx, text, who, now().isoformat(timespec='seconds')))
    db.commit()


def clear_note(key):
    n = db.execute('DELETE FROM notes WHERE day=? AND key=?', (today_iso(), key)).rowcount
    db.commit()
    return n


# ---------------------------------------------------------------- text helpers
def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def short(s, n=40):
    return s if len(s) <= n else s[:n - 3].rstrip() + '...'


def box(st):
    return '[x]' if st == DONE else '[~]' if st == DOING else '[ ]'


def label(it):
    if it['id'] in ('p1', 'p2', 'p3'):
        return note(it['id']) or f'{it["short"]} (write: {it["id"]} ...)'
    return it.get('short') or short(it['en'])


def num(v):
    return f'{v:g}'


LINE = '------------------------------'


def track_lines(day):
    vals = {k: v for k, v in db.execute('SELECT key, value FROM track WHERE day=?', (day,))}
    width = max((len(t['label']) for t in tracking()), default=0) + 1
    out = []
    for t in tracking():
        v = vals.get(t['key'])
        plan = f'  plan {num(t["plan"])}{t["unit"]}' if t.get('plan') else ''
        out.append(f'<code>{(t["label"] + ":"):<{width}} {(num(v) if v is not None else "__") + t["unit"]:>5}{plan}</code>')
    return out


def counts(day=None):
    sts = [status(it, day) for it in daily_tasks()]
    return len(sts), sts.count(DONE), sts.count(DOING)


# ---------------------------------------------------------------- the dashboard
def task_line(it, time_=''):
    t = it.get('target', it)
    return f'<code>{box(status(t))} {t["code"]:>3}  {time_}</code>{esc(label(t))}'


def section(g):
    k = g.get('kind')
    head = f'<b>{g["num"]}. {esc(g["title"])}</b>' if g.get('num') else f'<b>{esc(g["title"])}</b>'
    if k in ('priorities', 'checklist'):
        if g.get('weekly'):
            ws, we = week_range()
            head += f' ({ws:%d %b} - {we:%d %b})'
        return [head] + [task_line(it) for it in tasks(g)]
    if k == 'notes':
        return [head] + [f'{esc(f["label"])}: {esc(note(f["key"]) or "-")}' for f in g['fields']]
    if k == 'list':
        got = notes_list(g['key'])
        rows = [f'{i + 1}. {esc(x)}' for i, x in enumerate(got)]
        rows += [f'{i + 1}. -' for i in range(len(got), g.get('slots', 3))]
        return [head] + rows
    if k == 'progress':
        total, done, doing = counts()
        pct = round(100 * done / total) if total else 0
        return [head, f'<code>Total tasks:  {total:>3}</code>', f'<code>Completed:    {done:>3}</code>',
                f'<code>In progress:  {doing:>3}</code>', f'<code>Pending:      {total - done - doing:>3}</code>',
                f'<code>Completion:   {pct:>3}%</code>']
    if k == 'schedule':
        out = [head]
        for sec in g['sections']:
            out.append(f'<i>{esc(sec["title"])} ({esc(sec["range"])})</i>')
            out += [task_line(it, it.get('time', '') + '  ') for it in g['items'] if it.get('section') == sec['id']]
        if g.get('tracking'):
            out += ['<i>Time tracking</i>'] + track_lines(today_iso())
        return out
    return [head]


def dashboard(greet=False):
    d = todo()
    t = now()
    out = []
    if greet:
        out += ['<b>Good morning. It is 5:00.</b> Get up, then write <code>done T1</code>.', '']
    out += [f'<b>{esc(d.get("title", "Daily dashboard")).upper()}</b>', LINE,
            f'Date: {t:%A %d %B %Y}', f'Daily goal: {esc(note("goal") or d.get("goal", "-"))}']
    for g in groups():
        out += ['', *section(g)]
    out += ['', LINE, '<b>HOW TO USE</b>  (write in this group)',
            '<code>done W1 L2</code>  tick   <code>doing W1</code>  in progress   <code>undo W1</code>',
            '<code>p1 Finish login API</code>   set a priority',
            '<code>win Shipped the fix</code>   add an achievement',
            '<code>follow</code> <code>waiting</code> <code>review</code> <code>issue</code> <code>reason</code> <code>next</code> + text',
            '<code>well</code> <code>improve</code> <code>tomorrow</code> + text   end-of-day review',
            '<code>work 8</code> <code>learn 2</code> <code>deep 4</code> <code>focus 8</code>   time tracking']
    if d.get('footer'):
        out += [LINE] + [f'<b>{esc(x)}</b>' for x in d['footer']]
    text = '\n'.join(out)
    if len(text) > 4000:  # Telegram's limit is 4096: drop the how-to block first
        i = out.index('<b>HOW TO USE</b>  (write in this group)')
        out = out[:i] + ['Write /help to see how to use the bot.'] + out[i + 7:]
        text = '\n'.join(out)
    kb, row = [], []
    for g in groups():
        if g.get('kind') in ('priorities', 'checklist', 'schedule'):
            done = sum(status(it) == DONE for it in tasks(g))
            row.append({'text': f'{g.get("num", "")} {g["title"].title()} {done}/{len(tasks(g))}'.strip(), 'callback_data': f'g:{g["id"]}'})
            if len(row) == 2:
                kb.append(row)
                row = []
    if row:
        kb.append(row)
    kb.append([{'text': 'Today', 'callback_data': 'r:today'}, {'text': 'Week', 'callback_data': 'r:week'},
               {'text': 'Month', 'callback_data': 'r:month'}, {'text': 'Year', 'callback_data': 'r:year'}])
    kb.append([{'text': 'Refresh', 'callback_data': 'home'}, {'text': 'History', 'callback_data': 'h'}, {'text': 'Website', 'url': SITE_URL}])
    return text[:4096], {'inline_keyboard': kb}


def group_view(gid):
    g = group(gid)
    if not g or not tasks(g):
        return dashboard()
    out = [f'<b>{esc(g["title"])}</b>', f'<i>{esc(g.get("km", ""))}</i>', '']
    for it in g.get('items', []):
        t = it.get('target', it)
        tm = (it.get('time', '') + '  ') if it.get('time') else ''
        out += [f'<code>{box(status(t))} {t["code"]:>3}  {tm}</code><b>{esc(label(t))}</b>', esc(t['en']), f'<i>{esc(t["km"])}</i>', '']
    out.append('Tap to tick. Tap again to mark in progress, then again to clear.')
    kb = []
    for it in tasks(g):
        kb.append([{'text': f'{box(status(it))} {it["code"]}  {short(label(it), 34)}', 'callback_data': f't:{it["id"]}:{gid}'}])
    kb.append([{'text': 'Back to dashboard', 'callback_data': 'home'}])
    return '\n'.join(out), {'inline_keyboard': kb}


def review_prompt():
    g = next((g for g in groups() if g['id'] == 'review'), None)
    out = ['<b>END OF THE DAY</b>', '', 'Before you sleep, write your review:']
    if g:
        out += [f'<code>{f["key"]}</code> {esc(f["label"])}' for f in g['fields']]
    out += ['', 'And your hours: <code>work 8</code> <code>learn 2</code> <code>deep 4</code> <code>focus 8</code>']
    total, done, doing = counts()
    out += ['', f'Today so far: {done} of {total} tasks done.']
    return '\n'.join(out), {'inline_keyboard': [[{'text': 'Open dashboard', 'callback_data': 'home'}]]}


# ---------------------------------------------------------------- reports
def span(kind):
    t = now().date()
    if kind == 'today':
        return t, t, f'TODAY  {t:%A %d %B}'
    if kind == 'week':
        s, e = week_range(t)
        return s, t, f'THIS WEEK  {s:%d %b} - {e:%d %b}'
    if kind == 'month':
        return t.replace(day=1), t, f'THIS MONTH  {t:%B %Y}'
    return t.replace(month=1, day=1), t, f'THIS YEAR  {t:%Y}'


def report_view(kind):
    start, end, title = span(kind)
    rows = db.execute('SELECT item, at FROM state WHERE done=1 AND substr(at,1,10) BETWEEN ? AND ?',
                      (start.isoformat(), end.isoformat())).fetchall()
    first = db.execute("SELECT v FROM meta WHERE k='since'").fetchone()
    since = max(start, dt.date.fromisoformat(first[0])) if first else start
    days = (end - since).days + 1
    per_day, cnt = {}, {}
    for item, at in rows:
        per_day[at[:10]] = per_day.get(at[:10], 0) + 1
        cnt[item] = cnt.get(item, 0) + 1
    daily_ids = {it['id'] for it in daily_tasks()}
    daily_done = sum(c for i, c in cnt.items() if i in daily_ids)
    possible = days * len(daily_ids)
    active = {r[0] for r in db.execute('SELECT DISTINCT substr(at,1,10) FROM state WHERE done=1')}
    streak, d = 0, end if end.isoformat() in active else end - dt.timedelta(days=1)
    while d.isoformat() in active:
        streak += 1
        d -= dt.timedelta(days=1)
    pct = round(100 * daily_done / possible) if possible else 0
    lines = [f'<b>{title}</b>', LINE,
             f'<code>Tasks done     {len(rows)}</code>',
             f'<code>Completion     {daily_done} of {possible} ({pct}%)</code>',
             f'<code>Active days    {len(per_day)} of {days}</code>',
             f'<code>Streak         {streak} day{"s" if streak != 1 else ""}</code>']
    if kind in ('month', 'year') and per_day:
        best = max(per_day.items(), key=lambda x: x[1])
        lines.append(f'<code>Best day       {dt.date.fromisoformat(best[0]):%a %d %b} ({best[1]})</code>')
    tr = {k: (s, a, n) for k, s, a, n in db.execute(
        'SELECT key, SUM(value), AVG(value), COUNT(*) FROM track WHERE day BETWEEN ? AND ? GROUP BY key', (start.isoformat(), end.isoformat()))}
    if tr:
        lines += ['', '<b>Time tracking</b>']
        for t in tracking():
            if t['key'] in tr:
                s, a, n = tr[t['key']]
                lines.append(f'<code>{t["label"]:<16} ' + (f'average {a:.1f}/10' if t['unit'] == '/10' else f'{num(round(s, 1))}h, {a:.1f}h a day') + '</code>')
    if kind == 'week':
        lines += ['', '<b>Week goals</b>'] + [f'<code>{box(status(it))} {it["code"]:>3}</code>  {esc(label(it))}' for it in weekly_tasks()]
    if kind == 'month' and per_day:
        lines += ['', '<b>Tasks per week</b>']
        d = start
        while d <= end:
            ws, we = week_range(d)
            a, b = max(ws, start), min(we, end)
            lines.append(f'<code>{a:%d %b} - {b:%d %b}   {sum(v for k, v in per_day.items() if a.isoformat() <= k <= b.isoformat())}</code>')
            d = we + dt.timedelta(days=1)
    if kind == 'year' and per_day:
        lines += ['', '<b>Tasks per month</b>'] + [
            f'<code>{dt.date(end.year, m, 1):%B}  {sum(v for k, v in per_day.items() if int(k[5:7]) == m)}</code>' for m in range(1, end.month + 1)]
    wins = db.execute("SELECT day, text FROM notes WHERE key='win' AND day BETWEEN ? AND ? ORDER BY day, idx", (start.isoformat(), end.isoformat())).fetchall()
    if wins:
        lines += ['', '<b>Achievements</b>'] + [f'{dt.date.fromisoformat(d_):%d %b}  {esc(x)}' for d_, x in wins[-15:]]
    lines += ['', '<b>What you finished</b>']
    if not rows:
        lines.append('Nothing yet. Write <code>done T1</code> when you finish a task.')
    for g in groups():
        got = [(it, cnt[it['id']]) for it in tasks(g) if it['id'] in cnt]
        if got:
            lines.append(f'{esc(g["title"].title())}:')
            lines += [f'<code>  {it["code"]:>3}</code>  {esc(short(label(it), 44))}' + (f'  ({c} times)' if c > 1 else '') for it, c in got]
    kb = {'inline_keyboard': [[{'text': ('> ' if k == kind else '') + lab, 'callback_data': f'r:{k}'} for k, lab in
                               (('today', 'Today'), ('week', 'Week'), ('month', 'Month'), ('year', 'Year'))],
                              [{'text': 'Back to dashboard', 'callback_data': 'home'}, {'text': 'History', 'callback_data': 'h'}]]}
    return '\n'.join(lines), kb


def history_view():
    today = now().date()
    ids = [it['id'] for it in daily_tasks()]
    lines = ['<b>HISTORY</b>', LINE, '<b>Last 14 days</b>  (done of all tasks)']
    for i in range(14):
        day = today - dt.timedelta(days=i)
        n = db.execute(f'SELECT COUNT(*) FROM state WHERE period=? AND done=1 AND item IN ({",".join("?" * len(ids))})',
                       [day.isoformat(), *ids]).fetchone()[0]
        w = notes_list('win', day.isoformat())
        lines.append(f'<code>{day:%a %d %b}  {n:>2}/{len(ids)}  {round(100 * n / len(ids)) if ids else 0:>3}%</code>' + (f'  win: {esc(short(w[0], 30))}' if w else ''))
    lines += ['', '<b>Week goals, last 6 weeks</b>']
    for i in range(6):
        day = today - dt.timedelta(weeks=i)
        ws, _ = week_range(day)
        n = sum(status(it, day) == DONE for it in weekly_tasks())
        lines.append(f'<code>Week of {ws:%d %b}  {n}/{len(weekly_tasks())}</code>')
    first = db.execute('SELECT MIN(at), COUNT(*) FROM events WHERE done=1').fetchone()
    if first[0]:
        lines += ['', f'{first[1]} ticks since {first[0][:10]}.']
    return '\n'.join(lines), {'inline_keyboard': [[{'text': 'Back to dashboard', 'callback_data': 'home'}, {'text': 'Latest ticks', 'callback_data': 'log'}]]}


def log_view(n=25):
    rows = db.execute('SELECT at, item, done, by FROM events ORDER BY at DESC LIMIT ?', (n,)).fetchall()
    lines = [f'<b>LATEST {len(rows)} TICKS</b>', LINE]
    items = todo()['_items']
    for at, item, done, by in rows:
        it = items.get(item)
        word = {DONE: 'done ', DOING: 'doing'}.get(done, 'undo ')
        lines.append(f'<code>{at[5:16].replace("T", " ")}  {word}</code>  {esc(short(label(it), 36) if it else item)}  ({esc(by)})')
    if not rows:
        lines.append('Nothing yet.')
    return '\n'.join(lines), {'inline_keyboard': [[{'text': 'Back to dashboard', 'callback_data': 'home'}, {'text': 'History', 'callback_data': 'h'}]]}


def view(name):
    if name == 'home':
        return dashboard()
    if name == 'h':
        return history_view()
    if name == 'log':
        return log_view()
    if name.startswith('r:'):
        return report_view(name[2:])
    return group_view(name)


# ---------------------------------------------------------------- sending and commands
def say(text, kb=None, reply_to=None):
    p = dict(chat_id=CHAT, text=text, parse_mode='HTML', disable_web_page_preview=True)
    if kb:
        p['reply_markup'] = kb
    if reply_to:
        p['reply_to_message_id'] = reply_to
    return api('sendMessage', **p)


def send_home(greet=False):
    text, kb = dashboard(greet)
    return say(text, kb)


HELP = '\n'.join([
    '<b>HOW TO USE THIS BOT</b>', LINE,
    'Every morning at 5:00 I send your dashboard. At {evening} I remind you to write your review.', '',
    '<b>Tasks</b>  (codes: P1-P3, W1-W6, L1-L6, J1-J4, T1-T10, A1-A4)',
    '<code>done W1 L2</code>  tick',
    '<code>doing W1</code>  mark in progress',
    '<code>undo W1</code>  untick', '',
    '<b>Write things down</b>',
    '<code>p1 Finish login API</code>  set priority 1 (also p2, p3)',
    '<code>goal Ship the payment fix</code>  daily goal',
    '<code>win Shipped the payment fix</code>  add an achievement',
    '<code>follow</code> <code>waiting</code> <code>review</code>  follow-up and pending',
    '<code>issue</code> <code>reason</code> <code>next</code>  blockers',
    '<code>well</code> <code>improve</code> <code>tomorrow</code>  end-of-day review',
    '<code>clear win</code>  remove what you wrote today', '',
    '<b>Time tracking</b>',
    '<code>work 7.5</code>  <code>learn 1.5</code>  <code>deep 4</code>  <code>focus 8</code>', '',
    '<b>See your progress</b>',
    '/todo  the dashboard', '/today  /week  /month  /year  what you finished',
    '/history  the last 14 days', '/log  the latest ticks'])


def mark(codes, value, who, reply_to):
    ok, same, bad = [], [], []
    for c in codes:
        it = by_code(c)
        if not it:
            bad.append(c)
        elif set_status(it, value, who):
            ok.append(it)
        else:
            same.append(it)
    word = {DONE: 'Done', DOING: 'In progress', 0: 'Undone'}[value]
    lines = []
    if ok:
        lines.append(f'<b>{word}</b> ({esc(who)})')
        lines += [f'<code>{it["code"]:>3}</code>  {esc(label(it))}' for it in ok]
    if same:
        lines.append('No change: ' + ', '.join(it['code'] for it in same))
    if bad:
        lines.append('I do not know: ' + ', '.join(esc(b) for b in bad) + '. Codes look like P1, W1, L1, J1, T1, A1.')
    if ok:
        total, done, doing = counts()
        lines += ['', f'Today: {done} of {total} done, {doing} in progress ({round(100 * done / total) if total else 0}%).']
    say('\n'.join(lines) or 'Nothing to change.', reply_to=reply_to)


def set_track(key, raw, who, reply_to):
    t = next(t for t in tracking() if t['key'] == key)
    try:
        v = float(raw.replace(',', '.').rstrip('h'))
    except ValueError:
        return say(f'Write a number, for example <code>{key} 7.5</code>.', reply_to=reply_to)
    if not 0 <= v <= (10 if t['unit'] == '/10' else 24):
        return say('Focus is 0 to 10. Hours are 0 to 24.', reply_to=reply_to)
    db.execute('INSERT OR REPLACE INTO track VALUES (?,?,?,?,?)', (today_iso(), key, v, who, now().isoformat(timespec='seconds')))
    db.commit()
    say('<b>Saved for today</b>\n' + '\n'.join(track_lines(today_iso())), reply_to=reply_to)


CODE = re.compile(r'^(?:\d{1,2}|[A-Za-z]\d{1,2})[.,]?$')


def handle_text(m):
    text = (m.get('text') or '').strip()
    if not text:
        return
    who = m['from'].get('first_name') or m['from'].get('username') or 'someone'
    mid = m['message_id']
    words = text.split()
    head = words[0].split('@')[0].lower().lstrip('/')
    rest = words[1:]
    body = text.split(None, 1)[1].strip() if len(words) > 1 else ''
    to_bot = (m.get('reply_to_message') or {}).get('from', {}).get('is_bot')
    if head in ('done', 'doing', 'undo'):
        value = {'done': DONE, 'doing': DOING, 'undo': 0}[head]
        return mark(rest, value, who, mid) if rest else say(f'Which task? For example <code>{head} W1</code>.', reply_to=mid)
    if head in ('p1', 'p2', 'p3', 'goal'):
        if not body:
            return say(f'Write the text too, for example <code>{head} Finish the login API</code>.', reply_to=mid)
        set_note(head, body, who)
        return say(f'<b>Saved</b>  {"Priority " + head[1] if head != "goal" else "Daily goal"}: {esc(body)}', reply_to=mid)
    if head in note_fields():
        if not body:
            return say(f'Write the text too, for example <code>{head} ...</code>', reply_to=mid)
        set_note(head, body, who)
        return say(f'<b>Saved</b>  {esc(note_fields()[head]["label"])}: {esc(body)}', reply_to=mid)
    if head in list_keys():
        if not body:
            return say(f'Write the text too, for example <code>{head} Shipped the payment fix</code>.', reply_to=mid)
        set_note(head, body, who, append=True)
        got = notes_list(head)
        return say('<b>Achievements today</b>\n' + '\n'.join(f'{i + 1}. {esc(x)}' for i, x in enumerate(got)), reply_to=mid)
    if head == 'clear':
        key = (rest[0].lower() if rest else '')
        n = clear_note(key) if key else 0
        return say(f'Cleared {key} for today.' if n else 'Nothing to clear. For example <code>clear win</code>.', reply_to=mid)
    if head in [t['key'] for t in tracking()]:
        return set_track(head, rest[0], who, mid) if rest else say(f'Write a number, for example <code>{head} 7.5</code>.', reply_to=mid)
    if to_bot and all(CODE.match(w) for w in words):  # a reply to the bot with just codes
        return mark(words, DONE, who, mid)
    if head in ('todo', 'start', 'list', 'dashboard'):
        return send_home()
    if head in ('today', 'week', 'month', 'year'):
        t, kb = report_view(head)
        return say(t, kb)
    if head == 'history':
        t, kb = history_view()
        return say(t, kb)
    if head == 'log':
        t, kb = log_view()
        return say(t, kb)
    if head == 'help':
        return say(HELP.format(evening=EVENING))


def handle(u):
    if 'callback_query' in u:
        q = u['callback_query']
        msg = q.get('message') or {}
        if msg.get('chat', {}).get('id') != CHAT:
            return api('answerCallbackQuery', callback_query_id=q['id'], text='This bot only works in its group.')
        who = q['from'].get('first_name') or q['from'].get('username') or 'someone'
        data = q.get('data', '')
        note_ = ''
        target = data
        if data.startswith('t:'):
            _, item, target = data.split(':', 2)
            it = todo()['_items'].get(item)
            if it:
                nxt = {0: DONE, DONE: DOING, DOING: 0}[status(it)]  # tap: done, tap: in progress, tap: clear
                set_status(it, nxt, who)
                note_ = {DONE: 'Done: ', DOING: 'In progress: ', 0: 'Cleared: '}[nxt] + short(label(it), 50)
        elif data.startswith('g:'):
            target = data[2:]
        text, kb = view(target)
        api('editMessageText', chat_id=CHAT, message_id=msg['message_id'], text=text, parse_mode='HTML', reply_markup=kb, disable_web_page_preview=True)
        return api('answerCallbackQuery', callback_query_id=q['id'], text=note_)
    m = u.get('message') or {}
    if m.get('chat', {}).get('id') == CHAT:
        handle_text(m)


def due(key, hour, minute=0):
    t = now()
    last = db.execute('SELECT v FROM meta WHERE k=?', (key,)).fetchone()
    if (t.hour, t.minute) >= (hour, minute) and (not last or last[0] != t.date().isoformat()):
        db.execute('INSERT OR REPLACE INTO meta VALUES (?, ?)', (key, t.date().isoformat()))
        db.commit()
        return True
    return False


def main():
    if '--once' in sys.argv:
        r = send_home()
        print('sent' if r.get('ok') else r)
        return
    api('setMyCommands', commands=[
        {'command': 'todo', 'description': "Today's dashboard"},
        {'command': 'done', 'description': 'Tick tasks, e.g. /done W1 L2'},
        {'command': 'doing', 'description': 'Mark in progress, e.g. /doing W1'},
        {'command': 'undo', 'description': 'Untick, e.g. /undo W1'},
        {'command': 'win', 'description': 'Add an achievement'},
        {'command': 'today', 'description': 'What I finished today'},
        {'command': 'week', 'description': 'What I finished this week'},
        {'command': 'month', 'description': 'What I finished this month'},
        {'command': 'year', 'description': 'What I finished this year'},
        {'command': 'history', 'description': 'The last 14 days'},
        {'command': 'help', 'description': 'How this bot works'}])
    db.execute("INSERT OR IGNORE INTO meta VALUES ('since', ?)", (today_iso(),))
    db.commit()
    eh, em = (int(x) for x in EVENING.split(':'))
    offset = int((db.execute("SELECT v FROM meta WHERE k='offset'").fetchone() or ['0'])[0])
    log('bot running for chat', CHAT, f'dashboard at {MORNING}:00, review at {EVENING}')
    while True:
        try:
            if due('morning', MORNING):
                send_home(greet=True)
            if due('evening', eh, em):
                t, kb = review_prompt()
                say(t, kb)
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
