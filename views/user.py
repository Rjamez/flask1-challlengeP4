from flask import jsonify, request, Blueprint
from models import db, User
from werkzeug.security import generate_password_hash
from models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user_bp', __name__)

#Add user
@user_bp.route("/users", methods=["POST"])
def add_users():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    check_username = User.query.filter_by(username=username).first()
    check_email = User.query.filter_by(email=email).first()

    print("Email ",check_email)
    print("Username",check_username)
    if check_username or check_email:
        return jsonify({"error":"Username/email exists"}),406

    else:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success":"Added successfully"}), 201
    
    
#Update user 
@user_bp.route("/users/<int:user_id>", methods=["PATCH"])
@jwt_required()
def update_users(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user and user_id == current_user_id:
        data = request.get_json()
        username = data.get('username', user.username)
        email = data.get('email', user.email)
        password = generate_password_hash(data.get('password', user.password))

        # Correct filtering logic
        check_username = User.query.filter(User.username == username, User.id != user.id).first()
        check_email = User.query.filter(User.email == email, User.id != user.id).first()

        if check_username or check_email:
            return jsonify({"error": "Username/email exists"}), 406
        else:
            user.username = username
            user.email = email
            user.password = password
            db.session.commit()
            return jsonify({"success": "Updated successfully"}), 201
    else:
        return jsonify({"error": "User doesn't exist!"}), 406

    
# Delete
@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_users(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "The user you are trying to delete doesn't exist!"}), 406

    if user_id != current_user_id:
        return jsonify({"error": "You are not authorized to delete this user!"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": "Deleted successfully"}), 200

# Update password
@user_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_password(user_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user and user_id==current_user_id:
        data = request.get_json()
        password = generate_password_hash(data.get('password', user.password))

        
        check_password = User.query.filter_by(password=password ).first()

    
        if check_password:
            return jsonify({"error":"password exists"}),406

        else:
            user.password=password
          
            db.session.commit()
            return jsonify({"success":"Updated successfully"}), 201

    else:
        return jsonify({"error":"User doesn't exist!"}),406