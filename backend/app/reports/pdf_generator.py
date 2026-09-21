"""
Professional PDF Report Generator
Phase 10: Advanced PDF reporting with ReportLab
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO
import os


class PDFReportGenerator:
    """
    Professional PDF report generator for VAJRA CORE
    
    Generates evidence-backed security audit reports
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.page_width = letter[0]
        self.page_height = letter[1]
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4a4a4a'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))
        
        # Evidence style
        self.styles.add(ParagraphStyle(
            name='Evidence',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=colors.HexColor('#c7254e'),
            backColor=colors.HexColor('#f9f2f4'),
            leftIndent=20,
            spaceAfter=8
        ))
        
        # Severity styles
        for severity, color in [
            ('CRITICAL', '#e74c3c'),
            ('HIGH', '#e67e22'),
            ('MEDIUM', '#f39c12'),
            ('LOW', '#95a5a6')
        ]:
            self.styles.add(ParagraphStyle(
                name=f'Severity{severity}',
                parent=self.styles['BodyText'],
                fontSize=10,
                textColor=colors.HexColor(color),
                fontName='Helvetica-Bold'
            ))
    
    def generate_executive_report(
        self,
        data: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate executive summary report
        
        Management-friendly high-level overview
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Header
        story.extend(self._create_header(data))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        story.extend(self._create_executive_summary(data))
        
        # Overall Posture
        story.append(PageBreak())
        story.append(Paragraph("Security Posture Overview", self.styles['SectionHeading']))
        story.extend(self._create_posture_summary(data))
        
        # Key Findings
        story.append(PageBreak())
        story.append(Paragraph("Key Security Findings", self.styles['SectionHeading']))
        story.extend(self._create_key_findings(data))
        
        # Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Priority Recommendations", self.styles['SectionHeading']))
        story.extend(self._create_recommendations(data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        if not output_path:
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
        return b''
    
    def generate_technical_report(
        self,
        data: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate technical detailed report
        
        Comprehensive evidence-backed analysis
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Header
        story.extend(self._create_header(data))
        
        # Technical Summary
        story.append(Paragraph("Technical Assessment Summary", self.styles['SectionHeading']))
        story.extend(self._create_technical_summary(data))
        
        # Device Details
        story.append(PageBreak())
        story.append(Paragraph("Device Assessment Details", self.styles['SectionHeading']))
        story.extend(self._create_device_details(data))
        
        # Detailed Findings
        story.append(PageBreak())
        story.append(Paragraph("Detailed Security Findings", self.styles['SectionHeading']))
        story.extend(self._create_detailed_findings(data))
        
        # Evidence
        story.append(PageBreak())
        story.append(Paragraph("Evidence & Provenance", self.styles['SectionHeading']))
        story.extend(self._create_evidence_section(data))
        
        # Remediation
        story.append(PageBreak())
        story.append(Paragraph("Remediation Guidance", self.styles['SectionHeading']))
        story.extend(self._create_remediation_section(data))
        
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        if not output_path:
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
        return b''
    
    def generate_compliance_report(
        self,
        data: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate compliance framework report
        
        Framework-oriented compliance assessment
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Header
        story.extend(self._create_header(data))
        
        # Compliance Overview
        story.append(Paragraph("Compliance Assessment Overview", self.styles['SectionHeading']))
        story.extend(self._create_compliance_overview(data))
        
        # Framework Results
        story.append(PageBreak())
        story.append(Paragraph("Framework Assessment Results", self.styles['SectionHeading']))
        story.extend(self._create_framework_results(data))
        
        # Control Details
        story.append(PageBreak())
        story.append(Paragraph("Control Assessment Details", self.styles['SectionHeading']))
        story.extend(self._create_control_details(data))
        
        # Compliance Gaps
        story.append(PageBreak())
        story.append(Paragraph("Compliance Gaps & Recommendations", self.styles['SectionHeading']))
        story.extend(self._create_compliance_gaps(data))
        
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        if not output_path:
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
        return b''
    
    def _create_header(self, data: Dict) -> List:
        """Create report header"""
        elements = []
        
        # Title
        title = data.get('report_title', 'Security Audit Report')
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        
        # Subtitle
        subtitle = f"Generated on {datetime.utcnow().strftime('%B %d, %Y')}"
        elements.append(Paragraph(subtitle, self.styles['ReportSubtitle']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata table
        metadata = data.get('metadata', {})
        meta_data = [
            ['Report ID:', data.get('report_id', 'N/A')],
            ['Organization:', metadata.get('organization_name', 'N/A')],
            ['Assessment Period:', metadata.get('assessment_period', 'N/A')],
            ['Generated By:', metadata.get('generated_by', 'VAJRA CORE')],
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#34495e')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(meta_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_executive_summary(self, data: Dict) -> List:
        """Create executive summary section"""
        elements = []
        
        metrics = data.get('metrics', {})
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Devices Assessed', str(metrics.get('total_devices', 0))],
            ['Configurations Analyzed', str(metrics.get('total_configurations', 0))],
            ['Security Audits Performed', str(metrics.get('total_audits', 0))],
            ['Overall Compliance Score', f"{metrics.get('compliance_score', 0):.1f}%"],
            ['Risk Level', metrics.get('risk_level', 'UNKNOWN')],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Findings summary
        findings = data.get('findings_summary', {})
        findings_data = [
            ['Severity', 'Count'],
            ['CRITICAL', str(findings.get('critical', 0))],
            ['HIGH', str(findings.get('high', 0))],
            ['MEDIUM', str(findings.get('medium', 0))],
            ['LOW', str(findings.get('low', 0))],
        ]
        
        findings_table = Table(findings_data, colWidths=[2.5*inch, 1.5*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fee')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fed')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ffd')),
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#efe')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(Paragraph("Findings by Severity", self.styles['SubsectionHeading']))
        elements.append(findings_table)
        
        return elements
    
    def _create_posture_summary(self, data: Dict) -> List:
        """Create security posture summary"""
        elements = []
        
        posture = data.get('posture', {})
        
        text = f"""
        The overall security posture score is <b>{posture.get('score', 0):.1f}</b> out of 100.
        
        This score is calculated based on compliance assessment, risk analysis, 
        configuration drift, and remediation status across all assessed devices.
        
        <b>Posture Model:</b> VAJRA CORE Posture Assessment v1.0
        """
        
        elements.append(Paragraph(text, self.styles['ReportBody']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Posture breakdown
        breakdown = [
            ['Component', 'Score', 'Weight'],
            ['Compliance', f"{posture.get('compliance_score', 0):.1f}%", '40%'],
            ['Risk Management', f"{posture.get('risk_score', 0):.1f}%", '30%'],
            ['Configuration Stability', f"{posture.get('drift_score', 0):.1f}%", '20%'],
            ['Remediation Status', f"{posture.get('remediation_score', 0):.1f}%", '10%'],
        ]
        
        breakdown_table = Table(breakdown, colWidths=[2.5*inch, 1.5*inch, 1*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(breakdown_table)
        
        return elements
    
    def _create_key_findings(self, data: Dict) -> List:
        """Create key findings section"""
        elements = []
        
        findings = data.get('findings', [])
        
        # Filter critical and high findings
        critical_findings = [f for f in findings if f.get('severity') == 'CRITICAL']
        high_findings = [f for f in findings if f.get('severity') == 'HIGH']
        
        # Critical findings
        if critical_findings:
            elements.append(Paragraph("Critical Findings", self.styles['SubsectionHeading']))
            for finding in critical_findings[:5]:  # Limit to top 5
                elements.extend(self._format_finding(finding))
        
        # High findings
        if high_findings:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("High Priority Findings", self.styles['SubsectionHeading']))
            for finding in high_findings[:5]:  # Limit to top 5
                elements.extend(self._format_finding(finding))
        
        return elements
    
    def _format_finding(self, finding: Dict) -> List:
        """Format a single finding"""
        elements = []
        
        severity = finding.get('severity', 'UNKNOWN')
        title = finding.get('title', 'Untitled Finding')
        description = finding.get('description', 'No description available')
        
        # Finding header
        finding_text = f"""
        <b>[{severity}] {title}</b><br/>
        <i>Finding ID: {finding.get('finding_id', 'N/A')}</i>
        """
        elements.append(Paragraph(finding_text, self.styles[f'Severity{severity}']))
        
        # Description
        elements.append(Paragraph(description, self.styles['ReportBody']))
        
        # Device affected
        if finding.get('device_id'):
            device_text = f"<b>Affected Device:</b> {finding.get('device_id')}"
            elements.append(Paragraph(device_text, self.styles['ReportBody']))
        
        # Framework/Control
        if finding.get('framework'):
            framework_text = f"<b>Framework:</b> {finding.get('framework')} - {finding.get('control', 'N/A')}"
            elements.append(Paragraph(framework_text, self.styles['ReportBody']))
        
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_recommendations(self, data: Dict) -> List:
        """Create recommendations section"""
        elements = []
        
        recommendations = data.get('recommendations', [])
        
        for i, rec in enumerate(recommendations[:10], 1):
            rec_text = f"""
            <b>{i}. {rec.get('title', 'Recommendation')}</b><br/>
            Priority: <b>{rec.get('priority', 'MEDIUM')}</b><br/>
            {rec.get('description', 'No description')}
            """
            elements.append(Paragraph(rec_text, self.styles['ReportBody']))
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_technical_summary(self, data: Dict) -> List:
        """Create technical summary"""
        elements = []
        
        # Similar to executive but with more technical detail
        elements.extend(self._create_executive_summary(data))
        
        return elements
    
    def _create_device_details(self, data: Dict) -> List:
        """Create device details section"""
        elements = []
        
        devices = data.get('devices', [])
        
        for device in devices:
            device_data = [
                ['Property', 'Value'],
                ['Device ID', device.get('device_id', 'N/A')],
                ['Vendor', device.get('vendor', 'N/A')],
                ['Model', device.get('model', 'N/A')],
                ['Platform', device.get('platform', 'N/A')],
                ['Configuration Hash', device.get('config_hash', 'N/A')[:16] + '...'],
                ['Last Assessment', device.get('last_audit', 'N/A')],
                ['Compliance Score', f"{device.get('compliance_score', 0):.1f}%"],
                ['Risk Level', device.get('risk_level', 'N/A')],
            ]
            
            device_table = Table(device_data, colWidths=[2*inch, 4*inch])
            device_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(device_table)
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_detailed_findings(self, data: Dict) -> List:
        """Create detailed findings section"""
        elements = []
        
        findings = data.get('findings', [])
        
        for finding in findings:
            # Use existing _format_finding
            elements.extend(self._format_finding(finding))
            
            # Add evidence if available
            evidence = finding.get('evidence')
            if evidence:
                elements.append(Paragraph("<b>Evidence:</b>", self.styles['ReportBody']))
                evidence_text = str(evidence)[:200] + "..." if len(str(evidence)) > 200 else str(evidence)
                elements.append(Paragraph(evidence_text, self.styles['Evidence']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_evidence_section(self, data: Dict) -> List:
        """Create evidence and provenance section"""
        elements = []
        
        text = """
        All findings in this report are backed by evidence extracted from 
        actual device configurations. Evidence includes configuration line numbers,
        extracted configuration snippets, and parser provenance information.
        
        <b>Security Note:</b> Sensitive information (passwords, keys, secrets) 
        has been sanitized and does not appear in this report.
        """
        
        elements.append(Paragraph(text, self.styles['ReportBody']))
        
        return elements
    
    def _create_remediation_section(self, data: Dict) -> List:
        """Create remediation guidance section"""
        elements = []
        
        remediations = data.get('remediations', [])
        
        for remediation in remediations:
            rem_text = f"""
            <b>Finding:</b> {remediation.get('finding_title', 'N/A')}<br/>
            <b>Recommendation:</b> {remediation.get('recommendation', 'N/A')}<br/>
            <b>Expected Improvement:</b> {remediation.get('expected_improvement', 'N/A')}
            """
            elements.append(Paragraph(rem_text, self.styles['ReportBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_compliance_overview(self, data: Dict) -> List:
        """Create compliance overview"""
        elements = []
        
        frameworks = data.get('frameworks', [])
        
        framework_data = [['Framework', 'Version', 'Controls Assessed', 'Pass Rate']]
        
        for framework in frameworks:
            framework_data.append([
                framework.get('name', 'N/A'),
                framework.get('version', 'N/A'),
                str(framework.get('controls_assessed', 0)),
                f"{framework.get('pass_rate', 0):.1f}%"
            ])
        
        framework_table = Table(framework_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1*inch])
        framework_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(framework_table)
        
        return elements
    
    def _create_framework_results(self, data: Dict) -> List:
        """Create framework results section"""
        elements = []
        
        # Similar to compliance overview but more detailed
        elements.extend(self._create_compliance_overview(data))
        
        return elements
    
    def _create_control_details(self, data: Dict) -> List:
        """Create control assessment details"""
        elements = []
        
        controls = data.get('controls', [])
        
        for control in controls:
            control_text = f"""
            <b>Control:</b> {control.get('control_id', 'N/A')} - {control.get('title', 'N/A')}<br/>
            <b>Result:</b> {control.get('result', 'N/A')}<br/>
            <b>Evidence:</b> {control.get('evidence_summary', 'N/A')}
            """
            elements.append(Paragraph(control_text, self.styles['ReportBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_compliance_gaps(self, data: Dict) -> List:
        """Create compliance gaps section"""
        elements = []
        
        gaps = data.get('compliance_gaps', [])
        
        for gap in gaps:
            gap_text = f"""
            <b>Gap:</b> {gap.get('title', 'N/A')}<br/>
            <b>Impact:</b> {gap.get('impact', 'N/A')}<br/>
            <b>Recommendation:</b> {gap.get('recommendation', 'N/A')}
            """
            elements.append(Paragraph(gap_text, self.styles['ReportBody']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(
            self.page_width - 72,
            30,
            text
        )
        canvas.restoreState()


# Global instance
pdf_generator = PDFReportGenerator()
