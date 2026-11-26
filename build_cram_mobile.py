"""Build a blazing-fast, phone-first Morning-of-Exam Cram Page: mobile/cram.html

Covers all 39 exam question groups (Q01-Q39) with:
- Exam-day 1-minute cheat header (V1102, grading, spelling checklist, Bayes 3-step formula)
- Filter tabs: Final Core 26 (default), My Weak/Key 13, All 25 MCQs, All 14 OpenQ, All 39
- One-tap "Hide Answers (Self-Test) / Show All Answers" toggle
- Concise Chinese memory cues + exam-ready English answer templates for every OpenQ
- On-demand lazy slide image viewer (zero image download until tapped!)

Run: python build_cram_mobile.py
"""
import html
import pathlib

ROOT = pathlib.Path(r"D:/00.MyWorkSpace/Wyki_claude/20261118 research method")
E = lambda s: html.escape(str(s), quote=True)

# (qno, qid, round, kind, weak_flag, topic, prompt_short, ans_badge, zh_key, en_template, imgs)
# imgs = list of (label, lid, slide)
CRAM_ITEMS = [
    # ==================== ROUND 1: FINAL CORE MCQs (Q01-Q15) ====================
    ("Q01", "L07-E01", "final", "MCQ", False, "重点1 · 相关与因果",
     "肥胖与癌症共现，根因是糖摄入（Sugar intake）。那糖摄入与肥胖/癌症也相关吗？",
     "选 A",
     "题设已经给定“糖摄入是共同根因（因果关系）”，有因果就必然伴随相关；因果 ≠ 相关不代表根因就不相关。",
     "Yes, a common root cause is also correlated with its effects.",
     [("原题", "L07", 62), ("答案", "L07", 63)]),

    ("Q02", "L07-E02", "final", "MCQ", True, "重点1 · 反向题重编码 ⚠️易错",
     "2 题项量表：正向题“统计有趣” M=5，反向题（counter-indicative）“统计无聊” M=0，Spearman-Brown 信度可靠吗？",
     "选 B",
     "可靠（Reliable）！一正一反得分相反恰好说明态度完全一致，算信度前必须先把反向题重编码（recode: 0→5），千万别选 A（完全不一致）！",
     "Reliable. One should recode the contra-indication and then scores match.",
     [("原题", "L07", 64), ("答案", "L07", 65)]),

    ("Q03", "L12-E04", "final", "MCQ", False, "重点2 · 回归分析 ★L12新",
     "零售商预测下月销售额（sales），考虑天气、竞争者行为、道路维护、新品发布。谁是 IV / DV？",
     "选 A",
     "被预测的结果 Sales 是因变量（DV）；天气、竞争者、道路维护、新品发布是自变量/预测变量（IVs / predictors）。",
     "Sales = DV; weather, competitor behavior, road maintenance, new product launches = IVs.",
     [("原题", "L12", 65), ("答案", "L12", 66)]),

    ("Q04", "L12-E05", "final", "MCQ", False, "重点2 · 回归分析 ★L12新",
     "网页设计师把所有点击/加载日志全扔进回归预测网站访问量，错在哪里？",
     "选 D（A 和 C 都对）",
     "同时踩中两个坑：A 缺乏理论依据且遗漏混淆变量（误点、猫碰鼠标、竞争者浏览等）；C 只是凭空猜想加载时间与体验的关系。选最完整的 D！",
     "Both A and C: lacks theory / misses confounds, and merely guesses the link between load time and experience.",
     [("原题", "L12", 69), ("答案", "L12", 70)]),

    ("Q05", "L08-E02", "final", "MCQ", True, "重点2 · 回归与因果 ⚠️记课程口径",
     "相关不是因果，那在线性回归中，IV 与 DV 的相关是否来自因果？（老师特殊口径）",
     "选 B",
     "记牢老师口径选 B：回归中因变量（DV）的变化是由自变量（IV）的变化预测并加以检验（predicted from and tested against）的。注意：C 里的 defeasible reasoning 是真实术语，排除 C 是因为它只讲归纳相关、没答到预测与检验。",
     "Yes. Changes in the dependent variable are predicted from and tested against changes in the independent variable.",
     [("原题", "L08", 47), ("答案", "L08", 48)]),

    ("Q06", "L08-E03", "final", "MCQ", False, "重点2 · 结构方程 SEM",
     "SEM 用可观测题项推测潜变量，为什么它不只是“肯定后件谬误（Ex-consequentia）”？",
     "选 C",
     "SEM 不是直接从结果反推原因，而是先构建可检验的理论模型、用潜变量预测可观测项再检验，并明确允许未解释方差（unexplained variance / 误差项）。",
     "Latent variables predict observable items in a testable model while allowing unexplained variance.",
     [("原题", "L08", 49), ("答案", "L08", 50)]),

    ("Q07", "L12-E06", "final", "MCQ", False, "重点2 · 回归与神经网络 ★L12新",
     "神经网络用到线性回归 y = ax + b，其中斜率 a 和截距 b 分别对应什么？",
     "选 A",
     "秒选口诀：a = slope = weight（权重），b = intercept = bias（偏置）。（别和 B 颠倒！）",
     "a = slope / weight; b = intercept / bias.",
     [("原题", "L12", 91), ("答案", "L12", 92)]),

    ("Q08", "L09-E01", "final", "MCQ", False, "重点3 · 频率主义假设检验",
     "ReCAPTCHA 把“不是机器人”当作 H₀：未能拒绝 H₀，能否说明用户“是人类”？",
     "选 A",
     "频率主义只能拒绝 H₀，不能证实 H₀ 或直接推出相反结论：没拒绝“非机器人”≠ 证明“是人类”。",
     "Failing to reject H0 ('not a robot') does not prove the user is human.",
     [("原题", "L09", 11), ("答案", "L09", 12)]),

    ("Q09", "L09-E02", "final", "MCQ", False, "重点3 · 实验设计",
     "哪种实验设计对顺序效应（order effects）最敏感？",
     "选 A（Within-subjects）",
     "被试内设计（Within-subjects）同一人依次经历多个条件，最易受练习/疲劳等顺序效应影响；Randomization 和 Counter-balancing 是缓解手段，不是设计类型。",
     "A: Within-subjects design.",
     [("原题", "L09", 79), ("答案", "L09", 80)]),

    ("Q10", "L09-E04", "final", "MCQ", False, "重点3 · 所罗门四组 + 信度",
     "用 Cronbach’s α 检验测量信度，在所罗门四组设计中应选哪些组数据最有说服力？",
     "选 D",
     "原则：要最多且**未受前测影响**的首次测量数据 → G1before + G2before + G3after + G4after（排除已填过前测的 G1after 和 G2after）！",
     "D: G1before, G2before, G3after, G4after (maximum uncontaminated first-time measurements).",
     [("原题", "L09", 85), ("答案", "L09", 86)]),

    ("Q11", "L10-E02", "final", "MCQ", False, "重点4 · ANOVA 方差分析",
     "单因素方差分析（Oneway ANOVA）到底比较什么？",
     "选 B",
     "秒选口诀：Oneway ANOVA = **1 个因变量（one DV）**在 **3 个（及以上）组**之间的均值比较。（多个 DV 那是 MANOVA！）",
     "B: Oneway ANOVA compares means of one dependent variable across 3 (or more) groups.",
     [("原题", "L10", 61), ("答案", "L10", 62)]),

    ("Q12", "L10-E03", "final", "MCQ", False, "重点4 · t 检验显著性表",
     "如果确立显著效应最低需要 t = 63.657 这么大的临界值，意味着什么？",
     "选 D（A 和 B 都可能）",
     "临界 t 极大有两个原因：A 自由度（df）极少（表中仅 2 个观测值），且 B 拒绝域（rejection area / α）设得很小（1%）。选最完整的 D！",
     "D: Both very few degrees of freedom and a very small rejection area (e.g., α = 1%, df = 1).",
     [("原题", "L10", 74), ("答案", "L10", 75)]),

    ("Q13", "L11-E01", "final", "MCQ", False, "重点4 · t-test 选型（2 小题）",
     "1) I’m not better than anyone；2) I’m better than I was。分别对应 H₀/Hₐ 与哪种 t-test？",
     "1: D / 2: A",
     "拆两条轴：无差异=H₀，有改善=Hₐ；和别人比=independent samples，和过去的自己比=paired samples。另留意隐藏追问：better than 只是 Ordinal 尺度，严格用参数 t-test 需 Interval/Ratio！",
     "1) D: H0 and independent samples.  2) A: HA and paired samples. (Note: check measurement scale — ordinal vs interval/ratio!)",
     [("原题", "L11", 5), ("答案", "L11", 6)]),

    ("Q14", "L11-E02", "final", "MCQ", False, "重点4 · 频率主义与 MANOVA",
     "Edwards 等人跑 MANOVA 发现人与 Bot 无显著差异，能否得出“两者一样可信、有吸引力、高效”？",
     "选 C",
     "不能！MANOVA 属于频率主义零假设检验，不显著 = 未拒绝 H₀，不能反过来证明两者“一样好”（证明“相同”需要贝叶斯检验）。",
     "C: Failing to reject H0 in MANOVA does not prove humans and bots are equally credible, attractive, and competent.",
     [("原题", "L11", 39), ("答案", "L11", 40)]),

    ("Q15", "L12-E08", "final", "MCQ", True, "重点5 · 贝叶斯统计 ★L12新 ⚠️易错",
     "Naïve Bayes 忽略类别间相关（叶虫、蜂兰不存在），那它如何应对多重共线性（multicollinearity）？",
     "选 A",
     "千万别选 C！Naïve Bayes 不会通过反复更新慢慢容纳跨类特征，它的做法是“不处理（Not）”——直接一刀切掉（cuts off）所有与给定假设不一致的类别，无论类别之间多相关！",
     "A: Not. Naïve Bayes just cuts off classes that are not in line with a given hypothesis, no matter how related they are.",
     [("原题", "L12", 161), ("答案", "L12", 163)]),

    # ==================== ROUND 2: FINAL CORE OPEN-ENDED (Q16-Q26) ====================
    ("Q16", "L12-E01", "final", "OpenQ", True, "重点6 · 逻辑推理 ★L12新 ⚠️注意拼写",
     "对比 Modus ponens，洗发水/脑电广告（专注→脑电波；测到脑电波→推出专注）犯了哪种谬误？",
     "Ex-consequentia",
     "务必拼准：**Ex-consequentia**（或老师原页写的 **Ex-consequence**，括号补 affirming the consequent）。逻辑：`A→B`（专注→脑电波），看到 `B` 不能反推 `A`。",
     "Ex-consequentia / Ex-consequence (affirming the consequent).\nA → B (Focus → specific brainwave). Observing B (brainwave) does NOT logically prove A (Focus).",
     [("原题", "L12", 36), ("答案", "L12", 37)]),

    ("Q17", "L12-E02", "final", "OpenQ", True, "重点6 · 报告结果 ★L12新 ⚠️补全3点",
     "8% 男性 + 1% 女性色盲 → 推出总体 9%（房间里近 1/10）色盲，错在哪里？（含 CPU 变体）",
     "3 错 + 1 变体",
     "1) **子群分母不同，百分比不能直接相加**（缺子群绝对人数；即使男女对半也是 4.5% 不是 9%）；2) **隐藏假设**：假设男女人数相等且性别是二元名义变量（dichotomous nominal）；3) **数字修辞夸大**：9% 滑坡夸大成“近 1/10”。若考 CPU 变体，再加一条**过度概括**：硬件 bug ≠ 内存泄漏。",
     "1. Percentages are relative to sub-groups (males vs. females) and cannot be summed without knowing absolute sub-group sizes (even at 50/50, the rate is 4.5%, not 9%).\n2. Hidden assumptions: assumes equal numbers of men/women and treats gender as a dichotomous nominal variable.\n3. Rhetoric of numbers: rounding 9% to 'nearly 1 out of 10' exaggerates without base rates. (CPU variant: also overgeneralizes hardware bugs = memory leaks.)",
     [("原题", "L12", 39), ("要点1-3", "L12", 42), ("CPU变体", "L12", 44)]),

    ("Q18", "L12-E03", "final", "OpenQ", True, "重点6 · 报告结果 ★L12新 ⚠️必背2句",
     "药副作用风险从 10% 降到 5%，论文摘要宣称“风险降低了 50%”，这是虚假（false）还是误导（misleading）？",
     "不假，但误导",
     "拆两半答：1) **不是虚假（Not false）**：10%→5% 确实减半，这是**相对风险下降（relative risk reduction）** 50%；2) **是误导（Misleading, yes）**：**绝对风险下降（absolute risk reduction）**仅 5 个百分点，只报 50% 显得过度夸张（less spectacular）。",
     "1. Not false: Going from 10% to 5% removes half the risk — a 50% relative risk reduction.\n2. Misleading, yes: The absolute risk reduction is only 5 percentage points (10% → 5%). Reporting only 50% without the baseline sounds far more spectacular than it really is.",
     [("原题", "L12", 45), ("答案", "L12", 46)]),

    ("Q19", "L08-E01", "final", "OpenQ", True, "重点2 · 中介与调节四路径 ⚠️必背",
     "VR 健康应用 X 影响体验 Y，健康知识 M，健康动机 W。写出 A/B/C/D 四种路径。",
     "4 条固定句式",
     "A 中介：`X → M → Y`；B 调节：`W` 改变 `X → Y`；C 被调节的中介：`X → M → Y` 的中介效应取决于 `W`；D 被中介的调节（L12 修正！）：交互作用 `X × W` 影响 `M`，`M` 再影响 `Y`（控制 `X → Y` 主效应）。",
     "A. Mediation: VR health app (X) → Health knowledge (M) → User experience (Y).\nB. Moderation: The effect of X on Y depends on User motivation (W).\nC. Moderated mediation: The mediation effect of M between X and Y depends on W.\nD. Mediated moderation: The interaction between X and W (X × W) influences M, which in turn affects Y (controlling for the X → Y main effect).",
     [("原题", "L08", 26), ("L12修正图", "L12", 19), ("D答案", "L12", 76)]),

    ("Q20", "L10-E01", "final", "OpenQ", True, "重点4 · 两类错误 ⚠️别写反H0",
     "重设计飞机 FMS 触屏系统（H₀：新触屏不提高准确率；H₁：提高准确率），Type I 和 Type II 错误后果分别是什么？",
     "虚警 vs 漏报",
     "注意别写反！Type I 是 **H₀ 为真却错误拒绝**（新系统没用却换了）→ 浪费开发资源 + 飞行员白学新界面毫无收益；Type II 是 **H₁ 为真却未拒绝 H₀**（新系统有用却不用）→ 飞行员继续误操作甚至坠机（crashing，虽然省了学新界面）。",
     "Type I error (False alarm): H0 is true (new FMS does not improve accuracy), yet we wrongly reject H0 and switch anyway. Consequence: waste extra development resources and force pilots to learn a new GUI for no benefit.\nType II error (Missed signal): H1 is true (new FMS improves accuracy), yet we keep the old system. Consequence: pilots keep making input errors and risk crashing the plane (even though the old interface stays familiar).",
     [("原题", "L10", 41), ("答案", "L10", 42)]),

    ("Q21", "L10-E04", "final", "OpenQ", True, "重点4 · 测量黑箱（不显著） ⚠️必背",
     "220 人戴两种 VR 头盔测脸温，几台体温计互校都是 37°C，t 检验不显著就说安全，还把被试喊热归为自我暗示，错在哪？",
     "假体温计黑箱",
     "1) **黑箱仪器 & 互校≠效度**：同款假体温计互校一致不代表测到真温度（只是 [36.7–37.2] 随机数黑箱），**H₀ 根本无法被证伪**；2) **不显著 ≠ 安全**（且缺对照组/基线，两款头盔可能一样热）；3) **不能把一致的定性抱怨轻率归为自我暗示（auto-suggestion）**，这是仪器失灵警报。",
     "1. Black-box instrument: Calibrating thermometers only against each other checks consistency, not validity. If the IR sensor is a black box (e.g., outputting random numbers 36.7–37.2°C), H0 can never be refuted.\n2. Non-significance ≠ safety: Failing to reject H0 does not prove safety, and comparing two helmets lacks a baseline.\n3. Qualitative mismatch: Consistent complaints of heat should not be dismissed as auto-suggestion; they warn of faulty measurement.",
     [("原题1", "L10", 77), ("原题2", "L10", 78), ("答案", "L10", 79)]),

    ("Q22", "L10-E05", "final", "OpenQ", True, "重点4 · 测量黑箱（显著） ⚠️必背",
     "220 人玩 MOBA 游戏，用 EMOTIV 无线 EEG 软件得出 AI 队友“显著降低负面情绪”并发了论文，该质疑什么？",
     "BCI 软件黑箱",
     "核心四连问：EMOTIV 软件是**黑箱（black box）**——怎么解释信号（interpretations）？算法（algorithms）是什么？阈值（cut-off points）怎么定？凭什么有信心（confident）把某肌肉动作判成恐惧/喜悦？测量环节不透明，统计再显著也不能下结论！",
     "1. Black-box BCI software: EMOTIV's software is an opaque black box. We do not know how it interprets signals, what algorithms or cut-off points it uses, or how confident it is that a muscle motion means 'fear' vs. 'joy.'\n2. Significance ≠ validity: Even with N=220 and significant p-values, without transparent, validated measurement (and surface EEG cannot reliably measure deep amygdala), the claim that AI teammates reduce negative mood is unjustified.",
     [("原题1", "L10", 80), ("原题2", "L10", 81), ("答案", "L10", 82)]),

    ("Q23", "L11-E03", "final", "OpenQ", True, "重点5 · 贝叶斯决策信心 ⚠️必背2句",
     "Naïve Bayes 仅凭眼睛算出机器人为 Humanoid 的概率是 56%（50-50 为最大不确定性），说明什么？",
     "极不确定 / 可疑",
     "两端 `0% / 100%` 不确定性 = 0；中间 `50%` 不确定性最大；**`56%` 紧挨 `50%`，不确定性接近最大，判定为 Humanoid 非常可疑（very doubtful）**。",
     "When P = 0% (not Humanoid) or P = 100% (definitely Humanoid), uncertainty = 0. With P = 56%, uncertainty is almost at its maximum (50%), so the decision for Humanoid is very doubtful (very low confidence).",
     [("原题", "L11", 57), ("答案", "L11", 58)]),

    ("Q24", "L12-E07", "final", "OpenQ", True, "综合 · 研究质量评估 ★L12新 ⚠️必背",
     "MIT 科学家大模型 Arctan-10（大数据/96%/快）vs 小学生纸笔算术实验，4 位同学谁说得对？为什么？",
     "选 Dài ān（小学生）",
     "选 **Dài ān**（小学生更好）！大数据、权威、速度、96% 准确率都不是研究质量证据。背 4 大碾压点：1) **Interval 尺度** vs Nominal 鞋盒分类；2) **透明纸笔测试** vs **Black box**；3) **明确理论 + 参数 t-test（可因果预测）** vs 非参数相关探索；4) **100% 明确对错 + 高重测信度** vs 复杂易错 4% 概率误差。",
     "Answer: Dài ān (the school boy is the better researcher).\nMotivation: Big data, authority, speed, and 96% accuracy do not prove research quality. The school boy wins on:\n1. Measurement quality: Interval scale (mean/SD/variance) vs. Arctan-10's nominal classification.\n2. Transparency: Crystal-clear test vs. Arctan-10 as a black box.\n3. Theory & Test strength: Clear theory tested with parametric t-test (predictions/cause-effect) vs. non-parametric exploration only.\n4. Robustness & Reliability: Simple, 100% determined outcomes and high test-retest reliability vs. complex system with 4% failure.",
     [("4同学观点", "L12", 143), ("8维对比表", "L12", 144)]),

    ("Q25", "L12-E09", "final", "OpenQ", True, "综合 · 猫狗题 L12 新问法 ★L12改写 ⚠️必背",
     "把 Lakkaraju(2017) 训练数据看作 nominal measurement：A) 两个类别？B) 数据分割依据？C) 为何不自己证伪？",
     "极简 3 行满分",
     "老师专门用这题示范**开放题要简短精准**！A) **Dogs and Cats**；B) **Colour**（猫训练集和白色重合，狗训练集和黑色重合）；C) 神经网络**缺乏概念知识（lack conceptual knowledge）**，也**没有推理系统（no inference systems）**来做**逻辑验证（logic verification）**。",
     "A) Dogs and Cats.\nB) Colour — the training set of Cats coincides with being white, and Dogs coincides with being black, so the data split is based on colour.\nC) Neural Networks lack conceptual knowledge, have no inference systems, and cannot perform logic verification.",
     [("猫狗图", "L12", 169), ("答案A", "L12", 170), ("答案B", "L12", 171), ("答案C", "L12", 172)]),

    ("Q26", "L09-E03", "final", "OpenQ", False, "重点3 · 猫狗题 L09 原版问法",
     "同猫狗题，若按 L09 原版问法（看作 experimental design）：A) 两个条件？B) 混淆变量？C) 为何不证伪？",
     "对照 Q25 记差异",
     "答案骨架和 Q25 一模一样，只是按题干用词微调：A) **Dogs and Cats**；B) **Confound is colour**（白猫黑狗重合）；C) **lack conceptual knowledge**, no inference systems, cannot do **confirmatory statistics**。",
     "A) Dogs and Cats.\nB) The confound is colour (Cats coincide with white; Dogs coincide with black).\nC) Neural Networks lack conceptual knowledge, have no inference systems, and cannot do confirmatory statistics.",
     [("答案A", "L09", 82), ("答案B", "L09", 83), ("答案C", "L09", 84)]),

    # ==================== ROUND 3: MIDTERM CONSOLIDATION (Q27-Q39) ====================
    ("Q27", "L01-E01", "mid", "MCQ", False, "期中巩固 · 未解释方差",
     "为什么研究结果几乎达不到 100% 解释力？",
     "选 C",
     "因为总存在**未解释方差（unexplained variance）**（L12 第 11–13 页联动）。",
     "C: Unexplained variance.",
     [("原题", "L01", 18), ("答案", "L01", 19)]),

    ("Q28", "L02-E01", "mid", "MCQ", False, "期中巩固 · 研究问题 RQ",
     "为什么 'Will AI combat the human mind and who will have won?' 不是好 RQ？",
     "选 C",
     "核心概念（AI、mind、combat、won）全部模糊不清、未经界定。",
     "C: Core concepts (AI, mind, combat, won) are vague and undefined.",
     [("原题", "L02", 68), ("答案", "L02", 69)]),

    ("Q29", "L03-E01", "mid", "MCQ", False, "期中巩固 · 启发式测试",
     "启发式测试（Heuristic test）由谁做、成本和速度如何？",
     "选 D",
     "由**专家（experts）**凭经验法则执行，特点是**便宜且快速（cheap and fast）**。",
     "D: Experts using rules of thumb; cheap and fast.",
     [("原题", "L03", 54), ("答案", "L03", 55)]),

    ("Q30", "L03-E02", "mid", "MCQ", False, "期中巩固 · 访谈类型",
     "有预先提纲又允许顺着对话灵活追问，是哪种访谈？",
     "选 B",
     "**半结构式访谈（semi-structured interview）**。",
     "B: Semi-structured interview.",
     [("原题", "L03", 56), ("答案", "L03", 57)]),

    ("Q31", "L04-E02", "mid", "MCQ", False, "期中巩固 · 逻辑谬误",
     "把“决定”不断推向大脑→皮层→神经网络→突触→粒子，属于什么？",
     "选 D",
     "**无穷回归（Infinite regress）**——层层后退却始终没解释“决定”本身。",
     "D: Infinite regress.",
     [("原题", "L04", 76), ("答案", "L04", 77)]),

    ("Q32", "L04-E03", "mid", "MCQ", False, "期中巩固 · 意义与指称",
     "大模型能复制语言形式却不知词语指向现实何物，对应 Frege 哪项区分？",
     "选 A",
     "**懂得 sense（意义/词间形式），不懂 reference（现实指称）**。",
     "A: It knows sense but not reference.",
     [("原题", "L04", 78), ("答案", "L04", 79)]),

    ("Q33", "L04-E04", "mid", "MCQ", False, "期中巩固 · 单/双极量表（一）",
     "夜视研究中深灰在知觉上被视作纯黑、与纯白构成真对立，两条单极量表能否合并？",
     "选 B",
     "可以合并！老师看的是**知觉上的真对立**，不是物理 RGB 数值差异。",
     "B: Yes, perceptually dark grey is experienced as pure black, forming a true opposite to pure white.",
     [("原题", "L04", 80), ("答案", "L04", 81)]),

    ("Q34", "L04-E05", "mid", "MCQ", False, "期中巩固 · 单/双极量表（二）",
     "知觉评分 4 与 0：有对比是否等于正相反，能否合并成双极量表？",
     "选 C",
     "不能合并！知觉评分 4 与 0 未形成两极真对立（对比 ≠ 正相反）。",
     "C: No, perceptual scores 4 and 0 do not form true bipolar opposites.",
     [("原题", "L04", 82), ("答案", "L04", 83)]),

    ("Q35", "L05-E01", "mid", "MCQ", False, "期中巩固 · Fitts 定律",
     "胖手指现象（fat-finger syndrome）告诉我们关于 Fitts 定律的什么？",
     "选 D（A 和 B 都对）",
     "同时成立：A 压力增大错误率，且 B 指针宽度与目标宽度比值关键。",
     "D: Both A (stress increases errors) and B (pointer-to-target width ratio).",
     [("原题", "L05", 31), ("答案", "L05", 32)]),

    ("Q36", "L05-E04", "mid", "MCQ", False, "期中巩固 · 反向因果（联动 Q16）",
     "思考时皮层激活，能否反推用电刺激皮层来提高思考能力？",
     "选 C",
     "**Ex-consequentia（肯定后件谬误）**：思考→激活，不能反推刺激激活→思考。",
     "C: Ex-consequentia fallacy.",
     [("原题", "L05", 101), ("答案", "L05", 102)]),

    ("Q37", "L04-E01", "mid", "OpenQ", False, "期中巩固 · 测量尺度与题项",
     "Like / I don’t like 按钮与评论文本框的 4 个小问。",
     "4 短答",
     "1) **Nominal**（仅分类）；2) **不是 rating scale**（无有序等级/距离）；3) **I don’t like 不合适**（反向题避免用 not/don’t 防混淆）；4) 文本框是**定性/轶事数据（qualitative, anecdotal）**，若做统计需先评分编码。",
     "1. Nominal scale.\n2. No, not a rating scale (no ordered levels/meaningful distances).\n3. Inappropriate — avoid negations like 'don't/not' in contra-indicative items.\n4. Qualitative/anecdotal data; requires rating/coding for statistics.",
     [("原题", "L04", 74), ("答案", "L04", 75)]),

    ("Q38", "L05-E02", "mid", "OpenQ", False, "期中巩固 · 心理计时法",
     "预警信号与射击对手任务：A) 哪种条件最难？B) 表现如何？",
     "条件2 · 慢且错多",
     "A) **条件 2**：没有预警信号，却出现需要射击的对手；B) 反应更慢、错误率更高（效率更低）。",
     "A) Condition 2: no warning signal, yet an opponent appears requiring a shot.\nB) Slower reaction time and higher error rate (lower efficiency).",
     [("原题", "L05", 41), ("答案", "L05", 42)]),

    ("Q39", "L05-E03", "mid", "OpenQ", False, "期中巩固 · 语音测谎基线",
     "Truster 语音测谎系统失败的 3 小问：A) 中性基线错在哪？B) 其他变异来源？C) 哪些人无变异却能说谎？",
     "基线 / 干扰 / 训练者",
     "A) 被审问测谎时几乎不可能处于真正情绪中性状态；B) 感冒、恋爱/失恋、恐惧、烦躁、愤怒等；C) 受过声音训练者：职业扑克手、特工、惯犯、舞台演员。",
     "A) Hardly anyone is truly emotionally neutral when being tested for lying.\nB) Cold, being in/out of love, fear, annoyance, anger, etc.\nC) Voice-trained people: professional poker players, secret service agents, hardened criminals, stage actors.",
     [("原页", "L05", 65)]),
]

