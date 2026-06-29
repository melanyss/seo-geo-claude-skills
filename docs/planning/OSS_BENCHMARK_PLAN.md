# OSS 竞品借鉴方案 — 三大 Top Marketing Skills 仓库系统分析

> **状态:SUPERSEDED(支撑分析 · 已并入活路线图)。** 单一活路线图见 [UNIFIED_OPTIMIZATION_PLAN.md](UNIFIED_OPTIMIZATION_PLAN.md);本文件作为三仓竞品借鉴的原始分析存档,不再单独执行。索引见 [README.md](README.md)。

> **目的**:对标三个开源 Top Marketing Skills 仓库,系统梳理「哪些值得借鉴来提升 aaron-marketing-skills」,覆盖(a)强化现有 SEO/GEO 技能、(b)强化现有 influencer 技能、(c)我们尚未涉及、值得新增的营销领域与工程基建。
> **基线**:我们 = v10.0.1 · 38 skills(SEO/GEO 20 + 影响者/IMPACT 18)+ 5 commands;三大框架 CORE-EEAT / CITE / C³(带 veto);零依赖 + Markdown-first + keyless Tier-1 连接器哲学。
> **方法**:三仓各派一个深挖 agent(+子 agent)全文精读 → 带文件路径引证的对比报告 → 本文为四份报告的合并行动方案。
> **日期**:2026-06-29 · **状态**:分析稿,未纳入发布物(`reference-oss/` 已 gitignore)。

---

## 0. TL;DR — 一页结论

**三仓的差异化与我们的定位:**

| 仓库 | 规模 | 它的强项(我们该拿的) | 它的弱项(我们已更强) |
|------|------|----------------------|----------------------|
| **coreyhaines/marketingskills** | 45 技能 + 64 个零依赖 Node CLI | **全漏斗营销广度**(CRO/留存/付费/定价/PR…)、`ai-seo` 逐平台 AI 被引因子、`product-marketing` 基础上下文模式、CI 自动同步追踪文件 | 无任何质量评分/veto、无 handoff 契约、CLI 全是付费 API(违背 keyless) |
| **kostja94/marketing-skills** | 172 个极细技能(纯 Markdown) | **平台专属 playbook**(X/LinkedIn/TikTok/YouTube/Reddit/Grokipedia 算法级)、`parasite-seo`/`programmatic-seo`/`local-seo`、**GEO 的 RAG/爬虫模型** | 无评分/无 veto/无 handoff;172 个细技能有发现/重叠问题;长尾技能偏薄 |
| **ericosiu/ai-marketing-skills** | 22 个重代码 ops 技能(pandas/whisper/sklearn) | **`/eval` 输出回归测试**、**humanizer 24 条 AI-slop 检测**、**closed-loop 闭环度量方法论**、`content-ops` 专家评分面板 + 递归打磨 + 学习型拒绝记忆、PII 哨兵、统计显著性升级门 | 重第三方依赖 + 实时付费 API + 全仓单一 VERSION,直接违背我们零依赖哲学 |

**一句话战略**:**拿它们的「内容(playbook/被引因子)+ 工程严谨度(eval/slop 检测/闭环度量/评分细则)」,坚决不要它们的「重依赖 + 付费 API + 单 app runner」架构。** 我们的护城河(三框架 + veto + handoff 契约 + keyless 连接器 + 记忆温度层)保持不动,把它们的好内容以 references/ 与协议层方式吸收进来。

**最高杠杆的 6 件事(详见 §6 排期):**
1. **humanizer 24 条 AI-slop 检测**(纯 Markdown,直接进 4 个内容技能当 veto)— ericosiu
2. **`ai-seo` 逐平台 AI 被引因子 + AI-bot robots.txt 白名单 + llms.txt/OKF**(进 geo-content-optimizer/technical-seo-checker)— coreyhaines
3. **stdlib 版 `/eval` 输出回归测试网**(补我们最大的缺口:无法回归测试技能编辑是否降质)— ericosiu
4. **closed-loop 闭环度量协议**(readback 窗口 + 升级/回滚规则,作新的 cross-cutting 协议)— ericosiu
5. **平台 playbook 层**(X/LinkedIn/TikTok/YouTube/Reddit/Grokipedia,同时喂养 SEO/GEO 分发 + 18 个 influencer 技能)— kostja94
6. **3 个新 SEO 子技能**:`programmatic-seo` / `site-architecture` / `local-seo`(我们 SEO 侧最明确的空白)— coreyhaines + kostja94

**需你拍板的产品决策(§5)**:是否新增**第三条学科线**(CRO/转化 + 留存/生命周期),把漏斗从「我们止步的流量」延伸到「转化—留存—变现」。这是不可逆的边界扩张,先决策再排期。

---

## 1. 三仓定位与我们的对照

