# Expense Tracker API

Flask + SQLAlchemy + JWT based backend for Personal Expense Tracker.

## Features Done
- **User Auth**: User Registration & Login with JWT
- **Protected Routes**: All routes require JWT Token
- **Categories CRUD**: Create, Get categories with type expense/income
- **Transactions CRUD**: Create and Get transactions linked to categories

## Tech Stack
Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite

## API Endpoints

### Auth
`POST /register` - Register new user
`POST /login` - Login and get JWT token

### Categories
`POST /categories` - Create category. Auth required
`GET /categories` - Get all user categories. Auth required

### Transactions
`POST /transactions` - Create new transaction. Auth required
`GET /transactions` - Get all user transactions. Auth required

## How to Run
1. pip install -r requirements.txt
2. python app.py
3. API runs on http://127.0.0.1:5000
