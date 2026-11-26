"""Build a standalone local no-spoiler image Quiz Bank (quiz-bank.html) for interactive practice.

Ordered strictly for optimal Final Exam (L07-L12) + Midterm consolidation (L01-L05):
  Round 1: Q01-Q15  Final Core MCQs (L07-L12, 15 groups / 16 sub-items)
  Round 2: Q16-Q26  Final Core Open-ended Questions (L08-L12, 11 groups)
  Round 3: Q27-Q39  Midterm Foundation Consolidation (L01-L05, 10 MCQs + 3 OpenQ)
  Appendix: L12 s150-158 Naive Bayes worked calculation walkthrough

Run: python build_quiz_bank.py
"""
import html
import json
import pathlib
import re
import struct

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
E = lambda s: html.escape(str(s), quote=True)

pages = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "data/pages").glob("L??.json"))}
zh_slides = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "data/zh_slides").glob("L??.json"))}

# Ordered 39-question curriculum:
# (qno, id, round_key, kind, topic, title, stem_slides, is_l12_new, l12_echo, spoiler_safe_prompt_en, spoiler_safe_prompt_zh)
ORDER = [
    # ---- Round 1: Final Exam Core MCQs (L07-L12) ----
    ("Q01", "L07-E01", "r1", "MCQ", "重点 1 · 相关与因果", "根因（Sugar intake）也和结果相关吗？", [("L07", 62)], False, "L12 第 47–48 页复现", None, None),
    ("Q02", "L07-E02", "r1", "MCQ", "重点 1 · 信度与重编码", "2 题项量表与反向题重编码（Spearman-Brown）", [("L07", 64)], False, "L12 第 56–57 页复现", None, None),
    ("Q03", "L12-E04", "r1", "MCQ", "重点 2 · 回归分析", "零售商预测销售额：谁是自变量（IV）？", [("L12", 65)], True, "L12 新增", None, None),
    ("Q04", "L12-E05", "r1", "MCQ", "重点 2 · 回归分析", "把网站所有日志数据都丢进回归分析有什么问题？", [("L12", 69)], True, "L12 新增", None, None),
    ("Q05", "L08-E02", "r1", "MCQ", "重点 2 · 回归与因果", "相关不是因果，那线性回归能用来检验因果吗？", [("L08", 47)], False, "L12 第 77–78 页复现", None, None),
    ("Q06", "L08-E03", "r1", "MCQ", "重点 2 · SEM 结构方程", "SEM 为什么不只是从结果反推原因（Ex-consequentia）？", [("L08", 49)], False, "L12 第 81–82 页复现", None, None),
    ("Q07", "L12-E06", "r1", "MCQ", "重点 2 · 回归与神经网络", "回归直线 y = ax + b 在神经网络中对应 weight 与 bias", [("L12", 88), ("L12", 91)], True, "L12 新增（含第 88 页 SPSS 前导图）", None, None),
    ("Q08", "L09-E01", "r1", "MCQ", "重点 3 · 假设检验逻辑", "ReCAPTCHA：没有拒绝“非机器人”能否推出“是人类”？", [("L09", 11)], False, "L12 第 100–101 页复现", None, None),
    ("Q09", "L09-E02", "r1", "MCQ", "重点 3 · 实验设计", "哪种实验设计对顺序效应（order effects）最敏感？", [("L09", 79)], False, "L12 第 102–103 页复现", None, None),
    ("Q10", "L09-E04", "r1", "MCQ", "重点 3 · 所罗门四组 + 信度", "所罗门四组设计中用哪些组数据测 Cronbach’s α 最有力？", [("L09", 85)], False, "L12 第 104–106 页复现", None, None),
    ("Q11", "L10-E02", "r1", "MCQ", "重点 4 · ANOVA 方差分析", "单因素方差分析（Oneway ANOVA）到底比较什么？", [("L10", 61)], False, "L12 第 115–116 页复现", None, None),
    ("Q12", "L10-E03", "r1", "MCQ", "重点 4 · t 检验临界值", "为什么确立显著效应最低需要 t = 63.657 这么大的值？", [("L10", 74)], False, "L12 第 126–128 页复现", None, None),
    ("Q13", "L11-E01", "r1", "MCQ2", "重点 4 · t-test 选型（含两小题）", "独立样本 vs 配对样本；零假设 H₀ vs 备择假设 Hₐ", [("L11", 5)], False, "L12 第 118–120 页相关", None, None),
    ("Q14", "L11-E02", "r1", "MCQ", "重点 4 · 频率主义与 MANOVA", "MANOVA 不显著，能否推出人与 Bot 一样可信/高效？", [("L11", 39)], False, "L12 第 138–139 页复现", None, None),
    ("Q15", "L12-E08", "r1", "MCQ", "重点 5 · 贝叶斯统计", "Naïve Bayes 为什么“朴素”及如何应对多重共线性？", [("L12", 161)], True, "L12 新增", None, None),

    # ---- Round 2: Final Exam Core Open-Ended Questions (L08-L12) ----
    ("Q16", "L12-E01", "r2", "OpenQ", "重点 6 · 逻辑推理", "洗发水广告犯了哪种谬误（对比 Modus ponens）？", [("L12", 36)], True, "L12 新增", None, None),
    ("Q17", "L12-E02", "r2", "OpenQ", "重点 6 · 报告研究结果", "8% 男性 + 1% 女性色盲，为何不能推出总体 9%？", [("L12", 39)], True, "L12 新增（第 44 页附 CPU 变体）", None, None),
    ("Q18", "L12-E03", "r2", "OpenQ", "重点 6 · 报告研究结果", "副作用风险从 10% 降到 5%：声称“降低 50%”对吗？", [("L12", 45)], True, "L12 新增", None, None),
    ("Q19", "L08-E01", "r2", "OpenQ", "重点 2 · 中介与调节", "VR 健康应用：写出 Mediation / Moderation / 复合路径", [("L08", 26)], False, "L12 第 72–76 页复现 + 第 19–20 页修正", None, None),
    ("Q20", "L10-E01", "r2", "OpenQ", "重点 4 · 两类错误", "飞机 FMS 导航系统重设计：Type I 与 Type II 错误的实际后果", [("L10", 41)], False, "L12 第 108–114 页复现", None, None),
    ("Q21", "L10-E04", "r2", "OpenQ", "重点 4 · 测量效度黑箱", "VR 头盔实验：不显著结果、红外体温计与定性反馈怎么看？", [("L10", 77), ("L10", 78)], False, "L12 第 131–133 页复现", None, None),
    ("Q22", "L10-E05", "r2", "OpenQ", "重点 4 · 测量效度黑箱", "MOBA 游戏 EMOTIV 脑电测负面情绪：最该质疑什么？", [("L10", 80), ("L10", 81)], False, "L12 第 134–136 页复现", None, None),
    ("Q23", "L11-E03", "r2", "OpenQ", "重点 5 · 贝叶斯决策", "Naïve Bayes 算出 56% 为类人机器人，能有多大把握？", [("L11", 57)], False, "L12 第 159–160 页复现", None, None),
    ("Q24", "L12-E07", "r2", "OpenQ", "综合 · 研究质量评估", "MIT 大模型 Arctan-10 vs 小学生算术实验：谁是更好的研究者？", [("L12", 140), ("L12", 141), ("L12", 142), ("L12", 143)], True, "L12 新增", None, None),
    ("Q25", "L12-E09", "r2", "OpenQ", "综合 · 开放题新问法", "猫狗模型（L12 改写版）：名义测量类别、数据分割与证伪", [("L12", 169)], True, "L12 改写新问法（s170–172 原页含答案，题干见下方无剧透整理）",
     "If the training data in Lakkaraju et al. (2017) are taken as a nominal measurement:\nA) Then what are the two classes?\nB) What is the data split based on if with a confidence of 96%, the predictive model states that ‘white dogs are cats too?’\nC) Although the statement ‘Everything white is a cat’ is so easy to falsify with one single counter-example, then why does not the network do so?",
     "如果把 Lakkaraju 等人（2017）的训练数据看作一种名义测量（nominal measurement）：\nA）那么这两个类别（classes）是什么？\nB）如果预测模型以 96% 的置信度判定“白狗也是猫”，它的数据分割（data split）是依据什么做的？\nC）尽管“所有白色的都是猫”这句话用一个反例就能轻松证伪（falsify），为什么神经网络没有这样做？"),
    ("Q26", "L09-E03", "r2", "OpenQ", "重点 3 · 实验混淆与证伪", "猫狗模型（L09 原版问法，对比 Q25 差异）", [("L09", 81)], False, "原版见 L09 s81–84（s82–84 原页含答案，题干见下方无剧透整理）",
     "If the training data in Lakkaraju et al. (2017) are taken as an experimental design:\nA) Then what are the two conditions?\nB) What is the confound if with a confidence of 96%, the predictive model states that ‘a white dog is a cat too?’\nC) Although the statement in B is so easy to falsify, then why does not the network do so?",
     "如果把 Lakkaraju 等人（2017）的训练数据看作一种实验设计（experimental design）：\nA）那么这两个实验条件（conditions）是什么？\nB）如果预测模型以 96% 的置信度判定“白狗也是猫”，其中的混淆变量（confound）是什么？\nC）尽管 B 中的陈述如此容易证伪，为什么神经网络没有这样做？"),

    # ---- Round 3: Midterm Foundation Consolidation (L01-L05) ----
    ("Q27", "L01-E01", "r3", "MCQ", "期中巩固 · 方差与解释力", "为什么心理学/多媒体研究几乎达不到 100% 解释力？", [("L01", 18)], False, "L12 第 11–13 页联动", None, None),
    ("Q28", "L02-E01", "r3", "MCQ", "期中巩固 · 研究问题 RQ", "为什么 “Will AI combat the human mind and who will have won?” 不是好 RQ？", [("L02", 68)], False, "L02 理论先于方法", None, None),
    ("Q29", "L03-E01", "r3", "MCQ", "期中巩固 · 启发式测试", "启发式测试（Heuristic test）：由谁来做、成本与速度如何？", [("L03", 54)], False, "L03 质性方法", None, None),
    ("Q30", "L03-E02", "r3", "MCQ", "期中巩固 · 访谈类型", "有预先提纲又允许灵活追问的是哪一种访谈？", [("L03", 56)], False, "L03 质性方法", None, None),
    ("Q31", "L04-E02", "r3", "MCQ", "期中巩固 · 逻辑谬误", "把“决定”不断推向皮层→神经网络→突触→粒子属于什么？", [("L04", 76)], False, "L04 语言哲学", None, None),
    ("Q32", "L04-E03", "r3", "MCQ", "期中巩固 · 意义与指称", "大模型能流畅续写却不知词语指向何物：sense 与 reference 的区分", [("L04", 78)], False, "L04 语言哲学", None, None),
    ("Q33", "L04-E04", "r3", "MCQ", "期中巩固 · 双极量表合并（一）", "两条单极量表在知觉评分为真对立时能否合并为双极量表？", [("L04", 80)], False, "L04 问卷设计", None, None),
    ("Q34", "L04-E05", "r3", "MCQ", "期中巩固 · 双极量表合并（二）", "知觉评分 4 与 0：有对比是否等于正相反？", [("L04", 82)], False, "L04 问卷设计", None, None),
    ("Q35", "L05-E01", "r3", "MCQ", "期中巩固 · Fitts 定律", "胖手指现象（fat-finger syndrome）告诉我们关于 Fitts 定律的什么？", [("L05", 31)], False, "L05 行为测量", None, None),
    ("Q36", "L05-E04", "r3", "MCQ", "期中巩固 · 反向因果推理", "思考→激活皮层，能否反推电刺激皮层→提升思考能力？", [("L05", 101)], False, "L12 第 36–37 页联动（Ex-consequentia）", None, None),
    ("Q37", "L04-E01", "r3", "OpenQ", "期中巩固 · 测量尺度与题项", "Like / I don’t like 按钮与评论框的 4 个小问", [("L04", 74)], False, "L04 问卷设计", None, None),
    ("Q38", "L05-E02", "r3", "OpenQ", "期中巩固 · 心理计时法", "预警信号与对手出现：哪种条件最困难、表现如何？", [("L05", 41)], False, "L05 行为测量", None, None),
    ("Q39", "L05-E03", "r3", "OpenQ", "期中巩固 · 生理测量基线", "语音测谎系统 Truster 为什么彻底失败？（3 小问）", [], False, "原页 L05 s65 已含答案，以下为无剧透原题",
     "Based on the idea that the voice reflects the mood you are in, Libermann developed a computer program to detect whether someone is lying or speaks the truth. The Israeli border police wanted to use this program for their regular check ups. This lie detection system was available on the Dutch market as well under the name Truster. The system needed a practice set of neutrally spoken sentences of the suspect, which served as a baseline to detect discrepancies in the test set. The program detected changes in pitch, speaking pace, and trembling of the voice, which supposedly indicate that a statement is true or false. The system was a complete failure.\nA. What is the mistake in calibrating the system to a neutral voice?\nB. Can you think of other factors that can explain variance in voice pitch, speaking pace, and trembling other than stress by lying?\nC. Can you think of certain types of suspects who show no variance in the said variables and yet can lie?",
     "基于“声音反映情绪”的想法，Libermann 开发了一套测谎软件（Truster）。系统需要先录一段嫌疑人在“中性情绪”下说的话作为基线（baseline），再检测音高（pitch）、语速（speaking pace）和颤抖（trembling）的变化以判断是否说谎。结果该系统彻底失败。\nA. 把系统校准到“中性语音基线”错在哪里？\nB. 除了说谎带来的压力外，还有哪些因素能解释音高、语速和声音颤抖的变异（variance）？\nC. 你能想到哪些类型的嫌疑人即使说谎，在这些语音指标上也不会出现明显变化？"),
]


