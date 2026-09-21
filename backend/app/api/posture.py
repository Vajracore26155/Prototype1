"""
Security Posture Scoring API
Phase 5: Posture scores and trends
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta

from app.database import (
    get_db, Device, PostureScore, PostureTrend, User
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.posture import calculate_organization_score, calculate_device_score

router = APIRouter()


@router.get("/posture/organization")
async def get_organization_posture(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get organization-level security posture score
    """
    try:
        # Calculate current score
        score_result = calculate_organization_score(db, current_user.organization_id)
        
        # Get previous score for trend
        previous_score_record = db.query(PostureScore).filter(
            PostureScore.organization_id == current_user.organization_id,
            PostureScore.device_id.is_(None)
        ).order_by(PostureScore.calculated_at.desc()).first()
        
        previous_score = previous_score_record.score if previous_score_record else None
        score_change = score_result.score - previous_score if previous_score else 0
        
        # Determine trend
        if score_change > 5:
            trend = "IMPROVING"
        elif score_change < -5:
            trend = "DECLINING"
        else:
            trend = "STABLE"
        
        # Save new score
        score_id = f"SCR-{db.query(PostureScore).count() + 1:06d}"
        
        posture_score = PostureScore(
            score_id=score_id,
            organization_id=current_user.organization_id,
            device_id=None,  # Organization level
            score=score_result.score,
            compliance_score=score_result.factors.compliance_score,
            drift_score=score_result.factors.drift_score,
            risk_score=score_result.factors.risk_score,
            remediation_score=score_result.factors.remediation_score,
            config_age_score=score_result.factors.config_age_score,
            factor_breakdown=score_result.factor_breakdown,
            trend=trend,
            previous_score=previous_score,
            score_change=score_change
        )
        
        db.add(posture_score)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "score": score_result.score,
                "trend": trend,
                "score_change": round(score_change, 2),
                "previous_score": previous_score,
                "factors": {
                    "compliance": score_result.factors.compliance_score,
                    "drift": score_result.factors.drift_score,
                    "risk": score_result.factors.risk_score,
                    "remediation": score_result.factors.remediation_score,
                    "config_age": score_result.factors.config_age_score
                },
                "breakdown": score_result.factor_breakdown,
                "calculated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "CALCULATION_FAILED",
                    "message": f"Failed to calculate organization posture: {str(e)}"
                }
            }
        )


@router.get("/posture/devices")
async def get_device_postures(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db),
    limit: int = 100,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None
):
    """
    Get posture scores for all devices
    """
    try:
        # Get all active devices
        devices = db.query(Device).filter(
            Device.organization_id == current_user.organization_id,
            Device.status == "ACTIVE"
        ).limit(limit).all()
        
        device_scores = []
        
        for device in devices:
            try:
                # Get latest score or calculate new one
                latest_score = db.query(PostureScore).filter(
                    PostureScore.device_id == device.id
                ).order_by(PostureScore.calculated_at.desc()).first()
                
                # Recalculate if older than 24 hours or doesn't exist
                if not latest_score or (datetime.utcnow() - latest_score.calculated_at).days >= 1:
                    score_result = calculate_device_score(db, device.id)
                    score = score_result.score
                else:
                    score = latest_score.score
                
                # Apply filters
                if min_score and score < min_score:
                    continue
                if max_score and score > max_score:
                    continue
                
                device_scores.append({
                    "device_id": device.device_id,
                    "hostname": device.hostname,
                    "device_type": device.device_type,
                    "vendor": device.vendor,
                    "score": score,
                    "criticality": device.criticality,
                    "location": device.location
                })
                
            except Exception as e:
                print(f"Error calculating score for device {device.device_id}: {str(e)}")
                continue
        
        # Sort by score (lowest first - most critical)
        device_scores.sort(key=lambda x: x["score"])
        
        return {
            "success": True,
            "data": {
                "devices": device_scores,
                "total": len(device_scores),
                "average_score": round(sum(d["score"] for d in device_scores) / len(device_scores), 2) if device_scores else 0
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": f"Failed to retrieve device postures: {str(e)}"
                }
            }
        )


