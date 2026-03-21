"""
Username OSINT Scanner Module
=============================
Checks if a username exists across multiple social platforms and websites.
Uses async requests for fast parallel checking.

Privacy: Only checks public profile URLs, no data is stored.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class ProfileResult:
    """Represents a found profile on a platform."""
    platform: str
    url: str
    exists: bool
    category: str
    response_time: float
    error: Optional[str] = None


class UsernameOSINT:
    """
    OSINT scanner for checking username availability across platforms.
    
    Uses pattern-based detection to minimize false positives.
    Respects rate limits and uses appropriate timeouts.
    """
    
    # Platform configurations: (name, url_template, category, error_patterns)
    PLATFORMS = {
        # Social Media
        'Twitter/X': {
            'url': 'https://twitter.com/{}',
            'category': 'Social Media',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Instagram': {
            'url': 'https://www.instagram.com/{}/',
            'category': 'Social Media',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'TikTok': {
            'url': 'https://www.tiktok.com/@{}',
            'category': 'Social Media',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Facebook': {
            'url': 'https://www.facebook.com/{}',
            'category': 'Social Media',
            'error_type': 'content',
            'not_found_pattern': 'page isn\'t available'
        },
        'LinkedIn': {
            'url': 'https://www.linkedin.com/in/{}',
            'category': 'Professional',
            'error_type': 'status_code',
            'not_found_codes': [404, 999]
        },
        
        # Developer Platforms
        'GitHub': {
            'url': 'https://github.com/{}',
            'category': 'Development',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'GitLab': {
            'url': 'https://gitlab.com/{}',
            'category': 'Development',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Bitbucket': {
            'url': 'https://bitbucket.org/{}/',
            'category': 'Development',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Stack Overflow': {
            'url': 'https://stackoverflow.com/users/{}',
            'category': 'Development',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Dev.to': {
            'url': 'https://dev.to/{}',
            'category': 'Development',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        
        # Content Platforms
        'Medium': {
            'url': 'https://medium.com/@{}',
            'category': 'Content',
            'error_type': 'status_code',
            'not_found_codes': [404, 410]
        },
        'Reddit': {
            'url': 'https://www.reddit.com/user/{}',
            'category': 'Social Media',
            'error_type': 'content',
            'not_found_pattern': 'page not found'
        },
        'Pinterest': {
            'url': 'https://www.pinterest.com/{}/',
            'category': 'Social Media',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Twitch': {
            'url': 'https://www.twitch.tv/{}',
            'category': 'Gaming',
            'error_type': 'content',
            'not_found_pattern': 'channel has been suspended'
        },
        'YouTube': {
            'url': 'https://www.youtube.com/@{}',
            'category': 'Content',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        
        # Professional/Business
        'Behance': {
            'url': 'https://www.behance.net/{}',
            'category': 'Creative',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Dribbble': {
            'url': 'https://dribbble.com/{}',
            'category': 'Creative',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        
        # Gaming
        'Steam': {
            'url': 'https://steamcommunity.com/id/{}',
            'category': 'Gaming',
            'error_type': 'content',
            'not_found_pattern': 'The specified profile could not be found'
        },
        
        # Tech Forums
        'Hacker News': {
            'url': 'https://news.ycombinator.com/user?id={}',
            'category': 'Tech',
            'error_type': 'content',
            'not_found_pattern': 'No such user'
        },
        
        # Misc
        'Keybase': {
            'url': 'https://keybase.io/{}',
            'category': 'Security',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'About.me': {
            'url': 'https://about.me/{}',
            'category': 'Personal',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
        'Gravatar': {
            'url': 'https://en.gravatar.com/{}',
            'category': 'Personal',
            'error_type': 'status_code',
            'not_found_codes': [404]
        },
    }
    
    def __init__(self, timeout: int = 10, max_workers: int = 10):
        """
        Initialize the OSINT scanner.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum concurrent requests
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 2:
            return False, "Username must be at least 2 characters"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        # Allow alphanumeric, underscore, hyphen, period
        if not re.match(r'^[\w\-\.]+$', username):
            return False, "Username contains invalid characters"
        
        return True, ""
    
    def _check_platform(self, username: str, platform: str, config: dict) -> ProfileResult:
        """
        Check if username exists on a specific platform.
        
        Args:
            username: Username to check
            platform: Platform name
            config: Platform configuration
            
        Returns:
            ProfileResult with check results
        """
        url = config['url'].format(username)
        start_time = datetime.now()
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Determine if profile exists based on error type
            exists = True
            
            if config['error_type'] == 'status_code':
                if response.status_code in config.get('not_found_codes', [404]):
                    exists = False
                elif response.status_code >= 400:
                    exists = False
            
            elif config['error_type'] == 'content':
                pattern = config.get('not_found_pattern', '')
                if pattern and pattern.lower() in response.text.lower():
                    exists = False
            
            return ProfileResult(
                platform=platform,
                url=url,
                exists=exists,
                category=config['category'],
                response_time=response_time
            )
            
        except requests.Timeout:
            return ProfileResult(
                platform=platform,
                url=url,
                exists=False,
                category=config['category'],
                response_time=self.timeout,
                error="Request timed out"
            )
        except requests.RequestException as e:
            return ProfileResult(
                platform=platform,
                url=url,
                exists=False,
                category=config['category'],
                response_time=0,
                error=str(e)[:100]
            )
    
    def scan(self, username: str, platforms: Optional[List[str]] = None) -> Dict:
        """
        Scan multiple platforms for a username.
        
        Args:
            username: Username to search for
            platforms: Optional list of specific platforms to check
            
        Returns:
            Dictionary with scan results
        """
        # Validate username
        is_valid, error = self.validate_username(username)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'username': username
            }
        
        # Determine which platforms to check
        platforms_to_check = self.PLATFORMS
        if platforms:
            platforms_to_check = {
                k: v for k, v in self.PLATFORMS.items() 
                if k in platforms
            }
        
        results = []
        found_profiles = []
        
        # Use thread pool for parallel requests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._check_platform, username, platform, config): platform
                for platform, config in platforms_to_check.items()
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if result.exists:
                    found_profiles.append(result)
        
        # Sort results by platform name
        results.sort(key=lambda x: x.platform)
        found_profiles.sort(key=lambda x: x.platform)
        
        # Group by category
        categories = {}
        for profile in found_profiles:
            if profile.category not in categories:
                categories[profile.category] = []
            categories[profile.category].append({
                'platform': profile.platform,
                'url': profile.url
            })
        
        return {
            'success': True,
            'username': username,
            'total_checked': len(results),
            'total_found': len(found_profiles),
            'found_profiles': [
                {
                    'platform': p.platform,
                    'url': p.url,
                    'category': p.category,
                    'response_time': round(p.response_time, 2)
                }
                for p in found_profiles
            ],
            'by_category': categories,
            'all_results': [
                {
                    'platform': r.platform,
                    'url': r.url,
                    'exists': r.exists,
                    'category': r.category,
                    'error': r.error
                }
                for r in results
            ],
            'scan_time': datetime.now().isoformat()
        }
    
    def get_available_platforms(self) -> List[Dict]:
        """Get list of available platforms and their categories."""
        platforms = []
        for name, config in self.PLATFORMS.items():
            platforms.append({
                'name': name,
                'category': config['category'],
                'url_template': config['url']
            })
        return sorted(platforms, key=lambda x: (x['category'], x['name']))
    
    def get_categories(self) -> List[str]:
        """Get unique list of platform categories."""
        categories = set(config['category'] for config in self.PLATFORMS.values())
        return sorted(list(categories))


# Example usage and testing
if __name__ == "__main__":
    scanner = UsernameOSINT(timeout=8, max_workers=15)
    
    # Test with a common username
    print("=" * 60)
    print("Username OSINT Scanner - Test")
    print("=" * 60)
    
    test_username = "johndoe"
    print(f"\nScanning for username: {test_username}")
    print("-" * 40)
    
    results = scanner.scan(test_username)
    
    if results['success']:
        print(f"Platforms checked: {results['total_checked']}")
        print(f"Profiles found: {results['total_found']}")
        print("\nFound profiles:")
        for profile in results['found_profiles']:
            print(f"  [{profile['category']}] {profile['platform']}: {profile['url']}")
    else:
        print(f"Error: {results['error']}")
