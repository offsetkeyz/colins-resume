# Project Planning Documentation

This directory contains comprehensive planning documentation for the Dynamic YAML-Based Resume System refactoring project.

## 📚 Documentation Files

### Core Planning Documents

#### [Refactoring Plan](refactoring-plan.md)
**Comprehensive Project Management Document**
- Executive summary and project vision
- Detailed requirements (functional and non-functional)
- Technical architecture and data models
- 5-phase implementation plan with tasks and timelines (updated with migration validation)
- Risk assessment and mitigation strategies
- Success criteria and acceptance test plan

**Start here for:** Complete project overview, implementation roadmap, timeline

---

#### [Architectural Decisions](architectural-decisions.md)
**Architecture Decision Records (ADR)**
- ADR-001: Data Format Migration (JSON to YAML)
- ADR-002: Content Filtering Strategy (Tagging System)
- ADR-003: Profile Storage Location
- ADR-004: Private URL Implementation
- ADR-005: Branch-Based Workflow
- ADR-006: Master Resume Content Strategy
- ADR-007: Build System Architecture
- ADR-008: No Auto-Delete of Job Branches

**Start here for:** Understanding why key technical decisions were made

---

### Infrastructure & Security Documents

#### [AWS Infrastructure](aws-infrastructure.md)
**Complete AWS Setup and Configuration**
- S3 bucket structure and configuration
- CloudFront distribution settings and cache behaviors
- IAM roles and permissions (OIDC recommended)
- Deployment strategy and scripts
- Cost analysis and monitoring
- Security considerations and logging

**Start here for:** AWS setup, deployment configuration, infrastructure details

---

#### [GitHub Actions Specification](github-actions-spec.md)
**Detailed Workflow Implementation**
- Complete workflow file with all steps
- Branch detection and configuration logic
- Build steps specification with error handling
- AWS credential management (OIDC)
- Deployment to S3 and CloudFront invalidation
- Testing strategy and troubleshooting guide

**Start here for:** GitHub Actions setup, CI/CD pipeline, automated deployment

---

#### [Security Model](security-model.md)
**Threat Analysis and Security Strategy**
- Threat model and attack surface analysis
- Token security (generation, validation, entropy analysis)
- Search engine protection (robots.txt, meta tags, headers)
- Access logging and monitoring
- Incident response procedures
- GDPR and privacy considerations

**Start here for:** Security requirements, token implementation, threat mitigation

---

### Version History

#### [Changelog](../CHANGELOG.md)
**Version History and Release Notes**
- Current version: 1.0.2 (JSON-based)
- Planned versions: 2.0.0+ (YAML-based)
- Migration notes and breaking changes
- Feature additions by version

**Start here for:** Version history, what changed when

---

## 🎯 Project Overview

### Current State
**Version:** 1.0.2 (Production)
**Format:** JSON-based resume system
**Status:** Planning phase for YAML migration complete

### Future State
**Version:** 2.0.0+ (Planned)
**Format:** YAML-based with profile system
**Status:** Ready to begin Phase 1 implementation

### Key Goals
1. ✅ Single master resume (YAML) with ALL career content
2. ✅ Profile-based filtering for different job applications
3. ✅ Branch workflow (one branch per job application)
4. ✅ Private URLs with token-based access
5. ✅ Automated HTML, PDF, and JSON generation

---

## 📋 Implementation Phases

### Phase 1: Foundation & Migration (Week 1)
- Create YAML schema and validation
- Convert resume.json → resume.yaml
- Build profile system (default, leadership, technical)
- Implement profile_manager.py for filtering

### Phase 2: Generator Updates (Week 2)
- Update HTML and Markdown generators for YAML
- Create JSON export for API
- Update build scripts
- Remove JSON dependencies

### Phase 3: Branch Workflow & Automation (Week 3)
- Token generation for private URLs
- Branch template and setup scripts
- Enhanced GitHub Actions
- S3 deployment to /r/{token}/ paths

### Phase 4: Content Enhancement & Testing (Week 4)
- Expand master resume with comprehensive content
- Refine profiles based on output
- Create test job branches
- Integration testing and deployment

### Phase 5: Polish & Future-Proofing (Week 5)
- Error handling and logging
- Helper scripts for common tasks
- Complete documentation
- Future roadmap

**Total Timeline:** 6-8 weeks part-time or 3-4 weeks full-time
**Revised Estimate:** 150-195 hours (includes migration validation and testing)

---

