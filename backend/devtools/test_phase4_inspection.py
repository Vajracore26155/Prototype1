"""
Phase 4.2 Deep Inspection Test
Verify current system state before Phase 4 implementation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print('=' * 60)
print('VAJRA CORE PHASE 4.2 DEEP INSPECTION')
print('=' * 60)
print()

# Test 1: Database
print('[1] Database Status')
try:
    from app.database import init_db, SessionLocal
    init_db()
    db = SessionLocal()
    from app.database.models import Configuration, Audit, Finding, LearnedMapping
    config_count = db.query(Configuration).count()
    audit_count = db.query(Audit).count()
    finding_count = db.query(Finding).count()
    mapping_count = db.query(LearnedMapping).count()
    print(f'  Database: OPERATIONAL')
    print(f'  Configurations: {config_count}')
    print(f'  Audits: {audit_count}')
    print(f'  Findings: {finding_count}')
    print(f'  Learned Mappings: {mapping_count}')
    db.close()
except Exception as e:
    print(f'  Database: ERROR - {e}')

print()

# Test 2: Storage
print('[2] Storage Status')
try:
    from app.storage import UPLOAD_DIR, SANITIZED_DIR
    import os
    upload_exists = os.path.exists(UPLOAD_DIR)
    sanitized_exists = os.path.exists(SANITIZED_DIR)
    print(f'  Upload Dir: {"EXISTS" if upload_exists else "MISSING"}')
    print(f'  Sanitized Dir: {"EXISTS" if sanitized_exists else "MISSING"}')
    if upload_exists:
        file_count = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
        print(f'  Uploaded Files: {file_count}')
except Exception as e:
    print(f'  Storage: ERROR - {e}')

print()

# Test 3: Parsers
print('[3] Parser Registry')
try:
    from app.parsers import get_parser
    vendors = ['Cisco', 'Fortinet', 'Palo Alto', 'Juniper', 'Unknown']
    for vendor in vendors:
        try:
            parser = get_parser(vendor)
            print(f'  {vendor}: {parser.__class__.__name__}')
        except Exception as ve:
            print(f'  {vendor}: NOT REGISTERED ({ve})')
except Exception as e:
    print(f'  Parsers: ERROR - {e}')

print()

# Test 4: Frameworks
print('[4] Framework Engine')
try:
    from app.compliance.framework_engine import MultiFrameworkEngine, FrameworkType
    engine = MultiFrameworkEngine()
    print(f'  Engine: LOADED')
    frameworks = [f.value for f in FrameworkType]
    print(f'  Frameworks: {frameworks}')
    print(f'  Total Controls: {len(engine.controls)}')
except Exception as e:
    print(f'  Frameworks: ERROR - {e}')

print()

# Test 5: AI
print('[5] AI Components')
try:
    from app.adaptive.human_in_loop import HumanInLoopEngine
    ai_engine = HumanInLoopEngine()
    print(f'  HumanInLoopEngine: OPERATIONAL')
    print(f'  Confidence Threshold: {ai_engine.confidence_threshold}')
except Exception as e:
    print(f'  AI: ERROR - {e}')

print()

# Test 6: Environment
print('[6] Environment Configuration')
from dotenv import load_dotenv
load_dotenv()
print(f'  USE_POSTGRES: {os.getenv("USE_POSTGRES", "not set")}')
print(f'  USE_MINIO: {os.getenv("USE_MINIO", "not set")}')
print(f'  FEATURE_AUTHENTICATION: {os.getenv("FEATURE_AUTHENTICATION", "not set")}')
print(f'  FEATURE_ASYNC_PROCESSING: {os.getenv("FEATURE_ASYNC_PROCESSING", "not set")}')
print(f'  KEYCLOAK_ENABLED: {os.getenv("KEYCLOAK_ENABLED", "not set")}')
print(f'  DATABASE_URL: {os.getenv("DATABASE_URL", "not set")[:50]}...')

print()

# Test 7: Authentication
print('[7] Authentication Status')
try:
    # Check if any auth dependencies exist
    auth_exists = os.getenv('FEATURE_AUTHENTICATION', 'false').lower() == 'true'
    print(f'  Feature Flag: {auth_exists}')
    print(f'  Status: {"ENABLED" if auth_exists else "DISABLED"}')
    print(f'  Type: NO USER AUTHENTICATION IMPLEMENTED')
except Exception as e:
    print(f'  Authentication: ERROR - {e}')

print()

# Test 8: Security Features
print('[8] Security Features')
try:
    from app.security.masking import mask_sensitive_data
    test_data = "password secret123"
    masked = mask_sensitive_data(test_data)
    print(f'  Secret Masking: {"OPERATIONAL" if masked != test_data else "NOT WORKING"}')
except Exception as e:
    print(f'  Security: ERROR - {e}')

print()

# Test 9: API Endpoints
print('[9] API Endpoints')
try:
    from app.main import app
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    print(f'  Total Routes: {len(routes)}')
    api_routes = [r for r in routes if r.startswith('/api')]
    print(f'  API Routes: {len(api_routes)}')
    print('  Key Endpoints:')
    for route in ['/api/upload', '/api/audit', '/api/findings', '/api/frameworks', '/api/learning']:
        if any(route in r for r in routes):
            print(f'    {route}: EXISTS')
except Exception as e:
    print(f'  API: ERROR - {e}')

print()

# Test 10: Docker/Infrastructure
print('[10] Infrastructure Status')
docker_compose_exists = os.path.exists('docker-compose.yml')
print(f'  Docker Compose: {"EXISTS" if docker_compose_exists else "MISSING"}')
print(f'  PostgreSQL: NOT VERIFIED')
print(f'  Redis: NOT VERIFIED')
print(f'  MinIO: NOT VERIFIED')
print(f'  Celery Workers: NOT VERIFIED')

print()
print('=' * 60)
print('INSPECTION COMPLETE')
print('=' * 60)
print()
print('KEY FINDINGS:')
print('1. NO USER AUTHENTICATION - APIs are public')
print('2. Database: SQLite (development mode)')
print('3. Storage: Filesystem (not S3/MinIO)')
print('4. Async Processing: DISABLED')
print('5. Multi-tenancy: NOT IMPLEMENTED')
print('6. RBAC: NOT IMPLEMENTED')
print()
print('Ready for Phase 4 implementation planning.')
