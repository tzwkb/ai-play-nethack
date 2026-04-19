import os
import json
from datetime import datetime


class GameLogger:
    def __init__(self, log_dir, model, character):
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.path = os.path.join(log_dir, f'game_{ts}.json')
        self.data = {
            'meta': {
                'model': model,
                'character': character or 'random',
                'started_at': datetime.now().isoformat(),
            },
            'turns': [],
            'result': None,
        }

    def log_turn(self, turn, state, messages, api_response, action):
        hp, max_hp, dlvl = None, None, None
        import re
        m = re.search(r'HP:(\d+)/(\d+)', state)
        if m:
            hp, max_hp = int(m.group(1)), int(m.group(2))
        m2 = re.search(r'Dlvl:(\d+)', state)
        if m2:
            dlvl = int(m2.group(1))

        self.data['turns'].append({
            'turn': turn,
            'state': state,
            'messages': messages,
            'api_response': api_response,
            'action': action,
            'hp': [hp, max_hp],
            'dlvl': dlvl,
        })
        self._write()

    def log_result(self, cause, lessons, total_turns, final_depth):
        self.data['result'] = {
            'cause': cause,
            'lessons': lessons,
            'total_turns': total_turns,
            'final_depth': final_depth,
            'ended_at': datetime.now().isoformat(),
        }
        self._write()

    def _write(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
