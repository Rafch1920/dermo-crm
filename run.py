# -*- coding: utf-8 -*-
import os
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG', 'production'))

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Base de données créée!")

if __name__ == '__main__':
    # Utilise le port de Render ou 5000 par défaut
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
