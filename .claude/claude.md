# Claude Instructions for Colin's Resume Repository

## Project Overview

This is a dynamic YAML-based resume system that generates multiple output formats (HTML, PDF, JSON) from a single source of truth. The system supports profile-based filtering to create tailored resumes for different job applications.

**Owner:** Colin McAllister
**Website:** https://colinmca.com
**Repository:** https://github.com/offsetkeyz/colins-resume

## Current State

**Phase:** Migration to YAML-based system in progress
**Active Branch:** `claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK`
**Status:** Planning complete, ready for Phase 1 implementation

## Key Architectural Decisions

### 1. Data Format: YAML Only
- **Decision:** Full migration from JSON to YAML
- **Rationale:** More human-readable, supports comments, easier to maintain
- **Status:** To be implemented in Phase 1

### 2. Tagging System: include_in
- **Decision:** Use `include_in: [profile1, profile2, all]` tags
- **Rationale:** Simple, flexible, explicit control over content visibility
- **Example:**
  ```yaml
  responsibilities:
    - text: "Led team of 6 engineers"
      include_in: [leadership, management, all]
    - text: "Debugged Python codebase"
      include_in: [technical, all]
  ```

### 3. Profile Storage: Main Branch
- **Decision:** Profiles stored in `main` branch at `resume_builder/profiles/`
- **Job branches reference profiles via `active_profile.txt`**
- **Rationale:** Single source of truth, easier maintenance

### 4. Private URLs: Token-Based Obscurity
- **Decision:** Use random tokens for private resume URLs
- **Format:** `https://colinmca.com/r/{token}/resume.pdf`
- **Security:** 8-12 character cryptographically secure tokens
- **Rationale:** Simple, no authentication system needed

### 5. Content Management: Master Resume + Profiles
- **Decision:** Master resume contains ALL content, profiles filter selectively
- **Rationale:** Never lose content, easy to repurpose for different applications

## Repository Structure

```
colins-resume/
├── .claude/                          # Claude AI instructions
│   └── claude.md                     # This file
├── .github/workflows/
│   └── create-pdf.yml                # GitHub Actions (to be updated)
├── docs/
│   └── project-planning/
│       └── refactoring-plan.md       # Comprehensive PM document
├── resume_builder/                   # Core build system
│   ├── resume.json                   # LEGACY - to be replaced
│   ├── resume.yaml                   # NEW - master resume (Phase 1)
│   ├── profiles/                     # NEW - profile configs (Phase 1)
│   │   ├── default.yaml
│   │   ├── leadership.yaml
│   │   └── technical.yaml
│   ├── profile_manager.py            # NEW - filtering logic (Phase 1)
│   ├── html_generator.py             # TO UPDATE - Phase 2
│   ├── md_generator.py               # TO UPDATE - Phase 2
│   └── build_all.sh                  # TO UPDATE - Phase 2
├── css/                              # Styling
├── js/                               # JavaScript
├── index.html                        # Generated homepage
└── resume.pdf                        # Generated PDF
```

## Important Files

### Source Data
- **`resume_builder/resume.json`** - CURRENT source (will be replaced)
- **`resume_builder/resume.yaml`** - FUTURE master resume (all content)
- **`resume_builder/profiles/*.yaml`** - Profile configurations

### Generators
- **`resume_builder/html_generator.py`** - JSON → HTML (needs YAML support)
- **`resume_builder/md_generator.py`** - JSON → Markdown (needs YAML support)
- **`resume_builder/profile_manager.py`** - NEW - Content filtering

### Build System
- **`resume_builder/build_all.sh`** - Orchestrates all generators
- **`.github/workflows/create-pdf.yml`** - CI/CD automation

### Deployment
- **AWS S3** - Static file hosting
- **CloudFront** - CDN and SSL
- **Route53** - DNS management
- **CodePipeline** - Auto-deploy from `main` branch

## Working with This Repository

### When Making Changes

1. **Always work on feature branches** - Current: `claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK`
2. **Test locally before committing** - Use `build_all.sh` in `resume_builder/`
3. **Validate YAML** - Ensure schema compliance before pushing
4. **Update documentation** - Keep `docs/` in sync with code changes
5. **Commit with descriptive messages** - Reference phase/task numbers

### Testing Changes Locally

```bash
cd resume_builder/
source build_all.sh
# Outputs: index.html, resume.md, resume.html, resume.pdf
```

### Git Workflow

```bash
# Current feature branch
git checkout claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK

# Make changes, then commit
git add .
git commit -m "Phase 1, Task 1.2: Convert resume.json to resume.yaml"

# Push to feature branch
git push -u origin claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK
```

### Creating Job Application Branches (Future)

