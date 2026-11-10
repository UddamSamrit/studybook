# -*- coding: utf-8 -*-
"""Korean to Lyric: Hangul in English letters, written the way K-pop lyric sites and YouTube lyric
videos write it (ColorCodedLyrics style), so someone who cannot read Hangul can sing it out loud.
Standard library only.

    from romanize import romanize
    romanize('감사합니다')  # 'gamsahamnida'

The rules (see skill/korean-lyric/SKILL.md):
- word spacing as in the Hangul, particles stay on the word: 우리를 urireul
- all lowercase, punctuation and Latin words kept
- spelled as spoken: linking (먹어요 meogeoyo), nasal sounds (합니다 hamnida), ㄹ sounds (연락 yeollak),
  ㅎ (좋아요 joayo, 좋다 jota), 같이 gachi; tensing is not written (먹고 meokgo)
- ㅅ/ㅆ before an i or y sound is sh/ssh (시 shi, 씨 sshi, 쉬 shwi); ㅝ weo; ㅚ and ㅞ we
- 의 is ui at the start of a word, e as the particle, i after a consonant (희망 himang)
Spoken forms a rule cannot see, such as 맛없다 or ㄴ added between words in a compound, are listed
in SPOKEN. Numbers read with Sino-Korean counters are written out. Other text is left as it is.
"""
import re

