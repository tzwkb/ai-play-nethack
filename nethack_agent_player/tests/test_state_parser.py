import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from state_parser import parse_state, state_summary, GameState


SAMPLE_STATE = """Turn 407 | Dlvl:3 | HP:12/35 | AC:6 | XP:71 | Gold:10 | Hunger:Not Hungry | Str:16 Dex:12 Con:18
Message: You miss the dwarf.
Features:
  WARNING: Low HP (12/35) - consider retreating
  SITUATION: Stairs down at (8, 14). ACTION: goto:8,14

  Player: (4,17) on room floor
  Stairs down(>): [(8, 14)]
  Stairs up(<): [(20, 19)]
  Monsters visible: h@(5, 16) G@(3, 3)
  Items on floor: %@(13, 11) $@(14, 11)
  Passable moves: north->(4,16)[floor], south->(4,18)[floor], west->(3,17)[floor], east->(5,17)[floor], northeast->(5,16)[MONSTER(h) humanoid]
  Room exits - corridors: [(20, 10)]
  Room exits - open doors (walk through): [(3, 14), (8, 12)]
  Room exits - unexplored gaps (go here!): [(1, 13), (1, 14)]
  Explored map - stairs down(>) at: [(8, 14)]
  Explored map - stairs up(<) at: [(20, 19)]

Map (@ = you, # = corridor, + = door, > = stairs down, < = stairs up):
   0         1         2
   012345678901234567890
 1
 2
Inventory (14): $) 10 gold pieces  a) a +1 long sword (weapon in hand)  b) a +0 dagger (alternate weapon; not wielded)  c) an uncursed +3 small shield (being worn)

[GAME OVER] reward=0.0
"""


def test_parse_header():
    s = parse_state(SAMPLE_STATE)
    assert s.turn == 407
    assert s.dlvl == 3
    assert s.hp == 12
    assert s.hp_max == 35
    assert s.ac == 6
    assert s.xp == 71
    assert s.gold == 10
    assert s.hunger == "Not Hungry"
    assert s.str_ == 16
    assert s.dex == 12
    assert s.con == 18


def test_parse_message():
    s = parse_state(SAMPLE_STATE)
    assert s.message == "You miss the dwarf."


def test_parse_warnings():
    s = parse_state(SAMPLE_STATE)
    assert len(s.warnings) == 1
    assert "Low HP" in s.warnings[0]


def test_parse_player():
    s = parse_state(SAMPLE_STATE)
    assert s.player_x == 4
    assert s.player_y == 17
    assert s.player_terrain == "room floor"


def test_parse_stairs():
    s = parse_state(SAMPLE_STATE)
    assert s.stairs_down == [(8, 14)]
    assert s.stairs_up == [(20, 19)]


def test_parse_monsters():
    s = parse_state(SAMPLE_STATE)
    assert len(s.monsters) == 2
    assert s.monsters[0].symbol == 'h'
    assert s.monsters[0].x == 5
    assert s.monsters[0].y == 16
    assert s.monsters[1].symbol == 'G'
    assert s.monsters[1].x == 3
    assert s.monsters[1].y == 3


def test_parse_items():
    s = parse_state(SAMPLE_STATE)
    assert len(s.items_on_floor) == 2
    assert s.items_on_floor[0].symbol == '%'
    assert s.items_on_floor[1].symbol == '$'


def test_parse_passable_moves():
    s = parse_state(SAMPLE_STATE)
    assert len(s.passable_moves) == 5
    moves = {m.direction: m for m in s.passable_moves}
    assert moves['northeast'].has_monster is True
    assert moves['northeast'].monster_symbol == 'h'
    assert moves['north'].has_monster is False


def test_parse_inventory():
    s = parse_state(SAMPLE_STATE)
    assert s.inventory_count == 14
    assert '$' in s.inventory
    assert 'a' in s.inventory
    assert 'long sword' in s.inventory['a']
    assert 'c' in s.inventory
    assert 'shield' in s.inventory['c']


def test_game_over():
    s = parse_state(SAMPLE_STATE)
    assert s.game_over is True
    assert s.game_over_reward == 0.0


def test_state_summary():
    s = parse_state(SAMPLE_STATE)
    summary = state_summary(s)
    assert "T407" in summary
    assert "D3" in summary
    assert "HP:12/35" in summary
    assert "M:2" in summary


if __name__ == "__main__":
    test_parse_header()
    test_parse_message()
    test_parse_warnings()
    test_parse_player()
    test_parse_stairs()
    test_parse_monsters()
    test_parse_items()
    test_parse_passable_moves()
    test_parse_inventory()
    test_game_over()
    test_state_summary()
    print("All state_parser tests passed.")
