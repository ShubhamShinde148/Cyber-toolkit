# 🏗️ Platform Architecture & File Guide

This document provides a technical overview of the **DarkWeb Monitor** project structure. The platform uses a **Tiered Modular Architecture** designed for scalability, security, and high-performance OSINT scanning.

---

## 📂 Directory Hierarchy

### 1. 🏰 Application Entry Points
- `app.py`: The central hub. It handles legacy V1 routes and acts as a dispatcher for the V2 modular system.
- `app_modular.py`: The **Application Factory**. It initializes the Flask app, registers all blueprints (routes), and sets up shared extensions.
- `.env`: **Critical Security File**. Stores all private API keys (OpenAI, HIBP, Firebase) and SMTP credentials.

### 2. 🛡️ `services/` — The Intelligence Engines
This is the "Brain" of the platform. Each file is a standalone security service.
- `breach_checker.py`: Implements hashing and k-anonymity for safe password checking.
- `email_checker.py`: Interfaces with the HIBP API for deep email breach analysis.
- `domain_scanner.py`: Orchestrates DNS, SSL, and Header assessments.
- `chatbot.py`: Handles high-level AI reasoning via the GPT-4 "CyberGuard" engine.
- `cyber_risk_engine.py`: The logic that calculates the 0-100% "Risk Score".

### 3. 🌐 `routes/` — The Blueprint Layer
Separates the UI and logic from the main application file.
- `auth_routes.py`: Logic for User Login, Registration, and Session management.
- `ui_routes.py`: Delivers the V3 Mission Control Dashboard and tool interfaces.
- `ctf_routes.py`: Manages the Capture The Flag challenges and scoring.
- `osint_routes.py`: Dedicated endpoints for Domain and Username intelligence.

### 4. 🧰 `tools/` — Atomic Security Utilities
Lightweight, reusable technical tools (CyberChef style).
- `hash_tool.py`: Fast multi-algorithm hashing.
- `dns_lookup.py`: Raw DNS query engine (A, MX, TXT, etc.).
- `subdomain_finder.py`: Combines certificate logs and brute-force discovery.

### 5. 🎨 `static/` & `templates/` — The V3 Interface
- `static/css/style.css`: Contains the "Deep Cyber" design system (Glassmorphism, Neon Glows).
- `static/js/main.js`: Handles fast, asynchronous UI updates without page reloads.
- `templates/base.html`: The master layout that provides the unified cyber aesthetic across all 25+ pages.

### 6. 📁 Data & Assets
- `instance/`: Contains the local SQLite database for encrypted user credentials.
- `exports/`: Temporary storage for generated HTML and CSV security reports.
- `certificates/`: Repository for generated Cybersecurity Certification PDFs.

---

## ⚡ Development Workflow
- **Adding a Feature**: Create a new class in `services/`, define its routes in `routes/`, and add a UI link in `dashboard.html`.
- **Applying Styles**: Modify `style.css` globally; use CSS variables for neon colors.
- **API Updates**: Add new keys to `.env` and initialize the service in `app_modular.py`.