def img_tag(lid, s):
    p = ROOT / f"assets/img/{lid}/slide-{s:03}.png"
    with p.open("rb") as f:
        w, h = struct.unpack(">II", f.read(24)[16:24])
    src = f"assets/img/{lid}/slide-{s:03}.png"
    lbl = f"{lid} · 第 {s} 页 ({pages[lid]['source_file']})"
    return (
        f'<figure class="q-fig"><a href="{src}" data-image="{src}" data-pdf="pdfs/{lid}.pdf#page={s}" data-label="{E(lbl)}">'
        f'<img src="{src}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{E(lbl)}">'
        f'</a><figcaption>{lid} · PDF 第 {s} 页 · 点击放大查看原图</figcaption></figure>'
    )


def render_zh_simple(md):
    if not md:
        return ""
    s = E(md)
    s = re.sub(
        r"\[\[([^\[\]|]+)\|([^\[\]|]+)\]\]",
        lambda m: f'<mark class="rm-term"><strong>{m.group(1)}</strong>' + ("" if m.group(1).strip().lower() == m.group(2).strip().lower() else f'<span class="rm-en">（{m.group(2)}）</span>') + "</mark>",
        s,
    )
    s = re.sub(r"\*\*([^*\n]+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?m)^###\s+(.*)$", r"<h4>\1</h4>", s)
    return s.replace("\n", "<br>")


