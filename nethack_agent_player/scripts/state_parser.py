import re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


@dataclass
class Monster:
    symbol: str
    x: int
    y: int
    name: str = ""


@dataclass
class FloorItem:
    symbol: str
    x: int
    y: int


@dataclass
class PassableMove:
    direction: str
    x: int
    y: int
    terrain: str
    has_monster: bool = False
    monster_symbol: str = ""


@dataclass
class GameState:
    turn: int = 0
    dlvl: int = 0
    hp: int = 0
    hp_max: int = 0
    ac: int = 0
    xp: int = 0
    gold: int = 0
    hunger: str = ""
    str_: int = 0
    dex: int = 0
    con: int = 0
    message: str = ""
    warnings: List[str] = field(default_factory=list)
    situation: str = ""
    player_x: int = 0
    player_y: int = 0
    player_terrain: str = ""
    stairs_down: List[Tuple[int, int]] = field(default_factory=list)
    stairs_up: List[Tuple[int, int]] = field(default_factory=list)
    monsters: List[Monster] = field(default_factory=list)
    items_on_floor: List[FloorItem] = field(default_factory=list)
    passable_moves: List[PassableMove] = field(default_factory=list)
    room_exits_corridors: List[Tuple[int, int]] = field(default_factory=list)
    room_exits_doors: List[Tuple[int, int]] = field(default_factory=list)
    unexplored_gaps: List[Tuple[int, int]] = field(default_factory=list)
    explored_stairs_down: List[Tuple[int, int]] = field(default_factory=list)
    explored_stairs_up: List[Tuple[int, int]] = field(default_factory=list)
    inventory: Dict[str, str] = field(default_factory=dict)
    inventory_count: int = 0
    map_lines: List[str] = field(default_factory=list)
    game_over: bool = False
    game_over_reward: float = 0.0


def _parse_coords(text: str) -> List[Tuple[int, int]]:
    """Parse '(x, y)' or '(x,y)' pairs from text."""
    return [(int(m[0]), int(m[1])) for m in re.findall(r'\((\d+),\s*(\d+)\)', text)]


def _parse_header(line: str) -> Dict[str, any]:
    result = {}
    # Turn N | Dlvl:D | HP:h/H | AC:a | XP:x | Gold:g | Hunger:H | Str:s Dex:d Con:c
    m = re.search(r'Turn\s+(\d+)', line)
    if m:
        result['turn'] = int(m.group(1))
    m = re.search(r'Dlvl:(\d+)', line)
    if m:
        result['dlvl'] = int(m.group(1))
    m = re.search(r'HP:(\d+)/(\d+)', line)
    if m:
        result['hp'] = int(m.group(1))
        result['hp_max'] = int(m.group(2))
    m = re.search(r'AC:(\d+)', line)
    if m:
        result['ac'] = int(m.group(1))
    m = re.search(r'XP:(\d+)', line)
    if m:
        result['xp'] = int(m.group(1))
    m = re.search(r'Gold:(\d+)', line)
    if m:
        result['gold'] = int(m.group(1))
    m = re.search(r'Hunger:([^|]+)', line)
    if m:
        result['hunger'] = m.group(1).strip()
    m = re.search(r'Str:(\d+)', line)
    if m:
        result['str_'] = int(m.group(1))
    m = re.search(r'Dex:(\d+)', line)
    if m:
        result['dex'] = int(m.group(1))
    m = re.search(r'Con:(\d+)', line)
    if m:
        result['con'] = int(m.group(1))
    return result


def _parse_player(line: str) -> Optional[Tuple[int, int, str]]:
    m = re.search(r'Player:\s*\((\d+),\s*(\d+)\)\s+on\s+(.*)', line)
    if m:
        return int(m.group(1)), int(m.group(2)), m.group(3).strip()
    return None


def _parse_monsters(line: str) -> List[Monster]:
    monsters = []
    # Pattern: sym@(x, y)  or  sym@(x,y)
    for m in re.finditer(r'([a-zA-Z&;:@])@\((\d+),\s*(\d+)\)', line):
        monsters.append(Monster(symbol=m.group(1), x=int(m.group(2)), y=int(m.group(3))))
    return monsters


def _parse_floor_items(line: str) -> List[FloorItem]:
    items = []
    for m in re.finditer(r'([!$%&()*+,\-./:;<=>?@\[\\\]^_`{|}~])@\((\d+),\s*(\d+)\)', line):
        items.append(FloorItem(symbol=m.group(1), x=int(m.group(2)), y=int(m.group(3))))
    return items


def _parse_passable_moves(line: str) -> List[PassableMove]:
    moves = []
    # north->(4,16)[floor], south->(4,18)[floor], east->(5,17)[MONSTER(h) humanoid]
    for m in re.finditer(r'([a-z]+)->\((\d+),(\d+)\)\[([^\]]+)\]', line):
        direction = m.group(1)
        x, y = int(m.group(2)), int(m.group(3))
        terrain = m.group(4)
        has_monster = 'MONSTER' in terrain
        monster_symbol = ""
        if has_monster:
            mm = re.search(r'MONSTER\(([a-zA-Z])\)', terrain)
            if mm:
                monster_symbol = mm.group(1)
            terrain = terrain.split(' - ')[-1].strip()
        moves.append(PassableMove(
            direction=direction, x=x, y=y, terrain=terrain,
            has_monster=has_monster, monster_symbol=monster_symbol
        ))
    return moves


