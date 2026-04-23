# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.endpoints import admin, chat, evidencia, sessions, webhooks
from app.config import settings
from app.database import SessionLocal, create_tables
from app.utils.logger import log_start, log_stop, log_success
from app.utils.n8n import n8n_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log_start("Iniciando auditores-digitales-backend...")
    create_tables()
    log_success("Tablas listas en PostgreSQL")
    yield
    log_stop("Cerrando servidor...")


app = FastAPI(
    title="Auditores Digitales API",
    description="Backend para auditores autónomos genéricos de ASAI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(sessions.router, prefix="/api/v1")
app.include_router(evidencia.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def root() -> dict:
    return {
        "proyecto": "Auditores Digitales ASAI",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict:
    # Database check
    db_status: str
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    finally:
        db.close()

    # N8N check
    n8n_result = await n8n_client.check_health()
    n8n_info = {
        "status": n8n_result["status"],
        "url": n8n_result["url"],
        "mode": settings.n8n_webhook_mode,
    }
    if "error" in n8n_result:
        n8n_info["error"] = n8n_result["error"]

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "n8n": n8n_info,
        },
    }
