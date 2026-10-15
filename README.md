# SkillPilot Resources

The SkillPilot **Free Practice Workbooks** page — the link-in-bio page for Instagram, Reels, Stories and YouTube descriptions.

**Live page:** https://vikasthamke.github.io/skillpilot-resources/

Plain HTML, CSS and JavaScript, hosted on GitHub Pages. No build step, no framework, no external scripts or fonts.

```
index.html               page structure and copy
assets/css/styles.css    styles (brand colours are CSS variables at the top)
assets/js/main.js        renders the workbook cards from the JSON file
assets/images/           logo mark (header + favicon), Apple touch icon, 1200×630 social preview
data/workbooks.json      single source of truth: site links + every workbook
WORKBOOK_AUDIT.md        audit of the GitHub account that the listing is based on
.nojekyll                tells GitHub Pages to serve the files as they are
```

## Maintenance guide

All workbook content lives in `data/workbooks.json`. You never need to edit the HTML to add, change or remove a workbook.

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
| `title`, `description` | yes | Write them from the README and real contents. |
| `category` | yes | One of the `id`s in the `categories` array (`python`, `numpy`, `pandas`, `sql`, `statistics`, `machine-learning`, `deep-learning`, `genai`, `other`). Order of `categories` = order on the page. |
| `status` | yes | Only `"published"` is shown. Use `"draft"` while preparing an entry. |
| `verified` | yes | Must be `true` to be shown — set it after you've checked the repo and links. |
| `repositoryUrl` | yes | Must be an `https://github.com/...` URL, otherwise the card is skipped. |
| `problemCount` | no | Number added to the hero total ("413 practice questions and tasks"). |
| `countLabel`, `difficulty`, `skills`, `includes`, `requirements` | no | Leave out anything you can't verify — the card adapts. |
| `downloadZipUrl` | no | `https://github.com/<user>/<repo>/archive/refs/heads/main.zip` (use the repo's default branch). |

Icons exist for `python`, `numpy`, `pandas` and `sql`; other categories get a generic book icon until you add one to `ICONS` in `assets/js/main.js`.

### 2. Update a description

Edit the fields of that entry in `data/workbooks.json` and publish (step 5).

### 3. Remove a workbook

Delete its object from the array, or set `"status": "draft"` to hide it without losing the text.

### 4. Preview changes locally

The page loads the JSON with `fetch`, so open it through a local server, not by double-clicking the file:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. Check that the JSON is valid first: `python3 -m json.tool data/workbooks.json`.

### 5. Publish

```bash
git add -A && git commit -m "Add statistics workbook" && git push
```

GitHub Pages redeploys from the `main` branch automatically, usually within a minute. Progress is under the repository's **Actions** tab.

### 6. Where to find the public URL

Repository → **Settings → Pages** shows the live address: https://vikasthamke.github.io/skillpilot-resources/

## Site settings

In `data/workbooks.json → site`:

- `youtubeUrl` — **empty until you add your channel URL** (for example `https://www.youtube.com/@yourhandle`). While it is empty, the YouTube button, section and footer link stay hidden. Once set, all three appear.
- `githubProfileUrl` — header and footer GitHub links.
- `showSearchFromCount` — the search box and subject filters (and grouping by subject) appear once this many workbooks are published. Default `6`.
