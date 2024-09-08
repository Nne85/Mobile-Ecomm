""" This module contains the user model for creating database """

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime
import bcrypt
import re
from app import db


class User(db.Model):
    """User model for storing user related details"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship('Order', backref='users', lazy=True)

    def __repr__(self):
        return f"<User {'Admin' if self.is_admin else ''}  {self.username}>"


    def set_password(self, password):
        """ This function hashs the user password """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        """ This dunction verifies the password """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @staticmethod
    def validate_email(email):
        """Validates the email format."""
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }
