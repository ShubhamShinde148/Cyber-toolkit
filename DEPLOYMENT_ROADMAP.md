# Dark Web Leak Monitor: Professional Deployment Roadmap

This document outlines the end-to-end deployment strategy, architecture, and security practices for taking the **Dark Web Leak Monitor** platform from development to a production-grade external environment.

---

## 1. Hosting Architecture Diagram & Overview

For a cybersecurity-focused platform, the architecture must prioritize **uptime**, **security**, and **data protection**.

```mermaid
graph TD
    Client[Client / Web Browser] -->|HTTPS| CF[Cloudflare WAF / CDN]
    CF -->|Proxy/TLS| LB[Load Balancer / Ingress]
    
    subgraph Hosting Platform [Platform as a Service e.g., Render/Railway]
        LB --> FlaskApp[Flask Web App & API Gateway]
        FlaskApp <--> Services[Modular Scanners & Generators]
    end
    
    subgraph Data Layer
        FlaskApp <--> DB[(PostgreSQL Database)]
        FlaskApp <--> Redis[(Redis Cache)]
    end
    
    subgraph Storage
        FlaskApp <--> S3[Cloud Object Storage]
    end

    subgraph External APIs
        Services --> HIBP[HaveIBeenPwned API]
        Services --> VT[VirusTotal API]
        Services --> Shodan[Shodan API]
    end
```

---

## 2. Backend Hosting Platform

Since the platform relies on Flask and modular Python scripts (some of which perform network/OSINT operations), we need a platform that supports Python, environmental variables, and potentially background workers (for long-running OSINT scans).

### Recommended Platforms:
1.  **Render (Best Overall for Flask + PostgreSQL)**
    *   **Pros:** Native Python support, built-in free managed PostgreSQL (for the first 90 days, then easily scalable), free SSL, background workers (Web Services + Background Workers).
    *   **Cons:** Free tier spins down after inactivity (Upgrade to $7/mo "Starter" tier for production).
2.  **Railway (Best for Rapid Deployment)**
    *   **Pros:** Excellent GitHub integration, extremely fast deployments, easy to spin up a Redis or PostgreSQL instance alongside the app.
    *   **Cons:** No free tier anymore, but $5/mo gets you a highly capable production environment.
3.  **DigitalOcean Droplet / VPS (Best for Ultimate Control)**
    *   **Pros:** Full root access. Crucial if your OSINT tools require raw sockets or specific Linux networking utilities (like `nmap` or `masscan`).
    *   **Cons:** You must manage the OS, reverse proxy (Nginx), SSL (Certbot), and firewall (UFW) yourself.

**Recommendation:** Start with **Render** (Starter Tier) for simplicity and a managed database. If your OSINT tools require specialized binary dependencies, migrate to a **DigitalOcean VPS** layered with Docker.

---

## 3. Domain Setup

To appear professional and trustworthy as a cybersecurity platform, a custom domain is mandatory.

*   **Free Options:** `.tk`, `.ml`, `.ga` (Freenom) – **Do not use these.** They are heavily associated with phishing and malware, causing email deliverability issues and browser warnings.
*   **Paid Options (Recommended):** Purchase a `.com`, `.security`, or `.io` domain from **Cloudflare Registrar** or **Namecheap**. Cloudflare Registrar offers domains at wholesale prices with no markup.

---

## 4. Cloudflare Security Integration

Putting **Cloudflare** in front of your Flask application is non-negotiable for a cybersecurity product.

*   **DDoS Protection:** Absorbs volumetric attacks.
*   **Web Application Firewall (WAF):** Block SQLi, XSS, and known vulnerability scanners.
*   **TLS/SSL:** Strict SSL mode (Client <-> Cloudflare <-> Render).
*   **Bot Management:** Prevent automated scraping of your OSINT tools.
*   **Rate Limiting:** Protect your specific API routes (especially `Hash Generator`, `Breach Checker`) from abuse, ensuring you don't exhaust your upstream API quotas (like HIBP).

---

## 5. Database Recommendations (SQLite vs PostgreSQL)

**Current:** SQLite
**Production:** PostgreSQL

*   **Why migrate?** SQLite locks the entire database during write operations. If two users submit the cybersecurity quiz or generate certificates simultaneously, one will face an error or timeout. Furthermore, platforms like Render/Railway have ephemeral file systems—meaning if the server restarts, your SQLite database file resets unless attached to persistent storage.
*   **Action Plan:** Use `SQLAlchemy`. Changing from SQLite to PostgreSQL only requires changing the `SQLALCHEMY_DATABASE_URI` environment variable from `sqlite:///data.db` to `postgresql://user:pass@host:port/dbname`.

