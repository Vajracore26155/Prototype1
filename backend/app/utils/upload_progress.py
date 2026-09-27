"""
Upload Progress Tracking System
Provides real-time progress updates for vendor uploads with detailed status information
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class UploadStage(Enum):
    """Upload processing stages"""
    QUEUED = "queued"
    VALIDATING = "validating"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    INGESTING = "ingesting"
    VENDOR_DETECTION = "vendor_detection"
    AUDITING = "auditing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadStatus(Enum):
    """Overall upload status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class FileProgress:
    """Progress tracking for individual file"""
    file_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    file_size: int = 0
    current_stage: UploadStage = UploadStage.QUEUED
    status: UploadStatus = UploadStatus.PENDING
    progress_percentage: float = 0.0
    bytes_processed: int = 0
    
    # Stage timing
    stage_start_time: Optional[datetime] = None
    total_start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    
    # Results
    config_id: Optional[str] = None
    audit_id: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Validation results
    validation_result: Optional[Dict] = None
    
    # Processing details
    vendor_detected: Optional[str] = None
    vendor_confidence: Optional[float] = None
    compliance_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "file_size": self.file_size,
            "current_stage": self.current_stage.value,
            "status": self.status.value,
            "progress_percentage": round(self.progress_percentage, 1),
            "bytes_processed": self.bytes_processed,
            "stage_start_time": self.stage_start_time.isoformat() if self.stage_start_time else None,
            "total_start_time": self.total_start_time.isoformat() if self.total_start_time else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "config_id": self.config_id,
            "audit_id": self.audit_id,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "validation_result": self.validation_result,
            "vendor_detected": self.vendor_detected,
            "vendor_confidence": self.vendor_confidence,
            "compliance_score": self.compliance_score,
            "duration_seconds": self._calculate_duration()
        }
    
    def _calculate_duration(self) -> Optional[float]:
        """Calculate processing duration in seconds"""
        if not self.total_start_time:
            return None
        
        end_time = self.completion_time or datetime.utcnow()
        return (end_time - self.total_start_time).total_seconds()

@dataclass
class UploadSession:
    """Upload session tracking multiple files"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vendor_id: str = ""
    upload_type: str = "single"  # "single" or "bulk"
    total_files: int = 0
    files: Dict[str, FileProgress] = field(default_factory=dict)
    
    session_start_time: datetime = field(default_factory=datetime.utcnow)
    session_end_time: Optional[datetime] = None
    
    overall_status: UploadStatus = UploadStatus.PENDING
    
    def add_file(self, filename: str, file_size: int) -> FileProgress:
        """Add file to upload session"""
        file_progress = FileProgress(
            filename=filename,
            file_size=file_size,
            total_start_time=datetime.utcnow()
        )
        self.files[file_progress.file_id] = file_progress
        return file_progress
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Calculate overall session progress"""
        if not self.files:
            return {
                "session_id": self.session_id,
                "overall_progress": 0.0,
                "status": self.overall_status.value,
                "files_completed": 0,
                "files_failed": 0,
                "files_in_progress": 0,
                "total_files": self.total_files
            }
        
        files_completed = sum(1 for f in self.files.values() if f.status == UploadStatus.SUCCESS)
        files_failed = sum(1 for f in self.files.values() if f.status == UploadStatus.FAILED)
        files_in_progress = sum(1 for f in self.files.values() if f.status == UploadStatus.IN_PROGRESS)
        
        # Calculate weighted progress
        total_progress = sum(f.progress_percentage for f in self.files.values())
        overall_progress = total_progress / len(self.files) if self.files else 0.0
        
        # Determine overall status
        if files_failed > 0 and files_completed + files_failed == len(self.files):
            if files_completed > 0:
                self.overall_status = UploadStatus.SUCCESS  # Partial success
            else:
                self.overall_status = UploadStatus.FAILED
        elif files_completed == len(self.files):
            self.overall_status = UploadStatus.SUCCESS
            if not self.session_end_time:
                self.session_end_time = datetime.utcnow()
        elif files_in_progress > 0 or overall_progress > 0:
            self.overall_status = UploadStatus.IN_PROGRESS
        
        return {
            "session_id": self.session_id,
            "overall_progress": round(overall_progress, 1),
            "status": self.overall_status.value,
            "files_completed": files_completed,
            "files_failed": files_failed,
            "files_in_progress": files_in_progress,
            "total_files": len(self.files),
            "duration_seconds": self._calculate_session_duration(),
            "files": [f.to_dict() for f in self.files.values()]
        }
    
    def _calculate_session_duration(self) -> float:
        """Calculate session duration in seconds"""
        end_time = self.session_end_time or datetime.utcnow()
        return (end_time - self.session_start_time).total_seconds()

