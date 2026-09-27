"""
Enhanced Professional PDF Report Generator for Vendor System
Phase 4: Comprehensive vendor-specific reporting with detailed evidence traceability

Features:
- Vendor-specific branding and customization
- Comprehensive technical details and evidence
- AI parsing confidence and interpretation metrics
- Configuration file previews with highlighted issues
- Detailed remediation workflows with priority sequencing
- Evidence traceability linking findings to specific config lines
- Professional executive summary with business impact analysis
- Compliance framework mappings and standards references
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether, HRFlowable, NextPageTemplate,
    PageTemplate, Frame
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from io import BytesIO
import os
import logging
from xml.sax.saxutils import escape as _xml_escape

logger = logging.getLogger(__name__)


def _esc(v: Any) -> str:
    """Escape user-controlled text for ReportLab Paragraph (XML)."""
    if v is None:
        return "N/A"
    try:
        s = str(v)
    except Exception:
        return "N/A"
    # escape &, <, > ; keep <b>, <i>, <font>, <br/> we generate ourselves (callers escape inputs first)
    return _xml_escape(s)


class EnhancedPDFReportGenerator:
    """
    Enhanced professional PDF report generator for vendor-specific security reports
    
    Generates comprehensive, evidence-backed security audit reports with:
    - Professional branding and layout
    - Detailed technical analysis
    - Evidence traceability
    - Business impact assessment
    - Remediation guidance
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_enhanced_styles()
        self.page_width = letter[0]
        self.page_height = letter[1]
        self.colors = self._define_color_palette()
    
    def _define_color_palette(self) -> Dict[str, str]:
        """TATVA monochrome palette — matte black / white / gray only"""
        return {
            'primary': '#1C1C1C',
            'secondary': '#333333',
            'success': '#1C1C1C',
            'warning': '#4B5468',
            'danger': '#1C1C1C',
            'critical': '#000000',
            'info': '#4B5468',
            'light': '#F1F3F7',
            'dark': '#1C1C1C',
            'muted': '#6E6E6E'
        }
    
    def _create_enhanced_styles(self):
        """Create comprehensive custom paragraph styles"""
        
        # Executive styles — big, bold, monochrome
        self.styles.add(ParagraphStyle(
            name='ExecutiveTitle',
            parent=self.styles['Heading1'],
            fontSize=44,
            leading=44,
            textColor=colors.HexColor('#1C1C1C'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyTitle',
            parent=self.styles['Heading2'],
            fontSize=15,
            leading=18,
            textColor=colors.HexColor('#1C1C1C'),
            spaceAfter=26,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Professional section styles
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=17,
            leading=20,
            textColor=colors.white,
            spaceAfter=16,
            spaceBefore=28,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=10,
            backColor=colors.HexColor('#1C1C1C')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#1C1C1C'),
            spaceAfter=10,
            spaceBefore=18,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='MinorHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Content styles
        self.styles.add(ParagraphStyle(
            name='Professional',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='Technical',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            leftIndent=15,
            fontName='Helvetica',
            leading=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='EnhancedCode',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#c7254e'),
            backColor=colors.HexColor('#f8f9fa'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=8,
            spaceBefore=5,
            fontName='Courier',
            borderWidth=1,
            borderColor=colors.HexColor('#dee2e6'),
            borderPadding=6
        ))
        
        # Severity — grayscale weight ladder (no color)
        severity_colors = {
            'CRITICAL': '#000000',
            'HIGH': '#1C1C1C',
            'MEDIUM': '#4B5468',
            'LOW': '#9AA3B2'
        }
        
        for severity, color in severity_colors.items():
            self.styles.add(ParagraphStyle(
                name=f'Severity{severity}',
                parent=self.styles['BodyText'],
                fontSize=11,
                textColor=colors.HexColor(color),
                fontName='Helvetica-Bold',
                spaceAfter=8
            ))
        
        # Status styles — monochrome
        self.styles.add(ParagraphStyle(
            name='StatusPass',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#1C1C1C'),
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='StatusFail',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica-Bold'
        ))
        
        # Metadata styles
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#6c757d'),
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceAfter=10,
            fontStyle='italic'
        ))
    
    def generate_comprehensive_vendor_report(
        self,
        audit_data: Dict,
        config_data: Dict,
        vendor_info: Dict,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate comprehensive vendor-specific security audit report
        
        Args:
            audit_data: Enhanced audit details from vendor_get_audit_enhanced
            config_data: Configuration details from vendor_get_configuration_details  
            vendor_info: Vendor company information
            output_path: Optional file path to save PDF
            
        Returns:
            bytes: PDF content as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch,
            title=f"Security Audit Report - {vendor_info.get('company', 'Unknown Company')}"
        )
        
        story = []
        
        try:
            # Cover Page
            story.extend(self._create_professional_cover_page(audit_data, config_data, vendor_info))
            story.append(PageBreak())
            
            # Executive Summary
            story.extend(self._create_executive_summary_enhanced(audit_data, config_data, vendor_info))
            story.append(PageBreak())
            
            # Technical Assessment Overview
            story.extend(self._create_technical_assessment_overview(audit_data, config_data))
            story.append(PageBreak())
            
            # Configuration Analysis
            story.extend(self._create_configuration_analysis(config_data))
            story.append(PageBreak())
            
            # Security Findings Analysis
            story.extend(self._create_security_findings_analysis(audit_data))
            story.append(PageBreak())
            
            # Evidence and Provenance
            story.extend(self._create_evidence_section_enhanced(audit_data))
            story.append(PageBreak())
            
            # Remediation Guidance
            story.extend(self._create_remediation_guidance_enhanced(audit_data))
            story.append(PageBreak())
            
            # AI Analysis Appendix
            story.extend(self._create_ai_analysis_appendix(audit_data))
            story.append(PageBreak())
            
            # Technical Appendices
            story.extend(self._create_technical_appendices(audit_data, config_data))
            
            # Build PDF
            doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            
            if not output_path:
                pdf_bytes = buffer.getvalue()
                buffer.close()
                return pdf_bytes
            else:
                buffer.close()
                with open(output_path, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Error generating comprehensive vendor report: {e}")
            buffer.close()
            raise
    
    def _create_professional_cover_page(self, audit_data: Dict, config_data: Dict, vendor_info: Dict) -> List:
        """TATVA monochrome cover — vendor name, time, IDs, proper spacing"""
        elements = []
        
        # Brand eyebrow
        elements.append(Spacer(1, 0.7*inch))
        elements.append(Paragraph("TATVA BY TEAM VAJRACORE", self.styles['Caption']))
        elements.append(Spacer(1, 0.15*inch))
        elements.append(Paragraph("SECURITY AUDIT REPORT", self.styles['ExecutiveTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Company name
        company_name = _esc(vendor_info.get('company', 'Unknown Company'))
        elements.append(Paragraph(f"{company_name}", self.styles['CompanyTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Configuration information
        config_filename = _esc(audit_data.get('configuration', {}).get('filename', 'Unknown Configuration'))
        elements.append(Paragraph(f"Configuration: {config_filename}", self.styles['SubsectionTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report metadata table
        audit_summary = audit_data.get('audit_summary', {})
        report_date = datetime.now().strftime('%B %d, %Y')
        audit_date = audit_summary.get('completed_at', audit_summary.get('started_at', ''))
        if audit_date:
            audit_date = datetime.fromisoformat(audit_date.replace('Z', '+00:00')).strftime('%B %d, %Y')
        
        metadata_data = [
            ['Report Generated:', report_date],
            ['Audit Completed:', audit_date or 'In Progress'],
            ['Audit ID:', audit_data.get('audit_id', 'N/A')],
            ['Configuration ID:', audit_data.get('configuration', {}).get('config_id', 'N/A')],
            ['Compliance Score:', f"{audit_summary.get('compliance_score', 0)}%"],
            ['Risk Level:', audit_summary.get('risk_level', 'Unknown')],
            ['Vendor ID:', vendor_info.get('vendor_id', 'N/A')]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1C1C1C')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9E1EC')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(metadata_table)
        elements.append(Spacer(1, 1*inch))
        
        # Risk level indicator — monochrome weight, no color
        risk_level = audit_summary.get('risk_level', 'UNKNOWN').upper()
        
        elements.append(Paragraph(f'<b>OVERALL RISK ASSESSMENT</b>', self.styles['SubsectionTitle']))
        elements.append(Paragraph(
            f'<font color="#1C1C1C" size="18"><b>{risk_level} RISK</b></font>',
            self.styles['Professional']
        ))
        
        elements.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = """
        <i>This report contains a comprehensive security analysis of the submitted network device configuration. 
        All findings are based on industry best practices, compliance frameworks, and vendor-specific security guidelines. 
        Sensitive information has been sanitized and does not appear in this report. 
        This analysis was performed using advanced AI-assisted configuration parsing and security rule evaluation.</i>
        """
        elements.append(Paragraph(disclaimer, self.styles['Metadata']))
        
        return elements
    
    def _create_executive_summary_enhanced(self, audit_data: Dict, config_data: Dict, vendor_info: Dict) -> List:
        """Create comprehensive executive summary with business impact analysis"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionTitle']))
        
        # Overview paragraph
        audit_summary = audit_data.get('audit_summary', {})
        device_assessment = audit_data.get('device_assessment', {})
        parsing_analysis = audit_data.get('parsing_analysis', {})
        
        compliance_score = audit_summary.get('compliance_score', 0)
        risk_level = audit_summary.get('risk_level', 'Unknown')
        security_posture = device_assessment.get('security_posture', 'Unknown')
        
        overview_text = f"""
        This comprehensive security audit report analyzes the network device configuration submitted by 
        {vendor_info.get('company', 'your organization')}. Our advanced AI-powered analysis engine has 
        evaluated the configuration against industry security standards, vendor best practices, and 
        compliance frameworks.
        
        <b>Key Assessment Results:</b>
        • Overall Compliance Score: <b>{compliance_score}%</b>
        • Risk Level: <b>{risk_level}</b>
        • Security Posture: <b>{security_posture}</b>
        • AI Interpretation Confidence: <b>{(parsing_analysis.get('interpretation_confidence') or 0)*100:.1f}%</b>
        """
        
        elements.append(Paragraph(overview_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Findings summary table
        findings = audit_data.get('findings', {})
        findings_summary = findings.get('summary', {})
        by_severity = findings_summary.get('by_severity', {})
        by_status = findings_summary.get('by_status', {})
        
        findings_data = [
            ['Severity Level', 'Total Findings', 'Status Breakdown'],
            ['Critical', str(by_severity.get('critical', 0)), f"Failed: {by_severity.get('critical', 0)}"],
            ['High', str(by_severity.get('high', 0)), f"Failed: {by_status.get('fail', 0) if by_severity.get('high', 0) > 0 else 0}"],
            ['Medium', str(by_severity.get('medium', 0)), f"Mixed results"],
            ['Low', str(by_severity.get('low', 0)), f"Mostly informational"],
            ['', '', ''],
            ['Total Checks', str(findings.get('total_count', 0)), f"Pass: {by_status.get('pass', 0)} | Fail: {by_status.get('fail', 0)}"]
        ]
        
        findings_table = Table(findings_data, colWidths=[1.5*inch, 1.2*inch, 2*inch])
        findings_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#D9E1EC')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1C1C1C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#1C1C1C')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1C1C1C')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(findings_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Business impact assessment
        risk_assessment = audit_data.get('risk_assessment', {})
        business_risk_factors = risk_assessment.get('business_risk_factors', [])
        
        elements.append(Paragraph("Business Impact Assessment", self.styles['SubsectionTitle']))
        
        if business_risk_factors and business_risk_factors != ["No significant business risk factors identified"]:
            impact_text = "The following business risk factors have been identified:\n"
            for factor in business_risk_factors[:5]:  # Top 5 factors
                impact_text += f"• {factor}\n"
        else:
            impact_text = "No significant immediate business risk factors were identified in this analysis."
        
        elements.append(Paragraph(impact_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations summary
        remediation_guidance = audit_data.get('remediation_guidance', {})
        priority_1_count = len(remediation_guidance.get('priority_1_critical', []))
        priority_2_count = len(remediation_guidance.get('priority_2_important', []))
        estimated_effort = remediation_guidance.get('estimated_total_effort', 'Unknown')
        
        recommendations_text = f"""
        <b>Immediate Action Required:</b>
        • {priority_1_count} critical/high severity issues require immediate attention
        • {priority_2_count} medium severity issues should be addressed in the next maintenance window
        • Estimated total remediation effort: {estimated_effort}
        
        <b>Next Steps:</b>
        1. Review detailed findings in Section 4: Security Findings Analysis
        2. Implement priority 1 remediations immediately
        3. Schedule priority 2 remediations within 30 days
        4. Consider regular configuration audits to maintain security posture
        """
        
        elements.append(Paragraph(recommendations_text, self.styles['Professional']))
        
        return elements
    
    def _create_technical_assessment_overview(self, audit_data: Dict, config_data: Dict) -> List:
        """Create technical assessment overview with AI analysis metrics"""
        elements = []
        
        elements.append(Paragraph("TECHNICAL ASSESSMENT OVERVIEW", self.styles['SectionTitle']))
        
        # Configuration metadata
        elements.append(Paragraph("Configuration Analysis", self.styles['SubsectionTitle']))
        
        config_info = audit_data.get('configuration', {})
        vendor_detected = _esc(config_info.get('vendor', 'Unknown'))
        vendor_confidence = config_info.get('vendor_confidence', 0)
        _fh = config_info.get('file_hash') or 'N/A'
        _fh_short = (_fh[:16] + '...') if len(_fh) > 16 else _fh
        
        config_text = f"""
        <b>Device Information:</b>
        • Configuration File: {_esc(config_info.get('filename', 'N/A'))}
        • Detected Vendor: {vendor_detected} ({(vendor_confidence or 0)*100:.1f}% confidence)
        • File Hash: {_esc(_fh_short)}
        """
        
        elements.append(Paragraph(config_text, self.styles['Professional']))
        
        # AI Parsing Analysis
        parsing_analysis = audit_data.get('parsing_analysis', {})
        
        elements.append(Paragraph("AI Parsing and Interpretation Analysis", self.styles['SubsectionTitle']))
        
        total_lines = parsing_analysis.get('total_config_lines', 0)
        interpreted_lines = parsing_analysis.get('successfully_interpreted', 0)
        interpretation_rate = parsing_analysis.get('interpretation_rate', 0)
        confidence = parsing_analysis.get('interpretation_confidence', 0)
        
        parsing_text = f"""
        <b>Configuration Parsing Results:</b>
        • Total Configuration Lines: {total_lines:,}
        • Successfully Interpreted: {interpreted_lines:,} lines ({interpretation_rate:.1f}%)
        • Uninterpreted Sections: {parsing_analysis.get('uninterpreted_lines', 0):,} lines
        • Overall AI Confidence: {(confidence or 0)*100:.1f}%
        • Pending AI Mappings: {parsing_analysis.get('pending_ai_mappings', 0)}
        """
        
        if parsing_analysis.get('requires_human_review', False):
            parsing_text += f"\n\n<b>⚠ Human Review Required:</b> {parsing_analysis.get('review_reason', 'Expert review recommended')}"
        
        elements.append(Paragraph(parsing_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk Assessment Matrix
        elements.append(Paragraph("Risk Assessment Matrix", self.styles['SubsectionTitle']))
        
        risk_assessment = audit_data.get('risk_assessment', {})
        risk_breakdown = risk_assessment.get('risk_breakdown', {})
        
        risk_data = [
            ['Risk Category', 'Assessment', 'Impact Level'],
            ['Security Posture', str(risk_breakdown.get('security_posture', 'N/A')), 'Variable'],
            ['Compliance Gap', risk_breakdown.get('compliance_gap', 'N/A'), 'Business'],
            ['Configuration Complexity', risk_breakdown.get('configuration_complexity', 'N/A'), 'Operational'],
            ['Overall Risk Score', f"{risk_assessment.get('overall_risk_score', 0):.1f}/10", risk_assessment.get('risk_level', 'Unknown')]
        ]
        
        risk_table = Table(risk_data, colWidths=[1.8*inch, 2*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Device Assessment Summary
        device_assessment = audit_data.get('device_assessment', {})
        
        elements.append(Paragraph("Device Security Assessment", self.styles['SubsectionTitle']))
        
        assessment_text = f"""
        <b>Security Posture:</b> {device_assessment.get('security_posture', 'Not assessed')}
        
        <b>Configuration Quality:</b> {device_assessment.get('configuration_quality', 'Not assessed')}
        
        <b>Vendor Best Practices:</b> {device_assessment.get('vendor_best_practices', 'Not assessed')}
        
        <b>Maintenance Recommendations:</b>
        """
        
        maintenance_recs = device_assessment.get('maintenance_recommendations', [])
        for rec in maintenance_recs:
            assessment_text += f"• {rec}\n"
        
        elements.append(Paragraph(assessment_text, self.styles['Professional']))
        
        return elements
    
    def _create_configuration_analysis(self, config_data: Dict) -> List:
        """Create detailed configuration analysis section"""
        elements = []
        
        elements.append(Paragraph("CONFIGURATION ANALYSIS", self.styles['SectionTitle']))
        
        if not config_data:
            elements.append(Paragraph("Configuration details not available for analysis.", self.styles['Professional']))
            return elements
        
        # File integrity and metadata
        elements.append(Paragraph("File Integrity and Metadata", self.styles['SubsectionTitle']))
        
        file_integrity = config_data.get('file_integrity', {})
        file_content = config_data.get('file_content', {})
        file_stats = file_content.get('stats', {})
        
        integrity_text = f"""
        <b>File Verification:</b>
        • SHA-256 Hash: {file_integrity.get('sha256_hash', 'N/A')}
        • File Size: {self._format_bytes(file_stats.get('file_size_bytes', 0))}
        • Total Lines: {file_stats.get('total_lines', 0):,}
        • Storage Status: {'✓ Secure' if file_integrity.get('sanitized_path') else '⚠ Processing'}
        """
        
        elements.append(Paragraph(integrity_text, self.styles['Technical']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Vendor detection analysis
        elements.append(Paragraph("Vendor Detection Analysis", self.styles['SubsectionTitle']))
        
        vendor_detection = config_data.get('vendor_detection', {})
        
        vendor_detection = config_data.get('vendor_detection', {}) or {}
        vendor_text = f"""
        <b>Device Identification Results:</b>
        • Detected Vendor: {_esc(vendor_detection.get('detected_vendor', 'Unknown'))}
        • Detection Confidence: {(vendor_detection.get('confidence') or 0)*100:.1f}%
        • Analysis Method: AI pattern recognition and signature matching
        """
        
        elements.append(Paragraph(vendor_text, self.styles['Technical']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Configuration file preview (first 20 lines)
        elements.append(Paragraph("Configuration Preview (Sanitized)", self.styles['SubsectionTitle']))
        
        preview_content = file_content.get('preview', '') or ''
        if preview_content:
            # Take first 20 lines for the PDF
            preview_lines = preview_content.split('\n')[:20]
            preview_text = _esc('\n'.join(preview_lines)).replace('\n', '<br/>')
            
            elements.append(Paragraph(
                "First 20 lines of configuration (sensitive data sanitized):",
                self.styles['Metadata']
            ))
            elements.append(Paragraph(preview_text, self.styles['EnhancedCode']))
            
            if len(preview_lines) < file_stats.get('total_lines', 0):
                elements.append(Paragraph(
                    f"... {file_stats.get('total_lines', 0) - len(preview_lines):,} additional lines not shown",
                    self.styles['Caption']
                ))
        else:
            elements.append(Paragraph("Configuration content not available for preview.", self.styles['Technical']))
        
        # Processing status
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Processing Status", self.styles['SubsectionTitle']))
        
        processing_status = config_data.get('processing_status', {})
        
        status_data = [
            ['Processing Stage', 'Status', 'Details'],
            ['File Ingestion', '✓ Complete' if processing_status.get('ingested') else '⚠ Pending', 'File parsed and sanitized'],
            ['Vendor Detection', '✓ Complete' if processing_status.get('vendor_detected') else '⚠ Unknown', 'Device type identified'],
            ['Security Analysis', '✓ Complete' if processing_status.get('audited') else '⚠ Pending', 'Compliance rules evaluated'],
        ]
        
        status_table = Table(status_data, colWidths=[1.8*inch, 1.2*inch, 2.3*inch])
        status_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(status_table)
        
        return elements
    
    def _create_security_findings_analysis(self, audit_data: Dict) -> List:
        """Create detailed security findings analysis with evidence"""
        elements = []
        
        elements.append(Paragraph("SECURITY FINDINGS ANALYSIS", self.styles['SectionTitle']))
        
        findings = audit_data.get('findings', {})
        findings_details = findings.get('details', [])
        
        if not findings_details:
            elements.append(Paragraph("No security findings available for analysis.", self.styles['Professional']))
            return elements
        
        # Findings overview
        elements.append(Paragraph("Findings Overview", self.styles['SubsectionTitle']))
        
        findings_summary = findings.get('summary', {})
        by_severity = findings_summary.get('by_severity', {})
        by_status = findings_summary.get('by_status', {})
        
        overview_text = f"""
        <b>Total Security Checks:</b> {findings.get('total_count', 0)}
        
        <b>By Severity:</b>
        • Critical: {by_severity.get('critical', 0)} findings
        • High: {by_severity.get('high', 0)} findings  
        • Medium: {by_severity.get('medium', 0)} findings
        • Low: {by_severity.get('low', 0)} findings
        
        <b>By Status:</b>
        • Pass: {by_status.get('pass', 0)} checks
        • Fail: {by_status.get('fail', 0)} checks
        • Warning: {by_status.get('warning', 0)} checks
        """
        
        elements.append(Paragraph(overview_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))

        # Grayscale severity chart (monochrome, never breaks the report)
        try:
            elements.append(Paragraph("Severity Distribution (grayscale)", self.styles['SubsectionTitle']))
            chart = self._severity_chart(by_severity)
            if chart is not None:
                elements.append(chart)
                elements.append(Spacer(1, 0.15*inch))
        except Exception:
            pass

        # Detailed findings by severity — each severity starts cleanly
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        for severity in severity_order:
            severity_findings = [f for f in findings_details if f.get('severity') == severity and f.get('status') == 'FAIL']
            
            if not severity_findings:
                continue
                
            elements.append(Paragraph(f"{severity} Severity Findings", self.styles['MinorHeading']))
            
            for i, finding in enumerate(severity_findings[:10]):  # Limit to top 10 per severity
                elements.extend(self._format_detailed_finding(finding, i+1))
                elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _severity_chart(self, by_severity: Dict) -> Any:
        """Grayscale vertical bar chart: Critical/High/Medium/Low counts."""
        try:
            vals = [
                int(by_severity.get('critical', 0) or 0),
                int(by_severity.get('high', 0) or 0),
                int(by_severity.get('medium', 0) or 0),
                int(by_severity.get('low', 0) or 0),
            ]
            if sum(vals) == 0:
                return None
            drawing = Drawing(460, 170)
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 30
            chart.height = 120
            chart.width = 380
            chart.data = [vals]
            chart.categoryAxis.categoryNames = ['Critical', 'High', 'Medium', 'Low']
            chart.categoryAxis.labels.fontSize = 8
            chart.categoryAxis.labels.fontName = 'Helvetica-Bold'
            chart.valueAxis.labels.fontSize = 8
            chart.barLabels.fontSize = 8
            chart.barLabels.fontName = 'Helvetica-Bold'
            chart.bars[0].fillColor = colors.HexColor('#1C1C1C')
            drawing.add(chart)
            # Grayscale: single ink fill reads premium in B/W print; categories labeled below
            return drawing
        except Exception:
            return None

    def _format_detailed_finding(self, finding: Dict, number: int) -> List:
        """Format a single finding with comprehensive details"""
        elements = []
        
        severity = (finding.get('severity') or 'UNKNOWN').upper()
        if severity not in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'):
            severity = 'LOW'
        title = _esc(finding.get('rule_name', 'Unknown Finding'))
        
        # Finding header
        header_text = f"<b>{number}. [{severity}] {title}</b>"
        style_key = f'Severity{severity}' if f'Severity{severity}' in self.styles else 'Professional'
        elements.append(Paragraph(header_text, self.styles[style_key]))
        
        # Basic information
        description = _esc(finding.get('description', 'No description available'))
        elements.append(Paragraph(f"<b>Description:</b> {description}", self.styles['Professional']))
        
        # Technical details
        technical_details = finding.get('technical_details', {}) or {}
        if technical_details.get('expected') or technical_details.get('actual'):
            tech_text = f"""
            <b>Technical Analysis:</b>
            • Expected: {_esc(technical_details.get('expected', 'Not specified'))}
            • Actual: {_esc(technical_details.get('actual', 'Not specified'))}
            • Field Path: {_esc(technical_details.get('field_path', 'Not specified'))}
            """
            if technical_details.get('risk_score') is not None:
                tech_text += f"• Risk Score: {_esc(technical_details.get('risk_score'))}/10"
            
            elements.append(Paragraph(tech_text, self.styles['Technical']))
        
        # Evidence section
        evidence = finding.get('evidence', {}) or {}
        if evidence.get('evidence_text'):
            elements.append(Paragraph("<b>Evidence:</b>", self.styles['Technical']))
            raw_ev = evidence.get('evidence_text', '') or ''
            evidence_text = _esc(raw_ev[:300])
            if len(raw_ev) > 300:
                evidence_text += '...'
            elements.append(Paragraph(evidence_text, self.styles['EnhancedCode']))
            
            if evidence.get('evidence_line'):
                elements.append(Paragraph(
                    f"Configuration line {_esc(evidence.get('evidence_line'))}: {_esc(evidence.get('evidence_file', 'Unknown file'))}",
                    self.styles['Metadata']
                ))
        
        # Remediation guidance
        remediation = finding.get('remediation', {}) or {}
        if remediation.get('guidance') and remediation.get('guidance') != 'No remediation guidance available':
            rem_text = f"""
            <b>Remediation Guidance:</b>
            {_esc(remediation.get('guidance'))}
            
            <b>Priority:</b> {_esc(remediation.get('priority', 'Unknown'))}/5
            <b>Estimated Effort:</b> {_esc(remediation.get('estimated_effort', 'Unknown'))}
            <b>Business Impact:</b> {_esc(remediation.get('business_impact', 'Unknown'))}
            """
            elements.append(Paragraph(rem_text, self.styles['Technical']))
        
        # Compliance mapping
        compliance_mapping = finding.get('compliance_mapping', {}) or {}
        frameworks = compliance_mapping.get('frameworks', []) or []
        if frameworks:
            compliance_text = f"<b>Compliance Frameworks:</b> {_esc(', '.join([str(x) for x in frameworks]))}"
            elements.append(Paragraph(compliance_text, self.styles['Metadata']))
        
        return elements
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format"""
        if bytes_value == 0:
            return '0 B'
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = bytes_value
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _create_evidence_section_enhanced(self, audit_data: Dict) -> List:
        """Create comprehensive evidence and provenance section"""
        elements = []
        
        elements.append(Paragraph("EVIDENCE AND PROVENANCE", self.styles['SectionTitle']))
        
        evidence_info = audit_data.get('evidence_and_provenance', {})
        
        # Evidence overview
        elements.append(Paragraph("Evidence Analysis Overview", self.styles['SubsectionTitle']))
        
        evidence_text = f"""
        This section documents the evidence trail for all security findings in this report. 
        Every finding is backed by specific configuration evidence extracted from the analyzed device configuration.
        
        <b>Evidence Summary:</b>
        • Configuration Files Analyzed: {evidence_info.get('evidence_files_analyzed', 0)}
        • Configuration Lines Referenced: {evidence_info.get('configuration_lines_referenced', 0)}
        • Total Evidence Entries: {evidence_info.get('total_evidence_entries', 0)}
        
        <b>Evidence Chain Verification:</b>
        All evidence has been verified for integrity and traceability. Source configuration lines are 
        referenced by line number and file hash for complete auditability.
        """
        
        elements.append(Paragraph(evidence_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Evidence traceability for critical/high findings
        elements.append(Paragraph("Critical Evidence Traceability", self.styles['SubsectionTitle']))
        
        findings = audit_data.get('findings', {}).get('details', [])
        critical_high_findings = [
            f for f in findings 
            if f.get('severity') in ['CRITICAL', 'HIGH'] and f.get('status') == 'FAIL'
        ]
        
        if critical_high_findings:
            for finding in critical_high_findings[:5]:  # Top 5 critical/high findings
                elements.extend(self._format_evidence_trace(finding))
                elements.append(Spacer(1, 0.1*inch))
        else:
            elements.append(Paragraph("No critical or high severity findings with evidence traces.", self.styles['Professional']))
        
        # Data sanitization notice
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Data Sanitization and Security", self.styles['SubsectionTitle']))
        
        sanitization_text = """
        <b>Security Notice:</b> All configuration data in this report has been processed through 
        advanced sanitization algorithms to remove sensitive information including:
        
        • Passwords and authentication credentials
        • Encryption keys and certificates
        • IP addresses and network topology details
        • Proprietary configuration parameters
        • Personal identifiable information (PII)
        
        The sanitization process preserves the security-relevant configuration structure while 
        protecting sensitive operational data. Original configuration files are stored securely 
        and are accessible only to authorized personnel.
        """
        
        elements.append(Paragraph(sanitization_text, self.styles['Professional']))
        
        return elements
    
    def _format_evidence_trace(self, finding: Dict) -> List:
        """Format evidence traceability for a single finding"""
        elements = []
        
        evidence = finding.get('evidence', {}) or {}
        title = _esc(finding.get('rule_name', 'Unknown Finding'))
        severity = (finding.get('severity') or 'UNKNOWN').upper()
        if severity not in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'):
            severity = 'LOW'
        
        # Evidence header
        style_key = f'Severity{severity}' if f'Severity{severity}' in self.styles else 'Professional'
        elements.append(Paragraph(f"<b>[{severity}] {title}</b>", self.styles[style_key]))
        
        # Evidence details
        if evidence.get('evidence_text'):
            trace_text = f"""
            <b>Evidence Source:</b>
            • File: {_esc(evidence.get('evidence_file', 'Unknown'))}
            • Line Number: {_esc(evidence.get('evidence_line', 'Unknown'))}
            • Configuration Context: {len(evidence.get('configuration_context', []) or [])} surrounding lines
            
            <b>Evidence Extract:</b>
            """
            elements.append(Paragraph(trace_text, self.styles['Technical']))
            
            # Evidence text (truncated for PDF)
            raw = evidence.get('evidence_text', '') or ''
            evidence_text = _esc(raw[:200])
            if len(raw) > 200:
                evidence_text += '...'
            elements.append(Paragraph(evidence_text, self.styles['EnhancedCode']))
        
        return elements
    
    def _create_remediation_guidance_enhanced(self, audit_data: Dict) -> List:
        """Create comprehensive remediation guidance with prioritization"""
        elements = []
        
        elements.append(Paragraph("REMEDIATION GUIDANCE", self.styles['SectionTitle']))
        
        remediation_guidance = audit_data.get('remediation_guidance', {})
        
        # Remediation overview
        elements.append(Paragraph("Remediation Strategy Overview", self.styles['SubsectionTitle']))
        
        total_effort = remediation_guidance.get('estimated_total_effort', 'Unknown')
        priority_1_count = len(remediation_guidance.get('priority_1_critical', []))
        priority_2_count = len(remediation_guidance.get('priority_2_important', []))
        priority_3_count = len(remediation_guidance.get('priority_3_maintenance', []))
        
        overview_text = f"""
        This section provides detailed remediation guidance organized by priority level. 
        Recommendations are based on risk assessment, business impact analysis, and industry best practices.
        
        <b>Remediation Summary:</b>
        • Priority 1 (Critical/High): {priority_1_count} items - Immediate action required
        • Priority 2 (Medium): {priority_2_count} items - Address within 30 days  
        • Priority 3 (Low): {priority_3_count} items - Routine maintenance
        • Estimated Total Effort: {total_effort}
        
        <b>Implementation Strategy:</b>
        1. Address Priority 1 items immediately (within 24-48 hours)
        2. Schedule Priority 2 items for next maintenance window
        3. Include Priority 3 items in regular security maintenance cycles
        """
        
        elements.append(Paragraph(overview_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Priority 1: Critical/High remediation
        priority_1_items = remediation_guidance.get('priority_1_critical', [])
        if priority_1_items:
            elements.append(Paragraph("Priority 1: Critical & High Severity (Immediate Action Required)", self.styles['MinorHeading']))
            
            for i, item in enumerate(priority_1_items[:8], 1):  # Top 8 critical items
                elements.extend(self._format_remediation_item(item, i, 'CRITICAL'))
                elements.append(Spacer(1, 0.1*inch))
        
        # Priority 2: Medium remediation
        priority_2_items = remediation_guidance.get('priority_2_important', [])
        if priority_2_items:
            elements.append(PageBreak())  # New page for Priority 2
            elements.append(Paragraph("Priority 2: Medium Severity (Address Within 30 Days)", self.styles['MinorHeading']))
            
            for i, item in enumerate(priority_2_items[:10], 1):  # Top 10 medium items
                elements.extend(self._format_remediation_item(item, i, 'MEDIUM'))
                elements.append(Spacer(1, 0.08*inch))
        
        # General recommendations
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("General Security Recommendations", self.styles['SubsectionTitle']))
        
        general_text = """
        <b>Ongoing Security Practices:</b>
        • Implement regular configuration backup and version control
        • Establish automated configuration compliance monitoring
        • Schedule quarterly security configuration reviews
        • Maintain up-to-date documentation of security configurations
        • Implement change management processes for configuration updates
        • Consider deploying configuration management tools (Ansible, Puppet, etc.)
        
        <b>Compliance Maintenance:</b>
        • Regular audits against industry frameworks (CIS, NIST, ISO 27001)
        • Vendor security update monitoring and implementation
        • Baseline configuration management and drift detection
        • Security awareness training for network administration staff
        """
        
        elements.append(Paragraph(general_text, self.styles['Professional']))
        
        return elements
    
    def _format_remediation_item(self, item: Dict, number: int, priority_level: str) -> List:
        """Format a single remediation item"""
        elements = []
        
        severity = (item.get('severity') or priority_level or 'LOW').upper()
        if severity not in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'):
            severity = 'LOW'
        title = _esc(item.get('rule_name', 'Unknown Issue'))
        
        # Item header
        style_key = f'Severity{severity}' if f'Severity{severity}' in self.styles else 'Professional'
        elements.append(Paragraph(f"<b>{number}. [{severity}] {title}</b>", self.styles[style_key]))
        
        # Remediation guidance
        remediation = item.get('remediation', {}) or {}
        if remediation.get('guidance'):
            elements.append(Paragraph(f"<b>Action Required:</b> {_esc(remediation.get('guidance'))}", self.styles['Professional']))
        
        # Implementation details
        impl_text = f"""
        <b>Implementation Details:</b>
        • Priority Level: {_esc(remediation.get('priority', 'Unknown'))}/5
        • Estimated Effort: {_esc(remediation.get('estimated_effort', 'Unknown'))}
        • Business Impact: {_esc(remediation.get('business_impact', 'Unknown'))}
        """
        
        # Add compliance frameworks if available
        compliance_mapping = item.get('compliance_mapping', {}) or {}
        frameworks = compliance_mapping.get('frameworks', []) or []
        if frameworks:
            impl_text += f"\n• Compliance Frameworks: {_esc(', '.join([str(x) for x in frameworks]))}"
        
        elements.append(Paragraph(impl_text, self.styles['Technical']))
        
        return elements
    
    def _create_ai_analysis_appendix(self, audit_data: Dict) -> List:
        """Create AI analysis appendix with confidence metrics"""
        elements = []
        
        elements.append(Paragraph("AI ANALYSIS APPENDIX", self.styles['SectionTitle']))
        
        parsing_analysis = audit_data.get('parsing_analysis', {})
        
        # AI methodology overview
        elements.append(Paragraph("AI Analysis Methodology", self.styles['SubsectionTitle']))
        
        methodology_text = """
        This security audit was performed using advanced AI-powered configuration analysis. 
        The system employs machine learning models trained on thousands of network device configurations 
        and security best practices from multiple vendors and compliance frameworks.
        
        <b>AI Analysis Components:</b>
        • Pattern recognition for configuration syntax and structure
        • Semantic analysis of security-relevant configuration parameters
        • Risk assessment based on historical vulnerability data
        • Compliance mapping against industry standards and frameworks
        • Automated evidence extraction and traceability
        """
        
        elements.append(Paragraph(methodology_text, self.styles['Professional']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Confidence metrics
        elements.append(Paragraph("AI Confidence Metrics", self.styles['SubsectionTitle']))
        
        confidence_data = [
            ['Metric', 'Value', 'Assessment'],
            [
                'Overall Interpretation Confidence',
                f"{(parsing_analysis.get('interpretation_confidence') or 0)*100:.1f}%",
                self._assess_confidence_level(parsing_analysis.get('interpretation_confidence', 0))
            ],
            [
                'Configuration Lines Interpreted',
                f"{parsing_analysis.get('interpretation_rate', 0):.1f}%",
                f"({parsing_analysis.get('successfully_interpreted', 0):,} of {parsing_analysis.get('total_config_lines', 0):,} lines)"
            ],
            [
                'Uninterpreted Sections',
                str(parsing_analysis.get('uninterpreted_lines', 0)),
                'Require expert review' if parsing_analysis.get('uninterpreted_lines', 0) > 0 else 'None'
            ],
            [
                'Pending AI Mappings',
                str(parsing_analysis.get('pending_ai_mappings', 0)),
                'Learning opportunities'
            ]
        ]
        
        confidence_table = Table(confidence_data, colWidths=[2.2*inch, 1.5*inch, 1.8*inch])
        confidence_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(confidence_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Human review recommendations
        if parsing_analysis.get('requires_human_review', False):
            elements.append(Paragraph("Human Review Recommendations", self.styles['SubsectionTitle']))
            
            review_text = f"""
            <b>Expert Review Required:</b> {parsing_analysis.get('review_reason', 'Unknown reason')}
            
            The AI system has identified sections of the configuration that may benefit from 
            expert human review. This is normal for complex or non-standard configurations and 
            helps ensure the highest accuracy in security assessment.
            
            <b>Recommended Actions:</b>
            • Schedule review with a qualified network security expert
            • Focus on uninterpreted configuration sections
            • Validate AI findings against vendor-specific security guides
            • Consider updating configuration standards for better AI compatibility
            """
            
            elements.append(Paragraph(review_text, self.styles['Professional']))
        
        return elements
    
    def _assess_confidence_level(self, confidence: Optional[float]) -> str:
        """Assess confidence level description"""
        if confidence is None:
            confidence = 0.0
        if confidence >= 0.9:
            return "Excellent"
        elif confidence >= 0.8:
            return "Very Good"
        elif confidence >= 0.7:
            return "Good"
        elif confidence >= 0.6:
            return "Adequate"
        else:
            return "Needs Review"
    
    def _create_technical_appendices(self, audit_data: Dict, config_data: Dict) -> List:
        """Create technical appendices with detailed information"""
        elements = []
        
        elements.append(Paragraph("TECHNICAL APPENDICES", self.styles['SectionTitle']))
        
        # Appendix A: Complete Findings Summary
        elements.append(Paragraph("Appendix A: Complete Findings Summary", self.styles['SubsectionTitle']))
        
        findings = audit_data.get('findings', {}).get('details', [])
        
        if findings:
            # Create summary table of all findings
            findings_data = [['ID', 'Severity', 'Status', 'Rule', 'Description']]
            
            for i, finding in enumerate(findings, 1):
                findings_data.append([
                    str(i),
                    finding.get('severity', 'N/A'),
                    finding.get('status', 'N/A'),
                    finding.get('rule_id', 'N/A'),
                    (finding.get('rule_name', 'Unknown')[:40] + '...' 
                     if len(finding.get('rule_name', '')) > 40 
                     else finding.get('rule_name', 'Unknown'))
                ])
            
            findings_table = Table(findings_data, colWidths=[0.5*inch, 0.8*inch, 0.7*inch, 0.8*inch, 2.7*inch])
            findings_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(findings_table)
        else:
            elements.append(Paragraph("No findings available for summary.", self.styles['Professional']))
        
        # Appendix B: Configuration Metadata
        elements.append(PageBreak())
        elements.append(Paragraph("Appendix B: Configuration Metadata", self.styles['SubsectionTitle']))
        
        if config_data:
            metadata_text = f"""
            <b>File Information:</b>
            • Original Filename: {config_data.get('filename', 'N/A')}
            • Internal Reference: {config_data.get('internal_filename', 'N/A')}
            • File Type: {config_data.get('file_type', 'N/A')}
            • SHA-256 Hash: {config_data.get('file_integrity', {}).get('sha256_hash', 'N/A')}
            
            <b>Processing Information:</b>
            • Upload Date: {config_data.get('upload_metadata', {}).get('uploaded_at', 'N/A')}
            • Uploaded By: {config_data.get('upload_metadata', {}).get('uploaded_by', 'N/A')}
            • Processing Status: {'Complete' if config_data.get('processing_status', {}).get('ingested') else 'Incomplete'}
            """
            elements.append(Paragraph(metadata_text, self.styles['Technical']))
        else:
            elements.append(Paragraph("Configuration metadata not available.", self.styles['Professional']))
        
        return elements
    
    def _create_header_footer(self, canvas, doc):
        """TATVA monochrome header/footer"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 11)
        canvas.setFillColor(colors.HexColor('#1C1C1C'))
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 30, "TATVA  |  SECURITY AUDIT REPORT")
        
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6E6E6E'))
        canvas.drawRightString(
            doc.width + doc.leftMargin, 
            doc.height + doc.topMargin - 30, 
            f"Team Vajracore  •  {datetime.now().strftime('%B %d, %Y')}"
        )
        
        # Header line
        canvas.setStrokeColor(colors.HexColor('#1C1C1C'))
        canvas.setLineWidth(1.2)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 40, 
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 40)
        
        # Footer
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(colors.HexColor('#1C1C1C'))
        canvas.drawString(doc.leftMargin, 30, "CONFIDENTIAL  •  TATVA BY TEAM VAJRACORE")
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6E6E6E'))
        canvas.drawRightString(doc.width + doc.leftMargin, 30, f"Page {doc.page}")
        
        # Footer line
        canvas.line(doc.leftMargin, 45, doc.width + doc.leftMargin, 45)
        
        canvas.restoreState()