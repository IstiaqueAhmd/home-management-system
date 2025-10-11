# JWT Authentication Setup

This project now includes a comprehensive JWT authentication system with enhanced security features.

## Quick Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your settings
   # IMPORTANT: Change the SECRET_KEY for production!
   ```

3. **Generate a Secure Secret Key**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

4. **Run the Application**
   ```bash
   cd src
   python main.py
   ```

## Testing Authentication

### Automated Tests

**PowerShell (Windows):**
```powershell
.\test_jwt_auth.ps1
```

**Bash (Linux/Mac):**
```bash
chmod +x test_jwt_auth.sh
./test_jwt_auth.sh
```

**Python (Cross-platform):**
```bash
pip install requests
python test_jwt_auth.py
```

### Manual Testing

1. **Register a user:**
   ```bash
   curl -X POST http://localhost:8000/register \
     -d "username=testuser" \
     -d "email=test@example.com" \
     -d "full_name=Test User" \
     -d "password=TestPass123!"
   ```

2. **Get tokens:**
   ```bash
   curl -X POST http://localhost:8000/token \
     -d "username=testuser" \
     -d "password=TestPass123!"
   ```

3. **Use access token:**
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://localhost:8000/me
   ```

## Authentication Features

### ✅ Implemented Features

- **JWT Access & Refresh Tokens**: Secure token-based authentication
- **Password Strength Validation**: Enforces strong password requirements
- **Secure Cookie Storage**: HTTPOnly, Secure, SameSite settings
- **Token Blacklisting**: Support for logout and token revocation
- **CORS Protection**: Configurable allowed origins
- **Password Hashing**: Bcrypt with configurable rounds
- **Automatic Token Refresh**: API endpoint for token renewal
- **Environment-based Configuration**: Secure secret key management

### 🔒 Security Features

- **Production Security**: Trusted host middleware, secure cookies
- **Rate Limiting Ready**: Structure prepared for rate limiting
- **Audit Logging**: Authentication events logged
- **Error Handling**: Secure error messages, no information leakage
- **Token Expiration**: Configurable short and long-term token lifetimes

### 📋 Password Requirements

- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

## API Endpoints

### Authentication
- `POST /token` - OAuth2 compatible login
- `POST /refresh` - Refresh access token
- `POST /logout` - Logout and revoke tokens
- `GET /me` - Get current user info
- `POST /change-password` - Change password

### Web Authentication
- `GET /login` - Login page
- `POST /login` - Web login form
- `GET /register` - Registration page
- `POST /register` - Web registration form
- `GET /dashboard` - Protected dashboard

## Environment Variables

```bash
# Required
POSTGRES_URL=postgresql://user:pass@host:port/database
SECRET_KEY=your-super-secret-key-minimum-32-characters

# Optional (with defaults)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
ENVIRONMENT=production
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Development vs Production

### Development Settings
- Documentation endpoints enabled (`/docs`, `/redoc`)
- Detailed error messages
- Less strict security (but still secure)

### Production Settings
- Documentation endpoints disabled
- Sanitized error messages
- Enhanced security middleware
- Secure cookie enforcement

## Troubleshooting

### Common Issues

1. **"SECRET_KEY not set"**
   - Set a strong SECRET_KEY in your .env file
   - Use at least 32 characters

2. **"Invalid token"**
   - Token may be expired
   - Use refresh token to get new access token
   - Check token format (should be `Bearer <token>`)

3. **"CORS errors"**
   - Add your frontend URL to ALLOWED_ORIGINS
   - Check protocol (http vs https)

4. **Database connection failed**
   - Verify POSTGRES_URL is correct
   - Ensure PostgreSQL is running
   - Check network connectivity

### Debugging

Enable debug logging in development:
```bash
DEBUG=true
ENVIRONMENT=development
```

View authentication logs:
```bash
# Check application logs for authentication events
tail -f application.log | grep "auth\|login\|token"
```

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use strong SECRET_KEY** - Generate cryptographically secure keys
3. **Enable HTTPS in production** - Use secure cookies
4. **Implement rate limiting** - Prevent brute force attacks
5. **Monitor authentication logs** - Watch for suspicious activity
6. **Regular token rotation** - Use refresh tokens appropriately
7. **Validate all inputs** - Sanitize user data
8. **Keep dependencies updated** - Regular security updates

For detailed documentation, see [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md).