# Design

World: **Seoul Metro wayfinding.** The notebook is a subway line, each unit a station on the learner's
commute. Recorded 2026-11-05 from the built homepage (`index.html`, `assets/line.css`).
Product truth lives in PRODUCT.md; this file holds visual decisions only.

## Tokens (`assets/line.css`)

| Role | Light | Dark | Use |
|---|---|---|---|
| `--ground` | #EEF0F4 | #0E1322 | page ground (platform grey) |
| `--surface` | #FFFFFF | #18203A | station rows, panels |
| `--ink` | #16203A | #EEF1F8 | text |
| `--ink-2` | #4F5970 | #AAB3C7 | secondary text (meets 4.5:1 on ground and surface) |
| `--ink-3` | #8A93A6 | #6F7890 | strokes and dashed stops only, never small text |
| `--rule` | #D3D8E2 | #2C3654 | borders, dividers |
| `--sign` / `--on-sign` | #1C2A4A / #FFF | #0A0F1D / #FFF | the navy sign band |
| `--line` | #00A84D | #16B95E | the line stripe and station rings (decorative) |
| `--line-ink` | #00803A | #00803A | green that carries white text: badges, primary action |
| `--here` | #F5B700 | #FFC629 | "you are here" marker, focus ring, selection |
| `--notice` | #D7372B | #E5483C | NEW tag, alerts |

Radius `--r` 14px for rows and panels, 10 to 12px for buttons, 7px for badges.
Shadows are soft and offset (`--shadow`, `--shadow-up` on hover). No hard offset shadows.
Motion: `--ease-out` cubic-bezier(.16,1,.3,1); everything off under reduced motion.

## Type

One family for both scripts: **Gothic A1** (400, 500, 700, 800), a Korean signage grotesk.
Korean always `word-break: keep-all`. Scale: sign title clamp(1.75rem, 7.6vw, 2.3rem) 800;
station title 1.32rem 800; body 0.9rem; meta 0.8rem with tabular numerals.

## Components

- **Sign band**: navy, title + one line of status, install button at right (shown only when the
  browser offers install, or on iPhone where it toggles an Add to Home Screen hint).
- **Line stripe**: 8px `--line` under the sign band on every page.
- **Now-at panel**: yellow ring, state line ("Start here" / "You are here"), unit title, one
  full-width primary action (52px min height). Side-by-side at 720px and up.
- **Station row**: whole row is the link; number badge in `--line-ink`, Korean title, English line,
  counts. States: open (surface + shadow), closed / opening soon (outlined, muted), next (dashed).
- **Line and marker**: 8px vertical line at the left; white dots ringed in line green; the yellow
  marker slides to the tapped station (0.42s) before the page opens.

## Rules

- Phone first: 390px is the design width; content column max 640px; safe-area insets respected.
- Light and dark both follow the system setting.
- No eyebrow labels, gradient text, glass, emoji or unicode icons; icons are drawn SVG strokes.
- Unit pictures are flat 2D object drawings (PRODUCT.md brand commitment).

## Unit pages (`assets/unit.css`, `assets/unit.js`, rendered by `tools/render_unit.py`)

- **Sign band** is sticky and carries the four tabs; the selected tab has a yellow underline bar.
- **Section colours** are Seoul line colours set per element as `--lc`: Line 1 #0052A4, 2 #00A84D,
  3 #EF7C1C, 4 #00A5DE, 5 #996CAC, 6 #CD7C2F, opening and closing sections #6B7488. They appear as
  rings, dots and line segments, never as fills behind text.
- **Big picture tiles** (eli5): flat object in a tinted circle, short Korean word, a few English words.
- **Line map**: horizontal line of section stations; the current one gets the yellow ring.
- **Cards, phone and tablet**: a feed. Picture (16:10 on phones, 38% column from 720px) with a
  54px round play button on its corner, number badge ringed in `--lc`, section chip, hook chip,
  Korean at 1.18 to 1.45rem 700, a 4px progress line in `--lc` while it plays, English. No Listen pills.
- **Cards, desktop (960px and up)**: a platform display. Left (60%, sticky under the header): the
  stage with the selected card's picture, the full Korean (hatched when Korean is hidden; K or a click
  reveals), progress line, English, back / 64px play / next, count, and the key hints
  (Space listen, arrows move, K show Korean). Right: every line as a station row on a vertical line
  in section colours, Korean clamped to 2 lines and English to 1, a 38px play per row; the selected
  row gets a yellow ring and tint. The big picture tiles move below the platform; the line map hides.
- **Hidden text** keeps its box and shows a faint diagonal hatch, so the learner sees where the
  answer is; tap reveals one item.
- **Dock**: four equal 48px buttons, labels in Korean on phones, pressed state = navy.
- **Focus mode** (phones and tablets; desktop has the stage instead): full-screen layer, navy top bar with close, count and a progress line in section
  colours; the Korean box stays hidden until tapped; Back, Listen (primary), Next.
- Flat pictures always sit on a light tile (`#F4F6F9` tinted with `--lc`), in dark mode too, because
  the drawings use dark ink.
