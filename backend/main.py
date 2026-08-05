import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import database, models
from routers import objectives, indicators, milestones, snapshots, export, dashboard

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FONPLATA - Gestión de Indicadores y Objetivos", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(objectives.router)
app.include_router(indicators.router)
app.include_router(milestones.router)
app.include_router(snapshots.router)
app.include_router(export.router)
app.include_router(dashboard.router)

# Serve built React frontend (production only)
DIST_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="vite-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
else:
    @app.get("/")
    def root():
        return {"status": "ok", "app": "FONPLATA Indicadores & Objetivos"}
