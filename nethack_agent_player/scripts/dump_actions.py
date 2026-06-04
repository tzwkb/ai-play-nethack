"""Print all NLE action indices with their character and name.
Run inside WSL: python3 scripts/dump_actions.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import gymnasium as gym
import nle  # noqa: F401

env = gym.make('NetHack-v0', savedir=None, character='wiz-hum-mal-neu')
actions = env.unwrapped.actions
print(f"Total actions: {len(actions)}\n")
print(f"{'idx':>4}  {'char':>5}  {'ord':>4}  name")
print("-" * 40)
for i, a in enumerate(actions):
    val = getattr(a, 'value', None)
    ch = chr(val) if val is not None and 32 <= val < 127 else '?'
    print(f"{i:>4}  {ch:>5}  {val!s:>4}  {a}")
env.close()
