"""
Health Check System - Phase 0.5 Foundation
Monitors all infrastructure dependencies
"""
import os
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """Centralized health check for all infrastructure components"""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from app.database.database import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            # Get database type
            db_url = str(engine.url)
            if "postgresql" in db_url:
                db_type = "PostgreSQL"
            elif "sqlite" in db_url:
                db_type = "SQLite"
            else:
                db_type = "Unknown"
            
            return {
                "status": "healthy",
                "type": db_type,
                "message": "Database connection successful"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "type": "Unknown",
                "message": str(e)
            }
    
    @staticmethod
    def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity"""
        redis_enabled = os.getenv("FEATURE_ASYNC_PROCESSING", "false").lower() == "true"
        
        if not redis_enabled:
            return {
                "status": "disabled",
                "message": "Redis not configured (FEATURE_ASYNC_PROCESSING=false)"
            }
        
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://:vajra_redis_password@localhost:6379/0")
            
            # Parse Redis URL
            client = redis.from_url(redis_url)
            client.ping()
            
            # Get info
            info = client.info()
            
            return {
                "status": "healthy",
                "version": info.get("redis_version", "unknown"),
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "message": "Redis connection successful"
            }
        except ImportError:
            return {
                "status": "unavailable",
                "message": "Redis client not installed"
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e)
            }
    
    @staticmethod
    def check_minio() -> Dict[str, Any]:
        """Check MinIO connectivity"""
        use_minio = os.getenv("USE_MINIO", "false").lower() == "true"
        
        if not use_minio:
            return {
                "status": "disabled",
                "message": "MinIO not configured (USE_MINIO=false)"
            }
        
        try:
            from minio import Minio
            
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
            
            client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            
            # List buckets as health check
            buckets = list(client.list_buckets())
            
            return {
                "status": "healthy",
                "endpoint": endpoint,
                "buckets_count": len(buckets),
                "buckets": [b.name for b in buckets],
                "message": "MinIO connection successful"
            }
        except ImportError:
            return {
                "status": "unavailable",
                "message": "MinIO client not installed"
            }
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e)
            }
    
    @staticmethod
    def check_storage() -> Dict[str, Any]:
        """Check storage backend"""
        try:
            from app.storage.storage_backend import get_storage_backend
            
            storage = get_storage_backend()
            storage_type = type(storage).__name__
            
            return {
                "status": "healthy",
                "type": storage_type,
                "message": f"Using {storage_type}"
            }
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                "status": "unhealthy",
                "type": "Unknown",
                "message": str(e)
            }
    
    @staticmethod
    def check_celery() -> Dict[str, Any]:
        """Check Celery worker status"""
        celery_enabled = os.getenv("FEATURE_ASYNC_PROCESSING", "false").lower() == "true"
        
        if not celery_enabled:
            return {
                "status": "disabled",
                "message": "Celery not configured (FEATURE_ASYNC_PROCESSING=false)"
            }
        
        try:
            from celery import Celery
            
            broker_url = os.getenv("CELERY_BROKER_URL", "redis://:vajra_redis_password@localhost:6379/0")
            
            app = Celery(broker=broker_url)
            
            # Inspect active workers
            inspect = app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                worker_count = len(stats)
                return {
                    "status": "healthy",
                    "workers": worker_count,
                    "worker_names": list(stats.keys()),
                    "message": f"{worker_count} worker(s) active"
                }
            else:
                return {
                    "status": "unhealthy",
                    "workers": 0,
                    "message": "No workers available"
                }
        except ImportError:
            return {
                "status": "unavailable",
                "message": "Celery not installed"
            }
        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e)
            }
    
    @staticmethod
    def check_ai_model() -> Dict[str, Any]:
        """Check AI model availability"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = os.getenv("AI_MODEL", "all-MiniLM-L6-v2")
            
            # Try to load model (cached if already loaded)
            model = SentenceTransformer(model_name)
            
            return {
                "status": "healthy",
                "model": model_name,
                "embedding_dimension": model.get_sentence_embedding_dimension(),
                "message": "AI model loaded successfully"
            }
        except ImportError:
            return {
                "status": "unavailable",
                "message": "sentence-transformers not installed"
            }
        except Exception as e:
            logger.error(f"AI model health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e)
            }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system configuration information"""
        return {
            "environment": os.getenv("APP_ENV", "development"),
            "version": os.getenv("APP_VERSION", "0.5.0"),
            "features": {
                "postgres": os.getenv("USE_POSTGRES", "false").lower() == "true",
                "minio": os.getenv("USE_MINIO", "false").lower() == "true",
                "async_processing": os.getenv("FEATURE_ASYNC_PROCESSING", "false").lower() == "true",
                "authentication": os.getenv("FEATURE_AUTHENTICATION", "false").lower() == "true",
                "ai_learning": os.getenv("FEATURE_AI_LEARNING", "true").lower() == "true",
                "pdf_reports": os.getenv("FEATURE_PDF_REPORTS", "true").lower() == "true",
            }
        }
    
    @classmethod
    def check_all(cls) -> Dict[str, Any]:
        """Perform all health checks"""
        timestamp = datetime.utcnow().isoformat()
        
        # Core checks (always performed)
        database = cls.check_database()
        storage = cls.check_storage()
        ai_model = cls.check_ai_model()
        
        # Optional checks (based on configuration)
        redis = cls.check_redis()
        minio = cls.check_minio()
        celery = cls.check_celery()
        
        # System info
        system = cls.get_system_info()
        
        # Determine overall status
        critical_services = [database, storage]
        unhealthy_critical = any(s["status"] == "unhealthy" for s in critical_services)
        
        if unhealthy_critical:
            overall_status = "unhealthy"
        elif all(s["status"] in ["healthy", "disabled", "unavailable"] for s in critical_services):
            overall_status = "healthy"
        else:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": timestamp,
            "system": system,
            "services": {
                "database": database,
                "storage": storage,
                "redis": redis,
                "minio": minio,
                "celery": celery,
                "ai_model": ai_model
            }
        }


def get_health_summary() -> Dict[str, str]:
    """Get a simple health summary for quick checks"""
    try:
        results = HealthChecker.check_all()
        return {
            "status": results["status"],
            "timestamp": results["timestamp"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
