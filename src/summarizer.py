"""
summarizer.py
-------------
Utilise l'API Anthropic (Claude) pour sélectionner et résumer
les actualités les plus marquantes à partir d'une liste brute.
"""

from __future__ import annotations

import json
import os

import anthropic

from .news_fetcher import NewsItem

MODEL = "claude-sonnet-4-5"  # modèle Claude utilisé pour le résumé


SYSTEM_PROMPT = """Tu es un assistant de veille médiatique.
On te donne une liste brute d'actualités (titre, source, extrait).
Ta tâche : sélectionner les informations les plus marquantes et pertinentes,
en écartant les doublons et le contenu hors-sujet, puis produire pour chacune :
- un titre clair et concis (reformulé si besoin, en français)
- un résumé de 2 à 3 phrases
- la source d'origine

Réponds UNIQUEMENT en JSON valide, sous la forme d'une liste d'objets :
[{"titre": "...", "resume": "...", "source": "..."}, ...]
Aucun texte avant ou après le JSON."""


def summarize_news(items: list[NewsItem], topic: str, max_items: int = 15) -> list[dict]:
    """
    Envoie les actus brutes à Claude pour sélection + résumé.

    Args:
        items: Liste des actus brutes (NewsItem).
        topic: Le sujet de la veille, pour donner du contexte au modèle.
        max_items: Nombre maximum d'actus à conserver dans le résultat final.

    Returns:
        Liste de dicts {"titre", "resume", "source"}, prête à être
        transmise au générateur de présentation.

    Raises:
        RuntimeError: si la clé API Anthropic n'est pas configurée.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY manquante. Ajoute-la dans ton fichier .env "
            "(voir .env.example). Clé disponible sur https://console.anthropic.com/"
        )

    if not items:
        return []

    client = anthropic.Anthropic(api_key=api_key)

    raw_list = "\n\n".join(
        f"- Titre : {item.title}\n  Source : {item.source}\n  Extrait : {item.summary[:300]}"
        for item in items
    )

    user_prompt = (
        f"Sujet de veille : {topic}\n"
        f"Nombre maximum d'actus à retenir : {max_items}\n\n"
        f"Voici les actualités brutes collectées :\n\n{raw_list}"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text.strip()

    # Nettoyage au cas où le modèle entoure le JSON de balises markdown
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Réponse de Claude non-JSON, impossible de parser le résumé : {exc}\n"
            f"Réponse brute : {text[:500]}"
        ) from exc

    return result[:max_items]
