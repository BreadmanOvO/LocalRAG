# README Homepage Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `README.md` into a concise project homepage and split the existing long-form planning content into focused documents under `docs/`.

**Architecture:** Keep `README.md` as a navigation-first entry point with only current status, near-term priorities, roadmap summary, success targets, and doc links. Move the detailed planning, evaluation, resume/interview framing, and reference material into four focused markdown files so the repo can evolve from planning docs to implementation docs without losing context.

**Tech Stack:** Markdown, Git, repository docs under `README.md` and `docs/*.md`

---

## File Structure

- `README.md` — homepage-style entry point with project summary, current status, next steps, roadmap summary, doc navigation, success criteria, and repo notes.
- `docs/roadmap.md` — detailed version roadmap, technical decisions, architecture overview, development checklist, risks, and timeline strategy.
- `docs/evaluation.md` — evaluation framework, synthetic dataset rules, metrics definitions, and evaluation workflow.
- `docs/resume_notes.md` — resume framing, project highlights, interview talking points.
- `docs/references.md` — external resources, learning path, and domain references.

### Task 1: Rewrite README homepage

**Files:**
- Modify: `README.md`
- Reference: `docs/superpowers/specs/2026-04-09-readme-homepage-redesign-design.md`
- Reference: `docs/roadmap.md`
- Reference: `docs/evaluation.md`
- Reference: `docs/resume_notes.md`
- Reference: `docs/references.md`

- [ ] **Step 1: Replace the current top section with a homepage-focused structure**

```md
# 自动驾驶感知算法 RAG 项目

## 项目简介
一句话说明项目目标、领域范围和核心价值。

## 当前定位
- 项目状态：规划阶段
- 当前目标版本：v1.0 Baseline
- 当前最高优先级：先建立评估基线，再推进数据与检索升级
- 仓库内容：当前以规划与设计文档为主
```

- [ ] **Step 2: Add a real-status overview table that only states current facts or explicit next steps**

```md
## 当前状态总览

| 模块 | 当前状态 | 说明 | 下一步 |
| --- | --- | --- | --- |
| 数据源 | 已规划 | 已明确 Apollo、论文、技术文章等候选来源 | 整理首批核心文档 |
| 切分 | 计划中 | 当前仅有固定长度切分方案说明 | 落实语义切分方案 |
| 检索 | 计划中 | 已确定 v1.2 聚焦 HyDE + 混合检索 | 先完成 baseline 检索评估 |
| 评估 | 优先准备中 | 已确定 Ragas + LLM-as-a-Judge 方向 | 设计并生成首批评测集 |
| 模型 | 计划中 | 已确定 QLoRA 为必做、DPO 为可选 | 待 v1.2 后推进 |
| 部署 | 计划中 | 当前无运行入口与部署脚本 | 后续在 v1.4 再推进 |
| 文档 | 进行中 | 正在把首页改造成开发导航页 | 拆分详细 docs 文档 |
```

- [ ] **Step 3: Add action-oriented sections for current stage, roadmap summary, doc navigation, success criteria, and repo notes**

```md
## 当前阶段与下一步
- 当前阶段：v1.0 Baseline 规划中
- 本周重点：梳理评估框架、明确数据集结构、整理开发入口文档
- 下一步任务：
  1. 生成首批评测三元组
  2. 实现 Ragas 评估脚本
  3. 实现 LLM-as-a-Judge 评估脚本
  4. 产出 baseline 指标记录模板
- 优先级提醒：整体规划很多，但实际开发阶段要优先保证 v1.2 检索收益

## 开发路线图
| 版本 | 核心目标 | 关键产出 | 状态 |
| --- | --- | --- | --- |
| v1.0 | 建立评估基线 | 测试集与双评估框架 | 规划中 |
| v1.1 | 升级数据层 | 文档采集、解析、切分 | 计划中 |
| v1.2 | 升级检索层 | HyDE + 混合检索 + Rerank | 计划中 |
| v1.3 | 升级模型层 | QLoRA / DPO | 计划中 |
| v1.4 | 优化性能与部署 | llama.cpp 优化与部署整理 | 计划中 |

## 文档导航
- [详细版本规划](docs/roadmap.md)
- [评估框架与指标](docs/evaluation.md)
- [简历表达与面试亮点](docs/resume_notes.md)
- [参考资料与学习路径](docs/references.md)

## 成功标准
- 检索效果：目标提升 Top-k 召回与排序质量
- 回答质量：目标提升 faithfulness 与评审胜率
- 系统性能：目标控制端到端延迟与 TTFT
- 领域覆盖：覆盖感知、规划、安全等核心主题

## 仓库说明
当前仓库以规划文档为主；后续代码、脚本和评估结果会随版本推进逐步补齐。
```

