from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, TokenBlocklist
from flask_mail import Mail,Message
from views.post import post_bp  # Importing post_bp
from views.user import user_bp  # Ensure user_bp is imported
from views.auth import auth_bp  # Ensure auth_bp is imported
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your email server (Gmail in this case)
app.config['MAIL_PORT'] = 587                # Port for Gmail's SMTP server
app.config['MAIL_USE_TLS'] = True            # Use TLS (Transport Layer Security)
app.config['MAIL_USERNAME'] = 'robin.adhola@student.moringaschool.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'bary ebkb lntl xafp'        # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'MAIL_USERNAME'  # Default sender email

mail = Mail(app)

db.init_app(app)
migrate = Migrate(app, db)

app.config["JWT_SECRET_KEY"] = "vghsdvvsjvy436u4wu37118gcd#"  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
jwt.init_app(app)

from views import *

app.register_blueprint(post_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully."}), 201
