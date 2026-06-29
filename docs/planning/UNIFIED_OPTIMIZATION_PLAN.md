# 统一优化总方案 — aaron-marketing-skills

> **状态:LIVE — 单一活路线图(single source of truth)。** 执行以此为准。同目录 `docs/planning/` 下另三份均为归档:`OSS_BENCHMARK_PLAN.md`(支撑分析·superseded)、`ARCHITECTURE_PLAN.md`(支撑分析·superseded)、`OPTIMIZATION_PLAN.md`(已完成基线·done)。索引见 [README.md](README.md)。

> **这是什么**:把三份方案合并为**一份按依赖排序、可增量执行、对抗式核验过**的优化路线图。
> - [OSS_BENCHMARK_PLAN.md](OSS_BENCHMARK_PLAN.md) —— 三大竞品仓借鉴(*加什么*:能力/内容/质量严谨度)
> - [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) —— 平台架构(*怎么搭*:系统级平台层 vs 学科层)
> - [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md) —— 内部质量债(**已执行,作为已完成基线,不再重做**)
> **方法**:6 主题并行对齐(Reconcile)→ 按依赖合成波次(Sequence)→ 对抗式压测(Verify=`sound-with-fixes`,订正已并入)。
> **基线**:v10.0.1 · 38 skills(SEO/GEO 20 + 影响者 18)+ 5 commands。
> **硬约束(任何条目不得违反)**:skills 是 Markdown;唯一允许的代码 = bash 校验器 + **零依赖 Python-stdlib** 连接器(无 pip/第三方);每个连接器类目保留免费/keyless Tier-1 回退;外科手术式最小 diff。
> **日期**:2026-06-29 · 状态:规划稿。

---

## 0. TL;DR

**北极星**:把本仓从"两个半融合学科 bolt 在 SEO 地基上"变成**真正学科中立的平台**——一层薄的 Markdown/SSOT 平台层(门协议 / 记忆-状态模型 / 连接器注册表 / 构建-CI 脊柱)托住薄的学科层,并配上**回归保护的质量层**(eval 结构 lint + slop 屏 + C³ 数学守护),让**廉价的纯 Markdown 能力补丁**与(决策门控的)**新学科**都能安全落地。**护城河不动**:Markdown-first、零依赖、keyless Tier-1、外科手术文化。

**七波路线图(按依赖,不按文档):**

| 波 | 主题 | 重点 | 量级 |
|----|------|------|------|
| **0** | 产品/治理决策(无码) | 7 个决策拍板并写入文档之记录 | XS |
| **1** | 平台缝 | 让共享协议停止假装 SEO 专属(门协议纳 C³、记忆去 SEO 化、连接器加 discipline 标签、UA 改名) | S–M |
| **2** | 质量/eval/数学守护 | eval 结构 lint(**非 runner**)、C³ 数值算例+golden-math 守护、PII 哨兵、**依赖防 creep CI 守卫** | M |
| **3** | 纯 Markdown 能力补丁(批 A) | 共享 humanizer-slop、AI 被引因子扩 9 引擎、schema 假阳性修、平台 playbook、各技能小补丁 | M(量大但每个小) |
| **4** | 闭环度量 + 审计改进环 + 影响者方法升级 | 扩 measurement-protocol、审计递归环(限 1 个技能)、outreach 人物面板、UGC 原子提取 | M–L |
| **5** | 新 SEO/GEO 子技能 + 影响者门接入 + 路由 | 6 个新技能(各带 eval fixture)、content-reviewer 入 Artifact Gate(决策门控)、影响者路由场景 | L |
| **6** | **第三学科:付费广告 Paid Ads(已定)** + discipline-contract | 写 discipline-contract → 建 **ROAS** 框架 + 4 技能 + own-data keyless 连接器;**CRO/留存降为 DEFER** | L |

**10 个 Quick Win(最便宜、零冲突、可立刻起步——多为纯 Markdown):**
1. `_http.py:26` UA 改 `aaron-marketing-skills-connector/1.0`(中性核最后一个 SEO 残留字符串)
2. auditor-runbook 加 C³/ART veto 行 + Changelog 记 cap 对账(**先做 cap 对账**)——解锁整个门协议
3. memory-management 去 SEO 化措辞(name/version 字节稳定)
4. CONNECTORS.md 加 Discipline 标签列 + 每类目"Agent 推荐"行(**注:表已统一,见 §4-A,非重建**)
5. 给 schema/technical 审计器加"JS 注入 JSON-LD 假阳性"警告(很可能是我们自己审计器的真 bug)
6. `ai-citation-patterns.md` 从 4 引擎扩到 9 引擎(扩现有文件,补强我们最强 GEO 资产)
7. content-refresher + alert-manager 加"流量跌 >30% 触发刷新"数值阈值
8. 写**一份**共享 `references/humanizer-slop.md`,被 4 个内容技能引用(最高杠杆纯 Markdown 借鉴,双学科共用)
9. c3-benchmark.md 加数值 CVI 算例(对每个 C³ 技能都有用,且是 golden-math 守护的前置 fixture)
10. 建共享 `references/platforms/*.md`(影响者+SEO/GEO 分发双用,也缓解影响者技能臃肿)

