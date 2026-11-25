"""Extract the teacher's OWN concept PHRASES from Contents-of-today / outline pages.

Design rules (driven by user feedback: concepts are phrases, not single words):
  * Only "Contents of today" pages + early lecture outline pages (slide <= 20).
  * Merge soft-wrap continuation lines ONLY when they look like a phrase tail.
  * Drop lecture-number headers, "Main lesson" summary sentences, page numbers.
  * Drop isolated single-word list items (Linear / Multiple / Nominal / ...),
    except a small whitelist of genuine standalone terms the teacher listed.
  * If a single word is part of a listed phrase, the phrase wins.
"""
import json, pathlib, re, sys
from collections import OrderedDict
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
P = ROOT / "data/pages"
OUT = ROOT / "data/concepts_raw.json"
REPORT = ROOT / "data/reports/contents_concepts.md"

BULLETS = "\uf071●\uf02d\uf0b7\uf0ae•"
PAGE_RE = re.compile(r"^\s*\d+\s*/?\s*\d*\s*$")
NUMHEAD_RE = re.compile(r"^\d{2}\s")
DROP_RE = re.compile(
    r"^(Contents of today|What you will learn today|Main lessons?:|Main lesson:|"
    r"Summ?ary|Overview|Last time:|Main lesson of Lecture|Learning objectives)", re.I)
# Genuine standalone single-word terms the teacher explicitly listed
KEEP_SINGLE = {
    "variance", "ethnography", "triangulation", "argumentation", "hypotheses",
    "classification", "sem", "amos", "correlations", "interview", "eye-tracking",
}
TAIL_START = set("(,:“\"'‘’")


def canon(s):
    s = re.sub(r"[\uf000-\uf8ff\u00ad]", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def clean_line(l):
    return re.sub(r"^[" + re.escape(BULLETS) + r"]+\s*", "", l.strip()).strip()


def is_bullet(l):
    return bool(l) and l[0] in BULLETS


def extract(page_text, lid, slide, kind):
    # L01's "sneak preview" outline pages preview lectures 02-11; the concepts
    # listed there actually BELONG to those later lectures, not to L01.
    owner = lid
    if lid == "L01" and kind == "outline":
        m = re.search(r"\uf071(\d{2})\s", page_text)
        if m:
            owner = "L%02d" % int(m.group(1))
    lines = [x.strip() for x in page_text.splitlines()]
    items, cur = [], None
    for l in lines:
        if not l or PAGE_RE.match(l):
            continue
        if is_bullet(l):
            if cur:
                items.append(cur)
            cur = clean_line(l)
        elif cur is not None:
            tailish = (l[0].islower() or l[0] in TAIL_START
                       or (len(l) > 10 and any(c in l for c in ",()"))
                       or cur.endswith((",", ":")))
            if (DROP_RE.match(l) or l.startswith("Main lesson")
                    or len(l) < 4 or not tailish or len(cur) + len(l) > 120):
                items.append(cur)
                cur = None
            else:
                cur = (cur + " " + l).strip()
    if cur:
        items.append(cur)

    out = []
    for it in items:
        it = re.sub(r"\s+", " ", it).strip()
        if not it or DROP_RE.match(it) or NUMHEAD_RE.match(it):
            continue
        c = canon(it)
        if len(c) < 3 or len(it) > 120:
            continue
        if " " not in c and c not in KEEP_SINGLE:
            continue  # isolated single-word list item -> discard
        out.append({"text": it, "lecture": lid, "slide": slide,
                    "kind": kind, "canon": c, "owner_lecture": owner})
    return out


all_items = []
per_lec = OrderedDict()
for f in sorted(P.glob("L[0-9][0-9].json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    lid = f.stem
    per_lec[lid] = []
    for p in d["pages"]:
        t = p["text"]
        is_contents = "Contents of today" in t
        is_outline = (p["slide"] <= 20
                      and ("main_lesson" in p["flags"] or "What you will learn" in t)
                      and any(b in t for b in "●\uf02d\uf071"))
        if not (is_contents or is_outline):
            continue
        kind = "contents" if is_contents else "outline"
        got = extract(t, lid, p["slide"], kind)
        per_lec[lid].extend(got)
        all_items.extend(got)

# NOTE: do NOT drop a concept just because it is a substring of a longer one.
# "Linear regression" and "Multiple linear regression" are BOTH teacher-listed
# phrases and must both survive. Single-word list items are already filtered by
# KEEP_SINGLE above. Spelling variants (Modeling/Modelling) are handled later as
# term variants so both spellings map to one glossary entry.

# global dedupe, prefer 'contents'
seen = {}
for it in all_items:
    k = it["canon"]
    if k not in seen or (it["kind"] == "contents" and seen[k]["kind"] != "contents"):
        seen[k] = it
concepts = list(seen.values())

OUT.write_text(json.dumps({"per_lecture": per_lec, "concepts": concepts},
                          ensure_ascii=False, indent=1), encoding="utf-8")
rep = ["# 老师目录 / 大纲中的词组概念清单（新术语表主干）", "",
       "来源：每讲 `Contents of today` 页 + 讲次 `What you will learn today` / `Main lesson` 大纲页；"
       "bullet 条目**逐字取自 PPT**，仅合并软换行。", "",
       "- 清洗后 bullet 条目：%d 条" % len(all_items),
       "- 全局去重概念：**%d 条**" % len(concepts),
       "- 来自 Contents of today：%d 条 / 来自大纲页：%d 条" % (
           sum(1 for c in concepts if c["kind"] == "contents"),
           sum(1 for c in concepts if c["kind"] == "outline")),
       "- 多词词组占比：%.1f%%" % (100.0 * sum(1 for c in concepts if " " in c["canon"]) / len(concepts)),
       "", "## 全局概念清单（%d 条）" % len(concepts), ""]
for i, c in enumerate(concepts, 1):
    rep.append("%3d. %s  ← %s · Slide %d (%s)" % (i, c["text"], c["lecture"], c["slide"], c["kind"]))
REPORT.write_text("\n".join(rep), encoding="utf-8")
print("CLEAN_ITEMS", len(all_items), "CONCEPTS", len(concepts))
print("MULTIWORD", sum(1 for c in concepts if " " in c["canon"]), "/", len(concepts))
print("BY_KIND", {k: sum(1 for c in concepts if c["kind"] == k) for k in ("contents", "outline")})
for i, c in enumerate(concepts, 1):
    print("%3d. %s  [%s s%d]" % (i, c["text"], c["lecture"], c["slide"]))
