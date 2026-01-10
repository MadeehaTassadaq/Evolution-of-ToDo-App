# Todo AI Chatbot Security Guide

## Overview
This document outlines the security measures implemented in the Todo AI Chatbot application and provides guidelines for secure usage and deployment.

## Authentication & Authorization

### JWT-Based Authentication
The application uses JSON Web Tokens (JWT) for authentication:

- **Token Generation**: Upon successful login, a JWT is generated with the user ID as the subject
- **Token Expiration**: Configurable expiration time (default: 30 minutes)
- **Token Storage**: Frontend stores tokens in localStorage (should use HttpOnly cookies in production)
- **Token Validation**: All protected endpoints validate the JWT signature and expiration

### User Authorization
- Users can only access their own conversations and tasks
- Conversation ownership is verified on all access attempts
- MCP tools validate user ownership before executing operations

## Data Protection

### Input Validation
All user inputs are validated:
- Message lengths are limited (configurable maximum)
- Special characters are sanitized
- SQL injection is prevented through SQLModel parameterization
- Cross-site scripting (XSS) is mitigated through proper output encoding

### Password Security
- Passwords are hashed using bcrypt with salt
- Password strength requirements enforced (minimum 8 characters with upper, lower, and digit)
- Plain passwords are never stored or logged

### Data Encryption
- JWT tokens are signed with HS256 algorithm
- Database connections use SSL/TLS when configured
- Sensitive data should be encrypted at rest in production

## API Security

### Rate Limiting
- Configurable rate limiting to prevent abuse
- Default: 100 requests per hour per IP (configurable)

### CORS Configuration
- Restrictive CORS policy by default
- Only specified origins allowed in production
- Credentials allowed only for trusted origins

### Authentication Headers
- All authenticated requests require `Authorization: Bearer {token}` header
- Token validation occurs before processing requests
- Invalid tokens return 401 Unauthorized

## Database Security

### Access Control
- Database credentials stored in environment variables
- Connection pooling with secure parameters
- Parameterized queries prevent SQL injection

### Data Isolation
- User data is isolated by user_id
- Foreign key constraints maintain data integrity
- Access control enforced at application layer

## Infrastructure Security

### Environment Variables
- Sensitive configuration stored in environment variables
- Default values provided for development
- No secrets stored in source code

### Deployment Security
- HTTPS required for production deployments
- Security headers configured appropriately
- Regular security updates applied

## Security Best Practices

### For Administrators
- Regularly rotate JWT secrets
- Monitor authentication logs
- Apply security patches promptly
- Backup databases securely

### For Developers
- Never log sensitive data
- Validate all inputs at server-side
- Use parameterized queries
- Follow security guidelines for dependencies

### For Users
- Use strong, unique passwords
- Log out from shared devices
- Don't share authentication tokens
- Report suspicious activities

## Incident Response

### Security Monitoring
- Authentication failure logs
- Unusual access patterns
- Failed authorization attempts
- Database access anomalies

### Breach Response
1. Isolate affected systems
2. Rotate all secrets and tokens
3. Notify users if personal data compromised
4. Conduct security audit
5. Implement additional controls

## Compliance Considerations

### Data Privacy
- User data is stored only as needed for functionality
- Users can delete their accounts and data
- Data retention policies should be defined per jurisdiction

### Audit Trail
- Authentication events logged
- Data access patterns monitored
- Change logs maintained for security-relevant settings

## Vulnerability Management

### Regular Assessments
- Dependency vulnerability scans
- Code security reviews
- Penetration testing schedule
- Security configuration audits

### Patch Management
- Automated security updates for dependencies
- Regular framework updates
- Timely patch application
- Testing before production deployment

## Security Configuration

### Environment Variables
```
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
MAX_MESSAGE_LENGTH=1000
FRONTEND_ORIGIN=https://yourdomain.com
ENVIRONMENT=production
```

### Recommended Production Settings
- Strong, randomly generated JWT secret
- Short token expiration times
- Restrictive CORS origins
- Enabled HTTPS with HSTS
- Proper error message sanitization