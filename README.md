# 📡 Veille Auto → Gamma

Automatise ta veille quotidienne : recherche les actualités les plus récentes sur un sujet, les résume avec l'IA, puis génère automatiquement une présentation visuelle avec [Gamma](https://gamma.app).

**Pipeline en 3 étapes :**

```
[Recherche web RSS] → [Résumé & sélection via Claude] → [Présentation générée par Gamma]
```

## ✨ Fonctionnalités

- 🔎 Récupère les actualités des dernières **24h** (configurable) sur n'importe quel sujet, via Google News RSS — **aucune clé API requise pour cette étape**
- 🧠 Sélectionne et résume les actus les plus marquantes avec **Claude** (API Anthropic) : titre clair, résumé en 2-3 phrases, source
- 🎨 Génère automatiquement une **présentation Gamma** : une slide de titre datée + une slide par actualité, style épuré
- 📝 Garde un **historique local** (`data/history.json`) de toutes les veilles effectuées
- 🔧 Plafond de sécurité configurable (15 actus max par défaut) pour éviter les présentations surchargées

## 📦 Installation

```bash
git clone https://github.com/<ton-username>/veille-ia-gamma.git
cd veille-ia-gamma
pip install -r requirements.txt
```

## 🔑 Configuration

1. Copie le fichier d'exemple :
   ```bash
   cp .env.example .env
   ```
2. Renseigne tes clés API dans `.env` :
   - **Anthropic (Claude)** : crée une clé sur [console.anthropic.com](https://console.anthropic.com/settings/keys)
   - **Gamma** : crée une clé sur [gamma.app/settings/api-keys](https://gamma.app/settings/api-keys)

## 🚀 Utilisation

```bash
python main.py "intelligence artificielle Bénin"
```

Options disponibles :

```bash
python main.py "IA Afrique de l'Ouest" --hours 48 --max 10
```

| Option    | Description                                      | Défaut |
|-----------|---------------------------------------------------|--------|
| `--hours` | Fenêtre temporelle de recherche (en heures)        | 24     |
| `--max`   | Nombre maximum d'actus retenues dans la présentation | 15   |

### Exemple de sortie

```
🔎 Recherche des actualités sur « intelligence artificielle Bénin » (dernières 24h)...
   → 12 actus brutes récupérées.
🧠 Sélection et résumé via Claude...
   → 7 actus retenues :
     1. Six pays d'Afrique de l'Ouest adoptent des lignes directrices communes sur l'IA (WeAreTechAfrica)
     2. Le Cyber Africa Forum 2026 s'ouvre à Cotonou (APAnews)
     ...

🎨 Génération de la présentation via Gamma...
✅ Présentation prête : https://gamma.app/docs/xxxxx
📝 Entrée ajoutée à l'historique (data/history.json)
```

## 🗂️ Structure du projet

```
veille-ia-gamma/
├── main.py                 # Point d'entrée (CLI)
├── src/
│   ├── news_fetcher.py     # Récupération des actus (Google News RSS)
│   ├── summarizer.py        # Sélection + résumé via l'API Anthropic
│   ├── gamma_client.py       # Génération de présentation via l'API Gamma
│   └── history.py           # Journalisation locale de l'historique
├── data/
│   └── history.json         # Historique des veilles (généré, non versionné)
├── .env.example              # Modèle pour les clés API
├── requirements.txt
└── README.md
```

## 🛠️ Stack technique

- **Python 3.10+**
- [`feedparser`](https://pypi.org/project/feedparser/) — lecture des flux RSS Google News
- [`anthropic`](https://pypi.org/project/anthropic/) — SDK officiel Claude pour le résumé
- [`requests`](https://pypi.org/project/requests/) — appels à l'API REST Gamma
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) — gestion des clés API locales

## 🗺️ Pistes d'évolution

- [ ] Export PDF/Markdown en plus de Gamma
- [ ] Automatisation via GitHub Actions (exécution planifiée quotidienne)
- [ ] Interface web légère pour consulter l'historique
- [ ] Support multi-sujets en une seule exécution

## 📄 Licence

MIT — libre d'utilisation et de modification.

---

Projet développé par **Pacifique**, dans le cadre de son travail sur [Prompt Art Director](https://github.com/<ton-username>) — direction artistique assistée par IA pour les créateurs et marques francophones d'Afrique.
