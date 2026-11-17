"""
emailer.py
----------
Envoie un email récapitulatif de la veille via SMTP Gmail.

Nécessite un "mot de passe d'application" Gmail (pas ton mot de passe normal) :
https://myaccount.google.com/apppasswords
(la validation en 2 étapes doit être activée sur le compte Google au préalable)
"""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_veille_email(
    topic: str,
    count: int,
    presentation_url: str,
    run_date: str,
    embed_url: str = "",
    download_url: str = "",
) -> None:
    """
    Envoie un email récapitulatif de la veille effectuée.

    Args:
        topic: Sujet de la veille.
        count: Nombre d'actus retenues.
        presentation_url: Lien principal vers la présentation (le lien web
            slidesgpt.com/presentation/{id}, expérimental et non garanti).
        run_date: Date de la veille (format libre, ex: "16/11/2026").
        embed_url: Lien officiel d'aperçu (Microsoft PowerPoint Online),
            fourni en secours si le lien principal ne fonctionne pas.
        download_url: Lien officiel de téléchargement direct du .pptx,
            fourni en secours si le lien principal ne fonctionne pas.

    Raises:
        RuntimeError: si les variables d'environnement nécessaires sont
            manquantes (EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECIPIENT),
            ou si l'envoi échoue.
    """
    sender = os.environ.get("EMAIL_SENDER")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    recipient = os.environ.get("EMAIL_RECIPIENT")

    missing = [
        name
        for name, value in [
            ("EMAIL_SENDER", sender),
            ("EMAIL_APP_PASSWORD", app_password),
            ("EMAIL_RECIPIENT", recipient),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Variable(s) manquante(s) pour l'envoi d'email : {', '.join(missing)}. "
            "Ajoute-les dans ton fichier .env (voir .env.example)."
        )

    subject = f"Veille {topic} – {run_date}"

    lines = [
        "Bonjour,",
        "",
        f"Ta veille quotidienne sur « {topic} » est prête.",
        "",
        f"{count} actualité(s) retenue(s)",
        f"Présentation : {presentation_url}",
    ]
    if embed_url:
        lines.append(f"Aperçu (secours) : {embed_url}")
    if download_url:
        lines.append(f"Téléchargement direct .pptx (secours) : {download_url}")
    lines += ["", "Généré automatiquement par veille-ia-gamma"]

    body = "\n".join(lines)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, [recipient], msg.as_string())
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"Échec de l'envoi de l'email : {exc}") from exc
