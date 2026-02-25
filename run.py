# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app import init_db_command  # Importe la fonction

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialise la base de données avec données exemples"""
    init_db_command()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
