# Daily Work Planner

<div align="center">

[English](README.md) | 简体中文

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge)
![Agent Portable](https://img.shields.io/badge/Agent-Portable-DB2777?style=for-the-badge)
![Local First](https://img.shields.io/badge/Local--First-Privacy-0F766E?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.2.0-7C3AED?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-2563EB?style=for-the-badge)

**一个可安装到 Codex 和其他本地 agent 的工作会话预检系统。**

把零散文件、模糊任务、当前窗口备注、本地仓库 TODO 和 deadline，转化成可执行的工作会话计划：里程碑、验收标准、buffer、checkpoint、交接记录和本地记忆一次生成。

</div>

## 为什么需要它

很多工作不是从清晰任务开始的。你可能只知道今天要读论文、改 Word、写报告、调代码、做 PPT、清理仓库，但不知道第一步该做什么、到底需要多久、时间不够时应该保住什么。

Daily Work Planner 就用于这个“正式开始工作前”的阶段。

它不是日历软件，也不是普通每日待办清单。它主要回答三个现实问题：

| 问题 | Skill 给出的答案 |
|---|---|
| 我现在应该先做什么？ | 根据目标、文件、当前任务和可用时间生成第一行动。 |
| 做到什么程度才算完成？ | 每个阶段都有验收标准，而不是只写“继续做”。 |
| 时间不够怎么办？ | 提前定义最低可交付版本、降级范围、buffer 和 checkpoint 应对。 |

## 核心原则

规划必须服务执行。默认规划时间不超过总可用工作时间的 5%，并设置绝对上限：

| 总工作时间 | 规划上限 |
|---|---:|
| <= 60 分钟 | 3 分钟 |
| 61-240 分钟 | 8 分钟 |
| 241-480 分钟 | 15 分钟 |
| > 480 分钟或跨天 | 20 分钟 |

如果用户没有告诉 Skill 要做多久，Skill 会根据目标、文件、当前任务、本地仓库状态、用户速度、复盘日志和本地记忆估算所需时间。

## 快速案例

假设你要准备一个 5 分钟论文分享，但你还没想好要做多久，只知道当前有这些任务：

```text
阅读两篇论文摘要
整理 6 页汇报提纲
列出 5 分钟讲稿检查清单
```

你可以不提供 `--minutes`，直接让 Skill 自己估时：

```powershell
python -m daily_work_planner start --goal "准备一个 5 分钟论文分享" --start 09:00 --window-note "阅读两篇论文摘要`n整理 6 页汇报提纲`n列出 5 分钟讲稿检查清单" --speed normal --output-dir .\work-session
```

Skill 会把模糊任务变成一个可执行工作会话：

| 判断项 | 结果 |
|---|---|
| 识别到的任务 | 3 个当前任务 |
| 预计时长 | 约 190 分钟 |
| 可行性 | 高，建议完整完成 |
| 软 / 硬 deadline | 约 11:42 / 12:10 |
| buffer | 约 28 分钟 |
| 第一动作 | 先扫描材料，确定必读和可跳过部分 |

执行中可以记录 checkpoint：

```powershell
python -m daily_work_planner checkpoint --session .\work-session\session.json --now 10:15 --done "阅读两篇论文摘要" --remaining "整理 6 页汇报提纲" --remaining "列出 5 分钟讲稿检查清单"
```

它会判断延误是轻微、中等还是严重，并建议压缩 buffer、砍掉可选内容，或切换到最低可交付版本。之后可以用 `resume` 生成续做卡片，用 `handoff --remember` 生成交接包并记录实际用时，后续估时会更准。

完整案例见：[examples/quick-start-case.md](examples/quick-start-case.md)。

## 工作流

```mermaid
flowchart LR
    A["目标、文件、仓库任务、窗口备注"] --> B["任务识别"]
    B --> C["自动估时"]
    C --> D["可行性评分"]
    D --> E["会话计划"]
    E --> F["Checkpoint"]
    F --> G["续做或重排"]
    G --> H["交接总结"]
    H --> I["本地记忆"]
```

## 能力地图

| 阶段 | 可以做什么 |
|---|---|
| 输入 | 接收目标、文件、deadline、当前窗口备注、本地仓库状态、复盘日志和本地记忆。 |
| 检查 | 从 PDF、DOCX、Markdown、文本和代码文件中提取轻量上下文。 |
| 任务识别 | 从 `git status`、TODO/FIXME、Markdown 未完成清单和粘贴的任务文本中识别剩余工作。 |
| 自动估时 | 根据任务类型、文件数量、用户速度、复盘历史和本地记忆估算所需时长。 |
| 计划生成 | 生成软硬 deadline、里程碑、验收标准、buffer 和最低可交付版本。 |
| 计划校验 | 检查 deadline、里程碑、验收标准、buffer、降级方案和 5% 规划预算是否齐全。 |
| 执行中 | 记录 checkpoint，判断延误等级，重排剩余任务，生成续做卡片。 |
| 结束后 | 生成 handoff、预计 vs 实际复盘，并写入私有本地任务记忆。 |

## 工作模式

| 模式 | 重点输出 |
|---|---|
| 深度写作 | 章节结构、论证链条、引用缺口、修改验收标准。 |
| 快速阅读 | 必读范围、跳读边界、结构化笔记、后续可用摘要。 |
| 代码开发 | 最小可运行版本、相关文件、测试方法、调试顺序。 |
| 文档修改 | 主文档、格式规范、参考文献、图表编号、导出检查。 |
| PPT 制作 | 页数控制、汇报逻辑、图表优先级、讲稿 checkpoint、最低可展示版本。 |
| 考试复习 | 高频考点、薄弱点、背诵轮次、刷题安排、考前保底策略。 |
| 数据整理 | 数据来源、表格结构、命名规范、图表输出、异常值检查。 |
| 研究规划 | 文献优先级、阅读路线、综合输出、证据地图。 |
| 行政材料 | 必填信息、附件清单、提交检查、deadline buffer。 |
| 仓库清理 | 未提交文件、TODO、测试、可提交范围、交接状态。 |

## 输出工作包

默认一个 `start` 命令会生成一套紧凑工作包：

| 文件 | 用途 |
|---|---|
| `work_session.txt` | 人类可读的会话计划，包含任务、deadline、里程碑和降级方案。 |
| `work_session.docx` | Word 版本，方便分享、打印或归档。 |
| `session.ics` | 带提醒的日历事件。 |
| `session.json` | 持久状态文件，用于 checkpoint、resume、reschedule、handoff 和 memory。 |

计划内容本身可以包括：

| 计划元素 | 作用 |
|---|---|
| 规划预算 | 保证规划时间不超过 5% 规则。 |
| 软 / 硬 deadline | 区分内部目标时间和最终交付时间。 |
| 文件优先级 | 区分主文件、参考文件、可选文件和暂时忽略文件。 |
| 里程碑 | 每个阶段都有验收标准。 |
| buffer 和降级方案 | 时间不足时保护最低可交付版本。 |
| checkpoint 应对 | 判断延误等级并压缩计划。 |
| 复盘与记忆 | 记录预计 vs 实际用时，但不保存敏感原文。 |

如果还想生成分散的辅助文件，可以加 `--split-files`，额外输出 `session_plan.md`、`file_context.md`、`file_priority.md`、`todo.txt` 和 `plan_validation.md` 等文件。

## 已支持能力速览

| 能力 | 说明 |
|---|---|
| 当前窗口任务识别 | 通过 `--window-note` 输入当前任务文本。 |
| 本地仓库任务识别 | 从 `git status`、TODO/FIXME 和 Markdown 未完成清单中提取任务。 |
| 自动估时 | 未提供工作时长时，根据任务、文件、速度、复盘日志和本地记忆估算。 |
| 可行性评分 | 判断适合完整完成、可交付完成、保命完成还是重新定义范围。 |
| 执行中 checkpoint | 记录已完成和剩余任务，判断延误等级。 |
| resume card | 下次继续时告诉你从哪里开始。 |
| handoff | 结束时生成交接包，并可选写入本地记忆。 |
| 本地任务记忆 | 记录完成内容、实际用时和个人习惯，帮助后续估时更准。 |

## Agent 兼容性

这个仓库现在提供两个 agent 入口：

| Agent 类型 | 入口文件 | 说明 |
|---|---|---|
| Codex / OpenAI 兼容 skill loader | `daily-work-planner/SKILL.md` | 使用标准 Codex skill frontmatter 和 `agents/openai.yaml`。 |
| 通用本地 agent | `daily-work-planner/AGENTS.md` | 把同一套工作流写成通用 agent 指令。 |
| 从整个仓库读取指令的 agent | `AGENTS.md` | 指向真正可安装的 skill 文件夹和测试命令。 |
| 只使用命令行 | `python -m daily_work_planner --help` | 不需要 skill loader，安装 Python 包后即可使用。 |

如果某个 agent 没有正式的 skill 系统，可以把内层 `daily-work-planner/` 当作可移植指令包，让 agent 读取 `daily-work-planner/AGENTS.md`。如果 agent 支持本地工具调用，可以允许它运行 `daily-work-planner/scripts/` 下的 Python 脚本。

## 统一 CLI

```powershell
python -m daily_work_planner --help
```

## 安装方式

### 方式 1：让 Codex 直接从 GitHub 安装

在 Codex 里直接说：

```text
帮我安装这个 skill：https://github.com/Stephen-studying/daily-work-planner/tree/main/daily-work-planner
```

安装后重启 Codex。

### 方式 2：克隆仓库后安装到 Codex

Windows PowerShell：

```powershell
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Agent codex -Force
```

macOS / Linux：

```bash
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
sh ./install.sh --agent codex --force
```

安装脚本会把内层 Skill 文件夹复制到：

- Windows 默认：`%USERPROFILE%\.codex\skills\daily-work-planner`
- macOS/Linux 默认：`~/.codex/skills/daily-work-planner`
- 如果设置了 `CODEX_HOME`：`$CODEX_HOME/skills/daily-work-planner`

### 方式 3：安装到其他 agent

当你的 agent 有自己的 skill 目录或指令库目录时，使用 `generic` 模式：

Windows PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Agent generic -Destination "$env:USERPROFILE\.agent-skills" -Force
```

macOS / Linux：

```bash
sh ./install.sh --agent generic --dest "$HOME/.agent-skills" --force
```

然后让你的 agent 读取下面其中一个入口：

| 文件 | 适用情况 |
|---|---|
| `.agent-skills/daily-work-planner/AGENTS.md` | agent 支持通用指令文件。 |
| `.agent-skills/daily-work-planner/SKILL.md` | agent 能理解 OpenAI/Codex 风格 skill。 |

也可以设置 `AGENT_SKILLS_HOME`，这样就不用每次传 `-Destination` / `--dest`。

Windows 下可以这样验证：

```powershell
Test-Path "$env:USERPROFILE\.codex\skills\daily-work-planner\SKILL.md"
```

重启 Codex 后可以这样调用：

```text
Use $daily-work-planner to plan my next 2-hour work session.
```

如果还想使用命令行工具，可以在仓库根目录执行：

```powershell
python -m pip install -e .
python -m daily_work_planner --help
```

识别当前仓库仍存在的任务并估时：

```powershell
python -m daily_work_planner inspect --repo . --goal "完成当前仓库清理" --speed normal
```

传入当前窗口或当前任务文本：

```powershell
python -m daily_work_planner inspect --window-note "修复登录 bug`n更新 README`n运行测试" --goal "完成当前代码任务"
```

不提供 `--minutes`，让 Skill 自动估算时长并生成工作包：

```powershell
python -m daily_work_planner start --goal "完成当前代码任务" --start 09:00 --scan-repo --repo . --speed normal --output-dir .\work-session
```

先判断任务是否可行：

```powershell
python -m daily_work_planner feasibility --goal "完成最终报告" --available-minutes 90 --estimated-minutes 150 --mode writing
```

执行中记录 checkpoint：

```powershell
python -m daily_work_planner checkpoint --session .\work-session\session.json --now 10:30 --done "更新 README" --remaining "运行测试" --remaining "提交改动"
```

下次继续时生成续做卡片：

```powershell
python -m daily_work_planner resume --session .\work-session\session.json
```

结束时生成交接包：

```powershell
python -m daily_work_planner handoff --session .\work-session\session.json --completed "完成任务识别优化" --remaining "发布 v1.2 标签" --actual-minutes 145 --remember
```

提供明确时长时仍然可以按原方式使用：

```powershell
python -m daily_work_planner start --goal "阅读两篇论文并完成汇报提纲" --start 14:00 --minutes 240 --hard-deadline 18:00 .\paper1.pdf .\notes.docx --output-dir .\work-session
```

默认工作包会生成：

- `work_session.txt`
- `work_session.docx`
- `session.ics`
- `session.json`

如果还想生成分散的辅助文件，可以加 `--split-files`。

查看 session 状态：

```powershell
python -m daily_work_planner session status --session .\work-session\session.json
```

延误后基于 session 重排：

```powershell
python -m daily_work_planner reschedule --session .\work-session\session.json --now 15:40 --minutes-late 25 --output .\work-session\rescheduled_plan.md
```

任务结束后写入本地记忆：

```powershell
python -m daily_work_planner remember --session .\work-session\session.json --actual-minutes 145 --completed "生成综合工作包" --habit "代码清理通常需要额外测试时间"
```

默认会写入：

- `.daily-work-planner/memory.jsonl`
- `.daily-work-planner/MEMORY.md`

这个目录默认加入 `.gitignore`，因为它可能包含个人使用习惯和任务历史，不应默认上传到 GitHub。

## 隐私边界

Daily Work Planner 默认本地优先：

- 不主动上传用户文件；
- 不把完整文档、论文、代码或当前窗口原文写入记忆；
- 记忆只保存目标、模式、预计用时、实际用时、完成摘要、文件名和习惯信号；
- `.daily-work-planner/` 默认不提交到 Git。

## 后续路线

- 支持更多 Office、科研和课程资料格式；
- 为不熟悉命令行的用户提供可选 GUI 包装；
- 根据多次复盘进一步校准个人估时；
- 增加实验记录、文献综述、基金申请、面试准备等工作模式；
- 导出到更多任务管理器和日历系统。

## 不做什么

它不试图替代日历软件、长期项目管理工具或深度文档总结器。它的目标是让你更快开始工作，让进度可检查，并在计划延误时保住核心产出。

## License

MIT License.
