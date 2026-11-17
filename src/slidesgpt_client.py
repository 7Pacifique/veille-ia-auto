"""
slidesgpt_client.py
--------------------
Génère une présentation via l'API SlidesGPT à partir des actus résumées.

Documentation : https://slidesgpt.com/docs/getting-started/generate-presentation
"""

from __future__ import annotations

import os
from datetime import date

import requests

SLIDESGPT_API_URL = "https://api.slidesgpt.com/v1/presentations/generate"
REQUEST_TIMEOUT_SECONDS = 120  # la génération peut prendre 1-2 minutes


def _build_prompt(topic: str, news_items: list[dict], today: date) -> str:
    """Construit le prompt (toutes les actus) envoyé à SlidesGPT."""
    date_str = today.strftime("%d %B %Y")
    header = (
        f"Crée une présentation professionnelle et épurée intitulée "
        f"« Veille – {topic} – {date_str} ». "
        f"Une slide de titre, puis une slide par actualité ci-dessous, "
        f"chacune avec son titre, son résumé et sa source.\n\n"
    )

    sections = []
    for item in news_items:
        sections.append(
            f"{item['titre']}\n{item['resume']}\nSource : {item['source']}"
        )

    return header + "\n\n".join(sections)


def generate_presentation(
    topic: str,
    news_items: list[dict],
    today: date | None = None,
) -> dict:
    """
    Lance la génération d'une présentation SlidesGPT et retourne le résultat.

    Args:
        topic: Sujet de la veille (utilisé pour le titre).
        news_items: Liste de dicts {"titre", "resume", "source"}.
        today: Date à afficher sur la slide de titre (par défaut : aujourd'hui).

    Returns:
        Dict avec "gammaUrl" (clé conservée pour compatibilité avec le reste
        du pipeline – contient le lien slidesgpt.com/presentation/{id},
        reconstruit à partir de l'identifiant renvoyé par l'API).

    Raises:
        RuntimeError: si la clé API SlidesGPT est manquante, ou si la
            génération échoue.
    """
    api_key = os.environ.get("SLIDESGPT_API_KEY")
    if not api_key:
        raise RuntimeError(
            "SLIDESGPT_API_KEY manquante. Ajoute-la dans ton fichier .env "
            "(voir .env.example). Clé disponible sur https://slidesgpt.com/"
        )

    today = today or date.today()
    prompt = _build_prompt(topic, news_items, today)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    resp = requests.post(
        SLIDESGPT_API_URL,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if not resp.ok:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"Erreur API SlidesGPT ({resp.status_code}) : {detail}")

    data = resp.json()

    embed_url = data.get("embed", "")
    download_url = data.get("download", "")
    presentation_id = data.get("id", "")

    if not embed_url and not download_url:
        raise RuntimeError(f"La génération SlidesGPT a échoué : {data}")

    # Lien web reconstruit à partir de l'ID, vu dans l'interface SlidesGPT
    # ("Récents") une fois connecté. Non documenté par l'API officielle,
    # mais confirmé fonctionnel (y compris pour des tiers sans session active).
    web_url = f"https://slidesgpt.com/presentation/{presentation_id}" if presentation_id else ""

    return {
        "gammaUrl": web_url or embed_url,  # clé conservée pour compatibilité avec main.py / history.py
        "presentationId": presentation_id,
    }
