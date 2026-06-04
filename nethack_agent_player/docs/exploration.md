# Exploration

## Doorway mechanics

Passing through a closed door `+` takes **two steps**:
1. Move into `+` tile → door opens, you are now ON the door tile
2. Move again in the same direction → you exit

While standing ON a door tile: **diagonal movement is blocked**. Only N/S/E/W work.
`@` covers the door symbol — use `Features: Player: (x,y)` to confirm your position.

## Map tracking (maintain every turn)

```python
visited   = set()   # (x,y) tiles you have stood on
dead_ends = set()   # (x,y) tiles confirmed impassable
known_stairs = None # (x,y) of > once seen

# Each turn:
x, y = parse_player_pos(state)  # from Features line
visited.add((x, y))

# On blocked move:
dead_ends.add(neighbor_in_direction(x, y, failed_direction))

# On seeing > in Features:
known_stairs = parse_stairs_down(state)
```

Prefer unvisited tiles when choosing direction.

## Stairs not found — escalating protocol

Level 1 **always** has stairs down. If `Stairs↓(>): not found yet`:

1. Follow all unexplored `#` corridors and open all `+` doors
2. `search` on every wall tile, especially corners and dead-end corridors
3. **Wand of secret door detection in inventory** → zap in all 4 directions immediately (reveals all hidden doors)
4. **Scroll of magic mapping** → read it (reveals entire level)
5. **Potion of object detection** → drink it (shows all items including stairs)
6. Boulder blocking corridor → push it (walk into it); stairs may be behind it
7. Last resort: `search` 10+ times at dead-end corridor walls (hidden doors need multiple searches)

## Anti-loop rules

- Same direction 3+ turns with no position change → stop, pick a different direction
- Pacing east/west in same room → go north or south
- Revisiting same tiles → `search` near walls, then try a completely different direction
