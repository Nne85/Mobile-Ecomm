""" This module contains the user model for creating database """

from app import db
from app.models.product import Product
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship


class Category(db.Model):
    __tablename__ = 'categories'
    """ This class creates the Category model for products """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