- [ ] **Step 4: Verify README wording against the design constraints**

Run: `python - <<'PY'
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
for heading in ['## 项目简介', '## 当前定位', '## 当前状态总览', '## 当前阶段与下一步', '## 开发路线图', '## 文档导航', '## 成功标准', '## 仓库说明']:
    assert heading in text, heading
print('README headings verified')
PY`
Expected: `README headings verified`

- [ ] **Step 5: Commit**

```bash
git add README.md docs/roadmap.md docs/evaluation.md docs/resume_notes.md docs/references.md
git commit -m "docs: reorganize README into project homepage"
```

### Task 2: Create roadmap document

**Files:**
- Create: `docs/roadmap.md`
- Source: `README.md` (current long-form version before rewrite)

- [ ] **Step 1: Create the roadmap doc header and preserve the project framing**

```md
# 版本规划与技术路线

## 项目定位
- 自动驾驶感知算法垂直领域专家系统
- 目标时间：6 周分版本迭代
- 核心原则：评估先行、数据驱动、渐进优化
```

- [ ] **Step 2: Move the detailed version roadmap and per-version deliverables into this file**

```md
## 版本路线图
### v1.0 Baseline
- 建立合成测试集
- 建立 Ragas + LLM-as-a-Judge 双评估框架
- 记录 baseline 指标

### v1.1 数据层
- 收集核心文档
- 引入多模态解析
- 升级语义切分与元数据
```

- [ ] **Step 3: Move the non-evaluation technical decisions, architecture overview, development checklist, risks, and timeline strategy here**

```md
## 技术决策
## 项目架构概览
## 开发任务清单
## 风险与应对
## 时间管理策略
```

- [ ] **Step 4: Verify the roadmap doc contains all required top-level sections**

Run: `python - <<'PY'
from pathlib import Path
text = Path('docs/roadmap.md').read_text(encoding='utf-8')
for heading in ['# 版本规划与技术路线', '## 版本路线图', '## 技术决策', '## 项目架构概览', '## 开发任务清单', '## 风险与应对', '## 时间管理策略']:
    assert heading in text, heading
print('roadmap sections verified')
PY`
Expected: `roadmap sections verified`

### Task 3: Create evaluation document

**Files:**
- Create: `docs/evaluation.md`
- Source: `README.md` (current long-form version before rewrite)

- [ ] **Step 1: Create the evaluation doc with the framework overview**

```md
# 评估框架与指标口径

## 评估目标
- 建立可复用的 baseline 评估体系
- 用统一指标比较各版本改进效果
```

- [ ] **Step 2: Move the evaluation strategy, synthetic data rules, and metric definitions into dedicated sections**

```md
## 双评估框架
## 合成数据生成原则
## 评估数据构建原则
## 指标说明
```

- [ ] **Step 3: Keep the wording explicit that these are planned evaluation methods and target practices, not completed results**

```md
## 使用说明
当前文档描述的是规划中的评估体系与指标口径，后续版本落地后再补充真实结果。
```

- [ ] **Step 4: Verify the evaluation doc contains the expected headings**

Run: `python - <<'PY'
from pathlib import Path
text = Path('docs/evaluation.md').read_text(encoding='utf-8')
for heading in ['# 评估框架与指标口径', '## 评估目标', '## 双评估框架', '## 合成数据生成原则', '## 评估数据构建原则', '## 指标说明']:
    assert heading in text, heading
print('evaluation sections verified')
PY`
Expected: `evaluation sections verified`

