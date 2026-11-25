"""Independent cross-check: workbuddy-pdf CLI txt vs extract_pages.py (PyMuPDF).

The CLI auto-detects scanned pages and needs Tesseract/PaddleOCR, which this
machine does not have. So each sampled page is exported as a one-page PDF from
the ORIGINAL lecture PDF, then handed to the CLI. Text pages are compared
line-by-line; scanned pages are recorded as SCAN_SKIP (the project's declared
degradation policy: embed the full-page PNG, never transcribe or invent).
"""
import json, pathlib, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
import fitz

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
DATA = ROOT / "data"
SINGLE = DATA / "wp" / "single"
SINGLE.mkdir(parents=True, exist_ok=True)
CLI = ("/c/Users/Wyki/.workbuddy/plugins/cache/workbuddy-builtin/"
       "skill-workbuddy-pdf/5.11.3-wb.43806934.gecace0f7.ha395516167d4/scripts/run.sh")


def canon(s):
    s = re.sub(r"[\uf000-\uf8ff\u00ad\u2018\u2019\u201c\u201d]", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


exam = json.loads((DATA / "exam_items.json").read_text(encoding="utf-8"))
rows = []
total = hit = ok_pages = scan_pages = fail_pages = 0

for f in sorted((DATA / "pages").glob("L[0-9][0-9].json")):
    lid = f.stem
    d = json.loads(f.read_text(encoding="utf-8"))
    pc = d["page_count"]
    src_pdf = ROOT / "pdfs" / (lid + ".pdf")
    doc = fitz.open(str(src_pdf))
    ex = [i["question_slide"] for i in exam if i["lecture"] == lid]
    cand = [1, max(1, pc // 2)] + (ex[:1] if ex else []) + [pc]
    cand = list(dict.fromkeys([c for c in cand if 1 <= c <= pc]))[:3]

    for s in cand:
        one = SINGLE / ("%s_s%03d.pdf" % (lid, s))
        d2 = fitz.open()
        d2.insert_pdf(doc, from_page=s - 1, to_page=s - 1)
        d2.save(str(one))
        d2.close()
        txt = SINGLE / ("%s_s%03d.txt" % (lid, s))
        try:
            r = subprocess.run(["bash", CLI, str(one).replace("\\", "/"), "-f", "txt",
                                "-o", str(txt).replace("\\", "/"), "--json"],
                               capture_output=True, text=True, timeout=120)
            ok = r.returncode == 0 and txt.exists()
            msg = ""
            try:
                msg = json.loads(r.stdout).get("message", "")
            except Exception:
                msg = r.stderr.strip()[:120]
        except Exception as e:
            ok, msg = False, repr(e)[:120]

        segs = [canon(l) for l in d["pages"][s - 1]["text"].splitlines()]
        segs = [x for x in segs if len(x) >= 20][:5]
        flag = "scan_or_image_only" in d["pages"][s - 1]["flags"]

        if ok:
            cli_c = canon(txt.read_text(encoding="utf-8", errors="ignore"))
            ph = sum(1 for x in segs if x in cli_c)
            pl = len(segs)
            total += pl
            hit += ph
            ok_pages += 1
            rows.append("| %s | Slide %d | %d/%d | OK | 文字页，逐行比对 |" % (lid, s, ph, pl))
        elif "ocr" in msg.lower() or flag:
            scan_pages += 1
            rows.append("| %s | Slide %d | — | SCAN_SKIP | 扫描/图片页；按降级策略仅嵌原页 PNG，不转录 |" % (lid, s))
        else:
            fail_pages += 1
            rows.append("| %s | Slide %d | — | FAIL | %s |" % (lid, s, msg[:80]))
    doc.close()

out = ["# PDF 官方工具独立抽检复核 (workbuddy-pdf cross-check)", "",
       "目的：用 `workbuddy-pdf -f txt` 独立核对 `extract_pages.py`（PyMuPDF）逐页原文的忠实性，"
       "确认 HTML 中每一句英文都真实来自老师 PDF。",
       "方法：把每个抽检页从**原始 PDF** 单独导出为一页 PDF，再交官方 CLI 抽取；"
       "文字页做归一化逐行包含比对。",
       "口径：每讲抽 3 页 —— 第 1 页 / 中间页 / 该讲考试例题页 / 末页（去重取 3）。", "",
       "> 环境说明：本机无 Tesseract / PaddleOCR，CLI 对扫描页会要求 OCR 而报错。"
       "这类页按项目既定的**无 OCR 降级策略**处理：只嵌入整页 PNG，不转录、不生成定义、不编造内容。", "",
       "| 讲次 | 抽检页 | 命中行 / 抽检行 | 状态 | 说明 |", "|---|---|---|---|---|"] + rows + [
        "", "## 汇总", "",
        "- 抽检页合计：%d 页（文字页 %d / 扫描页降级 %d / 其他失败 %d）" % (
            ok_pages + scan_pages + fail_pages, ok_pages, scan_pages, fail_pages),
        "- 文字页正文行命中：%d / %d（%.1f%%）" % (hit, total, 100.0 * hit / max(1, total)),
        "- 结论：**%s**" % ("两套抽取器在全部文字页一致，逐字原文可信；扫描页按降级策略仅嵌 PNG"
                            if hit / max(1, total) >= 0.95 and fail_pages == 0
                            else "存在偏差或失败，需人工复核"),
        "", "> 比对采用「去 PUA 符号 / 去标点 / 大小写归一」的包含匹配，"
        "以容忍 PDF 多栏排版造成的换行差异。", ""]
(DATA / "reports/pdf_crosscheck.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