```bash
# Branch naming convention
git checkout -b resume/company-position-name

# Add profile selection
echo "leadership" > resume_builder/active_profile.txt

# Add token (will be automated)
python3 scripts/generate_token.py > resume_builder/resume_token.txt

# Push triggers GitHub Actions
git push -u origin resume/company-position-name
```

## Implementation Phases

### Phase 1: Foundation & Migration (Current)
- [ ] Create YAML schema
- [ ] Convert resume.json → resume.yaml
- [ ] Create profile system
- [ ] Build profile manager

### Phase 2: Generator Updates
- [ ] Update HTML generator for YAML
- [ ] Update Markdown generator for YAML
- [ ] Create JSON export
- [ ] Update build scripts
- [ ] Remove JSON dependencies

### Phase 3: Branch Workflow & Automation
- [ ] Token generation system
- [ ] Branch template scripts
- [ ] Enhanced GitHub Actions
- [ ] S3 deployment updates
- [ ] Documentation

### Phase 4: Content Enhancement & Testing
- [ ] Master resume expansion
- [ ] Profile refinement
- [ ] Test job branches
- [ ] Integration testing
- [ ] Main branch deployment

### Phase 5: Polish & Future-Proofing
- [ ] Error handling
- [ ] Monitoring & logging
- [ ] Helper scripts
- [ ] Final documentation
- [ ] Future roadmap

**See:** `docs/project-planning/refactoring-plan.md` for complete details

## Common Tasks

### Add New Profile

1. Create `resume_builder/profiles/new-profile.yaml`
2. Define filters and settings
3. Test with: `build_all.sh --profile new-profile`

### Add Content to Master Resume

1. Edit `resume_builder/resume.yaml`
2. Add `include_in: [profile1, profile2, all]` tags
3. Validate schema
4. Test profile filtering

### Update Website

1. Make changes to generators or CSS
2. Run `build_all.sh` locally
3. Commit and push to `main` (after merge)
4. CodePipeline auto-deploys to S3

### Debug Build Issues

1. Check GitHub Actions logs
2. Test locally with `build_all.sh`
3. Validate YAML syntax
4. Check wkhtmltopdf/Pandoc versions

## Key Principles

1. **Single Source of Truth** - Master resume.yaml contains everything
2. **Never Delete Content** - Archive in master, hide via profiles
3. **Profile-First Thinking** - Design for multiple resume variants
4. **Automation Over Manual Work** - Scripts for repetitive tasks
5. **Documentation is Code** - Keep docs updated with changes

## Style Guidelines

### YAML Formatting
- Use 2-space indentation
- Add comments for clarity
- Group related items
- Keep line length < 100 chars

### Python Code
- Follow PEP 8
- Type hints for functions
- Docstrings for modules
- Unit tests for logic

### Commit Messages
- Format: "Phase X, Task Y.Z: Description"
- Example: "Phase 1, Task 1.2: Convert resume.json to resume.yaml"
- Reference issues if applicable

## Dependencies

### Python Packages
- PyYAML - YAML parsing
- Jinja2 - Template rendering (optional)
- pytest - Testing (optional)

### System Tools
- Pandoc 3.0+ - Document conversion
- wkhtmltopdf 0.12.6+ - HTML to PDF
- Python 3.8+ - Script execution

### AWS Services
- S3 - Static hosting
- CloudFront - CDN
- Route53 - DNS
- CodePipeline - Deployment

## Troubleshooting

### Build Fails
- Check Python version (3.8+)
- Verify Pandoc/wkhtmltopdf installed
- Validate YAML syntax
- Check file permissions

### GitHub Actions Fails
- Review workflow logs
- Check YAML schema validation
- Verify S3 credentials
- Test locally first

### PDF Formatting Issues
- Check `resume-stylesheet.css`
- Verify wkhtmltopdf version
- Test HTML output first
- Check page break classes

## Future Enhancements

- LinkedIn integration (API research needed)
- Analytics tracking (download counts)
- Auto-expiring tokens
- Email notifications on build
- A/B testing different resume versions

## Questions or Issues?

1. Check `docs/project-planning/refactoring-plan.md`
2. Review this file for decisions
3. Test locally before pushing
4. Document any new patterns discovered

## Context for Claude AI

When working on this project:
1. **Read this file first** to understand current state
2. **Check phase status** in refactoring plan
3. **Follow git workflow** - use feature branches
4. **Test locally** before committing
5. **Update documentation** as you make changes
6. **Ask user** if architectural decisions needed

This project is well-structured with clear phases. Focus on completing current phase tasks before moving to next phase. Quality over speed - proper testing prevents deployment issues.

---

**Last Updated:** 2025-11-21
**Current Phase:** Phase 1 - Foundation & Migration
**Status:** Ready to begin implementation
