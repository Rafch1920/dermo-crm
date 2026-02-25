# Dermo-CRM - Démarrage Rapide

## Installation (5 minutes)

### Linux/Mac

```bash
# 1. Extraire l'archive
cd dermo-crm

# 2. Lancer le script d'installation
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Démarrer l'application
source venv/bin/activate
python run.py
```

### Windows

```cmd
:: 1. Extraire l'archive
cd dermo-crm

:: 2. Créer l'environnement virtuel
python -m venv venv

:: 3. Activer et installer
venv\Scripts\activate.bat
pip install -r requirements.txt

:: 4. Démarrer
python run.py
```

## Accès

- **URL**: http://127.0.0.1:5000
- **Login**: `admin`
- **Mot de passe**: `admin123`

## Fonctionnalités Clés

| Module | Description |
|--------|-------------|
| 🗺️ **Carte** | Visualisation géographique, ajout par clic/GPS/adresse |
| 🏥 **Pharmacies** | CRUD complet, contacts, historique |
| 📅 **Visites** | Enregistrement avec GPS, produits, photos |
| 👥 **Référents** | Zones, KPIs, couleurs personnalisées |
| 📦 **Produits** | Fiches, argumentaires, photos |
| 🎯 **Campagnes** | Périodes, objectifs, suivi |
| 📊 **Dashboard** | KPIs, graphiques, activités |
| 📄 **Rapports** | PDF par période/campagne/zone |

## Structure de la Base de Données

```
users          →  Authentification
pharmacies     →  Enseignes (pharma/parapharma)
contacts       →  Contacts par pharmacie
agents         →  Agents par pharmacie
referents      →  Référents commerciaux
products       →  Produits dermo-cosmétiques
campaigns      →  Campagnes marketing
visits         →  Visites réalisées
attachments    →  Photos/documents
activity_logs  →  Logs de sécurité
```

## Commandes Utiles

```bash
# Réinitialiser la base
cd dermo-crm
source venv/bin/activate
flask reset-db

# Créer un nouvel admin
flask create-admin

# Shell Flask
flask shell
```

## Personnalisation

### Changer le port
```python
# run.py
app.run(host='0.0.0.0', port=8080)  # Port 8080
```

### Mode production
```bash
export FLASK_CONFIG=production
python run.py
```

## Support

Documentation complète dans `docs/01_ARCHITECTURE.md`
