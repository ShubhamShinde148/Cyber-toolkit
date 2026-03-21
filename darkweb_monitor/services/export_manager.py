"""
Export Manager Module
Handles exporting results to multiple formats: JSON, CSV, HTML, TXT.
"""

import json
import csv
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class ExportConfig:
    """Configuration for export operations."""
    output_dir: str = "exports"
    include_timestamp: bool = True
    pretty_print: bool = True


class ExportManager:
    """Manages exporting data to various formats."""
    
    def __init__(self, config: Optional[ExportConfig] = None):
        self.config = config or ExportConfig()
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, base_name: str, extension: str) -> str:
        """Generate filename with optional timestamp."""
        if self.config.include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_name}_{timestamp}.{extension}"
        else:
            filename = f"{base_name}.{extension}"
        
        return os.path.join(self.config.output_dir, filename)
    
    def export_json(self, data: Any, filename: str = "report") -> str:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export (dict, list, or dataclass)
            filename: Base filename (without extension)
        
        Returns:
            Path to created file
        """
        filepath = self._generate_filename(filename, "json")
        
        # Convert dataclass to dict if needed
        if hasattr(data, '__dataclass_fields__'):
            data = asdict(data)
        elif isinstance(data, list) and data and hasattr(data[0], '__dataclass_fields__'):
            data = [asdict(item) for item in data]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if self.config.pretty_print:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            else:
                json.dump(data, f, default=str, ensure_ascii=False)
        
        return os.path.abspath(filepath)
    
    def export_csv(self, data: List[Dict], filename: str = "report") -> str:
        """
        Export data to CSV format.
        
        Args:
            data: List of dictionaries to export
            filename: Base filename (without extension)
        
        Returns:
            Path to created file
        """
        filepath = self._generate_filename(filename, "csv")
        
        if not data:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("")
            return os.path.abspath(filepath)
        
        # Flatten nested dicts for CSV compatibility
        flattened_data = []
        for item in data:
            flat_item = self._flatten_dict(item)
            flattened_data.append(flat_item)
        
        # Get all possible fieldnames
        fieldnames = set()
        for item in flattened_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
        
        return os.path.abspath(filepath)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV export."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def export_html(self, data: Dict, filename: str = "report") -> str:
        """
        Export data to styled HTML format.
        
        Args:
            data: Dictionary containing report data
            filename: Base filename (without extension)
        
        Returns:
            Path to created file
        """
        filepath = self._generate_filename(filename, "html")
        
        html_content = self._generate_html_report(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return os.path.abspath(filepath)
    
    def _generate_html_report(self, data: Dict) -> str:
        """Generate styled HTML report."""
        # Determine risk color
        risk = data.get('risk_level', data.get('risk', 'UNKNOWN')).upper()
        risk_colors = {
            'SAFE': '#27ae60',
            'LOW': '#2ecc71',
            'MEDIUM': '#f39c12',
            'HIGH': '#e74c3c',
            'CRITICAL': '#c0392b'
        }
        risk_color = risk_colors.get(risk, '#7f8c8d')
        
        breach_count = data.get('breach_count', 0)
        timestamp = data.get('checked_at', datetime.now().isoformat())
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dark Web Leak Monitor Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a252f 0%, #2c3e50 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.8;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .card h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        .risk-badge {{
            display: inline-block;
            padding: 15px 40px;
            border-radius: 50px;
            color: white;
            font-size: 1.5em;
            font-weight: bold;
            background: {risk_color};
            margin: 20px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .stat-box .value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-box .label {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .strength-meter {{
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .strength-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60);
            border-radius: 5px;
            transition: width 0.3s ease;
        }}
        .checklist {{
            list-style: none;
            padding: 0;
        }}
        .checklist li {{
            padding: 10px 15px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .checklist .check {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
        }}
        .checklist .check.pass {{
            background: #27ae60;
        }}
        .checklist .check.fail {{
            background: #e74c3c;
        }}
        .recommendations {{
            padding: 0;
            list-style: none;
        }}
        .recommendations li {{
            padding: 15px;
            margin: 10px 0;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.6);
            padding: 20px;
            font-size: 0.85em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .compromised {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .safe {{
            color: #27ae60;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Dark Web Leak Monitor</h1>
            <p>Security Assessment Report</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Generated: {timestamp}</p>
        </div>
        
        <div class="card" style="text-align: center;">
            <h2>Risk Assessment</h2>
            <div class="risk-badge">{risk}</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="value">{breach_count:,}</div>
                    <div class="label">Breach Count</div>
                </div>
                <div class="stat-box">
                    <div class="value">{"COMPROMISED" if breach_count > 0 else "SECURE"}</div>
                    <div class="label">Status</div>
                </div>
                <div class="stat-box">
                    <div class="value">{data.get('risk_score', risk_colors.get(risk, 50))}</div>
                    <div class="label">Risk Score</div>
                </div>
            </div>
        </div>
'''
        
        # Password Analysis Section
        if 'password_strength' in data or 'strength' in data:
            strength = data.get('password_strength', data.get('strength', {}))
            html += f'''
        <div class="card">
            <h2>Password Analysis</h2>
            <p style="margin-bottom: 15px;">Password Length: <strong>{strength.get('length', 'N/A')} characters</strong></p>
            
            <p style="margin-bottom: 5px;">Strength Score:</p>
            <div class="strength-meter">
                <div class="strength-fill" style="width: {min(strength.get('length', 0) * 6, 100)}%;"></div>
            </div>
            
            <ul class="checklist">
                <li>
                    <span class="check {'pass' if strength.get('has_upper') else 'fail'}">{'+' if strength.get('has_upper') else '-'}</span>
                    Uppercase Letters (A-Z)
                </li>
                <li>
                    <span class="check {'pass' if strength.get('has_lower') else 'fail'}">{'+' if strength.get('has_lower') else '-'}</span>
                    Lowercase Letters (a-z)
                </li>
                <li>
                    <span class="check {'pass' if strength.get('has_digit') else 'fail'}">{'+' if strength.get('has_digit') else '-'}</span>
                    Numbers (0-9)
                </li>
                <li>
                    <span class="check {'pass' if strength.get('has_special') else 'fail'}">{'+' if strength.get('has_special') else '-'}</span>
                    Special Characters (!@#$%)
                </li>
            </ul>
        </div>
'''
        
        # Recommendations Section
        recommendations = data.get('recommendations', [])
        if recommendations:
            html += '''
        <div class="card">
            <h2>Security Recommendations</h2>
            <ul class="recommendations">
'''
            for rec in recommendations[:6]:
                clean_rec = rec.replace('🚨', '').replace('⚠️', '').replace('✅', '').replace('🔴', '').strip()
                html += f'                <li>{clean_rec}</li>\n'
            
            html += '''            </ul>
        </div>
'''
        
        # Batch Results Table (if present)
        if 'results' in data and isinstance(data['results'], list) and data['results']:
            html += '''
        <div class="card">
            <h2>Batch Check Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Item</th>
                        <th>Status</th>
                        <th>Breaches</th>
                        <th>Risk</th>
                    </tr>
                </thead>
                <tbody>
'''
            for result in data['results']:
                item = result.get('password_masked', result.get('email', 'N/A'))
                status_class = 'compromised' if result.get('is_compromised') else 'safe'
                status_text = 'COMPROMISED' if result.get('is_compromised') else 'SAFE'
                html += f'''                    <tr>
                        <td>{result.get('index', '-')}</td>
                        <td><code>{item}</code></td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{result.get('breach_count', 0):,}</td>
                        <td>{result.get('risk_level', 'N/A')}</td>
                    </tr>
'''
            html += '''                </tbody>
            </table>
        </div>
'''
        
        # Footer
        html += '''
        <div class="footer">
            <p>This report uses k-anonymity protection. Your full password was NEVER transmitted over the internet.</p>
            <p style="margin-top: 10px;">Data Source: Have I Been Pwned API | Dark Web Leak Monitor</p>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def export_txt(self, data: Dict, filename: str = "report") -> str:
        """
        Export data to plain text format.
        
        Args:
            data: Dictionary containing report data
            filename: Base filename (without extension)
        
        Returns:
            Path to created file
        """
        filepath = self._generate_filename(filename, "txt")
        
        lines = [
            "=" * 70,
            "DARK WEB LEAK MONITOR - SECURITY REPORT",
            "=" * 70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 70,
            "SUMMARY",
            "-" * 70,
        ]
        
        # Add summary data
        if 'risk_level' in data or 'risk' in data:
            lines.append(f"Risk Level: {data.get('risk_level', data.get('risk', 'N/A'))}")
        if 'breach_count' in data:
            lines.append(f"Breach Count: {data['breach_count']:,}")
        if 'risk_score' in data:
            lines.append(f"Risk Score: {data['risk_score']}/100")
        
        # Password strength
        strength = data.get('password_strength', data.get('strength', {}))
        if strength:
            lines.extend([
                "",
                "-" * 70,
                "PASSWORD ANALYSIS",
                "-" * 70,
                f"Length: {strength.get('length', 'N/A')} characters",
                f"Uppercase: {'Yes' if strength.get('has_upper') else 'No'}",
                f"Lowercase: {'Yes' if strength.get('has_lower') else 'No'}",
                f"Numbers: {'Yes' if strength.get('has_digit') else 'No'}",
                f"Special Characters: {'Yes' if strength.get('has_special') else 'No'}",
            ])
        
        # Recommendations
        recommendations = data.get('recommendations', [])
        if recommendations:
            lines.extend([
                "",
                "-" * 70,
                "RECOMMENDATIONS",
                "-" * 70,
            ])
            for i, rec in enumerate(recommendations, 1):
                clean_rec = rec.replace('🚨', '').replace('⚠️', '').replace('✅', '').replace('🔴', '').strip()
                lines.append(f"{i}. {clean_rec}")
        
        # Batch results
        if 'results' in data and isinstance(data['results'], list):
            lines.extend([
                "",
                "-" * 70,
                "BATCH RESULTS",
                "-" * 70,
            ])
            for result in data['results']:
                item = result.get('password_masked', result.get('email', 'N/A'))
                status = 'COMPROMISED' if result.get('is_compromised') else 'SAFE'
                lines.append(f"#{result.get('index', '-')}: {item} | {status} | Breaches: {result.get('breach_count', 0):,}")
        
        lines.extend([
            "",
            "=" * 70,
            "Report generated by Dark Web Leak Monitor",
            "Data Source: Have I Been Pwned API (k-anonymity protected)",
            "=" * 70,
        ])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return os.path.abspath(filepath)
    
    def export_all(self, data: Dict, filename: str = "report") -> Dict[str, str]:
        """
        Export data to all supported formats.
        
        Returns:
            Dictionary with format names as keys and file paths as values
        """
        return {
            'json': self.export_json(data, filename),
            'csv': self.export_csv([data] if isinstance(data, dict) else data, filename),
            'html': self.export_html(data, filename),
            'txt': self.export_txt(data, filename)
        }


# Convenience functions
def export_to_json(data: Any, filename: str = "report") -> str:
    """Export data to JSON."""
    return ExportManager().export_json(data, filename)


def export_to_csv(data: List[Dict], filename: str = "report") -> str:
    """Export data to CSV."""
    return ExportManager().export_csv(data, filename)


def export_to_html(data: Dict, filename: str = "report") -> str:
    """Export data to HTML."""
    return ExportManager().export_html(data, filename)


def export_to_txt(data: Dict, filename: str = "report") -> str:
    """Export data to TXT."""
    return ExportManager().export_txt(data, filename)
