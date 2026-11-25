"""Stage 2: per-slide extraction (PyMuPDF) + full-page PNG for every slide.

All English text that reaches the HTML comes from data/pages/*.json produced here.
Slide numbers are 1-based ("Slide N"), matching the PDF page order.
"""
import hashlib, json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf as fitz

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
PDF_DIR = ROOT / "pdfs"
OUT = ROOT / "data/pages"
IMG_ROOT = ROOT / "assets/img"

manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
SOURCE_FILE = {x["id"]: x["source_file"] for x in manifest["items"]}

ONLY = None
if "--only" in sys.argv:
    ONLY = set(sys.argv[sys.argv.index("--only") + 1].split(","))

EXAM_RE = re.compile(r"Exam\s+Sample[-\s]?Item|Sample[-\s]?Item|Category\s*[\u201c\"']?\s*(?:Knowledge|Application|Insight)", re.I)
PUA_RE = re.compile(r"[\uE000-\uF8FF]")
MAIN_RE = re.compile(r"Main lesson", re.I)
SUMMARY_RE = re.compile(r"\bSumm?ary\b|Contents of today|What you will learn", re.I)


def norm(s):
    """Normalise for substring verification only; never used as displayed text."""
    s = s.replace("\u00ad", "")
    s = re.sub(r"-\n\s*", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


pdfs = sorted(p for p in PDF_DIR.glob("L[0-9][0-9].pdf"))
total_slides = 0
for pdf in pdfs:
    lid = pdf.stem
    if ONLY and lid not in ONLY:
        continue
    doc = fitz.open(str(pdf))
    pages = []
    img_dir = IMG_ROOT / lid
    img_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(doc):
        slide = i + 1
        text = page.get_text("text")
        ntext = norm(text)
        imgs = page.get_images(full=True)
        flags = []
        if EXAM_RE.search(text):
            flags.append("exam_item")
        if PUA_RE.search(text):
            flags.append("answer_mark")
        if MAIN_RE.search(text):
            flags.append("main_lesson")
        if SUMMARY_RE.search(text):
            flags.append("summary_or_contents")
        if len(ntext) < 40:
            flags.append("scan_or_image_only")
        # Render EVERY slide: the original page image is the ground truth for
        # formulas, tables, checkbox marks and "deep-dive every related PPT page".
        rel = f"assets/img/{lid}/slide-{slide:03d}.png"
        page.get_pixmap(dpi=100).save(str(ROOT / rel))
        pages.append({
            "slide": slide,
            "text": text,
            "text_norm": ntext,
            "char_count": len(ntext),
            "has_image": bool(imgs),
            "image_count": len(imgs),
            "png": rel,
            "flags": flags,
        })
    obj = {
        "lecture": lid,
        "source_file": SOURCE_FILE.get(lid, pdf.name),
        "chosen_source": str(pdf),
        "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "page_count": doc.page_count,
        "pages": pages,
    }
    (OUT / f"{lid}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    doc.close()
    total_slides += len(pages)
    n_exam = sum(1 for p in pages if "exam_item" in p["flags"])
    n_mark = sum(1 for p in pages if "answer_mark" in p["flags"])
    n_scan = sum(1 for p in pages if "scan_or_image_only" in p["flags"])
    print(f"{lid}: pages={len(pages)} exam_item_pages={n_exam} answer_mark_pages={n_mark} low_text_pages={n_scan}")
print("TOTAL_SLIDES", total_slides)
