# 📋 Project Management Document
## Dynamic YAML-Based Resume System

**Project Owner:** Colin McAllister
**Document Author:** Claude (AI PM)
**Date:** 2025-11-21
**Version:** 1.0
**Status:** Planning Phase

---

## 📊 Executive Summary

### Project Vision
Transform the current JSON-based resume system into a comprehensive YAML-driven platform that enables:
- Single master resume containing ALL career experiences and achievements
- Multiple profile-based resume versions for different job applications
- Branch-based workflow for managing concurrent job applications
- Automated generation of HTML, PDF, and JSON outputs
- Private, obscured URLs for sharing job-specific resumes

### Business Value
- **Time Savings:** Update one master file instead of multiple resume versions
- **Consistency:** Eliminate discrepancies between different resume versions
- **Flexibility:** Create unlimited resume variants for different opportunities
- **Version Control:** Track which resume was sent to which employer
- **Professionalism:** Tailored resumes for each application without manual editing

### Success Metrics
- ✅ Master resume.yaml contains 100% of career content
- ✅ Generate 3+ profile variations from single source
- ✅ Job application branches deploy in <5 minutes
- ✅ Zero manual HTML/PDF editing required
- ✅ Private URLs functional with token-based access

---

## 📝 Requirements Document

### Functional Requirements

#### FR-1: YAML Data Format
- **FR-1.1:** Complete migration from JSON to YAML for all resume data
- **FR-1.2:** Support include_in tagging for all content sections
- **FR-1.3:** Maintain schema validation for data integrity
- **FR-1.4:** Human-readable, comment-friendly format

#### FR-2: Tagging System
- **FR-2.1:** Each resume bullet/item can specify `include_in: [profile1, profile2, all]`
- **FR-2.2:** Support tagging for:
  - Work experience responsibilities
  - Skills and specialty skills
  - Projects and highlights
  - Certifications (optional filtering)
  - Education courses (optional filtering)
- **FR-2.3:** Special tag "all" includes item in every profile

#### FR-3: Profile Management
- **FR-3.1:** Profiles stored in `main` branch at `resume_builder/profiles/`
- **FR-3.2:** Each profile specifies:
  - Name and description
  - Which tags to include
  - Max bullets per job (optional)
  - Output customization (optional)
- **FR-3.3:** Minimum 3 starter profiles:
  - `default.yaml` - Full master resume
  - `leadership.yaml` - Leadership/management focused
  - `technical.yaml` - Technical/development focused

#### FR-4: Branch-Based Workflow
- **FR-4.1:** Job application branches follow naming: `resume/{job-identifier}`
- **FR-4.2:** Each job branch contains `resume_builder/active_profile.txt`
- **FR-4.3:** File specifies which profile to use (e.g., "leadership")
- **FR-4.4:** Branches remain permanent (no auto-delete)

#### FR-5: Build System
- **FR-5.1:** Generate HTML, PDF, and JSON from YAML source
- **FR-5.2:** Profile-aware generation (filter content based on include_in tags)
- **FR-5.3:** Maintain existing styling and layout quality
- **FR-5.4:** Support both local builds and GitHub Actions

#### FR-6: Private URL System
- **FR-6.1:** Generate random tokens (8-12 characters) for each job application
- **FR-6.2:** URL format: `https://colinmca.com/r/{token}/resume.pdf`
- **FR-6.3:** Token stored in job branch metadata or config
- **FR-6.4:** S3 deployment to token-based paths

### Non-Functional Requirements

#### NFR-1: Performance
- GitHub Actions build completes in <3 minutes
- PDF generation <30 seconds
- Website loads in <2 seconds

#### NFR-2: Maintainability
- Clear documentation for adding new profiles
- Self-documenting YAML with comments
- Migration guide for future updates

#### NFR-3: Reliability
- Schema validation catches errors before deployment
- Automated testing of profile filtering logic
- Rollback capability if builds fail

#### NFR-4: Usability
- Simple one-command local builds
- Clear error messages for validation failures
- Easy profile creation (copy template)

---

