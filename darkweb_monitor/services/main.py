"""
Dark Web Leak Monitor
A powerful security tool with password checking, email breach detection,
password generation, batch processing, and multiple export formats.
"""

import sys
import os
import getpass
from typing import Optional

from .breach_checker import BreachChecker
from .risk_analyzer import RiskAnalyzer
from .report_generator import ReportGenerator
from .email_checker import EmailChecker
from .password_generator import PasswordGenerator, PasswordConfig
from .batch_checker import BatchChecker
from .export_manager import ExportManager


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Display application banner."""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║            🔒 DARK WEB LEAK MONITOR v2.0 🔒                       ║
║                                                                    ║
║     Advanced Security Analysis & Breach Detection Platform         ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Display main menu options."""
    menu = """
┌────────────────────────────────────────────────────────────────────┐
│                         MAIN MENU                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   [1] 🔍 Check Password            - Check single password breach  │
│   [2] 📧 Check Email               - Check email breach status     │
│   [3] 🔐 Generate Password         - Create secure passwords       │
│   [4] 📁 Batch Check Passwords     - Check multiple passwords      │
│   [5] 📂 Batch Check Emails        - Check multiple emails         │
│   [6] 📊 Export Last Results       - Export to JSON/CSV/HTML       │
│   [7] ⚙️  Settings                  - Configure options             │
│   [0] 🚪 Exit                      - Close application             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
    """
    print(menu)


