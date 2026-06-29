# aaron-marketing-skills 优化方案 (Optimization Plan) · v2

> **状态:DONE / 基线(P0–P3 已执行,2026-06-28)。** 本文件为已完成的内部质量债基线,**不再重做**;后续一切优化以 [UNIFIED_OPTIMIZATION_PLAN.md](UNIFIED_OPTIMIZATION_PLAN.md) 为单一活路线图。索引见 [README.md](README.md)。

> **基线**:v10.0.0 · 38 skills + 5 commands
> **来源**:全面系统 review(9 维度并行审查 + 对抗式核验)→ 形成 v1 方案 → **对方案本身再做 4 维度 review + 对关键修复做实测** → 形成本 v2
> **日期**:2026-06-28
> **状态**:✅ 已执行(分支 `feature/v10-optimization`,2026-06-28)。P0–P3 全部实施并通过 §8 DoD(12/12);随后对实施本身又做了一轮 5 维度对抗式 review,确认的缺陷(C3-01 content-reviewer 范例、C3-03 fit-scorer 分数封顶、C3-04 ACE 映射、eval 缺 failure_modes 等)已回修。本文件为内部工作文档,未纳入发布物;可自行决定提交/移动/gitignore。

### 本次修订(v1 → v2)要点

v2 把「对方案的 review」结论全部并入。最重要的更正与新增:

- **P0-1 更正**:实测证明 `hb()` 修复本身正确且充分(无第二个代码 Bug)。原先一度怀疑的「BLOCKED 状态应豁免全部三个 cap 字段」是**误判**——runbook 权威段落(§2 表 + §4 自检清单)规定 BLOCKED 产物仍须带 `cap_applied`+`raw_overall_score`,当前网关代码与之一致。真正的缺陷是 runbook **文档自相矛盾**(:64-66 与 §2/§4 冲突),修法是改文档而非改代码。已给 P0-1 加防呆注记,避免误改网关。
- **P1-3 更正**:C³ 文档点名的是 **5 个**技能,原 route A 只接 3 个;新增 **route C(部分接线)**;并把 route A 改为「非默认、需先有 eval 网」。
- **§8 验证节强化**:补 `16 skills` 检查、P2-1/P2-2 的机器可查命令、cmd1 加 `set -e`、标注人工复核项。
- **新增 P3-9/P3-10**:补回 review 中被漏掉的 `evals-not-validated`、`field-array-empty-edge`。
- 修正若干表格 effort 标签、文件计数(7→8)、引用行号小错。

---

## 0. 如何使用本文档

- 全部问题按 **P0 → P3** 四个优先级分批。每批可独立成一个 PR。
- 每个条目给出:**问题 / 位置(file:line) / 根因 / 方案(含 diff 或步骤) / 验证 / 工作量 / 风险 / 依赖**。
- 工作量记号:**S** ≤30min · **M** ~1–2h · **L** 半天以上。
- 凡涉及 **产品决策**(非纯工程)的条目,标注 `⚠ 需决策`,执行前需确认。
- 相关上游仓库已克隆为同级目录:`seo-geo-claude-skills` · `influencer-marketing-agent-skills` · `core-eeat-content-benchmark` · `cite-domain-rating` · `influencer-marketing-c3-benchmark`

---

## 1. 总体评估与核心主题

### 1.1 健康度评分卡

| 维度 | 结论 |
|------|------|
| 版本/清单一致性 | ✅ 干净(38 个全 10.0.0;两份 marketplace.json 字节级一致;清单=磁盘) |
| 契约合规(验证器) | ✅ 38/38 通过,0 失败 |
| 链接完整性 | ✅ 615 条相对链接全可达;runtime 无 blob/main |
| 连接器代码 | ✅ 真·零依赖、编译通过、SSRF 防护有效(测试覆盖偏薄) |
| 框架数学 | ✅ CORE-EEAT 80项/8维、CITE 40项/4维、C³ 9维/CVI 几何平均全部自洽;golden 全过 |
| **Hooks** | 🔴 **Artifact Gate `hb()` 解析 Bug**(随附一处 runbook 文档自相矛盾) |
| 内容质量 / Voice | 🟡 禁用词基本干净;**C³ 框架"空挂"** |
| 文档准确性 | 🟡 CI 漏扫、CONNECTORS 漏配方、追踪清单不一致 |
| 结构覆盖 | 🟡 influencer 半边无 eval、无 references/ 拆分 |

### 1.2 核心主题:一条「20 → 38 迁移债」主线

本仓由「20 个 SEO 技能(`seo-geo-claude-skills`)」+「18 个 influencer 技能(`influencer-marketing-agent-skills`)」合并为 38-skill 伞仓。**表层规范同步到位了,底层基础设施只迁移了一半**:

