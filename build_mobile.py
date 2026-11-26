"""Dedicated Mobile Edition generator for SD5979 Revision Site.

Outputs under mobile/:
  mobile/index.html
  mobile/response.html
  mobile/exam-items.html
  mobile/glossary.html
  mobile/lectures/L00.html .. L12.html
  mobile/exam/L01-exam.html .. L12-exam.html

Shares assets/img/, pdfs/, assets/js/terms.js, assets/js/search_index.js with Desktop.
Zero external dependencies, 100% offline & GitHub Pages safe.
"""
import html
import struct


def build_mobile_site(ctx):
    root = ctx["root"]
    lectures = ctx["lectures"]
    items = ctx["items"]
    terms_js = ctx["terms_js"]
    zh_slides = ctx["zh_slides"]
    zh_exam = ctx["zh_exam"]
    mc = ctx["mc"]
    oq = ctx["oq"]
    extra = ctx["extra"]
    topics = ctx["topics"]
    audit = ctx["audit"]
    markup = ctx["markup"]
    render_zh_slide = ctx["render_zh_slide"]
    clean = ctx["clean"]

    E = lambda s: html.escape(str(s), quote=True)
    mroot = root / "mobile"
    (mroot / "lectures").mkdir(parents=True, exist_ok=True)
    (mroot / "exam").mkdir(parents=True, exist_ok=True)

    def asset_pre(mdepth):
        return "../" * (mdepth + 1)

    def m_pre(mdepth):
        return "../" * mdepth

    def m_cite(lid, s, mdepth=0):
        ap = asset_pre(mdepth)
        mp = m_pre(mdepth)
        title = f"{lectures[lid]['source_file']} · PDF 第 {s} 页"
        return (
            f'<a class="source-link" href="{mp}lectures/{lid}.html#{lid}-s{s}" '
            f'data-image="{ap}assets/img/{lid}/slide-{s:03}.png" '
            f'data-pdf="{ap}pdfs/{lid}.pdf#page={s}" '
            f'data-label="{E(title)}">{lid} · 第 {s} 页 ↗</a>'
        )

    def m_refs(rs, mdepth=0):
        return '<div class="refs">' + "".join(m_cite(l, s, mdepth) for l, s in dict.fromkeys(rs)) + "</div>"

    def m_img(lid, s, mdepth=0):
        ap = asset_pre(mdepth)
        with (root / f"assets/img/{lid}/slide-{s:03}.png").open("rb") as f:
            w, h = struct.unpack(">II", f.read(24)[16:24])
        lbl = f"{lectures[lid]['source_file']} · PDF 第 {s} 页"
        return (
            f'<div class="m-slide-img-wrap">'
            f'<a href="{ap}assets/img/{lid}/slide-{s:03}.png" '
            f'data-image="{ap}assets/img/{lid}/slide-{s:03}.png" '
            f'data-pdf="{ap}pdfs/{lid}.pdf#page={s}" data-label="{E(lbl)}">'
            f'<img src="{ap}assets/img/{lid}/slide-{s:03}.png" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async" alt="{lid} 原页第 {s} 页">'
            f'</a>'
            f'<div class="m-img-cap"><span>{E(lectures[lid]["source_file"])}</span><span>第 {s} 页 · 点图放大</span></div>'
            f'</div>'
        )

    def m_frame(title, subtitle, mdepth, active_tab, desktop_rel, body, back_href=None, has_pager=False, pager_html=""):
        ap = asset_pre(mdepth)
        mp = m_pre(mdepth)
        desktop_href = ap + desktop_rel
        back_btn = f'<a class="m-back" href="{back_href}" aria-label="返回">‹</a>' if back_href else ""
        tabs = [
            ("home", "🏠", "首页", mp + "index.html"),
            ("response", "🎯", "重点", mp + "response.html"),
            ("exam", "📝", "例题", mp + "exam-items.html"),
            ("lectures", "📖", "讲义", mp + "index.html#m-lectures"),
            ("glossary", "📚", "术语", mp + "glossary.html"),
        ]
        tab_html = "".join(
            f'<a class="{"active" if k == active_tab else ""}" href="{href}"><span class="ic">{ic}</span><span>{lbl}</span></a>'
            for k, ic, lbl, href in tabs
        )
        body_cls = ' class="has-pager"' if has_pager else ""
        sub_html = f"<small>{E(subtitle)}</small>" if subtitle else ""
        return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#163d35">
