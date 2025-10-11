import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class TokenBlacklist:
    """Simple in-memory token blacklist. In production, use Redis or database."""
    def __init__(self):
        self._blacklisted_tokens = set()
    
    def add_token(self, token: str):
        """Add token to blacklist"""
        self._blacklisted_tokens.add(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return token in self._blacklisted_tokens
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from blacklist (called periodically)"""
        # In production, implement proper cleanup logic
        pass

class AuthManager:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key or self.secret_key == "fallback-secret-key":
            logger.warning("SECRET_KEY not set or using fallback. Generating random key for development.")
            self.secret_key = secrets.token_urlsafe(32)
        
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
        
        # Configure bcrypt with higher rounds for production
        bcrypt_rounds = int(os.getenv("BCRYPT_ROUNDS", 12))
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], 
            deprecated="auto",
            bcrypt__rounds=bcrypt_rounds
        )
        
        # Token blacklist for logout functionality
        self.token_blacklist = TokenBlacklist()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password for storing"""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        # Use timezone-aware datetime
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        # Add standard JWT claims
        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for token revocation
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise ValueError("Failed to create access token")
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise ValueError("Failed to create refresh token")
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        if not token:
            raise JWTError("Token is required")
        
        # Check if token is blacklisted
        if self.token_blacklist.is_blacklisted(token):
            raise JWTError("Token has been revoked")
        
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise JWTError(f"Invalid token type. Expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JWTError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise JWTError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise JWTError("Token verification failed")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create a new access token using a refresh token"""
        try:
            payload = self.verify_token(refresh_token, token_type="refresh")
            username = payload.get("sub")
            
            if not username:
                raise JWTError("Invalid refresh token payload")
            
            # Create new access token
            new_access_token = self.create_access_token(data={"sub": username})
            return new_access_token
            
        except JWTError:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise JWTError("Failed to refresh token")
    
    def revoke_token(self, token: str):
        """Add token to blacklist (logout functionality)"""
        try:
            # Verify token first to ensure it's valid before blacklisting
            payload = self.verify_token(token)
            self.token_blacklist.add_token(token)
            logger.info(f"Token revoked for user: {payload.get('sub')}")
        except JWTError:
            # Token is already invalid, no need to blacklist
            pass
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get information about a token without full verification"""
        try:
            # Decode without verification to get basic info
            payload = jwt.decode(
                token, 
                options={"verify_signature": False, "verify_exp": False}
            )
            return {
                "username": payload.get("sub"),
                "expires_at": datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc),
                "token_type": payload.get("type", "unknown"),
                "jti": payload.get("jti")
            }
        except Exception as e:
            logger.error(f"Token info extraction error: {e}")
            return {}
