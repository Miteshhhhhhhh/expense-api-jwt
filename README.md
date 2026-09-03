# Expense Tracker API

Flask + SQLAlchemy + JWT based backend for Personal Expense Tracker.
> 🚀 Live: https://expense-api-jwt.onrender.com

## Features Done
- **Multi-Currency Support (NEW): Live currency conversion via Frankfurter API**
- **External API Integration: Integrated 3rd party exchange rate API with optimized single-call per request**
- **User Auth:** Registration & Login with JWT
- **Protected Routes:** All routes require JWT Token
- **Categories CRUD:** Create, Get categories with type expense/income + User Isolation
- **Transactions CRUD:** Create, Get, Update, Delete transactions linked to categories
- **Dynamic Transaction Filtering:** Filter by type and category_id
- **Summary Endpoint:** Total income, expense, balance for logged-in user
- **Category-based Summary:** Summary filtered by category_id
- **Monthly/Yearly Filtering:** Filter summary by month/year
- **Security:** JWT protection + 401/403 checks + User isolation (User A can't access User B's data)

## API Routes

### Auth (Public)
- `POST /register` - Register new user
- `POST /login` - Login & get JWT token

### Categories (Auth Required)
- `POST /categories` - Create category
- `GET /categories` - Get user's categories

### Transactions (Auth Required)
- `POST /transactions` - Create transaction
- `GET /transactions` - Get all user transactions
- `GET /transactions?type=Income` - Filter by type
- `GET /transactions?category_id=1` - Filter by category
- `GET /transactions?type=Expense&category_id=2` - Combine filters
- `PUT /transactions/<id>` - Update transaction (owner only)
- `DELETE /transactions/<id>` - Delete transaction (owner only)

### Summary (Auth Required)
* `GET /summary` - Get income, expense, balance
* `GET /summary?month=8&year=2026` - Monthly/yearly summary
* `GET /summary/category?month=09&year=2026` - Category-wise summary
* `GET /summary?currency=INR` - **Live conversion to INR (NEW)**
* `GET /summary/category?month=09&year=2026&currency=EUR` - **Category summary with live EUR conversion (NEW)**
* Supports: USD, INR, EUR, JPY, GBP, etc. - Live rates via https://api.frankfurter.dev

## Tech Stack
Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite, gunicorn, **requests, Frankfurter API**

## How to Run

1. Clone repo
   `git clone https://github.com/Miteshhhhhhh/expense-api-jwt.git`

2. Create virtual env
   `python -m venv venv` & `venv\Scripts\activate` (Windows)

3. Install dependencies
   `pip install -r requirements.txt`

4. Create .env (local only)
   DATABASE_URL=sqlite:///finance.db
   JWT_SECRET_KEY=your_super_secret_key_here

6. Run
   `python app.py`
   API runs on `http://127.0.0.1:5000`

## Security Checks Implemented
- 401 when no token
- 403 when accessing other user's category/transaction
- 404 for invalid IDs
- 400 for bad request body
