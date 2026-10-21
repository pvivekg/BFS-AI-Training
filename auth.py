"""API Authentication using JWT tokens."""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


class TokenManager:
    """Manage JWT tokens for API authentication."""

    @staticmethod
    def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT token.

        Args:
            data: Payload data to encode
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def create_access_token(user_id: str, api_key: str) -> str:
        """Create an access token for API usage.

        Args:
            user_id: User identifier
            api_key: API key identifier

        Returns:
            Access token
        """
        data = {
            "user_id": user_id,
            "api_key": api_key,
            "type": "access"
        }
        return TokenManager.create_token(data)


async def verify_api_token(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify API token from request header.

    Args:
        credentials: HTTP bearer credentials

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    return TokenManager.verify_token(token)


# Sample API Keys (in production, store securely in database)
VALID_API_KEYS = {
    "sk_test_123456": {"user_id": "user001", "name": "Test User"},
    "sk_live_789012": {"user_id": "user002", "name": "Production User"},
}


def authenticate_api_key(api_key: str) -> str:
    """Authenticate API key and return user ID.

    Args:
        api_key: API key to authenticate

    Returns:
        User ID associated with key

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return VALID_API_KEYS[api_key]["user_id"]


class RateLimiter:
    """Rate limiting for API requests."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}

    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limit.

        Args:
            user_id: User identifier

        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        if user_id not in self.requests:
            self.requests[user_id] = []

        # Remove old requests outside window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check if under limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)


# Test token generation
if __name__ == "__main__":
    # Generate test token
    test_token = TokenManager.create_access_token(
        user_id="user001",
        api_key="sk_test_123456"
    )
    print(f"Test token: {test_token}")

    # Verify token
    try:
        payload = TokenManager.verify_token(test_token)
        print(f"Token payload: {payload}")
    except HTTPException as e:
        print(f"Error: {e.detail}")
