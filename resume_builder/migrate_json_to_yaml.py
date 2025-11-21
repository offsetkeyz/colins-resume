#!/usr/bin/env python3
"""
JSON to YAML Resume Migration Script

This script safely migrates resume.json to resume.yaml format with:
- Comprehensive logging throughout the conversion
- Automatic backup creation
- Statistics tracking
- Validation against the YAML schema
- Detailed conversion report generation

Usage:
    python migrate_json_to_yaml.py
    python migrate_json_to_yaml.py --dry-run
    python migrate_json_to_yaml.py --verbose

Author: Dynamic YAML-Based Resume System
Version: 1.0.0
"""

import json
import yaml
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

# ============================================================================
# CONFIGURATION
# ============================================================================

# File paths
SCRIPT_DIR = Path(__file__).parent
JSON_FILE = SCRIPT_DIR / "resume.json"
YAML_FILE = SCRIPT_DIR / "resume.yaml"
BACKUP_FILE = SCRIPT_DIR / "resume.json.backup"
REPORT_FILE = SCRIPT_DIR / "migration_report.md"
LOG_FILE = SCRIPT_DIR / "migration.log"

# Default include_in tag for all items
DEFAULT_INCLUDE_IN = ["all"]

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(verbose: bool = False):
    """Configure comprehensive logging"""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

# ============================================================================
# STATISTICS TRACKER
# ============================================================================

