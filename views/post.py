from flask import jsonify, request
from flask import Blueprint
from models import Post, db
from flask_jwt_extended import jwt_required, get_jwt_identity

post_bp = Blueprint("post_bp", __name__)

# Add Post
@post_bp.route('/add', methods=['POST'])
@jwt_required()
def add():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    name = data['name']
    price = data['price']
    quantity = data['quantity']
    
    check_name = Post.query.filter_by(name=name).first()
    
    if check_name:
        return jsonify({'message': 'Product already exists'}), 400
    else:
        new_product = Post(name=name, price=price, quantity=quantity, user_id=current_user_id)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully'}), 201

# Get all products
@post_bp.route('/getall', methods=['GET'])
def get_all():
    products = Post.query.all()
    output = []
    for product in products:
        output.append({
            'id': product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        })
        
    return jsonify(output), 200

# Update Product
@post_bp.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Post.query.get(product_id)
    if product:
        data = request.get_json()
        user_id = data.get('user_id', product.user_id)
        name = data.get("name", product.name)
        price = data.get('price', product.price)
        quantity = data.get('quantity', product.quantity)
    
        check_name = Post.query.filter_by(name=name).first()

        if check_name:
            return jsonify({'message': 'Product already exists'}), 400
        else:
            product.name = name
            product.price = price
            product.quantity = quantity
            db.session.commit()
            return jsonify({'message': 'Product updated successfully'}), 200

# Delete Product
@post_bp.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Post.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    else:
        return jsonify({'message': 'Product not found'}), 404

# Get a single product by ID
@post_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Post.query.get(product_id)
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.quantity
        }), 200
    else:
        return jsonify({'message': 'Product not found'}), 404
