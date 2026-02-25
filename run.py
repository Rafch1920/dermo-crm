# -*- coding: utf-8 -*-
import os
from app import create_app, db

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialise la base de données avec données exemples"""
    from app import _create_initial_data
    
    with app.app_context():
        db.create_all()
        print("✅ Tables créées")
        _create_initial_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
