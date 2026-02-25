# recreate_table.py - ATTENTION: sauvegardez vos données d'abord !
import sqlite3

db_path = 'instance/dermo_crm.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("1. Sauvegarde des données existantes...")
cursor.execute("SELECT * FROM pharmacy_campaigns")
old_data = cursor.fetchall()
print(f"   {len(old_data)} lignes sauvegardées")

print("2. Suppression de l'ancienne table...")
cursor.execute("DROP TABLE pharmacy_campaigns")

print("3. Création de la nouvelle table...")
cursor.execute("""
    CREATE TABLE pharmacy_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pharmacy_id INTEGER NOT NULL,
        campaign_id INTEGER NOT NULL,
        enrollment_date DATE DEFAULT CURRENT_DATE,
        status VARCHAR(20) DEFAULT 'pending',
        scheduled_date TIMESTAMP NULL,
        comment TEXT NULL,
        done_date TIMESTAMP NULL,
        FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id),
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
    )
""")

print("4. Restauration des données...")
for row in old_data:
    # old_data: (pharmacy_id, campaign_id, enrollment_date, status)
    cursor.execute("""
        INSERT INTO pharmacy_campaigns (pharmacy_id, campaign_id, enrollment_date, status)
        VALUES (?, ?, ?, ?)
    """, (row[0], row[1], row[2], row[3]))

conn.commit()
conn.close()
print("\n✓ Table recréée avec succès !")
input("Appuyez sur Entrée...")