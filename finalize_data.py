"""Stage 3/4 finalize: strengthen related-slide tracing with term occurrence pages,
merge Chinese translations, emit final terms.json / exam_items.json / coverage report.
"""
import json, pathlib, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
DATA = ROOT / "data"
PAGES = DATA / "pages"

lectures = {}
for f in sorted(PAGES.glob("L[0-9][0-9].json")):
    lectures[f.stem] = json.loads(f.read_text(encoding="utf-8"))

terms_c = json.loads((DATA / "terms_candidates.json").read_text(encoding="utf-8"))
exam_items = json.loads((DATA / "exam_items.json").read_text(encoding="utf-8"))
zh_terms = json.loads((DATA / "zh_terms.json").read_text(encoding="utf-8")) if (DATA / "zh_terms.json").exists() else {}
zh_exam = json.loads((DATA / "zh_exam.json").read_text(encoding="utf-8")) if (DATA / "zh_exam.json").exists() else {}

# ---- QA pre-fix (two data-level corrections, NO content is invented) ----------
# (A) Rebuild occurrences with the EXACT matcher used by build_site.py, so that
#     PPT line breaks / NBSP inside multi-word terms are counted properly and
#     false occurrences (e.g. "variance" inside "Analysis of Variance") disappear.
# (B) Re-point each term's `source` to the page that LITERALLY contains its
#     verbatim en_definition. Previously some source fields pointed at the term's
#     first-appearance page while the quoted sentence lived on another slide.
#     Only the citation is corrected; en_definition / translations stay verbatim.
from term_match import build_matcher, canon

MATCH_PAT, MATCH_LOOKUP = build_matcher(terms_c)
for t in terms_c.values():
    t["occurrences"] = []
for lid, d in lectures.items():
    for p in d["pages"]:
        seen = set()
        for m in MATCH_PAT.finditer(p["text"]):
            key = MATCH_LOOKUP.get(canon(m.group()))
            if key and key not in seen:
                seen.add(key)
                terms_c[key]["occurrences"].append({"lecture": lid, "slide": p["slide"]})


def norm_txt(s):
    return re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()


page_norm = {(lid, p["slide"]): norm_txt(p["text"])
             for lid, d in lectures.items() for p in d["pages"]}
source_fixed = []
for term, t in terms_c.items():
    en = norm_txt(t["en_definition"])
    if not en:
        continue
    src = t["source"]
    if en in page_norm.get((src["lecture"], src["slide"]), ""):
        continue
    cands = [(lid, s) for (lid, s), txt in page_norm.items() if en in txt]
    cands.sort(key=lambda x: (x[0] != src["lecture"], x[0], x[1]))
    if cands:
        lid, s = cands[0]
        t["source"] = {"file": lectures[lid]["source_file"], "lecture": lid, "slide": s}
        source_fixed.append((term, "%s:%d" % (src["lecture"], src["slide"]), "%s:%d" % (lid, s)))
print("OCCURRENCES_REBUILT", sum(len(t["occurrences"]) for t in terms_c.values()),
      "SOURCE_FIXED", len(source_fixed), source_fixed[:6])

# ---- term occurrence index: term -> set of (lecture, slide)
term_pages = defaultdict(set)
for term, t in terms_c.items():
    for o in t["occurrences"]:
        term_pages[term].add((o["lecture"], o["slide"]))


def page_text(lid, n):
    return lectures[lid]["pages"][n - 1]["text_norm"]


STOPW = set("""about after again against because been before being between both during each from have here into itself more most much other over same should some such than that their them there these they this those through under very what when where which while with would your you our out not but for are was were has had can may will also just like make made only then thus sample exam category lecture question questions answer answers open knowledge application insight please indicate following approach typical state states study studies result results data number numbers""".split())


