"""
Posture Trend Tracking
Phase 5: Historical posture analysis
"""
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import PostureScore, PostureTrend


def track_posture_trend(db: Session, organization_id: int, device_id: int = None):
    """
    Track posture score trend
    
    Args:
        db: Database session
        organization_id: Organization ID
        device_id: Optional device ID (None for org-level)
    """
    # Get latest score
    query = db.query(PostureScore).filter(
        PostureScore.organization_id == organization_id
    )
    
    if device_id:
        query = query.filter(PostureScore.device_id == device_id)
    else:
        query = query.filter(PostureScore.device_id.is_(None))
    
    latest = query.order_by(PostureScore.calculated_at.desc()).first()
    
    if not latest:
        return None
    
    # Check if trend already exists for today
    today = datetime.utcnow().date()
    existing = db.query(PostureTrend).filter(
        PostureTrend.organization_id == organization_id,
        PostureTrend.device_id == device_id if device_id else PostureTrend.device_id.is_(None),
        PostureTrend.date >= today
    ).first()
    
    if existing:
        # Update existing
        existing.score = latest.score
        existing.compliance_score = latest.compliance_score
        existing.drift_score = latest.drift_score
        existing.risk_score = latest.risk_score
        db.commit()
        return existing
    
    # Create new trend record
    trend = PostureTrend(
        organization_id=organization_id,
        device_id=device_id,
        date=datetime.utcnow(),
        score=latest.score,
        compliance_score=latest.compliance_score,
        drift_score=latest.drift_score,
        risk_score=latest.risk_score
    )
    
    db.add(trend)
    db.commit()
    return trend


def get_trend_analysis(db: Session, organization_id: int, days: int = 30, device_id: int = None) -> Dict:
    """
    Analyze posture trends over time
    
    Args:
        db: Database session
        organization_id: Organization ID
        days: Number of days to analyze
        device_id: Optional device ID
        
    Returns:
        Dictionary with trend analysis
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(PostureTrend).filter(
        PostureTrend.organization_id == organization_id,
        PostureTrend.date >= cutoff_date
    )
    
    if device_id:
        query = query.filter(PostureTrend.device_id == device_id)
    else:
        query = query.filter(PostureTrend.device_id.is_(None))
    
    trends = query.order_by(PostureTrend.date).all()
    
    if not trends:
        return {
            "has_data": False,
            "message": "No trend data available"
        }
    
    scores = [t.score for t in trends]
    
    # Calculate statistics
    current_score = scores[-1]
    starting_score = scores[0]
    change = current_score - starting_score
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # Determine trend direction
    if change > 5:
        direction = "IMPROVING"
    elif change < -5:
        direction = "DECLINING"
    else:
        direction = "STABLE"
    
    return {
        "has_data": True,
        "period_days": days,
        "data_points": len(trends),
        "current_score": current_score,
        "starting_score": starting_score,
        "change": change,
        "change_percent": (change / starting_score * 100) if starting_score > 0 else 0,
        "average_score": round(avg_score, 2),
        "max_score": max_score,
        "min_score": min_score,
        "trend_direction": direction,
        "volatility": round(max_score - min_score, 2)
    }