### 1.1 架构哲学对比

| 维度 | coreyhaines | kostja94 | ericosiu | **我们 (aaron)** |
|------|------------|----------|----------|------------------|
| 技能单元 | 45 个中等粒度 | 172 个极细粒度 | 22 个重代码管线 | 38 个,两学科分相 |
| 主产物 | Markdown + 可选 CLI | 纯 Markdown | 可执行脚本 + SKILL 包装 | Markdown(skill 即内容) |
| 共享状态 | 单个 `product-marketing.md` 先读 | 静态 `project-context.md` | `data/*.json` + 本地 JSONL | HOT/WARM/COLD 记忆层 + hot-cache |
| 技能间衔接 | 非正式 `Related Skills` 链接 | 行内 `Related Skills` 散文 | 无统一契约 | **正式 handoff 契约**(目标/证据/分数/状态 token) |
| 质量控制 | 散文清单,**无评分** | **无评分** | 代码评分 + LLM 专家面板 + `/eval` 回归 | **CORE-EEAT/CITE/C³ + veto** |
| 依赖 | 64 个零依赖 Node CLI(但全是**付费 API**) | **零代码** | 重依赖(whisper/sklearn/pandas…) | 零第三方;bash 校验 + Python-stdlib 连接器 |
| 数据接入 | 需 API key | 靠宿主 agent 自带工具 | 实时 keyed API | **`~~category` 占位符 + 免费/keyless 配方** |
| 版本/追踪 | VERSIONS.md + CI 自动同步 | `metadata.version` | 全仓单一 `VERSION=1.0.0` | 每技能 semver + 8 文件追踪契约 |

**结论**:我们在**治理与基础设施**(框架/veto/契约/keyless/记忆)上全面领先;它们在**广度(coreyhaines)、平台深度(kostja94)、输出评测严谨度(ericosiu)**上各有我们缺的东西。借鉴策略=内容/方法搬过来,架构/依赖不要。

### 1.2 我们明显更强、勿动的部分(避免被"借鉴"带偏)

- 三大框架的**数学自洽 + veto 机制 + CVI 几何平均**——三仓都没有任何 pass/fail 质量门。
- **handoff 契约**(DONE/BLOCKED token、维度分、priority ID、URL)——三仓只有"Related Skills"名字列表。
- **keyless Tier-1 连接器哲学**——我们每个技能零安装即可用;ericosiu/coreyhaines 没 key 基本跑不了。
- **每技能 semver + 8 文件追踪契约**——比 ericosiu 单一 VERSION、kostja94 极简 frontmatter 都更严谨。
- **5 个 `/aaron-marketing:` 一次性命令**入口——三仓都无命令层。

---

## 2. 强化现有 SEO/GEO 技能(20 个)

> 这一节全部是「把它们的好内容,以 references/ 或 instructions 补丁方式,注入我们已有技能」,**不新增技能**。

