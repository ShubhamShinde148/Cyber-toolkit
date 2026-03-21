# Dark Web Leak Monitor – OSINT Security Platform

## Project Report

---

## Table of Contents

1. [Project Title](#1-project-title)
2. [Introduction](#2-introduction)
3. [Objectives](#3-objectives)
4. [Technologies Used](#4-technologies-used)
5. [System Architecture](#5-system-architecture)
6. [Project Modules](#6-project-modules)
7. [File Structure](#7-file-structure)
8. [Features](#8-features)
9. [Security Analysis](#9-security-analysis)
10. [Advantages](#10-advantages)
11. [Limitations](#11-limitations)
12. [Future Enhancements](#12-future-enhancements)
13. [Conclusion](#13-conclusion)

---

## 1. Project Title

**Dark Web Leak Monitor – OSINT Security Platform**

A comprehensive web-based cybersecurity platform built with Python and Flask that enables individuals and organizations to assess their digital exposure through Open-Source Intelligence (OSINT) techniques, dark web breach detection, and a full suite of cybersecurity analysis tools.

---

## 2. Introduction

The digital landscape has witnessed an unprecedented rise in data breaches, credential leaks, and cyber threats. Every year, billions of user credentials—including email addresses, passwords, and personal information—are exposed through breaches of online services and subsequently circulated on the dark web and underground forums. Individuals and organizations often remain unaware that their sensitive data has been compromised until it is too late, leading to identity theft, financial fraud, unauthorized account access, and reputational damage.

Cybersecurity monitoring tools play a critical role in bridging this awareness gap. By leveraging Open-Source Intelligence (OSINT) methodologies, these tools can proactively scan publicly available breach databases, DNS records, WHOIS registrations, and network metadata to identify potential security risks before they are exploited by malicious actors.

**Dark Web Leak Monitor** was developed to address this need. It is a unified, web-based security platform that consolidates over 15 cybersecurity tools into a single, accessible interface. The system empowers users to:

- Check whether their passwords or email addresses have been exposed in known data breaches.
- Perform OSINT reconnaissance on usernames, domains, and IP addresses.
- Analyze file metadata for sensitive information leakage.
- Assess their overall cyber risk posture through automated scoring engines.
- Generate actionable security recommendations and exportable reports.

The platform is designed with a strong emphasis on user privacy. Sensitive data such as passwords are never transmitted in plaintext; instead, the system employs the k-Anonymity protocol to verify breach status without exposing the actual credential. **In Version 3 (V3)**, the system features a "Deep Cyber Minimalist" aesthetic with immersive glassmorphism, transparent navigation, and a high-tech "Mission Control" experience. All operations are performed through a clean, modern web interface with a cybersecurity-themed design, making advanced security assessments accessible to both technical and non-technical users.

---

## 3. Objectives

The Dark Web Leak Monitor project was built to solve the following problems:

1. **Credential Exposure Detection**: Determine whether a user's passwords or email addresses have been leaked in any of the 700+ publicly documented data breaches affecting over 12 billion accounts.

2. **Digital Footprint Discovery**: Enable users to understand the extent of their online presence by scanning 25+ social media and web platforms for username registrations.

3. **Domain Security Assessment**: Provide comprehensive security scoring for domains by analyzing DNS configurations, SSL certificates, security headers, email authentication records (SPF, DKIM, DMARC), and open port exposure.

4. **Network Intelligence**: Offer IP address geolocation, threat classification (VPN, proxy, Tor, datacenter detection), and reverse DNS resolution for network investigation.

5. **Metadata Privacy Analysis**: Extract and analyze embedded metadata from files (images, PDFs, documents) to identify sensitive information leakage such as GPS coordinates, author names, software versions, and camera details.

6. **Cyber Risk Quantification**: Calculate a comprehensive cyber risk score based on multiple factors including breach history, password hygiene, domain security posture, and digital exposure levels.

7. **Security Education**: Provide interactive cybersecurity quizzes, AI-powered security advice, and contextual recommendations to improve users' security awareness and practices.

8. **Unified Tooling**: Consolidate essential cybersecurity utilities (hashing, encoding, DNS lookup, subdomain discovery, JWT decoding, cipher tools) into a single CyberChef-style interface, eliminating the need for multiple disparate tools.

9. **Actionable Reporting**: Generate professional security reports in multiple formats (PDF, HTML, JSON, CSV, TXT) that can be shared with stakeholders for compliance, audit, or remediation purposes.

10. **Privacy-First Architecture**: Ensure all breach checking is performed using privacy-preserving protocols (k-Anonymity) so that user credentials are never transmitted or stored in plaintext.

---

## 4. Technologies Used

### 4.1 Programming Language

| Technology | Purpose |
|---|---|
| **Python 3.x** | Primary backend language for all server-side logic, API integrations, data processing, and security analysis algorithms. |

### 4.2 Web Framework

| Technology | Purpose |
|---|---|
| **Flask 3.0+** | Lightweight Python web framework used for routing, request handling, template rendering, and REST API endpoint creation. |
| **Flask-Login 0.6+** | Extension providing user session management, authentication, and route protection via `@login_required` decorators. |
| **Flask-CORS 4.0+** | Cross-Origin Resource Sharing support for API access. |
| **Jinja2** | Server-side HTML templating engine (bundled with Flask) used to render dynamic pages with template inheritance. |

### 4.3 Frontend Technologies

| Technology | Purpose |
|---|---|
| **HTML5** | Semantic page structure for all 25+ web templates. |
| **CSS3** | Custom **Version 3 (V3)** cybersecurity-themed styling with high-fidelity glassmorphism, neon glows, responsive grid layouts, and a deep-space aesthetic. |
| **JavaScript (ES6+)** | Client-side interactivity including asynchronous API calls (Fetch API), dynamic DOM manipulation, form validation, animated counters, and real-time result rendering. |
| **Google Fonts** | Orbitron (display headings), JetBrains Mono (code/terminal), Rajdhani (body text). |
| **Font Awesome 6.4** | Icon library providing 6,000+ icons for the UI. |

### 4.4 Database

| Technology | Purpose |
|---|---|
| **SQLite** | Lightweight relational database for user account storage (usernames, email addresses, hashed passwords). Database file located at `instance/darkweb_monitor.db`. |

### 4.5 OSINT APIs and External Services

| API / Service | Purpose |
|---|---|
| **Have I Been Pwned (HIBP) v3 API** | Password breach checking via k-Anonymity range endpoint (`api.pwnedpasswords.com`). Email breach checking via the HIBP breachedaccount endpoint with API key authentication. |
| **crt.sh** | Certificate Transparency log search for subdomain enumeration via `crt.sh/?q=%.domain&output=json`. |
| **ip-api.com** | IP geolocation, ASN, ISP identification, and proxy/VPN/Tor detection. |
| **python-whois** | WHOIS registration data retrieval for domain investigation. |
| **OpenAI GPT API** | Powers the AI Cybersecurity Assistant chatbot with a system prompt specialized for cybersecurity advice. |

### 4.6 Cybersecurity and Analysis Libraries

| Library | Purpose |
|---|---|
| **hashlib** (stdlib) | SHA-1 hashing for k-Anonymity, plus MD5, SHA-256, SHA-384, SHA-512, SHA-224 for the hash generator tool. |
| **dnspython 2.4+** | Programmatic DNS record resolution (A, AAAA, MX, NS, TXT, CNAME, SOA, PTR, CAA records). |
| **python-whois 0.9+** | WHOIS protocol queries for domain registration metadata, registrar details, and expiration dates. |
| **exifread 3.0+** | EXIF metadata extraction from JPEG and TIFF image files (GPS, camera, timestamps). |
| **Pillow (PIL) 10.0+** | Image metadata extraction and format detection for PNG, BMP, and other image formats. |
| **PyPDF2 3.0+** | PDF document metadata extraction (author, creator, creation date, producer). |
| **python-docx 1.0+** | Microsoft Word (.docx) document metadata extraction (core properties, authors, dates). |
| **werkzeug.security** | Secure password hashing (`generate_password_hash`, `check_password_hash`) for user authentication. |
| **reportlab 4.0+** | PDF report and quiz certificate generation with custom layouts. |
| **openai 1.0+** | OpenAI API client for GPT-powered cybersecurity chatbot integration. |
| **python-dotenv 1.0+** | Environment variable management for API keys and secrets via `.env` file. |
| **requests 2.28+** | HTTP client for all external API communications. |

---

## 5. System Architecture

The Dark Web Leak Monitor follows a modular, layered architecture where each component has a clearly defined responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Browser)                       │
│         Accesses the platform via web browser                │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    WEB INTERFACE LAYER                       │
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │ index.html│  │dashboard │  │cyber_tools│  │ 25+ more │  │
│   │ (Landing) │  │  (Hub)   │  │(CyberChef)│  │ templates│  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│   CSS (style.css, chatbot.css)                              │
│   JS  (main.js, cyber-particles.js, chatbot.js)            │
└──────────────────────────┬──────────────────────────────────┘
                           │ AJAX (Fetch API) / Form POST
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FLASK BACKEND (app.py)                     │
│                                                             │
│   ┌─────────────────┐  ┌──────────────────┐                │
│   │  Page Routes     │  │  REST API Layer   │                │
│   │  (25+ GET routes)│  │  (40+ endpoints)  │                │
│   └─────────────────┘  └──────────────────┘                │
│                                                             │
│   ┌─────────────────┐  ┌──────────────────┐                │
│   │  Authentication  │  │  Session Manager  │                │
│   │  (Flask-Login)   │  │  (SQLite + Cookies│                │
│   └─────────────────┘  └──────────────────┘                │
└──────────────────────────┬──────────────────────────────────┘
                           │ Function calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               OSINT & SECURITY MODULES LAYER                │
│                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│   │ breach_checker │  │ email_checker │  │ domain_scanner│  │
│   │ (k-Anonymity)  │  │  (HIBP API)   │  │  (DNS/SSL)    │  │
│   └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│   │username_osint  │  │ip_intelligence│  │ whois_lookup  │  │
│   │ (25 platforms) │  │  (Geolocation) │  │  (WHOIS)      │  │
│   └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│   │cyber_risk_eng  │  │metadata_extr  │  │ chatbot       │  │
│   │ (Risk Scoring) │  │  (File Forensic│  │  (GPT AI)     │  │
│   └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                             │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│   │security_advisor│  │breach_timeline│  │ quiz_engine   │  │
│   │(Recommendations│  │  (History)     │  │  (Education)  │  │
│   └───────────────┘  └───────────────┘  └───────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ Function calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CYBER TOOLS LAYER (tools/)                  │
│                                                             │
│   HashTool │ Base64Tool │ URLTool │ JWTDecoder │ IPLookup   │
│   DNSLookup│ SubdomainFinder │ ROT13Tool │ TextBinary      │
│   PasswordStrengthAnalyzer                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                EXTERNAL SERVICES & APIs                      │
│                                                             │
│   HIBP API │ crt.sh │ ip-api.com │ WHOIS │ OpenAI GPT     │
│   DNS Resolvers │ Certificate Transparency Logs             │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 Architectural Flow

1. **User Layer**: The user interacts with the platform through a modern web browser. The interface features a cybersecurity-themed dark design with animated particle backgrounds, scan-line effects, and neon glow aesthetics.

2. **Web Interface Layer**: Built with 25+ Jinja2 HTML templates that extend a common base template (`base.html`). Client-side JavaScript handles asynchronous API calls via the Fetch API, dynamic result rendering, and interactive UI components.

3. **Flask Backend Layer**: The central `app.py` file manages all routing (25+ page routes and 40+ API endpoints), user authentication via Flask-Login with SQLite storage, session management with secure cookie configuration, and request dispatching to the appropriate modules.

4. **OSINT & Security Modules Layer**: Twelve specialized Python modules handle domain-specific logic—breach checking, OSINT scanning, risk analysis, metadata extraction, AI chatbot interaction, and security advisory generation. Each module is self-contained with its own classes, data models, and processing logic.

5. **Cyber Tools Layer**: Ten utility tools in the `tools/` package provide CyberChef-style encoding, hashing, DNS lookup, subdomain discovery, JWT decoding, and cipher operations.

6. **External Services Layer**: The platform integrates with multiple external APIs (HIBP, crt.sh, ip-api.com, WHOIS servers, OpenAI) to source real-time breach data, geolocation intelligence, certificate transparency logs, and AI-powered analysis.

---

## 6. Project Modules

### 6.1 Email Breach Checker (`email_checker.py`)

The Email Breach Checker enables users to determine if their email address has been involved in any known data breaches.

**How It Works:**
- Accepts a user-provided email address and queries the **Have I Been Pwned (HIBP) v3 API** via the `/breachedaccount/{email}` endpoint.
- Requires HIBP API key authentication (sent via `hibp-api-key` header).
- Implements a **1.5-second rate limiting delay** between requests to comply with HIBP's fair usage policy.
- Returns detailed breach information including the breach name, date, compromised data types (emails, passwords, IP addresses, phone numbers), and total affected accounts.
- Results include a risk classification: **Low** (0 breaches), **Medium** (1–2 breaches), **High** (3–5 breaches), or **Critical** (6+ breaches).

**Key Class:** `EmailChecker`
- `check(email)` — Performs the HIBP lookup and returns a structured result with breach details, risk level, and recommendations.

### 6.2 Password Breach Checker (`breach_checker.py`)

The Password Breach Checker verifies whether a password has appeared in known data breaches without ever transmitting the password itself.

**How It Works:**
- Computes the **SHA-1 hash** of the user's password locally.
- Sends only the **first 5 characters** of the hash to the HIBP Passwords API (`api.pwnedpasswords.com/range/{prefix}`).
- The API returns all hash suffixes matching the prefix (~500–800 entries).
- The system locally compares the remaining hash characters against the returned suffixes to determine if the password has been breached.
- This **k-Anonymity protocol** ensures the complete password hash is never exposed to any external service.
- Implements a **0.5-second rate limit** between requests.

**Key Class:** `BreachChecker`
- `check_password(password)` — Returns breach status, occurrence count, risk level (Safe/Low/Medium/High/Critical), and a risk score (0–100).
- Risk scoring: 0 occurrences = 0 (Safe), 1–5 = 30 (Low), 6–50 = 60 (Medium), 51–500 = 80 (High), 500+ = 100 (Critical).

### 6.3 Domain Scanner (`domain_scanner.py`)

The Domain Scanner performs comprehensive security analysis of web domains by evaluating multiple security dimensions.

**How It Works:**
- Resolves DNS records (A, MX, NS, TXT) using the `dnspython` library.
- Checks for **email security** protocols: SPF, DKIM, and DMARC records in DNS TXT entries.
- Evaluates **HTTP security headers**: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security (HSTS), X-XSS-Protection, Referrer-Policy.
- Tests for **HTTPS/SSL** availability and certificate validity.
- Performs **open port scanning** on common ports (21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 3389, 5432, 8080, 8443).
- Calculates a **Security Score (0–100)** based on a weighted combination of findings.

**Key Class:** `DomainScanner`
- `scan(domain)` — Returns a comprehensive `DomainResult` containing security score, DNS records, security headers analysis, email security status, open ports, and categorized recommendations.
- `quick_scan(domain)` — A lightweight scan covering only basic DNS and HTTP checks.

### 6.4 DNS Lookup Tool (`tools/dns_lookup.py`)

A dedicated DNS record resolution tool that queries authoritative nameservers for comprehensive record data.

**How It Works:**
- Uses `dnspython` as the primary resolver with fallback to `socket` for basic queries.
- Supports **9 record types**: A (IPv4), AAAA (IPv6), MX (mail exchange with priority), NS (nameservers), TXT (text records), CNAME (aliases), SOA (start of authority), PTR (reverse DNS), and CAA (certificate authority authorization).
- The `lookup_all()` method queries all supported record types in a single operation.

**Key Class:** `DNSLookupTool`
- `lookup(domain, record_type)` — Returns structured DNS results for the specified record type.
- `lookup_all(domain)` — Batch query returning all DNS record types.

### 6.5 Subdomain Finder (`tools/subdomain_finder.py`)

A multi-technique subdomain enumeration tool that discovers subdomains through both passive and active methods.

**How It Works:**
- **Certificate Transparency (CT) Log Search**: Queries `crt.sh` for SSL/TLS certificates issued for the target domain, extracting subdomain names from certificate Subject Alternative Names.
- **Brute-Force Enumeration**: Uses a wordlist of 120+ common subdomain prefixes (www, mail, ftp, admin, api, dev, staging, cdn, vpn, etc.) and attempts DNS resolution for each candidate using multi-threaded execution (20 concurrent workers via `ThreadPoolExecutor`).
- Each discovered subdomain is resolved to its IP address and tagged with the discovery source (crt.sh or bruteforce).

**Key Class:** `SubdomainFinder`
- `find(domain, use_bruteforce, use_crtsh, custom_wordlist)` — Full enumeration with configurable techniques.
- `quick_scan(domain)` — Fast scan using a 24-entry abbreviated wordlist.

### 6.6 IP Intelligence (`ip_intelligence.py`)

An IP address intelligence module that provides geolocation, network ownership, and threat classification data.

**How It Works:**
- Validates IPv4 and IPv6 addresses using regex patterns and `socket.inet_pton()`.
- Detects **private** (RFC 1918: 10.x, 172.16–31.x, 192.168.x), **reserved** (loopback, link-local, multicast), and **public** IP address ranges.
- For public IPs, queries `ip-api.com` for geolocation data (country, region, city, lat/lon, timezone) and network information (ASN, ISP, organization).
- Performs **threat classification**: identifies VPN, proxy, Tor exit node, and datacenter-hosted IP addresses.
- Includes reverse DNS (PTR) lookup via `socket.gethostbyaddr()`.
- Aggregates results into a structured intelligence report with risk indicators.

**Key Class:** `IPIntelligence`
- `lookup(ip_address)` — Returns comprehensive intelligence including geolocation, network ownership, threat indicators, and an overall threat score.

### 6.7 Username OSINT Scanner (`username_osint.py`)

A multi-platform username enumeration tool that checks whether a username is registered across 25+ online services.

**How It Works:**
- Maintains a curated list of **25 platform definitions**, each with a URL template and expected HTTP status codes for "found" vs "not found" responses.
- Platforms include: GitHub, Twitter/X, Instagram, Reddit, TikTok, LinkedIn, Pinterest, Steam, Twitch, YouTube, Medium, Dev.to, GitLab, Keybase, Flickr, About.me, Patreon, Spotify, SoundCloud, Behance, Dribbble, Gravatar, HackerOne, ProductHunt, and Replit.
- Sends HTTP HEAD/GET requests with a configurable timeout (5 seconds per platform).
- Classifies results as **Found**, **Not Found**, or **Error** based on HTTP status codes.
- Calculates a **digital footprint score** based on the ratio of found accounts to total platforms checked.

**Key Class:** `UsernameOSINT`
- `scan(username)` — Returns platform-by-platform results, total found count, digital footprint percentage, and a categorized summary.

### 6.8 WHOIS Lookup (`whois_lookup.py`)

A domain registration intelligence tool that retrieves comprehensive WHOIS records.

**How It Works:**
- Uses the `python-whois` library to query WHOIS servers for domain registration data.
- Extracts key metadata: registrar, organization, creation date, expiration date, last updated date, name servers, DNSSEC status, and registrant information (when available/not redacted).
- Calculates **domain age** from the creation date.
- Flags **expiring domains** (within 30 days of expiration) as potential security concerns.
- Handles WHOIS privacy protection and GDPR-redacted records gracefully.

**Key Class:** `WhoisLookup`
- `lookup(domain)` — Returns structured WHOIS data including registration details, domain age, expiration warnings, and nameserver information.

### 6.9 Metadata Extractor (`metadata_extractor.py`)

A file forensics module that extracts and analyzes embedded metadata from uploaded files to identify potential privacy and security risks.

**How It Works:**
- Supports four file types: **JPEG/TIFF** (via exifread), **PNG/BMP** (via Pillow/PIL), **PDF** (via PyPDF2), and **DOCX** (via python-docx).
- Validates uploads through **magic byte verification** (file signature checking) and extension whitelisting, with a 50 MB file size limit.
- **Image metadata extraction**: EXIF data including camera make/model, exposure settings, GPS coordinates (latitude/longitude with DMS conversion), timestamps, software used, and image dimensions.
- **PDF metadata extraction**: Title, author, creator application, producer, creation/modification dates, page count, and encryption status.
- **DOCX metadata extraction**: Core properties including author, last modified by, created/modified dates, revision number, and word/page/paragraph counts.
- Flags **OPSEC-sensitive findings**: GPS coordinates, author/creator names, software versions, and device identifiers are highlighted as potential privacy risks.

**Key Class:** `MetadataExtractor`
- `extract(file_path)` — Returns comprehensive metadata, identified risks, and privacy recommendations.
- `get_supported_formats()` — Lists available extraction capabilities based on installed libraries.

### 6.10 Cyber Risk Assessment (`cyber_risk_engine.py`)

A multi-factor risk scoring engine that evaluates an organization's or individual's overall cybersecurity posture.

**How It Works:**
- Accepts multiple input vectors: email addresses, passwords, domain names, and IP addresses.
- Performs a **comprehensive scan** by invoking the breach checker, email checker, domain scanner, and IP intelligence modules.
- Calculates a **Cyber Risk Score (0–100)** using a weighted formula:
  - Password breach exposure (35% weight)
  - Email breach count and severity (25% weight)
  - Domain security posture (25% weight)
  - IP threat indicators (15% weight)
- Generates risk category classifications: **Low** (0–25), **Medium** (26–50), **High** (51–75), **Critical** (76–100).
- Produces a prioritized list of **remediation actions** with severity ratings.

**Key Class:** `CyberRiskEngine`
- `assess(email, password, domain, ip)` — Returns overall risk score, per-category breakdown, and prioritized recommendations.
- `quick_assess(email)` — Lightweight assessment based solely on email breach data.

### 6.11 AI Cybersecurity Assistant (`chatbot.py`)

An AI-powered chatbot that provides contextual cybersecurity guidance using OpenAI's GPT models.

**How It Works:**
- Integrates with the **OpenAI GPT API** using a specialized system prompt that constrains responses to cybersecurity topics.
- The system prompt instructs the AI to act as a cybersecurity expert, providing advice on data breaches, password security, phishing, network security, and dark web monitoring.
- Maintains **conversation history** per session for contextual follow-up questions.
- Limits responses to relevant cybersecurity topics and redirects off-topic queries.
- Gracefully handles API unavailability with a fallback message.
- Configuration is controlled via the `OPENAI_API_KEY` environment variable.

**Key Functions:**
- `ask_chatbot(message, conversation_history)` — Sends a user message with context and returns the AI-generated response.
- `is_chatbot_configured()` — Returns whether the OpenAI API key is properly set.

### 6.12 Security Dashboard

The Security Dashboard serves as the authenticated user's central hub, providing quick-access navigation to all platform tools.

**How It Works:**
- Displays a personalized greeting with the user's email address.
- Presents a **10-item tool grid** with direct links to:
  1. Password Breach Check
  2. Email Breach Check
  3. Username OSINT
  4. Domain Security Scanner
  5. WHOIS Lookup
  6. IP Intelligence
  7. Website Technology Detector
  8. Cyber Tools
  9. Password Generator
  10. Batch Processing
- All dashboard routes are protected with the `@login_required` decorator.
- Session statistics tracking via the `/api/stats` endpoint provides usage metrics.

### 6.13 Additional Modules

#### Security Advisor (`security_advisor.py`)
Generates **context-aware security recommendations** based on the results of scans and assessments. Produces prioritized action plans grouped by category (passwords, email, network, device, social engineering) with severity ratings (Critical, High, Medium, Low).

#### Breach Timeline (`breach_timeline.py`)
Creates **chronological breach history visualizations** for email addresses, presenting when breaches occurred, what data was exposed, and the timeline progression of exposure events.

#### Quiz Engine (`quiz_engine.py`)
An interactive cybersecurity **knowledge assessment system** with categorized questions covering network security, passwords, phishing, malware, encryption, and data privacy. Features include question shuffling, per-category scoring with percentage breakdowns, and **PDF certificate generation** (via ReportLab) for completed quizzes.

#### Password Generator (`password_generator.py`)
A **secure random password generator** supporting configurable length, character set inclusion (uppercase, lowercase, digits, symbols), and exclusion of ambiguous characters. Uses Python's `secrets` module for cryptographically secure random generation.

#### Batch Checker (`batch_checker.py`)
Enables **bulk breach checking** for up to 50 passwords or email addresses in a single operation. Processes items sequentially with rate limiting and returns aggregated results with per-item breach status.

#### Website Technology Detector (`website_technology_detector.py`)
Identifies **web technologies** used by a target website through HTTP response header analysis, HTML content inspection, and known signature detection. Detects web servers, frameworks, CMS platforms, CDNs, analytics tools, and JavaScript libraries.

#### Report Generator (`report_generator.py`)
Produces **professional PDF security reports** using the ReportLab library. Reports include executive summaries, scan results, risk scores, visualizations, and actionable recommendations formatted for business stakeholders.

#### Export Manager (`export_manager.py`)
Handles **multi-format data export** supporting JSON, CSV, HTML, and TXT output. Exports are saved to the `exports/` directory and made available for download via the `/api/download/<filename>` endpoint.

#### Feedback Mailer (`feedback_mailer.py`)
Manages **user feedback collection** and email notification. Collects ratings, text feedback, page context, and user agent data. When email is configured (via SMTP environment variables), feedback is forwarded to the administrator.

#### Risk Analyzer (`risk_analyzer.py`)
A supplementary risk analysis module providing additional **risk quantification** logic used in conjunction with the Cyber Risk Engine for comprehensive assessments.

---

## 7. File Structure

```
darkweb_monitor/
│
├── app.py                          # Main Entry (V1 Legacy + V2 Dispatcher)
├── app_modular.py                  # V2 Modular Application Factory
├── requirements.txt                # System dependencies
├── .env                            # API keys & Security secrets
│
├── core/                           # V2 Foundation Layer
│   ├── config.py                   # Platform configuration settings
│   └── extensions.py               # Database, Login, and Firebase init
│
├── routes/                         # V2 Blueprint Route Layer
│   ├── auth_routes.py              # User authentication & session logic
│   ├── ui_routes.py                # Dashboard & Main UI delivery
│   ├── tools_routes.py             # Cyber Tools workspace routes
│   ├── osint_routes.py             # Domain/Username OSINT routes
│   └── ctf_routes.py               # Capture The Flag engine routes
│
├── services/                       # Security & OSINT Service Engines
│   ├── breach_checker.py           # Password leak detection (k-Anonymity)
│   ├── email_checker.py            # Email breach lookup (HIBP API)
│   ├── domain_scanner.py           # Domain security & scoring engine
│   ├── chatbot.py                  # CyberGuard AI (GPT-4) integration
│   ├── cyber_risk_engine.py        # Multi-factor risk quantification
│   ├── username_osint.py           # Digital footprint mapper (30+ sites)
│   └── ... (20+ specialized security modules)
│
├── tools/                          # Atomic Technical Utilities (CyberChef style)
│   ├── hash_tool.py                # Multi-algorithm hashing
│   ├── dns_lookup.py               # Advanced DNS enumeration
│   ├── subdomain_finder.py         # CT Log & Brute-force discovery
│   └── ... (10+ unified utility tools)
│
├── templates/                      # V3 UI Templates (Jinja2)
│   ├── base.html                   # Master layout (Glassmorphism + Particles)
│   ├── dashboard.html              # V3 Mission Control Hub
│   ├── certificate.html            # Certification generation layout
│   └── components/                 # Reusable UI fragments (nav, footer)
│
├── static/                         # Assets & UI Resources
│   ├── css/style.css               # V3 "Deep Cyber" design system tokens
│   ├── js/main.js                  # Core UI interactivity & AJAX
│   └── img/                        # High-tech vectors and icons
│
├── instance/                       # Local state components (DB)
├── certificates/                   # Generated certification storage
└── exports/                        # Security reports and data dumps
```

### Key File Descriptions

| File | Location | Purpose |
|---|---|---|
| `app_modular.py` | Root | The V2 Application Factory responsible for initializing the modular platform, mounting blueprints, and establishing the unified DispatcherMiddleware. |
| `core/extensions.py` | `core/` | Central extension registry handling Firestore client initialization, Flask-Login managers, and SQLAlchemy binding. |
| `routes/ui_routes.py` | `routes/` | Orchestrates the primary user interface delivery, including the V3 Mission Control dashboard and authenticated page routing. |
| `services/` | `services/` | Contains the platform's "Brain" - 27+ specialized security and OSINT engines ranging from breach detection to AI security advisors. |
| `tools/` | `tools/` | Atomic utility package providing standalone technical capabilities for hashing, DNS, and encoding. |

---

## 8. Features

### 8.1 Dark Web Breach Detection

The platform provides two primary breach detection mechanisms:

- **Password Breach Check**: Uses the k-Anonymity model to query the HIBP Passwords database of 600M+ compromised passwords. The user's password is SHA-1 hashed locally, and only a 5-character prefix is sent to the API, ensuring the actual password is never exposed. Results include the exact number of times the password appeared in breaches and a risk severity rating.

- **Email Breach Check**: Queries the HIBP v3 breached accounts API to identify all known data breaches involving the user's email address. Returns granular details including the breached service name, breach date, compromised data classes (passwords, IP addresses, geographic locations), and total affected accounts.

### 8.2 OSINT Intelligence Tools

- **Username OSINT**: Scans 25 platforms (GitHub, Twitter/X, Instagram, Reddit, TikTok, LinkedIn, Steam, Twitch, YouTube, and more) to map a username's digital footprint. Provides a footprint score and per-platform status.
- **Domain Scanner**: Security scoring (0–100) with DNS record analysis, security header evaluation, email authentication (SPF/DKIM/DMARC) verification, SSL check, and open port detection.
- **IP Intelligence**: Geolocation (country, city, coordinates), network ownership (ASN, ISP, organization), and threat indicators (VPN, proxy, Tor, datacenter).
- **WHOIS Lookup**: Domain registration details including registrar, creation/expiration dates, domain age, nameservers, and DNSSEC status.
- **Website Technology Detector**: Fingerprints web technologies through HTTP header analysis and content inspection.

### 8.3 CyberChef-Style Tools

A unified workspace providing 10 cybersecurity utility tools accessible from a single page:

| Tool | Functionality |
|---|---|
| Hash Generator | MD5, SHA-1, SHA-256, SHA-384, SHA-512, SHA-224 hash computation |
| Base64 Encoder/Decoder | Standard and URL-safe Base64 encoding/decoding |
| URL Encoder/Decoder | URL percent-encoding, decoding, and URL parsing |
| JWT Token Decoder | Decode JWT tokens, display header, payload, and signature |
| Password Strength Analyzer | 0–100 scoring, entropy calculation, crack time estimation |
| IP Lookup | IP geolocation, network details, threat classification |
| DNS Lookup | Query A, AAAA, MX, NS, TXT, CNAME, SOA, PTR, CAA records |
| Subdomain Finder | CT log search and bruteforce subdomain enumeration |
| Text ↔ Binary Converter | Convert between text, binary, hexadecimal, decimal, and octal |
| ROT13/Caesar Cipher | ROT13, ROT47, Atbash, Caesar cipher with brute-force mode |

### 8.5 V3 "Mission Control" Experience (New)

Introduced in the latest platform update, the **V3 Dashboard** transforms the user experience into a terminal-like "Mission Control" center.
- **Glassmorphism Grid**: Components use premium translucent backgrounds with high-fidelity blurs.
- **Transparent Navbar**: A high-tech glass navigation bar that dynamically blurs and darkens on scroll.
- **Advanced Tools Console**: A restructured intelligence grid with glowing hover effects and refined icons.
- **Real-time Status Indicators**: Immersive system badges showing "System Mode" and "Protection Coverage."

### 8.4 Security Dashboard

An authenticated hub providing:
- Personalized user greeting with account information.
- Quick-access grid to all 10 primary security tools.
- Session-based scan statistics and usage tracking.
- Protected routes requiring user authentication.

### 8.5 Feedback System

- **Exit Feedback Modal**: Triggered on page exit intent, collecting quick ratings and comments.
- **Feedback Form**: Detailed feedback submission with ratings, text input, and page context capture.
- **Email Notification**: When SMTP is configured, feedback is automatically forwarded to the administrator via email with full metadata (timestamp, IP, user agent, page URL).

### 8.6 AI Cybersecurity Chatbot

- Powered by OpenAI's GPT model with a specialized cybersecurity system prompt.
- Available as a floating widget across all pages and as a dedicated full-page interface.
- Maintains per-session conversation history for contextual multi-turn discussions.
- Topics include breach analysis, password security, phishing detection, network hardening, and dark web awareness.
- Gracefully handles API unavailability with informative fallback messages.

### 8.7 Security Report Generator

- Generates professional **PDF security reports** via the ReportLab library.
- Exports data in **5 formats**: JSON, CSV, HTML, TXT, and PDF.
- Reports include executive summaries, scan results, risk scores, and recommendations.
- Files are saved to the `exports/` directory and downloadable via the API.
- **HTML reports** with styled formatting for browser viewing.

### 8.8 Additional Features

- **Batch Processing**: Check up to 50 passwords or emails in a single bulk operation.
- **Cyber Risk Assessment**: Weighted multi-factor risk score (0–100) aggregating password, email, domain, and IP risk vectors.
- **Security Advisor**: Generates prioritized remediation action plans.
- **Breach Timeline**: Visualizes the chronological history of breach events.
- **Cybersecurity Quiz**: Interactive knowledge assessment with category-based scoring and PDF certificate generation upon completion.
- **Password Generator**: Cryptographically secure password generation with configurable complexity.
- **Metadata Extractor**: Upload-based file forensics with OPSEC risk flagging for JPEG, PNG, PDF, and DOCX files.

---

## 9. Security Analysis

### 9.1 How the System Detects Digital Exposure

The Dark Web Leak Monitor employs a multi-layered approach to identifying digital exposure and security risks:

#### Credential Exposure Detection
- **k-Anonymity Protocol**: Passwords are SHA-1 hashed locally, and only a 5-character hash prefix is transmitted to the HIBP API. This mathematical privacy guarantee ensures that the full password is never exposed to any external service, even if network traffic is intercepted.
- **Email Breach Correlation**: Email addresses are checked against the HIBP breach database, cross-referencing against 700+ documented breaches to identify specific services where the email was compromised.

#### Digital Footprint Mapping
- The **Username OSINT module** systematically probes 25 platforms to construct a map of a user's online presence. A large digital footprint increases attack surface for social engineering and credential stuffing attacks.
- The **WHOIS module** reveals domain registration details that may expose registrant identity, organization, and contact information.

#### Infrastructure Security Assessment
- **DNS Configuration Analysis**: Identifies missing email authentication records (SPF, DKIM, DMARC) that leave domains vulnerable to email spoofing and phishing attacks.
- **Security Header Evaluation**: Checks for critical HTTP security headers (CSP, HSTS, X-Frame-Options) whose absence enables XSS, clickjacking, and man-in-the-middle attacks.
- **Port Exposure Detection**: Identifies open network ports that may expose unnecessary services to the internet.
- **SSL/TLS Verification**: Confirms the presence and validity of SSL certificates for transport encryption.

#### Metadata Leakage Analysis
- **EXIF GPS Extraction**: Detects embedded GPS coordinates in images that could reveal the user's physical location.
- **Author/Software Identification**: Extracts creator names, software versions, and device identifiers that could be used for profiling or targeted attacks.
- **Document Properties Analysis**: Identifies revision history, company names, and internal usernames embedded in PDF and DOCX files.

#### Risk Quantification
- The **Cyber Risk Engine** aggregates findings across all scan dimensions into a single 0–100 risk score using weighted factors:
  - Password breach exposure: 35% weight
  - Email breach history: 25% weight
  - Domain security posture: 25% weight
  - IP threat indicators: 15% weight
- Generates **severity-rated recommendations** prioritized for maximum security impact.

### 9.2 Security Measures Implemented in the Platform

| Security Control | Implementation |
|---|---|
| Password Hashing | `werkzeug.security.generate_password_hash()` for user account passwords |
| Session Security | HttpOnly cookies, SameSite=Lax, SECRET_KEY-based session signing |
| Input Sanitization | `html.escape()` applied to user-facing inputs (feedback, metadata) |
| File Upload Validation | Magic byte verification, extension whitelist, 50 MB size limit |
| Rate Limiting | 0.5s delay for password checks, 1.5s for email checks (HIBP compliance) |
| API Key Management | Environment variables via `.env` file (never hardcoded) |
| Route Protection | `@login_required` decorator on all authenticated endpoints |
| CORS Configuration | Flask-CORS for controlled cross-origin API access |

---

## 10. Advantages

1. **All-in-One Platform**: Consolidates 15+ cybersecurity tools into a single web interface, eliminating the need to use multiple disparate tools and websites for security assessments.

2. **Privacy-First Design**: The k-Anonymity protocol ensures passwords are never transmitted in full to any external service, providing a mathematically proven privacy guarantee during breach checking.

3. **No Installation Required**: As a web-based application, users access the platform through any modern browser without installing specialized software or command-line tools.

4. **Comprehensive Risk Scoring**: The multi-factor Cyber Risk Engine provides a quantified, weighted risk score (0–100) that aggregates credential exposure, domain security, and network threat indicators into an actionable metric.

5. **Professional Report Generation**: Exportable security reports in 5 formats (PDF, HTML, JSON, CSV, TXT) suitable for business stakeholders, compliance audits, and remediation planning.

6. **Educational Component**: The cybersecurity quiz module with category scoring and PDF certificate generation promotes security awareness and knowledge development.

7. **AI-Powered Guidance**: The GPT-powered chatbot provides contextual cybersecurity advice, making expert-level security guidance accessible to non-technical users.

8. **Modular Architecture**: Each security tool is implemented as an independent Python module, enabling easy maintenance, testing, and extension without impacting other components.

9. **Accessibility**: The cybersecurity-themed dark UI with responsive design works across desktop and mobile devices, making security tools accessible from any device.

10. **Open-Source Intelligence**: Leverages publicly available data sources (HIBP, CT logs, WHOIS, DNS) without requiring expensive commercial threat intelligence subscriptions.

11. **Batch Processing**: The ability to check up to 50 credentials simultaneously saves significant time for users managing multiple accounts or performing organizational audits.

12. **Metadata Forensics**: File metadata extraction with OPSEC risk flagging helps users identify sensitive information they may be unknowingly sharing through file uploads and distribution.

---

## 11. Limitations

1. **Passive Monitoring Only**: The platform relies on publicly available breach databases and OSINT sources. It cannot detect undisclosed breaches, zero-day exposures, or data circulating exclusively on private dark web forums that have not been indexed by HIBP.

2. **API Dependencies**: Core functionality depends on external APIs (HIBP, ip-api.com, crt.sh, OpenAI). Service outages, rate limit changes, or API deprecation could temporarily or permanently affect specific features.

3. **HIBP API Key Requirement**: Email breach checking requires a paid HIBP API key. Without it, only password breach checking (which uses the free k-Anonymity endpoint) is available.

4. **No Real-Time Monitoring**: The system performs on-demand checks rather than continuous monitoring. Users must manually initiate scans to detect new exposures; there is no automated alerting for newly discovered breaches.

5. **Username OSINT Accuracy**: Platform availability checks rely on HTTP status codes, which can produce false positives (custom 404 pages returning 200 status) or false negatives (rate limiting, CAPTCHAs, geo-blocking).

6. **Limited Port Scanning**: The domain scanner checks only 16 common ports with basic TCP connectivity. It does not perform service fingerprinting, vulnerability detection, or deep protocol analysis.

7. **No Vulnerability Scanning**: The platform assesses security configuration and breach exposure but does not perform active vulnerability scanning (CVE detection, exploit testing) against target systems.

8. **Single-User SQLite Database**: The SQLite database is suitable for single-user or small-team deployments but does not support concurrent write operations required for high-traffic production environments.

9. **WHOIS Privacy**: Many domains use WHOIS privacy protection or GDPR-redacted records, limiting the registration intelligence that can be extracted.

10. **Metadata Extraction Scope**: File analysis is limited to JPEG, PNG, PDF, and DOCX formats. Other common formats (video, audio, spreadsheets, archives) are not currently supported.

11. **AI Chatbot Dependency**: The cybersecurity chatbot requires a valid OpenAI API key and incurs per-query costs. Without it, the chatbot feature is unavailable.

---

## 12. Future Enhancements

### 12.1 Live Breach Monitoring
Implement **continuous automated monitoring** with scheduled background scans for registered email addresses, triggering instant email/SMS/push notifications when new breaches are detected. Integration with breach notification feeds for real-time alerts.

### 12.2 Automated Recon Engine
Develop a **comprehensive automated reconnaissance workflow** that chains multiple OSINT tools into a single operation—given a target domain or organization, automatically execute DNS enumeration, subdomain discovery, WHOIS lookup, technology detection, port scanning, and email harvesting to produce a consolidated intelligence report.

### 12.3 Advanced Threat Intelligence
Integrate commercial and open-source **threat intelligence feeds** (AlienVault OTX, AbuseIPDB, VirusTotal, Shodan) to provide deeper context on IP reputation, malware indicators of compromise (IOCs), and known threat actor infrastructure.

### 12.4 Vulnerability Scanning
Add **active vulnerability assessment** capabilities including CVE database cross-referencing for detected technologies, SSL/TLS configuration analysis (cipher suites, protocol versions, certificate chain validation), and basic web application vulnerability detection (open redirects, directory traversal, information disclosure).

### 12.5 Multi-User & Team Support
Migrate from SQLite to **PostgreSQL/MySQL** with role-based access control (RBAC), team workspaces, shared scan histories, and collaborative report generation for organizational security teams.

### 12.6 API Platform
Expose the platform's capabilities through a **documented RESTful API** with API key authentication, rate limiting, and webhook support, enabling integration into existing security workflows, CI/CD pipelines, and SIEM systems.

### 12.7 Dark Web Crawling
Implement controlled **dark web monitoring** through Tor network integration, scanning paste sites, underground forums, and marketplace listings for leaked credentials and sensitive data mentions.

### 12.8 Enhanced Reporting & Compliance
Generate **compliance-mapped reports** aligned with frameworks such as NIST Cybersecurity Framework, ISO 27001, GDPR Article 32, and SOC 2, with automated gap analysis and remediation tracking.

### 12.9 Browser Extension
Develop a companion **browser extension** that provides real-time password breach warnings during login, scans visited websites for known vulnerabilities, and alerts users to phishing attempts.

### 12.10 Machine Learning Integration
Train models for **anomaly detection** in network traffic patterns, predictive breach risk scoring based on historical trends, and automated classification of OSINT findings by relevance and severity.

---

## 13. Conclusion

The **Dark Web Leak Monitor – OSINT Security Platform** represents a comprehensive approach to personal and organizational cybersecurity assessment. By consolidating 15+ specialized security tools into a unified web-based platform, it addresses the fragmentation problem that forces security professionals and everyday users alike to rely on multiple disparate services for basic security hygiene.

The platform's core strength lies in its **privacy-preserving breach detection** using the k-Anonymity protocol, ensuring that users can verify their credential exposure without creating additional security risks in the process. Combined with multi-platform OSINT scanning, domain security assessment, IP intelligence, metadata forensics, and AI-powered guidance, the system provides a holistic view of an individual's or organization's digital exposure.

The **modular Python architecture** ensures maintainability and extensibility—each security tool operates as an independent module that can be updated, replaced, or extended without impacting the broader system. The Flask backend efficiently orchestrates 40+ API endpoints serving both the web interface and programmatic access, while the cybersecurity-themed frontend delivers a professional, accessible user experience.

With its **Cyber Risk Engine** providing quantified risk scoring, **professional report generation** for stakeholder communication, **interactive quiz system** for security education, and **AI chatbot** for on-demand guidance, the platform goes beyond simple scanning tools to deliver actionable intelligence and promote security awareness.

While current limitations include the reliance on passive OSINT sources and external API dependencies, the planned future enhancements—including live monitoring, automated reconnaissance, threat intelligence integration, and vulnerability scanning—chart a clear path toward a more comprehensive cybersecurity operations platform.

In an era where data breaches affect billions of accounts annually and digital exposure continues to grow, tools like the Dark Web Leak Monitor serve a critical role in democratizing access to cybersecurity intelligence, helping users take proactive control of their digital security posture before threats materialize into real-world consequences.

---

**Project:** Dark Web Leak Monitor – OSINT Security Platform  
**Technology Stack:** Python 3.x, Flask 3.0+, SQLite, HTML5, CSS3, JavaScript ES6+, OpenAI GPT  
**Codebase:** ~8,500 lines across 38 source files  
**API Endpoints:** 40+ (25 page routes, 15+ REST APIs)  
**External Integrations:** HIBP, crt.sh, ip-api.com, WHOIS, OpenAI  
**Security Tools:** 15+ modules and utility tools  

---

*Report generated for academic and professional documentation purposes.*
