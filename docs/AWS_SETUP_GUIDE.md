# AWS Setup Guide for Resume Deployment System

**Document Version:** 1.0
**Created:** 2025-11-22
**Purpose:** Complete guide to configure AWS from scratch for the dynamic resume system
**Prerequisites:** AWS account, domain ownership (colinmca.com)

---

## Table of Contents

1. [Overview](#overview)
2. [Step 1: IAM Setup (Developer Permissions)](#step-1-iam-setup-developer-permissions)
3. [Step 2: S3 Bucket Creation](#step-2-s3-bucket-creation)
4. [Step 3: SSL Certificate (ACM)](#step-3-ssl-certificate-acm)
5. [Step 4: CloudFront Distribution](#step-4-cloudfront-distribution)
6. [Step 5: DNS Configuration](#step-5-dns-configuration)
7. [Step 6: GitHub Actions Integration](#step-6-github-actions-integration)
8. [Step 7: Testing Your Setup](#step-7-testing-your-setup)
9. [Troubleshooting](#troubleshooting)
10. [Cost Summary](#cost-summary)

---

## Overview

### What You're Building

```
GitHub Actions → S3 Bucket → CloudFront → colinmca.com
                    │
                    ├── / (main resume)
                    └── /r/{token}/ (job-specific resumes)
```

### AWS Services Used

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| S3 | File storage | ~$0.01/month |
| CloudFront | CDN & HTTPS | ~$0.20/month |
| ACM | SSL Certificate | Free |
| Route 53 | DNS (optional) | $0.50/month per zone |
| IAM | Access control | Free |

**Total: ~$0.25-$0.75/month**

---

## Step 1: IAM Setup (Developer Permissions)

You need two types of IAM configuration:
1. **Developer IAM User** - For your local AWS CLI access
2. **GitHub Actions Role** - For automated deployments (covered in Step 6)

### 1.1 Create an IAM User for Development

#### Via AWS Console

1. Go to **IAM** → **Users** → **Create user**
2. User name: `resume-developer`
3. Select **Provide user access to the AWS Management Console** (optional, for console access)
4. Select **I want to create an IAM user**
5. Click **Next**

#### Via AWS CLI (if you have root/admin access configured)

```bash
aws iam create-user --user-name resume-developer
```

### 1.2 Create the Developer Policy

Create a policy that grants permissions for S3 and CloudFront management.

#### Via AWS Console

1. Go to **IAM** → **Policies** → **Create policy**
2. Click **JSON** tab
3. Paste the following policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3FullAccessForResumeBucket",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "s3:GetBucketPolicy",
        "s3:PutBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:GetBucketWebsite",
        "s3:PutBucketWebsite",
        "s3:DeleteBucketWebsite",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketAcl",
        "s3:PutBucketAcl"
      ],
      "Resource": "arn:aws:s3:::colin-resume-*"
    },
    {
      "Sid": "S3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl",
        "s3:GetObjectAcl",
        "s3:ListMultipartUploadParts",
        "s3:AbortMultipartUpload"
      ],
      "Resource": "arn:aws:s3:::colin-resume-*/*"
    },
    {
      "Sid": "S3ListAllBuckets",
      "Effect": "Allow",
      "Action": "s3:ListAllMyBuckets",
      "Resource": "*"
    },
    {
      "Sid": "CloudFrontFullAccess",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:UpdateDistribution",
        "cloudfront:DeleteDistribution",
        "cloudfront:ListDistributions",
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations",
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:ListOriginAccessControls",
        "cloudfront:CreateResponseHeadersPolicy",
        "cloudfront:GetResponseHeadersPolicy",
        "cloudfront:ListResponseHeadersPolicies",
        "cloudfront:CreateCachePolicy",
        "cloudfront:GetCachePolicy",
        "cloudfront:ListCachePolicies",
        "cloudfront:TagResource",
        "cloudfront:UntagResource"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ACMCertificateManagement",
      "Effect": "Allow",
      "Action": [
        "acm:RequestCertificate",
        "acm:DescribeCertificate",
        "acm:ListCertificates",
        "acm:GetCertificate",
        "acm:DeleteCertificate",
        "acm:AddTagsToCertificate"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Route53Access",
      "Effect": "Allow",
      "Action": [
        "route53:GetHostedZone",
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets",
        "route53:ChangeResourceRecordSets",
        "route53:GetChange"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMForGitHubOIDC",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:GetRole",
        "iam:DeleteRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:GetRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:CreatePolicy",
        "iam:GetPolicy",
        "iam:DeletePolicy",
        "iam:CreateOpenIDConnectProvider",
        "iam:GetOpenIDConnectProvider",
        "iam:DeleteOpenIDConnectProvider",
        "iam:TagRole",
        "iam:TagPolicy"
      ],
      "Resource": [
        "arn:aws:iam::*:role/GitHubActions*",
        "arn:aws:iam::*:policy/GitHubActions*",
        "arn:aws:iam::*:oidc-provider/token.actions.githubusercontent.com"
      ]
    }
  ]
}
```

4. Click **Next**
5. Policy name: `ResumeDeveloperPolicy`
6. Description: `Full access to manage resume hosting infrastructure`
7. Click **Create policy**

### 1.3 Attach Policy to User

#### Via AWS Console

1. Go to **IAM** → **Users** → **resume-developer**
2. Click **Add permissions** → **Attach policies directly**
3. Search for `ResumeDeveloperPolicy`
4. Select it and click **Next** → **Add permissions**

#### Via AWS CLI

```bash
aws iam attach-user-policy \
  --user-name resume-developer \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/ResumeDeveloperPolicy
```

### 1.4 Create Access Keys for CLI

#### Via AWS Console

1. Go to **IAM** → **Users** → **resume-developer**
2. Click **Security credentials** tab
3. Scroll to **Access keys** → **Create access key**
4. Select **Command Line Interface (CLI)**
5. Check the acknowledgment box
6. Click **Next** → **Create access key**
7. **IMPORTANT:** Download the CSV or copy both keys now (you won't see the secret again)

#### Via AWS CLI

```bash
aws iam create-access-key --user-name resume-developer
```

### 1.5 Configure AWS CLI Locally

```bash
# Install AWS CLI if not already installed
# macOS: brew install awscli
# Linux: sudo apt install awscli or pip install awscli
# Windows: Download from AWS website

# Configure your credentials
aws configure --profile resume-dev

# Enter when prompted:
# AWS Access Key ID: [paste from step 1.4]
# AWS Secret Access Key: [paste from step 1.4]
# Default region name: us-east-1
# Default output format: json
```

**Verify it works:**

```bash
aws s3 ls --profile resume-dev
```

> **Note:** Use `us-east-1` region because ACM certificates for CloudFront MUST be in us-east-1.

---

## Step 2: S3 Bucket Creation

### 2.1 Create the S3 Bucket

Choose a unique bucket name (S3 bucket names are globally unique).

#### Via AWS Console

1. Go to **S3** → **Create bucket**
2. Bucket name: `colin-resume-hosting` (or similar unique name)
3. Region: `us-east-1`
4. **Object Ownership:** ACLs disabled (recommended)
5. **Block Public Access settings:**
   - **Uncheck** "Block all public access"
   - Check the acknowledgment box
6. **Bucket Versioning:** Enable (optional but recommended)
7. **Default encryption:** Enable with SSE-S3
8. Click **Create bucket**

#### Via AWS CLI

```bash
# Create bucket
aws s3 mb s3://colin-resume-hosting --region us-east-1 --profile resume-dev

# Disable block public access
aws s3api put-public-access-block \
  --bucket colin-resume-hosting \
  --public-access-block-configuration \
  "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" \
  --profile resume-dev

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket colin-resume-hosting \
  --versioning-configuration Status=Enabled \
  --profile resume-dev
```

### 2.2 Configure Bucket Policy for Public Read

#### Via AWS Console

1. Go to **S3** → **colin-resume-hosting** → **Permissions** tab
2. Scroll to **Bucket policy** → **Edit**
3. Paste the following policy (replace `colin-resume-hosting` with your bucket name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::colin-resume-hosting/*"
    }
  ]
}
```

4. Click **Save changes**

#### Via AWS CLI

```bash
# Create policy file
cat > /tmp/bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::colin-resume-hosting/*"
    }
  ]
}
EOF

# Apply policy
aws s3api put-bucket-policy \
  --bucket colin-resume-hosting \
  --policy file:///tmp/bucket-policy.json \
  --profile resume-dev
```

### 2.3 Enable Static Website Hosting (Optional)

This is optional since CloudFront will handle the website behavior, but useful for testing.

#### Via AWS Console

1. Go to **S3** → **colin-resume-hosting** → **Properties** tab
2. Scroll to **Static website hosting** → **Edit**
3. Select **Enable**
4. Index document: `index.html`
5. Error document: `404.html`
6. Click **Save changes**

### 2.4 Create Directory Structure

Upload a test file to create the `/r/` prefix:

```bash
# Create a placeholder to establish the /r/ "directory"
echo "Token-based resumes directory" | aws s3 cp - s3://colin-resume-hosting/r/.placeholder --profile resume-dev

# Upload robots.txt
cat > /tmp/robots.txt << 'EOF'
User-agent: *
Disallow: /r/

Sitemap: https://colinmca.com/sitemap.xml
EOF

aws s3 cp /tmp/robots.txt s3://colin-resume-hosting/robots.txt --profile resume-dev
```

### 2.5 Record Your Bucket Information

Save these values for later steps:

```
S3_BUCKET_NAME=colin-resume-hosting
S3_BUCKET_REGION=us-east-1
S3_BUCKET_ARN=arn:aws:s3:::colin-resume-hosting
S3_WEBSITE_ENDPOINT=colin-resume-hosting.s3-website-us-east-1.amazonaws.com
```

---

## Step 3: SSL Certificate (ACM)

**IMPORTANT:** The certificate MUST be created in `us-east-1` region for CloudFront to use it.

### 3.1 Request a Certificate

#### Via AWS Console

1. Switch to **N. Virginia (us-east-1)** region in the top-right dropdown
2. Go to **Certificate Manager** → **Request certificate**
3. Select **Request a public certificate** → **Next**
4. Domain names:
   - `colinmca.com`
   - `*.colinmca.com` (for www and any subdomains)
5. Validation method: **DNS validation** (recommended)
6. Key algorithm: **RSA 2048**
7. Click **Request**

#### Via AWS CLI

```bash
aws acm request-certificate \
  --domain-name colinmca.com \
  --subject-alternative-names "*.colinmca.com" \
  --validation-method DNS \
  --region us-east-1 \
  --profile resume-dev
```

### 3.2 Validate the Certificate (DNS Validation)

After requesting, you need to prove you own the domain by adding a DNS record.

#### Via AWS Console

1. Go to **Certificate Manager** → Click on your certificate
2. In the **Domains** section, you'll see a CNAME record to add
3. Click **Create records in Route 53** if using Route 53, OR
4. Copy the CNAME name and value to add to your DNS provider

**The DNS record looks like:**
```
Name:  _abc123.colinmca.com
Type:  CNAME
Value: _xyz789.acm-validations.aws.
```

#### For Non-Route 53 DNS Providers

Add the CNAME record in your DNS provider's control panel:
- **Cloudflare:** DNS → Add record → CNAME
- **GoDaddy:** DNS Management → Add → CNAME
- **Namecheap:** Advanced DNS → Add new record → CNAME

> **Note:** DNS validation can take 5-30 minutes. The certificate status will change from "Pending validation" to "Issued".

### 3.3 Verify Certificate is Issued

```bash
aws acm describe-certificate \
  --certificate-arn YOUR_CERTIFICATE_ARN \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --profile resume-dev
```

Should return: `"ISSUED"`

### 3.4 Record Your Certificate ARN

Save this for CloudFront setup:

```
ACM_CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/abc-123-def-456
```

---

## Step 4: CloudFront Distribution

### 4.1 Create the CloudFront Distribution

#### Via AWS Console

1. Go to **CloudFront** → **Create distribution**

**Origin Settings:**
| Setting | Value |
|---------|-------|
| Origin domain | `colin-resume-hosting.s3.us-east-1.amazonaws.com` |
| Origin path | Leave empty |
| Name | `S3-colin-resume-hosting` |
| Origin access | Public |

**Default Cache Behavior Settings:**
| Setting | Value |
|---------|-------|
| Compress objects automatically | Yes |
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed HTTP methods | GET, HEAD |
| Cache policy | CachingOptimized |
| Origin request policy | None |

**Settings:**
| Setting | Value |
|---------|-------|
| Price class | Use only North America and Europe (cheaper) |
| Alternate domain name (CNAME) | `colinmca.com` and `www.colinmca.com` |
| Custom SSL certificate | Select your ACM certificate |
| Default root object | `index.html` |
| Standard logging | Optional (enable for debugging) |

2. Click **Create distribution**

### 4.2 Add Cache Behavior for Token Paths

After the distribution is created:

1. Go to **CloudFront** → Your distribution → **Behaviors** tab
2. Click **Create behavior**

**Behavior for /r/* (token-based resumes):**
| Setting | Value |
|---------|-------|
| Path pattern | `/r/*` |
| Origin | S3-colin-resume-hosting |
| Compress objects automatically | Yes |
| Viewer protocol policy | Redirect HTTP to HTTPS |
| Allowed HTTP methods | GET, HEAD |
| Cache policy | CachingOptimized (or create custom with 24h TTL) |

3. Click **Create behavior**

### 4.3 Create Response Headers Policy (Security Headers)

1. Go to **CloudFront** → **Policies** → **Response headers** tab
2. Click **Create response headers policy**

**Policy settings:**
- Name: `ResumeSecurityHeaders`

**Security headers:**
| Header | Value |
|--------|-------|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` |
| X-Content-Type-Options | `nosniff` |
| X-Frame-Options | `DENY` |
| X-XSS-Protection | `1; mode=block` |
| Referrer-Policy | `strict-origin-when-cross-origin` |

**Custom headers:**
| Header | Value |
|--------|-------|
| X-Robots-Tag | `noindex, nofollow` |

3. Click **Create**

### 4.4 Apply Response Headers Policy to /r/* Behavior

1. Go to **CloudFront** → Your distribution → **Behaviors**
2. Select the `/r/*` behavior → **Edit**
3. Scroll to **Response headers policy**
4. Select `ResumeSecurityHeaders`
5. Click **Save changes**

### 4.5 Configure Custom Error Pages

1. Go to **CloudFront** → Your distribution → **Error pages** tab
2. Click **Create custom error response**

**Error Response 1:**
| Setting | Value |
|---------|-------|
| HTTP error code | 403 |
| Customize error response | Yes |
| Response page path | `/404.html` |
| HTTP response code | 404 |
| Error caching minimum TTL | 300 |

**Error Response 2:**
| Setting | Value |
|---------|-------|
| HTTP error code | 404 |
| Customize error response | Yes |
| Response page path | `/404.html` |
| HTTP response code | 404 |
| Error caching minimum TTL | 300 |

### 4.6 Record Your CloudFront Information

```
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
CLOUDFRONT_DOMAIN_NAME=d1234567890.cloudfront.net
```

> **Note:** Distribution deployment takes 5-15 minutes.

---

## Step 5: DNS Configuration

Point your domain to CloudFront.

### Option A: Using Route 53 (Recommended)

#### Create a Hosted Zone (if not already created)

1. Go to **Route 53** → **Hosted zones** → **Create hosted zone**
2. Domain name: `colinmca.com`
3. Type: Public hosted zone
4. Click **Create hosted zone**

#### Update Your Domain's Nameservers

After creating the hosted zone, Route 53 shows you 4 nameservers (NS records). Update these at your domain registrar:

```
ns-123.awsdns-12.com
ns-456.awsdns-34.net
ns-789.awsdns-56.org
ns-012.awsdns-78.co.uk
```

#### Create DNS Records

1. Go to **Route 53** → **Hosted zones** → **colinmca.com**

**Record 1: Root domain (colinmca.com)**
| Setting | Value |
|---------|-------|
| Record name | Leave empty (root) |
| Record type | A |
| Alias | Yes |
| Route traffic to | Alias to CloudFront distribution |
| Choose distribution | Select your distribution |

**Record 2: WWW subdomain**
| Setting | Value |
|---------|-------|
| Record name | www |
| Record type | A |
| Alias | Yes |
| Route traffic to | Alias to CloudFront distribution |
| Choose distribution | Select your distribution |

### Option B: Using External DNS (Cloudflare, GoDaddy, etc.)

Add CNAME records pointing to your CloudFront domain:

| Type | Name | Value |
|------|------|-------|
| CNAME | www | d1234567890.cloudfront.net |
| CNAME | @ | d1234567890.cloudfront.net (if supported) |

> **Note:** Some DNS providers don't allow CNAME at the root. Use their equivalent feature (e.g., Cloudflare's "CNAME flattening" or ALIAS record).

### 5.1 Verify DNS Propagation

```bash
# Check DNS resolution
dig colinmca.com +short
dig www.colinmca.com +short

# Or use nslookup
nslookup colinmca.com
```

Both should return your CloudFront distribution's IP addresses.

---

## Step 6: GitHub Actions Integration

Set up GitHub Actions to deploy automatically when you push code.

### 6.1 Create OIDC Identity Provider (Recommended - No Access Keys)

#### Via AWS Console

1. Go to **IAM** → **Identity providers** → **Add provider**
2. Provider type: **OpenID Connect**
3. Provider URL: `https://token.actions.githubusercontent.com`
4. Click **Get thumbprint**
5. Audience: `sts.amazonaws.com`
6. Click **Add provider**

#### Via AWS CLI

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --profile resume-dev
```

### 6.2 Create IAM Role for GitHub Actions

#### Via AWS Console

1. Go to **IAM** → **Roles** → **Create role**
2. Trusted entity type: **Web identity**
3. Identity provider: `token.actions.githubusercontent.com`
4. Audience: `sts.amazonaws.com`
5. Click **Next**
6. Don't attach any policies yet → **Next**
7. Role name: `GitHubActionsResumeDeployment`
8. Click **Create role**

#### Add Trust Policy

1. Go to **IAM** → **Roles** → **GitHubActionsResumeDeployment**
2. Click **Trust relationships** → **Edit trust policy**
3. Replace with (update `YOUR_GITHUB_USERNAME` and `YOUR_REPO_NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:*"
        }
      }
    }
  ]
}
```

**Example for this project:**
```json
"token.actions.githubusercontent.com:sub": "repo:offsetkeyz/colins-resume:*"
```

### 6.3 Create and Attach Deployment Policy

1. Go to **IAM** → **Policies** → **Create policy**
2. JSON tab, paste:

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
      "Resource": "arn:aws:s3:::colin-resume-hosting"
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
      "Resource": "arn:aws:s3:::colin-resume-hosting/*"
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
    }
  ]
}
```

3. Name: `GitHubActionsDeploymentPolicy`
4. Create and attach to the `GitHubActionsResumeDeployment` role

### 6.4 Configure GitHub Repository Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ROLE_ARN` | `arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActionsResumeDeployment` |
| `AWS_REGION` | `us-east-1` |
| `AWS_S3_BUCKET` | `colin-resume-hosting` |
| `AWS_CLOUDFRONT_DISTRIBUTION_ID` | `E1234567890ABC` |

### 6.5 Example GitHub Actions Workflow

Create `.github/workflows/deploy-resume.yml`:

```yaml
name: Deploy Resume

on:
  push:
    branches:
      - main
      - 'resume/*'

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Determine deployment path
        id: deploy-path
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "path=/" >> $GITHUB_OUTPUT
            echo "cache_control=public, max-age=3600" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/resume/* ]]; then
            TOKEN=$(cat resume_builder/resume_token.txt 2>/dev/null | tr -d '[:space:]' || echo "")
            if [ -z "$TOKEN" ]; then
              echo "Error: resume_token.txt not found or empty"
              exit 1
            fi
            echo "path=/r/${TOKEN}/" >> $GITHUB_OUTPUT
            echo "cache_control=public, max-age=86400" >> $GITHUB_OUTPUT
          fi

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml
          # Add other dependencies as needed

      - name: Build resume
        run: |
          # Your build commands here
          python resume_builder/build.py

      - name: Deploy to S3
        run: |
          aws s3 sync output/ s3://${{ secrets.AWS_S3_BUCKET }}${{ steps.deploy-path.outputs.path }} \
            --delete \
            --cache-control "${{ steps.deploy-path.outputs.cache_control }}"

      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.AWS_CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "${{ steps.deploy-path.outputs.path }}*"
```

---

## Step 7: Testing Your Setup

### 7.1 Test S3 Upload

```bash
# Create a test file
echo "<html><body><h1>Test Resume</h1></body></html>" > /tmp/test.html

# Upload to S3
aws s3 cp /tmp/test.html s3://colin-resume-hosting/test.html --profile resume-dev

# Verify it's there
aws s3 ls s3://colin-resume-hosting/ --profile resume-dev
```

### 7.2 Test CloudFront Access

Wait for DNS propagation (can take up to 48 hours, usually 15-30 minutes), then:

```bash
# Test via CloudFront domain
curl -I https://d1234567890.cloudfront.net/test.html

# Test via custom domain
curl -I https://colinmca.com/test.html
```

### 7.3 Test Token Path

```bash
# Upload to a token path
aws s3 cp /tmp/test.html s3://colin-resume-hosting/r/testtoken123/resume.html --profile resume-dev

# Test access
curl -I https://colinmca.com/r/testtoken123/resume.html

# Verify X-Robots-Tag header is present
curl -I https://colinmca.com/r/testtoken123/resume.html | grep -i x-robots
```

### 7.4 Test CloudFront Invalidation

```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*" \
  --profile resume-dev
```

### 7.5 Test GitHub Actions

1. Push a small change to your repository
2. Go to **Actions** tab in GitHub
3. Watch the workflow run
4. Verify files appear in S3

---

## Troubleshooting

### Common Issues

#### Issue: "Access Denied" when uploading to S3

**Cause:** IAM policy doesn't grant S3 write access

**Solution:**
```bash
# Check current user permissions
aws iam list-attached-user-policies --user-name resume-developer --profile resume-dev
aws iam get-policy --policy-arn YOUR_POLICY_ARN --profile resume-dev
```

#### Issue: Certificate stuck in "Pending validation"

**Cause:** DNS CNAME record not added or not propagated

**Solution:**
1. Verify the CNAME record in your DNS provider
2. Wait up to 30 minutes for propagation
3. Check with: `dig _abc123.colinmca.com CNAME`

#### Issue: CloudFront returns 403 Forbidden

**Cause:** S3 bucket policy doesn't allow public read, or bucket name mismatch

**Solution:**
1. Verify bucket policy allows `s3:GetObject` for `Principal: "*"`
2. Check CloudFront origin domain matches your bucket exactly

#### Issue: HTTPS not working

**Cause:** Certificate not attached to CloudFront or wrong domain

**Solution:**
1. Verify certificate is in `us-east-1` region
2. Verify certificate covers your domain (colinmca.com)
3. Check CloudFront settings → Custom SSL certificate

#### Issue: GitHub Actions fails with "Not authorized"

**Cause:** OIDC trust policy incorrect or role doesn't have permissions

**Solution:**
1. Verify the trust policy has correct GitHub repo format
2. Check the role has the deployment policy attached
3. Verify GitHub secrets are set correctly

#### Issue: Changes not appearing after deploy

**Cause:** CloudFront cache not invalidated

**Solution:**
```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*" \
  --profile resume-dev
```

---

## Cost Summary

### Monthly Estimated Costs

| Service | Usage | Cost |
|---------|-------|------|
| S3 Storage | ~100 MB | $0.01 |
| S3 Requests | ~1,000 | $0.01 |
| CloudFront Data Transfer | ~1 GB | $0.09 |
| CloudFront Requests | ~10,000 | $0.01 |
| Route 53 Hosted Zone | 1 zone | $0.50 |
| ACM Certificate | - | Free |
| **Total** | | **~$0.62/month** |

### Cost Optimization Tips

1. Use "Price Class 100" in CloudFront (North America & Europe only)
2. Increase cache TTLs to reduce S3 requests
3. Skip Route 53 if your domain registrar provides DNS

---

## Quick Reference

### Resource ARNs and IDs to Save

```bash
# AWS Account ID
aws sts get-caller-identity --query Account --output text --profile resume-dev

# S3 Bucket
S3_BUCKET=colin-resume-hosting
S3_BUCKET_ARN=arn:aws:s3:::colin-resume-hosting

# CloudFront Distribution
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
CLOUDFRONT_ARN=arn:aws:cloudfront::ACCOUNT_ID:distribution/E1234567890ABC

# ACM Certificate
ACM_CERTIFICATE_ARN=arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/xxx-xxx-xxx

# GitHub Actions Role
GITHUB_ACTIONS_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/GitHubActionsResumeDeployment
```

### Useful Commands

```bash
# List all S3 objects
aws s3 ls s3://colin-resume-hosting/ --recursive --profile resume-dev

# Upload files
aws s3 sync ./output s3://colin-resume-hosting/ --profile resume-dev

# Invalidate cache
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*" --profile resume-dev

# Check distribution status
aws cloudfront get-distribution --id E1234567890ABC --query 'Distribution.Status' --profile resume-dev
```

---

**Document Complete**

After completing this guide, you will have:
- An IAM user with appropriate permissions for development
- An S3 bucket configured for static website hosting
- A CloudFront distribution with HTTPS and custom domain
- GitHub Actions configured for automated deployments
- Support for token-based private resume URLs at `/r/{token}/`