<title>{E(title)} · SD5979 手机复习版</title>
<link rel="stylesheet" href="{ap}assets/css/mobile.css">
</head>
<body data-mdepth="{mdepth}"{body_cls}>
<header class="m-topbar">
  {back_btn}
  <div class="m-title">{E(title)}{sub_html}</div>
  <a class="m-switch" href="{desktop_href}" data-base-href="{desktop_href}">💻 电脑版</a>
</header>
<main class="m-main">{body}</main>
{pager_html}
<nav class="m-tabbar" aria-label="底部导航">{tab_html}</nav>
<script src="{ap}assets/js/terms.js"></script>
<script src="{ap}assets/js/search_index.js"></script>
<script src="{ap}assets/js/mobile.js"></script>
</body></html>"""

    def build_topic_cards(mdepth=0):
        mp = m_pre(mdepth)
        return "".join(
            f'<section class="m-topic">'
            f'<span class="eyebrow">老师重点 · {n+1:02}</span>'
            f'<h2>{E(t)}</h2><p>{E(desc)}</p>{m_refs([("L12", s)], mdepth)}'
            f'<details class="m-details"><summary>概念澄清与相关例题</summary>'
            f'{m_refs([("L12", p) for p in ps], mdepth)}'
            f'<div class="item-nav">'
            + "".join(f'<a class="pill" href="{mp}exam/{iid[:3]}-exam.html#{iid}">{iid}</a>' for iid in ids)
            + '</div></details></section>'
            for n, (t, desc, s, ps, ids) in enumerate(topics)
        )

    # ---------------- 1. mobile/index.html ----------------
    lec_cards = "".join(
        f'<a class="m-card" href="lectures/{l}.html">'
        f'<span class="eyebrow"><span>{l} · 中英对照</span><span>{d["page_count"]} 页</span></span>'
        f'<h3>{E(d["source_file"].split("SD5979")[-1].replace(".pdf", "").strip())}</h3>'
        f'<span class="meta"><span>支持左右滑动翻页 · 记忆进度</span><b>进入阅读 →</b></span></a>'
        for l, d in lectures.items()
    )
    total_pages = sum(d["page_count"] for d in lectures.values())
    idx_body = (
        '<section class="m-hero">'
        '<p class="eyebrow">SD5979 · MOBILE STUDY EDITION</p>'
        '<h1>多媒体娱乐研究方法<br>手机中英对照复习站</h1>'
        '<p>保留老师英文原图排版，逐页附忠实中文对照，研究课词汇已加粗高亮标注原英语；支持单手滑屏翻页与点词看定义。</p>'
        '<div class="m-cta-row">'
        '<a class="m-btn-primary" href="cram.html">⚡ 考前速背冲刺</a>'
        '<a class="m-btn-ghost" href="exam-items.html">📝 39 组例题</a>'
        '</div></section>'
        f'<div class="m-stats"><div><b>{total_pages}</b><span>中英对照页</span></div>'
        '<div><b>12</b><span>完整讲义</span></div>'
        f'<div><b>{len(items)}</b><span>出处例题组</span></div></div>'
        '<section class="m-search-box">'
        '<label for="m-q" style="display:block;font-size:13px;font-weight:700;margin-bottom:6px">🔍 全站中英文检索</label>'
        '<input id="m-q" type="search" placeholder="搜中文或英文：混淆变量 / mediation / 所罗门 / ANOVA" autocomplete="off">'
        '<div id="m-qres"></div></section>'
        '<div class="m-note-box"><p><b>手机端使用小技巧：</b></p>'
        '<p>• 讲义默认「单页翻卡」模式，<b>左右滑动</b>或点底部按钮切页，自动记住上次看到哪一页。</p>'
        '<p>• 遇到带虚线的<mark class="rm-term"><strong>高亮研究词</strong><span class="rm-en">（English）</span></mark>，<b>轻点</b>即可弹出老师原句定义；点原图可全屏放大 2×。</p></div>'
        '<h2 class="m-section-title" id="m-lectures"><span>📖 全部 12 讲 · 中英对照讲义</span><span class="note">不含 L06</span></h2>'
        f'<div class="m-card-list">{lec_cards}</div>'
        '<h2 class="m-section-title"><span>🎯 老师明确的六组重点</span></h2>'
        + build_topic_cards(0)
    )
    (mroot / "index.html").write_text(
        m_frame("SD5979 复习站", "手机中英对照版", 0, "home", "index.html", idx_body),
        encoding="utf-8",
    )

    # ---------------- 2. mobile/response.html ----------------
    corrections = [
        ("节点不只 bias 不同", "每条连接有自己的 weight，每个节点有自己的 bias；训练时两者都调整。", [15, 17]),
        ("Mediated moderation 的原图有问题", "老师承认学生图更好；原图是视觉比喻。回归表达为 X × W → M，再由 M → Y，同时考虑 X 对 Y 的控制主效应。", [19, 20]),
        ("Solomon 的比较要照原话区分", "老师保留 G1after 与 G3after 的比较，说明 G3after / G4after 都无前测，不能知道前测效应。不要将此段与第 106 页“首次测量用于信度”混成同一问题。", [28, 106]),
        ("哪些是旁支？哪些明确超出范围？", "CCI、DIC、unrestricted regression coefficients 在第 164 页明确称为 asides；第 85 页对梯度为何不断缩小的进一步数学解释明确说不属于本课。其余细节不据此自动判为不考。", [85, 164, 165, 166, 167]),
        ("开放题怎样获得分数？", "老师要求简短、精确。堆砌略有关联的内容、让老师自己挑答案，不算真正作答。猫狗题示例逐小问只回答所问。", [168, 169, 170, 171, 172]),
        ("选择题为什么两个答案看着都对？", "老师要求选择最精确、最完整的一项；区分完全对、不完整、方向反了或周边概念、拼凑术语。", [64]),
    ]
    resp_body = (
        '<div class="m-head"><p class="eyebrow">RESPONSE / 19 NOV 2026</p>'
        '<h1>老师答疑与六组重点</h1>'
        '<p>六组重点来自 L12 第 31–32 页，点击任意原页标签即可放大核对原话。</p></div>'
        + build_topic_cards(0)
        + '<h2 class="m-section-title">修正、边界与答题要求</h2><div class="answer-units">'
        + "".join(
            f'<section><h3>{E(t)}</h3><p>{E(a)}</p>{m_refs([("L12", s) for s in ss], 0)}</section>'
            for t, a, ss in corrections
        )
        + '</div><h2 class="m-section-title">老师讲清楚的公式与路径</h2>'
        '<div class="m-formula-card"><h3>配对 t-test</h3>'
        '<div class="formula"><math display="block"><mi>t</mi><mo>=</mo><mfrac><mrow><mover><mi>d</mi><mo>¯</mo></mover><mo>−</mo><mn>0</mn></mrow><mfrac><msub><mi>s</mi><mi>d</mi></msub><msqrt><mi>n</mi></msqrt></mfrac></mfrac></math></div>'
        '<p class="note">先算每对差值，再算差值均值与标准差，最后与“无差异 = 0”比较。</p>'
        + m_refs([("L12", 118), ("L12", 119), ("L12", 120)], 0)
        + '</div><div class="m-formula-card"><h3>Mediated moderation</h3>'
        '<div class="path"><span>X × W</span><b>→</b><span>M</span><b>→</b><span>Y</span></div>'
        '<p class="note">交互作用经中介传递，对应老师修正后的文字。</p>'
        + m_refs([("L12", 19), ("L12", 20), ("L12", 76)], 0)
        + '</div><div class="m-formula-card"><h3>相对下降 vs 绝对下降</h3>'
        '<div class="path"><span>10%</span><b>→</b><span>5%</span></div>'
        '<p class="note">相对风险下降 50%；绝对下降 5 个百分点。分母与基准必须讲清。</p>'
        + m_refs([("L12", 45), ("L12", 46)], 0)
        + '</div><div class="m-head"><h1>完整答疑与考试说明</h1>'
        '<p>L12 共 176 页已全部支持中英对照阅读。</p>'
        '<div class="refs" style="margin-top:10px">'
        '<a class="pill" href="lectures/L12.html">📖 阅读 176 页答疑</a>'
        '<a class="pill" href="exam/L12-exam.html">📝 新增 9 组例题</a></div>'
        + m_refs([("L12", 173), ("L12", 174), ("L12", 175)], 0)
        + "</div>"
    )
    (mroot / "response.html").write_text(
        m_frame("老师答疑与重点", "L12 核心考点地图", 0, "response", "response.html", resp_body, back_href="index.html"),
        encoding="utf-8",
    )

    # ---------------- 3. mobile/glossary.html ----------------
    g_rows = []
    for k, t in sorted(terms_js.items(), key=lambda x: x[0].lower()):
        status = "仅有出现，未抽取到独立定义；请看原页上下文。" if t["status"] == "occurrence_only" else "既有定义摘录与中文翻译；以原课件上下文为准。"
        g_rows.append(
            f'<article class="m-gitem" id="t-{E(k)}">'
            f'<h2>{E(k)}</h2><h3>{E(t["zh"])}</h3>'
            f'<p class="note">{status}</p>'
            f'<div class="term-en-box">{clean(t["en"])}</div>'
            f'<p>{clean(t["zhdef"])}</p>'
            f'{m_refs([(t["lecture"], t["slide"])], 0)}</article>'
        )
    gloss_body = (
        f'<div class="m-head"><p class="eyebrow">GLOSSARY</p><h1>{len(g_rows)} 个课程概念</h1>'
        '<p>来自老师大纲与目录的完整术语索引，点击出处可直达原图与中文对照页。</p></div>'
        '<div class="m-search-box">'
        '<input id="m-glossary-q" type="search" placeholder="筛选术语（中英文均可）…" autocomplete="off">'
        f'<p class="note" id="m-glossary-cnt" style="margin:6px 2px 0">共 {len(g_rows)} / {len(g_rows)} 条</p></div>'
        + "".join(g_rows)
    )
    (mroot / "glossary.html").write_text(
        m_frame("课程概念索引", f"{len(g_rows)} 条术语", 0, "glossary", "glossary.html", gloss_body, back_href="index.html"),
        encoding="utf-8",
    )

    # ---------------- 4. mobile/exam-items.html ----------------
    oq_titles = {
        "L04-E01": "Like / dislike 的四个小问",
        "L05-E02": "预警与对手：最难条件",
        "L05-E03": "测谎系统：中性基线",
        "L08-E01": "中介与调节的四种路径",
        "L09-E03": "猫狗模型的混淆与推理",
        "L10-E01": "FMS 两类错误的实际后果",
        "L10-E04": "VR 体温测量的黑箱",
        "L10-E05": "MOBA 情绪测量的黑箱",
        "L11-E03": "56% 与决策不确定性",
    }
    q_cards = []
    for i in items:
        iid = i["id"]
        if iid in mc:
            title = mc[iid][0]
        else:
            title = next((x[4] for x in extra if x[0] == iid), None) or (
                oq[iid][0][0] + " · " + oq_titles.get(iid, iid)
            )
        q_cards.append(
            f'<a class="m-card question-card" data-kind="{i["kind"]}" data-id="{iid}" data-lecture="{i["lecture"]}" '
            f'href="exam/{i["lecture"]}-exam.html#{iid}">'
            f'<span class="eyebrow"><span>{iid}</span><span>{"选择题" if i["kind"] == "MCQ" else "开放题"}</span></span>'
            f'<h3>{E(title)}</h3>'
            f'<span class="meta"><span>{i["lecture"]} 第 {i["question_slide"]} 页</span><b>开始复习 →</b></span></a>'
        )
    lec_opts = "".join(f"<option>{l}</option>" for l in lectures if any(i["lecture"] == l for i in items))
    exam_idx_body = (
        f'<div class="m-head"><p class="eyebrow">EXAM BANK</p><h1>{len(items)} 组考试例题</h1>'
        '<p>作答记录与错题本和电脑版共享保存。点击题目进入单手刷题模式。</p></div>'
        '<div class="m-filter">'
        '<input id="review-search" type="search" placeholder="搜索题号 / 概念 / 关键词">'
        '<div class="m-filter-row">'
        '<select id="kind-filter"><option value="">全部题型</option><option value="MCQ">选择题</option><option value="OpenQ">开放题</option></select>'
        f'<select id="lecture-filter"><option value="">全部讲次</option>{lec_opts}</select>'
        '</div>'
        '<label class="check"><input type="checkbox" id="mistake-filter">只看错题本</label>'
        '<p class="note" id="filter-count" style="margin:0"></p></div>'
        f'<div class="m-card-list">{"".join(q_cards)}</div>'
        '<p class="note empty-state" style="text-align:center;padding:24px" hidden>没有匹配的题目，可调整筛选条件。</p>'
    )
    (mroot / "exam-items.html").write_text(
        m_frame("例题题库", f"{len(items)} 组例题", 0, "exam", "exam-items.html", exam_idx_body, back_href="index.html"),
        encoding="utf-8",
    )

    # ---------------- 5. mobile/lectures/L00..L12.html ----------------
    for lid, d in lectures.items():
        lec_zh = zh_slides.get(lid, {})
        lec_term_total = 0
        blocks = []
        ap = asset_pre(1)
        for p in d["pages"]:
            s = p["slide"]
            related = [it for it in items if it["lecture"] == lid and (it["question_slide"] == s or s in it["answer_slides"])]
            links = "".join(f'<a class="pill" href="../exam/{lid}-exam.html#{it["id"]}">📝 {it["id"]}</a>' for it in related)
            found = set()
            markup(p["text"], found)
            ts = "".join(
                f'<span class="term" tabindex="0" data-term="{E(k)}">{E(k)} · {E(terms_js[k]["zh"])}</span>'
                for k in sorted(found)
            )
            zh_html, term_cnt = render_zh_slide(lec_zh.get(str(s), ""))
            lec_term_total += term_cnt
            term_badge = f'<span class="zh-badge">{term_cnt} 个研究词</span>' if term_cnt else ""
            term_strip = (
                f'<div class="term-strip"><span class="term-strip-label">本页大纲术语（轻点看定义）：</span>{ts}</div>'
                if ts else ""
            )
            lbl = f"{d['source_file']} · PDF 第 {s} 页"
            blocks.append(
                f'<section class="m-slide{" is-current" if s == 1 else ""}" id="{lid}-s{s}">'
                f'<div class="m-slide-bar">'
                f'<span class="m-slide-num">{lid} · 第 {s}/{d["page_count"]} 页 {links}</span>'
                f'<a class="m-zoom-btn" href="{ap}assets/img/{lid}/slide-{s:03}.png" '
                f'data-image="{ap}assets/img/{lid}/slide-{s:03}.png" '
                f'data-pdf="{ap}pdfs/{lid}.pdf#page={s}" data-label="{E(lbl)}">🔍 大图</a>'
                f'</div>'
                f'{m_img(lid, s, 1)}'
                f'<div class="m-slide-zh-wrap"><div class="zh-col-head"><span>中文对照</span>{term_badge}</div>'
                f'<div class="zh-body">{zh_html}</div></div>'
                f'<div class="m-slide-foot">{term_strip}'
                f'<details class="m-transcript"><summary>查看英文提取原文</summary><pre>{clean(p["text"])}</pre></details>'
                f'</div></section>'
            )

        short_title = d["source_file"].split("SD5979")[-1].replace(".pdf", "").strip()
        controls = (
            '<div class="m-controls">'
            '<div class="m-seg" role="group" aria-label="翻页方式">'
            '<button type="button" data-mode-btn="card" aria-pressed="true">单页翻卡（支持滑屏）</button>'
            '<button type="button" data-mode-btn="scroll" aria-pressed="false">连续滚动</button>'
            '</div>'
            '<div class="m-seg" role="group" aria-label="显示内容">'
            '<button type="button" data-view-btn="both" aria-pressed="true">中英对照</button>'
            '<button type="button" data-view-btn="zh" aria-pressed="false">仅看中文</button>'
            '<button type="button" data-view-btn="en" aria-pressed="false">仅看原图</button>'
            '</div>'
            '<div class="m-subctrl">'
            '<button type="button" class="m-toggle-btn" id="m-hl-toggle" aria-pressed="true">✦ 高亮研究词汇</button>'
            f'<span class="m-stat-mini">本讲共标 <b>{lec_term_total}</b> 处词汇</span>'
            '</div></div>'
        )
        pager = (
            '<div class="m-pager" role="navigation" aria-label="幻灯片翻页">'
            '<button type="button" class="pg-nav" id="pg-prev">← 上一页</button>'
            f'<button type="button" class="pg-jump" id="pg-jump">第 1 / {d["page_count"]} 页 ▾</button>'
            '<button type="button" class="pg-nav" id="pg-next">下一页 →</button>'
            '</div>'
        )
        body = (
            f'<div class="m-head"><p class="eyebrow">{lid} · {d["page_count"]} PAGES</p>'
            f'<h1>{E(short_title)}</h1>'
            '<p>原图在上、中文对照在下；研究课词汇已加粗高亮。左右滑动或点底部按钮切换页面。</p></div>'
            + controls
            + f'<div class="m-slides" data-lecture="{lid}" data-mode="card" data-view="both">{"".join(blocks)}</div>'
        )
        (mroot / "lectures" / f"{lid}.html").write_text(
            m_frame(f"{lid} 中英讲义", short_title, 1, "lectures", f"lectures/{lid}.html", body, back_href="../index.html#m-lectures", has_pager=True, pager_html=pager),
            encoding="utf-8",
        )

    # ---------------- 6. mobile/exam/L*-exam.html ----------------
    def m_audit_panel(iid):
        rows = []
        for x in audit.get(iid, []):
            hits = x["pages"]
            status = f"正文原词命中 {len(hits)} 页" if hits else "未检出独立正文原词命中"
            rows.append(
                f'<section><h3>{E(x["term"])}</h3><p class="note">{status}</p>'
                + (m_refs(hits, 1) if hits else "<p>这不证明概念从未以其他表达讲过；不把它直接当成该选项错误的理由。</p>")
                + "</section>"
            )
        return (
            '<details class="m-details"><summary>这些选项的概念，课件正文是否出现过？</summary>'
            '<p class="note">检索全部 903 页（排除题目、答案页与参考文献页）。</p>'
            '<div class="answer-units">' + "".join(rows) + "</div></details>"
        ) if rows else ""

    exam_count = 0
    for lid in lectures:
        its = [i for i in items if i["lecture"] == lid]
        if not its:
            continue
        exam_count += 1
        blocks = []
        for it in its:
            iid = it["id"]
            q = it["question_slide"]
            is_mc = iid in mc
            title = mc[iid][0] if is_mc else next((x[4] for x in extra if x[0] == iid), oq_titles.get(iid, iid))
            q_zh = zh_exam.get(iid, {}).get("question", "")
            trans_html = (
                f'<details class="m-details"><summary>题干中文译文</summary>'
                f'<p style="background:#f5f7f3;padding:11px;border-radius:8px;font-size:14px;line-height:1.7">{E(q_zh).replace(chr(10), "<br>")}</p></details>'
            ) if q_zh else ""
            stem_pages = {"L10-E05": [81], "L12-E07": [141, 142, 143]}.get(iid, [])
            stem_more = ("<h3>完整题目与情境延续</h3>" + "".join(m_img(lid, s, 1) for s in stem_pages)) if stem_pages else ""
            if is_mc:
                title, answer, rows, rs = mc[iid]
                opt_cards = "".join(
                    f'<div class="opt-card"><div class="opt-card-h">'
                    f'<span class="opt-letter">{E(chr(65+n)) if iid != "L11-E01" else "问 "+str(n+1)}</span>'
                    f'<span class="opt-tag">{E(r.split("｜")[0])}</span></div>'
                    f'<p>{E(r.split("｜", 1)[1] if "｜" in r else r)}</p>'
                    f'{m_refs([(lid, it["answer_slides"][0])] + rs, 1)}</div>'
                    for n, r in enumerate(rows)
                )
                response = (
                    f'<div class="answer-banner"><div><span style="display:block;font-size:11px;opacity:.85">老师答案</span><strong>{E(answer)}</strong></div><span>以原页勾选为准</span></div>'
                    f'<div class="opt-cards">{opt_cards}</div>'
                )
                if iid == "L08-E02":
                    response += '<p class="caveat">课程口径：此题在 L08 第 48 页和 L12 第 78 页均勾选 B，记录老师对题设的解释，不能扩大推出任意回归都证明因果。</p>'
                if iid == "L07-E02":
                    response += '<p class="caveat">信息边界：题目给的是两个均值，老师借此考重编码。</p>'
                response += m_audit_panel(iid)
            else:
                response = '<div class="answer-units">' + "".join(
                    f'<section><h3>{E(t)}</h3><p>{E(a)}</p>{m_refs(rs, 1)}</section>' for t, a, rs in oq[iid]
                ) + "</div>"
            orig_ans = "".join(m_img(lid, s, 1) for s in it["answer_slides"] if s not in stem_pages) or m_img(lid, q, 1)
            practice_inner = (
                "".join(f'<button type="button" data-choice="{c}" aria-pressed="false">{c}</button>' for c in "ABCD")
                if is_mc and iid != "L11-E01"
                else '<textarea aria-label="我的短答" placeholder="先写下自己的理由，再展开解析。"></textarea>'
            )
            blocks.append(
                f'<article class="m-exam-card" id="{iid}">'
                f'<span class="eyebrow" style="font-size:11.5px;font-weight:700;color:#146957">{iid} · {E(it["category"])} · {"选择题" if is_mc else "开放题"}</span>'
                f'<h2>{E(title)}</h2>{m_refs([(lid, q)], 1)}{m_img(lid, q, 1)}{stem_more}{trans_html}'
                f'<div class="practice" data-item="{iid}"><span>我的作答</span>{practice_inner}'
                f'<button type="button" class="bookmark" aria-pressed="false">☆ 加入错题本</button></div>'
                f'<details class="solution"><summary>查看老师答案与逐项解析 ▾</summary>{response}'
                f'<h3>老师原答案与延续页</h3>{orig_ans}</details></article>'
            )
        nav = "".join(f'<a class="pill" href="#{i["id"]}">{i["id"]}</a>' for i in its)
        body = (
            f'<div class="m-head"><p class="eyebrow">EXAM / {lid}</p><h1>{lid} · 逐题复习（{len(its)} 组）</h1>'
            '<p>解析默认收起，可先选答案再展开核对，作答与错题自动保存。</p>'
            f'<div class="item-nav">{nav}</div></div>' + "".join(blocks)
        )
        (mroot / "exam" / f"{lid}-exam.html").write_text(
            m_frame(f"{lid} 例题", f"共 {len(its)} 组", 1, "exam", f"exam/{lid}-exam.html", body, back_href="../exam-items.html"),
            encoding="utf-8",
        )

    return len(lectures), exam_count
