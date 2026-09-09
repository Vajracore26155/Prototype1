"""
Professional PDF Report Generator for Security Audit Results
Enterprise-grade document design with clean typography and layout.
"""
from datetime import datetime
from io import BytesIO
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Line

from app.database import Audit, Finding, Configuration, get_db_session


class ReportCanvas(canvas.Canvas):
    """Custom canvas for headers and footers"""
    
    def __init__(self, *args, **kwargs):
        self.audit_id = kwargs.pop('audit_id', 'N/A')
        self.report_date = datetime.utcnow().strftime('%B %d, %Y')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            if page_num > 1:  # Skip header/footer on cover
                self.draw_page_elements(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_elements(self, page_num, page_count):
        """Draw header and footer"""
        # Header line
        self.setStrokeColor(colors.HexColor('#667eea'))
        self.setLineWidth(1.5)
        self.line(0.75*inch, 10.5*inch, 7.75*inch, 10.5*inch)
        
        # Header text
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(0.75*inch, 10.65*inch, 'Tatva Network Security Audit')
        
        # Footer line
        self.setStrokeColor(colors.HexColor('#e2e8f0'))
        self.setLineWidth(0.5)
        self.line(0.75*inch, 0.65*inch, 7.75*inch, 0.65*inch)
        
        # Footer text
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#94a3b8'))
        self.drawString(0.75*inch, 0.5*inch, f'Report ID: {self.audit_id}')
        self.drawRightString(7.75*inch, 0.5*inch, f'Page {page_num} of {page_count}')
        self.drawCentredString(4.25*inch, 0.5*inch, self.report_date)


class AuditReportGenerator:
    """Generate professional PDF audit reports"""
    
    # Professional color palette
    COLORS = {
        'primary': colors.HexColor('#667eea'),
        'dark': colors.HexColor('#1e293b'),
        'medium': colors.HexColor('#475569'),
        'light': colors.HexColor('#64748b'),
        'lighter': colors.HexColor('#94a3b8'),
        'critical': colors.HexColor('#dc2626'),
        'high': colors.HexColor('#f97316'),
        'medium_sev': colors.HexColor('#eab308'),
        'low': colors.HexColor('#22c55e'),
        'pass': colors.HexColor('#10b981'),
        'fail': colors.HexColor('#ef4444'),
        'warning': colors.HexColor('#f59e0b'),
        'info': colors.HexColor('#3b82f6'),
    }
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        """Create professional paragraph styles"""
        
        def add_style(style):
            if style.name not in self.styles:
                self.styles.add(style)
        
        # Cover title
        add_style(ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=self.COLORS['dark'],
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        ))
        
        # Cover subtitle
        add_style(ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=self.COLORS['medium'],
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Cover info
        add_style(ParagraphStyle(
            name='CoverInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COLORS['light'],
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section title
        add_style(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=self.COLORS['dark'],
            spaceAfter=16,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            borderPadding=(0, 0, 8, 0),
        ))
        
        # Subsection
        add_style(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=self.COLORS['medium'],
            spaceAfter=10,
            spaceBefore=14,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        add_style(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLORS['medium'],
            spaceAfter=10,
            leading=14,
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        ))
        
        # Label style
        add_style(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.COLORS['lighter'],
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        # Value style
        add_style(ParagraphStyle(
            name='Value',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COLORS['dark'],
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
    def generate_report(self, audit_id: str) -> BytesIO:
        """
        Generate PDF report for an audit
        
        Args:
            audit_id: Audit ID (e.g., "AUD-000001")
            
        Returns:
            BytesIO buffer containing PDF data
        """
        db = get_db_session()
        try:
            # Fetch data
            audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
            if not audit:
                raise ValueError(f"Audit {audit_id} not found")
                
            config = db.query(Configuration).filter(
                Configuration.id == audit.configuration_id
            ).first()
            
            findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
            
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch,
                title=f"Security Audit Report - {audit_id}",
                author="Tatva Network Security Auditor"
            )
            
            # Build content
            story = []
            
            # Cover page
            story.extend(self._build_cover(audit, config))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._build_executive_summary(audit, findings))
            story.append(PageBreak())
            
            # Compliance overview
            story.extend(self._build_compliance_section(audit, findings))
            
            # Findings
            story.extend(self._build_findings_section(findings))
            
            # Build with custom canvas
            doc.build(
                story,
                canvasmaker=lambda *args, **kwargs: ReportCanvas(
                    *args, audit_id=audit_id, **kwargs
                )
            )
            
            buffer.seek(0)
            return buffer
            
        finally:
            db.close()
            
    def _build_cover(self, audit: Audit, config: Configuration) -> List:
        """Build professional cover page"""
        elements = []
        
        # Top spacing
        elements.append(Spacer(1, 2.5*inch))
        
        # Title
        elements.append(Paragraph(
            "NETWORK SECURITY<br/>AUDIT REPORT",
            self.styles['CoverTitle']
        ))
        
        elements.append(Spacer(1, 0.4*inch))
        
        # Accent line
        line = Drawing(2*inch, 2)
        line.add(Line(0, 1, 2*inch, 1, strokeColor=self.COLORS['primary'], strokeWidth=3))
        elements.append(line)
        
        elements.append(Spacer(1, 0.6*inch))
        
        # Report details
        elements.append(Paragraph(
            f"<b>Audit ID:</b> {audit.audit_id}",
            self.styles['CoverInfo']
        ))
        
        if config:
            elements.append(Paragraph(
                f"<b>Configuration:</b> {config.original_filename}",
                self.styles['CoverInfo']
            ))
            elements.append(Paragraph(
                f"<b>Vendor:</b> {config.vendor or 'Unknown'}",
                self.styles['CoverInfo']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        elements.append(Paragraph(
            f"<b>Generated:</b> {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
            self.styles['CoverInfo']
        ))
        
        elements.append(Paragraph(
            f"<b>Status:</b> {audit.status}",
            self.styles['CoverInfo']
        ))
        
        # Footer
        elements.append(Spacer(1, 1.5*inch))
        elements.append(Paragraph(
            "Tatva Network Security Compliance Auditor",
            self.styles['CoverSubtitle']
        ))
        
        return elements
        
    def _build_executive_summary(self, audit: Audit, findings: List[Finding]) -> List:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        
        # Add accent line
        line = Drawing(7*inch, 2)
        line.add(Line(0, 0, 1*inch, 0, strokeColor=self.COLORS['primary'], strokeWidth=2))
        elements.append(line)
        elements.append(Spacer(1, 0.25*inch))
        
        # Overview paragraph
        total = len(findings)
        passed = sum(1 for f in findings if f.status == 'PASS')
        failed = sum(1 for f in findings if f.status == 'FAIL')
        warnings = sum(1 for f in findings if f.status == 'WARNING')
        
        overview_text = f"""
        This report presents the results of an automated network security compliance audit
        performed on the submitted configuration file. The audit evaluated {total} security 
        controls across multiple domains including access control, encryption, authentication,
        and network security protocols. The analysis identified {failed} non-compliant 
        configuration{'s' if failed != 1 else ''} requiring immediate attention and {warnings} 
        configuration{'s' if warnings != 1 else ''} flagged for review.
        """
        
        elements.append(Paragraph(overview_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Key metrics table
        elements.append(Paragraph("Key Metrics", self.styles['Subsection']))
        
        compliance_pct = (passed / total * 100) if total > 0 else 0
        risk_level = audit.risk_level or 'N/A'
        risk_score = f"{audit.risk_score:.1f}/10.0" if audit.risk_score else 'N/A'
        
        data = [
            ['Metric', 'Value'],
            ['Total Controls Evaluated', str(total)],
            ['Compliant Controls', str(passed)],
            ['Non-Compliant Controls', str(failed)],
            ['Warnings', str(warnings)],
            ['Compliance Score', f'{compliance_pct:.1f}%'],
            ['Risk Level', risk_level],
            ['Risk Score', risk_score],
        ]
        
        table = Table(data, colWidths=[3.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['medium']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Human review alert if needed
        if audit.requires_human_review:
            elements.append(self._build_review_alert(audit))
        
        return elements
        
    def _build_review_alert(self, audit: Audit) -> KeepTogether:
        """Build human review alert box"""
        elements = []
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("⚠️ Manual Review Required", self.styles['Subsection']))
        
        confidence = audit.interpretation_confidence * 100 if audit.interpretation_confidence else 0
        uninterpreted = audit.uninterpreted_lines_count or 0
        total_lines = audit.total_lines_count or 0
        uninterpreted_pct = (uninterpreted / total_lines * 100) if total_lines > 0 else 0
        
        alert_text = f"""
        This configuration contains proprietary or uncommon syntax that could not be fully 
        interpreted by automated analysis. A security expert should manually validate the 
        findings to ensure accuracy and completeness.
        <br/><br/>
        <b>Interpretation Confidence:</b> {confidence:.1f}%<br/>
        <b>Uninterpreted Lines:</b> {uninterpreted} of {total_lines} ({uninterpreted_pct:.1f}%)<br/>
        <b>Reason:</b> {audit.review_reason or 'Interpretation uncertainty detected'}
        """
        
        alert_para = Paragraph(alert_text, self.styles['BodyText'])
        
        # Create table for background color
        table = Table([[alert_para]], colWidths=[6*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')),
            ('LEFTPADDING', (0, 0), (-1, -1), 16),
            ('RIGHTPADDING', (0, 0), (-1, -1), 16),
            ('TOPPADDING', (0, 0), (-1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        return KeepTogether(elements)
        
    def _build_compliance_section(self, audit: Audit, findings: List[Finding]) -> List:
        """Build compliance overview section"""
        elements = []
        
        elements.append(Paragraph("Compliance Analysis", self.styles['SectionTitle']))
        
        # Add accent line
        line = Drawing(7*inch, 2)
        line.add(Line(0, 0, 1*inch, 0, strokeColor=self.COLORS['primary'], strokeWidth=2))
        elements.append(line)
        elements.append(Spacer(1, 0.25*inch))
        
        # Findings by status
        elements.append(Paragraph("Results by Status", self.styles['Subsection']))
        
        status_counts = {
            'PASS': sum(1 for f in findings if f.status == 'PASS'),
            'FAIL': sum(1 for f in findings if f.status == 'FAIL'),
            'WARNING': sum(1 for f in findings if f.status == 'WARNING'),
            'NOT_APPLICABLE': sum(1 for f in findings if f.status == 'NOT_APPLICABLE'),
        }
        
        total = len(findings)
        
        status_data = [['Status', 'Count', 'Percentage']]
        for status, count in status_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            status_data.append([status.replace('_', ' ').title(), str(count), f'{pct:.1f}%'])
        
        table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['medium']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Findings by severity
        elements.append(Paragraph("Findings by Severity", self.styles['Subsection']))
        
        severity_counts = {
            'CRITICAL': sum(1 for f in findings if f.severity == 'CRITICAL'),
            'HIGH': sum(1 for f in findings if f.severity == 'HIGH'),
            'MEDIUM': sum(1 for f in findings if f.severity == 'MEDIUM'),
            'LOW': sum(1 for f in findings if f.severity == 'LOW'),
        }
        
        severity_data = [['Severity', 'Count', 'Percentage']]
        for severity, count in severity_counts.items():
            pct = (count / total * 100) if total > 0 else 0
            severity_data.append([severity.title(), str(count), f'{pct:.1f}%'])
        
        table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['medium']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
        
    def _build_findings_section(self, findings: List[Finding]) -> List:
        """Build detailed findings section"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Detailed Findings", self.styles['SectionTitle']))
        
        # Add accent line
        line = Drawing(7*inch, 2)
        line.add(Line(0, 0, 1*inch, 0, strokeColor=self.COLORS['primary'], strokeWidth=2))
        elements.append(line)
        elements.append(Spacer(1, 0.25*inch))
        
        # Group findings by severity
        critical = [f for f in findings if f.severity == 'CRITICAL' and f.status == 'FAIL']
        high = [f for f in findings if f.severity == 'HIGH' and f.status == 'FAIL']
        medium = [f for f in findings if f.severity == 'MEDIUM' and f.status == 'FAIL']
        low = [f for f in findings if f.severity == 'LOW' and f.status == 'FAIL']
        warnings = [f for f in findings if f.status == 'WARNING']
        
        # Critical findings
        if critical:
            elements.extend(self._build_severity_group('Critical Findings', critical, self.COLORS['critical']))
        
        # High findings
        if high:
            elements.extend(self._build_severity_group('High Severity Findings', high, self.COLORS['high']))
        
        # Medium findings
        if medium:
            elements.extend(self._build_severity_group('Medium Severity Findings', medium, self.COLORS['medium_sev']))
        
        # Low findings
        if low:
            elements.extend(self._build_severity_group('Low Severity Findings', low, self.COLORS['low']))
        
        # Warnings
        if warnings:
            elements.extend(self._build_severity_group('Warnings', warnings, self.COLORS['warning']))
        
        # If no failures, show success message
        if not (critical or high or medium or low or warnings):
            elements.append(Paragraph(
                "✓ All security controls passed compliance checks. No issues found.",
                self.styles['BodyText']
            ))
        
        return elements
        
    def _build_severity_group(self, title: str, findings: List[Finding], color) -> List:
        """Build a group of findings by severity"""
        elements = []
        
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"{title} ({len(findings)})", self.styles['Subsection']))
        elements.append(Spacer(1, 0.1*inch))
        
        for finding in findings:
            elements.extend(self._build_finding_entry(finding, color))
        
        return elements
        
    def _build_finding_entry(self, finding: Finding, color) -> List:
        """Build a single finding entry"""
        elements = []
        
        # Finding title
        title_text = f"<b>{finding.rule_id}:</b> {finding.title}"
        elements.append(Paragraph(title_text, self.styles['Value']))
        
        # Description
        if finding.description:
            elements.append(Paragraph(finding.description, self.styles['BodyText']))
        
        # Details table
        details = []
        
        if finding.expected:
            details.append(['Expected', finding.expected])
        if finding.actual:
            details.append(['Actual', finding.actual])
        if finding.field_path:
            details.append(['Configuration Path', finding.field_path])
        
        if details:
            table = Table(details, colWidths=[1.2*inch, 4.8*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Courier'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS['light']),
                ('TEXTCOLOR', (1, 0), (1, -1), self.COLORS['medium']),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(table)
        
        # Remediation
        if finding.remediation:
            elements.append(Paragraph("<b>Remediation:</b>", self.styles['Label']))
            elements.append(Paragraph(finding.remediation, self.styles['BodyText']))
        
        # Separator
        separator = Drawing(6*inch, 1)
        separator.add(Line(0, 0, 6*inch, 0, strokeColor=colors.HexColor('#e2e8f0'), strokeWidth=0.5))
        elements.append(separator)
        elements.append(Spacer(1, 0.15*inch))
        
        return elements


# Public API
def generate_audit_report(audit_id: str) -> BytesIO:
    """
    Generate PDF report for an audit
    
    Args:
        audit_id: Audit ID (e.g., "AUD-000001")
        
    Returns:
        BytesIO buffer containing PDF data
    """
    generator = AuditReportGenerator()
    return generator.generate_report(audit_id)
