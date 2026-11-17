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
) -> None:
    """
    Envoie un email récapitulatif de la veille effectuée.

    Args:
        topic: Sujet de la veille.
        count: Nombre d'actus retenues.
        presentation_url: Lien vers la présentation (slidesgpt.com/presentation/{id}).
        run_date: Date de la veille (format libre, ex: "16/11/2026").

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

    body = (
        f"Bonjour Pacifique.,\n\n"
        f"Ta veille quotidienne sur « {topic} » est prête.\n\n"
        f"{count} actualité(s) retenue(s)\n"
        f"Présentation : {presentation_url}\n\n"
        f"Généré automatiquement par veille-ia-auto"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"veille-ia-auto <{sender}>"
    msg["To"] = recipient

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, [recipient], msg.as_string())
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"Échec de l'envoi de l'email : {exc}") from exc
