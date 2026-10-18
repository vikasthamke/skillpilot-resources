# SkillPilot Resources (moved)

This GitHub Pages site used to host SkillPilot's free workbooks and roadmaps. They now live in the SkillPilot store:

**https://skillpilotofficial.com/free-resources**

- `index.html` immediately forwards visitors to the store (meta refresh + script, with a visible link as a fallback).
- `404.html` forwards any old deep link — for example the former roadmap PDF URL — to the matching store page.
- Both add `utm_source=skillpilot-resources` so these visits show up as a traffic source in the store's admin.
- `assets/images/` keeps the favicon and social preview image used by the redirect page.

The previous page (cards, build script, roadmap PDF) is preserved in this repository's git history.