## 🏗️ Architecture Highlights

### Data Flow
```
Master Resume (YAML)
    ↓
Profile Manager (filters by include_in tags)
    ↓
Filtered Content
    ↓
    ├─→ HTML Generator → index.html
    ├─→ Markdown Generator → resume.md → PDF
    └─→ JSON Generator → resume.json (API)
```

### Branch Strategy
```
main branch
├── resume.yaml (master with ALL content)
└── profiles/
    ├── default.yaml
    ├── leadership.yaml
    └── technical.yaml

resume/aws-security-eng branch
├── active_profile.txt ("technical")
└── resume_token.txt ("a8f3k2j9")
    ↓
https://colinmca.com/r/a8f3k2j9/resume.pdf
```

### Tagging System
```yaml
responsibilities:
  - text: "Led team of 6 engineers"
    include_in: [leadership, management, all]
  - text: "Debugged Python codebase"
    include_in: [technical, all]
```

---

## 📖 Related Documentation

| Document | Location | Purpose |
|----------|----------|---------|
| **Planning & Architecture** | | |
| Refactoring Plan | `refactoring-plan.md` | Complete project roadmap |
| Architectural Decisions | `architectural-decisions.md` | ADRs and design rationale |
| AWS Infrastructure | `aws-infrastructure.md` | Cloud setup and deployment |
| GitHub Actions Spec | `github-actions-spec.md` | CI/CD pipeline details |
| Security Model | `security-model.md` | Threat analysis and mitigations |
| **Development** | | |
| Requirements | `/requirements.txt` | Python dependencies (pinned) |
| Requirements (Minimal) | `/requirements-minimal.txt` | Production dependencies only |
| Claude Instructions | `/.claude/claude.md` | AI assistant context |
| Quick Reference | `/.claude/quick-reference.md` | Commands and troubleshooting |
| **Project** | | |
| Main README | `/README.md` | Project overview |
| Changelog | `/docs/CHANGELOG.md` | Version history |

---

## 🚀 Getting Started

### For Developers
1. Read the [Refactoring Plan](refactoring-plan.md) for complete project overview
2. Review [Architectural Decisions](architectural-decisions.md) to understand design choices
3. Study [GitHub Actions Specification](github-actions-spec.md) for CI/CD implementation
4. Review [AWS Infrastructure](aws-infrastructure.md) for deployment setup
5. Understand [Security Model](security-model.md) for security requirements
6. Install dependencies: `pip install -r requirements.txt`
7. Check `/.claude/claude.md` for development workflow

### For Project Managers
1. Review [Executive Summary](refactoring-plan.md#executive-summary) for business value
2. Check [Implementation Plan](refactoring-plan.md#implementation-plan) for timeline
3. Review [Risk Assessment](refactoring-plan.md#risk-assessment) for potential issues
4. Monitor [Success Criteria](refactoring-plan.md#success-criteria) for progress tracking

### For Future Maintainers
1. Read all ADRs to understand architectural context
2. Check [Changelog](../CHANGELOG.md) for version history
3. Review current phase status in [Refactoring Plan](refactoring-plan.md)
4. Use [Quick Reference](../../.claude/quick-reference.md) for daily operations

---

## 📊 Current Status

**Phase:** Planning Complete ✅
**Documentation Status:** Complete with infrastructure, security, and CI/CD specs
**Next Milestone:** Phase 1, Task 1.1 (YAML Schema Creation)
**Pre-Implementation Requirements:**
- ✅ AWS infrastructure documented
- ✅ GitHub Actions workflow specified
- ✅ Security model defined
- ✅ Migration validation strategy added
- ✅ Dependencies documented (requirements.txt)
**Blockers:** None
**Ready to Start:** ✅ Yes (all pre-work complete)

---

## 🤝 Contributing

When making changes to this project:
1. Follow the phase-by-phase implementation plan
2. Update this documentation as you go
3. Add new ADRs for significant architectural decisions
4. Keep the changelog current
5. Test locally before pushing

---

## 📞 Questions or Issues?

1. Check the [Refactoring Plan](refactoring-plan.md) FAQ section
2. Review [Architectural Decisions](architectural-decisions.md) for context
3. Use [Quick Reference](../../.claude/quick-reference.md) for troubleshooting
4. Consult `/.claude/claude.md` for development guidelines

---

**Last Updated:** 2025-11-21
**Maintained By:** Colin McAllister
**Status:** Living documentation (update as project progresses)