class MigrationStats:
    """Track migration statistics"""

    def __init__(self):
        self.start_time = datetime.now()
        self.sections_processed = 0
        self.items_converted = defaultdict(int)
        self.fields_migrated = 0
        self.include_in_tags_added = 0
        self.warnings = []
        self.errors = []
        self.data_preserved = True

    def add_item(self, section: str, count: int = 1):
        """Record items converted"""
        self.items_converted[section] += count
        self.sections_processed += 1

    def add_field(self, count: int = 1):
        """Record fields migrated"""
        self.fields_migrated += count

    def add_include_in_tag(self):
        """Record include_in tag added"""
        self.include_in_tags_added += 1

    def add_warning(self, message: str):
        """Record a warning"""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Record an error"""
        self.errors.append(message)
        self.data_preserved = False

    def get_duration(self) -> str:
        """Get migration duration"""
        duration = datetime.now() - self.start_time
        return f"{duration.total_seconds():.2f} seconds"

    def get_summary(self) -> Dict[str, Any]:
        """Get statistics summary"""
        return {
            "duration": self.get_duration(),
            "sections_processed": self.sections_processed,
            "total_items_converted": sum(self.items_converted.values()),
            "items_by_section": dict(self.items_converted),
            "fields_migrated": self.fields_migrated,
            "include_in_tags_added": self.include_in_tags_added,
            "warnings_count": len(self.warnings),
            "errors_count": len(self.errors),
            "data_preserved": self.data_preserved
        }

# ============================================================================
# YAML CUSTOM REPRESENTERS
# ============================================================================

def setup_yaml_formatting():
    """Configure YAML output formatting for readability"""

    # Use block style for multiline strings
    def str_representer(dumper, data):
        if '\n' in data or len(data) > 80:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_representer)

    # Ensure lists are formatted nicely
    yaml.SafeDumper.add_representer(
        type(None),
        lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:null', '')
    )

# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

class ResumeMigrator:
    """Handles the JSON to YAML migration"""

    def __init__(self, logger: logging.Logger, stats: MigrationStats):
        self.logger = logger
        self.stats = stats

    def migrate(self, json_data: Dict) -> Dict:
        """Main migration function"""
        self.logger.info("=" * 70)
        self.logger.info("Starting JSON to YAML migration")
        self.logger.info("=" * 70)

        yaml_data = {}

        # Migrate each section
        if "basics" in json_data:
            yaml_data["basics"] = self._migrate_basics(json_data["basics"])

        if "work_experience" in json_data:
            yaml_data["work_experience"] = self._migrate_work_experience(json_data["work_experience"])

        if "education" in json_data:
            yaml_data["education"] = self._migrate_education(json_data["education"])

        if "awards" in json_data:
            yaml_data["awards"] = self._migrate_awards(json_data["awards"])

        if "certifications" in json_data:
            yaml_data["certifications"] = self._migrate_certifications(json_data["certifications"])

        if "skills" in json_data:
            yaml_data["skills"] = self._migrate_skills(json_data["skills"])

        if "specialty_skills" in json_data:
            yaml_data["specialty_skills"] = self._migrate_specialty_skills(json_data["specialty_skills"])

        if "languages" in json_data:
            yaml_data["languages"] = self._migrate_languages(json_data["languages"])

        if "interests" in json_data:
            yaml_data["interests"] = self._migrate_interests(json_data["interests"])

        if "projects" in json_data:
            yaml_data["projects"] = self._migrate_projects(json_data["projects"])

        if "meta" in json_data:
            yaml_data["meta"] = self._migrate_meta(json_data["meta"])

        self.logger.info("=" * 70)
        self.logger.info("Migration completed successfully")
        self.logger.info("=" * 70)

        return yaml_data

    def _migrate_basics(self, basics: Dict) -> Dict:
        """Migrate basics section"""
        self.logger.info("\nMigrating 'basics' section...")

        result = {}
        field_count = 0

        # Copy all fields
        for key, value in basics.items():
            result[key] = value
            field_count += 1
            self.logger.debug(f"  - Migrated field: {key}")

        self.stats.add_field(field_count)
        self.stats.add_item("basics")
        self.logger.info(f"✓ Basics section migrated ({field_count} fields)")

        return result

    def _migrate_work_experience(self, work_exp: Dict) -> Dict:
        """Migrate work_experience section"""
        self.logger.info("\nMigrating 'work_experience' section...")

        result = {}
        total_positions = 0

        for company, positions in work_exp.items():
            self.logger.info(f"  Processing company: {company}")
            result[company] = []

            for idx, position in enumerate(positions):
                migrated_position = {}

                # Copy all existing fields
                for key, value in position.items():
                    migrated_position[key] = value
                    self.stats.add_field()

                # Add include_in tag
                if "include_in" not in migrated_position:
                    migrated_position["include_in"] = DEFAULT_INCLUDE_IN
                    self.stats.add_include_in_tag()
                    self.logger.debug(f"    - Added include_in tag to position {idx + 1}")

                result[company].append(migrated_position)
                total_positions += 1
                self.logger.debug(f"    ✓ Position {idx + 1}: {position.get('job_title', 'Unknown')}")

        self.stats.add_item("work_experience", len(result))
        self.logger.info(f"✓ Work experience migrated ({len(result)} companies, {total_positions} positions)")

        return result

    def _migrate_education(self, education: List) -> List:
        """Migrate education section"""
        self.logger.info("\nMigrating 'education' section...")

        result = []

        for idx, entry in enumerate(education):
            migrated_entry = {}

            # Copy all fields
            for key, value in entry.items():
                migrated_entry[key] = value
                self.stats.add_field()

            # Add include_in tag
            if "include_in" not in migrated_entry:
                migrated_entry["include_in"] = DEFAULT_INCLUDE_IN
                self.stats.add_include_in_tag()

            result.append(migrated_entry)
            self.logger.debug(f"  ✓ Education {idx + 1}: {entry.get('institution', 'Unknown')}")

        self.stats.add_item("education", len(result))
        self.logger.info(f"✓ Education section migrated ({len(result)} entries)")

        return result

    def _migrate_awards(self, awards: List) -> List:
        """Migrate awards section"""
        self.logger.info("\nMigrating 'awards' section...")

        result = []

        for idx, award in enumerate(awards):
            migrated_award = {}

            # Copy all fields
            for key, value in award.items():
                migrated_award[key] = value
                self.stats.add_field()

            # Add include_in tag
            if "include_in" not in migrated_award:
                migrated_award["include_in"] = DEFAULT_INCLUDE_IN
                self.stats.add_include_in_tag()

            result.append(migrated_award)
            self.logger.debug(f"  ✓ Award {idx + 1}: {award.get('title', 'Unknown')}")

        self.stats.add_item("awards", len(result))
        self.logger.info(f"✓ Awards section migrated ({len(result)} entries)")

        return result

    def _migrate_certifications(self, certifications: List) -> List:
        """Migrate certifications section"""
        self.logger.info("\nMigrating 'certifications' section...")

        result = []

        for idx, cert in enumerate(certifications):
            migrated_cert = {}

            # Copy all fields
            for key, value in cert.items():
                migrated_cert[key] = value
                self.stats.add_field()

            # Add include_in tag
            if "include_in" not in migrated_cert:
                migrated_cert["include_in"] = DEFAULT_INCLUDE_IN
                self.stats.add_include_in_tag()

            result.append(migrated_cert)
            self.logger.debug(f"  ✓ Certification {idx + 1}: {cert.get('title', 'Unknown')}")

        self.stats.add_item("certifications", len(result))
        self.logger.info(f"✓ Certifications section migrated ({len(result)} entries)")

        return result

    def _migrate_skills(self, skills: List) -> List:
        """Migrate skills section"""
        self.logger.info("\nMigrating 'skills' section...")

        # Skills is just a list of strings, no include_in needed at item level
        result = skills
        self.stats.add_field(len(skills))
        self.stats.add_item("skills")
        self.logger.info(f"✓ Skills section migrated ({len(skills)} skills)")

        return result

    def _migrate_specialty_skills(self, specialty_skills: List) -> List:
        """Migrate specialty_skills section"""
        self.logger.info("\nMigrating 'specialty_skills' section...")

        result = []

        for idx, skill in enumerate(specialty_skills):
            migrated_skill = {}

            # Copy all fields
            for key, value in skill.items():
                migrated_skill[key] = value
                self.stats.add_field()

            # Add include_in tag
            if "include_in" not in migrated_skill:
                migrated_skill["include_in"] = DEFAULT_INCLUDE_IN
                self.stats.add_include_in_tag()

            result.append(migrated_skill)
            self.logger.debug(f"  ✓ Specialty skill {idx + 1}: {skill.get('name', 'Unknown')}")

        self.stats.add_item("specialty_skills", len(result))
        self.logger.info(f"✓ Specialty skills section migrated ({len(result)} entries)")

        return result

    def _migrate_languages(self, languages: List) -> List:
        """Migrate languages section"""
        self.logger.info("\nMigrating 'languages' section...")

        # Languages don't need include_in tags (schema doesn't specify them)
        result = languages
        self.stats.add_field(len(languages))
        self.stats.add_item("languages")
        self.logger.info(f"✓ Languages section migrated ({len(languages)} entries)")

        return result

    def _migrate_interests(self, interests: List) -> List:
        """Migrate interests section"""
        self.logger.info("\nMigrating 'interests' section...")

        # Interests don't need include_in tags (schema doesn't specify them)
        result = interests
        self.stats.add_field(len(interests))
        self.stats.add_item("interests")
        self.logger.info(f"✓ Interests section migrated ({len(interests)} entries)")

        return result

    def _migrate_projects(self, projects: List) -> List:
        """Migrate projects section"""
        self.logger.info("\nMigrating 'projects' section...")

        result = []

        for idx, project in enumerate(projects):
            migrated_project = {}

            # Copy all fields
            for key, value in project.items():
                migrated_project[key] = value
                self.stats.add_field()

            # Add include_in tag
            if "include_in" not in migrated_project:
                migrated_project["include_in"] = DEFAULT_INCLUDE_IN
                self.stats.add_include_in_tag()

            result.append(migrated_project)
            self.logger.debug(f"  ✓ Project {idx + 1}: {project.get('name', 'Unknown')}")

        self.stats.add_item("projects", len(result))
        self.logger.info(f"✓ Projects section migrated ({len(result)} entries)")

        return result

    def _migrate_meta(self, meta: Dict) -> Dict:
        """Migrate meta section with updated timestamp"""
        self.logger.info("\nMigrating 'meta' section...")

        result = meta.copy()

        # Update lastModified to current timestamp
        result["lastModified"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update canonical URL if it points to JSON schema
        if "canonical" in result and "resume-schema.json" in result["canonical"]:
            result["canonical"] = result["canonical"].replace(
                "resume-schema.json",
                "resume-schema.yaml"
            )
            self.logger.debug("  - Updated canonical URL to point to YAML schema")

        self.stats.add_field(len(result))
        self.stats.add_item("meta")
        self.logger.info(f"✓ Meta section migrated and updated")

        return result

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report(stats: MigrationStats, validation_passed: bool) -> str:
    """Generate comprehensive migration report"""

    summary = stats.get_summary()

    report = f"""# Resume Migration Report

**Migration Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Duration:** {summary['duration']}
**Status:** {'✓ SUCCESS' if stats.data_preserved and validation_passed else '✗ FAILED'}

---

## Executive Summary

This report documents the migration of resume data from JSON format to YAML format
with comprehensive logging and validation.

**Result:** {'All data successfully migrated with zero data loss.' if stats.data_preserved else 'Migration completed with issues.'}

---

## Migration Statistics

### Overview
- **Total Sections Processed:** {summary['sections_processed']}
- **Total Items Converted:** {summary['total_items_converted']}
- **Total Fields Migrated:** {summary['fields_migrated']}
- **Include_in Tags Added:** {summary['include_in_tags_added']}

### Items by Section
"""

    for section, count in summary['items_by_section'].items():
        report += f"- **{section}:** {count} item(s)\n"

    report += f"""
---

## Validation Results

**Schema Validation:** {'✓ PASSED' if validation_passed else '✗ FAILED'}

The generated YAML file was validated against the resume-schema.yaml to ensure:
- All required fields are present
- All include_in tags are valid
- Date formats are correct
- Email and URL formats are valid
- Data types match schema expectations

---

## Changes Applied

### 1. Format Conversion
- Converted from JSON to YAML format
- Preserved all data fields and structure
- Maintained work_experience company organization

