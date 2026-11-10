# -*- coding: utf-8 -*-
"""Fill a unit's missing audio with a native neural voice in the unit's language (edge-tts, free, no key).

    python tools/gen_audio.py korean-funeral-visit [--voice ko-KR-SunHiNeural]

The voice comes from the study language (tools/sitecfg.py LANGS, unit.json "lang" or site.json "lang");
--voice or unit.json "voice" overrides it.

Gives every vocab word an audio path, fills the Full text from the cards when it is empty, then
synthesises every referenced clip that does not exist yet. Safe to re-run: existing files are kept.
"""
import asyncio
import io
import json
import os
import sys

import edge_tts

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sitecfg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    slug = sys.argv[1]
    d = os.path.join(ROOT, slug)
    path = os.path.join(d, 'unit.json')
    u = json.load(io.open(path, encoding='utf-8'))
    voice = sys.argv[sys.argv.index('--voice') + 1] if '--voice' in sys.argv else (sitecfg.lang_of(u)['voice'] or 'ko-KR-InJoonNeural')

    u.setdefault('full', [])
    jobs = []
    for c in u['cards']:
        jobs.append((c['ko'], c['audio']))
    for b in u['qa']:
        for it in b['items']:
            if b.get('kind') == 'surv':
                jobs.append((it['ko'], it['audio']))
            else:
                if it.get('qaudio'):
                    jobs.append((it['q'], it['qaudio']))
                if it.get('audio'):
                    jobs.append((it['a'], it['audio']))
    n = 0
    for g in u['vocab']:
        for it in g['items']:
            n += 1
            it.setdefault('audio', 'audio/v%02d.mp3' % n)
            jobs.append((it['ko'], it['audio']))
    if not u.get('full'):
        secs = {s['id']: s for s in u['sections']}
        for s in u['sections']:
            cs = [c for c in u['cards'] if c['sec'] == s['id']]
            if cs:
                u['full'].append({'title': f'{s["ko"]} · {s["en"]}', 'ko': ' '.join(c['ko'] for c in cs),
                                  'en': ' '.join(c['en'] for c in cs)})
    io.open(path, 'w', encoding='utf-8', newline='\n').write(json.dumps(u, ensure_ascii=False, indent=1))

    todo = [(t, os.path.join(d, a)) for t, a in jobs
            if not (os.path.exists(os.path.join(d, a)) and os.path.getsize(os.path.join(d, a)) > 1000)]

    # Korean quote marks are dropped; in English an apostrophe is part of the word ("I'm").
    keep_apostrophe = sitecfg.lang_of(u)['code'] != 'ko'

    async def run():
        sem = asyncio.Semaphore(2)

        async def one(text, out):
            async with sem:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                said = text if keep_apostrophe else text.replace("'", '')
                for attempt in range(8):  # the free voice service drops some requests; try again
                    try:  # a request that never answers must not hang the whole run: 60 s per clip, then retry
                        await asyncio.wait_for(edge_tts.Communicate(said, voice, rate='-5%').save(out), timeout=60)
                        return
                    except (edge_tts.exceptions.NoAudioReceived, asyncio.TimeoutError):
                        await asyncio.sleep(1.5 * (attempt + 1))
                raise RuntimeError(f'no audio after 8 tries: {text!r}')
        await asyncio.gather(*(one(t, o) for t, o in todo))

    asyncio.run(run())
    print(f'{slug}: {len(jobs)} clips referenced, {len(todo)} generated with {voice}')


if __name__ == '__main__':
    main()
