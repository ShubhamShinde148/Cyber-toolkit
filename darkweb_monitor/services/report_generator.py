"""
Report Generator Module
Creates professional PDF security reports with advanced visual styling.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.lib.units import inch, mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from typing import Optional, List
import os
import math


class ReportGenerator:
    """Generates professional security assessment PDF reports."""
    
    # Enhanced color scheme
    COLORS = {
        'primary': HexColor('#1a252f'),
        'secondary': HexColor('#2c3e50'),
        'accent': HexColor('#3498db'),
        'safe': HexColor('#27ae60'),
        'low': HexColor('#2ecc71'),
        'medium': HexColor('#f39c12'),
        'high': HexColor('#e74c3c'),
        'critical': HexColor('#c0392b'),
        'text': HexColor('#2c3e50'),
        'text_light': HexColor('#7f8c8d'),
        'card_bg': HexColor('#f8f9fa'),
        'border': HexColor('#dee2e6'),
        'white': white,
        'success': HexColor('#28a745'),
        'danger': HexColor('#dc3545'),
        'warning': HexColor('#ffc107'),
    }
    
    RISK_CONFIG = {
        'safe': {'color': 'safe', 'icon': 'SECURE', 'score': 0},
        'low': {'color': 'low', 'icon': 'LOW', 'score': 25},
        'medium': {'color': 'medium', 'icon': 'MEDIUM', 'score': 50},
        'high': {'color': 'high', 'icon': 'HIGH', 'score': 75},
        'critical': {'color': 'critical', 'icon': 'CRITICAL', 'score': 100},
    }
    
    def __init__(self, filename: str = "breach_report.pdf"):
        self.filename = filename
        self.width, self.height = A4
        self.margin = 40
        self.content_width = self.width - (2 * self.margin)
    
    def _get_risk_color(self, risk: str) -> HexColor:
        """Get color based on risk level."""
        config = self.RISK_CONFIG.get(risk.lower(), self.RISK_CONFIG['medium'])
        return self.COLORS[config['color']]
    
    def _draw_rounded_rect(self, c: canvas.Canvas, x, y, w, h, radius=8, fill=True, stroke=False):
        """Draw a rounded rectangle."""
        c.roundRect(x, y, w, h, radius, fill=fill, stroke=stroke)
    
    def _draw_header(self, c: canvas.Canvas):
        """Draw modern gradient-style header."""
        # Main header background
        c.setFillColor(self.COLORS['primary'])
        c.rect(0, self.height - 120, self.width, 120, fill=True, stroke=False)
        
        # Accent stripe
        c.setFillColor(self.COLORS['accent'])
        c.rect(0, self.height - 125, self.width, 5, fill=True, stroke=False)
        
        # Logo/Brand area
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(self.margin, self.height - 55, "DARK WEB LEAK MONITOR")
        
        # Subtitle
        c.setFillColor(HexColor('#bdc3c7'))
        c.setFont("Helvetica", 13)
        c.drawString(self.margin, self.height - 78, "Comprehensive Security Assessment Report")
        
        # Report metadata box
        c.setFillColor(HexColor('#34495e'))
        self._draw_rounded_rect(c, self.width - 200, self.height - 105, 160, 70, 5)
        
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(self.width - 190, self.height - 55, "REPORT GENERATED")
        c.setFont("Helvetica", 10)
        c.drawString(self.width - 190, self.height - 70, datetime.now().strftime("%B %d, %Y"))
        c.drawString(self.width - 190, self.height - 85, datetime.now().strftime("%H:%M:%S"))
    
    def _draw_risk_gauge(self, c: canvas.Canvas, risk: str, x: int, y: int, size: int = 80):
        """Draw a circular risk gauge/meter."""
        risk_config = self.RISK_CONFIG.get(risk.lower(), self.RISK_CONFIG['medium'])
        risk_color = self.COLORS[risk_config['color']]
        score = risk_config['score']
        
        center_x = x + size
        center_y = y - size
        
        # Background circle
        c.setFillColor(self.COLORS['card_bg'])
        c.setStrokeColor(self.COLORS['border'])
        c.setLineWidth(3)
        c.circle(center_x, center_y, size, fill=True, stroke=True)
        
        # Risk arc (progress indicator)
        c.setStrokeColor(risk_color)
        c.setLineWidth(12)
        
        # Draw arc based on risk score
        start_angle = 225
        sweep = -270 * (score / 100)
        
        # Draw the arc segments
        if score > 0:
            c.setFillColor(risk_color)
            # Draw filled segments to represent the gauge
            segments = int(score / 10)
            for i in range(segments):
                angle = math.radians(start_angle - (i * 27))
                inner_r = size - 15
                outer_r = size - 5
                seg_x = center_x + math.cos(angle) * (inner_r + outer_r) / 2
                seg_y = center_y + math.sin(angle) * (inner_r + outer_r) / 2
                c.circle(seg_x, seg_y, 6, fill=True, stroke=False)
        
        # Inner circle (white)
        c.setFillColor(white)
        c.circle(center_x, center_y, size - 25, fill=True, stroke=False)
        
        # Risk level text
        c.setFillColor(risk_color)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(center_x, center_y + 5, risk.upper())
        
        # Score text
        c.setFillColor(self.COLORS['text_light'])
        c.setFont("Helvetica", 11)
        c.drawCentredString(center_x, center_y - 15, f"Score: {score}")
    
    def _draw_stats_cards(self, c: canvas.Canvas, breach_count: int, risk: str, y_pos: int):
        """Draw statistics cards row."""
        card_width = (self.content_width - 30) / 3
        card_height = 80
        
        stats = [
            ("BREACH COUNT", f"{breach_count:,}", self.COLORS['danger'] if breach_count > 0 else self.COLORS['success']),
            ("STATUS", "COMPROMISED" if breach_count > 0 else "SECURE", self.COLORS['danger'] if breach_count > 0 else self.COLORS['success']),
            ("RISK LEVEL", risk.upper(), self._get_risk_color(risk)),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            x = self.margin + (i * (card_width + 15))
            
            # Card background
            c.setFillColor(self.COLORS['card_bg'])
            c.setStrokeColor(self.COLORS['border'])
            c.setLineWidth(1)
            self._draw_rounded_rect(c, x, y_pos - card_height, card_width, card_height)
            c.roundRect(x, y_pos - card_height, card_width, card_height, 8, fill=False, stroke=True)
            
            # Color accent bar at top
            c.setFillColor(color)
            c.rect(x + 10, y_pos - 8, card_width - 20, 4, fill=True, stroke=False)
            
            # Label
            c.setFillColor(self.COLORS['text_light'])
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + card_width/2, y_pos - 30, label)
            
            # Value
            c.setFillColor(color)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(x + card_width/2, y_pos - 55, value)
    
    def _draw_executive_summary(self, c: canvas.Canvas, breach_count: int, risk: str, y_pos: int):
        """Draw executive summary section."""
        # Section header
        c.setFillColor(self.COLORS['primary'])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_pos, "EXECUTIVE SUMMARY")
        
        # Underline
        c.setStrokeColor(self.COLORS['accent'])
        c.setLineWidth(3)
        c.line(self.margin, y_pos - 5, self.margin + 160, y_pos - 5)
        
        # Summary box
        box_y = y_pos - 100
        c.setFillColor(self.COLORS['card_bg'])
        self._draw_rounded_rect(c, self.margin, box_y, self.content_width, 85)
        
        # Summary text
        c.setFillColor(self.COLORS['text'])
        c.setFont("Helvetica", 11)
        
        if breach_count == 0:
            summary_lines = [
                "Your password was NOT found in any known data breaches.",
                "This is a positive indicator, but does not guarantee absolute security.",
                "Continue to follow best practices for password management."
            ]
        else:
            summary_lines = [
                f"WARNING: Your password was found in {breach_count:,} data breach(es).",
                "This means attackers have access to this password and may attempt to use it.",
                "Immediate action is recommended to secure your accounts."
            ]
        
        line_y = y_pos - 30
        for line in summary_lines:
            c.drawString(self.margin + 15, line_y, line)
            line_y -= 18
    
    def _draw_password_analysis(self, c: canvas.Canvas, password: str, y_pos: int):
        """Draw password analysis section with visual indicators."""
        # Section header
        c.setFillColor(self.COLORS['primary'])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_pos, "PASSWORD ANALYSIS")
        
        c.setStrokeColor(self.COLORS['accent'])
        c.setLineWidth(3)
        c.line(self.margin, y_pos - 5, self.margin + 160, y_pos - 5)
        
        # Analysis box
        box_y = y_pos - 155
        c.setFillColor(self.COLORS['card_bg'])
        self._draw_rounded_rect(c, self.margin, box_y, self.content_width, 140)
        
        # Masked password
        masked = password[:2] + '*' * min(len(password) - 4, 12) + password[-2:] if len(password) > 4 else '****'
        
        # Password characteristics
        checks = [
            ("Length", len(password), f"{len(password)} characters", len(password) >= 12),
            ("Uppercase", any(ch.isupper() for ch in password), "Contains A-Z", any(ch.isupper() for ch in password)),
            ("Lowercase", any(ch.islower() for ch in password), "Contains a-z", any(ch.islower() for ch in password)),
            ("Numbers", any(ch.isdigit() for ch in password), "Contains 0-9", any(ch.isdigit() for ch in password)),
            ("Special", any(ch in '!@#$%^&*()_+-=[]{}|;:,.<>?' for ch in password), "Contains !@#$%", any(ch in '!@#$%^&*()_+-=[]{}|;:,.<>?' for ch in password)),
        ]
        
        # Calculate strength score
        strength_score = sum([
            min(len(password) / 12, 1) * 30,  # Length (max 30 points)
            15 if any(ch.isupper() for ch in password) else 0,
            15 if any(ch.islower() for ch in password) else 0,
            20 if any(ch.isdigit() for ch in password) else 0,
            20 if any(ch in '!@#$%^&*()_+-=[]{}|;:,.<>?' for ch in password) else 0,
        ])
        
        # Draw strength meter
        meter_x = self.margin + 15
        meter_y = y_pos - 35
        meter_width = 200
        meter_height = 12
        
        c.setFillColor(self.COLORS['text'])
        c.setFont("Helvetica-Bold", 10)
        c.drawString(meter_x, meter_y + 5, f"Password Strength: {int(strength_score)}%")
        
        # Meter background
        c.setFillColor(HexColor('#e9ecef'))
        self._draw_rounded_rect(c, meter_x, meter_y - 18, meter_width, meter_height, 4)
        
        # Meter fill
        if strength_score >= 80:
            meter_color = self.COLORS['success']
        elif strength_score >= 50:
            meter_color = self.COLORS['warning']
        else:
            meter_color = self.COLORS['danger']
        
        c.setFillColor(meter_color)
        fill_width = (strength_score / 100) * meter_width
        if fill_width > 0:
            self._draw_rounded_rect(c, meter_x, meter_y - 18, fill_width, meter_height, 4)
        
        # Checkmarks grid
        grid_y = y_pos - 70
        col_width = self.content_width / 3
        
        for i, (name, _, desc, passed) in enumerate(checks):
            col = i % 3
            row = i // 3
            x = self.margin + 20 + (col * col_width)
            y = grid_y - (row * 35)
            
            # Checkbox
            c.setFillColor(self.COLORS['success'] if passed else self.COLORS['danger'])
            c.circle(x, y, 8, fill=True, stroke=False)
            
            # Checkmark or X
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x, y - 4, "+" if passed else "-")
            
            # Label
            c.setFillColor(self.COLORS['text'])
            c.setFont("Helvetica", 10)
            c.drawString(x + 15, y - 4, name)
    
    def _draw_recommendations(self, c: canvas.Canvas, recommendations: List[str], y_pos: int):
        """Draw recommendations section with icons."""
        # Section header
        c.setFillColor(self.COLORS['primary'])
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, y_pos, "SECURITY RECOMMENDATIONS")
        
        c.setStrokeColor(self.COLORS['accent'])
        c.setLineWidth(3)
        c.line(self.margin, y_pos - 5, self.margin + 220, y_pos - 5)
        
        # Recommendations list
        c.setFont("Helvetica", 10)
        line_y = y_pos - 30
        
        for i, rec in enumerate(recommendations[:5], 1):
            # Number badge
            c.setFillColor(self.COLORS['accent'])
            c.circle(self.margin + 12, line_y + 3, 10, fill=True, stroke=False)
            
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(self.margin + 12, line_y, str(i))
            
            # Recommendation text (clean up emojis for PDF)
            clean_rec = rec.replace("🚨", "").replace("⚠️", "").replace("✅", "").replace("🔴", "").strip()
            c.setFillColor(self.COLORS['text'])
            c.setFont("Helvetica", 10)
            c.drawString(self.margin + 30, line_y, clean_rec[:70])
            
            line_y -= 25
    
    def _draw_footer(self, c: canvas.Canvas):
        """Draw professional footer."""
        footer_y = 50
        
        # Footer line
        c.setStrokeColor(self.COLORS['border'])
        c.setLineWidth(1)
        c.line(self.margin, footer_y + 15, self.width - self.margin, footer_y + 15)
        
        # Privacy notice
        c.setFillColor(self.COLORS['text_light'])
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, footer_y, 
            "This report uses k-anonymity protection. Your full password was NEVER transmitted over the internet.")
        
        # Powered by
        c.setFont("Helvetica-Bold", 7)
        c.drawString(self.margin, footer_y - 15, "Data Source: Have I Been Pwned API")
        c.drawRightString(self.width - self.margin, footer_y - 15, 
            f"Report ID: {datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    def _draw_threat_indicator(self, c: canvas.Canvas, risk: str, y_pos: int):
        """Draw a visual threat level indicator bar."""
        bar_x = self.margin
        bar_y = y_pos
        bar_width = self.content_width
        bar_height = 25
        
        # Background segments
        levels = ['safe', 'low', 'medium', 'high', 'critical']
        segment_width = bar_width / 5
        
        for i, level in enumerate(levels):
            x = bar_x + (i * segment_width)
            c.setFillColor(self.COLORS[level])
            if i == 0:
                c.roundRect(x, bar_y, segment_width, bar_height, 5, fill=True, stroke=False)
            elif i == 4:
                c.roundRect(x, bar_y, segment_width, bar_height, 5, fill=True, stroke=False)
            else:
                c.rect(x, bar_y, segment_width, bar_height, fill=True, stroke=False)
        
        # Current level indicator
        current_idx = levels.index(risk.lower()) if risk.lower() in levels else 2
        indicator_x = bar_x + (current_idx * segment_width) + (segment_width / 2)
        
        # Triangle indicator
        c.setFillColor(self.COLORS['primary'])
        c.setStrokeColor(white)
        c.setLineWidth(2)
        
        # Draw pointer arrow using path
        arrow_y = bar_y + bar_height + 5
        path = c.beginPath()
        path.moveTo(indicator_x - 8, arrow_y + 15)
        path.lineTo(indicator_x + 8, arrow_y + 15)
        path.lineTo(indicator_x, arrow_y)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        
        # Level labels
        c.setFont("Helvetica", 7)
        c.setFillColor(white)
        for i, level in enumerate(levels):
            label_x = bar_x + (i * segment_width) + (segment_width / 2)
            c.drawCentredString(label_x, bar_y + 8, level.upper())
    
    def generate(
        self, 
        password: str, 
        breach_count: int, 
        risk: str,
        recommendations: Optional[List[str]] = None
    ) -> str:
        """
        Generate a comprehensive PDF security report.
        
        Returns: Path to generated PDF file
        """
        c = canvas.Canvas(self.filename, pagesize=A4)
        
        # Draw all sections
        self._draw_header(c)
        
        # Threat level bar
        self._draw_threat_indicator(c, risk, self.height - 170)
        
        # Stats cards
        self._draw_stats_cards(c, breach_count, risk, self.height - 210)
        
        # Executive summary
        self._draw_executive_summary(c, breach_count, risk, self.height - 320)
        
        # Password analysis
        self._draw_password_analysis(c, password, self.height - 450)
        
        # Recommendations
        if recommendations:
            self._draw_recommendations(c, recommendations, self.height - 620)
        
        # Footer
        self._draw_footer(c)
        
        c.save()
        return os.path.abspath(self.filename)


# Legacy function for backward compatibility
def generate_report(password: str, count, risk: str) -> None:
    """Legacy wrapper - generates basic report."""
    # Convert count to int if string
    if isinstance(count, str):
        count = int(count) if count.isdigit() else 0
    
    generator = ReportGenerator()
    filepath = generator.generate(password, count, risk)
    print(f"✅ PDF Report Generated: {filepath}")
