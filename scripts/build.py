#!/usr/bin/env python3
"""Write the roadmap and workbook directories from data/workbooks.json into index.html.

It also stamps the CSS/JS URLs with a content hash (?v=...) so browsers never mix a new page
with a cached old script. The cards, the hero count and the GitHub/YouTube links are plain HTML, so the page
works for every visitor, crawler and link preview, with or without JavaScript.
assets/js/main.js only adds the Roadmaps/Workbooks toggle, search and filtering on top of the generated cards.

    python3 scripts/build.py           # update index.html
    python3 scripts/build.py --check   # exit 1 if index.html is out of date

Standard library only (Python 3.8+).
"""
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "workbooks.json"
INDEX = ROOT / "index.html"

ICONS = {
    "python": '<path d="M8 7 3 12l5 5M16 7l5 5-5 5M13.5 5l-3 14"/>',
    "numpy": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
    "pandas": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9.5h18M9 9.5V20M15 9.5V20"/>',
    "sql": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.5"/><path d="M4.5 5.5v13c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-13M4.5 12c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5"/>',
    "roadmap": '<circle cx="6" cy="18.5" r="2.5"/><circle cx="18" cy="5.5" r="2.5"/><path d="M8.5 18.5H15a3.25 3.25 0 0 0 0-6.5H9a3.25 3.25 0 0 1 0-6.5h6.5"/>',
    "other": '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5zM13 4h5.5A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5H13z"/>',
}
OPEN_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>'
DOWNLOAD_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19h14"/></svg>'


def esc(value):
    return html.escape(str(value), quote=True)


def safe_url(url, hosts):
    """HTTPS URLs on an expected host only; anything else is treated as missing."""
    try:
        u = urlparse(url or "")
    except ValueError:
        return ""
    return url if u.scheme == "https" and u.hostname in hosts else ""


GITHUB = {"github.com"}
YOUTUBE = {"youtube.com", "www.youtube.com", "m.youtube.com"}


def load():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    labels = {c["id"]: c["label"] for c in data["categories"]}
    published, errors, seen = [], [], set()
    for w in data["workbooks"]:
        name = w.get("id", "?")
        if w.get("status") != "published" or w.get("verified") is not True:
            continue
        if name in seen:
            errors.append(f"{name}: duplicate id")
        seen.add(name)
        for field in ("id", "title", "category", "description", "repositoryUrl"):
            if not w.get(field):
                errors.append(f"{name}: missing {field}")
        if w.get("category") not in labels:
            errors.append(f"{name}: unknown category {w.get('category')!r}")
        if not safe_url(w.get("repositoryUrl"), GITHUB):
            errors.append(f"{name}: repositoryUrl must be an https://github.com/ URL")
        if w.get("downloadZipUrl") and not safe_url(w["downloadZipUrl"], GITHUB):
            errors.append(f"{name}: downloadZipUrl must be an https://github.com/ URL")
        published.append(w)
    if errors:
        sys.exit("data/workbooks.json has problems:\n  " + "\n  ".join(errors))
    order = [c["id"] for c in data["categories"]]
    published.sort(key=lambda w: order.index(w["category"]))  # stable: keeps file order within a category
    return data, labels, published, load_roadmaps(data, labels)


def local_file(rel, folder, suffix):
    """A file inside this site, e.g. roadmaps/X.pdf. Returns its Path, or None if unsafe or missing."""
    if not isinstance(rel, str) or not rel.startswith(folder + "/") or not rel.endswith(suffix):
        return None
    path = (ROOT / rel).resolve()
    if ROOT / folder not in path.parents or not path.is_file():
        return None
    return path


def pdf_pages(path):
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", path.read_bytes()))


def load_roadmaps(data, labels):
    """Published roadmaps: PDFs stored in roadmaps/ and served by this site."""
    published, errors, seen = [], [], set()
    for r in data.get("roadmaps", []):
        name = r.get("id", "?")
        if r.get("status") != "published" or r.get("verified") is not True:
            continue
        if name in seen:
            errors.append(f"{name}: duplicate id")
        seen.add(name)
        for field in ("id", "title", "category", "description", "fileUrl"):
            if not r.get(field):
                errors.append(f"{name}: missing {field}")
        if r.get("category") not in labels:
            errors.append(f"{name}: unknown category {r.get('category')!r}")
        path = local_file(r.get("fileUrl"), "roadmaps", ".pdf")
        if path is None:
            errors.append(f"{name}: fileUrl must be roadmaps/<file>.pdf and the file must exist")
        else:
            r = dict(r, _path=path, _pages=pdf_pages(path), _size=path.stat().st_size)
        published.append(r)
    if errors:
        sys.exit("data/workbooks.json has problems (roadmaps):\n  " + "\n  ".join(errors))
    return published