cards_html = []
toc_r1, toc_r2, toc_r3 = [], [], []

for qno, qid, rkey, kind, topic, title, stems, is_new, echo, sp_en, sp_zh in ORDER:
    toc_item = f'<a href="#{qno}" data-qno="{qno}"><b>{qno}</b> {E(qid)}</a>'
    if rkey == "r1":
        toc_r1.append(toc_item)
    elif rkey == "r2":
        toc_r2.append(toc_item)
    else:
        toc_r3.append(toc_item)

    imgs_html = "".join(img_tag(lid, s) for lid, s in stems)
    if sp_en:
        imgs_html += (
            f'<div class="sp-box"><div class="sp-h">原题题干（已隐藏原页附带答案，防剧透）</div>'
            f'<div class="sp-en">{E(sp_en).replace(chr(10), "<br>")}</div></div>'
        )
        if qid == "L05-E03":
            imgs_html += f'<details class="zh-aux"><summary>⚠️ 展开原页图片（L05 第 65 页，注意原图已印出答案）</summary>{img_tag("L05", 65)}</details>'

    # Spoiler-free Chinese helper
    if sp_zh:
        zh_aux_body = E(sp_zh).replace("\n", "<br>")
    else:
        zh_parts = []
        for lid, s in stems:
            zt = zh_slides.get(lid, {}).get(str(s), "")
            if zt:
                zh_parts.append(f'<div class="zh-slide-part"><div class="zh-tag">{lid} · 第 {s} 页中文对照</div>{render_zh_simple(zt)}</div>')
        zh_aux_body = "".join(zh_parts)

    zh_drawer = (
        f'<details class="zh-aux"><summary>🔤 查看中文题干（防生词，研究词汇已高亮，不含答案）</summary>'
        f'<div class="zh-aux-body">{zh_aux_body}</div></details>'
    ) if zh_aux_body else ""

    if kind == "MCQ":
        answer_ui = (
            f'<div class="ans-area" data-qno="{qno}" data-qid="{qid}" data-kind="MCQ">'
            '<div class="choice-row">'
            + "".join(f'<button type="button" class="ch-btn" data-choice="{c}" aria-pressed="false">{c}</button>' for c in "ABCD")
            + '</div>'
            '<input type="text" class="reason-inp" placeholder="可选：写一句你选它的理由（发给 AI 对比老师思路更精准）">'
            '</div>'
        )
    elif kind == "MCQ2":
        answer_ui = (
            f'<div class="ans-area" data-qno="{qno}" data-qid="{qid}" data-kind="MCQ2">'
            '<div class="subq-row"><span>第 1 问：</span>'
            + "".join(f'<button type="button" class="ch-btn" data-sub="1" data-choice="{c}" aria-pressed="false">{c}</button>' for c in "ABCD")
            + '</div><div class="subq-row"><span>第 2 问：</span>'
            + "".join(f'<button type="button" class="ch-btn" data-sub="2" data-choice="{c}" aria-pressed="false">{c}</button>' for c in "ABCD")
            + '</div>'
            '<input type="text" class="reason-inp" placeholder="可选：写下你对第 1 问、第 2 问以及能否用 t-test 的判断理由">'
            '</div>'
        )
    else:
        answer_ui = (
            f'<div class="ans-area" data-qno="{qno}" data-qid="{qid}" data-kind="OpenQ">'
            '<textarea class="open-inp" rows="4" placeholder="在这里写下你的简答（建议按 A / B / C 分点，尽量简短精准，贴近老师第 12 讲评分要求）"></textarea>'
            '</div>'
        )

    new_badge = '<span class="badge new">★ L12 新增</span>' if is_new else ""
    kind_lbl = "选择题（2 小题）" if kind == "MCQ2" else ("选择题 MCQ" if kind == "MCQ" else "简答题 OpenQ")
    kind_cls = "mcq" if kind.startswith("MCQ") else "openq"

    cards_html.append(
        f'<article class="q-card" id="{qno}" data-qno="{qno}" data-qid="{qid}" data-round="{rkey}" data-kind="{kind_cls}" data-new="{"1" if is_new else "0"}">'
        f'<div class="q-head">'
        f'<div class="q-meta">'
        f'<span class="qno">{qno}</span><span class="qid">{qid}</span>'
        f'<span class="badge {kind_cls}">{kind_lbl}</span>{new_badge}'
        f'<span class="badge topic">{E(topic)}</span>'
        f'</div>'
        f'<label class="done-chk"><input type="checkbox" data-done="{qno}">已做完</label>'
        f'</div>'
        f'<h2>{E(title)}</h2>'
        f'<p class="q-echo">出处与关联：{E(echo)}</p>'
        f'<div class="q-imgs">{imgs_html}</div>'
        f'{zh_drawer}'
        f'{answer_ui}'
        f'<div class="q-actions">'
        f'<button type="button" class="copy-one" data-copy="{qno}">📋 复制本题答案发给 AI</button>'
        f'<span class="copy-tip" aria-live="polite"></span>'
        f'</div>'
        f'</article>'
    )