- 共享契约 / 状态模型 仍停留在「20 skills」表述,influencer 类目与写路径未纳入;
- CI 逐技能校验只扫 5 个 SEO 目录,18 个 influencer 技能从不过结构校验;
- CONNECTORS 配方、eval 用例、references/ 拆分 全部只覆盖 SEO 半边;
- 第三个招牌框架 C³ 数学完美,但没有任何 influencer 技能真正把它接进 instructions。

**几乎所有问题都是这条主线的分支。** 修复策略:先堵运行时/CI 漏洞(P0),再对齐 SSOT 契约(P1),最后补齐文档与覆盖(P2)、清理打磨(P3)。

外加 **1 个与迁移无关的独立 Bug**:Artifact Gate 的 `hb()` 解析逻辑(P0-1,随附一处 runbook 文档自相矛盾的修正)。

---

## 2. 优先级与批次总览

| ID | 问题 | 优先级 | 工作量 | 风险 | 类型 |
|----|------|:------:|:------:|:----:|------|
| P0-1 | Artifact Gate `hb()` 误拒合规审计产物 + runbook 文档矛盾 | 🔴 P0 | S | 低 | Bug+文档 |
| P0-2 | CI 漏扫 18 个 influencer 技能 | 🔴 P0 | S | 低 | CI |
| P0-3 | hook/网关零行为测试 | 🔴 P0 | M | 低 | 测试 |
| P1-1 | skill-contract.md 升级到 38 技能 | 🟠 P1 | M | 低* | SSOT |
| P1-2 | state-model + `memory/influencer/` 入档 | 🟠 P1 | S | 低 | SSOT |
| P1-3 | C³ 框架定位:接线 / 降级 / 部分接线 | 🟠 P1 | S(B/C)/L(A) | 中 | ⚠ 需决策 |
| P2-1 | CONNECTORS 补 influencer 类目配方 | 🟡 P2 | M | 低 | 文档 |
| P2-2 | 统一追踪文件同步清单 | 🟡 P2 | S | 低 | 文档 |
| P2-3 | influencer eval 用例(或显式标注缺口) | 🟡 P2 | S(最小)/L(完整) | 低 | 覆盖 |
| P2-4 | 连接器纯函数单测 + 接入 CI | 🟡 P2 | M | 低 | 测试 |
| P2-5 | references/ 与 3 个 SSOT benchmark 仓同步核对 | 🟡 P2 | S | 低 | 一致性 |
| P3-* | 打磨清单(10 项) | 🟢 P3 | S each | 低 | 打磨 |

\* P1-1 风险标「低」仅指「非可执行文本、不会崩溃」;但它是仓内被引用最多的 SSOT(45 个文件回链),且要新增结构化内容块(见 P1-1「风险」栏),correctness 面不小,执行需「低风险 / 中谨慎」。

---

## 3. 批次一 · P0 — 功能性 Bug 与 CI 盲区

> 目标:堵住「运行时强制机制失效」和「半数技能无 CI」两个真窟窿。三项都小而确定,建议合一个 PR。

### P0-1 · 修复 `hb()` 解析 + 对齐 runbook 文档(无第二个代码 Bug)

- **位置**:[hooks/claude-hook.sh:17](../../hooks/claude-hook.sh:17)(网关逻辑在 [:39](../../hooks/claude-hook.sh:39));文档矛盾在 [references/auditor-runbook.md:64-66](../../references/auditor-runbook.md:64) vs [:100](../../references/auditor-runbook.md:100) / [:125-127](../../references/auditor-runbook.md:125)
- **问题**:`hb()` 抽取审计产物正文时,`a&&p&&!NF{exit}` 会**在第一个空行处停止**。标准格式([auditor-runbook.md:49-54](../../references/auditor-runbook.md:49))在 `cap_applied / raw_overall_score / final_overall_score` 这组前面留了空行 → 这三个字段被丢弃 → 网关报「missing …」并 **BLOCK 全部合规产物**。已实测复现(删掉空行才 PASS)。
- **根因**:`hb()` 把「正文区」误当成「到首个空行为止的第一段」。
- **方案 ①(代码,最小手术,只删不增逻辑)**:

  ```diff
  -hb(){ awk 'NR==1&&$0=="---"{i=1;next}i&&$0=="---"{a=1;next}a&&NF{p=1;print;next}a&&p&&!NF{exit}' "$1"; }
  +hb(){ awk 'NR==1&&$0=="---"{i=1;next}i&&$0=="---"{a=1;next}a&&NF{print}' "$1"; }
  ```

  改后:打印闭合 frontmatter 之后的**全部非空行**,忽略内部空行,永不提前退出。`field()`/`kf()` 本就按 `key:` 行扫描,空行与 `#` 注释行不影响,故无需改它们。**已实测**:`good`(合规)→ PASS;`missing`(非 BLOCKED 缺 final)→ BLOCK;`blocked_withcap`(合规 BLOCKED:带 `cap_applied:false`+`raw_overall_score`、无 final)→ PASS。
- **🛑 防呆注记(重要)**:网关第 39 行对 BLOCKED 的处理是**正确的**,**不要去改它**。它要求 BLOCKED 产物仍带 `cap_applied`+`raw_overall_score`、仅豁免 `final_overall_score`——这与权威的 §2 场景表([:100](../../references/auditor-runbook.md:100):「2+ veto → BLOCKED,`raw_overall_score` retained,`cap_applied: false`」)和 §4 自检清单([:125-127](../../references/auditor-runbook.md:125))一致。**没有第二个代码 Bug。** 一个完全没有 cap 字段的 BLOCKED 产物按 §2/§4 本就是不合规的,网关拦它是对的。
- **方案 ②(文档,修自相矛盾)**:runbook 的旧版兼容散文 [:64-66](../../references/auditor-runbook.md:64) 写「missing `cap_applied`, `raw_overall_score`, or `final_overall_score` (unless `status: BLOCKED`)」,其括号读起来像豁免**全部三个**,与 §2/§4(仅豁免 `final_overall_score`)冲突。**把 :64-66 改成与 §2/§4 一致**:BLOCKED 下仍需 `cap_applied`+`raw_overall_score`,仅 `final_overall_score` 可省。一行散文修订,**不动代码**。
- **验证**:见 P0-3 测试 + §8 cmd4(必须覆盖「合规 BLOCKED → PASS」与「缺 cap 字段 BLOCKED → BLOCK」两种)。
- **工作量**:S · **风险**:低(fail-closed,且 `memory/audits/` 当前仅 `.gitkeep`,无线上产物受影响) · **依赖**:无

### P0-2 · CI 加入 6 个 influencer 目录

- **位置**:[.github/workflows/validate-skill.yml:64-66](../../.github/workflows/validate-skill.yml:64)
- **问题**:逐技能校验的 `find` 只列了 5 个 SEO 目录,18/38 技能从不过结构校验(契约段落、frontmatter、blob/main 守卫)。
- **方案**:

  ```diff
  -          find research build optimize monitor cross-cutting \
  +          find research build optimize monitor cross-cutting \
  +            insight map plan activate convert track \
               -mindepth 2 -maxdepth 2 -name SKILL.md \
               -print | sort | while read -r file; do
  ```
- **验证**:`find … | wc -l` = 38;影响范围内 18 个 influencer 技能各产 1 条 references/ warning 但 `exit 0`(已实测),故 `pipefail` 下 CI 仍绿。
- **优先级批注**:源 review 将此项核验为 **medium**;此处升到 P0,理由是它与 P0 的 hook 修复同属「合并任何 influencer 改动前必须先有的结构门禁」,且修复成本极低、与 P0 同批最省事——是有意的升档,非误判。
- **工作量**:S · **风险**:低 · **依赖**:无

### P0-3 · 为 hook / Artifact Gate 补行为测试并接入 CI

- **位置**:新增 `tests/test_hook_artifact_gate.sh`;CI 在 [validate-skill.yml:89](../../.github/workflows/validate-skill.yml:89)(现有 `bash -n` hook 解析步骤)旁新增一步
- **问题**:CI 对 hook 只做 `bash -n`(语法检查),从不喂 JSON 断言行为。仓库逻辑最密集的唯一运行时文件零行为测试——这正是 P0-1 的 `hb()` Bug 能悄悄上线的原因。
- **方案**:新建 `tests/test_hook_artifact_gate.sh`,用 here-doc 造 fixture 写入临时 `memory/audits/*.md`,管道喂入 `bash hooks/claude-hook.sh post-tool-use`,**断言全部以下用例**(均已在实测中验证过预期):
  1. 合规产物(cap 组前带空行)→ **不** block;
  2. 非 BLOCKED 缺 `final_overall_score` → block(reason 含字段名);
  3. **合规 BLOCKED**(带 `cap_applied:false`+`raw_overall_score`、无 `final_overall_score`)→ **不** block;
  4. **缺 `cap_applied`/`raw_overall_score` 的 BLOCKED** → block(确认 §2/§4 不合规仍被拦);
  5. SessionStart 注入清洗:含 `ignore previous instructions` 的 hot-cache → 输出含 `[redacted`;软链 hot-cache → 无输出。
  - CI 增一步:`- name: Hook behavior tests` → `run: bash tests/test_hook_artifact_gate.sh`。