CHO = ['g', 'kk', 'n', 'd', 'tt', 'r', 'm', 'b', 'pp', 's', 'ss', '', 'j', 'jj', 'ch', 'k', 't', 'p', 'h']
JUNG = ['a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'we', 'yo', 'u', 'weo', 'we', 'wi', 'yu', 'eu', 'ui', 'i']
JONG = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# The sound a final consonant has when no vowel follows.
CODA = {'': '', 'ㄱ': 'k', 'ㄲ': 'k', 'ㄳ': 'k', 'ㅋ': 'k', 'ㄺ': 'k', 'ㄴ': 'n', 'ㄵ': 'n', 'ㄶ': 'n', 'ㄷ': 't', 'ㅅ': 't',
        'ㅆ': 't', 'ㅈ': 't', 'ㅊ': 't', 'ㅌ': 't', 'ㅎ': 't', 'ㄹ': 'l', 'ㄼ': 'l', 'ㄽ': 'l', 'ㄾ': 'l', 'ㅀ': 'l',
        'ㅁ': 'm', 'ㄻ': 'm', 'ㅂ': 'p', 'ㅍ': 'p', 'ㅄ': 'p', 'ㄿ': 'p', 'ㅇ': 'ng'}

# Before a vowel the final moves to the next syllable: (what stays, what moves).
LINK = {'ㄱ': ('', 'g'), 'ㄲ': ('', 'kk'), 'ㄳ': ('k', 's'), 'ㄴ': ('', 'n'), 'ㄵ': ('n', 'j'), 'ㄶ': ('', 'n'), 'ㄷ': ('', 'd'),
        'ㄹ': ('', 'r'), 'ㄺ': ('l', 'g'), 'ㄻ': ('l', 'm'), 'ㄼ': ('l', 'b'), 'ㄽ': ('l', 's'), 'ㄾ': ('l', 't'), 'ㄿ': ('l', 'p'),
        'ㅀ': ('', 'r'), 'ㅁ': ('', 'm'), 'ㅂ': ('', 'b'), 'ㅄ': ('p', 's'), 'ㅅ': ('', 's'), 'ㅆ': ('', 'ss'), 'ㅈ': ('', 'j'),
        'ㅊ': ('', 'ch'), 'ㅋ': ('', 'k'), 'ㅌ': ('', 't'), 'ㅍ': ('', 'p'), 'ㅎ': ('', '')}

# Spelling to spoken form, for what the rules below cannot work out from the letters.
# Longer entries win. Add to this list when a word reads wrong.
SPOKEN = {
    '맛없': '마덦', '멋없': '머덦',
    '거의': '거이', '부의': '부이', '회의': '회이', '주의': '주이', '예의': '예이', '강의': '강이',
    '한국요리': '한궁뇨리',
    '삼러꺼꼬': 'samlor kkeokko',
}

# A consonant written alone, as in grammar notes: -(으)ㄴ 후에.
JAMO = {'ㄱ': 'g', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄹ': 'l', 'ㅁ': 'm', 'ㅂ': 'b', 'ㅅ': 's', 'ㅇ': 'ng', 'ㅈ': 'j', 'ㅊ': 'ch',
        'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h', 'ㄲ': 'kk', 'ㄸ': 'tt', 'ㅃ': 'pp', 'ㅆ': 'ss', 'ㅉ': 'jj'}

UNITS = ['', '십', '백', '천']
DIGITS = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구']
COUNTERS = '년도회만팀월일분원번째층살'
NATIVE_COUNTERS = '살번째'  # read with native numbers, so left as digits


def _sino(n):
    """12 -> 십이, 2026 -> 이천이십육 (0 < n < 10000)."""
    out = ''
    for i, ch in enumerate(reversed(str(n))):
        d = int(ch)
        if d:
            out = ('' if d == 1 and i else DIGITS[d]) + UNITS[i] + out
    return out


def _numbers(s):
    def sub(m):
        n = int(m.group(1))
        if not 0 < n < 10000 or m.group(2) in NATIVE_COUNTERS:
            return m.group(0)
        return _sino(n) + m.group(2)
    return re.sub(r'(?<![\d.,])(\d+)\s*([' + COUNTERS + '])', sub, s)


def _split(word):
    out = []
    for ch in word:
        c = ord(ch) - 0xAC00
        out.append((c // 588, (c % 588) // 28, c % 28))
    return out


def _word(word):
    syl = _split(word)
    res = []
    carry = None  # the onset the previous syllable decided for this one
    for i, (cho, jung, jong) in enumerate(syl):
        onset = carry if carry is not None else CHO[cho]
        carry = None
        vowel = JUNG[jung]
        if jung == 19:  # ㅢ
            if cho != 11:
                vowel = 'i'  # 희망 himang
            elif i and i == len(syl) - 1:
                vowel = 'e'  # 우리의 urie
        final = JONG[jong]
        coda = CODA[final]
        if i + 1 < len(syl) and final:
            ncho, njung, _ = syl[i + 1]
            coda, carry = _join(final, ncho, njung)
        if onset in ('s', 'ss') and (vowel[0] in 'iy' or vowel == 'wi'):
            onset += 'h'  # 시 shi, 셔 shyeo, 씨 sshi, 쉬 shwi
        res.append(onset + vowel + coda)
    return ''.join(res)


def _join(final, ncho, njung):
    """What one final and the next initial sound like together: (coda, next onset)."""
    nxt = CHO[ncho]
    if ncho == 11:  # the next syllable starts with a vowel
        if final == 'ㅇ':
            return 'ng', ''
        if njung == 20 and final in ('ㄷ', 'ㅌ', 'ㄾ'):  # 굳이 guji, 같이 gachi, 핥이 halchi
            return ('l' if final == 'ㄾ' else ''), ('j' if final == 'ㄷ' else 'ch')
        return LINK[final]
    if final in ('ㅎ', 'ㄶ', 'ㅀ'):
        base = {'ㅎ': '', 'ㄶ': 'n', 'ㅀ': 'l'}[final]
        if ncho in (0, 3, 12):  # 좋다 jota, 많고 manko, 좋지 jochi
            return base, {0: 'k', 3: 't', 12: 'ch'}[ncho]
        if ncho == 9:  # 좋습니다 joseumnida
            return base, 's'
        if ncho == 2:  # 좋네 jonne, 많네 manne, 싫네 sille
            return ('l', 'l') if final == 'ㅀ' else ('n', 'n')
    coda = CODA[final]
    if ncho == 18 and coda in ('k', 't', 'p'):  # 축하 chuka, 못해 motae, 입학 ipak
        if coda == 't' and njung == 20:
            return '', 'ch'  # 닫히 dachi
        return '', {'k': 'k', 't': 't', 'p': 'p'}[coda]
    if ncho in (2, 6):  # next is ㄴ or ㅁ: 먹는 meongneun, 있는 inneun, 합니다 hamnida
        if coda in ('k', 't', 'p'):
            coda = {'k': 'ng', 't': 'n', 'p': 'm'}[coda]
        elif coda == 'l' and ncho == 2:  # 설날 seollal
            return 'l', 'l'
        return coda, nxt
    if ncho == 5:  # next is ㄹ
        if coda in ('n', 'l'):  # 연락 yeollak
            return 'l', 'l'
        if coda in ('m', 'ng'):  # 음료 eumnyo, 정리 jeongni
            return coda, 'n'
        return {'k': 'ng', 't': 'n', 'p': 'm'}[coda], 'n'  # 독립 dongnip
    return coda, nxt


def _across_space(s):
    # 못 먹어요 sounds like 몬 머거요.
    def sub(m):
        return '몬 ' + m.group(1)
    return re.sub(r'(?<![가-힣])못 ([나-닣마-밓])', sub, s)


_KEYS = sorted(SPOKEN, key=len, reverse=True)


def romanize(text):
    """Every Hangul run in text, in English letters. Everything else stays as it is."""
    if not text or not re.search('[가-힣ㄱ-ㅎ]', text):
        return text or ''
    s = _across_space(_numbers(text))
    s = re.sub('([가-힣]):([가-힣])', r'\1\2', s)  # the long-vowel mark in [놀:라다]
    for k in _KEYS:
        s = s.replace(k, SPOKEN[k])
    # Latin right before Hangul keeps a hyphen, so AI를 reads AI-reul
    s = re.sub('([A-Za-z])(?=[가-힣])', r'\1-', s)
    s = re.sub('[가-힣]+', lambda m: _word(m.group(0)), s)
    s = re.sub('[ㄱ-ㅎ]', lambda m: JAMO.get(m.group(0), m.group(0)), s)
    return s  # all lowercase, as on lyric sites
