# nethack_agent_player

Let the Agent play NetHack via the NLE interface.

## Environment Check (run before every session)

Before calling any `scripts` code, verify the environment:

```bash
# 1. Check WSL
wsl -l -v 2>&1

# 2. Check NLE inside WSL
wsl -d Ubuntu -- python3 -c "import nle; print('ok')" 2>&1
```

- WSL missing → ask user if they want to install it
- NLE missing → ask user if they want to install it
- Both OK → proceed

Install WSL:
1. `powershell.exe -Command "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart"`
2. `powershell.exe -Command "Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart"`
3. Prompt user to reboot, then continue
4. `powershell.exe -Command "wsl --install --no-distribution"`
5. Import Ubuntu rootfs: `wsl --import Ubuntu <target-path> <rootfs-path> --version 2`

Install NLE:
```bash
wsl -d Ubuntu -- bash -c "apt-get update -qq && apt-get install -y -qq python3 python3-pip cmake build-essential libncurses-dev bison flex && pip3 install nle gymnasium"
```

## Trigger keywords

nethack / NetHack / NLE / play nethack / AI plays NetHack

## Usage

```python
from scripts import create_env

env = create_env(character='wizard')  # or None for random

state = env.reset()   # returns readable game state string
state = env.step('north')   # execute action, returns new state
```

## Available Actions

Actions must exactly match the table below. NLE v1.2.0 mappings — if `ACTION_MAP` in `scripts/env.py` differs, fix it first:

| Action | NLE index | Description |
|--------|-----------|-------------|
| north | 0 | move north |
| east | 1 | move east |
| south | 2 | move south |
| west | 3 | move west |
| northeast | 4 | move NE |
| southeast | 5 | move SE |
| southwest | 6 | move SW |
| northwest | 7 | move NW |
| wait | 18 | wait one turn |
| search | 75 | search for hidden doors/traps |
| descend | 17 | go down stairs (`>`) |
| ascend | 16 | go up stairs (`<`) |
| pickup | 61 | pick up item underfoot |
| eat | 35 | eat |
| drink | 64 | quaff potion |
| open | 57 | open door |

> **Critical**: old mappings (north=1, pickup=44) are wrong for NLE 1.2.0 and will break all movement. Always verify before running.

## render() output format

```
Turn 0 | Dlvl:1 | HP:14/14 | AC:10 | XP:1 | Gold:0
Message: Hello, wizard.
[24-line ASCII map]
Inventory (1): a) +1 quarterstaff
```

## Wiki Lookup (MANDATORY)

`wiki_lookup` is available via `from scripts import wiki_lookup`. You MUST use it — do not guess.

**Trigger it immediately when:**
- You see a monster you don't recognize (e.g. `n`, `j`, `f`, `d`, `x` on the map) → `wiki_lookup('newt')`, `wiki_lookup('jackal')`, etc.
- You see an unknown map symbol (e.g. `:`, `^`, `_`, `{`) → `wiki_lookup('fountain')`, `wiki_lookup('trap')`, etc.
- HP drops suddenly without an obvious cause → look up the monster that attacked
- You find an unidentified item (potion, scroll, wand) → `wiki_lookup('potion of healing')`, etc.
- You are unsure about a game mechanic → look it up before acting

**How to call it:**
```python
from scripts import wiki_lookup
info = wiki_lookup('newt')   # returns first ~800 chars from nethackwiki.com
print(info)
```

If `wiki_lookup` returns `None`, the page doesn't exist — try a different search term.

**Do NOT skip this step** to save turns. One wiki lookup can prevent a death.

**After every lookup, record what you learned:**
- New monster → `save_monster(...)` then it's in `monsters.json` permanently
- New item (identified) → `save_item(...)` then it's in `items.json` permanently
- New map symbol → add a row to the Symbol reference table below
- New mechanic or rule → add a bullet to the relevant section in this file
- Do this during the run, not after. Knowledge that isn't written down is lost next session.

### Monster lookup workflow

```python
from scripts import lookup_monster, save_monster, wiki_lookup

# 1. check local DB first
info = lookup_monster('newt')
if info is None:
    # 2. not found — query wiki
    raw = wiki_lookup('newt')
    # 3. extract key facts and save permanently
    save_monster(name='newt', symbol='n', threat='low',
                 notes='Can drain stats. Let pet handle.')
    info = lookup_monster('newt')
# 4. use info to decide action
```

### Item lookup workflow

```python
from scripts import lookup_item, save_item, wiki_lookup

# 1. check local DB first (use identified name, not appearance)
info = lookup_item('potion of healing')
if info is None:
    # 2. not found — query wiki
    raw = wiki_lookup('potion of healing')
    # 3. save permanently
    save_item(name='potion of healing', category='potion',
              effect='restores HP', notes='use when HP < 60%')
    info = lookup_item('potion of healing')
# 4. use info to decide action

# NOTE: unidentified items (e.g. 'blue potion') — do NOT save until identified.
# Use scroll of identify first, then save with the real name.
```

**After a successful lookup, you MUST record what you learned:**
- If it's a monster → add a row to the Monster reference table below
- If it's a map symbol → add a row to the Symbol reference table below
- If it's a game mechanic or role strategy → add a note to the relevant section
- Update SKILL.md immediately, before taking your next action

This ensures knowledge accumulates across runs and you never look up the same thing twice.

---

## Agent Decision Guide

### Map symbols

