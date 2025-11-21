# Quick Reference Guide

## Common Commands

### Local Build
```bash
cd resume_builder/
source build_all.sh
# Outputs: index.html, resume.md, resume.html, resume.pdf
```

### Test with Profile (After Phase 2)
```bash
cd resume_builder/
./build_all.sh --profile leadership
./build_all.sh --profile technical
```

### Validate YAML (After Phase 1)
```bash
cd resume_builder/
python3 validate_resume.py resume.yaml
```

### Create Job Application Branch (After Phase 3)
```bash
./scripts/new-job-application.sh aws-security-engineer technical
# Creates resume/aws-security-engineer branch
# Sets active_profile.txt to "technical"
# Generates unique token
```

---

## File Locations

| What | Where |
|------|-------|
| Master Resume | `resume_builder/resume.yaml` |
| Profiles | `resume_builder/profiles/*.yaml` |
| Generators | `resume_builder/*_generator.py` |
| Build Script | `resume_builder/build_all.sh` |
| GitHub Actions | `.github/workflows/create-pdf.yml` |
| Documentation | `docs/project-planning/` |
| Helper Scripts | `scripts/` (Phase 5) |

---

## Git Workflow

### Feature Branch Work
```bash
# Current branch
git checkout claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK

# Make changes
git add .
git commit -m "Phase X, Task Y: Description"
git push -u origin claude/dynamic-resume-yaml-01NN6fTVNXibJGBMS4QJDpSK
```

### Job Application Branch
```bash
# Create from main
git checkout main
git pull origin main
git checkout -b resume/company-position

# Add profile config
echo "leadership" > resume_builder/active_profile.txt
git add resume_builder/active_profile.txt
git commit -m "Configure profile for Company position"

# Push triggers build
git push -u origin resume/company-position
```

---

## Profile System

### Available Profiles (After Phase 1)
- **default** - Full resume with all content
- **leadership** - Management and team leadership focus
- **technical** - Development and technical skills focus

### Add Content to Master Resume
```yaml
work_experience:
  "Company Name":
    - job_title: "Position"
      responsibilities:
        - text: "Your achievement here"
          include_in: [leadership, all]  # Shows in leadership + all profiles
        - text: "Technical achievement"
          include_in: [technical, all]   # Shows in technical + all profiles
```

### Create New Profile
```yaml
# resume_builder/profiles/security-focused.yaml
profile:
  name: "Security Focused"
  description: "Emphasizes cybersecurity experience"
  slug: "security"

filters:
  include_tags: [security, technical, all]
  max_bullets_per_job: 4

output:
  title_suffix: " - Security Focus"
  filename: "resume-security"
```

---

## Troubleshooting

### Build Fails
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
which pandoc       # Should return path
which wkhtmltopdf  # Should return path

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('resume_builder/resume.yaml'))"

# Check file permissions
ls -la resume_builder/
```

### GitHub Actions Fails
```bash
# View workflow runs
# Visit: https://github.com/offsetkeyz/colins-resume/actions

# Test locally first
cd resume_builder/
source build_all.sh

# Check logs for specific error
# Look for: YAML validation, Pandoc errors, wkhtmltopdf issues
```

### PDF Formatting Issues
```bash
# Test HTML generation first
cd resume_builder/
python3 html_generator.py

# Check stylesheet
ls -la resume-stylesheet.css

# Test Pandoc conversion
pandoc resume.md -f markdown -t html -c resume-stylesheet.css -s -o test.html

# Test wkhtmltopdf
wkhtmltopdf --enable-local-file-access test.html test.pdf
```

---

## Phase Status

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 1 | 🔵 Planned | YAML migration, profiles, profile_manager |
| Phase 2 | 🔵 Planned | Generator updates, JSON removal |
| Phase 3 | 🔵 Planned | Branch workflow, tokens, GitHub Actions |
| Phase 4 | 🔵 Planned | Content expansion, testing, deployment |
| Phase 5 | 🔵 Planned | Polish, documentation, helper scripts |

Legend: 🔵 Planned | 🟡 In Progress | 🟢 Complete | 🔴 Blocked

---

## URLs & Access

| Environment | URL | Notes |
|------------|-----|-------|
| Production | https://colinmca.com | Main website (default profile) |
| PDF Download | https://colinmca.com/resume.pdf | Public resume PDF |
| Job-Specific | https://colinmca.com/r/{token}/ | Private URLs (Phase 3+) |
| GitHub | https://github.com/offsetkeyz/colins-resume | Repository |

---

## Key Contacts

| Role | Contact |
|------|---------|
| Owner | Colin McAllister |
| Email | colin@thedailydecrypt.com |
| Website | https://colinmca.com |
| GitHub | @offsetkeyz |

---

## Emergency Procedures

### Rollback to Previous Version
```bash
# Revert to last working commit
git log --oneline -10
git revert <commit-hash>
git push origin <branch>

# Or hard reset (use carefully)
git reset --hard <commit-hash>
git push --force origin <branch>  # Only on feature branches!
```

### Restore from Backup
```bash
# JSON backup (Phase 1 transition only)
cp resume_builder/resume.json.backup resume_builder/resume.json

# Git restore
git checkout HEAD~1 -- resume_builder/resume.yaml
```

### Contact AWS Support
- Issue: Deployment or S3 access problems
- Action: Check CodePipeline, S3 bucket permissions, CloudFront cache
- Console: https://console.aws.amazon.com

---

## Tips & Best Practices

1. **Test locally before pushing** - Saves GitHub Actions minutes
2. **Commit often** - Small commits are easier to debug
3. **Tag important versions** - `git tag v2.0.0` for milestones
4. **Validate YAML** - Syntax errors break builds
5. **Profile tags are inclusive** - Use "all" for universal content
6. **Document as you go** - Future you will thank present you
7. **Keep master resume comprehensive** - Never delete content
8. **Token security** - 12+ characters, cryptographically random

---

## Learning Resources

### YAML
- [YAML Specification](https://yaml.org/spec/)
- [Learn YAML in Y Minutes](https://learnxinyminutes.com/docs/yaml/)

### Python
- [Python Official Docs](https://docs.python.org/3/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

### Git Workflows
- [Git Branching](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging)
- [GitHub Actions](https://docs.github.com/en/actions)

### AWS
- [S3 Static Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront](https://docs.aws.amazon.com/cloudfront/)

---

**Last Updated:** 2025-11-21
**Maintained By:** Project team
**Version:** 1.0 (Planning Phase)
