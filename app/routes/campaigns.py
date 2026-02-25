# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from datetime import datetime, date, timedelta
import smtplib
import socket
from app import db, mail
from app.models import (Campaign, Pharmacy, PharmacyCampaign, Product, 
                       CampaignProduct, Referent, StatusChangeLog, Reminder)

bp = Blueprint('campaigns', __name__, url_prefix='/campaigns')


def send_email_with_cc(to, cc, subject, body):
    """Fonction pour envoyer un email avec CC via Gmail"""
    try:
        current_app.logger.info(f"Tentative d'envoi email a {to}")
        
        recipients = []
        if to and '@' in to:
            recipients.append(to)
        if cc and '@' in cc:
            recipients.append(cc)
        
        if not recipients:
            return False, "Pas de destinataire valide"
        
        msg = Message(
            subject=subject,
            recipients=[to] if to else [],
            body=body,
            cc=[cc] if cc else []
        )
        
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(15)
        
        try:
            mail.send(msg)
            current_app.logger.info(f"Email envoye avec succes a {to}")
            return True, None
        finally:
            socket.setdefaulttimeout(old_timeout)
        
    except smtplib.SMTPAuthenticationError as e:
        current_app.logger.error(f"Erreur authentification Gmail: {str(e)}")
        return False, "Erreur d'authentification Gmail - verifiez le mot de passe d'application"
    except smtplib.SMTPException as e:
        current_app.logger.error(f"Erreur SMTP: {str(e)}")
        return False, f"Erreur SMTP: {str(e)}"
    except Exception as e:
        current_app.logger.error(f"Erreur envoi email: {str(e)}")
        return False, str(e)


