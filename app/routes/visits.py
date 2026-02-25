"""
Dermo-CRM - Routes Visites
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os

from app import db
from app.models import Visit, Pharmacy, Product, VisitProduct, Attachment
from app.utils.validators import allowed_file

bp = Blueprint('visits', __name__)


@bp.route('/')
@login_required
def index():
    """Liste des visites"""
    page = request.args.get('page', 1, type=int)
    pharmacy_id = request.args.get('pharmacy_id', type=int)
    
    query = Visit.query
    
    if pharmacy_id:
        query = query.filter_by(pharmacy_id=pharmacy_id)
    
    visits = query.order_by(Visit.visit_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    pharmacies = Pharmacy.query.filter_by(is_active=True).order_by(Pharmacy.name).all()
    
    return render_template('visits/index.html',
                         visits=visits,
                         pharmacies=pharmacies,
                         pharmacy_filter=pharmacy_id)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Créer une visite"""
    if request.method == 'POST':
        pharmacy_id = request.form.get('pharmacy_id', type=int)
        visit_date_str = request.form.get('visit_date')
        duration = request.form.get('duration', type=int)
        objective = request.form.get('objective', '').strip()
        notes = request.form.get('notes', '').strip()
        quality_score = request.form.get('quality_score', type=int)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        
        # Parsing date
        try:
            visit_date = datetime.fromisoformat(visit_date_str.replace('T', ' '))
        except:
            visit_date = datetime.now()
        
        # Création visite
        visit = Visit(
            pharmacy_id=pharmacy_id,
            user_id=current_user.id,
            visit_date=visit_date,
            duration=duration,
            objective=objective,
            notes=notes,
            quality_score=quality_score,
            latitude=latitude,
            longitude=longitude,
            is_completed=True
        )
        
        db.session.add(visit)
        db.session.flush()  # Pour obtenir l'ID
        
        # Produits formés
        product_ids = request.form.getlist('product_id[]')
        trained_counts = request.form.getlist('trained_count[]')
        
        for i, pid in enumerate(product_ids):
            if pid:
                vp = VisitProduct(
                    visit_id=visit.id,
                    product_id=int(pid),
                    trained_agents_count=int(trained_counts[i]) if i < len(trained_counts) else 0
                )
                db.session.add(vp)
        
        # Upload de fichiers
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Ajouter timestamp pour unicité
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{int(datetime.now().timestamp())}{ext}"
                    
                    filepath = os.path.join(
                        current_app.config['UPLOAD_FOLDER'], 
                        filename
                    )
                    file.save(filepath)
                    
                    attachment = Attachment(
                        entity_type='visit',
                        entity_id=visit.id,
                        filename=filename,
                        original_name=file.filename,
                        file_type=file.content_type,
                        file_size=os.path.getsize(filepath),
                        uploaded_by=current_user.id
                    )
                    db.session.add(attachment)
        
        db.session.commit()
        
        flash('Visite enregistrée avec succès.', 'success')
        return redirect(url_for('visits.index'))
    
    pharmacy_id = request.args.get('pharmacy_id', type=int)
    pharmacy = None
    if pharmacy_id:
        pharmacy = Pharmacy.query.get(pharmacy_id)
    
    pharmacies = Pharmacy.query.filter_by(is_active=True).order_by(Pharmacy.name).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    return render_template('visits/create.html',
                         pharmacies=pharmacies,
                         products=products,
                         pharmacy=pharmacy,
                         now=datetime.now())


@bp.route('/<int:id>')
@login_required
def detail(id):
    """Détail d'une visite"""
    visit = Visit.query.get_or_404(id)
    attachments = Attachment.query.filter_by(
        entity_type='visit',
        entity_id=id
    ).all()
    
    return render_template('visits/detail.html',
                         visit=visit,
                         attachments=attachments)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Modifier une visite"""
    visit = Visit.query.get_or_404(id)
    
    if request.method == 'POST':
        visit_date_str = request.form.get('visit_date')
        visit.duration = request.form.get('duration', type=int)
        visit.objective = request.form.get('objective', '').strip()
        visit.notes = request.form.get('notes', '').strip()
        visit.quality_score = request.form.get('quality_score', type=int)
        
        try:
            visit.visit_date = datetime.fromisoformat(visit_date_str.replace('T', ' '))
        except:
            pass
        
        # Mise à jour produits
        VisitProduct.query.filter_by(visit_id=id).delete()
        
        product_ids = request.form.getlist('product_id[]')
        trained_counts = request.form.getlist('trained_count[]')
        
        for i, pid in enumerate(product_ids):
            if pid:
                vp = VisitProduct(
                    visit_id=visit.id,
                    product_id=int(pid),
                    trained_agents_count=int(trained_counts[i]) if i < len(trained_counts) else 0
                )
                db.session.add(vp)
        
        db.session.commit()
        
        flash('Visite mise à jour.', 'success')
        return redirect(url_for('visits.detail', id=id))
    
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    selected_products = {vp.product_id: vp.trained_agents_count for vp in visit.products}
    
    return render_template('visits/edit.html',
                         visit=visit,
                         products=products,
                         selected_products=selected_products)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Supprimer une visite"""
    visit = Visit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    
    flash('Visite supprimée.', 'info')
    return redirect(url_for('visits.index'))


# =====================================================
# API
# =====================================================

@bp.route('/api/visits')
@login_required
def api_visits():
    """API - Liste des visites"""
    pharmacy_id = request.args.get('pharmacy_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Visit.query
    
    if pharmacy_id:
        query = query.filter_by(pharmacy_id=pharmacy_id)
    if start_date:
        query = query.filter(Visit.visit_date >= start_date)
    if end_date:
        query = query.filter(Visit.visit_date <= end_date)
    
    visits = query.order_by(Visit.visit_date.desc()).limit(100).all()
    
    return jsonify([v.to_dict() for v in visits])


@bp.route('/api/visits/<int:id>')
@login_required
def api_visit_detail(id):
    """API - Détail d'une visite"""
    visit = Visit.query.get_or_404(id)
    data = visit.to_dict()
    
    # Produits
    products = []
    for vp in visit.products:
        products.append({
            'id': vp.product.id,
            'name': vp.product.name,
            'trained_agents_count': vp.trained_agents_count
        })
    data['products'] = products
    
    # Pièces jointes
    attachments = Attachment.query.filter_by(
        entity_type='visit',
        entity_id=id
    ).all()
    data['attachments'] = [{
        'id': a.id,
        'filename': a.filename,
        'original_name': a.original_name,
        'url': a.get_url()
    } for a in attachments]
    
    return jsonify(data)


# Import pour les uploads
from flask import current_app
