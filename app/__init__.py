# -*- coding: utf-8 -*-
"""
Dermo-CRM - Application Factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    """
    Factory pattern pour creer l'application Flask
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Import ici pour eviter le conflit circulaire
    from config import config_dict
    app.config.from_object(config_dict[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    
    # Configuration LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour acceder a cette page.'
    login_manager.login_message_category = 'warning'
    
    # Enregistrer les blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.pharmacies import bp as pharmacies_bp
    app.register_blueprint(pharmacies_bp, url_prefix='/pharmacies')
    
    from app.routes.visits import bp as visits_bp
    app.register_blueprint(visits_bp, url_prefix='/visits')
    
    from app.routes.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from app.routes.campaigns import bp as campaigns_bp
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    
    from app.routes.referents import bp as referents_bp
    app.register_blueprint(referents_bp, url_prefix='/referents')
    
    from app.routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Creer les tables et donnees initiales
    with app.app_context():
        db.create_all()
        _create_initial_data()
    
    return app


def _create_initial_data():
    """Creer les donnees initiales si elles n'existent pas"""
    from app.models import User, Referent, Product, Campaign
    from werkzeug.security import generate_password_hash
    
    # Creer l'admin s'il n'existe pas
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@dermo-crm.local',
            full_name='Administrateur',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("OK - Utilisateur admin cree (admin / admin123)")
    
    # Creer des referents exemples
    if not Referent.query.first():
        referents = [
            Referent(name='Marie Dupont', email='marie.dupont@email.com', 
                    phone='06 12 34 56 78', zone='Nord', color='#e74c3c'),
            Referent(name='Jean Martin', email='jean.martin@email.com', 
                    phone='06 23 45 67 89', zone='Sud', color='#3498db'),
            Referent(name='Sophie Bernard', email='sophie.bernard@email.com', 
                    phone='06 34 56 78 90', zone='Est', color='#2ecc71')
        ]
        db.session.add_all(referents)
        db.session.commit()
        print("OK - Referents exemples crees")
    
    # Creer des produits exemples
    if not Product.query.first():
        products = [
            Product(name='Creme Hydratante Ultra', brand='Dermophil', 
                   category='Hydratation', 
                   description='Creme hydratante pour peaux sensibles'),
            Product(name='Serum Anti-Age', brand='SkinScience', 
                   category='Anti-Age', 
                   description='Serum concentre au retinol'),
            Product(name='Protection Solaire SPF50', brand='SunCare', 
                   category='Protection', 
                   description='Ecran solaire haute protection')
        ]
        db.session.add_all(products)
        db.session.commit()
        print("OK - Produits exemples crees")
    
    # Creer une campagne exemple
    if not Campaign.query.first():
        from datetime import date
        campaign = Campaign(
            name='Campagne Ete 2024',
            description='Promotion des produits solaires',
            start_date=date(2024, 6, 1),
            end_date=date(2024, 8, 31),
            objectives='Former 100 pharmacies sur la gamme solaire',
            status='active'
        )
        db.session.add(campaign)
        db.session.commit()
        print("OK - Campagne exemple creee")