from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database import db, Category, Transaction
from auth import register_user, login_user
from datetime import timedelta
import os
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///finance.db')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-karna')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
db.init_app(app)
jwt = JWTManager(app)
with app.app_context():
    db.create_all()

def get_converted_amount(amount, target_currency):
    if not target_currency or target_currency.upper() == "USD":
        return amount, 1

    try:
        url = f"https://api.frankfurter.dev/v1/latest?from=USD&to={target_currency.upper()}"
        response = requests.get(url, timeout=5).json()
        rate = response['rates'][target_currency.upper()]
        return amount * rate, rate
    except Exception as e:
        print("Conversion Error:", e)
        return amount, None

@app.route('/')
def home():
    return {"message": "API is Live! Use /register and /login"}

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
    if not name:
        return {"error": "Name is required"}, 409

    category = Category.query.filter_by(name=name, user_id=current_user_id).first()
    if category:
        return {"error": "Category already exists"}, 400

    new_category = Category(name=name, user_id=current_user_id)
    db.session.add(new_category)
    db.session.commit()
    return {
        "message": "Category created",
        "id": new_category.id,
        "name": new_category.name,
    }, 201

@app.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    current_user_id = get_jwt_identity()
    categories = Category.query.filter_by(user_id=current_user_id).all()
    return jsonify([{"id": c.id, "name": c.name, "user_id": c.user_id} for c in categories]), 200

@app.route('/transactions', methods=['POST'])
@jwt_required()
def add_transactions():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    amount = data.get('amount')
    if not amount:
        return {"error": "Enter The Amount"}
    try:
        amount = float(amount)
    except:
        return jsonify({"error": "Amount must be a number"}), 400
    if amount <=0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

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
    type = request.args.get("type")
    category_id = request.args.get("category_id")


    query = Transaction.query.filter_by(user_id=current_user_id)
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == int(category_id))

    transactions = query.all()
    return jsonify([{"amount": t.amount, "type": t.type, "id": t.id, "user_id": t.user_id, "category_id": t.category_id, "description": t.description, "date": t.transaction_date} for t in transactions]), 200

@app.route('/transactions/<int:id>', methods=['PUT'])
@jwt_required()
def update_transactions(id):
    current_user_id = int(get_jwt_identity())
    edit = Transaction.query.filter_by(id=id).first()
    if not edit:
        return {"error": "Transactions not found"}, 404

    if edit.user_id != current_user_id:
        return {"error": "Forbidden"}, 403

    data = request.get_json()
    edit.amount = data.get('amount', edit.amount)
    edit.type = data.get('type', edit.type)
    edit.category_id = data.get('category_id', edit.category_id)
    edit.description = data.get('description', edit.description)
    edit.transaction_date = data.get('transaction_date', edit.transaction_date)

    db.session.commit()
    return jsonify({
        "id": edit.id,
        "amount": edit.amount,
        "type": edit.type,
        "description": edit.description,
        "date": str(edit.transaction_date)
    }), 200

@app.route('/transactions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transactions(id):
    current_user_id = int(get_jwt_identity())
    delete = Transaction.query.filter_by(id=id).first()

    if not delete:
        return {"error": "Transaction not found"}, 404

    if delete.user_id != current_user_id:
        return {"error": "Forbidden"}, 403

    db.session.delete(delete)
    db.session.commit()
    return {"message": "Delete Successfully"}, 200

@app.route('/summary', methods=['GET'])
@jwt_required()
def transaction_summary():
    current_user_id = get_jwt_identity()
    month = request.args.get("month")
    year = request.args.get("year")

    if month and year:
        month = int(month)
        year = int(year)
        income_sum = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.user_id==current_user_id, Transaction.type=="Income",
                                                                          db.func.extract("month", Transaction.created_at) == int(month),
                                                                          db.func.extract("year", Transaction.created_at) == int(year)).scalar()

        expense_sum = db.session.query(db.func.sum(Transaction.amount)).filter(Transaction.user_id==current_user_id, Transaction.type=="Expense",
                                                                           db.func.extract("month", Transaction.created_at) == int(month),
                                                                           db.func.extract("year", Transaction.created_at) == int(year)).scalar()
    else:
        income_sum = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=current_user_id, type="Income").scalar()
        expense_sum = db.session.query(db.func.sum(Transaction.amount)).filter_by(user_id=current_user_id, type="Expense").scalar()

    total_income = income_sum or 0
    total_expense = expense_sum or 0
    balance = total_income - total_expense

    target_currency = request.args.get('currency', 'USD')
    converted_income, rate = get_converted_amount(total_income, target_currency)
    converted_expense, _ = get_converted_amount(total_expense, target_currency)
    converted_balance, _ = get_converted_amount(balance, target_currency)

    return jsonify({
        "Total Income": total_income,
        "Total Expense": total_expense,
        "Balance": balance,
        "Converted": {
            "currency": target_currency.upper(),
            "rate_used": rate,
            "Total Income": round(converted_income, 2),
            "Total Expense": round(converted_expense, 2),
            "Balance": round(converted_balance, 2)
        }
    }), 200


@app.route('/summary/category', methods=['GET'])
@jwt_required()
def category_summary():
    current_user_id = get_jwt_identity()
    month = request.args.get("month")
    year = request.args.get("year")

    if not month or not year:
        return jsonify({"error": "month & year required"}), 400
    try:
        month = int(month)
        year = int(year)
        if month <1 or month >12:
            return jsonify({"error": "Invalid month"}), 400
    except:
        return jsonify({"error": "month & year must be numbers"}), 400

    expense_result = db.session.query(Transaction.category_id, Category.name, db.func.sum(Transaction.amount)).join(Category).filter(Transaction.user_id==current_user_id,
                                                                                                                Transaction.type=="Expense",
                                             db.func.extract('month', Transaction.created_at) == int(month),
                                             db.func.extract('year', Transaction.created_at) == int(year)).group_by(Category.name)

    result = []
    target_currency = request.args.get('currency', 'USD')
    converted_rate = None
    if target_currency.upper() != "USD":
        try:
            url = f"https://api.frankfurter.dev/v1/latest?from=USD&to={target_currency.upper()}"
            resp = requests.get(url, timeout=5).json()
            converted_rate = resp['rates'][target_currency.upper()]
        except:
            converted_rate = None

    result = []
    for category_id, name, total in expense_result:
        converted_total = total * converted_rate if converted_rate else total
        result.append({
            "category_id": category_id,
            "category": name,
            "total": total,
            "converted_total": round(converted_total, 2),
            "currency": target_currency.upper(),
            "rate": converted_rate or 1
        })

    return jsonify(result)

if __name__ == '__main__':
     app.run(debug=False)




