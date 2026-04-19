import json
import os
from datetime import datetime


class Memory:
    def __init__(self, path="./run_history.json"):
        self.path = path

    def load(self, last_n=5):
        if not os.path.exists(self.path):
            return ""
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        games = data.get("games", [])[-last_n:]
        if not games:
            return ""
        lines = ["Past lessons:"]
        for g in games:
            lines.append(f"- Depth {g.get('depth',1)}, Turn {g.get('turns',0)}: {g.get('cause','unknown')}")
            for lesson in g.get("lessons", []):
                lines.append(f"  * {lesson}")
        return '\n'.join(lines)

    def save(self, record):
        if os.path.exists(self.path):
            with open(self.path, encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"games": []}
        record.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
        data["games"].append(record)
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
