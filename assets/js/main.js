// Renders the workbook directory from data/workbooks.json.
// Only entries with status "published" and verified: true are shown.
(function () {
  "use strict";

  var ICONS = {
    python: '<path d="M8 7 3 12l5 5M16 7l5 5-5 5M13.5 5l-3 14"/>',
    numpy: '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
    pandas: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9.5h18M9 9.5V20M15 9.5V20"/>',
    sql: '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.5"/><path d="M4.5 5.5v13c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-13M4.5 12c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5"/>',
    other: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5zM13 4h5.5A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5H13z"/>'
  };

  var state = { query: "", category: "all" };
  var data, published, grouped = false, labels = {};

  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Links must be HTTPS and point to the expected host; anything else is dropped.
  function safeUrl(url, hostPattern) {
    try {
      var u = new URL(url);
      return u.protocol === "https:" && hostPattern.test(u.hostname) ? u.href : "";
    } catch (e) { return ""; }
  }

  function card(w) {
    var repo = safeUrl(w.repositoryUrl, /^github\.com$/);
    if (!repo) return "";
    var zip = w.downloadZipUrl ? safeUrl(w.downloadZipUrl, /^github\.com$/) : "";
    var icon = ICONS[w.category] || ICONS.other;
    var hTag = grouped ? "h4" : "h3";
    var skills = (w.skills || []).map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("");
    var facts = "";
    if (w.includes) facts += "<div><dt>Includes</dt><dd>" + esc(w.includes) + "</dd></div>";
    if (w.requirements) facts += "<div><dt>You need</dt><dd>" + esc(w.requirements) + "</dd></div>";

    return '<li class="card">' +
      '<div class="card-top"><span class="icon" aria-hidden="true"><svg viewBox="0 0 24 24">' + icon + "</svg></span>" +
      '<div><div class="card-meta"><span class="badge">' + esc(labels[w.category] || w.category) + "</span>" +
      (w.difficulty ? '<span class="level">' + esc(w.difficulty) + "</span>" : "") + "</div>" +
      (w.countLabel ? '<p class="count">' + esc(w.countLabel) + "</p>" : "") + "</div></div>" +
      "<" + hTag + ">" + esc(w.title) + "</" + hTag + ">" +
      '<p class="desc">' + esc(w.description) + "</p>" +
      (skills ? '<ul class="skills" aria-label="Skills practised">' + skills + "</ul>" : "") +
      (facts ? '<dl class="facts">' + facts + "</dl>" : "") +
      '<div class="card-actions">' +
      '<a class="btn btn-primary" href="' + esc(repo) + '" target="_blank" rel="noopener noreferrer">Open Workbook<span class="visually-hidden">: ' + esc(w.title) + " on GitHub (opens in a new tab)</span></a>" +
      (zip ? '<a class="text-link" href="' + esc(zip) + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19h14"/></svg>Download ZIP<span class="visually-hidden"> of ' + esc(w.title) + "</span></a>" : "") +
      "</div></li>";
  }

  function matches(w) {
    if (state.category !== "all" && w.category !== state.category) return false;
    if (!state.query) return true;
    var hay = [w.title, labels[w.category], w.description, w.includes, w.requirements, w.difficulty].concat(w.skills || []).join(" ").toLowerCase();
    return state.query.split(/\s+/).every(function (term) { return hay.indexOf(term) !== -1; });
  }

  function render() {
    var visible = published.filter(matches);
    // Few workbooks: one grid in category order. Many: grouped under category headings.
    var order = data.categories.map(function (c) { return c.id; });
    if (!grouped) {
      visible.sort(function (a, b) { return order.indexOf(a.category) - order.indexOf(b.category); });
      $("[data-directory]").innerHTML = '<ul class="grid">' + visible.map(card).join("") + "</ul>";
      $("[data-empty]").hidden = visible.length > 0;
      return;
    }
    var html = data.categories.map(function (cat) {
      var items = visible.filter(function (w) { return w.category === cat.id; });
      if (!items.length) return "";
      return '<section class="category" aria-labelledby="cat-' + esc(cat.id) + '">' +
        '<h3 class="category-title" id="cat-' + esc(cat.id) + '">' + esc(cat.label) + "</h3>" +
        '<ul class="grid">' + items.map(card).join("") + "</ul></section>";
    }).join("");
    $("[data-directory]").innerHTML = html;
    $("[data-empty]").hidden = visible.length > 0;
  }

  function setupControls() {
    var threshold = (data.site && data.site.showSearchFromCount) || 6;
    if (published.length < threshold) return;
    grouped = true;

    var used = data.categories.filter(function (c) {
      return published.some(function (w) { return w.category === c.id; });
    });
    var chips = [{ id: "all", label: "All" }].concat(used);
    var box = $("[data-chips]");
    box.innerHTML = chips.map(function (c) {
      return '<button type="button" class="chip" data-cat="' + esc(c.id) + '" aria-pressed="' + (c.id === "all") + '">' + esc(c.label) + "</button>";
    }).join("");
    box.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-cat]");
      if (!btn) return;
      state.category = btn.getAttribute("data-cat");
      $all("[data-cat]").forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
      render();
    });
    $("[data-search]").addEventListener("input", function (e) {
      state.query = e.target.value.trim().toLowerCase();
      render();
    });
    $("[data-controls]").hidden = false;
  }

  function setupLinks() {
    var site = data.site || {};
    var gh = safeUrl(site.githubProfileUrl || "", /^github\.com$/);
    if (gh) $all("[data-github-link]").forEach(function (a) { a.href = gh; });

    var yt = safeUrl(site.youtubeUrl || "", /^(www\.|m\.)?youtube\.com$/);
    if (!yt) return; // stays hidden until a real channel URL is configured
    $all("[data-youtube-link]").forEach(function (a) { a.href = yt; a.hidden = false; });
    $all("[data-youtube-section], [data-youtube-item]").forEach(function (el) { el.hidden = false; });
  }

  function setupStats() {
    var total = published.reduce(function (n, w) { return n + (Number(w.problemCount) || 0); }, 0);
    var count = published.length;
    $("[data-stats]").innerHTML = "<strong>" + count + "</strong> free workbook" + (count === 1 ? "" : "s") +
      (total ? " · <strong>" + total + "</strong> practice questions and tasks" : "");
  }

  document.addEventListener("DOMContentLoaded", function () {
    $("[data-year]").textContent = new Date().getFullYear();

    fetch("data/workbooks.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (json) {
        data = json;
        data.categories.forEach(function (c) { labels[c.id] = c.label; });
        published = data.workbooks.filter(function (w) { return w.status === "published" && w.verified === true; });
        setupLinks();
        setupStats();
        setupControls();
        render();
      })
      .catch(function () {
        $("[data-directory]").innerHTML = '<p class="notice">The workbook list could not be loaded. Browse every workbook on ' +
          '<a href="https://github.com/vikasthamke?tab=repositories">GitHub</a>.</p>';
      });
  });
})();
