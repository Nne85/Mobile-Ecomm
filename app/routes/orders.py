from flask import Blueprint, request, jsonify
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('orders', __name__)

@bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """
      Create a new order.
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Missing order data'}), 400
    user_id = get_jwt_identity()

    errors = []
    if not data.get('product_id'):
        errors.append({'field': 'product_id', 'message': 'Missing product ID'})
    if data.get('quantity', 1) <= 0:
        errors.append({'field': 'quantity', 'message': 'Quantity must be a positive integer'})
    product = db.session.get(Product, data.get('product_id'))
    if not product:
        errors.append({'field': 'product_id', 'message': 'Product not found'})

    if errors:
        return jsonify({'message': 'Validation errors', 'errors': errors}), 400
    
    order = Order(
        user_id=user_id,
        product_id=product.id,
        quantity=data['quantity'],
        total_price=product.price * data['quantity']
    )

    db.session.add(order)
    db.session.commit()

    return jsonify(order.to_dict()), 201


@bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """
       Retrieve a list of all orders (admin only or filter by user).
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if user.is_admin:
        orders = db.session.query(Order).all()
    else:
        orders = db.session.query(Order).filter_by(user_id=user.id)
    return jsonify([order.to_dict() for order in orders]), 200


@bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_by_id(order_id):
    """
      Retrieve a specific order by ID.
    """
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Oder not found'}), 404

    if not user.is_admin and order.user_id != user.id:
        return jsonify({'message': 'Unauthorized access'}), 403

    return jsonify(order.to_dict()), 200


@bp.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """
      Update an existing order (e.g., shipping address, billing information).
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Missing order data'}), 400
    
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    if not current_user.is_admin and order.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized access'}), 403

    order.quantity = data.get('quantity', order.quantity)
    order.total_price = order.product.price * order.quantity

    db.session.commit()
    return jsonify(order.to_dict()), 200


@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """
      Update order status.
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'message': 'Missing status information'}), 400

    if not current_user.is_admin and order.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized access'}), 403

    order.status = data.get('status', order.status)
    db.session.commit()
    return jsonify({'message': 'Order updated successfully', 'order': order.to_dict()}), 200


@bp.route('/orders/history/<int:user_id>', methods=['GET'])
@jwt_required()
def order_history(user_id):
    """
       Retrieve a list of the user's past orders.
    """
    orders = db.session.query(Order).filter_by(user_id=current_user_id).all()
    return jsonify([order.to_dict() for order in orders]), 200


@bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """
       Cancel Order
    """
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    if not current_user.is_admin and order.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized access'}), 403

    if order.status not in ['pending', 'processing']:
        return jsonify({'message': 'Order cannot be canceled'}), 400


    order.status = 'Order Canceled'
    db.session.commit()
    return jsonify(order.to_dict()), 200
