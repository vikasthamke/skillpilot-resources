# SkillPilot Resources

The SkillPilot **Free Roadmaps & Practice Workbooks** page — the link-in-bio page for Instagram, Reels, Stories and YouTube descriptions.

**Live page:** https://vikasthamke.github.io/skillpilot-resources/

Plain HTML, CSS and JavaScript, hosted on GitHub Pages. No framework, no external scripts or fonts. One small standard-library
Python script writes the roadmap and workbook cards into `index.html`, so the page works for every visitor, crawler and link preview —
with or without JavaScript.

```
index.html               page structure and copy; the workbook cards, hero count and links are generated into it
assets/css/styles.css    styles (brand colours are CSS variables at the top)
assets/js/main.js        adds the Roadmaps / Workbooks toggle, search and subject filters (progressive enhancement)
assets/images/           logo mark (header + favicon), desktop hero emblem, Apple touch icon, 1200×630 social preview
data/workbooks.json      single source of truth: site links, every roadmap and every workbook
roadmaps/                roadmap PDFs served by this site
scripts/build.py         writes data/workbooks.json into index.html (python3 scripts/build.py)
WORKBOOK_AUDIT.md        audit of the GitHub account that the listing is based on
.nojekyll                tells GitHub Pages to serve the files as they are
```

## Maintenance guide

All workbook content lives in `data/workbooks.json`. You never edit the cards in the HTML by hand. After **any** change to the
JSON, run:

```bash
python3 scripts/build.py
```

It checks the entries (required fields, known category, `https://github.com/` links) and rewrites the generated parts of
`index.html` between the `<!-- build:… -->` markers. Commit both files. A local pre-commit hook runs
`python3 scripts/build.py --check` and blocks a commit if `index.html` is out of date.

### 1. Add a workbook

1. Make sure the workbook repository is **public** and its README explains setup.
2. Add an object to the `workbooks` array:

```json
{
  "id": "statistics-practice-workbook",
  "title": "Statistics Practice Workbook",
  "category": "statistics",
  "status": "published",
  "verified": true,
  "problemCount": 50,
  "countLabel": "50 exercises",
  "difficulty": "Beginner → Intermediate",
  "description": "One or two sentences based on what the repository actually contains.",
  "shortDescription": "One short sentence (about 100 characters) shown on the card.",
  "skills": ["Distributions", "Hypothesis tests", "Confidence intervals"],
  "includes": "Jupyter notebook, helper module and datasets",
  "requirements": "Python 3, NumPy, SciPy and Jupyter.",
  "repositoryUrl": "https://github.com/vikasthamke/statistics-practice-workbook",
  "downloadZipUrl": "https://github.com/vikasthamke/statistics-practice-workbook/archive/refs/heads/main.zip"
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Unique, usually the repo name. |
| `title`, `description` | yes | Write them from the README and real contents. `description` is used for search. |
| `shortDescription` | recommended | The text shown on the square card. Keep it to about 100 characters so the card stays square; falls back to `description`. |
| `category` | yes | One of the `id`s in the `categories` array (`python`, `numpy`, `pandas`, `sql`, `statistics`, `machine-learning`, `deep-learning`, `genai`, `other`). Order of `categories` = order on the page. |
| `status` | yes | Only `"published"` is shown. Use `"draft"` while preparing an entry. |
| `verified` | yes | Must be `true` to be shown — set it after you've checked the repo and links. |
| `repositoryUrl` | yes | Must be an `https://github.com/...` URL; the build stops with an error otherwise. |
| `problemCount` | no | Number added to the hero total ("413 practice questions and tasks"). |
| `countLabel` | no | The card shows the part before the first ` · ` ("100 questions · 615 automated tests" → "100 questions"). |
| `difficulty`, `skills`, `includes`, `requirements` | no | Not shown on the card, but included in search. Leave out anything you can't verify. |
| `downloadZipUrl` | no | `https://github.com/<user>/<repo>/archive/refs/heads/main.zip` (use the repo's default branch). |

Workbook cards are square and show only the title, the count, `shortDescription` and the two links. They sit four per row
on wide screens and wrap to three, two or one column as the screen narrows.

### 1b. Add a roadmap

Roadmaps are PDFs hosted on this site. They appear under the **Roadmaps** toggle.

1. Copy the PDF into `roadmaps/`, for example `roadmaps/SkillPilot_Machine_Learning_Roadmap.pdf`.
2. Add an object to the `roadmaps` array in `data/workbooks.json`:

```json
{
  "id": "machine-learning-roadmap",
  "title": "The Machine Learning Roadmap",
  "category": "machine-learning",
  "status": "published",
  "verified": true,
  "countLabel": "9 stages · 4 portfolio projects · 12-week plan",
  "difficulty": "Beginner-friendly",
  "description": "What the roadmap covers, in one or two sentences.",
  "skills": ["Python & data libraries", "Model evaluation"],
  "includes": "What is inside the PDF",
  "fileUrl": "roadmaps/SkillPilot_Machine_Learning_Roadmap.pdf"
}
```

`fileUrl` must point to a `.pdf` inside `roadmaps/` that exists; the build stops otherwise. The page count and file size on the
card ("PDF · 24 pages · 1.4 MB") are read from the file, and the link carries a content hash (`?v=…`), so replacing the PDF
with a new version and rebuilding is enough to update it everywhere.

### Roadmaps / Workbooks toggle

The toggle is added by `assets/js/main.js` (accessible tabs, arrow keys switch between them). Links ending in `#roadmaps` or
`#workbooks` open the matching tab, so `https://vikasthamke.github.io/skillpilot-resources/#roadmaps` is a direct link to the
roadmaps. Without JavaScript both lists are shown one after the other.

### 2. Update a description

Edit the fields of that entry in `data/workbooks.json`, run `python3 scripts/build.py`, and publish (step 5).

### 3. Remove a workbook

Delete its object from the array, or set `"status": "draft"` to hide it without losing the text. Then run `python3 scripts/build.py`.

### 4. Preview changes locally

Run `python3 scripts/build.py`, then serve the folder:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. (Double-clicking `index.html` also works now, since nothing is fetched.)

### 5. Publish

```bash
python3 scripts/build.py && git add -A && git commit -m "Add statistics workbook" && git push
```

GitHub Pages redeploys from the `main` branch automatically, usually within a minute. Progress is under the repository's **Actions** tab.

### 6. Where to find the public URL

Repository → **Settings → Pages** shows the live address: https://vikasthamke.github.io/skillpilot-resources/

## Site settings

In `data/workbooks.json → site`:

- `youtubeUrl` (then run the build) — the SkillPilot channel, `https://www.youtube.com/@TheSkillPilot`. It feeds the hero "Explore on YouTube" button, the "Keep Learning with SkillPilot" section and the footer link. If you empty it, all three are hidden.
- `githubProfileUrl` — header and footer GitHub links.
- `showSearchFromCount` (then run the build) — the search box and subject filters (and grouping by subject) appear once this many workbooks are published. Default `6`.
