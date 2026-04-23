import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.services.auth_service import seed_initial_data
from app.routers import auth, products, sales, employees, dashboard, reports, company


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de Administración para PyMEs Chilenas",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

cors_origins = settings.CORS_ORIGINS
allow_all = cors_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.railway\.app" if allow_all else None,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(company.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if settings.FRONTEND_BUILD_DIR and os.path.isdir(settings.FRONTEND_BUILD_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(settings.FRONTEND_BUILD_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        index_path = os.path.join(settings.FRONTEND_BUILD_DIR, "index.html")
        return FileResponse(index_path)