# Appendix: L12 s150-158 Naive Bayes worked example
nb_imgs = "".join(img_tag("L12", s) for s in range(150, 159))

page_html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SD5979 本地无剧透全题库（Q01–Q39）</title>
<style>
:root{{--ink:#162d2a;--muted:#526764;--accent:#146957;--paper:#f4f5ef;--white:#fff;--line:#d5dfd7;--hl:#fff0bc;--hlb:#d7971e}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.68;font-size:15.5px}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}
.wrap{{max-width:1120px;margin:0 auto;padding:24px 20px 90px}}
.hero{{background:linear-gradient(135deg,#153e35,#1b6251);color:#fff;border-radius:16px;padding:24px 28px;margin-bottom:18px}}
.hero h1{{margin:0 0 8px;font-size:26px;line-height:1.3}}
.hero p{{margin:4px 0;opacity:.92;font-size:14.5px}}
.hero-links{{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}}
.hero-links a{{background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.32);border-radius:8px;padding:6px 13px;font-size:13px;font-weight:600}}
.hero-links a:hover{{background:rgba(255,255,255,.26);text-decoration:none}}

.toolbar{{position:sticky;top:8px;z-index:20;background:#fffffff2;backdrop-filter:blur(8px);border:1px solid var(--line);border-radius:13px;padding:12px 15px;margin-bottom:18px;box-shadow:0 4px 18px rgba(18,52,44,.08)}}
.tb-row{{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}}
.tb-row+.tb-row{{margin-top:9px;padding-top:9px;border-top:1px solid #e8efe8}}
.pills{{display:flex;gap:7px;flex-wrap:wrap}}
.f-btn{{border:1px solid #b8c9bc;background:#f7faf6;color:var(--ink);border-radius:8px;padding:6px 12px;font-size:13px;font-weight:600;cursor:pointer}}
.f-btn[aria-pressed="true"]{{background:var(--accent);border-color:var(--accent);color:#fff}}
.prog{{font-size:13.5px;font-weight:700;color:var(--accent)}}
.copy-batch{{border:0;background:#164b3e;color:#fff;border-radius:8px;padding:8px 15px;font-size:13.5px;font-weight:700;cursor:pointer}}
.copy-batch:hover{{background:#11392f}}

.toc-box{{background:var(--white);border:1px solid var(--line);border-radius:13px;padding:16px 20px;margin-bottom:22px}}
.toc-box h3{{margin:0 0 10px;font-size:15px;color:var(--accent)}}
.toc-sec{{margin-bottom:10px}}
.toc-sec:last-child{{margin-bottom:0}}
.toc-lbl{{font-size:12.5px;font-weight:700;color:var(--muted);margin-bottom:6px}}
.toc-grid{{display:flex;flex-wrap:wrap;gap:6px}}
.toc-grid a{{font-size:12px;padding:4px 8px;border:1px solid var(--line);border-radius:6px;background:#f8faf7;color:var(--ink)}}
.toc-grid a.is-done{{background:#dff2e6;border-color:#74b995;color:#114b34}}
.toc-grid a b{{color:var(--accent)}}

.q-card{{background:var(--white);border:1px solid var(--line);border-radius:15px;padding:22px 24px;margin-bottom:22px;scroll-margin-top:120px;box-shadow:0 2px 10px rgba(20,50,42,.04)}}
.q-card.is-done{{border-left:5px solid #2b8a62}}
.q-head{{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
.q-meta{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}
.qno{{font-size:16px;font-weight:800;color:#fff;background:var(--accent);padding:2px 10px;border-radius:7px}}
.qid{{font-size:13px;font-weight:700;color:var(--muted);font-family:Consolas,monospace}}
.badge{{font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;border:1px solid var(--line);background:#f3f7f2;color:var(--ink)}}
.badge.mcq{{background:#e9f3fb;border-color:#bdd6ee;color:#1c4f7a}}
.badge.openq{{background:#f4eefb;border-color:#d4c0ee;color:#512c82}}
.badge.new{{background:#fff0bc;border-color:#e4b644;color:#7a4b00}}
.done-chk{{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;color:var(--muted);cursor:pointer;user-select:none}}
.done-chk input{{width:17px;height:17px;accent-color:var(--accent)}}
.q-card h2{{margin:4px 0 4px;font-size:19.5px;line-height:1.38}}
.q-echo{{margin:0 0 14px;font-size:13px;color:var(--muted)}}

.q-imgs{{display:flex;flex-direction:column;gap:12px;margin-bottom:12px}}
.q-fig{{margin:0;border:1px solid #dfe7df;border-radius:10px;overflow:hidden;background:#fff}}
.q-fig a{{display:block}}
.q-fig img{{width:100%;height:auto;display:block;object-fit:contain}}
.q-fig figcaption{{font-size:12px;color:var(--muted);padding:7px 12px;background:#f5f8f3}}
.sp-box{{background:#f8faf6;border:1.5px solid #c5d6c7;border-radius:10px;padding:14px 16px}}
.sp-h{{font-size:12px;font-weight:700;color:var(--accent);margin-bottom:6px}}
.sp-en{{font-size:14.5px;line-height:1.75;color:#1b2c29}}

.zh-aux{{margin:10px 0 14px;border:1px solid #e1e9e1;border-radius:10px;padding:6px 14px;background:#fbfcf8}}
.zh-aux summary{{cursor:pointer;font-size:13.5px;font-weight:700;color:var(--accent);padding:6px 0}}
.zh-aux-body{{padding:8px 0 6px;font-size:14.5px;line-height:1.8}}
.zh-slide-part+.zh-slide-part{{margin-top:12px;padding-top:12px;border-top:1px dashed #d5e0d4}}
.zh-tag{{font-size:12px;font-weight:700;color:var(--muted);margin-bottom:4px}}
.rm-term{{background:var(--hl);border-bottom:2px solid var(--hlb);border-radius:4px;padding:1px 4px;font-weight:700}}
.rm-en{{color:#7a4b00;font-weight:600;font-size:.93em}}

.ans-area{{background:#f5f8f4;border:1px solid #d9e4d9;border-radius:11px;padding:14px 15px;margin-top:10px}}
.choice-row,.subq-row{{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:10px}}
.subq-row>span{{font-size:13.5px;font-weight:700;min-width:60px}}
.ch-btn{{min-width:52px;min-height:42px;border-radius:8px;border:1.5px solid #a9bfb0;background:#fff;color:var(--ink);font-size:15px;font-weight:700;cursor:pointer}}
.ch-btn[aria-pressed="true"]{{background:var(--accent);border-color:var(--accent);color:#fff}}
.reason-inp,.open-inp{{width:100%;border:1px solid #b5c7ba;border-radius:8px;padding:10px 12px;font:inherit;font-size:14.5px;background:#fff;color:var(--ink)}}
.open-inp{{resize:vertical;min-height:96px}}
.q-actions{{display:flex;align-items:center;gap:12px;margin-top:10px;flex-wrap:wrap}}
.copy-one{{border:1px solid var(--accent);background:#eaf3ee;color:var(--accent);border-radius:8px;padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer}}
.copy-one:hover{{background:#d9ece2}}
.copy-tip{{font-size:12.5px;color:#1a7a50;font-weight:600}}

.appendix{{background:var(--white);border:1px solid var(--line);border-top:4px solid var(--accent);border-radius:15px;padding:22px 24px;margin-top:30px}}
.appendix h2{{margin:0 0 8px;font-size:20px}}
.nb-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;margin-top:14px}}

dialog.zoom-dlg{{width:min(1480px,96vw);max-width:96vw;max-height:95vh;border:0;border-radius:12px;padding:0;background:#fafbf7}}
dialog.zoom-dlg::backdrop{{background:rgba(14,38,32,.76)}}
.zbar{{position:sticky;top:0;display:flex;align-items:center;gap:10px;background:#163d35;color:#fff;padding:12px 16px;flex-wrap:wrap}}
.zbar span{{flex:1;font-size:13.5px}}
.zbar button,.zbar a{{font-size:13px;padding:7px 12px;border:1px solid #9db4a7;color:#fff;background:transparent;border-radius:6px;cursor:pointer}}
.zbody{{overflow:auto;max-height:82vh;padding:12px}}
.zbody img{{width:100%;display:block;max-width:none}}
.zbody.big img{{width:180%}}
[hidden]{{display:none!important}}
</style></head>
<body>
<div class="wrap">
  <header class="hero">
    <h1>SD5979 本地无剧透全题库（共 39 组 · Q01–Q39）</h1>
    <p>包含全课程全部 <b>25 组选择题 + 14 组简答题</b>（已完整合并第 12 讲全部 9 组新增/改写例题），默认隐藏答案与勾选页。</p>
    <p>建议按 <b>Q01 → Q15（期末核心选择）→ Q16 → Q26（期末核心简答）→ Q27 → Q39（期中基础巩固）</b> 顺序作答；填好后点「复制发给 AI」，直接粘贴到聊天框，我会逐项对比老师答案与原课件依据帮你分析！</p>
    <div class="hero-links">
      <a href="index.html">← 返回电脑版复习站</a>
      <a href="mobile/index.html">📱 打开手机版复习站</a>
      <a href="#appendix-nb">📎 附录：L12 贝叶斯手算推导示例（s150–158）</a>
    </div>
  </header>

  <div class="toolbar" role="toolbar" aria-label="题库筛选与复制">
    <div class="tb-row">
      <div class="pills">
        <button type="button" class="f-btn" data-filter="all" aria-pressed="true">全部 39 题</button>
        <button type="button" class="f-btn" data-filter="r1" aria-pressed="false">第一轮：期末选择 Q01–Q15</button>
        <button type="button" class="f-btn" data-filter="r2" aria-pressed="false">第二轮：期末简答 Q16–Q26</button>
        <button type="button" class="f-btn" data-filter="r3" aria-pressed="false">第三轮：期中巩固 Q27–Q39</button>
        <button type="button" class="f-btn" data-filter="new" aria-pressed="false">★ 仅看 L12 新增 9 题</button>
        <button type="button" class="f-btn" data-filter="todo" aria-pressed="false">只看未完成</button>
      </div>
      <span class="prog" id="prog-text">已完成 0 / 39 题</span>
    </div>
    <div class="tb-row">
      <span style="font-size:13px;color:var(--muted)">做完 1 题或连续做完几题后，点右侧按钮一键打包复制你的作答发给 AI：</span>
      <button type="button" class="copy-batch" id="copy-batch-btn">📋 打包复制所有已填未提交答案</button>
      <span class="copy-tip" id="batch-tip" aria-live="polite"></span>
    </div>
  </div>

  <section class="toc-box">
    <h3>推荐做题顺序总览（点击题号直达）</h3>
    <div class="toc-sec"><div class="toc-lbl">第一轮 · 期末核心选择题（L07–L12，15 组 / 16 小题，对应期末 10 道选择题范围）</div><div class="toc-grid">{"".join(toc_r1)}</div></div>
    <div class="toc-sec"><div class="toc-lbl">第二轮 · 期末核心简答 / 开放题（L08–L12，11 组，对应期末 2 道大题范围）</div><div class="toc-grid">{"".join(toc_r2)}</div></div>
    <div class="toc-sec"><div class="toc-lbl">第三轮 · 期中基础巩固（L01–L05，10 选择 + 3 简答，查漏补缺联动概念）</div><div class="toc-grid">{"".join(toc_r3)}</div></div>
  </section>

  <main id="q-list">{"".join(cards_html)}</main>

  <section class="appendix" id="appendix-nb">
    <h2>附录：第 12 讲贝叶斯概率手算推导示范（L12 第 150–158 页）</h2>
    <p style="color:var(--muted);font-size:14px;margin:0">这 9 页印有 <code>Exam Sample Item</code> 抬头，属于老师演示 <b>Prior（先验）/ Likelihood（似然）/ Data（数据）/ Posterior（后验归一化）</b> 的分步计算案例（并非发问式考题），建议做完 <b>Q15</b> 与 <b>Q23</b> 后对照查看。</p>
    <div class="nb-grid">{nb_imgs}</div>
  </section>
</div>

<dialog class="zoom-dlg" id="zoom-dlg">
  <div class="zbar"><span id="z-title"></span><button type="button" id="z-toggle">放大 180%</button><a id="z-pdf" target="_blank" rel="noopener">打开 PDF 原页</a><button type="button" id="z-close">关闭 Esc</button></div>
  <div class="zbody" id="z-body"><img id="z-img" alt="原题大图"></div>
</dialog>

<script>
(()=>{{'use strict';
const KEY='sd5979-quiz-bank-v1';
const load=()=>{{try{{return JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch{{return {{}}}}}};
let db=load();
const save=()=>{{try{{localStorage.setItem(KEY,JSON.stringify(db))}}catch{{}}}};

const cards=[...document.querySelectorAll('.q-card')];
const tocLinks=[...document.querySelectorAll('.toc-grid a')];

const refreshProg=()=>{{
  let done=0;
  cards.forEach(c=>{{
    const q=c.dataset.qno, isDone=!!db[q]?.done;
    if(isDone)done++;
    c.classList.toggle('is-done',isDone);
    const cb=c.querySelector('input[data-done]');
    if(cb)cb.checked=isDone;
  }});
  tocLinks.forEach(a=>a.classList.toggle('is-done',!!db[a.dataset.qno]?.done));
  document.getElementById('prog-text').textContent=`已完成 ${{done}} / ${{cards.length}} 题`;
}};

// Restore & bind inputs
cards.forEach(c=>{{
  const q=c.dataset.qno, st=db[q]||{{}}, area=c.querySelector('.ans-area'), kind=area.dataset.kind;
  const cb=c.querySelector('input[data-done]');
  cb.addEventListener('change',()=>{{db[q]=Object.assign(db[q]||{{}},{{done:cb.checked}});save();refreshProg();applyFilter()}});
  if(kind==='MCQ'){{
    area.querySelectorAll('.ch-btn').forEach(b=>{{
      b.setAttribute('aria-pressed',String(b.dataset.choice===st.choice));
      b.addEventListener('click',()=>{{
        db[q]=Object.assign(db[q]||{{}},{{choice:b.dataset.choice}});save();
        area.querySelectorAll('.ch-btn').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
      }});
    }});
    const inp=area.querySelector('.reason-inp');
    inp.value=st.reason||'';
    inp.addEventListener('input',()=>{{db[q]=Object.assign(db[q]||{{}},{{reason:inp.value}});save()}});
  }}else if(kind==='MCQ2'){{
    ['1','2'].forEach(sub=>{{
      area.querySelectorAll(`.ch-btn[data-sub="${{sub}}"]`).forEach(b=>{{
        b.setAttribute('aria-pressed',String(b.dataset.choice===st['c'+sub]));
        b.addEventListener('click',()=>{{
          db[q]=Object.assign(db[q]||{{}},{{['c'+sub]:b.dataset.choice}});save();
          area.querySelectorAll(`.ch-btn[data-sub="${{sub}}"]`).forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
        }});
      }});
    }});
    const inp=area.querySelector('.reason-inp');
    inp.value=st.reason||'';
    inp.addEventListener('input',()=>{{db[q]=Object.assign(db[q]||{{}},{{reason:inp.value}});save()}});
  }}else{{
    const ta=area.querySelector('.open-inp');
    ta.value=st.text||'';
    ta.addEventListener('input',()=>{{db[q]=Object.assign(db[q]||{{}},{{text:ta.value}});save()}});
  }}
}});

const formatAnswer=c=>{{
  const q=c.dataset.qno, qid=c.dataset.qid, st=db[q]||{{}}, kind=c.querySelector('.ans-area').dataset.kind;
  if(kind==='MCQ'){{
    if(!st.choice && !(st.reason||'').trim()) return '';
    return `【${{q}} | ${{qid}}】我的选择：${{st.choice||'未选'}}${{(st.reason||'').trim()?'\\n我的理由：'+st.reason.trim():''}}`;
  }}
  if(kind==='MCQ2'){{
    if(!st.c1 && !st.c2 && !(st.reason||'').trim()) return '';
    return `【${{q}} | ${{qid}}】我的选择：第1问 ${{st.c1||'未选'}} / 第2问 ${{st.c2||'未选'}}${{(st.reason||'').trim()?'\\n我的理由：'+st.reason.trim():''}}`;
  }}
  if(!(st.text||'').trim()) return '';
  return `【${{q}} | ${{qid}}】我的简答：\\n${{st.text.trim()}}`;
}};

const doCopy=async (txt, tipEl)=>{{
  if(!txt){{tipEl.textContent='请先选择选项或写下回答再复制';return}}
  try{{await navigator.clipboard.writeText(txt);tipEl.textContent='✓ 已复制！直接 Ctrl+V 发给 AI 即可'}}
  catch{{const ta=document.createElement('textarea');ta.value=txt;document.body.append(ta);ta.select();document.execCommand('copy');ta.remove();tipEl.textContent='✓ 已复制！直接 Ctrl+V 发给 AI 即可'}}
  setTimeout(()=>{{tipEl.textContent=''}},3500);
}};

cards.forEach(c=>{{
  const btn=c.querySelector('.copy-one'), tip=c.querySelector('.copy-tip');
  btn.addEventListener('click',()=>doCopy(formatAnswer(c),tip));
}});

document.getElementById('copy-batch-btn').addEventListener('click',()=>{{
  const parts=cards.filter(c=>!c.hidden).map(formatAnswer).filter(Boolean);
  doCopy(parts.join('\\n\\n'),document.getElementById('batch-tip'));
}});

// Filters
let curFilter='all';
const fBtns=[...document.querySelectorAll('.f-btn')];
const applyFilter=()=>{{
  cards.forEach(c=>{{
    let show=true;
    if(curFilter==='r1'||curFilter==='r2'||curFilter==='r3') show=c.dataset.round===curFilter;
    else if(curFilter==='new') show=c.dataset.new==='1';
    else if(curFilter==='todo') show=!db[c.dataset.qno]?.done;
    c.hidden=!show;
  }});
}};
fBtns.forEach(b=>b.addEventListener('click',()=>{{
  curFilter=b.dataset.filter;
  fBtns.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));
  applyFilter();
}}));
refreshProg();

// Zoom dialog
const dlg=document.getElementById('zoom-dlg'), zImg=document.getElementById('z-img'), zBody=document.getElementById('z-body'), zTog=document.getElementById('z-toggle');
document.addEventListener('click',e=>{{
  const a=e.target.closest('a[data-image]');if(!a)return;
  e.preventDefault();
  zImg.src=a.dataset.image;
  document.getElementById('z-title').textContent=a.dataset.label||'';
  document.getElementById('z-pdf').href=a.dataset.pdf||a.dataset.image;
  zBody.classList.remove('big');zTog.textContent='放大 180%';
  dlg.showModal();
}});
document.getElementById('z-close').addEventListener('click',()=>dlg.close());
zTog.addEventListener('click',()=>{{const on=zBody.classList.toggle('big');zTog.textContent=on?'适应宽度':'放大 180%'}});
dlg.addEventListener('click',e=>{{if(e.target===dlg)dlg.close()}});
}})();
</script>
</body></html>"""

out = ROOT / "quiz-bank.html"
out.write_text(page_html, encoding="utf-8")
print(f"BUILT {out} ({len(ORDER)} ordered questions + 9 Naive Bayes appendix slides, {len(page_html):,} bytes)")