def card(w, labels, heading):
    label = labels[w["category"]]
    search = " ".join(
        [w["title"], label, w["description"], w.get("includes", ""), w.get("requirements", ""), w.get("difficulty", "")]
        + w.get("skills", [])
    ).lower()
    skills = "".join(f"<li>{esc(s)}</li>" for s in w.get("skills", []))
    facts = ""
    if w.get("includes"):
        facts += f"<div><dt>Includes</dt><dd>{esc(w['includes'])}</dd></div>"
    if w.get("requirements"):
        facts += f"<div><dt>You need</dt><dd>{esc(w['requirements'])}</dd></div>"
    zip_url = safe_url(w.get("downloadZipUrl"), GITHUB)
    title = esc(w["title"])
    return (
        f'<li class="card" data-category="{esc(w["category"])}" data-search="{esc(search)}">'
        f'<div class="card-top"><span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24">{ICONS.get(w["category"], ICONS["other"])}</svg></span>'
        f'<div><div class="card-meta"><span class="badge">{esc(label)}</span>'
        + (f'<span class="level">{esc(w["difficulty"])}</span>' if w.get("difficulty") else "")
        + "</div>"
        + (f'<p class="count">{esc(w["countLabel"])}</p>' if w.get("countLabel") else "")
        + "</div></div>"
        f"<{heading}>{title}</{heading}>"
        f'<p class="desc">{esc(w["description"])}</p>'
        + (f'<ul class="skills" aria-label="Skills practised">{skills}</ul>' if skills else "")
        + (f'<dl class="facts">{facts}</dl>' if facts else "")
        + '<div class="card-actions">'
        f'<a class="btn btn-primary" href="{esc(w["repositoryUrl"])}" target="_blank" rel="noopener noreferrer">Open Workbook<span class="visually-hidden">: {title} on GitHub (opens in a new tab)</span></a>'
        + (f'<a class="text-link" href="{esc(zip_url)}">{DOWNLOAD_ICON}Download ZIP<span class="visually-hidden"> of {title}</span></a>' if zip_url else "")
        + "</div></li>"
    )


def roadmap_card(r, labels, heading):
    label = labels[r["category"]]
    skills = "".join(f"<li>{esc(s)}</li>" for s in r.get("skills", []))
    size_mb = r["_size"] / 1_000_000
    fmt = f"PDF · {r['_pages']} pages · {size_mb:.1f} MB"
    facts = f"<div><dt>Format</dt><dd>{esc(fmt)}</dd></div>"
    if r.get("includes"):
        facts += f"<div><dt>Includes</dt><dd>{esc(r['includes'])}</dd></div>"
    digest = hashlib.sha256(r["_path"].read_bytes()).hexdigest()[:10]
    href = f"{r['fileUrl']}?v={digest}"
    title = esc(r["title"])
    return (
        f'<li class="card card-roadmap">'
        f'<div class="card-top"><span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24">{ICONS["roadmap"]}</svg></span>'
        f'<div><div class="card-meta"><span class="badge">{esc(label)}</span>'
        + (f'<span class="level">{esc(r["difficulty"])}</span>' if r.get("difficulty") else "")
        + "</div>"
        + (f'<p class="count">{esc(r["countLabel"])}</p>' if r.get("countLabel") else "")
        + "</div></div>"
        f"<{heading}>{title}</{heading}>"
        f'<p class="desc">{esc(r["description"])}</p>'
        + (f'<ul class="skills" aria-label="Topics covered">{skills}</ul>' if skills else "")
        + f'<dl class="facts">{facts}</dl>'
        + '<div class="card-actions">'
        f'<a class="btn btn-primary" href="{esc(href)}" target="_blank" rel="noopener">{OPEN_ICON}Open Roadmap<span class="visually-hidden">: {title} PDF (opens in a new tab)</span></a>'
        f'<a class="text-link" href="{esc(href)}" download="{esc(r["_path"].name)}">{DOWNLOAD_ICON}Download PDF<span class="visually-hidden"> of {title}</span></a>'
        + "</div></li>"
    )


def roadmap_directory(labels, roadmaps):
    if not roadmaps:
        return '<p class="empty">New roadmaps are on the way.</p>'
    items = "\n".join("            " + roadmap_card(r, labels, "h4") for r in roadmaps)
    return f'<ul class="grid">\n{items}\n          </ul>'