- **验证**:`bash tests/test_hook_artifact_gate.sh` 退出 0;在未修 P0-1 的分支上运行,用例 1 与 3 应**失败**(证明测试有效)。
- **工作量**:M · **风险**:低 · **依赖**:P0-1(用例 1/3 以修复后行为为准)

---

## 4. 批次二 · P1 — SSOT 契约对齐

> 目标:让「共享契约 / 状态模型」真正覆盖全部 38 个技能,消除迁移债的根。

### P1-1 · skill-contract.md 升级到 38 技能

- **位置**:[references/skill-contract.md:3](../../references/skill-contract.md:3) · [:208](../../references/skill-contract.md:208) · [:174-204 Category Defaults](../../references/skill-contract.md:174) · [:304-315 Write Paths](../../references/skill-contract.md:304)
- **问题**:CLAUDE.md 指定它为全部 38 技能的共享契约(18 个 influencer 技能也确实回链它),但正文仍写「all **20** skills」「Execution Layer (16) / Protocol Layer (4)」,且类目默认值与写路径表只覆盖 5 个 SEO 类目。
- **方案**:
  - line 3:`all 20 skills` → `all 38 skills`;
  - line 208:`Execution Layer (16 skills) | Protocol Layer (4 skills)` → `Execution Layer (34 skills) | Protocol Layer (4 skills)`;
  - **Category Defaults** 增 Influencer(IMPACT)块,列出 6 个阶段 Insight/Map/Plan/Activate/Convert/Track 的 Reads/Writes/Promotes 默认值;
  - **Write Paths** 表增一行:`Influencer (18 skills) | memory/influencer/<skill>/ | 受众/创作者/活动/ROI 产物`;
  - 在框架引用处把 C³ 与 CORE-EEAT/CITE 并列(交叉链接 [references/c3-benchmark.md](../../references/c3-benchmark.md))。
- **风险(更正,原标「纯文档/低」被指出低估)**:它是仓内被引用最多的 SSOT(45 个文件回链),且这不是 line-3 的查找替换,而是**新增结构化内容块**(Category Defaults 子节 + Write Paths 行)。新增块若与 18 个技能各自的 `Writes:` 路径不一致,会把迁移债漂移再扩散一次。重标:**runtime 风险低 / correctness 谨慎度中**。
- **验证(机器可查,强制)**:对每个 influencer SKILL.md `grep` 其 `Writes:` 路径,断言其逐字出现在新 Write-Paths 行;`grep -c '20 skills'` 与 `grep -c '16 skills'` **均 => 0**;line-3/line-208/结构块放**同一 commit**,避免文档处于半迁移态。
- **工作量**:M · **风险**:低*/中谨慎 · **依赖**:无

### P1-2 · state-model.md 纳入 `memory/influencer/`

- **位置**:[references/state-model.md](../../references/state-model.md)(WARM 区,参照 :126 `memory/research/` 写法)
- **问题**:全部 18 个 influencer 技能写 `memory/influencer/<skill>/`,但状态模型 0 命中该树;负责 WARM→COLD 归档的 `memory-management` 只按 SEO 路径写文档 → influencer WARM 层无归档负责人。
- **方案**:新增 `### memory/influencer/`(WARM)小节;在 `memory-management` 的归档/清理步骤里把 `memory/influencer/` 与 research/audits/monitoring 并列。
- **验证**:`grep -n 'memory/influencer' references/state-model.md cross-cutting/memory-management/SKILL.md` 均有命中。
- **工作量**:S · **风险**:低 · **依赖**:与 P1-1 同批提交

### P1-3 · C³ 框架定位 — 接线 / 降级 / 部分接线 ⚠ 需决策

