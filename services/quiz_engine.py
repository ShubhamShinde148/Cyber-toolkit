
class Question:
    def __init__(self, id=None, question=None, options=None, correct_answer=None, category=None, difficulty=None, explanation=None):
        self.id = id
        self.question = question
        self.options = options or []
        self.correct_answer = correct_answer
        self.category = category
        self.difficulty = difficulty
        self.explanation = explanation



import uuid
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class CybersecurityQuiz:
    def __init__(self):
        self.active_quizzes = {}
        def q(question, options, correct_answer, category, difficulty, explanation):
            return Question(
                id=str(uuid.uuid4()),
                question=question,
                options=options,
                correct_answer=correct_answer,
                category=category,
                difficulty=difficulty,
                explanation=explanation
            )

        self.questions_bank = [
            q(
                "What is phishing?",
                ["A social engineering attack", "A backup strategy", "A firewall mode", "A VPN protocol"],
                0, "Social Engineering", "Easy",
                "Phishing tricks users into revealing credentials or sensitive data."
            ),
            q(
                "What does VPN stand for?",
                ["Virtual Private Network", "Verified Public Node", "Virtual Protection Net", "Variable Proxy Network"],
                0, "Network Security", "Easy",
                "VPN stands for Virtual Private Network."
            ),
            q(
                "Which control is best for reducing password reuse risk?",
                ["Single Sign-On with no MFA", "Password complexity only", "Multi-Factor Authentication", "Weekly password hints"],
                2, "Identity & Access", "Easy",
                "MFA significantly reduces account takeover risk even when passwords are reused."
            ),
            q(
                "Which protocol provides encrypted web traffic?",
                ["HTTP", "FTP", "HTTPS", "Telnet"],
                2, "Network Security", "Easy",
                "HTTPS wraps HTTP with TLS encryption."
            ),
            q(
                "In cloud security, least privilege means:",
                ["Users get admin by default", "Access is granted only as needed", "All users share one root account", "Permissions never expire"],
                1, "Cloud Security", "Easy",
                "Least privilege grants minimal access required for tasks."
            ),
            q(
                "What is a common indicator of malware infection?",
                ["Faster boot time", "Unexpected pop-ups and high CPU", "Lower memory use", "Automatic OS hardening"],
                1, "Endpoint Security", "Easy",
                "Unusual pop-ups and resource spikes are frequent malware indicators."
            ),
            q(
                "What does SQL injection target?",
                ["Network cable firmware", "Database queries in applications", "DNS cache only", "Bluetooth pairing keys"],
                1, "Application Security", "Medium",
                "SQL injection exploits unsafe query construction."
            ),
            q(
                "What is the purpose of a SIEM platform?",
                ["Store backups offline", "Aggregate and analyze security logs", "Design UI dashboards", "Patch routers automatically"],
                1, "Security Operations", "Medium",
                "SIEM centralizes logs and supports threat detection and investigation."
            ),
            q(
                "Which is the strongest hash for password storage when configured correctly?",
                ["MD5", "SHA1", "bcrypt", "CRC32"],
                2, "Cryptography", "Medium",
                "bcrypt is a slow, adaptive password hashing algorithm."
            ),
            q(
                "What is the main goal of network segmentation?",
                ["Increase monitor resolution", "Limit lateral movement", "Disable encryption", "Reduce DNS queries"],
                1, "Network Security", "Medium",
                "Segmentation isolates zones to contain breaches."
            ),
            q(
                "Which header helps mitigate clickjacking?",
                ["X-Frame-Options", "Content-Encoding", "ETag", "Accept-Language"],
                0, "Application Security", "Medium",
                "X-Frame-Options prevents untrusted framing."
            ),
            q(
                "What is an IOC in incident response?",
                ["Internet Operations Command", "Indicator of Compromise", "Identity of Customer", "Inline Object Cache"],
                1, "Incident Response", "Medium",
                "IOCs are forensic artifacts signaling possible intrusion."
            ),
            q(
                "Why is patch management critical?",
                ["It changes UI themes", "It removes known vulnerabilities", "It deletes logs", "It disables admin accounts"],
                1, "Vulnerability Management", "Easy",
                "Patching closes known security gaps before attackers exploit them."
            ),
            q(
                "Which attack attempts to overwhelm a service with traffic?",
                ["MITM", "DDoS", "Privilege escalation", "Code signing"],
                1, "Network Security", "Easy",
                "DDoS floods a target to disrupt availability."
            ),
            q(
                "What is data exfiltration?",
                ["Encrypting files at rest", "Unauthorized transfer of data out of an environment", "Deleting old backups", "Rotating API keys"],
                1, "Data Protection", "Medium",
                "Exfiltration is the theft and outbound movement of sensitive data."
            ),
            q(
                "What does RBAC stand for?",
                ["Risk-Based Access Control", "Role-Based Access Control", "Remote Backup Access Channel", "Resource Boundary Access Code"],
                1, "Identity & Access", "Easy",
                "RBAC assigns permissions based on user roles."
            ),
            q(
                "What is the safest default action for a suspicious email attachment?",
                ["Open it in production", "Forward to all colleagues", "Report and quarantine", "Rename and execute"],
                2, "Social Engineering", "Easy",
                "Suspicious attachments should be reported and isolated."
            ),
            q(
                "Which model assumes breach and continuously verifies access?",
                ["Castle-and-moat", "Zero Trust", "Flat network trust", "Anonymous trust"],
                1, "Architecture", "Medium",
                "Zero Trust validates every request regardless of network location."
            ),
            q(
                "Which is a key objective of disaster recovery planning?",
                ["Increase ad click-through", "Restore critical services quickly after disruption", "Replace antivirus daily", "Reduce password length"],
                1, "Business Continuity", "Medium",
                "DR focuses on recovering systems within target timelines."
            ),
            q(
                "What is privilege escalation?",
                ["Gaining higher access than authorized", "Reducing account permissions", "Encrypting admin logs", "Changing DNS zones"],
                0, "Threats", "Medium",
                "Privilege escalation lets attackers move from low to high permissions."
            ),
            q(
                "Which statement about backups is most secure?",
                ["Backups should be writable by everyone", "Only cloud backups matter", "Use versioned, offline or immutable backups", "Backups are optional with RAID"],
                2, "Data Protection", "Medium",
                "Offline/immutable backups help resist ransomware tampering."
            ),
            q(
                "What is CSP primarily used for in web apps?",
                ["Compress static assets", "Restrict allowed content sources", "Manage SQL transactions", "Schedule cron jobs"],
                1, "Application Security", "Medium",
                "Content Security Policy helps reduce XSS and content injection risk."
            ),
            q(
                "A security runbook is best described as:",
                ["A legal privacy policy", "A step-by-step operational response guide", "A type of firewall rule", "A public bug bounty report"],
                1, "Security Operations", "Easy",
                "Runbooks standardize response actions during incidents."
            ),
            q(
                "Which metric indicates how quickly a team detects incidents?",
                ["MTTD", "MTBF", "CVE", "RTO"],
                0, "Security Operations", "Medium",
                "MTTD means Mean Time To Detect."
            ),
            q(
                "What is tokenization in data protection?",
                ["Replacing sensitive data with non-sensitive tokens", "Compressing encrypted files", "Hashing network packets", "Blocking MFA prompts"],
                0, "Data Protection", "Medium",
                "Tokenization substitutes sensitive values with mapped tokens."
            ),
            q(
                "Why is security awareness training repeated regularly?",
                ["Threats and attacker tactics evolve", "To reduce patch frequency", "To disable spam filters", "To avoid access reviews"],
                0, "Governance", "Easy",
                "Regular training keeps users current against evolving social engineering techniques."
            )
        ]

    def start_quiz(self, category="all", count=10, shuffle=True):
        import random
        questions = self.questions_bank.copy()
        if shuffle:
            random.shuffle(questions)
        selected = questions[:count]
        quiz_id = str(uuid.uuid4())
        self.active_quizzes[quiz_id] = selected
        return {
            "quiz_id": quiz_id,
            "total_questions": len(selected),
            "pass_threshold": 70,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "explanation": q.explanation
                } for q in selected
            ]
        }

    def get_detailed_results(self, quiz_id, answers):
        questions = self.active_quizzes.get(quiz_id, [])
        correct = 0
        details = []
        for idx, q in enumerate(questions):
            user_ans = self._get_user_answer(answers, q, idx)
            is_correct, correct_answer_index = self._is_correct_answer(q, user_ans)
            if is_correct:
                correct += 1
            details.append({
                "id": q.id,
                "question": q.question,
                "category": q.category or "General",
                "options": q.options,
                "user_answer": user_ans,
                "correct_answer": correct_answer_index,
                "is_correct": is_correct,
                "explanation": q.explanation
            })
        return {
            "total": len(questions),
            "correct": correct,
            "details": details
        }

    def submit_quiz(self, quiz_id, participant_name, email, answers):
        questions = self.active_quizzes.get(quiz_id, [])
        if not questions:
            return None
        correct = 0
        category_scores = {}
        for idx, q in enumerate(questions):
            user_ans = self._get_user_answer(answers, q, idx)
            is_correct, _ = self._is_correct_answer(q, user_ans)
            if is_correct:
                correct += 1
            # Category breakdown
            cat = q.category or "General"
            if cat not in category_scores:
                category_scores[cat] = {"correct": 0, "total": 0}
            category_scores[cat]["total"] += 1
            if is_correct:
                category_scores[cat]["correct"] += 1
        total = len(questions)
        percentage = (correct / total * 100) if total > 0 else 0
        passed = percentage >= 70
        completion_time = datetime.now().isoformat()
        result = QuizResult(
            quiz_id=quiz_id,
            participant_name=participant_name,
            email=email,
            score=correct,
            total=total,
            percentage=percentage,
            passed=passed,
            completion_time=completion_time,
            answers=answers,
            category_scores=category_scores
        )
        return result

    def _get_user_answer(self, answers, question, idx):
        """
        Support both modern UI payloads keyed by question UUID and older payloads keyed by index.
        """
        if not isinstance(answers, dict):
            return None

        raw = None
        question_id = str(question.id) if question.id is not None else None
        if question_id and question_id in answers:
            raw = answers.get(question_id)
        elif idx in answers:
            raw = answers.get(idx)
        elif str(idx) in answers:
            raw = answers.get(str(idx))

        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return raw

    def _is_correct_answer(self, question, user_ans):
        """
        Returns: (is_correct: bool, correct_answer_index: int)
        Handles correct answers stored either as index or option text.
        """
        if question is None:
            return False, -1

        correct_raw = question.correct_answer
        correct_index = -1

        if isinstance(correct_raw, int):
            correct_index = correct_raw
        else:
            try:
                correct_index = int(correct_raw)
            except (TypeError, ValueError):
                if correct_raw in question.options:
                    correct_index = question.options.index(correct_raw)

        if correct_index < 0 or correct_index >= len(question.options):
            return False, -1

        return user_ans == correct_index, correct_index



