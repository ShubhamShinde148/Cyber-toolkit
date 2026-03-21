"""
Breach Timeline Visualization Module
====================================
Generates timeline data for visualizing breach history and security events.
Provides data structures optimized for chart.js and other visualization libraries.

Features:
- Chronological breach timeline
- Severity distribution over time
- Category analysis
- Interactive data points
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class BreachEvent:
    """Represents a single breach event."""
    id: str
    name: str
    date: datetime
    severity: str  # critical, high, medium, low
    data_types: List[str]
    affected_count: int
    description: str
    source: str
    is_verified: bool = True
    is_sensitive: bool = False


@dataclass
class TimelinePoint:
    """A point on the timeline."""
    date: str
    event_count: int
    severity_breakdown: Dict[str, int]
    events: List[Dict]


class BreachTimeline:
    """
    Breach timeline generator for visualization.
    
    Processes breach data and generates structured timeline data
    suitable for various chart libraries.
    """
    
    SEVERITY_COLORS = {
        'critical': '#ff0055',
        'high': '#ff6600',
        'medium': '#ffcc00',
        'low': '#00cc00',
        'unknown': '#888888'
    }
    
    SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'unknown']
    
    def __init__(self):
        """Initialize the breach timeline generator."""
        self.events: List[BreachEvent] = []
    
    def clear(self):
        """Clear all events."""
        self.events = []
    
    def add_event(self, event: BreachEvent):
        """
        Add a breach event.
        
        Args:
            event: BreachEvent to add
        """
        self.events.append(event)
    
    def add_breach_from_dict(self, breach_data: Dict):
        """
        Add breach from dictionary data (e.g., from HIBP API).
        
        Args:
            breach_data: Dictionary with breach information
        """
        # Parse date
        date_str = breach_data.get('BreachDate', breach_data.get('date', ''))
        try:
            if isinstance(date_str, datetime):
                breach_date = date_str
            elif date_str:
                breach_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
            else:
                breach_date = datetime.now()
        except ValueError:
            breach_date = datetime.now()
        
        # Determine severity based on data types and sensitivity
        data_types = breach_data.get('DataClasses', breach_data.get('data_types', []))
        is_sensitive = breach_data.get('IsSensitive', breach_data.get('is_sensitive', False))
        
        severity = self._calculate_severity(data_types, is_sensitive)
        
        # Get affected count
        affected = breach_data.get('PwnCount', breach_data.get('affected_count', 0))
        
        event = BreachEvent(
            id=breach_data.get('Name', breach_data.get('id', str(len(self.events)))),
            name=breach_data.get('Title', breach_data.get('name', 'Unknown Breach')),
            date=breach_date,
            severity=severity,
            data_types=data_types,
            affected_count=affected,
            description=breach_data.get('Description', breach_data.get('description', '')),
            source=breach_data.get('Domain', breach_data.get('source', 'Unknown')),
            is_verified=breach_data.get('IsVerified', True),
            is_sensitive=is_sensitive
        )
        
        self.add_event(event)
    
    def _calculate_severity(self, data_types: List[str], is_sensitive: bool) -> str:
        """
        Calculate breach severity based on exposed data types.
        
        Args:
            data_types: List of exposed data types
            is_sensitive: Whether breach is marked sensitive
            
        Returns:
            Severity level string
        """
        if is_sensitive:
            return 'critical'
        
        critical_types = ['Passwords', 'Credit cards', 'Bank account numbers', 
                          'Social security numbers', 'Financial data']
        high_types = ['Email addresses', 'Phone numbers', 'Physical addresses',
                      'Private messages', 'IP addresses']
        medium_types = ['Usernames', 'Names', 'Dates of birth', 'Genders']
        
        data_types_lower = [dt.lower() for dt in data_types]
        
        for ct in critical_types:
            if ct.lower() in data_types_lower:
                return 'critical'
        
        for ht in high_types:
            if ht.lower() in data_types_lower:
                return 'high'
        
        for mt in medium_types:
            if mt.lower() in data_types_lower:
                return 'medium'
        
        return 'low' if data_types else 'unknown'
    
    def get_timeline_data(self, group_by: str = 'year') -> Dict:
        """
        Generate timeline data grouped by time period.
        
        Args:
            group_by: 'year', 'month', or 'quarter'
            
        Returns:
            Dictionary with timeline data for charts
        """
        if not self.events:
            return {
                'success': False,
                'error': 'No events to display',
                'data': []
            }
        
        # Sort events by date
        sorted_events = sorted(self.events, key=lambda x: x.date)
        
        # Group events
        groups = defaultdict(list)
        
        for event in sorted_events:
            if group_by == 'year':
                key = event.date.strftime('%Y')
            elif group_by == 'month':
                key = event.date.strftime('%Y-%m')
            elif group_by == 'quarter':
                quarter = (event.date.month - 1) // 3 + 1
                key = f"{event.date.year}-Q{quarter}"
            else:
                key = event.date.strftime('%Y')
            
            groups[key].append(event)
        
        # Build timeline data
        timeline_data = []
        cumulative = 0
        
        for period in sorted(groups.keys()):
            events = groups[period]
            cumulative += len(events)
            
            severity_breakdown = defaultdict(int)
            for event in events:
                severity_breakdown[event.severity] += 1
            
            timeline_data.append({
                'period': period,
                'count': len(events),
                'cumulative': cumulative,
                'severity': dict(severity_breakdown),
                'events': [
                    {
                        'name': e.name,
                        'date': e.date.strftime('%Y-%m-%d'),
                        'severity': e.severity,
                        'affected': e.affected_count,
                        'data_types': e.data_types[:5]  # Limit for display
                    }
                    for e in events
                ]
            })
        
        return {
            'success': True,
            'group_by': group_by,
            'total_events': len(self.events),
            'date_range': {
                'start': sorted_events[0].date.strftime('%Y-%m-%d'),
                'end': sorted_events[-1].date.strftime('%Y-%m-%d')
            },
            'data': timeline_data
        }
    
    def get_chart_js_data(self, chart_type: str = 'line') -> Dict:
        """
        Generate data formatted for Chart.js.
        
        Args:
            chart_type: 'line', 'bar', or 'doughnut'
            
        Returns:
            Chart.js compatible data structure
        """
        timeline = self.get_timeline_data()
        
        if not timeline['success']:
            return timeline
        
        if chart_type == 'line':
            return self._generate_line_chart_data(timeline['data'])
        elif chart_type == 'bar':
            return self._generate_bar_chart_data(timeline['data'])
        elif chart_type == 'doughnut':
            return self._generate_doughnut_chart_data()
        else:
            return self._generate_line_chart_data(timeline['data'])
    
    def _generate_line_chart_data(self, timeline_data: List[Dict]) -> Dict:
        """Generate line chart data."""
        labels = [d['period'] for d in timeline_data]
        
        datasets = [
            {
                'label': 'Breaches per Period',
                'data': [d['count'] for d in timeline_data],
                'borderColor': '#00ff88',
                'backgroundColor': 'rgba(0, 255, 136, 0.1)',
                'fill': True,
                'tension': 0.4
            },
            {
                'label': 'Cumulative Breaches',
                'data': [d['cumulative'] for d in timeline_data],
                'borderColor': '#00d4ff',
                'backgroundColor': 'rgba(0, 212, 255, 0.1)',
                'fill': True,
                'tension': 0.4,
                'yAxisID': 'y1'
            }
        ]
        
        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Breach Timeline'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {'display': True, 'text': 'Breaches'}
                    },
                    'y1': {
                        'position': 'right',
                        'beginAtZero': True,
                        'title': {'display': True, 'text': 'Cumulative'}
                    }
                }
            }
        }
    
    def _generate_bar_chart_data(self, timeline_data: List[Dict]) -> Dict:
        """Generate stacked bar chart data by severity."""
        labels = [d['period'] for d in timeline_data]
        
        # Create dataset for each severity level
        datasets = []
        
        for severity in self.SEVERITY_ORDER:
            data = []
            for d in timeline_data:
                data.append(d['severity'].get(severity, 0))
            
            if any(data):  # Only include if has data
                datasets.append({
                    'label': severity.capitalize(),
                    'data': data,
                    'backgroundColor': self.SEVERITY_COLORS[severity],
                    'borderColor': self.SEVERITY_COLORS[severity],
                    'borderWidth': 1
                })
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Breaches by Severity Over Time'
                    },
                    'legend': {
                        'position': 'bottom'
                    }
                },
                'scales': {
                    'x': {'stacked': True},
                    'y': {'stacked': True, 'beginAtZero': True}
                }
            }
        }
    
    def _generate_doughnut_chart_data(self) -> Dict:
        """Generate doughnut chart data for severity distribution."""
        severity_counts = defaultdict(int)
        
        for event in self.events:
            severity_counts[event.severity] += 1
        
        labels = []
        data = []
        colors = []
        
        for severity in self.SEVERITY_ORDER:
            if severity in severity_counts:
                labels.append(severity.capitalize())
                data.append(severity_counts[severity])
                colors.append(self.SEVERITY_COLORS[severity])
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderColor': '#1a1a2e',
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Breach Severity Distribution'
                    },
                    'legend': {
                        'position': 'right'
                    }
                }
            }
        }
    
    def get_severity_summary(self) -> Dict:
        """
        Get summary of breaches by severity.
        
        Returns:
            Dictionary with severity statistics
        """
        summary = {severity: 0 for severity in self.SEVERITY_ORDER}
        
        for event in self.events:
            summary[event.severity] = summary.get(event.severity, 0) + 1
        
        total = len(self.events)
        
        return {
            'total_breaches': total,
            'by_severity': summary,
            'percentages': {
                s: round(c / total * 100, 1) if total > 0 else 0
                for s, c in summary.items()
            },
            'most_common': max(summary.keys(), key=lambda k: summary[k]) if total > 0 else None
        }
    
    def get_data_types_analysis(self) -> Dict:
        """
        Analyze most commonly exposed data types.
        
        Returns:
            Dictionary with data type statistics
        """
        type_counts = defaultdict(int)
        
        for event in self.events:
            for data_type in event.data_types:
                type_counts[data_type] += 1
        
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_breaches_analyzed': len(self.events),
            'unique_data_types': len(type_counts),
            'data_types': [
                {
                    'type': dt,
                    'count': count,
                    'percentage': round(count / len(self.events) * 100, 1) if self.events else 0
                }
                for dt, count in sorted_types
            ],
            'top_5': sorted_types[:5]
        }
    
    def get_yearly_trend(self) -> Dict:
        """
        Calculate year-over-year breach trend.
        
        Returns:
            Dictionary with trend analysis
        """
        yearly_counts = defaultdict(int)
        
        for event in self.events:
            year = event.date.year
            yearly_counts[year] += 1
        
        years = sorted(yearly_counts.keys())
        
        if len(years) < 2:
            return {
                'available': False,
                'message': 'Not enough data for trend analysis'
            }
        
        # Calculate trend
        total_change = yearly_counts[years[-1]] - yearly_counts[years[0]]
        avg_per_year = sum(yearly_counts.values()) / len(years)
        
        # Determine trend direction
        if yearly_counts[years[-1]] > avg_per_year * 1.2:
            trend = 'increasing'
        elif yearly_counts[years[-1]] < avg_per_year * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'available': True,
            'years_analyzed': len(years),
            'yearly_counts': dict(yearly_counts),
            'average_per_year': round(avg_per_year, 1),
            'trend': trend,
            'first_year': years[0],
            'last_year': years[-1],
            'total_change': total_change
        }
    
    def get_full_report(self) -> Dict:
        """
        Generate comprehensive timeline report.
        
        Returns:
            Complete report dictionary
        """
        return {
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'timeline': self.get_timeline_data(),
            'severity_summary': self.get_severity_summary(),
            'data_types': self.get_data_types_analysis(),
            'yearly_trend': self.get_yearly_trend(),
            'charts': {
                'line': self.get_chart_js_data('line'),
                'bar': self.get_chart_js_data('bar'),
                'doughnut': self.get_chart_js_data('doughnut')
            },
            'total_events': len(self.events),
            'events_list': [
                {
                    'id': e.id,
                    'name': e.name,
                    'date': e.date.strftime('%Y-%m-%d'),
                    'severity': e.severity,
                    'affected': e.affected_count,
                    'source': e.source
                }
                for e in sorted(self.events, key=lambda x: x.date, reverse=True)
            ]
        }
    
    def export_to_json(self, filepath: str = None) -> str:
        """
        Export timeline data to JSON.
        
        Args:
            filepath: Optional file path to save to
            
        Returns:
            JSON string
        """
        report = self.get_full_report()
        json_str = json.dumps(report, indent=2, default=str)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str


# Example usage
if __name__ == "__main__":
    timeline = BreachTimeline()
    
    print("=" * 60)
    print("Breach Timeline Visualization - Test")
    print("=" * 60)
    
    # Add sample breaches
    sample_breaches = [
        {
            'Name': 'Adobe',
            'Title': 'Adobe',
            'BreachDate': '2013-10-04',
            'DataClasses': ['Email addresses', 'Passwords', 'Usernames'],
            'PwnCount': 153000000,
            'IsSensitive': False
        },
        {
            'Name': 'LinkedIn',
            'Title': 'LinkedIn',
            'BreachDate': '2016-05-18',
            'DataClasses': ['Email addresses', 'Passwords'],
            'PwnCount': 164611595,
            'IsSensitive': False
        },
        {
            'Name': 'Dropbox',
            'Title': 'Dropbox',
            'BreachDate': '2012-07-01',
            'DataClasses': ['Email addresses', 'Passwords'],
            'PwnCount': 68648009,
            'IsSensitive': False
        },
        {
            'Name': 'MyFitnessPal',
            'Title': 'MyFitnessPal',
            'BreachDate': '2018-02-01',
            'DataClasses': ['Email addresses', 'Passwords', 'Usernames'],
            'PwnCount': 143606147,
            'IsSensitive': False
        },
        {
            'Name': 'Canva',
            'Title': 'Canva',
            'BreachDate': '2019-05-24',
            'DataClasses': ['Email addresses', 'Names', 'Usernames', 'Passwords'],
            'PwnCount': 137272116,
            'IsSensitive': False
        }
    ]
    
    for breach in sample_breaches:
        timeline.add_breach_from_dict(breach)
    
    # Get report
    report = timeline.get_full_report()
    
    print(f"\nTotal Breaches: {report['total_events']}")
    print(f"\nSeverity Summary:")
    for severity, count in report['severity_summary']['by_severity'].items():
        if count > 0:
            print(f"  {severity.capitalize()}: {count}")
    
    print(f"\nYearly Trend: {report['yearly_trend'].get('trend', 'N/A')}")
    
    print("\nTop Exposed Data Types:")
    for dt, count in report['data_types']['top_5']:
        print(f"  {dt}: {count} breaches")
    
    print("\nTimeline Preview:")
    for point in report['timeline']['data']:
        print(f"  {point['period']}: {point['count']} breach(es)")
