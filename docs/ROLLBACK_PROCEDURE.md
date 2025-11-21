# Rollback Procedure for YAML Resume Migration

**Document Version:** 1.1.0
**Last Updated:** 2025-11-21
**Status:** Active (JSON Archived)

---

## Overview

This document provides step-by-step instructions for rolling back from the YAML-based resume system to the original JSON-based system in case critical issues are discovered.

**Note:** As of 2025-11-21, the JSON source has been archived. The YAML system is now the primary data source.

## Prerequisites

Before proceeding with a rollback, ensure:
- Access to the repository
- Ability to run Python scripts
- Familiarity with git commands

## Critical Files

The following files are part of the migration:

| File | Purpose | Status |
|------|---------|--------|
| `archive/resume.json.deprecated` | Original JSON source | Archived (was `resume_builder/json_resume.json`) |
| `resume_builder/resume.yaml` | YAML format | **PRIMARY SOURCE** |
| `resume_builder/profile_manager.py` | Profile filtering logic | Version controlled |
| `resume_builder/profiles/*.yaml` | Profile configurations | Version controlled |

## Rollback Decision Matrix

| Scenario | Action | Urgency |
|----------|--------|---------|
| Minor formatting differences | Continue with YAML, note in docs | Low |
| Missing data in YAML | Re-run migration, investigate | Medium |
| Build system failures | Rollback to JSON | High |
| Production deployment issues | Immediate rollback | Critical |

---

## Rollback Procedure

### Step 1: Verify Current State

```bash
# Check current branch
cd /home/user/colins-resume
git status

# Verify archived JSON source file exists
ls -la archive/resume.json.deprecated
```

### Step 2: Quick Rollback (Build System Only)

If the issue is with the build system, you can temporarily switch back to JSON without reverting code:

```bash
# Option A: Restore JSON from archive
# Copy archived JSON to resume_builder directory
cp archive/resume.json.deprecated resume_builder/json_resume.json

# Uncomment the read_json_file function in md_generator.py and html_generator.py
# Then modify load_resume_data to use JSON instead of YAML
```

### Step 3: Full Code Rollback

If a complete rollback is needed:

```bash
# Create a rollback branch
git checkout -b rollback/yaml-migration-$(date +%Y%m%d)

# Option A: Revert to previous commit (before YAML migration)
# Find the commit before migration started
git log --oneline -20

# Revert to that commit
git revert HEAD~N..HEAD  # Where N is number of commits to revert

# Option B: Reset specific files
git checkout main -- resume_builder/md_generator.py
git checkout main -- resume_builder/html_generator.py
git checkout main -- resume_builder/build_all.sh

# Commit the rollback
git commit -m "Rollback: Revert YAML migration changes"
```

### Step 4: Restore JSON-Only Operation

To operate purely on JSON:

```python
# In Python scripts, change YAML loading to JSON:

# Before (YAML):
import yaml
with open('resume.yaml', 'r') as f:
    data = yaml.safe_load(f)

# After (JSON):
import json
with open('json_resume.json', 'r') as f:
    data = json.load(f)
```

### Step 5: Verify Rollback Success

```bash
# Run the original build process
cd resume_builder
./build_all.sh

# Verify output files are generated
ls -la ../resume.pdf
ls -la ../index.html

# Check for any errors in output
echo "Build completed. Verify PDF and HTML manually."
```

---

## Re-Migration After Rollback

If issues are fixed and you want to re-attempt migration:

### Step 1: Fix Identified Issues

```bash
# Review validation report
cat resume_builder/validation_report.md

# Fix issues in migrate_json_to_yaml.py
# Or fix source data in archive/resume.json.deprecated
```

### Step 2: Re-run Migration

```bash
# Clear previous migration artifacts
rm -f resume_builder/resume.yaml
rm -f resume_builder/migration_report.md
rm -f resume_builder/migration.log

# Run migration again
cd resume_builder
python3 migrate_json_to_yaml.py --verbose
```

### Step 3: Run Validation

```bash
# Run validation tests
python3 test_migration_validation.py

# Or with pytest
pytest test_migration_validation.py -v

# Verify validation report
cat validation_report.md
```

---

## Emergency Contacts

If rollback fails or critical issues arise:

1. Check repository issues for known problems
2. Review migration logs in `resume_builder/migration.log`
3. Consult validation report in `resume_builder/validation_report.md`

---

## Rollback Verification Checklist

After rollback, verify:

- [ ] `archive/resume.json.deprecated` is intact and valid JSON
- [ ] JSON has been restored to `resume_builder/json_resume.json`
- [ ] Build scripts execute without errors
- [ ] PDF is generated correctly
- [ ] HTML is generated correctly
- [ ] No data loss in generated outputs
- [ ] Website displays resume correctly (if deployed)

---

## Timeline for Backup Retention

| Phase | Status |
|-------|--------|
| Phase 1-3 | Completed |
| Phase 4 | JSON archived to `archive/resume.json.deprecated` |
| Post-migration | Keep archived JSON for 90 days minimum from 2025-11-21 |

---

## Recovery Scripts

### Script 1: Quick JSON Restore

```bash
#!/bin/bash
# quick_restore.sh
# Quickly restore JSON-based operation from archive

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Verify archived JSON exists
if [ ! -f "$PROJECT_ROOT/archive/resume.json.deprecated" ]; then
    echo "ERROR: archive/resume.json.deprecated not found!"
    exit 1
fi

# Restore from archive
cp "$PROJECT_ROOT/archive/resume.json.deprecated" "$PROJECT_ROOT/resume_builder/json_resume.json"

echo "JSON restored from archive. Edit generators to use JSON, then run ./build_all.sh to rebuild."
```

### Script 2: Full Validation Re-run

```bash
#!/bin/bash
# revalidate.sh
# Re-run all validation tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/resume_builder"

echo "Running validation tests..."
python3 -m pytest test_migration_validation.py -v --tb=short

echo ""
echo "Running validation report generator..."
python3 test_migration_validation.py

echo ""
echo "Validation complete. Check validation_report.md for results."
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-21 | Initial rollback procedure document |
| 1.1.0 | 2025-11-21 | Updated for JSON archival (Task 2.6) - JSON moved to archive/ directory |

---

*This document is part of the YAML Resume Migration project (Task 1.5, updated for Task 2.6)*
