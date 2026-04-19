import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "items.json")


def _load():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def lookup_item(name: str) -> dict | None:
    """Return item record by identified name, or None if not in local DB.
    Always use the identified name (e.g. 'potion of healing'), not appearance.
    """
    db = _load()
    return db.get(name.strip().lower())


def save_item(name: str, category: str, effect: str, notes: str, source: str = "wiki"):
    """Save an item record after wiki lookup or identification.
    name: identified name, e.g. 'potion of healing'
    category: potion / scroll / wand / ring / amulet / weapon / armor / food / tool
    effect: brief description of what it does
    notes: tactical advice
    """
    db = _load()
    db[name.strip().lower()] = {
        "name": name,
        "category": category,
        "effect": effect,
        "notes": notes,
        "source": source,
    }
    _save(db)
