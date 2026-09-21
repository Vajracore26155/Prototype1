"""
Advanced Report Templates Engine
Phase 7.3: Customizable report generation with templates
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json


class ReportType(str, Enum):
    """Report types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_DETAILED = "technical_detailed"
    COMPLIANCE_AUDIT = "compliance_audit"
    TREND_ANALYSIS = "trend_analysis"
    SECURITY_POSTURE = "security_posture"
    RISK_ASSESSMENT = "risk_assessment"
    DEVICE_INVENTORY = "device_inventory"
    CHANGE_LOG = "change_log"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Output formats"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class ReportTemplate:
    """Base report template"""
    
    def __init__(
        self,
        template_id: str,
        name: str,
        report_type: ReportType,
        description: str,
        sections: List[Dict]
    ):
        self.template_id = template_id
        self.name = name
        self.report_type = report_type
        self.description = description
        self.sections = sections
        self.created_at = datetime.utcnow()
    
    def render(self, data: Dict, format: ReportFormat = ReportFormat.JSON) -> Any:
        """Render report with data"""
        rendered_sections = []
        
        for section in self.sections:
            rendered_section = self._render_section(section, data)
            rendered_sections.append(rendered_section)
        
        report = {
            "template_id": self.template_id,
            "template_name": self.name,
            "report_type": self.report_type.value,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": rendered_sections,
            "metadata": {
                "organization_id": data.get("organization_id"),
                "generated_by": data.get("generated_by"),
                "date_range": data.get("date_range")
            }
        }
        
        if format == ReportFormat.JSON:
            return json.dumps(report, indent=2)
        elif format == ReportFormat.HTML:
            return self._render_html(report)
        elif format == ReportFormat.PDF:
            return self._render_pdf(report)
        else:
            return report
    
    def _render_section(self, section: Dict, data: Dict) -> Dict:
        """Render individual section"""
        section_type = section.get("type")
        
        if section_type == "summary":
            return self._render_summary(section, data)
        elif section_type == "table":
            return self._render_table(section, data)
        elif section_type == "chart":
            return self._render_chart(section, data)
        elif section_type == "findings":
            return self._render_findings(section, data)
        elif section_type == "recommendations":
            return self._render_recommendations(section, data)
        else:
            return section
    
    def _render_summary(self, section: Dict, data: Dict) -> Dict:
        """Render summary section"""
        metrics = data.get("metrics", {})
        return {
            "type": "summary",
            "title": section.get("title"),
            "content": {
                "total_devices": metrics.get("total_devices", 0),
                "total_audits": metrics.get("total_audits", 0),
                "critical_findings": metrics.get("critical_findings", 0),
                "high_findings": metrics.get("high_findings", 0),
                "compliance_score": metrics.get("compliance_score", 0),
                "trend": metrics.get("trend", "stable")
            }
        }
    
    def _render_table(self, section: Dict, data: Dict) -> Dict:
        """Render table section"""
        data_source = section.get("data_source")
        table_data = data.get(data_source, [])
        
        return {
            "type": "table",
            "title": section.get("title"),
            "columns": section.get("columns", []),
            "rows": table_data
        }
    
    def _render_chart(self, section: Dict, data: Dict) -> Dict:
        """Render chart section"""
        chart_data = data.get(section.get("data_source"), {})
        
        return {
            "type": "chart",
            "title": section.get("title"),
            "chart_type": section.get("chart_type", "bar"),
            "data": chart_data
        }
    
    def _render_findings(self, section: Dict, data: Dict) -> Dict:
        """Render findings section"""
        findings = data.get("findings", [])
        
        # Group by severity
        grouped = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        for finding in findings:
            severity = finding.get("severity", "LOW")
            grouped[severity].append(finding)
        
        return {
            "type": "findings",
            "title": section.get("title"),
            "findings_by_severity": grouped,
            "total_findings": len(findings)
        }
    
    def _render_recommendations(self, section: Dict, data: Dict) -> Dict:
        """Render recommendations section"""
        recommendations = data.get("recommendations", [])
        
        return {
            "type": "recommendations",
            "title": section.get("title"),
            "recommendations": recommendations
        }
    
    def _render_html(self, report: Dict) -> str:
        """Render report as HTML"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report['template_name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                .critical {{ color: #e74c3c; font-weight: bold; }}
                .high {{ color: #e67e22; font-weight: bold; }}
                .medium {{ color: #f39c12; }}
                .low {{ color: #95a5a6; }}
            </style>
        </head>
        <body>
            <h1>{report['template_name']}</h1>
            <p>Generated: {report['generated_at']}</p>
        """
        
        for section in report['sections']:
            html += f"<h2>{section.get('title', 'Section')}</h2>"
            
            if section['type'] == 'summary':
                content = section['content']
                html += f"""
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Devices</td><td>{content.get('total_devices', 0)}</td></tr>
                    <tr><td>Total Audits</td><td>{content.get('total_audits', 0)}</td></tr>
                    <tr><td>Critical Findings</td><td class="critical">{content.get('critical_findings', 0)}</td></tr>
                    <tr><td>High Findings</td><td class="high">{content.get('high_findings', 0)}</td></tr>
                    <tr><td>Compliance Score</td><td>{content.get('compliance_score', 0)}%</td></tr>
                </table>
                """
            
            elif section['type'] == 'findings':
                findings = section.get('findings_by_severity', {})
                for severity, items in findings.items():
                    if items:
                        html += f"<h3 class='{severity.lower()}'>{severity} ({len(items)})</h3><ul>"
                        for item in items[:10]:  # Limit display
                            html += f"<li>{item.get('title', 'Finding')}</li>"
                        html += "</ul>"
        
        html += "</body></html>"
        return html
    
    def _render_pdf(self, report: Dict) -> bytes:
        """Render report as PDF (placeholder)"""
        # Would use ReportLab or WeasyPrint
        return b"PDF generation not implemented"


