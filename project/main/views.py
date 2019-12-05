from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError

from project.models.models import User, Product
from project import db


main_blueprint = Blueprint('main', __name__, template_folder='templates')

@main_blueprint.route('/')
def home():
    new_products = Product.query.order_by(Product.id.desc()).limit(8).all()
    return render_template('main.html', new_products=new_products)

@main_blueprint.route('/product_detail/<product_id>/', methods=['GET', 'POST'])
def product_detail(product_id):
    product = Product.find_by_id(product_id)
    return render_template('main_product_detail.html', product=product)