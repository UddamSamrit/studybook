# 02 · Build a study unit (book page)

One unit = one folder `<slug>/` with `unit.json`, `img/`, `audio/` and the rendered `index.html`.
Never hand-write the page: write `unit.json` and run `render_unit.py`. Design rules: `DESIGN.md`.

## Any language
The field names come from the first (Korean) book, but they mean the same thing in every language:
`ko`, `q`, `a` and `title_ko` hold the **study language**; `en`, `qen`, `aen` and `title_en` hold the **translation**
(Khmer, English, whatever `site.json` "support" says). The study language is `site.json` "lang" (or
`"lang": "ja"` in one unit.json). Korean gets the Lyric line and Korean control labels; every other language
gets its own native voice (`tools/sitecfg.py` LANGS) and controls in English. Write section and group titles
as plain text for non-Korean units (no `한국어 · English` pairs). The copy rules below about 해요체 are for Korean.

## The page (rendered from unit.json)
- **Sign band** (sticky): back to the homepage, unit title, then four tabs:
  그림 카드 (cards), 예상 질문 (Q&A), 단어 (vocab), 전체 (full text). The hash (`#qa`) opens a tab.
- **한눈에 · The big picture** (`explain`, optional but recommended): eli5 style. A one-line `why`,
  then 4 to 6 tiles, each a big flat picture, a short Korean word and at most ~7 English words.
  Explain *why* things are done, not the steps the cards already teach.
- **노선도 line map** (`spine`): the unit's sections drawn as stations on a line, each in its own
  Seoul line colour, mapped onto a real sequence the learner already owns (a day, a visit).
  Tapping a station jumps to its first card; the yellow ring follows the scroll.
- **Cards**: one idea each (5 to 14). Picture, number badge ringed in the section colour, section
  chip, one-word hook, the Korean line, the English, a Listen button.
- **Dock** (fixed bottom): 집중 (focus mode), 전체 듣기 (play all), hide Korean, hide English on cards;
  show all answers on Q&A; hide either side on vocab; hide English and print on full.
- **Focus mode**: one card at a time, Korean hidden until tapped, Listen, Back/Next, swipe and arrow
  keys, progress line. It remembers the card, so the homepage can say "card 3 of 7".
- **Q&A** blocks in this order: `trap` (what the learner gets wrong or worries about, with a `why`),
  `qa` (the questions someone will really ask), `surv` (lines for when stuck). Mark any answer that
  asserts a personal fact the learner must confirm with `"check": true`.
- **Vocab** groups with a colour each; two-way hide.
- **Full**: every line, Q&A and word as one printable document; also what `feed.xml` carries.

## Copy rules
- Easy, natural 해요체 unless the material is a formal speech (then 습니다체).
- Never tell the learner to say anything aloud; write "in your head".
- Few words everywhere outside the Korean lines. A note is one sentence.

## After rendering
Run `build_stations.py` (it rewrites the homepage station list, numbers and counts from every unit.json; never edit
it by hand), then `build_feed.py`, then `build_images.py` (app icons + link covers).
Check every `img/` and `audio/` reference exists, and look at the page at 390px wide in light and dark.
