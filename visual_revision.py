"""Visual, source-first revision edition. Course-specific interpretation is labelled.
Run with python build_site.py; content data remains in data/pages and exam_items.
"""
import re, html, json, struct

# Each entry: title, teacher answer, option-by-option diagnosis, additional evidence.
MC = {
'L01-E01': ('为什么不是 100%？','C', ['答非所问｜相关与因果不能解释这里为什么有剩余方差。','答非所问｜定性研究的作用不是本题所问。','正确｜老师把原因归于尚未解释的方差。','答非所问｜多题项测量并不回答剩余方差问题。'], [('L12',11)]),
'L02-E01': ('研究问题需要多精确？','C',['逻辑跳跃｜不能从 subordinative 直接推出论证弱。','定义偏差｜问题不是太具体，而是核心概念太含糊。','正确｜AI、mind、combat 和 won 都未明确界定。','题目层级混淆｜比较针对假设检验，不能代替对研究问题概念的澄清。'], [('L02',23),('L02',65)]),
'L03-E01': ('启发式测试：谁来做，成本如何？','D',['定义错误｜把专家换成了无经验用户。','定义错误｜把 cheap and fast 换成 slow but thorough。','定义错误｜参与者与成本描述都不符合本题定义。','正确｜专家用经验法则，廉价而快速。'], [('L03',6),('L03',7),('L03',10)]),
'L03-E02': ('有提纲，还能追问：哪种访谈？','B',['不够精确｜开放式问题只是其中一个特征，未涵盖访谈提纲。','正确｜有预设提纲，又允许灵活追问，属于半结构访谈。','定义错误｜structured 无法完整概括题中的灵活探索。','不够精确｜focused 不如 semi-structured 对题述步骤的对应直接。'], [('L03',26),('L03',27),('L03',28)]),
'L04-E02': ('把“决定”不断向下一层推','D',['概念错位｜本题答案页强调解释不断后退。','逻辑形式错误｜题干不是有效的 modus ponens。','定义混淆｜这里是继续推向新一层，不是回到同一前提。','正确｜无限后退：人→皮层→神经网络→突触→粒子，仍未解释决定是什么。'], []),
'L04-E03': ('sense 与 reference 的课程区分','A',['正确｜按老师解释：复制外部形式，却不知道词指向什么。','定义颠倒｜把 sense 与 reference 的能力方向倒过来了。','概念偷换｜日常的“不通顺”不是本题的 sense/reference 区分。','不够贴题｜知道如何知道属于认识论表述，未回答指定的两个概念。'], []),
'L04-E04': ('两条单极量表何时能合并？','B',['证据层级错误｜老师在此看知觉上的相反关系，不能只凭 RGB 否决。','正确｜题设在知觉上把深灰当作纯黑，与纯白形成真对立。','证据层级错误｜同 A，物理 RGB 差别没有直接回答知觉量表问题。','依据不足｜“再加灰色量表”不是当前可以合并的理由。'], [('L04',29),('L04',30),('L04',31),('L04',32)]),
'L04-E05': ('4 与 0：对比不等于正相反','C',['理由错误｜结论虽为不合并，却仅用 RGB 差异解释。','定义错误｜“几乎相同”不足以证明两端正相反。','正确｜知觉评分 4 与 0 未形成题目要求的两极真对立。','逻辑缺口｜新增灰色量表不能证明当前两条量表已可合并。'], [('L04',29),('L04',30),('L04',31),('L04',32)]),
'L05-E01': ('fat finger 与 Fitts：最佳答案要完整','D',['不完整｜老师承认压力使错误增加，但这不是全部。','不完整｜指针与目标宽度比是要点，但还遗漏 A。','依据不符｜老师答案页没有把差异归于另一种对数分布。','正确｜答案页同时确认 A 和 B。'], [('L05',32)]),
'L05-E04': ('思考→激活，能否反推？','C',['逻辑形式不符｜不是否定前件，而是从结果反推原因。','术语不符｜不能概括题中的推理方向错误。','正确｜思考时激活，不代表刺激皮层就会思考或提高能力。','概念错位｜triangulation 不是这类反向因果推理。'], [('L12',37)]),
'L07-E01': ('根因也相关吗？','A',['正确｜在题设已经给定因果关系的前提下，老师选 A。','推理错误｜因果与相关有区别，不意味着根因反而不相关。','答非所问｜把题设关系问题换成了样本量与显著性。','违背题设｜忽略题目已经给定的共同根因关系。'], [('L12',47),('L12',48)]),
'L07-E02': ('反向题先重编码','B',['定义错误｜原始均值相反可能来自题意方向相反。','正确｜按本题答案，应先对 contra-indicative 项重编码再比较。','无题设依据｜“心理意义有争议”不是题中给出的不可靠证据。','逻辑错误｜总均值是 2.5 不能推出相关系数为零。'], [('L07',32),('L12',55),('L12',57)]),
'L08-E02': ('回归与因果：保留老师的 B','B',['课程答案未选｜带条件的泛论没有给出本题老师强调的预测并检验关系。','正确（课程口径）｜老师强调由自变量变化预测因变量变化并据此检验。','不够精确｜归纳与 defeasible reasoning 未涵盖老师选项 B 的检验表述。','答非所问｜测量误差并未直接解释题设的因果提问。'], [('L12',77),('L12',78)]),
'L08-E03': ('SEM 为什么不只是反推原因？','C',['缺少检验环节｜把可检验模型当成直接肯定后件。','逻辑错位｜换个箭头方向不能说明 SEM 如何建模和检验。','正确｜潜变量由可观测项预测后再检验，并允许未解释方差。','推理过度｜存在测量误差不等于模型推断完全不可检验。'], [('L08',33),('L08',46),('L12',82)]),
'L09-E01': ('ReCAPTCHA：没拒绝不等于证实','A',['正确｜未拒绝“非机器人”不能推出“是人类”。','假设混淆｜把拒绝 H₀ 的状态与“是人类”的结论混在一起。','逻辑错误｜未拒绝 Hₐ 不能推出相反身份。','逻辑错误｜把不能成立的推断当作确认人类的依据。'], [('L12',22),('L12',101)]),
'L09-E02': ('哪种设计更受顺序影响？','A',['正确｜同一参与者经历多个条件，更易有练习、疲劳等顺序影响。','概念类别错误｜随机化是缓解方法，不是题问的设计类型。','定义对比错误｜组间设计没有同一人依次完成各条件的同样结构。','概念类别错误｜平衡顺序是缓解办法。'], [('L09',25),('L09',27),('L09',28),('L12',103)]),
'L09-E04': ('Solomon：用最多的首次测量','D',['不完整｜只有一组，漏掉其他可用的首次测量。','不完整｜两组前测可用，但还可纳入 G3、G4 的首次后测。','混入重测｜G1after、G2after 已受先前填问卷影响。','正确｜G1before、G2before、G3after、G4after；老师要最多且未受先前问卷影响的数据。'], [('L09',29),('L12',106)]),
'L10-E02': ('One-way ANOVA 到底比较什么？','B',['定义错误｜三个因变量不是这道题的一元方差分析定义。','正确｜本题比较三个组在一个因变量上的均值。','定义错误｜把一个因变量换成了两个。','定义错误｜同样把一个因变量换成两个，不能由一个 IV 补救。'], [('L10',73),('L12',130)]),
'L10-E03': ('临界 t 为什么可能很大？','D',['不完整｜少自由度可能有关，但还需考虑拒绝域。','不完整｜小拒绝域也可能有关，但还需考虑自由度。','方向错误｜老师图例是较小 α，不是较大 α。','正确｜A 与 B 都可能作用；答疑表中是很少观测、1% 拒绝域。'], [('L10',26),('L10',27),('L10',28),('L12',128)]),
'L11-E01': ('与别人比，还是与过去的自己比？','1:D / 2:A',['第 1 问：A、B 错在 paired；C 错在 Hₐ；D 是老师答案。','第 2 问：A 是老师答案；B 错在 H₀；C、D 错在 independent。','先拆两条轴：无差异/有改善 → H₀/Hₐ；不同人/同一人前后 → independent/paired。','条件检查｜老师答案页还追问测量水平以及能否用 t-test，不要漏看。'], [('L11',6),('L12',118)]),
'L11-E02': ('不显著，能说一样好吗？','C',['无题设依据｜题目没有给出未校正 α 导致的问题。','方法理解错误｜MANOVA 的这项检验本来就在处理零假设。','正确｜未拒绝 H₀，不能据此证明人和 bot 同样可信、有吸引力、高效。','概念错位｜CCI 不是题中 MANOVA 结论的已给证据；老师另将其列为旁支。'], [('L11',10),('L12',96),('L12',139),('L12',164)]),
}

