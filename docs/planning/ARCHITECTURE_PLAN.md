# 平台架构规划 — 系统级层 vs 学科专属层

> **状态:SUPERSEDED(支撑分析 · 已并入活路线图)。** 单一活路线图见 [UNIFIED_OPTIMIZATION_PLAN.md](UNIFIED_OPTIMIZATION_PLAN.md);本文件作为平台架构(平台层 vs 学科层)的原始分析存档,不再单独执行。索引见 [README.md](README.md)。

> **问题**:我们的 SEO/GEO 项目里有些 cross-cutting 概念(审计协议、连接器、记忆、CI…)是不是应该上升为整个 marketing-skills 的**系统级横向平台层**?整体架构应该怎么规划?
> **方法**:6 维度并行精读现状 → 3 个独立架构师(外科手术 / 干净分层 / 面向扩展)各出方案 → 评审选基底 + 择优嫁接 → 合成 → **对抗式压力测试**。结论已用文件 `file:line` 核验。
> **基线**:v10.0.1 · 38 skills(SEO/GEO 20 + 影响者 18)。本文为架构规划稿,未纳入发布物。
> **日期**:2026-06-29 · **对抗复核结论**:`sound-with-fixes`(必修订正已并入 §7)。

---

## 0. TL;DR — 直接回答你的两个问题

**Q1:cross-cutting 该不该做成系统级?** —— **该,但要分清"协议"和"技能本体"。**
- 真正该上升为系统级的是这些技能**背后的协议/SSOT**:① **质量门协议**(`references/auditor-runbook.md`,它自己第 5 行就声明"framework-agnostic",已经是 SSOT,只是 veto 集只挂了两个 SEO 框架);② **记忆/状态模型**(`state-model.md` 已经把 `memory/influencer/` 当对等 WARM 分区,~80% 已系统级)。
- **不该**被"通用化"的是 4 个审计技能的**本体**:`content-quality-auditor` 是 CORE-EEAT 的实例、`domain-authority-auditor` 是 CITE 的实例、`entity-optimizer` 是 SEO 实体——它们是协议的**学科实例**,不是通用门。强行合并 = 错误抽象。
- 真正的动作:让协议**承认第三个框架(C³/ART)**,把已存在但"裸奔"的影响者质量门 `content-reviewer` 纳入同一协议(它今天 0 引用 runbook、无 `class:` 标记、产物写到 `memory/influencer/` 而 Artifact Gate 对它**不做任何校验**)。

**Q2:connectors 该不该做成系统级?** —— **注册表和中性代码核该,领域提取器不该。**
- `CONNECTORS.md`(`~~category` ↔ Tier-1 keyless 配方的契约)+ 三个机制上学科无关的 helper(`_http.py` 礼貌 HTTP、`ledger.py` 任意 `<target>/<source>` 键、`rss_monitor.py` 任意 feed)= 应是系统级。今天它们只是**文案上**写死成 SEO(`_http.py:26` 的 UA 是 `seo-geo-skills-connector/1.0`,CONNECTORS.md 把 SEO/影响者拆成两张无 discipline 标签的表)。
- 15 个 SEO 领域提取器(crawl/onpage/robots/sitemap/psi/schema_lint/kg/wayback/linkgraph/openpagerank/suggest)= 学科专属,**保持现状**,只共享"注册表契约 + ledger JSON 形状 + _http 核"。
- 影响者类目(`~~social platform analytics`、`~~influencer database`)的现实是**无公开 API、只能手动导出**——在注册表里明确标 `manual export only`,正好守住我们零依赖/keyless 红线(防止后来者加爬虫或 pip 依赖)。

**一句话模型**:**一层很薄的横向"平台层"(几乎全是已存在的 Markdown SSOT)托住几层很薄的纵向"学科层"(seo-geo / influencer / 未来 CRO·留存)。这个仓不需要重建目录,只需要让那几个"其实早就共享"的协议停止假装自己是 SEO 专属,并让构建/CI 脊柱停止写死学科清单。**

**判定一个概念能否"升系统级"的硬测试**(防过度设计):它**当前就服务、或能不分叉地平凡服务于**多个学科,**且**这次泛化是**替换一个已存在的写死项**,而非发明一个投机抽象。凡通不过这条测试的,一律推迟(§6)。

