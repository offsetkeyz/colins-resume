# Dynamic YAML-Based Resume System - Master Task List

**Project Owner:** Colin McAllister
**Created:** 2025-11-21
**Status:** Ready for Implementation
**Total Estimated Hours:** 150-195 hours
**Current Branch:** claude/create-task-list-014MrVUCxe7KELyZ7SgDuQst

---

## Quick Reference

| Phase | Duration | Hours | Status | Progress |
|-------|----------|-------|--------|----------|
| Phase 1: Foundation & Migration | 1.5-2 weeks | 28 hours | Not Started | 0/5 tasks |
| Phase 2: Generator Updates | 1.5 weeks | 21 hours | Not Started | 0/6 tasks |
| Phase 3: Branch Workflow & Automation | 1 week | 23 hours | Not Started | 0/5 tasks |
| Phase 4: Content Enhancement & Testing | 1 week | 21 hours | Not Started | 0/5 tasks |
| Phase 5: Polish & Future-Proofing | 3-5 days | 19 hours | Not Started | 0/5 tasks |
| **TOTAL** | **6-8 weeks** | **112 hours** | **Planning Complete** | **0/26 tasks** |

---

## PHASE 1: FOUNDATION & MIGRATION
**Duration:** 1.5-2 weeks | **Goal:** Migrate to YAML and establish core infrastructure with validation

### Task 1.1: YAML Schema & Validation
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Create comprehensive YAML schema and validation system to ensure data integrity throughout the project.

#### Subtasks
- [ ] Create `resume-schema.yaml` based on existing JSON schema
- [ ] Add validation rules for `include_in` tags
- [ ] Write Python validator script
- [ ] Document schema with inline comments

#### Deliverables
- `resume_builder/resume-schema.yaml`
- Validation script with error reporting

#### Acceptance Criteria
- Schema validates all required fields
- `include_in` tag validation works correctly
- Clear error messages for validation failures
- Documentation includes examples

#### Dependencies
- None (can start immediately)

---

### Task 1.2: Convert resume.json → resume.yaml
**Estimated:** 6 hours | **Status:** [ ] Not Started

#### Description
Safely migrate existing JSON resume data to YAML format with comprehensive logging and backup procedures.

#### Subtasks
- [ ] Write conversion script `migrate_json_to_yaml.py` with comprehensive logging
- [ ] Back up current resume.json to `resume.json.backup`
- [ ] Run conversion on current resume.json
- [ ] Generate conversion report (fields converted, warnings, etc.)
- [ ] Manually review output for accuracy
- [ ] Add `include_in: [all]` to every existing item (default)
- [ ] Validate YAML syntax and schema compliance

#### Deliverables
- `resume_builder/resume.yaml`
- `resume.json.backup`
- Conversion report document
- Migration log with statistics

#### Acceptance Criteria
- All JSON data successfully converted to YAML
- Backup file created before conversion
- Conversion report shows zero data loss
- YAML passes schema validation
- All items tagged with `include_in: [all]`

#### Dependencies
- Task 1.1 (schema must exist for validation)

---

### Task 1.3: Create Profile System
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Establish the profile system infrastructure with three initial profiles for different resume variations.

#### Subtasks
- [ ] Create `profiles/` directory structure
- [ ] Write `default.yaml` profile (includes everything)
- [ ] Write `leadership.yaml` profile
- [ ] Write `technical.yaml` profile
- [ ] Document profile creation guide

#### Deliverables
- `resume_builder/profiles/default.yaml`
- `resume_builder/profiles/leadership.yaml`
- `resume_builder/profiles/technical.yaml`
- Profile creation documentation

#### Profile Specifications

**default.yaml:**
```yaml
profile:
  name: "Full Resume"
  description: "Complete resume with all experience"
  slug: "default"
filters:
  include_tags: [all]
output:
  title_suffix: ""
  filename: "resume"
```

**leadership.yaml:**
```yaml
profile:
  name: "Leadership Focused"
  description: "Emphasizes people management and team leadership"
  slug: "leadership"
filters:
  include_tags: [leadership, management, all]
  max_bullets_per_job: 4
output:
  title_suffix: " - Leadership Focus"
  filename: "resume-leadership"
```

**technical.yaml:**
```yaml
profile:
  name: "Technical Focused"
  description: "Emphasizes technical skills and development"
  slug: "technical"
filters:
  include_tags: [technical, development, all]
  max_bullets_per_job: 4
output:
  title_suffix: " - Technical Focus"
  filename: "resume-technical"
```

#### Acceptance Criteria
- All 3 profiles load without errors
- Each profile has distinct configuration
- Documentation explains how to create new profiles
- Profile YAML validates against schema

#### Dependencies
- Task 1.1 (schema needed for profile validation)

---

### Task 1.4: Build Profile Manager
**Estimated:** 8 hours | **Status:** [ ] Not Started

#### Description
Create the core filtering logic that applies profile rules to resume data.

#### Subtasks
- [ ] Create `profile_manager.py`
- [ ] Implement tag filtering logic
- [ ] Add max_bullets_per_job limiting
- [ ] Write unit tests for filtering (see test cases below)
- [ ] Test with edge cases (missing tags, empty profiles, etc.)

#### Deliverables
- `resume_builder/profile_manager.py`
- Unit test suite with 85%+ coverage
- Test report document

