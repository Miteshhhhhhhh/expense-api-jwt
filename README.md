# Expense Tracker API

Flask + SQLAlchemy + JWT based backend for Personal Expense Tracker.

## Features Done
- User Auth: User Registration & Login with JWT
- Protected Routes: All routes require JWT Token
- Categories CRUD: Create, Get categories with type expense/income
- Transactions CRUD: Create, Get, Update, Delete transactions linked to categories
- Summary Endpoint: Get total income, total expense, and balance for logged-in user
- Monthly/Yearly Filtering: Filter summary by month and year using query parameters.

## Transactions
POST /transactions - Create new transaction. Auth required

GET /transactions - Get all user transactions. Auth required

PUT /transactions/<id> - Update a transaction. Auth required

DELETE /transactions/<id> - Delete a transaction. Auth required

Summary
GET /summary - Get income, expense and balance summary. Auth required

Summary GET /summary?month=8&year=2026 - Get monthly/yearly summary. Auth required

## Tech Stack
Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite

## How to Run
1. pip install -r requirements.txt
2. python app.py
3. API runs on http://127.0.0.1:5000
