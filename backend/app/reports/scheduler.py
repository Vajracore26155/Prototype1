"""
Report Scheduler
Phase 7.3: Automated report generation with APScheduler
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
import asyncio

from app.database import ScheduledReport, Report, User
from app.reports.templates import TemplateLibrary, ReportFormat


class ReportScheduler:
    """
    Automated report generation scheduler
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print("Report scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("Report scheduler stopped")
    
    def schedule_report(
        self,
        schedule_id: str,
        scheduled_report: 'ScheduledReport',
        db: Session
    ):
        """
        Schedule a report for automatic generation
        
        Args:
            schedule_id: Unique schedule identifier
            scheduled_report: ScheduledReport database model
            db: Database session
        """
        schedule_type = scheduled_report.schedule_type
        
        if schedule_type == "DAILY":
            trigger = CronTrigger(
                hour=scheduled_report.schedule_time.hour,
                minute=scheduled_report.schedule_time.minute
            )
        elif schedule_type == "WEEKLY":
            trigger = CronTrigger(
                day_of_week=scheduled_report.schedule_day_of_week or 1,
                hour=scheduled_report.schedule_time.hour,
                minute=scheduled_report.schedule_time.minute
            )
        elif schedule_type == "MONTHLY":
            trigger = CronTrigger(
                day=scheduled_report.schedule_day_of_month or 1,
                hour=scheduled_report.schedule_time.hour,
                minute=scheduled_report.schedule_time.minute
            )
        elif schedule_type == "CUSTOM":
            # Parse cron expression
            trigger = CronTrigger.from_crontab(scheduled_report.cron_expression)
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")
        
        # Add job to scheduler
        self.scheduler.add_job(
            func=self._generate_scheduled_report,
            trigger=trigger,
            id=schedule_id,
            args=[scheduled_report.id, db],
            name=f"Report: {scheduled_report.name}",
            replace_existing=True
        )
        
        print(f"Scheduled report: {scheduled_report.name} ({schedule_type})")
    
    async def _generate_scheduled_report(self, scheduled_report_id: int, db: Session):
        """
        Generate a scheduled report
        
        This is called automatically by the scheduler
        """
        try:
            # Get scheduled report config
            scheduled_report = db.query(ScheduledReport).filter(
                ScheduledReport.id == scheduled_report_id
            ).first()
            
            if not scheduled_report or not scheduled_report.is_active:
                return
            
            # Get template
            templates = TemplateLibrary.get_all_templates()
            template = next(
                (t for t in templates if t.template_id == scheduled_report.template_id),
                None
            )
            
            if not template:
                print(f"Template not found: {scheduled_report.template_id}")
                return
            
            # Gather report data
            report_data = await self._gather_report_data(
                scheduled_report.organization_id,
                scheduled_report.filters,
                db
            )
            
            # Generate report
            content = template.render(report_data, format=ReportFormat.HTML)
            
            # Save report
            report_count = db.query(Report).count()
            report_id = f"RPT-{report_count + 1:08d}"
            
            report = Report(
                report_id=report_id,
                organization_id=scheduled_report.organization_id,
                audit_id=None,  # Not tied to specific audit
                report_type=scheduled_report.report_type,
                name=f"{scheduled_report.name} - {datetime.utcnow().strftime('%Y-%m-%d')}",
                format=scheduled_report.format,
                content=content,
                metadata={
                    "scheduled_report_id": scheduled_report.schedule_id,
                    "generated_by": "scheduler",
                    "template_id": scheduled_report.template_id
                },
                generated_by="system",
                file_path=f"reports/{report_id}.{scheduled_report.format}"
            )
            
            db.add(report)
            
            # Update scheduled report
            scheduled_report.last_run_at = datetime.utcnow()
            scheduled_report.run_count += 1
            
            db.commit()
            
            # Send notifications if configured
            if scheduled_report.recipients:
                await self._send_report_notifications(
                    report,
                    scheduled_report.recipients,
                    db
                )
            
            print(f"Generated report: {report_id}")
            
        except Exception as e:
            print(f"Error generating scheduled report: {e}")
            db.rollback()
    
    async def _gather_report_data(
        self,
        organization_id: int,
        filters: Dict,
        db: Session
    ) -> Dict:
        """
        Gather data for report generation
        
        This would query various tables to collect metrics,
        findings, devices, etc.
        """
        from app.database import (
            SecurityAudit, Finding, Device,
            ConfigurationFile, ComplianceCheck
        )
        
        # Calculate date range
        date_range = filters.get("date_range", "30d")
        if date_range == "7d":
            start_date = datetime.utcnow() - timedelta(days=7)
        elif date_range == "30d":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif date_range == "90d":
            start_date = datetime.utcnow() - timedelta(days=90)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
        
        # Get audits
        audits = db.query(SecurityAudit).filter(
            SecurityAudit.organization_id == organization_id,
            SecurityAudit.created_at >= start_date
        ).all()
        
        # Get findings
        findings = db.query(Finding).filter(
            Finding.organization_id == organization_id,
            Finding.created_at >= start_date
        ).all()
        
        # Get devices
        devices = db.query(Device).filter(
            Device.organization_id == organization_id
        ).all()
        
        # Calculate metrics
        metrics = {
            "total_devices": len(devices),
            "total_audits": len(audits),
            "critical_findings": len([f for f in findings if f.severity == "CRITICAL"]),
            "high_findings": len([f for f in findings if f.severity == "HIGH"]),
            "medium_findings": len([f for f in findings if f.severity == "MEDIUM"]),
            "low_findings": len([f for f in findings if f.severity == "LOW"]),
            "compliance_score": self._calculate_compliance_score(audits),
            "trend": "improving"  # Would calculate actual trend
        }
        
        # Format findings
        findings_data = [
            {
                "finding_id": f.finding_id,
                "title": f.title,
                "severity": f.severity,
                "category": f.category,
                "description": f.description,
                "device_id": f.device_id
            }
            for f in findings
        ]
        
        # Format devices
        devices_data = [
            {
                "device_id": d.device_id,
                "vendor": d.vendor,
                "model": d.model,
                "status": d.status
            }
            for d in devices
        ]
        
        return {
            "organization_id": organization_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "metrics": metrics,
            "findings": findings_data,
            "devices": devices_data,
            "recommendations": self._generate_recommendations(findings)
        }
    
    def _calculate_compliance_score(self, audits: List) -> float:
        """Calculate overall compliance score"""
        if not audits:
            return 0.0
        
        total_score = sum(audit.compliance_score for audit in audits if audit.compliance_score)
        return round(total_score / len(audits), 2) if audits else 0.0
    
    def _generate_recommendations(self, findings: List) -> List[Dict]:
        """Generate top recommendations based on findings"""
        recommendations = []
        
        # Group by category
        categories = {}
        for finding in findings:
            cat = finding.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        # Generate recommendations for top categories
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            recommendations.append({
                "category": category,
                "priority": "HIGH" if count > 10 else "MEDIUM",
                "issue_count": count,
                "recommendation": f"Review and address {count} issues in {category}"
            })
        
        return recommendations
    
    async def _send_report_notifications(
        self,
        report: 'Report',
        recipients: List[str],
        db: Session
    ):
        """
        Send email notifications with report
        
        Placeholder for email integration
        """
        print(f"Would send report {report.report_id} to {len(recipients)} recipients")
        # TODO: Integrate with email service
    
    def unschedule_report(self, schedule_id: str):
        """Remove a scheduled report"""
        try:
            self.scheduler.remove_job(schedule_id)
            print(f"Unscheduled report: {schedule_id}")
        except Exception as e:
            print(f"Error unscheduling report: {e}")
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]


# Global scheduler instance
report_scheduler = ReportScheduler()