| 借鉴项 | 来源(文件路径) | 注入我们的技能 | 具体可搬内容 |
|--------|----------------|---------------|-------------|
| **逐平台 AI 被引因子** ⭐ | coreyhaines `ai-seo/references/platform-ranking-factors.md` | `geo-content-optimizer`, `content-quality-auditor` | Google AIO / ChatGPT / Perplexity / Copilot / **Claude·Brave** 各引擎的来源选择逻辑,带引用研究(Princeton GEO KDD'24、SE Ranking 12.9 万域、ZipTie 40 万页);如「ChatGPT:内容-答案契合 ≈ 55% 被引概率」「<30 天新鲜度 → 3.2× 被引」。**单文件价值最高,正中我们 GEO 主场。** |
| **GEO 的 RAG/爬虫模型** ⭐ | kostja94 `skills/strategies/commercial/geo/SKILL.md` | `geo-content-optimizer` | 检索供给分类(自建索引/绑定搜索引擎/三方 API/混合)逐平台映射 + 爬虫分类(训练 vs 索引/RAG vs 实时,含 GPTBot/OAI-SearchBot/PerplexityBot/ClaudeBot 名);两仓互补,是我见过最系统的 GEO 文档。 |
| **AI-bot robots.txt 白名单** | coreyhaines `ai-seo/references/platform-ranking-factors.md:120-131` | `technical-seo-checker` | 可直接复制的 user-agent 允许/拒绝清单 + 「CCBot 可拦不丢被引(仅训练用)」要点。改动极小、立即正确。 |
| **llms.txt + OKF 机读栈** | coreyhaines `ai-seo/references/okf.md` | `geo-content-optimizer`, `entity-optimizer`, `schema-markup-generator` | 分层模型 `sitemap → robots → llms.txt → /pricing.md → /okf/ → schema`;诚实标注 OKF 当前无排名信号、属协议层注册。**我们今天完全无 llms.txt/OKF 覆盖。** |
| **Schema 检测假阳性修复** ⚠ | coreyhaines `seo-audit/SKILL.md:38-49` | `technical-seo-checker`, `schema-markup-generator`, `on-page-seo-auditor` | 关键实务警告:`web_fetch`/`curl` 会剥离 `<script>`,导致 JS 注入的 JSON-LD(Yoast/RankMath/AIOSEO)**不可见** → 误报「无 schema」。改用浏览器 `document.querySelectorAll('script[type="application/ld+json"]')` 或 Rich Results Test。**我们很可能有同一个误报 bug,值得自查。** |
| **Impact × Confidence + 漏斗关键词打分** | ericosiu `seo-ops/SKILL.md:112-131` | `keyword-research` | Impact(量+CPC+漏斗+趋势)× Confidence(难度+当前位+主题权威),并按关键词模式分 BOFU/MOFU/TOFU。比平铺优先级分更清晰。 |
| **Striking-distance(4-20 位)快赢监控** | ericosiu `seo-ops/SKILL.md:54-62` | `rank-tracker` | GSC 第 4-20 位作为每日快赢面;给出明确节奏(周全量/日 striking/周双趋势)。 |
| **衰退页数值化告警** | ericosiu `seo-ops/SKILL.md:46` | `content-refresher`, `alert-manager` | 流量跌 >30% 触发刷新——我们目前未给数值阈值。 |
| **多源、keyless 趋势侦察** | ericosiu `seo-ops/trend_scout.py`(方法,非代码) | `trend-spotter`, `content-gap-analysis` | Google Trends RSS + HN + Reddit + YouTube outlier,基础无需 key,按配置垂类相关性打分。正合我们 keyless 连接器哲学,可作配方。 |
| **YouTube outlier + 标题包装骨架** | ericosiu `yt-competitive-analysis/SKILL.md`(stdlib) + kostja94 `platforms/youtube` | `serp-analysis`, `competitor-analysis` | 2× 频道均播放 = outlier,提取标题模式;「YouTube+Reddit ≈ AI Overviews 社媒被引 78%」。视频 SERP 与 GEO 都吃这块。 |
| **国际化/hreflang 包** | coreyhaines `seo-audit/references/international-seo.md` | `technical-seo-checker` | hreflang 实施细则——我们缺。 |
| **AI 写作检测启发式** | coreyhaines `seo-audit/references/ai-writing-detection.md` | `content-quality-auditor`, `seo-content-writer` | 与下方 ericosiu humanizer 合并使用,映射 CORE-EEAT 的 Experience/真实性维度。 |
| **CWV 阈值 + 抓取预算清单** | coreyhaines `seo-audit/SKILL.md:109-120` | `technical-seo-checker` | LCP<2.5s/INP<200ms/CLS<0.1;faceted-nav、参数 URL、session-ID 抓取预算控制。 |
| **SSR/SSG/CSR 渲染策略** | kostja94 `seo/technical/rendering-strategies` | `technical-seo-checker` | 「AI 爬虫不执行 JS,关键内容须在首屏 HTML」。 |
| **`@id` 实体链接 + 知识面板现实性** | kostja94 `seo/entity-seo` | `entity-optimizer` | `https://example.com/#organization` 实体链接、Organization↔WebSite 关联、知识面板「多数站点无法直接获得」的诚实框定。 |
| **Mermaid 可视化站点图** | coreyhaines `site-architecture/references/mermaid-templates.md` | `internal-linking-optimizer` | 可复制 `graph TD` 站点图 + 导航分区子图,用于可视化孤儿页/孤岛。 |
| **Grokipedia AI 被引实操** ⭐ | kostja94 `skills/platforms/grokipedia/SKILL.md` | `geo-content-optimizer`(新增 reference) | 实测「隐形」战术:Suggest-Article 绝不放自己 URL;把内容概念改写成中立「应覆盖的方面」让 Grok 网搜重新发现你的页;Suggest-Edit 时只在「再加一个来源」处放 URL,旁配 1-2 个权威源。**带可直接粘贴的表单模板。** Grok 被 ChatGPT/Perplexity/Gemini 引用,是高价值 GEO 真房产。 |

---

## 3. 强化现有 influencer 技能(18 个)

> 影响者半边是我们**基础设施欠债最多**的一侧(据内部 OPTIMIZATION_PLAN:无 eval 覆盖、C³ 框架"空挂"、技能单体 415-603 行)。三仓的「创作者内容生产 + 平台 playbook」正好补这块。

| 借鉴项 | 来源 | 注入我们的技能 | 具体内容 |
|--------|------|---------------|---------|
| **平台专属 playbook** ⭐ | kostja94 `platforms/{x,linkedin,tiktok,youtube,reddit}` | `influencer-discovery`, `content-reviewer`, `content-amplifier`, `ugc-repurposer`, `outreach-manager` | 我们 18 个技能只抽象点名「Instagram/TikTok/YouTube」,**完全无逐平台算法 playbook**。可搬:X 回复≈54-75× 点赞、外链砍约 50% 曝光→链接放评论、TweepCred 阈值;LinkedIn「Headline 当 title tag」「About 写成答案优先 40-60 词块」;Reddit 90/10 原则、flair 必填;TikTok 字幕(80%+ 静音观看,字幕 +12-20% 观看时长)。**这是 kostja94 单一最大可搬资产。** |
| **创始人/创作者声音模板** ⭐ | ericosiu `x-longform-post/references/founder-voice.md`、`content-eval/references/voice-rules.md` | `brief-generator`, `content-reviewer` | 结构化捕捉创作者真实声音的 intake——直接补我们 brief 的声音段。 |
| **humanizer 24 条 AI-slop 检测** ⭐ | ericosiu `content-ops/experts/humanizer.md` | `content-reviewer`(作 veto) | 24 条 AI 写作模式(意义膨胀、肤浅 -ing 分析、空泛归因、规则三连、破折号滥用、谄媚腔…),每条带扣分 + 前后改写例 + ~55 词禁用表(delve/tapestry/leverage/robust/seamless…)。 |
| **7 级内容原子提取 + 病毒分 + 语义去重** ⭐ | ericosiu `podcast-ops/podcast_pipeline.py:297,564` + `content-ops/scripts/content-transform.py`(`--template-only` 无需 key) | `ugc-repurposer`, `content-amplifier` | 把一份转录拆成 7 类原子(narrative_arc/quote/controversial_take/data_point/story/framework/prediction),各带时间戳+建议平台;病毒分 = Novelty×0.4+Controversy×0.3+Utility×0.3,按内容/原子类型加权;**Jaccard 0.70 语义去重**(批内 + 对 30 天已发历史,flag 而非硬删)防日历饱和。比通用切块强,是「编辑大脑」。template-only 模式正合我们 keyless Tier-1。 |
| **10 人物画像递归评分面板(迭代到 90)** ⭐ | ericosiu `outbound-engine/references/expert-panel.md`(全仓"招牌"模式,video/podcast 也复用) | `outreach-manager`, `content-reviewer` | 10 个具名人物画像(各自评分镜头:回复率/框架-地位/反垃圾/模式打断/研究深度/可读性/可达性),0-100 打分**迭代到 ≥90**,每轮投票表保留进交付物;面板 5-15 人、按垂类换人。比单次打分更具操作性,补我们 outreach 侧空白。 |
| **冷邮文案硬规则** | ericosiu `outbound-engine/references/copy-rules.md` | `outreach-manager` | 首句硬禁(永不 I/We/"Hope this finds you well")、逐步句数上限(Step1 ≤3)、软 CTA 清单、观察 vs 研究框定、Step1 不放链接(可达性)。 |
| **clip 价值评分(hook/build/payoff/clean-cut)** | ericosiu `short-form-pipeline` `editorial-brain.py`(两遍扫描,仅 90+ 才切) | `content-reviewer`, `ugc-repurposer` | 选「值得切的片段」的清晰评分镜头(实现用 whisper/mediapipe,**只搬方法不搬代码**)。 |
| **一源 20+ 件 fan-out 框架** | ericosiu `podcast-ops` | `content-amplifier`, `ugc-repurposer` | 单集播客 → 跨平台 20+ 件的内容倍增框定。 |
| **影响者 vs 联盟 vs 创作者 决策表 + 分层** | kostja94 `channels/partnerships/influencer-marketing` | `campaign-planner`, `fit-scorer`, `budget-optimizer` | 干净的决策表 + 分层(纳米 1-10K/微 10-100K/中 100K-1M/宏 1M+)+ 合作模式 +「互动率 > 粉丝数」筛选。**注:它本身只 85 行、无评分,深度不如我们 C³;只取决策表/分层。** |
| **创作者长期项目 / EGC** | kostja94 `channels/partnerships/creator-program`、`channels/owned/employee-generated-content` | (我们无对应,概念补充) | 长期创作者项目模型 + 员工生成内容——我们 18 个里的空白。 |
| **多源 dossier + 缺口检测 + 瀑布式补全** | ericosiu `lead-dossier/account-researcher.py`(**stdlib-only**)、`cascade-enricher.py`(无 key 自动 dry-run) | `influencer-discovery`, `fit-scorer` | 抓首页 meta/正文(stdlib `HTMLParser`)→检测缺口(无博客/无 GA/内容稀薄)→技术栈分桶→合成 3-5 句 brief;瀑布式联系方式补全(主→finder API→仅 LinkedIn→无)。直接映射创作者背调/联系发现,且**多数脚本纯 stdlib**。 |
| **co-marketing / prospecting 交叉喂养** | coreyhaines `co-marketing`, `prospecting`, `social`, `customer-research` | `influencer-discovery`, `fit-scorer`, `audience-analyzer`, `niche-researcher` | 伙伴识别 + 伙伴-契合打分(种 fit-scorer 输入)、list-build→qualify→enrich 管线、VoC 逐字语言法。 |
| **content-eval 7 专家面板 + 4 周排期** | ericosiu `content-eval/SKILL.md` + `references/panel.md` | `campaign-planner`, `content-reviewer` | ideation 打分(85+ 过)+ kill-list + 生产排期输出,映射活动内容规划。 |

**最高价值影响者搬运**:创始人声音模板 + humanizer slop 检测 + atom→多平台转换环——全是 Markdown/stdlib,直接补 `content-reviewer`/`ugc-repurposer`/`content-amplifier` 的真实空白。

---

## 4. 新增 SEO/GEO 子技能(明确空白)

> 这些是我们 SEO 侧**真正缺的技能单元**,非补丁。建议作为新 SKILL.md 加入对应相位。

| 候选新技能 | 来源 | 相位 | 价值/理由 | 工作量 |
|-----------|------|------|----------|--------|
| **`programmatic-seo`** ⭐ | coreyhaines `programmatic-seo/references/playbooks.md`(12 套命名打法)+ kostja94 `seo/programmatic-seo`(319 行,**5 级数据可防御性层级** + 「同质化页修复」N-gram 去重 P0/P1/P2) | Build | 我们有 keyword/gap/serp 研究但**无规模化建页技能**——最明确的 SEO 空白。两仓内容互补,起步即很扎实。 | M-L |
| **`site-architecture`** | coreyhaines `site-architecture/`(站点层级/导航/URL 拓扑 + Mermaid 站点图) | Optimize | 我们 `internal-linking-optimizer` 是页面链接级,无**全站 IA 级**规划。net-new。 | M |
| **`local-seo`** | kostja94 `seo/local/local-seo` | Build/Optimize | GBP、NAP 一致性、引用优先级——我们完全无本地 SEO。干净 net-new。 | S-M |
| **`parasite-seo`(寄生/藤壶 SEO)** | kostja94 `seo/parasite-seo` | Build/Optimize | 分布式权威工程:平台分层(T1 GEO 权威 Medium/Reddit/LinkedIn/Quora;T2 技术 GitHub/SO/Dev.to)+ Google「站点声誉滥用 2024」风险规避。高价值、确实缺。 | M |
| **`competitors`(对比/替代页构建)** | coreyhaines `competitors/SKILL.md`(4 种格式) | Build | **内容生产**技能(建「vs/alternative」页),区别于我们分析型 `competitor-analysis`。单数/复数替代页、you-vs、competitor-vs。 | S-M |
| **`aso`(应用商店优化)** | coreyhaines `aso/`(312 行) | Build | 我们 20 个里完全没有;小而干净的学科邻接空白。⚠ 仅当用户群涉及 App 才值得。 | S |
| **`ai-traffic` 分析** | kostja94 `analytics/sources/ai-traffic` | Monitor | 在 GA4/GSC 中追踪 AI 搜索流量;配我们 keyless 连接器配方。喂 `performance-reporter`。 | S |
| **AI-citation 平面技能**(Medium/GitHub/Grokipedia) | kostja94 `platforms/{medium,github,grokipedia}` | Build(GEO) | 作 `geo-content-optimizer` 的 references 或独立轻技能,把「在高权威平台发布以被 AI 引用」操作化。 | S 每个 |

---

## 5. 全新营销领域(扩边界)— ⚠ 需产品决策

> 以下是我们**两学科之外**、三仓覆盖而我们没有的领域。是否纳入会改变项目边界,属不可逆决策,**先拍板再排期**。

### 5.1 建议设立的「第三条学科线」候选

| 领域 | 来源强度 | 建议 | 归属 |
|------|---------|------|------|
| **CRO / 转化** | coreyhaines `cro`(7 维框架:价值主张→标题→CTA→层级→信任→异议→摩擦)、`signup`、`onboarding`、`popups`、`paywalls`;ericosiu `conversion-ops`(8 维加权 CRO 审计 + `conversion-quality.md` rubric) | **强烈建议** | 新「Convert/转化」学科,或并入 SEO/GEO 漏斗尾。CRO 是 SEO 流量与转化之间的天然桥。 |
| **留存 / 生命周期** | coreyhaines `emails`(生命周期/drip)、`sms`、`cold-email`、`churn-prevention`(424 行,最深:取消流/挽留 offer/dunning/失败扣款恢复) | **建议** | 新「Retain/留存」学科。与我们 performance/report 自然配对,把漏斗延伸到流量之后。 |
| **度量 / 闭环**(cross-cutting,非学科) ⭐ | ericosiu `closed-loop-analytics-upgrade/SKILL.md`(纯 Markdown 零依赖)+ `growth-engine`(bootstrap CI + Mann-Whitney U,p<0.05 且 ≥15% lift 才升级) | **强烈建议(薄协议层)** | **不是新学科,是新 cross-cutting 协议**,插入 Monitor 相位,像 memory-management 一样横切。详见 §6 Tier-1。 |

### 5.2 可选 / 低优先

| 领域 | 来源 | 建议 |
|------|------|------|
| 定价 | coreyhaines `pricing`、kostja94 `commercial/pricing`、ericosiu `sales-playbook`(价值定价/分层包) | 单技能、高杠杆,可作 Strategy 邻接;ericosiu 的 4 层定价心理学(锚点 130-150%)可搬。 |
| 付费广告 | kostja94 `paid-ads/platforms/{google,meta,linkedin}`(google-ads 含 Quality-Score CPC 数学、付费-自然蚕食审计)、coreyhaines `ads`/`ad-creative` | 面大、与 keyless 理念协同弱(广告平台需 key)。**缓**。若做,独立学科。 |
| Launch/GTM 策略 | coreyhaines `launch`、kostja94 `strategies/launch/{cold-start,pmf,gtm}` | `cold-start`/`gtm`/`pmf` 是 net-new 策略层;episodic,可作 Strategy 邻接。 |
| 战略评估镜头 | coreyhaines `marketing-plan`(AARRR + 17 段 /85 现状 rubric,最深资产)、`marketing-ideas`(139 创意路由器) | 借 **AARRR rubric + 创意库路由**概念作 cross-cutting 规划层,不必建整个学科。 |
| **明确不建议** | ericosiu `finance-ops`/`deck-generator`/`team-ops`/`sales-pipeline`(RB2B 路由/deal 复活);coreyhaines `revops`/`sales-enablement` | 超出营销执行范围(财务/HR/B2B 销售),且重依赖。**跳过**。 |

---

## 6. 工程 / 质量基建借鉴(最具复利、与理念零冲突)

> 这一组是三仓里**对我们护城河增益最大**的部分:全部可在「零依赖 + Markdown/stdlib」约束下落地,且填补我们真实缺口。

### Tier-0 — 立即、纯 Markdown、零冲突、高杠杆

| # | 借鉴项 | 来源 | 落地方式 |
|---|--------|------|---------|
| T0-1 | **humanizer 24 条 AI-slop 检测** | ericosiu `content-ops/experts/humanizer.md` | 整体搬入 `references/`,在 `seo-content-writer`/`geo-content-optimizer`/`content-quality-auditor`/`content-reviewer` 引用为 slop veto。已是 Markdown。 |
| T0-2 | **逐平台 AI 被引因子 + AI-bot robots.txt 白名单 + llms.txt/OKF** | coreyhaines `ai-seo/references/*` | 拆成 `geo-content-optimizer` 与 `technical-seo-checker` 的 references。 |
| T0-3 | **closed-loop 闭环度量方法论** | ericosiu `closed-loop-analytics-upgrade/SKILL.md` | 作新的 cross-cutting 协议 `references/closed-loop.md`:readback 窗口(内容刷新 7/14/28/56 天等)、必填 readback 字段、promote/keep-testing/rollback/unproven 规则、不可升级清单(量太小/归因脏/季节性/连接器失败/只有作者喜欢)。 |
| T0-4 | **Schema 检测假阳性自查与修复** | coreyhaines `seo-audit/SKILL.md:38-49` | 改 `technical-seo-checker`/`schema-markup-generator`,渲染 JS 注入 JSON-LD 而非信任 `web_fetch`。 |

### Tier-1 — 工程基建(中成本,抬升全局质量门)

| # | 借鉴项 | 来源 | 落地方式 / 适配 |
|---|--------|------|----------------|
| T1-1 | **stdlib 版 `/eval` 输出回归测试网** ⭐ | ericosiu `eval/run-eval.ts` + `eval/CLAUDE.md` | **我们最大的缺口**:有质量标准却无法回归测试技能编辑是否降质。用 Python-stdlib 重写:每技能跑 golden-input fixture → 按声明式判据(`contains`/`regex`/`max_sentences`/`no_hallucination`/`preserves_numbers`…)打分 → 与 `eval-baseline.json` diff,降分则 CI 非零退出。配 OPTIMIZATION_PLAN 的 P2-3(influencer eval 缺口)一并补。 |
| T1-2 | **递归打磨到目标分 + 学习型拒绝记忆** | ericosiu `content-ops/SKILL.md:101-231` + `references/patterns.md` | 给 `content-quality-auditor`:打分→列 top-3 弱项→修订→重打(≤3 轮)迭代到 CORE-EEAT 目标;用户拒绝时把(类型/规则/例/扣分)追加进 `patterns.md`,**未来每次打分先预扣已知坏模式**。接我们 memory-management。 |
| T1-3 | **转化 + 视觉质量评分细则** | ericosiu `content-ops/scoring-rubrics/{conversion-quality,visual-quality}.md` | 作 auditor 新 references,补 CORE-EEAT 欠覆盖的落地页摩擦/CTA 强度/图表完整性。 |
| T1-4 | **CI 从 frontmatter 自动同步追踪文件** ⭐ | coreyhaines `.github/scripts/sync-skills.js` + `sync-skills.yml` | 解决我们手工「8 文件追踪清单」漂移:从各 SKILL.md frontmatter 自动重生成 README 技能表 / marketplace.json / plugin.json。纯 infra,无理念冲突(用 stdlib/node 任一)。 |
| T1-5 | **PII 哨兵 + pre-commit + CI 安全门** | ericosiu `security/sanitizer.py` + `pre-commit-hook.sh` + `skill-safety.yml`(PII 那半) | 纯 stdlib + bash,近零成本增强我们 validator/CI。**丢掉 CTA-block 那半(那是他们的归因强制)。** |

### Tier-2 — 体验/工具层(锦上添花)

| # | 借鉴项 | 来源 | 落地方式 |
|---|--------|------|---------|
| T2-1 | **REGISTRY「Agent 推荐」决策行** | coreyhaines `tools/REGISTRY.md` | 把我们 `CONNECTORS.md` 从清单升级为决策辅助:每个 `~~category` 加一行「默认选谁、何时换」(保持 keyless 配方)。 |
| T2-2 | **`product-marketing` 基础上下文模式** | coreyhaines `product-marketing/SKILL.md` | 加一个可从 repo(README/落地页/package.json)自动起草的「定位 SSOT」文件,所有技能先读。**补充而非替代**我们记忆层。 |
| T2-3 | **CLI 形态规范(若做 Tier-2 自动化层)** | coreyhaines `tools/clis/*`(`--dry-run` 凭证打码 `***`、结构化错误带提示、`{tool} <resource> <action>`) | **只借形态,不借那 64 个付费 API CLI**。我们 stdlib 连接器仍指向 GSC/GA4-own/PageSpeed/Wikidata/Common Crawl/Open PageRank。 |
| T2-4 | **统计显著性升级门(方法,非代码)** | ericosiu `growth-engine/SKILL.md` | `performance-analyzer`/`roi-calculator` 文档化决策规则:bootstrap CI + Mann-Whitney U,p<0.05 且 ≥15% lift 才 promote。保留为方法指引,不引 scipy。 |
| T2-5 | **时间衰减多触点归因(方法)** | ericosiu `revenue-intelligence/revenue_attribution.py:392-426` | 若未来扩内容→营收度量:`weight = 0.5^(days_before/half_life)`(默认 7 天半衰期)归一化。最严谨可复用算法。 |

---

## 7. 明确「不要借鉴」清单(避免被带偏)

- **ericosiu 的重依赖脚本实现**:whisper/mediapipe/opencv/scipy/sklearn/pandas/psycopg2 + 实时 keyed API(Ahrefs/Gong/RB2B/Instantly/HubSpot)。**只搬方法论,deterministic 部分用 stdlib 重写。** 注:并非全仓都重——`video-caption-generator`、`growth-engine` 的 scorecard/pacing、`lead-dossier/account-researcher`、`outbound-engine` 的 competitive-monitor/cross-signal-detector 等**本就是纯 stdlib**(caption 脚本甚至用裸 `urllib` 调 Anthropic 而非 SDK),这部分可近乎直接移植,印证「方法可搬、依赖不搬」。
- **coreyhaines 的 64 个 Node CLI**:全是付费 API 封装,会随 API 变更腐烂(clearbit 已变 HubSpot Breeze)。只借「单文件零依赖 + dry-run 打码 + 结构化错误」之**形**。
- **coreyhaines 的 94 个 `tools/integrations/` 文件**:与 REGISTRY 大量冗余,过度建设。只取 REGISTRY 蒸馏索引。
- **ericosiu `skill-safety.yml` 的 CTA-block 检查**(强制每个 README 含 `singlebrain.com`):那是归因/营销强制,非质量门。**丢弃。**
- **ericosiu telemetry 的「每技能 shell-out 上报」**:即便干净、opt-in,一个**对外分发的插件**默认 phone-home 是不同信任姿态。若采用须**仅本地、无远端端点、用户显式开 hook**,且不破坏「skill 即 Markdown」身份。
- **kostja94 的 `components/` + `pages/` 网站构建器(69 个,40%)**:属网站/落地页搭建,出我们营销-技能范围,会稀释焦点。例外:`landing-page-generator`/`hero-generator` 的转化模式可喂我们已有的 `landing-optimizer`。
- **kostja94 的薄长尾技能**:`medium-posts`(54 行)/`pinterest`/`native-ads`/`ctv-ads`/法务页生成器/通用 `card`/`grid`/`masonry` UI——分类完整性产物,搬来只增表面积不增价值。
- **kostja94 的 `creator-attribution`(按用户情绪触发自我推广行)**:反特性,勿碰。
- **ericosiu `finance-ops`/`team-ops`/`deck-generator`/`sales-pipeline`**:超营销范围(财务/HR 排名/B2B 销售路由),且重依赖。

---

## 8. 建议执行顺序(把上面变成 PR 批次)

> 原则:先做「纯 Markdown、零冲突、高杠杆」,再做「工程基建」,最后才是「新技能/新学科」(后者依赖前面的 eval 网做回归保护)。与内部 `OPTIMIZATION_PLAN.md` 的质量债修复**互补**——那个先修地基,这个再扩内容。

- **批次 A(Tier-0,1 个 PR,S-M)**:T0-1 humanizer slop veto + T0-2 AI 被引因子/robots/llms.txt + T0-3 closed-loop 协议 + T0-4 schema 假阳性修复。全 Markdown,立即见效,零回归风险。
- **批次 B(Tier-1 基建,2-3 个 PR,M-L)**:T1-1 stdlib eval 回归网(**优先,且顺带补 influencer eval 缺口**)→ T1-4 CI 自动同步 → T1-5 PII 哨兵 → T1-2/T1-3 auditor 递归打磨 + 新评分细则。
- **批次 C(新 SEO 子技能,逐个 PR,M each)**:`programmatic-seo` → `site-architecture` → `local-seo` → `parasite-seo` → `competitors` 构建页 →(可选)`aso`/`ai-traffic`。**每个新技能必须先有批次 B 的 eval fixture。**
- **批次 D(平台 playbook 层,1-2 个 PR,M)**:把 kostja94 的 6 个平台 playbook 拆成共享 `references/platforms/*.md`,被 SEO 分发与 influencer 技能双向引用。
- **批次 E(新学科,⚠ 决策后)**:CRO/Convert 簇 + 留存/生命周期簇。**先回答 §5 的产品决策**,再排期;依赖 eval 网与 closed-loop 协议先就位。

---

## 9. 待你决策的 3 件事

1. **是否扩第三条学科线(CRO/转化 + 留存/生命周期)?** 这是把项目从「SEO/GEO + 影响者」扩成「全漏斗」的不可逆边界决策。建议:**先做 CRO/Convert 簇**(与 SEO 流量协同最强),留存簇随后;付费广告缓做。
2. **eval 回归网做多大?** 最小=先给 C³ veto 相关的 fit-scorer/content-reviewer + 4 个 SEO build 技能补 fixture;完整=38 技能全覆盖。建议跟 `OPTIMIZATION_PLAN` 的 P2-3 合并。
3. **平台 playbook 放哪?** 作共享 `references/platforms/`(被多技能引用)还是塞进各技能?建议共享 references,避免 18 个影响者技能各自重复(也契合我们 references/ 拆分方向)。

---

### 附:四份原始深挖报告的来源仓库与关键文件

- **coreyhaines**(45 技能 + tools/):`ai-seo/references/platform-ranking-factors.md`、`ai-seo/references/okf.md`、`seo-audit/SKILL.md:38-49`、`programmatic-seo/references/playbooks.md`、`site-architecture/references/mermaid-templates.md`、`competitors/SKILL.md`、`product-marketing/SKILL.md`、`tools/REGISTRY.md`、`.github/scripts/sync-skills.js`、`marketing-plan/references/current-state-rubric.md`
- **kostja94**(172 技能):`skills/platforms/{x,linkedin,tiktok,youtube,reddit,grokipedia}/SKILL.md`、`skills/strategies/commercial/geo/SKILL.md`、`skills/seo/{parasite-seo,programmatic-seo,local,entity-seo,technical/rendering-strategies}/SKILL.md`、`skills/paid-ads/platforms/google-ads/SKILL.md`、`skills/analytics/sources/ai-traffic`
- **ericosiu**(22 技能 + 基建):`eval/run-eval.ts`、`eval/CLAUDE.md`、`content-ops/experts/humanizer.md`、`content-ops/scoring-rubrics/*.md`、`content-ops/SKILL.md:101-231`、`closed-loop-analytics-upgrade/SKILL.md`、`seo-ops/SKILL.md:54-171`、`security/sanitizer.py`、`skill-safety.yml`、`growth-engine/SKILL.md`、`x-longform-post/references/founder-voice.md`、`revenue-intelligence/revenue_attribution.py:392-426`
