from groq import Groq
# === AI PROVIDER HELPERS ===
def generate_with_groq(prompt, model="mixtral-8x7b-32768", temperature=0.7, max_tokens=1024):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

def generate_with_gemini(prompt, model="gemini-2.0-flash", temperature=0.7, max_tokens=1024):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set")
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"temperature": temperature, "max_output_tokens": max_tokens},
    )
    return response.text.strip()

def generate_ai_content(prompt, static_fallback, model_groq="mixtral-8x7b-32768", model_gemini="gemini-2.0-flash"):
    try:
        return generate_with_groq(prompt, model=model_groq)
    except Exception as groq_err:
        logger.warning(f"GROQ failed: {groq_err}")
        try:
            return generate_with_gemini(prompt, model=model_gemini)
        except Exception as gemini_err:
            logger.warning(f"Gemini failed: {gemini_err}")
            return static_fallback
"""
Cybersecurity Learning Mode Engine
===================================
Generates dynamic cybersecurity learning roadmaps, notes, and step-by-step
guides using the Google Gemini API.
"""


import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configure logging for the module
logger = logging.getLogger("learning_mode")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[LEARNING_MODE] %(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# ==================== ROADMAP DATA ====================

ROADMAP = {
    "beginner": {
        "label": "Beginner",
        "icon": "fa-seedling",
        "color": "#00e676",
        "topics": [
            {"id": "what-is-cybersecurity", "title": "What is Cybersecurity", "time": "30 min"},
            {"id": "internet-security-basics", "title": "Internet Security Basics", "time": "45 min"},
            {"id": "password-security", "title": "Password Security", "time": "40 min"},
            {"id": "phishing-awareness", "title": "Phishing Awareness", "time": "45 min"},
            {"id": "malware-basics", "title": "Malware Basics", "time": "50 min"},
            {"id": "network-fundamentals", "title": "Network Fundamentals", "time": "60 min"},
        ],
    },
    "intermediate": {
        "label": "Intermediate",
        "icon": "fa-laptop-code",
        "color": "#ffab00",
        "topics": [
            {"id": "linux-for-hackers", "title": "Linux for Hackers", "time": "90 min"},
            {"id": "networking-protocols", "title": "Networking Protocols", "time": "75 min"},
            {"id": "web-security", "title": "Web Security", "time": "80 min"},
            {"id": "sql-injection", "title": "SQL Injection", "time": "70 min"},
            {"id": "osint-techniques", "title": "OSINT Techniques", "time": "60 min"},
            {"id": "wireshark-basics", "title": "Wireshark Basics", "time": "75 min"},
        ],
    },
    "advanced": {
        "label": "Advanced",
        "icon": "fa-user-ninja",
        "color": "#ff1744",
        "topics": [
            {"id": "penetration-testing", "title": "Penetration Testing", "time": "120 min"},
            {"id": "vulnerability-scanning", "title": "Vulnerability Scanning", "time": "90 min"},
            {"id": "red-team-vs-blue-team", "title": "Red Team vs Blue Team", "time": "100 min"},
            {"id": "malware-analysis", "title": "Malware Analysis", "time": "120 min"},
            {"id": "digital-forensics", "title": "Digital Forensics", "time": "110 min"},
            {"id": "threat-intelligence", "title": "Threat Intelligence", "time": "100 min"},
        ],
    },
}


class LearningModeEngine:
    """Generate cybersecurity learning content via Google Gemini, with robust fallback and caching."""

    # Static fallback for Topic of the Day
    STATIC_DAILY_TOPIC = {
        "title": "Phishing Awareness",
        "summary": "Phishing is a common cyber attack where attackers trick users into revealing sensitive information. Learn how to spot and avoid phishing attempts.",
        "fun_fact": "The first phishing lawsuit was filed in 2004 against a California teenager.",
        "difficulty": "beginner"
    }

    # In-memory cache for daily topic
    _daily_topic_cache = {
        "data": None,
        "timestamp": None
    }

    MODELS = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash"]

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[LEARNING] Failed to init Gemini client: {e}")
                return None
        return self._client

    def _call_gemini(self, prompt: str, max_tokens: int = 4096) -> str | None:
        """Call Gemini with automatic model fallback."""
        if not self.api_key:
            print("[LEARNING] GEMINI_API_KEY not configured")
            return None
        if self.client is None:
            return None

        for model_name in self.MODELS:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"temperature": 0.7, "max_output_tokens": max_tokens},
                )
                return response.text.strip()
            except Exception as e:
                print(f"[LEARNING] Model {model_name} failed: {e}")
                continue
        return None

    def _parse_json(self, text: str):
        """Extract JSON from a Gemini response that may include markdown fences."""
        if text is None:
            return None
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None

    # ---------- public methods ----------

    def get_roadmap(self, topic: str = "cybersecurity"):
        """
        Generate a learning roadmap for a given topic using GROQ API, fallback to Gemini, then static content.
        """
        prompt = f"""Generate a concise, step-by-step learning roadmap for mastering {topic} in cybersecurity.\n\nFormat:\n1. Step 1\n2. Step 2\n...\n\nKeep each step short and actionable. Return plain text only."""
        static_fallback = ROADMAP
        content = generate_ai_content(prompt, static_fallback)
        if not content or (isinstance(content, str) and len(content.strip()) < 10):
            logger.warning("Empty AI response. Using static roadmap.")
            return static_fallback
        return content

    def generate_topic_content(self, topic_title: str, difficulty: str) -> dict | None:
        """Generate structured learning content for a single topic. Fallback to static roadmap if AI fails."""
        try:
            prompt = f"""You are a cybersecurity instructor. Generate structured learning content for the topic \"{topic_title}\" at {difficulty} level.\n\nReturn ONLY valid JSON (no markdown fences, no extra text):\n{{\n  \"title\": \"{topic_title}\",\n  \"difficulty\": \"{difficulty}\",\n  \"explanation\": \"A detailed 3-5 paragraph explanation of the topic\",\n  \"tools\": [\"Tool 1\", \"Tool 2\", \"Tool 3\"],\n  \"practice\": \"A practical exercise description (2-3 sentences)\",\n  \"quick_notes\": [\"Note 1\", \"Note 2\", \"Note 3\", \"Note 4\", \"Note 5\"],\n  \"steps\": [\n    \"Step 1 – description\",\n    \"Step 2 – description\",\n    \"Step 3 – description\",\n    \"Step 4 – description\"\n  ]\n}}"""
            raw = self._call_gemini(prompt, max_tokens=4096)
            data = self._parse_json(raw)
            if data and isinstance(data, dict):
                return data
            logger.warning(f"AI failed to generate topic content for '{topic_title}'. Returning static roadmap content.")
        except Exception as e:
            logger.error(f"Exception in generate_topic_content: {e}")
        # Fallback: return static roadmap topic if available
        for level in ROADMAP.values():
            for topic in level["topics"]:
                if topic["title"].lower() == topic_title.lower():
                    return {
                        "title": topic["title"],
                        "difficulty": difficulty,
                        "explanation": f"This is a static fallback explanation for {topic["title"]}.",
                        "tools": [],
                        "practice": "No AI content available. Practice with online resources.",
                        "quick_notes": [],
                        "steps": []
                    }
        # If not found, return a generic fallback
        return {
            "title": topic_title,
            "difficulty": difficulty,
            "explanation": "AI content unavailable. Please try again later.",
            "tools": [],
            "practice": "No AI content available.",
            "quick_notes": [],
            "steps": []
        }

    def ask_about_topic(self, topic_title: str, question: str) -> str | None:
        """Answer a deeper question about a topic. Fallback to static message if AI fails."""
        try:
            prompt = f"""You are a cybersecurity instructor. The student is learning about \"{topic_title}\" and has asked:\n\n\"{question}\"\n\nProvide a clear, detailed answer in plain text. Use bullet points where appropriate. Keep the answer educational and practical. Limit to around 300 words."""
            answer = self._call_gemini(prompt, max_tokens=2048)
            if answer:
                return answer
            logger.warning(f"AI failed to answer question about '{topic_title}'. Returning static answer.")
        except Exception as e:
            logger.error(f"Exception in ask_about_topic: {e}")
        return "AI is currently unavailable. Please try again later or review the static roadmap content."

    def generate_daily_topic(self) -> dict | None:
        """Generate a random daily cybersecurity learning topic, with 24h cache and fallback."""
        try:
            now = datetime.now()
            cache = self._daily_topic_cache
            # Check if cache is valid (24h)
            if cache["data"] and cache["timestamp"]:
                age = (now - cache["timestamp"]).total_seconds()
                if age < 86400:
                    logger.info("Returning cached daily topic.")
                    return cache["data"]

            prompt = """You are a cybersecurity instructor. Suggest one interesting cybersecurity topic of the day for students.\n\nReturn ONLY valid JSON (no markdown fences):\n{\n  \"title\": \"Topic title\",\n  \"summary\": \"A short 2-3 sentence summary\",\n  \"fun_fact\": \"An interesting fact related to the topic\",\n  \"difficulty\": \"beginner or intermediate or advanced\"\n}"""
            raw = self._call_gemini(prompt, max_tokens=1024)
            data = self._parse_json(raw)
            if data and isinstance(data, dict):
                cache["data"] = data
                cache["timestamp"] = now
                logger.info("Generated and cached new daily topic.")
                return data
            logger.warning("AI failed to generate daily topic. Using static fallback.")
        except Exception as e:
            logger.error(f"Exception in generate_daily_topic: {e}")
        # Fallback: static topic, also cache it
        self._daily_topic_cache["data"] = self.STATIC_DAILY_TOPIC
        self._daily_topic_cache["timestamp"] = datetime.now()
        return self.STATIC_DAILY_TOPIC

    def generate_full_roadmap_content(self) -> dict | None:
        """Generate an AI-powered overview of the entire roadmap. Fallback to static summary if AI fails."""
        try:
            prompt = """You are a cybersecurity instructor. Generate a learning roadmap overview from beginner to advanced.\n\nReturn ONLY valid JSON (no markdown fences):\n{\n  \"overview\": \"A motivational 2-3 sentence overview for learners\",\n  \"beginner_summary\": \"What beginners will learn (2 sentences)\",\n  \"intermediate_summary\": \"What intermediates will learn (2 sentences)\",\n  \"advanced_summary\": \"What advanced learners will master (2 sentences)\",\n  \"career_tip\": \"A short career tip for aspiring cybersecurity professionals\"\n}"""
            raw = self._call_gemini(prompt, max_tokens=1024)
            data = self._parse_json(raw)
            if data and isinstance(data, dict):
                return data
            logger.warning("AI failed to generate roadmap overview. Returning static summary.")
        except Exception as e:
            logger.error(f"Exception in generate_full_roadmap_content: {e}")
        # Fallback: static roadmap summary
        return {
            "overview": "Welcome to your cybersecurity journey! This roadmap will guide you from the basics to advanced topics, helping you build real-world skills.",
            "beginner_summary": "Beginners will learn the fundamentals of cybersecurity, including password safety, phishing, and basic network concepts.",
            "intermediate_summary": "Intermediates will explore technical concepts like web security, OSINT, and hands-on tools.",
            "advanced_summary": "Advanced learners will master penetration testing, malware analysis, and threat intelligence.",
            "career_tip": "Stay curious and keep practicing—cybersecurity is a field that rewards continuous learning!"
        }
