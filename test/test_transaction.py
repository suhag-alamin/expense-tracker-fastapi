from datetime import datetime
from test.test_main import client
from main import app
from fastapi import status
from security import get_current_user
from database import SessionLocal
from models import Transaction, User


def override_get_current_user():
    return {"username": "testuser", "id": 123}


app.dependency_overrides[get_current_user] = override_get_current_user


def test_transaction():
    db = SessionLocal()

    # remove any existing data for the test user
    db.query(Transaction).filter(Transaction.owner_id == 123).delete()
    db.query(User).filter(User.id == 123).delete()
    db.commit()

    user = User(
        id=123,
        username="testuser",
        email="testuser@example.com",
        hashed_password="password123"
    )
    db.add(user)
    db.commit()

    transaction = Transaction(
        id=123,
        title="Test Transaction",
        amount=50.75,
        type="expense",
        category="Food",
        date="2026-08-25T00:00:00",
        owner_id=123
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.close()


def test_read_transactions():
    response = client.get("/transactions/")
    assert response.status_code == status.HTTP_200_OK


def test_read_transaction():
    response = client.get("/transactions/123")
    assert response.status_code == status.HTTP_200_OK


def test_create_transaction():
    transaction_data = {
        "title": "New Test Transaction",
        "amount": 25.50,
        "type": "income",
        "category": "Salary",
        "date": "2026-08-24T10:00:00"
    }
    response = client.post("/transactions/", json=transaction_data)
    assert response.status_code == status.HTTP_201_CREATED


def test_update_transaction():
    updated_data = {
        "title": "Updated Test Transaction",
        "amount": 75.25,
        "type": "expense",
        "category": "Groceries"
    }
    response = client.put("/transactions/123", json=updated_data)
    assert response.status_code == status.HTTP_200_OK


def test_delete_transaction():
    response = client.delete("/transactions/123")
    assert response.status_code == status.HTTP_200_OK

    # remove the remaining dummy data
    db = SessionLocal()
    db.query(Transaction).filter(Transaction.owner_id == 123).delete()
    db.query(User).filter(User.id == 123).delete()
    db.commit()
    db.close()
