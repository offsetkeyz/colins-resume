# Architectural Decision Records (ADR)

## Overview
This document records key architectural decisions made during the resume system refactoring project. Each decision includes the context, options considered, decision made, and rationale.

---

## ADR-001: Data Format Migration (JSON to YAML)

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Need to choose between JSON, YAML, or supporting both formats for resume data

### Options Considered:
1. **Keep JSON only** - Maintain status quo
2. **Support both JSON and YAML** - Maximum flexibility
3. **Migrate to YAML only** - Single format

### Decision: Migrate to YAML only

### Rationale:
- YAML is more human-readable and easier to edit
- Supports comments for documentation within the data
- Better suited for configuration files
- Eliminates maintenance burden of supporting multiple formats
- Industry standard for configuration (Docker, Kubernetes, GitHub Actions)
- Less error-prone with proper indentation over brackets/commas

### Consequences:
- ✅ Easier to maintain and update resume content
- ✅ Self-documenting with inline comments
- ✅ Reduced complexity in codebase
- ❌ Requires one-time migration effort
- ❌ Team needs to learn YAML if unfamiliar

---

## ADR-002: Content Filtering Strategy (Tagging System)

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Need method to selectively include/exclude content in different resume versions

### Options Considered:
1. **Tags/labels (include_in)** - List of profiles each item belongs to
2. **Boolean flags per profile** - True/false for each profile
3. **Separate YAML files** - Duplicate content for each resume version
4. **Complex filtering rules** - Advanced query language for selection

### Decision: Use include_in tagging with profile names

### Rationale:
- Simple and explicit - easy to understand what appears where
- Flexible - items can appear in multiple profiles
- Scalable - new profiles don't require updating all items
- Readable - `include_in: [leadership, all]` is self-documenting
- Maintainable - single source of truth with clear inclusion rules

### Implementation:
```yaml
responsibilities:
  - text: "Led team of 6 engineers"
    include_in: [leadership, management, all]
  - text: "Debugged Python codebase"
    include_in: [technical, all]
```

### Consequences:
- ✅ Clear, explicit control over content visibility
- ✅ Easy to understand and maintain
- ✅ Supports unlimited profiles
- ❌ Requires tagging all content (one-time effort)
- ❌ No dynamic/automatic categorization

---

## ADR-003: Profile Storage Location

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Determine where profile configurations should be stored

### Options Considered:
1. **Profiles in main branch, job branches reference them**
2. **Each job branch has its own custom profile**
3. **External configuration service**
4. **Environment variables**

### Decision: Profiles in main branch at `resume_builder/profiles/`, job branches reference via `active_profile.txt`

### Rationale:
- Single source of truth for profile definitions
- Easier to maintain and update profiles centrally
- Job branches remain lightweight (just a reference)
- Profiles can evolve over time (updates propagate to all job branches)
- Clear separation of concerns (profiles vs. applications)

### Implementation:
```
main branch:
  └── resume_builder/profiles/
      ├── default.yaml
      ├── leadership.yaml
      └── technical.yaml

job branch (resume/aws-security):
  └── resume_builder/active_profile.txt
      Contains: "technical"
```

### Consequences:
- ✅ Centralized profile management
- ✅ Profile updates benefit all job applications
- ✅ Lighter job branches (less duplication)
- ❌ Job-specific customizations require new profile
- ❌ Branches depend on main for profile definitions

---

## ADR-004: Private URL Implementation

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Job-specific resumes should not be publicly discoverable

### Options Considered:
1. **Obscured URLs with random tokens** - https://colinmca.com/r/{token}/
2. **Password-protected pages** - Authentication required
3. **Signed/expiring S3 URLs** - Time-limited access
4. **No public links** - Manual sharing of direct URLs

### Decision: Obscured URLs with cryptographically secure random tokens

### Rationale:
- Simple to implement (no auth system needed)
- Good balance of security and convenience
- Tokens are unguessable (cryptographic randomness)
- No authentication friction for employers
- Can be easily shared via email/application
- Low maintenance overhead

### Implementation:
- Generate 8-12 character tokens using Python `secrets` module
- Store token in `resume_token.txt` in job branch
- Deploy to S3 at `/r/{token}/resume.pdf`
- Token remains constant for each job application

### Consequences:
- ✅ Simple and frictionless for employers
- ✅ No authentication system needed
- ✅ Easy to generate and share
- ⚠️ Security through obscurity (not cryptographic security)
- ❌ If token leaked, URL is accessible
- ❌ No access revocation without changing token

---

## ADR-005: Branch-Based Workflow for Job Applications

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Need version control strategy for managing multiple job applications

### Options Considered:
1. **Branch per job application** - `resume/company-position`
2. **Tags for releases** - Tag main branch for each application
3. **Directories in main branch** - `/resumes/job1/`, `/resumes/job2/`
4. **Separate repositories** - One repo per job

