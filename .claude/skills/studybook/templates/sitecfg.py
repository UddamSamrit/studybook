# -*- coding: utf-8 -*-
"""The site's own settings, shared by every builder: title, web address, study language.

They live in site.json at the site root (written by new_site.py). The web address comes from
site.json "url"; when that is empty it is worked out from the git remote
(https://github.com/<user>/<repo> -> https://<user>.github.io/<repo>/), so nobody's pages ever
point at someone else's site.
"""
import io
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Study languages. "name" is how the language writes its own name (the text switch shows it),
# "voice" is the free edge-tts neural voice used by gen_audio.py.
LANGS = {
    'ko': {'name': '한국어', 'en': 'Korean', 'voice': 'ko-KR-InJoonNeural'},
    'en': {'name': 'English', 'en': 'English', 'voice': 'en-US-AndrewNeural'},
    'ja': {'name': '日本語', 'en': 'Japanese', 'voice': 'ja-JP-KeitaNeural'},
    'zh': {'name': '中文', 'en': 'Chinese', 'voice': 'zh-CN-YunxiNeural'},
    'fr': {'name': 'Français', 'en': 'French', 'voice': 'fr-FR-HenriNeural'},
    'es': {'name': 'Español', 'en': 'Spanish', 'voice': 'es-ES-AlvaroNeural'},
    'de': {'name': 'Deutsch', 'en': 'German', 'voice': 'de-DE-ConradNeural'},
    'th': {'name': 'ไทย', 'en': 'Thai', 'voice': 'th-TH-NiwatNeural'},
    'vi': {'name': 'Tiếng Việt', 'en': 'Vietnamese', 'voice': 'vi-VN-NamMinhNeural'},
    'km': {'name': 'ខ្មែរ', 'en': 'Khmer', 'voice': 'km-KH-PisethNeural'},
}


def _git_url():
    try:
        r = subprocess.run(['git', '-C', ROOT, 'remote', 'get-url', 'origin'], capture_output=True, text=True, timeout=10)
    except Exception:
        return ''
    m = re.search(r'github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?\s*$', r.stdout or '')
    if not m:
        return ''
    user, repo = m.group(1), m.group(2)
    if repo.lower() == f'{user.lower()}.github.io':
        return f'https://{user.lower()}.github.io/'
    return f'https://{user.lower()}.github.io/{repo}/'


def load():
    p = os.path.join(ROOT, 'site.json')
    s = json.load(io.open(p, encoding='utf-8')) if os.path.exists(p) else {}
    s.setdefault('title', 'Studybook')
    s.setdefault('short', 'Studybook')
    s.setdefault('description', 'Study units: picture cards with native audio, Q&A, vocabulary and full text.')
    s.setdefault('lang', 'ko')
    s.setdefault('support', 'English')
    url = s.get('url') or _git_url()
    s['url'] = url if not url or url.endswith('/') else url + '/'
    return s


def lang_of(u, site=None):
    """The study language of one unit: unit.json "lang" (a code like "ja"), else the site's."""
    site = site or load()
    code = u.get('lang') or site.get('lang') or 'ko'
    info = dict(LANGS.get(code, {'name': code, 'en': code, 'voice': ''}))
    if site.get('voice'):
        info['voice'] = site['voice']
    if u.get('voice'):
        info['voice'] = u['voice']
    info['code'] = code
    info['support'] = u.get('support') or site.get('support') or 'English'
    return info
