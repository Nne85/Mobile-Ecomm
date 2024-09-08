""" This module tests for  user endpoints """

import unittest
from config import TestingConfig
from flask import json
from app import create_app, db
from app.models.user import User
from app.models.order import Order
from app.models.blacklist import TokenBlacklist
from flask_jwt_extended import create_access_token, get_jwt
import os

os.environ['Testing'] = 'True'


class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class=TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        db.session.query(User).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user(self):
        data = {'username': 'test', 'email': 'test@example.com', 'password': 'password'}
        response = self.client.post('/users/register', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'User registered successfully')
        user = db.session.query(User).filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)

    def test_register_user_missing_fields(self):
        data = {'username': 'test', 'email': 'test@example.com'}
        response = self.client.post('/users/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Username, email, and password are required')

    def test_register_user_invalid_email(self):
        data = {'username': 'test', 'email': 'invalid_email', 'password': 'password'}
        response = self.client.post('/users/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', [error['field'] for error in response.json['errors']])

    def test_register_user_password_too_short(self):
        """ Test registration with password less than 8 characters """
        data = {'username': 'test', 'email': 'test@example.com', 'password': 'short'}
        response = self.client.post('/users/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', [error['field'] for error in response.json['errors']])

    def test_register_user_username_taken(self):
        """ Test registration with existing username """
        user = User(username='test', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        data = {'username': 'test', 'email': 'test2@example.com', 'password': 'password'}
        response = self.client.post('/users/register', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', [error['field'] for error in response.json['errors']])

    def test_login_user(self):
        """ Test user login with valid credentials """
        user = User(username='test', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        data = {'email': 'test@example.com', 'password': 'password'}
        response = self.client.post('/users/login', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login_user_invalid_credentials(self):
        """ Test login with missing fields """
        data = {'email': 'test@example.com', 'password': 'wrong_password'}
        response = self.client.post('/users/login', json=data)
        self.assertEqual(response.status_code, 401)
        if 'error' in response.json:
            self.assertEqual(response.json['error'], 'Email and password are required')

    def test_logout_user(self):
        user = User(username='test', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        login_data = {'email': 'test@example.com', 'password': 'password'}
        login_response = self.client.post('/users/login', json=login_data)
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json['access_token']
        
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.post('/users/logout', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Logged out successfully', response.json['message'])


        # Check if the token is blacklisted
        jti = get_jwt()['jti']
        blacklisted = TokenBlacklist.query.filter_by(jti=jti).first()
        self.assertIsNotNone(blacklisted)


if __name__ == "__main__":
    unittest.main()
