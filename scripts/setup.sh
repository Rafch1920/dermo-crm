#!/bin/bash
# Dermo-CRM - Script d'installation

echo "=========================================="
echo "Dermo-CRM - Installation"
echo "=========================================="

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 détecté"

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement
echo "🚀 Activation de l'environnement..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p instance
mkdir -p app/static/uploads

echo ""
echo "=========================================="
echo "✅ Installation terminée !"
echo "=========================================="
echo ""
echo "Pour démarrer l'application:"
echo "  source venv/bin/activate"
echo "  python run.py"
echo ""
echo "Accès: http://127.0.0.1:5000"
echo "Login: admin / admin123"
echo "=========================================="
