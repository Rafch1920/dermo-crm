# Architecture Dermo-CRM

## Stack Technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.11 + Flask 3.x |
| Frontend | HTML5 + Bootstrap 5.3 + Vanilla JS |
| Cartographie | Leaflet.js 1.9 + OpenStreetMap |
| Base de données | SQLite 3 |
| Graphiques | Chart.js 4.x |
| PDF | ReportLab 4.x |
| Auth | Flask-Login + Werkzeug (hash) |

## Arborescence Projet

```
dermo-crm/
├── app/
│   ├── __init__.py              # Factory Flask
│   ├── config.py                # Configuration
│   ├── models.py                # Modèles SQLAlchemy
│   ├── routes/                  # Blueprints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── pharmacies.py
│   │   ├── visits.py
│   │   ├── products.py
│   │   ├── campaigns.py
│   │   ├── referents.py
│   │   └── reports.py
│   ├── static/
│   │   ├── css/                 # Styles custom
│   │   ├── js/                  # Scripts JS
│   │   ├── images/              # Assets
│   │   └── uploads/             # Fichiers uploadés
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── pharmacies/
│   │   ├── visits/
│   │   ├── products/
│   │   ├── campaigns/
│   │   ├── referents/
│   │   └── reports/
│   └── utils/                   # Helpers
│       ├── pdf_generator.py
│       ├── geo_utils.py
│       └── validators.py
├── instance/                    # DB + config locale
├── migrations/                  # Alembic (futur)
├── tests/
├── docs/                        # Documentation
├── scripts/                     # Utilitaires
├── requirements.txt
├── run.py                       # Point d'entrée
└── config.py                    # Config globale
```

## Schéma Base de Données

### Tables Principales

```
users
├── id (PK)
├── username
├── password_hash
├── email
├── role
├── created_at
└── is_active

pharmacies
├── id (PK)
├── name
├── type (pharmacie|parapharmacie)
├── address
├── city
├── postal_code
├── region
├── latitude
├── longitude
├── phone
├── email
├── referent_id (FK)
├── is_active
├── created_at
└── updated_at

contacts
├── id (PK)
├── pharmacy_id (FK)
├── name
├── role
├── phone
├── email
├── is_primary
└── created_at

agents
├── id (PK)
├── pharmacy_id (FK)
├── name
├── role
├── phone
├── email
└── created_at

referents
├── id (PK)
├── name
├── email
├── phone
├── zone
├── color (pour carte)
└── is_active

products
├── id (PK)
├── name
├── brand
├── category
├── description
├── argumentaire
├── photo_path
├── documents
└── is_active

campaigns
├── id (PK)
├── name
├── description
├── start_date
├── end_date
├── objectives
├── zones
├── status
└── created_at

campaign_products (many-to-many)
├── campaign_id (FK)
└── product_id (FK)

visits
├── id (PK)
├── pharmacy_id (FK)
├── user_id (FK)
├── visit_date
├── duration
├── objective
├── notes
├── quality_score
├── photos
├── documents
├── latitude (GPS)
├── longitude (GPS)
└── created_at

visit_products (many-to-many)
├── visit_id (FK)
├── product_id (FK)
└── trained_agents_count

pharmacy_products (many-to-many)
├── pharmacy_id (FK)
└── product_id (FK)

pharmacy_campaigns (many-to-many)
├── pharmacy_id (FK)
└── campaign_id (FK)

attachments
├── id (PK)
├── entity_type (visit|product|campaign)
├── entity_id
├── filename
├── original_name
├── file_type
├── file_size
└── uploaded_at

activity_logs
├── id (PK)
├── user_id (FK)
├── action
├── entity_type
├── entity_id
├── details
├── ip_address
└── created_at
```

## Flux de Données

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Flask     │────▶│   SQLite    │
│  (Browser)  │◀────│   Server    │◀────│    DB       │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │            ┌──────┴──────┐
       │            │             │
       ▼            ▼             ▼
┌─────────────┐  ┌────────┐  ┌──────────┐
│  Leaflet.js │  │Chart.js│  │ReportLab │
│    (Map)    │  │(Charts)│  │  (PDF)   │
└─────────────┘  └────────┘  └──────────┘
```

## Sécurité

- Mots de passe hashés avec Werkzeug
- Sessions Flask sécurisées
- CSRF protection (Flask-WTF)
- Validation uploads (type, taille)
- Logs d'activité
- Backups automatiques

## Évolutions Prévues

1. **PWA** : Service worker, manifest, cache
2. **Sync** : Synchronisation offline/online
3. **Multi-user** : Rôles avancés (admin, formateur, viewer)
4. **API REST** : Endpoints JSON pour mobile