---

## 1. 现状诊断:为什么是"两个半融合学科"

这个仓由"20 个 SEO 技能"+"18 个影响者技能"合并而来。**表层规范已对齐**(`skill-contract.md:3` 已写"all 38 skills — 20 Search + 18 influencer",CI 也已覆盖全部 11 个相位目录——这些是 OPTIMIZATION_PLAN 已执行的成果),**但底层基础设施仍是"为 SEO 建、影响者搭便车"**:

| 层 | 现状(file:line 核验) | 病灶 |
|----|----------------------|------|
| 质量门协议 | `auditor-runbook.md` 自称 framework-agnostic,但 veto 集只有 SEO(`:91-93` CORE-EEAT T04/C01/R10 + CITE T03/T05/T09);C³/ART 缺席 | 影响者门 `content-reviewer` **绕过协议自建门**:0 引用 runbook、无 `class:` 标记、写 `memory/influencer/content-reviewer/`(SKILL.md:38),Artifact Gate(`claude-hook.sh:39` 只匹配 `memory/audits/*.md`)对它**零校验** |
| 评分数学 | `golden-auditor-math.py` 只守 CORE-EEAT/CITE(`:25-26`),还写死两个审计技能路径(`:27-28`);C³ 的 `CVI=(ACE×ART×ROI)^(1/3)` 无人守 | C³ 数学"裸奔";且 `c3-benchmark.md:36` 只有公式、**无数值算例**,导致 golden-math 无从断言 |
| 记忆/状态 | `state-model.md:191-204` 已把 `memory/influencer/` 当对等 WARM 分区按 C³ 计分 | 但 `memory-management/SKILL.md` 标题(:17"for SEO and GEO projects")、入口(:124)、查找流(:137-156)全是 SEO 措辞 |
| 连接器 | `CONNECTORS.md` 两张分离的表(SEO :76-94 / 影响者 :96-118,无 discipline 标签);`_http.py:26` UA 写死 seo-geo;`ledger`/`rss_monitor` 标 SEO 实则通用 | 注册表"账面共享、物理割裂";影响者类目无配方代码(本就该是 manual-export) |
| 构建/CI | 一套 validator + 一条 CI + 单 bundle 版本 + 8 文件追踪 = 结构上已系统级 | 但**4 处写死学科清单**:CI find 的 11 个位置参数(`validate-skill.yml:64-65`)、validator 的影响者 case(`validate-skill.sh:217-218`)、golden-math 框架表(`:25-26`)、golden-math 审计路径(`:27-28`) |
| 路由/命令 | 5 个命令全是 SEO 意图;`aaron-product-api-contract.md:2` 明写"declines clearly non-SEO/GEO work";`auto-routing-scenarios.md` **0 个影响者场景**(核验:3 处 outreach 命中全是 SEO 外链语境) | `auto.md` 宣称能路由 IMPACT 目标,但**无场景支撑**——这是一条命名的平台缝,但按治理须先播种场景 |
| 实体 | `entity-optimizer` 独写 `memory/entities/<name>.md`,6 类信号全是 KG/Wikidata/schema | 影响者侧**无人写**规范创作者档案(`influencer-discovery` 只读品牌档案)——所以创作者实体是**没有消费者的空抽象** |

**结论**:不是"目录乱了",而是"几个本就共享的协议在文案上假装自己是 SEO 专属"+"4 个写死的学科清单"。**修法是外科手术式的,不是重建。**

---

## 2. 目标架构:薄平台层 + 薄学科层

