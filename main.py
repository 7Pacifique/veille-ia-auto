#!/usr/bin/env python3
"""
main.py
-------
Point d'entrée : lance une veille complète sur un sujet donné.

Pipeline :
  1. Récupère les actus des dernières 24h (Google News RSS, sans clé API)
  2. Sélectionne et résume les plus marquantes via GROQ (API GROQ)
  3. Génère une présentation via l'API Gamma
  4. Journalise le résultat dans l'historique local (data/history.json)

Usage :
    python main.py "intelligence artificielle Bénin"
    python main.py "intelligence artificielle Bénin" --max 10 --hours 48
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from src import history
from src.gamma_client import generate_presentation
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

    print(f"🔎 Recherche des actualités sur « {args.topic} » (dernières {args.hours}h)...")
    raw_items = fetch_news(args.topic, hours=args.hours, max_results=args.max * 3)

    if not raw_items:
        print("⚠️  Aucune actualité trouvée dans cette fenêtre temporelle. Essaie d'élargir "
              "--hours ou de reformuler le sujet.")
        return 1

    print(f"   → {len(raw_items)} actus brutes récupérées.")

    print("🧠 Sélection et résumé via GROQ...")
    try:
        summarized = summarize_news(raw_items, topic=args.topic, max_items=args.max)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1

    if not summarized:
        print("⚠️  Aucune actu retenue après résumé.")
        return 1

    print(f"   → {len(summarized)} actus retenues :")
    for i, item in enumerate(summarized, 1):
        print(f"     {i}. {item['titre']} ({item['source']})")

    print("\n🎨 Génération de la présentation via Gamma...")
    try:
        result = generate_presentation(args.topic, summarized)
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return 1

    gamma_url = result.get("gammaUrl", "")
    print(f"✅ Présentation prête : {gamma_url}")

    history.add_entry(topic=args.topic, count=len(summarized), gamma_url=gamma_url)
    print("📝 Entrée ajoutée à l'historique (data/history.json)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
