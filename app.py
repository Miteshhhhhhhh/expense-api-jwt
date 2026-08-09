from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database import db, Category, Transaction
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
    current_user_id = get_jwt_identity()
    name = data.get('name')
    type = data.get('type')
    if not name or not type:
        return {"error": "Name & Type are required"}, 409

    category = Category.query.filter_by(name=name, user_id=current_user_id).first()
    if category:
        return {"error": "Category already exists"}, 400

    new_category = Category(name=name, type=type, user_id=current_user_id)
    db.session.add(new_category)
    db.session.commit()
    return {
        "message": "Category created",
        "id": new_category.id,
        "name": new_category.name,
        "type": new_category.type
    }, 201

@app.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    current_user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=current_user_id).all()
    return jsonify([{"id": c.id, "name": c.name, "type": c.type, "user_id": c.user_id} for c in categories]), 200

@app.route('/transactions', methods=['POST'])
@jwt_required()
def add_transactions():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = data.get('amount')
    if not amount or amount <=0:
        return {"error": "Enter The Amount"}

    type = data.get('type')
    if type not in ['Income', 'Expense']:
        return {"error": "Select the type: Income or Expense"}

    category_id = data.get('category_id')
    if not category_id:
        return {"error": "category_id is required"}, 400

    category = Category.query.get(category_id)
    if not category or category.user_id != current_user_id:
        return {"error": "Forbidden "}, 403

    description = data.get('description')
    new_transaction = Transaction(amount=amount, type=type, category_id=category_id, description=description, user_id=current_user_id)
    db.session.add(new_transaction)
    db.session.commit()
    return {"message": "Transaction Done"}, 201

@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(user_id=current_user_id).all()
    return jsonify([{"amount": t.amount, "type": t.type, "description": t.description, "date": t.transaction_date} for t in transactions]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


