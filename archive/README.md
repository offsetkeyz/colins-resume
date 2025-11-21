# Archive Directory

This directory contains deprecated files from the JSON-to-YAML migration.

## Archived Files

| File | Original Location | Description |
|------|-------------------|-------------|
| `resume.json.deprecated` | `resume_builder/json_resume.json` | Original JSON resume data (source of truth before YAML migration) |
| `resume.json.deprecated.backup` | `resume_builder/json_resume.json.backup` | Backup of the original JSON file |

## Archive Date

These files were archived on 2025-11-21 as part of Task 2.6: Remove JSON Dependencies.

## Important Notes

- **Do NOT delete these files** - They are kept for reference and potential rollback scenarios
- The YAML system (`resume_builder/resume.yaml`) is now the primary data source
- If you need to reference the original JSON structure, these files are available here

## Migration History

1. **Phase 1**: JSON to YAML migration completed
2. **Phase 2**: YAML system validated and functional
3. **Phase 2.6**: JSON system archived (current)

## Rollback Information

If rollback is ever needed:
1. Copy `resume.json.deprecated` back to `resume_builder/json_resume.json`
2. Refer to `docs/ROLLBACK_PROCEDURE.md` for detailed instructions

## Retention Policy

These files should be retained for a minimum of 90 days after the migration is confirmed stable in production.
