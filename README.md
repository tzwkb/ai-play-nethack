# AI Plays NetHack

<!-- bilingual-readme:start -->

## 双语说明 / Bilingual Documentation

> 本节提供整篇 README 的中英双语维护说明；下方保留原始详细说明、命令、路径和配置示例。
> This section provides bilingual maintenance notes for the full README; the original detailed notes, commands, paths, and configuration examples are preserved below.

### 中文

**概览**：基于 NLE 的 NetHack AI 游玩/观测项目，包含面向不同受众的运行与展示模块。

**主要能力**：
- 通过 NLE 环境运行或观察 AI 玩 NetHack。
- 保留跨局记忆和运行历史。
- 适合实验、演示和 agent 行为观察。

**使用方式**：按下方模块说明安装依赖、选择入口并运行。

**状态**：该仓库仍按当前 README 的说明维护或使用。

**注意事项**：NetHack/NLE 行为细节以原 README 的最新变更和模块说明为准。

### English

**Overview**: NLE-based NetHack AI play and observation project with modules for different audiences.

**Key capabilities**:
- Runs or watches AI play NetHack through an NLE environment.
- Keeps cross-run memory and run history.
- Useful for experiments, demos, and agent-behavior observation.

**Usage**: Install dependencies, choose the appropriate module, and run the entrypoint described below.

**Status**: This repository is maintained or used according to the current README notes.

**Notes**: NetHack/NLE behavior details follow the latest-change notes and module descriptions below.

<!-- bilingual-readme:end -->

Two modules for watching AI play NetHack, built for different audiences.

> **Latest changes (2026-04):**
> - `run_history.json` replaces `nethack_memory.json` for cross-run memory
> - `env.py` now injects a `[NAV]` hint each turn: player coords, nearest stairs/door/corridor, and the recommended action word (e.g. `go southeast toward door (+) at (62,10)`)
> - SYSTEM_PROMPT tightened: 3-priority decision order, `<`/`>` confusion fixed

---

## nethack_agent_player — Developer / Research

For iterative experimentation. Claude Code agent plays the game directly via NLE, accumulates experience, and updates decision rules in `SKILL.md` after each run.

**Requirements:** WSL + Ubuntu, NLE installed in WSL

**Usage:**
```
# Invoke via Claude Code skill: nethack_agent_player
```

**Key files:**
- `play.py` — entry point
- `scripts/env.py` — NLE environment wrapper
- `scripts/memory.py` — cross-session memory (`run_history.json`)
- `SKILL.md` (project root) — living decision guide, update after each run

---

## nethack_api_player — General User / Viewer

For watching AI play without any setup beyond an API key. Connects to any OpenAI-compatible API (DeepSeek, GPT-4o, etc.), remembers your config, and shows the game turn by turn.

**Requirements:** WSL + Ubuntu, NLE installed in WSL, an API key

**Usage:**
```bash
cd nethack_api_player
python main.py
```

**First launch prompts:**
- Language — saved for next time
- API Key / Base URL / Model — saved for next time
- Role and race selection menu

**Key files:**
- `main.py` — launcher with config memory
- `game.py` — game loop + LLM decision
- `scripts/env.py` — NLE environment wrapper (includes NAV hints)
- `scripts/memory.py` — death analysis + lessons across runs (`run_history.json`)
- `scripts/i18n/` — localization (zh / en)

---

## Workflow

```
nethack_agent_player runs a game
        ↓
discover new rules → update SKILL.md
        ↓
"sync to api module"
        ↓
nethack_api_player/game.py SYSTEM_PROMPT updated
```

SKILL.md is the single source of truth for game strategy. The API module's SYSTEM_PROMPT is its downstream compiled version.

---

## Recent Updates

### NAV hints in env.py
`scripts/env.py` now injects a `[NAV]` line into every state, computed directly from `blstats` and `tty_chars`:
- Player position from `blstats[8,9]`
- Nearest `>` (stairs down), `+` (door), `#` (corridor) scanned from the raw char array
- Translated into a plain-English action: `ACTION: go northeast toward door (+) at (42,8).`

### run_history.json
Memory file renamed from `nethack_memory.json` to `run_history.json` in both modules.

---

## Known Limitations of nethack_api_player

The API mode has a hard capability ceiling that NAV hints alone cannot fix:

- **No spatial memory.** The LLM receives a fresh text snapshot each turn. It has no internal map, no record of which tiles it has visited, and no way to know which directions it has already tried.
- **NAV hints are ignored under pressure.** When the LLM has a long conversation history, the `[NAV]` line competes with many other signals and is frequently ignored — observed in logs as the AI walking east/west repeatedly while NAV says "go southeast."
- **Stateless navigation.** Without knowing its previous position, the AI cannot detect that it is stuck or looping. It will repeat the same direction for many turns without realizing it is hitting a wall.

**Attempted mitigations:**
- Injecting explicit `ACTION: go <direction>` instructions in the NAV hint (reduces but does not eliminate ignoring)
- Loop detection in `game.py` with a `[LOOP WARNING]` injected into state after 4+ repeated actions
- Cross-run lessons stored in `run_history.json` to avoid repeating known mistakes

**Conclusion:** Reliable navigation in NetHack requires persistent spatial state. This is the core advantage of `nethack_agent_player`, which can maintain a map and reason over multiple steps using tool calls.

---

## Supported Characters

Roles: archeologist · barbarian · caveman · healer · knight · monk · priest · ranger · rogue · samurai · tourist · valkyrie · wizard

Races: human · elf · dwarf · gnome · orc