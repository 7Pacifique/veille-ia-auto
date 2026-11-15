"""
gamma_client.py
----------------
Génère une présentation via l'API Gamma à partir des actus résumées.
Documentation officielle : https://developers.gamma.app/
"""

from __future__ import annotations

import os
import time
from datetime import date

import requests

GAMMA_API_BASE = "https://public-api.gamma.app/v1.0"
POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 180


def _build_input_text(topic: str, news_items: list[dict], today: date) -> str:
    """Construit le texte structuré (une section par actu) envoyé à Gamma."""
    date_str = today.strftime("%d %B %Y")
    header = f"Veille — {topic} — {date_str}\n"

    sections = []
    for item in news_items:
        sections.append(
            f"{item['titre']}\n{item['resume']}\nSource : {item['source']}"
        )

    # Le séparateur "---" indique à Gamma où couper les cartes (cardSplit=inputTextBreaks)
    return header + "\n\n---\n\n".join(sections)


def generate_presentation(
    topic: str,
    news_items: list[dict],
    today: date | None = None,
) -> dict:
    """
    Lance la génération d'une présentation Gamma (asynchrone) et attend le résultat.

    Args:
        topic: Sujet de la veille (utilisé pour le titre).
        news_items: Liste de dicts {"titre", "resume", "source"}.
        today: Date à afficher sur la slide de titre (par défaut : aujourd'hui).

    Returns:
        Dict avec au moins "gammaUrl" et "status".

    Raises:
        RuntimeError: si la clé API Gamma est manquante ou si la génération échoue.
    """
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GAMMA_API_KEY manquante. Ajoute-la dans ton fichier .env "
            "(voir .env.example). Clé disponible sur https://gamma.app/settings/api-keys"
        )

    today = today or date.today()
    input_text = _build_input_text(topic, news_items, today)

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {
        "inputText": input_text,
        "textMode": "preserve",
        "cardSplit": "inputTextBreaks",
        "format": "presentation",
        "title": f"Veille {topic} — {today.strftime('%d/%m/%Y')}",
        "additionalInstructions": "Style visuel épuré et moderne, sobre, professionnel.",
    }

    create_resp = requests.post(
        f"{GAMMA_API_BASE}/generations", headers=headers, json=payload, timeout=30
    )
    create_resp.raise_for_status()
    generation_id = create_resp.json()["generationId"]

    return _poll_until_done(generation_id, headers)


def _poll_until_done(generation_id: str, headers: dict) -> dict:
    """Interroge périodiquement le statut de génération jusqu'à complétion."""
    status_url = f"{GAMMA_API_BASE}/generations/{generation_id}"
    elapsed = 0

    while elapsed < POLL_TIMEOUT_SECONDS:
        resp = requests.get(status_url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "completed":
            return data
        if data.get("status") == "failed":
            raise RuntimeError(f"La génération Gamma a échoué : {data}")

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed += POLL_INTERVAL_SECONDS

    raise RuntimeError(
        f"Timeout : la génération Gamma n'a pas terminé après {POLL_TIMEOUT_SECONDS}s."
    )