class QuizResult:
    def __init__(self, quiz_id=None, participant_name=None, email=None, score=0, total=0, percentage=0.0, passed=False, completion_time=None, answers=None, category_scores=None):
        self.quiz_id = quiz_id
        self.participant_name = participant_name
        self.email = email
        self.score = score
        self.total = total
        self.percentage = percentage
        self.passed = passed
        self.completion_time = completion_time or datetime.now().isoformat()
        self.answers = answers or {}
        self.category_scores = category_scores or {}



class CertificateGenerator:
    def generate(self, result, certificate_id=None):
        """
        Generate a valid PDF certificate bytes payload.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        title = "CERTIFICATE OF COMPLETION"
        name = result.participant_name or "Participant"
        cert_id = certificate_id or f"DWM-CERT-{datetime.now().strftime('%Y')}-LOCAL"
        pct = int(result.percentage or 0)
        status = "PASSED" if result.passed else "NOT PASSED"

        c.setTitle(f"Cybersecurity Certificate - {cert_id}")
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 110, title)

        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2, height - 155, "This is to certify that")

        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(width / 2, height - 205, name)

        c.setFont("Helvetica", 13)
        c.drawCentredString(
            width / 2,
            height - 245,
            "has successfully completed the Cybersecurity Awareness Quiz"
        )

        c.setFont("Helvetica", 12)
        c.drawCentredString(
            width / 2,
            height - 285,
            f"Score: {result.score}/{result.total} ({pct}%)   |   Status: {status}"
        )

        c.setFont("Helvetica", 11)
        c.drawCentredString(
            width / 2,
            height - 315,
            f"Certificate ID: {cert_id}"
        )
        c.drawCentredString(
            width / 2,
            height - 335,
            f"Issued: {result.completion_time}"
        )

        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(
            width / 2,
            80,
            "Dark Web Monitor Security Lab"
        )

        c.showPage()
        c.save()
        return buffer.getvalue()
