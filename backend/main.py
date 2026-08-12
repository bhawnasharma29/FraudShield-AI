from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from auth import router as auth_router
from transaction import router as transaction_router
import dashboard


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="FraudShield-AI",
    version="1.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://fraudshield-ai-1-eu8l.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# INCLUDE AUTH ROUTER
# ============================================================

app.include_router(
    auth_router
)


# ============================================================
# INCLUDE TRANSACTION ROUTER
# ============================================================

app.include_router(
    transaction_router
)


# ============================================================
# INCLUDE DASHBOARD ROUTER
# ============================================================

app.include_router(
    dashboard.router
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "FraudShield-AI Backend Running"
    }