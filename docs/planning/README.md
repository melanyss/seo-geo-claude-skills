# docs/planning/ — 规划与治理史

本目录保存 aaron-marketing-skills 的**规划文档与治理历史**(已纳入版本库,可见可审)。
区别于 `.gitignore` 掉的 `docs/plans/`(一次性内部草稿):本目录是**保留的**决策记录。

## 文档索引

| 文档 | 状态 | 作用 |
|------|------|------|
| [UNIFIED_OPTIMIZATION_PLAN.md](UNIFIED_OPTIMIZATION_PLAN.md) | 🟢 **LIVE** | **单一活路线图**(single source of truth)。执行、排期、对外沟通一律以此为准。 |
| [OSS_BENCHMARK_PLAN.md](OSS_BENCHMARK_PLAN.md) | ⚪ SUPERSEDED | 支撑分析:三大竞品仓(coreyhaines / kostja94 / ericosiu)借鉴的原始分析。内容已并入 LIVE,不再单独执行。 |
| [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) | ⚪ SUPERSEDED | 支撑分析:平台架构(系统级平台层 vs 学科层)的原始分析。内容已并入 LIVE,不再单独执行。 |
| [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md) | ✅ DONE / 基线 | 内部质量债 P0–P3,已执行完毕(2026-06-28)。作为已完成基线,不再重做。 |

## 规则

- **只改 LIVE**:新决策、新波次、新订正只写进 `UNIFIED_OPTIMIZATION_PLAN.md`。其余三份是冻结存档,仅作溯源,不再编辑(除非订正事实错误)。
- **互链同目录**:四份文档互相用同目录相对链接引用,迁移到本目录后链接保持有效。
- **发布物边界**:这些是内部规划文档,**不属于插件发布物**(不计入 CLAUDE.md 的技能/命令清单,也不在 8 文件追踪清单内)。