# Short answer units with precise page-level evidence, never keyword-only matches.
OQ = {
'L04-E01': [('1 · 测量水平','Nominal：分到 like / dislike 类别。',[('L04',75)]),('2 · 是否为 rating scale？','不是；没有多个有序等级，距离没有意义。',[('L04',75)]),('3 · I don’t like 是否合适？','不合适；老师要求避免在反向题中使用 not / don’t，以减少混淆。',[('L04',48),('L04',75)]),('4 · 文本框是什么数据？','定性、轶事性证据；若做统计处理，需进行评分。',[('L04',75)])],
'L05-E02': [('A · 最困难条件','条件 2：没有预警，却出现需要射击的对手。',[('L05',42)]),('B · 表现如何？','反应更慢，错误率更高，即效率更低。',[('L05',42)])],
'L05-E03': [('A · 中性基线的问题','被检查是否说谎时，很难处于真正情绪中性的状态。',[('L05',65)]),('B · 其他变异来源','感冒、恋爱或失恋、恐惧、烦恼、愤怒等。',[('L05',65)]),('C · 可能没有这些变异的人','受过声音训练者：职业扑克玩家、特工、惯犯、舞台演员。',[('L05',65)])],
'L08-E01': [('A · Mediation','X（VR app）→ M（健康知识）→ Y（体验）。',[('L08',27),('L12',73)]),('B · Moderation','W（健康动机）改变 X 对 Y 的作用。',[('L08',28),('L12',74)]),('C · Moderated mediation','X 经 M 影响 Y 的间接效应取决于 W。',[('L08',29),('L12',75)]),('D · Mediated moderation','X × W → M → Y；交互作用经 M 传递。答疑承认原箭头图是视觉比喻，学生图更好。',[('L08',30),('L12',19),('L12',20),('L12',76)])],
'L09-E03': [('A · 两个条件','Dogs and Cats（狗与猫）。这是 L09 第 82 页给出的原答案。',[('L09',82)]),('B · 混淆变量是什么？','颜色：猫训练集与白色重合，狗训练集与黑色重合。原题问 confound，答疑变体问 data split，都需讲明颜色与类别重合。',[('L09',83),('L12',171)]),('C · 为何不自己推翻？','原课件说缺少概念知识、推理系统，无法做验证性统计；新答疑强调无法进行逻辑验证。',[('L09',84),('L12',172)])],
'L10-E01': [('Type I · 错误报警','新 FMS 并未提高表现，却仍然更换；花资源，还让飞行员重学界面，得不到收益。',[('L10',35),('L10',42),('L12',114)]),('Type II · 漏掉信号','新 FMS 本来能提高准确率，却继续旧界面；原本可减少的操作错误仍可能发生。',[('L10',35),('L10',42),('L12',114)])],
'L10-E04': [('测量是否可信？','体温计的 IR 感测部分未连接，输出只是一定范围的随机数；仪器互相一致不保证测到真实温度。',[('L10',79),('L12',133)]),('不显著能推出安全吗？','此黑箱让 H₀ 根本无法被反驳；据此不能支撑两种头盔安全的结论。',[('L10',79)]),('如何对待定性反馈？','参与者报告太热，不能仅因坏仪器没有极端值就归为自我暗示；这是题目延续页要你质疑的推断。',[('L10',78),('L12',132)])],
'L10-E05': [('真正该质疑什么？','EMOTIV 的情绪解释过程是黑箱：算法、阈值和判断信心从何而来？',[('L10',82),('L12',136)]),('为何显著也不够？','把肌肉或脑活动解释成某种情绪的测量环节尚待说明，不能只凭显著结果跳到“AI 队友改善情绪”。',[('L10',81),('L10',82),('L12',136)])],
'L11-E03': [('56% 意味着什么？','56% 接近 50–50 的最大不确定位置，因此“Humanoid”的决定仍很可疑；不能把 56% 直接说成很有把握。',[('L11',58),('L12',160)]),('两个端点作对比','P = 0% 或 100% 时，老师图中不确定性为零。',[('L11',58),('L12',160)])],
}

