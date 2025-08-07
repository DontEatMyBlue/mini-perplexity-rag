# main.py
from fastapi import FastAPI
from routes import question

app = FastAPI()

app.include_router(question.router, prefix="/api")