### Decision: Branch per job application with naming `resume/{job-identifier}`

### Rationale:
- Git branches are designed for parallel development
- Clear isolation between different applications
- Easy to track which resume sent to which company
- Branches persist indefinitely (audit trail)
- Can make job-specific tweaks without affecting others
- GitHub Actions can trigger on branch patterns

### Implementation:
```bash
# Branch naming convention
resume/aws-security-engineer
resume/google-tech-lead
resume/startup-cto

# Each branch contains:
- active_profile.txt (which profile to use)
- resume_token.txt (unique URL token)
```

### Consequences:
- ✅ Clear version control for each application
- ✅ Parallel job applications don't conflict
- ✅ Full git history per application
- ✅ Easy rollback if needed
- ❌ Branch proliferation over time (not auto-deleted)
- ❌ Requires branch management discipline

---

## ADR-006: Master Resume Content Strategy

**Date:** 2025-11-21
**Status:** Accepted
**Context:** How to handle comprehensive vs. tailored content

### Options Considered:
1. **Master resume with ALL content, profiles filter down** - Single source
2. **Multiple standalone resume files** - Duplicate content
3. **Modular content blocks** - Assemble dynamically
4. **Priority/weight system** - Auto-select top N items

### Decision: Master resume contains ALL career content, profiles specify which items to include

### Rationale:
- Never lose content (everything captured in master)
- Single source of truth for all experiences
- Easy to repurpose content for different applications
- Profiles provide explicit control over what appears
- Future-proof (content grows over time)
- Easier to maintain consistency

### Implementation:
```yaml
# Master resume has 7 bullets for current role
responsibilities:
  - text: "Reduced backlog from 300 to 0"
    include_in: [leadership, all]
  - text: "Spearheaded automation saving 2000 hours"
    include_in: [technical, leadership, all]
  # ... 5 more bullets

# Leadership profile shows 3-4 bullets
# Technical profile shows 3-4 different bullets
```

### Consequences:
- ✅ Comprehensive repository of achievements
- ✅ Never delete content, just hide via profiles
- ✅ Easy to create new profiles from existing content
- ❌ Requires discipline to tag all content
- ❌ Master resume is longer (not directly usable)

---

## ADR-007: Build System Architecture

**Date:** 2025-11-21
**Status:** Accepted
**Context:** How to generate multiple formats from YAML source

### Options Considered:
1. **Python scripts + Pandoc + wkhtmltopdf** - Current system enhanced
2. **Static site generator (Jekyll, Hugo)** - Complete rewrite
3. **JavaScript-based (Node.js)** - Different ecosystem
4. **Template engine (Jinja2, Mustache)** - HTML generation only

### Decision: Enhance existing Python + Pandoc + wkhtmltopdf pipeline

### Rationale:
- Already proven to work in production
- Minimal rewrite required (update existing scripts)
- Python is well-suited for data transformation
- Pandoc excellent for document conversion
- wkhtmltopdf produces high-quality PDFs
- Team already familiar with tools

### Implementation:
```
YAML → profile_manager.py → filtered YAML →
  ├─ html_generator.py → HTML
  ├─ md_generator.py → Markdown → Pandoc → HTML → wkhtmltopdf → PDF
  └─ json_generator.py → JSON (for API/dynamic loading)
```

### Consequences:
- ✅ Leverage existing investment
- ✅ Proven technology stack
- ✅ Minimal learning curve
- ❌ Multiple tools in pipeline (complexity)
- ❌ Python dependency for builds

---

## ADR-008: No Auto-Delete of Job Branches

**Date:** 2025-11-21
**Status:** Accepted
**Context:** Should old job application branches be automatically deleted?

### Options Considered:
1. **Keep all branches indefinitely** - Complete history
2. **Auto-delete after N days** - Automatic cleanup
3. **Archive to separate repository** - Clean main repo
4. **Manual deletion on request** - User controlled

### Decision: Keep all job application branches indefinitely (no auto-delete)

### Rationale:
- Provides complete audit trail of job applications
- May need to reference old resumes (follow-ups, interviews)
- Disk space is cheap (git branches are lightweight)
- Accidental deletion can lose important history
- User can manually clean up if desired

### Consequences:
- ✅ Complete historical record
- ✅ No risk of accidental data loss
- ✅ Can reference old applications years later
- ❌ Branch list grows over time
- ❌ Requires manual cleanup if desired

---

## Future ADRs

### Pending Decisions:
- **LinkedIn API Integration** - Research needed on API capabilities
- **Analytics Implementation** - Which metrics to track, privacy concerns
- **Token Expiration** - Should URLs expire? How to handle renewals?
- **Multi-language Support** - International job applications
- **A/B Testing Framework** - Test different resume variations

---

**Document Maintenance:**
- Add new ADRs as architectural decisions are made
- Update status if decisions are superseded
- Reference ADR numbers in code comments for context