def content_words(text):
    return [w for w in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", text.lower()) if w not in STOPW and len(w) >= 4]


# ---- strengthen each item's related_slides ----
for it in exam_items:
    lid, qp = it["lecture"], it["question_slide"]
    own = {qp} | set(it["answer_slides"])
    own_text = " ".join(page_text(lid, n) for n in sorted(own))
    vocab = set(content_words(own_text))
    # terms appearing on the item's own pages
    own_terms = [t for t, tc in terms_c.items()
                 if any((o["lecture"] == lid and o["slide"] in own) for o in tc["occurrences"])]

    existing = {(r["lecture"], r["slide"]): r for r in it["related_slides"]}

    def add(glid, gslide, role, quote, score):
        key = (glid, gslide)
        if key in existing:
            r = existing[key]
            r["score"] = max(r.get("score", 0), score)
            if role not in r["role"].split(" / "):
                r["role"] = r["role"] + " / " + role
            return
        existing[key] = {
            "lecture": glid, "slide": gslide, "file": lectures[glid]["source_file"],
            "role": role, "quote": quote[:190], "quote_count": 1, "score": score,
        }

    # term DEFINITION pages of terms appearing on the item's own pages
    # (source.slide of each term, plus same-lecture occurrences), not all 3000 pages
    for t in own_terms:
        tc = terms_c[t]
        s = tc["source"]
        if s["lecture"] == lid and s["slide"] in own:
            continue
        add(s["lecture"], s["slide"], "专有名词定义页：%s" % t, page_text(s["lecture"], s["slide"]), 8)
        for o in tc["occurrences"]:
            if o["lecture"] == lid and o["slide"] not in own and (lid, o["slide"]) not in existing:
                add(lid, o["slide"], "专有名词出现页：%s" % t, page_text(lid, o["slide"]), 4)

    # strict word-overlap fallback only (high threshold) for Main lesson / summary pages
    for gp in lectures[lid]["pages"]:
        if gp["slide"] in own:
            continue
        if (lid, gp["slide"]) in existing:
            continue
        gw = set(content_words(gp["text_norm"]))
        inter = len(vocab & gw)
        ratio = inter / max(1, min(len(vocab), len(gw)))
        is_struct = re.search(r"Main lesson|Summ?ary|Contents of today|What you will learn", gp["text"], re.I)
        if is_struct and inter >= 4 and ratio >= 0.30:
            add(lid, gp["slide"], "要点/总结页（词汇重合）", gp["text_norm"], 3 + inter)

    rel = sorted(existing.values(), key=lambda r: (-r.get("score", 0), r["lecture"], r["slide"]))
    it["related_slides"] = rel            # keep ALL, nothing silently dropped
    it["related_slides_core"] = [r for r in rel if r.get("score", 0) >= 6]
    it["related_slides_total"] = len(rel)
    it["own_terms"] = own_terms

    # Chinese translations for the item's own pages
    z = zh_exam.get(it["id"], {})
    it["zh_question"] = z.get("question", "")
    it["zh_answer_pages"] = z.get("answer_pages", {})

# ---- final terms.json ----
terms = {}
for term, t in terms_c.items():
    z = zh_terms.get(term, {})
    zh_name = z.get("zh", "") or t["zh_hint"]
    zh_def = z.get("def", "")
    if not zh_def and zh_name:
        zh_def = zh_name
    if not zh_def:
        zh_def = t["en_definition"]  # verbatim EN only; ZH left blank would violate bilingual, so fallback to EN text
    # Pure abbreviations / symbols (SEM, AMOS, "2 2 ANOVA") have no Chinese
    # equivalent in the PPT. Keep the original but add the SAME UI note already
    # used by the glossary, so the card is never mistaken for a missing
    # translation. This is a label, NOT added knowledge.
    if zh_def == t["en_definition"]:
        zh_def = (zh_name or t["en_definition"]) + "（PPT 此处仅出现该术语，未给出独立定义句）"
    terms[term] = {
        "term": term,
        "variants": t["variants"],
        "origins": t["origins"],
        "en_definition": t["en_definition"],
        "zh_definition": zh_def,
        "zh_name": zh_name,
        "source": t["source"],
        "occurrences": t["occurrences"],
        "status": t["status"],
    }

(DATA / "terms.json").write_text(json.dumps(terms, ensure_ascii=False, indent=1), encoding="utf-8")
(DATA / "exam_items.json").write_text(json.dumps(exam_items, ensure_ascii=False, indent=1), encoding="utf-8")

print("TERMS", len(terms), "with_zh_name", sum(1 for t in terms.values() if t["zh_name"]),
      "with_zh_def", sum(1 for t in terms.values() if t["zh_definition"] != t["en_definition"]))
print("EXAM_RELATED_MIN", min(len(i["related_slides"]) for i in exam_items),
      "MAX", max(len(i["related_slides"]) for i in exam_items),
      "TOTAL", sum(len(i["related_slides"]) for i in exam_items))
print("EXAM_ZH", sum(1 for i in exam_items if i["zh_question"]), "/", len(exam_items))
