# -*- coding: utf-8 -*-
"""
Dermo-CRM - Modeles de donnees SQLAlchemy
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

from app import db


# =====================================================
# UTILISATEURS
# =====================================================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='trainer')
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'


# =====================================================
# REFERENTS
# =====================================================
class Referent(db.Model):
    __tablename__ = 'referents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    zone = db.Column(db.String(100))
    color = db.Column(db.String(7), default='#007bff')
    target_pharmacies = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_pharmacy_count(self):
        return Pharmacy.query.filter_by(referent_id=self.id, is_active=True).count()
    
    def __repr__(self):
        return f'<Referent {self.name}>'


# =====================================================
# PRODUITS
# =====================================================
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    argumentaire = db.Column(db.Text)
    photo_path = db.Column(db.String(255))
    documents = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_documents_list(self):
        if self.documents:
            return json.loads(self.documents)
        return []
    
    def __repr__(self):
        return f'<Product {self.name}>'


# =====================================================
# CAMPAGNES
# =====================================================
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    objectives = db.Column(db.Text)
    target_zones = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_target_zones_list(self):
        if self.target_zones:
            return json.loads(self.target_zones)
        return []
    
    def set_target_zones_list(self, zones):
        self.target_zones = json.dumps(zones)
    
    def get_progress(self):
        total = PharmacyCampaign.query.filter_by(campaign_id=self.id).count()
        if total == 0:
            return 0
        done = PharmacyCampaign.query.filter_by(campaign_id=self.id, status='done').count()
        return int((done / total) * 100)
    
    def is_active_now(self):
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    def __repr__(self):
        return f'<Campaign {self.name}>'


# =====================================================
# PHARMACIES
# =====================================================
class Pharmacy(db.Model):
    __tablename__ = 'pharmacies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(30), default='pharmacie')
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    region = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    referent_id = db.Column(db.Integer, db.ForeignKey('referents.id'))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def referent(self):
        return Referent.query.get(self.referent_id) if self.referent_id else None
    
    def get_primary_contact(self):
        return Contact.query.filter_by(pharmacy_id=self.id, is_primary=True).first() or Contact.query.filter_by(pharmacy_id=self.id).first()
    
    def get_last_visit(self):
        return Visit.query.filter_by(pharmacy_id=self.id, is_completed=True).order_by(Visit.visit_date.desc()).first()
    
    def get_visit_count(self):
        return Visit.query.filter_by(pharmacy_id=self.id, is_completed=True).count()
    
    def get_coordinates(self):
        if self.latitude and self.longitude:
            return {'lat': float(self.latitude), 'lng': float(self.longitude)}
        return None
    
    def to_dict(self):
        last_visit = self.get_last_visit()
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'region': self.region,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'phone': self.phone,
            'email': self.email,
            'referent_id': self.referent_id,
            'referent_name': self.referent.name if self.referent else None,
            'referent_color': self.referent.color if self.referent else '#007bff',
            'is_active': self.is_active,
            'visit_count': self.get_visit_count(),
            'last_visit': last_visit.visit_date.isoformat() if last_visit else None
        }
    
    def __repr__(self):
        return f'<Pharmacy {self.name}>'


# =====================================================
# CONTACTS
# =====================================================
class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def pharmacy(self):
        return Pharmacy.query.get(self.pharmacy_id)
    
    def __repr__(self):
        return f'<Contact {self.name}>'


# =====================================================
# AGENTS
# =====================================================
class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def pharmacy(self):
        return Pharmacy.query.get(self.pharmacy_id)
    
    def __repr__(self):
        return f'<Agent {self.name}>'


# =====================================================
# VISITES
# =====================================================
class Visit(db.Model):
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)
    objective = db.Column(db.Text)
    notes = db.Column(db.Text)
    quality_score = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    is_completed = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def pharmacy(self):
        return Pharmacy.query.get(self.pharmacy_id)
    
    @property
    def user(self):
        return User.query.get(self.user_id)
    
    def get_products_trained(self):
        return Product.query.join(VisitProduct).filter(VisitProduct.visit_id == self.id).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'pharmacy_name': self.pharmacy.name if self.pharmacy else None,
            'user_id': self.user_id,
            'user_name': self.user.full_name or self.user.username if self.user else None,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'duration': self.duration,
            'objective': self.objective,
            'notes': self.notes,
            'quality_score': self.quality_score,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None
        }
    
    def __repr__(self):
        return f'<Visit {self.id} - {self.pharmacy.name if self.pharmacy else "?"}>'


# =====================================================
# TABLES DE LIAISON
# =====================================================

class CampaignProduct(db.Model):
    __tablename__ = 'campaign_products'
    
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)


class VisitProduct(db.Model):
    __tablename__ = 'visit_products'
    
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    trained_agents_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)


class PharmacyProduct(db.Model):
    __tablename__ = 'pharmacy_products'
    
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    is_available = db.Column(db.Boolean, default=True)
    stock_status = db.Column(db.String(20), default='normal')


class PharmacyCampaign(db.Model):
    __tablename__ = 'pharmacy_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='pending')
    scheduled_date = db.Column(db.DateTime, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    done_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    @property
    def pharmacy(self):
        return Pharmacy.query.get(self.pharmacy_id)
    
    @property
    def pharmacy_obj(self):
        return self.pharmacy
    
    @property
    def campaign(self):
        return Campaign.query.get(self.campaign_id)
    
    @property
    def campaign_obj(self):
        return self.campaign
    
    __table_args__ = (
        db.UniqueConstraint('pharmacy_id', 'campaign_id', name='unique_pharmacy_campaign'),
    )
    
    def __repr__(self):
        return f'<PharmacyCampaign {self.pharmacy_id}-{self.campaign_id}: {self.status}>'


# =====================================================
# LOGS DE MODIFICATION DES STATUTS
# =====================================================
class StatusChangeLog(db.Model):
    __tablename__ = 'status_change_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_campaign_id = db.Column(db.Integer, db.ForeignKey('pharmacy_campaigns.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user(self):
        return User.query.get(self.changed_by)
    
    @property
    def pharmacy_campaign(self):
        return PharmacyCampaign.query.get(self.pharmacy_campaign_id)
    
    def __repr__(self):
        return f'<StatusChangeLog {self.old_status} -> {self.new_status}>'


# =====================================================
# REMINDERS / NOTIFICATIONS
# =====================================================
class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_campaign_id = db.Column(db.Integer, db.ForeignKey('pharmacy_campaigns.id'), nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    email_to = db.Column(db.String(255))
    email_cc = db.Column(db.String(255))
    email_subject = db.Column(db.String(255))
    email_body = db.Column(db.Text)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def pharmacy_campaign(self):
        return PharmacyCampaign.query.get(self.pharmacy_campaign_id)
    
    @property
    def user(self):
        return User.query.get(self.created_by)
    
    def __repr__(self):
        return f'<Reminder {self.reminder_type} at {self.scheduled_time}>'


# =====================================================
# PIECES JOINTES
# =====================================================
class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user(self):
        return User.query.get(self.uploaded_by)
    
    def get_url(self):
        from flask import url_for
        return url_for('static', filename=f'uploads/{self.filename}')
    
    def __repr__(self):
        return f'<Attachment {self.filename}>'


# =====================================================
# LOGS D'ACTIVITE
# =====================================================
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(20))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def user(self):
        return User.query.get(self.user_id)
    
    def get_details_dict(self):
        if self.details:
            return json.loads(self.details)
        return {}
    
    def __repr__(self):
        return f'<ActivityLog {self.action}>'


# =====================================================
# CALLBACKS
# =====================================================
@db.event.listens_for(Pharmacy, 'after_insert')
def log_pharmacy_create(mapper, connection, target):
    pass