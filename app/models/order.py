""" This module contains the order model for creating database. """

from app import db
from app.models.user import User
from app.models.product import Product
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    """ This class creates the Order model with fields id, user_id, product_id, quantity,
    total_price, status, and created_at.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __repr__(self):
        return f'<Order {self.id} - User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status,
            'user_id': self.user_id,
            'product_id': self.product_id
        }
