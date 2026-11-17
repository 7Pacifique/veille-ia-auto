#!/usr/bin/env python3
"""
main.py
-------
Point d'entrée : lance une veille complète sur un sujet donné.

Pipeline :
  1. Récupère les actus des dernières 24h (Google News RSS, sans clé API)
  2. Sélectionne et résume les plus marquantes via Groq (openai/gpt-oss-120b)
  3. Génère une présentation via l'API SlidesGPT
  4. Journalise le résultat dans l'historique local (data/history.json)
  5. Envoie un email récapitulatif (optionnel, si EMAIL_* est configuré)

Usage :
    python main.py "intelligence artificielle Bénin"
    python main.py "intelligence artificielle Bénin" --max 10 --hours 48
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from dotenv import load_dotenv

from src import history
from src.emailer import send_veille_email
from src.slidesgpt_client import generate_presentation
from src.news_fetcher import fetch_news
from src.summarizer import summarize_news


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lance une veille quotidienne automatisée sur un sujet donné."
    )
    parser.add_argument("topic", help="Sujet de la veille, ex: 'intelligence artificielle Bénin'")
    parser.add_argument(
        "--hours", type=int, default=24, help="Fenêtre temporelle en heures (défaut : 24)"
    )
    parser.add_argument(
        "--max", type=int, default=15, help="Nombre maximum d'actus à retenir (défaut : 15)"
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    print(f"-> Recherche des actualités sur « {args.topic} » (dernières {args.hours}h)...")
    raw_items = fetch_news(args.topic, hours=args.hours, max_results=args.max * 3)

    if not raw_items:
        print("! Aucune actualité trouvée dans cette fenêtre temporelle. Essaie d'élargir "
              "--hours ou de reformuler le sujet.")
        return 1

    print(f"   -> {len(raw_items)} actus brutes récupérées.")

    print("-> Sélection et résumé via Groq...")
    try:
        summarized = summarize_news(raw_items, topic=args.topic, max_items=args.max)
    except RuntimeError as exc:
        print(f"[ERREUR] {exc}")
        return 1

    if not summarized:
        print("! Aucune actu retenue après résumé.")
        return 1

    print(f"   -> {len(summarized)} actus retenues :")
    for i, item in enumerate(summarized, 1):
        print(f"     {i}. {item['titre']} ({item['source']})")

    print("\n-> Génération de la présentation via SlidesGPT...")
    try:
        result = generate_presentation(args.topic, summarized)
    except RuntimeError as exc:
        print(f"[ERREUR] {exc}")
        return 1

    presentation_url = result.get("slidesgptUrl", "")
    print(f"[OK] Présentation prête : {presentation_url}")

    history.add_entry(topic=args.topic, count=len(summarized), slidesgpt_url=presentation_url)
    print("-> Entrée ajoutée à l'historique (data/history.json)")

    print("-> Envoi de l'email récapitulatif...")
    try:
        send_veille_email(
            topic=args.topic,
            count=len(summarized),
            presentation_url=presentation_url,
            run_date=date.today().strftime("%d/%m/%Y"),
        )
        print("   -> Email envoyé.")
    except RuntimeError as exc:
        # Non bloquant : la veille a réussi même si l'email échoue.
        print(f"! Email non envoyé : {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
