# Expense Tracker API

A FastAPI backend for tracking income and expenses. Users register, log in to get a JWT, and manage their own transactions.

## Tech Stack

FastAPI, SQLAlchemy, PostgreSQL, Pydantic, python-jose for JWT, passlib with bcrypt for password hashing.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your own values:

| Variable | Description |
|----------|-------------|
| `DB_PASS` | PostgreSQL password |
| `DATABASE_URL` | Connection string, for example `postgresql://postgres:pass@localhost:5432/expense_tracker` |
| `SECRET_KEY` | Secret for signing JWTs, generate with `openssl rand -hex 32` |
| `ALGORITHM` | Signing algorithm, `HS256` |

Create the database before starting. Tables are created automatically on first run.

## Run

```bash
uvicorn main:app --reload
```

Interactive docs at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create an account |
| POST | `/auth/login` | No | Get an access token |
| POST | `/transactions/` | Yes | Create a transaction |
| GET | `/transactions/` | Yes | List your transactions |
| GET | `/transactions/filter` | Yes | List with optional filters |
| GET | `/transactions/{id}` | Yes | Get one transaction |
| PUT | `/transactions/{id}` | Yes | Update a transaction |
| DELETE | `/transactions/{id}` | Yes | Delete a transaction |

Protected endpoints need an `Authorization: Bearer <token>` header. Tokens expire after 15 minutes.

## Examples

### Register

Request:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123"
}
```

Response:

```json
{ "message": "User registered successfully!" }
```

### Login

Sent as form data, not JSON, since it uses the OAuth2 password flow. Fields are `username` and `password`.

Response:

```json
{
  "message": "Login successful!",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create transaction

Request:

```json
{
  "title": "Grocery Shopping",
  "amount": 50.75,
  "type": "expense",
  "category": "Food",
  "date": "2026-08-23T14:30:00"
}
```

Response, status 201:

```json
{
  "message": "Transaction created successfully",
  "transaction": {
    "id": 1,
    "title": "Grocery Shopping",
    "amount": 50.75,
    "type": "expense",
    "category": "Food",
    "date": "2026-08-23T14:30:00",
    "owner_id": 1
  }
}
```

`type` must be either `income` or `expense`, and `amount` must be greater than zero.

### Update transaction

Send only the fields you want to change.

```json
{
  "title": "Weekly Groceries",
  "amount": 75.25
}
```

### Filter transactions

All query parameters are optional and can be combined:

```
/transactions/filter?type=expense&category=Food&minimum_amount=10&maximum_amount=100
```

## Tests

```bash
pytest test/ -v
```

The tests run against the database in `DATABASE_URL` and use a dummy user with id 123. Any rows for that user are removed before and after the run, and the delete test runs last so nothing is left behind.