class TemplateLibrary:
    """Built-in report templates"""
    
    @staticmethod
    def get_executive_summary_template() -> ReportTemplate:
        """Executive summary template"""
        return ReportTemplate(
            template_id="TMPL-001",
            name="Executive Summary Report",
            report_type=ReportType.EXECUTIVE_SUMMARY,
            description="High-level overview for executives",
            sections=[
                {
                    "type": "summary",
                    "title": "Overview",
                    "metrics": ["total_devices", "total_audits", "compliance_score"]
                },
                {
                    "type": "chart",
                    "title": "Compliance Trend",
                    "chart_type": "line",
                    "data_source": "compliance_trend"
                },
                {
                    "type": "findings",
                    "title": "Critical Findings",
                    "severity_filter": ["CRITICAL", "HIGH"]
                },
                {
                    "type": "recommendations",
                    "title": "Top Recommendations"
                }
            ]
        )
    
    @staticmethod
    def get_technical_detailed_template() -> ReportTemplate:
        """Technical detailed report"""
        return ReportTemplate(
            template_id="TMPL-002",
            name="Technical Detailed Report",
            report_type=ReportType.TECHNICAL_DETAILED,
            description="Comprehensive technical analysis",
            sections=[
                {
                    "type": "summary",
                    "title": "Executive Summary"
                },
                {
                    "type": "table",
                    "title": "Device Inventory",
                    "data_source": "devices",
                    "columns": ["device_id", "vendor", "model", "status"]
                },
                {
                    "type": "findings",
                    "title": "All Findings"
                },
                {
                    "type": "table",
                    "title": "Configuration Issues",
                    "data_source": "issues"
                },
                {
                    "type": "recommendations",
                    "title": "Remediation Steps"
                }
            ]
        )
    
    @staticmethod
    def get_compliance_audit_template() -> ReportTemplate:
        """Compliance audit report"""
        return ReportTemplate(
            template_id="TMPL-003",
            name="Compliance Audit Report",
            report_type=ReportType.COMPLIANCE_AUDIT,
            description="Regulatory compliance assessment",
            sections=[
                {
                    "type": "summary",
                    "title": "Compliance Overview"
                },
                {
                    "type": "table",
                    "title": "Standards Compliance",
                    "data_source": "standards_compliance"
                },
                {
                    "type": "findings",
                    "title": "Non-Compliance Issues"
                },
                {
                    "type": "table",
                    "title": "Risk Assessment",
                    "data_source": "risks"
                }
            ]
        )
    
    @staticmethod
    def get_all_templates() -> List[ReportTemplate]:
        """Get all built-in templates"""
        return [
            TemplateLibrary.get_executive_summary_template(),
            TemplateLibrary.get_technical_detailed_template(),
            TemplateLibrary.get_compliance_audit_template()
        ]