class UploadProgressTracker:
    """Centralized upload progress tracking"""
    
    def __init__(self):
        self.sessions: Dict[str, UploadSession] = {}
        self.cleanup_interval = timedelta(hours=2)  # Clean up old sessions after 2 hours
        
        # Stage progress weights (for calculating percentage)
        self.stage_weights = {
            UploadStage.QUEUED: 0,
            UploadStage.VALIDATING: 10,
            UploadStage.UPLOADING: 20,
            UploadStage.PROCESSING: 30,
            UploadStage.INGESTING: 50,
            UploadStage.VENDOR_DETECTION: 70,
            UploadStage.AUDITING: 85,
            UploadStage.COMPLETED: 100,
            UploadStage.FAILED: 0
        }
    
    def create_upload_session(self, vendor_id: str, upload_type: str = "single") -> UploadSession:
        """Create new upload session"""
        session = UploadSession(
            vendor_id=vendor_id,
            upload_type=upload_type
        )
        self.sessions[session.session_id] = session
        
        # Cleanup old sessions
        self._cleanup_old_sessions()
        
        logger.info(f"Created upload session {session.session_id} for vendor {vendor_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UploadSession]:
        """Get upload session by ID"""
        return self.sessions.get(session_id)
    
    def update_file_stage(self, session_id: str, file_id: str, stage: UploadStage, 
                         progress_data: Optional[Dict] = None) -> bool:
        """Update file processing stage"""
        session = self.get_session(session_id)
        if not session or file_id not in session.files:
            logger.warning(f"Session {session_id} or file {file_id} not found")
            return False
        
        file_progress = session.files[file_id]
        
        # Update stage and timing
        old_stage = file_progress.current_stage
        file_progress.current_stage = stage
        file_progress.stage_start_time = datetime.utcnow()
        
        # Update progress percentage based on stage
        file_progress.progress_percentage = self.stage_weights.get(stage, 0)
        
        # Update status based on stage
        if stage == UploadStage.FAILED:
            file_progress.status = UploadStatus.FAILED
            file_progress.completion_time = datetime.utcnow()
        elif stage == UploadStage.COMPLETED:
            file_progress.status = UploadStatus.SUCCESS
            file_progress.completion_time = datetime.utcnow()
            file_progress.progress_percentage = 100.0
        elif stage != UploadStage.QUEUED:
            file_progress.status = UploadStatus.IN_PROGRESS
        
        # Update additional data if provided
        if progress_data:
            for key, value in progress_data.items():
                if hasattr(file_progress, key):
                    setattr(file_progress, key, value)
        
        logger.info(f"Updated file {file_id} stage: {old_stage.value} -> {stage.value}")
        return True
    
    def update_file_error(self, session_id: str, file_id: str, error_message: str, 
                         error_code: Optional[str] = None) -> bool:
        """Update file with error information"""
        return self.update_file_stage(session_id, file_id, UploadStage.FAILED, {
            "error_message": error_message,
            "error_code": error_code or "UPLOAD_ERROR"
        })
    
    def get_session_progress(self, session_id: str) -> Optional[Dict]:
        """Get current session progress"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return session.get_overall_progress()
    
    def get_vendor_sessions(self, vendor_id: str, limit: int = 10) -> List[Dict]:
        """Get recent sessions for vendor"""
        vendor_sessions = [
            session for session in self.sessions.values() 
            if session.vendor_id == vendor_id
        ]
        
        # Sort by start time (newest first)
        vendor_sessions.sort(key=lambda s: s.session_start_time, reverse=True)
        
        return [session.get_overall_progress() for session in vendor_sessions[:limit]]
    
    def _cleanup_old_sessions(self):
        """Clean up old upload sessions"""
        cutoff_time = datetime.utcnow() - self.cleanup_interval
        old_session_ids = [
            session_id for session_id, session in self.sessions.items()
            if session.session_start_time < cutoff_time
        ]
        
        for session_id in old_session_ids:
            del self.sessions[session_id]
            logger.info(f"Cleaned up old session {session_id}")

# Global progress tracker instance
progress_tracker = UploadProgressTracker()

# Convenience functions
def create_upload_session(vendor_id: str, upload_type: str = "single") -> UploadSession:
    """Create new upload session"""
    return progress_tracker.create_upload_session(vendor_id, upload_type)

def update_file_stage(session_id: str, file_id: str, stage: UploadStage, 
                     progress_data: Optional[Dict] = None) -> bool:
    """Update file processing stage"""
    return progress_tracker.update_file_stage(session_id, file_id, stage, progress_data)

def update_file_error(session_id: str, file_id: str, error_message: str, 
                     error_code: Optional[str] = None) -> bool:
    """Update file with error information"""
    return progress_tracker.update_file_error(session_id, file_id, error_message, error_code)

def get_session_progress(session_id: str) -> Optional[Dict]:
    """Get current session progress"""
    return progress_tracker.get_session_progress(session_id)