# QA 自检报告 (QA Report)

- [PASS] L00 Slide 卡片数 == 5 — 实测 5
- [PASS] L01 Slide 卡片数 == 49 — 实测 49
- [PASS] L02 Slide 卡片数 == 70 — 实测 70
- [PASS] L03 Slide 卡片数 == 61 — 实测 61
- [PASS] L04 Slide 卡片数 == 87 — 实测 87
- [PASS] L05 Slide 卡片数 == 103 — 实测 103
- [PASS] L07 Slide 卡片数 == 66 — 实测 66
- [PASS] L08 Slide 卡片数 == 51 — 实测 51
- [PASS] L09 Slide 卡片数 == 87 — 实测 87
- [PASS] L10 Slide 卡片数 == 83 — 实测 83
- [PASS] L11 Slide 卡片数 == 65 — 实测 65
- [PASS] 无出处术语 0 条 — []
- [PASS] 全部术语有中文定义 — []
- [PASS] 英文定义逐字命中 PPT 原句 — 不匹配 0 条：[]
- [PASS] 每页术语均挂 data-term（逐 Slide 严格核验） — 缺 0：[]
- [PASS] 全站术语悬浮标记数（>= 术语出现位置总数） — 983 处 / 出现位置 779 个
- [PASS] 例题 30 道 — 30
- [PASS] 每题中文翻译齐全
- [PASS] 每题相关页不为空
- [PASS] 每题答案页中文齐全
- [PASS] 内部链接/资源全部存在 — 损坏 0：[]
- [PASS] 零 fetch / 零外部资源 — []
- [PASS] 逐页 PNG == 727 — 实测 727
- [PASS] 无 AI 归纳文字 — []

## 汇总

- 幻灯片 727 页 / PDF 11 份 / 例题 30 道 / 术语 122 条 / 悬浮标记 983 处
- 结论：**全部通过**

## 附 A：术语表重整口径（本次用户反馈）

用户指出旧术语表把老师目录中的**词组概念**拆成了单字，故全表重建：

- 新主干来自每讲 `Contents of today` 页 + `What you will learn today` / `Main lesson` 大纲页的
  bullet 条目，**逐字取自 PPT**；清洗掉讲次标题、总结句、软换行误拼与单字列举项。
- 术语 **122 条，其中 112 条是多词词组（91.9%）**；`Linear regression`、`Multiple linear regression`、
  `Pearson Product-Moment Correlation (r)`、`Confirmatory data analysis` 等均以完整词组为单位。
- 缩写与括号写法（`PCA`、`SEM`、`RQ`、Modeling/Modelling）作为**同一词组的变体**，
  不再作为独立单字术语；旧的 325 条单字/人名/缩写表已备份为
  `data/terms_candidates_old.json` / `data/terms_old.json`。
- 58 条有老师逐字解释句（`verbatim`），64 条只有目录行/概念名（`occurrence_only`，不补写解释）。
- 悬浮标记 983 处 ≥ 术语出现位置 779 个；旧阈值 `>1000` 是按 325 条单字表设的，已改为
  与 occurrences 挂钩的规模检查。

## 附 B：PDF 官方工具独立抽检复核

由 `data/pdf_crosscheck.py` 独立执行（完整报告见 `data/reports/pdf_crosscheck.md`）：

- 用 `workbuddy-pdf -f txt` 对每讲抽检 3 页（共 33 页，含各讲考试例题页），从原始 PDF 单页导出后交叉比对。
- 文字页 32 页，正文行命中 **126 / 126（100.0%）**，与 `extract_pages.py`（PyMuPDF）逐页原文完全一致。
- 扫描/图片页 1 页（L09 Slide 43）：本机无 Tesseract / PaddleOCR，按项目既定的**无 OCR 降级策略**只嵌入整页 PNG，不转录、不生成定义、不编造内容。
- 结论：HTML 中每一句英文都真实来自老师 PPT 原文，出处可逐页回溯。
