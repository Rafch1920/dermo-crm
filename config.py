# -*- coding: utf-8 -*-
"""
Configuration Dermo-CRM
"""
import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

# Creer le dossier instance s'il n'existe pas
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    """Configuration de base"""
    
    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de donnees
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(INSTANCE_DIR, 'dermo_crm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Application
    APP_NAME = 'Dermo-CRM'
    APP_VERSION = '1.0.0'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Carte
    MAP_DEFAULT_LAT = 46.603354
    MAP_DEFAULT_LNG = 1.888334
    MAP_DEFAULT_ZOOM = 6
    
    # Configuration Email - Utilise les variables d'environnement ou les valeurs par defaut
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'nourcherifargania@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'ffhdrbaeydtbrvbh')
    MAIL_DEFAULT_SENDER = ('Dermo-CRM', MAIL_USERNAME)
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() in ['true', '1', 'yes']
    MAIL_ASCII_ATTACHMENTS = False


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Dictionnaire des configurations
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
