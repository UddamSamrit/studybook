# 01 · Create a new studybook site

Goal: an empty GitHub Pages site with a notebook-style hub, ready for units.

## Fastest way
`PY <skill>/templates/new_site.py <folder> --lang <code> --support "<translation language>" --title "..."`
does steps 2-4 for you (empty homepage, builders in `tools/`, app files, `site.json`, `.nojekyll`).
Then step 1 with `gh repo create <repo> --public --source . --remote origin`, and steps 5-6.
A person starting with nothing at all: follow `00-start-from-zero.md` instead.

## Steps
1. **Repo.** Create (or reuse) a public GitHub repo, e.g. `studybook`. GitHub Pages on the free tier
   needs the repo public. Confirm the active `gh` account owns it: `gh auth status --active`.
2. **Layout.** One folder per unit; the hub at the root:
   ```
   studybook/
     index.html                 hub (table of contents)
     feed.xml                   RSS feed (see 05)
     .nojekyll                  disable Jekyll so _underscore/asset folders serve verbatim
     <unit-slug>/               one per unit (see 02, 04)
       index.html  img/  audio/
   ```
3. **Hub page.** Copy `templates/hub_index.html` and adapt: the site title, and one "unit card" per
   unit (number, title, one-line description, a small table of contents of its tabs, and a link to
   `<unit-slug>/`). Keep the notebook look from `06-style-and-sample.md`. Add RSS auto-discovery in
   `<head>`: `<link rel="alternate" type="application/rss+xml" href="feed.xml">`.
4. **`.nojekyll`.** Create an empty `.nojekyll` at the root.
5. **First commit + push** to `main`.
6. **Enable Pages** from `main` / root:
   ```
   gh api -X POST repos/<owner>/<repo>/pages -f "source[branch]=main" -f "source[path]=/"
   ```
   (In Git Bash put `MSYS_NO_PATHCONV=1` in front, or it mangles the path; PowerShell needs nothing.)
   The response `html_url` is your site root. First build takes 1–2 min; poll
   `gh api repos/<owner>/<repo>/pages/builds/latest` until `status: built`, then check the URL is 200.

## Notes
- The hub is where a learner (and the RSS reader) starts. Every new unit adds a card here and an
  item to `feed.xml`.
- Local working copy of the repo lives on the user's machine; edits rebuild and re-push (see 04).
- Do not silently rewrite an existing `origin` that points elsewhere — report and stop.
