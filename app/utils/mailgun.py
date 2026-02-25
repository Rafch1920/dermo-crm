# -*- coding: utf-8 -*-
"""
Envoi d'emails via API Mailgun HTTP (contourne le blocage SMTP de Render)
"""
import requests
from flask import current_app


def send_email(to, subject, body, html=None):
    """
    Envoie un email via l'API Mailgun HTTP
    Retourne (success: bool, message: str)
    """
    try:
        # Récupère la config
        domain = current_app.config.get('MAILGUN_DOMAIN')
        api_key = current_app.config.get('MAILGUN_API_KEY')
        from_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        if not domain or not api_key:
            return False, "Configuration Mailgun manquante"
        
        # API Mailgun
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        auth = ("api", api_key)
        data = {
            "from": from_email,
            "to": to if isinstance(to, list) else [to],
            "subject": subject,
            "text": body
        }
        
        if html:
            data["html"] = html
        
        # Envoie la requête HTTP (port 443, jamais bloqué)
        response = requests.post(url, auth=auth, data=data, timeout=10)
        
        if response.status_code == 200:
            return True, "Email envoyé"
        else:
            return False, f"Erreur {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Erreur: {str(e)}"
