# Workbook Audit — GitHub account `vikasthamke`

Audit date: 2026-10-15. All 21 repositories on the account were listed with `gh repo list`. Every candidate was
inspected by its README, full file tree, `requirements.txt` and notebook (each notebook was parsed as valid JSON).
All four workbook repositories were shallow-cloned and scanned for common credential patterns (GitHub, OpenAI and AWS
keys, private-key blocks, Slack tokens): **no matches**. The `main.zip` download URL of each returned HTTP 200.

## 1. Ready to publish

| Workbook | Repository | Visibility | What is inside (from the repo itself) | Setup |
|---|---|---|---|---|
| Python Practice Workbook | [python-practice-workbook](https://github.com/vikasthamke/python-practice-workbook) | Public | 100 questions (20 Beginner, 35 Intermediate, 30 Advanced, 15 Expert), 615 automated tests, 3-level hints, hidden reference solutions, Testing Mode, local progress tracking. Notebook in `notebooks/`, practice system in `src/`, 13 synthetic datasets in `data/sample_data/`. | Python 3.10+, `pip install -r requirements.txt` (Jupyter only; questions use the standard library). Needs the whole repo: the notebook imports `src/`. |
| Pandas Practice Workbook | [pandas-practice-workbook](https://github.com/vikasthamke/pandas-practice-workbook) | Public, MIT | 75 challenges: Learning tasks 1–44, Testing tasks 45–74, final Customer Value & Retention challenge (task 75). Hints and solutions via `practice_system.py`. 5 CSV datasets in `data/` (customers, products, orders, order_items, student_performance). | Python 3, `pip install -r requirements.txt` (pandas, numpy, jupyter, ipykernel). Needs the whole repo: `data/` + `practice_system.py`. |
| SQL Practice Workbook | [sql-practice-workbook](https://github.com/vikasthamke/sql-practice-workbook) | Public, MIT | 171 questions in 12 modules (33 Easy, 65 Medium, 50 Hard, 23 Advanced), 3 role capstones, a 16-question final assessment, on a 32-table synthetic SaaS dataset. Validated on PostgreSQL 18.6 and MySQL 8.4.11. Setup scripts, CSVs, per-engine solution files, `sql_practice.py` helper. | Requires a local **PostgreSQL 16+ or MySQL 8.0+**; load `setup.sql` / `setup_mysql.sql`. Python packages are optional. README has full database setup steps. |

## 2. Needed minor improvements — resolved 2026-10-15

| Workbook | Issue found | Fix (pushed) |
|---|---|---|
| [NumPy Practice Workbook](https://github.com/vikasthamke/numpy-practice-workbook) | `requirements.txt` listed only `Jupyter`, which does not install NumPy, so a fresh virtual environment failed with `ModuleNotFoundError: numpy`. | `requirements.txt` is now `numpy`, `jupyter`, `ipykernel` (commit 22bfe3e). Verified in a fresh venv: all 70 notebook code cells execute without errors. |
| [Python Practice Workbook](https://github.com/vikasthamke/python-practice-workbook) | (a) No `LICENSE`. (b) Installation started with `cd` but never said how to get the code. | (a) MIT licence added, matching the other workbooks (03e626c). (b) Clone / Download ZIP step added (21255a8). |

The NumPy workbook is otherwise complete: 67 tasks (Learning 1–38, Testing 39–66, final Factory Health Dashboard
task 67), MIT licence, and the Smart Factory dataset is generated in code by `practice_system.load_dataset()`
(seeded), so no data files are missing.

## 3. Relevant-looking repositories not published on the page

| Repository | Visibility | Reason |
|---|---|---|
| Learning-ML | Private | Private; not changed. |
| Fairness-in-ML | Private | Private; not changed. |
| BloodPressure-Estimation | Private | Private research project, not a workbook. |
| AtliQ-Hotels-Data-Analysis-Project | Public | A finished analysis project (one notebook + datasets), not a practice workbook. Could later go under "Projects". |
| library-management-system, python-file-folder-manager, tic-tac-toe | Public | Small Python apps/projects, not structured practice resources. |
| vikas-thamke-portfolio, vikas-thamke-store, momentum-productivity-tracker | Mixed | Personal sites/apps, unrelated. |
| vikasthamke.github.io | Public, Pages on | Existing user site containing only a README. Left untouched; the resource page lives in its own repo and publishes under this domain as `/skillpilot-resources/`. |
| Minnesota_forked, Pan-Tompkins-FixedPoint, qrs_detector, evosuite | Forks | Forks of other people's projects. |
| test, vikasthamke (profile README) | — | Not resources. |

No Statistics, Machine Learning, Deep Learning or Generative AI workbook repositories exist yet, so those categories
are not shown.

## 4. Missing information

- **YouTube channel URL** — resolved: the owner supplied `https://www.youtube.com/@TheSkillPilot`. It was checked on 2026-10-15: HTTP 200, and the channel title is "SkillPilot".
- **Social preview image** — resolved: `assets/images/og-image.png` (1200×630) was made from the SkillPilot logo.
- **Pandas/NumPy difficulty labels** — the READMEs describe progression (fundamentals → testing/interview-style) but give
  no per-task levels, so the cards describe the progression rather than a single difficulty.
