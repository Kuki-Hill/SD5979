"""Stage 3/4 analysis: curated technical-term candidates with VERBATIM one-line
PPT definitions + traceable sources.

Origin classes (all from the teacher's PDFs or the course glossary word list):
  glossary  - headwords in glossary.md (course L09/L10 term list)
  abbr      - acronym / symbol tokens found in slides
  defsent   - subject of a definitional sentence in a slide ("X is ...", "X: ...")
  name      - author (year) citations
  quoted    - short quoted phrases
  label     - instructor's fixed labels
"""
import json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
PAGES = ROOT / "data/pages"
DATA = ROOT / "data"
GLOSSARY = pathlib.Path(r"C:/Users/Wyki/WorkBuddy/2026-11-05-22-47-18/bilingual_pdf/glossary.md")

lectures = {}
for f in sorted(PAGES.glob("L[0-9][0-9].json")):
    lectures[f.stem] = json.loads(f.read_text(encoding="utf-8"))
ALL = []  # (lid, slide, text, text_norm, source_file)
for lid, d in lectures.items():
    for p in d["pages"]:
        ALL.append((lid, p["slide"], p["text"], p["text_norm"], d["source_file"]))

cands = {}   # lower -> {display, variants, zh_hint, origins}


def add(t, zh="", origin=""):
    t = re.sub(r"\s+", " ", t).strip(" .,:;-\u201c\u201d\"'()")
    if not t or len(t) < 2 or len(t) > 52 or len(t.split()) > 7:
        return
    if not re.match(r"^[A-Za-z(]", t):
        return
    k = t.lower()
    if k not in cands:
        cands[k] = {"display": t, "variants": set(), "zh_hint": zh, "origins": set()}
    cands[k]["variants"].add(t)
    cands[k]["origins"].add(origin)
    if zh and not cands[k]["zh_hint"]:
        cands[k]["zh_hint"] = zh


# 1) glossary headwords (with bracketed abbreviations)
for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line.startswith("|") or line.startswith("|---") or "English" in line:
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if len(cells) < 2 or not cells[0] or not cells[1]:
        continue
    en, zh = cells[0], cells[1]
    add(re.split(r"\s*[/(]", en)[0].strip(), zh, "glossary")
    for m in re.findall(r"\(([^)]+)\)", en):
        for part in re.split(r"[/,]", m):
            add(part.strip(), zh, "glossary")

