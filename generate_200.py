import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables to get the API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") 
if not api_key:
    print("NO API KEY")
    exit(1)

genai.configure(api_key=api_key)

CATEGORIES = [
    "OSINT",
    "Web Security",
    "Network Security",
    "Cryptography",
    "Malware & Threats",
    "Phishing Attacks",
    "Data Breaches",
    "Authentication",
    "Password Security",
    "Social Engineering"
]

QUESTIONS_PER_CATEGORY = 20  # 10 categories * 20 = 200 questions

def generate_questions(category, count):
    prompt = f"""
    Generate exactly {count} UNIQUE cybersecurity multiple-choice questions about "{category}".
    Do not repeat any questions. Ensure they are varying in difficulty and cover diverse sub-topics within {category}.
    
    Output ONLY raw JSON format matching this exact array structure, with no markdown code blocks around it:
    [
      {{
        "question": "What does XSS stand for?",
        "options": [
          "Cross Site Scripting",
          "External Server Security",
          "Cross Server Scripting",
          "Extensible Secure System"
        ],
        "answer": "Cross Site Scripting"
      }}
    ]
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    # Try to parse the JSON
    try:
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return parsed
    except Exception as e:
        print(f"Failed to parse category {category}: {e}")
        return []

all_data = {}

for cat in CATEGORIES:
    print(f"Generating 20 questions for {cat}...")
    safe_cat_name = cat.lower().replace(" ", "_").replace("&", "and")
    questions = generate_questions(cat, QUESTIONS_PER_CATEGORY)
    print(f"Got {len(questions)} for {cat}")
    all_data[safe_cat_name] = questions

# Save to the JSON file
output_path = "cybersecurity_quiz_200_questions.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=4)

print(f"Successfully generated unique 200 questions and saved to {output_path}")