```
┌─────────────────────────────────────────────────────────────────────┐
│  平台层 PLATFORM(学科中立,服务所有现有+未来学科)                      │
│  1. 质量门协议    references/auditor-runbook.md(handoff schema / veto→cap │
│                   / Artifact Gate / 翻译层 / 安全边界)——承认 C³ 为第三框架  │
│  2. 记忆/状态模型  state-model.md + HOT/WARM/COLD + memory/<分区>/ + GDPR purge │
│  3. 连接器注册表 + 中性核  CONNECTORS.md(~~category↔Tier1) + _http/ledger/rss_monitor │
│  4. 构建/CI/版本/追踪脊柱  validate-skill.sh / CI / golden-math / 8 文件追踪     │
│  5.(命名但推迟)学科路由   auto 分类器 + /impact——须先播种场景               │
└─────────────────────────────────────────────────────────────────────┘
        ▲ 插件缝(都已存在,提升=放第三个实例进去,而非造新抽象)
┌───────────────────────────┐   ┌───────────────────────────────────────┐
│ 学科层 SEO/GEO            │   │ 学科层 Influencer                      │
│ · CORE-EEAT / CITE 量表   │   │ · C³ ACE/ART/ROI 量表 + CVI 几何平均    │
│ · 3 个审计/实体技能本体    │   │ · content-reviewer 门本体(ART T1/T2)  │
│ · 15 个 SEO 领域提取器     │   │ ·(未来)csv_ingest——有消费者才建        │
└───────────────────────────┘   └───────────────────────────────────────┘
```

**四条"插件缝"(都已存在,提升 = 承认第三个实例,不是造新机器):**
- **门缝**:共享 handoff schema + veto→cap 法;插件 = 该量表的 veto-ID 行 + 加权/几何算例。(这正是 runbook 已经为 CORE-EEAT vs CITE 用的模式。)
- **记忆缝**:共享 HOT/WARM/COLD 生命周期 + `memory/<分区>/` + 一次性规范档案 + GDPR purge;插件 = 哪个框架给该分区计分。
- **连接器缝**:共享 `~~category` 键 + ledger JSON 形状;插件 = 领域提取器。
- **构建缝**:(可选)一行注册表项(学科→相位目录→框架文件→记忆分区→命令);auto-discovery 让新学科的技能一落地就过校验。

---

## 3. 四个 cross-cutting 协议技能 —— 逐个裁决

| 技能 | 裁决 | 理由 |
|------|------|------|
| **content-quality-auditor** | **保持学科专属**(它是 CORE-EEAT 实例) | 本体硬绑 80 项 CORE-EEAT、`GEO=(C+O+R+E)/4`、T04/C01/R10 veto(SKILL.md:299-336)。它**不是**通用内容门;它的影响者对应物是另一个技能 `content-reviewer`,不是合并目标。系统级的部分是它**已经在读**的 runbook。 |
| **domain-authority-auditor** | **保持学科专属**(CITE 实例) | 本质 SEO(外链/知识图谱/Google 惩罚/40 项 CITE)。无影响者对应物、也不需要。本体完全不动。 |
| **entity-optimizer** | **保持 SEO 专属;创作者实体推迟** | 今天**零个**影响者技能写规范创作者档案(`influencer-discovery` 只读品牌档案)。现在建 creator-entity 类型 = 复制粘贴未满两次就抽象 = 错误抽象。**用真实消费者(fit-scorer/competitor-tracker 需要持久档案时)来触发**,不预建。 |
| **memory-management** | **提升到系统级(仅改文案)** | 已~80% 系统级(state-model 已对等处理 memory/influencer/)。只把标题/入口/查找流的 SEO 措辞改成"营销记忆"并补影响者查找路径。**最小 diff**。⚠ `name:` 与 `metadata.version` 保持字节稳定,否则 validator `--status` 报 SPLIT、8 文件追踪连锁。 |

**真正升系统级的不是这 4 个技能,而是它们之上的两个协议:质量门协议(runbook)+ 记忆/状态模型。**

---

## 4. 连接器层裁决

| 组件 | 裁决 | 动作 |
|------|------|------|
| `CONNECTORS.md` 注册表 | **系统级** | 两张表合并成一张,加 `Discipline` 列(search/influencer/both)+ 强制 `Tier-1 keyless/own-data` 列。`~~social platform analytics`、`~~influencer database` 明标 `manual export only — no public API`(守 keyless 红线)。纯文档。 |
| `_http.py` / `ledger.py` / `rss_monitor.py` | **系统级(中性核)** | `_http.py:26` UA 改 `aaron-marketing-skills-connector/1.0`(纯 cosmetic,记 changelog);ledger/rss_monitor 在注册表改标 `both`(**无代码改动**,它们本就接受任意键/任意 feed)。 |
| 15 个 SEO 领域提取器 | **保持学科专属** | 不动。只共享注册表契约 + ledger JSON 形状 + _http 核。 |
| `scripts/connectors/{shared,seo,influencer}/` 子目录拆分 | **不做(推迟)** | 13 个连接器是裸 `import _http`(同目录),子目录化要改每个 importer,**零当前收益**。等真有影响者 helper 落地再说。 |

