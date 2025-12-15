"""
Report Generation System for Vehicle Damage Assessment
"""

import os
import io
from datetime import datetime
from typing import List, Dict, Any
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkred
        ))
    
    def generate_pdf_report(self, damage_report, image_paths: List[str]) -> bytes:
        """Generate PDF report for damage assessment"""
        try:
            # Create buffer for PDF
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                 topMargin=72, bottomMargin=18)
            
            # Build content
            story = []
            
            # Add title
            story.append(Paragraph("Vehicle Damage Assessment Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Add report information
            story.extend(self.add_report_info(damage_report))
            story.append(Spacer(1, 20))
            
            # Add damage analysis
            story.extend(self.add_damage_analysis(damage_report))
            story.append(Spacer(1, 20))
            
            # Add cost estimation
            story.extend(self.add_cost_estimation(damage_report))
            story.append(Spacer(1, 20))
            
            # Add images
            if image_paths:
                story.extend(self.add_images(image_paths))
                story.append(Spacer(1, 20))
            
            # Add recommendations
            story.extend(self.add_recommendations(damage_report))
            story.append(Spacer(1, 20))
            
            # Add footer
            story.extend(self.add_footer())
            
            # Build PDF
            doc.build(story)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            return self.generate_error_report(str(e))
    
    def add_report_info(self, damage_report) -> List:
        """Add report information section"""
        story = []
        
        # Report details table
        report_data = [
            ['Report ID:', str(damage_report.id)],
            ['Date:', damage_report.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Vehicle Type:', damage_report.vehicle_type],
            ['Damage Type:', damage_report.damage_type],
            ['Severity:', damage_report.severity],
            ['Status:', damage_report.status.title()],
            ['Confidence Score:', f"{damage_report.confidence_score:.2f}"]
        ]
        
        report_table = Table(report_data, colWidths=[2*inch, 3*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        
        story.append(Paragraph("Report Information", self.styles['CustomSubtitle']))
        story.append(report_table)
        
        return story
    
    def add_damage_analysis(self, damage_report) -> List:
        """Add damage analysis section"""
        story = []
        
        story.append(Paragraph("Damage Analysis", self.styles['CustomSubtitle']))
        
        # Damage description
        damage_desc = f"""
        The vehicle has been assessed for {damage_report.damage_type.lower()} damage with a severity level of {damage_report.severity.lower()}. 
        The assessment was performed with a confidence score of {damage_report.confidence_score:.2f}, indicating 
        {'high' if damage_report.confidence_score > 0.7 else 'medium' if damage_report.confidence_score > 0.4 else 'low'} reliability.
        """
        
        story.append(Paragraph(damage_desc, self.styles['CustomBody']))
        
        # Severity explanation
        severity_explanations = {
            'Minor': 'Minor damage typically involves cosmetic issues that can be repaired quickly and inexpensively.',
            'Moderate': 'Moderate damage may require professional repair and could affect vehicle performance.',
            'Severe': 'Severe damage requires immediate attention and may involve structural components.',
            'Critical': 'Critical damage poses safety risks and requires immediate professional intervention.'
        }
        
        severity_desc = severity_explanations.get(damage_report.severity, 'Damage severity assessment completed.')
        story.append(Paragraph(f"Severity Assessment: {severity_desc}", self.styles['CustomBody']))
        
        return story
    
    def add_cost_estimation(self, damage_report) -> List:
        """Add cost estimation section"""
        story = []
        
        story.append(Paragraph("Cost Estimation", self.styles['CustomSubtitle']))
        
        # Cost breakdown
        cost_data = [
            ['Item', 'Amount ($)'],
            ['Estimated Repair Cost', f"${damage_report.estimated_cost:.2f}"],
            ['Confidence Level', f"{'High' if damage_report.confidence_score > 0.7 else 'Medium' if damage_report.confidence_score > 0.4 else 'Low'}"],
            ['Recommended Action', self.get_recommended_action(damage_report.estimated_cost, damage_report.severity)]
        ]
        
        cost_table = Table(cost_data, colWidths=[3*inch, 2*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(cost_table)
        
        # Cost disclaimer
        disclaimer = """
        <b>Disclaimer:</b> The cost estimation provided is based on current market rates and typical repair scenarios. 
        Actual costs may vary depending on specific repair shop rates, part availability, and additional damage discovered during repair.
        """
        story.append(Paragraph(disclaimer, self.styles['CustomBody']))
        
        return story
    
    def add_images(self, image_paths: List[str]) -> List:
        """Add images to the report"""
        story = []
        
        story.append(Paragraph("Damage Images", self.styles['CustomSubtitle']))
        
        for i, image_path in enumerate(image_paths[:4]):  # Limit to 4 images
            # Convert relative path to absolute path
            if image_path.startswith('static/'):
                full_path = image_path
            else:
                full_path = os.path.join('static', image_path) if not os.path.isabs(image_path) else image_path
            
            if os.path.exists(full_path):
                try:
                    # Resize image to fit on page
                    img = Image(full_path, width=4*inch, height=3*inch)
                    story.append(img)
                    story.append(Spacer(1, 10))
                except Exception as e:
                    logger.warning(f"Could not add image {full_path}: {e}")
            else:
                logger.warning(f"Image not found: {full_path}")
        
        return story
    
    def add_recommendations(self, damage_report) -> List:
        """Add recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
        
        recommendations = self.generate_recommendations(damage_report)
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        return story
    
    def add_footer(self) -> List:
        """Add footer information"""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by Vehicle Damage Assessment System", 
                             self.styles['CustomBody']))
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                             self.styles['CustomBody']))
        
        return story
    
    def generate_recommendations(self, damage_report) -> List[str]:
        """Generate repair recommendations based on damage report"""
        recommendations = []
        
        # Basic recommendations
        if damage_report.severity in ['Severe', 'Critical']:
            recommendations.append("Schedule immediate inspection with a certified repair shop")
            recommendations.append("Consider towing the vehicle to prevent further damage")
        
        if damage_report.estimated_cost > 1000:
            recommendations.append("Contact your insurance company to file a claim")
            recommendations.append("Obtain multiple repair estimates for comparison")
        
        if damage_report.damage_type in ['Structural Damage', 'Broken Part']:
            recommendations.append("Avoid driving the vehicle until repairs are completed")
            recommendations.append("Request a detailed inspection of related components")
        
        # General recommendations
        recommendations.append("Keep all repair documentation for insurance purposes")
        recommendations.append("Consider getting a second opinion for major repairs")
        
        return recommendations
    
    def get_recommended_action(self, cost: float, severity: str) -> str:
        """Get recommended action based on cost and severity"""
        if severity in ['Critical', 'Severe']:
            return "Immediate Professional Repair Required"
        elif cost > 2000:
            return "Professional Repair Recommended"
        elif cost > 500:
            return "Professional Repair or Insurance Claim"
        else:
            return "Minor Repair or DIY Option Available"
    
    def generate_error_report(self, error_message: str) -> bytes:
        """Generate error report when PDF generation fails"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            story.append(Paragraph("Error Generating Report", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"An error occurred while generating the report: {error_message}", 
                                 self.styles['CustomBody']))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            logger.error(f"Error generating error report: {e}")
            return b"Error generating report"
    
    def generate_html_report(self, damage_report, image_paths: List[str]) -> str:
        """Generate HTML report for web display"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Vehicle Damage Assessment Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { text-align: center; color: #2c3e50; }
                    .section { margin: 20px 0; }
                    .info-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                    .info-table th, .info-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    .info-table th { background-color: #3498db; color: white; }
                    .cost-highlight { font-size: 18px; font-weight: bold; color: #e74c3c; }
                    .image-container { margin: 10px 0; }
                    .image-container img { max-width: 300px; margin: 5px; border: 1px solid #ddd; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Vehicle Damage Assessment Report</h1>
                </div>
                
                <div class="section">
                    <h2>Report Information</h2>
                    <table class="info-table">
                        <tr><th>Report ID</th><td>{report_id}</td></tr>
                        <tr><th>Date</th><td>{date}</td></tr>
                        <tr><th>Vehicle Type</th><td>{vehicle_type}</td></tr>
                        <tr><th>Damage Type</th><td>{damage_type}</td></tr>
                        <tr><th>Severity</th><td>{severity}</td></tr>
                        <tr><th>Status</th><td>{status}</td></tr>
                        <tr><th>Confidence Score</th><td>{confidence}</td></tr>
                    </table>
                </div>
                
                <div class="section">
                    <h2>Cost Estimation</h2>
                    <p class="cost-highlight">Estimated Repair Cost: ${estimated_cost}</p>
                    <p>Confidence Level: {confidence_level}</p>
                </div>
                
                <div class="section">
                    <h2>Damage Images</h2>
                    <div class="image-container">
                        {images_html}
                    </div>
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    <ul>
                        {recommendations_html}
                    </ul>
                </div>
            </body>
            </html>
            """
            
            # Generate images HTML
            images_html = ""
            for image_path in image_paths[:4]:
                if os.path.exists(image_path):
                    images_html += f'<img src="{image_path}" alt="Damage Image">'
            
            # Generate recommendations HTML
            recommendations = self.generate_recommendations(damage_report)
            recommendations_html = "".join([f"<li>{rec}</li>" for rec in recommendations])
            
            # Fill template
            html_content = html_template.format(
                report_id=damage_report.id,
                date=damage_report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                vehicle_type=damage_report.vehicle_type,
                damage_type=damage_report.damage_type,
                severity=damage_report.severity,
                status=damage_report.status.title(),
                confidence=f"{damage_report.confidence_score:.2f}",
                estimated_cost=f"{damage_report.estimated_cost:.2f}",
                confidence_level='High' if damage_report.confidence_score > 0.7 else 'Medium' if damage_report.confidence_score > 0.4 else 'Low',
                images_html=images_html,
                recommendations_html=recommendations_html
            )
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
