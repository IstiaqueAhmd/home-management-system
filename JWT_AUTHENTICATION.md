# JWT Authentication Implementation

This document describes the enhanced JWT authentication system implemented for the Home Management System.

## Features

### Core Authentication Features
- **JWT Access Tokens**: Short-lived tokens (30 minutes default) for API access
- **JWT Refresh Tokens**: Longer-lived tokens (7 days default) for token renewal
- **Token Blacklisting**: Support for token revocation on logout
- **Password Strength Validation**: Enforces strong password requirements
- **Secure Cookie Storage**: HTTPOnly, Secure, SameSite cookie settings
- **Automatic Token Refresh**: API endpoint for refreshing expired access tokens

### Security Features
- **Bcrypt Password Hashing**: Configurable rounds (default: 12)
- **Secret Key Management**: Environment-based secret key configuration
- **Token Expiration**: Configurable token lifetimes
- **CORS Protection**: Configurable allowed origins
- **Trusted Host Middleware**: Protection against host header attacks (production)
- **GZip Compression**: Response compression for better performance

## API Endpoints

### Authentication Endpoints

#### POST `/token`
OAuth2-compatible token endpoint for programmatic access.
```json
{
  "username": "string",
  "password": "string"
}
```
Response:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/refresh`
Refresh access token using refresh token.
```json
{
  "refresh_token": "string"
}
```

#### POST `/logout`
Revoke tokens and logout (both API and web).

#### POST `/login`
Web form login (redirects to dashboard).

### User Management Endpoints

#### GET `/me`
Get current user information (requires authentication).

#### POST `/change-password`
Change user password (requires authentication).
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

#### GET `/token-info`
Get information about the current token.

## Environment Variables

```bash
# Database
POSTGRES_URL=postgresql://user:pass@host:port/db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=strict

# CORS & Hosts
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
ALLOWED_HOSTS=localhost,yourdomain.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

## Token Usage

### For Web Applications
- Tokens are stored in HTTPOnly cookies automatically
- No additional headers required for authenticated requests
- Automatic token refresh handling

### For API Clients
- Include access token in Authorization header: `Bearer <token>`
- Use refresh token endpoint when access token expires
- Store refresh token securely

## Security Best Practices

1. **Environment Variables**: Never hardcode secret keys
2. **HTTPS Only**: Use secure cookies in production
3. **Token Rotation**: Regularly refresh tokens
4. **Logout Handling**: Always revoke tokens on logout
5. **Password Policy**: Enforce strong password requirements
6. **Rate Limiting**: Implement rate limiting for auth endpoints
7. **Monitoring**: Log authentication events for security monitoring

## Development vs Production

### Development
- Docs endpoints enabled (`/docs`, `/redoc`)
- Less strict security settings
- Detailed error messages

### Production
- Docs endpoints disabled
- Trusted host middleware enabled
- Secure cookie settings enforced
- Error messages sanitized

## Error Handling

All authentication errors return appropriate HTTP status codes:
- `401 Unauthorized`: Invalid or expired tokens
- `400 Bad Request`: Invalid input (weak passwords, etc.)
- `403 Forbidden`: Valid token but insufficient permissions
- `500 Internal Server Error`: Server-side authentication errors

## Token Lifecycle

1. **Login**: User provides credentials → Receive access + refresh tokens
2. **API Calls**: Use access token for authenticated requests
3. **Token Expiry**: Access token expires → Use refresh token to get new access token
4. **Logout**: Revoke both tokens → Redirect to login
5. **Security Event**: Automatic token revocation if suspicious activity detected

## Implementation Notes

- Token blacklisting is currently in-memory (use Redis in production)
- Password hashing uses bcrypt with configurable rounds
- JWT tokens include standard claims (exp, iat, jti, sub)
- Cookie security settings are environment-configurable
- All sensitive operations are logged for audit trails