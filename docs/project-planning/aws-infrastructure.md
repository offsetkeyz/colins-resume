# AWS Infrastructure Documentation
## Dynamic YAML-Based Resume System

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Owner:** Colin McAllister
**Status:** Planning Phase

---

## Table of Contents
1. [Overview](#overview)
2. [Current Infrastructure](#current-infrastructure)
3. [Proposed Infrastructure](#proposed-infrastructure)
4. [S3 Bucket Structure](#s3-bucket-structure)
5. [CloudFront Configuration](#cloudfront-configuration)
6. [IAM Permissions](#iam-permissions)
7. [Deployment Strategy](#deployment-strategy)
8. [Cost Analysis](#cost-analysis)
9. [Security Considerations](#security-considerations)
10. [Monitoring and Logging](#monitoring-and-logging)

---

## Overview

This document specifies the AWS infrastructure required to support the dynamic resume system with:
- Main website at `https://colinmca.com`
- Private, token-based resume URLs at `https://colinmca.com/r/{token}/`
- Static file hosting via S3 and CloudFront
- GitHub Actions automated deployment

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       GitHub Actions                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Build Pipeline:                                         │     │
│  │  1. Generate HTML/PDF/JSON                             │     │
│  │  2. Determine deployment path                          │     │
│  │     - main branch → /                                   │     │
│  │     - resume/* → /r/{token}/                           │     │
│  │  3. AWS CLI sync to S3                                 │     │
│  │  4. CloudFront invalidation                            │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────────────────┘
                     │ OIDC / AWS Credentials
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Account                                   │
│                                                                  │
│  ┌─────────────────────────────────────────┐                    │
│  │         S3 Bucket: resume-bucket        │                    │
│  │  ┌────────────────────────────────┐     │                    │
│  │  │ / (root)                       │     │                    │
│  │  │  ├── index.html                │     │                    │
│  │  │  ├── resume.pdf                │     │                    │
│  │  │  ├── resume.json               │     │                    │
│  │  │  ├── css/                      │     │                    │
│  │  │  ├── js/                       │     │                    │
│  │  │  ├── img/                      │     │                    │
│  │  │  └── fonts/                    │     │                    │
│  │  │                                │     │                    │
│  │  │ /r/ (token-based resumes)      │     │                    │
│  │  │  ├── a8f3k2j9/                 │     │                    │
│  │  │  │   ├── resume.pdf            │     │                    │
│  │  │  │   ├── resume.html           │     │                    │
│  │  │  │   ├── resume.json           │     │                    │
│  │  │  │   └── metadata.json         │     │                    │
│  │  │  ├── x7k2m9n4/                 │     │                    │
│  │  │  │   └── ...                   │     │                    │
│  │  │  └── b5h8t3w1/                 │     │                    │
│  │  │      └── ...                   │     │                    │
│  │  └────────────────────────────────┘     │                    │
│  │                                          │                    │
│  │  Properties:                             │                    │
│  │  - Bucket Policy: Public Read            │                    │
│  │  - Versioning: Enabled (optional)        │                    │
│  │  - Encryption: AES-256                   │                    │
│  │  - Lifecycle: Archive old tokens > 1yr   │                    │
│  └─────────────────────────────────────────┘                    │
│                     │                                            │
│                     │ Origin                                     │
│                     ▼                                            │
│  ┌─────────────────────────────────────────┐                    │
│  │  CloudFront Distribution                │                    │
│  │  - Domain: colinmca.com                 │                    │
│  │  - SSL Certificate: ACM                 │                    │
│  │  - Cache Behaviors:                     │                    │
│  │    • /* → Cache 1 hour                  │                    │
│  │    • /r/* → Cache 24 hours              │                    │
│  │  - Security Headers:                    │                    │
│  │    • X-Frame-Options: DENY              │                    │
│  │    • X-Content-Type-Options: nosniff    │                    │
│  │  - Custom Error Pages                   │                    │
│  │  - Access Logging: Enabled              │                    │
│  └─────────────────────────────────────────┘                    │
│                     │                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │   End Users  │
              └──────────────┘
```

---

## Current Infrastructure

### Current Setup (To Be Documented)

**TODO: Fill in actual current values**

| Resource | Value | Notes |
|----------|-------|-------|
| **S3 Bucket Name** | `[TO BE FILLED]` | Verify actual bucket name |
| **S3 Region** | `[TO BE FILLED]` | e.g., us-east-1 |
| **CloudFront Distribution ID** | `[TO BE FILLED]` | Find in AWS Console |
| **CloudFront Domain** | `colinmca.com` | Assumed from documentation |
| **SSL Certificate ARN** | `[TO BE FILLED]` | ACM certificate |
| **Deployment Method** | Manual / GitHub Actions? | Current deployment process |

### Current Deployment Process

**TODO: Document current workflow**
- How are files currently uploaded to S3?
- Is GitHub Actions currently deploying? (Workflow appears paused)
- What AWS credentials are configured in GitHub Secrets?

---

## Proposed Infrastructure

### S3 Bucket Configuration

**Bucket Name:** `[current-bucket-name]` or create new `colin-resume-hosting`

**Bucket Settings:**
```json
{
  "Versioning": "Enabled",
  "Encryption": {
    "SSEAlgorithm": "AES256"
  },
  "PublicAccessBlock": {
    "BlockPublicAcls": false,
    "IgnorePublicAcls": false,
    "BlockPublicPolicy": false,
    "RestrictPublicBuckets": false
  },
  "Tags": [
    {"Key": "Project", "Value": "Resume"},
    {"Key": "ManagedBy", "Value": "GitHubActions"}
  ]
}
```

**Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::[bucket-name]/*"
    }
  ]
}
```

**Static Website Hosting:**
- Enable: Yes
- Index Document: `index.html`
- Error Document: `404.html` (optional)

---

## S3 Bucket Structure

### Directory Layout

```
s3://[bucket-name]/
│
├── index.html                    # Main website homepage
├── resume.pdf                    # Default resume (public)
├── resume.json                   # Resume data API
├── resume.html                   # HTML resume view
│
├── css/                          # Stylesheets
│   ├── main.css
│   └── resume-stylesheet.css
│
├── js/                           # JavaScript files
│   └── main.js
│
├── img/                          # Images
│   └── [profile-photo, etc.]
│
├── fonts/                        # Web fonts
│   └── [font files]
│
├── r/                            # Token-based resume directory
│   │
│   ├── a8f3k2j9/                 # Job-specific resume (Leadership profile)
│   │   ├── resume.pdf            # PDF version
│   │   ├── resume.html           # HTML version
│   │   ├── resume.json           # JSON data
│   │   ├── metadata.json         # Build metadata (see below)
│   │   └── css/                  # Copied stylesheets
│   │       └── resume-stylesheet.css
│   │
│   ├── x7k2m9n4/                 # Another job-specific resume
│   │   └── [same structure]
│   │
│   └── b5h8t3w1/                 # Another job-specific resume
│       └── [same structure]
│
└── robots.txt                    # Search engine directives
```

### Metadata File Format

Each token directory includes a `metadata.json` file:

```json
{
  "token": "a8f3k2j9",
  "branch": "resume/aws-security-eng",
  "profile": "technical",
  "build_timestamp": "2025-11-21T15:30:00Z",
  "commit_sha": "abc123def456",
  "github_run_id": "1234567890",
  "created_by": "github-actions[bot]",
  "company": "AWS",
  "role": "Security Engineer",
  "notes": "Technical profile emphasizing cloud security"
}
```

### Object Tagging

All S3 objects should be tagged for lifecycle management:

| Tag Key | Tag Value | Purpose |
|---------|-----------|---------|
| `Type` | `main` or `job-application` | Differentiate main site from job resumes |
| `Profile` | `default`, `leadership`, `technical` | Track which profile was used |
| `Branch` | Branch name | Reference source branch |
| `CreatedDate` | ISO 8601 date | Track object age |

---

## CloudFront Configuration

### Distribution Settings

**General:**
- **Origin Domain:** `[bucket-name].s3.[region].amazonaws.com`
- **Origin Path:** Leave empty
- **Origin Access:** Public (or use OAI for enhanced security)
- **Viewer Protocol Policy:** Redirect HTTP to HTTPS
- **Allowed HTTP Methods:** GET, HEAD, OPTIONS
- **Compress Objects:** Yes

### Cache Behaviors

#### Behavior 1: Main Site (Default)
```yaml
Path Pattern: Default (*)
Origin: S3 Bucket
Viewer Protocol: Redirect HTTP → HTTPS
Allowed Methods: GET, HEAD, OPTIONS
Cache Policy: CachingOptimized
TTL:
  - Minimum: 0
  - Maximum: 86400 (1 day)
  - Default: 3600 (1 hour)
Compress: Yes
```

#### Behavior 2: Job Resume Tokens
```yaml
Path Pattern: /r/*
Origin: S3 Bucket
Viewer Protocol: Redirect HTTP → HTTPS
Allowed Methods: GET, HEAD, OPTIONS
Cache Policy: Custom
TTL:
  - Minimum: 3600 (1 hour)
  - Maximum: 604800 (7 days)
  - Default: 86400 (1 day)
Compress: Yes
Forward Query Strings: No
```

**Rationale:** Job application resumes change infrequently once deployed, so longer cache times improve performance and reduce costs.

### Custom Error Responses

| HTTP Code | Response Page | Response Code | TTL |
|-----------|---------------|---------------|-----|
| 403 | /404.html | 404 | 300 |
| 404 | /404.html | 404 | 300 |

**Purpose:** Hide S3 bucket structure; treat access denied as not found.

### Security Headers (via Response Headers Policy)

Create a custom Response Headers Policy:

```yaml
Security Headers:
  Strict-Transport-Security:
    Override: Yes
    Value: max-age=31536000; includeSubDomains; preload

  X-Content-Type-Options:
    Override: Yes
    Value: nosniff

  X-Frame-Options:
    Override: Yes
    Value: DENY

  X-XSS-Protection:
    Override: Yes
    Value: 1; mode=block

  Referrer-Policy:
    Override: Yes
    Value: strict-origin-when-cross-origin

Custom Headers:
  X-Robots-Tag:
    Path Pattern: /r/*
    Value: noindex, nofollow
```

### SSL/TLS Configuration

- **SSL Certificate:** AWS Certificate Manager (ACM)
- **Domain:** `colinmca.com`, `www.colinmca.com`
- **Security Policy:** TLSv1.2_2021 (or latest)
- **Supported HTTP Versions:** HTTP/2, HTTP/3

### Access Logging

**Enable CloudFront Access Logs:**
- **S3 Bucket:** `[bucket-name]-logs` or same bucket with `/logs/` prefix
- **Log Prefix:** `cloudfront/`
- **Cookie Logging:** No
- **Include Cookies:** No

**Log Fields Include:**
- Date, Time
- Edge Location
- Bytes Sent
- Client IP
- Request Method
- Host
- URI Path
- Status Code
- Referrer
- User Agent
- Query String
- Edge Response Result Type

---

## IAM Permissions

### GitHub Actions Service Account

**Recommended:** Use OpenID Connect (OIDC) for GitHub Actions authentication (no long-lived credentials).

#### Option 1: OIDC Federation (Recommended)

**IAM Role:** `GitHubActionsResumeDeployment`

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::[account-id]:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:offsetkeyz/colins-resume:*"
        }
      }
    }
  ]
}
```

**Permissions Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::[bucket-name]"
    },
    {
      "Sid": "S3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::[bucket-name]/*"
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "arn:aws:cloudfront::[account-id]:distribution/[distribution-id]"
    }
  ]
}
```

#### Option 2: IAM User with Access Keys (Less Secure)

**IAM User:** `github-actions-resume-deploy`

**Same permissions policy as above**

**GitHub Secrets Required:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`
- `AWS_CLOUDFRONT_DISTRIBUTION_ID`

---

## Deployment Strategy

### Deployment Workflow

#### Main Branch Deployment
```bash
# When pushing to main branch
1. Build HTML/PDF/JSON (default profile)
2. Deploy to S3 root:
   aws s3 sync output/ s3://[bucket-name]/ \
     --delete \
     --cache-control "public, max-age=3600" \
     --exclude "r/*"
3. Invalidate CloudFront cache:
   aws cloudfront create-invalidation \
     --distribution-id [dist-id] \
     --paths "/*"
```

#### Job Branch Deployment
```bash
# When pushing to resume/* branch
1. Read active_profile.txt → "technical"
2. Read resume_token.txt → "a8f3k2j9"
3. Checkout main branch files (resume.yaml, profiles/)
4. Build HTML/PDF/JSON with profile filtering
5. Deploy to S3 token path:
   aws s3 sync output/ s3://[bucket-name]/r/a8f3k2j9/ \
     --cache-control "public, max-age=86400" \
     --metadata "profile=technical,branch=resume/aws-security-eng"
6. Upload metadata.json
7. Invalidate CloudFront cache:
   aws cloudfront create-invalidation \
     --distribution-id [dist-id] \
     --paths "/r/a8f3k2j9/*"
```

### Deployment Script Template

```bash
#!/bin/bash
set -e

# Determine deployment path
if [[ "$GITHUB_REF" == "refs/heads/main" ]]; then
  DEPLOY_PATH="/"
  CACHE_CONTROL="public, max-age=3600"
  echo "Deploying to main site"
elif [[ "$GITHUB_REF" == refs/heads/resume/* ]]; then
  TOKEN=$(cat resume_builder/resume_token.txt | tr -d '[:space:]')
  DEPLOY_PATH="/r/${TOKEN}/"
  CACHE_CONTROL="public, max-age=86400"
  echo "Deploying to token path: ${DEPLOY_PATH}"
else
  echo "Not a deployment branch, skipping"
  exit 0
fi

# Sync to S3
aws s3 sync output/ s3://${AWS_S3_BUCKET}${DEPLOY_PATH} \
  --delete \
  --cache-control "${CACHE_CONTROL}" \
  --metadata-directive REPLACE

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "${DEPLOY_PATH}*"

echo "Deployment complete: https://colinmca.com${DEPLOY_PATH}"
```

---

## Cost Analysis

### Estimated Monthly Costs

**Assumptions:**
- 50 job application branches (resumes)
- Average 3 MB per resume set (HTML, PDF, JSON, CSS)
- 1,000 page views/month (main site)
- 100 resume views/month (job applications)

#### S3 Storage Costs

| Item | Calculation | Cost |
|------|-------------|------|
| Main site | 5 MB × $0.023/GB | $0.0001 |
| Job resumes | 50 × 3 MB × $0.023/GB | $0.0035 |
| **Total Storage** | 155 MB | **$0.004/month** |

#### S3 Request Costs

| Request Type | Count/Month | Cost per 1000 | Total |
|--------------|-------------|---------------|-------|
| PUT (deploys) | 200 | $0.005 | $0.001 |
| GET (via CloudFront) | ~0 (cached) | $0.0004 | $0.00 |
| **Total Requests** | | | **$0.001/month** |

#### CloudFront Costs

| Item | Calculation | Cost |
|------|-------------|------|
| Data Transfer | 1 GB/month × $0.085/GB | $0.085 |
| HTTP Requests | 10,000 × $0.0075/10,000 | $0.0075 |
| HTTPS Requests | 90,000 × $0.01/10,000 | $0.09 |
| **Total CloudFront** | | **$0.18/month** |

#### GitHub Actions Minutes

| Item | Calculation | Cost |
|------|-------------|------|
| Build time per run | 3 minutes | Free tier: 2,000 min/month |
| Deploys per month | ~20 | 60 minutes used |
| **Total Actions** | | **$0.00** (within free tier) |

### Total Estimated Cost: **$0.20 - $0.30/month**

**At Scale (100 job branches):**
- Storage: $0.007/month
- Requests: Same
- Data Transfer: ~$0.20/month
- **Total: $0.40/month**

**Conclusion:** Cost is negligible for personal use.

---

## Security Considerations

### Token Security

**Token Generation:**
```python
import secrets
import string

def generate_resume_token(length=12):
    """Generate cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

**Token Entropy:**
- 12 characters alphanumeric: 62^12 = 3.22 × 10^21 combinations
- Collision probability with 100 tokens: ~0.0000000000000000002%
- Brute force rate-limited by CloudFront/WAF

### Search Engine Protection

**robots.txt (S3 root):**
```
User-agent: *
Disallow: /r/

Sitemap: https://colinmca.com/sitemap.xml
```

**Meta Tags (in /r/{token}/ HTML):**
```html
<meta name="robots" content="noindex, nofollow">
<meta name="googlebot" content="noindex, nofollow">
```

**CloudFront Headers:**
- X-Robots-Tag: noindex, nofollow (for /r/* paths)

### Access Logging

**Enable CloudFront Logs:**
- Monitor for unusual access patterns
- Detect potential token enumeration attempts
- Track geographic distribution of access

**CloudWatch Alarms:**
```yaml
Alarm: High404Rate
Metric: 4xxErrorRate
Threshold: > 10% of requests
Actions: SNS notification

Alarm: UnusualTokenAccess
Metric: RequestCount for /r/* paths
Threshold: > 100 requests/hour to single token
Actions: SNS notification
```

### Bucket Security

**Prevent Direct S3 Access (Optional):**
- Use CloudFront Origin Access Identity (OAI)
- Restrict S3 bucket policy to only allow CloudFront
- Forces all access through CloudFront (headers, caching, logging)

**Example Bucket Policy with OAI:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAI",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity [OAI-ID]"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::[bucket-name]/*"
    }
  ]
}
```

---

## Monitoring and Logging

### CloudWatch Metrics

**Track the following:**
- CloudFront 4xx error rate (broken links, enumeration attempts)
- CloudFront 5xx error rate (origin errors)
- CloudFront request count by path (/r/* vs main site)
- S3 bucket size over time
- Invalidation request count

### Log Analysis

**Common Queries (CloudWatch Logs Insights):**

**1. Token Access Patterns:**
```
fields @timestamp, cs-uri-stem, c-ip, sc-status
| filter cs-uri-stem like /\/r\//
| stats count() by cs-uri-stem
| sort count desc
```

**2. Detect Enumeration Attempts:**
```
fields @timestamp, c-ip, sc-status
| filter cs-uri-stem like /\/r\// and sc-status == 404
| stats count() as attempts by c-ip
| filter attempts > 10
| sort attempts desc
```

**3. Geographic Distribution:**
```
fields @timestamp, x-edge-location, cs-uri-stem
| filter cs-uri-stem like /\/r\//
| stats count() by x-edge-location
```

### Alerting Strategy

| Alert | Condition | Action |
|-------|-----------|--------|
| Build Failure | GitHub Actions workflow fails | Email notification |
| High 404 Rate | >10% of /r/* requests return 404 | Check for enumeration |
| Storage Spike | S3 bucket size increases >50% | Review for unexpected files |
| Cost Anomaly | AWS bill >$5/month | Review usage patterns |

### Dashboard

**Create CloudWatch Dashboard with:**
- CloudFront request rate (last 24h)
- CloudFront error rates (4xx, 5xx)
- S3 bucket size trend
- Top 10 accessed token paths
- Geographic heat map of requests

---

## Implementation Checklist

### Pre-Implementation

- [ ] Document current S3 bucket name
- [ ] Document current CloudFront distribution ID
- [ ] Verify AWS credentials in GitHub Secrets
- [ ] Review current IAM permissions
- [ ] Backup current S3 bucket contents

### Phase 1: Infrastructure Setup

- [ ] Create/verify S3 bucket configuration
- [ ] Enable S3 versioning
- [ ] Configure S3 bucket policy for public read
- [ ] Create `/r/` directory structure
- [ ] Upload robots.txt

### Phase 2: CloudFront Configuration

- [ ] Configure cache behaviors for `/r/*`
- [ ] Add custom error responses
- [ ] Create Response Headers Policy for security headers
- [ ] Enable access logging
- [ ] Test cache invalidation

### Phase 3: IAM Configuration

- [ ] Set up OIDC provider for GitHub Actions (recommended)
  - OR create IAM user with access keys
- [ ] Create IAM role/user with deployment permissions
- [ ] Test permissions with AWS CLI locally
- [ ] Configure GitHub Secrets

### Phase 4: Monitoring Setup

- [ ] Enable CloudFront access logs
- [ ] Create CloudWatch Log Group
- [ ] Set up CloudWatch alarms
- [ ] Create CloudWatch dashboard
- [ ] Test log queries

### Phase 5: Testing

- [ ] Test main branch deployment
- [ ] Test job branch deployment with token
- [ ] Verify token-based URLs are accessible
- [ ] Verify robots.txt and meta tags
- [ ] Test CloudFront cache invalidation
- [ ] Review access logs

---

## Troubleshooting

### Common Issues

#### Issue: 403 Forbidden on S3 Objects
**Cause:** Bucket policy doesn't allow public read
**Solution:** Verify bucket policy includes `s3:GetObject` for `"Principal": "*"`

#### Issue: CloudFront Cache Not Invalidating
**Cause:** Invalid paths in invalidation request
**Solution:** Use `/*` for all files, `/r/token/*` for specific token

#### Issue: GitHub Actions Deployment Fails (403)
**Cause:** Insufficient IAM permissions
**Solution:** Verify IAM role has `s3:PutObject` and `cloudfront:CreateInvalidation`

#### Issue: Token URLs Return 404
**Cause:** Files not uploaded to correct S3 path
**Solution:** Verify deployment script uses `s3://bucket/r/{token}/` not `s3://bucket/r/{token}`

#### Issue: High AWS Costs
**Cause:** Excessive CloudFront invalidations or data transfer
**Solution:** Reduce invalidation frequency; review cache TTLs

---

## Future Enhancements

### Potential Improvements

1. **CloudFront Functions for Dynamic Headers**
   - Add X-Robots-Tag header dynamically based on path
   - Implement security headers via viewer request function

2. **S3 Lifecycle Policies**
   - Archive tokens older than 1 year to S3 Glacier
   - Delete tokens older than 2 years (with manual review)

3. **AWS WAF Integration**
   - Rate limiting for /r/* paths
   - Geographic blocking if needed
   - Custom rules for bot detection

4. **CloudWatch Anomaly Detection**
   - ML-based anomaly detection for traffic patterns
   - Automatic alerting on unusual activity

5. **Cost Optimization**
   - S3 Intelligent-Tiering for infrequently accessed tokens
   - CloudFront reserved capacity (if traffic grows)

---

## References

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [GitHub Actions AWS Deployment Guide](https://docs.github.com/en/actions/deployment/deploying-to-aws)
- [AWS OIDC for GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

---

**Document Status:** ✅ Complete - Ready for Implementation
**Next Steps:** Fill in current infrastructure values, set up OIDC, test deployment
