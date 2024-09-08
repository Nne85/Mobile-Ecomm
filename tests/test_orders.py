""" This module is to test orders """

import unittest
from flask import Flask, json
from config import TestingConfig
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order


class TestOrdersEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class=TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Creating test users
        self.admin_user = User(username='admin', email='admin@test.com', is_admin=True)
        self.admin_user.set_password('adminpass')
        self.regular_user = User(username='user', email='user@test.com', is_admin=False)
        self.regular_user.set_password('userpass')
        db.session.add_all([self.admin_user, self.regular_user])
        db.session.commit()

        # Creating access token for login
        with self.app.test_request_context():
            self.admin_token = create_access_token(identity=self.admin_user.id)
            self.user_token = create_access_token(identity=self.regular_user.id)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_order(self):
        """ Create a user and a product """
        product = Product(name='Test Product', price=10.99)
        db.session.add(product)
        db.session.commit()

        # Create an order
        order_data = {'product_id': product.id, 'quantity': 2}
        response = self.client.post('/orders', json=order_data, headers={'Authorization': f'Bearer {self.user_token}'})
        print(response.data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['product_id'], product.id)
        self.assertEqual(data['quantity'], 2)
        self.assertEqual(data['total_price'], 21.98)

        # Test missing product_id
        invalid_order = {'quantity': 1}
        response = self.client.post('/orders', json=invalid_order, headers={'Authorization': f'Bearer {self.user_token}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Missing product ID', str(data['errors']))

        # Test non-existent product
        invalid_order = {'product_id': 999, 'quantity': 1}
        response = self.client.post('/orders', json=invalid_order, headers={'Authorization': f'Bearer {self.user_token}'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Product not found', str(data['errors']))


    def test_get_orders(self):
        """ Create a user and some orders """
        product = Product(name='Test Product', price=10.99)
        db.session.add(product)
        db.session.commit()
        
        order1 = Order(user_id=self.regular_user.id, product_id=product.id, quantity=1, total_price=10.0)
        order2 = Order(user_id=self.admin_user.id, product_id=product.id, quantity=2, total_price=20.0)
        db.session.add(order1)
        db.session.add(order2)
        db.session.commit()

        # Test admin user can see all orders
        response = self.client.get('/orders', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)


        # Test regular user can only see their own orders
        response = self.client.get('/orders', headers={'Authorization': f'Bearer {self.user_token}'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_id'], self.regular_user.id)

    def test_get_order_by_id(self):
        """ Create a user and an order """
        product = Product(name='Test Product', price=10.99)
        db.session.add(product)
        db.session.commit()

        order = Order(user_id=self.regular_user.id, product_id=product.id,
                      quantity=1, total_price=11.0)
        db.session.add(order)
        db.session.commit()

        # Test admin user can see the order
        response = self.client.get(f'/orders/{order.id}', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(response.status_code, 200)

        # Test order owner can see the order
        response = self.client.get(f'/orders/{order.id}',
                                   headers={'Authorization': f'Bearer {self.user_token}'})
        self.assertEqual(response.status_code, 200)

        # Test unauthorized access
        other_user = User(username='other', email='other@test.com', is_admin=False)
        other_user.set_password('otherpass')
        db.session.add(other_user)
        db.session.commit()
        with self.app.test_request_context():
            other_token = create_access_token(identity=other_user.id)
        response = self.client.get(f'/orders/{order.id}', headers={'Authorization': f'Bearer {other_token}'})
        self.assertEqual(response.status_code, 403)

        # Test non-existent order
        response = self.client.get('/orders/999', headers={'Authorization': f'Bearer {self.user_token}'})
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
