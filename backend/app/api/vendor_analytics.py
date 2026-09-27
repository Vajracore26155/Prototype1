"""
Enhanced Vendor Analytics API
Provides detailed analytics, metrics, and insights for vendor dashboard
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.database.models import (
    Configuration, Audit, Finding, VendorUser, VendorUploadSession
)
from app.auth.vendor_auth import require_vendor_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vendor")

@router.get("/analytics/overview")
async def get_vendor_analytics_overview(
    timeframe: str = "30d",
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics overview for vendor dashboard
    
    Returns:
    - Key performance metrics
    - Trend data
    - Compliance statistics
    - Processing performance
    """
    vendor, session = vendor_session
    
    try:
        # Calculate date range
        if timeframe == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif timeframe == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
        elif timeframe == "1y":
            start_date = datetime.utcnow() - timedelta(days=365)
        else:  # Default 30d
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get vendor-specific configurations
        configs_query = db.query(Configuration).filter(
            Configuration.uploaded_by == vendor.vendor_id,
            Configuration.created_at >= start_date
        )
        
        total_configurations = configs_query.count()
        
        # Get audits for vendor's configurations
        audits_query = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id,
            Audit.started_at >= start_date
        )
        
        total_audits = audits_query.count()
        completed_audits = audits_query.filter(Audit.status == "COMPLETED").all()
        
        # Calculate compliance metrics
        if completed_audits:
            avg_compliance = sum(audit.compliance_score or 0 for audit in completed_audits) / len(completed_audits)
            avg_risk_score = sum(audit.risk_score or 0 for audit in completed_audits) / len(completed_audits)
        else:
            avg_compliance = 0
            avg_risk_score = 0
        
        # Get findings breakdown
        findings_query = db.query(Finding).join(
            Audit, Finding.audit_id == Audit.id
        ).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id,
            Audit.started_at >= start_date
        )
        
        findings_by_severity = {
            "CRITICAL": findings_query.filter(Finding.severity == "CRITICAL").count(),
            "HIGH": findings_query.filter(Finding.severity == "HIGH").count(),
            "MEDIUM": findings_query.filter(Finding.severity == "MEDIUM").count(),
            "LOW": findings_query.filter(Finding.severity == "LOW").count()
        }
        
        findings_by_status = {
            "PASS": findings_query.filter(Finding.status == "PASS").count(),
            "FAIL": findings_query.filter(Finding.status == "FAIL").count(),
            "WARNING": findings_query.filter(Finding.status == "WARNING").count(),
            "UNKNOWN": findings_query.filter(Finding.status == "UNKNOWN").count()
        }
        
        # Calculate processing metrics
        processing_times = [
            (audit.completed_at - audit.started_at).total_seconds() / 60 
            for audit in completed_audits 
            if audit.completed_at and audit.started_at
        ]
        
        if processing_times:
            avg_processing_time = sum(processing_times) / len(processing_times)
            fastest_processing = min(processing_times)
            slowest_processing = max(processing_times)
        else:
            avg_processing_time = 0
            fastest_processing = 0
            slowest_processing = 0
        
        # Calculate trends (compare with previous period)
        previous_start = start_date - (datetime.utcnow() - start_date)
        previous_configs = db.query(Configuration).filter(
            Configuration.uploaded_by == vendor.vendor_id,
            Configuration.created_at >= previous_start,
            Configuration.created_at < start_date
        ).count()
        
        previous_audits = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id,
            Audit.started_at >= previous_start,
            Audit.started_at < start_date,
            Audit.status == "COMPLETED"
        ).all()
        
        previous_avg_compliance = 0
        if previous_audits:
            previous_avg_compliance = sum(audit.compliance_score or 0 for audit in previous_audits) / len(previous_audits)
        
        # Determine trends
        compliance_trend = "stable"
        if avg_compliance > previous_avg_compliance + 1:
            compliance_trend = "improving"
        elif avg_compliance < previous_avg_compliance - 1:
            compliance_trend = "declining"
        
        risk_trend = "stable"  # Simplified for now
        if findings_by_severity["CRITICAL"] == 0 and findings_by_severity["HIGH"] < 5:
            risk_trend = "improving"
        
        return {
            "success": True,
            "data": {
                "metrics": {
                    "total_configurations": total_configurations,
                    "total_audits": total_audits,
                    "avg_compliance_score": round(avg_compliance, 1),
                    "critical_findings": findings_by_severity["CRITICAL"],
                    "high_findings": findings_by_severity["HIGH"],
                    "medium_findings": findings_by_severity["MEDIUM"],
                    "low_findings": findings_by_severity["LOW"],
                    "passed_controls": findings_by_status["PASS"],
                    "failed_controls": findings_by_status["FAIL"],
                    "warning_controls": findings_by_status["WARNING"],
                    "processing_time": {
                        "average": round(avg_processing_time, 1),
                        "fastest": round(fastest_processing, 1),
                        "slowest": round(slowest_processing, 1)
                    },
                    "risk_trend": risk_trend,
                    "compliance_trend": compliance_trend
                },
                "timeframe": timeframe,
                "period_comparison": {
                    "configurations_change": total_configurations - previous_configs,
                    "compliance_change": round(avg_compliance - previous_avg_compliance, 1)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get vendor analytics overview: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "ANALYTICS_FAILED",
                    "message": "Failed to retrieve analytics data"
                }
            }
        )


