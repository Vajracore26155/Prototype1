"""
Configuration file ingestion and processing
"""
from typing import Tuple, Optional
from dataclasses import dataclass

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


def ingest_configuration(file_path: str, original_filename: str) -> IngestionResult:
    """
    Ingest and process uploaded configuration file
    
    Pipeline:
    1. Read file
    2. Mask secrets
    3. Detect vendor
    4. Save sanitized version
    
    Args:
        file_path: Path to uploaded file
        original_filename: Original filename
        
    Returns:
        IngestionResult with processed data
    """
    try:
        # Step 1: Read configuration
        content = read_file(file_path)
        
        # Step 2: Mask secrets
        masking_result = mask_configuration(content)
        
        # Step 3: Detect vendor (use sanitized content to avoid secret leakage in logs)
        detection_result = detect_vendor(masking_result.sanitized_content)
        
        # Step 4: Save sanitized file
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
        
    except Exception as e:
        return IngestionResult(
            sanitized_path="",
            masking_result=None,
            detection_result=None,
            success=False,
            error_message=str(e)
        )
