"""
SIH26155 - AI-Driven Multi-Vendor Network Security Compliance Auditor
Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import database initialization
from app.database import init_db, SessionLocal, Organization, User
from app.auth.security import get_password_hash
from app.auth.permissions import Role

def ensure_default_organization():
    """Ensure the default organization exists for vendor registration."""
    db = SessionLocal()

    try:
        # Vendor registration currently defaults to organization_id=1.
        organization = db.query(Organization).filter(
            Organization.id == 1
        ).first()

        if organization:
            print(
                f"[STARTUP] Default organization already exists: "
                f"{organization.org_id}"
            )
            return

        organization = Organization(
            org_id="ORG-000001",
            name="Admin Organization",
            slug="admin-org",
            status="ACTIVE"
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        print(
            f"[SUCCESS] Default organization created: "
            f"{organization.org_id} (ID: {organization.id})"
        )

    except Exception as e:
        db.rollback()
        print(f"[WARNING] Default organization initialization failed: {e}")

    finally:
        db.close()

def ensure_default_admin():
    """Ensure the default SUPER_ADMIN user exists."""
    db = SessionLocal()

    try:
        admin_email = os.getenv(
            "DEFAULT_ADMIN_EMAIL",
            "admin@tatva.security"
        )

        admin_password = os.getenv(
            "DEFAULT_ADMIN_PASSWORD"
        )

        if not admin_password:
            print(
                "[WARNING] DEFAULT_ADMIN_PASSWORD is not configured. "
                "Skipping default admin creation."
            )
            return

        # Check whether admin already exists
        admin = db.query(User).filter(
            User.email == admin_email
        ).first()

        if admin:
            print(
                f"[STARTUP] Default admin already exists: "
                f"{admin.email} (role={admin.role})"
            )
            return

        # Make sure organization ID 1 exists
        organization = db.query(Organization).filter(
            Organization.id == 1
        ).first()

        if not organization:
            print(
                "[WARNING] Cannot create default admin because "
                "organization ID 1 does not exist."
            )
            return

        admin = User(
            user_id="USR-000001",
            email=admin_email,
            username="admin",
            hashed_password=get_password_hash(admin_password),
            full_name="System Administrator",
            organization_id=organization.id,
            role=Role.SUPER_ADMIN.value,
            is_active=True,
            is_verified=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(
            f"[SUCCESS] Default admin created: "
            f"{admin.email} "
            f"(ID={admin.id}, role={admin.role})"
        )

    except Exception as e:
        db.rollback()
        print(
            f"[WARNING] Default admin initialization failed: {e}"
        )

    finally:
        db.close()

# Import API routers
from app.api import upload, audit, findings, learning
from app.api import frameworks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""

    # Startup
    print("[STARTUP] Starting SIH26155 Network Security Auditor...")

    try:
        # Create database tables
        init_db()

        # Ensure required default organization exists
        ensure_default_organization()
        ensure_default_admin()

    except Exception as e:
        print(f"[WARNING] Database initialization error: {e}")

    print("[STARTUP] Application ready!")

    yield

    # Shutdown
    print("[SHUTDOWN] Shutting down...")


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

# Phase 4: Security and observability middleware
from app.middleware import RequestIDMiddleware, LoggingMiddleware, RateLimitMiddleware

# Request ID tracking (first, so it's available to other middleware)
app.add_middleware(RequestIDMiddleware)

# Structured logging
app.add_middleware(LoggingMiddleware)

# Rate limiting (set to False in .env to disable during testing)
if os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true":
    requests_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)


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

# Phase 0: Bulk Upload
from app.api import bulk_upload
app.include_router(bulk_upload.router, prefix="/api", tags=["Bulk Upload"])

# Phase 0: Deviation/Comparison
from app.api import comparison
app.include_router(comparison.router, prefix="/api", tags=["Comparison"])

# Phase 2: Multi-Framework Compliance
app.include_router(frameworks.router, tags=["Multi-Framework Compliance"])

# Phase 4: Authentication
from app.api import auth
app.include_router(auth.router, tags=["Authentication"])

# Phase 4: Job Status
from app.api import jobs
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])

# Phase 5: Device Management
from app.api import devices
app.include_router(devices.router, prefix="/api", tags=["Devices"])

# Phase 5: Drift Detection
from app.api import drift
app.include_router(drift.router, prefix="/api", tags=["Drift Detection"])

# Phase 5: Posture Scoring
from app.api import posture
app.include_router(posture.router, prefix="/api", tags=["Posture Scoring"])

# Phase 6: AI/LLM Integration
from app.api import ai
app.include_router(ai.router, prefix="/api", tags=["AI & LLM"])

# Phase 5: Remediation Management
from app.api import remediation
app.include_router(remediation.router, prefix="/api", tags=["Remediation"])

# Phase 7: Configuration Version Management
from app.api import config_versions
app.include_router(config_versions.router, prefix="/api", tags=["Configuration Versions"])

# Phase 7: Configuration Monitoring
from app.api import monitoring
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring"])

# Phase 7: Webhooks
from app.api import webhooks
app.include_router(webhooks.router, prefix="/api", tags=["Webhooks"])

# Phase 7.3: Advanced Reporting
from app.api import reports
app.include_router(reports.router, prefix="/api", tags=["Reports"])

# Phase 7.4: Knowledge Graph
from app.api import knowledge_graph
app.include_router(knowledge_graph.router, prefix="/api", tags=["Knowledge Graph"])

# Phase 7.5: Advanced Search
from app.api import search
app.include_router(search.router, prefix="/api", tags=["Search"])

# Phase 11: System Administration
from app.api import admin
app.include_router(admin.router, prefix="/api", tags=["System Administration"])

# Phase 10: Vendor Management System
from app.api import vendor_auth, vendor_upload, vendor_profile, enhanced_vendor_upload, vendor_analytics
app.include_router(vendor_auth.router, prefix="/api", tags=["Vendor Auth"])
app.include_router(vendor_upload.router, prefix="/api", tags=["Vendor Upload"])
app.include_router(enhanced_vendor_upload.router, prefix="/api", tags=["Enhanced Vendor Upload"])
app.include_router(vendor_analytics.router, prefix="/api", tags=["Vendor Analytics"])
app.include_router(vendor_profile.router, prefix="/api", tags=["Vendor Profile"])

# Phase 12: Mobile QR Session
from app.api import mobile
app.include_router(mobile.router, prefix="/api", tags=["Mobile"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=port,
        reload=True
    )