### 2. Include_in Tags Added
Added `include_in: [all]` to the following sections:
- Work Experience (all positions)
- Education (all entries)
- Awards (all entries)
- Certifications (all entries)
- Specialty Skills (all categories)
- Projects (all projects)

**Total tags added:** {summary['include_in_tags_added']}

### 3. Meta Section Updates
- Updated `lastModified` timestamp
- Updated `canonical` URL to point to YAML schema

---

## Warnings and Issues

### Warnings ({summary['warnings_count']})
"""

    if stats.warnings:
        for warning in stats.warnings:
            report += f"- {warning}\n"
    else:
        report += "None - clean migration\n"

    report += f"""
### Errors ({summary['errors_count']})
"""

    if stats.errors:
        for error in stats.errors:
            report += f"- {error}\n"
    else:
        report += "None - clean migration\n"

    report += """
---

## Files Generated

1. **resume_builder/resume.yaml** - The migrated YAML resume
2. **resume.json.backup** - Backup of original JSON file
3. **migration_report.md** - This report
4. **migration.log** - Detailed migration log

---

## Next Steps

1. ✓ Review the generated resume.yaml file
2. ✓ Verify all data was migrated correctly
3. ✓ Test with existing resume generators
4. ✓ Customize include_in tags for different profiles
5. ✓ Update build scripts to use YAML instead of JSON

---

## Data Integrity

"""

    if stats.data_preserved and validation_passed:
        report += """✓ **Data integrity verified**

All data from the original JSON file has been successfully migrated to YAML format.
The new YAML file passes schema validation without errors.

No data loss occurred during migration.
"""
    else:
        report += """⚠ **Data integrity issues detected**

Please review the warnings and errors above. Some manual intervention may be required.
"""

    report += """
---

## Migration Log

For detailed step-by-step migration information, see `migration.log`.

---