**头号冲突已解(eval)**:OSS 要"eval 回归网" vs 架构"不要 eval runner"——**调和为**:做一个**纯 stdlib 结构 lint 检查器 + 存在性滚动**(进 CI、fail-closed,**永不调模型/不执行技能**);输出打分层保留为**手动/opt-in,不进 CI**。拒绝自动 runner。

---

## 1. 已完成基线(不要重做)

> 对抗复核明确点名:以下已由 OPTIMIZATION_PLAN(已执行)或本轮完成,**不得当新缺口再提**:

- hook `hb()` 解析修复;CI 已覆盖**全部 12 个相位目录**(P0-2,所以"auto-discovery"只是维护气味清理、**非覆盖缺口**,低优先);
- `skill-contract.md` 已写"38 skills";C³ 已按 route-C 接线 fit-scorer/content-reviewer/roi-calculator;
- 18 个影响者 `evals/<skill>/cases.md` **已存在**(P2-3);P3-9 已提出非致命 eval-presence warn;P3-7 bug-report.yml(仅需 verify);
- **CONNECTORS.md 已统一**:已有"Tool Categories"段 + "Influencer / IMPACT categories"子段 + keyless/own-data 右列,`~~influencer database`/`~~social platform analytics`/`~~ad platform` 已标 manual-export(P2-1);
- 8 文件追踪清单 + 两份 marketplace.json 字节一致 CI 校验(`validate-skill.yml:91`);
- **本轮已完成**:`validate-skill.sh:68` 加 `reference-oss/` 排除。

---

## 2. 七波路线图(已并入对抗订正)

### 波 0 — 产品/治理决策(无码,XS)
**目标**:把"做错了贵、写下来便宜"的不可逆/治理问题先拍板并记录,避免下游反复。
- **cap 阈值**:把 C³ ≤59 记为 runbook ≤60 cap 的"band 对齐形式",**显式写进 auditor-runbook §Changelog**(已核验 c3 Low 段 40-59、veto-cap ≤59 与 runbook cap-to-60 表本就对齐 → **零裁决漂移**;仅需记录,不改任何数字)。**此项必须先于波 1 的 C³ runbook 措辞。**
- **eval 冲突**:书面拒绝自动 runner;只采纳 stdlib 结构 lint + 存在性滚动;输出打分手动/opt-in。写进 CONTRIBUTING + evals/README 作定论。
- **路线图之记录**:定本文件为单一活路线图;OPTIMIZATION_PLAN 标 DONE/基线;OSS_BENCHMARK_PLAN + ARCHITECTURE_PLAN 计划归档到 `docs/planning/`(加"superseded by UNIFIED_OPTIMIZATION_PLAN"头);定 commit-vs-gitignore。
- **第三学科已定 = 付费广告 Paid Ads**(用户拍板;**CRO 与留存降为 DEFER**)。作为**独立顶层学科**:自带 ROAS 质量框架、own-data 手动导出 keyless 连接器、命令入口、`memory/paid-ads/` 分区。波 0 只记录决策 + "keyless 兼容"定调(广告数据按自有账户手动导出作 Tier-1,keyed API 仅可选 Tier-2/3 MCP),先不建。
- **预记录**三个产品决策的取向(content-reviewer 是否产 gated 产物 / 写路径 / `/impact` 命令),让后续波知道范围。

### 波 1 — 平台缝(纯文档 + 一个字符串,S–M)
**目标**:让共享 SSOT 停止假装 SEO 专属。
**理由**:门协议与记忆模型~80% 已共享、只是措辞 SEO;这是最便宜、最低风险的提升,且是后续一切能力/学科的前置。C³ 是验证"veto→cap 插件模式可泛化"的彩排。
- auditor-runbook §5 加一行 C³/ART veto-set(ACE A2/C1/E2;ART T1/T2),与 CORE-EEAT、CITE 并列(行**非字节相同**;**不改名 runbook、不改 `class:` 标识符**)。
- memory-management 去 SEO 化措辞(:17/:124/:137-156)→"营销记忆"+ 加影响者查找路径;**name/metadata.version 字节稳定**(避免 validator SPLIT + 8 文件连锁)。
- **CONNECTORS.md 加 Discipline 列(search/influencer/both)+ 每类目一行"Agent 推荐"**(默认选谁+何时换),保留 keyless Tier-1。⚠ **已统一,非重建**(§4-A);`ledger.py`/`rss_monitor.py` 改标 both(无代码)。
- `_http.py:26` UA 改名(cosmetic,changelog;**零依赖项,可搭任何 PR**)。
**退出**:runbook 列三套 veto;memory 无 SEO 措辞且版本不变;CONNECTORS 有 Discipline 列;UA 中性;`--status` 仍全 OK 无 SPLIT。

