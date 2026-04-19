import os
import json
from datetime import datetime


def _t(key, **kwargs):
    try:
        from scripts.i18n import t
        return t(key, **kwargs)
    except Exception:
        return key


ACTION_MAP = {
    'north':     1,
    'east':      2,
    'south':     3,
    'west':      4,
    'northeast': 5,
    'southeast': 6,
    'southwest': 7,
    'northwest': 8,
    'ascend':    17,
    'descend':   18,
    'wait':      19,
    'eat':       21,
    'search':    22,
    'pickup':    19,
    'drink':     19,
    'open':      19,
}


class NLEEnv:
    def __init__(self, character=None, log_dir=None, verbose=False):
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
        self.verbose = verbose

    def reset(self):
        obs, _ = self.env.reset()
        self._obs = obs
        self.turn = 0
        self.history = []
        state = self.render(obs)
        if self.verbose:
            print(state)
        return state

    def step(self, action_name):
        action_int = ACTION_MAP.get(action_name.lower())
        if action_int is None:
            return f"Unknown action: {action_name}. Valid: {list(ACTION_MAP)}"

        obs, reward, done, truncated, info = self.env.step(action_int)
        self._obs = obs
        self.turn += 1

        state = self.render(obs)
        self.history.append({'turn': self.turn, 'action': action_name, 'reward': reward})

        if done or truncated:
            state += f"\n\n[{_t('game_over_label')}] reward={reward:.1f}"
            if self.log_dir:
                self._save_log(reward)

        if self.verbose:
            print(state)
        return state

    def render(self, obs=None):
        if obs is None:
            obs = self._obs
        b = obs['blstats']

        msg = bytes(obs['message']).decode('utf-8', errors='ignore').strip('\x00').strip()

        chars = obs['tty_chars']
        screen = '\n'.join(
            ''.join(chr(c) for c in row)
            for row in chars
        )

        inv_lines = []
        for i in range(55):
            item = bytes(obs['inv_strs'][i]).decode('utf-8', errors='ignore').strip('\x00').strip()
            if item:
                letter = chr(obs['inv_letters'][i]) if obs['inv_letters'][i] > 0 else '?'
                inv_lines.append(f"{letter}) {item}")

        if inv_lines:
            inv_str = f"{_t('inv_label')} ({len(inv_lines)}): " + '  '.join(inv_lines[:8])
        else:
            inv_str = _t('inv_empty')

        stats = (f"{_t('turn_label')} {self.turn} | Dlvl:{int(b[12])} | "
                 f"HP:{int(b[10])}/{int(b[11])} | AC:{int(b[16])} | "
                 f"XP:{int(b[19])} | Gold:{int(b[13])}")

        # spatial hints: player pos, stairs, exits
        px, py = int(b[8]), int(b[9])

        def to_direction(tx, ty):
            """Convert target coords to a single action word."""
            dx = tx - px
            dy = ty - py
            if dx == 0 and dy == 0:
                return 'descend'
            vert = 'south' if dy > 0 else 'north' if dy < 0 else ''
            horiz = 'east' if dx > 0 else 'west' if dx < 0 else ''
            return (vert + horiz) or 'wait'

        # scan map for key symbols
        stairs_down, doors, corridors = [], [], []
        for row in range(len(chars)):
            for col in range(len(chars[row])):
                c = chr(chars[row][col])
                if c == '>':
                    stairs_down.append((col, row))
                elif c == '+':
                    doors.append((col, row))
                elif c == '#':
                    corridors.append((col, row))

        hints = []
        if stairs_down:
            sx, sy = min(stairs_down, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
            if sx == px and sy == py:
                hints.append("ACTION: descend (you are standing on > right now).")
            else:
                d = to_direction(sx, sy)
                hints.append(f"ACTION: go {d} toward > (stairs down) at ({sx},{sy}).")
        else:
            hints.append("No > visible.")
            if doors:
                tx, ty = min(doors, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
                d = to_direction(tx, ty)
                hints.append(f"ACTION: go {d} toward nearest door (+) at ({tx},{ty}).")
            elif corridors:
                tx, ty = min(corridors, key=lambda p: abs(p[0]-px)+abs(p[1]-py))
                d = to_direction(tx, ty)
                hints.append(f"ACTION: go {d} toward corridor (#) at ({tx},{ty}).")
            else:
                hints.append("No doors or corridors visible — use search to find hidden exits.")

        nav = ' '.join(hints)

        parts = [stats]
        if msg:
            parts.append(f"{_t('msg_label')}: {msg}")
        parts.append(f"[NAV] {nav}")
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


def create_env(character=None, log_dir=None, verbose=False):
    return NLEEnv(character=character, log_dir=log_dir, verbose=verbose)
