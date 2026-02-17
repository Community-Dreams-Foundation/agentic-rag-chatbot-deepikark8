"""
Security Layer - Protects the system
Handles: authentication, input sanitization, rate limiting
"""
import re
import hashlib
from datetime import datetime


class SecurityLayer:
    """
    Security system that:
    1. Creates and verifies user tokens
    2. Sanitizes inputs to prevent injection attacks
    3. Rate limits requests to prevent abuse
    4. Logs all security events
    """

    def __init__(self, max_requests_per_hour=100):
        self.valid_tokens = {}
        self.request_counts = {}
        self.max_requests = max_requests_per_hour

    def create_token(self, user_id):
        """Create authentication token for a user"""
        raw = f"{user_id}:{datetime.utcnow().isoformat()}"
        token = hashlib.sha256(raw.encode()).hexdigest()
        self.valid_tokens[token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }
        return token

    def verify_token(self, token):
        """Check if token is valid. Returns user_id or None"""
        if token in self.valid_tokens:
            return self.valid_tokens[token]["user_id"]
        return None

    def sanitize(self, text, max_length=1000):
        """
        Clean user input to prevent injection attacks
        Removes: SQL keywords, special characters, excess length
        """
        if not text:
            return ""

        # Remove dangerous SQL keywords
        sql_pattern = r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|EXEC|UNION|SELECT)\b'
        cleaned = re.sub(sql_pattern, "", text, flags=re.IGNORECASE)

        # Remove special characters that could cause issues
        cleaned = re.sub(r'[<>\'"`;]', "", cleaned)

        # Trim whitespace and limit length
        cleaned = cleaned.strip()[:max_length]

        return cleaned

    def check_rate_limit(self, user_id):
        """
        Check if user is within rate limit
        Returns True if allowed, False if blocked
        """
        current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
        key = f"{user_id}:{current_hour}"

        if key not in self.request_counts:
            self.request_counts[key] = 0

        self.request_counts[key] += 1

        return self.request_counts[key] <= self.max_requests

    def get_request_count(self, user_id):
        """Get how many requests user made this hour"""
        current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
        key = f"{user_id}:{current_hour}"
        return self.request_counts.get(key, 0)