#### Key Functions
```python
def load_profile(profile_name: str) -> dict:
    """Load profile configuration from profiles/ directory."""

def filter_resume_data(resume_data: dict, profile: dict) -> dict:
    """Apply profile filters to resume data."""

def filter_items(items: list, include_tags: list) -> list:
    """Filter list items based on include_in tags."""

def apply_bullet_limit(bullets: list, max_bullets: int) -> list:
    """Limit number of bullets per job."""
```

#### Unit Test Cases

**Test Suite 1: Tag Filtering**
- [ ] test_include_in_filtering()
- [ ] test_missing_include_in_tag()
- [ ] test_all_tag_includes_everywhere()
- [ ] test_multiple_tags_on_item()

**Test Suite 2: Max Bullets Limiting**
- [ ] test_max_bullets_per_job()
- [ ] test_max_bullets_with_filtering()
- [ ] test_no_bullet_limit()

**Test Suite 3: Edge Cases**
- [ ] test_profile_not_found()
- [ ] test_empty_profile()
- [ ] test_nested_filtering()
- [ ] test_malformed_tags()

#### Acceptance Criteria
- All unit tests pass
- Code coverage ≥ 85%
- Profile manager filters correctly for all 3 profiles
- Edge cases handled gracefully
- Performance: Filter 1000 items in <100ms

#### Dependencies
- Task 1.2 (needs resume.yaml to test against)
- Task 1.3 (needs profiles to load)

---

### Task 1.5: Migration Validation
**Estimated:** 6 hours | **Status:** [ ] Not Started

#### Description
Comprehensive validation that YAML system produces identical output to JSON system with zero data loss.

#### Subtasks
- [ ] Create YAML→JSON export function for comparison
- [ ] Build resume using JSON system (baseline)
- [ ] Build resume using YAML system (new)
- [ ] Automated comparison tests:
  - [ ] Compare generated HTML (diff should be minimal)
  - [ ] Compare generated PDF metadata (page count, file size)
  - [ ] Verify all content fields present in both outputs
  - [ ] Check for data loss or corruption
- [ ] Manual review of both PDFs side-by-side
- [ ] Document any intentional differences
- [ ] Create rollback procedure if validation fails
- [ ] Keep `resume.json.backup` until Phase 4 complete

#### Deliverables
- Validation test suite
- Validation report document
- Rollback procedure documentation
- Side-by-side comparison screenshots

#### Validation Checklist
- [ ] HTML output comparison: < 5% difference (whitespace excluded)
- [ ] PDF page count identical
- [ ] All work experiences present
- [ ] All skills present
- [ ] All education entries present
- [ ] All projects present
- [ ] Contact information identical
- [ ] Formatting preserved
- [ ] No encoding issues
- [ ] Links functional

#### Acceptance Criteria
- Automated validation passes all checks
- Manual PDF review shows no quality degradation
- Validation report shows zero data loss
- Rollback procedure documented and tested
- Confidence level: 95%+ that YAML system works correctly

#### Dependencies
- Task 1.4 (needs profile manager to generate YAML output)
- Existing JSON system (must remain functional during validation)

---

### PHASE 1 ACCEPTANCE CRITERIA

**Must Complete Before Moving to Phase 2:**
- ✅ resume.yaml validates successfully
- ✅ All 3 profiles load without errors
- ✅ Profile manager filters content correctly
- ✅ Unit tests pass with 85%+ coverage
- ✅ YAML-generated output matches JSON-generated output (content-wise)
- ✅ No data loss detected in migration
- ✅ Rollback procedure documented and tested

**Phase 1 Deliverables:**
- `/home/user/colins-resume/resume_builder/resume-schema.yaml`
- `/home/user/colins-resume/resume_builder/resume.yaml`
- `/home/user/colins-resume/resume_builder/profiles/` (3 profiles)
- `/home/user/colins-resume/resume_builder/profile_manager.py`
- Validation report
- Migration documentation

---

## PHASE 2: GENERATOR UPDATES
**Duration:** 1.5 weeks | **Goal:** Update all generators to use YAML and profiles with parallel validation

### Task 2.1: Update HTML Generator
**Estimated:** 5 hours | **Status:** [ ] Not Started

#### Description
Modify HTML generator to load YAML data and integrate profile filtering.

#### Subtasks
- [ ] Replace JSON loading with YAML loading
- [ ] Integrate profile_manager for content filtering
- [ ] Test with all 3 profiles
- [ ] Verify HTML output quality

#### Deliverables
- Updated `html_generator.py`
- Test results for all 3 profiles
- HTML output samples

#### Acceptance Criteria
- HTML generates successfully from YAML
- Profile filtering works correctly
- Output quality maintained
- All 3 profiles produce valid HTML

#### Dependencies
- Task 1.4 (profile_manager must exist)
- Task 1.5 (YAML system validated)

---

### Task 2.2: Update Markdown Generator
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Modify Markdown generator to load YAML data and integrate profile filtering.

#### Subtasks
- [ ] Replace JSON loading with YAML loading
- [ ] Integrate profile_manager
- [ ] Test markdown → HTML → PDF pipeline

#### Deliverables
- Updated `md_generator.py`
- Test results for markdown pipeline

#### Acceptance Criteria
- Markdown generates successfully from YAML
- Profile filtering works correctly
- PDF output quality maintained

#### Dependencies
- Task 1.4 (profile_manager must exist)
- Task 2.1 (HTML generator provides reference implementation)

---

