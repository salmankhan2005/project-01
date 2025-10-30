import re
import secrets
import hashlib
import hmac
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import ipaddress
import time
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration and constants"""
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = False
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    LOGIN_RATE_LIMIT = 5      # login attempts per minute
    
    # Token settings
    JWT_ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': \"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'\",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format and security"""
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email too long"
        
        # Basic email regex (more permissive than strict RFC)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.{2,}',  # Multiple consecutive dots
            r'^\.|\.$',  # Starting or ending with dot
            r'@.*@',    # Multiple @ symbols
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email):
                return False, "Invalid email format"
        
        return True, "Valid email"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
        
        if len(password) > SecurityConfig.MAX_PASSWORD_LENGTH:
            return False, f"Password must be at most {SecurityConfig.MAX_PASSWORD_LENGTH} characters"
        
        # Check character requirements
        if SecurityConfig.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if SecurityConfig.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if SecurityConfig.REQUIRE_DIGITS and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{3,}',  # 4+ repeated characters
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                return False, "Password contains weak patterns"
        
        # Check against common passwords (simplified check)
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, "Password is strong"
    
    @staticmethod
    def sanitize_input(data: Any, max_length: int = 1000) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(data, str):
            data = str(data) if data is not None else ""
        
        # Limit length
        data = data[:max_length]
        
        # Remove null bytes
        data = data.replace('\\x00', '')\n        \n        # HTML encode dangerous characters\n        html_escape_table = {\n            '&': '&amp;',\n            '<': '&lt;',\n            '>': '&gt;',\n            '\"': '&quot;',\n            \"'\": '&#x27;',\n            '/': '&#x2F;'\n        }\n        \n        for char, escape in html_escape_table.items():\n            data = data.replace(char, escape)\n        \n        # Remove potentially dangerous protocols\n        dangerous_protocols = [\n            'javascript:', 'data:', 'vbscript:', 'file:', 'about:',\n            'chrome:', 'chrome-extension:', 'moz-extension:'\n        ]\n        \n        data_lower = data.lower()\n        for protocol in dangerous_protocols:\n            if protocol in data_lower:\n                data = data.replace(protocol, '')\n                data = data.replace(protocol.upper(), '')\n        \n        # Remove script tags and event handlers\n        script_patterns = [\n            r'<script[^>]*>.*?</script>',\n            r'on\\w+\\s*=',\n            r'expression\\s*\\(',\n            r'url\\s*\\(',\n            r'@import'\n        ]\n        \n        for pattern in script_patterns:\n            data = re.sub(pattern, '', data, flags=re.IGNORECASE | re.DOTALL)\n        \n        return data.strip()\n    \n    @staticmethod\n    def validate_json_input(data: Dict[str, Any], required_fields: List[str] = None, \n                          max_depth: int = 10) -> Tuple[bool, str]:\n        \"\"\"Validate JSON input structure and content\"\"\"\n        if not isinstance(data, dict):\n            return False, \"Input must be a JSON object\"\n        \n        # Check depth to prevent deeply nested attacks\n        def check_depth(obj, current_depth=0):\n            if current_depth > max_depth:\n                return False\n            if isinstance(obj, dict):\n                return all(check_depth(v, current_depth + 1) for v in obj.values())\n            elif isinstance(obj, list):\n                return all(check_depth(item, current_depth + 1) for item in obj)\n            return True\n        \n        if not check_depth(data):\n            return False, \"Input structure too deeply nested\"\n        \n        # Check required fields\n        if required_fields:\n            missing_fields = [field for field in required_fields if field not in data]\n            if missing_fields:\n                return False, f\"Missing required fields: {', '.join(missing_fields)}\"\n        \n        # Check for suspicious keys\n        suspicious_keys = ['__proto__', 'constructor', 'prototype', 'eval', 'function']\n        for key in data.keys():\n            if any(suspicious in str(key).lower() for suspicious in suspicious_keys):\n                return False, f\"Suspicious key detected: {key}\"\n        \n        return True, \"Valid input\"\n\nclass RateLimiter:\n    \"\"\"Advanced rate limiting with multiple strategies\"\"\"\n    \n    def __init__(self):\n        self.requests = defaultdict(list)\n        self.blocked_ips = defaultdict(datetime)\n        self.lock = threading.RLock()\n    \n    def is_allowed(self, identifier: str, limit: int = SecurityConfig.DEFAULT_RATE_LIMIT, \n                   window_seconds: int = 60, block_duration: int = 300) -> Tuple[bool, Dict[str, Any]]:\n        \"\"\"Check if request is allowed with detailed response\"\"\"\n        current_time = time.time()\n        \n        with self.lock:\n            # Check if IP is currently blocked\n            if identifier in self.blocked_ips:\n                if datetime.now() < self.blocked_ips[identifier]:\n                    return False, {\n                        'blocked': True,\n                        'reason': 'IP temporarily blocked',\n                        'retry_after': (self.blocked_ips[identifier] - datetime.now()).seconds\n                    }\n                else:\n                    del self.blocked_ips[identifier]\n            \n            # Clean old requests\n            if identifier in self.requests:\n                self.requests[identifier] = [\n                    req_time for req_time in self.requests[identifier]\n                    if current_time - req_time < window_seconds\n                ]\n            \n            # Check rate limit\n            request_count = len(self.requests[identifier])\n            if request_count >= limit:\n                # Block IP for repeated violations\n                self.blocked_ips[identifier] = datetime.now() + timedelta(seconds=block_duration)\n                return False, {\n                    'blocked': False,\n                    'rate_limited': True,\n                    'reason': 'Rate limit exceeded',\n                    'requests_made': request_count,\n                    'limit': limit,\n                    'window_seconds': window_seconds\n                }\n            \n            # Add current request\n            self.requests[identifier].append(current_time)\n            \n            return True, {\n                'allowed': True,\n                'requests_made': request_count + 1,\n                'limit': limit,\n                'remaining': limit - request_count - 1\n            }\n    \n    def get_stats(self, identifier: str) -> Dict[str, Any]:\n        \"\"\"Get rate limiting stats for identifier\"\"\"\n        with self.lock:\n            current_time = time.time()\n            recent_requests = [\n                req_time for req_time in self.requests.get(identifier, [])\n                if current_time - req_time < 60\n            ]\n            \n            return {\n                'recent_requests': len(recent_requests),\n                'is_blocked': identifier in self.blocked_ips and datetime.now() < self.blocked_ips[identifier],\n                'total_tracked_ips': len(self.requests)\n            }\n\nclass TokenManager:\n    \"\"\"Secure JWT token management\"\"\"\n    \n    def __init__(self, secret_key: str, algorithm: str = SecurityConfig.JWT_ALGORITHM):\n        if len(secret_key) < 32:\n            raise ValueError(\"Secret key must be at least 32 characters long\")\n        self.secret_key = secret_key\n        self.algorithm = algorithm\n        self.blacklisted_tokens = set()\n        self.token_lock = threading.RLock()\n    \n    def generate_token(self, payload: Dict[str, Any], expires_hours: int = SecurityConfig.ACCESS_TOKEN_EXPIRE_HOURS) -> str:\n        \"\"\"Generate a secure JWT token\"\"\"\n        try:\n            # Add standard claims\n            now = datetime.utcnow()\n            payload.update({\n                'iat': now,  # Issued at\n                'exp': now + timedelta(hours=expires_hours),  # Expiration\n                'jti': secrets.token_urlsafe(16),  # JWT ID for blacklisting\n            })\n            \n            return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)\n        except Exception as e:\n            logger.error(f\"Token generation error: {e}\")\n            raise\n    \n    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:\n        \"\"\"Verify and decode JWT token\"\"\"\n        try:\n            # Check if token is blacklisted\n            with self.token_lock:\n                if token in self.blacklisted_tokens:\n                    return False, None, \"Token has been revoked\"\n            \n            # Decode and verify token\n            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])\n            \n            # Additional security checks\n            required_claims = ['iat', 'exp', 'jti']\n            for claim in required_claims:\n                if claim not in payload:\n                    return False, None, f\"Missing required claim: {claim}\"\n            \n            return True, payload, \"Token is valid\"\n            \n        except jwt.ExpiredSignatureError:\n            return False, None, \"Token has expired\"\n        except jwt.InvalidTokenError as e:\n            return False, None, f\"Invalid token: {str(e)}\"\n        except Exception as e:\n            logger.error(f\"Token verification error: {e}\")\n            return False, None, \"Token verification failed\"\n    \n    def blacklist_token(self, token: str) -> bool:\n        \"\"\"Add token to blacklist\"\"\"\n        try:\n            # Extract JTI from token without verification (for logout)\n            unverified_payload = jwt.decode(token, options={\"verify_signature\": False})\n            jti = unverified_payload.get('jti')\n            \n            if jti:\n                with self.token_lock:\n                    self.blacklisted_tokens.add(token)\n                return True\n            return False\n        except Exception as e:\n            logger.error(f\"Token blacklisting error: {e}\")\n            return False\n    \n    def cleanup_expired_tokens(self):\n        \"\"\"Remove expired tokens from blacklist\"\"\"\n        with self.token_lock:\n            valid_tokens = set()\n            for token in self.blacklisted_tokens:\n                try:\n                    jwt.decode(token, self.secret_key, algorithms=[self.algorithm])\n                    valid_tokens.add(token)  # Token is still valid, keep in blacklist\n                except jwt.ExpiredSignatureError:\n                    pass  # Token expired, remove from blacklist\n                except:\n                    pass  # Invalid token, remove from blacklist\n            \n            removed_count = len(self.blacklisted_tokens) - len(valid_tokens)\n            self.blacklisted_tokens = valid_tokens\n            \n            if removed_count > 0:\n                logger.info(f\"Cleaned up {removed_count} expired tokens from blacklist\")\n\nclass PasswordManager:\n    \"\"\"Secure password hashing and verification\"\"\"\n    \n    @staticmethod\n    def hash_password(password: str) -> str:\n        \"\"\"Hash password using secure method\"\"\"\n        return generate_password_hash(\n            password, \n            method='pbkdf2:sha256:100000',  # 100,000 iterations\n            salt_length=16\n        )\n    \n    @staticmethod\n    def verify_password(password: str, password_hash: str) -> bool:\n        \"\"\"Verify password against hash\"\"\"\n        try:\n            return check_password_hash(password_hash, password)\n        except Exception as e:\n            logger.error(f\"Password verification error: {e}\")\n            return False\n    \n    @staticmethod\n    def generate_secure_password(length: int = 16) -> str:\n        \"\"\"Generate a cryptographically secure password\"\"\"\n        if length < 8:\n            length = 8\n        if length > 128:\n            length = 128\n        \n        # Ensure password contains all required character types\n        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\n        lowercase = 'abcdefghijklmnopqrstuvwxyz'\n        digits = '0123456789'\n        special = '!@#$%^&*()_+-=[]{}|;:,.<>?'\n        \n        # Start with one character from each required type\n        password = [\n            secrets.choice(uppercase),\n            secrets.choice(lowercase),\n            secrets.choice(digits)\n        ]\n        \n        # Fill the rest randomly\n        all_chars = uppercase + lowercase + digits + special\n        for _ in range(length - 3):\n            password.append(secrets.choice(all_chars))\n        \n        # Shuffle the password\n        secrets.SystemRandom().shuffle(password)\n        return ''.join(password)\n\nclass IPSecurityManager:\n    \"\"\"IP-based security management\"\"\"\n    \n    def __init__(self):\n        self.trusted_networks = [\n            ipaddress.ip_network('127.0.0.0/8'),    # Localhost\n            ipaddress.ip_network('10.0.0.0/8'),     # Private network\n            ipaddress.ip_network('172.16.0.0/12'),  # Private network\n            ipaddress.ip_network('192.168.0.0/16'), # Private network\n        ]\n        self.blocked_ips = set()\n        self.suspicious_ips = defaultdict(int)\n    \n    def is_ip_allowed(self, ip_address: str) -> Tuple[bool, str]:\n        \"\"\"Check if IP address is allowed\"\"\"\n        try:\n            ip = ipaddress.ip_address(ip_address)\n            \n            # Check if IP is explicitly blocked\n            if ip_address in self.blocked_ips:\n                return False, \"IP address is blocked\"\n            \n            # Check if IP is suspicious\n            if self.suspicious_ips[ip_address] > 10:\n                return False, \"IP address flagged as suspicious\"\n            \n            return True, \"IP address is allowed\"\n            \n        except ValueError:\n            return False, \"Invalid IP address format\"\n    \n    def is_trusted_network(self, ip_address: str) -> bool:\n        \"\"\"Check if IP is from trusted network\"\"\"\n        try:\n            ip = ipaddress.ip_address(ip_address)\n            return any(ip in network for network in self.trusted_networks)\n        except ValueError:\n            return False\n    \n    def flag_suspicious_activity(self, ip_address: str):\n        \"\"\"Flag IP for suspicious activity\"\"\"\n        self.suspicious_ips[ip_address] += 1\n        if self.suspicious_ips[ip_address] > 20:\n            self.blocked_ips.add(ip_address)\n            logger.warning(f\"IP {ip_address} blocked due to suspicious activity\")\n\n# Global instances\nrate_limiter = RateLimiter()\nip_security = IPSecurityManager()\n\n# Security decorators\ndef require_rate_limit(limit: int = SecurityConfig.DEFAULT_RATE_LIMIT, window: int = 60):\n    \"\"\"Decorator to enforce rate limiting\"\"\"\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            from flask import request, jsonify\n            \n            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)\n            if client_ip:\n                client_ip = client_ip.split(',')[0].strip()\n            \n            allowed, info = rate_limiter.is_allowed(client_ip, limit, window)\n            if not allowed:\n                return jsonify({\n                    'error': 'Rate limit exceeded',\n                    'details': info\n                }), 429\n            \n            return func(*args, **kwargs)\n        return wrapper\n    return decorator\n\ndef require_ip_whitelist():\n    \"\"\"Decorator to require IP whitelist\"\"\"\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            from flask import request, jsonify\n            \n            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)\n            if client_ip:\n                client_ip = client_ip.split(',')[0].strip()\n            \n            allowed, reason = ip_security.is_ip_allowed(client_ip)\n            if not allowed:\n                ip_security.flag_suspicious_activity(client_ip)\n                return jsonify({'error': reason}), 403\n            \n            return func(*args, **kwargs)\n        return wrapper\n    return decorator\n\ndef add_security_headers():\n    \"\"\"Decorator to add security headers\"\"\"\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            from flask import make_response\n            \n            response = make_response(func(*args, **kwargs))\n            \n            for header, value in SecurityConfig.SECURITY_HEADERS.items():\n                response.headers[header] = value\n            \n            return response\n        return wrapper\n    return decorator