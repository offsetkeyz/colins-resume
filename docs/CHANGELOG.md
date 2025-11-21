# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planning Phase
- Created comprehensive project management document
- Established architectural decision records
- Designed YAML-based resume system architecture
- Planned 5-phase implementation roadmap

---

## [1.0.2] - 2025-11-21 (Previous State)

### Added
- Certificate acronym support in resume data
- Separate acronym field for certifications
- Leadership content updates

### Fixed
- Acronym display bug in PDF generation
- Certificate formatting issues

### Changed
- Optimized resume length for better readability
- Updated certificate display to include acronyms

---

## Planned Changes (Future Versions)

### [2.0.0] - YAML Migration (Phase 1-2)
#### Added
- YAML data format support
- Master resume with tagging system (include_in)
- Profile management system (default, leadership, technical)
- Profile filtering logic (profile_manager.py)
- YAML schema validation

#### Changed
- All generators updated to use YAML instead of JSON
- Build scripts support profile parameter

#### Removed
- JSON format support (migrated to YAML)
- resume.json file

---

### [2.1.0] - Branch Workflow (Phase 3)
#### Added
- Token generation system for private URLs
- Job branch template and setup scripts
- Enhanced GitHub Actions for branch-based builds
- Support for resume/{job-identifier} branch naming
- S3 deployment to /r/{token}/ paths

#### Changed
- GitHub Actions workflow detects branch type
- Deployment strategy supports multiple resume versions

---

### [2.2.0] - Content Enhancement (Phase 4)
#### Added
- Expanded master resume with comprehensive content
- Multiple profile variations tested in production
- Test job branches for validation
- Integration test suite

#### Changed
- Profile configurations refined based on output
- PDF formatting optimized for different profiles

---

### [2.3.0] - Polish & Documentation (Phase 5)
#### Added
- Helper scripts for common tasks
- Comprehensive error handling
- Build monitoring and logging
- Complete user and developer documentation
- Future roadmap document

#### Changed
- README updated with new system overview
- Architecture diagrams added

---

## Version History Reference

### Version Numbering Scheme
- **Major (X.0.0)**: Breaking changes, significant architecture updates
- **Minor (x.Y.0)**: New features, profiles, or workflows
- **Patch (x.y.Z)**: Bug fixes, content updates, minor improvements

### Past Versions
- **1.0.2**: Current production version (JSON-based)
- **1.0.1**: Previous iterations with bug fixes
- **1.0.0**: Initial cloud resume implementation

---

## Migration Notes

### From JSON to YAML (v1.x to v2.0)
- All resume data migrated from resume.json to resume.yaml
- No functional changes to website or PDF output
- Backward compatibility: Not maintained (clean cutover)
- Migration script: `resume_builder/migrate_json_to_yaml.py`

---

## Maintenance Log

| Date | Version | Maintainer | Notes |
|------|---------|------------|-------|
| 2025-11-21 | Planning | Claude AI | Created PM documents and planning phase |
| 2025-11-21 | 1.0.2 | Colin McAllister | Current production version |

---

**Note:** This changelog will be updated as each phase is completed. Version numbers are subject to change based on actual implementation timeline.