EXTRA = [
('L12-E01',36,[37],'OpenQ','广告里的肯定后件',[('推理形式','Focus → Brainwave；观察 Brainwave，不能推出 Focus。老师称 ex-consequence。',[('L12',37)])]),
('L12-E02',39,[40,41,42,43,44],'OpenQ','8% + 1% 为什么不是总体 9%？',[('分母问题','8% 与 1% 分别以男女子群为分母，不能直接相加。',[('L12',42)]),('绝对数检查','老师例子：男性 125,000 × 8% = 10,000；女性 2,000,000 × 1% = 20,000。低比例不一定意味着绝对人数少。',[('L12',40)]),('隐藏假设','男女数量是否相等？是否只有两个类别？CPU 变体还额外假设硬件 bug 一定造成内存泄漏。',[('L12',41),('L12',44)])]),
('L12-E03',45,[46],'OpenQ','风险从 10% 降到 5%',[('判断','老师答案：并非虚假，但可能误导；相对下降 50%，绝对下降 5 个百分点。',[('L12',46)])]),
('L12-E04',65,[66],'MCQ','零售回归：谁是自变量？',('A',['正确｜Sales 是被预测的结果；天气、竞争者行为、道路维护、新产品发布是 predictors。','角色颠倒｜把预测结果与解释变量换了方向。','角色错误｜本题要预测 sales，不是 competitor behavior；sales 也不应被当作这里的 predictor。','角色错误｜把 competitor behavior 放成唯一 IV，又把 sales 和其他 predictors 都放进 DV。'])),
('L12-E05',69,[70,71],'MCQ','把所有日志丢进回归就够了吗？',('D',['不完整｜缺乏理论与遗漏混淆都对，但还漏掉 C。','理由不符｜本题老师没有用“ordinal 不允许回归”概括核心错误。','不完整｜加载时间与体验的关系出于猜想是问题之一，但还漏掉 A。','正确｜A 与 C 都对；71 页列出误点、猫碰鼠标、竞争者浏览等其他解释。'])),
('L12-E06',91,[92],'MCQ','y = ax + b：weight 与 bias',('A',['正确｜a = slope / weight；b = intercept / bias。','定义颠倒｜slope 与 intercept 交换了。','术语不符｜本题 a 不是 offset，b 不是 cutoff。','术语不符｜把回归系数和阈值概念混在一起。'])),
('L12-E07',140,[141,142,143,144],'OpenQ','大模型与小学生：谁的研究更有力？',[('选择','Dài ān；按 144 页的比较，小学生的算术研究更好。',[('L12',143),('L12',144)]),('证据维度','技术稳健性、测量可靠性、数据采集透明度、可重复性、测量水平、理论效度、检验强度和允许的结论。逐项比较见原表。',[('L12',144)]),('为什么不选其他人？','更复杂的架构、更多数据、权威作者、更快训练，都不能替代上面这些研究质量证据。',[('L12',142),('L12',143),('L12',144)])]),
('L12-E08',161,[162,163],'MCQ','Naïve Bayes 与 multicollinearity',('A',['正确｜按老师答案：无论类别多相关，都剔除与给定假设不一致的类别。','方法混淆｜题述方法不是借助 PCA 剔除中间值。','机制不符｜不是靠重复更新来逐渐容纳跨类混合特征。','定义不符｜不是允许特征按比例属于多个集合。'])),
('L12-E09',169,[170,171,172],'OpenQ','猫狗题的新问法：nominal measurement',[('A · 两个类别','Dogs and Cats。原 L09 问“实验条件”，这里改问“名义测量类别”；两份原答案都写狗与猫，但作答应对应当前问题的用词。',[('L09',82),('L12',170)]),('B · 分割依据','颜色；猫与白色重合，狗与黑色重合。',[('L12',171)]),('C · 不会自我证伪的原因','按老师解释：缺乏概念知识，也没有推理系统进行逻辑验证。',[('L12',172)])]),
]

TOPICS = [
('相关与因果','根因是否也相关；反向题重编码；Spearman–Brown 信度。',31,[7,55,56,57],['L07-E01','L07-E02']),
('回归与 SEM','预测和检验；潜变量与误差；中介、调节以及交互路径。',31,[15,17,19,59,60,68,78,82],['L08-E01','L08-E02','L08-E03']),
('实验设计','组内/组间；顺序效应；Solomon 四组与信度数据选择。',31,[28,101,103,106],['L09-E01','L09-E02','L09-E04']),
('t-test 与 ANOVA','一个 DV 还是多个；临界值、自由度与 α；Type I / II。',32,[114,118,120,122,124,125,128,130],['L10-E01','L10-E02','L10-E03']),
('Bayesian statistics','先验信息；Naïve 的限制；56% 与决策不确定性。',32,[146,153,154,155,156,157,158,160,163],['L11-E03','L12-E08']),
('报告研究结果','区分绝对与相对风险下降；分清误导性表述与虚假陈述。',32,[40,41,42,46,64,168],['L12-E02','L12-E03','L12-E07']),
]

# Phrase occurrence is evidence of presence, not evidence of truth or importance.
CONCEPTS = {
'L01-E01':['correlation','qualitative data','unexplained variance','psychometric scales'],
'L02-E01':['subordinative','Research Question','concepts','hypotheses'],
'L03-E01':['heuristic','experts','naïve users'], 'L03-E02':['open-ended','semi-structured','structured','focused'],
'L04-E02':['sense','Modus ponens','Circularity','Infinite regress'], 'L04-E03':['sense','reference','epistemology'],
'L04-E04':['bipolar','unipolar','RGB'], 'L04-E05':['bipolar','unipolar','RGB'],
'L05-E01':['Fitts','stress','logarithmic'], 'L05-E04':['Fallacy of the inverse','Ambiguity variability','Ex-consequentia','Triangulation'],
'L07-E01':['causation','correlation','sample size'], 'L07-E02':['Spearman-Brown','recod','grand mean'],
'L08-E02':['causation','defeasible','measurement error'], 'L08-E03':['latent','ex-consequentia','unexplained variance'],
'L09-E01':['Null','Alternative'], 'L09-E02':['Within-subjects','Randomisation','Between-subjects','Counter-balancing'],
'L09-E04':['Solomon','Cronbach'], 'L10-E02':['Oneway ANOVA','MANOVA'], 'L10-E03':['degrees of freedom','rejection area'],
'L11-E01':['paired samples','independent samples'], 'L11-E02':['MANOVA','CCIs'],
'L12-E04':['dependent variable','independent variable'], 'L12-E05':['confound','ordinal','theory'],
'L12-E06':['slope','intercept','bias','cutoff'], 'L12-E08':['Naïve Bayes','Principal Component Analysis','multicollinearity']
}