## 🏗️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN BRANCH                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │ resume_builder/                                    │     │
│  │   ├── resume.yaml (MASTER - ALL CONTENT)          │     │
│  │   ├── profiles/                                    │     │
│  │   │   ├── default.yaml                             │     │
│  │   │   ├── leadership.yaml                          │     │
│  │   │   └── technical.yaml                           │     │
│  │   └── generators/                                  │     │
│  │       ├── profile_manager.py (NEW)                 │     │
│  │       ├── yaml_loader.py (NEW)                     │     │
│  │       ├── html_generator.py (ENHANCED)             │     │
│  │       └── md_generator.py (ENHANCED)               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Branch from
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              JOB BRANCH: resume/aws-security-eng            │
│  ┌────────────────────────────────────────────────────┐     │
│  │ resume_builder/                                    │     │
│  │   ├── active_profile.txt (contains: "technical")  │     │
│  │   └── resume_token.txt (contains: "a8f3k2j9")     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  GitHub Actions Trigger on Push                             │
│         ▼                                                    │
│  1. Read active_profile.txt → "technical"                   │
│  2. Load resume.yaml from main                              │
│  3. Load profiles/technical.yaml from main                  │
│  4. Filter content based on include_in tags                 │
│  5. Generate HTML/PDF/JSON                                  │
│  6. Read resume_token.txt → "a8f3k2j9"                      │
│  7. Deploy to S3: s3://bucket/r/a8f3k2j9/                   │
│         ▼                                                    │
│  https://colinmca.com/r/a8f3k2j9/resume.pdf                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Model

**Master Resume (resume.yaml):**
```yaml
basics:
  name: "Colin McAllister"
  # ... basic info

work_experience:
  "Arctic Wolf Networks":
    - job_title: "Team Lead - Security Developer"
      start_date: "2024-03-01"
      end_date: "Present"
      responsibilities:
        - text: "Reduced team backlog from 300 to 0..."
          include_in: [leadership, management, all]
        - text: "Spearheaded automation tool saving 2000 hours..."
          include_in: [technical, leadership, all]
        - text: "Prioritized team happiness and productivity..."
          include_in: [leadership, all]
      skills:
        - name: "Leadership"
          include_in: [all]
```

**Profile Configuration (profiles/leadership.yaml):**
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

**Job Branch Config (active_profile.txt):**
```
leadership
```

