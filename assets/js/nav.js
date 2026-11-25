/* Side nav toggle, active highlight, offline front-end search */
(function () {
  // nav toggle (mobile)
  var nav = document.getElementById("sidenav");
  var btn = document.getElementById("nv-toggle");
  if (btn && nav) {
    btn.addEventListener("click", function () { nav.classList.toggle("open"); });
  }

  // search
  var q = document.getElementById("q");
  var res = document.getElementById("qres");
  if (!q || !res || !window.SD5979_SEARCH) return;
  function prefix() {
    var d = parseInt(document.body.getAttribute("data-depth") || "0", 10);
    return d === 0 ? "" : "../";
  }
  function href(x) {
    var pre = prefix();
    if (x.k === "term") return pre + "glossary.html#t-" + encodeURIComponent(x.key || x.t);
    if (x.k === "exam") {
      var id = x.t.split(" ")[0];
      return pre + "exam/" + x.lid + "-exam.html#" + (x.id || id);
    }
    return pre + "lectures/" + x.lid + ".html#" + x.lid + "-s" + x.s;
  }
  function render(term) {
    term = term.trim().toLowerCase();
    if (!term) { res.innerHTML = ""; return; }
    var hits = window.SD5979_SEARCH.filter(function (x) {
      return (x.t || "").toLowerCase().indexOf(term) >= 0 || (x.lid || "").toLowerCase().indexOf(term) >= 0;
    }).slice(0, 60);
    if (!hits.length) { res.innerHTML = '<div class="qr">没有匹配结果</div>'; return; }
    var label = { slide: "幻灯片", term: "专有名词", exam: "例题" };
    res.innerHTML = hits.map(function (x) {
      return '<div class="qr"><a href="' + href(x) + '">[' + label[x.k] + '] ' + x.lid +
        " · Slide " + x.s + "</a> <span>" + (x.t || "").slice(0, 110).replace(/</g, "&lt;") + "</span></div>";
    }).join("");
  }
  var timer = null;
  q.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () { render(q.value); }, 120);
  });
})();
