"""
Storage Backend Abstraction - Phase 0.5 Foundation
Supports both filesystem (development) and MinIO (production) storage
"""
import os
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract storage backend interface"""
    
    @abstractmethod
    def save_file(self, file_content: bytes, bucket: str, object_name: str) -> str:
        """Save file and return storage path/URL"""
        pass
    
    @abstractmethod
    def get_file(self, bucket: str, object_name: str) -> bytes:
        """Retrieve file content"""
        pass
    
    @abstractmethod
    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    def get_file_url(self, bucket: str, object_name: str) -> str:
        """Get URL or path to file"""
        pass
    
    @abstractmethod
    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in bucket with optional prefix"""
        pass


class FilesystemStorage(StorageBackend):
    """Filesystem-based storage (development mode)"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"Initialized filesystem storage at {self.base_path}")
    
    def _get_bucket_path(self, bucket: str) -> Path:
        """Get bucket directory path"""
        bucket_path = self.base_path / bucket
        bucket_path.mkdir(exist_ok=True)
        return bucket_path
    
    def save_file(self, file_content: bytes, bucket: str, object_name: str) -> str:
        """Save file to filesystem"""
        bucket_path = self._get_bucket_path(bucket)
        file_path = bucket_path / object_name
        
        # Create subdirectories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path.write_bytes(file_content)
        
        logger.info(f"Saved file to filesystem: {file_path}")
        return str(file_path)
    
    def get_file(self, bucket: str, object_name: str) -> bytes:
        """Read file from filesystem"""
        bucket_path = self._get_bucket_path(bucket)
        file_path = bucket_path / object_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return file_path.read_bytes()
    
    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete file from filesystem"""
        bucket_path = self._get_bucket_path(bucket)
        file_path = bucket_path / object_name
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        return False
    
    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists"""
        bucket_path = self._get_bucket_path(bucket)
        file_path = bucket_path / object_name
        return file_path.exists()
    
    def get_file_url(self, bucket: str, object_name: str) -> str:
        """Get filesystem path"""
        bucket_path = self._get_bucket_path(bucket)
        file_path = bucket_path / object_name
        return str(file_path)
    
    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in bucket"""
        bucket_path = self._get_bucket_path(bucket)
        
        if prefix:
            search_path = bucket_path / prefix
        else:
            search_path = bucket_path
        
        if not search_path.exists():
            return []
        
        files = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(bucket_path)
                files.append(str(relative_path))
        
        return sorted(files)


class MinIOStorage(StorageBackend):
    """MinIO S3-compatible storage (production mode)"""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        try:
            from minio import Minio
            from minio.error import S3Error
        except ImportError:
            raise ImportError("MinIO client not installed. Install with: pip install minio")
        
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.S3Error = S3Error
        logger.info(f"Initialized MinIO storage at {endpoint}")
    
    def _ensure_bucket(self, bucket: str):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"Created bucket: {bucket}")
        except self.S3Error as e:
            logger.error(f"Error ensuring bucket {bucket}: {e}")
            raise
    
    def save_file(self, file_content: bytes, bucket: str, object_name: str) -> str:
        """Save file to MinIO"""
        from io import BytesIO
        
        self._ensure_bucket(bucket)
        
        # Upload file
        self.client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=BytesIO(file_content),
            length=len(file_content)
        )
        
        logger.info(f"Saved file to MinIO: {bucket}/{object_name}")
        return f"s3://{bucket}/{object_name}"
    
    def get_file(self, bucket: str, object_name: str) -> bytes:
        """Retrieve file from MinIO"""
        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except self.S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {bucket}/{object_name}")
            raise
    
    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file from MinIO: {bucket}/{object_name}")
            return True
        except self.S3Error as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists in MinIO"""
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except self.S3Error:
            return False
    
    def get_file_url(self, bucket: str, object_name: str) -> str:
        """Get presigned URL for file"""
        try:
            # Generate presigned URL valid for 7 days
            url = self.client.presigned_get_object(bucket, object_name, expires=timedelta(days=7))
            return url
        except self.S3Error as e:
            logger.error(f"Error generating URL: {e}")
            return f"s3://{bucket}/{object_name}"
    
    def list_files(self, bucket: str, prefix: str = "") -> list:
        """List files in MinIO bucket"""
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except self.S3Error as e:
            logger.error(f"Error listing files: {e}")
            return []


def get_storage_backend() -> StorageBackend:
    """Factory function to get appropriate storage backend based on configuration"""
    use_minio = os.getenv("USE_MINIO", "false").lower() == "true"
    
    if use_minio:
        try:
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
            
            storage = MinIOStorage(endpoint, access_key, secret_key, secure)
            logger.info("Using MinIO storage backend")
            return storage
        except Exception as e:
            logger.warning(f"Failed to initialize MinIO, falling back to filesystem: {e}")
            return FilesystemStorage()
    else:
        base_path = os.getenv("STORAGE_BASE_PATH", "./data")
        logger.info("Using filesystem storage backend")
        return FilesystemStorage(base_path)


def calculate_file_hash(file_content: bytes, algorithm: str = "sha256") -> str:
    """Calculate hash of file content"""
    hasher = hashlib.new(algorithm)
    hasher.update(file_content)
    return hasher.hexdigest()


# Bucket name constants
BUCKET_CONFIGS = "vajra-configs"
BUCKET_REPORTS = "vajra-reports"
BUCKET_ARTIFACTS = "vajra-artifacts"
