from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from models import db, User, Post, TokenBlacklist
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure key in production

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()  # Create tables if they don't exist

@app.route('/')
def index():
    return "Welcome to the Flask App!"

# Route to register a user
@app.route('/register', methods=['POST'])
def register_user():
    """Route to create a new user."""
    data = request.get_json()
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields: username, email, or password"}), 400

    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Username or email already exists"}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

# Route to login a user
@app.route('/login', methods=['POST'])
def login():
    """Route to authenticate a user and return a JWT."""
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200

# Route to logout user
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Route to blacklist the user's token."""
    jti = get_jwt()['jti']  # Get the unique identifier for the token
    blacklist_entry = TokenBlacklist(jti=jti, created_at=datetime.utcnow())
    db.session.add(blacklist_entry)
    db.session.commit()
    return jsonify({"message": "Successfully logged out"}), 200

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    """Check if a token is in the blacklist."""
    jti = jwt_payload['jti']
    token = TokenBlacklist.query.filter_by(jti=jti).first()
    return token is not None

# Route to get current user
@app.route('/current_user', methods=['GET'])
@jwt_required()
def get_current_user():
    """Route to fetch details of the currently logged-in user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        # Include other fields as needed
    }
    return jsonify(user_data), 200

# Route to update user profile
@app.route('/user/update', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Route to update the profile information of the current user."""
    data = request.get_json()
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check if username or email is already taken
    if data.get('username') and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        user.username = data['username']

    if data.get('email') and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']

    db.session.commit()

    return jsonify({
        "message": "User profile updated successfully!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }), 200

# Route to update user password
@app.route('/user/updatepassword', methods=['PUT'])
@jwt_required()
def update_password():
    """Route to allow users to update their password."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({"error": "Missing required fields: current_password or new_password"}), 400

    if not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({"message": "Password updated successfully!"}), 200

# Route to delete user account
@app.route('/user/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Route to allow users to delete their own account."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User account deleted successfully!"}), 200

# Routes for posts
@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Route to create a new post."""
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if not data.get('title') or not data.get('content'):
        return jsonify({"error": "Missing required fields: title or content"}), 400

    new_post = Post(title=data['title'], content=data['content'], user_id=current_user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created successfully!", "post": {"id": new_post.id, "title": new_post.title, "content": new_post.content}}), 201

@app.route('/posts', methods=['GET'])
@jwt_required()
def fetch_posts():
    """Route to fetch all posts of the current user."""
    current_user_id = get_jwt_identity()
    posts = Post.query.filter_by(user_id=current_user_id).all()

    post_list = [{"id": post.id, "title": post.title, "content": post.content} for post in posts]
    return jsonify(post_list), 200

@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    """Route to update a specific post."""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()

    if not post:
        return jsonify({"error": "Post not found or not authorized"}), 404

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    db.session.commit()

    return jsonify({"message": "Post updated successfully!", "post": {"id": post.id, "title": post.title, "content": post.content}}), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Route to delete a specific post."""
    current_user_id = get_jwt_identity()
    post = Post.query.filter_by(id=post_id, user_id=current_user_id).first()

    if not post:
        return jsonify({"error": "Post not found or not authorized"}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({"message": "Post deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)