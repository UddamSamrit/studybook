# 05 · RSS feed (so an AI can read the studybook)

The feed makes each unit **readable as text** by an AI or a feed reader, without running the
interactive app. Build it with `templates/build_feed.py` and write `feed.xml` at the repo root.

## What goes in it
RSS 2.0 with the `content` namespace. One `<item>` per unit:
- `title`, `link` (the unit URL), `guid` (same URL, `isPermaLink="true"`), `pubDate`.
- `description` — a one-line summary.
- **`content:encoded`** wrapped in `<![CDATA[ ... ]]>` — the unit's **full text**: the whole speech
  (target + translation), every Q&A question and answer, and all vocab (`word = meaning`). This is
  the part that lets an AI actually learn the material from the feed alone.

Channel-level: `title`, `link` (site root), an `atom:link rel="self"` to `feed.xml`, `description`,
`language`, `lastBuildDate`.

## Make it discoverable
Add to the hub `index.html` `<head>`:
```
<link rel="alternate" type="application/rss+xml" title="<site> feed" href="feed.xml">
```
so an agent pointed at the site root finds the feed on its own. A visible "RSS feed" link in the
footer helps too.

## Rules
- XML-escape `title` / `description`; the CDATA body needs no escaping but must not contain `]]>`
  (plain study text never does).
- One item per unit — regenerate the whole feed when you add or change a unit.
- Serve as `application/xml` (GitHub Pages does this for `.xml` automatically).
- Verify live: `curl -sI .../feed.xml` returns 200, and the body parses as XML.

`build_feed.py` in `templates/` is a working generator; adapt the item list and the content builder
to your units' data.