- **位置**:[references/c3-benchmark.md:68-70](../../references/c3-benchmark.md:68) ↔ 它点名的 **5 个**技能:[map/fit-scorer](../../map/fit-scorer/SKILL.md)(ACE)、[map/influencer-discovery](../../map/influencer-discovery/SKILL.md)(按 ACE 筛)、[activate/content-reviewer](../../activate/content-reviewer/SKILL.md)(ART,T1/T2 veto)、[track/roi-calculator](../../track/roi-calculator/SKILL.md)(CVI)、[track/performance-analyzer](../../track/performance-analyzer/SKILL.md)(ROI/CVI 汇总)
- **问题**:C³ 数学完美,但是「空挂」——c3-benchmark.md:68-70 宣称上述 **5 个**技能已集成,实际:content-reviewer 用 ad-hoc「✅/❌」无 veto ID、roi-calculator 完全不提 CVI、fit-scorer 用自己的 **5 维 1–5 加权量表**(非 ACE)、influencer-discovery 与 performance-analyzer 也未按 ACE/CVI 执行。链接方向也是反的(C³ 点名的两个网关反而不链接它)。
- **三条路线(需拍板)**:
  - **路线 A — 全量接线(最彻底,工作量大,非默认)**:让全部 **5 个**被点名技能像 SEO build 技能加载 CORE-EEAT 那样 in-body 重述并执行 C³ 规则(ACE 含 A2/C1/E2 veto、ART 强制 T1/T2、CVI 汇总)。⚠ 注意:这会把 3 个最大的技能(464–521 行)进一步推过 P3-1 的 250 行建议线;且 influencer 半边 **0 eval 覆盖**,无回归网——**必须先完成 P2-3 的相关 eval(至少 fit-scorer/content-reviewer)再做**。
  - **路线 B — 全量降级表述(快,诚实)**:在 c3-benchmark.md 与 README/CLAUDE/AGENTS 把 C³ 表述为「参考评分量表,非强制集成」,删除「content-reviewer gates on ART」等宣称已集成的措辞。
  - **路线 C — 部分接线(推荐折中,最贴合仓库 surgical 风格)**:只给 **3 个网关关键**技能(fit-scorer 出 ACE、content-reviewer 强制 T1/T2 veto ID、roi-calculator 出 CVI)真接线;对 **2 个支撑**技能(influencer-discovery、performance-analyzer)把 c3-benchmark.md 的措辞从「已集成」降为「informs/contributes」。这样文档不再说谎,改动面最小。
- **无条件子任务(无论选哪条路线都做)**:修正 C³ 反向链接——给 content-reviewer 与 roi-calculator 补 c3-benchmark 链接(它们是被点名的网关却没链),或在降级时同步删除对应宣称。**单列于此,确保不会因为选了路线 B 而丢失。**
- **建议**:若 C³ 是对外卖点 → 路线 A(但排在 P2-3 之后);否则 → 路线 C 立即消除「文档说谎」且最省。**先定路线再排期。** 注意:路线 A/C 的接线**无法**用 `golden-auditor-math.py` 验证(它只校验框架数学,不校验技能接线),只能人工/eval 复核。
- **工作量**:A=L / B=S / C=S–M · **风险**:中(A/C 改技能正文,需回归) · **依赖**:决策;**且路线 A 依赖 P2-3 先完成**

---

## 5. 批次三 · P2 — 文档与覆盖补齐

### P2-1 · CONNECTORS.md 补 influencer 类目配方

- **位置**:[CONNECTORS.md:76-94](../../CONNECTORS.md:76)
- **问题**:类目表只列 SEO 占位符;influencer 高频用 `~~social platform analytics`(19×)、`~~influencer database`(17×)及约 10 个其它 `~~` 类目全无配方,违背 CLAUDE.md「a free/keyless recipe **for each category**」。
- **方案**:新增 Influencer/IMPACT 行,给每个 `~~` 类目配示例工具 + Tier-1 免费回退(如 `~~social platform analytics → 平台原生 creator/insights API`;`~~influencer database → Modash/HypeAuditor + 手动 CSV 回退`)。无法给免费配方的,明确标注「Tier 1 手动输入」。
- **验证(机器可查)**:见 §8 cmd7——枚举 influencer 技能里所有 `~~` token 并逐一 `grep` CONNECTORS.md,应无 MISSING 输出。
- **工作量**:M · **风险**:低

### P2-2 · 统一追踪文件同步清单

- **位置**:[CLAUDE.md:77](../../CLAUDE.md:77) · [AGENTS.md:60](../../AGENTS.md:60) · [CONTRIBUTING.md:69-76](../../CONTRIBUTING.md:69)
- **问题**:三处对「改版本/计数后同步哪些文件」给出三种清单(AGENTS.md 甚至漏了 marketplace 镜像),且都没列 `AGENTS.md` 和 `docs/README.zh.md`——而这两个文件恰恰都带版本号与计数 → 漂移入口。
- **方案**:在 CONTRIBUTING.md 立一份权威清单(见 §9.2 的 8 个文件);CLAUDE.md / AGENTS.md 改为**指向**它而非各自重述。
- **验证**:见 §8 cmd8。
- **工作量**:S · **风险**:低

### P2-3 · influencer eval 覆盖

- **位置**:[evals/](../../evals/) · [evals/README.md](../../evals/README.md)
- **问题**:20/20 SEO 技能有 `cases.md`,0/18 influencer 技能有;且无任何文档说明这是已知缺口。
- **方案**(二选一):
  - **最小**:在 evals/README.md 加一行,声明当前种子集仅覆盖 SEO/GEO,influencer 用例为待补缺口 → 把「未文档化的洞」转为「已文档化的限制」。
  - **完整**:按 SEO 种子模式给 18 个 influencer 技能补 `cases.md`(status: simulated),**优先 C³ veto 相关的 fit-scorer / content-reviewer**(它们是 P1-3 路线 A 的回归前置)。
