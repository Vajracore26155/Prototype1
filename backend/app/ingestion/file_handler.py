"""
Configuration file ingestion and processing
"""
import zipfile
from io import BytesIO
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from app.security import mask_configuration, MaskingResult
from app.detection import detect_vendor, DetectionResult
from app.storage import read_file, save_sanitized_file


@dataclass
class IngestionResult:
    """Result of configuration ingestion"""
    sanitized_path: str
    masking_result: MaskingResult
    detection_result: DetectionResult
    success: bool
    error_message: Optional[str] = None


class FileSecurityError(Exception):
    """Raised when file fails security validation"""
    pass


def validate_file_security(file_content: bytes, filename: str) -> None:
    """
    Validate file security before processing
    
    Checks:
    - Magic bytes match file extension
    - No path traversal in filename
    - No ZIP bombs
    - File size limits
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        
    Raises:
        FileSecurityError: If validation fails
    """
    # Check for path traversal
    if ".." in filename or filename.startswith("/") or "\\" in filename:
        raise FileSecurityError(f"Invalid filename (path traversal): {filename}")
    
    # Check file size (max 50MB uncompressed)
    if len(file_content) > 50 * 1024 * 1024:
        raise FileSecurityError("File too large (max 50MB)")
    
    # Check magic bytes (if python-magic is available)
    if MAGIC_AVAILABLE:
        try:
            mime = magic.from_buffer(file_content, mime=True)
            
            # Allow text files and ZIP archives
            allowed_mimes = [
                'text/plain',
                'text/x-shellscript',
                'application/octet-stream',  # Generic binary, common for configs
                'application/x-empty',  # Empty file
                'application/zip',
                'application/x-zip-compressed'
            ]
            
            if mime not in allowed_mimes:
                raise FileSecurityError(f"Invalid file type: {mime}")
            
            # Special handling for ZIP files - check for ZIP bombs
            if mime in ['application/zip', 'application/x-zip-compressed']:
                validate_zip_file(file_content)
                
        except Exception as e:
            # If magic fails, continue with other validations
            pass
    
    # Check for null bytes (can indicate binary/malicious content)
    if b'\x00' in file_content and not filename.endswith('.zip'):
        raise FileSecurityError("File contains null bytes (possible binary/malicious content)")


def validate_zip_file(zip_content: bytes) -> None:
    """
    Validate ZIP file to prevent ZIP bombs
    
    Args:
        zip_content: Raw ZIP file bytes
        
    Raises:
        FileSecurityError: If ZIP is malicious
    """
    try:
        with zipfile.ZipFile(BytesIO(zip_content), 'r') as zip_ref:
            # Check compression ratio
            total_compressed = 0
            total_uncompressed = 0
            
            for info in zip_ref.infolist():
                total_compressed += info.compress_size
                total_uncompressed += info.file_size
                
                # Check individual file size (max 50MB uncompressed)
                if info.file_size > 50 * 1024 * 1024:
                    raise FileSecurityError(f"ZIP contains file too large: {info.filename}")
            
            # Check total uncompressed size (max 500MB)
            if total_uncompressed > 500 * 1024 * 1024:
                raise FileSecurityError("ZIP uncompressed size too large (max 500MB)")
            
            # Check compression ratio (max 100:1 to prevent bombs)
            if total_compressed > 0:
                ratio = total_uncompressed / total_compressed
                if ratio > 100:
                    raise FileSecurityError(f"Suspicious compression ratio: {ratio:.1f}:1 (possible ZIP bomb)")
            
            # Check for path traversal in ZIP entries
            for info in zip_ref.infolist():
                if ".." in info.filename or info.filename.startswith("/"):
                    raise FileSecurityError(f"ZIP contains path traversal: {info.filename}")
    
    except zipfile.BadZipFile:
        raise FileSecurityError("Invalid or corrupted ZIP file")


def ingest_configuration(file_path: str, original_filename: str) -> IngestionResult:
    """
    Ingest and process uploaded configuration file
    
    Pipeline:
    1. Read file
    2. Validate security
    3. Mask secrets
    4. Detect vendor
    5. Save sanitized version
    
    Args:
        file_path: Path to uploaded file
        original_filename: Original filename
        
    Returns:
        IngestionResult with processed data
    """
    try:
        # Step 1: Read configuration
        content = read_file(file_path)
        
        # Step 2: Validate file security
        validate_file_security(content.encode('utf-8'), original_filename)
        
        # Step 3: Mask secrets
        masking_result = mask_configuration(content)
        
        # Step 4: Detect vendor (use sanitized content to avoid secret leakage in logs)
        detection_result = detect_vendor(masking_result.sanitized_content)
        
        # Step 5: Save sanitized file
        sanitized_path = save_sanitized_file(
            masking_result.sanitized_content,
            original_filename
        )
        
        return IngestionResult(
            sanitized_path=sanitized_path,
            masking_result=masking_result,
            detection_result=detection_result,
            success=True
        )
        
    except FileSecurityError as e:
        return IngestionResult(
            sanitized_path="",
            masking_result=None,
            detection_result=None,
            success=False,
            error_message=f"Security validation failed: {str(e)}"
        )
    except Exception as e:
        return IngestionResult(
            sanitized_path="",
            masking_result=None,
            detection_result=None,
            success=False,
            error_message=str(e)
        )


def process_configuration_file(file_content: bytes, filename: str, organization_id: int, uploaded_by: str):
    """
    Process configuration file bytes and create database record
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
        organization_id: Organization ID
        uploaded_by: Email of uploader
        
    Returns:
        Configuration: Database record
    """
    from app.database import SessionLocal, Configuration
    from datetime import datetime
    import hashlib
    
    # Validate security
    validate_file_security(file_content, filename)
    
    # Decode content
    content = file_content.decode('utf-8', errors='ignore')
    
    # Mask secrets
    masking_result = mask_configuration(content)
    
    # Detect vendor
    from app.detection import detect_vendor
    vendor, confidence = detect_vendor(masking_result.sanitized_content)
    
    # Calculate hash
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Create database record
    db = SessionLocal()
    try:
        config = Configuration(
            original_filename=filename,
            sanitized_content=masking_result.sanitized_content,
            vendor=vendor,
            vendor_confidence=confidence,
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            file_hash=file_hash,
            file_size=len(file_content),
            created_at=datetime.utcnow()
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return config
    finally:
        db.close()

