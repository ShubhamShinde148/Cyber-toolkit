"""
Dark Web Leak Monitor - CyberGuard AI Chatbot
Advanced AI-powered cybersecurity assistant.
"""

import os
import re
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from openai import OpenAI


# ==================== CyberGuard AI Knowledge Engine ====================

KNOWLEDGE_BASE = {
    "password_breach": {
        "keywords": ["password breach", "password leak", "password compromised", "check password", "password hack", "password stolen", "pwned password", "password exposed", "haveibeenpwned", "have i been pwned"],
        "response": """**🔐 Password Breach Checking**

A password breach happens when your password is exposed in a data leak. Here's what you should know:

**How to Check:**
1. Go to the **Password Check** page on this platform
2. Enter your password — it will be securely hashed (SHA-1) before checking
3. We use the HaveIBeenPwned API to check if your password hash appears in known breaches
4. Your actual password is **never sent** over the network

**If Your Password Was Breached:**
- Change it immediately on **all** sites where you used it
- Use a unique password for every account
- Enable two-factor authentication (2FA)
- Consider using a password manager

**How It Works Technically:**
- Your password is hashed using SHA-1
- Only the first 5 characters of the hash are sent to the API (k-anonymity)
- The API returns all matching hashes, and we check locally
- This means your password remains private even during the check"""
    },

    "email_breach": {
        "keywords": ["email breach", "email leak", "email compromised", "check email", "email hack", "email stolen", "email exposed", "email pwned", "email data", "my email"],
        "response": """**📧 Email Breach Detection**

Email breaches occur when your email address appears in leaked databases. Here's what you need to know:

**How to Check:**
1. Go to the **Email Check** page on this platform
2. Enter your email address
3. We'll check multiple breach databases to see if your email was exposed

**If Your Email Was Found in a Breach:**
- Change the password for that email account immediately
- Change passwords on all accounts using that email
- Enable 2FA on your email account (this is critical!)
- Watch for phishing emails pretending to be from breached services
- Check what data was exposed (passwords, personal info, financial data)

**Prevention Tips:**
- Use email aliases for different services
- Don't use your primary email for sketchy websites
- Enable login notifications on your email provider
- Regularly check for breaches at haveibeenpwned.com"""
    },

    "strong_password": {
        "keywords": ["strong password", "create password", "good password", "password tips", "password generator", "generate password", "password strength", "secure password", "password best practice", "how to make password"],
        "response": """**🔒 Creating Strong Passwords**

A strong password is your first line of defense. Here are the best practices:

**Requirements for a Strong Password:**
- At least **12-16 characters** long (longer is better)
- Mix of **uppercase**, **lowercase**, **numbers**, and **symbols**
- **No dictionary words** or common phrases
- **No personal info** (birthdays, names, pet names)
- **Unique** for every single account

**Good Password Examples (patterns, not actual passwords):**
- `Tr0ub4dor&3$kY!` — Mixed characters with symbols
- Use a **passphrase**: `correct-horse-battery-staple-42!`
- Random: Use our **Password Generator** tool!

**Pro Tips:**
- Use a **password manager** (Bitwarden, KeePass, 1Password)
- Never reuse passwords across sites
- Change passwords if a service reports a breach
- The longer the password, the exponentially harder it is to crack"""
    },

    "two_factor": {
        "keywords": ["two factor", "2fa", "two-factor", "mfa", "multi factor", "authenticator", "authentication app", "google authenticator", "authy", "totp", "otp"],
        "response": """**🔑 Two-Factor Authentication (2FA)**

2FA adds a second layer of security beyond your password. Even if your password is stolen, attackers can't access your account without the second factor.

**Types of 2FA:**
1. **Authenticator Apps** (Best) — Google Authenticator, Authy, Microsoft Authenticator
2. **Hardware Keys** (Most Secure) — YubiKey, Google Titan
3. **SMS Codes** (Least Secure) — Vulnerable to SIM swapping
4. **Email Codes** — Better than nothing, but email can be compromised

**How It Works:**
1. You enter your password (something you know)
2. You provide a second factor (something you have)
3. Only with both factors can you log in

**Recommended Setup:**
- Enable 2FA on ALL important accounts (email, banking, social media)
- Use an **authenticator app** over SMS when possible
- Save **backup codes** in a secure location
- Consider a hardware security key for critical accounts

**Where to Enable 2FA:**
- Gmail/Google: google.com/2step
- Microsoft: account.microsoft.com/security
- GitHub, Discord, Twitter/X, Instagram — all support 2FA"""
    },

    "osint": {
        "keywords": ["osint", "open source intelligence", "osint tool", "reconnaissance", "recon", "information gathering", "footprint", "digital footprint", "username search", "username osint", "domain scan"],
        "response": """**🔍 OSINT (Open Source Intelligence)**

OSINT is the practice of collecting and analyzing publicly available information. Our platform provides several OSINT tools:

**Available OSINT Techniques:**
1. **Username Search** — Search for a username across 100+ platforms to see where accounts exist
2. **Domain Analysis** — Analyze a domain's security configuration (DNS, SSL, headers)
3. **IP Intelligence** — Get geolocation, ISP info, and threat data for any IP
4. **Metadata Extraction** — Extract hidden metadata from images, PDFs, and documents

**Legitimate Uses of OSINT:**
- Checking your own digital footprint
- Security assessments and penetration testing (with authorization)
- Investigating phishing or scam sources
- Verifying the security of services you use

**Reduce Your Digital Footprint:**
- Google yourself regularly
- Remove unused accounts
- Check privacy settings on social media
- Use OSINT tools like Sherlock to find accounts you forgot about
- Use different usernames across platforms

⚠️ **Important:** OSINT tools should only be used ethically and legally. Never use them to stalk, harass, or compromise others."""
    },

    "vpn_privacy": {
        "keywords": ["vpn", "privacy", "anonymous", "anonymity", "tor", "proxy", "hide ip", "private browsing", "incognito", "tracking", "online privacy"],
        "response": """**🛡️ VPN & Online Privacy**

Protecting your privacy online is essential in today's digital world.

**VPN (Virtual Private Network):**
- Encrypts your internet traffic
- Hides your real IP address
- Protects you on public WiFi
- Recommended: NordVPN, ProtonVPN, Mullvad

**Browser Privacy:**
- Use **Firefox** or **Brave** for better privacy
- Install **uBlock Origin** for ad/tracker blocking
- Use **HTTPS Everywhere**
- Clear cookies regularly
- Incognito mode ≠ anonymous (it only clears local history)

**Advanced Privacy:**
- **Tor Browser** for maximum anonymity
- Use **encrypted email** (ProtonMail, Tutanota)
- Use **encrypted messaging** (Signal, Wire)
- Disable location services when not needed
- Review app permissions on your phone

**DNS Privacy:**
- Use encrypted DNS: Cloudflare (1.1.1.1) or Quad9 (9.9.9.9)
- Enable DNS over HTTPS (DoH) in your browser"""
    },

    "phishing": {
        "keywords": ["phishing", "scam", "fake email", "suspicious email", "social engineering", "fake website", "spoofing", "fraud", "suspicious link"],
        "response": """**🎣 Phishing & Social Engineering**

Phishing is one of the most common cyber attacks. Here's how to protect yourself:

**How to Identify Phishing:**
- Check the sender's email address carefully (look for misspellings)
- Hover over links before clicking — does the URL match?
- Watch for urgency: "Act now!" "Your account will be closed!"
- Look for grammar/spelling mistakes
- Be suspicious of unexpected attachments

**What to Do:**
- **Don't click** suspicious links
- **Don't download** unexpected attachments
- **Verify** by contacting the company directly (not through the email)
- **Report** phishing to your email provider
- **Check URLs** using our Cyber Tools

**Common Phishing Types:**
1. Email phishing (most common)
2. Spear phishing (targeted at specific people)
3. Smishing (SMS/text phishing)
4. Vishing (voice/phone phishing)
5. Whaling (targeting executives)"""
    },

    "data_breach_response": {
        "keywords": ["what to do", "data breach", "been hacked", "hacked", "account compromised", "someone accessed", "breach response", "after breach", "after hack"],
        "response": """**🚨 What To Do After a Data Breach**

If you suspect your data has been breached, follow these steps immediately:

**Immediate Actions:**
1. **Change your password** on the affected account
2. **Change passwords** on any other account using the same password
3. **Enable 2FA** on all important accounts
4. **Check email** for unauthorized password reset requests

**Monitor & Protect:**
5. Monitor your bank/credit card statements
6. Check for unauthorized logins on your accounts
7. Set up **login alerts** where available
8. Consider a **credit freeze** if financial data was exposed

**Long-Term Steps:**
9. Use a **password manager** going forward
10. Use **unique passwords** for every site
11. Regularly check for breaches using our tools
12. Enable **2FA** everywhere possible

**Useful Resources:**
- Check haveibeenpwned.com for breach lookups
- Use a password manager to generate and store unique passwords
- Enable 2FA everywhere possible"""
    },

    "website_features": {
        "keywords": ["website feature", "how to use", "this website", "this platform", "this tool", "what can", "features", "help me", "guide", "tutorial", "how does this work"],
        "response": """This platform is a cybersecurity toolkit. Here's a quick overview:

**Security Checks:** Password breach checking, email leak detection, batch checking
**OSINT:** Username search, domain scanning, IP intelligence, metadata extraction
**Cyber Tools:** Hash generator, Base64, URL encoder, JWT decoder, DNS lookup, subdomain finder
**Analysis:** Risk assessment, security advisor, breach timeline
**Learning:** Cybersecurity quiz with certificates

Just use the navigation menu to access any tool. What would you like to do?"""
    },

    "malware": {
        "keywords": ["malware", "virus", "ransomware", "trojan", "worm", "spyware", "adware", "keylogger", "antivirus", "infected"],
        "response": """**🦠 Malware Protection**

Malware is malicious software designed to harm your device or steal your data.

**Common Types:**
- **Ransomware** — Encrypts your files, demands payment
- **Trojans** — Disguised as legitimate software
- **Spyware** — Secretly monitors your activity
- **Keyloggers** — Records your keystrokes
- **Adware** — Shows unwanted advertisements

**Protection Tips:**
1. Keep your OS and software **updated**
2. Use a reputable **antivirus** (Windows Defender is good!)
3. **Don't download** from untrusted sources
4. Be cautious with **email attachments**
5. **Back up** your data regularly (3-2-1 rule)
6. Use **standard user accounts**, not admin, for daily use

**If You're Infected:**
- Disconnect from the internet
- Run a full antivirus scan
- Boot into Safe Mode if needed
- Don't pay ransomware demands
- Restore from a clean backup"""
    },

    "encryption": {
        "keywords": ["encryption", "encrypt", "decrypt", "hashing", "hash", "sha256", "md5", "aes", "rsa", "ssl", "tls", "https", "cryptography", "cipher"],
        "response": """**🔏 Encryption & Hashing**

Understanding encryption is key to cybersecurity.

**Encryption vs Hashing:**
- **Encryption** = reversible (decrypt with a key). Used for: data in transit, stored files
- **Hashing** = one-way (cannot reverse). Used for: passwords, data integrity

**Common Hash Algorithms:**
- **MD5** — Fast but broken, don't use for security
- **SHA-1** — Deprecated, used in HIBP checks
- **SHA-256** — Secure, widely used
- **bcrypt/argon2** — Best for password storage

**Encryption in Practice:**
- **HTTPS/TLS** — Encrypts web traffic (look for 🔒 in browser)
- **AES-256** — Standard for file encryption
- **RSA** — Used for key exchange

**Practical Tools:**
- `openssl` for encryption/hashing on command line
- `hashlib` in Python for generating hashes
- Online JWT debuggers like jwt.io for inspecting tokens"""
    },

    "greeting": {
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "namaste", "howdy", "greetings", "sup"],
        "response": """Hey there! 👋 How can I help you today?"""
    },

    "thanks": {
        "keywords": ["thank", "thanks", "thank you", "thx", "appreciated", "helpful"],
        "response": """You're welcome! 😊 Feel free to ask if you need anything else."""
    },

    "linux": {
        "keywords": ["linux", "ubuntu", "debian", "fedora", "kali linux", "kali", "centos", "arch linux", "mint", "linux distro"],
        "response": """**🐧 Linux**

Linux is a free, open-source operating system kernel created by **Linus Torvalds** in 1991. It powers everything from servers to smartphones.

**Popular Distributions:**
- **Ubuntu** — Beginner-friendly, great for desktops
- **Kali Linux** — Built for penetration testing & cybersecurity
- **Debian** — Stable, used for servers
- **Fedora** — Cutting-edge features, Red Hat backed
- **Arch Linux** — DIY, for advanced users
- **CentOS/Rocky** — Enterprise server use

**Why Linux Matters for Cybersecurity:**
- Most servers run Linux (~96% of top web servers)
- Kali Linux comes with 600+ security tools pre-installed
- Better control over system processes and networking
- Open source = auditable code, fewer hidden backdoors
- Essential skill for penetration testers and security analysts

**Key Commands:**
- `ls` — list files
- `cd` — change directory
- `chmod` — change permissions
- `grep` — search text patterns
- `nmap` — network scanning
- `netstat` — view network connections

**Getting Started:**
You can try Linux in a virtual machine (VirtualBox/VMware) without affecting your current OS."""
    },

    "windows": {
        "keywords": ["windows", "windows 10", "windows 11", "microsoft windows", "windows security", "windows defender"],
        "response": """**🪟 Windows Security**

Windows is the most widely used desktop OS, making it a prime target for cyber attacks.

**Built-in Security Features:**
- **Windows Defender** — Solid built-in antivirus (good enough for most users)
- **Windows Firewall** — Controls inbound/outbound traffic
- **BitLocker** — Full disk encryption
- **Windows Hello** — Biometric authentication
- **SmartScreen** — Blocks malicious downloads

**Hardening Tips:**
1. Keep Windows Update enabled (always patch!)
2. Use a standard user account for daily tasks, not admin
3. Enable BitLocker for full disk encryption
4. Turn on Controlled Folder Access (ransomware protection)
5. Disable Remote Desktop if not needed
6. Review installed apps and remove unused ones

**PowerShell Security:**
- Run `Get-ExecutionPolicy` to check script execution policy
- Use `Set-ExecutionPolicy RemoteSigned` for balanced security
- Monitor PowerShell logs for suspicious activity"""
    },

    "networking": {
        "keywords": ["networking", "network", "tcp", "udp", "ip address", "subnet", "firewall", "router", "switch", "port", "protocol", "osi model", "dns", "dhcp", "nat"],
        "response": """**🌐 Networking Fundamentals**

Understanding networking is essential for cybersecurity.

**OSI Model (7 Layers):**
7. Application (HTTP, FTP, DNS)
6. Presentation (SSL/TLS, encryption)
5. Session (connections management)
4. Transport (TCP, UDP)
3. Network (IP, routing)
2. Data Link (MAC, switches)
1. Physical (cables, signals)

**Key Protocols:**
- **TCP** — Reliable, ordered delivery (web, email)
- **UDP** — Fast, no guarantee (streaming, DNS, gaming)
- **HTTP/HTTPS** — Web traffic (443 = secure, 80 = unencrypted)
- **DNS** — Translates domain names to IP addresses
- **DHCP** — Automatically assigns IP addresses
- **SSH** — Secure remote access (port 22)

**Common Ports:**
- 21: FTP | 22: SSH | 23: Telnet | 25: SMTP
- 53: DNS | 80: HTTP | 443: HTTPS | 3389: RDP

**Useful Commands:**
- `nslookup` / `dig` — DNS queries
- `traceroute` / `tracert` — Trace network path
- `netstat -tulnp` — View active connections
- `nmap` — Network scanning"""
    },

    "dark_web": {
        "keywords": ["dark web", "darkweb", "deep web", "tor network", "onion", "dark net", "darknet", "hidden services"],
        "response": """**🕸️ The Dark Web**

The internet has three layers:

**1. Surface Web (~5%)**
- Indexed by search engines (Google, Bing)
- Regular websites you visit daily

**2. Deep Web (~90%)**
- Not indexed by search engines
- Includes: email inboxes, bank portals, databases, private content
- Perfectly legal and normal

**3. Dark Web (~5%)**
- Requires special software (Tor Browser) to access
- Uses .onion domains
- Contains both legal and illegal content

**Why It Matters for Security:**
- Stolen credentials are sold on dark web marketplaces
- Leaked databases appear on dark web forums
- Our platform helps you check if YOUR data has been leaked
- Monitoring dark web leaks helps you react quickly to breaches

**Stay Protected:**
- Regularly check if your email was in a breach (haveibeenpwned.com)
- Verify your password safety against known breaches
- Enable **2FA** to protect accounts even if passwords leak
- Monitor your digital footprint regularly"""
    },

    "programming": {
        "keywords": ["programming", "coding", "python", "javascript", "java", "c++", "html", "css", "code", "developer", "software", "programming language"],
        "response": """**💻 Programming & Cybersecurity**

Programming is a vital skill for cybersecurity professionals.

**Top Languages for Cybersecurity:**
1. **Python** — #1 choice: scripting, automation, exploit development, tool building
2. **Bash/Shell** — Linux automation and system administration
3. **JavaScript** — Web security, XSS understanding, Node.js tools
4. **C/C++** — Understanding memory vulnerabilities, buffer overflows
5. **SQL** — Database security, SQL injection understanding
6. **PowerShell** — Windows automation and security scripting
7. **Go** — Modern security tools (many offensive tools written in Go)

**Python for Security (Examples):**
- Network scanning with `scapy`
- Web scraping with `requests` + `BeautifulSoup`
- Password cracking with `hashlib`
- API interaction with `requests`
- Automation with `paramiko` (SSH)

**Learning Resources:**
- Python.org for fundamentals
- OverTheWire.org for practice challenges
- HackTheBox for hands-on security labs
- TryHackMe for beginner-friendly learning

Start with Python — it's the most versatile and beginner-friendly language for both general development and security work."""
    },

    "hacking_ethical": {
        "keywords": ["ethical hacking", "penetration testing", "pentest", "bug bounty", "white hat", "red team", "blue team", "ctf", "capture the flag", "security testing", "vulnerability"],
        "response": """**🎯 Ethical Hacking & Penetration Testing**

Ethical hacking is the practice of testing systems for vulnerabilities — with permission.

**Career Paths:**
- **Penetration Tester** — Finds vulnerabilities in systems
- **Red Team** — Simulates real-world attacks
- **Blue Team** — Defends against attacks
- **Bug Bounty Hunter** — Finds bugs for rewards
- **Security Analyst** — Monitors and responds to threats

**Popular Tools:**
- **Nmap** — Network scanning
- **Burp Suite** — Web app testing
- **Metasploit** — Exploitation framework
- **Wireshark** — Network packet analysis
- **John the Ripper** — Password cracking
- **Hashcat** — GPU-accelerated password recovery

**Certifications:**
- **CEH** — Certified Ethical Hacker
- **OSCP** — Offensive Security Certified Professional
- **CompTIA Security+** — Entry-level security cert
- **eJPT** — eLearnSecurity Junior Penetration Tester

**Practice Platforms:**
- HackTheBox, TryHackMe, VulnHub, OverTheWire, PicoCTF

⚠️ **Always get written permission before testing any system you don't own!**"""
    },

    "wifi_security": {
        "keywords": ["wifi", "wi-fi", "wireless", "wifi security", "wifi hack", "wifi password", "wpa", "wep", "wireless security", "hotspot"],
        "response": """**📶 WiFi Security**

Securing your wireless network is crucial for protecting your data.

**WiFi Encryption Standards:**
- **WEP** — 🔴 Broken, never use (crackable in minutes)
- **WPA** — 🟡 Outdated, avoid
- **WPA2** — 🟢 Good, widely supported
- **WPA3** — 🟢 Best, latest standard

**Secure Your Home WiFi:**
1. Use **WPA2 or WPA3** encryption
2. Set a **strong password** (16+ characters)
3. Change the **default admin password** on your router
4. **Disable WPS** (WiFi Protected Setup)
5. Update your router's **firmware** regularly
6. **Hide your SSID** (optional, minor security)
7. Use a **guest network** for visitors and IoT devices

**Public WiFi Safety:**
- Never access banking/sensitive sites on public WiFi
- Always use a **VPN** on public networks
- Verify the network name with staff (avoid evil twin attacks)
- Forget public networks after use
- Use mobile data for sensitive transactions"""
    },

    "social_media": {
        "keywords": ["social media", "facebook", "instagram", "twitter", "tiktok", "snapchat", "linkedin", "social media security", "privacy settings", "account security"],
        "response": """**📱 Social Media Security**

Social media accounts are prime targets for hackers and identity thieves.

**Essential Security Steps:**
1. Enable **2FA** on all social media accounts
2. Use **unique, strong passwords** for each platform
3. Review **privacy settings** regularly
4. Be cautious with **friend/follow requests** from strangers
5. Limit **personal information** in your profile

**Privacy Tips:**
- Disable location tagging on posts
- Review tagged photos before they appear on your profile
- Limit who can see your friends list
- Be careful what you share — it's permanent once posted
- Audit third-party app permissions regularly

**Common Attacks on Social Media:**
- Phishing links in DMs
- Fake giveaway scams
- Account impersonation
- Social engineering via public info
- Session hijacking on public WiFi

You can search for your username across platforms using OSINT tools like Sherlock, Namechk, or WhatsMyName."""
    },

    "cybersecurity_career": {
        "keywords": ["career", "job", "cybersecurity career", "security job", "how to start", "learn cybersecurity", "beginner", "getting started", "roadmap"],
        "response": """**🚀 Cybersecurity Career Roadmap**

Cybersecurity is one of the fastest-growing fields with millions of unfilled positions.

**Beginner Path:**
1. Learn **networking fundamentals** (CompTIA Network+)
2. Learn **Linux** basics
3. Get **CompTIA Security+** certification
4. Practice on **TryHackMe** (beginner-friendly)
5. Build a **home lab** with virtual machines

**Intermediate Path:**
6. Choose a specialization (offensive/defensive/GRC)
7. Get hands-on with **HackTheBox**
8. Learn **Python** scripting for automation
9. Pursue **CEH** or **eJPT** certification
10. Contribute to open-source security projects

**Advanced Path:**
11. Get **OSCP** (gold standard for pentesters)
12. Participate in **bug bounty** programs
13. Attend **security conferences** (DEF CON, Black Hat)
14. Build and share your own security tools

**Salary Ranges (US):**
- Entry Level: $60,000 - $85,000
- Mid Level: $85,000 - $120,000
- Senior: $120,000 - $200,000+
- CISO: $200,000 - $400,000+

The best way to start is by getting hands-on — build a home lab, practice on CTF platforms, and never stop learning."""
    },

    "ip_address": {
        "keywords": ["ip address", "what is ip", "my ip", "ipv4", "ipv6", "ip lookup", "geolocation", "trace ip", "ip location"],
        "response": """**🌍 IP Addresses**

An IP (Internet Protocol) address is a unique identifier for devices on a network.

**Types:**
- **IPv4** — e.g., 192.168.1.1 (4.3 billion addresses, running out)
- **IPv6** — e.g., 2001:0db8::1 (virtually unlimited addresses)
- **Public IP** — Your address on the internet (visible to websites)
- **Private IP** — Your address on local network (192.168.x.x, 10.x.x.x)

**What Can Be Found From an IP:**
- Approximate geolocation (city-level, not exact address)
- ISP (Internet Service Provider)
- Whether it's a VPN/proxy/Tor exit node
- Abuse reports and threat intelligence

**Privacy Considerations:**
- Use a **VPN** to mask your real IP
- Websites log your IP address
- IP alone usually can't identify you personally
- ISPs can link IPs to subscribers (with legal process)

**Useful Commands:**
- `nslookup` — Resolve domain to IP
- `whois` — Look up IP/domain registration info
- `traceroute` — Trace the network path to an IP
- `curl ifconfig.me` — Check your own public IP"""
    },

    "database_security": {
        "keywords": ["database", "sql", "sql injection", "sqli", "nosql", "mongodb", "mysql", "postgresql", "database security"],
        "response": """**🗄️ Database Security**

Databases store the most valuable data — making them prime targets.

**SQL Injection (SQLi):**
The #1 web vulnerability for decades:
- Attacker inserts malicious SQL code through input fields
- Can dump entire databases, bypass logins, modify data
- Prevention: **parameterized queries**, input validation, WAFs

**Database Security Best Practices:**
1. Use **parameterized queries** (never concatenate user input into SQL)
2. Apply **principle of least privilege** for database users
3. **Encrypt** sensitive data at rest and in transit
4. Keep database software **updated**
5. **Backup** regularly and test restoration
6. Use **strong authentication** and limit network access
7. Enable **audit logging**

**Common Database Ports:**
- MySQL: 3306
- PostgreSQL: 5432
- MongoDB: 27017
- MSSQL: 1433
- Redis: 6379"""
    },

    "web_security": {
        "keywords": ["web security", "xss", "cross site", "csrf", "owasp", "web application", "website security", "web vulnerability", "injection"],
        "response": """**🌐 Web Application Security**

Web apps are a major attack surface. The **OWASP Top 10** lists the most critical risks:

**OWASP Top 10 (2021):**
1. **Broken Access Control** — Unauthorized access to resources
2. **Cryptographic Failures** — Weak encryption, exposed data
3. **Injection** — SQL, XSS, command injection
4. **Insecure Design** — Flawed architecture
5. **Security Misconfiguration** — Default settings, open ports
6. **Vulnerable Components** — Outdated libraries
7. **Auth Failures** — Weak login mechanisms
8. **Data Integrity Failures** — Unverified updates
9. **Logging Failures** — No monitoring/alerting
10. **SSRF** — Server-side request forgery

**Key Web Attacks:**
- **XSS** — Injecting scripts into web pages
- **CSRF** — Tricking users into unwanted actions
- **SQLi** — Injecting database queries

Practice on platforms like OWASP WebGoat, DVWA, or PortSwigger Web Security Academy to learn hands-on."""
    },

    "cryptocurrency": {
        "keywords": ["crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain", "wallet", "crypto security", "nft"],
        "response": """**₿ Cryptocurrency Security**

Cryptocurrency introduces unique security challenges.

**Securing Your Crypto:**
1. Use a **hardware wallet** (Ledger, Trezor) for large holdings
2. **Never share** your seed phrase / private keys
3. Enable **2FA** on exchange accounts
4. Use **strong, unique passwords** for each exchange
5. Beware of **phishing sites** mimicking exchanges
6. **Verify addresses** before sending (clipboard malware exists)

**Common Crypto Scams:**
- Fake giveaways ("Send 1 BTC, get 2 back")
- Phishing sites mimicking exchanges
- Pump and dump schemes
- Fake wallet/exchange apps
- Social engineering for seed phrases

**Blockchain Basics:**
- Decentralized, distributed ledger
- Transactions are immutable once confirmed
- Public (Bitcoin, Ethereum) vs Private blockchains
- Smart contracts run on platforms like Ethereum

**Remember:** If someone has your private key or seed phrase, they have ALL your crypto. Never store it digitally unencrypted."""
    },

    "ai_ml": {
        "keywords": ["artificial intelligence", "ai", "machine learning", "ml", "chatgpt", "deep learning", "neural network", "gpt", "llm"],
        "response": """**🤖 AI & Machine Learning in Cybersecurity**

AI is transforming both cyber attacks and defenses.

**AI for Defense:**
- **Threat detection** — AI identifies anomalies in network traffic
- **Malware analysis** — ML classifies new malware variants
- **Phishing detection** — NLP identifies phishing emails
- **User behavior analytics** — Detects compromised accounts
- **Automated incident response** — Speeds up threat handling

**AI-Powered Attacks:**
- **Deepfakes** — Realistic fake audio/video for social engineering
- **AI-generated phishing** — More convincing scam emails
- **Automated vulnerability scanning** — Faster attack discovery
- **Password guessing** — AI-powered pattern prediction
- **Evasion techniques** — AI to bypass security tools

**AI Tools You've Used:**
- This chatbot uses AI to help with your cybersecurity questions!
- Many modern security tools incorporate ML models

**Key Concepts:**
- **LLM** (Large Language Model) — ChatGPT, Claude, etc.
- **NLP** (Natural Language Processing) — Understanding text
- **Neural Networks** — Brain-inspired computing models
- **Deep Learning** — Multi-layered neural networks"""
    },

    "cloud_security": {
        "keywords": ["cloud", "aws", "azure", "gcp", "cloud security", "s3", "cloud computing", "saas", "iaas"],
        "response": """**☁️ Cloud Security**

Cloud computing has become the backbone of modern IT.

**Cloud Service Models:**
- **IaaS** (Infrastructure) — AWS EC2, Azure VMs, Google Compute
- **PaaS** (Platform) — Heroku, AWS Elastic Beanstalk
- **SaaS** (Software) — Gmail, Dropbox, Office 365

**Major Cloud Providers:**
- **AWS** — Amazon Web Services (market leader)
- **Azure** — Microsoft (strong enterprise integration)
- **GCP** — Google Cloud Platform

**Cloud Security Best Practices:**
1. Follow **least privilege** for IAM roles
2. Enable **MFA** for all cloud accounts
3. **Encrypt** data at rest and in transit
4. Monitor with **CloudTrail** / **Azure Monitor** / **Stackdriver**
5. Regularly audit **security groups** and firewall rules
6. Don't expose **S3 buckets** or storage publicly
7. Use **infrastructure as code** (Terraform, CloudFormation)

**Common Cloud Mistakes:**
- Publicly accessible storage buckets
- Overly permissive IAM policies
- Hardcoded credentials in code
- Unencrypted databases
- No logging or monitoring"""
    },

    "mobile_security": {
        "keywords": ["mobile", "android", "ios", "iphone", "phone security", "mobile security", "app security", "smartphone"],
        "response": """**📱 Mobile Device Security**

Your smartphone holds your most sensitive data — emails, banking, photos, locations.

**Essential Mobile Security:**
1. Keep your OS and apps **updated**
2. Only install apps from **official stores** (App Store / Play Store)
3. Review **app permissions** (does a flashlight app need your contacts?)
4. Enable **biometric authentication** (fingerprint / face)
5. Set a strong **lock screen PIN/password** (not 1234 or 0000)
6. Enable **remote wipe** (Find My iPhone / Find My Device)

**Android vs iOS Security:**
- **iOS** — More restricted, stronger sandboxing, consistent updates
- **Android** — More flexible, varies by manufacturer, wider attack surface

**Mobile Threats:**
- Malicious apps (sideloaded or even in stores)
- SIM swapping attacks
- Public WiFi sniffing
- SMS phishing (smishing)
- Spyware and stalkerware

**Pro Tips:**
- Use a **VPN** on public WiFi
- Enable **2FA** with an authenticator app (not SMS)
- Back up your data regularly
- Don't root/jailbreak unless you know the risks"""
    }
}

