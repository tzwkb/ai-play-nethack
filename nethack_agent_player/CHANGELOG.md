# Changelog

## v5.2.0 (2026-04-20)
- Fixed `send_keys` IndexError: chars now resolved via `env.unwrapped.actions`, not `ord()`
- Added `/tmp/nethack_ready` IPC sync signal — eliminates blind-wait race condition
- Fixed `wiki.py` Cloudflare bypass: full browser UA + Accept headers + mirror fallback
- Expanded `monsters.json` 7→24 entries; `items.json` 7→21 entries
- Added `scripts/dump_actions.py` utility to print all NLE action indices
- Documented doorway two-step mechanic, diagonal block on door tile
- Added stairs search escalation protocol
- Added Windows IPC write pattern (UTF-8, no echo)

## v5.1.0 (2026-04-20)
- Added character selection phase via `/tmp/nethack_charselect` IPC

## v5.0.0 (2026-04-20)
- Added `send_keys()` for multi-step interactions
- Atomic file IPC via `os.replace`
- `try/finally` gameover guarantee in `play.py`
- Melee rule with explicit exceptions
- Internal map tracking rule

## v4.0.0 (2026-04-19)
- Rewritten in English
- Anti-loop rules, door exploration, `<` vs `>` clarification, last-action context guide

## v3.0.0 (2026-04-19)
- Refactored, removed translation layer, direct TTY rendering