def _parse_inventory(line: str) -> Tuple[int, Dict[str, str]]:
    # "Inventory (14): $) 10 gold pieces  a) a +1 long sword ..."
    m = re.match(r'Inventory\s*\((\d+)\):\s*(.*)', line)
    if not m:
        return 0, {}
    count = int(m.group(1))
    rest = m.group(2)
    inv = {}
    # Find all slot markers: single char followed by )
    # Slots can be: a-z, $, and sometimes other symbols
    markers = list(re.finditer(r'(?:^|\s+)([a-z$])\)\s+', rest))
    for i, marker in enumerate(markers):
        slot = marker.group(1)
        start = marker.end()
        if i + 1 < len(markers):
            end = markers[i + 1].start()
        else:
            end = len(rest)
        desc = rest[start:end].strip()
        inv[slot] = desc
    return count, inv


def parse_state(text: str) -> GameState:
    state = GameState()
    lines = text.splitlines()

    # Check game over
    if '[GAME OVER]' in text:
        state.game_over = True
        m = re.search(r'\[GAME OVER\]\s+reward=([\d.]+)', text)
        if m:
            state.game_over_reward = float(m.group(1))

    in_map = False
    map_lines = []
    inventory_line = ""

    for line in lines:
        stripped = line.strip()

        # Header line
        if stripped.startswith('Turn ') and '| Dlvl:' in stripped:
            state.__dict__.update(_parse_header(stripped))
            continue

        # Message
        if stripped.startswith('Message: '):
            state.message = stripped[len('Message: '):].strip()
            continue

        # Warnings
        if stripped.startswith('WARNING: '):
            state.warnings.append(stripped[len('WARNING: '):].strip())
            continue

        # Situation
        if stripped.startswith('SITUATION: '):
            state.situation = stripped[len('SITUATION: '):].strip()
            continue

        # Player
        if stripped.startswith('Player: '):
            parsed = _parse_player(stripped)
            if parsed:
                state.player_x, state.player_y, state.player_terrain = parsed
            continue

        # Stairs
        if stripped.startswith('Stairs down(>): '):
            state.stairs_down = _parse_coords(stripped)
            continue
        if stripped.startswith('Stairs up(<): '):
            state.stairs_up = _parse_coords(stripped)
            continue

        # Monsters
        if stripped.startswith('Monsters visible: '):
            state.monsters = _parse_monsters(stripped)
            continue

        # Items
        if stripped.startswith('Items on floor: '):
            state.items_on_floor = _parse_floor_items(stripped)
            continue

        # Passable moves
        if stripped.startswith('Passable moves: '):
            state.passable_moves = _parse_passable_moves(stripped)
            continue

        # Room exits
        if stripped.startswith('Room exits - corridors: '):
            state.room_exits_corridors = _parse_coords(stripped)
            continue
        if stripped.startswith('Room exits - open doors '):
            state.room_exits_doors = _parse_coords(stripped)
            continue
        if stripped.startswith('Room exits - unexplored gaps '):
            state.unexplored_gaps = _parse_coords(stripped)
            continue

        # Explored map
        if stripped.startswith('Explored map - stairs down(>) at: '):
            state.explored_stairs_down = _parse_coords(stripped)
            continue
        if stripped.startswith('Explored map - stairs up(<) at: '):
            state.explored_stairs_up = _parse_coords(stripped)
            continue

        # Inventory
        if stripped.startswith('Inventory '):
            inventory_line = stripped
            continue

        # Map section
        if stripped.startswith('Map (@ = you'):
            in_map = True
            continue
        if in_map:
            if re.match(r'^\s*\d+\s+', stripped) or re.match(r'^\s*\d+\s*$', stripped):
                map_lines.append(stripped)
            elif re.match(r'^\s+0\s+1', stripped):
                map_lines.append(stripped)

    # Parse inventory from collected line
    if inventory_line:
        state.inventory_count, state.inventory = _parse_inventory(inventory_line)

    state.map_lines = map_lines
    return state


def state_summary(state: GameState) -> str:
    """Return a concise one-line summary for logging."""
    parts = [
        f"T{state.turn} D{state.dlvl}",
        f"HP:{state.hp}/{state.hp_max}",
        f"AC:{state.ac} XP:{state.xp}",
        f"@({state.player_x},{state.player_y})",
    ]
    if state.monsters:
        parts.append(f"M:{len(state.monsters)}")
    if state.items_on_floor:
        parts.append(f"I:{len(state.items_on_floor)}")
    if state.message:
        parts.append(f'"{state.message[:40]}"')
    if state.warnings:
        parts.append(f"WARN:{len(state.warnings)}")
    return " | ".join(parts)