### Task 2.3: Create JSON Export
**Estimated:** 3 hours | **Status:** [ ] Not Started

#### Description
Create JSON export functionality for API output and future dynamic website loading.

#### Subtasks
- [ ] Add `json_generator.py` for API output
- [ ] Export filtered resume as JSON
- [ ] Test JSON output structure

#### Deliverables
- `json_generator.py`
- Sample JSON outputs for each profile

#### Purpose
- Used for future dynamic website loading
- API endpoint data source
- Alternative output format

#### Acceptance Criteria
- JSON exports successfully from YAML
- Profile filtering applied correctly
- Valid JSON structure
- All data fields preserved

#### Dependencies
- Task 1.4 (profile_manager for filtering)

---

### Task 2.4: Update Build Scripts
**Estimated:** 3 hours | **Status:** [ ] Not Started

#### Description
Update local build scripts to support YAML input and profile selection.

#### Subtasks
- [ ] Update `build_all.sh` to use YAML
- [ ] Add profile parameter support
- [ ] Test local builds with all profiles

#### Deliverables
- Updated `build_all.sh`
- Build script documentation

#### New Command Format
```bash
# Build with default profile
./build_all.sh

# Build with specific profile
./build_all.sh --profile leadership

# Build all profiles
./build_all.sh --all-profiles
```

#### Acceptance Criteria
- Build script works with YAML input
- Profile selection functions correctly
- All 3 profiles build successfully locally
- Error messages clear and helpful

#### Dependencies
- Tasks 2.1, 2.2, 2.3 (all generators updated)

---

### Task 2.5: Parallel Running Period
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Run JSON and YAML systems in parallel for one week to validate consistency and catch edge cases.

#### Subtasks
- [ ] Keep both JSON and YAML systems functional
- [ ] Build outputs from both systems for comparison
- [ ] Run for at least 1 week in parallel
- [ ] Monitor for discrepancies or issues
- [ ] Final validation before JSON removal

#### Deliverables
- Parallel running report
- Discrepancy log (if any)
- Confidence assessment

#### Validation Activities
- [ ] Daily builds from both systems
- [ ] Compare outputs every 2 days
- [ ] Test all profiles multiple times
- [ ] Document any differences found
- [ ] Fix issues discovered during parallel run

#### Acceptance Criteria
- Both systems run without conflicts
- Output consistency ≥ 99%
- All discrepancies investigated and resolved
- Team confidence level: 95%+ in YAML system

#### Dependencies
- Task 2.4 (build scripts must support both systems)

---

### Task 2.6: Remove JSON Dependencies
**Estimated:** 2 hours | **Status:** [ ] Not Started

#### Description
Clean transition from JSON to YAML by archiving old system after successful validation.

#### Subtasks
- [ ] Rename `resume.json` to `resume.json.deprecated`
- [ ] Move to `archive/` directory (keep for reference)
- [ ] Update documentation to reference YAML
- [ ] Remove JSON-specific code paths
- [ ] Update build scripts to YAML-only

#### Deliverables
- `archive/resume.json.deprecated`
- Updated documentation
- Clean codebase

#### What Gets Archived
- `resume.json` → `archive/resume.json.deprecated`
- Old JSON loading functions (commented, not deleted)
- JSON-specific documentation

#### What Gets Updated
- All README references
- Build scripts
- Generator imports
- Documentation links

#### Acceptance Criteria
- JSON system fully archived (not deleted)
- YAML system is primary
- No broken references in code
- Documentation reflects new system
- Archive is clearly labeled

#### Dependencies
- Task 2.5 (parallel running must complete successfully)

---

### PHASE 2 ACCEPTANCE CRITERIA

**Must Complete Before Moving to Phase 3:**
- ✅ Generate HTML from YAML successfully
- ✅ Generate PDF from YAML successfully
- ✅ All 3 profiles produce valid outputs
- ✅ Parallel running validates consistency
- ✅ JSON system archived (not deleted)
- ✅ Local builds work with `./build_all.sh --profile leadership`
- ✅ Visual comparison shows no quality degradation

**Phase 2 Deliverables:**
- Updated `html_generator.py`
- Updated `md_generator.py`
- New `json_generator.py`
- Updated `build_all.sh`
- Parallel running report
- Archived JSON system

---

## PHASE 3: BRANCH WORKFLOW & AUTOMATION
**Duration:** 1 week | **Goal:** Implement job branch workflow with GitHub Actions

### Task 3.1: Token Generation System
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Create secure token generation system for private resume URLs.

#### Subtasks
- [ ] Create `generate_token.py` script
- [ ] Generate 8-12 character secure tokens
- [ ] Write token to `resume_token.txt`
- [ ] Add token to .gitignore (or commit based on preference)

#### Deliverables
- `scripts/generate_token.py`
- Token generation documentation

#### Token Requirements
- Length: 8-12 characters
- Character set: a-z, A-Z, 0-9
- Cryptographically secure (using `secrets` module)
- Collision probability: < 0.0001%
- No offensive words (use word filter)

#### Implementation Example
```python
import secrets
import string

def generate_token(length=10):
    """Generate cryptographically secure token."""
    alphabet = string.ascii_lowercase + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token
```

#### Acceptance Criteria
- Tokens are cryptographically secure
- Token length configurable
- No duplicate tokens generated in 10,000 runs
- Clear documentation on usage

#### Dependencies
- None (can start immediately)

---

### Task 3.2: Branch Template
**Estimated:** 3 hours | **Status:** [ ] Not Started

#### Description
Create automated script for setting up new job application branches with all required files.

#### Subtasks
- [ ] Create `templates/job-branch-setup.sh`
- [ ] Script creates new job branch
- [ ] Adds `active_profile.txt`
- [ ] Generates and adds `resume_token.txt`

#### Deliverables
- `templates/job-branch-setup.sh`
- Branch setup documentation

#### Script Usage
```bash
# Create new job branch
./templates/job-branch-setup.sh aws-security-eng leadership

# Creates:
# - Branch: resume/aws-security-eng
# - File: resume_builder/active_profile.txt (contains: "leadership")
# - File: resume_builder/resume_token.txt (contains: random token)
```

#### Script Features
- [ ] Branch naming validation
- [ ] Profile existence check
- [ ] Automatic token generation
- [ ] Git operations (branch, commit)
- [ ] Success confirmation message

#### Acceptance Criteria
- Script creates branch successfully
- All required files generated
- Profile name validated
- Token generated automatically
- Clear success/error messages

#### Dependencies
- Task 3.1 (token generation script)

---

### Task 3.3: Enhanced GitHub Actions
**Estimated:** 8 hours | **Status:** [ ] Not Started

#### Description
Update GitHub Actions workflow to support branch-specific builds with profile filtering and token-based deployment.

#### Subtasks
- [ ] Update `.github/workflows/build-resume.yml`
- [ ] Detect branch type (main vs resume/*)
- [ ] Read active_profile.txt from job branches
- [ ] Load master resume.yaml from main branch
- [ ] Apply profile filtering
- [ ] Read resume_token.txt
- [ ] Deploy to S3 with token path

#### Deliverables
- Updated `.github/workflows/build-resume.yml`
- Workflow documentation
- Test results for main and job branches

#### Workflow Logic

**For Main Branch:**
```yaml
- Use default profile
- Deploy to: https://colinmca.com/
- Standard deployment path
```

**For Job Branches (resume/*):**
```yaml
- Read active_profile.txt
- Read resume_token.txt
- Load profile from main branch
- Filter resume data
- Generate HTML/PDF/JSON
- Deploy to: https://colinmca.com/r/{token}/
```

#### Key Workflow Steps
1. **Branch Detection:**
   ```yaml
   - name: Detect Branch Type
     run: |
       if [[ ${{ github.ref }} == refs/heads/main ]]; then
         echo "BRANCH_TYPE=main" >> $GITHUB_ENV
       elif [[ ${{ github.ref }} == refs/heads/resume/* ]]; then
         echo "BRANCH_TYPE=job" >> $GITHUB_ENV
       fi
   ```

2. **Profile Loading:**
   ```yaml
   - name: Load Active Profile
     if: env.BRANCH_TYPE == 'job'
     run: |
       PROFILE=$(cat resume_builder/active_profile.txt)
       echo "ACTIVE_PROFILE=$PROFILE" >> $GITHUB_ENV
   ```

3. **Token Reading:**
   ```yaml
   - name: Read Resume Token
     if: env.BRANCH_TYPE == 'job'
     run: |
       TOKEN=$(cat resume_builder/resume_token.txt)
       echo "RESUME_TOKEN=$TOKEN" >> $GITHUB_ENV
   ```

#### Acceptance Criteria
- Workflow detects branch type correctly
- Reads profile and token from job branches
- Applies profile filtering correctly
- Deploys to correct S3 path
- Main branch deployment unaffected
- Clear logs for debugging

#### Dependencies
- Task 3.2 (branch setup must create required files)
- Phase 2 complete (generators must use YAML)

---

### Task 3.4: S3 Deployment Updates
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Update AWS S3 bucket structure and CloudFront configuration to support token-based paths.

#### Subtasks
- [ ] Update S3 bucket structure for `/r/{token}/` paths
- [ ] Configure CloudFront for new paths
- [ ] Test file uploads to token paths
- [ ] Verify URL access

#### Deliverables
- Updated S3 bucket policy
- CloudFront distribution configuration
- Deployment test results

#### S3 Structure
```
s3://colins-resume-bucket/
├── index.html (main site)
├── resume.pdf (main site)
├── resume.json (main site)
└── r/
    ├── a8f3k2j9/
    │   ├── resume.html
    │   ├── resume.pdf
    │   └── resume.json
    └── b9j4m3k1/
        ├── resume.html
        ├── resume.pdf
        └── resume.json
```

#### CloudFront Configuration
- [ ] Enable directory browsing: OFF
- [ ] Default root object: index.html
- [ ] Error pages: 404 → 403 (hide structure)
- [ ] Cache policy: Standard (1 hour TTL)
- [ ] HTTPS only

#### Security Considerations
- [ ] No directory listing
- [ ] Tokens not guessable
- [ ] No robots.txt for /r/ paths
- [ ] X-Robots-Tag: noindex header

#### Acceptance Criteria
- Files upload to token paths successfully
- URLs accessible: `https://colinmca.com/r/{token}/resume.pdf`
- Directory listing disabled
- CloudFront caches correctly
- HTTPS enforced

#### Dependencies
- Task 3.1 (token generation)
- AWS credentials configured

---

### Task 3.5: Documentation
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Create comprehensive documentation for job branch workflow and troubleshooting.

#### Subtasks
- [ ] Write "Creating a Job Application Branch" guide
- [ ] Document profile selection process
- [ ] Explain token system
- [ ] Create troubleshooting guide

#### Deliverables
- `docs/job-branch-workflow.md`
- `docs/troubleshooting.md`
- Updated README.md

#### Documentation Sections

**Creating a Job Application Branch:**
1. Choose appropriate profile
2. Run setup script
3. Verify files created
4. Push branch
5. Get resume URL

**Profile Selection Guide:**
- When to use leadership profile
- When to use technical profile
- Creating custom profiles

**Token System:**
- How tokens are generated
- Token security
- Managing multiple tokens
- Token expiration (future)

**Troubleshooting:**
- Build failures
- Profile not found errors
- Token deployment issues
- URL not accessible

#### Acceptance Criteria
- Documentation is clear and complete
- Includes examples and screenshots
- Troubleshooting covers common issues
- Easy for new users to follow

#### Dependencies
- Tasks 3.1-3.4 (all features must be implemented)

---

### PHASE 3 ACCEPTANCE CRITERIA

**Must Complete Before Moving to Phase 4:**
- ✅ Create new job branch in <5 minutes
- ✅ Push to job branch triggers build
- ✅ PDF deploys to https://colinmca.com/r/{token}/resume.pdf
- ✅ URL is accessible and private (not indexed)
- ✅ Documentation is clear and complete

**Phase 3 Deliverables:**
- Token generation script
- Branch setup script
- Updated GitHub Actions workflow
- AWS infrastructure configuration
- Comprehensive documentation

---

## PHASE 4: CONTENT ENHANCEMENT & TESTING
**Duration:** 1 week | **Goal:** Populate master resume and validate all workflows

### Task 4.1: Master Resume Expansion
**Estimated:** 6 hours | **Status:** [ ] Not Started

#### Description
Expand master resume with all hidden content and tag everything appropriately.

#### Subtasks
- [ ] Review current resume content
- [ ] Add all "hidden" experiences/bullets you've removed over time
- [ ] Add alternative phrasings for key achievements
- [ ] Tag everything with appropriate `include_in` values

#### Deliverables
- Comprehensive `resume.yaml` (150%+ of current content)
- Tagging documentation

#### Content Expansion Goals
- **Current:** ~50 experience bullets
- **Target:** ~75-100 experience bullets
- **Profiles:** Each shows 30-40 bullets after filtering

#### Tagging Strategy
```yaml
# Leadership-focused items
include_in: [leadership, management, all]

# Technical-focused items
include_in: [technical, development, all]

# Universal items (appear in all profiles)
include_in: [all]

# Specific profile only
include_in: [leadership]
```

#### Content Areas to Expand
- [ ] Work experience bullets (add 20-30 more)
- [ ] Skills (categorize with tags)
- [ ] Projects (tag by focus area)
- [ ] Alternative achievement phrasings
- [ ] Detailed technical accomplishments
- [ ] Leadership/management achievements

#### Acceptance Criteria
- Master resume has 150%+ content vs current
- Every item has appropriate tags
- No untagged content
- Validation passes
- Resume still readable and maintainable

#### Dependencies
- Phase 2 complete (YAML system working)

---

### Task 4.2: Profile Refinement
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Test and refine profiles to ensure optimal output quality and length.

#### Subtasks
- [ ] Test leadership profile output
- [ ] Test technical profile output
- [ ] Adjust filters based on output
- [ ] Ensure PDF length is appropriate (1-2 pages)

#### Deliverables
- Refined profile configurations
- Sample PDFs for each profile
- Profile optimization report

#### Refinement Checklist

**Leadership Profile:**
- [ ] Emphasizes team management
- [ ] Highlights strategic thinking
- [ ] Shows impact on people/process
- [ ] 1-2 pages in length
- [ ] Professional appearance

**Technical Profile:**
- [ ] Emphasizes technical skills
- [ ] Highlights system design
- [ ] Shows technical accomplishments
- [ ] 1-2 pages in length
- [ ] Technical depth appropriate

**Default Profile:**
- [ ] Balanced content
- [ ] Comprehensive but concise
- [ ] 2 pages maximum
- [ ] Professional formatting

#### Optimization Techniques
- Adjust max_bullets_per_job
- Refine include_tags
- Balance content distribution
- Optimize for readability

#### Acceptance Criteria
- All profiles produce high-quality PDFs
- Length appropriate (1-2 pages)
- Content relevant to profile focus
- No formatting issues
- Professional appearance maintained

#### Dependencies
- Task 4.1 (expanded content needed)

---

### Task 4.3: Create Test Job Branches
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Create test job branches to validate complete workflow from branch creation to deployment.

#### Subtasks
- [ ] Create `resume/test-leadership-role`
- [ ] Create `resume/test-technical-role`
- [ ] Verify builds and deployments
- [ ] Test PDF downloads

#### Deliverables
- 2 test branches with deployed resumes
- Test branch validation report
- Sample URLs for verification

#### Test Branches

**Test Branch 1: Leadership Focus**
```bash
./templates/job-branch-setup.sh test-leadership-role leadership

# Expected Output:
# Branch: resume/test-leadership-role
# Profile: leadership
# Token: abc123xyz (example)
# URL: https://colinmca.com/r/abc123xyz/resume.pdf
```

**Test Branch 2: Technical Focus**
```bash
./templates/job-branch-setup.sh test-technical-role technical

# Expected Output:
# Branch: resume/test-technical-role
# Profile: technical
# Token: def456uvw (example)
# URL: https://colinmca.com/r/def456uvw/resume.pdf
```

#### Validation Checklist
- [ ] Branch creation successful
- [ ] GitHub Actions triggered
- [ ] Build completed without errors
- [ ] PDF deployed to S3
- [ ] URL accessible
- [ ] Content matches profile
- [ ] Formatting correct
- [ ] Token unique

#### Acceptance Criteria
- Both test branches deploy successfully
- PDFs are accessible via tokens
- Content filtered correctly by profile
- No build errors
- Complete in <10 minutes per branch

#### Dependencies
- Phase 3 complete (workflow automation ready)
- Task 4.2 (profiles refined)

---

### Task 4.4: Integration Testing
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Comprehensive end-to-end testing of all system components.

#### Subtasks
- [ ] Test complete workflow end-to-end
- [ ] Verify all generators work
- [ ] Check PDF formatting and styling
- [ ] Validate private URLs

#### Deliverables
- Integration test report
- Test case results
- Bug tracking log (if issues found)

#### Test Cases

**TC-1: Main Branch Deployment**
- Push to main → default profile → https://colinmca.com

**TC-2: Leadership Job Branch**
- Create branch → push → leadership profile → token URL

**TC-3: Technical Job Branch**
- Create branch → push → technical profile → token URL

**TC-4: Profile Switching**
- Change active_profile.txt → rebuild → verify content changes

**TC-5: Token Security**
- Generate multiple tokens → verify uniqueness → test collision

**TC-6: Error Handling**
- Invalid profile → expect clear error
- Missing token → expect default behavior
- Malformed YAML → expect validation error

**TC-7: Performance**
- Build time < 3 minutes
- PDF generation < 30 seconds
- Deployment < 1 minute

#### Acceptance Criteria
- All test cases pass
- No critical bugs found
- Performance targets met
- Error handling works correctly
- Documentation accurate

#### Dependencies
- Task 4.3 (test branches created)

---

### Task 4.5: Main Branch Deployment
**Estimated:** 3 hours | **Status:** [ ] Not Started

#### Description
Deploy refined system to production main branch.

#### Subtasks
- [ ] Deploy default profile to https://colinmca.com
- [ ] Verify main website updates
- [ ] Test PDF download from main site

#### Deliverables
- Live production deployment
- Deployment verification report
- Rollback plan (if needed)

#### Pre-Deployment Checklist
- [ ] All Phase 4 tests passing
- [ ] Integration testing complete
- [ ] Test branches successful
- [ ] Backup of current main branch
- [ ] Rollback procedure ready

#### Deployment Steps
1. Merge to main branch
2. Trigger GitHub Actions build
3. Monitor build logs
4. Verify S3 deployment
5. Check CloudFront invalidation
6. Test live URLs
7. Verify PDF quality
8. Confirm no errors

#### Post-Deployment Verification
- [ ] https://colinmca.com loads correctly
- [ ] resume.pdf downloads successfully
- [ ] Content is current
- [ ] Formatting perfect
- [ ] Links functional
- [ ] Mobile responsive

#### Acceptance Criteria
- Main site deploys successfully
- PDF quality maintained
- No errors or warnings
- All functionality working
- Performance acceptable

#### Dependencies
- Task 4.4 (integration testing passed)

---

### PHASE 4 ACCEPTANCE CRITERIA

**Must Complete Before Moving to Phase 5:**
- ✅ Master resume contains 150%+ of normal resume content
- ✅ Leadership profile generates 1-2 page PDF
- ✅ Technical profile generates 1-2 page PDF
- ✅ Test branches deploy successfully
- ✅ Main website reflects new system

**Phase 4 Deliverables:**
- Expanded master resume
- Refined profiles
- Test job branches
- Integration test report
- Live production deployment

---

## PHASE 5: POLISH & FUTURE-PROOFING
**Duration:** 3-5 days | **Goal:** Add quality-of-life features and documentation

### Task 5.1: Error Handling
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Implement comprehensive error handling and validation across all components.

#### Subtasks
- [ ] Add validation error messages
- [ ] Handle missing profile gracefully
- [ ] Provide helpful GitHub Actions logs

#### Deliverables
- Enhanced error handling in all scripts
- Error documentation
- Error message guide

#### Error Scenarios

**Scenario 1: Profile Not Found**
```
ERROR: Profile 'nonexistent' not found in profiles/ directory.
Available profiles: default, leadership, technical
```

**Scenario 2: Invalid YAML**
```
ERROR: resume.yaml validation failed at line 45
Issue: Missing required field 'include_in' for work experience item
Fix: Add 'include_in: [all]' to the item
```

**Scenario 3: Missing Token**
```
WARNING: resume_token.txt not found, generating new token
Generated token: xyz789abc
```

**Scenario 4: Build Failure**
```
ERROR: PDF generation failed
Cause: wkhtmltopdf returned exit code 1
Solution: Check HTML output for invalid formatting
```

#### Error Handling Improvements
- [ ] Descriptive error messages
- [ ] Suggested fixes for common errors
- [ ] Graceful degradation where possible
- [ ] Clear GitHub Actions logs
- [ ] Stack traces for debugging

#### Acceptance Criteria
- All error scenarios have clear messages
- Users can self-diagnose issues
- GitHub Actions logs are helpful
- No cryptic error messages
- Graceful failure modes

#### Dependencies
- All previous phases complete

---

### Task 5.2: Monitoring & Logging
**Estimated:** 3 hours | **Status:** [ ] Not Started

#### Description
Add build metadata and logging for tracking resume versions and deployments.

#### Subtasks
- [ ] Log which profile was used for each build
- [ ] Track token generation
- [ ] Add build timestamps

#### Deliverables
- Build metadata system
- Logging configuration
- Build history tracking

#### Build Metadata
```json
{
  "build_id": "20250121-143052",
  "branch": "resume/aws-security-eng",
  "profile": "technical",
  "token": "abc123xyz",
  "timestamp": "2025-01-21T14:30:52Z",
  "commit": "a1b2c3d",
  "status": "success",
  "output_files": [
    "resume.html",
    "resume.pdf",
    "resume.json"
  ]
}
```

#### Logging Features
- [ ] Build start/end timestamps
- [ ] Profile loading logs
- [ ] Token generation logs
- [ ] Deployment logs
- [ ] Error logs with context
- [ ] Performance metrics

#### Acceptance Criteria
- Build metadata tracked for all builds
- Logs are searchable
- Build history accessible
- Performance metrics tracked

#### Dependencies
- Phase 3 complete (workflow automation)

---

### Task 5.3: Helper Scripts
**Estimated:** 4 hours | **Status:** [ ] Not Started

#### Description
Create convenience scripts for common workflows and operations.

#### Subtasks
- [ ] Create `new-job-application.sh` script
- [ ] Create `list-resume-urls.sh` to show all tokens
- [ ] Create `validate-resume.sh` for local testing

#### Deliverables
- `scripts/new-job-application.sh`
- `scripts/list-resume-urls.sh`
- `scripts/validate-resume.sh`
- Helper scripts documentation

#### Script Specifications

**new-job-application.sh**
```bash
#!/bin/bash
# Usage: ./scripts/new-job-application.sh <job-name> <profile>
# Example: ./scripts/new-job-application.sh aws-security-eng technical

# Features:
# - Validates profile exists
# - Creates branch
# - Generates token
# - Commits files
# - Pushes branch
# - Outputs resume URL
```

**list-resume-urls.sh**
```bash
#!/bin/bash
# Lists all job branches with their tokens and URLs

# Output:
# resume/aws-security-eng    technical    abc123xyz    https://colinmca.com/r/abc123xyz/resume.pdf
# resume/google-sre          leadership   def456uvw    https://colinmca.com/r/def456uvw/resume.pdf
```

**validate-resume.sh**
```bash
#!/bin/bash
# Validates resume.yaml locally before pushing

# Checks:
# - YAML syntax
# - Schema compliance
# - Tag validity
# - Profile references
# - Content completeness
```

#### Acceptance Criteria
- All scripts work without errors
- Clear usage documentation
- Error handling included
- User-friendly output

#### Dependencies
- Phase 3 complete (branch workflow)

---

### Task 5.4: Final Documentation
**Estimated:** 6 hours | **Status:** [ ] Not Started

#### Description
Create comprehensive final documentation for the entire system.

#### Subtasks
- [ ] Update README.md with new system
- [ ] Create architecture diagram
- [ ] Write migration guide (for future users)
- [ ] Add FAQ section

#### Deliverables
- Updated README.md
- Architecture documentation
- Migration guide
- FAQ document

#### Documentation Structure

**README.md Updates:**
- System overview
- Quick start guide
- Profile system explanation
- Job application workflow
- Local development setup
- Troubleshooting

**Architecture Documentation:**
- System diagram
- Data flow
- Component descriptions
- Technology stack
- Design decisions

**Migration Guide:**
- For users wanting to replicate system
- Step-by-step setup
- Configuration examples
- Customization options

**FAQ:**
- How do I create a new profile?
- How do I add new content?
- What if a build fails?
- How do I share my resume?
- Can I have multiple tokens per job?

#### Acceptance Criteria
- Documentation is comprehensive
- New user could replicate system
- All features documented
- Examples included
- Troubleshooting covered

#### Dependencies
- All previous tasks complete

---

### Task 5.5: Future Enhancements Backlog
**Estimated:** 2 hours | **Status:** [ ] Not Started

#### Description
Document future enhancement ideas and create roadmap for continued development.

#### Subtasks
- [ ] Document LinkedIn integration ideas
- [ ] Note analytics tracking possibilities
- [ ] List potential profile improvements

#### Deliverables
- `docs/future-roadmap.md`
- Enhancement proposals
- Priority recommendations

#### Future Enhancement Ideas

**Near-term (3-6 months):**
- [ ] Analytics tracking (which resumes viewed most)
- [ ] Token expiration system
- [ ] Email notifications on build completion
- [ ] Preview mode (before deployment)
- [ ] Additional profiles (consulting, startup, etc.)

**Mid-term (6-12 months):**
- [ ] LinkedIn profile sync
- [ ] Dynamic website with profile switching
- [ ] Cover letter generation system
- [ ] Application tracking integration
- [ ] Multi-language support

**Long-term (12+ months):**
- [ ] AI-powered content suggestions
- [ ] A/B testing different resume versions
- [ ] Automated profile optimization
- [ ] Integration with job boards
- [ ] Resume analytics dashboard

#### Acceptance Criteria
- Roadmap is documented
- Ideas are categorized by priority
- Technical feasibility assessed
- Resource requirements estimated

#### Dependencies
- All other Phase 5 tasks complete

---

### PHASE 5 ACCEPTANCE CRITERIA

**Must Complete For Project Closure:**
- ✅ All scripts work without errors
- ✅ Documentation is comprehensive
- ✅ New user could replicate system
- ✅ Roadmap is documented

**Phase 5 Deliverables:**
- Enhanced error handling
- Build monitoring system
- Helper scripts
- Complete documentation
- Future roadmap

---

## PROJECT COMPLETION CRITERIA

### MVP Success Metrics
- [x] Complete YAML migration (JSON removed)
- [x] 3 working profiles (default, leadership, technical)
- [x] Master resume with 100% content tagged
- [x] Job branch workflow functional
- [x] Private URLs with tokens working
- [x] GitHub Actions deploys correctly
- [x] PDF output maintains quality

### Final Deliverables Checklist
- [ ] `/home/user/colins-resume/resume_builder/resume.yaml` (master data)
- [ ] `/home/user/colins-resume/resume_builder/profiles/` (3+ profiles)
- [ ] `/home/user/colins-resume/resume_builder/profile_manager.py`
- [ ] `/home/user/colins-resume/scripts/generate_token.py`
- [ ] `/home/user/colins-resume/templates/job-branch-setup.sh`
- [ ] `/home/user/colins-resume/.github/workflows/build-resume.yml` (updated)
- [ ] `/home/user/colins-resume/docs/job-branch-workflow.md`
- [ ] `/home/user/colins-resume/docs/troubleshooting.md`
- [ ] `/home/user/colins-resume/docs/future-roadmap.md`
- [ ] 2+ test job branches deployed
- [ ] Live production site updated

### Project Sign-off Requirements
- [ ] All Phase 1-5 acceptance criteria met
- [ ] Documentation complete and reviewed
- [ ] Test branches successfully deployed
- [ ] Main production site updated
- [ ] At least 2 real job applications using new system
- [ ] No critical bugs outstanding
- [ ] Performance targets met
- [ ] Owner approval received

---

## RISK MITIGATION TRACKER

| Risk ID | Risk Description | Probability | Impact | Mitigation Status |
|---------|-----------------|-------------|--------|-------------------|
| R-1 | YAML conversion loses data | Medium | High | Backup + validation in Task 1.5 |
| R-2 | Profile filtering too complex | Low | Medium | Simple tag-based system |
| R-3 | PDF formatting breaks | Medium | Medium | Test after each generator change |
| R-4 | GitHub Actions fails on branch | Medium | High | Extensive testing in Phase 3 |
| R-5 | S3 token paths conflict | Low | Medium | Token uniqueness validation |
| R-6 | Private URLs discovered | Low | High | 12+ char cryptographic tokens |
| R-7 | Migration timeline overrun | Medium | Low | Phased rollout allows flexibility |

---

## PROGRESS TRACKING

### Current Status
- **Phase:** Planning Complete
- **Branch:** claude/create-task-list-014MrVUCxe7KELyZ7SgDuQst
- **Next Task:** Task 1.1 (YAML Schema & Validation)
- **Ready to Start:** Yes

### Task Completion Log
To be updated as tasks are completed:

```
[YYYY-MM-DD HH:MM] Task X.X completed by [agent/user] in [hours]
```

### Velocity Tracking
- **Planned Velocity:** 10-15 hours/week
- **Actual Velocity:** TBD
- **Estimated Completion:** 6-8 weeks from start

---

## QUICK COMMAND REFERENCE

### Starting Phase 1
```bash
# Navigate to project directory
cd /home/user/colins-resume

# Ensure on correct branch
git checkout claude/create-task-list-014MrVUCxe7KELyZ7SgDuQst

# Begin Task 1.1
# Create YAML schema file
touch resume_builder/resume-schema.yaml
```

### Building Locally (Post-Phase 2)
```bash
# Build with default profile
./build_all.sh

# Build with specific profile
./build_all.sh --profile leadership

# Validate before building
./scripts/validate-resume.sh
```

### Creating Job Application Branch (Post-Phase 3)
```bash
# Create new job branch
./scripts/new-job-application.sh aws-security-eng technical

# List all resume URLs
./scripts/list-resume-urls.sh
```

---

## NOTES & DECISIONS

### Key Design Decisions
1. **YAML over JSON:** Human-readable, comment-friendly
2. **Tag-based filtering:** Simple, extensible
3. **Branch-per-job:** Clear separation, permanent history
4. **Token-based URLs:** Security through obscurity + crypto tokens
5. **Parallel running:** Risk mitigation during migration

### Assumptions
- AWS S3 + CloudFront already configured
- GitHub Actions enabled on repository
- Python 3.8+ available
- wkhtmltopdf and Pandoc installed

### Open Questions
- [ ] Should tokens be committed to git or .gitignored?
- [ ] Token expiration policy (manual vs automatic)?
- [ ] Max number of profiles (performance consideration)?
- [ ] Branch cleanup policy (keep all vs archive old)?

---

**Task List Status:** ✅ Complete and Ready for Implementation
**Total Tasks:** 26 tasks across 5 phases
**Total Estimated Hours:** 112 hours
**Recommended Start Date:** Immediately (Planning Complete)
**Target Completion:** 6-8 weeks (part-time) or 3-4 weeks (full-time)

---

*This task list is a living document. Update task status, hours, and notes as work progresses.*