### 波 2 — 质量/eval/数学守护(M)
**目标**:给语料正确的回归保护——结构 lint(**非 runner**)、C³ 算例+golden-math 守护、PII 哨兵、依赖防 creep 守卫。
- c3-benchmark.md 加数值 `CVI=(ACE×ART×ROI)^(1/3)` 算例(**硬前置**;CI 顺序:算例 commit 先于断言 commit)。
- golden-auditor-math.py 加 C³ CVI 断言块,用**写死的期望输入/输出向量**(不动态解析 Markdown 表);CORE-EEAT/CITE 守护保持。golden-math 的两个 SEO 审计路径**保持内联**(不为它建 disciplines.md)。
- 新 `scripts/check-evals.py`(stdlib)**仅结构 lint**:每个 cases.md 可解析、必填键齐、target_skill 真实存在、无掉队技能;+ `evals/eval-baseline.json`(**只存结构事实:技能清单/必填键存在,绝不存输出分**)。**永不调模型/不执行技能。**
- CI 只接 check-evals 的**结构 lint 那半**(fail-closed)+ 非致命 per-discipline eval-presence 滚动;**输出打分不进 CI**。
- **【新增·对抗补】依赖防 creep CI 守卫**:一条 grep,扫 `scripts/` 任何 .py 只 import stdlib(denylist:numpy/pandas/scipy/sklearn/requests/whisper/mediapipe/cv2),fail-closed。**比 tracking-verifier 更便宜,直接守护护城河**——尤其防 trend-scout/dossier/atom-extraction 这几个重依赖来源的 dep creep。
- `scripts/check-pii.py`(stdlib regex:邮箱/key/token)+ CI 步 + 可选本地 pre-commit;**丢弃 CTA-block/归因强制、丢弃 telemetry**;加 example.com/555 allowlist。
- **【对抗订正·降级】**追踪同步:**不**新建 count/version 解析脚本(过度设计,单消费者)。已有 marketplace 字节校验(`:91`)+ PR-checklist 行即可;最多给现有 diff 加 1-2 条 grep 断言。
- CI find-loop auto-discovery(排除 docs/.claude/reference-oss/evals)= **低优先维护清理**(覆盖本就全,P0-2);先确认 disciplines.md 消费者 <2 → **默认不建**。
- PR/issue 模板:加"8 文件追踪同步""无新 pip/第三方依赖""每个新 `~~category` 有 Tier-1 keyless 回退"三条 checklist;verify P3-7 bug-report.yml 已发。
**退出**:三框架数学全有 golden 守护;check-evals 结构 lint fail-closed;依赖守卫 fail-closed;PII 守卫上线;disciplines.md 确认不建。

