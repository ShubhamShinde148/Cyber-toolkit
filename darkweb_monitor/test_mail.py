
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the project directory to sys.path
sys.path.append('e:/dark moniter/darkweb_monitor')

from services.quiz_engine import QuizResult, CertificateGenerator
import smtplib
from email.message import EmailMessage as EM
from email.utils import formatdate

load_dotenv('e:/dark moniter/darkweb_monitor/.env')

def send_test_email():
    name = "CHETAN PAWAR"
    user_email = "shubhamshin148@gmail.com" # Using the user's configured feedback email for test
    cert_id = "TEST-CERT-2026-0001"
    pct = 100
    score = 10
    total = 10
    passed = True
    status_text = 'PASSED'
    status_color = '#00ff88'
    comp_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    verify_url = f"http://localhost:5000/verify/{cert_id}"
    cert_url = f"http://localhost:5000/certificate/{cert_id}"

    # Photo 1 Style Email Body
    html_body = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; font-family:'Helvetica Neue', Helvetica, Arial, sans-serif; background:#050a0f;">
<table width="100%" cellspacing="0" cellpadding="0" style="background:#050a0f; padding:50px 0;">
<tr><td align="center">
    <table width="680" cellspacing="0" cellpadding="0" style="background:#08111a; border:1px solid #00ffc6; border-radius:4px; position:relative; table-layout:fixed;">
        <tr><td style="padding:2px; position:relative;">
            <table width="100%" cellspacing="0" cellpadding="0" style="background:#080f19;">
                <tr><td style="padding:30px 40px 10px;">
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td>
                                <div style="font-size:18px; font-weight:bold; color:#00ffc6; letter-spacing:2px; display:inline-block; vertical-align:middle;">🛡️ DARK WEB MONITOR</div>
                                <div style="font-size:10px; color:#888; letter-spacing:1px; text-transform:uppercase; margin-top:2px;">Security Lab</div>
                            </td>
                            <td align="right">
                                <div style="font-size:9px; color:#ffd700; letter-spacing:2px; text-transform:uppercase; font-weight:bold;">CYBERSECURITY AWARENESS PROGRAM</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>
                <tr><td align="center" style="padding:20px 40px 40px;">
                    <div style="margin:0 auto 20px; width:45px; height:45px; border:2.5px solid #00ffc6; border-radius:50%; color:#00ffc6; line-height:42px; font-size:9px; font-weight:bold; text-align:center; background:rgba(0,255,198,0.05);">AWARD</div>
                    <h1 style="color:#ffffff; font-size:32px; font-weight:900; margin:0 0 15px; letter-spacing:6px; text-shadow:0 0 15px rgba(255,255,255,0.2);">CERTIFICATE OF COMPLETION</h1>
                    <div style="width:200px; height:2px; background:#00ffc6; margin:0 auto 30px; border-radius:1px;"></div>
                    <p style="color:#666; font-size:12px; margin:0 0 10px; text-transform:uppercase; letter-spacing:3px;">This is to certify that</p>
                    <h2 style="color:#ffd700; font-size:48px; font-weight:800; margin:0 0 5px; letter-spacing:3px; text-shadow:0 0 10px rgba(255,215,0,0.3);">{name}</h2>
                    <div style="width:300px; height:2px; background:linear-gradient(90deg, transparent, #ffd700, transparent); margin:0 auto 30px;"></div>
                    <p style="color:#888; font-size:16px; line-height:1.7; margin:0 0 40px; max-width:540px;">
                        has successfully completed the <strong style="color:#00ffc6;">Cybersecurity Awareness Quiz</strong> demonstrating proficiency in cybersecurity fundamentals, threat awareness, and security best practices.
                    </p>
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td align="center" width="50%">
                                <div style="width:90px; height:90px; border:4px solid #00ffc6; border-radius:50%; line-height:82px; display:inline-block; text-align:center; box-shadow:0 0 15px rgba(0,255,198,0.2);">
                                    <span style="color:#ffffff; font-size:22px; font-weight:bold;">{pct}%</span>
                                </div>
                                <div style="margin-top:10px; color:#888; font-size:11px; letter-spacing:1px;">SCORE: {score}/{total}</div>
                            </td>
                            <td align="center" width="50%">
                                <div style="width:50px; height:50px; border:2.5px solid {status_color}; border-radius:50%; line-height:45px; display:inline-block; text-align:center; color:{status_color};">
                                    <span style="font-size:24px;">{'✓' if passed else '✕'}</span>
                                </div>
                                <div style="margin-top:10px; color:{status_color}; font-size:14px; font-weight:bolder; letter-spacing:1px;">{status_text}</div>
                                <div style="color:#888; font-size:10px; letter-spacing:1px;">STATUS</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>
                <tr><td style="padding:25px 40px; background:rgba(255,255,255,0.015); border-top:1px solid rgba(0,255,198,0.15); border-bottom:1px solid rgba(0,255,198,0.05);">
                    <table width="100%" cellspacing="0" cellpadding="0">
                        <tr>
                            <td width="33%" style="font-size:11px; color:#555; vertical-align:middle;">
                                <div style="margin-bottom:4px;">CERT ID: <span style="font-family:monospace; color:#888;">{cert_id}</span></div>
                                <div>ISSUED: <span style="color:#888;">{comp_time}</span></div>
                            </td>
                            <td width="34%" align="center" style="vertical-align:middle;">
                                <div style="background:#fff; padding:6px; display:inline-block; border-radius:2px;">
                                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=60x60&data={verify_url}" width="60" height="60" alt="QR" style="display:block;">
                                </div>
                                <div style="margin-top:5px; font-size:8px; color:#444; letter-spacing:1px;">SCAN TO VERIFY</div>
                            </td>
                            <td width="33%" align="right" style="vertical-align:bottom; padding-bottom:5px;">
                                <div style="font-size:13px; font-weight:bold; color:#fff; border-bottom:2px solid #00ffc6; padding-bottom:3px; display:inline-block;">Verified by Dark Web Monitor</div>
                            </td>
                        </tr>
                    </table>
                </td></tr>
                <tr><td style="padding:30px; text-align:center; background:#050a0f;">
                     <a href="{cert_url}" style="display:inline-block; padding:12px 30px; background:transparent; color:#00ffc6; border:1px solid #00ffc6; text-decoration:none; border-radius:3px; font-weight:bold; font-size:13px; letter-spacing:2px; text-transform:uppercase; transition:all 0.3s;">VALIDATE SECURE ACCESS</a>
                     <p style="margin:25px 0 0; color:#333; font-size:10px; letter-spacing:0.5px;">&copy; 2026 Dark Web Monitor Security Lab. All rights reserved.</p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</td></tr></table>