- **工作量**:最小 S / 完整 L · **风险**:低 · **被依赖**:P1-3 路线 A

### P2-4 · 连接器纯函数单测 + 接入 CI

- **位置**:[tests/test_connectors_local.py](../../tests/test_connectors_local.py)
- **问题**:13 个用户向连接器只测 3 个;且这 3 个测试**未接入 CI**(CI 只 `py_compile`)。最被宣传的纯函数裸奔:`robots.can_fetch` 最长匹配优先级、`psi.grade` CWV 分级、`ledger.cmd_diff` 增量、`openpagerank.parse_response`。
- **方案**:为上述纯函数补离线单测(无网络);CI 增 `python3 tests/test_connectors_local.py` 一步。注意该测试文件**已存在并通过**,本项是**扩充用例 + 接入 CI**,不是新建。
- **验证**:`python3 tests/test_connectors_local.py` 退出 0,用例数 > 现有 3 个。
- **工作量**:M · **风险**:低

### P2-5 · references/ 与 3 个 SSOT benchmark 仓同步核对

- **位置**:本仓 `references/{core-eeat-benchmark,cite-domain-rating,c3-benchmark}.md` + `references/c3/` ↔ 同级 `core-eeat-content-benchmark` / `cite-domain-rating` / `influencer-marketing-c3-benchmark`
- **问题**:伞仓的框架文件是上游 benchmark 仓的副本;需确认未偏离 SSOT(条目数、veto ID、权重、CVI 公式)。
- **方案**:对三对文件做结构化 diff(条目数、veto 编号、权重表、公式),记录差异;若上游更新,回流伞仓。`golden-auditor-math.py` 已验证伞仓内部自洽,本步验证**跨仓**一致。
- **验证**:**人工复核**——产出一份「伞仓 vs SSOT」差异清单;无实质差异则记录「已对齐」。(无自动化命令。)
- **工作量**:S · **风险**:低

---

## 6. 批次四 · P3 — 打磨清单

> 全部为低风险小改,可零散搭车进任意 PR。

| ID | 问题 | 位置 | 方案 |
|----|------|------|------|
| P3-1 | 18 个 influencer 技能单体 415–603 行、无 references/ 拆分,每个触发验证器 >250 行 warning | 各 influencer SKILL.md | **推荐**:让验证器把「链接共享 references/c3/ 包」视为满足该 advisory(一行改 [validate-skill.sh:217](../../scripts/validate-skill.sh:217),零技能 churn)。仅当 §7 设计意图判定「应拆分」时,才做 per-skill references/ 抽取(churn 大,改 18 个健康技能)。**先答 §7 再动手。** |
| P3-2 | `_http.get` 网络错误**最后一次尝试后仍 sleep**(浪费 ~4s) | [_http.py:90](../../scripts/connectors/_http.py:90) | `time.sleep(2 ** attempt)` → `if attempt < retries - 1: time.sleep(2 ** attempt)`(对齐 :77 的 429/503 分支) |
| P3-3 | crawl 用**重定向前** host 过滤 → apex→www 起始 URL 只爬一页 | [crawl.py:103](../../scripts/connectors/crawl.py:103),[:134](../../scripts/connectors/crawl.py:134) | 首个成功抓取后以落地 host 重定基:`if not results: host = urlparse(final_url).netloc.lower() or host` |
| P3-4 | `memory/` 只 scaffold 了 6 个 WARM/COLD 子目录中的 2 个 | [memory/](../../memory/) | 补 `.gitkeep`(research/content/monitoring/archive),或在 state-model 注明「惰性创建」 |
| P3-5 | SISTRIX MCP 端点尾斜杠不一致 | [CONNECTORS.md:111](../../CONNECTORS.md:111) ↔ [.mcp.json:17](../../.mcp.json:17) | 二者对齐(去掉 CONNECTORS 的尾 `/`) |
| P3-6 | on-page-seo-auditor 描述用「For X use Y」而非规范的「Not for X — use Y」 | [optimize/on-page-seo-auditor/SKILL.md:3](../../optimize/on-page-seo-auditor/SKILL.md:3) | 改为 canonical 边界措辞 |
| P3-7 | ISSUE_TEMPLATE 无 bug-report 模板 | [.github/ISSUE_TEMPLATE/](../../.github/ISSUE_TEMPLATE/) | 加轻量 `bug-report.yml` |
| P3-8 | 三处「landscape」边缘用法(其余 Output Voice 已干净,属自选收紧,非确认缺陷) | trend-spotter:81 / niche-researcher:348 / commands/research.md:22 | 把两处小标题改为「Current Trends」「Competitive Map」;commands/research.md:22 去掉比喻义。**注意**:source review 将 Voice 维度评为「干净」,brief-generator:445 的「Landscape」是图片方向词,**勿动**。 |
| **P3-9** | 验证器/CI 从不检查 eval 是否存在——这是 P2-3 症状的根因,补回 | [scripts/validate-skill.sh](../../scripts/validate-skill.sh) | 加一条**非致命** warn:技能目录无对应 `evals/<skill>/cases.md` 时提示(仿现有 >250 行 references/ advisory)。或在 P2-3 明确「eval 校验有意不入门禁」。 |
| **P3-10** | `field()` 对「key 后空值且无续行」判为缺失(与 cap 字段路径相关的 hook 边缘) | [hooks/claude-hook.sh:18](../../hooks/claude-hook.sh:18) | 当前正常格式总给 cap 字段内联值,故**默认不改 `field()`**;但在 P0-3 补一个 fixture(cap 字段同行内联值 → PASS),并显式记录「`field()` 按设计保留」,避免该边缘悬空。 |

