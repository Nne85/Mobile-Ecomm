""" This module contain the Product class for creating database. """

from app import db
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import validates


class Product(db.Model):
        __tablename__ = 'products'
        """ This class represents a Product in the system with fields like id, name,
        description, etc.
        """

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=True)
        price = db.Column(db.Float, nullable=False)
        image_path = db.Column(db.String(255))
        category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
        stock = db.Column(db.Integer, nullable=False, default=0)
        status = db.Column(db.String(20), nullable=False, default='available')

        orders = db.relationship('Order', backref='products', lazy='dynamic')
        category = db.relationship('Category', backref='products')

        def __repr__(self):
            return f'<Product {self.name}>'

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'price': self.price,
                'stock': self.stock,
                'status': self.status,
                'category_id': self.category_id
            }
        
        @validates('price')
        def validate_price(self, key, value):
            if value < 0:
                raise ValueError("Price must be non-negative")
            return value

        @validates('stock')
        def validate_stock(self, key, value):
            if value < 0:
                raise ValueError("Stock cannot be negative")
            return value

        def is_in_stock(self):
            return self.stock > 0

        def adjust_stock(self, quantity):
            if self.stock - quantity < 0:
                raise ValueError("Insufficient stock")
            self.stock -= quantity
