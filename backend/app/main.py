from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import init_db
from app.api import consultation, admin

# Initialize FastAPI app
app = FastAPI(
    title="Visa Expert System API",
    description="オブジェクト指向エキスパートシステム - ビザ選定診断",
    version="4.1.1",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(consultation.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")


@app.get("/")
async def root():
    return {
        "message": "Visa Expert System API",
        "version": "4.1.1",
        "documentation": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
