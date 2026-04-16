from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_tables
from backend.routes import chat as chat_router
from backend.routes import evidencia as evidencia_router
from backend.routes import sessions as sessions_router


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


app.include_router(sessions_router.router)
app.include_router(evidencia_router.router)
app.include_router(chat_router.router)


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
