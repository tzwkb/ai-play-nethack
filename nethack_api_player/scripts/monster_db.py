import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "monsters.json")


def _load():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def lookup_monster(name: str) -> dict | None:
    """Return the monster record for `name`, or None if not in local DB."""
    db = _load()
    return db.get(name.strip().lower())


def save_monster(name: str, symbol: str, threat: str, notes: str, source: str = "wiki"):
    """Save a monster record. Call this after every wiki lookup for a new monster."""
    db = _load()
    db[name.strip().lower()] = {
        "name": name,
        "symbol": symbol,
        "threat": threat,
        "notes": notes,
        "source": source,
    }
    _save(db)