# Generic responses for topics not yet covered in detail
GENERIC_RESPONSES = [
    "That's an interesting topic! Could you give me a bit more detail about what specifically you'd like to know? I want to make sure I give you the most useful answer.",
    "Good question! This is a broad area — could you narrow it down a bit? For example, are you looking for a general explanation, a step-by-step guide, or specific tools and commands?",
    "I'd be happy to help with that! Could you provide a bit more context or specify what aspect you're most interested in? That way I can give you a more targeted and useful answer."
]


def _match_knowledge_base(message: str) -> str | None:
    """Match user message against the knowledge engine using keyword matching."""
    msg_lower = message.lower().strip()
    msg_words = set(re.findall(r'\b\w+\b', msg_lower))

    best_match = None
    best_score = 0

    for topic, data in KNOWLEDGE_BASE.items():
        score = 0
        for keyword in data["keywords"]:
            kw_words = keyword.split()
            if len(kw_words) == 1:
                # Single-word keywords must match as whole words
                if kw_words[0] in msg_words:
                    score += 1
            else:
                # Multi-word keywords: check exact phrase first
                if keyword in msg_lower:
                    score += len(kw_words) * 1.5
                elif all(w in msg_words for w in kw_words):
                    score += len(kw_words) * 0.8
        if score > best_score:
            best_score = score
            best_match = data["response"]

    # Require a minimum score to avoid false positives from single incidental keyword matches
    # For short messages (1-4 words), trust even single keyword matches
    min_score = 1.5 if len(msg_words) > 4 else 0.5

    if best_score < min_score:
        return None

    return best_match


