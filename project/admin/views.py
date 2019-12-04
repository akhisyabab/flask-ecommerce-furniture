import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from project.models.models import User, Category, Product
from project.utils.decorator import admin_required
from project import db


admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        current_user = User.find_by_username(username)
        if not current_user:
            flash('ERROR! user not found.', 'error')
            return redirect(url_for('admin.dashboard'))

        if current_user.role != 'admin':
            flash('Permission denied. Admin only', 'error')
            return redirect(url_for('admin.dashboard'))

        if User.verify_hash(password, current_user.password):
            current_user.authenticated = True
            db.session.add(current_user)
            db.session.commit()
            login_user(current_user)

            return redirect(url_for('admin.dashboard'))
        else:
            db.session.rollback()
            flash('ERROR! Incorrect login credentials.', 'error')

    return render_template('login.html')


@admin_blueprint.route('/admin/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('admin.login'))


@admin_blueprint.route('/admin/')
@login_required
def dashboard():
    user = current_user
    return render_template('dashboard.html', current_user=user)


# USERS ############################################
@admin_blueprint.route('/admin/users')
@login_required
def users():
    all_user = User.query.all()
    user = current_user
    return render_template('users.html', users=all_user, current_user=user)


@admin_blueprint.route('/admin/user_add', methods=['GET', 'POST'])
@login_required
def user_add():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = User.generate_hash(request.form.get('password'))
            is_admin = request.form.get('is-admin')
            if is_admin:
                new_user = User(username, password, role='admin')
            else:
                new_user = User(username, password)

            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('admin.users'))

        except IntegrityError:
            db.session.rollback()
            flash('ERROR! username ({}) already exists.'.format(username), 'error')

    return render_template('user_add.html')


@admin_blueprint.route('/admin/user_delete/<user_id>')
@login_required
def user_delete(user_id):
    user = User.find_by_id(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users'))


@admin_blueprint.route('/admin/user_edit/<user_id>/', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    user = User.find_by_id(user_id)
    if request.method == 'POST':
        try:
            is_admin = request.form.get('is-admin')
            password = request.form.get('password')

            user.username = request.form.get('username')
            # user.password = User.generate_hash(password)
            # if User.verify_hash(password, current_user.password):
            #     user.password = password

            user.address = request.form.get('address')
            if is_admin:
                user.role = 'admin'
            else:
                user.role = 'user'

            db.session.commit()
            return redirect(url_for('admin.users'))

        except IntegrityError:
            db.session.rollback()
            flash('ERROR! username ({}) already exists.'.format(user.username), 'error')

    return render_template('user_edit.html', user=user)


# Categories ############################################
@admin_blueprint.route('/admin/categories')
@login_required
def categories():
    all_category = Category.query.all()
    return render_template('categories.html', categories=all_category)

@admin_blueprint.route('/admin/category_add', methods=['GET', 'POST'])
@login_required
def category_add():
    if request.method == 'POST':
        try:
            category_name = request.form.get('category-name')
            new_category = Category(category_name)
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for('admin.categories'))

        except IntegrityError as e:
            db.session.rollback()
            flash('ERROR! ({}) '.format(e), 'error')

    return render_template('category_add.html')


@admin_blueprint.route('/admin/category_delete/<category_id>')
@login_required
def category_delete(category_id):
    category = Category.find_by_id(category_id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin.categories'))


@admin_blueprint.route('/admin/category_edit/<category_id>', methods=['GET', 'POST'])
@login_required
def category_edit(category_id):
    category = Category.find_by_id(category_id)
    if request.method == 'POST':
        try:
            category_name = request.form.get('category-name')
            category.name = category_name

            db.session.commit()
            return redirect(url_for('admin.categories'))

        except IntegrityError as e:
            db.session.rollback()
            flash('ERROR! ({}) '.format(e), 'error')

    return render_template('category_edit.html', category=category)

# Products ############################################
@admin_blueprint.route('/admin/products')
@login_required
def products():
    all_product = Product.query.all()
    return render_template('products.html', products=all_product, cat=Category)


@admin_blueprint.route('/admin/product_add', methods=['GET', 'POST'])
@login_required
def product_add():
    all_category = Category.query.all()
    if request.method == 'POST':
        try:
            product_name = request.form.get('product-name')
            product_price = request.form.get('product-price')
            product_description = request.form.get('product-description')
            product_image_file = request.files['product-image']
            if product_image_file:
                product_image = '{}-{}'.format(product_name, product_image_file.filename)
                basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                product_image_file.save(os.path.join(basedir, current_app.config['PRODUCT_IMAGE'], product_image))
            else:
                product_image = None

            product_stock = request.form.get('product-stock')
            product_category_id = request.form.get('product-category_id')
            new_product = Product(product_name, product_price, product_description, product_image, product_stock, product_category_id)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('admin.products'))

        except IntegrityError as e:
            db.session.rollback()
            flash('ERROR! ({}) '.format(e), 'error')

    return render_template('product_add.html', categories=all_category)


@admin_blueprint.route('/admin/product_delete/<product_id>')
@login_required
def product_delete(product_id):
    product = Product.find_by_id(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.products'))


@admin_blueprint.route('/admin/product_edit/<product_id>', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    product = Product.find_by_id(product_id)
    all_category = Category.query.all()
    if request.method == 'POST':
        try:
            product_name = request.form.get('product-name')
            product_price = request.form.get('product-price')
            product_description = request.form.get('product-description')
            product_image_file = request.files['product-image']
            if product_image_file:
                product_image = '{}-{}'.format(product_name, product_image_file.filename)
                basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
                product_image_file.save(os.path.join(basedir, current_app.config['PRODUCT_IMAGE'], product_image))
            else:
                product_image = None

            product_stock = request.form.get('product-stock')
            product_category_id = request.form.get('product-category_id')

            product.name = product_name
            product.price = product_price
            product.description = product_description
            if product_image_file:
                product.image = product_image
            product.stock = product_stock
            product.category = product_category_id

            db.session.commit()
            return redirect(url_for('admin.products'))

        except IntegrityError as e:
            db.session.rollback()
            flash('ERROR! ({}) '.format(e), 'error')

    return render_template('product_edit.html', product=product, categories=all_category, cat=Category)