class DarkWebMonitor:
    """Main application class with interactive menu."""
    
    def __init__(self):
        self.breach_checker = BreachChecker()
        self.risk_analyzer = RiskAnalyzer()
        self.report_generator = ReportGenerator()
        self.email_checker = EmailChecker()
        self.password_generator = PasswordGenerator()
        self.batch_checker = BatchChecker()
        self.export_manager = ExportManager()
        self.last_results = None
    
    def print_result(self, breach_result, risk_assessment, password_strength):
        """Display results in a formatted way."""
        print("\n" + "=" * 60)
        print("📊 SCAN RESULTS")
        print("=" * 60)
        
        risk_icons = {
            'SAFE': '🟢', 'LOW': '🟡', 'MEDIUM': '🟠',
            'HIGH': '🔴', 'CRITICAL': '💀'
        }
        risk_icon = risk_icons.get(risk_assessment.level.value, '❓')
        
        print(f"\n{risk_icon} Risk Level: {risk_assessment.level.value}")
        print(f"📈 Risk Score: {risk_assessment.score}/100")
        print(f"🔍 Breach Count: {breach_result.breach_count:,}")
        print(f"🌐 API Status: {breach_result.api_status}")
        
        print("\n📝 Password Strength:")
        checks = [
            ("Length", f"{password_strength['length']} chars", password_strength['length'] >= 12),
            ("Uppercase", "Yes" if password_strength['has_upper'] else "No", password_strength['has_upper']),
            ("Lowercase", "Yes" if password_strength['has_lower'] else "No", password_strength['has_lower']),
            ("Numbers", "Yes" if password_strength['has_digit'] else "No", password_strength['has_digit']),
            ("Special", "Yes" if password_strength['has_special'] else "No", password_strength['has_special']),
        ]
        
        for name, value, is_good in checks:
            icon = "✅" if is_good else "❌"
            print(f"   {icon} {name}: {value}")
        
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(risk_assessment.recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 60)
    
    def check_password(self):
        """Check a single password for breaches."""
        print("\n" + "=" * 60)
        print("🔍 PASSWORD BREACH CHECK")
        print("=" * 60)
        
        print("\n🔐 Enter password to check (input hidden for security):")
        try:
            password = getpass.getpass(prompt="   Password: ")
        except Exception:
            password = input("   Password: ")
        
        if not password:
            print("❌ Error: Password cannot be empty")
            return
        
        if len(password) < 4:
            print("❌ Error: Password too short for meaningful analysis")
            return
        
        print("\n⏳ Checking password against breach databases...")
        
        breach_result = self.breach_checker.check(password)
        password_strength = self.breach_checker.check_password_strength(password)
        risk_assessment = self.risk_analyzer.analyze(breach_result.breach_count, password_strength)
        
        self.print_result(breach_result, risk_assessment, password_strength)
        
        # Store results
        self.last_results = {
            'type': 'password_check',
            'breach_count': breach_result.breach_count,
            'risk_level': risk_assessment.level.value,
            'risk_score': risk_assessment.score,
            'password_strength': password_strength,
            'recommendations': risk_assessment.recommendations,
            'api_status': breach_result.api_status
        }
        
        # Ask about report generation
        print("\n📄 Generate reports?")
        print("   [1] PDF only")
        print("   [2] All formats (PDF, JSON, CSV, HTML)")
        print("   [3] Skip")
        
        choice = input("\n   Select option: ").strip()
        
        if choice == '1':
            filepath = self.report_generator.generate(
                password=password,
                breach_count=breach_result.breach_count,
                risk=risk_assessment.level.value,
                recommendations=risk_assessment.recommendations
            )
            print(f"✅ PDF Report saved: {filepath}")
        elif choice == '2':
            # PDF
            pdf_path = self.report_generator.generate(
                password=password,
                breach_count=breach_result.breach_count,
                risk=risk_assessment.level.value,
                recommendations=risk_assessment.recommendations
            )
            print(f"✅ PDF: {pdf_path}")
            
            # Other formats
            exports = self.export_manager.export_all(self.last_results, "password_check")
            for fmt, path in exports.items():
                print(f"✅ {fmt.upper()}: {path}")
    
    def check_email(self):
        """Check an email for breaches."""
        print("\n" + "=" * 60)
        print("📧 EMAIL BREACH CHECK")
        print("=" * 60)
        
        email = input("\n   Enter email address: ").strip()
        
        if not email or '@' not in email:
            print("❌ Error: Invalid email address")
            return
        
        print("\n⏳ Checking email against breach databases...")
        print("   (Note: Using simulated data - get API key for real results)")
        
        result = self.email_checker.check_breaches(email)
        
        print("\n" + "=" * 60)
        print("📊 EMAIL BREACH RESULTS")
        print("=" * 60)
        
        status_icon = "🔴" if result.is_compromised else "🟢"
        status_text = "COMPROMISED" if result.is_compromised else "SECURE"
        
        print(f"\n{status_icon} Status: {status_text}")
        print(f"📧 Email: {result.email}")
        print(f"🔍 Breaches Found: {result.breach_count}")
        print(f"🌐 API Status: {result.api_status}")
        
        if result.breaches:
            print("\n📋 Breach Details:")
            for i, breach in enumerate(result.breaches, 1):
                print(f"\n   {i}. {breach.name}")
                print(f"      Domain: {breach.domain}")
                print(f"      Date: {breach.breach_date}")
                print(f"      Accounts Affected: {breach.pwn_count:,}")
                print(f"      Data Exposed: {', '.join(breach.data_classes[:3])}")
        
        print("\n" + "=" * 60)
        
        # Store results
        self.last_results = {
            'type': 'email_check',
            'email': result.email,
            'is_compromised': result.is_compromised,
            'breach_count': result.breach_count,
            'breaches': [
                {
                    'name': b.name,
                    'domain': b.domain,
                    'date': b.breach_date,
                    'pwn_count': b.pwn_count,
                    'data_classes': b.data_classes
                }
                for b in result.breaches
            ],
            'api_status': result.api_status
        }
    
    def generate_password(self):
        """Generate secure passwords."""
        print("\n" + "=" * 60)
        print("🔐 SECURE PASSWORD GENERATOR")
        print("=" * 60)
        
        print("\n   Select generation type:")
        print("   [1] Random Password (recommended)")
        print("   [2] Memorable Passphrase")
        print("   [3] Numeric PIN")
        print("   [4] Multiple Passwords")
        
        choice = input("\n   Select option: ").strip()
        
        if choice == '1':
            length = input("   Password length (default 16): ").strip()
            length = int(length) if length.isdigit() else 16
            
            config = PasswordConfig(length=max(8, min(128, length)))
            generator = PasswordGenerator(config)
            result = generator.generate()
            
            print("\n" + "-" * 50)
            print(f"🔐 Generated Password: {result.password}")
            print("-" * 50)
            print(f"   Length: {result.length}")
            print(f"   Entropy: {result.entropy} bits")
            print(f"   Strength: {result.strength.value}")
            
        elif choice == '2':
            words = input("   Number of words (default 4): ").strip()
            words = int(words) if words.isdigit() else 4
            
            result = self.password_generator.generate_memorable(num_words=max(2, min(8, words)))
            
            print("\n" + "-" * 50)
            print(f"🔐 Generated Passphrase: {result.password}")
            print("-" * 50)
            print(f"   Entropy: {result.entropy} bits")
            print(f"   Strength: {result.strength.value}")
            print(f"   Easy to remember: Yes")
            
        elif choice == '3':
            length = input("   PIN length (default 6): ").strip()
            length = int(length) if length.isdigit() else 6
            
            result = self.password_generator.generate_pin(length=max(4, min(12, length)))
            
            print("\n" + "-" * 50)
            print(f"🔢 Generated PIN: {result.password}")
            print("-" * 50)
            
        elif choice == '4':
            count = input("   How many passwords (default 5): ").strip()
            count = int(count) if count.isdigit() else 5
            
            results = self.password_generator.generate_multiple(count=max(1, min(20, count)))
            
            print("\n" + "-" * 50)
            print("🔐 Generated Passwords:")
            print("-" * 50)
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.password} ({result.strength.value})")
        else:
            print("❌ Invalid option")
            return
        
        print("\n✅ Password(s) generated successfully!")
    
    def batch_check_passwords(self):
        """Check multiple passwords from file or input."""
        print("\n" + "=" * 60)
        print("📁 BATCH PASSWORD CHECK")
        print("=" * 60)
        
        print("\n   Input method:")
        print("   [1] Enter passwords manually (one per line)")
        print("   [2] Load from file")
        
        choice = input("\n   Select option: ").strip()
        
        passwords = []
        
        if choice == '1':
            print("\n   Enter passwords (one per line, empty line to finish):")
            while True:
                pwd = input("   > ").strip()
                if not pwd:
                    break
                passwords.append(pwd)
        elif choice == '2':
            filepath = input("\n   Enter file path: ").strip()
            try:
                passwords = self.batch_checker._read_file(filepath)
                print(f"   ✅ Loaded {len(passwords)} passwords from file")
            except FileNotFoundError:
                print("   ❌ File not found")
                return
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
                return
        else:
            print("❌ Invalid option")
            return
        
        if not passwords:
            print("❌ No passwords to check")
            return
        
        print(f"\n⏳ Checking {len(passwords)} passwords...")
        
        def progress_callback(current, total, result):
            status = "⚠️" if result.get('is_compromised') else "✅"
            print(f"   [{current}/{total}] {result.get('password_masked', '****')} {status}")
        
        batch_result = self.batch_checker.check_passwords(passwords, callback=progress_callback)
        
        print("\n" + "=" * 60)
        print("📊 BATCH RESULTS SUMMARY")
        print("=" * 60)
        print(f"\n   Total Checked: {batch_result.total_items}")
        print(f"   Compromised: {batch_result.compromised_count} ({batch_result.compromise_rate:.1f}%)")
        print(f"   Safe: {batch_result.safe_count}")
        print(f"   Errors: {batch_result.error_count}")
        print(f"   Processing Time: {batch_result.processing_time}s")
        
        # Store results
        self.last_results = {
            'type': 'batch_password_check',
            'total_items': batch_result.total_items,
            'compromised_count': batch_result.compromised_count,
            'safe_count': batch_result.safe_count,
            'compromise_rate': batch_result.compromise_rate,
            'results': batch_result.results,
            'processing_time': batch_result.processing_time
        }
        
        print("\n" + "=" * 60)
    
    def batch_check_emails(self):
        """Check multiple emails from file or input."""
        print("\n" + "=" * 60)
        print("📂 BATCH EMAIL CHECK")
        print("=" * 60)
        
        print("\n   Input method:")
        print("   [1] Enter emails manually (one per line)")
        print("   [2] Load from file")
        
        choice = input("\n   Select option: ").strip()
        
        emails = []
        
        if choice == '1':
            print("\n   Enter emails (one per line, empty line to finish):")
            while True:
                email = input("   > ").strip()
                if not email:
                    break
                emails.append(email)
        elif choice == '2':
            filepath = input("\n   Enter file path: ").strip()
            try:
                emails = self.batch_checker._read_file(filepath)
                print(f"   ✅ Loaded {len(emails)} emails from file")
            except FileNotFoundError:
                print("   ❌ File not found")
                return
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
                return
        else:
            print("❌ Invalid option")
            return
        
        if not emails:
            print("❌ No emails to check")
            return
        
        print(f"\n⏳ Checking {len(emails)} emails...")
        print("   (Note: Using simulated data - get API key for real results)")
        
        def progress_callback(current, total, result):
            status = "⚠️" if result.get('is_compromised') else "✅"
            print(f"   [{current}/{total}] {result.get('email', 'N/A')} {status}")
        
        batch_result = self.batch_checker.check_emails(emails, callback=progress_callback)
        
        print("\n" + "=" * 60)
        print("📊 BATCH RESULTS SUMMARY")
        print("=" * 60)
        print(f"\n   Total Checked: {batch_result.total_items}")
        print(f"   Compromised: {batch_result.compromised_count} ({batch_result.compromise_rate:.1f}%)")
        print(f"   Safe: {batch_result.safe_count}")
        print(f"   Processing Time: {batch_result.processing_time}s")
        
        # Store results
        self.last_results = {
            'type': 'batch_email_check',
            'total_items': batch_result.total_items,
            'compromised_count': batch_result.compromised_count,
            'safe_count': batch_result.safe_count,
            'compromise_rate': batch_result.compromise_rate,
            'results': batch_result.results,
            'processing_time': batch_result.processing_time
        }
        
        print("\n" + "=" * 60)
    
    def export_results(self):
        """Export last results to various formats."""
        print("\n" + "=" * 60)
        print("📊 EXPORT RESULTS")
        print("=" * 60)
        
        if not self.last_results:
            print("\n❌ No results to export. Run a check first.")
            return
        
        print(f"\n   Last check type: {self.last_results.get('type', 'unknown')}")
        print("\n   Export format:")
        print("   [1] JSON")
        print("   [2] CSV")
        print("   [3] HTML")
        print("   [4] Text")
        print("   [5] All formats")
        
        choice = input("\n   Select option: ").strip()
        
        format_map = {
            '1': ('json', self.export_manager.export_json),
            '2': ('csv', lambda d, f: self.export_manager.export_csv([d], f)),
            '3': ('html', self.export_manager.export_html),
            '4': ('txt', self.export_manager.export_txt),
        }
        
        if choice == '5':
            exports = self.export_manager.export_all(self.last_results, "security_report")
            print("\n✅ Exported to all formats:")
            for fmt, path in exports.items():
                print(f"   {fmt.upper()}: {path}")
        elif choice in format_map:
            fmt, export_func = format_map[choice]
            path = export_func(self.last_results, "security_report")
            print(f"\n✅ Exported to {fmt.upper()}: {path}")
        else:
            print("❌ Invalid option")
    
    def settings(self):
        """Configure application settings."""
        print("\n" + "=" * 60)
        print("⚙️ SETTINGS")
        print("=" * 60)
        
        print("\n   [1] View current configuration")
        print("   [2] Set HIBP API Key (for email checks)")
        print("   [3] Change export directory")
        print("   [4] Back to main menu")
        
        choice = input("\n   Select option: ").strip()
        
        if choice == '1':
            print("\n   Current Configuration:")
            print(f"   - Export Directory: {self.export_manager.config.output_dir}")
            print(f"   - Rate Limit Delay: {self.batch_checker.rate_limit_delay}s")
            print(f"   - HIBP API Key: {'Set' if self.email_checker.api_key else 'Not Set'}")
        elif choice == '2':
            api_key = input("\n   Enter HIBP API Key: ").strip()
            if api_key:
                self.email_checker = EmailChecker(api_key=api_key)
                print("   ✅ API Key set successfully")
            else:
                print("   ❌ Invalid API key")
        elif choice == '3':
            new_dir = input("\n   Enter new export directory: ").strip()
            if new_dir:
                self.export_manager.config.output_dir = new_dir
                self.export_manager._ensure_output_dir()
                print(f"   ✅ Export directory set to: {new_dir}")
    
    def run_interactive(self):
        """Run the interactive menu loop."""
        while True:
            clear_screen()
            print_banner()
            print_menu()
            
            choice = input("   Enter your choice: ").strip()
            
            if choice == '1':
                self.check_password()
            elif choice == '2':
                self.check_email()
            elif choice == '3':
                self.generate_password()
            elif choice == '4':
                self.batch_check_passwords()
            elif choice == '5':
                self.batch_check_emails()
            elif choice == '6':
                self.export_results()
            elif choice == '7':
                self.settings()
            elif choice == '0':
                print("\n👋 Thank you for using Dark Web Leak Monitor!")
                print("   Stay safe online! 🔒\n")
                break
            else:
                print("\n❌ Invalid option. Please try again.")
            
            input("\n   Press Enter to continue...")
    
    def run(self, password: Optional[str] = None):
        """Run single password check (legacy mode)."""
        print_banner()
        
        if password is None:
            print("🔐 Enter password to check (input hidden for security):")
            try:
                password = getpass.getpass(prompt="   Password: ")
            except Exception:
                password = input("   Password: ")
        
        if not password or len(password) < 4:
            print("❌ Error: Invalid password")
            return
        
        print("\n⏳ Checking password against breach databases...")
        
        breach_result = self.breach_checker.check(password)
        password_strength = self.breach_checker.check_password_strength(password)
        risk_assessment = self.risk_analyzer.analyze(breach_result.breach_count, password_strength)
        
        self.print_result(breach_result, risk_assessment, password_strength)
        
        print("📄 Generating PDF report...")
        filepath = self.report_generator.generate(
            password=password,
            breach_count=breach_result.breach_count,
            risk=risk_assessment.level.value,
            recommendations=risk_assessment.recommendations
        )
        print(f"✅ Report saved: {filepath}")
        
        return risk_assessment


def main():
    """Entry point for the application."""
    try:
        monitor = DarkWebMonitor()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            
            if arg in ['-i', '--interactive', 'menu']:
                # Interactive mode
                monitor.run_interactive()
            elif arg in ['-h', '--help']:
                print("""
Dark Web Leak Monitor v2.0 - Help

Usage:
    python main.py                    Start interactive menu
    python main.py -i                 Start interactive menu
    python main.py <password>         Quick password check
    python main.py -h                 Show this help

Features:
    - Password breach checking
    - Email breach detection
    - Secure password generation
    - Batch checking from files
    - Multiple export formats (PDF, JSON, CSV, HTML)
                """)
            else:
                # Quick password check with argument
                monitor.run(password=arg)
        else:
            # Default: Interactive mode
            monitor.run_interactive()
        
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
