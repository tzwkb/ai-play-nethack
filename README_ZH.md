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
