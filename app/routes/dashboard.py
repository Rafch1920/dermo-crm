# -*- coding: utf-8 -*-
"""
Dermo-CRM - Routes Dashboard
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from calendar import monthrange

from app import db
from app.models import (
    Pharmacy, Visit, Product, Campaign, Referent, 
    Contact, Agent, ActivityLog, VisitProduct, PharmacyCampaign
)

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Page d'accueil / Dashboard"""
    
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Page pour les rendez-vous (pagination)
    appointment_page = request.args.get('appt_page', 1, type=int)
    
    kpis = _get_kpis(current_month, current_year)
    chart_data = _get_chart_data()
    
    recent_activities = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    
    recent_visits = Visit.query.order_by(
        Visit.visit_date.desc()
    ).limit(5).all()
    
    thirty_days_ago = today - timedelta(days=30)
    pharmacies_no_visit = Pharmacy.query.filter(
        Pharmacy.is_active == True
    ).outerjoin(Visit).filter(
        db.or_(
            Visit.id == None,
            Visit.visit_date < thirty_days_ago
        )
    ).limit(5).all()
    
    active_campaigns = Campaign.query.filter(
        Campaign.status == 'active',
        Campaign.start_date <= today,
        Campaign.end_date >= today
    ).all()
    
    # Rendez-vous avec pagination (9 par page)
    appointments_data, total_appointments = _get_upcoming_appointments_paginated(today, appointment_page, per_page=9)
    
    # Calculer le nombre total de pages
    total_pages = (total_appointments + 9 - 1) // 9  # Arrondi superieur
    
    return render_template('dashboard/index.html',
                         kpis=kpis,
                         chart_data=chart_data,
                         recent_activities=recent_activities,
                         recent_visits=recent_visits,
                         pharmacies_no_visit=pharmacies_no_visit,
                         active_campaigns=active_campaigns,
                         appointments=appointments_data,
                         total_appointments=total_appointments,
                         appointment_page=appointment_page,
                         total_pages=total_pages,
                         today=today)


def _get_upcoming_appointments_paginated(today, page=1, per_page=9):
    """Recupere les rendez-vous programmes avec pagination"""
    
    seven_days_later = today + timedelta(days=7)
    
    # Requete pour compter le total
    total = db.session.query(func.count(PharmacyCampaign.id)).select_from(PharmacyCampaign).join(
        Campaign, PharmacyCampaign.campaign_id == Campaign.id
    ).filter(
        PharmacyCampaign.status == 'scheduled',
        PharmacyCampaign.scheduled_date.isnot(None),
        PharmacyCampaign.scheduled_date >= datetime.combine(today, datetime.min.time()),
        PharmacyCampaign.scheduled_date <= datetime.combine(seven_days_later, datetime.max.time()),
        Campaign.status == 'active'
    ).scalar() or 0
    
    # Requete paginee
    upcoming = db.session.query(
        PharmacyCampaign.scheduled_date,
        Pharmacy.name.label('pharmacy_name'),
        Campaign.name.label('campaign_name')
    ).select_from(PharmacyCampaign).join(
        Pharmacy, PharmacyCampaign.pharmacy_id == Pharmacy.id
    ).join(
        Campaign, PharmacyCampaign.campaign_id == Campaign.id
    ).filter(
        PharmacyCampaign.status == 'scheduled',
        PharmacyCampaign.scheduled_date.isnot(None),
        PharmacyCampaign.scheduled_date >= datetime.combine(today, datetime.min.time()),
        PharmacyCampaign.scheduled_date <= datetime.combine(seven_days_later, datetime.max.time()),
        Campaign.status == 'active'
    ).order_by(
        PharmacyCampaign.scheduled_date.asc()
    ).offset((page - 1) * per_page).limit(per_page).all()
    
    appointments_data = []
    for appt in upcoming:
        appt_date = appt.scheduled_date.date() if isinstance(appt.scheduled_date, datetime) else appt.scheduled_date
        days_until = (appt_date - today).days
        
        if days_until >= 7:
            color_class = 'appointment-green'
        elif days_until >= 3:
            color_class = 'appointment-orange'
        else:
            color_class = 'appointment-red'
            
        appointments_data.append({
            'date': appt.scheduled_date,
            'pharmacy_name': appt.pharmacy_name,
            'campaign_name': appt.campaign_name,
            'days_until': days_until,
            'color_class': color_class
        })
    
    return appointments_data, total


