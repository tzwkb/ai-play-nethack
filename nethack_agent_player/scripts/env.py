import os
import json
from datetime import datetime

ACTION_MAP = {
    'north': 0, 'east': 1, 'south': 2, 'west': 3,
    'northeast': 4, 'southeast': 5, 'southwest': 6, 'northwest': 7,
    'wait': 18, 'search': 75, 'descend': 17, 'ascend': 16,
    'pickup': 61, 'eat': 35, 'drink': 64,
    # 'open' removed: walking into a door auto-opens it in NetHack.
    # Command.OPEN (57) requires a follow-up direction prompt which
    # the file-polling loop cannot handle.
}

BLSTATS = ['x', 'y', 'str_pct', 'str', 'dex', 'con', 'int', 'wis', 'cha',
           'score', 'hp', 'hpmax', 'depth', 'gold', 'energy', 'energymax',
           'ac', 'monster_level', 'xp', 'xplevel', 'time', 'hunger',
           'carrying_cap', 'dungeon_num', 'level_num', 'prop_mask']


class NLEEnv:
    def __init__(self, character=None, log_dir=None):
        import gymnasium as gym
        import nle  # noqa: F401

        kwargs = {'savedir': None}
        if character:
            kwargs['character'] = character
            env_id = 'NetHack-v0'
        else:
            env_id = 'NetHackScore-v0'

        self.env = gym.make(env_id, **kwargs)
        self.log_dir = log_dir
        self.turn = 0
        self.history = []
        self._obs = None
        self.verbose = False
        self._explored = {}  # world (col, row) -> char

    def set_verbose(self, value):
        self.verbose = value

    def reset(self):
        ans = input('Print game state each turn? (y/n): ').strip().lower()
        self.verbose = ans == 'y'
        obs, _ = self.env.reset()
        self._obs = obs
        self.turn = 0
        self.history = []
        self._explored = {}
        state = self.render(obs)
        if self.verbose:
            print(state)
        return state

    def step(self, action_name):
        action_int = ACTION_MAP.get(action_name.lower())
        if action_int is None:
            return f'Unknown action: {action_name}. Valid: {list(ACTION_MAP)}'
        obs, reward, done, truncated, info = self.env.step(action_int)
        self._obs = obs
        self.turn += 1
        state = self.render(obs)
        self.history.append({'turn': self.turn, 'action': action_name, 'reward': reward})
        if done or truncated:
            state += f'\n\n[GAME OVER] reward={reward:.1f}'
            if self.log_dir:
                self._save_log(reward)
        if self.verbose:
            print(state)
        return state

    def _update_explored(self, obs):
        b = obs['blstats']
        px, py = int(b[0]), int(b[1])
        chars = obs['tty_chars']
        for row_i, row in enumerate(chars):
            for col_i, ch in enumerate(row):
                if chr(ch) == '@':
                    off_col = px - col_i
                    off_row = py - (row_i - 1)
                    for r, row2 in enumerate(chars):
                        for c, ch2 in enumerate(row2):
                            s = chr(ch2)
                            if s not in (' ', '\x00'):
                                self._explored[(c + off_col, (r - 1) + off_row)] = s
                    return
        for r, row in enumerate(chars):
            for c, ch in enumerate(row):
                s = chr(ch)
                if s not in (' ', '\x00'):
                    self._explored[(c, r - 1)] = s

    def render(self, obs=None):
        if obs is None:
            obs = self._obs
        self._update_explored(obs)
        b = obs['blstats']
        px, py = int(b[0]), int(b[1])
        msg = bytes(obs['message']).decode('utf-8', errors='ignore').strip('\x00').strip()
        screen = '\n'.join(
            ''.join(chr(c) for c in row)
            for row in obs['tty_chars']
        )
        inv_lines = []
        for i in range(55):
            item = bytes(obs['inv_strs'][i]).decode('utf-8', errors='ignore').strip('\x00').strip()
            if item:
                letter = chr(obs['inv_letters'][i]) if obs['inv_letters'][i] > 0 else '?'
                inv_lines.append(f'{letter}) {item}')
        inv_str = (f'Inventory ({len(inv_lines)}): ' + '  '.join(inv_lines[:8])
                   if inv_lines else 'Inventory: empty')
        stats = (f'Turn {self.turn} | Dlvl:{int(b[12])} | '
                 f'HP:{int(b[10])}/{int(b[11])} | AC:{int(b[16])} | '
                 f'XP:{int(b[19])} | Gold:{int(b[13])}')

        chars = obs['tty_chars']

        def to_dir(tx, ty):
            dx, dy = tx - px, ty - py
            v = 'south' if dy > 0 else 'north' if dy < 0 else ''
            h = 'east' if dx > 0 else 'west' if dx < 0 else ''
            return (v + h) or 'wait'

        stairs_down, doors, corridors = [], [], []
        for row in range(len(chars)):
            for col in range(len(chars[row])):
                c = chr(chars[row][col])
                wy = row - 1
                if c == '>':
                    stairs_down.append((col, wy))
                elif c == '+':
                    doors.append((col, wy))
                elif c == '#':
                    corridors.append((col, wy))

        hints = []
        if stairs_down:
            sx, sy = min(stairs_down, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
            if sx == px and sy == py:
                hints.append('ACTION: descend (standing on >).')
            else:
                hints.append(f'ACTION: go {to_dir(sx, sy)} toward > at ({sx},{sy}).')
        else:
            if doors:
                tx, ty = min(doors, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
                hints.append(f'ACTION: go {to_dir(tx, ty)} toward door (+) at ({tx},{ty}).')
            elif corridors:
                tx, ty = min(corridors, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
                hints.append(f'ACTION: go {to_dir(tx, ty)} toward corridor (#) at ({tx},{ty}).')
            else:
                hints.append('No exits visible - use search.')

        visited = sum(1 for v in self._explored.values() if v == '.')
        hints.append(f'Explored floor tiles: {visited}.')
        nav = ' '.join(hints)

        parts = [stats]
        if msg:
            parts.append(f'Message: {msg}')
        parts.append(f'[NAV] {nav}')
        parts.append(screen)
        parts.append(inv_str)
        return '\n'.join(parts)

    def _save_log(self, final_reward):
        os.makedirs(self.log_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.log_dir, f'game_{ts}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'turns': self.turn, 'reward': final_reward, 'history': self.history}, f)

    def close(self):
        self.env.close()


def create_env(character=None, log_dir=None):
    return NLEEnv(character=character, log_dir=log_dir)