@router.get("/posture/devices/{device_id}")
async def get_device_posture(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get detailed posture score for a specific device
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Device {device_id} not found"
                    }
                }
            )
        
        # Calculate score
        score_result = calculate_device_score(db, device.id)
        
        # Get previous score
        previous_score_record = db.query(PostureScore).filter(
            PostureScore.device_id == device.id
        ).order_by(PostureScore.calculated_at.desc()).first()
        
        previous_score = previous_score_record.score if previous_score_record else None
        score_change = score_result.score - previous_score if previous_score else 0
        
        # Determine trend
        if score_change > 5:
            trend = "IMPROVING"
        elif score_change < -5:
            trend = "DECLINING"
        else:
            trend = "STABLE"
        
        # Save new score
        score_id = f"SCR-{db.query(PostureScore).count() + 1:06d}"
        
        posture_score = PostureScore(
            score_id=score_id,
            organization_id=current_user.organization_id,
            device_id=device.id,
            score=score_result.score,
            compliance_score=score_result.factors.compliance_score,
            drift_score=score_result.factors.drift_score,
            risk_score=score_result.factors.risk_score,
            remediation_score=score_result.factors.remediation_score,
            config_age_score=score_result.factors.config_age_score,
            factor_breakdown=score_result.factor_breakdown,
            trend=trend,
            previous_score=previous_score,
            score_change=score_change
        )
        
        db.add(posture_score)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "hostname": device.hostname,
                "score": score_result.score,
                "trend": trend,
                "score_change": round(score_change, 2),
                "previous_score": previous_score,
                "factors": {
                    "compliance": score_result.factors.compliance_score,
                    "drift": score_result.factors.drift_score,
                    "risk": score_result.factors.risk_score,
                    "remediation": score_result.factors.remediation_score,
                    "config_age": score_result.factors.config_age_score
                },
                "breakdown": score_result.factor_breakdown,
                "calculated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "CALCULATION_FAILED",
                    "message": f"Failed to calculate device posture: {str(e)}"
                }
            }
        )


@router.get("/posture/trends")
async def get_posture_trends(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db),
    days: int = 30,
    device_id: Optional[str] = None
):
    """
    Get posture score trends over time
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        if device_id:
            # Device-level trends
            device = db.query(Device).filter(
                Device.device_id == device_id,
                Device.organization_id == current_user.organization_id
            ).first()
            
            if not device:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": {
                            "code": "NOT_FOUND",
                            "message": f"Device {device_id} not found"
                        }
                    }
                )
            
            scores = db.query(PostureScore).filter(
                PostureScore.device_id == device.id,
                PostureScore.calculated_at >= cutoff_date
            ).order_by(PostureScore.calculated_at).all()
            
        else:
            # Organization-level trends
            scores = db.query(PostureScore).filter(
                PostureScore.organization_id == current_user.organization_id,
                PostureScore.device_id.is_(None),
                PostureScore.calculated_at >= cutoff_date
            ).order_by(PostureScore.calculated_at).all()
        
        trend_data = [
            {
                "date": score.calculated_at.isoformat(),
                "score": score.score,
                "compliance_score": score.compliance_score,
                "drift_score": score.drift_score,
                "risk_score": score.risk_score,
                "trend": score.trend
            }
            for score in scores
        ]
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "period_days": days,
                "data_points": len(trend_data),
                "trends": trend_data,
                "summary": {
                    "current_score": trend_data[-1]["score"] if trend_data else 0,
                    "starting_score": trend_data[0]["score"] if trend_data else 0,
                    "change": trend_data[-1]["score"] - trend_data[0]["score"] if len(trend_data) > 1 else 0,
                    "average_score": round(sum(t["score"] for t in trend_data) / len(trend_data), 2) if trend_data else 0
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve posture trends"
                }
            }
        )


@router.get("/posture/breakdown")
async def get_posture_breakdown(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get detailed posture score breakdown by category
    """
    try:
        # Get latest organization score
        latest = db.query(PostureScore).filter(
            PostureScore.organization_id == current_user.organization_id,
            PostureScore.device_id.is_(None)
        ).order_by(PostureScore.calculated_at.desc()).first()
        
        if not latest:
            # Calculate if doesn't exist
            score_result = calculate_organization_score(db, current_user.organization_id)
            breakdown = score_result.factor_breakdown
            score = score_result.score
        else:
            breakdown = latest.factor_breakdown
            score = latest.score
        
        return {
            "success": True,
            "data": {
                "overall_score": score,
                "factors": breakdown,
                "recommendations": generate_recommendations(breakdown)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve posture breakdown"
                }
            }
        )


def generate_recommendations(breakdown: dict) -> list:
    """
    Generate recommendations based on posture breakdown
    """
    recommendations = []
    
    # Check each factor
    if breakdown.get("compliance", {}).get("score", 100) < 70:
        recommendations.append({
            "category": "Compliance",
            "priority": "HIGH",
            "message": "Compliance score is below threshold. Review failed controls and implement remediation plans."
        })
    
    if breakdown.get("drift", {}).get("raw_drift", 0) > 50:
        recommendations.append({
            "category": "Configuration Drift",
            "priority": "MEDIUM",
            "message": "Significant configuration drift detected. Review drift analysis and update baselines."
        })
    
    if breakdown.get("risk", {}).get("critical_findings", 0) > 0:
        recommendations.append({
            "category": "Risk",
            "priority": "CRITICAL",
            "message": f"Critical security findings detected. Immediate remediation required."
        })
    
    if breakdown.get("config_age", {}).get("age_days", 0) > 90:
        recommendations.append({
            "category": "Configuration Age",
            "priority": "LOW",
            "message": "Configurations are outdated. Consider updating to latest secure baselines."
        })
    
    return recommendations
