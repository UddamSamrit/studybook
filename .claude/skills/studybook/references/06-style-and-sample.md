# 06 · Style and the live sample

**Current system (2026-11-05): Seoul Metro wayfinding.** The homepage is a subway line, each unit a
station; inside a unit the sections are transfer lines in Seoul line colours. Tokens live in
`assets/line.css`, unit components in `assets/unit.css`, rules in `templates/DESIGN.example.md`.
One family, Gothic A1, for Korean and English. Light and dark follow the system. Phone first (390px).

Do not bring back the old look below (cream paper, serif, terracotta): it was replaced on purpose.

---

Older notes, kept for history:

# 06 · Style template and the live sample

Keep every studybook recognizably one family. Read the sample, then match it.

## The live sample (read it first)
- Hub: **https://1l3oth.github.io/studybook/**
- A unit: **https://1l3oth.github.io/studybook/korean-summer-speech/**
- Feed (full text of every unit): **https://1l3oth.github.io/studybook/feed.xml**

Fetch these to see the exact structure and copy it. The feed is the fastest way for an AI to read a
whole unit's content.

## Visual language
- **Warm study-notebook palette.** Paper/cream ground, soft ink text, one warm accent (terracotta),
  a muted secondary (teal). Define the full light palette as CSS tokens on `:root`; redefine only the
  changed tokens under `@media (prefers-color-scheme: dark)` and `[data-theme]`. Paint `body`
  background explicitly.
- **Hub texture:** a subtle dot-grid ("graph paper") background via a `radial-gradient` tile.
- **Type:** a serif with strong CJK/Latin coverage for titles and target-language lines (the sample
  uses **Hahmlet**); a clean sans for UI (**IBM Plex Sans**); optionally a handwriting face for one
  accent line (**Gaegu**). Google Fonts only, always with real fallback stacks.
- **Hub unit card:** a numbered "Unit NN", the title (target language), a one-line description, a
  small table of contents of the four tabs with a colored dot each, and an Open link. A colored left
  spine ties the card to the tab colors.
- **Unit page:** in-page tab bar (single row, horizontally scrollable on narrow screens, not
  wrapping), image-left cards, the fixed bottom control bar, and the same accent/tokens as the hub.

## Responsive + accessible
- Single column on phones; the tab bar scrolls rather than wraps; wide content (tables, the full
  document) scrolls inside its own container, never the page body.
- Respect the viewer's theme; never hard-code a single background.
- Real focus states on buttons and links.

`templates/hub_index.html` is the sample hub verbatim — adapt its title and unit cards. The unit page
CSS lives in the shared `assets/line.css` and `assets/unit.css` (see `DESIGN.example.md`); units never carry their own styles.