---

## 7. 不在本次范围 / 需要决策

- **P1-3 C³ 路线 A / B / C** —— 核心产品决策,决定后才能给 C³ 部分排期。若选 A,**必须**先做 P2-3 的相关 eval。
- **influencer 技能架构是否「故意内联」** —— 若认定单体内联是有意为之,则 P3-1 走「放宽验证器阈值」(推荐);否则才做 references/ 抽取。需先确认设计意图,**不要在答案出来前 churn 18 个健康技能**。
- **influencer eval 是否要做完整 18 个** —— 取决于是否把 eval 作为长期质量门(当前自述为「轻量模拟、非 CI 门禁」)。

---

## 8. 验收标准(整体完成后如何验证)

```bash
# 1. 全量结构校验(含 influencer)——CI 形式,单个失败即中止(P0-2)
set -euo pipefail
find research build optimize monitor cross-cutting insight map plan activate convert track \
  -mindepth 2 -maxdepth 2 -name SKILL.md | sort | while read -r f; do
  bash scripts/validate-skill.sh "$(dirname "$f")"; done
bash scripts/validate-skill.sh --status        # 全 OK,无 SPLIT/CORRUPTION

# 2. 框架数学 golden(始终全过;回归基线,非任何 item 的产物)
python3 scripts/golden-auditor-math.py

# 3. 连接器编译 + 单测(文件已存在并通过;P2-4 扩充用例 + 接入 CI 后用例数应 > 3)
python3 -m py_compile scripts/connectors/*.py scripts/golden-auditor-math.py
python3 tests/test_connectors_local.py

# 4. hook 行为测试(P0-3 新增)——必须覆盖 5 个用例:
#    good→PASS · 非BLOCKED缺final→BLOCK · 合规BLOCKED(带cap_applied+raw_overall_score,无final)→PASS
#    · 缺cap_applied/raw_overall_score的BLOCKED→BLOCK · 注入清洗+软链拒绝
bash tests/test_hook_artifact_gate.sh

# 5. 契约 20→38 迁移完成(P1-1/P1-2)——两个陈旧计数都要归零
grep -c '20 skills' references/skill-contract.md     # => 0  (line 3)
grep -c '16 skills' references/skill-contract.md     # => 0  (line 208 Execution Layer)
grep -n 'memory/influencer' references/skill-contract.md references/state-model.md  # 均有命中

# 6. 两份 marketplace 仍字节一致
diff -q marketplace.json .claude-plugin/marketplace.json

# 7. CONNECTORS 覆盖全部 influencer ~~ 类目(P2-1)。占位符是反引号包裹的,逐行安全迭代(勿用
#    `for t in $(...)`——会按空格拆开 `~~social platform analytics` 这类多词 token)。修复前会列出
#    18 个缺失类目(已实测),P2-1 后应无输出。
grep -rhoE '`~~[^`]+`' insight map plan activate convert track --include=SKILL.md \
  | tr -d '`' | sort -u | while IFS= read -r t; do
    grep -qF "$t" CONNECTORS.md || echo "MISSING recipe: $t"; done   # 修复后应无输出

# 8. 追踪清单一致(P2-2)——CONTRIBUTING 为权威,且含 AGENTS.md + zh README
grep -q 'AGENTS.md' CONTRIBUTING.md && grep -q 'README.zh' CONTRIBUTING.md && echo "tracking list updated"

# 人工复核项(无自动化命令):P1-3(C³ 接线/降级与技能行为一致)、P2-5(跨仓 benchmark 比对)
```

**完成定义(DoD)**:cmd1–8 全绿;CI 在 PR 上对 38 个技能逐个校验且含 hook 行为测试;C³ 文档与技能行为一致(按所选路线人工确认,含被点名的全部 5 个技能);CONNECTORS 覆盖全部 `~~` 类目(cmd7 无输出);追踪清单三处一致且含 §9.2 的 8 个文件。

---

## 9. 附录

### 9.1 文件影响清单(按批次)

- **P0**:`hooks/claude-hook.sh`、`.github/workflows/validate-skill.yml`、`tests/test_hook_artifact_gate.sh`(新)、`references/auditor-runbook.md`(P0-1 文档修订)
- **P1**:`references/skill-contract.md`、`references/state-model.md`、`cross-cutting/memory-management/SKILL.md`、`references/c3-benchmark.md`;(路线 A/C)`map/fit-scorer/SKILL.md`、`activate/content-reviewer/SKILL.md`、`track/roi-calculator/SKILL.md`,(仅路线 A 另含)`map/influencer-discovery/SKILL.md`、`track/performance-analyzer/SKILL.md`
- **P2**:`CONNECTORS.md`、`CLAUDE.md`、`AGENTS.md`、`CONTRIBUTING.md`、`evals/README.md`(+ 可选 18 个 `evals/<skill>/cases.md`)、`tests/test_connectors_local.py`;(P2-5,条件性)`references/core-eeat-benchmark.md`、`references/cite-domain-rating.md`、`references/c3-benchmark.md`、`references/c3/*`(仅在与上游 SSOT 有偏差需回流时)
- **P3**:`scripts/connectors/_http.py`、`scripts/connectors/crawl.py`、`scripts/validate-skill.sh`(P3-1 阈值 + P3-9 eval warn)、`memory/*`、`.mcp.json`、`optimize/on-page-seo-auditor/SKILL.md`、`.github/ISSUE_TEMPLATE/bug-report.yml`(新)、`insight/trend-spotter/SKILL.md`、`insight/niche-researcher/SKILL.md`、`commands/research.md`、`hooks/claude-hook.sh`(P3-10 仅加测试 fixture,代码默认不改);**P3-1 若走「拆分」路线另含全部 18 个 influencer SKILL.md**

### 9.2 发布后必须同步的追踪文件(P2-2 的权威清单 —— 8 个文件,其中 marketplace 两份为镜像对)

`VERSIONS.md` · `.claude-plugin/plugin.json` · `marketplace.json` · `.claude-plugin/marketplace.json`(镜像) · `README.md` · `CLAUDE.md` · `AGENTS.md` · `docs/README.zh.md`

### 9.3 已验证为「健康、无需改动」的部分(避免误动)

版本治理 · 清单/磁盘一致性 · 相对链接完整性 · 连接器零依赖与 SSRF 防护 · 三大框架数学与 golden 校验 · 验证器与契约 heading 一致性 · Output Voice 禁用词合规 · hook 的清洗/软链拒绝/fail-open/最小-PATH 安全姿态 · **Artifact Gate 对 BLOCKED 的 cap 字段处理(§2/§4 一致,见 P0-1 防呆注记)**——以上勿动,除 P0-1 的 `hb()` 一行。

### 9.4 方案自查留痕(v2 已并入的更正)

| 来源发现 | 处理 |
|----------|------|
| 「P0-1 有第二个代码 Bug / 应豁免全部 cap 字段」 | **撤销**——实测证明是误判;改为「`hb()` 修复 + runbook :64-66 文档对齐 + 防呆注记」 |
| P1-3 route A 只接 3 个技能(C³ 实际点名 5 个) | 已扩为 5 个;新增 route C;反向链接修正改为无条件子任务 |
| route A 被无条件「推荐」且无回归网 | 已改为非默认 + 依赖 P2-3 先行 |
| §8 cmd5 漏检 `16 skills` | 已补 cmd5 第二条 grep |
| 多个 item 无 §8 验证命令 | 已补 P2-1(cmd7)、P2-2(cmd8);P1-3/P2-5 标人工复核 |
| §2 effort 标签与正文矛盾(P1-3/P2-3) | 已改为 `S(B/C)/L(A)`、`S(最小)/L(完整)` |
| §9.2「7 文件」与列表「8 文件」矛盾 | 统一为 8(注明 marketplace 镜像对) |
| §9.1 漏 P2-5 references / P3-1 拆分的 18 技能 | 已补 |
| `evals-not-validated`、`field-array-empty-edge` 被漏 | 已补为 P3-9、P3-10 |
| 引用小错(.mcp.json:16、P0-3 行号、fit-scorer「/100」) | 已更正为 :17、:89、「5 维 1–5 加权量表」 |
| P0-2 升档至 P0 vs review 的 medium | 已加优先级批注说明理由 |
