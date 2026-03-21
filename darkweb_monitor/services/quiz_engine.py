# Global AI quiz generator instance removed in favor of static bank


"""
Cybersecurity Quiz Engine
=========================
Quiz engine loading questions from a local static JSON file.
"""

import random
import copy
import os
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

# Configure logging for the module
logger = logging.getLogger("quiz_engine")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[QUIZ_ENGINE] %(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


@dataclass
class Question:
    """Represents a quiz question."""
    id: int
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option (0-3)
    category: str
    difficulty: str  # beginner, intermediate, advanced
    explanation: str = ""


@dataclass
class QuizResult:
    """Stores quiz completion results."""
    quiz_id: str
    participant_name: str
    email: str
    score: int
    total: int
    percentage: float
    passed: bool
    completion_time: str
    answers: Dict[int, int]
    category_scores: Dict[str, Dict]

class CybersecurityQuiz:
    """Offline Static Cybersecurity Knowledge Quiz."""
    
    PASS_THRESHOLD = 70  # 70% to pass
    
    def __init__(self):
        self.all_questions: List[Question] = self._load_questions()
        self.active_quizzes: Dict[str, List[Question]] = {}
    
    def _load_questions(self) -> List[Question]:
        """Load all quiz questions from the local JSON file."""
        questions_list = []
        try:
            # Load the new 200 question static bank
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cybersecurity_quiz_200_questions.json')
            if not os.path.exists(data_path):
                logger.error(f"Quiz questions file not found at {data_path}")
                return []
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_id = 1
            for category, q_list in data.items():
                # Make the category name readable e.g., "osint" -> "OSINT", "web_security" -> "Web Security"
                display_category = category.replace('_', ' ').title() if category != 'osint' else 'OSINT'
                
                for q in q_list:
                    options = q.get('options', [])
                    answer_str = q.get('answer', '')
                    
                    # Find the index of the correct answer
                    correct_idx = -1
                    for i, opt in enumerate(options):
                        if opt == answer_str:
                            correct_idx = i
                            break
                    
                    # Fallback if answer string doesn't exactly match
                    if correct_idx == -1:
                        logger.warning(f"Answer mismatch for question: {q.get('question')} - Answer: {answer_str}")
                        correct_idx = 0
                        
                    questions_list.append(Question(
                        id=current_id,
                        question=q.get('question', ''),
                        options=options,
                        correct_answer=correct_idx,
                        category=display_category,
                        difficulty='intermediate', # The new JSON doesn't specify difficulty, default to intermediate
                        explanation=q.get('explanation', '')
                    ))
                    current_id += 1
            
            logger.info(f"Successfully loaded {len(questions_list)} questions from static bank.")
            return questions_list
            
        except Exception as e:
            logger.error(f"Failed to load static quiz questions: {e}")
            return []
    
    def start_quiz(self, category: str = "all", difficulty: str = "intermediate", count: int = 10, shuffle: bool = True) -> Dict:
        """Start a new quiz session filtered by category and difficulty."""
        quiz_id = hashlib.md5(f"{datetime.now().isoformat()}{random.random()}".encode()).hexdigest()[:12]
        
        # Filter available questions based on criteria
        pool = []
        for q in self.all_questions:
            category_match = (category.lower() == "all" or category.lower() == q.category.lower().replace(" ", "_"))
            
            if category_match:
                pool.append(q)
        
        # Fallback if not enough questions meet criteria
        if len(pool) < count:
            logger.warning(f"Only {len(pool)} questions found for {category}. Supplementing with other categories.")
            for q in self.all_questions:
                if q not in pool:
                    pool.append(q)
                if len(pool) >= count:
                    break
                     
        # Select the requested count of questions
        selected_questions = random.sample(pool, min(int(count), len(pool)))
        selected_questions = copy.deepcopy(selected_questions)
        
        if shuffle:
            random.shuffle(selected_questions)
            # Reassign IDs specifically for this session 1 -> N
            for i, q in enumerate(selected_questions):
                q.id = i + 1
                # Shuffle options for each question
                options_with_correct = list(enumerate(q.options))
                random.shuffle(options_with_correct)
                new_correct = next(i for i, (orig_i, _) in enumerate(options_with_correct) if orig_i == q.correct_answer)
                q.options = [opt for _, opt in options_with_correct]
                q.correct_answer = new_correct
        else:
            for i, q in enumerate(selected_questions):
                q.id = i + 1
        
        self.active_quizzes[quiz_id] = selected_questions
        
        return {
            "quiz_id": quiz_id,
            "total_questions": len(selected_questions),
            "pass_threshold": self.PASS_THRESHOLD,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options,
                    "category": q.category,
                    "difficulty": q.difficulty
                }
                for q in selected_questions
            ]
        }
    
    def submit_quiz(self, quiz_id: str, participant_name: str, email: str, answers: Dict[int, int]) -> Optional[QuizResult]:
        """Submit quiz answers and calculate results."""
        if quiz_id not in self.active_quizzes:
            return None
        
        questions = self.active_quizzes[quiz_id]
        correct = 0
        category_scores: Dict[str, Dict] = {}
        
        for q in questions:
            cat = q.category
            if cat not in category_scores:
                category_scores[cat] = {"correct": 0, "total": 0}
            category_scores[cat]["total"] += 1
            
            if answers.get(q.id) == q.correct_answer:
                correct += 1
                category_scores[cat]["correct"] += 1
        
        total = len(questions)
        percentage = (correct / total) * 100 if total > 0 else 0
        passed = percentage >= self.PASS_THRESHOLD
        
        result = QuizResult(
            quiz_id=quiz_id,
            participant_name=participant_name,
            email=email,
            score=correct,
            total=total,
            percentage=round(percentage, 1),
            passed=passed,
            completion_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            answers=answers,
            category_scores=category_scores
        )
        
        # Clean up active quiz
        del self.active_quizzes[quiz_id]
        
        return result
    
    def get_detailed_results(self, quiz_id: str, answers: Dict[int, int]) -> List[Dict]:
        """Get detailed results with explanations."""
        if quiz_id not in self.active_quizzes:
            return []
        
        questions = self.active_quizzes[quiz_id]
        results = []
        
        for q in questions:
            user_answer = answers.get(q.id, -1)
            results.append({
                "question_id": q.id,
                "question": q.question,
                "options": q.options,
                "user_answer": user_answer,
                "correct_answer": q.correct_answer,
                "is_correct": user_answer == q.correct_answer,
                "explanation": q.explanation,
                "category": q.category
            })
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all question categories."""
        return list(set(q.category for q in self.questions))


# Certificate generation using ReportLab
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
import io
import math


class CertificateGenerator:
    """Generate professional PDF certificates for quiz completion."""
    
    def __init__(self):
        self.width, self.height = landscape(letter)
    
    def _draw_shield_icon(self, c, x, y, size, fill_color, stroke_color):
        """Draw a shield icon at the specified position."""
        p = c.beginPath()
        s = size
        p.moveTo(x, y + s * 0.5)
        p.curveTo(x, y + s * 0.85, x + s * 0.2, y + s, x + s * 0.5, y + s)
        p.curveTo(x + s * 0.8, y + s, x + s, y + s * 0.85, x + s, y + s * 0.5)
        p.lineTo(x + s, y + s * 0.15)
        p.curveTo(x + s * 0.75, y + s * 0.1, x + s * 0.55, y, x + s * 0.5, y - s * 0.15)
        p.curveTo(x + s * 0.45, y, x + s * 0.25, y + s * 0.1, x, y + s * 0.15)
        p.close()
        c.setFillColor(fill_color)
        c.setStrokeColor(stroke_color)
        c.setLineWidth(1.5)
        c.drawPath(p, fill=1, stroke=1)
    
    def _draw_decorative_corners(self, c, x1, y1, x2, y2, color, length=40):
        """Draw decorative corner brackets."""
        c.setStrokeColor(color)
        c.setLineWidth(2.5)
        # Top-left
        c.line(x1, y1, x1 + length, y1)
        c.line(x1, y1, x1, y1 - length)
        # Top-right
        c.line(x2, y1, x2 - length, y1)
        c.line(x2, y1, x2, y1 - length)
        # Bottom-left
        c.line(x1, y2, x1 + length, y2)
        c.line(x1, y2, x1, y2 + length)
        # Bottom-right
        c.line(x2, y2, x2 - length, y2)
        c.line(x2, y2, x2, y2 + length)
    
    def _draw_hexagon(self, c, cx, cy, radius, fill_color, stroke_color):
        """Draw a hexagonal shape."""
        p = c.beginPath()
        for i in range(6):
            angle = math.radians(60 * i - 30)
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            if i == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        p.close()
        c.setFillColor(fill_color)
        c.setStrokeColor(stroke_color)
        c.setLineWidth(2)
        c.drawPath(p, fill=1, stroke=1)
    
    def _draw_circuit_lines(self, c, color):
        """Draw subtle circuit-board pattern as background decoration."""
        c.saveState()
        c.setStrokeColor(color)
        c.setLineWidth(0.5)
        
        # Horizontal lines with nodes
        lines = [
            (60, self.height - 80, 180, self.height - 80),
            (self.width - 180, self.height - 80, self.width - 60, self.height - 80),
            (60, 80, 180, 80),
            (self.width - 180, 80, self.width - 60, 80),
            (60, self.height / 2 - 10, 100, self.height / 2 - 10),
            (self.width - 100, self.height / 2 - 10, self.width - 60, self.height / 2 - 10),
        ]
        for x1, y1, x2, y2 in lines:
            c.line(x1, y1, x2, y2)
            c.circle(x1, y1, 2, fill=1)
            c.circle(x2, y2, 2, fill=1)
        
        # Vertical accent lines
        c.line(60, 80, 60, 140)
        c.line(self.width - 60, 80, self.width - 60, 140)
        c.line(60, self.height - 140, 60, self.height - 80)
        c.line(self.width - 60, self.height - 140, self.width - 60, self.height - 80)
        
        c.restoreState()
    
    def _draw_qr_code(self, c, x, y, size, url):
        """Draw a QR code at the specified position."""
        qr_code = qr.QrCodeWidget(url)
        bounds = qr_code.getBounds()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
        d.add(qr_code)
        renderPDF.draw(d, c, x, y)

    def generate(self, result: QuizResult, certificate_id: str = None) -> bytes:
        """Generate a premium professional PDF certificate (landscape letter)."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        c.setTitle("Cybersecurity Awareness Certificate")
        c.setAuthor("Dark Web Monitor")

        # Colors
        primary = HexColor("#00ffc6")  # Cyber Green
        secondary = HexColor("#00d4ff") # Cyber Blue
        dark_bg = HexColor("#050a0f")   # Deep Dark
        dark_card = HexColor("#080f19") # Card Dark
        gold = HexColor("#ffd700")
        white = HexColor("#ffffff")
        gray_text = HexColor("#888888")
        light_gray = HexColor("#c0c0d0")
        red_fail = HexColor("#ff4d4d")
        
        cx = self.width / 2

        # ── 1. Background ──
        c.setFillColor(dark_bg)
        c.rect(0, 0, self.width, self.height, fill=1)

        # ── 2. Decorative Elements ──
        # Glowing border lines top/bottom
        c.setLineWidth(2)
        c.setStrokeColor(primary)
        c.line(40, self.height - 20, self.width - 40, self.height - 20)
        c.line(40, 20, self.width - 40, 20)
        
        # Decorative corners
        self._draw_decorative_corners(c, 40, self.height - 40, self.width - 40, 40, primary, length=30)

        # ── 2.5. Watermark Background (Shield from Photo 1) ──
        c.saveState()
        # Draw a large subtle shield in the center instead of "SECURED" text
        self._draw_shield_icon(c, cx - 150, self.height/2 - 180, 300, dark_bg, primary)
        c.restoreState()

        # ── 3. Header ──
        # Logo Icon
        shield_size = 30
        self._draw_shield_icon(c, 60, self.height - 80, shield_size, dark_card, primary)
        
        # Logo Text
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(100, self.height - 65, "DARK WEB MONITOR")
        c.setFillColor(gray_text)
        c.setFont("Helvetica", 7)
        c.drawString(100, self.height - 75, "SECURITY LAB")
        
        # Program Label
        c.setFillColor(gold)
        c.setFont("Helvetica", 8)
        c.drawRightString(self.width - 60, self.height - 70, "CYBERSECURITY AWARENESS PROGRAM")

        # ── 4. Main Title Section ──
        # Draw the Award Seal with ribbon effect from Photo 1
        seal_y = self.height - 130
        c.setFillColorRGB(0, 1, 0.776, alpha=0.15)
        c.circle(cx, seal_y, 25, fill=1, stroke=0)
        c.setStrokeColor(primary)
        c.setLineWidth(1.5)
        c.circle(cx, seal_y, 25, fill=0, stroke=1)
        
        # Ribbon spikes/decoration
        c.setLineWidth(1)
        for i in range(12):
            angle = math.radians(i * 30)
            inner_r = 25
            outer_r = 28
            c.line(cx + inner_r * math.cos(angle), seal_y + inner_r * math.sin(angle),
                   cx + outer_r * math.cos(angle), seal_y + outer_r * math.sin(angle))
        
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx, seal_y - 4, "AWARD")
        
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(cx, self.height - 190, "CERTIFICATE OF COMPLETION")
        
        # Divider Line
        c.setStrokeColor(primary)
        c.setLineWidth(1)
        c.line(cx - 150, self.height - 205, cx + 150, self.height - 205)
        # Diamond in center of line
        c.setFillColor(primary)
        c.rect(cx - 3, self.height - 208, 6, 6, fill=1, stroke=0)

        c.setFillColor(light_gray)
        c.setFont("Helvetica", 11)
        c.drawCentredString(cx, self.height - 235, "This is to certify that")

        # ── 5. Participant Name ──
        name_text = result.participant_name.upper()
        c.setFillColor(gold)
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(cx, self.height - 285, name_text)
        
        # Name underline
        c.setStrokeColor(gold)
        c.setLineWidth(2)
        c.line(cx - 120, self.height - 300, cx + 120, self.height - 300)

        # ── 6. Description ──
        c.setFillColor(light_gray)
        c.setFont("Helvetica", 10)
        c.drawCentredString(cx, self.height - 335, "has successfully completed the Cybersecurity Awareness Quiz demonstrating proficiency in")
        c.drawCentredString(cx, self.height - 350, "cybersecurity fundamentals, threat awareness, and security best practices.")

        # ── 7. Info Blocks (Score, Status) ──
        info_y = self.height - 430
        
        # Score Block
        score_x = cx - 100
        # Draw Ring (glowing effect)
        c.setStrokeColor(primary)
        c.setLineWidth(4)
        c.circle(score_x, info_y + 35, 30, fill=0)
        c.setStrokeColorRGB(0, 1, 0.776, alpha=0.3)
        c.setLineWidth(6)
        c.circle(score_x, info_y + 35, 32, fill=0) # Outer glow
        
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(score_x, info_y + 28, f"{result.percentage}%")
        c.setFillColor(gray_text)
        c.setFont("Helvetica", 8)
        c.drawCentredString(score_x, info_y - 10, f"Score: {result.score}/{result.total}")

        # Status Block
        status_x = cx + 100
        status_color = primary if result.passed else red_fail
        status_text = "PASSED" if result.passed else "NOT PASSED"
        # Icon representation
        c.setStrokeColor(status_color)
        c.setLineWidth(2)
        c.circle(status_x, info_y + 40, 15, fill=0)
        c.setFillColor(status_color)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(status_x, info_y + 10, status_text)
        c.setFillColor(gray_text)
        c.setFont("Helvetica", 8)
        c.drawCentredString(status_x, info_y - 10, "Status")

        # ── 8. QR Code Section ──
        qr_y = 65
        qr_size = 50
        verify_url = f"https://darkwebmonitor.com/verify/{certificate_id or 'DEFAULT'}"
        c.setFillColor(white)
        c.rect(cx - qr_size/2 - 5, qr_y - 5, qr_size + 10, qr_size + 10, fill=1, stroke=0)
        self._draw_qr_code(c, cx - qr_size/2, qr_y, qr_size, verify_url)
        
        c.setFillColor(gray_text)
        c.setFont("Helvetica", 6)
        c.drawCentredString(cx, qr_y - 15, "Scan to Verify Certificate")

        # ── 9. Footer Section ──
        # Cert ID (Left)
        c.setFillColor(gray_text)
        c.setFont("Helvetica", 8)
        cert_id = certificate_id or f"DWM-CERT-{result.quiz_id[:8].upper()}"
        c.drawString(60, 55, f"Certificate ID: {cert_id}")
        
        try:
            parsed_date = datetime.strptime(result.completion_time, '%Y-%m-%d %H:%M:%S')
            fmt_date = parsed_date.strftime('%B %d, %Y').replace(' 0', ' ')
        except Exception:
            fmt_date = result.completion_time.split(' ')[0]
            
        c.drawString(60, 42, f"Date Issued: {fmt_date}")

        # Signature (Right)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(self.width - 60, 45, "Verified by Dark Web Monitor")

        c.save()
        buffer.seek(0)
        return buffer.getvalue()


if __name__ == "__main__":
    # Test quiz
    quiz = CybersecurityQuiz()
    session = quiz.start_quiz()
    print(f"Quiz started: {session['quiz_id']}")
    print(f"Questions: {session['total_questions']}")
    
    # Simulate answers (all correct for testing)
    answers = {}
    for q in quiz.active_quizzes[session['quiz_id']]:
        answers[q.id] = q.correct_answer
    
    result = quiz.submit_quiz(session['quiz_id'], "Test User", "test@example.com", answers)
    print(f"Score: {result.score}/{result.total} ({result.percentage}%)")
    print(f"Passed: {result.passed}")
    
    # Generate certificate
    generator = CertificateGenerator()
    pdf_bytes = generator.generate(result)
    with open("test_certificate.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("Certificate generated: test_certificate.pdf")
