# fix_db.py
import sqlite3
import os

db_path = 'instance/dermo_crm.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Ajout des colonnes manquantes...")

# Ajouter les colonnes manquantes
try:
    cursor.execute("ALTER TABLE pharmacy_campaigns ADD COLUMN scheduled_date TIMESTAMP")
    print("✓ scheduled_date ajoutée")
except:
    print("✗ scheduled_date existe déjà ou erreur")

try:
    cursor.execute("ALTER TABLE pharmacy_campaigns ADD COLUMN comment TEXT")
    print("✓ comment ajoutée")
except:
    print("✗ comment existe déjà ou erreur")

try:
    cursor.execute("ALTER TABLE pharmacy_campaigns ADD COLUMN done_date TIMESTAMP")
    print("✓ done_date ajoutée")
except:
    print("✗ done_date existe déjà ou erreur")

conn.commit()
conn.close()
print("\nTerminé !")
input("Appuyez sur Entrée...")