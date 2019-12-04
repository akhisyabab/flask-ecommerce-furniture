import datetime

from functools import wraps
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from project import db, bcrypt

from passlib.hash import pbkdf2_sha256 as sha256


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(128), nullable=True)
    username = db.Column(db.String(128), nullable=False, unique=True,)
    password = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=True)
    register_on = db.Column(db.DateTime, nullable=True)
    is_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    role = db.Column(db.String, default='user')
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = password
        self.phone = None
        self.address = None
        self.register_on = datetime.datetime.now()
        self.is_confirmed = False
        self.role = role
        self.authenticated = False

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def __repr__(self):
        return 'User {}'.format(self.username)

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=True)

    def __init__(self, name='uncategorized'):
        self.name = name

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def __repr__(self):
        return 'Category {}'.format(self.name)


class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.DECIMAL, nullable=False)
    description = db.Column(db.String(128), nullable=True)
    image = db.Column(db.String(128), nullable=False)
    stock = db.Column(db.Integer, nullable=True)
    category = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def __init__(self, name, price, description, image, stock, category):
        self.name = name
        self.price = price
        self.description = description
        self.image = image
        self.stock = stock
        self.category = category

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def __repr__(self):
        return 'Product {}'.format(self.name)


class Cart(db.Model):

    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('carts.id'))

    def __init__(self, user_id, product_id):
        self.user_id = user_id
        self.product_id = product_id


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
