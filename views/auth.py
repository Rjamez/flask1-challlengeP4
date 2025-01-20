from flask import jsonify, request
from flask import Blueprint
from models import User,db
from datetime import datetime
from datetime import timezone
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth_bp", __name__)

#Login
@auth_bp.route('/login', methods= ['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    access_token = create_access_token(identity=user.id)
    if user and check_password_hash(user.password, password) :
        return jsonify({"access_token": access_token}), 200
    
    else:
        return jsonify({"error" : "User doesn't exist"}), 404
    
    
# Logout (not implementing token blacklisting here)
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Successfully logged out"}), 200

# # current user
@auth_bp.route('/current_user', methods=['GET'])
@jwt_required()
def current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    user_data = {
        'id' : user.id,
        'username' : user.username,
        'email' : user.email,
        'password' : user.password
    }
    return jsonify(user_data)

# # Logout
# @auth_bp.route("/logout", methods=["DELETE"])
# @jwt_required()
# def logout():
#     jti = get_jwt()["jti"]
#     now = datetime.now(timezone.utc)
#     db.session.add(TokenBlocklist(jti=jti, created_at=now))
#     db.session.commit()
#     return jsonify({"success ":"Logged out successfully"})