def directory(data, labels, published):
    threshold = data.get("site", {}).get("showSearchFromCount", 6)
    if len(published) < threshold:  # few workbooks: one grid in category order
        items = "\n".join("            " + card(w, labels, "h4") for w in published)
        return f'<ul class="grid">\n{items}\n          </ul>'
    sections = []
    for cat in data["categories"]:  # many workbooks: grouped under category headings
        items = [w for w in published if w["category"] == cat["id"]]
        if not items:
            continue
        cards = "\n".join("              " + card(w, labels, "h5") for w in items)
        sections.append(
            f'<section class="category" data-category-section="{esc(cat["id"])}" aria-labelledby="cat-{esc(cat["id"])}">\n'
            f'            <h4 class="category-title" id="cat-{esc(cat["id"])}">{esc(cat["label"])}</h4>\n'
            f'            <ul class="grid">\n{cards}\n            </ul>\n          </section>'
        )
    return "\n          ".join(sections)


def plural(n, word):
    return f"<strong>{n}</strong> {word}{'' if n == 1 else 's'}"


def stats(published, roadmaps):
    total = sum(int(w.get("problemCount") or 0) for w in published)
    parts = ([plural(len(roadmaps), "free roadmap")] if roadmaps else []) + [plural(len(published), "free workbook")]
    text = " · ".join(parts)
    if total:
        text += f" · <strong>{total}</strong> practice questions and tasks"
    return text


def replace_block(page, name, content):
    pattern = re.compile(rf"(<!-- build:{name} -->)(.*?)(<!-- /build:{name} -->)", re.S)
    if not pattern.search(page):
        sys.exit(f"index.html is missing the <!-- build:{name} --> markers")
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), page, count=1)


def set_links(page, attr, url):
    """Point every tag carrying `attr` at `url`, hiding the YouTube parts when no URL is set."""
    def fix(m):
        tag = re.sub(r"\s+hidden(?=[\s>])", "", m.group(0))
        if tag.startswith("<a") and url:
            tag = re.sub(r'href="[^"]*"', f'href="{esc(url)}"', tag, count=1)
        if not url:
            tag = tag[:-1] + " hidden>"
        return tag
    return re.sub(rf"<[a-z]+\b[^>]*\b{attr}\b[^>]*>", fix, page)


def version_assets(page):
    """Add a content hash to the CSS/JS URLs so a new deploy never pairs new HTML with a cached old script."""
    for rel in ("assets/css/styles.css", "assets/js/main.js"):
        digest = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:10]
        page, n = re.subn(rf'"{re.escape(rel)}(?:\?v=[0-9a-f]*)?"', f'"{rel}?v={digest}"', page)
        if n != 1:
            sys.exit(f"index.html should reference {rel} exactly once (found {n})")
    return page


def build():
    data, labels, published, roadmaps = load()
    site = data.get("site", {})
    page = INDEX.read_text(encoding="utf-8")
    page = replace_block(page, "stats", stats(published, roadmaps))
    page = replace_block(page, "roadmaps", "\n          " + roadmap_directory(labels, roadmaps) + "\n          ")
    page = replace_block(page, "roadmap-count", str(len(roadmaps)))
    page = replace_block(page, "workbook-count", str(len(published)))
    page = replace_block(page, "directory", "\n          " + directory(data, labels, published) + "\n          ")
    threshold = site.get("showSearchFromCount", 6)
    page = re.sub(r'data-search-from="\d+"', f'data-search-from="{int(threshold)}"', page)
    github = safe_url(site.get("githubProfileUrl"), GITHUB) or "https://github.com/vikasthamke"
    page = set_links(page, "data-github-link", github)
    page = set_links(page, r"data-youtube-(?:link|section|item)", safe_url(site.get("youtubeUrl"), YOUTUBE))
    page = version_assets(page)
    return page, published, roadmaps


def main():
    page, published, roadmaps = build()
    current = INDEX.read_text(encoding="utf-8")
    if "--check" in sys.argv:
        if page != current:
            sys.exit("index.html is out of date: run python3 scripts/build.py")
        print(f"index.html is up to date ({len(roadmaps)} roadmaps, {len(published)} workbooks)")
        return
    if page != current:
        INDEX.write_text(page, encoding="utf-8")
    print(f"index.html {'updated' if page != current else 'already up to date'}: "
          f"{len(roadmaps)} roadmaps, {len(published)} workbooks")


if __name__ == "__main__":
    main()
