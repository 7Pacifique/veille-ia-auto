"""
news_fetcher.py
----------------
Récupère les actualités des dernières 24h sur un sujet donné,
via le flux RSS de Google News (gratuit, sans clé API).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from urllib.parse import quote_plus

import feedparser


@dataclass
class NewsItem:
    """Une actualité brute récupérée depuis le flux RSS."""

    title: str
    link: str
    source: str
    published: dt.datetime
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "published": self.published.isoformat(),
            "summary": self.summary,
        }


def _parse_published_date(entry) -> dt.datetime:
    """Extrait une date de publication exploitable depuis une entrée RSS."""
    if getattr(entry, "published_parsed", None):
        return dt.datetime(*entry.published_parsed[:6], tzinfo=dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc)


def fetch_news(
    topic: str,
    hours: int = 24,
    max_results: int = 15,
    language: str = "fr",
    country: str = "FR",
) -> list[NewsItem]:
    """
    Recherche les actualités sur `topic` publiées dans les `hours` dernières heures.

    Utilise le flux RSS public de Google News (aucune clé API requise).

    Args:
        topic: Sujet de recherche (ex: "intelligence artificielle Bénin").
        hours: Fenêtre temporelle en heures (par défaut 24h).
        max_results: Nombre maximum d'actus à retourner (plafond de sécurité).
        language: Code langue pour Google News (ex: "fr").
        country: Code pays pour Google News (ex: "FR", "BJ" peut être limité).

    Returns:
        Liste de NewsItem triée par date décroissante (plus récent en premier).
    """
    query = quote_plus(topic)
    feed_url = (
        f"https://news.google.com/rss/search?q={query}"
        f"&hl={language}&gl={country}&ceid={country}:{language}"
    )

    feed = feedparser.parse(feed_url)

    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    items: list[NewsItem] = []

    for entry in feed.entries:
        published = _parse_published_date(entry)
        if published < cutoff:
            continue

        source = ""
        if getattr(entry, "source", None):
            source = getattr(entry.source, "title", "") or ""
        if not source and hasattr(entry, "title"):
            # Google News met parfois la source à la fin du titre après " - "
            if " - " in entry.title:
                source = entry.title.rsplit(" - ", 1)[-1]

        items.append(
            NewsItem(
                title=entry.title,
                link=entry.link,
                source=source or "Source inconnue",
                published=published,
                summary=getattr(entry, "summary", ""),
            )
        )

    items.sort(key=lambda i: i.published, reverse=True)
    return items[:max_results]