### 波 3 — 纯 Markdown 能力补丁(批 A,M;每个小,可 2–3 个批 PR)
**目标**:落地零依赖、零冲突、零回归风险的 Markdown 借鉴,补强现有 SEO/GEO 与影响者技能。无新技能、无新机器。
- **写一份共享 `references/humanizer-slop.md`**(24 条 AI-slop 模式 + ~55 词禁用表 + 每条扣分 + 前后改写;并入 coreyhaines ai-writing-detection 启发式)。被 seo-content-writer / geo-content-optimizer / content-quality-auditor(映射 CORE-EEAT Experience,**先做软惩罚**)/ content-reviewer(映射 ART 质量维,**非 veto**——ART veto 留给 T1/T2)**引用,不内联复制**。⚠ **【新增·对抗补】与现有 skill-contract Output Voice 禁用词表去重**,避免两份分叉 banlist。
- `geo-content-optimizer/references/ai-citation-patterns.md` 从 4 引擎扩到 9(加 Copilot/Gemini/Grok/Brave/Bing + 引用来源逻辑);被 content-quality-auditor 引用。
- schema-markup-generator + technical-seo-checker + on-page-seo-auditor 加"JS 注入 JSON-LD 假阳性"警告(用 rendered DOM/Rich Results Test 再报"无 schema")。
- 加 `references/llms-txt-okf.md`(分层 sitemap→robots→llms.txt→/pricing.md→/okf/→schema,诚实标"协议层注册、当前无排名信号");被 geo-content-optimizer/entity-optimizer/schema-markup-generator 引用。
- keyword-research 加 Impact×Confidence + BOFU/MOFU/TOFU 漏斗打分(叠加现有 striking-distance,不重做)。
- technical-seo-checker 加 SSR/SSG/CSR 渲染 note + CWV 阈值(LCP<2.5s/INP<200ms/CLS<0.1)+ 抓取预算清单 + hreflang/国际化 reference(不重做现有 AI-bot allowlist)。
- serp-analysis + competitor-analysis 加 YouTube-outlier + 标题包装方法;geo-content-optimizer 加 `grokipedia-tactics.md`(隐形 Suggest 战术 + 可粘贴模板)+ `medium-github-surfaces.md`(**不建独立薄技能**)。
- internal-linking-optimizer 加 Mermaid 站点图模板(孤儿/孤岛检测)。
- **建共享 `references/platforms/*.md`**(X/LinkedIn/TikTok/YouTube/Reddit + Grokipedia,各~1 页:算法/格式/排名/披露);被 influencer-discovery/content-reviewer/content-amplifier/ugc-repurposer/outreach-manager **及** geo-content-optimizer 引用(双用 + 缓解影响者臃肿)。
- brief-generator 的 Tone&Style 扩成创始人/创作者声音 intake 块;content-reviewer 读取已捕捉声音。
- campaign-planner 加"影响者 vs 联盟 vs 创作者"决策表 + nano/micro/mid/macro 分层 +"互动率>粉丝数"(被 fit-scorer/budget-optimizer 引用;只取表/分层,不取 kostja94 的浅评分)。
- 加 `references/scoring-rubrics/{conversion-quality,visual-quality}.md` 作**顾问 reference**(→ landing-optimizer / content-quality-auditor;**非新审计技能、非为 CRO 预建**)。
- **【对抗订正·合并】**人物评分面板:把 expert-panel 方法**合成一份** `references/expert-panel.md`(具名人物镜头、迭代到目标、每轮投票表),被 content-reviewer **和** outreach-manager 共同引用(**不写三份近重复文档**)。
**退出**:humanizer-slop 一份并被 4 技能引用;9 引擎被引因子;schema 假阳性警告在 3 审计器;platforms/* 与各小补丁落地;check-evals 仍绿。

### 波 4 — 闭环度量 + 审计改进环 + 影响者方法升级(M–L)
**目标**:加度量严谨层、限域递归改进、outreach 人物面板、UGC 原子提取、(stdlib)创作者 dossier。
- **扩**现有 `references/measurement-protocol.md`(**不新建 closed-loop.md**——⚠ OSS 源说"create closed-loop.md",但我们已有 measurement-protocol.md,执行波须读"EXTEND"):readback 窗口(7/14/28/56 天)、必填字段、promote/keep-testing/rollback/unproven 规则、不可升级清单、显著性门**仅作文档方法**(bootstrap CI + Mann-Whitney U,p<0.05 且 ≥15% lift;**无 scipy/代码**);插入 performance-reporter/performance-analyzer/roi-calculator/content-refresher/alert-manager。
- content-quality-auditor 加**限域**递归打磨环(≤3 轮、**永不覆盖 veto**)。**【对抗订正】学习型拒绝记忆默认 DEFER**(今天无拒绝语料 = 同 creator-entity 的错误抽象);若做,**仅项目本地 memory、有上限,不写 committed 文件**。
- outreach-manager 加多人物递归评审面板(≤3 轮、每轮投票表,**复用波 3 的 expert-panel.md**)+ 冷邮硬规则(首句禁词、Step1 ≤3 句、软 CTA、Step1 不放链接)。
- ugc-repurposer 加 7 级内容原子提取 + 病毒启发式 + Jaccard ~0.70 近重复 flag(批内 + 对近 30 天)**仅作 Markdown 方法**(**不移植 whisper/mediapipe/pandas**)。
- trend-spotter/content-gap-analysis 加多源 keyless trend-scout 配方(Google Trends RSS + HN + Reddit + YouTube-outlier),**用现有 stdlib `rss_monitor.py` 实现**(无新依赖)。
- **【对抗订正·默认 method-only】**创作者 dossier:**默认作 method-only Markdown**(HTMLParser 首页解析 + 缺口检测 + 3-5 句 brief);**不为单个薄 helper 建 `scripts/connectors/influencer/` 子目录**;仅当真有 load-bearing stdlib helper 落地才建(架构的明确触发条件)。

### 波 5 — 新 SEO/GEO 子技能 + 影响者门接入 + 路由(L)
**目标**:在平台缝 + eval-lint 网就位后,补真正缺的 SEO/GEO 技能单元;(决策门控)把 content-reviewer 接入运行时 Artifact Gate;播种影响者路由。
**规则**:每个新技能**合并前先有手动 `evals/<skill>/cases.md`**(波 2 的 lint 网保证无掉队/损坏);validator 本就自动校验相位目录里任何 SKILL.md,SEO 技能无需 infra 改动。**【对抗补】每个加技能 PR 必须同步 8 文件 + 两份 marketplace 镜像(HARD 合并要求)。**
- 新技能:`build/programmatic-seo`(12 打法 + 5 级数据可防御 + N-gram 薄页去重)、`optimize/site-architecture`(全站 IA + Mermaid)、`local-seo`(GBP/NAP/引用优先级;`~~local-listings` 标 Tier-1 手动)、`build/parasite-seo`(平台分层 + 站点声誉滥用规避)、`build/comparison-page-builder`(vs/alternative 页;**命名避开** analytical competitor-analysis)、`monitor/ai-traffic`(GA4/GSC 追 AI 流量,复用现有 keyless own-data 配方)。每个**先落 cases.md**。
- **【决策门控】content-reviewer 入门**:若决定产持久 gated 产物 → 它读 auditor-runbook、发 `class:` 标记;hook **加 additive、fail-open 的第二套 C³ 字段 schema** 或让 content-reviewer 写完整 handoff schema 到 `memory/audits/influencer/`;给 `tests/test_hook_artifact_gate.sh` 加影响者 fixture。若否 → 保持对话内,slop 屏维持顾问性。
- **影响者路由**:**先**在 auto-routing-scenarios.md 播种真实影响者场景;**仅在场景存在后**才考虑 `/impact` 命令——**而命令的前置是改写 `aaron-product-api-contract.md` 的"declines non-SEO/GEO"边界行**(场景的前置不是它,**别在 auto 仍拒 IMPACT 时加 /impact**)。

### 波 6 — 第三学科:付费广告 Paid Ads(已定)+ discipline-contract(L)
**目标**:把付费广告作为**独立顶层第三学科**落地——先写 discipline-contract 文档,再按 6 缝建 **ROAS** 质量框架 + 精简 4 技能 + own-data keyless 连接器。**CRO/留存降为 DEFER**。
**keyless 定调(红线第一)**:付费广告全部从**自有账户手动导出**的数据运行(原生广告后台 CSV/截图/粘贴),与 GSC/GA4 own-data 同理;keyed 广告 API(google-ads SDK / Meta Marketing API)**仅可选 Tier-2/3 MCP,永不作 Tier-1 前置**。这是本学科最高红线漂移风险 → 见下方 lint 守卫。
**理由**:用户拍板;付费广告是真正净新增的获客学科(SEO/影响者均不覆盖),且与现有"流量+落地页+ROI"工作协同强(复用 roi-calculator/budget-optimizer/landing-optimizer)。

**ROAS 质量框架(CORE-EEAT/CITE/C³ 的对等物;首字母正好拼出付费广告的北极星指标 ROAS,R 即字面的 Return)**:
- 4 个目标加权维度 = 付费的四个杠杆:**R**eturn(回报:ROAS/CPA vs 目标、盈利性 + **衡量信号完整性**:追踪/归因/UTM-离线导入/iOS-ATT)· **O**ffer(广告/创意:创意质量与 hook、广告↔落地页 message-match、Quality Score 相关性杠杆、格式适配 + 合规)· **A**udience(受众/账户:定向、匹配类型、活动类型 Search/PMax/broad、账户结构、否定词/排除)· **S**pend-efficiency(花费效率:CPC/CPM/CTR/CVR vs benchmark、预算节奏/分配、学习期尊重、付费↔自然蚕食)。助记:**谁看(A)→ 看什么(O)→ 花多少(S)→ 回多少(R)**。
- **方法论流程(ROAS 闭环,与维度共享助记)**:**R**esearch(研究受众/关键词/offer)→ **O**rchestrate(搭账户结构+创意)→ **A**ctivate(上线:QA/追踪/合规门)→ **S**cale(衡量→优化出价预算→扩量赢家/砍输家)→ 回到 R。相位目录保持功能命名(build/launch/scale),ROAS 闭环作教学叙事,不强行改目录名以免与"评分维度"的 ROAS 混淆。
- Rollup = **RQS(ROAS Quality Score 0–100)= floor(weighted({R,O,A,S}, 目标权重))** —— **算术加权平均(同 CITE),非 C³ 几何 CVI**;复用 `golden-auditor-math.py` 现有 `weighted()/floor()` helper,**不引入新数学**。⚠ RQS(0–100 质量分)≠ 字面 roas 倍数(后者只是 Return 维的一个输入)。
- 目标权重双列:DR/绩效 `R0.40 O0.20 A0.15 S0.25`、拉新/品宣 `R0.15 O0.30 A0.30 S0.25`,两列各 sum=1.0。
- veto(**钉死一套稳定 ID,5 条,按维度对称归位 R:2 / O:2 / A:1**):**R1**=转化追踪损坏/不可验证(无数据=veto;**iOS/ATT 建模/部分=Partial/flag,不自动 veto**,否则现代账户几乎必触)· **R2**=跨平台归因重复计数/虚高(按订单 ID/时间戳跨两份粘贴 CSV 对账作 **LLM 读表,非 pandas join**,并校正不同归因窗口)· **O1**=广告宣称真实性/必需披露(claim integrity,虚假/无据宣称、缺法定披露)· **O2**=平台政策合规(违禁品类/商标滥用/受限行业 → 拒登或账户风险;与 O1 证据与补救不同,故拆开)· **A1**=品牌/版位安全(需版位报告导出)。**"过早扩量/学习期违规"降级为 S 维下高严重度 guardrail/flag,非 veto**(流程错误,不使分数不可信)。注:5 条单 veto cap-to-60、**2+ 同时硬失败 → BLOCKED 是正确行为**(追踪坏+政策违规的账户本就不该投),非过严——iOS/ATT 已软化 R1 降低误触。
- cap:完全复用 `auditor-runbook §2`(单 veto cap-to-60;2+ veto → BLOCKED 不出 final),**无新 cap 机器**。
- golden-math 算例:`R=75 O=80 A=85 S=78`,DR 权重 → 30+16+12.75+19.5=78.25 → floor 78;veto 分支(R1 触发)→ min(78,60)=60。**断言两列权重各 sum=1.0、断言算例输入向量字符串出现在审计器本体、断言 2+veto BLOCKED 不出 final**。QS 5→7 ≈ −30~50% CPC 仅作**有标注的估算区间**(kostja94),不作框架计算分。

**技能集(精简 4 个,新相位目录;复用而非重复)**:
- `paid/build · campaign-architect` —— 账户/活动结构、活动类型选择(Search/PMax/broad)、定向、否定词/排除卫生、**付费↔自然蚕食审计**(kostja94);评 A/结构;**budget-optimizer 为分配 SSOT**。
- `paid/build · ad-creative-builder` —— 批量 RSA/创意变体 + 与落地页 message-match(coreyhaines 批量迭代打法,纯 Markdown)。
- `paid/launch · ad-account-auditor` —— **auditor-class 门**(`class: auditor-output`,Read auditor-runbook),按 ROAS/RQS 打分、强制 R1/R2/O1/O2/A1 veto、读 QS 相关性杠杆;O 维的广告↔落地页 message-match **只评消息匹配**,LP 内部质量委托 landing-optimizer(避免同页两套 rubric 打架)。付费学科的发布就绪门。
- `paid/scale · paid-measurement-loop` —— ROAS/CPA readback,**复用 measurement-protocol.md + ledger.py + roi-calculator**;与 performance-analyzer 划清快照/diff 边界;输出走 report-generator。

**连接器(全部 own-data keyless Tier-1;对抗订正后)**:
- `~~ad platform`(已在 CONNECTORS.md,标 own-data 手动导出)→ **明列各 veto/维度所需的原生导出列契约**(搜索词报告列、版位报告列等)。
- `~~conversion tracking / analytics` → GA4 own-data 导出(S1/S2 据此评);跨平台去重从**两份手动粘贴的 per-platform 导出**按订单 ID/时间戳对账。
- 落地页 → 复用现有零依赖 `_http.py/onpage.py` 抓取 + 粘贴回退(R 维)。
- **丢弃 `~~creative asset library(DAM)`**(无 Tier-1 消费步骤,"粘贴你的创意"即可);**广告政策/合规改为 `references/` 包**喂 R1,**非连接器类目**(它只是文档、无导出路径)。

**discipline-contract 与落地(6 缝)**:
- 写 `references/discipline-contract.md` 为 **6 缝 Markdown 清单**(相位目录;rubric 插 auditor-runbook + golden-math 数值算例;`memory/paid-ads/<skill>/` 进 state-model WARM;连接器 `~~category` 带 keyless Tier-1 或 manual-export;命令入口;eval 集)——**非 loader/非重组/非 disciplines.md**;兼作两现有学科 onboarding SSOT;**保持"描述现有学科",不为付费广告预建投机字段**。
- 前置:确认波 1+2 缝已落(C³ 为可用第三框架 = 第 4 框架 ROAS 插入前的彩排、记忆/连接器中性、golden-math 守三框架)。
- **红线漂移 lint(必做)**:validator 新增一条——**任何 paid-ads SKILL.md 本体把广告平台 API 措辞成"必需/Tier-1"即 fail**(authoring 期最高红线风险);并入波 2 的"依赖防 creep"守卫。
- 每个付费技能建时即写手动 `cases.md`,**含 NEEDS_INPUT(缺导出)与 多-veto BLOCKED 两个非 happy-path 用例**。
- 命令入口 = **专属 `/aaron-marketing:paid`**(与"每学科一命令"模式一致,保 auto 的 SEO/GEO 契约不动)——**按路由缝推迟**:先在 auto-routing-scenarios.md 播种付费场景后才加;"改写 api-contract 边界 + 让 auto 跨学科分类"是**更后、单独**的可选项,非本期。
- 更新 CONTRIBUTING/CLAUDE/AGENTS 文档化新平台协议(runbook 为**四框架**门 SSOT、统一连接器注册表、闭环)+ 技能/命令计数写进 8 文件追踪;CONTRIBUTING §6 仍是唯一权威追踪清单。
- 未映射的 kostja94 项归位:付费↔自然蚕食 → S 子项;PMax/学习期违规 → guardrail/flag;版位安全 → A1 需版位报告导出。
- **留存/生命周期、以及付费广告之外的 pricing/launch/AARRR/ASO** 仍 DEFER,等确认消费者。

---

## 3. 关键依赖

- 波 0 cap 决策 **先于** 波 1 C³ runbook 措辞(否则现有影响者裁决漂移一分)。
- 波 1 C³ runbook 行(便宜的文档半)**先于** 波 5 content-reviewer 门接入(把耦合变成更小的 additive 改动)。
- 波 2 C³ 数值算例 **硬先于** golden-math C³ 断言(算例 commit 先,否则断言空过)。
- 波 2 check-evals 结构 lint **先于** 波 5/6 任何新技能(防能力扩张时 cases.md 静默腐烂)。
- 波 2 依赖防 creep 守卫宜早(波 4 的 trend-scout/dossier/atom-extraction 是 dep creep 最高风险来源)。
- 波 4 measurement-protocol 扩展是任何波 6 学科"报结果"的前置 → 可早做且学科中立。
- 波 6 discipline-contract + 付费广告 ROAS 受波 1/2 缝落地门控(C³ 须为可用第三框架 = 第 4 框架 ROAS 插入前的彩排;golden-math 须先守三框架);付费广告命令受"先播种付费路由场景 + 改写 api-contract 边界"双前置。ROAS 用算术加权(同 CITE)→ golden-math 复用现有 helper,无新解析。
- `/impact` 命令受"先播种场景 + 改写 api-contract 边界"双前置;auto-discovery/disciplines.md 受"消费者 <2"判定门控(默认不建)。

---

## 4. 对抗复核的必修订正(已并入上文,集中列示)

> 复核结论 `sound-with-fixes`。以下订正已写入对应波次:

- **A · CONNECTORS.md 已统一,重 scope**:不是"合并两表"(P2-1 已把它做成"Tool Categories + Influencer/IMPACT 子段 + keyless 列",已核验)。波 1 的真实剩余工作只剩**加 Discipline 标签列 + 每类目 Agent-推荐行**——一个 Quick Win,非表重建。
- **B · eval 调和锁死**:check-evals.py **只做**结构 lint + 存在性滚动,**绝不调模型/不执行技能**;`eval-baseline.json` **只存结构事实,不存输出分**(否则 baseline 悄悄变成被拒 runner 的状态文件);输出打分层 opt-in/非 CI;在 CONTRIBUTING/evals/README 写一行"禁止 scope creep"。
- **C · 砍/降级 tracking-sync 脚本**:别建跨文件 count/version 解析器(单消费者过度设计);用现有 marketplace 字节校验 + PR-checklist 行 + 至多 1-2 条 grep。
- **D · 学习型拒绝记忆默认 DEFER**:波 4 只发限域递归环(≤3 轮、不覆盖 veto);拒绝记忆无语料 = 错误抽象,若做则项目本地、有上限。
- **E · dossier 默认 method-only**:不为单薄 helper 建 influencer/ 子目录。
- **F · 人物面板合并一份**:expert-panel.md + 多人物面板 + scoring-rubrics 三处同源,合成一份 reference 被两技能引用。
- **G · 新增三条遗漏守卫**:① 依赖防 creep CI grep(波 2,**最高性价比护城河守卫**);② humanizer banlist 与现有 Output Voice 禁用词去重(波 3);③ cap 对账对现有影响者 eval cases 做零漂移人工抽查(波 0/1)。
- **H · 诚实 scope**:CI find-loop 已覆盖全 12 目录(P0-2),auto-discovery 是维护气味、低优先非覆盖修;golden-math 两审计路径保持内联,**不宣称"4 处写死全替换"**。
- **I · 硬顺序**:cap 对账 commit 先于 C³ runbook 行;C³ 算例 commit 先于 golden-math 断言;`/impact` 的前置是改 api-contract 边界(非场景)。

---

## 5. 决策(已定 ✅ —— 用户拍板"第三学科 = 付费广告;其余按建议")

| # | 决策 | 已定 |
|---|------|------|
| 1 | eval 形态(头号冲突) | ✅ stdlib 结构 lint + 非致命存在滚动作 CI 门;**输出打分手动/opt-in、不进 CI;拒绝自动 runner**。结构 lint 先发 |
| 2 | cap 阈值对账 | ✅ C³ ≤59 记为 ≤60 的 band 对齐形式(零裁决漂移),显式 changelog |
| 3 | content-reviewer gated 产物 | ✅ **是**——产持久 gated 产物、进 Artifact Gate(影响者侧 slop 屏转为强制 veto);改动 **additive + fail-open** |
| 4 | 影响者门写路径 | ✅ `memory/audits/influencer/`(统一 Gate 路径,更干净) |
| 5 | `/impact` 命令 | ✅ 先播种影响者路由场景,**缓命令**;加命令前先改写 api-contract 的"declines non-SEO/GEO" |
| 6 | **第三学科** | ✅ **付费广告 Paid Ads**(独立顶层学科,ROAS 框架);**CRO 与留存降为 DEFER**;付费广告之外的扩张暂缓 |
| 7 | AI-slop 严重度 | ✅ 软 CORE-EEAT 惩罚(非新硬 veto) |
| 8 | 拒绝记忆持久化 | ✅ 默认 **DEFER**(今天无拒绝语料);若做则项目本地 memory、有上限,不写 committed 文件 |
| 9 | dossier 形态 | ✅ method-only Markdown(不建 `connectors/influencer/` 子目录) |
| 10 | 路线图文档 | ✅ 本文件为单一活路线图;另两份**归档 `docs/planning/` 并提交**(可见治理史)+ 加 superseded 头;OPTIMIZATION_PLAN 标 DONE |
| 11 | ASO / 新技能排序 | ✅ ASO 暂缓(无 app 营销消费者);波 5 顺序照旧 programmatic-seo → site-architecture → local-seo → parasite-seo → comparison-page-builder → ai-traffic |

> **全部决策已定 ✅**。两个落地内细节也已定:① 付费 veto **拆为 O1(宣称真实性)+ O2(平台政策),共 5 条**(R1/R2/O1/O2/A1,对称归位 R:2/O:2/A:1);② 付费命令 = **专属 `/aaron-marketing:paid`(推迟到播种场景后再加),不并入 auto**。

---

## 6. 明确不做(过度设计/越界守则)

- 不建自动 eval **runner**(调模型/执行技能);只许结构 lint + 存在滚动进 CI。
- 不合并三个量表(CORE-EEAT 加权和 / CITE / C³ 几何 CVI)——不同 rollup 是特性;共享流程不共享量表。
- 不把递归改进环泛化到 4 个审计器——只限 content-quality-auditor。
- **付费广告:不把任何 keyed 广告 API(google-ads SDK/Meta Marketing API)作 Tier-1 前置**——仅可选 Tier-2/3 MCP;authoring 期用 validator lint 拦"API 必需"措辞。
- **付费广告:不做按平台拆的广告技能**(Google/Meta/TikTok/LinkedIn 各一个 = kostja94 反模式);平台特性进 `references/` 包,技能保持 4 个跨平台。
- **付费广告:不引入第 5 个维度/技能**;ROAS 用算术加权平均(同 CITE),**不套 C³ 几何 rollup**(会逼新数学解析);**不建 `~~creative asset library(DAM)` 连接器**;广告政策作 references 包、非连接器。
- **CRO/留存现为 DEFER**(被付费广告取代为第三学科);conversion/visual rubric 仍以 reference 形式进、非机器,等 CRO 重新进入范围再用。
- 不建 `disciplines.md`/plugin-loader/连接器框架(消费者太少;内联修 golden-math + CI auto-discovery 后默认不建)。
- 不物理重组成 `disciplines/`+`platform/`(38 路径 diff、宿主行为零变化;等第 3 学科)。
- 不改名 auditor-runbook.md 或 `class: auditor-output`(会连锁 hook + 两审计本体 + golden-math + validator)。
- 不拆 `scripts/connectors` 子目录,除非真有 load-bearing stdlib 影响者 helper 落地。
- 改 memory-management 散文时不 bump name/version(避免 SPLIT + 8 文件连锁)。
- **不加任何新 pip/第三方依赖**(whisper/mediapipe/opencv/scipy/sklearn/pandas/psycopg2)或任何 keyed/付费实时 API;重依赖 OSS 脚本只移植为 Markdown 方法。
- 不借 coreyhaines 64 个付费 CLI / 94 个 integrations 文件——只蒸馏 REGISTRY 决策辅助进 keyless CONNECTORS。
- 不加任何 telemetry/phone-home(丢弃 ericosiu 逐技能上报);未来本地度量须用户自装 hook、无远端端点、单独决策。
- 不借 ericosiu CTA-block/强制厂商 URL 归因——只取 PII 检测半。
- 不加薄长尾完整性技能(medium-posts/pinterest/native-ads/UI card-grid)或越界的财务/HR/B2B 销售/建站技能;Medium/GitHub/Grokipedia 作 geo-content-optimizer references。
- 不建 creator-entity/csv_ingest,除非真有影响者消费者需要持久规范创作者档案(今天无写入者 = 错误抽象)。
- **不重做已完成基线**(§1)。

---

## 7. 主题项索引

六个对齐主题共产出可执行建议项,已全部按 id 编织进上文波次:`quality-eval`(11)· `platform-protocol`(15)· `seo-geo-capability`(20)· `influencer-capability`(11)· `new-disciplines`(9)· `repo-governance`(10)。每条均带 source(oss/arch/internal-done/new)/target/effort/risk/depends_on,详见各波次条目与 §4 订正。

## 8. 文档治理(已执行 ✅,2026-06-29)

- 四份规划文档已统一归档到 **`docs/planning/`**(tracked,区别于 gitignore 的 `docs/plans/` 临时草稿);同目录共置 → 互链零改写。索引见 [README.md](README.md)。
- 本文件 = **单一活路线图 LIVE**(执行以此为准)。
- `OPTIMIZATION_PLAN.md` → **DONE / 基线**(P0–P3 已执行,不再重做)。
- `OSS_BENCHMARK_PLAN.md` + `ARCHITECTURE_PLAN.md` → **SUPERSEDED 支撑分析**(已加 banner;内容已并入本文件,不再单独执行)。
- 已 commit 进版本库作可见治理史(分支 `docs/planning-governance`)。
- `reference-oss/` → 分析已完成,可在确认不再需要原文后 `rm -rf`(已 gitignore;且 validator `--status` 已加排除)。
