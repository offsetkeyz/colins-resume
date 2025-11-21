# Security Model and Threat Analysis
## Dynamic YAML-Based Resume System

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Owner:** Colin McAllister
**Status:** Planning Phase

---

## Table of Contents
1. [Security Overview](#security-overview)
2. [Threat Model](#threat-model)
3. [Attack Surface Analysis](#attack-surface-analysis)
4. [Token Security](#token-security)
5. [Search Engine Protection](#search-engine-protection)
6. [Access Control](#access-control)
7. [Data Privacy](#data-privacy)
8. [Monitoring and Detection](#monitoring-and-detection)
9. [Incident Response](#incident-response)
10. [Compliance Considerations](#compliance-considerations)

---

## Security Overview

### Security Posture

**Classification:** Personal Information (PII)
**Sensitivity Level:** Medium
**Target Audience:** Prospective employers (trusted but not authenticated)

### Security Philosophy

This system employs **security through obscurity with defense in depth**:

1. **Primary Defense:** Long, cryptographically random tokens (obscurity)
2. **Secondary Defense:** Search engine exclusion (prevent discovery)
3. **Tertiary Defense:** Access logging and monitoring (detection)
4. **Future Defense:** Optional expiring tokens via CloudFront Signed URLs

**Explicit Non-Goals:**
- ❌ Authentication/authorization (no login required)
- ❌ Per-user access control (URLs are shareable)
- ❌ DRM or download prevention (PDFs are meant to be saved)
- ❌ Cryptographic protection (tokens are in URLs, visible to proxies/logs)

**Rationale:** This is a resume system for job applications. The goal is to:
- Prevent casual discovery via search engines
- Allow easy sharing with recruiters/hiring managers
- Track which employers received which version
- Maintain professional obscurity without complexity

---

## Threat Model

### Assets to Protect

| Asset | Sensitivity | Consequences of Exposure |
|-------|-------------|--------------------------|
| **Resume Content** | Medium | Contains PII (name, email, phone, work history) |
| **Email Address** | Low-Medium | Potential spam/phishing |
| **Phone Number** | Low-Medium | Unwanted calls |
| **Private Token URLs** | Medium | Unintended disclosure of job applications |
| **Profile Associations** | Low | Reveals job application strategy |

### Threat Actors

#### 1. Casual Observers
- **Motivation:** Curiosity, competitor research
- **Capabilities:** Web browsing, basic search skills
- **Likelihood:** Medium
- **Impact:** Low (resume is semi-public anyway)

#### 2. Automated Scrapers / Bots
- **Motivation:** Data aggregation, contact harvesting
- **Capabilities:** Crawling, basic enumeration
- **Likelihood:** High
- **Impact:** Medium (unwanted indexing, spam)

#### 3. Targeted Adversaries
- **Motivation:** Identity theft, corporate espionage, stalking
- **Capabilities:** Advanced enumeration, social engineering
- **Likelihood:** Low
- **Impact:** High (privacy violation, safety concerns)

#### 4. Accidental Disclosure
- **Motivation:** None (user error)
- **Capabilities:** Copy-paste URL to public forum
- **Likelihood:** Low
- **Impact:** Medium (unintended public access)

### Threat Scenarios

#### Scenario 1: Search Engine Indexing

**Attack Path:**
```
1. Resume deployed to https://colinmca.com/r/a8f3k2j9/resume.pdf
2. Google crawler discovers URL via:
   - Referrer headers from LinkedIn
   - Browser history sync
   - Public link sharing
3. URL indexed in search results
4. Resume becomes publicly discoverable
```

**Impact:** Medium (intended to be shared, but not publicly searchable)

**Mitigations:**
- ✅ `robots.txt` disallows `/r/` directory
- ✅ `<meta name="robots" content="noindex, nofollow">` in HTML
- ✅ `X-Robots-Tag: noindex, nofollow` HTTP header via CloudFront
- ✅ No sitemap.xml entries for `/r/*` paths

#### Scenario 2: Token Enumeration

**Attack Path:**
```
1. Attacker knows format: /r/{8-16 alphanumeric}/
2. Generates candidate tokens: a8f3k2j9, b7k2m9n4, etc.
3. Sends HTTP HEAD requests to test existence
4. Discovers valid tokens via 200 vs 404 responses
5. Downloads resumes from discovered tokens
```

**Impact:** Medium (resume content exposed to adversary)

**Mitigations:**
- ✅ Minimum 12-character tokens (62^12 = 3.2 × 10^21 combinations)
- ✅ CloudFront rate limiting / AWS WAF (future enhancement)
- ✅ Access logging with anomaly detection
- ✅ CloudWatch alarms for high 404 rates on `/r/*`
- ⚠️ No CAPTCHA or IP blocking (would complicate legitimate access)

**Risk Assessment:**
- Token space: 62^12 = 3,226,266,762,397,899,821,056 combinations
- At 1,000 requests/second: 102,205,769,423 years to enumerate 1% of space
- **Conclusion:** Computationally infeasible without rate limiting; trivial with rate limiting

#### Scenario 3: Referrer Leakage

**Attack Path:**
```
1. User shares URL https://colinmca.com/r/a8f3k2j9/resume.pdf
2. User clicks external link from resume HTML
3. Referrer header contains: Referer: https://colinmca.com/r/a8f3k2j9/resume.pdf
4. External site logs token URL
5. Token may appear in analytics dashboards
```

**Impact:** Low (only if resume HTML contains external links)

**Mitigations:**
- ✅ `Referrer-Policy: strict-origin-when-cross-origin` header
- ✅ Resume HTML should avoid external links
- ✅ If external links needed, use `rel="noopener noreferrer"`
- ℹ️ PDF downloads don't leak referrers (file download, not navigation)

#### Scenario 4: Accidental Public Sharing

**Attack Path:**
```
1. User posts URL to public forum: "Check out my resume!"
2. URL becomes publicly accessible
3. Anyone can view resume
```

**Impact:** Low (user error, resume is intended to be shared)

**Mitigations:**
- ℹ️ No technical mitigation (user education only)
- 📝 Documentation should warn against public sharing
- 🔮 Future: Token expiration via CloudFront Signed URLs

#### Scenario 5: Token Collision

**Attack Path:**
```
1. User generates token for Job A: a8f3k2j9
2. Later, different user generates same token for Job B
3. Job B deployment overwrites Job A files
4. Original URL now shows wrong resume
```

**Impact:** Medium (wrong resume sent to employer)

**Mitigations:**
- ✅ Cryptographically secure random generation (Python `secrets` module)
- ✅ GitHub Actions checks S3 for existing token before deployment
- ✅ Collision probability with 100 tokens: ~0.0000000000000000002%
- ✅ Use 12+ character tokens for adequate entropy

**Risk Assessment:**
- With 12-character tokens: Collision probability ≈ n²/(2 × 62^12) where n = number of tokens
- For 100 tokens: 100²/(2 × 3.2×10^21) ≈ 1.5 × 10^-18
- **Conclusion:** Negligible risk, but collision detection recommended

#### Scenario 6: Man-in-the-Middle (MITM)

**Attack Path:**
```
1. User connects to public WiFi
2. Attacker intercepts HTTP traffic
3. Attacker reads resume content in transit
```

**Impact:** Medium (resume content exposed)

**Mitigations:**
- ✅ HTTPS enforced (CloudFront redirects HTTP → HTTPS)
- ✅ HSTS header: `Strict-Transport-Security: max-age=31536000`
- ✅ TLS 1.2+ only (CloudFront security policy)
- ✅ No mixed content warnings

**Risk Assessment:** Effectively mitigated by HTTPS

---

## Attack Surface Analysis

### Public Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│                    Public Attack Surface                     │
└─────────────────────────────────────────────────────────────┘

1. CloudFront Distribution (colinmca.com)
   ├─ GET / → Main website (public, indexed)
   ├─ GET /r/{token}/ → Token-based resume (obscured, not indexed)
   └─ Attack Vectors:
       • DDoS (mitigated by CloudFront)
       • Token enumeration (mitigated by token entropy + rate limiting)
       • Cache poisoning (mitigated by CloudFront design)

2. S3 Bucket (resume-bucket)
   ├─ Public read access (required for CloudFront)
   └─ Attack Vectors:
       • Direct S3 URL access (mitigated by OAI, future enhancement)
       • Bucket listing (mitigated by bucket policy, ListBucket denied)
       • Object enumeration (same as token enumeration above)

3. DNS (colinmca.com)
   └─ Attack Vectors:
       • DNS hijacking (mitigated by DNSSEC, registrar security)
       • Subdomain takeover (no unused subdomains)
```

### Internal Attack Surface

```
┌─────────────────────────────────────────────────────────────┐
│                   Internal Attack Surface                    │
└─────────────────────────────────────────────────────────────┘

1. GitHub Repository (offsetkeyz/colins-resume)
   ├─ Contains resume source data (YAML)
   ├─ Contains profile configurations
   └─ Attack Vectors:
       • Repository compromise (mitigated by GitHub 2FA, SSH keys)
       • Malicious commits (mitigated by commit signing, review)
       • Secrets leakage (mitigated by .gitignore, secret scanning)

2. GitHub Actions
   ├─ Builds and deploys resume
   └─ Attack Vectors:
       • Workflow tampering (mitigated by branch protection)
       • Secret exfiltration (mitigated by read-only OIDC, audit logs)
       • Supply chain attack (mitigated by pinned action versions)

3. AWS Account
   ├─ S3 bucket storage
   ├─ CloudFront distribution
   ├─ IAM roles
   └─ Attack Vectors:
       • Credential theft (mitigated by OIDC, no long-lived keys)
       • Privilege escalation (mitigated by least-privilege IAM)
       • Resource deletion (mitigated by versioning, backups)
```

---

## Token Security

### Token Generation

**Requirements:**
- **Entropy:** Minimum 12 characters (recommended 12-16)
- **Character Set:** Alphanumeric (a-z, A-Z, 0-9) = 62 possible characters
- **Randomness:** Cryptographically secure (not predictable)
- **Uniqueness:** No collisions across all job branches

**Implementation:**

```python
import secrets
import string

def generate_resume_token(length=12):
    """
    Generate cryptographically secure resume token.

    Args:
        length (int): Token length (default: 12, min: 8, max: 16)

    Returns:
        str: Random alphanumeric token

    Security:
        - Uses secrets module (not random module)
        - Entropy: log2(62^12) = ~71.4 bits
        - CSPRNG seeded from OS entropy source
    """
    if length < 8 or length > 16:
        raise ValueError("Token length must be between 8 and 16")

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Example usage
token = generate_resume_token(12)
print(f"Token: {token}")  # e.g., "a8F3k2J9mX7n"
```

### Token Entropy Analysis

| Length | Combinations | Bits of Entropy | Brute Force Time (1000 req/s) |
|--------|--------------|-----------------|-------------------------------|
| 8 chars | 2.18 × 10^14 | 47.6 bits | 6,918 years |
| 10 chars | 8.39 × 10^17 | 59.5 bits | 26.6 million years |
| 12 chars | 3.23 × 10^21 | 71.4 bits | 102 billion years |
| 16 chars | 4.77 × 10^28 | 95.3 bits | 1.5 × 10^18 years |

**Recommendation:** **12 characters** provides excellent security-to-usability ratio.

### Token Validation

**GitHub Actions validation:**

```bash
# Validate token format
TOKEN=$(cat resume_builder/resume_token.txt | tr -d '[:space:]')

# Check format: 8-16 alphanumeric characters
if ! [[ "$TOKEN" =~ ^[a-zA-Z0-9]{8,16}$ ]]; then
    echo "::error::Invalid token format"
    echo "::notice::Token must be 8-16 alphanumeric characters (a-zA-Z0-9)"
    exit 1
fi

# Check for collision (token already exists in S3)
if aws s3 ls "s3://${AWS_S3_BUCKET}/r/${TOKEN}/" 2>/dev/null; then
    echo "::error::Token collision detected: $TOKEN"
    echo "::notice::Please generate a new token"
    exit 1
fi
```

### Token Storage

**In Repository:**
```
resume_builder/resume_token.txt
a8f3k2j9
```

**Decision:** Tokens are committed to repository (not secrets)

**Rationale:**
- Tokens are used in public URLs (not cryptographic secrets)
- Need to persist token for rebuild consistency
- If token leaked from repo, URL still obscured (not indexed)

**Alternative Approach (Future Enhancement):**
- Store tokens in GitHub Secrets
- Inject at build time
- Pros: No token in commit history
- Cons: Cannot rebuild old job branches without token

---

## Search Engine Protection

### Multi-Layer Defense

#### Layer 1: robots.txt

**Location:** `s3://bucket/robots.txt`

```
User-agent: *
Disallow: /r/

# Allow main site
Allow: /

Sitemap: https://colinmca.com/sitemap.xml
```

**Effectiveness:** Blocks well-behaved crawlers (Google, Bing)
**Limitations:** Not enforceable (malicious bots can ignore)

#### Layer 2: Meta Tags

**Location:** `s3://bucket/r/{token}/resume.html`

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex, nofollow">
    <meta name="bingbot" content="noindex, nofollow">
    <title>Resume - Colin McAllister</title>
</head>
<body>
    <!-- Resume content -->
</body>
</html>
```

**Effectiveness:** Prevents indexing of HTML pages
**Limitations:** Doesn't apply to PDF files (no HTML to parse)

#### Layer 3: HTTP Headers

**Location:** CloudFront Response Headers Policy

```yaml
X-Robots-Tag:
  Path Pattern: /r/*
  Value: noindex, nofollow, noarchive
```

**Implementation via CloudFront:**
1. Create Response Headers Policy
2. Add custom header: `X-Robots-Tag: noindex, nofollow`
3. Apply policy to `/r/*` cache behavior

**Effectiveness:** Applies to all file types (HTML, PDF, JSON)
**Limitations:** Requires crawler to check HTTP headers (most do)

#### Layer 4: No Sitemap Entries

**Location:** `s3://bucket/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://colinmca.com/</loc>
    <lastmod>2025-11-21</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- No /r/* URLs -->
</urlset>
```

**Effectiveness:** Prevents proactive indexing
**Limitations:** Doesn't prevent discovery via other means

### Testing Search Engine Exclusion

**Google Search Console:**
1. Submit main domain for indexing
2. Monitor crawl stats
3. Verify `/r/*` paths are not indexed

**Manual Testing:**
```bash
# Check robots.txt
curl https://colinmca.com/robots.txt

# Check HTTP headers
curl -I https://colinmca.com/r/testtoken/resume.pdf

# Check for X-Robots-Tag header
```

**Search Queries (should return no results):**
```
site:colinmca.com/r/
inurl:colinmca.com/r/
"colinmca.com/r/"
```

---

## Access Control

### Current Model: No Access Control

**Design Decision:** URLs are shareable, no authentication required

**Rationale:**
- Resume is intended to be shared with employers
- Adding auth would complicate sharing (employer needs account?)
- Token provides sufficient obscurity for intended use case

### Access Logging

**CloudFront Access Logs:**

```
Log Fields:
  - date, time: When request occurred
  - c-ip: Client IP address
  - cs-method: HTTP method (GET, HEAD)
  - cs-uri-stem: Request path (/r/a8f3k2j9/resume.pdf)
  - sc-status: Response code (200, 404, 403)
  - sc-bytes: Bytes sent
  - cs-referer: Referring URL
  - cs-user-agent: Browser/client
  - x-edge-location: CloudFront edge location (geographic)
```

**Example Log Entry:**
```
2025-11-21  15:30:45  SFO5  192.0.2.1  GET  colinmca.com  /r/a8f3k2j9/resume.pdf  200  -  Mozilla/5.0...  -
```

**Log Retention:** 90 days (configurable)

**Log Storage:** S3 bucket with lifecycle policy

### Rate Limiting (Future Enhancement)

**AWS WAF Rules:**

```yaml
Rule: RateLimitTokenPath
  Conditions:
    - URI starts with /r/
  Rate Limit: 100 requests per 5 minutes per IP
  Action: Block with 429 Too Many Requests

Rule: BlockEnumeration
  Conditions:
    - URI starts with /r/
    - Response status: 404
    - Count: >10 in 1 minute
  Action: Block IP for 1 hour
```

**Cost:** AWS WAF ~$5-10/month (may not be worth it for personal use)

**Alternative:** CloudFront Functions (cheaper, simpler)

---

## Data Privacy

### Personally Identifiable Information (PII)

**PII in Resume:**
- Full name
- Email address
- Phone number
- LinkedIn URL
- Work history (company names, dates)
- Location (city, state)

**Privacy Risk:** Low-Medium (resume is intended to be shared)

### Data Minimization

**Best Practices:**
1. ❌ Don't include: SSN, driver's license, date of birth, full address
2. ✅ Use professional email (not personal)
3. ✅ Consider Google Voice number (can be disabled)
4. ✅ Omit sensitive projects (NDA, security-critical)

### GDPR Considerations (if applicable)

**Right to be Forgotten:**
- Delete S3 objects: `aws s3 rm s3://bucket/r/{token}/ --recursive`
- Invalidate CloudFront cache
- Token becomes 404

**Data Retention:**
- Old tokens can be archived or deleted after job search concludes
- CloudFront logs retained for 90 days, then auto-deleted

**Lawful Basis:** Legitimate interest (job application process)

---

## Monitoring and Detection

### Security Monitoring

#### CloudWatch Alarms

**Alarm 1: High 404 Rate on Token Paths**
```yaml
Metric: 4xxErrorRate
Namespace: AWS/CloudFront
Dimensions:
  - DistributionId: [distribution-id]
Filter: cs-uri-stem LIKE '/r/%'
Threshold: > 50% of requests
Evaluation Periods: 2 of 5 (5 minutes)
Action: SNS notification to email
```

**Rationale:** High 404 rate indicates enumeration attack

**Alarm 2: Unusual Traffic Volume**
```yaml
Metric: Requests
Namespace: AWS/CloudFront
Filter: cs-uri-stem LIKE '/r/%'
Threshold: > 100 requests in 5 minutes
Action: SNS notification
```

**Rationale:** Resume URLs should have low, sporadic traffic

**Alarm 3: Geographic Anomaly**
```yaml
Metric: Requests by EdgeLocation
Threshold: Requests from >10 countries in 1 hour
Action: SNS notification
```

**Rationale:** Job applications typically come from specific regions

#### Log Queries (CloudWatch Logs Insights)

**Query 1: Token Access Summary**
```sql
fields @timestamp, cs-uri-stem, c-ip, sc-status
| filter cs-uri-stem like /\/r\//
| stats count() as requests by cs-uri-stem, sc-status
| sort requests desc
```

**Query 2: Failed Enumeration Attempts**
```sql
fields @timestamp, c-ip, cs-uri-stem
| filter cs-uri-stem like /\/r\// and sc-status == 404
| stats count() as failures by c-ip
| filter failures > 10
| sort failures desc
```

**Query 3: Successful Access by Token**
```sql
fields @timestamp, c-ip, cs-user-agent
| filter cs-uri-stem == '/r/a8f3k2j9/resume.pdf' and sc-status == 200
| sort @timestamp desc
```

**Use Case:** See who accessed specific resume URL

### Security Dashboard

**CloudWatch Dashboard Components:**
1. Request rate graph (last 24h)
2. Error rate (4xx, 5xx) by path
3. Top 10 accessed tokens
4. Geographic distribution map
5. Failed enumeration attempts (404s)
6. Recent alerts

---

## Incident Response

### Incident Types

#### Incident 1: Token Discovered/Leaked

**Symptoms:**
- High traffic to specific token URL
- Access from unexpected geographic regions
- Resume URL appears in search results

**Response:**
```bash
# 1. Delete S3 objects immediately
aws s3 rm s3://bucket/r/{token}/ --recursive

# 2. Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id [dist-id] \
  --paths "/r/{token}/*"

# 3. Generate new token for job application
python3 scripts/generate_token.py > resume_builder/resume_token.txt

# 4. Rebuild and redeploy
git add resume_builder/resume_token.txt
git commit -m "Security: Rotate token after leak"
git push

# 5. Update employer with new URL (if needed)
```

**Prevention:**
- Don't post URLs to public forums
- Use email to share (not public channels)
- Monitor access logs regularly

#### Incident 2: Enumeration Attack Detected

**Symptoms:**
- High 404 rate on `/r/*` paths
- Many requests from single IP
- Sequential token guessing pattern

**Response:**
```bash
# 1. Identify attacking IP
aws logs tail /aws/cloudfront/resume-distribution --follow \
  | grep "404" | grep "/r/"

# 2. Block IP via AWS WAF (if enabled)
aws wafv2 update-ip-set \
  --name BlockedIPs \
  --addresses 192.0.2.1/32

# 3. Review all tokens for potential exposure
# (enumeration unlikely to succeed, but review logs)

# 4. Consider enabling rate limiting
```

**Prevention:**
- Enable AWS WAF rate limiting
- Use 12+ character tokens
- Monitor 404 rates

#### Incident 3: Repository Compromise

**Symptoms:**
- Unauthorized commits to repository
- GitHub security alert
- Unexpected workflow runs

**Response:**
```bash
# 1. Revoke compromised credentials
# (GitHub personal access tokens, SSH keys)

# 2. Review commit history for malicious changes
git log --all --oneline

# 3. Revert unauthorized commits
git revert <commit-hash>

# 4. Rotate all secrets
# (AWS role ARN, GitHub secrets)

# 5. Review GitHub Actions logs for secret exfiltration
# Check for suspicious network requests

# 6. Force push if needed (with caution)
git reset --hard <last-good-commit>
git push --force

# 7. Enable GitHub security features
# - Require signed commits
# - Enable secret scanning
# - Enable Dependabot alerts
```

**Prevention:**
- Use SSH keys with passphrase
- Enable GitHub 2FA
- Use branch protection rules
- Review PRs before merging (even your own)

---

## Compliance Considerations

### Regulatory Landscape

**Applicability:**
- ✅ GDPR (if job applications to EU companies)
- ⚠️ CCPA (if job applications to CA companies)
- ❌ HIPAA (not applicable)
- ❌ PCI DSS (not applicable)

### GDPR Compliance

**Article 6 (Lawful Basis):** Legitimate interest (job application)

**Article 15 (Right of Access):** Resume owner is data controller (self-access)

**Article 17 (Right to Erasure):**
```bash
# Delete all resume data
aws s3 rm s3://bucket/r/{token}/ --recursive
aws cloudfront create-invalidation --distribution-id [dist-id] --paths "/r/{token}/*"
```

**Article 32 (Security):**
- ✅ HTTPS encryption in transit
- ✅ S3 encryption at rest (AES-256)
- ✅ Access logging enabled
- ✅ Regular security reviews

### Data Breach Notification

**Trigger:** Unauthorized access to resume data

**Notification Requirements (GDPR):**
- Within 72 hours of discovery
- To data subjects (yourself, if PII exposed)
- To supervisory authority (if high risk)

**Practical Impact:** Low (resume is semi-public document)

---

## Security Checklist

### Pre-Deployment Security Checklist

#### Repository Security
- [ ] Enable GitHub 2FA
- [ ] Use SSH keys with passphrase
- [ ] Enable GitHub secret scanning
- [ ] Enable Dependabot security alerts
- [ ] Configure branch protection for main branch
- [ ] Review .gitignore (no secrets committed)

#### AWS Security
- [ ] Use OIDC for GitHub Actions (no long-lived keys)
- [ ] IAM role follows least-privilege principle
- [ ] S3 bucket encryption enabled (AES-256)
- [ ] CloudFront HTTPS-only (redirect HTTP)
- [ ] CloudFront access logging enabled
- [ ] S3 versioning enabled (rollback capability)

#### Token Security
- [ ] Use 12+ character tokens
- [ ] Use cryptographically secure generation (secrets module)
- [ ] Validate token format in GitHub Actions
- [ ] Check for token collisions before deployment

#### Search Engine Protection
- [ ] Upload robots.txt with /r/ disallow
- [ ] Add X-Robots-Tag header via CloudFront
- [ ] Add noindex meta tags to HTML
- [ ] Verify no /r/ URLs in sitemap.xml

#### Monitoring
- [ ] CloudWatch alarms configured
- [ ] CloudFront access logs enabled
- [ ] Log retention policy set (90 days)
- [ ] Dashboard created for visibility
- [ ] Test alarm notifications

---

## Future Security Enhancements

### Phase 1 (Low Effort, High Impact)

1. **Enable AWS WAF Rate Limiting**
   - Cost: ~$5-10/month
   - Benefit: Prevent enumeration attacks
   - Priority: Medium

2. **Token Collision Detection**
   - Check S3 before deployment
   - GitHub Actions validation step
   - Priority: High

3. **Security Headers Audit**
   - Review all CloudFront headers
   - Add CSP, Permissions-Policy
   - Priority: Low

### Phase 2 (Medium Effort, Medium Impact)

4. **CloudFront Origin Access Identity (OAI)**
   - Block direct S3 access
   - Force traffic through CloudFront
   - Priority: Medium

5. **Automated Log Analysis**
   - Weekly anomaly report
   - Email digest of access patterns
   - Priority: Low

6. **Token Expiration (Optional)**
   - CloudFront Signed URLs with expiration
   - Requires URL regeneration for resume updates
   - Priority: Low (may complicate workflow)

### Phase 3 (High Effort, Low Impact)

7. **IP Allowlisting (Optional)**
   - Restrict token access by IP range
   - Requires employer IP addresses
   - Priority: Very Low (impractical for job applications)

8. **Blockchain Token Registry (Over-Engineering)**
   - Cryptographic proof of token ownership
   - Public/verifiable token metadata
   - Priority: None (fun thought experiment)

---

## Security FAQs

**Q: Are tokens secure enough?**
A: Yes, 12-character alphanumeric tokens have 71.4 bits of entropy, making brute force infeasible even at 1000 req/s. Combined with rate limiting, tokens are highly secure for this use case.

**Q: What if someone shares my URL publicly?**
A: You can delete the S3 objects and generate a new token. The old URL becomes a 404. However, once a PDF is downloaded, you cannot un-share it (like any file).

**Q: Can employers see each other's resumes?**
A: No, each token is unique and unguessable. Employers only know URLs you explicitly share with them.

**Q: Will my resume appear in Google search results?**
A: No, multiple layers prevent indexing: robots.txt, meta tags, and X-Robots-Tag headers. Your main site resume at colinmca.com/ is indexed, but /r/* paths are not.

**Q: What if I lose a token?**
A: Check the job branch's `resume_token.txt` file. If the branch is deleted, the token is lost, but you can still delete the S3 objects via AWS Console.

**Q: Can I revoke access to a specific URL?**
A: Yes, delete the S3 objects at `/r/{token}/`. The URL becomes a 404 immediately (after CloudFront cache expires, ~24 hours, or instant with invalidation).

**Q: Should I use CloudFront Signed URLs with expiration?**
A: Optional. Pros: Time-limited access. Cons: Requires re-generating URLs for resume updates, more complexity. Only needed for highly sensitive positions.

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST SP 800-63B (Digital Identity Guidelines)](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html)
- [Robots.txt Specification](https://www.robotstxt.org/robotstxt.html)
- [X-Robots-Tag Documentation](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)

---

**Document Status:** ✅ Complete - Ready for Implementation
**Security Posture:** Medium (Appropriate for personal resume system)
**Risk Level:** Low-Medium (Acceptable for intended use case)
**Next Steps:** Implement baseline security measures, test search engine exclusion
