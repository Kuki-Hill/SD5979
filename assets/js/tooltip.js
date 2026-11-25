/* Bilingual term tooltip — pure JS/CSS, no fetch, no external deps, file:// safe */
(function () {
  var box = document.getElementById("tooltip");
  if (!box) return;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function prefix() {
    var d = parseInt(document.body.getAttribute("data-depth") || "0", 10);
    return d === 0 ? "" : "../";
  }
  function jumpLink(t) {
    var pre = prefix();
    return pre + "lectures/" + t.lecture + ".html#" + t.lecture + "-s" + t.slide;
  }

  function show(el) {
    var key = el.getAttribute("data-term");
    var T = window.SD5979_TERMS || {};
    var t = T[key];
    if (!t) return;
    var flag = t.status === "occurrence_only"
      ? '<span class="tc-flag">仅出现，无独立定义句</span>' : "";
    box.innerHTML =
      '<div class="tc-term">' + esc(t.term) + flag + "</div>" +
      '<div class="tc-zh">' + esc(t.zh) + "</div>" +
      '<div class="tc-en">' + esc(t.en) + "</div>" +
      '<div class="tc-zhd">' + esc(t.zhdef) + "</div>" +
      '<div class="tc-src">定义出处：<a href="' + jumpLink(t) + '">' +
      esc(t.file) + " · Slide " + t.slide + "</a></div>";
    box.classList.add("on");
    box.setAttribute("aria-hidden", "false");
    position(el);
  }
  function position(el) {
    var r = el.getBoundingClientRect();
    var left = Math.min(window.scrollX + r.left, window.scrollX + window.innerWidth - 445);
    var top = window.scrollY + r.bottom + 8;
    var h = box.offsetHeight;
    if (r.bottom + h + 20 > window.innerHeight) {
      top = window.scrollY + r.top - h - 8;
    }
    box.style.left = Math.max(window.scrollX + 8, left) + "px";
    box.style.top = Math.max(window.scrollY + 8, top) + "px";
  }
  function hide() {
    box.classList.remove("on");
    box.setAttribute("aria-hidden", "true");
  }

  document.addEventListener("mouseover", function (e) {
    var el = e.target.closest ? e.target.closest(".term") : null;
    if (el) show(el);
  });
  document.addEventListener("mouseout", function (e) {
    var el = e.target.closest ? e.target.closest(".term") : null;
    if (el) hide();
  });
  document.addEventListener("focusin", function (e) {
    var el = e.target.closest ? e.target.closest(".term") : null;
    if (el) show(el);
  });
  document.addEventListener("focusout", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("term")) hide();
  });
  document.addEventListener("scroll", hide, true);
})();