def install(g):
    root, lectures, items = g['ROOT'], g['lectures'], g['items']
    E = lambda s: html.escape(str(s), quote=True)
    for id,q,ans,kind,title,notes in EXTRA:
        p=lectures['L12']['pages'][q-1]
        items.append(dict(id=id,lecture='L12',category='Response',kind=kind,source_file=lectures['L12']['source_file'],question_slide=q,answer_slides=ans,question_text=p['text'],question_text_norm=p['text_norm']))
        if kind=='MCQ': MC[id]=(title,notes[0],notes[1],[('L12',n) for n in ans])
        else: OQ[id]=notes
    for it in items:
        # The old derived file mislabels this one as Insight; visible source says Application.
        if it['id']=='L07-E02': it['category']='Application'
    (root/'data/review_notes.json').write_text(json.dumps(dict(mc=MC,open=OQ,topics=TOPICS,extra=EXTRA),ensure_ascii=False,indent=2),encoding='utf-8')
    def cite(lid,s,depth=0):
        pre='../'*depth
        title=f"{lectures[lid]['source_file']} · PDF 第 {s} 页"
        return f'<a class="source-link" href="{pre}lectures/{lid}.html#{lid}-s{s}" data-image="{pre}assets/img/{lid}/slide-{s:03}.png" data-pdf="{pre}pdfs/{lid}.pdf#page={s}" data-label="{E(title)}">{lid} · 第 {s} 页 ↗</a>'
    def refs(rs,depth=0): return '<div class="refs">'+''.join(cite(l,s,depth) for l,s in dict.fromkeys(rs))+'</div>'
    def figure(lid,s,depth=0):
        pre='../'*depth
        with (root/f'assets/img/{lid}/slide-{s:03}.png').open('rb') as f: w,h=struct.unpack('>II',f.read(24)[16:24])
        return f'<figure class="source-figure"><a href="{pre}assets/img/{lid}/slide-{s:03}.png" data-image="{pre}assets/img/{lid}/slide-{s:03}.png" data-pdf="{pre}pdfs/{lid}.pdf#page={s}" data-label="{E(lectures[lid]["source_file"])} · PDF 第 {s} 页"><img src="{pre}assets/img/{lid}/slide-{s:03}.png" width="{w}" height="{h}" loading="lazy" alt="{lid} 课件原页，第 {s} 页。点击放大查看公式、图表和全部选项"></a><figcaption>{E(lectures[lid]["source_file"])} · PDF 第 {s} 页 · 点击放大</figcaption></figure>'
    old_frame=g['frame']
    def frame(title,depth,active,body,extra_head=''):
        pre='../'*depth
        s=old_frame(title,depth,active,body,extra_head+f'<link rel="stylesheet" href="{pre}assets/css/revision.css">')
        if depth==0:
            mobile_target=f'mobile/{active}'
        elif active.endswith('-exam.html'):
            mobile_target=f'{pre}mobile/exam/{active}'
        else:
            mobile_target=f'{pre}mobile/lectures/{active}'
        s=s.replace('<div id="nv-list">',f'<a class="mobile-switch-btn" href="{mobile_target}">📱 切换到手机版 →</a><div id="nv-list">',1)
        s=s.replace('<a href="'+pre+'exam-items.html">','<a href="'+pre+'response.html">老师答疑 / 重点地图</a><a href="'+pre+'exam-items.html">',1)
        s=s.replace('</body>',f'<script src="{pre}assets/js/revision.js"></script></body>')
        return s
    g['frame']=frame
    def clean(t):
        t=re.sub('[\ue000-\uf8ff]','',t)
        return E(t)
    audit={}
    for id,words in CONCEPTS.items():
        audit[id]=[]
        for word in words:
            hits=[]
            # Ignore embedded questions, answer/continuation pages, bibliographies.
            for lid,d in lectures.items():
                for p in d['pages']:
                    t=p['text_norm']
                    if any(i['lecture']==lid and (i['question_slide']==p['slide'] or p['slide'] in i['answer_slides']) for i in items):continue
                    if re.search(r'exam\s*sample|sample[- ]item|^References\b',t,re.I):continue
                    if word.lower() in t.lower():hits.append((lid,p['slide']))
            audit[id].append(dict(term=word,pages=hits))
    (root/'data/concept_evidence_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    def audit_panel(id):
        rows=[]
        for x in audit.get(id,[]):
            hits=x['pages']
            status=f'正文原词命中 {len(hits)} 页' if hits else '未检出独立正文原词命中'
            rows.append(f'<section><h3>{E(x["term"])}</h3><p class="note">{status}</p>{refs(hits,1) if hits else "<p>这不证明概念从未以其他表达讲过；不把它直接当成该选项错误的理由。</p>"}</section>')
        return '<details class="concept-audit"><summary>这些选项的概念，课件正文是否出现过？</summary><p class="note">检索全部 903 页，排除已收录题目、答案页和可识别的样题 / 参考文献页。下列为按原词检索的出现记录，可能包含变体遗漏；出现不代表定义正确，也不代表考试重点。错项判定仍以逐项解释和老师答案为准。</p><div class="answer-units">'+''.join(rows)+'</div></details>' if rows else ''
    # ---------------- Bilingual slide Chinese renderer (offline, zero deps) ----------------
    zh_slides = {}
    zh_dir = root / 'data/zh_slides'
    if zh_dir.exists():
        for lid in lectures:
            zf = zh_dir / f'{lid}.json'
            if zf.exists():
                zh_slides[lid] = json.loads(zf.read_text(encoding='utf-8'))

    def _norm_key(s):
        return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', s.lower())).strip()

    term_key_lookup = {}
    for k, t in g['TERMS_JS'].items():
        term_key_lookup[_norm_key(k)] = k
        if '(' in k:
            term_key_lookup[_norm_key(re.sub(r'\([^)]*\)', '', k))] = k
    for alias, k in g.get('MATCH_LOOKUP', {}).items():
        term_key_lookup[_norm_key(alias)] = k

    def _match_course_term(en_text):
        nk = _norm_key(en_text)
        if nk in term_key_lookup:
            return term_key_lookup[nk]
        if ',' in en_text:
            nk2 = _norm_key(en_text.split(',', 1)[0])
            if nk2 in term_key_lookup:
                return term_key_lookup[nk2]
        return None

    def _extract_brace(s, pos):
        if pos >= len(s) or s[pos] != '{':
            return '', pos
        depth, i = 0, pos
        while i < len(s):
            if s[i] == '{': depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return s[pos+1:i], i+1
            i += 1
        return s[pos+1:], len(s)

    MATH_SYMS = {
        r'\alpha':'α', r'\beta':'β', r'\gamma':'γ', r'\delta':'δ', r'\eta':'η',
        r'\mu':'μ', r'\sigma':'σ', r'\Sigma':'Σ', r'\psi':'ψ', r'\rho':'ρ',
        r'\kappa':'κ', r'\zeta':'ζ', r'\xi':'ξ', r'\chi':'χ', r'\lambda':'λ',
        r'\times':'×', r'\cdot':'·', r'\cap':'∩', r'\cup':'∪', r'\rangle':'⟩',
        r'\langle':'⟨', r'\le':'≤', r'\ge':'≥', r'\neq':'≠', r'\ne':'≠',
        r'\pm':'±', r'\approx':'≈', r'\infty':'∞', r'\to':'→', r'\rightarrow':'→',
        r'\circ':'°', r'\sum':'∑',
    }

    def render_math(expr):
        s = expr.strip()
        out = []
        i = 0
        n = len(s)
        while i < n:
            if s.startswith(r'\frac', i):
                j = i + 5
                while j < n and s[j] == ' ': j += 1
                num, j = _extract_brace(s, j)
                while j < n and s[j] == ' ': j += 1
                den, j = _extract_brace(s, j)
                out.append(f'<span class="zh-frac"><span class="zh-num">{render_math(num)}</span><span class="zh-den">{render_math(den)}</span></span>')
                i = j
            elif s.startswith(r'\sqrt', i):
                j = i + 5
                while j < n and s[j] == ' ': j += 1
                body, j = _extract_brace(s, j)
                out.append(f'<span class="zh-sqrt">√<span class="zh-rad">{render_math(body)}</span></span>')
                i = j
            elif s.startswith(r'\bar', i) and (i + 4 == n or not s[i+4].isalpha()):
                j = i + 4
                while j < n and s[j] == ' ': j += 1
                if j < n and s[j] == '{':
                    body, j = _extract_brace(s, j)
                else:
                    body, j = (s[j] if j < n else ''), j + 1
                out.append(f'<span class="zh-bar">{render_math(body)}</span>')
                i = j
            elif s.startswith(r'\text', i):
                j = i + 5
                while j < n and s[j] == ' ': j += 1
                body, j = _extract_brace(s, j)
                out.append(f'<span class="zh-mtext">{E(body)}</span>')
                i = j
            elif s.startswith(r'\ ', i):
                out.append(' ')
                i += 2
            elif s[i] == '\\':
                m = re.match(r'\\[A-Za-z]+', s[i:])
                if m:
                    cmd = m.group(0)
                    out.append(MATH_SYMS.get(cmd, E(cmd[1:])))
                    i += len(cmd)
                else:
                    i += 1
            elif s[i] in ('_', '^'):
                tag = 'sub' if s[i] == '_' else 'sup'
                j = i + 1
                if j < n and s[j] == '{':
                    body, j = _extract_brace(s, j)
                    out.append(f'<{tag}>{render_math(body)}</{tag}>')
                elif j < n and s[j] == '\\':
                    m = re.match(r'\\[A-Za-z]+', s[j:])
                    if m and m.group(0) == r'\circ' and tag == 'sup':
                        out.append('°')
                        j += len(m.group(0))
                    elif m:
                        out.append(f'<{tag}>{MATH_SYMS.get(m.group(0), E(m.group(0)[1:]))}</{tag}>')
                        j += len(m.group(0))
                    else:
                        j += 1
                elif j < n:
                    out.append(f'<{tag}>{E(s[j])}</{tag}>')
                    j += 1
                i = j
            elif s[i] in ('{', '}'):
                i += 1
            else:
                out.append(E(s[i]))
                i += 1
        return ''.join(out)

    INLINE_PAT = re.compile(
        r'(`[^`\n]+`)'
        r'|(\[\[[^\[\]|]+\|[^\[\]|]+\]\])'
        r'|(\*\*[^*\n]+?\*\*)'
        r'|(\$(?!\s)[^$\n]+?(?<!\s)\$)'
        r'|((?<!\*)\*(?!\s|\*)[^*\n]+?(?<!\s)\*(?!\*))'
    )

    def render_inline(text, stats):
        text = text.replace(r'\$', '\x00USD\x00')
        out, last = [], 0
        for m in INLINE_PAT.finditer(text):
            if m.start() > last:
                out.append(E(text[last:m.start()]).replace('\x00USD\x00', '$'))
            tok = m.group(0)
            if m.group(1):
                inner_code = tok[1:-1]
                if re.fullmatch(r'\[\[[^\[\]|]+\|[^\[\]|]+\]\]', inner_code.strip()):
                    out.append(render_inline(inner_code.strip(), stats))
                elif '[[' in inner_code and ']]' in inner_code:
                    out.append(f'<code>{render_inline(inner_code, stats)}</code>')
                else:
                    out.append(f'<code>{E(inner_code).replace(chr(0)+"USD"+chr(0), "$")}</code>')
            elif m.group(2):
                zh_part, en_part = tok[2:-2].split('|', 1)
                zh_part, en_part = zh_part.strip(), en_part.strip()
                stats['terms'] += 1
                ckey = _match_course_term(en_part)
                cls = 'rm-term term' if ckey else 'rm-term'
                extra = f' data-term="{E(ckey)}" tabindex="0"' if ckey else ''
                if zh_part.lower() == en_part.lower():
                    out.append(f'<mark class="{cls}"{extra}><strong>{E(en_part)}</strong></mark>')
                else:
                    out.append(f'<mark class="{cls}"{extra}><strong>{E(zh_part)}</strong><span class="rm-en">（{E(en_part)}）</span></mark>')
            elif m.group(3):
                out.append(f'<strong>{render_inline(tok[2:-2], stats)}</strong>')
            elif m.group(4):
                out.append(f'<span class="zh-math">{render_math(tok[1:-1])}</span>')
            elif m.group(5):
                out.append(f'<em>{render_inline(tok[1:-1], stats)}</em>')
            last = m.end()
        if last < len(text):
            out.append(E(text[last:]).replace('\x00USD\x00', '$'))
        return ''.join(out)

    def render_zh_slide(md_text):
        stats = {'terms': 0}
        if not md_text or not md_text.strip():
            return '<p class="note">本页暂无中文对照，请查看左侧原图。</p>', 0
        lines = md_text.replace('\r\n', '\n').split('\n')
        out = []
        i, n = 0, len(lines)
        while i < n:
            ln = lines[i]
            st = ln.strip()
            if not st:
                i += 1
                continue
            # Display math $$...$$
            if st.startswith('$$'):
                if st.endswith('$$') and len(st) > 4:
                    out.append(f'<div class="zh-math-block">{render_math(st[2:-2])}</div>')
                    i += 1
                else:
                    buf = [st[2:]]
                    i += 1
                    while i < n and not lines[i].strip().endswith('$$'):
                        buf.append(lines[i])
                        i += 1
                    if i < n:
                        buf.append(lines[i].strip()[:-2])
                        i += 1
                    out.append(f'<div class="zh-math-block">{render_math(" ".join(buf))}</div>')
                continue
            # Headings
            mh = re.match(r'^(#{1,4})\s+(.*)$', st)
            if mh:
                lvl = min(max(len(mh.group(1)), 3), 4)
                out.append(f'<h{lvl} class="zh-h{lvl}">{render_inline(mh.group(2), stats)}</h{lvl}>')
                i += 1
                continue
            # Horizontal rule
            if re.match(r'^[-*_]{3,}$', st):
                out.append('<hr class="zh-hr">')
                i += 1
                continue
            # Blockquote
            if st.startswith('>'):
                qbuf = []
                while i < n and lines[i].strip().startswith('>'):
                    qbuf.append(re.sub(r'^>\s?', '', lines[i].strip()))
                    i += 1
                out.append('<blockquote class="zh-quote">' + '<br>'.join(render_inline(q, stats) for q in qbuf if q) + '</blockquote>')
                continue
            # Markdown table
            if st.startswith('|') and st.endswith('|') and i + 1 < n and re.match(r'^\|[\s:|-]+\|$', lines[i+1].strip()):
                def split_row(r):
                    masked = re.sub(r'\[\[[^\[\]]+\]\]', lambda m: m.group(0).replace('|', '\x00PIPE\x00'), r.strip().strip('|'))
                    return [c.replace('\x00PIPE\x00', '|').strip() for c in masked.split('|')]
                headers = split_row(st)
                i += 2
                rows = []
                while i < n and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                    rows.append(split_row(lines[i]))
                    i += 1
                thead = '<thead><tr>' + ''.join(f'<th>{render_inline(c, stats)}</th>' for c in headers) + '</tr></thead>'
                tbody = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{render_inline(c, stats)}</td>' for c in r) + '</tr>' for r in rows) + '</tbody>'
                out.append(f'<div class="zh-table-wrap"><table class="zh-table">{thead}{tbody}</table></div>')
                continue
            # Unordered list (supports 2 levels of nesting)
            if re.match(r'^\s*[-*•]\s+', ln):
                items_html = []
                while i < n and re.match(r'^\s*[-*•]\s+', lines[i]):
                    m_li = re.match(r'^(\s*)[-*•]\s+(.*)$', lines[i])
                    indent = len(m_li.group(1).replace('\t', '  '))
                    content = render_inline(m_li.group(2), stats)
                    if indent >= 2 and items_html:
                        if items_html[-1].endswith('</ul></li>'):
                            items_html[-1] = items_html[-1][:-10] + f'<li>{content}</li></ul></li>'
                        else:
                            items_html[-1] = items_html[-1][:-5] + f'<ul class="zh-sublist"><li>{content}</li></ul></li>'
                    else:
                        items_html.append(f'<li>{content}</li>')
                    i += 1
                out.append('<ul class="zh-list">' + ''.join(items_html) + '</ul>')
                continue
            # Ordered list
            if re.match(r'^\d+\.\s+', st):
                olist = []
                while i < n and re.match(r'^\d+\.\s+', lines[i].strip()):
                    content = re.sub(r'^\d+\.\s+', '', lines[i].strip())
                    olist.append(f'<li>{render_inline(content, stats)}</li>')
                    i += 1
                out.append('<ol class="zh-olist">' + ''.join(olist) + '</ol>')
                continue
            # Paragraph
            pbuf = []
            while i < n:
                cur = lines[i].strip()
                if not cur or cur.startswith(('###', '####', '>', '$$')) or re.match(r'^\s*[-*•]\s+', lines[i]) or re.match(r'^\d+\.\s+', cur) or (cur.startswith('|') and cur.endswith('|')):
                    break
                pbuf.append(render_inline(cur, stats))
                i += 1
            out.append('<p>' + '<br>'.join(pbuf) + '</p>')
        return ''.join(out), stats['terms']

    def strip_zh_plain(md_text):
        s = re.sub(r'\[\[([^\[\]|]+)\|([^\[\]|]+)\]\]', r'\1 \2', md_text or '')
        s = re.sub(r'[#>*`]', ' ', s)
        return re.sub(r'\s+', ' ', s).strip()

    def header(k,t,p):return f'<header class="review-head"><p class="eyebrow">SD5979 / {k}</p><h1>{t}</h1><p class="lead">{p}</p></header>'
    def lecture(lid,d):
        blocks=[]
        lec_zh = zh_slides.get(lid, {})
        lec_term_total = 0
        for p in d['pages']:
            s=p['slide'];related=[it for it in items if it['lecture']==lid and (it['question_slide']==s or s in it['answer_slides'])]
            links=''.join(f'<a class="pill" href="../exam/{lid}-exam.html#{it["id"]}">复习 {it["id"]}</a>' for it in related)
            found=set();g['markup'](p['text'],found)
            ts=''.join(f'<span class="term" tabindex="0" data-term="{E(k)}">{E(k)} · {E(g["TERMS_JS"][k]["zh"])}</span> ' for k in sorted(found))
            zh_html, term_cnt = render_zh_slide(lec_zh.get(str(s), ''))
            lec_term_total += term_cnt
            term_badge = f'<span class="zh-badge">含 {term_cnt} 个研究词汇</span>' if term_cnt else ''
            term_strip_html = f'<div class="term-strip"><span class="term-strip-label">本页大纲术语（悬浮看定义）：</span>{ts}</div>' if ts else ''
            blocks.append(
                f'<section class="slide visual-slide bilingual-slide" id="{lid}-s{s}">'
                f'<div class="slide-head"><div class="section-label">{lid} / {s:03} <span class="slide-count">第 {s} / {d["page_count"]} 页</span> {links}</div>'
                f'<a class="zoom-pill" href="../assets/img/{lid}/slide-{s:03}.png" data-image="../assets/img/{lid}/slide-{s:03}.png" data-pdf="../pdfs/{lid}.pdf#page={s}" data-label="{E(d["source_file"])} · PDF 第 {s} 页">🔍 放大原图</a></div>'
                f'<div class="bilingual-stage">'
                f'<div class="slide-en-col">{figure(lid,s,1)}</div>'
                f'<div class="slide-zh-col"><div class="zh-col-head"><span>中文对照</span>{term_badge}</div><div class="zh-body">{zh_html}</div></div>'
                f'</div>'
                f'{term_strip_html}'
                f'<details class="transcript"><summary>英文检索原文（公式与版式请看左侧原图）</summary><pre>{clean(p["text"])}</pre></details>'
                f'</section>'
            )
        jump=''.join(f'<a href="#{lid}-s{p["slide"]}">{p["slide"]}</a>' for p in d['pages'])
        toolbar = (
            '<div class="bilingual-toolbar" role="toolbar" aria-label="中英对照阅读设置">'
            '<div class="bt-group"><span class="bt-label">阅读布局</span>'
            '<button type="button" data-layout="side" aria-pressed="true">并排中英对照</button>'
            '<button type="button" data-layout="stack" aria-pressed="false">上下对照（大图）</button>'
            '<button type="button" data-layout="zh" aria-pressed="false">仅看中文</button>'
            '<button type="button" data-layout="en" aria-pressed="false">仅看原图</button>'
            '</div>'
            '<div class="bt-group">'
            '<button type="button" id="toggle-term-hl" aria-pressed="true">高亮研究词汇（含原英语）</button>'
            f'<span class="bt-stat">本讲共标注 <b>{lec_term_total}</b> 处研究词汇</span>'
            '</div></div>'
        )
        return frame(
            lid+' 中英对照讲义',1,lid+'.html',
            header('原课件 · 中英对照',lid+' · 逐页中英对照讲义',E(d['source_file'])+f' · 共 {d["page_count"]} 页 · 左侧保留老师英文原图与原版式，右侧逐页中文对照，研究课相关词汇已加粗高亮并括号标注原英语。')
            + toolbar
            + f'<div class="jump"><b>跳页</b>{jump}</div>'
            + '<div class="slides-wrap" data-layout="side">' + ''.join(blocks) + '</div>'
        )
    g['build_lecture']=lecture
    def exam(lid):
        its=[i for i in items if i['lecture']==lid]
        if not its:return None
        blocks=[]
        for it in its:
            id=it['id'];q=it['question_slide'];is_mc=id in MC
            title=MC[id][0] if is_mc else next((x[4] for x in EXTRA if x[0]==id),{'L04-E01':'Like / dislike 的四个小问','L05-E02':'预警与对手：最难条件','L05-E03':'测谎系统：中性基线可靠吗？','L08-E01':'中介与调节：四条路径','L09-E03':'猫狗模型：实验条件与逻辑','L10-E01':'FMS：两类错误的实际后果','L10-E04':'VR 头盔：体温计的黑箱','L10-E05':'MOBA：情绪测量的黑箱','L11-E03':'56%：有多确定？'}.get(id,id))
            question_zh=g['zh_exam'].get(id,{}).get('question','')
            translation=f'<details class="translation"><summary>题干中文辅助（原译文）</summary><p>{E(question_zh).replace(chr(10),"<br>")}</p></details>' if question_zh else ''
            stem_pages={'L10-E05':[81],'L12-E07':[141,142,143]}.get(id,[])
            stem_more=(' <h3>完整题目与情境延续</h3>'+''.join(figure(lid,s,1) for s in stem_pages)) if stem_pages else ''
            if is_mc:
                title,answer,rows,rs=MC[id]
                diag=''.join(f'<tr><th>{E(chr(65+n)) if id!="L11-E01" else "分析 "+str(n+1)}</th><td><span class="diagnosis">{E(r.split("｜")[0])}</span>{E(r.split("｜",1)[1] if "｜" in r else r)}</td><td>{refs([(lid,it["answer_slides"][0])]+rs,1)}</td></tr>' for n,r in enumerate(rows))
                response=f'<div class="answer-banner">老师答案 <strong>{E(answer)}</strong><span>以原页勾选为准</span></div><p class="note">以下为依据课件整理的逐项解释。未被选中不等于概念从未讲过；“无题设依据”也不等于全课未出现。</p><div class="table-scroll"><table class="diagnosis-table"><thead><tr><th>选项</th><th>为什么选 / 为什么错</th><th>依据原页</th></tr></thead><tbody>{diag}</tbody></table></div>'
                if id=='L08-E02':response+='<p class="caveat">课程口径：此题在 L08 第 48 页和 L12 第 78 页均勾选 B。这里记录老师对题设的解释；这张答案页不能支持“任何回归都自动证明因果”的扩大结论。</p>'
                if id=='L07-E02':response+='<p class="caveat">信息边界：题目给的是两个均值，老师借此考重编码。这里不据此虚构个体数据，也不额外计算信度系数。</p>'
                response+=audit_panel(id)
            else:
                response='<div class="answer-units">'+''.join(f'<section><h3>{E(t)}</h3><p>{E(a)}</p>{refs(rs,1)}</section>' for t,a,rs in OQ[id])+'</div>'
                response+='<p class="note">以上短答是课件内容的中文整理；每一小问分别对应上面的证据页。原答案 / 延续页见下方。</p>'
            original=''.join(figure(lid,s,1) for s in it['answer_slides'] if s not in stem_pages) or figure(lid,q,1)
            blocks.append(f'<article class="exam-item visual-exam" id="{id}"><div class="section-label">{id} / {E(it["category"])} / {"选择题" if is_mc else "开放题"}</div><h2>{E(title)}</h2>{refs([(lid,q)],1)}{figure(lid,q,1)}{stem_more}{translation}<div class="practice" data-item="{id}"><span>我的作答</span>'+(''.join(f'<button type="button" data-choice="{c}" aria-pressed="false">{c}</button>' for c in 'ABCD') if is_mc and id!='L11-E01' else '<textarea aria-label="我的短答" placeholder="先写下自己的理由，再展开解析。"></textarea>')+'<button type="button" class="bookmark" aria-pressed="false">加入错题</button></div>'+f'<details class="solution"><summary>查看老师答案与逐项解释 / 来源</summary>{response}<h3>老师原答案与题目延续</h3>{original}</details></article>')
        nav=''.join(f'<a class="pill" href="#{i["id"]}">{i["id"]}</a>' for i in its)
        return frame(lid+' 例题',1,lid+'-exam.html',header('逐题复习',lid+' · 看题、作答、核对证据','题目与公式保留原版式；解析默认收起，可先独立作答。')+f'<div class="item-nav">{nav}</div>'+''.join(blocks))
    g['build_exam_lecture']=exam
    def exam_index():
        cards=[]
        for i in items:
            id=i['id'];title=MC[id][0] if id in MC else next((x[4] for x in EXTRA if x[0]==id),i['question_text_norm'][:110])
            if id not in MC and id not in {x[0] for x in EXTRA}:title=OQ[id][0][0]+' · '+{'L04-E01':'Like / dislike 的四个小问','L05-E02':'预警与对手：最难条件','L05-E03':'测谎系统：中性基线','L08-E01':'中介与调节的四种路径','L09-E03':'猫狗模型的混淆与推理','L10-E01':'FMS 两类错误的实际后果','L10-E04':'VR 体温测量的黑箱','L10-E05':'MOBA 情绪测量的黑箱','L11-E03':'56% 与决策不确定性'}[id]
            cards.append(f'<a class="question-card" data-kind="{i["kind"]}" data-id="{id}" data-lecture="{i["lecture"]}" href="exam/{i["lecture"]}-exam.html#{id}"><span class="eyebrow">{id} · {"选择题" if i["kind"]=="MCQ" else "开放题"}</span><h3>{E(title)}</h3><span class="card-bottom">{i["lecture"]} 第 {i["question_slide"]} 页 <b>开始复习 ↗</b></span></a>')
        return frame('例题练习',0,'exam-items.html',header('题库',f'{len(items)} 组例题 · 每题都有课件证据','原有 30 组 + 答疑新增 9 组；L11 第一组含两小题。错题和作答保存在当前浏览器。')+'<div class="filter-bar"><label>搜索<input id="review-search" type="search" placeholder="题号 / 概念 / 关键词"></label><label>题型<select id="kind-filter"><option value="">全部题型</option><option value="MCQ">选择题</option><option value="OpenQ">开放题</option></select></label><label>讲次<select id="lecture-filter"><option value="">全部讲次</option>'+''.join(f'<option>{l}</option>' for l in lectures if any(i['lecture']==l for i in items))+'</select></label><label class="check"><input type="checkbox" id="mistake-filter">只看错题</label></div><p id="filter-count" aria-live="polite"></p><div class="question-grid">'+''.join(cards)+'</div><p class="empty-state" hidden>没有匹配的题目。可调整筛选条件，或在题目页加入错题。</p>')
    g['build_exam_index']=exam_index
    topic_cards=''.join(f'<section class="topic-card"><span class="eyebrow">老师明确列出的重点 · {n+1:02}</span><h2>{E(t)}</h2><p>{E(desc)}</p>{refs([("L12",s)])}<details><summary>概念澄清与相关练习</summary>{refs([("L12",p) for p in ps])}<div class="item-nav">'+''.join(f'<a class="pill" href="exam/{id[:3]}-exam.html#{id}">{id}</a>' for id in ids)+'</div></details></section>' for n,(t,desc,s,ps,ids) in enumerate(TOPICS))
    def index():
        cards=''.join(f'<a class="lecture-card" href="lectures/{l}.html"><span class="eyebrow">{l} / {d["page_count"]} PAGES · 中英对照</span><h3>{E(d["source_file"].split("SD5979")[-1].replace(".pdf","").strip())}</h3><span>打开中英对照讲义 →</span></a>' for l,d in lectures.items())
        return frame('可视化复习',0,'index.html',header('RESEARCH METHODS / 可视化复习','读懂概念。<br>说清理由。<span class="accent">找到原页。</span>','全部 12 讲 903 页课件均已升级为逐页中英对照：左侧保留老师英文原图与排版，右侧对照中文并将研究课词汇加粗高亮标注原英语。')+f'<div class="action-row"><a class="primary" href="response.html">从老师答疑开始 →</a><a class="secondary" href="exam-items.html">进入 39 组例题</a></div><div class="review-stats"><div><b>{sum(d["page_count"] for d in lectures.values())}</b><span>中英对照课件页</span></div><div><b>176</b><span>新增答疑页</span></div><div><b>39</b><span>带出处的例题组</span></div></div><section class="editorial-note"><b>这版如何阅读</b><p>每一页讲义均采用「左图右文」中英对照（可一键切换上下大图 / 仅看中文 / 仅看原图）：左侧完整保留老师的 PPT 原图与排版（点击可放大 180%），右侧为忠实中文对照，凡涉及研究方法课与统计学的词汇均已<mark class="rm-term"><strong>加粗高亮</strong><span class="rm-en">（并括号标注原英语）</span></mark>。</p><p>错项按定义错误、推理错误、不完整、答非所问或题设依据不足解释。不因为一个术语陌生，就断言老师没教过。</p></section><div class="section-heading"><h2>老师明确列出的六组重点</h2>{refs([("L12",31),("L12",32)])}</div><div class="topic-grid">'+topic_cards+'</div><section><h2>全站中英文检索</h2><label for="q">搜索课件中英文内容、术语或例题</label><input id="q" type="search" placeholder="例如 mediation / 混淆变量 / Type I / 所罗门" autocomplete="off"><div id="qres"></div></section><section><h2>全部课件 · 逐页中英对照阅读</h2><p class="note">现有材料是 PPT 的 PDF 导出版；页码按 PDF 实际页序标记，避免沿用答疑中个别错误的页脚。L06 未提供课件。</p><div class="lecture-grid">'+cards+'</div></section>')
    g['build_index']=index
    def glossary():
        rows=[]
        for k,t in sorted(g['TERMS_JS'].items(),key=lambda x:x[0].lower()):
            status='仅有出现，未抽取到独立定义；请看原页上下文。' if t['status']=='occurrence_only' else '既有定义摘录与中文翻译；以原课件上下文为准。'
            rows.append(f'<article class="gitem" id="t-{E(k)}"><h2>{E(k)}</h2><h3>{E(t["zh"])}</h3><p class="note">{status}</p><p>{clean(t["en"])}</p><p>{clean(t["zhdef"])}</p>{refs([(t["lecture"],t["slide"])])}</article>')
        return frame('概念索引',0,'glossary.html',header('概念索引',f'{len(rows)} 个概念 · 连接原课件','英文摘录与既有中文翻译供辅助理解；点击来源可检查图表、公式和定义的完整上下文。')+''.join(rows))
    g['build_glossary']=glossary
    search=[]
    for lid,d in lectures.items():
        lec_zh = zh_slides.get(lid, {})
        for p in d['pages']:
            en_t = re.sub('[\ue000-\uf8ff]','',p['text_norm'])
            zh_t = strip_zh_plain(lec_zh.get(str(p['slide']), ''))
            search.append(dict(k='slide',lid=lid,s=p['slide'],t=(en_t + (' | ' + zh_t if zh_t else ''))[:520],f=d['source_file']))
    for k,t in g['TERMS_JS'].items():search.append(dict(k='term',lid=t['lecture'],s=t['slide'],key=k,t=k+' '+t['zh'],f=t['file']))
    for i in items:search.append(dict(k='exam',lid=i['lecture'],s=i['question_slide'],id=i['id'],t=i['id']+' '+i['question_text_norm'],f=i['source_file']))
    (root/'assets/js/search_index.js').write_text('window.SD5979_SEARCH = '+json.dumps(search,ensure_ascii=False)+';\n',encoding='utf-8')
    response=header('RESPONSE / 19 NOV 2026','老师答疑，连接到每个考点。','六组重点来自第 31–32 页；以下中文均为依据课件整理，可点击来源核对原话。')+'<div class="topic-grid">'+topic_cards+'</div>'
    corrections=[('节点不只 bias 不同','每条连接有自己的 weight，每个节点有自己的 bias；训练时两者都调整。',[15,17]),('Mediated moderation 的原图有问题','老师承认学生图更好；原图是视觉比喻。回归表达为 X × W → M，再由 M → Y，同时考虑 X 对 Y 的控制主效应。',[19,20]),('Solomon 的比较要照原话区分','老师保留 G1after 与 G3after 的比较，说明 G3after / G4after 都无前测，不能知道前测效应。不要将此段与第 106 页“首次测量用于信度”混成同一问题。',[28,106]),('哪些是旁支？哪些明确超出范围？','CCI、DIC、unrestricted regression coefficients 在第 164 页明确称为 asides；第 85 页对梯度为何不断缩小的进一步数学解释明确说不属于本课。其余细节不据此自动判为不考。',[85,164,165,166,167]),('开放题怎样获得分数？','老师要求简短、精确。堆砌略有关联的内容、让老师自己挑答案，不算真正作答。猫狗题示例逐小问只回答所问。',[168,169,170,171,172]),('选择题为什么两个答案看着都对？','老师要求选择最精确、最完整的一项；区分完全对、不完整、方向反了或周边概念、拼凑术语。',[64])]
    response+='<section><h2>修正、边界与答题要求</h2><div class="answer-units">'+''.join(f'<section><h3>{E(t)}</h3><p>{E(a)}</p>{refs([("L12",s) for s in ss])}</section>' for t,a,ss in corrections)+'</div></section><section><h2>老师讲清楚的公式与路径</h2><div class="formula-grid"><section><h3>配对 t-test</h3><div class="formula"><math display="block"><mi>t</mi><mo>=</mo><mfrac><mrow><mover><mi>d</mi><mo>¯</mo></mover><mo>−</mo><mn>0</mn></mrow><mfrac><msub><mi>s</mi><mi>d</mi></msub><msqrt><mi>n</mi></msqrt></mfrac></mfrac></math></div><p>先算每对差值，再算差值均值与标准差，最后与“无差异 = 0”比较。符号重排自老师公式。</p>'+refs([('L12',118),('L12',119),('L12',120)])+'</section><section><h3>Mediated moderation</h3><div class="path"><span>X × W</span><b>→</b><span>M</span><b>→</b><span>Y</span></div><p>交互作用经中介传递。此简图对应老师修正后的文字，不保留“箭头指向箭头”的歧义。</p>'+refs([('L12',19),('L12',20),('L12',76)])+'</section><section><h3>相对下降 vs 绝对下降</h3><div class="path"><span>10%</span><b>→</b><span>5%</span></div><p>相对风险下降 50%；绝对下降 5 个百分点。分母与基准必须讲清。</p>'+refs([('L12',45),('L12',46)])+'</section></div></section><section><h2>完整答疑与考试说明</h2><p>176 页全部纳入原课件浏览。考试说明是该课件记载的信息，请对照学校后续通知。</p><div class="action-row"><a class="primary" href="lectures/L12.html">阅读 176 页答疑 →</a><a class="secondary" href="exam/L12-exam.html">新增 9 组例题</a></div>'+refs([('L12',173),('L12',174),('L12',175)])+'</section>'
    (root/'response.html').write_text(frame('老师答疑与重点',0,'response.html',response),encoding='utf-8')
    if not g.get('CHECK'):
        from build_mobile import build_mobile_site
        ml, me = build_mobile_site(dict(
            root=root, lectures=lectures, items=items, terms_js=g['TERMS_JS'],
            zh_slides=zh_slides, zh_exam=g['zh_exam'], mc=MC, oq=OQ, extra=EXTRA,
            topics=TOPICS, audit=audit, markup=g['markup'],
            render_zh_slide=render_zh_slide, clean=clean,
        ))
        print(f'BUILT mobile edition: index / response / exam-items / glossary / {ml} lectures / {me} exam pages')
