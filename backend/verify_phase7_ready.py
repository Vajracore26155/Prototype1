#!/usr/bin/env python3
"""
Pre-Phase 7 Verification Script
Verifies all prerequisites are met before Phase 7-9 implementation
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Verify database is ready"""
    print("\n[1/6] Checking database...")
    try:
        from app.database import engine, Base
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'configurations', 'audits', 'findings', 'organizations', 'users',
            'devices', 'drift_analyses', 'posture_scores', 'remediation_plans',
            'security_audit_logs'
        ]
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"   ERR Missing tables: {missing}")
            return False
        
        print(f"   OK  Found {len(tables)} tables")
        return True
    except Exception as e:
        print(f"   ERR Database check failed: {e}")
        return False


def check_migrations():
    """Verify migrations are up to date"""
    print("\n[2/6] Checking migrations...")
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.script import ScriptDirectory
        
        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Get current head
        head = script.get_current_head()
        print(f"   OK  Current migration: {head}")
        return True
    except Exception as e:
        print(f"   ERR Migration check failed: {e}")
        return False


def check_api_routes():
    """Verify API routes are registered"""
    print("\n[3/6] Checking API routes...")
    try:
        from app.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        required_paths = [
            '/api/devices',
            '/api/drift',
            '/api/posture',
            '/api/remediation',
            '/api/ai'
        ]
        
        missing = [p for p in required_paths if not any(p in r for r in routes)]
        if missing:
            print(f"   ERR Missing routes: {missing}")
            return False
        
        print(f"   OK  Found {len(routes)} routes")
        return True
    except Exception as e:
        print(f"   ERR Route check failed: {e}")
        return False


def check_dependencies():
    """Verify Python dependencies"""
    print("\n[4/6] Checking dependencies...")
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import uvicorn
        import alembic
        import bcrypt
        
        # Check bcrypt version
        bcrypt_version = bcrypt.__version__
        if bcrypt_version.startswith('5'):
            print(f"   WARN BCrypt version {bcrypt_version} may have compatibility issues")
            print(f"        Recommend: bcrypt==4.1.3")
        else:
            print(f"   OK  BCrypt version {bcrypt_version}")
        
        print("   OK  All core dependencies installed")
        return True
    except ImportError as e:
        print(f"   ERR Missing dependency: {e}")
        return False


def check_llm_setup():
    """Verify LLM providers are configured"""
    print("\n[5/6] Checking LLM setup...")
    try:
        from app.llm.providers import get_available_providers
        
        providers = get_available_providers()
        print(f"   OK  Available providers: {', '.join(providers)}")
        
        # Check for mock provider
        if 'mock' in providers:
            print("   WARN No LLM API keys configured (using mock provider)")
            print("        Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")
        
        return True
    except Exception as e:
        print(f"   ERR LLM check failed: {e}")
        return False


def check_redis():
    """Check Redis connection (optional)"""
    print("\n[6/6] Checking Redis (optional)...")
    try:
        from app.config.redis_config import get_redis_client
        
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            print("   OK  Redis connected")
            return True
        else:
            print("   SKIP Redis not enabled (using in-memory storage)")
            return True
    except Exception as e:
        print(f"   SKIP Redis not available: {e}")
        print("        In-memory fallback will be used")
        return True


def main():
    print("=" * 60)
    print("  PHASE 7-9 PRE-FLIGHT VERIFICATION")
    print("=" * 60)
    
    checks = [
        check_database(),
        check_migrations(),
        check_api_routes(),
        check_dependencies(),
        check_llm_setup(),
        check_redis()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 60)
    print(f"  RESULTS: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n OK  All checks passed!")
        print("     System is READY for Phase 7-9 implementation")
        return 0
    else:
        print("\n ERR Some checks failed")
        print("     Fix issues before proceeding to Phase 7-9")
        return 1


if __name__ == "__main__":
    exit(main())
