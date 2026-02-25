# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Referent, Pharmacy

bp = Blueprint('referents', __name__, url_prefix='/referents')


@bp.route('/')
@login_required
def index():
    referents = Referent.query.filter_by(is_active=True).all()
    
    for r in referents:
        r.pharmacy_count = Pharmacy.query.filter_by(
            referent_id=r.id, 
            is_active=True
        ).count()
    
    return render_template('referents/index.html', referents=referents)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            referent = Referent(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                zone=request.form.get('zone'),
                color=request.form.get('color', '#007bff'),
                target_pharmacies=request.form.get('target_pharmacies', 0, type=int),
                is_active=True
            )
            db.session.add(referent)
            db.session.commit()
            flash('Referent cree avec succes', 'success')
            return redirect(url_for('referents.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    return render_template('referents/new.html')


# ALIAS pour compatibilite
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    return new()


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    referent = Referent.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            referent.name = request.form.get('name')
            referent.email = request.form.get('email')
            referent.phone = request.form.get('phone')
            referent.zone = request.form.get('zone')
            referent.color = request.form.get('color', '#007bff')
            referent.target_pharmacies = request.form.get('target_pharmacies', 0, type=int)
            
            db.session.commit()
            flash('Referent modifie avec succes', 'success')
            return redirect(url_for('referents.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    return render_template('referents/edit.html', referent=referent)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete - met is_active a False"""
    try:
        referent = Referent.query.get_or_404(id)
        referent.is_active = False
        db.session.commit()
        flash('Referent supprime avec succes', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('referents.index'))


@bp.route('/<int:id>/restore', methods=['POST'])
@login_required
def restore(id):
    """Restaurer un referent supprime"""
    try:
        referent = Referent.query.get_or_404(id)
        referent.is_active = True
        db.session.commit()
        flash('Referent restaure avec succes', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('referents.inactive'))


@bp.route('/inactive')
@login_required
def inactive():
    """Liste des referents supprimes (inactifs)"""
    referents = Referent.query.filter_by(is_active=False).order_by(
        Referent.name
    ).all()
    
    return render_template('referents/inactive.html', referents=referents)


@bp.route('/<int:id>/destroy', methods=['POST'])
@login_required
def destroy(id):
    """Suppression definitive - ATTENTION: irreversible"""
    try:
        referent = Referent.query.get_or_404(id)
        db.session.delete(referent)
        db.session.commit()
        flash('Referent definitivement supprime', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('referents.inactive'))


@bp.route('/<int:id>')
@login_required
def view(id):
    referent = Referent.query.get_or_404(id)
    pharmacies = Pharmacy.query.filter_by(
        referent_id=id,
        is_active=True
    ).all()
    
    return render_template('referents/view.html', 
                         referent=referent, 
                         pharmacies=pharmacies)