def _looks_like_html_response(value: str) -> bool:
    """Detect proxy or gateway HTML that should never be shown in chat."""
    if not isinstance(value, str):
        return False
    normalized = value.lower()
    return (
        "<html" in normalized
        or "<!doctype" in normalized
        or "<head" in normalized
        or "<body" in normalized
        or "cloudflare" in normalized
    )


# ==================== OpenAI Client ====================

SYSTEM_PROMPT = """You are a helpful AI assistant called CyberGuard AI.

Critical Rules:
1. Respond DIRECTLY to the user's question. Never start with introductions or capability listings.
2. Never say "Hello I'm CyberGuard AI" or "I can help you with" unless the user asks who you are.
3. Never display template text, pre-written messages, or promotional content.
4. Never say "My knowledge is limited", "offline knowledge base", or "I cannot answer".
5. If the question is simple, give a direct and concise answer.
6. If the question is technical, explain clearly with examples, commands, or steps.

Response Style:
- Natural conversation like ChatGPT
- Clear explanations with short paragraphs
- Step-by-step answers when needed
- Examples or commands when relevant
- No unnecessary preambles or sign-offs

You can answer ANY topic: programming, cybersecurity, technology, science, education, networking, Linux/Windows, AI, web development, general knowledge, and more."""

client = None
_api_key = os.getenv("OPENAI_API_KEY")
if _api_key:
    client = OpenAI(api_key=_api_key)


