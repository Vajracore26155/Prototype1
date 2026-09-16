"""
SIH26155 - AI-Driven Multi-Vendor Network Security Compliance Auditor
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database initialization
from app.database import init_db

# Import API routers
from app.api import upload, audit, findings, learning


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting SIH26155 Network Security Auditor...")
    init_db()
    print("✓ Application ready!")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="SIH26155 Network Security Auditor",
    description="AI-Driven Multi-Vendor Network Security Compliance Auditor",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    from app.core.health import get_health_summary
    return get_health_summary()


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with all service statuses"""
    from app.core.health import HealthChecker
    return HealthChecker.check_all()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SIH26155 Network Security Auditor",
        "version": "1.0.0",
        "status": "running",
        "phase": "0.5 - Foundation"
    }


# Include API routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(audit.router, prefix="/api", tags=["Audit"])
app.include_router(findings.router, prefix="/api", tags=["Findings"])
app.include_router(learning.router, prefix="/api", tags=["Learning"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=port,
        reload=True
    )