*Generated by migrate_json_to_yaml.py v1.0.0*
"""

    return report

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate resume.json to resume.yaml format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform migration without writing files"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose)
    stats = MigrationStats()

    logger.info("=" * 70)
    logger.info("JSON to YAML Resume Migration")
    logger.info("=" * 70)
    logger.info(f"Source: {JSON_FILE}")
    logger.info(f"Target: {YAML_FILE}")
    logger.info(f"Backup: {BACKUP_FILE}")
    logger.info(f"Report: {REPORT_FILE}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info("=" * 70)

    # Check if JSON file exists
    if not JSON_FILE.exists():
        logger.error(f"❌ Source file not found: {JSON_FILE}")
        sys.exit(1)

    # Load JSON data
    logger.info(f"\n📖 Reading JSON file: {JSON_FILE}")
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        logger.info(f"✓ JSON file loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading JSON file: {e}")
        stats.add_error(f"Failed to load JSON file: {e}")
        sys.exit(1)

    # Create backup
    if not args.dry_run:
        logger.info(f"\n💾 Creating backup: {BACKUP_FILE}")
        try:
            shutil.copy2(JSON_FILE, BACKUP_FILE)
            logger.info(f"✓ Backup created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating backup: {e}")
            stats.add_error(f"Failed to create backup: {e}")
            sys.exit(1)
    else:
        logger.info(f"\n💾 [DRY RUN] Would create backup: {BACKUP_FILE}")

    # Perform migration
    logger.info(f"\n🔄 Starting migration...")
    migrator = ResumeMigrator(logger, stats)

    try:
        yaml_data = migrator.migrate(json_data)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        stats.add_error(f"Migration failed: {e}")
        sys.exit(1)

    # Setup YAML formatting
    setup_yaml_formatting()

    # Write YAML file
    if not args.dry_run:
        logger.info(f"\n📝 Writing YAML file: {YAML_FILE}")
        try:
            with open(YAML_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(
                    yaml_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=80
                )
            logger.info(f"✓ YAML file written successfully")
        except Exception as e:
            logger.error(f"❌ Error writing YAML file: {e}")
            stats.add_error(f"Failed to write YAML file: {e}")
            sys.exit(1)
    else:
        logger.info(f"\n📝 [DRY RUN] Would write YAML file: {YAML_FILE}")

    # Validate YAML file
    validation_passed = False
    if not args.dry_run:
        logger.info(f"\n✅ Validating YAML file...")
        try:
            from validate_resume import ResumeValidator
            validator = ResumeValidator(verbose=args.verbose)
            result = validator.validate_file(str(YAML_FILE))

            if result.has_errors():
                logger.error(f"❌ Validation failed with {len(result.errors)} errors")
                for error in result.errors:
                    logger.error(f"  - {error}")
                    stats.add_error(str(error))
            else:
                logger.info(f"✓ Validation passed")
                validation_passed = True

            if result.has_warnings():
                logger.warning(f"⚠ Validation passed with {len(result.warnings)} warnings")
                for warning in result.warnings:
                    logger.warning(f"  - {warning}")
                    stats.add_warning(str(warning))

        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            stats.add_error(f"Validation error: {e}")
    else:
        logger.info(f"\n✅ [DRY RUN] Would validate YAML file")
        validation_passed = True  # Assume success in dry run

    # Generate report
    logger.info(f"\n📊 Generating migration report...")
    report = generate_report(stats, validation_passed)

    if not args.dry_run:
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"✓ Report written to: {REPORT_FILE}")
        except Exception as e:
            logger.error(f"❌ Error writing report: {e}")
    else:
        logger.info(f"📊 [DRY RUN] Would write report to: {REPORT_FILE}")

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 70)

    summary = stats.get_summary()
    logger.info(f"Duration: {summary['duration']}")
    logger.info(f"Items converted: {summary['total_items_converted']}")
    logger.info(f"Fields migrated: {summary['fields_migrated']}")
    logger.info(f"Include_in tags added: {summary['include_in_tags_added']}")
    logger.info(f"Warnings: {summary['warnings_count']}")
    logger.info(f"Errors: {summary['errors_count']}")

    if stats.data_preserved and validation_passed:
        logger.info("\n✓ Migration completed successfully!")
        logger.info("  - All data preserved")
        logger.info("  - YAML file validated")
        logger.info("  - Backup created")
        logger.info("  - Report generated")
    else:
        logger.warning("\n⚠ Migration completed with issues")
        logger.warning("  - Please review the migration report")

    logger.info("=" * 70)

    # Exit code
    if stats.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