**Token Config (resume_token.txt):**
```
a8f3k2j9
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Format | YAML | Human-readable resume data |
| Schema Validation | PyYAML + Custom | Ensure data integrity |
| Profile Filter | Python 3.x | Content filtering logic |
| HTML Generator | Python + Jinja2 | Web output |
| PDF Generator | wkhtmltopdf | Print-ready output |
| CI/CD | GitHub Actions | Automated builds |
| Hosting | AWS S3 + CloudFront | Static file serving |
| Token Generator | Python secrets module | Secure random tokens |

---

## 📅 Implementation Plan

### Phase 1: Foundation & Migration
**Duration:** 1.5-2 weeks
**Goal:** Migrate to YAML and establish core infrastructure with validation

#### Tasks:

**1.1 YAML Schema & Validation** ⏱️ 4 hours
- [ ] Create `resume-schema.yaml` based on existing JSON schema
- [ ] Add validation rules for `include_in` tags
- [ ] Write Python validator script
- [ ] Document schema with inline comments
- **Deliverable:** `resume_builder/resume-schema.yaml`

**1.2 Convert resume.json → resume.yaml** ⏱️ 6 hours
- [ ] Write conversion script `migrate_json_to_yaml.py` with comprehensive logging
- [ ] Back up current resume.json to `resume.json.backup`
- [ ] Run conversion on current resume.json
- [ ] Generate conversion report (fields converted, warnings, etc.)
- [ ] Manually review output for accuracy
- [ ] Add `include_in: [all]` to every existing item (default)
- [ ] Validate YAML syntax and schema compliance
- **Deliverable:** `resume_builder/resume.yaml` and conversion report

**1.3 Create Profile System** ⏱️ 4 hours
- [ ] Create `profiles/` directory structure
- [ ] Write `default.yaml` profile (includes everything)
- [ ] Write `leadership.yaml` profile
- [ ] Write `technical.yaml` profile
- [ ] Document profile creation guide
- **Deliverable:** `resume_builder/profiles/*.yaml`

**1.4 Build Profile Manager** ⏱️ 8 hours
- [ ] Create `profile_manager.py`
- [ ] Implement tag filtering logic
- [ ] Add max_bullets_per_job limiting
- [ ] Write unit tests for filtering (see test cases below)
- [ ] Test with edge cases (missing tags, empty profiles, etc.)
- **Deliverable:** `resume_builder/profile_manager.py`

**1.5 Migration Validation** ⏱️ 6 hours
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
- **Deliverable:** Validation report and rollback procedure

**Phase 1 Acceptance Criteria:**
- ✅ resume.yaml validates successfully
- ✅ All 3 profiles load without errors
- ✅ Profile manager filters content correctly
- ✅ Unit tests pass with 85%+ coverage
- ✅ YAML-generated output matches JSON-generated output (content-wise)
- ✅ No data loss detected in migration
- ✅ Rollback procedure documented and tested

---

### Phase 2: Generator Updates
**Duration:** 1.5 weeks
**Goal:** Update all generators to use YAML and profiles with parallel validation

#### Tasks:

**2.1 Update HTML Generator** ⏱️ 5 hours
- [ ] Replace JSON loading with YAML loading
- [ ] Integrate profile_manager for content filtering
- [ ] Test with all 3 profiles
- [ ] Verify HTML output quality
- **Deliverable:** Updated `html_generator.py`

**2.2 Update Markdown Generator** ⏱️ 4 hours
- [ ] Replace JSON loading with YAML loading
- [ ] Integrate profile_manager
- [ ] Test markdown → HTML → PDF pipeline
- **Deliverable:** Updated `md_generator.py`

**2.3 Create JSON Export** ⏱️ 3 hours
- [ ] Add `json_generator.py` for API output
- [ ] Export filtered resume as JSON
- [ ] Used for future dynamic website loading
- **Deliverable:** `json_generator.py`

**2.4 Update Build Scripts** ⏱️ 3 hours
- [ ] Update `build_all.sh` to use YAML
- [ ] Add profile parameter support
- [ ] Test local builds with all profiles
- **Deliverable:** Updated `build_all.sh`

**2.5 Parallel Running Period** ⏱️ 4 hours
- [ ] Keep both JSON and YAML systems functional
- [ ] Build outputs from both systems for comparison
- [ ] Run for at least 1 week in parallel
- [ ] Monitor for discrepancies or issues
- [ ] Final validation before JSON removal
- **Deliverable:** Confidence in YAML system

**2.6 Remove JSON Dependencies** ⏱️ 2 hours
- [ ] Rename `resume.json` to `resume.json.deprecated`
- [ ] Move to `archive/` directory (keep for reference)
- [ ] Update documentation to reference YAML
- [ ] Remove JSON-specific code paths
- [ ] Update build scripts to YAML-only
- **Deliverable:** Clean codebase with JSON archived

**Phase 2 Acceptance Criteria:**
- ✅ Generate HTML from YAML successfully
- ✅ Generate PDF from YAML successfully
- ✅ All 3 profiles produce valid outputs
- ✅ Parallel running validates consistency
- ✅ JSON system archived (not deleted)
- ✅ Local builds work with `./build_all.sh --profile leadership`
- ✅ Visual comparison shows no quality degradation

---

### Phase 3: Branch Workflow & Automation
**Duration:** 1 week
**Goal:** Implement job branch workflow with GitHub Actions

#### Tasks:

**3.1 Token Generation System** ⏱️ 4 hours
- [ ] Create `generate_token.py` script
- [ ] Generate 8-12 character secure tokens
- [ ] Write token to `resume_token.txt`
- [ ] Add token to .gitignore (or commit based on preference)
- **Deliverable:** `generate_token.py`

**3.2 Branch Template** ⏱️ 3 hours
- [ ] Create `templates/job-branch-setup.sh`
- [ ] Script creates new job branch
- [ ] Adds `active_profile.txt`
- [ ] Generates and adds `resume_token.txt`
- **Deliverable:** `templates/job-branch-setup.sh`

**3.3 Enhanced GitHub Actions** ⏱️ 8 hours
- [ ] Update `.github/workflows/build-resume.yml`
- [ ] Detect branch type (main vs resume/*)
- [ ] Read active_profile.txt from job branches
- [ ] Load master resume.yaml from main branch
- [ ] Apply profile filtering
- [ ] Read resume_token.txt
- [ ] Deploy to S3 with token path
- **Deliverable:** Updated `.github/workflows/build-resume.yml`

**3.4 S3 Deployment Updates** ⏱️ 4 hours
- [ ] Update S3 bucket structure for `/r/{token}/` paths
- [ ] Configure CloudFront for new paths
- [ ] Test file uploads to token paths
- [ ] Verify URL access
- **Deliverable:** Updated AWS infrastructure

**3.5 Documentation** ⏱️ 4 hours
- [ ] Write "Creating a Job Application Branch" guide
- [ ] Document profile selection process
- [ ] Explain token system
- [ ] Create troubleshooting guide
- **Deliverable:** `docs/job-branch-workflow.md`

**Phase 3 Acceptance Criteria:**
- ✅ Create new job branch in <5 minutes
- ✅ Push to job branch triggers build
- ✅ PDF deploys to https://colinmca.com/r/{token}/resume.pdf
- ✅ URL is accessible and private (not indexed)
- ✅ Documentation is clear and complete

---

### Phase 4: Content Enhancement & Testing
**Duration:** 1 week
**Goal:** Populate master resume and validate all workflows

#### Tasks:

**4.1 Master Resume Expansion** ⏱️ 6 hours
- [ ] Review current resume content
- [ ] Add all "hidden" experiences/bullets you've removed over time
- [ ] Add alternative phrasings for key achievements
- [ ] Tag everything with appropriate `include_in` values
- **Deliverable:** Comprehensive `resume.yaml`

**4.2 Profile Refinement** ⏱️ 4 hours
- [ ] Test leadership profile output
- [ ] Test technical profile output
- [ ] Adjust filters based on output
- [ ] Ensure PDF length is appropriate (1-2 pages)
- **Deliverable:** Refined profiles

**4.3 Create Test Job Branches** ⏱️ 4 hours
- [ ] Create `resume/test-leadership-role`
- [ ] Create `resume/test-technical-role`
- [ ] Verify builds and deployments
- [ ] Test PDF downloads
- **Deliverable:** 2 test branches with deployed resumes

**4.4 Integration Testing** ⏱️ 4 hours
- [ ] Test complete workflow end-to-end
- [ ] Verify all generators work
- [ ] Check PDF formatting and styling
- [ ] Validate private URLs
- **Deliverable:** Test report

**4.5 Main Branch Deployment** ⏱️ 3 hours
- [ ] Deploy default profile to https://colinmca.com
- [ ] Verify main website updates
- [ ] Test PDF download from main site
- **Deliverable:** Live production deployment

**Phase 4 Acceptance Criteria:**
- ✅ Master resume contains 150%+ of normal resume content
- ✅ Leadership profile generates 1-2 page PDF
- ✅ Technical profile generates 1-2 page PDF
- ✅ Test branches deploy successfully
- ✅ Main website reflects new system

---

### Phase 5: Polish & Future-Proofing
**Duration:** 3-5 days
**Goal:** Add quality-of-life features and documentation

#### Tasks:

**5.1 Error Handling** ⏱️ 4 hours
- [ ] Add validation error messages
- [ ] Handle missing profile gracefully
- [ ] Provide helpful GitHub Actions logs
- **Deliverable:** Robust error handling

**5.2 Monitoring & Logging** ⏱️ 3 hours
- [ ] Log which profile was used for each build
- [ ] Track token generation
- [ ] Add build timestamps
- **Deliverable:** Build metadata

**5.3 Helper Scripts** ⏱️ 4 hours
- [ ] Create `new-job-application.sh` script
- [ ] Create `list-resume-urls.sh` to show all tokens
- [ ] Create `validate-resume.sh` for local testing
- **Deliverable:** Helper scripts in `scripts/`

**5.4 Final Documentation** ⏱️ 6 hours
- [ ] Update README.md with new system
- [ ] Create architecture diagram
- [ ] Write migration guide (for future users)
- [ ] Add FAQ section
- **Deliverable:** Complete documentation

**5.5 Future Enhancements Backlog** ⏱️ 2 hours
- [ ] Document LinkedIn integration ideas
- [ ] Note analytics tracking possibilities
- [ ] List potential profile improvements
- **Deliverable:** `docs/future-roadmap.md`

**Phase 5 Acceptance Criteria:**
- ✅ All scripts work without errors
- ✅ Documentation is comprehensive
- ✅ New user could replicate system
- ✅ Roadmap is documented

---

## 📊 Project Timeline

```
Week 1-2: Foundation & Migration (Updated: +4 hours for validation)
├─ Day 1-2: YAML Schema & Validation
├─ Day 3-4: JSON → YAML Conversion (with backups and logging)
├─ Day 5-7: Profile System & Manager
└─ Day 8-9: Migration Validation (parallel testing)

Week 3-4: Generator Updates (Updated: +4 hours for parallel running)
├─ Day 1-2: HTML & Markdown Generators
├─ Day 3-4: JSON Export & Build Scripts
├─ Day 5-7: Parallel Running Period (both systems)
└─ Day 8: Archive JSON Dependencies

Week 5: Branch Workflow & Automation
├─ Day 1-2: Token System & Branch Template
├─ Day 3-5: GitHub Actions Enhancement
└─ Day 6-7: S3 Deployment & Documentation

Week 6: Content Enhancement & Testing
├─ Day 1-2: Master Resume Expansion
├─ Day 3-4: Profile Refinement & Test Branches
└─ Day 5-7: Integration Testing & Deployment

Week 7: Polish & Documentation
├─ Day 1-2: Error Handling & Monitoring
├─ Day 3-4: Helper Scripts
└─ Day 5: Final Documentation

Total Duration: 6-8 weeks (Part-time) or 3-4 weeks (Full-time)
Revised Estimate: 150-195 hours (was 97 hours)
```

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| YAML conversion loses data | Medium | High | Manual review + backup JSON file until validated |
| Profile filtering too complex | Low | Medium | Keep it simple - just include_in tags initially |
| PDF formatting breaks | Medium | Medium | Test after each generator change |
| GitHub Actions fails on branch | Medium | High | Extensive testing before production use |
| S3 token paths conflict | Low | Medium | Validate token uniqueness before deployment |
| Private URLs discovered | Low | High | Use cryptographically secure tokens (12+ chars) |
| Migration takes longer than expected | Medium | Low | Phased rollout allows partial completion |
| Profile system too rigid | Medium | Medium | Design for extensibility from start |

### Mitigation Actions

1. **Data Loss Prevention:**
   - Keep resume.json as `resume.json.backup` until YAML proven
   - Git commit after each major change
   - Test suite validates all data present

2. **Rollback Plan:**
   - Each phase can be reverted independently
   - Main branch always deployable
   - Feature flags for new functionality

3. **Testing Strategy:**
   - Unit tests for profile_manager
   - Integration tests for full pipeline
   - Manual review of PDF output quality

---

## ✅ Success Criteria

### Must Have (MVP)
- [ ] Complete YAML migration (JSON removed)
- [ ] 3 working profiles (default, leadership, technical)
- [ ] Master resume with 100% content tagged
- [ ] Job branch workflow functional
- [ ] Private URLs with tokens working
- [ ] GitHub Actions deploys correctly
- [ ] PDF output maintains quality

### Should Have
- [ ] 5+ profiles available
- [ ] Helper scripts for common tasks
- [ ] Comprehensive documentation
- [ ] Error handling and validation
- [ ] Build logs and metadata

### Nice to Have
- [ ] Analytics on resume downloads
- [ ] Multiple token support per branch
- [ ] Auto-expiring tokens
- [ ] Email notifications on build completion

---

## 🧪 Acceptance Test Plan

### Unit Test Cases for Profile Manager

**Test Suite 1: Tag Filtering**
```python
def test_include_in_filtering():
    """Test that items are filtered based on include_in tags."""
    item_leadership = {"text": "Led team", "include_in": ["leadership"]}
    item_technical = {"text": "Wrote code", "include_in": ["technical"]}
    item_all = {"text": "Collaborated", "include_in": ["all"]}

    # Leadership profile should include leadership and all items
    result = filter_items([item_leadership, item_technical, item_all], "leadership")
    assert item_leadership in result
    assert item_all in result
    assert item_technical not in result

def test_missing_include_in_tag():
    """Test handling of items without include_in tag."""
    item_no_tag = {"text": "Something"}

    # Should either raise error or default to [all]
    # (Document which behavior is chosen)
    result = filter_items([item_no_tag], "leadership")
    # Assert based on chosen behavior
```

**Test Suite 2: Max Bullets Limiting**
```python
def test_max_bullets_per_job():
    """Test max_bullets_per_job limiting."""
    bullets = [
        {"text": "Bullet 1", "include_in": ["all"]},
        {"text": "Bullet 2", "include_in": ["all"]},
        {"text": "Bullet 3", "include_in": ["all"]},
        {"text": "Bullet 4", "include_in": ["all"]},
        {"text": "Bullet 5", "include_in": ["all"]},
    ]

    profile_config = {"max_bullets_per_job": 3}
    result = apply_profile_limits(bullets, profile_config)

    assert len(result) == 3
    assert result[0]["text"] == "Bullet 1"  # First 3 bullets
    assert result[2]["text"] == "Bullet 3"
```

**Test Suite 3: Edge Cases**
```python
def test_profile_not_found():
    """Test error handling when profile doesn't exist."""
    with pytest.raises(ProfileNotFoundError):
        load_profile("nonexistent_profile")

def test_empty_profile():
    """Test handling of profile with no items selected."""
    result = filter_resume_with_profile(resume_data, "empty_profile")
    assert result is not None  # Should return valid but empty structure

def test_nested_filtering():
    """Test that nested items (skills within jobs) are filtered."""
    job = {
        "title": "Engineer",
        "responsibilities": [
            {"text": "Led", "include_in": ["leadership"]},
            {"text": "Coded", "include_in": ["technical"]}
        ]
    }

    result = filter_job(job, "leadership")
    assert len(result["responsibilities"]) == 1
    assert result["responsibilities"][0]["text"] == "Led"
```

### Integration Test Case 1: YAML Validation
```
Given: resume.yaml with all content
When: Running validation script
Then: No errors, all tags valid, schema compliant
```

### Integration Test Case 2: Profile Filtering
```
Given: Master resume with mixed tags
When: Building with "leadership" profile
Then: Only items with include_in: [leadership, all] appear
```

### Integration Test Case 3: Migration Validation
```
Given: Existing resume.json and new resume.yaml
When: Building outputs from both systems
Then:
  - HTML content is equivalent (ignoring whitespace)
  - PDF has same page count
  - All key fields present in both
  - No data loss detected
```

### Integration Test Case 4: Job Branch Creation
```
Given: Main branch with profiles
When: Creating new job branch with setup script
Then: Branch created, active_profile.txt exists, token generated
```

### Integration Test Case 5: End-to-End Build
```
Given: Job branch pushed to GitHub
When: GitHub Actions runs
Then: PDF generated, deployed to /r/{token}/, URL accessible
```

### Integration Test Case 6: Private URL Access
```
Given: Deployed resume at /r/a8f3k2j9/resume.pdf
When: Accessing URL directly
Then: PDF downloads successfully, not indexed by search engines
```

### Integration Test Case 7: Profile Comparison
```
Given: Same master resume
When: Building leadership vs technical profiles
Then: Different content appears, both are valid, no overlap in focus
```

---

## 📚 Dependencies

### External Dependencies
- Python 3.8+ with PyYAML
- wkhtmltopdf 0.12.6+
- Pandoc 3.0+
- AWS S3 bucket access
- GitHub Actions enabled

### Internal Dependencies
| Task | Depends On | Blocker If Delayed? |
|------|-----------|---------------------|
| Generator Updates | YAML Migration | Yes |
| GitHub Actions | Profile Manager | Yes |
| S3 Deployment | Token System | Yes |
| Test Branches | GitHub Actions | Yes |
| Content Enhancement | Profile System | No (can be parallel) |

---

## 👥 Stakeholder Communication

### Weekly Status Updates
- Progress on current phase
- Blockers and risks
- Upcoming milestones
- Questions/decisions needed

### Demo Schedule
- **End of Week 1:** YAML conversion demo
- **End of Week 2:** Profile filtering demo
- **End of Week 3:** Job branch workflow demo
- **End of Week 4:** Live deployment demo

---

## 📖 Documentation Deliverables

1. **User Guide:** How to update resume and create job applications
2. **Developer Guide:** How to extend profiles and generators
3. **Architecture Document:** System design and data flow
4. **Troubleshooting Guide:** Common issues and solutions
5. **Migration Guide:** For future users adapting this system

---

## 🎯 Definition of Done

A task is considered "done" when:
- [ ] Code is written and tested
- [ ] Unit tests pass (if applicable)
- [ ] Integration tests pass
- [ ] Documentation is updated
- [ ] Code is committed to appropriate branch
- [ ] Peer review completed (self-review if solo)
- [ ] Acceptance criteria met

The project is considered "complete" when:
- [ ] All Phase 1-4 tasks completed
- [ ] All MVP success criteria met
- [ ] Documentation published
- [ ] Live production deployment successful
- [ ] At least 2 real job applications using new system

---

## 🚀 Next Steps

### Immediate Actions (Phase 1)
1. Create YAML schema validation
2. Convert resume.json to resume.yaml
3. Build profile system
4. Implement profile manager

### Questions Before Starting
1. Review this plan - any changes needed?
2. Confirm timeline works for you
3. Ready to begin Phase 1?
4. Review after each phase or continuous implementation?

---

**Document Status:** ✅ Complete - Ready for Implementation
**Next Action:** Begin Phase 1, Task 1.1 (YAML Schema Creation)
**Owner Approval:** Pending
