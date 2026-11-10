# Uddam's Studybook

A free study site with Khmer translations. It's a shelf of books, and each book has its own units. Open it on your phone and add it to your home screen, and it works like an app.

**Open the site: https://uddamsamrit.github.io/studybook/**

```
studybook/
├── english/              English: the 4 skills
│   ├── reading/
│   ├── listening/
│   ├── speaking/         Introducing yourself
│   └── writing/
└── kubernetes/           Kubernetes: zero to hero (steps 0–11)
```

Each unit is one page with four tabs:

| Tab | What it's for |
|---|---|
| **Cards** | One idea per card: a flat picture, an English line, the Khmer meaning and a native voice. |
| **Q&A** | Common mistakes first, then real questions. Answer in your head, then tap to check. |
| **Vocab** | The unit's words in groups, with audio. Hide either side to test yourself. |
| **Full** | The whole unit as one page you can read or print. |

## How to study

1. Look at the picture and say the English line in your head.
2. Tap to check, then listen to the voice.
3. Turn on **Hide** to see a blank and recall the line first.
4. Use **Focus** to go through the unit one card at a time.

## Books

### English: the 4 skills · [open](https://uddamsamrit.github.io/studybook/english/)

| Skill | What it trains | Units |
|---|---|---|
| [Reading](https://uddamsamrit.github.io/studybook/english/reading/) | Read short texts and understand the key words | coming soon |
| [Listening](https://uddamsamrit.github.io/studybook/english/listening/) | Native audio at a calm speed | coming soon |
| [Speaking](https://uddamsamrit.github.io/studybook/english/speaking/) | Lines for real conversations | [Introducing yourself](https://uddamsamrit.github.io/studybook/english/speaking/introducing-yourself/) |
| [Writing](https://uddamsamrit.github.io/studybook/english/writing/) | Clear sentences for messages, emails and reports | coming soon |

### Kubernetes: zero to hero · [open](https://uddamsamrit.github.io/studybook/kubernetes/)

| Step | Unit | Link |
|---|---|---|
| 0 | Kubernetes basics | [open](https://uddamsamrit.github.io/studybook/kubernetes/00-basics/) |
| 1 | Containers and images | [open](https://uddamsamrit.github.io/studybook/kubernetes/01-containers/) |
| 2 | Pods and kubectl | [open](https://uddamsamrit.github.io/studybook/kubernetes/02-pods/) |
| 3 | Deployments and rollouts | [open](https://uddamsamrit.github.io/studybook/kubernetes/03-deployments/) |
| 4 | Services and Ingress | [open](https://uddamsamrit.github.io/studybook/kubernetes/04-services/) |
| 5 | ConfigMaps and Secrets | [open](https://uddamsamrit.github.io/studybook/kubernetes/05-config/) |
| 6 | Volumes and StatefulSets | [open](https://uddamsamrit.github.io/studybook/kubernetes/06-storage/) |
| 7 | Scaling and health checks | [open](https://uddamsamrit.github.io/studybook/kubernetes/07-scaling/) |
| 8 | Helm and namespaces | [open](https://uddamsamrit.github.io/studybook/kubernetes/08-helm/) |
| 9 | Monitoring and debugging | [open](https://uddamsamrit.github.io/studybook/kubernetes/09-monitoring/) |
| 10 | Security and RBAC | [open](https://uddamsamrit.github.io/studybook/kubernetes/10-security/) |
| 11 | CI/CD and GitOps | [open](https://uddamsamrit.github.io/studybook/kubernetes/11-production/) |

Old links such as `/studybook/kubernetes-basics/` still work: they forward to the new page.

An AI can read every unit as text from the feed: [feed.xml](https://uddamsamrit.github.io/studybook/feed.xml).

## More English practice

| Site | Use it for |
|---|---|
| [YouGlish](https://youglish.com/) | Type a word or phrase (for example "idempotent" or "trade-off") and hear real people say it in YouTube videos. |
| [VOA Learning English](https://learningenglish.voanews.com/) | Slow, clear news in American English, with the full text under each story. |
| [BBC Learning English](https://www.bbc.co.uk/learningenglish) | Short courses, grammar, pronunciation and "6 Minute English" in British English. |

## Add a unit or a book

Units are built with the [studybook skill](https://github.com/1l3oth/studybook). In Claude Code, open this folder and type:

```
/studybook make a unit about <topic> in english/listening
```

A **book** is a folder with a `book.json` (title, Khmer title, description, order). A folder with a `book.json` inside a book is a section. A folder with a `unit.json` is a unit. Add `"draft": true` to a `book.json` to keep that book off the site while you work on it.

What happens behind the scenes:

```
<book>/<unit>/unit.json                    # the content: cards, Q&A, words (write this first)
python <book>/<unit>/draw.py               # flat SVG pictures      -> img/
python tools/gen_audio.py <book>/<unit>    # native voice (edge-tts) -> audio/
python tools/render_unit.py <book>/<unit>  # the unit page          -> index.html
python tools/build_stations.py             # every book page and the homepage
python tools/build_feed.py                 # feed.xml
git push                                   # GitHub Pages updates the site
```

You need Python 3.12+ and `pip install edge-tts`. The builders use only the standard library.

## Folder layout

```
index.html          homepage: one "station" per book
<book>/book.json    a book or section: title, Khmer title, description, order
<book>/<unit>/      one unit: unit.json, draw.py, index.html, img/, audio/
assets/             shared styles and the page script
tools/              builders (render, audio, stations, feed, pictures) and hub_template.html
site.json           site title, study language (en) and translation language (Khmer)
manifest.webmanifest, sw.js, offline.html, icons/   make the site installable
```