ABBR = re.compile(r"\b(?:ANOVA|MANOVA|MANCOVA|ANCOVA|GLM|CLT|PCA|SEM|SD|IV|DV|RQ|H0|H1|H2|H3|HA|df|BCI|CBI|EEG|ECG|ERP|ERPs|fMRI|GSR|HCI|FMS|GUI|MOBA|RT|SPSS|AMOS|APA|RGB|tDCS|ReCAPTCHA|EMOTIV|BCI|MC|OQ|Ss|UK|ID|IP|TP|t-test|F-test|p-value|G\*Power)\b")
ABBR_OK = set("""ANOVA MANOVA MANCOVA ANCOVA GLM CLT PCA SEM SD IV DV RQ H0 H1 H2 H3 HA df BCI CBI EEG ECG ERP ERPs fMRI GSR HCI FMS GUI MOBA RT SPSS AMOS APA RGB tDCS ReCAPTCHA EMOTIV MC OQ Ss UK ID IP TP""".split())
DEF_SUBJ = re.compile(r"^\s*[●\-\uF0B7\uF0A7]*\s*([A-Z][A-Za-z0-9 \-()/'\u2019]{2,48}?)\s+(?:is|are|means|refers to|denotes|stands for|equals|can be defined as|tells|shows|assesses|tests)\b")
DEF_COLON = re.compile(r"^\s*[●\-\uF0B7\uF0A7]*\s*([A-Z][A-Za-z0-9 \-()/'\u2019]{2,48}?)\s*[:=]\s+\S")
NAME_YEAR = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+(?:[A-Z][a-z]{2,}|[A-Z]\.)){0,2})\s*(?:et al\.?)?\s*\(?\b(?:19|20)\d{2}\b")
QUOTED = re.compile(r"[\u201c\"]([^\u201d\"]{3,42})[\u201d\"]")
STATSYM = re.compile(r"(?:Cronbach.?s?\s*(?:alpha|α)|p-value|t-test|F-test|R\s*-squared|R²|Spearman-Brown|Solomon\s*4-group|alpha level|significance level|degrees of freedom|confidence interval|effect size|null hypothesis|alternative hypothesis|Type I error|Type II error|factor analysis|structural equation modeling|path analysis|Naïve Bayes|Bayesian statistics|frequentist statistics)")

for lid, slide, text, ntext, src in ALL:
    for m in ABBR.finditer(text):
        if m.group(0) in ABBR_OK:
            add(m.group(0), "", "abbr")
    for m in STATSYM.finditer(text):
        add(m.group(0), "", "statsym")
    for m in NAME_YEAR.finditer(text):
        add(m.group(1), "", "name")
    for m in QUOTED.finditer(text):
        if len(m.group(1).split()) <= 5:
            add(m.group(1), "", "quoted")
    for line in text.splitlines():
        for rx in (DEF_SUBJ, DEF_COLON):
            m = rx.match(line)
            if m:
                add(m.group(1), "", "defsent")

for t, zh in [("Main lesson", "本课要点"), ("Exam Sample Item", "考试样题"),
              ("Exam sample item", "考试样题"), ("Open Question", "开放题"),
              ("Open-ended question", "开放题"), ("Σummary", "总结"),
              ("Solomon 4-group design", "所罗门四组设计"),
              ("Fitts' Law", "菲茨定律"), ("ReCAPTCHA", "ReCAPTCHA 验证码")]:
    add(t, zh, "label")

STOP_START = re.compile(r"^(?:In|The|This|That|These|Those|What|Why|How|If|Because|There|We|You|Your|A|An|For|With|But|And|So|No|Yes|Some|Both|During|After|Before|Based|Suppose|Imagine|Describe|Which|Does|Can|Not|Is|Are|It|Its|As|At|By|On|Or|Of|To|When|Where|Who|Such|One|Two|Three|First|Second|Then|Also|However|Moreover|Finally|Now|Here|Let|Note|See|Given|Consider|Take|There|Luckily|After|Using|Although|For|Browsing|Remember|Please|Do|Think|Explain|Explain)\b", re.I)
BAD = re.compile(r"\b(?:Lecture \d|Question|Category|Exam Sample|et al|http|www\.|\d{2}/\d{2}|Slide)\b", re.I)
TECH = re.compile(r"(?:hypothes|variable|design|effect|test|analys|statistic|measur|scale|valid|reliab|error|bias|fallacy|law|model|theor|sampl|distribut|correlat|regress|variance|coefficient|confidence|signific|probab|bayes|frequent|experiment|group|threat|confound|interview|questionnaire|method|data|signal|noise|power|sample|level|factor|median|mean|deviation|outlier|inference|deduct|induct|falsif|paradigm|construct|item|score|rating|response|condition|treatment|manipulat|random|counter|balance|mediat|moderat|latent|path|structural|causal|causation|observation|evidence|argument|literature|review|ethic|replic|general|population|parameter|estim|interval|alpha|beta|rho|chi|freedom|cut-off|rejection|alarm|decision|heuristic|grounded|phenomen|hermeneut|discourse|ethnograph|protocol|triangul|saturat|coding|themat|semantic|reference|sense|denot|connot|pragmatic|syntactic|lexical|nominal|ordinal|interval|ratio|bipolar|unipolar|likert|cronbach|spearman|pearson|kolmogorov|shapiro|levene|anova|manova|ttest|t-test|fitt|solomon|fitts|gpower|g\*power|recaptcha|emotiv|moba|eeg|bci|gsr|tdcs|fmri|vr|ai|blackbox|black box|naïve|bayes)", re.I)
KEEP_ORIGIN = {"glossary", "abbr", "name", "quoted", "statsym", "label"}
for k in list(cands):
    t = cands[k]["display"]
    origins = cands[k]["origins"]
    is_tech = bool(TECH.search(t)) or bool(origins & KEEP_ORIGIN) or bool(re.fullmatch(r"[A-Z0-9()*]{2,12}", t))
    if (STOP_START.match(t) or BAD.search(t) or re.search(r"[.!?]$", t)
            or t.lower() in {"the", "and", "for", "with", "this", "that", "from", "what", "how", "why", "which", "does", "are", "not", "but", "can", "you", "your", "type", "ii", "iii", "i"}
            or re.match(r"^[A-Z]\)?\s", t)
            or not is_tech):
        del cands[k]

# Merge near-duplicate keys (e.g. "H0" / "H0 :") so variants share one card.
keys = sorted(cands, key=len)
for k in keys:
    if k not in cands:
        continue
    for other in list(cands):
        if other == k or other not in cands:
            continue
        if (k in other or other in k) and abs(len(k) - len(other)) <= 10 and len(other) > len(k):
            cands[k]["variants"].add(cands[other]["display"])
            cands[k]["origins"] |= cands[other]["origins"]
            if not cands[k]["zh_hint"]:
                cands[k]["zh_hint"] = cands[other]["zh_hint"]
            del cands[other]

# Merge word-fragments of multiword terms into the longest term as variants
# (e.g. "Flight"/"System" -> "Flight Management System"), never as own cards.
PROTECT = {"H0", "H1", "H2", "H3", "HA", "IV", "DV", "df", "SD", "SEM", "RQ", "AI", "AR", "CA", "AG", "BCI", "EEG", "ECG", "GSR", "GLM", "CLT", "APA", "RT", "VR", "IR", "GUI", "MC", "OQ", "HCI", "FMS", "PCA", "ERPs", "ANOVA", "MANOVA", "SPSS", "IBM", "Power", "Law", "Student", "Error", "Central", "Theorem", "Repeated", "Measures", "Socratic", "Proxy", "Online", "Battle", "Flight", "System", "Fitts", "Solomon", "Multiplayer", "Human", "Computer", "Interaction"}
multi = [k for k in cands if " " in k and len(k) >= 10]
for k in list(cands):
    if k in PROTECT or " " in k or len(k) < 4:
        continue
    disp = cands[k]["display"]
    host = None
    for mk in multi:
        if re.search(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", mk, re.I):
            if host is None or len(mk) > len(host):
                host = mk
    if host:
        cands[host]["variants"].add(disp)
        cands[host]["origins"] |= cands[k]["origins"]
        if not cands[host]["zh_hint"]:
            cands[host]["zh_hint"] = cands[k]["zh_hint"]
        del cands[k]

# ---- For each term: occurrences + best verbatim one-line PPT sentence ----
SIGNAL = re.compile(r"\b(is|are|means|refers|defined|called|denotes|stands|equals|tells|shows|assesses|tests)\b|[=:]", re.I)
NOISE_LINE = re.compile(r"Main lesson|Contents of today|Exam [Ss]ample|Category|\?|https?://|\d{2}/\d{2}|^[A-D][\s).]|\bLecture \d|et al|Prof\.|Retrieved|doi|pp\.|In Proceedings", re.I)


def has(sent, variants):
    low = sent.lower()
    return any(re.search(r"(?<![A-Za-z0-9])" + re.escape(v.lower()) + r"(?![A-Za-z0-9])", low) for v in variants)


def starts_with_term(sent, variants):
    low = re.sub(r"^[^\w(]+", "", sent.lower())
    return any(low.startswith(v.lower()) for v in variants)


def lines(text):
    """Candidate definition sentences: each PPT line, plus a 2-line merge for
    soft-wrapped sentences. Verbatim words, ASCII single spaces only."""
    raw = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    raw = [l for l in raw if l]
    out = []
    for i, l in enumerate(raw):
        out.append(l)
        if not re.search(r"[.!?;:]$", l) and i + 1 < len(raw):
            merged = (l + " " + raw[i + 1]).strip()
            if len(merged) <= 210:
                out.append(merged)
    return out


terms = {}
for key, c in cands.items():
    disp, variants = c["display"], sorted(c["variants"], key=len, reverse=True)
    occ, best = [], None
    for lid, slide, text, ntext, src in ALL:
        if not has(ntext, variants):
            continue
        occ.append({"file": src, "lecture": lid, "slide": slide})
        for l in lines(text):
            if not has(l, variants) or len(l) > 260:
                continue
            sc = 0
            st = starts_with_term(l, variants)
            # Strong: line starts with the term and then a definitional verb/colon.
            core = re.sub(r"^[^\w(]+", "", l)
            after = core[len(disp):].strip() if core.lower().startswith(disp.lower()) else ""
            if st and re.match(r"^(?:is|are|means|refers|denotes|stands|equals|:|=|—|-)", after):
                sc += 12
            elif st and SIGNAL.search(after):
                sc += 7
            elif SIGNAL.search(l):
                sc += 4
            if re.search(r"\b(is|are)\b", l, re.I):
                sc += 2
            if 22 <= len(l) <= 190:
                sc += 2
            if len(l) < 20:
                sc -= 4
            if NOISE_LINE.search(l):
                sc -= 8
            if re.search(r"Main lesson|Summary|Contents of today", text, re.I) and not st:
                sc -= 3
            if best is None or sc > best[0]:
                best = (sc, lid, slide, l, src)
    if not occ:
        continue
    if best and best[0] >= 7:
        status, en_def = "verbatim", best[3]
        s_lid, s_slide, s_file = best[1], best[2], best[4]
    else:
        status = "occurrence_only"
        s_lid, s_slide, s_file = occ[0]["lecture"], occ[0]["slide"], occ[0]["file"]
        en_def = ""
        if best:
            en_def = best[3]
    terms[disp] = {
        "term": disp, "variants": variants, "origins": sorted(c["origins"]),
        "en_definition": en_def, "zh_definition": "",
        "zh_hint": c["zh_hint"],
        "source": {"file": s_file, "lecture": s_lid, "slide": s_slide},
        "occurrences": occ, "status": status,
    }

(DATA / "terms_candidates.json").write_text(json.dumps(terms, ensure_ascii=False, indent=1), encoding="utf-8")
print("TERMS", len(terms), "VERBATIM", sum(1 for t in terms.values() if t["status"] == "verbatim"),
      "OCC_ONLY", sum(1 for t in terms.values() if t["status"] == "occurrence_only"))
print("ORIGINS", {o: sum(1 for t in terms.values() if o in t["origins"]) for o in ["glossary", "abbr", "defsent", "name", "quoted", "statsym", "label"]})
print("OCC_TOTAL", sum(len(t["occurrences"]) for t in terms.values()))
