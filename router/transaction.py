from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from models import Transaction
from dependencies import db_dependency, user_dependency
from typing import Optional

router = APIRouter()


class CreateTransaction(BaseModel):
    title: str = Field(..., examples=["Grocery Shopping"])
    amount: float = Field(..., examples=[50.75], gt=0)
    type: str = Field(..., examples=["expense"])
    category: str = Field(..., examples=["Food"])
    date: datetime = Field(..., examples=["2026-08-23"])


class UpdateTransaction(BaseModel):
    title: Optional[str] = Field(None, examples=["Grocery Shopping"])
    amount: Optional[float] = Field(None, examples=[50.75], gt=0)
    type: Optional[str] = Field(None, examples=["expense"])
    category: Optional[str] = Field(None, examples=["Food"])
    date: Optional[datetime] = Field(None, examples=["2026-08-23"])


@router.post("/")
def create_transaction(transaction: CreateTransaction, db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # type must be either 'income' or 'expense'
    if transaction.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400, detail="Invalid transaction type. Must be 'income' or 'expense'.")

    new_transaction = Transaction(
        **transaction.model_dump(), owner_id=user.get("id"))

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return JSONResponse(content={
        "message": "Transaction created successfully",
        "transaction": {
            "id": new_transaction.id,
            "title": new_transaction.title,
            "amount": new_transaction.amount,
            "type": new_transaction.type,
            "category": new_transaction.category,
            "date": new_transaction.date.isoformat(),
            "owner_id": new_transaction.owner_id,
        }
    }, status_code=201)

# get all transactions for the current user


@router.get("/")
def get_transactions(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = user.get("id")
    transactions = db.query(Transaction).filter(
        Transaction.owner_id == user_id).all()

    return JSONResponse(content={
        "message": "Transactions retrieved successfully",
        "transactions": [
            {
                "id": tx.id,
                "title": tx.title,
                "amount": tx.amount,
                "type": tx.type,
                "category": tx.category,
                "date": tx.date.isoformat(),
                "owner_id": tx.owner_id,
            }
            for tx in transactions
        ]
    }, status_code=200)

# get all transactions for the current user with optional filters for type, category, minimum amount, and maximum amount


@router.get("/filter")
def get_filtered_transactions(
    db: db_dependency,
    user: user_dependency,
    type: Optional[str] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None,
):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user.get("id")

    query = db.query(Transaction).filter(Transaction.owner_id == user_id)

    if type is not None:
        query = query.filter(Transaction.type.ilike(type))
    if category is not None:
        query = query.filter(Transaction.category.ilike(category))

    if minimum_amount is not None:
        query = query.filter(Transaction.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(Transaction.amount <= maximum_amount)

    transactions = query.all()

    return JSONResponse(content={
        "message": "Filtered transactions retrieved successfully",
        "transactions": [
            {
                "id": tx.id,
                "title": tx.title,
                "amount": tx.amount,
                "type": tx.type,
                "category": tx.category,
                "date": tx.date.isoformat(),
                "owner_id": tx.owner_id,
            }
            for tx in transactions
        ]
    }, status_code=200)


# get a single transaction by id for the current user
@router.get("/{transaction_id}")
def get_transaction(transaction_id: int, db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = user.get("id")

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).filter(
        Transaction.owner_id == user_id
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404, detail="Transaction not found")

    return JSONResponse(content={
        "message": "Transaction retrieved successfully",
        "transaction": {
            "id": transaction.id,
            "title": transaction.title,
            "amount": transaction.amount,
            "type": transaction.type,
            "category": transaction.category,
            "date": transaction.date.isoformat(),
            "owner_id": transaction.owner_id,
        }
    }, status_code=200)


# update a transaction by id for the current user
@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, updated_transaction: UpdateTransaction, db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = user.get("id")

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).filter(
        Transaction.owner_id == user_id
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404, detail="Transaction not found")

    # type must be either 'income' or 'expense'
    if updated_transaction.type and updated_transaction.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400, detail="Invalid transaction type. Must be 'income' or 'expense'.")

    updated_data = updated_transaction.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return JSONResponse(content={
        "message": "Transaction updated successfully",
        "transaction": {
            "id": transaction.id,
            "title": transaction.title,
            "amount": transaction.amount,
            "type": transaction.type,
            "category": transaction.category,
            "date": transaction.date.isoformat(),
            "owner_id": transaction.owner_id,
        }
    }, status_code=200)


# delete a transaction by id for the current user
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_id = user.get("id")

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).filter(
        Transaction.owner_id == user_id
    ).first()

    if transaction is None:
        raise HTTPException(
            status_code=404, detail="Transaction not found")

    db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).filter(
        Transaction.owner_id == user_id
    ).delete()

    db.commit()

    return JSONResponse(content={"message": "Transaction deleted successfully"}, status_code=200)
