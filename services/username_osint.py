from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests
from urllib.parse import urlparse


class UsernameOSINT:
    PLATFORMS = [
        {"name": "GitHub", "category": "Development", "url": "https://github.com/{username}", "not_found": ["not found"]},
        {"name": "GitLab", "category": "Development", "url": "https://gitlab.com/{username}", "not_found": ["404", "not found"]},
        {"name": "Bitbucket", "category": "Development", "url": "https://bitbucket.org/{username}/", "not_found": ["not found"]},
        {"name": "Stack Overflow", "category": "Development", "url": "https://stackoverflow.com/users/{username}", "not_found": ["not found"]},
        {"name": "Twitter", "category": "Social Media", "url": "https://x.com/{username}", "not_found": ["this account doesn", "not found"]},
        {"name": "Instagram", "category": "Social Media", "url": "https://www.instagram.com/{username}/", "not_found": ["sorry, this page isn't available"]},
        {"name": "Facebook", "category": "Social Media", "url": "https://www.facebook.com/{username}", "not_found": ["content isn't available"]},
        {"name": "TikTok", "category": "Social Media", "url": "https://www.tiktok.com/@{username}", "not_found": ["couldn't find this account"]},
        {"name": "Reddit", "category": "Social Media", "url": "https://www.reddit.com/user/{username}/", "not_found": ["page not found"]},
        {"name": "LinkedIn", "category": "Professional", "url": "https://www.linkedin.com/in/{username}", "not_found": ["page not found"]},
        {"name": "Medium", "category": "Content", "url": "https://medium.com/@{username}", "not_found": ["404"]},
        {"name": "DEV", "category": "Content", "url": "https://dev.to/{username}", "not_found": ["404", "not found"]},
        {"name": "YouTube", "category": "Content", "url": "https://www.youtube.com/@{username}", "not_found": ["not found"]},
        {"name": "Twitch", "category": "Gaming", "url": "https://www.twitch.tv/{username}", "not_found": ["sorry. unless you've got a time machine"]},
        {"name": "Steam", "category": "Gaming", "url": "https://steamcommunity.com/id/{username}", "not_found": ["the specified profile could not be found"]},
        {"name": "Pinterest", "category": "Creative", "url": "https://www.pinterest.com/{username}/", "not_found": ["sorry, couldn't find that page"]},
        {"name": "Behance", "category": "Creative", "url": "https://www.behance.net/{username}", "not_found": ["404"]},
        {"name": "Dribbble", "category": "Creative", "url": "https://dribbble.com/{username}", "not_found": ["404"]},
        {"name": "HackerOne", "category": "Security", "url": "https://hackerone.com/{username}", "not_found": ["404", "not found"]},
        {"name": "TryHackMe", "category": "Security", "url": "https://tryhackme.com/p/{username}", "not_found": ["404"]},
        {"name": "CodePen", "category": "Tech", "url": "https://codepen.io/{username}", "not_found": ["404"]},
        {"name": "Kaggle", "category": "Tech", "url": "https://www.kaggle.com/{username}", "not_found": ["404"]},
        {"name": "Replit", "category": "Tech", "url": "https://replit.com/@{username}", "not_found": ["404"]},
        {"name": "Flickr", "category": "Personal", "url": "https://www.flickr.com/people/{username}/", "not_found": ["not found"]},
        {"name": "WordPress", "category": "Personal", "url": "https://{username}.wordpress.com", "not_found": ["do you want to register"]},
    ]

    def __init__(self, timeout=5, max_workers=5):
        self.timeout = timeout
        self.max_workers = max_workers
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }

    def scan(self, username, platforms=None):
        username = self._normalize_username(username)
        if not username:
            return {"success": False, "error": "Username is required"}

        selected = self._select_platforms(platforms)
        if not selected:
            return {"success": False, "error": "No valid platforms selected"}

        found_profiles = []
        checked_profiles = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._check_platform, username, platform): platform for platform in selected}
            for future in as_completed(futures):
                result = future.result()
                checked_profiles.append(result)
                if result.get("found"):
                    found_profiles.append(result)

        total_checked = len(selected)
        total_found = len(found_profiles)
        by_category = {}
        for profile in found_profiles:
            category = profile.get("category", "Other")
            by_category.setdefault(category, []).append(profile)

        # Stable ordering for UI consistency.
        found_profiles.sort(key=lambda p: (p.get("category", ""), p.get("platform", "")))
        checked_profiles.sort(key=lambda p: p.get("platform", ""))

        return {
            "success": True,
            "username": username,
            "total_checked": total_checked,
            "total_found": total_found,
            "found_profiles": found_profiles,
            "checked_profiles": checked_profiles,
            "by_category": by_category,
            "platforms": [p["name"] for p in selected],
        }

    def _normalize_username(self, raw_value):
        value = str(raw_value or "").strip()
        if not value:
            return ""

        if value.startswith("@"):
            value = value[1:]

        if "://" in value:
            try:
                parsed = urlparse(value)
                if parsed.netloc:
                    path = (parsed.path or "").strip("/")
                    if path:
                        # Handle URLs like /@username or /user/username
                        parts = [p for p in path.split("/") if p]
                        if parts:
                            candidate = parts[-1]
                            if candidate.startswith("@"):
                                candidate = candidate[1:]
                            return candidate.strip()
            except Exception:
                pass

        return value

    def _select_platforms(self, platforms):
        if not platforms:
            return list(self.PLATFORMS)

        wanted = {str(p).strip().lower() for p in platforms}
        return [p for p in self.PLATFORMS if p["name"].lower() in wanted]

    def _check_platform(self, username, platform):
        url = platform["url"].format(username=username)
        started = time.perf_counter()
        status_code = None
        error = None
        found = False

        try:
            # Use GET for better reliability across anti-bot behavior.
            resp = requests.get(
                url,
                headers=self._headers,
                timeout=self.timeout,
                allow_redirects=True,
            )
            status_code = resp.status_code

            if status_code == 200:
                body = (resp.text or "").lower()
                not_found_markers = [m.lower() for m in platform.get("not_found", [])]
                found = not any(marker in body for marker in not_found_markers)
            elif status_code in (301, 302):
                found = True
            else:
                found = False
        except requests.RequestException as exc:
            error = str(exc)
            found = False

        elapsed = round(time.perf_counter() - started, 2)
        return {
            "platform": platform["name"],
            "category": platform["category"],
            "url": url,
            "found": found,
            "status_code": status_code,
            "response_time": elapsed,
            "error": error,
        }

    def get_available_platforms(self):
        return [{"name": p["name"], "category": p["category"]} for p in self.PLATFORMS]

    def get_categories(self):
        return sorted({p["category"] for p in self.PLATFORMS})
