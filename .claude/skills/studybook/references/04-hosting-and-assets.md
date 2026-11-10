# 04 · Hosting and assets (GitHub Pages)

GitHub Pages is a real web server, so a unit should **not** be one giant self-contained file there.
Each unit is a light HTML page plus separate `img/` and `audio/` folders that load on demand.

## The unit folder
`render_unit.py` writes the page from `unit.json`; the unit's folder holds:
```
<unit-slug>/
  index.html     ~100 KB (references assets by relative path: img/..., audio/...)
  img/           one file per beat image
  audio/         one file per clip (speech lines, Q&A, vocab)
```
It clears and rewrites `img/` and `audio/` each run, and returns relative paths instead of base64
`data:` URIs. Point the builder's output dir at the unit folder inside the local repo clone.

## Why not the self-contained file on Pages
The single-file build embeds everything as base64 and grows large (10 MB+). A claude.ai **artifact**
times out above ~6 MB; a normal web server does not, but a 10 MB page still loads slowly and wastes
bandwidth. Separate assets → the page is instant and clips stream only when played. Keep the
self-contained file only for offline use or a claude.ai artifact (`lite`).

## Your web address
`site.json` "url" is empty on a new site; every builder then reads it from the git remote
(`github.com/<user>/<repo>` → `https://<user>.github.io/<repo>/`). Add the remote before rendering, or render again after.

## Deploy
1. Copy/emit the unit into the local repo clone (`web` mode straight into `<repo>/<unit-slug>/`).
2. Add the unit's card to the hub `index.html` and refresh `feed.xml` (see 05).
3. `git add -A && git commit && git push origin main`.
4. Pages rebuilds automatically. Poll `gh api repos/<owner>/<repo>/pages/builds/latest` until
   `status: built`, then curl the unit URL and one asset (e.g. `.../audio/<id>.mp3`) for HTTP 200.

## Gotchas
- **`.nojekyll`** must exist at the repo root or Jekyll may skip folders it dislikes.
- **Charset:** the page still needs `<meta charset="utf-8">` first even on Pages.
- **Lazy images** report `naturalWidth==0` until scrolled into view; that is not breakage.
- The Chrome extension can't open `file://` for local preview — serve with
  `python -m http.server <port> --directory <repo>` and open the `http://localhost` URL.
- Never force-push the site repo; if a push is rejected, `git pull --rebase` then push.
