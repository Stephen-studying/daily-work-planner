# Daily Work Planner

[English](README.md) | 简体中文

Daily Work Planner 是一个 Codex Skill，用于在开始一次工作之前完成工作会话预检。它会把目标、可用时间、文件材料和截止时间转化为可执行的工作计划。

它不是日历软件，也不是普通每日待办清单。它主要回答三个问题：

1. 我现在先做什么？
2. 每个阶段做到什么程度算完成？
3. 如果时间不够，应该保住什么？

## 核心原则

规划必须服务于执行。默认规划时间不超过总可用工作时间的 5%，并设置绝对上限：

| 总工作时间 | 规划上限 |
|---|---:|
| <= 60 分钟 | 3 分钟 |
| 61-240 分钟 | 8 分钟 |
| 241-480 分钟 | 15 分钟 |
| > 480 分钟或跨天 | 20 分钟 |

如果时间很短，Skill 会生成极简计划，而不是反复追问。

## 已支持能力

- 规划预算计算
- 软 deadline 和硬 deadline
- 文件上下文提取
- 文件优先级排序
- 工作模式自动识别
- 里程碑和验收标准
- buffer 和最低可交付版本
- checkpoint 延误重排
- todo.txt 导出
- 带提醒的 `.ics` 日历事件
- 复盘日志
- 基于复盘日志的个人估时画像
- `session.json` 状态机
- 根据历史复盘自动增加 buffer
- 一键生成完整工作包
- 默认生成综合 `work_session.txt` 和 `work_session.docx`，减少文件分散

## 统一 CLI

```powershell
python -m daily_work_planner --help
```

一键生成工作包：

```powershell
python -m daily_work_planner start --goal "阅读两篇论文并完成汇报提纲" --start 14:00 --minutes 240 --hard-deadline 18:00 .\paper1.pdf .\notes.docx --output-dir .\work-session
```

默认工作包会生成：

- `session.ics`
- `session.json`
- `work_session.txt`
- `work_session.docx`

如果还想生成分散的辅助文件，可以加 `--split-files`：

```powershell
python -m daily_work_planner start --goal "阅读两篇论文并完成汇报提纲" --start 14:00 --minutes 240 --hard-deadline 18:00 .\paper1.pdf .\notes.docx --output-dir .\work-session --split-files
```

查看 session 状态：

```powershell
python -m daily_work_planner session status --session .\work-session\session.json
```

延误后基于 session 重排：

```powershell
python -m daily_work_planner reschedule --session .\work-session\session.json --now 15:40 --minutes-late 25 --output .\work-session\rescheduled_plan.md
```

使用复盘日志自动调整 buffer：

```powershell
python -m daily_work_planner start --goal "制作最终汇报 PPT" --start 09:00 --minutes 180 --hard-deadline 12:00 --profile-log .\review-log.md --output-dir .\work-session
```

## 常用脚本

提取文件上下文：

```powershell
python .\daily-work-planner\scripts\extract_file_context.py .\paper.pdf .\draft.docx .\src --recursive --max-files 20 --format markdown
```

识别工作模式：

```powershell
python .\daily-work-planner\scripts\classify_work_mode.py --goal "修复登录 bug 并运行测试" .\src\auth.py
```

文件优先级排序：

```powershell
python .\daily-work-planner\scripts\rank_files.py --goal "修改最终报告并准备提交" .\report.docx .\rubric.pdf .\notes.md
```

生成估时画像：

```powershell
python .\daily-work-planner\scripts\estimate_profile.py .\review-log.md
```
