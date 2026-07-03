# AI Plays NetHack

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

[English](README.md) | 中文

## 概览

基于 NLE 的 NetHack AI 游玩/观测项目，包含面向不同受众的运行与展示模块。

## 文档对齐说明

本 README_ZH.md 与英文 README.md 使用同一项目事实，但采用中文读者更容易扫描的结构。命令、路径、配置键和示例数据保持原样。

## 主要能力

- 通过面向 Agent 的 API 控制 NetHack 会话。
- 保留导航提示、运行历史和角色支持说明。
- 区分研究/开发流程和普通查看流程。

## 主要能力

- 通过 NLE 环境运行或观察 AI 玩 NetHack。
- 保留跨局记忆和运行历史。
- 适合实验、演示和 agent 行为观察。

## 使用方式

按下方模块说明安装依赖、选择入口并运行。

## 注意事项

NetHack/NLE 行为细节以原 README 的最新变更和模块说明为准。

## 命令与配置参考

以下命令、路径和配置键保持原样，复制时请以实际环境为准。

```
# Invoke via Claude Code skill: nethack_agent_player
```

```bash
cd nethack_api_player
python main.py
```

```
nethack_agent_player runs a game
        ↓
discover new rules → update SKILL.md
        ↓
"sync to api module"
        ↓
nethack_api_player/game.py SYSTEM_PROMPT updated
```

## 对应技术覆盖

### 双入口说明

- `nethack_agent_player` 面向开发和研究使用，提供 Agent 控制、状态解析和动作执行能力。
- `nethack_api_player` 面向普通查看或演示流程，隐藏底层控制细节。

### 工作流

典型流程是启动 NetHack 会话、读取当前状态、让 Agent 选择动作、执行动作并把结果写入运行历史。`run_history.json` 用于复盘动作序列、失败点和导航行为。

### 导航与限制

`env.py` 中的 NAV hints 用于辅助路径规划和位置判断。当前限制主要来自 NetHack 本身的复杂状态、地图遮挡、物品识别和长期目标规划，因此该仓库更适合作为 Agent 控制实验场，而不是完整自动通关系统。

### 角色支持

英文 README 中列出的 supported characters 是当前测试过或计划支持的角色集合；新增角色时应同步更新角色初始化、状态解析和策略假设。

## 补充实现说明

### `nethack_agent_player`

该入口更接近底层控制层，适合研究 Agent 如何读取游戏状态、规划动作并通过 IPC 执行命令。它关注可复现的状态表示、动作接口和失败复盘。

### `nethack_api_player`

该入口面向更高层的用户或演示流程，目标是让使用者更容易启动、观察和复用 Agent 行为，而不必理解所有底层状态字段。

### 运行历史

`run_history.json` 是重要调试材料。它应记录关键动作、状态变化和失败上下文，用于判断问题来自导航、解析、策略还是游戏随机事件。

### 已知限制

NetHack 的长期规划、隐藏信息、背包管理、怪物威胁和地图变化都可能导致 Agent 行为不稳定。README 中的限制说明是实际使用边界，不应被理解为完整自动玩家能力。

## 英文章节对应说明

### Developer / Research

对应 `nethack_agent_player`。该部分说明底层 Agent 控制、状态解析、动作执行和研究用接口。

### General User / Viewer

对应 `nethack_api_player`。该部分说明更高层、更易启动的演示或观察流程。

### Workflow / Recent Updates

对应中文的“工作流”和“运行历史”。这些内容用于说明每次运行如何启动、记录和复盘。

### NAV Hints / Known Limitations

对应中文的“导航与限制”。NetHack 状态复杂，README 应明确说明导航提示能解决什么、不能解决什么。

### Supported Characters

角色支持列表用于限定当前测试范围。新增角色不只是改名称，还要同步初始化、动作假设和状态解析。
