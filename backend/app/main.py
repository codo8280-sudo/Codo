from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config import settings
from .db import close_pool, open_pool
from .routers import (
    admin_auth,
    admin_ingestion,
    admin_relationships,
    admin_workflow,
    ai,
    health,
    legal,
    relationships,
    search,
    user_account,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_pool()
    yield
    await close_pool()


app = FastAPI(
    title="CODO API",
    version="0.8.0",
    description="Source-first legal information API for Côte d'Ivoire.",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(search.router)
app.include_router(legal.router)
app.include_router(ai.router)
app.include_router(admin_auth.router)
app.include_router(admin_ingestion.router)
app.include_router(admin_workflow.router)
app.include_router(admin_relationships.router)
app.include_router(relationships.router)
app.include_router(user_account.router)


@app.get("/")
async def root() -> dict:
    return {
        "name": "CODO API",
        "version": "0.8.0",
        "principle": "Une question. Une règle. Une source. Une orientation.",
    }
