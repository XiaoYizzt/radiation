/* 辐射备忘录 — small, dependency-free progressive enhancements. */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var base = root.getAttribute("data-base") || "";
  doc.documentElement.classList.add("js");

  /* ------------------------------------------------------------------ */
  /* Header                                                             */
  /* ------------------------------------------------------------------ */
  var header = doc.querySelector("[data-header]");
  var drawer = doc.querySelector("[data-nav-drawer]");

  function onScrollHeader() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 6);
  }
  window.addEventListener("scroll", onScrollHeader, { passive: true });
  onScrollHeader();

  if (drawer) {
    doc.addEventListener("click", function (event) {
      if (drawer.open && !drawer.contains(event.target)) drawer.open = false;
    });
    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && drawer.open) drawer.open = false;
    });
    drawer.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { drawer.open = false; });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Search index (loaded once, lazily)                                 */
  /* ------------------------------------------------------------------ */
  var indexPromise = null;

  function loadIndex() {
    if (window.SITE_SEARCH) return Promise.resolve(window.SITE_SEARCH);
    if (indexPromise) return indexPromise;
    indexPromise = new Promise(function (resolve, reject) {
      var script = doc.createElement("script");
      script.src = base + "js/search-index.js";
      script.async = true;
      script.onload = function () { resolve(window.SITE_SEARCH || []); };
      script.onerror = function () { reject(new Error("search index failed to load")); };
      doc.head.appendChild(script);
    });
    return indexPromise;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function highlight(text, terms) {
    var safe = escapeHtml(text);
    terms.forEach(function (term) {
      if (!term) return;
      try {
        safe = safe.replace(new RegExp(escapeRegExp(escapeHtml(term)), "gi"), function (match) {
          return "<mark>" + match + "</mark>";
        });
      } catch (error) { /* ignore malformed term */ }
    });
    return safe;
  }

  function snippetFor(item, terms) {
    var body = item.b || "";
    var lower = body.toLowerCase();
    var at = -1;
    for (var i = 0; i < terms.length; i++) {
      var pos = lower.indexOf(terms[i]);
      if (pos !== -1 && (at === -1 || pos < at)) at = pos;
    }
    if (at === -1) return item.d || body.slice(0, 160);
    var start = Math.max(0, at - 60);
    var before = body.slice(start, at);
    var boundary = Math.max(before.lastIndexOf("。"), before.lastIndexOf("；"),
      before.lastIndexOf("！"), before.lastIndexOf("？"), before.lastIndexOf("\n"));
    if (boundary >= 0) start += boundary + 1;
    var end = Math.min(body.length, at + 170);
    var after = body.slice(at, end);
    var stop = -1;
    ["。", "；", "！", "？", "\n"].forEach(function (mark) {
      var position = after.indexOf(mark);
      if (position !== -1 && (stop === -1 || position < stop)) stop = position;
    });
    if (stop !== -1) end = at + stop + 1;
    return (start > 0 ? "…" : "") + body.slice(start, end).trim() + (end < body.length ? "…" : "");
  }

  function runSearch(items, query, section) {
    var q = query.trim().toLowerCase();
    if (!q) return [];
    var terms = q.split(/\s+/).filter(Boolean).slice(0, 6);
    var output = [];
    items.forEach(function (item) {
      if (section && item.s !== section) return;
      var title = (item.t || "").toLowerCase();
      var tags = (item.k || "").toLowerCase();
      var desc = (item.d || "").toLowerCase();
      var body = (item.b || "").toLowerCase();
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var term = terms[i];
        var inTitle = title.indexOf(term) !== -1;
        var inTags = tags.indexOf(term) !== -1;
        var inDesc = desc.indexOf(term) !== -1;
        var inBody = body.indexOf(term) !== -1;
        if (!inTitle && !inTags && !inDesc && !inBody) return;
        score += (inTitle ? 16 : 0) + (inTags ? 8 : 0) + (inDesc ? 4 : 0) + (inBody ? 1 : 0);
      }
      if (title.indexOf(q) !== -1) score += 30;
      if (title === q) score += 60;
      output.push({ item: item, score: score });
    });
    output.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return a.item.t.length - b.item.t.length;
    });
    return output;
  }

  function resultMarkup(item, terms) {
    var href = base + item.u;
    var section = item.sn || "";
    return '<a class="search-result" href="' + escapeHtml(href) + '">' +
      '<span class="result-path">' + escapeHtml(section) + (item.l ? " · " + escapeHtml(item.l) : "") + '</span>' +
      '<h3>' + highlight(item.t, terms) + '</h3>' +
      '<p>' + highlight(snippetFor(item, terms), terms) + '</p></a>';
  }

  function renderResults(container, results, terms, query, limit) {
    if (!query.trim()) {
      container.innerHTML = '<div class="search-empty"><p>输入标题、仪器型号、核素或技术关键词开始搜索。</p>' +
        '<p class="muted">也可以试试：希沃特、能量补偿、氡、Cs-137、PM1405、能谱。</p></div>';
      return;
    }
    if (!results.length) {
      container.innerHTML = '<div class="search-empty"><p>没有找到与“' + escapeHtml(query) + '”匹配的内容。</p>' +
        '<p class="muted">试试更短的关键词，或从 <a href="' + base + 'sitemap.html">站点地图</a> 浏览全部页面。</p></div>';
      return;
    }
    var shown = results.slice(0, limit || 30);
    container.innerHTML = '<div class="search-status">' + results.length + ' 条结果</div>' +
      shown.map(function (entry) { return resultMarkup(entry.item, terms); }).join("");
  }

  var dialog = doc.querySelector("[data-search-dialog]");
  var dialogInput = dialog ? dialog.querySelector("[data-search-input]") : null;
  var dialogResults = dialog ? dialog.querySelector("[data-search-results]") : null;
  var dialogFilters = dialog ? dialog.querySelector("[data-search-filters]") : null;
  var allItems = null;
  var activeSection = "";
  var selectedIndex = -1;

  function updateDialog() {
    if (!dialogInput || !dialogResults || !allItems) return;
    var query = dialogInput.value;
    var terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean).slice(0, 6);
    var results = runSearch(allItems, query, activeSection);
    renderResults(dialogResults, results, terms, query, 30);
    selectedIndex = -1;
  }

  function openDialog() {
    if (!dialog) return false;
    if (typeof dialog.showModal === "function") {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute("open", "open");
    }
    loadIndex().then(function (items) {
      allItems = items;
      updateDialog();
    }).catch(function () {
      if (dialogResults) dialogResults.innerHTML = '<div class="search-empty"><p>搜索索引加载失败。请直接前往 <a href="' + base + 'search.html">搜索页面</a>，或从 <a href="' + base + 'sitemap.html">站点地图</a> 浏览。</p></div>';
    });
    window.setTimeout(function () { if (dialogInput) dialogInput.focus(); }, 30);
    return true;
  }

  function closeDialog() {
    if (!dialog) return;
    if (typeof dialog.close === "function" && dialog.open) dialog.close();
    else dialog.removeAttribute("open");
  }

  doc.querySelectorAll("[data-search-open]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (event.button !== 0) return;
      if (openDialog()) event.preventDefault();
    });
  });

  if (dialog) {
    dialog.querySelectorAll("[data-search-close]").forEach(function (button) {
      button.addEventListener("click", closeDialog);
    });
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) closeDialog();
    });
    if (dialogInput) {
      dialogInput.addEventListener("input", updateDialog);
      dialogInput.addEventListener("keydown", function (event) {
        var results = dialogResults ? Array.prototype.slice.call(dialogResults.querySelectorAll(".search-result")) : [];
        if (event.key === "ArrowDown" && results.length) {
          event.preventDefault();
          selectedIndex = Math.min(results.length - 1, selectedIndex + 1);
        } else if (event.key === "ArrowUp" && results.length) {
          event.preventDefault();
          selectedIndex = Math.max(0, selectedIndex - 1);
        } else if (event.key === "Enter" && selectedIndex >= 0 && results[selectedIndex]) {
          event.preventDefault();
          window.location.href = results[selectedIndex].href;
          return;
        } else {
          return;
        }
        results.forEach(function (el, i) { el.classList.toggle("is-selected", i === selectedIndex); });
        if (results[selectedIndex]) results[selectedIndex].scrollIntoView({ block: "nearest" });
      });
    }
    if (dialogFilters) {
      dialogFilters.addEventListener("click", function (event) {
        var chip = event.target.closest("[data-section]");
        if (!chip) return;
        activeSection = chip.getAttribute("data-section") || "";
        dialogFilters.querySelectorAll(".chip").forEach(function (button) {
          button.classList.toggle("is-active", button === chip);
        });
        updateDialog();
      });
    }
  }

  doc.addEventListener("keydown", function (event) {
    var tag = (event.target.tagName || "").toLowerCase();
    var typing = tag === "input" || tag === "textarea" || tag === "select" || event.target.isContentEditable;
    if (typing) return;
    if (event.key === "/" || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k")) {
      if (openDialog()) event.preventDefault();
    }
  });

  /* ------------------------------------------------------------------ */
  /* Search page                                                        */
  /* ------------------------------------------------------------------ */
  var pageInput = doc.querySelector("[data-search-page-input]");
  var pageResults = doc.querySelector("[data-search-page-results]");
  var pageFilters = null;

  function renderPageFilters(items) {
    if (!pageResults || pageFilters) return;
    var sections = [];
    var seen = {};
    items.forEach(function (item) {
      if (!item.s || item.s === "home" || item.s === "search") return;
      if (!seen[item.s]) { seen[item.s] = true; sections.push([item.s, item.sn]); }
    });
    pageFilters = doc.createElement("div");
    pageFilters.className = "search-filters search-filters-page";
    pageFilters.innerHTML = '<button type="button" class="chip is-active" data-section="">全部</button>' +
      sections.map(function (pair) {
        return '<button type="button" class="chip" data-section="' + escapeHtml(pair[0]) + '">' + escapeHtml(pair[1]) + '</button>';
      }).join("");
    pageResults.parentNode.insertBefore(pageFilters, pageResults);
    pageFilters.addEventListener("click", function (event) {
      var chip = event.target.closest("[data-section]");
      if (!chip) return;
      activeSection = chip.getAttribute("data-section") || "";
      pageFilters.querySelectorAll(".chip").forEach(function (button) {
        button.classList.toggle("is-active", button === chip);
      });
      updatePageSearch(true);
    });
  }

  function updatePageSearch(fromInput) {
    if (!pageResults || !allItems) return;
    var query = pageInput ? pageInput.value : "";
    var terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean).slice(0, 6);
    var results = runSearch(allItems, query, activeSection);
    renderResults(pageResults, results, terms, query, 80);
    if (fromInput) {
      try {
        var url = new URL(window.location.href);
        if (query.trim()) url.searchParams.set("q", query.trim());
        else url.searchParams.delete("q");
        window.history.replaceState(null, "", url.toString());
      } catch (error) { /* file:// may refuse history updates */ }
    }
  }

  if (pageInput && pageResults) {
    var params = new URLSearchParams(window.location.search);
    var initial = params.get("q") || "";
    if (initial) pageInput.value = initial;
    loadIndex().then(function (items) {
      allItems = items;
      renderPageFilters(items);
      updatePageSearch(false);
    }).catch(function () {
      pageResults.innerHTML = '<p class="search-empty">搜索索引加载失败。请从 <a href="' + base + 'sitemap.html">站点地图</a> 浏览全部页面。</p>';
    });
    pageInput.addEventListener("input", function () { updatePageSearch(true); });
    var pageForm = doc.querySelector("[data-search-page-form]");
    if (pageForm) {
      pageForm.addEventListener("submit", function (event) {
        event.preventDefault();
        updatePageSearch(true);
      });
    }
  }

  /* Random knowledge tip, adapted from the legacy document.write version */
  var tipBox = doc.querySelector("[data-tip]");
  if (tipBox) {
    var tips = tipBox.querySelectorAll(".tip-item");
    if (tips.length > 1) {
      var chosen = Math.floor(Math.random() * tips.length);
      tips.forEach(function (tip, index) { tip.hidden = index !== chosen; });
    }
  }

  /* Legacy visitor-IP widget (the original used document.write + ipify) */
  var welcome = doc.querySelector(".prose > p");
  if (welcome && welcome.textContent.indexOf("欢迎访问数据库") !== -1) {
    var ipSpan = doc.createElement("span");
    ipSpan.className = "visitor-ip";
    welcome.appendChild(doc.createTextNode(" "));
    welcome.appendChild(ipSpan);
    if (window.fetch && window.location.protocol !== "file:") {
      fetch("https://api.ipify.org?format=json").then(function (response) {
        return response.json();
      }).then(function (data) {
        if (data && data.ip) ipSpan.textContent = "访问IP: " + data.ip;
      }).catch(function () { /* offline or blocked: leave the line empty */ });
    }
  }

  /* Legacy data page clock (restores the old showLeftTime widget)      */
  var clock = doc.getElementById("show");
  if (clock) {
    var tickClock = function () {
      var now = new Date();
      var pad = function (value) { return value < 10 ? "0" + value : String(value); };
      clock.textContent = now.getFullYear() + "年" + (now.getMonth() + 1) + "月" +
        now.getDate() + "日 " + pad(now.getHours()) + ":" + pad(now.getMinutes()) +
        ":" + pad(now.getSeconds());
    };
    tickClock();
    window.setInterval(tickClock, 1000);
  }

  /* ------------------------------------------------------------------ */
  /* WESViewer on file://                                               */
  /* ------------------------------------------------------------------ */
  if (doc.body.classList.contains("page-viewer") && window.location.protocol === "file:") {
    var viewerBar = doc.querySelector(".viewer-bar");
    if (viewerBar) {
      var hint = doc.createElement("p");
      hint.className = "viewer-hint";
      hint.innerHTML = "当前页面以 <code>file://</code> 方式打开。浏览器会阻止读取本地光谱 XML 文件，" +
        "因此下方图表可能为空；请把站点部署到任意静态 HTTP 托管空间，或使用本地静态服务器访问，以完整加载光谱。";
      viewerBar.insertAdjacentElement("afterend", hint);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Article table of contents                                          */
  /* ------------------------------------------------------------------ */
  var toc = doc.querySelector("[data-toc]");
  if (toc) {
    var links = Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]'));
    var targets = links.map(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      return doc.getElementById(id);
    });
    var ticking = false;
    function updateToc() {
      ticking = false;
      var offset = 110;
      var current = -1;
      for (var i = 0; i < targets.length; i++) {
        if (targets[i] && targets[i].getBoundingClientRect().top <= offset) current = i;
      }
      links.forEach(function (link, i) { link.classList.toggle("is-active", i === current); });
    }
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; window.requestAnimationFrame(updateToc); }
    }, { passive: true });
    updateToc();
  }

  /* ------------------------------------------------------------------ */
  /* Tables: indicate horizontal overflow                               */
  /* ------------------------------------------------------------------ */
  var scrollers = Array.prototype.slice.call(doc.querySelectorAll(".table-scroll"));
  function markTables() {
    scrollers.forEach(function (box) {
      var scrollable = box.scrollWidth > box.clientWidth + 2;
      box.classList.toggle("is-scrollable", scrollable);
      var hint = box.nextElementSibling;
      var hasHint = hint && hint.classList.contains("table-hint");
      if (scrollable && !hasHint) {
        var note = doc.createElement("p");
        note.className = "table-hint";
        note.textContent = "表格较宽，可左右滑动查看完整内容";
        box.insertAdjacentElement("afterend", note);
      } else if (!scrollable && hasHint) {
        hint.remove();
      }
    });
  }
  if (scrollers.length) {
    markTables();
    window.addEventListener("resize", markTables, { passive: true });
  }

  /* ------------------------------------------------------------------ */
  /* Image lightbox                                                     */
  /* ------------------------------------------------------------------ */
  var lightbox = doc.querySelector("[data-lightbox]");
  var lightboxImg = lightbox ? lightbox.querySelector("[data-lightbox-img]") : null;
  var lightboxCap = lightbox ? lightbox.querySelector("[data-lightbox-caption]") : null;

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.hidden = true;
    doc.body.style.overflow = "";
    if (lightboxImg) lightboxImg.removeAttribute("src");
  }

  if (lightbox && lightboxImg) {
    doc.querySelectorAll(".prose img.content-img").forEach(function (img) {
      if (img.closest("a")) return;
      img.style.cursor = "zoom-in";
      img.addEventListener("click", function () {
        lightbox.hidden = false;
        lightboxImg.src = img.currentSrc || img.src;
        lightboxImg.alt = img.alt || "";
        lightboxCap.textContent = img.alt || "";
        doc.body.style.overflow = "hidden";
      });
    });
    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) closeLightbox();
    });
    lightbox.querySelectorAll("[data-lightbox-close]").forEach(function (button) {
      button.addEventListener("click", closeLightbox);
    });
    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !lightbox.hidden) closeLightbox();
    });
  }

  /* ------------------------------------------------------------------ */
  /* Reading progress                                                   */
  /* ------------------------------------------------------------------ */
  if (doc.querySelector(".page-article")) {
    var bar = doc.createElement("div");
    bar.className = "reading-progress";
    bar.setAttribute("aria-hidden", "true");
    doc.body.appendChild(bar);
    var progressTicking = false;
    function updateProgress() {
      progressTicking = false;
      var max = doc.documentElement.scrollHeight - window.innerHeight;
      var value = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
      bar.style.transform = "scaleX(" + value + ")";
    }
    window.addEventListener("scroll", function () {
      if (!progressTicking) { progressTicking = true; window.requestAnimationFrame(updateProgress); }
    }, { passive: true });
    updateProgress();
  }
})();