---

## 5. 系统级提升清单(from → to)

> 按"价值/成本"排序。**全部是文档/措辞/去写死,几乎不碰技能本体逻辑**,契合外科手术文化。

| # | 项 | from(现状) | to(目标) | 成本/风险 |
|---|----|-----------|---------|----------|
| **P5-1** | **质量门协议:承认 C³**(仅文档) | runbook veto 集只有 SEO 两框架(`:91-93`) | runbook 加一行 C³/ART veto-set(ACE A2/C1/E2、ART T1/T2),并把 cap 阈值口径在 §Changelog 显式对账 | S / 低。**只加文档行,不动共享逻辑**(复用 CORE-EEAT-vs-CITE 插件模式) |
| **P5-2** | **记忆模型去 SEO 化** | memory-management 文案 SEO(:17/:124/:137-156) | 改"营销记忆"+ 补影响者查找路径;name/version 字节稳定 | S / 低。四个里最小的 diff |
| **P5-3** | **连接器注册表统一** | 两张分离表 + SEO UA | 一张 discipline 标签表 + UA 改名 + ledger/rss 标 both | S / 低。纯文档 + 一个字符串 |
| **P5-4** | **构建/CI 去写死**(条件性,见 §7) | 4 处写死学科/路径 | auto-discovery find +(**可选**)一行 `disciplines.md` 注册表 | S / 中。**先修 reference-oss 排除(§7 必修)** |
| **P5-5** | **golden-math 守 C³**(有前置) | C³ CVI 无人守 | 先给 c3-benchmark.md 加**数值算例**,再让 golden-math 加一个 C³ CVI 断言块 | M / 中。**前置:算例必须先落地**,否则断言空过 |
| **P5-6** | **content-reviewer 纳入门协议**(产品决策门控,见 §9) | 影响者门裸奔、Artifact Gate 不校验它 | 决定它是否产出持久 gated 产物;若是,读 runbook、发 `class:` 标记、走 per-discipline audit 分区 | M / 中。**这是净新增耦合,不是"扩文档"——单列决策** |

---

## 6. 保留学科专属 + 明确不做(防过度设计)

> 这些是对抗复核明确点名要**拒绝**的"投机抽象",写入 non-goals 以防 runaway-refactor。

- **不做** `disciplines/` + `platform/` 物理重组目录:那是横跨 plugin.json + 两份字节一致 marketplace.json 镜像 + 每条 validator 强制的相对链接 + golden-math 写死路径的 **38 路径 diff,而宿主行为零变化**(plugin.json 才是真相源)。**等第 3 个学科出现再说**;最多把 4 个协议技能挪出 SEO 树,且只作一个独立机械 PR。
- **不做**现在就建 creator-entity 类型(零写入者 = 错误抽象,见 §3)。
- **不做** `csv_ingest.py` / 连接器子目录拆分(无非-SEO 消费者)。
- **不做**给 `auditor-runbook.md` 或 `class: auditor-output` 标识符改名(会同时触碰 hook + 两个审计本体 + golden-math + validator = runaway refactor)。**只扩文档范围,标识符保持稳定**。
- **不做**通用"连接器框架"/plugin-loader(只有一个共享模块 _http + ~80% 文档,抽象它 = dead flexibility)。
- **不做**合并三个量表(CORE-EEAT/CITE/C³ 计算不同的数:加权和 vs 几何平均 CVI;**不同的 rollup 数学是特性,不是 bug**。共享的是它们周围的*流程*,不是量表)。
- **不做**自动化 eval **runner**(`evals/` 明确是手工模拟种子集,这个约束保留;最多在 CI 加一条"每学科 eval 是否存在"的薄滚动)。
- **不做**为不存在的学科(CRO/留存)预埋字段/机制——**每一处改动只用今天的两个学科来论证**(对抗复核要求剥离所有"为将来加学科更便宜"的理由)。

