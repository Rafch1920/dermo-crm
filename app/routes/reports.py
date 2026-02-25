"""
Dermo-CRM - Routes Rapports PDF
"""
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from datetime import datetime, date
from io import BytesIO

from app import db
from app.models import Visit, Pharmacy, Product, Campaign, Referent
from app.utils.pdf_generator import generate_visit_report, generate_campaign_report, generate_zone_report

bp = Blueprint('reports', __name__)


@bp.route('/')
@login_required
def index():
    """Page des rapports"""
    # Filtres disponibles
    referents = Referent.query.filter_by(is_active=True).order_by(Referent.name).all()
    campaigns = Campaign.query.order_by(Campaign.start_date.desc()).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
    
    # Régions
    regions = db.session.query(Pharmacy.region).distinct().filter(
        Pharmacy.region != None
    ).order_by(Pharmacy.region).all()
    regions = [r[0] for r in regions if r[0]]
    
    return render_template('reports/index.html',
                         referents=referents,
                         campaigns=campaigns,
                         products=products,
                         regions=regions)


@bp.route('/generate', methods=['POST'])
@login_required
def generate():
    """Générer un rapport PDF"""
    report_type = request.form.get('report_type')
    
    if report_type == 'visits':
        return _generate_visits_report()
    elif report_type == 'campaign':
        return _generate_campaign_report()
    elif report_type == 'zone':
        return _generate_zone_report()
    else:
        flash('Type de rapport inconnu.', 'danger')
        return redirect(url_for('reports.index'))


def _generate_visits_report():
    """Génère un rapport de visites"""
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    referent_id = request.form.get('referent_id', type=int)
    
    # Conversion dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    except:
        start = end = None
    
    # Requête
    query = Visit.query
    if start:
        query = query.filter(Visit.visit_date >= start)
    if end:
        query = query.filter(Visit.visit_date <= end)
    if referent_id:
        query = query.join(Pharmacy).filter(Pharmacy.referent_id == referent_id)
    
    visits = query.order_by(Visit.visit_date.desc()).all()
    
    # Génération PDF
    pdf_buffer = generate_visit_report(visits, start, end)
    
    filename = f"rapport_visites_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def _generate_campaign_report():
    """Génère un rapport de campagne"""
    campaign_id = request.form.get('campaign_id', type=int)
    
    if not campaign_id:
        flash('Veuillez sélectionner une campagne.', 'warning')
        return redirect(url_for('reports.index'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Génération PDF
    pdf_buffer = generate_campaign_report(campaign)
    
    filename = f"rapport_campagne_{campaign.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def _generate_zone_report():
    """Génère un rapport par zone"""
    region = request.form.get('region')
    
    if not region:
        flash('Veuillez sélectionner une région.', 'warning')
        return redirect(url_for('reports.index'))
    
    pharmacies = Pharmacy.query.filter_by(region=region, is_active=True).all()
    
    # Génération PDF
    pdf_buffer = generate_zone_report(region, pharmacies)
    
    filename = f"rapport_zone_{region.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/preview')
@login_required
def preview():
    """Aperçu d'un rapport (HTML)"""
    report_type = request.args.get('report_type')
    
    if report_type == 'visits':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Visit.query
        if start_date:
            query = query.filter(Visit.visit_date >= start_date)
        if end_date:
            query = query.filter(Visit.visit_date <= end_date)
        
        visits = query.order_by(Visit.visit_date.desc()).limit(50).all()
        
        return render_template('reports/preview_visits.html', visits=visits)
    
    return redirect(url_for('reports.index'))
