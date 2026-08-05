# Expense Tracker API

Flask + SQLAlchemy + JWT based backend for Expense Tracker.

## Features Done
- User Registration & Login with JWT
- Protected Routes
- Categories CRUD: Create category with type expense/income

## Tech Stack
Flask, Flask-SQLAlchemy, Flask-JWT-Extended, SQLite

## How to Run
1. pip install -r requirements.txt
2. python app.py
3. API runs on http://127.0.0.1:5000

## API Endpoints
POST /register - Register user
POST /login - Get JWT token
POST /categories - Create category [Auth required]
GET /categories - Get all categories [Auth required]

