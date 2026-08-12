from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://fraudshield-ai-1-eu8l.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Neeche tumhare existing routers/imports exactly waise hi rahenge.
# Example:
# app.include_router(auth.router)
# app.include_router(transaction.router)
# app.include_router(dashboard.router)