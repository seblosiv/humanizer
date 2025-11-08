# ClearCraft Security Best Practices

Comprehensive security guide for deploying and operating ClearCraft in production environments.

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Deployment Security](#deployment-security)
3. [API Security](#api-security)
4. [Data Privacy & PII Protection](#data-privacy--pii-protection)
5. [Secret Management](#secret-management)
6. [Input Validation](#input-validation)
7. [Logging Security](#logging-security)
8. [Network Security](#network-security)
9. [Ethical Guardrails](#ethical-guardrails)
10. [Compliance Considerations](#compliance-considerations)
11. [Incident Response](#incident-response)
12. [Security Checklist](#security-checklist)

---

## Security Overview

### Security Principles

ClearCraft follows these security principles:

1. **Privacy by Design**: PII redaction, minimal data collection
2. **Least Privilege**: Minimal permissions, non-root execution
3. **Defense in Depth**: Multiple security layers
4. **Transparency**: Disclosure of AI usage
5. **Ethical Operation**: Guardrails against misuse

### Threat Model

**Protected Against:**
- Unauthorized API access
- PII exposure in logs
- Secret exposure in code/config
- Malicious text injection
- Resource exhaustion (DoS)
- Bypass of ethical guardrails

**NOT Protected Against (Out of Scope):**
- Physical server access
- Network-level attacks (use firewall/WAF)
- Social engineering
- Insider threats (requires organizational controls)

---

## Deployment Security

### Never Run as Root

**Problem:** Root execution = full system compromise if breached.

**Solution:**

```dockerfile
# Dockerfile (already implemented)
RUN groupadd -r clearcraft && useradd -r -g clearcraft clearcraft
USER clearcraft
```

**Systemd service:**

```ini
[Service]
User=clearcraft
Group=clearcraft
NoNewPrivileges=true
```

**Verification:**

```bash
# Should NOT be root
docker exec clearcraft whoami
# Should output: clearcraft
```

---

### Minimal Container Image

**Problem:** Large images = larger attack surface.

**Solution:**

```dockerfile
# Use slim base image
FROM python:3.11-slim

# Remove unnecessary packages
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Multi-stage build (future enhancement)
FROM python:3.11-slim AS builder
# ... build dependencies
FROM python:3.11-slim
COPY --from=builder /app /app
```

---

### Read-Only Filesystem

**Problem:** Write access enables persistence of attacks.

**Solution:**

```yaml
# docker-compose.yml
services:
  clearcraft:
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache:mode=1777
```

**Verification:**

```bash
docker exec clearcraft touch /test
# Should fail: Read-only file system
```

---

### Resource Limits

**Problem:** Resource exhaustion DoS.

**Solution:**

```yaml
# docker-compose.yml
services:
  clearcraft:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
```

**Systemd:**

```ini
[Service]
MemoryMax=4G
CPUQuota=200%
```

---

### Disable Debug Mode in Production

**Problem:** Debug mode exposes internals, stack traces.

**Critical:**

```bash
# .env - MUST be false in production
DEBUG=false

# Verify
curl http://localhost:8000/api/nonexistent
# Should return generic error, NOT stack trace
```

---

## API Security

### Authentication (Future Enhancement)

**Current State:** No authentication (assumes trusted network).

**Production Recommendation:**

```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/api/rewrite", dependencies=[Depends(verify_api_key)])
async def rewrite_text(request: RewriteRequest):
    # ... existing code
```

**Environment config:**

```bash
API_KEY=your-secure-random-key-here
# Generate: openssl rand -base64 32
```

---

### Rate Limiting

**Problem:** API abuse, DoS attacks.

**Solution:**

```python
# Using slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/rewrite")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def rewrite_text(request: Request, data: RewriteRequest):
    # ... existing code
```

**Install:**

```bash
pip install slowapi
```

---

### CORS Configuration

**Problem:** Unauthorized cross-origin requests.

**Solution:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # NOT ["*"]
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-API-Key"],
)
```

**Development only:**

```python
if settings.debug:
    allow_origins = ["*"]  # Allow all in dev
else:
    allow_origins = ["https://yourdomain.com"]  # Restrict in prod
```

---

### HTTPS/TLS

**Problem:** Data in transit visible to attackers.

**Solution:**

**Nginx reverse proxy:**

```nginx
server {
    listen 443 ssl http2;
    server_name clearcraft.example.com;

    ssl_certificate /etc/letsencrypt/live/clearcraft.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/clearcraft.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Certbot (free TLS):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d clearcraft.example.com
```

---

### Request Size Limits

**Problem:** Large payloads cause DoS.

**Solution:**

```python
# FastAPI (already has defaults)
app = FastAPI(
    # Max request body size: 10MB
    max_request_size=10 * 1024 * 1024
)
```

**Nginx:**

```nginx
client_max_body_size 10M;
```

**Application-level:**

```python
# In config.py (already implemented)
MAX_TEXT_LENGTH=50000  # characters
```

---

## Data Privacy & PII Protection

### PII Redaction in Logs

**Critical:** MUST be enabled in production.

```bash
# .env
REDACT_PII_IN_LOGS=true
```

**Implementation (already in place):**

```python
# clearcraft/config.py
if settings.redact_pii_in_logs:
    # Redact email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Redact phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    # Redact SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
```

**Verification:**

```python
# Test
import logging
logger.info("User email is john.doe@example.com")
# Should log: "User email is [EMAIL]"
```

---

### Data Retention

**Principle:** Don't store user data.

**Implementation:**

ClearCraft is stateless - no data persistence by default.

**If logging to file:**

```bash
# Rotate logs
# /etc/logrotate.d/clearcraft
/var/log/clearcraft/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 clearcraft clearcraft
    sharedscripts
    postrotate
        systemctl reload clearcraft
    endscript
}
```

---

### Disclosure Requirement

**Transparency:** Users should know AI was used.

```bash
# .env - MUST be true in production
ENABLE_DISCLOSURE=true
```

**Verification:**

```python
result = selector.rewrite(text, enable_disclosure=True)
assert "AI assistance" in result.rewritten_text
```

---

### GDPR Compliance

**Recommendations:**

1. **Data Minimization**: Don't log full text (✓ already implemented)
2. **Purpose Limitation**: Use only for clarity enhancement (✓ documented)
3. **Right to Erasure**: Stateless = no data to erase (✓ by design)
4. **Privacy by Design**: PII redaction enabled (✓ implemented)
5. **Data Processing Agreement**: Required if using DeepInfra

**DeepInfra considerations:**

- Text sent to DeepInfra API (third party)
- Check DeepInfra's data processing agreement
- Ensure users consent to external LLM processing

---

## Secret Management

### Never Hardcode Secrets

**Problem:** Secrets in code = leaked in version control.

**❌ Bad:**

```python
DEEPINFRA_API_TOKEN = "abc123xyz"  # NEVER DO THIS
```

**✅ Good:**

```python
# .env
DEEPINFRA_API_TOKEN=abc123xyz

# config.py
deepinfra_api_token: Optional[str] = Field(default=None, env="DEEPINFRA_API_TOKEN")
```

---

### Protect .env File

**Critical:**

```bash
# Set strict permissions
chmod 600 .env
chown clearcraft:clearcraft .env

# Verify
ls -la .env
# Should show: -rw------- 1 clearcraft clearcraft
```

**Never commit .env:**

```bash
# .gitignore (already included)
.env
.env.local
.env.production
```

---

### Use Secrets Manager (Production)

**AWS Secrets Manager:**

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# In config.py
deepinfra_api_token = get_secret('clearcraft/deepinfra-token')
```

**Docker secrets:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  clearcraft:
    secrets:
      - deepinfra_token
    environment:
      DEEPINFRA_API_TOKEN_FILE: /run/secrets/deepinfra_token

secrets:
  deepinfra_token:
    file: ./secrets/deepinfra_token.txt
```

**Environment-based (Heroku, etc.):**

```bash
# Set via CLI, not in code
heroku config:set DEEPINFRA_API_TOKEN=abc123xyz
```

---

### Rotate Secrets Regularly

**Best Practice:**

1. **API Keys**: Rotate every 90 days
2. **Generate new key** in DeepInfra dashboard
3. **Update** in secrets manager
4. **Restart** service
5. **Revoke old key**

---

## Input Validation

### Text Length Validation

**Problem:** Excessively long text causes resource exhaustion.

**Solution (already implemented):**

```python
# config.py
MAX_TEXT_LENGTH: int = Field(default=50000, ge=1, le=1000000)

# selector.py
if len(text) > settings.max_text_length:
    raise ValueError(f"Text exceeds maximum length of {settings.max_text_length}")
```

---

### Character Encoding Validation

**Problem:** Invalid encoding causes crashes.

**Solution:**

```python
def validate_text(text: str) -> str:
    """Validate and sanitize text input."""
    # Check type
    if not isinstance(text, str):
        raise ValueError("Text must be a string")

    # Check encoding (already UTF-8 in Python 3)
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        raise ValueError("Text contains invalid characters")

    # Strip null bytes
    text = text.replace('\x00', '')

    return text
```

---

### Keyword Blocking (Ethical Guardrails)

**Problem:** Attempts to bypass AI detection.

**Solution (already implemented):**

```python
# config.py
DISALLOWED_KEYWORDS = [
    "bypass", "evade", "undetectable", "fool", "trick",
    "ai detector", "humanize to avoid detection"
]

# deepinfra_llm.py
def check_disallowed_intent(self, text: str) -> None:
    text_lower = text.lower()
    for keyword in settings.disallowed_keywords:
        if keyword.lower() in text_lower:
            raise DisallowedIntentError(keyword=keyword)
```

**Customize for your use case:**

```bash
# .env - Override default list
DISALLOWED_KEYWORDS=bypass,evade,undetectable,custom_keyword
```

---

### Sanitize File Uploads (If Implemented)

**If adding file upload:**

```python
import magic

def validate_file(file: UploadFile):
    # Check file size
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise ValueError("File too large")

    # Check MIME type
    mime = magic.from_buffer(file.file.read(1024), mime=True)
    if mime not in ['text/plain', 'text/markdown']:
        raise ValueError("Invalid file type")

    file.file.seek(0)  # Reset
    return file
```

---

## Logging Security

### Minimize Logging in Production

**Problem:** Verbose logs = potential data leakage.

```bash
# .env
LOG_LEVEL=WARNING  # Only warnings and errors
LOG_FILE=/var/log/clearcraft/clearcraft.log
```

**Never log:**
- Full user text (log only metadata)
- API keys or tokens
- PII without redaction

---

### Secure Log Files

```bash
# Set permissions
chmod 640 /var/log/clearcraft/*.log
chown clearcraft:clearcraft /var/log/clearcraft/*.log

# Rotate regularly (see Data Retention section)
```

---

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Good: Structured, no PII
logger.info("text_rewritten", text_length=len(text), similarity=0.95)

# Bad: Logs full text
logger.info(f"Rewrote: {text}")  # NEVER DO THIS
```

---

## Network Security

### Firewall Configuration

**Principle:** Deny all, allow specific.

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Don't expose 8000 directly - use reverse proxy
```

---

### Reverse Proxy (Nginx)

**Benefits:**
- TLS termination
- Rate limiting
- Request filtering
- Header security

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;

# Hide version
server_tokens off;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/m;
limit_req zone=api_limit burst=20 nodelay;
```

---

### VPC/Private Network (Cloud)

**Recommendation:**

- Deploy in private subnet
- Use load balancer in public subnet
- No direct internet access to app server

**AWS Example:**

```
Internet → ALB (public subnet) → ClearCraft (private subnet)
```

---

## Ethical Guardrails

### Disallowed Intent Detection

**Already implemented** - see Input Validation section.

**Monitoring:**

```python
# Log blocked attempts (without logging text)
logger.warning("disallowed_intent_detected", keyword=keyword, ip=request.client.host)
```

---

### Disclosure Requirement

**Principle:** Transparency about AI usage.

```bash
# .env - Enable disclosure
ENABLE_DISCLOSURE=true
```

**Enforcement:**

```python
# Make it default, hard to bypass
def rewrite(text: str, enable_disclosure: bool = True):
    if not enable_disclosure:
        logger.warning("disclosure_disabled", reason="user_override")
    # ... proceed
```

---

### Usage Terms

**Add to frontend/API docs:**

```markdown
## Acceptable Use Policy

ClearCraft is designed for legitimate text clarity enhancement. Prohibited uses:

- Bypassing AI detection systems
- Evading content filters
- Generating deceptive content
- Academic dishonesty
- Spam generation
- Any illegal activity

Violation may result in service termination.
```

---

## Compliance Considerations

### GDPR (EU)

- ✅ **Data minimization**: Stateless design
- ✅ **Privacy by design**: PII redaction
- ✅ **Right to erasure**: No data stored
- ⚠️ **Lawful basis**: Get user consent for LLM processing
- ⚠️ **Data processing agreement**: Required for DeepInfra

---

### CCPA (California)

- ✅ **Data disclosure**: Users know AI is used
- ✅ **Data deletion**: Stateless = auto-deleted
- ⚠️ **Do Not Sell**: Don't sell user data (not applicable)

---

### HIPAA (Healthcare)

**⚠️ ClearCraft is NOT HIPAA-compliant by default.**

If processing healthcare data:
- Deploy in HIPAA-compliant environment
- Sign BAA with hosting provider
- Encrypt data at rest and in transit
- Implement audit logging
- Use HIPAA-compliant LLM (not DeepInfra)

**Recommendation:** Don't use ClearCraft for PHI without professional compliance review.

---

### SOC 2 (Enterprise)

**Type II controls needed:**
- Access control (authentication)
- Encryption (TLS)
- Monitoring (logging)
- Change management (version control)
- Incident response (see next section)

---

## Incident Response

### Detection

**Monitoring for:**
- Unusual traffic patterns
- High error rates
- Resource exhaustion
- Security exceptions (DisallowedIntentError)

```python
# Add alerting
if error_rate > 5%:
    alert_oncall("High error rate detected")
```

---

### Response Plan

**1. Identify** - Determine incident type
- Unauthorized access?
- Data breach?
- DoS attack?
- Misuse of service?

**2. Contain** - Stop the bleeding
```bash
# Block attacking IP
sudo ufw deny from <IP_ADDRESS>

# Stop service if compromised
docker-compose down
```

**3. Eradicate** - Remove threat
```bash
# Rotate secrets
heroku config:set DEEPINFRA_API_TOKEN=<new_key>

# Update dependencies
pip install --upgrade clearcraft
```

**4. Recover** - Resume operations
```bash
# Restart service
docker-compose up -d

# Verify health
curl http://localhost:8000/healthz
```

**5. Learn** - Post-mortem
- Document incident
- Update security measures
- Implement additional controls

---

### Security Contacts

**Reporting vulnerabilities:**

```
Security contact: security@example.com
PGP key: [provide key]
Response time: Within 48 hours
```

---

## Security Checklist

### Deployment

- [ ] Running as non-root user
- [ ] DEBUG=false in production
- [ ] REDACT_PII_IN_LOGS=true
- [ ] ENABLE_DISCLOSURE=true
- [ ] Resource limits configured
- [ ] Firewall configured (deny all, allow specific)
- [ ] TLS/HTTPS enabled
- [ ] Secrets in secrets manager (not .env in production)
- [ ] .env file permissions: 600
- [ ] Log file permissions: 640
- [ ] Log rotation configured

### API Security

- [ ] Rate limiting enabled
- [ ] CORS configured (not "*")
- [ ] Request size limits set
- [ ] Authentication implemented (if public)
- [ ] Input validation active
- [ ] Ethical guardrails enabled

### Data Privacy

- [ ] PII redaction enabled
- [ ] Minimal logging configured
- [ ] Disclosure message active
- [ ] Data retention policy set
- [ ] No data stored unencrypted

### Monitoring

- [ ] Health checks configured
- [ ] Error monitoring active
- [ ] Security event logging enabled
- [ ] Alerting configured
- [ ] Log aggregation setup

### Compliance

- [ ] Usage terms documented
- [ ] Privacy policy published
- [ ] Data processing agreement (if using LLM)
- [ ] User consent mechanism (if required)
- [ ] Audit logging (if required)

### Operational

- [ ] Secrets rotation schedule
- [ ] Dependency update policy
- [ ] Incident response plan
- [ ] Backup/recovery plan (if stateful)
- [ ] Security contact documented

---

## Security Resources

### Internal Documentation

- [Deployment Guide](DEPLOYMENT.md)
- [Configuration Reference](README.md#configuration)
- [Troubleshooting](TROUBLESHOOTING.md)

### External Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [GDPR Compliance](https://gdpr.eu/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## Summary

**Security is a shared responsibility:**

1. **ClearCraft provides**: Ethical guardrails, PII redaction, secure defaults
2. **You must provide**: TLS, authentication, network security, secret management
3. **Together we ensure**: Safe, ethical, compliant operation

**Golden Rules:**
1. Never run as root
2. Always use HTTPS in production
3. Never commit secrets to version control
4. Always enable PII redaction
5. Always enable disclosure
6. Monitor and alert on security events
7. Keep dependencies updated
8. Have an incident response plan

---

**Last Updated:** 2025-01-08
**Version:** 1.0.0
**Next:** [Performance Tuning](PERFORMANCE.md)