def _get_kpis(month, year):
    """Calcule les KPIs du mois"""
    
    visits_this_month = Visit.query.filter(
        extract('month', Visit.visit_date) == month,
        extract('year', Visit.visit_date) == year
    ).count()
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    visits_last_month = Visit.query.filter(
        extract('month', Visit.visit_date) == prev_month,
        extract('year', Visit.visit_date) == prev_year
    ).count()
    
    total_pharmacies = Pharmacy.query.filter_by(is_active=True).count()
    visited_pharmacies = db.session.query(Visit.pharmacy_id).filter(
        extract('month', Visit.visit_date) == month,
        extract('year', Visit.visit_date) == year
    ).distinct().count()
    coverage_rate = (visited_pharmacies / total_pharmacies * 100) if total_pharmacies > 0 else 0
    
    avg_duration = db.session.query(func.avg(Visit.duration)).filter(
        extract('month', Visit.visit_date) == month,
        extract('year', Visit.visit_date) == year
    ).scalar() or 0
    
    avg_quality = db.session.query(func.avg(Visit.quality_score)).filter(
        extract('month', Visit.visit_date) == month,
        extract('year', Visit.visit_date) == year
    ).scalar() or 0
    
    new_pharmacies = Pharmacy.query.filter(
        extract('month', Pharmacy.created_at) == month,
        extract('year', Pharmacy.created_at) == year
    ).count()
    
    return {
        'visits_this_month': visits_this_month,
        'visits_last_month': visits_last_month,
        'visits_evolution': visits_this_month - visits_last_month,
        'total_pharmacies': total_pharmacies,
        'visited_pharmacies': visited_pharmacies,
        'coverage_rate': round(coverage_rate, 1),
        'avg_duration': round(avg_duration, 0),
        'avg_quality': round(avg_quality, 1),
        'new_pharmacies': new_pharmacies
    }


def _get_chart_data():
    """Prepare les donnees pour les graphiques"""
    
    months = []
    visits_data = []
    
    for i in range(5, -1, -1):
        d = date.today() - timedelta(days=i*30)
        month_label = d.strftime('%b %Y')
        months.append(month_label)
        
        count = Visit.query.filter(
            extract('month', Visit.visit_date) == d.month,
            extract('year', Visit.visit_date) == d.year
        ).count()
        visits_data.append(count)
    
    region_data = db.session.query(
        Pharmacy.region,
        func.count(Pharmacy.id)
    ).filter_by(is_active=True).group_by(Pharmacy.region).all()
    
    regions = [r[0] or 'Non defini' for r in region_data]
    region_counts = [r[1] for r in region_data]
    
    top_products = db.session.query(
        Product.name,
        func.count('*')
    ).select_from(
        Product
    ).join(
        VisitProduct, VisitProduct.product_id == Product.id
    ).group_by(
        Product.id, Product.name
    ).order_by(
        func.count('*').desc()
    ).limit(5).all()
    
    return {
        'months': months,
        'visits': visits_data,
        'regions': regions,
        'region_counts': region_counts,
        'top_products': [{'name': p[0], 'count': p[1]} for p in top_products]
    }


@bp.route('/api/stats')
@login_required
def api_stats():
    """API - Statistiques en temps reel"""
    today = date.today()
    
    stats = {
        'total_pharmacies': Pharmacy.query.filter_by(is_active=True).count(),
        'total_visits': Visit.query.count(),
        'visits_today': Visit.query.filter(
            func.date(Visit.visit_date) == today
        ).count(),
        'active_campaigns': Campaign.query.filter_by(status='active').count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_referents': Referent.query.filter_by(is_active=True).count()
    }
    
    return jsonify(stats)