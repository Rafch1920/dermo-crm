# Dermo-CRM

**Mini-CRM pour formateurs en dermo-cosmétique**

Application web locale pour la gestion de pharmacies, visites, campagnes marketing et reporting.

## Stack Technique

- **Backend**: Python 3.11 + Flask 3.x
- **Frontend**: HTML5 + Bootstrap 5.3 + JavaScript
- **Cartographie**: Leaflet.js + OpenStreetMap
- **Base de données**: SQLite 3
- **Graphiques**: Chart.js 4.x
- **PDF**: ReportLab 4.x

## Fonctionnalités

### Modules

1. **Authentification**
   - Login sécurisé avec hash de mot de passe
   - Gestion de session
   - Profil utilisateur

2. **Carte Interactive**
   - Visualisation des pharmacies sur carte
   - Filtres par région, référent, campagne
   - Ajout par clic, adresse ou GPS
   - Popups détaillés

3. **Gestion des Pharmacies**
   - CRUD complet
   - Géocodage automatique
   - Contacts multiples
   - Historique des visites

4. **Gestion des Visites**
   - Enregistrement avec GPS
   - Produits formés
   - Photos et documents
   - Score qualité

5. **Référents**
   - Zones géographiques
   - KPIs de performance
   - Couleurs personnalisées

6. **Produits**
   - Fiches produits
   - Photos
   - Argumentaires

7. **Campagnes**
   - Périodes et objectifs
   - Suivi d'avancement
   - Pharmacies inscrites

8. **Dashboard**
   - KPIs en temps réel
   - Graphiques Chart.js
   - Activités récentes

9. **Rapports PDF**
   - Visites par période
   - Rapports de campagne
   - Analyses par zone

## Installation

### Prérequis

- Python 3.11+
- pip

### Setup

```bash
# 1. Cloner le projet
cd dermo-crm

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer l'application
python run.py
```

L'application est accessible à `http://127.0.0.1:5000`

**Login par défaut**: `admin` / `admin123`

## Structure du Projet

```
dermo-crm/
├── app/
│   ├── __init__.py          # Factory Flask
│   ├── config.py            # Configuration
│   ├── models.py            # Modèles SQLAlchemy
│   ├── routes/              # Blueprints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── pharmacies.py
│   │   ├── visits.py
│   │   ├── products.py
│   │   ├── campaigns.py
│   │   ├── referents.py
│   │   └── reports.py
│   ├── static/              # CSS, JS, uploads
│   ├── templates/           # Jinja2 templates
│   └── utils/               # Helpers
├── instance/                # Base SQLite
├── docs/                    # Documentation
├── requirements.txt
├── run.py                   # Point d'entrée
└── README.md
```

## Commandes CLI

```bash
# Réinitialiser la base de données
flask reset-db

# Créer un admin
flask create-admin

# Shell avec contexte
flask shell
```

## Sécurité

- Mots de passe hashés avec Werkzeug
- Protection CSRF
- Validation des uploads
- Logs d'activité

## Évolutions Prévues

- [ ] PWA (Service Worker, Manifest)
- [ ] Synchronisation offline/online
- [ ] API REST complète
- [ ] Multi-utilisateurs avancé
- [ ] Application mobile

## Licence

Propriétaire - Usage interne uniquement