class CybersecurityChatbot:
    """ChatGPT-powered cybersecurity assistant with local fallback."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = "gpt-4.1-mini"
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_configured(self) -> bool:
        return self.api_key is not None and len(self.api_key) > 0

    def get_response(self, user_message: str, conversation_history: list = None) -> dict:
        if not user_message or not user_message.strip():
            return {"success": False, "error": "Message cannot be empty.", "message": None}

        # Try OpenAI first
        if self.is_configured() and self.client:
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                if conversation_history:
                    for msg in conversation_history[-10:]:
                        messages.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
                messages.append({"role": "user", "content": user_message.strip()})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=15
                )
                ai_message = response.choices[0].message.content
                if isinstance(ai_message, str) and not _looks_like_html_response(ai_message):
                    return {"success": True, "message": ai_message.strip()}
            except Exception as e:
                print("CyberGuard AI: switching to built-in engine:", e)

        # Built-in knowledge engine
        local_answer = _match_knowledge_base(user_message)
        if local_answer:
            return {"success": True, "message": local_answer}

        return {"success": True, "message": random.choice(GENERIC_RESPONSES)}

    def get_quick_responses(self) -> list:
        return [
            "How do I check if my password was breached?",
            "Explain ethical hacking for beginners",
            "What is Linux and why is it used in cybersecurity?",
            "How can AI help in cybersecurity?",
            "What programming language should I learn first?",
            "How does encryption work?"
        ]


# ==================== Standalone Functions ====================

def ask_chatbot(message: str) -> str:
    """Get a CyberGuard AI response."""
    if not message or not message.strip():
        return "Please enter a message."

    # Try OpenAI first
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.strip()}
                ],
                max_tokens=1000,
                temperature=0.7,
                timeout=15
            )
            ai_message = response.choices[0].message.content
            if isinstance(ai_message, str) and not _looks_like_html_response(ai_message):
                return ai_message.strip()
        except Exception as e:
            print("CyberGuard AI: switching to built-in engine:", e)

    # Built-in knowledge engine
    local_answer = _match_knowledge_base(message)
    if local_answer:
        return local_answer

    return random.choice(GENERIC_RESPONSES)


def is_chatbot_configured() -> bool:
    """Check if the chatbot API key is configured."""
    return client is not None
