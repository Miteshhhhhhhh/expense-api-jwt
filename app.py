from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database import db, Category
from auth import register_user, login_user
from datetime import timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-karna'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
db.init_app(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    return register_user(username, email, password)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    return login_user(username, password)

@app.route('/categories', methods=['POST'])
@jwt_required()
def categories():
    data = request.get_json()
    user_id = get_jwt_identity()
    name = data.get('name')
    type = data.get('type')
    if not name or not type:
        return {"error": "Name & Type are required"}, 409

    category = Category.query.filter_by(name=name, user_id=user_id).first()
    if category:
        return {"error": "Category already exists"}, 400

    new_category = Category(name=name, type=type, user_id=user_id)
    db.session.add(new_category)
    db.session.commit()
    return {"message": "Category created"}, 201

@app.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": c.id, "name": c.name, "type": c.type} for c in categories]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


