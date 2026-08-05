from database import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

def register_user(username, email, password):
    existing_user = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()

    if existing_user or existing_email:
        return {"error": "User already exists"}, 409

    hashed_Password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_Password)

    db.session.add(new_user)
    db.session.commit()
    return {"message": "User created successfully"}, 201

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": "Invalid credentials"}, 401
    if not check_password_hash(user.password_hash, password):
        return {"error": "Invalid credentials"}, 401

    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}, 200


