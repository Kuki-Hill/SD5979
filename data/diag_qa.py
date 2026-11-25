"""Diagnose the 3 QA FAILs before fixing."""
import json, pathlib, re, html, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
DATA = ROOT / "data"
terms = json.loads((DATA / "terms.json").read_text(encoding="utf-8"))
lectures = {}
for f in sorted((DATA / "pages").glob("L[0-9][0-9].json")):
    lectures[f.stem] = json.loads(f.read_text(encoding="utf-8"))

def norm(s):
    return re.sub(r"\s+", " ", s.replace("\u00ad", "")).strip()

BAD = ['experiment design', 'control group', 'curve fitting', 'Grady', 'Schellens',
       'Braun', 'MC', 'totally disagree', 'Douglas Engelbart', 'Dawson',
       'frequentist statistics', 'Konijn', 'Pontier']
print("########## PART 1: 13 verbatim-definition mismatches ##########")
for k in BAD:
    t = terms[k]
    d = norm(t["en_definition"])
    hits = []
    for lid, dd in lectures.items():
        for p in dd["pages"]:
            if d in norm(p["text"]):
                hits.append((lid, p["slide"]))
    print("=" * 78)
    print("TERM:", k, "| status:", t["status"], "| source:", t["source"])
    print("  EN_DEF :", repr(t["en_definition"]))
    print("  ZH_DEF :", repr(t["zh_definition"]))
    print("  ZH_NAME:", repr(t["zh_name"]))
    print("  HITS   :", hits[:14], "total", len(hits))
    src = t["source"]
    if src["lecture"] in lectures and src["slide"] <= lectures[src["lecture"]]["page_count"]:
        raw = lectures[src["lecture"]]["pages"][src["slide"] - 1]["text"]
        print("  SRC_PAGE_VERBATIM_HIT:", d in norm(raw))
        print("  SRC_PAGE_TEXT:", repr(raw[:500]))

print()
print("########## PART 2: uncovered term occurrences ##########")
# reproduce QA uncovered list
uncovered = []
for lid, d in lectures.items():
    f = ROOT / "lectures" / (lid + ".html")
    txt = f.read_text(encoding="utf-8") if f.exists() else ""
    for k, t in terms.items():
        needle = 'data-term="%s"' % html.escape(k, quote=True)
        for o in t["occurrences"]:
            if o["lecture"] == lid and needle not in txt:
                uncovered.append((lid, o["slide"], k))
                break
print("UNCOVERED", len(uncovered))
# dedupe by (lid,k) and show raw text shape
seen = set()
for lid, s, k in uncovered:
    if (lid, k) in seen:
        continue
    seen.add((lid, k))
    t = terms[k]
    raw = lectures[lid]["pages"][s - 1]["text"]
    first = k.split()[0]
    idx = raw.lower().find(first.lower())
    snip = raw[max(0, idx - 60):idx + 140] if idx >= 0 else raw[:200]
    print("-" * 78)
    print("(%s, s%d) %s variants=%s" % (lid, s, k, t["variants"]))
    print("   NORM_HAS:", k.lower() in norm(raw).lower())
    print("   RAW_SNIP:", repr(snip))