---

## 7. 对抗式复核的必修订正(已并入)

> 对抗 agent 给出 `sound-with-fixes`,以下是落地前**必须**吸收的订正,均已 file:line 核验:

1. **✅ 已修复:`reference-oss/` 排除(我克隆竞品引入的真实隐患)。** `validate-skill.sh:68` 的 `--status` find 原先只排除 `docs/` 和 `.claude/`,**不排除 `reference-oss/`**——会扫到 **239 个第三方 SKILL.md**。已补 `-not -path "$REPO_ROOT/reference-oss/*"`(2026-06-29);核验后 `--status` 仅扫本仓 38 个技能、0 个 reference-oss、全 OK。已确认 `evals/` 无 SKILL.md fixture、过度扫描文件 100% 来自 reference-oss,故此排除即完整修复。(当前 CI 因用写死的 11 目录列表本就安全;此修复保护本地 `--status` 与未来 auto-discovery。)
2. **`disciplines.md` 降级为"条件性",别假设要做。** 4 处写死里有 2 处其实很薄:CI find-loop 换 auto-discovery **不需要表**(只需排除路径);validator `:217` 的影响者 case 是个"body-length 建议豁免"的 6-token case,**不是学科清单**,把它换成"grep Markdown 表"反而给 bash validator 加了文件读取、降低健壮性。**保留该 case 为字面量**;`disciplines.md` 只在"去掉前两者后仍有 ≥2 个真实消费者(golden-math 路径 + 框架表)"时才建,否则**直接内联修 find 排除 + golden-math 路径**即可。
3. **拆开 P5-1 的两半。** (a) runbook 加 C³ veto 行 + cap 对账 = 便宜、稳、做;(b) `content-reviewer` 接入门协议 = **净新增耦合**(hook 的 `fm()` 在 `:16` 写死 `class: auditor-output`,`:39` 写死 SEO 字段 cap_applied/raw_overall_score/final_overall_score;C³ CVI 产物一个都没有)。"加宽 glob"**不够**——要么给 hook awk 加**第二套 C³ 字段 schema**,要么让 content-reviewer 改成发完整 SEO handoff schema 并写 `memory/audits/influencer/`(本体改动)。**(b) 单列为需求门控决策(§9),不要打包进"扩文档"。**
4. **golden-math 守 C³ 有硬前置:先给 `c3-benchmark.md` 加数值算例**(给定 ACE/ART/ROI 输入 + 算出的 CVI),且断言块用**写死的期望输入/输出**,**不要**做"从 Markdown 表动态发现框架"(那会让测试本身变成解析器、表损坏时静默通过)。golden-math 改动**阻塞**于算例先落地(CI 顺序门)。
5. **`disciplines.md` schema 缺一列。** golden-math `:27-28` 写死的是**审计技能 SKILL.md 路径**,而提议的表(学科→相位目录→框架文件→记忆分区→命令)没有这列。**要么加列(scope creep)、要么 golden-math 保留这处写死**——二选一,别声称"4 处全替换"。
6. **hook 是 decision:block 钩子且修过 false-block(VERSIONS.md:55)**:任何新分支必须**additive + fail-open**,对未知形状用 runbook 的读时默认。给 `tests/test_hook_artifact_gate.sh` 加一个影响者 fixture。
7. **版本纪律**:即便只改 memory-management 散文,按本仓发布文化也容易触发 version bump → 连锁 8 文件追踪。**刻意保持 name/version 字节稳定**。
8. 已澄清两处**原假设是错的**(对抗已核验):`skill-contract.md:3` **已写 38 skills**(无需改计数);CI **已覆盖全部 11 相位目录**(`yml:64-65`)。所以 build-ci 的病灶只是"写死清单的维护气味",**不是覆盖缺口**。

---

## 8. 迁移路径(增量、可回滚、对抗已订正)

> 与内部 `OPTIMIZATION_PLAN.md`(质量债修复)互补:那个先修地基,这个再做平台化。可各自独立成 PR。

