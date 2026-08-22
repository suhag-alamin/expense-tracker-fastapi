from fastapi import FastAPI
from fastapi.responses import JSONResponse
import models
from database import engine
from router import auth, transaction


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(transaction.router,
                   prefix="/transactions", tags=["transactions"]
                   )


@app.get("/")
def root():
    return JSONResponse(content={"message": "Welcome to the Expense Tracker API!"})
