"""Playground UI per Laya/Jev locale.

Serve la pagina in ui/ e fa da proxy verso laya-serve (evita CORS).

  Terminale 1:  .\\scripts\\start_laya.ps1
  Terminale 2:  .\\.venv-laya\\Scripts\\python.exe scripts\\lab_ui.py

Apri http://127.0.0.1:8501
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx2 as httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "ui"
LAYA = os.getenv("LAYA_URL", "http://127.0.0.1:8000").rstrip("/")

app = FastAPI(title="Jev lab UI")
app.mount("/static", StaticFiles(directory=UI), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(UI / "index.html")


@app.get("/api/health")
async def health() -> Response:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{LAYA}/health")
    return Response(content=r.content, status_code=r.status_code, media_type="application/json")


@app.post("/api/systemone")
async def systemone(request: Request) -> Response:
    body = await request.body()
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(
            f"{LAYA}/v1/systemone",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    return Response(content=r.content, status_code=r.status_code, media_type="application/json")


if __name__ == "__main__":
    print(f"UI  -> http://127.0.0.1:8501")
    print(f"API -> {LAYA}/v1/systemone")
    uvicorn.run(app, host="127.0.0.1", port=8501, log_level="info")
