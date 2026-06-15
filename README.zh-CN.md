# Daily Work Planner

[English](README.md) | 简体中文

Daily Work Planner 是一个用于工作开始前预检、执行中检查、结束后复盘记忆的 Codex Skill。它会把目标、可用时间、当前窗口任务、本地仓库状态、文件材料和截止时间转化成可执行的工作计划。

它不是日历软件，也不是普通每日待办清单。它主要回答三个问题：

1. 我现在应该先做什么？
2. 每个阶段做到什么程度才算完成？
3. 如果时间不够，应该保住什么最低可交付成果？

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

如果进度轻微延误，它会提示压缩 buffer，但保留核心目标。之后可以用 `resume` 生成续做卡片，用 `handoff --remember` 生成交接包并记录实际用时，后续估时会更准。

完整案例见：[examples/quick-start-case.md](examples/quick-start-case.md)。

## 已支持能力

- 规划预算计算
- 软 deadline 和硬 deadline
- 文件上下文提取
- 文件优先级排序
- 工作模式自动识别
- 里程碑和验收标准
- buffer 和最低可交付版本
- checkpoint 延误重排
- TXT/DOCX 综合工作包
- 带提醒的 `.ics` 日历事件
- `session.json` 状态机
- 复盘日志
- 基于复盘日志的个人估时画像
- 当前窗口任务文本识别：通过 `--window-note`
- 本地仓库任务识别：从 `git status`、TODO/FIXME 标记、Markdown 未完成清单中提取
- 未提供工作时长时自动估算所需时间
- 可行性评分：完整版本、可交付版本、保命版本
- 执行中 checkpoint：记录已完成和剩余任务，判断延误等级
- resume card：下次继续时告诉你从哪里开始
- handoff：结束时生成交接包，并可选写入本地记忆
- 本地任务记忆：记录完成内容、实际用时和个人习惯

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

### 方式 2：克隆仓库后本地安装

Windows PowerShell：

```powershell
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Force
```

macOS / Linux：

```bash
git clone https://github.com/Stephen-studying/daily-work-planner.git
cd daily-work-planner
sh ./install.sh --force
```

安装脚本会把内层 Skill 文件夹复制到：

- Windows 默认：`%USERPROFILE%\.codex\skills\daily-work-planner`
- macOS/Linux 默认：`~/.codex/skills/daily-work-planner`
- 如果设置了 `CODEX_HOME`：`$CODEX_HOME/skills/daily-work-planner`

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

## License

MIT License.
