"""Dump every 'Contents of today' page and every main_lesson/outline page verbatim."""
import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
P = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method/data/pages")
OUT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method/data/reports/contents_raw.md")

lines = ["# 老师目录 / 大纲页逐字原文（Contents of today & Main lesson）", "",
         "抽取自 `data/pages/*.json`（逐字来自 Canvas PDF）。", ""]
for f in sorted(P.glob("L[0-9][0-9].json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    lid = f.stem
    picked = [p for p in d["pages"]
              if "Contents of today" in p["text"] or "main_lesson" in p["flags"]
              or "summary_or_contents" in p["flags"]]
    if not picked:
        continue
    lines += ["", "## %s · %s" % (lid, d["source_file"]), ""]
    for p in picked:
        lines += ["### Slide %d  flags=%s" % (p["slide"], ",".join(p["flags"]) or "-"), "",
                  "```text", p["text"].rstrip(), "```", ""]
OUT.write_text("\n".join(lines), encoding="utf-8")
print("WROTE", OUT, "lectures", len(list(P.glob('L[0-9][0-9].json'))),
      "pages", sum(1 for l in lines if l.startswith("### Slide")))
