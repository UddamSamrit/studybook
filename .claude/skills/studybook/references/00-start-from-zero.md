# 00 · Start from zero (for the AI: walk a person with nothing to their own live studybook)

The person may have **nothing**: no GitHub account, no Git, no Python, no idea what a "skill" is. They
only installed a free AI app (Antigravity, the ChatGPT desktop app with Codex, Claude Code) and pasted
one message. Your job: take them from that to **their own study site on the internet**, with their
first unit, that they can open on their phone. You do the typing; they do only the few things a person
must do themselves (make an account, type their own password, click Authorize).

## How to talk to them
- Answer in the language they wrote in (often Khmer). Short sentences, one step at a time.
- Before each step, say in one line what it is for, with an everyday comparison
  ("Git is like a save button that remembers every version", "GitHub Pages is a free shelf on the internet for your site").
- Never ask for, type, or look at a password, a card number, or a one-time code they type into a website.
  The GitHub login code below is shown *to* them; they type it into the browser themselves.
- When your app asks permission to run a command, tell them what it does and that it is safe to press Run / Accept.
- If something fails, read the error, fix it, and tell them in one line what happened. Don't dump logs on them.

## What a skill is (say this once, early)
A skill is a recipe card for the AI, not an app. "studybook" is the recipe for building a study site:
picture cards with a native voice, a question drill, a word list, hide-and-recall. The AI reads the recipe
and builds the site on *their* computer, and it goes on *their* GitHub account. Nothing to buy.

## Step 1 · The tools (check first, install only what is missing)
Run the checks; skip any tool that is already there.

| Tool | Why | Check | Windows install | Mac install |
|---|---|---|---|---|
| Git | saves versions and sends the site to GitHub | `git --version` | `winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements` | `xcode-select --install` (a window opens; they click Install) |
| Python 3.12+ | runs the page builders | `py -3.12 --version` (Windows) / `python3 --version` (Mac, must be 3.12 or newer) | `winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements` | download the macOS installer from python.org/downloads and open it (they click through) |
| GitHub CLI (`gh`) | logs in to GitHub and turns the site on | `gh --version` | `winget install --id GitHub.cli -e --silent --accept-package-agreements --accept-source-agreements` | after Homebrew: `brew install gh` (Homebrew from brew.sh asks for their Mac password: they type it) |
| edge-tts | the free native voice | `py -3.12 -m edge_tts --help` / `python3 -m edge_tts --help` | `py -3.12 -m pip install -U edge-tts` | `python3 -m pip install -U edge-tts` |

Windows notes:
- A tool installed by winget is not on the PATH of the terminal that is already open. Use full paths
  for the rest of this session: `"C:\Program Files\Git\cmd\git.exe"`, `"C:\Program Files\GitHub CLI\gh.exe"`,
  and `py -3.12` for Python (the launcher always finds it). Or open a new terminal.
- Always call Python as `py -3.12` on Windows: an older Python may also be installed, and the builders need 3.12+.
- If `winget` is missing (very old Windows 10), send them to the Microsoft Store page "App Installer" and click Update.

From here on, `PY` means `py -3.12` on Windows and `python3` on Mac.

## Step 2 · Put the studybook skill into this folder
Work in the folder that is open in their AI app (make one called `my-studybook` if they have none open).
```
git clone --depth 1 https://github.com/1l3oth/studybook.git .studybook-src
```
Copy the skill to where their app reads skills from, then remove the download:
- Antigravity and Codex (ChatGPT app), Git Bash / Mac:
  `mkdir -p .agents/skills && cp -r .studybook-src/skill/studybook .agents/skills/studybook && rm -rf .studybook-src`
- Same in PowerShell:
  `New-Item -ItemType Directory -Force .agents\skills | Out-Null; Copy-Item -Recurse .studybook-src\skill\studybook .agents\skills\studybook; Remove-Item -Recurse -Force .studybook-src`
- Claude Code: use `.claude/skills/studybook` instead of `.agents/skills/studybook`.
(With Node.js installed, `npx github:1l3oth/studybook --agents` does the same.)
Read `.agents/skills/studybook/SKILL.md` (or the `.claude` copy) now: it is the router for every step below.

## Step 3 · A GitHub account (only if they have none)
Ask: "Do you already have a GitHub account?" If not, walk them through it; they do it in their browser:
1. Open https://github.com/signup
2. Type their email, make a password (they type it, you never see it), and pick a **username**.
   Tell them: the username becomes their site's address, `https://<username>.github.io/...`, so pick
   something short they like (lowercase letters, numbers and dashes).
