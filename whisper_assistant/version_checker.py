"""
Version checker for Carl's Whisper Assistant
"""
import json
import time
import urllib.request
from config import APP_VERSION, GITHUB_REPO, check_for_updates

class VersionChecker:
    """Checks for new versions of the application"""
    
    def __init__(self):
        self.last_check_time = 0
        self.check_interval = 86400  # 24 hours in seconds
    
    def should_check(self):
        """Determine if we should check for updates"""
        current_time = time.time()
        if current_time - self.last_check_time > self.check_interval:
            return True
        return False
    
    def check_now(self):
        """Force an update check"""
        self.last_check_time = time.time()
        return check_for_updates()
    
    def get_changelog(self, version):
        """Get the changelog for a specific version"""
        try:
            with urllib.request.urlopen(f"{GITHUB_REPO}/{version}") as response:
                data = json.loads(response.read().decode())
                return data.get('body', 'No release notes available')
        except:
            return "Unable to fetch changelog"

def get_checker():
    """Get a singleton instance of the version checker"""
    global _checker
    if '_checker' not in globals():
        _checker = VersionChecker()
    return _checker