- **Phase 0 — 只决策,不动码(XS)**:定 cap 阈值口径(60 vs ≤59,§9)。确认目标宿主是否只认 plugin.json(决定未来物理重组是否可能)。
- **Phase 1 — 立即 correctness 修(S)** ✅ **已完成(2026-06-29)**:`validate-skill.sh:68` 已加 `-not -path "$REPO_ROOT/reference-oss/*"`(§7-1,我引入的隐患)。已核验 `--status` 仅扫 38 技能、全 OK。
- **Phase 2 — 文案级提升(S,零结构风险)**:memory-management 去 SEO 化 + `_http.py` UA 改名。name/version 字节稳定。
- **Phase 3 — 连接器注册表统一(S,纯文档)**:合并两表 + discipline 标签 + Tier-1 列 + `manual export only` 标记 + ledger/rss 标 both。
- **Phase 4 — 门协议文档提升(M)**:runbook 加 C³/ART veto 行 + cap 对账(§Changelog)。**仅文档那半**;`content-reviewer` 接入留到 §9 决策后。
- **Phase 5 — 构建/CI 去写死(S,先做 Phase 1)**:CI find 换 auto-discovery(带全部排除);golden-math 框架表/路径**就地内联修**或(仅当 §7-2 判定值得)引 `disciplines.md`。
- **Phase 6 — golden-math 守 C³(M,有前置)**:先 c3-benchmark.md 加数值算例,再 golden-math 加写死断言块。
- **Phase 7(产品决策后,条件性)**:若决定 content-reviewer 出 gated 产物 → hook 加 C³ schema(additive/fail-open)+ 影响者 fixture。
- **推迟(需求门控,别现在做)**:学科路由(先播种影响者场景 → 再考虑 `/impact`)、creator-entity、csv_ingest、连接器子目录、`disciplines/`+`platform/` 物理重组。

---

## 9. 待你决策

1. **cap 阈值对账**:runbook §2 的 60/100 vs C³ 的 ≤59(`c3-benchmark.md:34`,C³ Low 段本就封顶 59)。**建议**:把 ≤59 记为"≤60 上限的 band 对齐形式",这样**现有影响者门裁决一个都不漂移**。但无论选哪个,必须 changelog 显式记录(静默改 = 每个现有影响者门裁决移动一分)。
2. **content-reviewer 是否产出持久 gated 产物?** 若是 → 它该过 Artifact Gate(需 §7-3 的 hook C³ schema 或改写本体);若只在对话内 → 维持现状。**这一个决定门控 Phase 7。**
3. **(若上一条为是)影响者门写路径**:走 `memory/audits/influencer/`(统一 Gate 路径,更干净)还是留 `memory/influencer/content-reviewer/` 并加宽 hook glob(保学科局部性)。
4. **学科路由**:接受 `auto.md` 的 IMPACT 路由暂"无支撑"(推迟),还是投入播种影响者场景 + `/impact`?后者要先改写 `api-contract.md:2`("declines non-SEO/GEO")并按 `:21` 治理先播种场景。
5. **`disciplines.md` 要不要建**:仅当去掉那 2 处薄写死后仍有 ≥2 个真实消费者才值得(§7-2);否则内联修更省。格式建议 Markdown 表(与"skills 即内容"一致)。
6. **entity 协议**:确认近期没有影响者技能(fit-scorer/competitor-tracker/performance-analyzer)需要**持久规范创作者档案**。若有 → creator-entity 提升成立;若无 → 保持推迟。

---

## 10. 附:本结论的生成方法

6 维度并行 Map(协议技能 / 连接器 / 框架评分 / 契约状态记忆 / 构建CI / 目录路由)→ 3 个独立架构师(外科手术 / 干净分层 / 面向扩展)→ 评审(外科手术胜出 34.5/40,择优嫁接路由缝、golden-math C³ 前置、content-reviewer 未集成事实)→ 合成 → 对抗式压力测试(`sound-with-fixes`,订正已并入 §7)。其中 2 个 Map agent(框架、契约状态记忆)结构化输出重试超限失败,但其内容已被"协议技能"维度与 3 个架构师方案覆盖;关键事实均已主回路 file:line 复核。