3. Solve the puzzle GitHub shows, then type the code GitHub emails them.
4. If GitHub asks about a plan, the **Free** plan is enough. Skip the survey questions.
Wait until they say they are in.

## Step 4 · Log the computer in to GitHub (no password typed in the terminal)
First run `gh auth status`. If it already says "Logged in to github.com", skip the login command and go
straight to `gh auth setup-git` below. If it lists more than one account, ask which one the site should go
on and make it active with `gh auth switch --user <username>`.
```
gh auth login --hostname github.com --git-protocol https --web
```
Run it in the background and read its output. It prints a one-time code like `834E-DCFF` and the page
https://github.com/login/device. Tell them: open that page, type the code, press Continue, then
**Authorize GitHub CLI**. The command finishes on its own when they are done. Then:
```
gh auth setup-git
gh api user --jq .login                      # their username
gh api user --jq .id                         # their numeric id
```
Only if `git config --global user.email` prints nothing (never overwrite a name or email they already have):
```
git config --global user.name  "<username>"
git config --global user.email "<id>+<username>@users.noreply.github.com"
```
(The noreply address keeps their real email private.)

## Step 5 · Start their site
Ask two quick things in one message: which language they want to study (Korean, English, Japanese,
Chinese, French, Spanish, German, Thai, Vietnamese, ...) and which language the translations should be in
(Khmer, English, ...). Then, inside the work folder:
```
PY .agents/skills/studybook/templates/new_site.py site --lang <code> --support "<translation language>" --title "<Name>'s <Language> Studybook"
cd site
git init -b main
gh repo create studybook --public --source . --remote origin
```
On a re-run: skip `git init` if `.git` exists, and skip `gh repo create` if `git remote get-url origin`
already prints an address.
(If `studybook` is taken on their account, use `studybook-<language>`.) `public` is required for the
free GitHub Pages. `new_site.py` copies the builders into `site/tools/` and writes `site.json`; the web
address is read from the git remote, so their pages point at **their** site.

## Step 6 · Their first unit
Ask what they want to learn first (a topic, or text they paste, or a link). Keep it small: about 8-12
cards. Build it exactly as `references/02-build-unit-page.md` and `03-media-generation.md` say:
write `<slug>/unit.json` (target-language text in the `ko` fields, the translation in the `en` fields,
whatever the language), draw the flat SVG pictures, then:
```
PY tools/gen_audio.py <slug>
PY tools/render_unit.py <slug>
PY tools/build_stations.py
PY tools/build_feed.py
PY tools/build_images.py
```
`build_images.py` makes the app icons (the phone's "Install app" / Add to Home Screen needs them) and the
link-preview pictures. It uses Edge or Chrome; every Windows PC has Edge. Only if it says "No Chromium found",
skip it and tell them the site still works, just without an app icon.

Every unit.json must have `"full": []` (the audio step fills it); `gen_audio.py` adds it when missing.

## Step 7 · Put it on the internet (GitHub Pages)
```
git add -A
git commit -m "My first studybook unit"
git push -u origin main
gh api -X POST repos/<username>/<repo>/pages -f "source[branch]=main" -f "source[path]=/"
```
(Git Bash only: put `MSYS_NO_PATHCONV=1` in front of the `gh api` line.) Then wait 1-2 minutes, checking
`gh api repos/<username>/<repo>/pages/builds/latest --jq .status` until it says `built`.
Open `https://<username>.github.io/<repo>/` and check the page loads and one audio file plays
(`.../<slug>/audio/c01.mp3` answers 200).

## Step 8 · Hand it over
Give them the link and tell them:
- Open it on the phone. iPhone: Share → Add to Home Screen. Android: the "Install app" button. It opens like an app.
- How to study: look at the picture, say the line in your head, tap to check, then listen. Hide shows a blank so they recall first.
- Next time: open this folder in the same AI app and say "make a new studybook unit about <topic>" (Antigravity and Claude Code: `/studybook`, Codex: `$studybook`). The AI builds it and pushes; the site updates by itself.

## Free-plan notes
- Antigravity's free plan and ChatGPT Free's Codex have usage limits that reset. If the AI stops mid-way,
  they can come back after the reset and say "continue the studybook setup": check what already exists
  (the skill folder, `site/`, `.git`, the `origin` remote, the Pages site) and carry on from the first missing step.
- Nothing here costs money: Git, Python, GitHub, GitHub Pages and the edge-tts voice are all free.
