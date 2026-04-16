from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("🚀 Iniciando auditores-digitales-backend...")
    create_tables()
    print("✅ Tablas listas en PostgreSQL")
    yield
    print("🛑 Cerrando servidor...")


app = FastAPI(
    title="Auditores Digitales API",
    description="Backend para auditores autónomos genéricos de ASAI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "proyecto": "Auditores Digitales ASAI",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }
