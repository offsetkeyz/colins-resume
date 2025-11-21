# GitHub Actions Workflow Specification
## Dynamic YAML-Based Resume System

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Owner:** Colin McAllister
**Status:** Planning Phase

---

## Table of Contents
1. [Overview](#overview)
2. [Workflow Architecture](#workflow-architecture)
3. [Branch Detection Logic](#branch-detection-logic)
4. [Workflow File Structure](#workflow-file-structure)
5. [Build Steps Specification](#build-steps-specification)
6. [Error Handling](#error-handling)
7. [Secret Management](#secret-management)
8. [Testing Strategy](#testing-strategy)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This document specifies the complete GitHub Actions workflow for building and deploying the dynamic resume system. The workflow must handle two distinct scenarios:

1. **Main Branch:** Deploy full resume (default profile) to `https://colinmca.com/`
2. **Job Branches:** Deploy filtered resume to `https://colinmca.com/r/{token}/`

### Workflow Triggers

```yaml
on:
  push:
    branches:
      - main
      - 'resume/**'
  workflow_dispatch:
    inputs:
      profile:
        description: 'Profile to build (for testing)'
        required: false
        type: string
      branch_type:
        description: 'Force branch type (main/job)'
        required: false
        type: choice
        options:
          - auto
          - main
          - job
```

**Rationale:**
- Automatic builds on push to main or any resume/* branch
- Manual workflow_dispatch for testing with custom profiles
- Support for forced branch type testing

---

## Workflow Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
         ┌──────▼──────┐           ┌───────▼────────┐
         │ MAIN BRANCH │           │ RESUME/* BRANCH│
         └──────┬──────┘           └───────┬────────┘
                │                           │
    ┌───────────▼───────────┐  ┌───────────▼────────────┐
    │ 1. Checkout main      │  │ 1. Checkout job branch │
    │ 2. Install deps       │  │ 2. Install deps        │
    │ 3. Load resume.yaml   │  │ 3. Read active_profile │
    │ 4. Use default profile│  │ 4. Read resume_token   │
    │ 5. Generate outputs   │  │ 5. Checkout main:      │
    │ 6. Deploy to /        │  │    - resume.yaml       │
    │ 7. Invalidate CF      │  │    - profiles/         │
    └───────────┬───────────┘  │ 6. Load profile config │
                │               │ 7. Filter content      │
                │               │ 8. Generate outputs    │
                │               │ 9. Add metadata.json   │
                │               │ 10. Deploy to /r/token/│
                │               │ 11. Invalidate CF      │
                │               └────────────┬───────────┘
                │                            │
                └────────────┬───────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Deployment Done  │
                   │  URL in logs      │
                   └───────────────────┘
```

---

## Branch Detection Logic

### Detection Algorithm

```bash
#!/bin/bash

# Function to detect branch type
detect_branch_type() {
  local github_ref="$1"
  local manual_override="$2"

  # Check for manual override (workflow_dispatch)
  if [[ -n "$manual_override" && "$manual_override" != "auto" ]]; then
    echo "$manual_override"
    return 0
  fi

  # Auto-detect based on GITHUB_REF
  if [[ "$github_ref" == "refs/heads/main" ]]; then
    echo "main"
  elif [[ "$github_ref" =~ ^refs/heads/resume/.+ ]]; then
    echo "job"
  else
    echo "unknown"
    return 1
  fi
}

# Usage in workflow
BRANCH_TYPE=$(detect_branch_type "$GITHUB_REF" "${{ inputs.branch_type }}")

if [[ "$BRANCH_TYPE" == "unknown" ]]; then
  echo "::error::Cannot determine branch type. Expected 'main' or 'resume/*'"
  exit 1
fi

echo "BRANCH_TYPE=$BRANCH_TYPE" >> $GITHUB_ENV
```

### Branch Type Outputs

| Branch Name | GITHUB_REF | Detected Type | Deploy Path |
|-------------|------------|---------------|-------------|
| `main` | `refs/heads/main` | `main` | `/` |
| `resume/aws-security-eng` | `refs/heads/resume/aws-security-eng` | `job` | `/r/{token}/` |
| `resume/google-tech-lead` | `refs/heads/resume/google-tech-lead` | `job` | `/r/{token}/` |
| `feature/new-design` | `refs/heads/feature/new-design` | `unknown` | ❌ Error |

---

## Workflow File Structure

### Complete Workflow File

**Location:** `.github/workflows/build-deploy-resume.yml`

```yaml
name: Build and Deploy Resume

on:
  push:
    branches:
      - main
      - 'resume/**'
  workflow_dispatch:
    inputs:
      profile:
        description: 'Profile to build (for testing)'
        required: false
        type: string
      branch_type:
        description: 'Force branch type (main/job)'
        required: false
        default: 'auto'
        type: choice
        options:
          - auto
          - main
          - job

# Required for OIDC authentication with AWS
permissions:
  id-token: write
  contents: read

jobs:
  build-and-deploy:
    runs-on: ubuntu-22.04

    steps:
      #########################################
      # STEP 1: CHECKOUT AND SETUP
      #########################################

      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 2  # Needed for accessing main branch from job branches

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install system dependencies
        run: |
          # Download specific versions for reproducibility
          wget -q https://github.com/jgm/pandoc/releases/download/3.0.1/pandoc-3.0.1-1-amd64.deb
          wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb

          sudo apt-get update
          sudo apt-get install -y ./pandoc-3.0.1-1-amd64.deb
          sudo apt-get install -y ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb

          # Verify installations
          pandoc --version
          wkhtmltopdf --version

      #########################################
      # STEP 2: DETECT BRANCH TYPE
      #########################################

      - name: Detect branch type and configuration
        id: config
        run: |
          #!/bin/bash
          set -e

          # Determine branch type
          MANUAL_OVERRIDE="${{ inputs.branch_type }}"

          if [[ -n "$MANUAL_OVERRIDE" && "$MANUAL_OVERRIDE" != "auto" ]]; then
            BRANCH_TYPE="$MANUAL_OVERRIDE"
            echo "Using manual override: $BRANCH_TYPE"
          elif [[ "$GITHUB_REF" == "refs/heads/main" ]]; then
            BRANCH_TYPE="main"
          elif [[ "$GITHUB_REF" =~ ^refs/heads/resume/.+ ]]; then
            BRANCH_TYPE="job"
          else
            echo "::error::Unknown branch type. Expected 'main' or 'resume/*'"
            exit 1
          fi

          echo "branch_type=$BRANCH_TYPE" >> $GITHUB_OUTPUT
          echo "::notice::Detected branch type: $BRANCH_TYPE"

      #########################################
      # STEP 3: CONFIGURE BASED ON BRANCH TYPE
      #########################################

      - name: Configure for main branch
        if: steps.config.outputs.branch_type == 'main'
        run: |
          echo "PROFILE=default" >> $GITHUB_ENV
          echo "DEPLOY_PATH=/" >> $GITHUB_ENV
          echo "CACHE_CONTROL=public, max-age=3600" >> $GITHUB_ENV
          echo "::notice::Deploying to main site with default profile"

      - name: Configure for job branch
        if: steps.config.outputs.branch_type == 'job'
        run: |
          #!/bin/bash
          set -e

          # Fetch main branch to access master resume and profiles
          git fetch origin main:refs/remotes/origin/main

          # Read profile configuration from job branch
          if [[ ! -f "resume_builder/active_profile.txt" ]]; then
            echo "::error::Missing active_profile.txt in resume_builder/"
            exit 1
          fi

          PROFILE=$(cat resume_builder/active_profile.txt | tr -d '[:space:]')

          if [[ -z "$PROFILE" ]]; then
            echo "::error::active_profile.txt is empty"
            exit 1
          fi

          # Read token configuration from job branch
          if [[ ! -f "resume_builder/resume_token.txt" ]]; then
            echo "::error::Missing resume_token.txt in resume_builder/"
            exit 1
          fi

          TOKEN=$(cat resume_builder/resume_token.txt | tr -d '[:space:]')

          if [[ -z "$TOKEN" ]]; then
            echo "::error::resume_token.txt is empty"
            exit 1
          fi

          # Validate token format (alphanumeric, 8-16 characters)
          if ! [[ "$TOKEN" =~ ^[a-zA-Z0-9]{8,16}$ ]]; then
            echo "::error::Invalid token format. Must be 8-16 alphanumeric characters."
            echo "::error::Got: $TOKEN"
            exit 1
          fi

          # Checkout master resume and profiles from main branch
          git checkout origin/main -- resume_builder/resume.yaml
          git checkout origin/main -- resume_builder/profiles/

          # Verify profile exists
          if [[ ! -f "resume_builder/profiles/${PROFILE}.yaml" ]]; then
            echo "::error::Profile '${PROFILE}' not found in resume_builder/profiles/"
            echo "::notice::Available profiles:"
            ls -1 resume_builder/profiles/*.yaml | xargs -n1 basename | sed 's/.yaml$//' || echo "None found"
            exit 1
          fi

          # Set environment variables
          echo "PROFILE=$PROFILE" >> $GITHUB_ENV
          echo "TOKEN=$TOKEN" >> $GITHUB_ENV
          echo "DEPLOY_PATH=/r/${TOKEN}/" >> $GITHUB_ENV
          echo "CACHE_CONTROL=public, max-age=86400" >> $GITHUB_ENV

          echo "::notice::Using profile: $PROFILE"
          echo "::notice::Using token: $TOKEN"
          echo "::notice::Deploy path: /r/${TOKEN}/"

      #########################################
      # STEP 4: BUILD RESUME
      #########################################

      - name: Build resume
        run: |
          cd resume_builder

          # Run generators with profile filtering
          python3 yaml_loader.py --profile "$PROFILE"
          python3 html_generator.py --profile "$PROFILE"
          python3 md_generator.py --profile "$PROFILE"
          python3 json_generator.py --profile "$PROFILE"

          cd ..

          echo "::notice::Resume built successfully with profile: $PROFILE"

      - name: Convert Markdown to HTML
        run: |
          pandoc resume_builder/resume.md \
            -f markdown \
            -t html \
            -c css/resume-stylesheet.css \
            -s \
            -o output/resume.html

      - name: Convert HTML to PDF
        run: |
          wkhtmltopdf \
            --enable-local-file-access \
            --page-size Letter \
            --margin-top 10mm \
            --margin-bottom 10mm \
            --margin-left 10mm \
            --margin-right 10mm \
            output/resume.html \
            output/resume.pdf

          # Verify PDF was created
          if [[ ! -f "output/resume.pdf" ]]; then
            echo "::error::PDF generation failed"
            exit 1
          fi

          # Check PDF file size (should be > 10KB for valid resume)
          PDF_SIZE=$(stat -f%z "output/resume.pdf" 2>/dev/null || stat -c%s "output/resume.pdf")
          if [[ $PDF_SIZE -lt 10240 ]]; then
            echo "::error::PDF file too small ($PDF_SIZE bytes), likely generation error"
            exit 1
          fi

          echo "::notice::PDF generated successfully ($PDF_SIZE bytes)"

      #########################################
      # STEP 5: CREATE METADATA
      #########################################

      - name: Create deployment metadata
        if: steps.config.outputs.branch_type == 'job'
        run: |
          cat > output/metadata.json <<EOF
          {
            "token": "$TOKEN",
            "profile": "$PROFILE",
            "branch": "${GITHUB_REF#refs/heads/}",
            "commit_sha": "$GITHUB_SHA",
            "build_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "github_run_id": "$GITHUB_RUN_ID",
            "github_run_number": "$GITHUB_RUN_NUMBER",
            "github_actor": "$GITHUB_ACTOR",
            "github_repository": "$GITHUB_REPOSITORY"
          }
          EOF

          echo "::notice::Metadata created"
          cat output/metadata.json

      #########################################
      # STEP 6: CONFIGURE AWS CREDENTIALS
      #########################################

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ secrets.AWS_REGION }}
          role-session-name: GitHubActions-${{ github.run_id }}

      #########################################
      # STEP 7: DEPLOY TO S3
      #########################################

      - name: Deploy to S3
        run: |
          # Sync output directory to S3
          aws s3 sync output/ s3://${{ secrets.AWS_S3_BUCKET }}${DEPLOY_PATH} \
            --delete \
            --cache-control "${CACHE_CONTROL}" \
            --metadata-directive REPLACE \
            --only-show-errors

          # Add tags to uploaded objects (job branches only)
          if [[ "${{ steps.config.outputs.branch_type }}" == "job" ]]; then
            aws s3api put-object-tagging \
              --bucket ${{ secrets.AWS_S3_BUCKET }} \
              --key "${DEPLOY_PATH#/}resume.pdf" \
              --tagging "TagSet=[{Key=Type,Value=job-application},{Key=Profile,Value=${PROFILE}},{Key=Branch,Value=${GITHUB_REF#refs/heads/}},{Key=CreatedDate,Value=$(date -u +%Y-%m-%d)}]" \
              2>/dev/null || echo "::warning::Failed to tag S3 objects (non-critical)"
          fi

          echo "::notice::Files deployed to s3://${{ secrets.AWS_S3_BUCKET }}${DEPLOY_PATH}"

      #########################################
      # STEP 8: INVALIDATE CLOUDFRONT CACHE
      #########################################

      - name: Invalidate CloudFront cache
        run: |
          INVALIDATION_PATH="${DEPLOY_PATH}*"

          INVALIDATION_ID=$(aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.AWS_CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "$INVALIDATION_PATH" \
            --query 'Invalidation.Id' \
            --output text)

          echo "::notice::CloudFront invalidation created: $INVALIDATION_ID"
          echo "::notice::Path invalidated: $INVALIDATION_PATH"

      #########################################
      # STEP 9: OUTPUT RESULTS
      #########################################

      - name: Output deployment URL
        run: |
          if [[ "${{ steps.config.outputs.branch_type }}" == "main" ]]; then
            RESUME_URL="https://colinmca.com/resume.pdf"
          else
            RESUME_URL="https://colinmca.com/r/${TOKEN}/resume.pdf"
          fi

          echo "::notice::✅ Deployment successful!"
          echo "::notice::📄 Resume URL: $RESUME_URL"
          echo "::notice::🔧 Profile: $PROFILE"

          # Set job output for potential downstream jobs
          echo "resume_url=$RESUME_URL" >> $GITHUB_OUTPUT

      #########################################
      # STEP 10: UPLOAD ARTIFACTS (for debugging)
      #########################################

      - name: Upload build artifacts
        if: always()  # Upload even if deployment fails
        uses: actions/upload-artifact@v4
        with:
          name: resume-${{ steps.config.outputs.branch_type }}-${{ env.PROFILE }}-${{ github.run_number }}
          path: |
            output/
            resume_builder/resume.yaml
            resume_builder/active_profile.txt
            resume_builder/resume_token.txt
          retention-days: 30
```

---

## Build Steps Specification

### Step-by-Step Breakdown

#### Step 1: Checkout and Setup

**Purpose:** Prepare the build environment

**Actions:**
1. Checkout repository with `fetch-depth: 2` (allows access to main branch)
2. Set up Python 3.11 with pip cache
3. Install Python dependencies from `requirements.txt`
4. Install Pandoc 3.0.1 and wkhtmltopdf 0.12.6.1

**Error Conditions:**
- Checkout fails → Abort workflow
- Python setup fails → Abort workflow
- Dependency installation fails → Abort workflow
- Pandoc/wkhtmltopdf installation fails → Abort workflow

#### Step 2: Detect Branch Type

**Purpose:** Determine deployment configuration

**Logic:**
```python
if manual_override and manual_override != 'auto':
    branch_type = manual_override
elif GITHUB_REF == 'refs/heads/main':
    branch_type = 'main'
elif GITHUB_REF.startswith('refs/heads/resume/'):
    branch_type = 'job'
else:
    ERROR: Unknown branch type
```

**Outputs:**
- `steps.config.outputs.branch_type`: "main" or "job"

**Error Conditions:**
- Unknown branch → Abort with error message

#### Step 3: Configure Based on Branch Type

**Main Branch Configuration:**
```bash
PROFILE=default
DEPLOY_PATH=/
CACHE_CONTROL=public, max-age=3600
```

**Job Branch Configuration:**
```bash
# 1. Fetch main branch
git fetch origin main:refs/remotes/origin/main

# 2. Read active_profile.txt
PROFILE=$(cat resume_builder/active_profile.txt | tr -d '[:space:]')

# 3. Read resume_token.txt
TOKEN=$(cat resume_builder/resume_token.txt | tr -d '[:space:]')

# 4. Validate token format: ^[a-zA-Z0-9]{8,16}$
if ! [[ "$TOKEN" =~ ^[a-zA-Z0-9]{8,16}$ ]]; then
    ERROR: Invalid token format
fi

# 5. Checkout files from main branch
git checkout origin/main -- resume_builder/resume.yaml
git checkout origin/main -- resume_builder/profiles/

# 6. Verify profile exists
if [[ ! -f "resume_builder/profiles/${PROFILE}.yaml" ]]; then
    ERROR: Profile not found
fi

# 7. Set environment variables
DEPLOY_PATH=/r/${TOKEN}/
CACHE_CONTROL=public, max-age=86400
```

**Error Conditions:**
- Missing `active_profile.txt` → Abort with error
- Empty profile value → Abort with error
- Missing `resume_token.txt` → Abort with error
- Invalid token format → Abort with error and show format requirements
- Profile file doesn't exist → Abort with error and list available profiles

#### Step 4: Build Resume

**Purpose:** Generate HTML, PDF, and JSON outputs

**Actions:**
```bash
cd resume_builder
python3 yaml_loader.py --profile "$PROFILE"
python3 html_generator.py --profile "$PROFILE"
python3 md_generator.py --profile "$PROFILE"
python3 json_generator.py --profile "$PROFILE"

cd ..

# Convert Markdown → HTML
pandoc resume_builder/resume.md \
  -f markdown -t html \
  -c css/resume-stylesheet.css \
  -s -o output/resume.html

# Convert HTML → PDF
wkhtmltopdf --enable-local-file-access \
  --page-size Letter \
  --margin-top 10mm --margin-bottom 10mm \
  --margin-left 10mm --margin-right 10mm \
  output/resume.html output/resume.pdf

# Validate PDF
PDF_SIZE=$(stat -c%s "output/resume.pdf")
if [[ $PDF_SIZE -lt 10240 ]]; then
    ERROR: PDF too small
fi
```

**Error Conditions:**
- YAML loading fails → Abort with Python traceback
- Profile filtering fails → Abort with error
- Pandoc conversion fails → Abort with error
- wkhtmltopdf fails → Abort with error
- PDF file missing → Abort with error
- PDF file too small (<10KB) → Abort with warning

#### Step 5: Create Metadata

**Purpose:** Document build information (job branches only)

**Actions:**
```json
{
  "token": "a8f3k2j9",
  "profile": "technical",
  "branch": "resume/aws-security-eng",
  "commit_sha": "abc123...",
  "build_timestamp": "2025-11-21T15:30:00Z",
  "github_run_id": "1234567890",
  "github_run_number": "42",
  "github_actor": "offsetkeyz",
  "github_repository": "offsetkeyz/colins-resume"
}
```

#### Step 6: Configure AWS Credentials

**Purpose:** Authenticate with AWS using OIDC

**Actions:**
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: ${{ secrets.AWS_REGION }}
```

**Required Secrets:**
- `AWS_ROLE_ARN`: IAM role ARN with deployment permissions
- `AWS_REGION`: AWS region (e.g., us-east-1)
- `AWS_S3_BUCKET`: S3 bucket name
- `AWS_CLOUDFRONT_DISTRIBUTION_ID`: CloudFront distribution ID

**Error Conditions:**
- OIDC authentication fails → Abort with AWS error
- Invalid role ARN → Abort with error
- Insufficient permissions → Abort with AWS error

#### Step 7: Deploy to S3

**Purpose:** Upload files to S3 bucket

**Actions:**
```bash
aws s3 sync output/ s3://$BUCKET$DEPLOY_PATH \
  --delete \
  --cache-control "$CACHE_CONTROL" \
  --metadata-directive REPLACE
```

**Parameters:**
- `--delete`: Remove files not in source (for main branch updates)
- `--cache-control`: Set HTTP cache headers
- `--metadata-directive REPLACE`: Overwrite existing metadata

**Error Conditions:**
- S3 upload fails → Abort with AWS error
- Permission denied → Abort with error
- Bucket doesn't exist → Abort with error

#### Step 8: Invalidate CloudFront Cache

**Purpose:** Force CloudFront to serve updated files

**Actions:**
```bash
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "$DEPLOY_PATH*"
```

**Error Conditions:**
- Invalidation fails → Log warning but continue (non-critical)
- Invalid distribution ID → Abort with error

#### Step 9: Output Results

**Purpose:** Display deployment information

**Outputs:**
```
✅ Deployment successful!
📄 Resume URL: https://colinmca.com/r/a8f3k2j9/resume.pdf
🔧 Profile: technical
```

#### Step 10: Upload Artifacts

**Purpose:** Save build artifacts for debugging

**Artifacts:**
- `output/` directory (HTML, PDF, JSON)
- `resume.yaml` (master resume)
- `active_profile.txt` (job branches)
- `resume_token.txt` (job branches)

**Retention:** 30 days

---

## Error Handling

### Error Categories

#### 1. Configuration Errors

**Missing Files:**
```bash
if [[ ! -f "resume_builder/active_profile.txt" ]]; then
  echo "::error::Missing active_profile.txt in resume_builder/"
  echo "::notice::Please create the file with the desired profile name"
  echo "::notice::Example: echo 'technical' > resume_builder/active_profile.txt"
  exit 1
fi
```

**Invalid Token Format:**
```bash
if ! [[ "$TOKEN" =~ ^[a-zA-Z0-9]{8,16}$ ]]; then
  echo "::error::Invalid token format: $TOKEN"
  echo "::notice::Token must be 8-16 alphanumeric characters (a-zA-Z0-9)"
  echo "::notice::Example: a8f3k2j9"
  exit 1
fi
```

**Profile Not Found:**
```bash
if [[ ! -f "resume_builder/profiles/${PROFILE}.yaml" ]]; then
  echo "::error::Profile '${PROFILE}' not found"
  echo "::notice::Available profiles:"
  ls -1 resume_builder/profiles/*.yaml | xargs -n1 basename | sed 's/.yaml$//'
  exit 1
fi
```

#### 2. Build Errors

**YAML Parsing Error:**
```python
try:
    with open('resume.yaml', 'r') as f:
        resume_data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"::error::YAML parsing failed: {e}")
    print(f"::notice::Check resume.yaml for syntax errors")
    sys.exit(1)
```

**Profile Filtering Error:**
```python
try:
    filtered_resume = profile_manager.filter_resume(resume_data, profile)
except Exception as e:
    print(f"::error::Profile filtering failed: {e}")
    print(f"::notice::Profile: {profile}")
    sys.exit(1)
```

**PDF Generation Error:**
```bash
if ! wkhtmltopdf --enable-local-file-access output/resume.html output/resume.pdf; then
  echo "::error::PDF generation failed"
  echo "::notice::Check output/resume.html for rendering issues"
  exit 1
fi
```

#### 3. Deployment Errors

**S3 Upload Error:**
```bash
if ! aws s3 sync output/ s3://$BUCKET$DEPLOY_PATH --delete; then
  echo "::error::S3 upload failed"
  echo "::notice::Check AWS credentials and bucket permissions"
  exit 1
fi
```

**CloudFront Invalidation Error:**
```bash
if ! aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "$DEPLOY_PATH*"; then
  echo "::warning::CloudFront invalidation failed (non-critical)"
  echo "::notice::Files deployed but cache not invalidated. May take up to TTL to see changes."
fi
```

### Retry Logic

For transient failures (network issues, AWS throttling):

```bash
retry_command() {
  local max_attempts=3
  local delay=2
  local attempt=1

  while [[ $attempt -le $max_attempts ]]; do
    if "$@"; then
      return 0
    else
      echo "::warning::Command failed (attempt $attempt/$max_attempts)"
      if [[ $attempt -lt $max_attempts ]]; then
        echo "::notice::Retrying in ${delay}s..."
        sleep $delay
        delay=$((delay * 2))  # Exponential backoff
      fi
      attempt=$((attempt + 1))
    fi
  done

  return 1
}

# Usage
retry_command aws s3 sync output/ s3://$BUCKET$DEPLOY_PATH --delete
```

---

## Secret Management

### Required GitHub Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `AWS_ROLE_ARN` | IAM role for OIDC authentication | `arn:aws:iam::123456789012:role/GitHubActionsResumeDeployment` |
| `AWS_REGION` | AWS region for deployment | `us-east-1` |
| `AWS_S3_BUCKET` | S3 bucket name | `colin-resume-hosting` |
| `AWS_CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | `E1234ABCDEFGHI` |

### Setting Up Secrets

**Via GitHub CLI:**
```bash
gh secret set AWS_ROLE_ARN --body "arn:aws:iam::123456789012:role/GitHubActionsResumeDeployment"
gh secret set AWS_REGION --body "us-east-1"
gh secret set AWS_S3_BUCKET --body "colin-resume-hosting"
gh secret set AWS_CLOUDFRONT_DISTRIBUTION_ID --body "E1234ABCDEFGHI"
```

**Via GitHub Web UI:**
1. Navigate to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"

### Security Best Practices

1. **Use OIDC (OpenID Connect):** Avoid long-lived AWS access keys
2. **Least Privilege:** IAM role should only have permissions needed
3. **Audit Logs:** Enable CloudTrail for deployment auditing
4. **Rotate Secrets:** If using access keys, rotate every 90 days
5. **Limit Scope:** Use repository secrets, not organization secrets

---

## Testing Strategy

### Local Testing

**Test Branch Detection:**
```bash
# Simulate main branch
export GITHUB_REF="refs/heads/main"
./scripts/detect_branch_type.sh

# Simulate job branch
export GITHUB_REF="refs/heads/resume/test-job"
./scripts/detect_branch_type.sh
```

**Test Build Process:**
```bash
# Create test job branch
git checkout -b resume/test-local
echo "technical" > resume_builder/active_profile.txt
echo "testtoken123" > resume_builder/resume_token.txt

# Run build locally
cd resume_builder
python3 yaml_loader.py --profile technical
python3 html_generator.py --profile technical
python3 md_generator.py --profile technical
cd ..

pandoc resume_builder/resume.md -f markdown -t html -c css/resume-stylesheet.css -s -o output/resume.html
wkhtmltopdf --enable-local-file-access output/resume.html output/resume.pdf

# Verify PDF
ls -lh output/resume.pdf
```

### GitHub Actions Testing

**Method 1: Workflow Dispatch**
1. Navigate to Actions → Build and Deploy Resume
2. Click "Run workflow"
3. Select branch, profile (optional), and branch type
4. Click "Run workflow"
5. Monitor logs for errors

**Method 2: Push to Test Branch**
```bash
git checkout -b resume/test-github-actions
echo "leadership" > resume_builder/active_profile.txt
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)))" > resume_builder/resume_token.txt
git add .
git commit -m "Test GitHub Actions deployment"
git push -u origin resume/test-github-actions
```

### Test Cases

| Test Case | Branch | Expected Result |
|-----------|--------|-----------------|
| Main branch build | `main` | Deploy to `/`, default profile |
| Job branch with technical profile | `resume/test-tech` | Deploy to `/r/{token}/`, technical profile |
| Job branch with leadership profile | `resume/test-lead` | Deploy to `/r/{token}/`, leadership profile |
| Missing active_profile.txt | `resume/test-missing-profile` | ❌ Error: Missing file |
| Invalid token format | `resume/test-bad-token` | ❌ Error: Invalid token |
| Non-existent profile | `resume/test-bad-profile` | ❌ Error: Profile not found |
| Manual workflow dispatch | Any | Use specified profile |

---

## Troubleshooting

### Common Issues

#### Issue 1: "Profile not found" Error

**Symptoms:**
```
Error: Profile 'technical' not found in resume_builder/profiles/
Available profiles:
default
leadership
```

**Cause:** Profile name mismatch or typo

**Solution:**
1. Check `active_profile.txt` for correct profile name (case-sensitive)
2. Verify profile file exists: `ls resume_builder/profiles/`
3. Ensure profile file is named `{profile}.yaml` not `{profile}.yml`

#### Issue 2: "Invalid token format" Error

**Symptoms:**
```
Error: Invalid token format. Must be 8-16 alphanumeric characters.
Got: test_token_123
```

**Cause:** Token contains invalid characters (underscores, hyphens)

**Solution:**
```bash
# Generate valid token
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)))" > resume_builder/resume_token.txt
```

#### Issue 3: AWS Authentication Failed

**Symptoms:**
```
Error: Unable to assume role arn:aws:iam::123456789012:role/GitHubActionsResumeDeployment
```

**Cause:** OIDC not configured or IAM trust policy incorrect

**Solution:**
1. Verify OIDC provider exists in AWS IAM
2. Check IAM role trust policy includes GitHub repository
3. Verify `AWS_ROLE_ARN` secret is correct

#### Issue 4: PDF Generation Fails

**Symptoms:**
```
Error: PDF file too small (1234 bytes), likely generation error
```

**Cause:** wkhtmltopdf rendering error or missing CSS

**Solution:**
1. Check `output/resume.html` renders correctly in browser
2. Verify CSS file path is correct
3. Check for JavaScript errors in HTML
4. Try generating PDF locally to debug

#### Issue 5: S3 Upload Permission Denied

**Symptoms:**
```
Error: Access Denied (Service: Amazon S3; Status Code: 403)
```

**Cause:** IAM role lacks S3 permissions

**Solution:**
1. Verify IAM role has `s3:PutObject` permission
2. Check S3 bucket policy doesn't block uploads
3. Verify bucket name is correct in `AWS_S3_BUCKET` secret

### Debug Mode

Enable detailed logging for debugging:

```yaml
- name: Enable debug logging
  run: |
    echo "::debug::Branch: $GITHUB_REF"
    echo "::debug::Commit: $GITHUB_SHA"
    echo "::debug::Profile: $PROFILE"
    echo "::debug::Token: ${TOKEN:0:4}****"  # Partial token for security
    echo "::debug::Deploy path: $DEPLOY_PATH"

    # List files being deployed
    echo "::debug::Files to deploy:"
    ls -lh output/
```

---

## Performance Optimization

### Caching Strategies

**Pip Cache:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**System Dependency Cache:**
```yaml
- name: Cache Pandoc and wkhtmltopdf
  uses: actions/cache@v4
  with:
    path: |
      pandoc-3.0.1-1-amd64.deb
      wkhtmltox_0.12.6.1-2.jammy_amd64.deb
    key: system-deps-v1

- name: Install system dependencies
  run: |
    # Use cached .deb files if available
    if [[ ! -f pandoc-3.0.1-1-amd64.deb ]]; then
      wget -q https://github.com/jgm/pandoc/releases/download/3.0.1/pandoc-3.0.1-1-amd64.deb
    fi
    # ... rest of installation
```

### Parallel Builds

For multiple profiles:

```yaml
strategy:
  matrix:
    profile: [default, leadership, technical]

steps:
  - name: Build resume
    run: |
      python3 build_resume.py --profile ${{ matrix.profile }}
```

---

## Monitoring and Logging

### Workflow Metrics

**Track the following:**
- Build duration (should be <3 minutes)
- Success rate (target: >95%)
- Deployment frequency
- Error types and frequency

### Notification Strategy

**Success Notifications:**
- GitHub Actions UI (green checkmark)
- Optional: Slack webhook for deployments

**Failure Notifications:**
- GitHub Actions UI (red X)
- Email to repository owner (GitHub default)
- Optional: Create GitHub Issue on failure

**Example Issue Creation on Failure:**
```yaml
- name: Create issue on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Build failed for ${{ github.ref }}',
        body: 'Build failed in run ${{ github.run_id }}\n\nView logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}',
        labels: ['build-failure', 'automated']
      })
```

---

## Future Enhancements

1. **Multi-Region Deployment:** Deploy to multiple S3 buckets/regions
2. **Preview Deployments:** Deploy PR branches to `/preview/{pr-number}/`
3. **Rollback Capability:** Restore previous deployment if validation fails
4. **Visual Regression Testing:** Compare PDF outputs before deployment
5. **Scheduled Rebuilds:** Rebuild main branch weekly to catch drift
6. **Dependency Updates:** Automated PRs for Python package updates

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Actions: Configure Credentials](https://github.com/aws-actions/configure-aws-credentials)
- [GitHub OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

**Document Status:** ✅ Complete - Ready for Implementation
**Next Steps:** Create workflow file, configure secrets, test deployment
