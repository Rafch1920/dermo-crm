"""
Utilitaires de validation
"""
from flask import current_app


def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def allowed_image_file(filename):
    """Vérifie si le fichier est une image autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_IMAGE_EXTENSIONS']


def validate_phone(phone):
    """Valide un numéro de téléphone français"""
    import re
    pattern = r'^(0[1-9])(?:[\s\.]?\d{2}){4}$'
    return re.match(pattern, phone) is not None


def validate_email(email):
    """Valide une adresse email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
