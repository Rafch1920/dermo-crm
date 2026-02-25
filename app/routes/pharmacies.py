# -*- coding: utf-8 -*-
"""
Dermo-CRM - Routes Pharmacies
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_
import json

from app import db
from app.models import Pharmacy, Contact, Agent, Referent, Visit, Attachment
from app.utils.geo_utils import geocode_address

bp = Blueprint('pharmacies', __name__)


@bp.route('/')
@login_required
def index():
    """Liste des pharmacies"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    region = request.args.get('region', '')
    referent_id = request.args.get('referent_id', type=int)
    
    query = Pharmacy.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            or_(
                Pharmacy.name.ilike(f'%{search}%'),
                Pharmacy.city.ilike(f'%{search}%'),
                Pharmacy.address.ilike(f'%{search}%')
            )
        )
    
    if region:
        query = query.filter_by(region=region)
    
    if referent_id:
        query = query.filter_by(referent_id=referent_id)
    
    pharmacies = query.order_by(Pharmacy.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Liste des regions pour filtre
    regions = db.session.query(Pharmacy.region).distinct().filter(
        Pharmacy.region != None
    ).order_by(Pharmacy.region).all()
    regions = [r[0] for r in regions]
    
    # Liste des referents
    referents = Referent.query.filter_by(is_active=True).order_by(Referent.name).all()
    
    return render_template('pharmacies/index.html',
                         pharmacies=pharmacies,
                         regions=regions,
                         referents=referents,
                         search=search,
                         region_filter=region,
                         referent_filter=referent_id)


@bp.route('/map')
@login_required
def map_view():
    """Vue carte des pharmacies"""
    referents = Referent.query.filter_by(is_active=True).order_by(Referent.name).all()
    
    # Convert Referent objects to dictionaries for JSON serialization
    referents_data = [
        {
            'id': r.id,
            'name': r.name,
            'email': r.email,
            'phone': r.phone,
            'zone': r.zone,
            'color': r.color
        }
        for r in referents
    ]
    
    # Filtres
    region = request.args.get('region', '')
    referent_id = request.args.get('referent_id', type=int)
    product_id = request.args.get('product_id', type=int)
    
    # Liste des regions
    regions = db.session.query(Pharmacy.region).distinct().filter(
        Pharmacy.region != None
    ).order_by(Pharmacy.region).all()
    regions = [r[0] for r in regions]
    
    return render_template('pharmacies/map.html',
                         referents=referents_data,
                         regions=regions,
                         region_filter=region,
                         referent_filter=referent_id)


@bp.route('/api/pharmacies')
@login_required
def api_pharmacies():
    """API - Liste des pharmacies pour la carte"""
    region = request.args.get('region')
    referent_id = request.args.get('referent_id', type=int)
    product_id = request.args.get('product_id', type=int)
    campaign_id = request.args.get('campaign_id', type=int)
    
    query = Pharmacy.query.filter_by(is_active=True)
    
    if region:
        query = query.filter_by(region=region)
    if referent_id:
        query = query.filter_by(referent_id=referent_id)
    if product_id:
        query = query.join('products').filter_by(product_id=product_id)
    if campaign_id:
        query = query.join('campaigns').filter_by(campaign_id=campaign_id)
    
    pharmacies = query.all()
    
    return jsonify([p.to_dict() for p in pharmacies])


@bp.route('/api/pharmacies/<int:id>')
@login_required
def api_pharmacy_detail(id):
    """API - Details d'une pharmacie"""
    pharmacy = Pharmacy.query.get_or_404(id)
    
    # Contacts
    contacts = Contact.query.filter_by(pharmacy_id=id).all()
    contacts_data = [{
        'id': c.id,
        'name': c.name,
        'role': c.role,
        'phone': c.phone,
        'email': c.email,
        'is_primary': c.is_primary
    } for c in contacts]
    
    # Agents
    agents = Agent.query.filter_by(pharmacy_id=id, is_active=True).all()
    agents_data = [{
        'id': a.id,
        'name': a.name,
        'role': a.role,
        'phone': a.phone,
        'email': a.email
    } for a in agents]
    
    # Dernieres visites
    visits = Visit.query.filter_by(pharmacy_id=id).order_by(
        Visit.visit_date.desc()
    ).limit(5).all()
    visits_data = [v.to_dict() for v in visits]
    
    # Produits
    products = pharmacy.products.all()
    products_data = [{
        'id': p.product.id,
        'name': p.product.name,
        'brand': p.product.brand,
        'is_available': p.is_available
    } for p in products]
    
    # Campagnes
    campaigns = pharmacy.campaigns.all()
    campaigns_data = [{
        'id': c.campaign.id,
        'name': c.campaign.name,
        'status': c.campaign.status
    } for c in campaigns]
    
    data = pharmacy.to_dict()
    data.update({
        'contacts': contacts_data,
        'agents': agents_data,
        'visits': visits_data,
        'products': products_data,
        'campaigns': campaigns_data
    })
    
    return jsonify(data)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Creer une pharmacie avec selection sur carte"""
    if request.method == 'POST':
        # Recuperation des donnees
        name = request.form.get('name', '').strip()
        type_ = request.form.get('type', 'pharmacie')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        region = request.form.get('region', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        referent_id = request.form.get('referent_id', type=int)
        notes = request.form.get('notes', '').strip()
        
        # Coordonnees depuis la carte (prioritaire)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Geocodage seulement si pas de coordonnees manuelles
        if not latitude or not longitude:
            full_address = f"{address}, {postal_code} {city}"
            coords = geocode_address(full_address)
            if coords:
                latitude = coords['lat']
                longitude = coords['lng']
        
        # Creation
        pharmacy = Pharmacy(
            name=name,
            type=type_,
            address=address,
            city=city,
            postal_code=postal_code,
            region=region,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            email=email,
            referent_id=referent_id,
            notes=notes
        )
        
        db.session.add(pharmacy)
        db.session.commit()
        
        # Ajout des contacts
        contact_names = request.form.getlist('contact_name[]')
        contact_roles = request.form.getlist('contact_role[]')
        contact_phones = request.form.getlist('contact_phone[]')
        contact_emails = request.form.getlist('contact_email[]')
        
        for i, name in enumerate(contact_names):
            if name.strip():
                contact = Contact(
                    pharmacy_id=pharmacy.id,
                    name=name.strip(),
                    role=contact_roles[i] if i < len(contact_roles) else '',
                    phone=contact_phones[i] if i < len(contact_phones) else '',
                    email=contact_emails[i] if i < len(contact_emails) else '',
                    is_primary=(i == 0)
                )
                db.session.add(contact)
        
        db.session.commit()
        
        flash(f'Pharmacie "{name}" creee avec succes.', 'success')
        return redirect(url_for('pharmacies.index'))
    
    referents = Referent.query.filter_by(is_active=True).order_by(Referent.name).all()
    return render_template('pharmacies/create.html', referents=referents)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier une pharmacie avec selection sur carte"""
    pharmacy = Pharmacy.query.get_or_404(id)
    
    if request.method == 'POST':
        pharmacy.name = request.form.get('name', '').strip()
        pharmacy.type = request.form.get('type', 'pharmacie')
        pharmacy.address = request.form.get('address', '').strip()
        pharmacy.city = request.form.get('city', '').strip()
        pharmacy.postal_code = request.form.get('postal_code', '').strip()
        pharmacy.region = request.form.get('region', '').strip()
        pharmacy.phone = request.form.get('phone', '').strip()
        pharmacy.email = request.form.get('email', '').strip()
        pharmacy.referent_id = request.form.get('referent_id', type=int)
        pharmacy.notes = request.form.get('notes', '').strip()
        
        # Mise a jour coordonnees depuis la carte si fournies
        lat = request.form.get('latitude', type=float)
        lng = request.form.get('longitude', type=float)
        if lat and lng:
            pharmacy.latitude = lat
            pharmacy.longitude = lng
        
        db.session.commit()
        
        flash('Pharmacie mise a jour.', 'success')
        return redirect(url_for('pharmacies.index'))
    
    referents = Referent.query.filter_by(is_active=True).order_by(Referent.name).all()
    contacts = Contact.query.filter_by(pharmacy_id=id).all()
    
    return render_template('pharmacies/edit.html', 
                         pharmacy=pharmacy, 
                         referents=referents,
                         contacts=contacts)


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Detail d'une pharmacie"""
    pharmacy = Pharmacy.query.get_or_404(id)
    visits = Visit.query.filter_by(pharmacy_id=id).order_by(Visit.visit_date.desc()).all()
    contacts = Contact.query.filter_by(pharmacy_id=id).all()
    agents = Agent.query.filter_by(pharmacy_id=id, is_active=True).all()
    
    return render_template('pharmacies/detail.html',
                         pharmacy=pharmacy,
                         visits=visits,
                         contacts=contacts,
                         agents=agents)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer (archiver) une pharmacie"""
    pharmacy = Pharmacy.query.get_or_404(id)
    pharmacy.is_active = False
    db.session.commit()
    
    flash('Pharmacie archivee.', 'info')
    return redirect(url_for('pharmacies.index'))


# =====================================================
# API CONTACTS
# =====================================================

@bp.route('/api/contacts', methods=['POST'])
@login_required
def api_add_contact():
    """API - Ajouter un contact"""
    data = request.get_json()
    
    contact = Contact(
        pharmacy_id=data.get('pharmacy_id'),
        name=data.get('name'),
        role=data.get('role'),
        phone=data.get('phone'),
        email=data.get('email')
    )
    
    db.session.add(contact)
    db.session.commit()
    
    return jsonify({'success': True, 'id': contact.id})


@bp.route('/api/contacts/<int:id>', methods=['DELETE'])
@login_required
def api_delete_contact(id):
    """API - Supprimer un contact"""
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({'success': True})