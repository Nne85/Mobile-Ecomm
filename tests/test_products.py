import unittest
from config import TestingConfig
from flask import json
from app import create_app, db
from app.models import Product, Category, User
from flask_jwt_extended import create_access_token
import os

os.environ['Testing'] = 'True'


class TestProductEndpoints(unittest.TestCase):
    """  Setup and Create app in testing mode """
    def setUp(self):
        """ Create app in testing mode """
        self.app = create_app(config_class=TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()


        db.session.query(Category).delete()
        db.session.commit()

        self.category = Category(name='Test Category',
                                 description='Test Category Description')
        db.session.add(self.category)
        db.session.commit()
        
        db.session.query(Product).delete()
        db.session.commit()
        self.product = Product(name='Test Product',
                               description='Test Description',
                               image_path='/path/to/image.jpg',
                               price=10.0,
                               category_id=self.category.id,
                               stock=10,
                               status='available'
                            )
        db.session.add(self.product)


        db.session.query(User).delete()
        db.session.commit()
        self.admin_user = User(username='admin', email='admin@test.com',
                               is_admin=True)
        self.admin_user.set_password('password')
        db.session.add(self.admin_user)

        self.regular_user = User(username='user', email='user@test.com',
                                 is_admin=False)
        self.regular_user.set_password('password')
        db.session.add(self.regular_user)
        db.session.commit()

    def tearDown(self):
        """ Remove data from testing database"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_products(self):
        """ Test to get all products """
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Product')

    def test_get_product_by_id_success(self):
        """ Test to get product by id """
        response = self.client.get(f'/products/{self.product.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Test Product')

    def test_get_product_by_id_not_found(self):
        """ Test non-existent product """
        response = self.client.get('/products/100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_search_products(self):
        response = self.client.get('/products/search?query=Test')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Product')

    def test_get_categories(self):
        """ Test to get product category"""
        response = self.client.get('/products/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Category')

    def test_get_products_by_category(self):
        """ Test for getting products by a cAategory """
        response = self.client.get(f'/products/category/{self.category.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Product')

    def test_create_product_admin(self):
        """ Test to post a product """
        token = create_access_token(identity=self.admin_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'New Product',
                'price': 20.0, 'stock': 20,
                'atatus': 'available',
                'description': 'New Description',
                'image_path': '/path/to/new_image.jpg',
                'category_id': self.category.id
            }
        response = self.client.post('/products', json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'New Product')

    def test_create_product_non_admin(self):
        """ Test to add product as non-admin"""
        token = create_access_token(identity=self.regular_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'New Product',
                'price': 20.0,
                'category_id': self.category.id,
                'stock': 30,
                'image_path': '/path/to/new_image.jpg',
                'atatus': 'available'
            }
        response = self.client.post('/products', json=data, headers=headers)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Only admins can create products')

    def test_update_product_admin(self):
        """ Test if admin can update product"""

        token = create_access_token(identity=self.admin_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'Updated Product', 'price': 15.0}
        response = self.client.put(f'/products/{self.product.id}', json=data,
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Updated Product')
        self.assertEqual(data['price'], 15.0)

    def test_update_product_non_admin(self):
        """ Test to check if product update by non-admin"""
        token = create_access_token(identity=self.regular_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        data = {'name': 'Updated Product', 'price': 15.0}
        response = self.client.put(f'/products/{self.product.id}', json=data,
                                   headers=headers)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Only admins can update products')

    def test_delete_product_admin(self):
        """ Test to delete a product by an admin"""
        token = create_access_token(identity=self.admin_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/products/{self.product.id}', headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(db.session.get(Product, self.product.id))

    def test_delete_product_non_admin(self):
        """ Test to delete a product by non-admin"""
        token = create_access_token(identity=self.regular_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.delete(f'/products/{self.product.id}', headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(db.session.get(Product, self.product.id))


if __name__ == '__main__':
    unittest.main()