@bp.route('/')
@login_required
def index():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    
    campaigns_data = []
    for campaign in campaigns:
        links = PharmacyCampaign.query.filter_by(campaign_id=campaign.id).all()
        total = len(links)
        completed = sum(1 for p in links if p.status == 'done')
        progress = int((completed / total * 100)) if total > 0 else 0
        
        campaigns_data.append({
            'campaign': campaign,
            'total': total,
            'completed': completed,
            'progress': progress
        })
    
    return render_template('campaigns/index.html', campaigns_data=campaigns_data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            pharmacy_ids = request.form.getlist('pharmacy_ids[]')
            product_ids = request.form.getlist('product_ids[]')
            
            campaign = Campaign(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                created_by=current_user.id,
                status='active'
            )
            db.session.add(campaign)
            db.session.flush()
            
            for pid in pharmacy_ids:
                if pid:
                    pc = PharmacyCampaign(
                        pharmacy_id=int(pid),
                        campaign_id=campaign.id,
                        status='pending'
                    )
                    db.session.add(pc)
            
            for pid in product_ids:
                if pid:
                    cp = CampaignProduct(
                        campaign_id=campaign.id,
                        product_id=int(pid)
                    )
                    db.session.add(cp)
            
            db.session.commit()
            flash('Campagne creee avec succes', 'success')
            return redirect(url_for('campaigns.view', id=campaign.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
            return redirect(url_for('campaigns.new'))
    
    referents = Referent.query.filter_by(is_active=True).all()
    zones = db.session.query(Pharmacy.region).distinct().all()
    regions = [z[0] for z in zones if z[0]]
    types = ['pharmacie', 'parapharmacie', 'grande_surface']
    pharmacies = Pharmacy.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('campaigns/new.html', 
                         pharmacies=pharmacies,
                         products=products,
                         referents=referents,
                         regions=regions,
                         types=types)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    campaign = Campaign.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            campaign.name = request.form.get('name')
            campaign.description = request.form.get('description')
            campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            campaign.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            campaign.status = request.form.get('status', 'active')
            
            # Mise a jour des produits
            current_products = CampaignProduct.query.filter_by(campaign_id=id).all()
            for cp in current_products:
                db.session.delete(cp)
            
            product_ids = request.form.getlist('product_ids[]')
            for pid in product_ids:
                if pid:
                    cp = CampaignProduct(campaign_id=id, product_id=int(pid))
                    db.session.add(cp)
            
            # AJOUT: Ajouter de nouvelles pharmacies
            new_pharmacy_ids = request.form.getlist('new_pharmacy_ids[]')
            for pid in new_pharmacy_ids:
                if pid:
                    existing = PharmacyCampaign.query.filter_by(
                        campaign_id=id, 
                        pharmacy_id=int(pid)
                    ).first()
                    if not existing:
                        pc = PharmacyCampaign(
                            pharmacy_id=int(pid),
                            campaign_id=id,
                            status='pending'
                        )
                        db.session.add(pc)
            
            db.session.commit()
            flash('Campagne modifiee avec succes', 'success')
            return redirect(url_for('campaigns.view', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    products = Product.query.filter_by(is_active=True).all()
    selected_products = [cp.product_id for cp in CampaignProduct.query.filter_by(campaign_id=id).all()]
    
    # AJOUT: Pharmacies deja dans la campagne
    existing_pharmacies = PharmacyCampaign.query.filter_by(campaign_id=id).all()
    existing_pharmacy_ids = [p.pharmacy_id for p in existing_pharmacies]
    
    # AJOUT: Pharmacies disponibles (pas encore dans la campagne)
    available_pharmacies = Pharmacy.query.filter(
        Pharmacy.is_active == True,
        ~Pharmacy.id.in_(existing_pharmacy_ids) if existing_pharmacy_ids else True
    ).order_by(Pharmacy.name).all()
    
    return render_template('campaigns/edit.html',
                         campaign=campaign,
                         products=products,
                         selected_products=selected_products,
                         existing_pharmacies=existing_pharmacies,
                         available_pharmacies=available_pharmacies)


@bp.route('/<int:id>')
@login_required
def view(id):
    campaign = Campaign.query.get_or_404(id)
    pharmacy_links = PharmacyCampaign.query.filter_by(campaign_id=id).all()
    
    for link in pharmacy_links:
        link.status_logs = StatusChangeLog.query.filter_by(
            pharmacy_campaign_id=link.id
        ).order_by(StatusChangeLog.created_at.desc()).all()
        
        link.reminders = Reminder.query.filter_by(
            pharmacy_campaign_id=link.id
        ).order_by(Reminder.scheduled_time.desc()).all()
    
    stats = {
        'total': len(pharmacy_links),
        'done': sum(1 for p in pharmacy_links if p.status == 'done'),
        'scheduled': sum(1 for p in pharmacy_links if p.status == 'scheduled'),
        'pending': sum(1 for p in pharmacy_links if p.status == 'pending'),
        'problem': sum(1 for p in pharmacy_links if p.status == 'problem'),
        'cancelled': sum(1 for p in pharmacy_links if p.status == 'cancelled')
    }
    
    # AJOUT: Pharmacies disponibles pour ajout rapide
    existing_ids = [p.pharmacy_id for p in pharmacy_links]
    available_pharmacies = Pharmacy.query.filter(
        Pharmacy.is_active == True,
        ~Pharmacy.id.in_(existing_ids) if existing_ids else True
    ).order_by(Pharmacy.name).all()
    
    return render_template('campaigns/view.html', 
                         campaign=campaign,
                         pharmacy_links=pharmacy_links,
                         stats=stats,
                         available_pharmacies=available_pharmacies)


# NOUVELLE ROUTE: Ajouter une pharmacie a la campagne
@bp.route('/<int:id>/add_pharmacy', methods=['POST'])
@login_required
def add_pharmacy(id):
    """Ajouter une pharmacie a la campagne"""
    try:
        data = request.get_json()
        pharmacy_id = data.get('pharmacy_id')
        
        if not pharmacy_id:
            return jsonify({'error': 'ID pharmacie manquant'}), 400
        
        # Verifier si deja presente
        existing = PharmacyCampaign.query.filter_by(
            campaign_id=id,
            pharmacy_id=pharmacy_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Cette pharmacie est deja dans la campagne'}), 400
        
        # Ajouter la pharmacie
        pc = PharmacyCampaign(
            pharmacy_id=pharmacy_id,
            campaign_id=id,
            status='pending'
        )
        db.session.add(pc)
        db.session.commit()
        
        pharmacy = Pharmacy.query.get(pharmacy_id)
        
        return jsonify({
            'success': True,
            'link_id': pc.id,
            'pharmacy_name': pharmacy.name if pharmacy else 'Inconnue',
            'message': 'Pharmacie ajoutee avec succes'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# NOUVELLE ROUTE: Liste des pharmacies disponibles
@bp.route('/<int:id>/available_pharmacies')
@login_required
def available_pharmacies(id):
    """API - Liste des pharmacies disponibles pour ajout"""
    try:
        # Pharmacies deja dans la campagne
        existing_ids = db.session.query(PharmacyCampaign.pharmacy_id).filter_by(campaign_id=id).all()
        existing_ids = [p[0] for p in existing_ids]
        
        # Pharmacies disponibles
        query = Pharmacy.query.filter_by(is_active=True)
        if existing_ids:
            query = query.filter(~Pharmacy.id.in_(existing_ids))
        
        pharmacies = query.order_by(Pharmacy.name).all()
        
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'city': p.city,
            'address': p.address
        } for p in pharmacies])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/update_status', methods=['POST'])
@login_required
def update_status(id):
    try:
        data = request.get_json()
        link_id = data.get('link_id')
        pharmacy_id = data.get('pharmacy_id')
        status = data.get('status')
        comment = data.get('comment')
        scheduled_date = data.get('scheduled_date')
        completed_date = data.get('completed_date')
        
        if not link_id and pharmacy_id:
            link = PharmacyCampaign.query.filter_by(
                campaign_id=id, 
                pharmacy_id=pharmacy_id
            ).first()
            if not link:
                link = PharmacyCampaign(
                    campaign_id=id,
                    pharmacy_id=pharmacy_id,
                    status='pending'
                )
                db.session.add(link)
                db.session.flush()
            link_id = link.id
        else:
            link = PharmacyCampaign.query.get_or_404(link_id)
        
        if link.campaign_id != id:
            return jsonify({'error': 'Non autorise'}), 403
        
        old_status = link.status
        
        if old_status in ['cancelled', 'problem'] and status in ['done', 'scheduled', 'pending']:
            link.comment = None
        
        link.status = status
        
        if status == 'scheduled' and scheduled_date:
            link.scheduled_date = datetime.fromisoformat(scheduled_date)
            link.done_date = None
            link.completed_date = None
        elif status == 'done':
            if completed_date:
                link.done_date = datetime.fromisoformat(completed_date)
            else:
                link.done_date = datetime.now()
            link.scheduled_date = None
            link.completed_date = link.done_date
        elif status in ['problem', 'cancelled']:
            link.comment = comment
            if completed_date:
                link.completed_date = datetime.fromisoformat(completed_date)
            else:
                link.completed_date = datetime.now()
            link.scheduled_date = None
        elif status == 'pending':
            link.scheduled_date = None
            link.done_date = None
            link.comment = None
            link.completed_date = None
        
        db.session.flush()
        
        status_log = StatusChangeLog(
            pharmacy_campaign_id=link.id,
            old_status=old_status,
            new_status=status,
            reason=comment if status in ['problem', 'cancelled'] else None,
            changed_by=current_user.id
        )
        db.session.add(status_log)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'link_id': link.id,
            'old_status': old_status,
            'new_status': status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur update_status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/create_reminder', methods=['POST'])
@login_required
def create_reminder(id):
    try:
        data = request.get_json()
        link_id = data.get('link_id')
        reminder_type = data.get('reminder_type')
        scheduled_time_str = data.get('scheduled_time')
        send_confirmation = data.get('send_confirmation', False)
        email_to = data.get('email_to')
        email_cc = data.get('email_cc')
        email_subject = data.get('email_subject')
        email_body = data.get('email_body')
        
        current_app.logger.info(f"Creation reminder pour link_id={link_id}, envoi={send_confirmation}, vers={email_to}")
        
        link = PharmacyCampaign.query.get_or_404(link_id)
        if link.campaign_id != id:
            return jsonify({'error': 'Non autorise'}), 403
        
        visit_date = link.scheduled_date or datetime.now()
        if scheduled_time_str:
            hour, minute = map(int, scheduled_time_str.split(':'))
            reminder_time = visit_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        else:
            reminder_time = visit_date.replace(hour=9, minute=30, second=0, microsecond=0)
        
        pharmacy = link.pharmacy
        campaign = link.campaign
        
        if not email_subject:
            email_subject = f"Confirmation de visite - {campaign.name}"
        
        if not email_body:
            email_body = f"""Bonjour,

Ceci est un email automatique de confirmation.

Votre pharmacie ({pharmacy.name}) est programmee pour une visite dans le cadre de la campagne "{campaign.name}".

Heure d'arrivee estimee : {reminder_time.strftime('%H:%M')} (plus ou moins 15 min selon la circulation routiere)

Cordialement,
L'equipe Dermo-CRM
"""
        
        reminder = Reminder(
            pharmacy_campaign_id=link.id,
            reminder_type=reminder_type,
            scheduled_time=reminder_time,
            email_to=email_to or pharmacy.email,
            email_cc=email_cc,
            email_subject=email_subject,
            email_body=email_body,
            created_by=current_user.id
        )
        db.session.add(reminder)
        db.session.commit()
        
        email_sent = False
        email_error = None
        
        if send_confirmation and email_to:
            success, error = send_email_with_cc(
                email_to,
                email_cc,
                email_subject,
                email_body
            )
            if success:
                reminder.is_sent = True
                reminder.sent_at = datetime.now()
                db.session.commit()
                email_sent = True
                current_app.logger.info("Email envoye avec succes")
            else:
                email_error = error
                current_app.logger.error(f"Echec envoi email: {error}")
        
        message = 'Rappel cree avec succes'
        if email_sent:
            message += ' et email envoye'
        elif email_error:
            message += f' (email non envoye: {email_error})'
        
        return jsonify({
            'success': True,
            'reminder_id': reminder.id,
            'scheduled_time': reminder_time.isoformat(),
            'email_sent': email_sent,
            'email_error': email_error,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur create_reminder: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/test_email')
@login_required
def test_email(id):
    try:
        success, error = send_email_with_cc(
            'nourcherifargania@gmail.com',
            '',
            'Test Dermo-CRM Gmail',
            'Ceci est un email de test depuis Dermo-CRM avec Gmail.'
        )
        if success:
            return 'Email envoye avec succes!'
        else:
            return f'Erreur: {error}'
    except Exception as e:
        return f'Exception: {str(e)}'


@bp.route('/<int:id>/get_status_logs/<int:link_id>')
@login_required
def get_status_logs(id, link_id):
    try:
        link = PharmacyCampaign.query.get_or_404(link_id)
        if link.campaign_id != id:
            return jsonify({'error': 'Non autorise'}), 403
        
        logs = StatusChangeLog.query.filter_by(
            pharmacy_campaign_id=link_id
        ).order_by(StatusChangeLog.created_at.desc()).all()
        
        return jsonify([{
            'id': log.id,
            'old_status': log.old_status,
            'new_status': log.new_status,
            'reason': log.reason,
            'changed_by': log.user.full_name if log.user else 'Systeme',
            'created_at': log.created_at.isoformat()
        } for log in logs])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/remove_pharmacy', methods=['POST'])
@login_required
def remove_pharmacy(id):
    try:
        data = request.get_json()
        link_id = data.get('link_id')
        
        link = PharmacyCampaign.query.get_or_404(link_id)
        if link.campaign_id != id:
            return jsonify({'error': 'Non autorise'}), 403
        
        # Supprimer les reminders et logs associes
        Reminder.query.filter_by(pharmacy_campaign_id=link_id).delete()
        StatusChangeLog.query.filter_by(pharmacy_campaign_id=link_id).delete()
        
        db.session.delete(link)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pharmacie retiree de la campagne'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/calendar_data')
@login_required
def calendar_data(id):
    try:
        links = PharmacyCampaign.query.filter_by(campaign_id=id).all()
        
        events = []
        for link in links:
            event_date = None
            
            if link.scheduled_date:
                event_date = link.scheduled_date
            elif link.done_date:
                event_date = link.done_date
            elif link.completed_date:
                event_date = link.completed_date
            
            if event_date:
                events.append({
                    'id': link.id,
                    'title': link.pharmacy_obj.name + ' (' + link.status + ')',
                    'start': event_date.strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': link.status,
                    'pharmacy_id': link.pharmacy_id,
                    'comment': link.comment or ''
                })
        
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/pharmacies_by_date')
@login_required
def pharmacies_by_date(id):
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Date manquante'}), 400
            
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        links = PharmacyCampaign.query.filter_by(campaign_id=id).all()
        result = []
        
        for link in links:
            include = False
            time_str = None
            
            if link.scheduled_date and link.scheduled_date.date() == target_date:
                include = True
                time_str = link.scheduled_date.strftime('%H:%M')
            elif link.done_date and link.done_date.date() == target_date:
                include = True
                time_str = link.done_date.strftime('%H:%M')
            elif link.completed_date and link.completed_date.date() == target_date:
                include = True
                time_str = link.completed_date.strftime('%H:%M')
            
            if include:
                result.append({
                    'id': link.id,
                    'pharmacy_id': link.pharmacy_id,
                    'pharmacy_name': link.pharmacy_obj.name,
                    'time': time_str,
                    'status': link.status,
                    'comment': link.comment or '',
                    'address': link.pharmacy_obj.address or '',
                    'city': link.pharmacy_obj.city or ''
                })
        
        result.sort(key=lambda x: x['time'] or '00:00')
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/map_data')
@login_required
def map_data(id):
    try:
        links = PharmacyCampaign.query.filter_by(campaign_id=id).all()
        
        markers = []
        for link in links:
            if link.pharmacy_obj.latitude and link.pharmacy_obj.longitude:
                markers.append({
                    'id': link.pharmacy_id,
                    'name': link.pharmacy_obj.name,
                    'lat': float(link.pharmacy_obj.latitude),
                    'lng': float(link.pharmacy_obj.longitude),
                    'status': link.status,
                    'address': link.pharmacy_obj.address or '',
                    'city': link.pharmacy_obj.city or ''
                })
        
        return jsonify(markers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500