# check_db.py - Placez ce fichier dans le dossier dermo-crm
import sqlite3
import os

# Trouvez votre fichier .db
db_path = None
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.db') or file.endswith('.sqlite'):
            db_path = os.path.join(root, file)
            break
    if db_path:
        break

print(f"Base de données trouvée: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Voir la structure de la table
cursor.execute("PRAGMA table_info(pharmacy_campaigns)")
columns = cursor.fetchall()

print("\nColonnes dans pharmacy_campaigns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Voir quelques données
cursor.execute("SELECT * FROM pharmacy_campaigns LIMIT 3")
rows = cursor.fetchall()
print(f"\nExemple de données ({len(rows)} lignes):")
for row in rows:
    print(row)

conn.close()
input("\nAppuyez sur Entrée pour fermer...")