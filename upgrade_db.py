# -*- coding: utf-8 -*-
import sqlite3
import os

# Chemin vers ta base de données
db_path = os.path.join('instance', 'dermo_crm.db')

def upgrade_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Vérifier si les colonnes existent déjà
    cursor.execute("PRAGMA table_info(reminders)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Ajouter les nouvelles colonnes si elles n'existent pas
    new_columns = {
        'email_to': 'VARCHAR(255)',
        'email_cc': 'VARCHAR(255)',
        'email_subject': 'VARCHAR(255)',
        'email_body': 'TEXT'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            print(f"Ajout de la colonne {col_name}...")
            cursor.execute(f"ALTER TABLE reminders ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Colonne {col_name} existe déjà")
    
    conn.commit()
    conn.close()
    print("Migration terminée avec succès!")

if __name__ == '__main__':
    upgrade_database()