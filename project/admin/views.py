from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from project.models.models import User, Category
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