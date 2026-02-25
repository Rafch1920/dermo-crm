# migrate_full.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()

def migrate():
    with app.app_context():
        print("=" * 60)
        print("MIGRATION COMPLETE: pharmacy_campaigns")
        print("=" * 60)
        
        # 1. Sauvegarder les données
        print("\n1. Sauvegarde des données...")
        result = db.session.execute(text("""
            SELECT id, pharmacy_id, campaign_id, enrollment_date, status, 
                   scheduled_date, comment, done_date 
            FROM pharmacy_campaigns
        """))
        old_data = result.fetchall()
        print(f"   {len(old_data)} lignes sauvegardées")
        
        # 2. Supprimer et recréer
        print("\n2. Recréation de la table...")
        db.session.execute(text("DROP TABLE IF EXISTS pharmacy_campaigns"))
        
        db.session.execute(text("""
            CREATE TABLE pharmacy_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pharmacy_id INTEGER NOT NULL,
                campaign_id INTEGER NOT NULL,
                enrollment_date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(20) DEFAULT 'pending',
                scheduled_date TIMESTAMP NULL,
                comment TEXT NULL,
                done_date TIMESTAMP NULL,
                completed_date TIMESTAMP NULL,
                FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                UNIQUE(pharmacy_id, campaign_id)
            )
        """))
        
        # 3. Restaurer
        print("\n3. Restauration des données...")
        for row in old_data:
            db.session.execute(text("""
                INSERT INTO pharmacy_campaigns 
                (id, pharmacy_id, campaign_id, enrollment_date, status, 
                 scheduled_date, comment, done_date, completed_date)
                VALUES 
                (:id, :pharmacy_id, :campaign_id, :enrollment_date, :status,
                 :scheduled_date, :comment, :done_date, :done_date)
            """), {
                'id': row[0],
                'pharmacy_id': row[1],
                'campaign_id': row[2],
                'enrollment_date': row[3],
                'status': row[4] or 'pending',
                'scheduled_date': row[5],
                'comment': row[6],
                'done_date': row[7]
            })
        
        db.session.commit()
        print(f"   {len(old_data)} lignes restaurées")
        
        # 4. Vérification
        print("\n4. Vérification...")
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('pharmacy_campaigns')]
        print(f"   ✓ Colonnes: {', '.join(columns)}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM pharmacy_campaigns"))
        count = result.scalar()
        print(f"   ✓ {count} lignes dans la table")
        
        print("\n" + "=" * 60)
        print("MIGRATION TERMINÉE")
        print("=" * 60)

if __name__ == '__main__':
    migrate()
    input("\nAppuyez sur Entrée pour fermer...")