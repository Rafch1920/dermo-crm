from app import create_app, db
from app.models import PharmacyCampaign

app = create_app()
with app.app_context():
    # Voir si la table existe
    count = PharmacyCampaign.query.count()
    print(f"Nombre de PharmacyCampaign: {count}")
    
    # Voir les scheduled
    scheduled = PharmacyCampaign.query.filter_by(status='scheduled').all()
    print(f"Nombre de scheduled: {len(scheduled)}")
    for s in scheduled:
        print(f"  - {s.scheduled_date} - Pharmacy {s.pharmacy_id} - Campaign {s.campaign_id}")