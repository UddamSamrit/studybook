# 03 · Media (pictures + voice)

## Pictures: flat 2D object drawings (SVG)
- One object per card that stands for the idea: an envelope, a flower, a phone, a bowl. No people
  scenes, no photos, no image model (the learner asked for flat objects, 2026-11-05).
- Draw them in code: see `templates/draw_flat_objects.example.py`. ViewBox `0 0 160 100`,
  transparent background, the palette from DESIGN.md, the same stroke grey `#C9CED8` everywhere.
- Set `"flat": true` on the card so the page shows it contained on a light tint of the section colour.
- Render a contact sheet and look at all of them together before building the page.
- Existing raster units (old jpg pictures) keep their pictures; leave `flat` off for those.

## Voice: native Korean neural voice (edge-tts)
- `python tools/gen_audio.py <slug>`: male `ko-KR-InJoonNeural` by default, `--voice
  ko-KR-SunHiNeural` for female. Rate -5%. One clip per card line, question, answer, survival line
  and word. Files under 1 KB count as missing and are regenerated.
- If it fails with HTTP 403, update the package: `pip install -U edge-tts`.
- fal.ai (`fal-ai/bytedance/seed-speech/tts/v2`, voice `shane_ko`) is the older paid route; use it
  only when the user asks and the account has balance.
