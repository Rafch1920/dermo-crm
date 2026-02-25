# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Product

bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Ne montrer que les produits actifs
    query = Product.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.order_by(Product.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = db.session.query(Product.category).distinct().filter(
        Product.category.isnot(None)
    ).all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('products/index.html', 
                         products=products, 
                         categories=categories,
                         search=search,
                         category=category)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form.get('name'),
                brand=request.form.get('brand'),
                category=request.form.get('category'),
                description=request.form.get('description'),
                argumentaire=request.form.get('argumentaire'),
                is_active=True
            )
            db.session.add(product)
            db.session.commit()
            flash('Produit cree avec succes', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    return render_template('products/new.html')


# ALIAS pour compatibilite
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    return new()


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name')
            product.brand = request.form.get('brand')
            product.category = request.form.get('category')
            product.description = request.form.get('description')
            product.argumentaire = request.form.get('argumentaire')
            
            db.session.commit()
            flash('Produit modifie avec succes', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur: {str(e)}', 'danger')
    
    return render_template('products/edit.html', product=product)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete - met is_active a False"""
    try:
        product = Product.query.get_or_404(id)
        product.is_active = False
        db.session.commit()
        flash('Produit supprime avec succes', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('products.index'))


@bp.route('/<int:id>/restore', methods=['POST'])
@login_required
def restore(id):
    """Restaurer un produit supprime"""
    try:
        product = Product.query.get_or_404(id)
        product.is_active = True
        db.session.commit()
        flash('Produit restaure avec succes', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('products.inactive'))


@bp.route('/inactive')
@login_required
def inactive():
    """Liste des produits supprimes (inactifs)"""
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(is_active=False).order_by(
        Product.name
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('products/inactive.html', products=products)


@bp.route('/<int:id>/destroy', methods=['POST'])
@login_required
def destroy(id):
    """Suppression definitive - ATTENTION: irreversible"""
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('Produit definitivement supprime', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur: {str(e)}', 'danger')
    
    return redirect(url_for('products.inactive'))