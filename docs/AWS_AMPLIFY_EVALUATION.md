# AWS Amplify Evaluation
## Should You Switch from S3+CloudFront to AWS Amplify?

**Document Version:** 1.0
**Created:** 2025-11-25
**Project:** Colin's Resume Builder
**Current Stack:** S3 + CloudFront + Route53 + GitHub Actions

---

## Executive Summary

**Recommendation: Stick with S3 + CloudFront**

While AWS Amplify offers simplified setup and management, your project's unique requirements—particularly custom build tools (Pandoc, wkhtmltopdf), Python-based generators, and token-based deployment paths—make it a **poor fit** for Amplify. The current S3 + CloudFront architecture provides the flexibility and control you need.

### Quick Comparison

| Factor | Current (S3+CloudFront) | AWS Amplify | Winner |
|--------|------------------------|-------------|--------|
| **Build Tool Support** | ✅ Full control | ⚠️ Limited custom builds | **S3+CloudFront** |
| **Token-based Deployment** | ✅ Perfect fit | ❌ Not designed for this | **S3+CloudFront** |
| **Setup Complexity** | ⚠️ More components | ✅ Simpler | Amplify |
| **Cost** | ✅ ~$0.20/month | ⚠️ ~$1-2/month | **S3+CloudFront** |
| **Flexibility** | ✅ Full control | ⚠️ Limited | **S3+CloudFront** |
| **Branch Deployments** | ✅ Already working | ✅ Built-in | Tie |
| **PDF Generation** | ✅ Full control | ❌ Difficult | **S3+CloudFront** |

---

## Current Architecture Analysis

### What You Have Now

```
┌──────────────────────────────────────────────────────────────┐
│                    GitHub Repository                          │
│  ┌────────────────────────────────────────────────────┐      │
│  │ resume_builder/                                     │      │
│  │  ├── resume.yaml (source of truth)                 │      │
│  │  ├── profiles/ (default, technical, leadership)    │      │
│  │  ├── md_generator.py                               │      │
│  │  ├── html_generator.py                             │      │
│  │  ├── json_generator.py                             │      │
│  │  └── build_all.sh                                  │      │
│  └────────────────────────────────────────────────────┘      │
└────────────────┬─────────────────────────────────────────────┘
                 │ GitHub Actions
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   Build Pipeline                             │
│  1. Install Python + PyYAML                                  │
│  2. Install Pandoc (markdown → HTML)                         │
│  3. Install wkhtmltopdf (HTML → PDF)                         │
│  4. Run Python generators                                    │
│  5. Deploy to S3:                                            │
│     - main branch → /                                        │
│     - resume/* → /r/{token}/                                 │
│  6. Invalidate CloudFront cache                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  S3 Bucket                CloudFront              Route53    │
│  ├── index.html      →    SSL/TLS           →    DNS         │
│  ├── resume.pdf           Caching                colinmca.com│
│  └── r/                   Headers                            │
│      ├── abc123/          Edge locations                     │
│      └── xyz789/                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Strengths of Current Setup

1. **Full Build Control**: Can install any system packages (Pandoc, wkhtmltopdf)
2. **Flexible Deployment**: Token-based paths for job-specific resumes
3. **Profile System**: Filter resume content by profile (technical, leadership)
4. **Cost-Effective**: ~$0.20/month
5. **Already Working**: Build pipeline is functional

---

## AWS Amplify Overview

### What is AWS Amplify?

AWS Amplify is a platform for building and deploying full-stack web applications. It consists of:

- **Amplify Hosting**: CI/CD + static hosting (like Netlify/Vercel)
- **Amplify Studio**: Visual development tools
- **Amplify Libraries**: Frontend libraries for auth, API, storage
- **Amplify CLI**: Development tooling

For your use case, you'd only use **Amplify Hosting**.

### How Amplify Works

```
GitHub Push → Amplify detects → Runs build → Deploys to CDN → Live site
```

**Build Process:**
1. Amplify uses a `amplify.yml` file to define build steps
2. Runs in a managed container (Amazon Linux 2)
3. Supports Node.js, Python, Go, Ruby out of the box
4. Deploys to built-in CDN (similar to CloudFront)
5. Automatic SSL via AWS Certificate Manager
6. Branch-based deployments automatically

---

## Detailed Comparison

### 1. Build Tool Support

#### Current Setup (S3 + CloudFront)
✅ **Advantages:**
- Full control over GitHub Actions runner
- Can install any Debian package (Pandoc, wkhtmltopdf)
- Can run arbitrary Python scripts
- Can cache build tools for faster builds
- Works perfectly with your current build process

❌ **Disadvantages:**
- Need to manage build dependencies in workflow file
- More verbose configuration

#### AWS Amplify
⚠️ **Concerns:**
- Build environment is Amazon Linux 2 (not Ubuntu)
- Installing custom packages requires `yum` commands
- **Pandoc**: Available via `yum install pandoc` (but may be older version)
- **wkhtmltopdf**: **NOT available in default repos**—would need manual download/install
- Build container has resource limits (configurable, but costs more)
- Less transparent about available tools

✅ **Advantages:**
- Simpler configuration for standard builds (React, Next.js, etc.)
- Built-in support for common frameworks

**Verdict:** Your custom build process (Pandoc + wkhtmltopdf + Python) is easier with GitHub Actions.

---

### 2. Token-Based Deployment Pattern

#### Current Setup
✅ **Perfect Fit:**
```bash
# Main branch → https://colinmca.com/
aws s3 sync output/ s3://bucket/