</body></html>'''

    # Generate PDF for attachment
    mock_result = QuizResult(
        quiz_id=cert_id,
        participant_name=name,
        email=user_email,
        score=score,
        total=total,
        percentage=pct,
        passed=passed,
        completion_time=comp_time,
        answers={},
        category_scores={}
    )
    
    pdf_gen = CertificateGenerator()
    pdf_bytes = pdf_gen.generate(mock_result, certificate_id=cert_id)

    sender_email = os.getenv('FEEDBACK_EMAIL_ADDRESS')
    sender_password = os.getenv('FEEDBACK_EMAIL_PASSWORD')

    msg = EM()
    msg['Subject'] = f'Official Cybersecurity Certificate [TEST] - {cert_id}'
    msg['From'] = f'Dark Web Monitor <{sender_email}>'
    msg['To'] = user_email
    msg['Date'] = formatdate(localtime=True)

    msg.set_content(f'Dear {name},\n\nCongratulations! You have successfully completed the Cybersecurity Awareness Quiz. Please find your official certificate attached as a PDF.\n\nCertificate ID: {cert_id}\nScore: {pct}%\n\nYou can also verify your certificate online at: {cert_url}')
    msg.add_alternative(html_body, subtype='html')
    
    msg.add_attachment(
        pdf_bytes,
        maintype='application',
        subtype='pdf',
        filename=f'DarkWebMonitor_Certificate_{cert_id}.pdf'
    )

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    
    print(f"Test email sent successfully to {user_email}")

if __name__ == "__main__":
    send_test_email()
