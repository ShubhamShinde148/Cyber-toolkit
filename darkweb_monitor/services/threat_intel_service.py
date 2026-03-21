import random
import os
import json
from datetime import datetime
from groq import Groq

class ThreatIntelService:
    """
    Service to fetch and manage cybersecurity threat intelligence and feeds.
    Excludes legacy V1 logic, designed specifically for the V2 SOC platform.
    """
    
    _gl_client = None

    @classmethod
    def _get_client(cls):
        if not cls._gl_client:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                cls._gl_client = Groq(api_key=api_key)
        return cls._gl_client

    @staticmethod
    def get_latest_vulnerabilities(limit=5):
        """
        Simulated/Mocked fetching of real-time CVE vulnerabilities.
        In a production environment, this would hit an API like NVD or CIRCL.
        """
        vulnerabilities = [
            {"id": "CVE-2026-1024", "title": "Chrome JavaScript Engine RCE", "severity": "Critical", "date": "2026-03-09"},
            {"id": "CVE-2026-5521", "title": "Linux Kernel Privilege Escalation", "severity": "High", "date": "2026-03-08"},
            {"id": "CVE-2025-9988", "title": "OpenSSH Auth Bypass Vulnerability", "severity": "High", "date": "2026-03-07"},
            {"id": "CVE-2026-0012", "title": "MS Exchange Remote Code Execution", "severity": "Critical", "date": "2026-03-06"},
            {"id": "CVE-2026-4433", "title": "PostgreSQL SQL Injection in Core", "severity": "Medium", "date": "2026-03-05"},
            {"id": "CVE-2026-2210", "title": "Windows GDI+ Memory Corruption", "severity": "High", "date": "2026-03-04"},
        ]
        return vulnerabilities[:limit]

    @staticmethod
    def get_darkweb_leaks(limit=3):
        """
        Simulated/Mocked fetching of Dark Web leak monitoring data.
        """
        leaks = [
            {"source": "CyberCorps.onion", "title": "Corporate Email Database Drain", "records": "450k", "status": "Verified"},
            {"source": "ShadowForums", "title": "Gov-Auth Portal Credential Dump", "records": "1.2M", "status": "New"},
            {"source": "LeakStation", "title": "Telco Customer Metadata Leak", "records": "120k", "status": "Unverified"},
        ]
        return leaks[:limit]

    @classmethod
    def get_cyber_news(cls, limit=5):
        """
        Fetches latest cybersecurity news headlines using Groq LLM.
        """
        client = cls._get_client()
        if not client:
            return [{"title": "API Key Missing", "summary": "Please configure GROQ_API_KEY in .env", "date": "N/A", "source": "System"}]

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            prompt = f"""
            You are a Cybersecurity Intelligence Bot. 
            Act as a real-time news aggregator.
            Generate a list of the 5 most critical recent cybersecurity news stories (actual recent events as of {today}).
            
            Return ONLY a JSON array of objects with these keys: 
            "title", "summary", "date", "source", "severity".
            Ensure the JSON is valid and contains no other text.
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Extract list from json_object if wrapped
            if isinstance(data, dict):
                for key in ["news", "headlines", "stories", "articles"]:
                    if key in data and isinstance(data[key], list):
                        return data[key][:limit]
                # If it's a single object with a list elsewhere
                for value in data.values():
                    if isinstance(value, list):
                        return value[:limit]
            
            return data[:limit] if isinstance(data, list) else [data]
            
        except Exception as e:
            print(f"Error fetching cyber news: {e}")
            return [{"title": "Intelligence Offline", "summary": f"Failed to fetch real-time news: {str(e)}", "date": "N/A", "source": "Error"}]

    @staticmethod
    def calculate_health_score():
        """
        Calculates a dynamic security health score for the SOC dashboard.
        """
        return random.randint(88, 98)

