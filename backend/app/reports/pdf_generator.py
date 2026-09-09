"""
PDF Report Generator for Security Audit Results

Generates comprehensive, professional PDF reports including:
- Executive summary
- Compliance scores and risk analysis
- Detailed findings with evidence
- Remediation recommendations
- Charts and visualizations
"""
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

from app.database import Audit, Finding, Configuration, get_db_session


class AuditReportGenerator:
    """Generate professional PDF reports for security audits"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the report"""
        
        # Helper function to add style only if it doesn't exist
        def add_style_if_new(style):
            if style.name not in self.styles:
                self.styles.add(style)
        
        # Title style
        add_style_if_new(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        add_style_if_new(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section heading
        add_style_if_new(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        add_style_if_new(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Alert box style
        add_style_if_new(ParagraphStyle(
            name='AlertBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#854d0e'),
            spaceAfter=10,
            leftIndent=20,
            rightIndent=20,
            fontName='Helvetica-Bold'
        ))
        
        # Code style
        add_style_if_new(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1e293b'),
            fontName='Courier',
            leftIndent=20,
            spaceAfter=10
        ))
    
    def generate_report(self, audit_id: str) -> BytesIO:
        """
        Generate complete PDF report for an audit
        
        Args:
            audit_id: Audit ID (e.g., "AUD-000001")
            
        Returns:
            BytesIO buffer containing PDF data
        """
        db = get_db_session()
        try:
            # Get audit data
            audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
            if not audit:
                raise ValueError(f"Audit {audit_id} not found")
            
            # Get configuration
            config = db.query(Configuration).filter(
                Configuration.id == audit.configuration_id
            ).first()
            
            # Get findings
            findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
            
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=f"Security Audit Report - {audit_id}",
                author="SIH26155 Security Audit System"
            )
            
            # Build report content
            story = []
            
            # Cover page
            story.extend(self._build_cover_page(audit, config))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._build_executive_summary(audit, config, findings))
            story.append(PageBreak())
            
            # Human intervention alert (if needed)
            if audit.requires_human_review:
                story.extend(self._build_review_alert(audit))
            
            # Compliance and risk overview
            story.extend(self._build_compliance_overview(audit, findings))
            story.append(Spacer(1, 0.3*inch))
            
            # Findings by severity
            story.extend(self._build_findings_section(findings))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
            
        finally:
            db.close()
    
    def _build_cover_page(self, audit: Audit, config: Configuration) -> List:
        """Build report cover page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(
            "SECURITY AUDIT REPORT",
            self.styles['CustomTitle']
        ))
        
        # Subtitle
        elements.append(Paragraph(
            f"Configuration: {config.original_filename if config else 'N/A'}",
            self.styles['CustomSubtitle']
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Audit info table
        info_data = [
            ['Audit ID:', audit.audit_id],
            ['Configuration ID:', config.config_id if config else 'N/A'],
            ['Vendor:', config.vendor if config else 'Unknown'],
            ['Status:', audit.status],
            ['Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#475569')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 1*inch))
        
        # Status badge
        status_color = self._get_status_color(audit.status)
        status_para = Paragraph(
            f"<font color='{status_color}' size='14'><b>Status: {audit.status}</b></font>",
            self.styles['Normal']
        )
        elements.append(status_para)
        
        return elements
    
    def _build_executive_summary(self, audit: Audit, config: Configuration, findings: List[Finding]) -> List:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        
        # Summary text
        summary_text = f"""
        This report presents the results of an automated security audit conducted on the 
        configuration file <b>{config.original_filename if config else 'N/A'}</b> from 
        vendor <b>{config.vendor if config else 'Unknown'}</b>. 
        The audit evaluated {len(findings)} security controls across multiple compliance domains.
        """
        
        elements.append(Paragraph(summary_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key metrics table
        failed_findings = [f for f in findings if f.status == 'FAIL']
        passed_findings = [f for f in findings if f.status == 'PASS']
        
        critical_count = len([f for f in failed_findings if f.severity == 'CRITICAL'])
        high_count = len([f for f in failed_findings if f.severity == 'HIGH'])
        medium_count = len([f for f in failed_findings if f.severity == 'MEDIUM'])
        low_count = len([f for f in failed_findings if f.severity == 'LOW'])
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Compliance Score', f"{audit.compliance_score:.1f}%" if audit.compliance_score else 'N/A'],
            ['Risk Level', audit.risk_level or 'N/A'],
            ['Risk Score', f"{audit.risk_score:.2f}" if audit.risk_score else 'N/A'],
            ['Controls Passed', str(len(passed_findings))],
            ['Controls Failed', str(len(failed_findings))],
            ['Critical Issues', str(critical_count)],
            ['High Severity Issues', str(high_count)],
            ['Medium Severity Issues', str(medium_count)],
            ['Low Severity Issues', str(low_count)],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    def _build_review_alert(self, audit: Audit) -> List:
        """Build human intervention alert section"""
        elements = []
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Alert box
        alert_data = [[
            Paragraph(
                "⚠ HUMAN REVIEW REQUIRED",
                self.styles['AlertBox']
            )
        ]]
        
        alert_table = Table(alert_data, colWidths=[6.5*inch])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ca8a04')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(alert_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Alert details
        alert_text = f"""
        <b>Reason:</b> {audit.review_reason or 'Manual validation required'}<br/>
        <br/>
        <b>Interpretation Confidence:</b> {audit.interpretation_confidence * 100:.1f}%<br/>
        <b>Uninterpreted Lines:</b> {audit.uninterpreted_lines_count} / {audit.total_lines_count}<br/>
        """
        
        if audit.pending_mappings_count and audit.pending_mappings_count > 0:
            alert_text += f"<b>Pending AI Mappings:</b> {audit.pending_mappings_count}<br/>"
        
        alert_text += """
        <br/>
        This configuration contains proprietary or unknown syntax that could not be interpreted 
        with high confidence. Manual review by a security expert is recommended to validate the 
        audit findings and ensure accuracy.
        """
        
        elements.append(Paragraph(alert_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_compliance_overview(self, audit: Audit, findings: List[Finding]) -> List:
        """Build compliance and risk overview section"""
        elements = []
        
        elements.append(Paragraph("Compliance & Risk Analysis", self.styles['SectionHeading']))
        
        # Risk level indicator
        risk_color = self._get_risk_color(audit.risk_level)
        risk_para = Paragraph(
            f"<font color='{risk_color}' size='13'><b>Overall Risk Level: {audit.risk_level or 'N/A'}</b></font>",
            self.styles['Normal']
        )
        elements.append(risk_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # Compliance score visualization
        if audit.compliance_score is not None:
            drawing = Drawing(400, 200)
            
            # Create pie chart for pass/fail
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            
            passed = audit.passed_count or 0
            failed = audit.failed_count or 0
            total = passed + failed
            
            if total > 0:
                pie.data = [passed, failed]
                pie.labels = [f'Passed\n({passed})', f'Failed\n({failed})']
                pie.slices[0].fillColor = colors.HexColor('#22c55e')
                pie.slices[1].fillColor = colors.HexColor('#ef4444')
                
                drawing.add(pie)
                elements.append(drawing)
        
        return elements
    
    def _build_findings_section(self, findings: List[Finding]) -> List:
        """Build detailed findings section"""
        elements = []
        
        elements.append(Paragraph("Detailed Findings", self.styles['SectionHeading']))
        
        # Group findings by severity
        failed_findings = [f for f in findings if f.status == 'FAIL']
        
        if not failed_findings:
            elements.append(Paragraph(
                "✓ No security violations detected. All controls passed.",
                self.styles['BodyText']
            ))
            return elements
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        failed_findings.sort(key=lambda x: severity_order.get(x.severity, 999))
        
        # Add each finding
        for finding in failed_findings:
            finding_elements = self._build_finding_detail(finding)
            elements.append(KeepTogether(finding_elements))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _build_finding_detail(self, finding: Finding) -> List:
        """Build detail section for a single finding"""
        elements = []
        
        # Finding header
        severity_color = self._get_severity_color(finding.severity)
        header_text = f"""
        <font color='{severity_color}' size='12'><b>[{finding.severity}]</b></font> 
        <font size='12'><b>{finding.title}</b></font>
        """
        elements.append(Paragraph(header_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Rule ID
        elements.append(Paragraph(
            f"<font size='9' color='#64748b'>Rule ID: {finding.rule_id}</font>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1*inch))
        
        # Description
        if finding.description:
            elements.append(Paragraph(
                f"<b>Description:</b> {finding.description}",
                self.styles['BodyText']
            ))
        
        # Expected vs Actual
        if finding.expected or finding.actual:
            detail_text = ""
            if finding.expected:
                detail_text += f"<b>Expected:</b> {finding.expected}<br/>"
            if finding.actual:
                detail_text += f"<b>Actual:</b> {finding.actual}<br/>"
            
            elements.append(Paragraph(detail_text, self.styles['BodyText']))
        
        # Evidence
        if finding.evidence_text:
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph("<b>Evidence:</b>", self.styles['BodyText']))
            elements.append(Paragraph(
                f"<font face='Courier' size='8'>{finding.evidence_text[:200]}</font>",
                self.styles['CodeStyle']
            ))
            if finding.evidence_file and finding.evidence_line:
                elements.append(Paragraph(
                    f"<font size='8' color='#64748b'>Location: {finding.evidence_file}, Line {finding.evidence_line}</font>",
                    self.styles['Normal']
                ))
        
        # Remediation
        if finding.remediation:
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph("<b>Recommended Fix:</b>", self.styles['BodyText']))
            elements.append(Paragraph(
                f"<font face='Courier' size='8'>{finding.remediation[:300]}</font>",
                self.styles['CodeStyle']
            ))
        
        # Risk score
        if finding.risk_score:
            elements.append(Paragraph(
                f"<font size='9' color='#64748b'>Risk Score: {finding.risk_score:.2f}</font>",
                self.styles['Normal']
            ))
        
        # Separator line
        line_data = [['─' * 100]]
        line_table = Table(line_data, colWidths=[6.5*inch])
        line_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(line_table)
        
        return elements
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status"""
        colors_map = {
            'COMPLETED': '#22c55e',
            'NEEDS_REVIEW': '#eab308',
            'PROCESSING': '#3b82f6',
            'FAILED': '#ef4444'
        }
        return colors_map.get(status, '#64748b')
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level"""
        colors_map = {
            'CRITICAL': '#dc2626',
            'HIGH': '#f59e0b',
            'MEDIUM': '#eab308',
            'LOW': '#22c55e'
        }
        return colors_map.get(risk_level, '#64748b')
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity"""
        return self._get_risk_color(severity)


def generate_audit_report(audit_id: str) -> BytesIO:
    """
    Convenience function to generate PDF report
    
    Args:
        audit_id: Audit ID (e.g., "AUD-000001")
        
    Returns:
        BytesIO buffer containing PDF data
    """
    generator = AuditReportGenerator()
    return generator.generate_report(audit_id)
