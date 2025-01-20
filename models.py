from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates  # Importing validates

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    # Hash the password before storing it
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check the hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Relationship to Product model
    products = db.relationship('Product', backref='user', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    # Foreign key to User model
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name cannot be empty.")
        return name

    @validates('price')
    def validate_price(self, key, price):
        if price <= 0:
            raise ValueError("Price must be a positive value.")
        return price

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return quantity

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# class TokenBlocklist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     jti = db.Column(db.String(36), nullable=False, index=True)
#     created_at = db.Column(db.DateTime, nullable=False)
