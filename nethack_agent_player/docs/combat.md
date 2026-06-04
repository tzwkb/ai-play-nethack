# Combat

## Default stance by role

| Role | Default | Exception |
|------|---------|-----------|
| Wizard / Healer / Priest | avoid melee | see below |
| Valkyrie / Barbarian / Caveman | melee OK | flee if outnumbered |
| Others | avoid if possible | — |

## Melee exceptions (wizard/healer/priest)

Melee is acceptable when ANY of these apply:
- 1-tile-wide corridor and pet cannot reach the enemy
- Single low-threat enemy (grid bug, jackal) AND HP > 60%
- Surrounded with no escape route

## HP thresholds

| HP | Action |
|----|--------|
| < 30% + clearly dangerous enemy (dragon, demon, high-XP monster) | flee toward `<` or narrow `#` corridor |
| < 20% | use healing potion if available |
| < 10% | use best healing available, pray if no potions |

**Low HP alone is NOT a reason to flee.** If the enemy is weak (jackal, grid bug, newt, kobold, etc.), fight even at low HP — fleeing wastes turns and may not be possible anyway. Judge the threat, not just your HP.

## Tactics

- `wait` → lets pet move first and draw aggro
- Funnel enemies into corridors — fight one at a time, never in open rooms
- Diagonal movement to dodge grid bugs (they only move cardinally)
- **Floating eye** (`e`): NEVER melee — paralyzes you. Use wand or let pet handle.
- **Gas spore** (`e`): NEVER melee — explodes on death. Flee immediately.
- **Nymph** (`n`): steals items. Flee on sight.

## Pet management

- Do NOT attack your pet (kitten `f`, little dog `d`)
- Pet blocking path → **move in the pet's direction to swap places** ("You swap places with your kitten") — do NOT wait
- `wait` is only needed when you want the pet to act first (draw aggro), not to unblock it
- Pet fights for you — stay behind it when possible