### Task 4: Create resume/interview notes document

**Files:**
- Create: `docs/resume_notes.md`
- Source: `README.md` (current long-form version before rewrite)

- [ ] **Step 1: Create the doc header and position it as external-facing framing material**

```md
# 简历表达与面试亮点

## 使用方式
本文件整理项目完成后可用于简历与面试表达的内容，不作为当前实现状态说明。
```

- [ ] **Step 2: Move the resume phrasing, high-level project description, contribution framing, and interview talking points here**

```md
## 项目名称建议
## 项目描述建议
## 核心贡献表达
## 面试亮点准备
```

- [ ] **Step 3: Preserve the distinction between current plan and future achievement claims**

```md
## 表达规则
- 未完成的数据与指标必须保留“目标”或“规划”口径
- 只有真实落地后的结果才能改写成既成事实
```

- [ ] **Step 4: Verify the resume notes doc headings**

Run: `python - <<'PY'
from pathlib import Path
text = Path('docs/resume_notes.md').read_text(encoding='utf-8')
for heading in ['# 简历表达与面试亮点', '## 使用方式', '## 项目名称建议', '## 项目描述建议', '## 核心贡献表达', '## 面试亮点准备', '## 表达规则']:
    assert heading in text, heading
print('resume notes sections verified')
PY`
Expected: `resume notes sections verified`

### Task 5: Create references document

**Files:**
- Create: `docs/references.md`
- Source: `README.md` (current long-form version before rewrite)

- [ ] **Step 1: Create the references doc header and scope statement**

```md
# 参考资料与学习路径

## 使用方式
集中存放项目规划阶段参考的技术文档、论文、数据源与面试学习材料。
```

- [ ] **Step 2: Move the current reference links into grouped sections**

```md
## 核心技术文档
## 数据源（自动驾驶领域）
## 面试准备资料
```

- [ ] **Step 3: Keep the external links grouped by purpose so they do not clutter the homepage**

```md
- 评估框架
- 检索优化
- 模型微调
- 部署优化
```

- [ ] **Step 4: Verify the references doc headings**

Run: `python - <<'PY'
from pathlib import Path
text = Path('docs/references.md').read_text(encoding='utf-8')
for heading in ['# 参考资料与学习路径', '## 使用方式', '## 核心技术文档', '## 数据源（自动驾驶领域）', '## 面试准备资料']:
    assert heading in text, heading
print('references sections verified')
PY`
Expected: `references sections verified`

### Task 6: Final documentation verification

**Files:**
- Verify: `README.md`
- Verify: `docs/roadmap.md`
- Verify: `docs/evaluation.md`
- Verify: `docs/resume_notes.md`
- Verify: `docs/references.md`

- [ ] **Step 1: Verify the README doc links point to files that exist**

Run: `python - <<'PY'
from pathlib import Path
import re
root = Path('.')
text = Path('README.md').read_text(encoding='utf-8')
links = re.findall(r'\((docs/[^)]+\.md)\)', text)
missing = [p for p in links if not (root / p).exists()]
assert not missing, missing
print('README links verified')
PY`
Expected: `README links verified`

- [ ] **Step 2: Verify that the homepage no longer contains long resume/reference sections**

Run: `python - <<'PY'
from pathlib import Path
text = Path('README.md').read_text(encoding='utf-8')
for forbidden in ['简历呈现高级表达', '面试亮点准备', '参考资料 + 学习路径']:
    assert forbidden not in text, forbidden
print('README content scope verified')
PY`
Expected: `README content scope verified`

- [ ] **Step 3: Review the diff for consistency and markdown hierarchy**

Run: `git diff -- README.md docs/roadmap.md docs/evaluation.md docs/resume_notes.md docs/references.md`
Expected: A docs-only diff showing homepage simplification and content moved into focused docs.

## Self-Review

- **Spec coverage:** The plan covers homepage rewrite, docs splitting, migration targets, wording constraints, and cross-link verification from the approved spec.
- **Placeholder scan:** No TBD/TODO placeholders remain; each task names exact files, expected sections, and verification commands.
- **Type consistency:** All referenced files and section names are consistent across the tasks.