# Job branch → https://colinmca.com/r/abc123/
TOKEN=$(cat resume_token.txt)
aws s3 sync output/ s3://bucket/r/$TOKEN/
```

Your current workflow:
1. Create `resume/*` branch for job application
2. Add `resume_token.txt` with unique token
3. Add `active_profile.txt` with profile name
4. Push → deploys to `/r/{token}/`
5. Share private URL with recruiter

This is **custom logic** that works perfectly with S3's flat structure.

#### AWS Amplify
❌ **Major Limitation:**

Amplify's deployment model:
- One deployment per branch
- Branch URLs are predictable: `{branch}.{app-id}.amplifyapp.com`
- **Cannot deploy to custom paths like `/r/{token}/`**
- All branches share the same domain structure

**Workarounds (all unsatisfactory):**
1. **Create separate Amplify app per token** → Expensive, unmanageable
2. **Use subdomains** → `abc123.colinmca.com` → Requires DNS management, token leakage
3. **Post-build script to copy to S3** → Defeats the purpose of using Amplify

**Verdict:** Amplify is fundamentally incompatible with your token-based deployment pattern.

---

### 3. Cost Comparison

#### Current Setup: ~$0.20-0.30/month

Breakdown:
```
S3 Storage (150 MB):              $0.004/month
S3 Requests (200 PUTs):           $0.001/month
CloudFront Data Transfer (1 GB):  $0.085/month
CloudFront Requests (100k):       $0.10/month
GitHub Actions:                   $0.00 (free tier)
────────────────────────────────────────────
Total:                            ~$0.20/month
```

At scale (100 job branches):
```
S3 Storage (300 MB):              $0.007/month
CloudFront:                       ~$0.20/month
────────────────────────────────────────────
Total:                            ~$0.30/month
```

#### AWS Amplify: ~$1-2/month (minimum)

Breakdown:
```
Build Minutes (20 deploys/month):  $0.01/minute × 3 min × 20 = $0.60
Hosting Data Served (1 GB):        $0.15/GB × 1 GB = $0.15
Hosting Requests (100k):           $0.15 (first 50k free, then $0.01/10k)
────────────────────────────────────────────
Total:                             ~$1.00/month
```

With 100 job branches (deploying separately):
```
Build Minutes (100 deploys):       $3.00
Hosting:                           ~$0.50
────────────────────────────────────────────
Total:                             ~$3.50/month
```

**Amplify Pricing Notes:**
- First 1,000 build minutes free per month (covers ~333 builds)
- First 15 GB data transfer free per month
- After free tier: $0.01/minute for builds
- More expensive than DIY S3+CloudFront for low-traffic sites

**Verdict:** Current setup is 5-10x cheaper.

---

### 4. Setup Complexity

#### Current Setup
**Initial Setup:** ⚠️ More Complex
- Create S3 bucket
- Configure bucket policy for public read
- Create CloudFront distribution
- Configure SSL certificate in ACM
- Set up Route53 DNS
- Configure GitHub Actions workflow
- Add AWS credentials to GitHub Secrets

**Ongoing Maintenance:** ✅ Low
- Everything is in code (infrastructure as code)
- Rarely need to touch AWS console
- Changes are in GitHub Actions workflow

#### AWS Amplify
**Initial Setup:** ✅ Simpler
- Connect GitHub repository
- Configure build settings (amplify.yml)
- Automatic SSL certificate
- Automatic subdomain
- Point custom domain (optional)

**Ongoing Maintenance:** ⚠️ Vendor Lock-in
- Build logs only in Amplify console
- Less control over caching behavior
- Environment variables in Amplify console
- Harder to migrate away later

**Verdict:** Amplify is easier to set up initially, but you've already done the hard work for S3+CloudFront.

---

### 5. Branch Deployment & Previews

#### Current Setup
✅ **What You Have:**
- Main branch → production (colinmca.com)
- Job branches (resume/*) → token paths (/r/{token}/)
- Pull requests → build only (no deploy)
- Full control over deployment logic

❌ **What You Don't Have:**
- Automatic preview URLs for PRs
- Visual deployment dashboard

#### AWS Amplify
✅ **Built-in Features:**
- Automatic preview URLs for every branch
- PR previews: `pr-123.{app-id}.amplifyapp.com`
- Visual deployment dashboard
- Rollback to previous deployments
- Branch-specific environment variables

❌ **Limitations:**
- Cannot customize deployment paths (breaks your `/r/{token}/` pattern)
- All branches use same build configuration

**Verdict:** Amplify has nice preview features, but they're not worth sacrificing your token-based deployment.

---

### 6. PDF Generation

#### Current Setup
✅ **Full Control:**
```yaml
# GitHub Actions can install anything
- name: Install wkhtmltopdf
  run: |
    wget https://github.com/wkhtmltopdf/.../wkhtmltox.deb
    sudo apt install ./wkhtmltox.deb

- name: Generate PDF
  run: wkhtmltopdf resume.html resume.pdf
```

Works perfectly. You control the exact version and configuration.

#### AWS Amplify
⚠️ **Challenging:**

Amplify build environment:
- Amazon Linux 2 (not Ubuntu)
- No `apt` package manager (uses `yum`)
- wkhtmltopdf not in default repositories

**Workaround needed:**
```yaml
# In amplify.yml
build:
  phases:
    preBuild:
      commands:
        # Download and install wkhtmltopdf manually
        - wget https://github.com/wkhtmltopdf/.../wkhtmltox.rpm
        - sudo yum localinstall -y wkhtmltox.rpm
        # Hope it works...
```

**Risks:**
- RPM compatibility issues with Amazon Linux 2
- Harder to cache dependencies
- Less documentation/examples
- Potential headless browser issues in container

**Alternative:**
- Use a cloud service for PDF generation (puppeteer, headless Chrome)
- More complexity, potential cost

**Verdict:** PDF generation is significantly easier with GitHub Actions.

---

### 7. Flexibility & Control

#### Current Setup
✅ **Full Control:**
- Choose exact GitHub Actions runner (ubuntu-22.04)
- Install any dependencies
- Custom deployment logic (token-based paths)
- Detailed cache control headers
- CloudFront behaviors and edge functions
- Direct S3 access for debugging
- Can switch to different CI/CD anytime (GitLab CI, CircleCI, etc.)

#### AWS Amplify
⚠️ **Limited Control:**
- Build environment is fixed (Amazon Linux 2)
- Cannot customize cache headers as granularly
- Cannot customize CDN behavior as much as CloudFront
- Deployment logic is opinionated
- Vendor lock-in to Amplify platform

**Verdict:** Current setup provides vastly more control and flexibility.

---

## Use Cases Where Amplify Excels

AWS Amplify is excellent for:

1. **Modern Frontend Frameworks**
   - React, Vue, Angular, Svelte apps
   - Next.js, Gatsby, Nuxt.js sites
   - Built-in support for SSR, SPA routing

2. **Full-Stack Serverless Apps**
   - Need authentication (Cognito)
   - Need API (AppSync GraphQL)
   - Need database (DynamoDB via Amplify)
   - Want integrated backend + frontend

3. **Teams Without DevOps Experience**
   - Don't want to manage S3/CloudFront
   - Don't want to write CI/CD pipelines
   - Want a "just works" platform

4. **Prototypes & MVPs**
   - Quick setup
   - Fast iteration
   - Built-in previews

---

## Use Cases Where S3+CloudFront Excels

Your current setup is better for:

1. **Static Sites with Custom Build Processes** ✅ (You)
   - Need specific system packages
   - Python/Ruby/Go generators
   - PDF generation, image processing

2. **Custom Deployment Patterns** ✅ (You)
   - Token-based paths
   - Multi-tenant structure
   - Complex routing logic

3. **Cost-Sensitive Projects** ✅ (You)
   - Low traffic
   - Many branches/variants
   - Want to minimize costs

4. **Maximum Control** ✅ (You)
   - Fine-tune caching behavior
   - Custom CloudFront functions
   - Specific performance optimizations

---

## Migration Effort (If You Still Want Amplify)

If you decide to move to Amplify despite the limitations, here's what it would take:

### Migration Steps

1. **Create Amplify App**
   - Connect GitHub repository
   - Configure custom domain

2. **Create `amplify.yml`**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - pip install pyyaml
           - yum install -y pandoc
           # wkhtmltopdf installation (tricky on Amazon Linux 2)
           - wget https://github.com/wkhtmltopdf/packaging/releases/...
           - yum localinstall -y wkhtmltox.rpm
       build:
         commands:
           - cd resume_builder
           - python3 md_generator.py
           - python3 html_generator.py
           - python3 json_generator.py
           # PDF generation (may not work)
     artifacts:
       baseDirectory: /
       files:
         - '**/*'
     cache:
       paths: []
   ```

3. **Abandon Token-Based Deployment**
   - Each job resume would need its own Amplify app
   - OR use a different URL structure (subdomains)
   - OR give up on private URLs

4. **Migrate Environment Variables**
   - Move GitHub Secrets to Amplify console

5. **Update DNS**
   - Point colinmca.com to Amplify instead of CloudFront

### Estimated Effort: 8-16 hours

**Risks:**
- PDF generation may not work reliably
- Token deployment pattern incompatible
- Higher ongoing costs
- Less flexibility for future changes

---

## Recommendation: Stick with S3 + CloudFront

### Why Your Current Setup is Better

1. **✅ Already Working**: Your GitHub Actions workflow is functional
2. **✅ Perfect Fit**: Token-based deployment works great with S3
3. **✅ Cost-Effective**: 5-10x cheaper than Amplify
4. **✅ Reliable PDF Generation**: wkhtmltopdf works perfectly on Ubuntu
5. **✅ Flexibility**: Full control over build and deployment
6. **✅ Scalable**: Easy to add more job branches

### What You Can Improve (If Needed)

Instead of migrating to Amplify, consider these enhancements to your current setup:

#### 1. Add Preview URLs for Pull Requests
```yaml
# In GitHub Actions workflow
- name: Deploy PR Preview
  if: github.event_name == 'pull_request'
  run: |
    PR_NUM=${{ github.event.pull_request.number }}
    aws s3 sync output/ s3://$BUCKET/preview/pr-$PR_NUM/
    echo "Preview: https://colinmca.com/preview/pr-$PR_NUM/"
