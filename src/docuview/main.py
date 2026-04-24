from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from docuview.config import settings
from docuview.db import ping as db_ping

app = FastAPI(title="docuview", version="0.1.0")

# В dev-режиме разрешаем CORS с фронта на localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "docuview-api", "env": settings.environment}


@app.get("/health")
def health() -> dict[str, str]:
    try:
        info = db_ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"db not ready: {exc}") from exc
    return {"status": "ok", "db": info["version"]}