@router.get("/analytics/trends")
async def get_vendor_compliance_trends(
    timeframe: str = "30d",
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get compliance trend data for charts and visualizations
    """
    vendor, session = vendor_session
    
    try:
        # Calculate date range and intervals
        if timeframe == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
            interval_days = 1
        elif timeframe == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
            interval_days = 3
        elif timeframe == "1y":
            start_date = datetime.utcnow() - timedelta(days=365)
            interval_days = 7
        else:  # Default 30d
            start_date = datetime.utcnow() - timedelta(days=30)
            interval_days = 1
        
        # Generate trend data points
        trend_data = []
        current_date = start_date
        
        while current_date <= datetime.utcnow():
            next_date = current_date + timedelta(days=interval_days)
            
            # Get audits completed in this interval
            interval_audits = db.query(Audit).join(
                Configuration, Audit.configuration_id == Configuration.id
            ).filter(
                Configuration.uploaded_by == vendor.vendor_id,
                Audit.completed_at >= current_date,
                Audit.completed_at < next_date,
                Audit.status == "COMPLETED"
            ).all()
            
            # Calculate metrics for this interval
            if interval_audits:
                avg_compliance = sum(audit.compliance_score or 0 for audit in interval_audits) / len(interval_audits)
                critical_findings = sum(1 for audit in interval_audits 
                                     if db.query(Finding).filter(
                                         Finding.audit_id == audit.id,
                                         Finding.severity == "CRITICAL"
                                     ).count() > 0)
            else:
                avg_compliance = 0
                critical_findings = 0
            
            trend_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "compliance": round(avg_compliance, 1),
                "configurations": len(interval_audits),
                "critical_findings": critical_findings
            })
            
            current_date = next_date
        
        return {
            "success": True,
            "data": {
                "trend_data": trend_data,
                "timeframe": timeframe
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get vendor trends: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "TRENDS_FAILED",
                    "message": "Failed to retrieve trend data"
                }
            }
        )


@router.get("/analytics/risk-distribution")
async def get_vendor_risk_distribution(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get risk distribution analytics for vendor
    """
    vendor, session = vendor_session
    
    try:
        # Get all findings for vendor's configurations
        findings = db.query(Finding).join(
            Audit, Finding.audit_id == Audit.id
        ).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id
        ).all()
        
        # Calculate risk distribution
        total_findings = len(findings)
        if total_findings == 0:
            return {
                "success": True,
                "data": {
                    "risk_analysis": [],
                    "total_findings": 0
                }
            }
        
        severity_counts = {}
        for finding in findings:
            severity = finding.severity
            if severity not in severity_counts:
                severity_counts[severity] = 0
            severity_counts[severity] += 1
        
        # Format risk analysis — grayscale only
        colors = {
            "CRITICAL": "#1C1C1C",
            "HIGH": "#555555",
            "MEDIUM": "#9A9A9A",
            "LOW": "#D8D8D8"
        }
        
        risk_analysis = []
        for severity, count in severity_counts.items():
            percentage = (count / total_findings) * 100
            risk_analysis.append({
                "risk_level": severity.title(),
                "count": count,
                "percentage": round(percentage, 1),
                "color": colors.get(severity, "#6B7280")
            })
        
        # Sort by severity (Critical first)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        risk_analysis.sort(key=lambda x: severity_order.get(x["risk_level"].upper(), 4))
        
        return {
            "success": True,
            "data": {
                "risk_analysis": risk_analysis,
                "total_findings": total_findings
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get risk distribution: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "RISK_ANALYSIS_FAILED",
                    "message": "Failed to retrieve risk distribution"
                }
            }
        )


@router.get("/analytics/categories")
async def get_vendor_finding_categories(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get finding distribution by category
    """
    vendor, session = vendor_session
    
    try:
        # Get findings with categories (simplified categorization)
        findings = db.query(Finding).join(
            Audit, Finding.audit_id == Audit.id
        ).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id
        ).all()
        
        # Categorize findings based on rule patterns (simplified)
        categories = {}
        
        for finding in findings:
            # Real categorization based on rule_id pattern (NET-xxx are network-device controls)
            category = "Other"
            rid = (finding.rule_id or "").upper()
            title = (finding.title or "").upper()
            if rid.startswith("NET-") or "SSH" in rid or "TELNET" in rid or "SSH" in title:
                category = "Network Security"
            elif "AUTH" in rid or "USER" in rid or "ACCESS" in rid:
                category = "Access Control"
            elif "ENCRYPT" in rid or "CRYPTO" in rid:
                category = "Data Protection"
            elif "LOG" in rid or "AUDIT" in rid:
                category = "Logging & Monitoring"
            elif "PASS" in rid or "PWD" in rid:
                category = "Authentication"
            
            if category not in categories:
                categories[category] = {
                    "category": category,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "total": 0
                }
            
            categories[category][finding.severity.lower()] += 1
            categories[category]["total"] += 1
        
        return {
            "success": True,
            "data": {
                "finding_distribution": list(categories.values())
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get finding categories: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "CATEGORIES_FAILED",
                    "message": "Failed to retrieve finding categories"
                }
            }
        )