```

#### 2. Add Deployment Dashboard
- Use GitHub Environments feature (already in your workflow)
- View deployments at: `https://github.com/offsetkeyz/colins-resume/deployments`

#### 3. Improve Monitoring
```yaml
# CloudWatch alarms for:
- High 404 rate (token enumeration detection)
- Unusual traffic spikes
- Cost anomalies
```

#### 4. Add Rollback Script
```bash
#!/bin/bash
# rollback.sh - Restore previous deployment
aws s3 sync s3://$BUCKET/_backups/$(date -d yesterday +%Y-%m-%d)/ s3://$BUCKET/
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

#### 5. Optimize CloudFront Caching
- Increase TTL for job resumes (`/r/*` → 7 days cache)
- Add CloudFront Functions for dynamic headers
- Enable compression for all text files

---

## Alternative: Hybrid Approach

If you like some Amplify features, you could use a **hybrid approach**:

### Option: Amplify for Main Site, S3 for Job Resumes

```
Main Site (colinmca.com) → Amplify Hosting
  - Easy updates
  - Built-in CI/CD
  - Modern features

Job Resumes (colinmca.com/r/*) → S3 + CloudFront
  - Token-based deployment
  - Custom routing
  - Cost-effective
```

**Implementation:**
1. Host main site on Amplify
2. Use CloudFront distribution in front of both:
   - Path `/` → Amplify origin
   - Path `/r/*` → S3 origin
3. Keep GitHub Actions for job resume deployments

**Pros:**
- Best of both worlds
- Modern tooling for main site
- Flexibility for job resumes

**Cons:**
- More complex architecture
- Two hosting platforms to manage
- Not worth it for a simple resume site

---

## Final Verdict

### Stick with S3 + CloudFront + GitHub Actions

**Why:**
1. Your project is not a good fit for Amplify's opinionated approach
2. Custom build tools (Pandoc, wkhtmltopdf) work better in GitHub Actions
3. Token-based deployment pattern is incompatible with Amplify
4. Current costs are negligible (~$0.20/month)
5. You've already invested in the setup—it's working well
6. Amplify would cost 5-10x more with less functionality

**When to Reconsider Amplify:**
- You rebuild the project as a React/Next.js app
- You add backend features (auth, database, API)
- You want a fully managed platform (cost becomes less important)
- You abandon the token-based deployment pattern

---

## Questions to Ask Yourself

Before making any changes, consider:

1. **What problem are you trying to solve?**
   - Is your current setup broken?
   - Is it too hard to maintain?
   - Are costs too high?

2. **Is Amplify actually simpler for your use case?**
   - Given PDF generation requirements?
   - Given token-based deployment pattern?

3. **What would you gain?**
   - Faster deployments? (Current builds are fast)
   - Better UI? (GitHub Actions UI is adequate)
   - Cost savings? (No—it's more expensive)

4. **What would you lose?**
   - Deployment flexibility
   - Cost efficiency
   - Build tool control

---

## Conclusion

**AWS Amplify is a great service, but it's not the right tool for this job.**

Your resume builder has unique requirements:
- Custom Python build scripts
- PDF generation with wkhtmltopdf
- Token-based private resume URLs
- Profile-based filtering

These are all easier to handle with your current S3 + CloudFront + GitHub Actions setup.

**If you're happy with your current setup, keep it.** It's cost-effective, flexible, and working well.

**If you want to simplify, focus on improving the current architecture** rather than migrating to a platform that doesn't fit your needs.

---

## Resources

- [AWS Amplify Pricing](https://aws.amazon.com/amplify/pricing/)
- [AWS Amplify Build Specification](https://docs.aws.amazon.com/amplify/latest/userguide/build-settings.html)
- [CloudFront vs Amplify Hosting](https://aws.amazon.com/amplify/hosting/)
- [GitHub Actions vs Amplify Build](https://github.com/aws-amplify/amplify-hosting/discussions)

---

**Document Status:** ✅ Complete
**Next Steps:** Review this analysis and decide whether to proceed with current architecture or explore improvements.
