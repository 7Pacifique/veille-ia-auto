"""
history.py
-----------
Gère l'historique local des veilles effectuées (fichier JSON).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "data" / "history.json"


def _load() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(entries: list[dict]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def add_entry(topic: str, count: int, gamma_url: str, run_date: date | None = None) -> None:
    """Ajoute une veille à l'historique et sauvegarde le fichier."""
    run_date = run_date or date.today()
    entries = _load()
    entries.append(
        {
            "date": run_date.isoformat(),
            "topic": topic,
            "count": count,
            "gamma_url": gamma_url,
            "created_at": datetime.now().isoformat(),
        }
    )
    _save(entries)


def get_history() -> list[dict]:
    """Retourne l'historique complet, du plus récent au plus ancien."""
    return list(reversed(_load()))
