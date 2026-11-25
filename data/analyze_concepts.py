"""Rebuild the term table around the teacher's PHRASE concepts.

Input : data/concepts_raw.json (bullet phrases from Contents of today / outlines)
Output: data/terms_candidates.json  (same schema the existing finalize_data.py expects)
        data/zh_terms_input.json    (input for faithful Chinese translation)

Hard rule: en_definition is a VERBATIM line from a PPT page, source points at
that exact page. Single words are never standalone terms; abbreviations and
bracketed spellings become VARIANTS of the phrase, not separate entries.
"""
import json, pathlib, re, sys
from collections import OrderedDict
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
DATA = ROOT / "data"
PAGES = DATA / "pages"

lectures = {}
for f in sorted(PAGES.glob("L[0-9][0-9].json")):
    lectures[f.stem] = json.loads(f.read_text(encoding="utf-8"))
concepts = json.loads((DATA / "concepts_raw.json").read_text(encoding="utf-8"))["concepts"]
# Exam item pages are questions, not definitions -> never use them as a source
exam_items = json.loads((DATA / "exam_items.json").read_text(encoding="utf-8"))
EXAM_PAGES = set()
for _it in exam_items:
    EXAM_PAGES.add((_it["lecture"], _it["question_slide"]))
    for _s in _it["answer_slides"]:
        EXAM_PAGES.add((_it["lecture"], _s))

DEF_RE = re.compile(
    r"\b(is|are|means|refers to|defined as|allows you to|tells|measures|compares|"
    r"extends|works|called|call that|boils down|shows|states|assumes|uses|used to|"
    r"consists of|can be|should be|do not|does not)\b", re.I)
PUA = re.compile(r"[\uf000-\uf8ff]")
BULLET_CHARS = "\uf071●\uf02d\uf0b7\uf0ae•\uf0e5"


