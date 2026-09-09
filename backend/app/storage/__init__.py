"""
File storage utilities for configuration files
"""
import os
import uuid
from pathlib import Path
from typing import Optional

# Storage directories
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")
SANITIZED_DIR = os.getenv("SANITIZED_DIR", "./data/sanitized")
NORMALIZED_DIR = os.getenv("NORMALIZED_DIR", "./data/normalized")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./data/reports")

# Create directories if they don't exist
for directory in [UPLOAD_DIR, SANITIZED_DIR, NORMALIZED_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)


def generate_config_id() -> str:
    """Generate unique configuration ID like CFG-000001"""
    # In production, this would query database for the last ID
    # For prototype, use timestamp-based approach
    import time
    timestamp = int(time.time() * 1000) % 1000000
    return f"CFG-{timestamp:06d}"


def generate_audit_id() -> str:
    """Generate unique audit ID like AUD-000001"""
    import time
    timestamp = int(time.time() * 1000) % 1000000
    return f"AUD-{timestamp:06d}"


def generate_finding_id() -> str:
    """Generate unique finding ID like FND-000001"""
    import uuid
    # Use last 6 characters of UUID for uniqueness
    unique_suffix = str(uuid.uuid4())[:8].replace('-', '').upper()
    return f"FND-{unique_suffix}"


def generate_mapping_id() -> str:
    """Generate unique mapping ID like MAP-000001"""
    import time
    timestamp = int(time.time() * 1000) % 1000000
    return f"MAP-{timestamp:06d}"


def save_uploaded_file(file_content: bytes, original_filename: str) -> tuple[str, str]:
    """
    Save uploaded file with secure filename
    Returns: (internal_filename, full_path)
    """
    # Generate secure filename
    file_ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    internal_filename = f"{unique_id}{file_ext}"
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, internal_filename)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return internal_filename, file_path


def save_sanitized_file(content: str, original_filename: str) -> str:
    """Save sanitized configuration file"""
    file_ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    internal_filename = f"{unique_id}_sanitized{file_ext}"
    
    file_path = os.path.join(SANITIZED_DIR, internal_filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def read_file(file_path: str) -> str:
    """Read file content as text"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def validate_filename(filename: str) -> bool:
    """Validate uploaded filename for security"""
    # Prevent path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check allowed extensions
    allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", ".cfg,.conf,.txt,.json").split(',')
    file_ext = Path(filename).suffix.lower()
    
    return file_ext in allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """Validate file size"""
    max_size = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
    return file_size <= max_size