cards = []
for qno, qid, rnd, kind, weak, topic, prompt, badge, zh_key, en_tpl, imgs in CRAM_ITEMS:
    kind_cls = "mcq" if kind == "MCQ" else "openq"
    kind_lbl = "选择" if kind == "MCQ" else "简答"
    weak_badge = '<span class="b-weak">⚡重点复盘</span>' if weak else ""
    img_links = "".join(
        f'<div class="lazy-img-slot" data-src="../assets/img/{lid}/slide-{s:03}.png" data-cap="{E(lbl)} · {lid} 第 {s} 页"></div>'
        for lbl, lid, s in imgs
    )
    en_box = (
        f'<div class="en-tpl"><div class="en-lbl">英文背诵 / 得分句式</div>'
        f'<div class="en-txt">{E(en_tpl).replace(chr(10), "<br>")}</div></div>'
    )
    cards.append(
        f'<article class="c-card" data-qno="{qno}" data-round="{rnd}" data-kind="{kind_cls}" data-weak="{"1" if weak else "0"}">'
        f'<div class="c-top">'
        f'<div class="c-tags"><span class="qno">{qno}</span><span class="qid">{qid}</span>'
        f'<span class="b-{kind_cls}">{kind_lbl}</span>{weak_badge}</div>'
        f'<button type="button" class="master-btn" data-master="{qno}" aria-pressed="false">○ 标已背</button>'
        f'</div>'
        f'<div class="c-topic">{E(topic)}</div>'
        f'<p class="c-q">{E(prompt)}</p>'
        f'<div class="c-ans" data-reveal="0">'
        f'<div class="ans-mask">👆 轻点展开答案自测</div>'
        f'<div class="ans-inner">'
        f'<div class="ans-head"><span class="ans-badge">{E(badge)}</span></div>'
        f'<p class="ans-zh">{zh_key.replace("**", "")}</p>'
        f'{en_box}'
        f'</div></div>'
        f'<details class="img-fold"><summary>🖼️ 查看原题 / 原答案图片（点开再加载）</summary>'
        f'<div class="img-holder">{img_links}</div></details>'
        f'</article>'
    )

