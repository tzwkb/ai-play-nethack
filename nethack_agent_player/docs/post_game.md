# Post-game

Triggered when `[GAME OVER]` appears in state.

## Steps

1. Read `/tmp/nethack_gameover` for the final state
2. Analyze: cause of death, depth reached, key mistakes
3. Save lessons to memory:

```python
from scripts.memory import Memory

memory = Memory("nethack_memory.json")
memory.save({
    "turns": <total turns>,
    "depth": <final dlvl>,
    "cause": "<what killed you or why you stopped>",
    "lessons": [
        "<specific lesson 1>",
        "<specific lesson 2>",
    ],
})
```

4. If a new rule should apply to all future runs → update the relevant `docs/` file
5. At the start of the next run: `memory.load(last_n=5)` to recall past lessons

## Memory path

`nethack_memory.json` is in the project root.
