# Veille Auto -> SlidesGPT

Automatise ta veille quotidienne : recherche les actualités les plus récentes sur un sujet, les résume avec l'IA, puis génère automatiquement une présentation visuelle avec [SlidesGPT](https://slidesgpt.com).

**Pipeline :**

```
[Recherche web RSS] -> [Résumé & sélection via Groq] -> [Présentation SlidesGPT] -> [Email récapitulatif]
```

## Fonctionnalités

- Récupère les actualités des dernières **24h** (configurable) sur n'importe quel sujet, via Google News RSS – **aucune clé API requise pour cette étape**
- Sélectionne et résume les actus les plus marquantes avec **Groq** (modèle `openai/gpt-oss-120b`, accès gratuit sans carte bancaire) : titre clair, résumé en 2-3 phrases, source
- Génère automatiquement une **présentation SlidesGPT** : une slide de titre, puis une slide par actualité
- Envoie un **email récapitulatif** avec le lien principal de la présentation, plus deux liens de secours (aperçu et téléchargement direct du .pptx)
- Garde un **historique** (`data/history.json`, suivi par Git) de toutes les veilles effectuées
- Plafond de sécurité configurable (15 actus max par défaut)
- **Automatisable via GitHub Actions** : exécution planifiée quotidienne, sans PC allumé (voir ci-dessous)

## Installation

```bash
git clone https://github.com/7Pacifique/veille-ia-auto.git
cd veille-ia-auto
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

1. Copie le fichier d'exemple :
   ```bash
   cp .env.example .env
   ```
2. Renseigne tes clés API dans `.env` :
   - **Groq** (gratuit, sans carte bancaire) : crée une clé sur [console.groq.com/keys](https://console.groq.com/keys)
   - **SlidesGPT** : crée une clé sur [slidesgpt.com](https://slidesgpt.com/)
3. *(Optionnel)* Pour recevoir un email récapitulatif, renseigne aussi :
   - **EMAIL_SENDER** : ton adresse Gmail d'envoi
   - **EMAIL_APP_PASSWORD** : un "mot de passe d'application" Gmail – **pas** ton mot de passe normal. Génère-le sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (nécessite la validation en 2 étapes activée sur le compte Google)
   - **EMAIL_RECIPIENT** : l'adresse qui recevra le récapitulatif

   Si ces 3 variables sont absentes, l'étape d'email est simplement ignorée (le reste du pipeline fonctionne normalement).

## Utilisation

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
-> Recherche des actualités sur « intelligence artificielle Bénin » (dernières 24h)...
   -> 12 actus brutes récupérées.
-> Sélection et résumé via Groq...
   -> 7 actus retenues :
     1. Six pays d'Afrique de l'Ouest adoptent des lignes directrices communes sur l'IA (WeAreTechAfrica)
     2. Le Cyber Africa Forum 2026 s'ouvre à Cotonou (APAnews)
     ...

-> Génération de la présentation via SlidesGPT...
[OK] Présentation prête : https://slidesgpt.com/presentation/xxxxx
-> Entrée ajoutée à l'historique (data/history.json)
-> Envoi de l'email récapitulatif...
   -> Email envoyé.
```

## Structure du projet

```
veille-ia-auto/
├── main.py                      # Point d'entrée (CLI)
├── src/
│   ├── news_fetcher.py          # Récupération des actus (Google News RSS)
│   ├── summarizer.py            # Sélection + résumé via l'API Groq
│   ├── slidesgpt_client.py      # Génération de présentation via l'API SlidesGPT
│   ├── emailer.py                # Envoi de l'email récapitulatif (SMTP Gmail)
│   └── history.py                # Journalisation de l'historique
├── data/
│   └── history.json              # Historique des veilles (suivi par Git)
├── .github/workflows/
│   └── veille-quotidienne.yml    # Automatisation GitHub Actions
├── .env.example                   # Modèle pour les clés API
├── requirements.txt
└── README.md
```

## Stack technique

- **Python 3.10+**
- [`feedparser`](https://pypi.org/project/feedparser/) – lecture des flux RSS Google News
- [`groq`](https://pypi.org/project/groq/) – SDK officiel Groq pour le résumé, gratuit
- [`requests`](https://pypi.org/project/requests/) – appels à l'API REST SlidesGPT
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) – gestion des clés API locales
- `smtplib` (bibliothèque standard Python) – envoi de l'email récapitulatif

## Automatisation quotidienne (GitHub Actions)

Le workflow `.github/workflows/veille-quotidienne.yml` lance automatiquement
`python main.py "l'IA dans le monde"` tous les jours à 7h UTC (8h heure du
Bénin), sur les serveurs de GitHub – ton PC n'a pas besoin d'être allumé.

**Pour l'activer sur ton propre dépôt :**

1. Va dans **Settings -> Actions -> General**, section *Workflow permissions*,
   et sélectionne **"Read and write permissions"** (nécessaire pour que le
   workflow puisse committer l'historique mis à jour).
2. Va dans **Settings -> Secrets and variables -> Actions** et ajoute chaque
   clé comme secret (`New repository secret`) :
   - `GROQ_API_KEY`
   - `SLIDESGPT_API_KEY`
   - `EMAIL_SENDER`, `EMAIL_APP_PASSWORD`, `EMAIL_RECIPIENT` (si tu veux l'email)
3. Le workflow se déclenche automatiquement chaque jour. Tu peux aussi le
   lancer manuellement depuis l'onglet **Actions** du repo -> *Veille
   quotidienne* -> *Run workflow*.
4. L'historique (`data/history.json`) est committé automatiquement par le
   workflow après chaque exécution, pour rester synchronisé entre les runs.

Pour changer le sujet ou l'horaire, modifie directement les champs `cron`
et la commande `python main.py "..."` dans le fichier du workflow.

> **Note sur le lien envoyé par email :** il s'agit du lien
> `slidesgpt.com/presentation/{id}`, reconstruit à partir de l'identifiant
> renvoyé par l'API. Ce lien n'est pas documenté officiellement par
> SlidesGPT, mais s'est révélé fiable à l'usage, y compris pour des tiers
> sans session active sur le compte SlidesGPT.

> **Note sur un changement de fournisseur futur :** si tu changes à nouveau
> de service de génération de présentation, seul le fichier
> `src/slidesgpt_client.py` a besoin d'être adapté ou remplacé – le reste du
> pipeline (recherche, résumé, email, historique) n'est pas concerné.

## Pistes d'évolution

- [ ] Export PDF/Markdown en plus de SlidesGPT
- [ ] Interface web légère pour consulter l'historique
- [ ] Support multi-sujets en une seule exécution

## Licence

MIT – libre d'utilisation et de modification.

---

Projet développé par **Pacifique**, AI Software Builder.