# Keep bold nicely rendered in zh_key
import re
cards_rendered = []
for qno, qid, rnd, kind, weak, topic, prompt, badge, zh_key, en_tpl, imgs in CRAM_ITEMS:
    kind_cls = "mcq" if kind == "MCQ" else "openq"
    kind_lbl = "选择" if kind == "MCQ" else "简答"
    weak_badge = '<span class="b-weak">⚡重点</span>' if weak else ""
    zh_html = re.sub(r"\*\*([^*]+)\*\*", r"<mark>\1</mark>", E(zh_key))
    img_links = "".join(
        f'<div class="lazy-img-slot" data-src="../assets/img/{lid}/slide-{s:03}.png" data-cap="{E(lbl)} · {lid} 第 {s} 页"></div>'
        for lbl, lid, s in imgs
    )
    cards_rendered.append(
        f'<article class="c-card" id="{qno}" data-qno="{qno}" data-round="{rnd}" data-kind="{kind_cls}" data-weak="{"1" if weak else "0"}">'
        f'<div class="c-top">'
        f'<div class="c-tags"><span class="qno">{qno}</span><span class="qid">{qid}</span>'
        f'<span class="b-{kind_cls}">{kind_lbl}</span>{weak_badge}</div>'
        f'<button type="button" class="master-btn" data-master="{qno}" aria-pressed="false">○ 未背</button>'
        f'</div>'
        f'<div class="c-topic">{E(topic)}</div>'
        f'<p class="c-q">{E(prompt)}</p>'
        f'<div class="c-ans">'
        f'<div class="ans-mask">👆 轻点揭晓答案</div>'
        f'<div class="ans-inner">'
        f'<div class="ans-head"><span class="ans-badge">{E(badge)}</span></div>'
        f'<p class="ans-zh">{zh_html}</p>'
        f'<div class="en-tpl"><div class="en-lbl">英文得分句式</div>'
        f'<div class="en-txt">{E(en_tpl).replace(chr(10), "<br>")}</div></div>'
        f'</div></div>'
        f'<details class="img-fold"><summary>🖼️ 看原题 / 原答案图</summary>'
        f'<div class="img-holder">{img_links}</div></details>'
        f'</article>'
    )

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#153d34">
<title>SD5979 考前速背冲刺（手机版）</title>
<style>
:root{{--ink:#152c29;--muted:#536864;--accent:#146957;--paper:#f4f5ef;--card:#fff;--line:#d7e0d8;--hl:#fff0bc;--safe-b:env(safe-area-inset-bottom,0px)}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:rgba(20,105,87,.12)}}
html,body{{margin:0;padding:0;background:var(--paper);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Segoe UI","Microsoft YaHei",sans-serif;font-size:15px;line-height:1.65}}
a{{color:var(--accent);text-decoration:none}}
button{{font:inherit}}
[hidden]{{display:none!important}}

.topbar{{position:sticky;top:0;z-index:30;height:52px;display:flex;align-items:center;gap:10px;padding:0 12px;background:#153d34;color:#fff;box-shadow:0 2px 10px rgba(14,42,36,.2)}}
.topbar .back{{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:8px;background:rgba(255,255,255,.15);color:#fff;font-size:18px;font-weight:700}}
.topbar .ttl{{flex:1;font-size:15.5px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.topbar .prog{{font-size:12px;font-weight:700;background:rgba(255,255,255,.18);padding:4px 9px;border-radius:999px}}

.main{{max-width:720px;margin:0 auto;padding:12px 11px calc(44px + var(--safe-b))}}

.cheat{{background:linear-gradient(145deg,#153d34,#1c5e4e);color:#fff;border-radius:14px;padding:14px 15px;margin-bottom:12px}}
.cheat h1{{margin:0 0 6px;font-size:18px}}
.cheat ul{{margin:6px 0 0;padding-left:18px;font-size:13px;line-height:1.65;opacity:.95}}
.cheat li{{margin:3px 0}}
.cheat code{{background:rgba(255,255,255,.18);padding:1px 5px;border-radius:4px;font-size:12.5px}}

.ctrl{{position:sticky;top:52px;z-index:25;background:#f4f5eff7;backdrop-filter:blur(8px);padding:8px 0 7px;margin:0 -11px 10px;padding-left:11px;padding-right:11px;border-bottom:1px solid var(--line)}}
.tabs{{display:flex;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:6px;scrollbar-width:none}}
.tabs::-webkit-scrollbar{{display:none}}
.tab-btn{{flex-shrink:0;border:1px solid #b8c9bc;background:#fff;color:var(--ink);border-radius:999px;padding:6px 12px;font-size:12.5px;font-weight:700;min-height:34px;cursor:pointer}}
.tab-btn[aria-pressed="true"]{{background:var(--accent);border-color:var(--accent);color:#fff}}
.ctrl-row{{display:flex;align-items:center;justify-content:space-between;gap:8px}}
.mode-btn{{border:1.5px solid var(--accent);background:#eaf4ef;color:var(--accent);border-radius:9px;padding:6px 12px;font-size:12.5px;font-weight:700;min-height:34px;cursor:pointer}}
.mode-btn[aria-pressed="true"]{{background:#164b3e;color:#fff}}
.cnt{{font-size:12px;color:var(--muted);font-weight:600}}

.c-card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:13px 13px 11px;margin-bottom:12px;box-shadow:0 2px 7px rgba(18,48,40,.04)}}
.c-card.is-mastered{{border-left:4px solid #2b8a62;opacity:.88}}
.c-top{{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:5px}}
.c-tags{{display:flex;align-items:center;gap:5px;flex-wrap:wrap}}
.qno{{font-size:13px;font-weight:800;background:var(--accent);color:#fff;padding:2px 8px;border-radius:6px}}
.qid{{font-size:11.5px;font-weight:700;color:var(--muted);font-family:Consolas,monospace}}
.b-mcq,.b-openq,.b-weak{{font-size:11px;font-weight:700;padding:2px 7px;border-radius:999px}}
.b-mcq{{background:#e8f2fb;color:#1a507c}}
.b-openq{{background:#f2ebfb;color:#512c82}}
.b-weak{{background:#fff0bc;color:#824f00;border:1px solid #e6ba4c}}
.master-btn{{border:1px solid #c3d3c6;background:#f7faf6;color:var(--muted);border-radius:999px;padding:4px 10px;font-size:11.5px;font-weight:700;min-height:28px;cursor:pointer}}
.master-btn[aria-pressed="true"]{{background:#dff3e7;border-color:#5bb184;color:#115737}}

.c-topic{{font-size:12px;font-weight:700;color:var(--accent);margin-bottom:3px}}
.c-q{{margin:0 0 9px;font-size:15px;font-weight:700;line-height:1.5;color:#122522}}

.c-ans{{position:relative;border-radius:11px;background:#f7faf5;border:1px solid #d9e4d9;padding:11px 12px}}
.ans-mask{{display:none;text-align:center;padding:16px 8px;font-size:14px;font-weight:700;color:var(--accent);cursor:pointer;user-select:none}}
body.quiz-hide .c-ans:not(.revealed) .ans-mask{{display:block}}
body.quiz-hide .c-ans:not(.revealed) .ans-inner{{display:none}}
.ans-head{{margin-bottom:6px}}
.ans-badge{{display:inline-block;background:#164b3e;color:#fff;font-size:13px;font-weight:800;padding:3px 10px;border-radius:7px}}
.ans-zh{{margin:0 0 8px;font-size:14px;line-height:1.72}}
.ans-zh mark{{background:var(--hl);color:#142825;font-weight:700;padding:0 3px;border-radius:3px}}
.en-tpl{{background:#fff;border:1px solid #dce6dc;border-left:3.5px solid var(--accent);border-radius:0 8px 8px 0;padding:9px 10px}}
.en-lbl{{font-size:11px;font-weight:700;color:var(--muted);margin-bottom:3px;letter-spacing:.03em}}
.en-txt{{font-size:13.5px;line-height:1.62;color:#162d2a}}

.img-fold{{margin-top:8px}}
.img-fold summary{{font-size:12.5px;font-weight:700;color:var(--accent);padding:5px 2px;cursor:pointer;list-style:none}}
.img-holder{{display:flex;flex-direction:column;gap:8px;margin-top:6px}}
.img-holder figure{{margin:0;border:1px solid #dce4dc;border-radius:8px;overflow:hidden;background:#fff}}
.img-holder img{{width:100%;height:auto;display:block}}
.img-holder figcaption{{font-size:11.5px;color:var(--muted);padding:5px 9px;background:#f4f7f2}}
</style></head>
<body>
<header class="topbar">
  <a class="back" href="index.html" aria-label="返回手机版首页">‹</a>
  <div class="ttl">SD5979 考前速背冲刺</div>
  <span class="prog" id="m-prog">0 / 26</span>
</header>

<main class="main">
  <section class="cheat">
    <h1>⚡ 考前 1 分钟终极备忘</h1>
    <ul>
      <li><b>考试信息</b>：<code>V1102</code> · <code>09:30–11:30</code> · 带圆珠笔（禁铅笔）· <code>10 选择×0.5 + 2 简答×2.5 (+0.5 bonus)</code></li>
      <li><b>开放题铁律（L12 s168）</b>：简短精准、按 A/B/C 直奔采分点，切忌长篇大论让老师自己找答案！</li>
      <li><b>5 个高频拼写防扣分</b>：<code>Ex-consequentia</code> · <code>hypothesis</code> · <code>confounding</code> · <code>multicollinearity</code> · <code>within-subjects</code></li>
      <li><b>贝叶斯手算 3 步（L12 s150–158）</b>：无先验时各假设等概率（如 3 个各 33.3%）；<code>Prior = H × Likelihood</code> → 划掉与 Data 不符分支 → 剩余分支求和并归一化到 100% 即 Posterior。</li>
    </ul>
  </section>

  <div class="ctrl">
    <div class="tabs" role="tablist">
      <button type="button" class="tab-btn" data-tab="final" aria-pressed="true">🔥 期末必背 26 题</button>
      <button type="button" class="tab-btn" data-tab="weak" aria-pressed="false">⚡ 错题与核心简答 13 题</button>
      <button type="button" class="tab-btn" data-tab="openq" aria-pressed="false">✍️ 全部简答 14 题</button>
      <button type="button" class="tab-btn" data-tab="mcq" aria-pressed="false">☑️ 全部选择 25 题</button>
      <button type="button" class="tab-btn" data-tab="all" aria-pressed="false">📚 全库 39 题</button>
    </div>
    <div class="ctrl-row">
      <button type="button" class="mode-btn" id="toggle-hide" aria-pressed="false">🙈 遮盖答案自测</button>
      <span class="cnt" id="vis-cnt">显示 26 题</span>
    </div>
  </div>

  <div id="cram-list">{"".join(cards_rendered)}</div>
</main>

<script>
(()=>{{'use strict';
const KEY='sd5979-cram-v1';
const load=()=>{{try{{return JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch{{return {{}}}}}};
let mastered=load();
const save=()=>{{try{{localStorage.setItem(KEY,JSON.stringify(mastered))}}catch{{}}}};

const cards=[...document.querySelectorAll('.c-card')];
const tabBtns=[...document.querySelectorAll('.tab-btn')];
let curTab='final';

const updateProg=()=>{{
  let vis=0, done=0;
  cards.forEach(c=>{{
    const q=c.dataset.qno, isM=!!mastered[q];
    c.classList.toggle('is-mastered',isM);
    const b=c.querySelector('.master-btn');
    b.setAttribute('aria-pressed',String(isM));
    b.textContent=isM?'✓ 已背':'○ 未背';
    if(!c.hidden){{vis++;if(isM)done++}}
  }});
  document.getElementById('m-prog').textContent=`已背 ${{done}} / ${{vis}}`;
  document.getElementById('vis-cnt').textContent=`当前 ${{vis}} 题`;
}};

const applyTab=t=>{{
  curTab=t;
  tabBtns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tab===t)));
  cards.forEach(c=>{{
    let show=true;
    if(t==='final') show=c.dataset.round==='final';
    else if(t==='weak') show=c.dataset.weak==='1';
    else if(t==='openq') show=c.dataset.kind==='openq';
    else if(t==='mcq') show=c.dataset.kind==='mcq';
    c.hidden=!show;
  }});
  updateProg();
}};

tabBtns.forEach(b=>b.addEventListener('click',()=>applyTab(b.dataset.tab)));
cards.forEach(c=>{{
  c.querySelector('.master-btn').addEventListener('click',()=>{{
    const q=c.dataset.qno;mastered[q]=!mastered[q];save();updateProg();
  }});
  const ans=c.querySelector('.c-ans');
  ans.addEventListener('click',()=>{{
    if(document.body.classList.contains('quiz-hide')) ans.classList.toggle('revealed');
  }});
  // On-demand image loading only when user opens <details>
  const det=c.querySelector('.img-fold');
  det.addEventListener('toggle',()=>{{
    if(!det.open)return;
    det.querySelectorAll('.lazy-img-slot').forEach(slot=>{{
      const fig=document.createElement('figure');
      const img=document.createElement('img');
      img.loading='lazy';img.alt=slot.dataset.cap||'';img.setAttribute('src',slot.dataset.src);
      const cap=document.createElement('figcaption');cap.textContent=slot.dataset.cap||'';
      fig.append(img,cap);
      slot.replaceWith(fig);
    }});
  }});
}});

const hideBtn=document.getElementById('toggle-hide');
hideBtn.addEventListener('click',()=>{{
  const on=document.body.classList.toggle('quiz-hide');
  hideBtn.setAttribute('aria-pressed',String(on));
  hideBtn.textContent=on?'👁️ 展开全部答案':'🙈 遮盖答案自测';
  if(on) document.querySelectorAll('.c-ans').forEach(a=>a.classList.remove('revealed'));
}});

applyTab('final');
}})();
</script>
</body></html>"""

out = ROOT / "mobile/cram.html"
out.write_text(html_doc, encoding="utf-8")
print(f"BUILT {out} ({len(CRAM_ITEMS)} cram cards, {len(html_doc):,} bytes)")