| Symbol | Meaning |
|--------|---------|
| `@` | you |
| `>` | stairs DOWN — primary goal each level |
| `<` | stairs UP — do NOT use ascend unless standing on `<` |
| `#` | corridor — leads to new rooms, always follow |
| `+` | closed door — move into it to open, leads to new rooms |
| `.` | floor (passable) |
| `\|` `-` | walls (impassable) |
| `$` | gold |
| `%` | corpse / food |
| `f` | kitten (your pet) |

### Core rules

1. **Read Message every turn**
   - `"It's a wall."` / `"You can't go"` → that direction is blocked, pick a different one immediately, never retry it
   - `"You swap places with your kitten."` → normal, pet was in the way

2. **Primary objective**: find `>` and use `descend`. That is the goal every level. `<` is NOT the exit.

3. **Explore systematically**
   - When you see `+` (closed door) → move toward it and open it, it leads to a new room
   - When you see `#` (corridor) → follow it, it connects rooms
   - Walk the perimeter of each room to find all exits before backtracking
   - Unexplored areas are always in directions you haven't walked yet

4. **Anti-loop rule**
   - If you have moved the same direction 3+ turns in a row without progress → stop, change direction now
   - If you are pacing east/west repeatedly in the same room → you are looping, go north or south instead
   - If you notice you are revisiting the same tiles → use `search` near walls, then try a completely different direction

5. **Standard opening sequence**
   1. Read Message, identify `@` position and passable directions
   2. Pick up any `$` nearby
   3. Find room exits: doors `.` or corridors `#`
   4. Follow corridors to find `>`, then `descend`
   5. If surrounded with no visible exits → use `search` to find hidden doors

6. **Never do these**
   - Don't retry a direction that just gave "It's a wall"
   - Don't use `west` into `|` (wall)
   - Don't use a movement action on a closed door `+` — use `open` or just walk into it
   - Don't use `ascend` when standing on `<` unless you intend to go up

### Last-action context

Each turn you will see a `[Last action: X | Result: Y]` prefix in the state. Use it:
- If Result contains "wall" or "can't" → that direction failed, do NOT repeat it
- If Result is "ok" → action succeeded, continue in that direction or reassess

### Wiki lookup — MANDATORY

`wiki_lookup` is available via `from scripts import wiki_lookup`. You MUST call it in these situations — do not skip:

| Trigger | Query |
|---------|-------|
| Unknown map symbol (`:` `^` `_` etc.) | `wiki_lookup('fountain')`, `wiki_lookup('trap')`, etc. |
| First encounter with any monster | `wiki_lookup('newt')`, `wiki_lookup('fox')`, etc. |
| Unsure about an item | `wiki_lookup('potion of healing')`, etc. |
| Role-specific strategy at game start | `wiki_lookup('wizard')`, `wiki_lookup('valkyrie')`, etc. |
| Any message you don't understand | `wiki_lookup('the message text')` |

Call wiki_lookup **before deciding your action**, not after. If the result is None (network error), proceed with best guess and note it.

```python
from scripts import wiki_lookup
info = wiki_lookup('newt')
# use info to decide: flee, fight, or let pet handle it
```

### Combat rules (role-aware)

- **Wizard / Healer / Priest**: do NOT melee. Stay behind your pet. Let the kitten attack first.
- HP < 60% + visible enemy → flee mode: move away from enemy, toward `<` or a narrow `#` corridor
- HP < 40% → use healing potion if available, then flee
- Never fight multiple enemies at once — use corridors to funnel them one at a time
- `wait` lets your pet move first and draw aggro

### Symbol reference (extended)

> When you look up a new symbol and learn what it is, add a row here immediately.

| Symbol | Meaning | Action |
|--------|---------|--------|
| `:` | pool / fountain / grave | `wiki_lookup('fountain')` before stepping on it |
| `^` | trap | avoid or `wiki_lookup('trap')` |
| `_` | altar | `wiki_lookup('altar')` — can be useful or dangerous |
| `{` | fountain | `wiki_lookup('fountain')` |
| `d` `j` `r` etc. | monsters | `wiki_lookup` the monster name from Message |
| `f` | kitten (your pet) | do NOT attack, let it fight |

### Monster reference (accumulated)

> When you look up a monster for the first time, add a row here immediately.

| Monster | Symbol | Threat | Notes |
|---------|--------|--------|-------|
| newt | `n` | low dmg but can drain stats | do NOT melee as wizard, let pet handle |
| jackal | `j` | low | fast, let pet handle or flee |
| fox | `f` (sometimes) | low-medium | faster than jackal, flee if HP < 60% |

## Character options

`character` format: `role-race-gender-align`
Examples: `wizard-human-male-neutral`, `knight`, `valkyrie`

## Post-game (MANDATORY after every run)

When `[GAME OVER]` appears in state, `play.py` automatically saves a placeholder record to `nethack_memory.json` and writes `/tmp/nethack_gameover`.

You MUST then:
1. Read `/tmp/nethack_gameover` to get the final state
2. Analyze: cause of death, depth reached, key mistakes
3. Update the memory record with real lessons:

```python
from scripts import Memory
memory = Memory("/mnt/c/Users/ASUS/.kimi/skills/nethack_agent_player/nethack_memory.json")
memory.save({
    "turns": <total turns>,
    "depth": <final dlvl>,
    "cause": "<what killed you>",
    "lessons": [
        "<lesson 1>",
        "<lesson 2>",
    ],
})
```

4. Update `SKILL.md` if a new rule should be added permanently
5. Check `memory.load()` at the start of the next run to recall past lessons

## Changelog

- v4.0.0 (2026-04-19): Rewritten in English. Added anti-loop rules, door exploration, `<` vs `>` clarification, last-action context guide.
- v3.0.0 (2026-04-19): Refactored, removed translation layer, direct TTY rendering