---

## 6. File Storage (Certificates, PDFs, Metadata Reports)

Because PaaS providers (Render, Railway, Heroku) use **ephemeral file systems**, any PDF certificate or OSINT report generated and saved locally will disappear when the app restarts or scales.

*   **Solution:** Cloud Object Storage (Amazon S3, Supabase Storage, or Cloudflare R2).
*   **Implementation:** When the user generates a Certificate or a Breach Report PDF, your app should upload the file to S3 using the `boto3` library, generate a presigned URL, and return that URL to the user to download.

---

## 7. CI/CD Workflow via GitHub

Automating deployments ensures code quality and prevents "it works on my machine" errors.

1.  **Branching Strategy:** `main` (Production) and `develop` (Staging).
2.  **GitHub Actions:**
    *   **On Push to `develop`:** Run `pytest`, `flake8` (linting), and `bandit` (Python security scanner).
    *   **On Push to `main`:** Run tests. If pass, trigger a deployment webhook to Render/Railway.
3.  **No downtime:** The PaaS will build the new image in the background and hot-swap the traffic, ensuring zero downtime.

---

## 8. Environment Variables and Secrets Management

Never hardcode your Firebase JSON, Shodan API keys, VirusTotal API keys, or Flask Secret Keys.

*   **Local Development:** Use python-dotenv and a `.env` file (ensure `.env` is in `.gitignore`).
*   **Production:** Inject secrets directly into the hosting environment (Render/Railway Environment Variables dashboard).
*   **Firebase JSON:** For the CTF Firebase credentials, convert the raw JSON into a base64 string, store it as an environment variable (`FIREBASE_B64`), and decode it in Python at runtime to initialize the SDK.

---

## 9. Security Best Practices for Flask Applications

As a cybersecurity platform, your app will be targeted. Treat your own infrastructure securely.

*   **Flask Secret Key:** Generate a cryptographically strong 64-byte key. Do not use random strings like `"super-secret-key"`.
*   **CORS Configuration:** Use `flask-cors` restrictively. Only allow your exact domain.
*   **Secure Headers:** Implement the `flask-talisman` extension to automatically set HTTP security headers:
    *   `Strict-Transport-Security` (HSTS)
    *   `Content-Security-Policy` (CSP)
    *   `X-Frame-Options: DENY`
    *   `X-Content-Type-Options: nosniff`
*   **Rate-Limiting (App Level):** While Cloudflare handles edge rate limiting, use `Flask-Limiter` to protect specific endpoints (e.g., `/login`, `/api/osint_scan`) from brute force.
*   **Input Validation:** Sanitize all inputs in the OSINT/Network tools to prevent Command Injection (e.g., if a user passes `; rm -rf /` to the ping tool).

---

## 10. Future Scalability Plan

As Dark Web Leak Monitor grows:

1.  **Asynchronous Tasks (Celery + Redis):** Currently, if an OSINT scan takes 30 seconds, the HTTP request hangs. Implement Celery workers and a Redis broker. The user submits a scan -> gets a `task_id` -> the frontend polls until the background worker finishes the complex OSINT scan -> results displayed.
2.  **Microservices:** Break out the `core/` and `tools/` into a separate internal FastAPI microservice to decouple the heavy processing from the Flask frontend/dashboard.
3.  **Containerization:** Write a `Dockerfile` and `docker-compose.yml`. This standardizes the environment entirely and allows deployment to AWS ECS or a Kubernetes cluster.

---

## Execution: Step-by-Step Deployment Workflow

1.  **Prep:** Replace SQLite URIs with environment variables. Configure `flask-talisman` and `flask-limiter`.
2.  **Test:** Run `pytest` and ensure no hardcoded API keys exist in git history.
3.  **Repo Setup:** Push to a private GitHub repository.
4.  **Database Provision:** Spin up a PostgreSQL database on Render. Update the database URL locally and run `flask db upgrade` (Alembic/Flask-Migrate) to build the schema.
5.  **App Provision:** Connect Render to your GitHub repo. Set the Start Command: `gunicorn -w 4 'app:app'`.
6.  **Secrets:** Copy all variables from `.env` to the Render Dashboard.
7.  **DNS & Cloudflare:** Purchase domain. Point nameservers to Cloudflare. Create an A-record pointing to the Render application IP/CNAME.
8.  **Verify:** Turn on "Strict (SSL-Only Pull)" in Cloudflare. Test all OSINT tools and CTF modules.
