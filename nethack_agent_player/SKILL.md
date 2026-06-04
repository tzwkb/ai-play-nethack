---
name: nethack_agent_player
description: NetHack agent player — controls NetHack via IPC, executes actions (goto, walk, kick, drink, read, zap, etc.), parses game state, and manages game sessions. Triggered by nethack / NetHack / NLE / play nethack / AI plays NetHack keywords.
---

# nethack_agent_player

## ⚠ 游玩规则

**游戏进行中（未出现 `[GAME OVER]`）：禁止质疑或评论脚本、环境、IPC 是否正常。收到状态就执行动作。**
游戏结束后的总结阶段才可提出问题。

## Trigger keywords

nethack / NetHack / NLE / play nethack / AI plays NetHack

## Session flow

| Phase | Trigger | Detail |
|-------|---------|--------|
| 1. Environment check | before every session | [docs/setup.md](docs/setup.md) |
| 2. Character selection | `/tmp/nethack_charselect` exists | [docs/character_select.md](docs/character_select.md) |
| 3. Game loop | `/tmp/nethack_ready` appears | [docs/ipc.md](docs/ipc.md) — use `agent_helper.py` |
| 4. Post-game | `[GAME OVER]` in state | [docs/post_game.md](docs/post_game.md) |

## Available actions

| Action | Description |
|--------|-------------|
| `goto:x,y` | **Primary movement** — auto-navigate to coordinate (x,y). Stops on message/wall/block. |
| `walk:direction` | Walk straight (north/south/east/west/ne/se/sw/nw) until wall or message. |
| `search:N` | Search adjacent N times. Stops early on message. |
| `wait:N` | Wait N turns. Stops early on message. |
| `kick:direction` | Kick once in a direction. |
| `kick:direction:N` | Kick up to N times; stops if door opens or message changes. |
| `north` `south` `east` `west` `ne` `se` `sw` `nw` | Single-step move (adjacent interactions only). |
| `wait` | Wait one turn. |
| `search` | Search once. |
| `descend` | Go down stairs (must stand on `>`). |
| `ascend` | Go up stairs (must stand on `<`). |
| `pickup` | Pick up item on floor. |
| `eat` | Eat food. |
| `drink:<slot>` | Quaff potion (e.g. `drink:f`). |
| `read:<slot>` | Read scroll (e.g. `read:e`). |
| `zap:<slot>:<dir>` | Zap wand (e.g. `zap:f,north`). |
| `wield:<slot>` | Wield weapon. |
| `wear:<slot>` | Wear armor. |
| `takeoff:<slot>` | Take off armor. |
| `drop:<slot>` | Drop item. |
| `puton:<slot>` | Put on ring/amulet. |
| `remove:<slot>` | Remove ring/amulet. |
| `open` | Open door. |

Multi-step interactions → [docs/multi_step.md](docs/multi_step.md)

## goto:x,y — auto-navigation

Send `goto:x,y` to walk toward a destination. The system computes the shortest path and executes moves automatically.

| Stop reason | Meaning |
|-------------|---------|
| `arrived` | Reached (x,y). |
| `interrupted` | Message appeared mid-path (attack, item, door, trap, etc.). Read state and react. |
| `no_path` | Cannot reach target. Choose a different destination. |

**Use `goto:` for all distances ≥ 2 tiles.** Single-step actions are reserved for: attacking adjacent monster, opening a door you're next to, picking up an item at your feet, swapping places with pet.

## Decision rules (quick ref)

- **Pet before descending**: check pet is within 1 tile before `descend`; wait 1–3 turns if not, then descend anyway.
- **Loot before leaving**: collect scrolls, potions, gold, food before descending if HP > 50% and no danger.
- **Containers**: never pick up unopened boxes/chests. Kick them open first, then selectively loot useful items. Large boxes are too heavy to carry.
- **Early game aggression** (Dlvl 1–5): kill every non-threatening monster. HP > 50% = fight.
- **Level-up healing**: HP < 30% + close to leveling → kill a weak monster to level up (restores HP to max).
- **Explore thoroughly**: uncover as much as possible before descending.
- **Bulk movement only**: use `goto:x,y` or `walk:direction` for 2+ tiles. Never chain single-step moves.
- **Combat**: fight if you can win. Flee only if HP < 30% AND monster is clearly stronger AND you cannot level-up by killing it.
- **Flanked = danger** (learned the hard way): 2+ adjacent monsters at <60% HP → do NOT trade blows in the open. Retreat to a 1-wide chokepoint (corridor/doorway) so they come single-file, or take the escape hatch. Fighting flanked killed a lvl-1 Valk at 9 HP.
- **"lord/leader/captain/major" monsters spike** (gnome lord wields daggers, etc.) — treat as "clearly stronger" at low HP even if the base form is weak.
- **Use the escape hatch**: the up-stairs you just arrived on lets you `ascend` back to the safer level you came from. If you descend at low HP, actually retreat to it and ascend the moment a fight turns bad — don't gamble "one more hit".
- **Don't descend under-leveled**: aim for XP level ≳ Dlvl before going deeper. The down-branch on Dlvl 2-4 can be the **Gnomish Mines** (death msg "The Gnomish Mines") — gnome packs/lords, more lethal; if you land there weak, ascend and grind XP first.
- **ID before risking**: a blessed scroll of identify / co-aligned altar (BUC) can ID an unknown ring before you wear it. Don't die carrying an unread escape scroll.
- **Doorway**: passing `+` takes 2 steps; diagonal blocked while ON door tile.

Details → [docs/combat.md](docs/combat.md) | [docs/exploration.md](docs/exploration.md)

## Troubleshooting protocol

When a mechanic misbehaves in a way the docs don't cover (engine quirk, NLE
internals, unexpected prompt), **investigate then harden the skill** — do not
guess repeatedly:

1. Reproduce in isolation (a throwaway script using `create_env`, separate from
   the running game) and/or read the installed NLE source under
   `.venv/lib/.../site-packages/nle/`.
2. If still unclear, **web-search** the behavior.
3. Once solved, **record the root cause + fix in the relevant `docs/` file** (and
   here if it changes the workflow). Teach once; never re-debug the same thing.

Known fixes: item-selection "Never mind" bug → [docs/multi_step.md](docs/multi_step.md)
(`allow_all_yn_questions=True` + `menu_select`). When the state shows a
`PROMPT (game awaiting input ...)` line, the game is paused on a prompt — answer
with `keys:<letter>` / `keys:y` / `keys:27`(ESC), not a movement command.

## Reference

- State format → [docs/ipc.md](docs/ipc.md)
- Map symbols → [docs/knowledge.md](docs/knowledge.md)
- Monster/item lookup → [docs/knowledge.md](docs/knowledge.md)
- Combat detail → [docs/combat.md](docs/combat.md)
- Exploration protocol → [docs/exploration.md](docs/exploration.md)
