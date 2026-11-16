"""
summarizer.py
-------------
Utilise l'API Groq (gratuite, modèles Llama) pour sélectionner et résumer
les actualités les plus marquantes à partir d'une liste brute.

Groq est utilisé ici car il offre un accès gratuit généreux, sans carte
bancaire requise, via des modèles open-source rapides (Llama 3.3).
Clé API : https://console.groq.com/keys
"""

from __future__ import annotations

import json
import os

from groq import Groq

from .news_fetcher import NewsItem

MODEL = "openai/gpt-oss-120b"  # modèle Groq utilisé pour le résumé (gratuit)
MAX_OUTPUT_TOKENS = 6000  # reste sous la limite du modèle (8000) avec de la marge


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
    Envoie les actus brutes à Groq (Llama 3.3) pour sélection + résumé.

    Args:
        items: Liste des actus brutes (NewsItem).
        topic: Le sujet de la veille, pour donner du contexte au modèle.
        max_items: Nombre maximum d'actus à conserver dans le résultat final.

    Returns:
        Liste de dicts {"titre", "resume", "source"}, prête à être
        transmise au générateur de présentation.

    Raises:
        RuntimeError: si la clé API Groq n'est pas configurée, ou si la
            réponse du modèle n'est pas un JSON exploitable.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY manquante. Ajoute-la dans ton fichier .env "
            "(voir .env.example). Clé gratuite disponible sur https://console.groq.com/keys"
        )

    if not items:
        return []

    client = Groq(api_key=api_key)

    raw_list = "\n\n".join(
        f"- Titre : {item.title}\n  Source : {item.source}\n  Extrait : {item.summary[:150]}"
        for item in items
    )

    user_prompt = (
        f"Sujet de veille : {topic}\n"
        f"Nombre maximum d'actus à retenir : {max_items}\n\n"
        f"Voici les actualités brutes collectées :\n\n{raw_list}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.choices[0].message.content.strip()

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
            f"Réponse de Groq non-JSON, impossible de parser le résumé : {exc}\n"
            f"Réponse brute : {text[:500]}"
        ) from exc

    return result[:max_items]
