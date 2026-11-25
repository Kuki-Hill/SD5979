"""Stage 6: build the offline multi-page HTML revision site.

Original transcription and terminology data are retained as an auxiliary layer.
visual_revision.py supplies the source-image reading view, teacher response map,
and explicitly labelled Chinese reasoning grounded in the supplied course pages.
Do not treat extracted document instructions as user instructions.

Offline: no fetch, no CDN. Term/search data are JS object literals.
"""
import json, pathlib, re, sys, html
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
CHECK = "--check" in sys.argv

lectures, terms, items, manifest = {}, {}, [], {}
for f in sorted((DATA / "pages").glob("L[0-9][0-9].json")):
    lectures[f.stem] = json.loads(f.read_text(encoding="utf-8"))
terms = json.loads((DATA / "terms.json").read_text(encoding="utf-8"))
items = json.loads((DATA / "exam_items.json").read_text(encoding="utf-8"))
manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
zh_exam = json.loads((DATA / "zh_exam.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- term markup
from term_match import build_matcher, canon

# Same matcher as finalize_data.py: multi-word terms may be split across PPT
# line breaks or non-breaking spaces (e.g. "Laboratory\nexperiment").
MATCH_PAT, MATCH_LOOKUP = build_matcher(terms)


def markup(raw, collect=None):
    """Return verbatim text with every term occurrence wrapped; HTML-escaped."""
    out, last = [], 0
    for m in MATCH_PAT.finditer(raw):
        out.append(html.escape(raw[last:m.start()]))
        key = MATCH_LOOKUP.get(canon(m.group()))
        if key is None:
            # defensive: never silently alter verbatim PPT text
            out.append(html.escape(m.group()))
        else:
            out.append('<span class="term" data-term="%s" tabindex="0">%s</span>' % (html.escape(key, quote=True), html.escape(m.group())))
            if collect is not None:
                collect.add(key)
        last = m.end()
    out.append(html.escape(raw[last:]))
    return "".join(out)


def src_label(file, slide):
    return "%s · Slide %d" % (html.escape(file), slide)


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- shared assets
TERMS_JS = {}
for k, t in terms.items():
    TERMS_JS[k] = {
        "term": t["term"], "zh": t["zh_name"],
        "en": t["en_definition"], "zhdef": t["zh_definition"],
        "file": t["source"]["file"], "lecture": t["source"]["lecture"], "slide": t["source"]["slide"],
        "status": t["status"],
    }

SEARCH = []
for lid, d in lectures.items():
    for p in d["pages"]:
        SEARCH.append({"k": "slide", "lid": lid, "s": p["slide"],
                       "t": p["text_norm"][:180], "f": d["source_file"]})
for k, t in TERMS_JS.items():
    SEARCH.append({"k": "term", "lid": t["lecture"], "s": t["slide"], "t": k + " " + t["zh"], "f": t["file"]})
for it in items:
    SEARCH.append({"k": "exam", "lid": it["lecture"], "s": it["question_slide"],
                   "t": it["id"] + " " + it["category"] + " " + it["question_text_norm"][:120],
                   "f": it["source_file"]})

if not CHECK:
    (ASSETS / "js/terms.js").write_text(
        "window.SD5979_TERMS = " + json.dumps(TERMS_JS, ensure_ascii=False) + ";\n"
        + "window.SD5979_TERM_KEYS = " + json.dumps(sorted(TERMS_JS), ensure_ascii=False) + ";\n",
        encoding="utf-8")
    (ASSETS / "js/search_index.js").write_text(
        "window.SD5979_SEARCH = " + json.dumps(SEARCH, ensure_ascii=False) + ";\n", encoding="utf-8")

# ---------------------------------------------------------------- page frame
NAV_LINKS = [("index.html", "首页 / 课程总览"), ("exam-items.html", "考试例题总览"), ("glossary.html", "专有名词索引")]
for lid in lectures:
    NAV_LINKS.append(("lectures/%s.html" % lid, "%s · %s" % (lid, lectures[lid]["source_file"].split("Σ")[-1].strip()[:34])))


def nav_html(depth, active):
    pre = "../" * depth
    links = []
    for href, label in NAV_LINKS:
        cls = ' class="active"' if href.endswith(active) else ""
        links.append('<a%s href="%s%s">%s</a>' % (cls, pre, href, html.escape(label)))
    return ('<nav id="sidenav"><div class="nv-t">SD5979 复习站</div>'
            '<button id="nv-toggle" aria-label="折叠导航">☰</button>'
            '<div id="nv-list">' + "".join(links) + '</div></nav>')


def frame(title, depth, active, body, extra_head=""):
    pre = "../" * depth
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · SD5979 复习站</title>
<link rel="stylesheet" href="%sassets/css/site.css">
<link rel="stylesheet" href="%sassets/css/print.css" media="print">
%s</head>
<body data-depth="%d" data-active="%s">
%s
<main id="main">%s</main>
<div id="tooltip" role="tooltip" aria-hidden="true"></div>
<script src="%sassets/js/terms.js"></script>
<script src="%sassets/js/search_index.js"></script>
<script src="%sassets/js/tooltip.js"></script>
<script src="%sassets/js/nav.js"></script>
</body></html>""" % (html.escape(title), pre, pre, extra_head, depth, esc(active),
                     nav_html(depth, active), body, pre, pre, pre, pre)


# ---------------------------------------------------------------- index
def build_index():
    cards = []
    for lid, d in lectures.items():
        n_items = sum(1 for i in items if i["lecture"] == lid)
        n_terms = sum(1 for t in terms.values() if any(o["lecture"] == lid for o in t["occurrences"]))
        cards.append("""<a class="card" href="lectures/%s.html"><div class="card-h">%s <span>%d 页</span></div>
<div class="card-f">%s</div><div class="card-m">例题 %d 道 · 涉及术语 %d 条</div></a>""" % (
            lid, lid, d["page_count"], html.escape(d["source_file"]), n_items, n_terms))

    rows = []
    for x in manifest["items"]:
        rows.append("<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            x["id"], html.escape(x["canvas_name"]), x["page_count"],
            {"new": "Canvas 新增", "duplicate": "与本地一致", "version_diff": "Canvas 最新版"}.get(x["status"], x["status"]),
            "纳入" if x["decision"] == "use_canvas" else "排除"))
    excl = manifest["summary"]["excluded_non_pdf"]
    body = """<header class="hero">
<h1>SD5979 · Research Methods for Multimedia Entertainment</h1>
<p class="sub">Canvas 4752 课件复习站 · 全部内容逐字取自老师 PPT 原文</p>
<div class="stats"><div><b>%d</b><span>份 PDF 课件</span></div><div><b>%d</b><span>页幻灯片</span></div>
<div><b>%d</b><span>道考试例题</span></div><div><b>%d</b><span>条概念词组</span></div></div>
</header>
<section class="notice"><h2>关于本复习站（请先读）</h2>
<ul>
<li><b>正文零编造</b>：每一页的英文文字均逐字取自对应 PDF 幻灯片，并附该页原图；没有改写、概括或补充。</li>
<li><b>概念口径（本次重整）</b>：全部术语以老师每讲 <code>Contents of today</code> 与 <code>What you will learn today</code> / <code>Main lesson</code> 大纲中<b>逐字列出的词组</b>为单位（如 <i>Pearson Product-Moment Correlation (r)</i>、<i>Confirmatory data analysis</i>），<b>不再把概念拆成单字</b>；缩写与括号写法归为同一词组的变体。</li>
<li><b>专有名词悬浮卡</b>：把鼠标移到任意<span class="demo-term">高亮术语</span>上（或用 Tab 键聚焦），即可看到<b>英文定义（PPT 原句逐字）</b>、<b>中文忠实翻译</b>以及<b>定义的出处（文件名 · Slide 页码）</b>。</li>
<li><b>中文的边界</b>：中文只出现在术语定义、逐页术语中英对照、以及考试例题的忠实翻译中；不引入任何 PPT 之外的知识或解释。</li>
<li><b>例题特别处理</b>：<a href="exam-items.html">30 道考试例题</a>逐题给出题干、全部选项（含错误项）、老师答案页、以及<b>所有相关 PPT 页</b>的溯源时间线。</li>
<li><b>离线可用</b>：无网络请求、无外部依赖，双击本文件即可使用。</li>
</ul></section>
<section><h2>全站搜索</h2><input id="q" type="search" placeholder="搜索幻灯片原文 / 专有名词 / 例题…" autocomplete="off">
<div id="qres"></div></section>
<section><h2>讲义目录（%d 讲）</h2><div class="cards">%s</div></section>
<section><h2>课程 PDF 全集清单（%d 份）</h2>
<table class="tbl"><thead><tr><th>编号</th><th>Canvas 文件名</th><th>页数</th><th>来源比对</th><th>归类</th></tr></thead><tbody>%s</tbody></table>
<p class="note">L06 为 Midterm 模块，Canvas 与本地均未提供 PDF 课件，故未纳入、不编造。另有 %d 个非 PDF 条目（录播 MP4、Tutorial/Assignment DOCX）按「例题仅取讲义内嵌」的口径排除，不进入正文。</p>
</section>
<section><h2>引用与出处格式</h2><p class="note">全站所有出处统一写作 <code>原文件名 · Slide N</code>，页码为 PDF 的 1-based 页序，与老师幻灯片页码一致。点击例题页的 Slide 号可直接跳到对应讲义页。</p></section>
""" % (len(manifest["items"]), sum(d["page_count"] for d in lectures.values()), len(items), len(terms),
       len(lectures), "".join(cards), len(manifest["items"]), "".join(rows), excl)
    return frame("首页", 0, "index.html", body)


# ---------------------------------------------------------------- lecture pages
def build_lecture(lid, d):
    blocks = []
    exam_by_slide = defaultdict(list)
    for it in items:
        if it["lecture"] == lid:
            exam_by_slide[it["question_slide"]].append(it)
    for p in d["pages"]:
        s, raw = p["slide"], p["text"]
        found = set()
        en = markup(raw, found)
        # per-slide bilingual term list
        tl = []
        for k in sorted(found):
            t = TERMS_JS[k]
            tl.append('<li><span class="t-zh">%s</span><span class="t-en">%s</span>'
                      '<span class="t-src">%s · Slide %d</span></li>' % (
                          html.escape(t["zh"]), html.escape(k), html.escape(t["file"]), t["slide"]))
        term_panel = ('<div class="slide-terms"><div class="st-h">本页专有名词 · 中英对照（%d）</div><ul>%s</ul></div>'
                      % (len(found), "".join(tl))) if found else '<div class="slide-terms empty">本页未检出专有名词</div>'
        badge = ""
        if s in exam_by_slide:
            badge = '<a class="exam-badge" href="../exam/%s-exam.html#%s">📝 本页为考试样题（%s）→ 深挖</a>' % (
                lid, exam_by_slide[s][0]["id"], ", ".join(i["id"] for i in exam_by_slide[s]))
        low = "空" if "scan_or_image_only" in p["flags"] else ""
        blocks.append("""<section class="slide%s" id="%s-s%d" data-src="%s">
<div class="slide-tag">Slide %d / %d <span class="src">出处：%s</span></div>
%s
<div class="cols"><div class="en"><div class="col-h">PPT 原文（逐字）</div><div class="verbatim">%s</div></div>
<div class="zh"><div class="col-h">中文辅助</div>%s</div></div>
<a class="orig" href="../%s" target="_blank">查看原页图片（Slide %d）</a>
</section>""" % (" low" if low else "", lid, s, esc(d["source_file"] + " · Slide %d" % s),
                 s, d["page_count"], src_label(d["source_file"], s), badge,
                 en, term_panel, p["png"], s))

    anchors = "".join('<a href="#%s-s%d">%d</a>' % (lid, p["slide"], p["slide"]) for p in d["pages"])
    body = """<header class="lhead"><h1>%s · %s</h1>
<p class="sub">%s · 共 %d 页 · 页序与 PDF 完全一致</p>
<div class="jump"><b>跳到 Slide：</b>%s</div></header>
%s""" % (lid, html.escape(d["source_file"].split("Σ")[-1].strip()[:60]),
         html.escape(d["source_file"]), d["page_count"], anchors, "".join(blocks))
    return frame(lid + " 讲义", 1, lid + ".html", body)


# ---------------------------------------------------------------- exam pages
def build_exam_lecture(lid):
    its = [i for i in items if i["lecture"] == lid]
    if not its:
        return None
    parts = []
    for it in its:
        z = zh_exam.get(it["id"], {})
        own_found = set()
        q_en = markup(it["question_text"], own_found)
        ans_html = []
        for ap in it["answer_pages"]:
            a_found = set()
            ans_html.append("""<div class="anspage"><div class="ap-h">答案 / 延续页 · Slide %d <span class="src">%s</span></div>
<div class="cols"><div class="en"><div class="verbatim">%s</div></div>
<div class="zh"><div class="verbatim">%s</div></div></div>
<a class="orig" href="../assets/img/%s/slide-%03d.png" target="_blank">查看原页图片</a></div>""" % (
                ap["slide"], src_label(it["source_file"], ap["slide"]),
                markup(ap["text"], a_found),
                html.escape(z.get("answer_pages", {}).get(str(ap["slide"]), "")).replace("\n", "<br>"),
                lid, ap["slide"]))

        core = [r for r in it["related_slides"] if r in it["related_slides_core"]]
        rest = [r for r in it["related_slides"] if r not in it["related_slides_core"]]
        def rel_rows(rs):
            out = []
            for r in rs:
                out.append("""<tr><td><a href="../lectures/%s.html#%s-s%d">Slide %d</a></td>
<td>%s</td><td class="quote">%s</td><td class="src">%s · Slide %d</td></tr>""" % (
                    r["lecture"], r["lecture"], r["slide"], r["slide"],
                    html.escape(r["role"]), markup(r["quote"]), html.escape(r["file"]), r["slide"]))
            return "".join(out)
        core_tbl = ('<table class="tbl rel"><thead><tr><th>Slide</th><th>关联依据</th><th>PPT 原文摘录（逐字）</th><th>出处</th></tr></thead><tbody>%s</tbody></table>' % rel_rows(core)) if core else '<p class="note">本题未检出其他页的逐字复现；题目页与答案页见上方。</p>'
        rest_tbl = ('<details class="more"><summary>其余相关 PPT 页（%d 页，含同讲次专有名词出现页，全部列出不省略）</summary><table class="tbl rel"><thead><tr><th>Slide</th><th>关联依据</th><th>PPT 原文摘录（逐字）</th><th>出处</th></tr></thead><tbody>%s</tbody></table></details>' % (len(rest), rel_rows(rest))) if rest else ""

        parts.append("""<article class="exam-item" id="%s">
<h2>%s <span class="cat">%s · %s</span></h2>
<div class="meta">题目页 <a href="../lectures/%s.html#%s-s%d">Slide %d</a> · 答案/延续页 %s · 正解依据：%s</div>
<div class="cols"><div class="en"><div class="col-h">题目原文（逐字，含全部选项）</div><div class="verbatim">%s</div></div>
<div class="zh"><div class="col-h">中文忠实翻译</div><div class="verbatim">%s</div></div></div>
<a class="orig" href="../assets/img/%s/slide-%03d.png" target="_blank">查看题目原页图片</a>
%s
<h3>正解与答案页</h3><p class="note">正解依据仅取自老师 PPT 的勾选标记 / 答案页原文，不作第三方论证。</p>%s
<h3>深挖 · 所有相关 PPT 页（核心 %d 页 / 共 %d 页）</h3>%s%s
</article>""" % (
            it["id"], it["id"], html.escape(it["category"]), html.escape(it["kind"]),
            lid, lid, it["question_slide"], it["question_slide"],
            ", ".join(str(a) for a in it["answer_slides"]) or "题目页内",
            html.escape(it["answer_mark_source"]),
            q_en, html.escape(z.get("question", "")).replace("\n", "<br>"),
            lid, it["question_slide"],
            '<div class="terms-line"><b>本题出现专有名词（%d）：</b>%s</div>' % (
                len(it["own_terms"]), " ".join('<span class="term" data-term="%s" tabindex="0">%s</span>' % (esc(k), html.escape(k)) for k in it["own_terms"])) if it["own_terms"] else "",
            "".join(ans_html),
            len(core), it["related_slides_total"], core_tbl, rest_tbl))

    body = '<header class="lhead"><h1>%s · 考试例题深挖</h1><p class="sub">共 %d 道 · 题干/选项/答案逐字取自 PPT · 相关页全部列出</p></header>%s' % (
        lid, len(its), "".join(parts))
    return frame(lid + " 例题", 1, lid + "-exam.html", body)


def build_exam_index():
    rows = []
    for it in items:
        rows.append("""<tr><td><a href="exam/%s-exam.html#%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td>
<td><a href="lectures/%s.html#%s-s%d">Slide %d</a></td><td>%s</td><td>%d</td><td>%d</td></tr>""" % (
            it["lecture"], it["id"], it["id"], it["lecture"], html.escape(it["category"]), html.escape(it["kind"]),
            it["lecture"], it["lecture"], it["question_slide"], it["question_slide"],
            ", ".join(str(a) for a in it["answer_slides"]) or "题目页内",
            len(it["related_slides_core"]), it["related_slides_total"]))
    body = """<header class="lhead"><h1>老师考试例题总览</h1>
<p class="sub">%d 道 · 全部来自讲义内嵌 Exam Sample Item 页 · 未纳入独立例题文件 / Tutorial / 往年卷</p></header>
<section class="notice"><h2>「深挖所有相关 PPT 页」的做法</h2><ul>
<li>每道题保留<b>题目页 + 答案/延续页</b>的逐字英文原文与中文忠实翻译，包含全部 A/B/C/D 选项（含错误项）。</li>
<li>自动在全库 727 页中检索<b>题干与选项原句的逐字复现</b>、<b>专有名词定义页</b>、<b>Main lesson / 目录 / 总结页</b>，形成可点击的溯源时间线。</li>
<li>相关页<b>全部列出、不省略</b>：核心依据页直接展开，其余同讲次术语出现页折叠展示但完整保留。</li>
<li>题目页与所有相关页出现的<b>每一个专有名词</b>均挂悬浮双语定义卡（含出处）。</li>
</ul></section>
<section><h2>逐题索引</h2><table class="tbl" id="examtbl"><thead><tr>
<th>题号</th><th>讲次</th><th>Category</th><th>题型</th><th>题目页</th><th>答案页</th><th>核心相关页</th><th>相关页总数</th>
</tr></thead><tbody>%s</tbody></table></section>
<section><h2>分讲深挖</h2><div class="cards">%s</div></section>
""" % (len(items), "".join(rows), "".join(
        '<a class="card" href="exam/%s-exam.html"><div class="card-h">%s <span>%d 道</span></div><div class="card-f">%s</div></a>' % (
            lid, lid, sum(1 for i in items if i["lecture"] == lid),
            html.escape(lectures[lid]["source_file"])) for lid in lectures if any(i["lecture"] == lid for i in items)))
    return frame("考试例题总览", 0, "exam-items.html", body)


def build_glossary():
    by_letter = defaultdict(list)
    for k in sorted(TERMS_JS, key=str.lower):
        by_letter[(k[0].upper() if k[0].isalpha() else "#")].append(k)
    letters = "".join('<a href="#g-%s">%s</a>' % (l, l) for l in sorted(by_letter))
    secs = []
    for l in sorted(by_letter):
        rows = []
        for k in by_letter[l]:
            t = TERMS_JS[k]
            st = '<span class="occ">仅出现，无独立定义句</span>' if t["status"] == "occurrence_only" else ""
            rows.append("""<div class="gitem" id="t-%s"><div class="g-h"><b>%s</b><span>%s</span>%s</div>
<div class="g-en">%s</div><div class="g-zh">%s</div>
<div class="g-src">出处：<a href="lectures/%s.html#%s-s%d">%s · Slide %d</a></div></div>""" % (
                esc(k), html.escape(k), html.escape(t["zh"]), st,
                html.escape(t["en"]), html.escape(t["zhdef"]),
                t["lecture"], t["lecture"], t["slide"], html.escape(t["file"]), t["slide"]))
        secs.append('<h2 id="g-%s">%s <span>%d 条</span></h2><div class="glist">%s</div>' % (l, l, len(rows), "".join(rows)))
    body = """<header class="lhead"><h1>概念 / 专有名词索引</h1>
<p class="sub">%d 条 · 以老师目录与大纲中的词组为单位 · 每条 = 英文定义（PPT 原句逐字）+ 中文忠实翻译 + 定义出处</p></header>
<section class="notice"><b>状态说明</b>：标注「仅出现，无独立定义句」的术语，表示老师 PPT 中该词只出现在标题、图注或正文里，没有单独下定义；此时按硬约束<b>不补写任何词典式解释</b>，仅给出含该词的 PPT 原句与出处。缩写 / 符号类术语按 PPT 原文保留，中文不作展开。</section>
<div class="letters">%s</div>%s""" % (len(TERMS_JS), letters, "".join(secs))
    return frame("专有名词索引", 0, "glossary.html", body)


# ---------------------------------------------------------------- emit / check
from visual_revision import install
install(globals())
if CHECK:
    from verify_revision import verify
    sys.exit(0 if verify() else 1)

if not CHECK:
    (ROOT / "index.html").write_text(build_index(), encoding="utf-8")
    (ROOT / "exam-items.html").write_text(build_exam_index(), encoding="utf-8")
    (ROOT / "glossary.html").write_text(build_glossary(), encoding="utf-8")
    (ROOT / "lectures").mkdir(exist_ok=True)
    (ROOT / "exam").mkdir(exist_ok=True)
    for lid, d in lectures.items():
        (ROOT / "lectures" / (lid + ".html")).write_text(build_lecture(lid, d), encoding="utf-8")
        e = build_exam_lecture(lid)
        if e:
            (ROOT / "exam" / (lid + "-exam.html")).write_text(e, encoding="utf-8")
    print("BUILT index / exam-items / glossary / %d lectures / %d exam pages" % (
        len(lectures), len({i["lecture"] for i in items})))
else:
    # ---------------- verification ----------------
    report = ["# QA 自检报告 (QA Report)", ""]
    state = {"ok": True}

    def chk(name, cond, detail=""):
        report.append("- [%s] %s%s" % ("PASS" if cond else "FAIL", name, (" — " + detail) if detail else ""))
        if not cond:
            state["ok"] = False

    # 1. slide counts
    for lid, d in lectures.items():
        f = ROOT / "lectures" / (lid + ".html")
        c = f.read_text(encoding="utf-8").count('<section class="slide') if f.exists() else -1
        chk("%s Slide 卡片数 == %d" % (lid, d["page_count"]), c == d["page_count"], "实测 %d" % c)

    # 2. every term has source + bilingual + en_def verbatim in the source slide
    miss_src = [k for k, t in terms.items() if not t["source"]["file"] or not t["source"]["slide"]]
    chk("无出处术语 0 条", len(miss_src) == 0, str(miss_src[:5]))
    miss_zh = [k for k, t in terms.items() if not t["zh_definition"] or t["zh_definition"] == t["en_definition"]]
    chk("全部术语有中文定义", len(miss_zh) == 0, str(miss_zh[:5]))
    def norm(s):
        return re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()
    bad_en = []
    for k, t in terms.items():
        if not t["en_definition"]:
            continue
        lid, s = t["source"]["lecture"], t["source"]["slide"]
        if lid not in lectures or s > lectures[lid]["page_count"]:
            bad_en.append((k, "bad source")); continue
        if norm(t["en_definition"]) not in norm(lectures[lid]["pages"][s - 1]["text"]):
            bad_en.append(k)
    chk("英文定义逐字命中 PPT 原句", len(bad_en) == 0, "不匹配 %d 条：%s" % (len(bad_en), bad_en[:8]))

    # 3. term coverage on EVERY individual slide (strict, per-<section>)
    uncovered = []
    total_spans = 0
    for lid, d in lectures.items():
        f = ROOT / "lectures" / (lid + ".html")
        txt = f.read_text(encoding="utf-8")
        total_spans += txt.count('class="term"')
        sec_text = {}
        for chunk in re.split(r'(?=<section class="slide)', txt):
            m = re.search(r'id="%s-s(\d+)"' % lid, chunk)
            if m:
                sec_text[int(m.group(1))] = chunk
        for k, t in terms.items():
            needle = 'data-term="%s"' % esc(k)
            for o in t["occurrences"]:
                if o["lecture"] == lid and needle not in sec_text.get(o["slide"], ""):
                    uncovered.append((lid, o["slide"], k)); break
    chk("每页术语均挂 data-term（逐 Slide 严格核验）", len(uncovered) == 0,
        "缺 %d：%s" % (len(uncovered), uncovered[:6]))
    occ_total = sum(len(t["occurrences"]) for t in terms.values())
    chk("全站术语悬浮标记数（>= 术语出现位置总数）", total_spans >= occ_total,
        "%d 处 / 出现位置 %d 个" % (total_spans, occ_total))

    # 4. exam coverage
    decl = [i["id"] for i in items]
    chk("例题 30 道", len(items) == 30, str(len(decl)))
    chk("每题中文翻译齐全", all(zh_exam.get(i["id"], {}).get("question") for i in items), "")
    chk("每题相关页不为空", all(len(i["related_slides"]) > 0 for i in items), "")
    chk("每题答案页中文齐全", all(
        all(str(ap["slide"]) in zh_exam.get(i["id"], {}).get("answer_pages", {}) for ap in i["answer_pages"])
        for i in items), "")

    # 5. links / assets / offline
    allhtml = list(ROOT.glob("*.html")) + list((ROOT / "lectures").glob("*.html")) + list((ROOT / "exam").glob("*.html"))
    # (?<=\s) is essential: 'data-src="..."' is a metadata attribute, NOT a src.
    # Matching bare 'src="' wrongly reported 727 slide citations as broken links.
    broken = []
    for f in allhtml:
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r'(?<=\s)(?:href|src)="([^"]+)"', txt):
            u = m.group(1).split("#")[0].split("?")[0]
            if not u or u.startswith("http") or u.startswith("mailto"):
                continue
            p = (f.parent / u).resolve()
            if not p.exists():
                broken.append((f.name, u))
    chk("内部链接/资源全部存在", len(broken) == 0, "损坏 %d：%s" % (len(broken), broken[:8]))

    offline = []
    for f in allhtml:
        t = f.read_text(encoding="utf-8")
        if "fetch(" in t or re.search(r'(?:src|href)="https?://', t):
            offline.append(f.name)
    chk("零 fetch / 零外部资源", len(offline) == 0, str(offline))

    pngs = len(list((ASSETS / "img").rglob("*.png")))
    chk("逐页 PNG == 727", pngs == 727, "实测 %d" % pngs)

    # 6. no invented AI-analysis tags anywhere
    banned = ["命题规律", "记忆要点", "真实但无关", "听起来专业", "逐句精讲", "常见误解", "考点提示", "错解设计"]
    hits = []
    for f in allhtml:
        t = f.read_text(encoding="utf-8")
        for b in banned:
            if b in t:
                hits.append((f.name, b))
    chk("无 AI 归纳文字", len(hits) == 0, str(hits[:6]))

    report += ["", "## 汇总", "", "- 幻灯片 %d 页 / PDF %d 份 / 例题 %d 道 / 术语 %d 条 / 悬浮标记 %d 处" % (
        sum(d["page_count"] for d in lectures.values()), len(lectures), len(items), len(terms), total_spans),
        "- 结论：**%s**" % ("全部通过" if state["ok"] else "存在 FAIL，需修复"), ""]
    (DATA / "reports/qa_report.md").write_text("\n".join(report), encoding="utf-8")

    # coverage report
    cov = ["# 术语覆盖率报告 (Coverage Report)", "",
           "- 术语总数：%d（verbatim %d / occurrence_only %d）" % (
               len(terms), sum(1 for t in terms.values() if t["status"] == "verbatim"),
               sum(1 for t in terms.values() if t["status"] == "occurrence_only")),
           "- 术语出现位置总数：%d" % sum(len(t["occurrences"]) for t in terms.values()),
           "- 全站已挂悬浮标记：%d 处" % total_spans,
           "- 每页检出术语均已在 HTML 中包裹：%s" % ("是" if not uncovered else "否"),
           "", "## 人工抽查清单（建议 100% 核对）", "",
           "- 全部 %d 条术语定义（英文是否逐字、中文是否忠实、出处是否正确）" % len(terms),
           "- 全部 %d 道例题页（题干/选项/答案原文与中文翻译）" % len(items),
           "- 全部 %d 条 occurrence_only 术语（确认未补写解释）" % sum(1 for t in terms.values() if t["status"] == "occurrence_only"),
           "- 每讲抽查 5 页正文与对应原页 PNG 是否一致", ""]
    (DATA / "reports/coverage_report.md").write_text("\n".join(cov), encoding="utf-8")
    print("\n".join(report[:8]))
    print("CHECK_RESULT", "PASS" if state["ok"] else "FAIL")