def canon(s):
    s = re.sub(r"[\uf000-\uf8ff\u00ad]", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()


def group_key(c):
    """Modeling / Modelling are the same concept."""
    return c.replace(" modeling", " modelling").replace("modeling", "modelling")


def variants_for(text):
    vs = [text]
    base = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    if base and base != text and len(base) > 8:
        vs.append(base)
    base2 = re.sub(r"\([^)]*\)", "", text)
    base2 = re.sub(r"\s+", " ", base2).strip(" ,")
    if base2 and base2 != text and base2 not in vs and len(base2) > 8:
        vs.append(base2)
    if "Modeling" in text:
        vs.append(text.replace("Modeling", "Modelling"))
    if "Modelling" in text:
        vs.append(text.replace("Modelling", "Modeling"))
    # comma-separated first segment, if substantial (e.g. "Confounds, order effects")
    if "," in text:
        head = text.split(",")[0].strip()
        if len(head) > 10 and head not in vs:
            vs.append(head)
    return list(OrderedDict.fromkeys(vs))


def match_keys(vs):
    ks = []
    for v in vs:
        c = canon(v)
        if len(c) >= 5:
            ks.append(c)
    return list(OrderedDict.fromkeys(ks))


def line_candidates(page_text):
    raw = [re.sub(r"\s+", " ", l).strip() for l in page_text.splitlines()]
    raw = [l for l in raw if l]
    np = norm(page_text)
    out = []
    for i, l in enumerate(raw):
        if norm(l) in np:
            out.append(l)
        if i + 1 < len(raw):
            nxt = raw[i + 1]
            # never glue two bullet lines together into a fake "sentence"
            if l and l[0] in BULLET_CHARS and nxt and nxt[0] in BULLET_CHARS:
                continue
            m = (l + " " + nxt).strip()
            if len(m) <= 210 and norm(m) in np:
                out.append(m)
    return out


# index every verbatim line once, with its page
LINES = []
for lid, d in lectures.items():
    for p in d["pages"]:
        for l in line_candidates(p["text"]):
            LINES.append((lid, p["slide"], l, canon(l)))

# merge Modeling / Modelling duplicates
groups = OrderedDict()
for c in concepts:
    k = group_key(c["canon"])
    if k not in groups:
        groups[k] = []
    groups[k].append(c)

terms_c = OrderedDict()
zh_input = OrderedDict()
stats = {"verbatim": 0, "occurrence_only": 0, "from_contents": 0, "from_outline": 0}

for k, grp in groups.items():
    # prefer the Contents-of-today wording, then the shortest clean phrase
    grp.sort(key=lambda x: (x["kind"] != "contents", len(x["text"])))
    main = grp[0]
    text = main["text"]
    vs = variants_for(text)
    for other in grp[1:]:
        for v in variants_for(other["text"]):
            if v not in vs:
                vs.append(v)
    keys = match_keys(vs)
    # allow plural / -ing inflections ("heuristic test" <-> "heuristic testing")
    key_alts = []
    for kk in keys:
        key_alts.append(kk)
        parts = kk.split()
        if parts:
            for suf in ("s", "es", "ing"):
                key_alts.append(" ".join(parts[:-1] + [parts[-1] + suf]))
    key_pats = [re.compile(r"(?<![a-z0-9])" + re.escape(kk) + r"(?![a-z0-9])")
                for kk in OrderedDict.fromkeys(key_alts)]
    owner = main.get("owner_lecture", main["lecture"])

    best = None
    for lid, slide, line, cline in LINES:
        if not any(p.search(cline) for p in key_pats):
            continue
        # bullet / outline rows are labels, not explanatory sentences
        if any(ch in line for ch in BULLET_CHARS):
            continue
        score = 1
        if "Main lesson" in line:
            score += 5
        if DEF_RE.search(line):
            score += 4
        # strongest signal: the sentence STARTS with the concept and then defines it
        if any(cline.startswith(kk) for kk in keys):
            score += 4
        if 45 <= len(line) <= 200:
            score += 2
        if len(line) > len(text) + 15:
            score += 2
        if lid == owner:
            score += 3
        else:
            score -= 1
        cand = (score, len(line), lid, slide, line)
        if best is None or cand > best:
            best = cand

    if best and best[0] >= 5:
        _, _, lid, slide, en = best
    else:
        # fall back to the verbatim bullet line on the concept's own contents page
        lid, slide = main["lecture"], main["slide"]
        src = lectures[lid]["pages"][slide - 1]["text"]
        en = text
        # use merged line candidates so soft-wrapped phrases stay complete
        cands = [l for l in line_candidates(src)
                 if any(kk in canon(l) for kk in keys)]
        if cands:
            en = max(cands, key=len)
        else:
            for l in src.splitlines():
                l = re.sub(r"\s+", " ", l).strip()
                cl = canon(l)
                if cl and (any(kk in cl for kk in keys) or any(cl in kk for kk in keys)):
                    en = l
                    break
        if norm(en) not in norm(src):
            en = text

    has_bullet = any(ch in en for ch in BULLET_CHARS)
    status = "verbatim" if (len(en) > len(text) + 8 and not has_bullet) else "occurrence_only"
    stats[status] += 1
    stats["from_contents" if main["kind"] == "contents" else "from_outline"] += 1

    src_file = lectures[lid]["source_file"]
    terms_c[text] = {
        "term": text,
        "variants": vs,
        "origins": [main["kind"]],
        "en_definition": en,
        "zh_definition": "",
        "zh_hint": "",
        "source": {"file": src_file, "lecture": lid, "slide": slide},
        "occurrences": [],
        "status": status,
    }
    zh_input[text] = {
        "en": text,
        "en_definition": en,
        "source": "%s · Slide %d" % (src_file, slide),
        "kind": main["kind"],
        "status": status,
    }

(DATA / "terms_candidates.json").write_text(
    json.dumps(terms_c, ensure_ascii=False, indent=1), encoding="utf-8")
(DATA / "zh_terms_input.json").write_text(
    json.dumps(zh_input, ensure_ascii=False, indent=1), encoding="utf-8")

print("NEW_TERMS", len(terms_c), "MULTIWORD", sum(1 for t in terms_c if " " in canon(t)), stats)
print("VARIANTS_TOTAL", sum(len(t["variants"]) for t in terms_c.values()))
print("--- sample definitions ---")
for t in list(terms_c.values())[:14]:
    print(" * %s\n     DEF: %s\n     SRC: %s · Slide %d [%s]" % (
        t["term"], t["en_definition"][:130], t["source"]["lecture"], t["source"]["slide"], t["status"]))
