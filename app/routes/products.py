
from flask import Blueprint, request, jsonify, abort
from app.models.product import Product
from app.models.user import User
from app.models.order import Order
from app.models.category import Category
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db

bp = Blueprint('products', __name__)

@bp.route('/products', methods=['GET'])
def get_all_products():
    """ Returns list of all products """
    products = db.session.query(Product).all()
    return jsonify([product.to_dict() for product in products]), 200


@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """ Retrieve a specific product by ID. """
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict()), 200


@bp.route('/products/search', methods=['GET'])
def search_products():
    """ Search products by keyword."""
    query = request.args.get('query', '')
    products = db.session.query(Product).filter(Product.name.like(f'%{query}%')).all()
    return jsonify([product.to_dict() for product in products]), 200



@bp.route('/products/categories', methods=['GET'])
def get_categories():
    """ Retrieve product by category"""
    categories = db.session.query(Category).all()
    return jsonify([category.to_dict() for category in categories])


@bp.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    products = db.session.query(Product).filter_by(category_id=category_id).all()
    return jsonify([product.to_dict() for product in products]), 200


@bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    """ Create produt by admin"""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user.is_admin:
        return jsonify({'error': 'Only admins can create products'}), 403
    
    data = request.get_json()
    product = Product(
        name=data['name'],
        description=data.get('description'),
        image_path=data.get('image_path'),
        price=data['price'],
        stock=data.get('stock', 0),
        category_id=data.get('category_id')
    )

    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """  Updates an existing product."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user.is_admin:
        return jsonify({'error': 'Only admins can update products'}), 403

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 401
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.category_id = data.get('category_id', product.category_id)

    db.session.commit()
    return jsonify(product.to_dict()), 200


@bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """ Delete a product """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user.is_admin:
        return jsonify({'error': 'Only admins can delete products'}), 403

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'Product not found'})

    db.session.delete(product)
    db.session.commit()
    return '', 204
