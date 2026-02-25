# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models import User, Referent, Product, Campaign, Pharmacy

# CRUCIAL : Définir app au niveau global pour Gunicorn
app = create_app(os.getenv('FLASK_CONFIG', 'production'))

@app.cli.command("init-db")
def init_db():
    """Initialise la base de données"""
    db.create_all()
    print("✅ Base de données créée!")

if __name__ == '__main__':
    app.run()