#!/usr/bin/env python3
"""
Resume YAML Validator

This script validates resume YAML files against the resume schema.
It checks for:
- Required fields
- include_in tag validity
- Date format validation
- Email and URL format validation
- Data type validation

Usage:
    python validate_resume.py resume.yaml
    python validate_resume.py resume.yaml --verbose
    python validate_resume.py resume.yaml --strict

Exit codes:
    0: Validation passed
    1: Validation failed with errors
    2: Validation passed with warnings (--strict makes this exit 1)
"""

import sys
import re
import yaml
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from pathlib import Path

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

ALLOWED_INCLUDE_IN_TAGS = [
    "all",
    "leadership",
    "management",
    "technical",
    "development",
    "consulting",
    "startup"
]

DATE_REGEX = re.compile(r"^([1-2][0-9]{3}(-[0-1][0-9](-[0-3][0-9])?)?|Present)$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_REGEX = re.compile(r"^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$")

REQUIRED_ROOT_FIELDS = ["basics"]

# ============================================================================
# VALIDATION RESULT CLASSES
# ============================================================================

class ValidationMessage:
    """Represents a validation error or warning"""

    def __init__(self, level: str, field_path: str, message: str, suggestion: Optional[str] = None):
        self.level = level  # "ERROR", "WARNING", "INFO"
        self.field_path = field_path
        self.message = message
        self.suggestion = suggestion

    def __str__(self):
        result = f"[{self.level}] {self.field_path}: {self.message}"
        if self.suggestion:
            result += f"\n  → Suggestion: {self.suggestion}"
        return result

    def __repr__(self):
        return f"ValidationMessage({self.level}, {self.field_path})"


class ValidationResult:
    """Stores validation results"""

    def __init__(self):
        self.errors: List[ValidationMessage] = []
        self.warnings: List[ValidationMessage] = []
        self.info: List[ValidationMessage] = []

    def add_error(self, field_path: str, message: str, suggestion: Optional[str] = None):
        self.errors.append(ValidationMessage("ERROR", field_path, message, suggestion))

    def add_warning(self, field_path: str, message: str, suggestion: Optional[str] = None):
        self.warnings.append(ValidationMessage("WARNING", field_path, message, suggestion))

    def add_info(self, field_path: str, message: str):
        self.info.append(ValidationMessage("INFO", field_path, message))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def is_valid(self, strict: bool = False) -> bool:
        if strict:
            return not self.has_errors() and not self.has_warnings()
        return not self.has_errors()

    def get_summary(self) -> str:
        return f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Info: {len(self.info)}"


# ============================================================================
# VALIDATOR CLASS
# ============================================================================

class ResumeValidator:
    """Validates resume YAML files against schema"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.result = ValidationResult()

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a resume YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            self.result.add_error("file", f"File not found: {file_path}")
            return self.result
        except yaml.YAMLError as e:
            self.result.add_error("file", f"YAML parsing error: {str(e)}",
                                  "Check for invalid YAML syntax, missing colons, or incorrect indentation")
            return self.result

        if data is None:
            self.result.add_error("file", "YAML file is empty")
            return self.result

        # Run all validations
        self._validate_structure(data)
        self._validate_basics(data.get("basics", {}))
        self._validate_work_experience(data.get("work_experience", {}))
        self._validate_education(data.get("education", []))
        self._validate_awards(data.get("awards", []))
        self._validate_certifications(data.get("certifications", []))
        self._validate_projects(data.get("projects", []))
        self._validate_volunteer(data.get("volunteer", []))
        self._validate_specialty_skills(data.get("specialty_skills", []))

        return self.result

    def _validate_structure(self, data: Dict):
        """Validate root-level structure"""
        for required_field in REQUIRED_ROOT_FIELDS:
            if required_field not in data:
                self.result.add_error(
                    "root",
                    f"Missing required field: {required_field}",
                    f"Add '{required_field}:' section to your resume"
                )

    def _validate_basics(self, basics: Dict):
        """Validate basics section"""
        if not basics:
            return

        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in basics:
                self.result.add_error(
                    "basics",
                    f"Missing required field: {field}",
                    f"Add 'basics.{field}' to your resume"
                )

        # Validate email format
        if "email" in basics and basics["email"]:
            if not EMAIL_REGEX.match(basics["email"]):
                self.result.add_error(
                    "basics.email",
                    f"Invalid email format: {basics['email']}",
                    "Use format: user@example.com"
                )

        # Validate URL format
        if "url" in basics and basics["url"]:
            if not URL_REGEX.match(basics["url"]):
                self.result.add_error(
                    "basics.url",
                    f"Invalid URL format: {basics['url']}",
                    "URL must start with http:// or https://"
                )

        # Validate profiles
        if "profiles" in basics and basics["profiles"]:
            for idx, profile in enumerate(basics["profiles"]):
                self._validate_profile(profile, f"basics.profiles[{idx}]")

    def _validate_profile(self, profile: Dict, path: str):
        """Validate a social profile entry"""
        required = ["network", "url"]
        for field in required:
            if field not in profile:
                self.result.add_error(path, f"Missing required field: {field}")

        if "url" in profile and profile["url"]:
            if not URL_REGEX.match(profile["url"]):
                self.result.add_error(
                    f"{path}.url",
                    f"Invalid URL: {profile['url']}",
                    "URL must start with http:// or https://"
                )

    def _validate_work_experience(self, work_exp: Dict):
        """Validate work experience section"""
        if not work_exp:
            return

        if not isinstance(work_exp, dict):
            self.result.add_error(
                "work_experience",
                "work_experience must be an object with company names as keys"
            )
            return

        for company, positions in work_exp.items():
            if not isinstance(positions, list):
                self.result.add_error(
                    f"work_experience.{company}",
                    "Company entry must be an array of positions"
                )
                continue

            for idx, position in enumerate(positions):
                self._validate_position(position, f"work_experience.{company}[{idx}]")

    def _validate_position(self, position: Dict, path: str):
        """Validate a single position entry"""
        required_fields = ["job_title", "location", "start_date", "end_date"]
        for field in required_fields:
            if field not in position:
                self.result.add_error(path, f"Missing required field: {field}")

        # Validate dates
        if "start_date" in position:
            self._validate_date(position["start_date"], f"{path}.start_date")

        if "end_date" in position:
            self._validate_date(position["end_date"], f"{path}.end_date")

        # Validate include_in tags at position level
        if "include_in" in position:
            self._validate_include_in_tags(position["include_in"], path)

        # Validate responsibilities
        if "responsibilities" in position and position["responsibilities"]:
            for idx, resp in enumerate(position["responsibilities"]):
                if isinstance(resp, dict):
                    # Object with include_in tag
                    if "description" not in resp:
                        self.result.add_error(
                            f"{path}.responsibilities[{idx}]",
                            "Responsibility object must have 'description' field"
                        )
                    if "include_in" in resp:
                        self._validate_include_in_tags(
                            resp["include_in"],
                            f"{path}.responsibilities[{idx}]"
                        )
                elif not isinstance(resp, str):
                    self.result.add_error(
                        f"{path}.responsibilities[{idx}]",
                        "Responsibility must be a string or object with description and include_in"
                    )

        # Validate projects
        if "projects" in position and position["projects"]:
            for idx, project in enumerate(position["projects"]):
                self._validate_project_in_position(project, f"{path}.projects[{idx}]")

    def _validate_project_in_position(self, project: Dict, path: str):
        """Validate a project within a work position"""
        required = ["name", "description"]
        for field in required:
            if field not in project:
                self.result.add_error(path, f"Missing required field: {field}")

        if "include_in" in project:
            self._validate_include_in_tags(project["include_in"], path)

    def _validate_education(self, education: List):
        """Validate education section"""
        if not education:
            return

        for idx, entry in enumerate(education):
            path = f"education[{idx}]"
            required = ["institution", "area", "studyType", "startDate", "endDate"]
            for field in required:
                if field not in entry:
                    self.result.add_error(path, f"Missing required field: {field}")

            # Validate dates
            if "startDate" in entry:
                self._validate_date(entry["startDate"], f"{path}.startDate")
            if "endDate" in entry:
                self._validate_date(entry["endDate"], f"{path}.endDate")

            # Validate include_in
            if "include_in" in entry:
                self._validate_include_in_tags(entry["include_in"], path)

    def _validate_awards(self, awards: List):
        """Validate awards section"""
        if not awards:
            return

        for idx, award in enumerate(awards):
            path = f"awards[{idx}]"
            required = ["title", "date", "awarder"]
            for field in required:
                if field not in award:
                    self.result.add_error(path, f"Missing required field: {field}")

            if "date" in award:
                self._validate_date(award["date"], f"{path}.date")

            if "include_in" in award:
                self._validate_include_in_tags(award["include_in"], path)

    def _validate_certifications(self, certifications: List):
        """Validate certifications section"""
        if not certifications:
            return

        for idx, cert in enumerate(certifications):
            path = f"certifications[{idx}]"
            required = ["title", "date", "url"]
            for field in required:
                if field not in cert:
                    self.result.add_error(path, f"Missing required field: {field}")

            if "acronym" in cert and cert["acronym"] is not None:
                if not isinstance(cert["acronym"], str):
                    self.result.add_error(f"{path}.acronym", "Acronym must be a string")

            if "date" in cert:
                self._validate_date(cert["date"], f"{path}.date")

            if "url" in cert and cert["url"]:
                if not URL_REGEX.match(cert["url"]):
                    self.result.add_error(f"{path}.url", f"Invalid URL: {cert['url']}")

            if "badge_url" in cert and cert["badge_url"]:
                if not URL_REGEX.match(cert["badge_url"]):
                    self.result.add_error(f"{path}.badge_url", f"Invalid badge URL: {cert['badge_url']}")

            if "include_in" in cert:
                self._validate_include_in_tags(cert["include_in"], path)

    def _validate_projects(self, projects: List):
        """Validate projects section"""
        if not projects:
            return

        for idx, project in enumerate(projects):
            path = f"projects[{idx}]"
            required = ["name", "description", "startDate", "roles", "type"]
            for field in required:
                if field not in project:
                    self.result.add_error(path, f"Missing required field: {field}")

            if "startDate" in project:
                self._validate_date(project["startDate"], f"{path}.startDate")

            if "endDate" in project:
                self._validate_date(project["endDate"], f"{path}.endDate")

            if "url" in project and project["url"]:
                if not URL_REGEX.match(project["url"]):
                    self.result.add_error(f"{path}.url", f"Invalid URL: {project['url']}")

            if "include_in" in project:
                self._validate_include_in_tags(project["include_in"], path)

            # Validate highlights
            if "highlights" in project and project["highlights"]:
                for hidx, highlight in enumerate(project["highlights"]):
                    if isinstance(highlight, dict):
                        if "description" not in highlight:
                            self.result.add_error(
                                f"{path}.highlights[{hidx}]",
                                "Highlight object must have 'description' field"
                            )
                        if "include_in" in highlight:
                            self._validate_include_in_tags(
                                highlight["include_in"],
                                f"{path}.highlights[{hidx}]"
                            )

    def _validate_volunteer(self, volunteer: List):
        """Validate volunteer section"""
        if not volunteer:
            return

        for idx, vol in enumerate(volunteer):
            path = f"volunteer[{idx}]"
            required = ["organization", "position", "startDate", "endDate"]
            for field in required:
                if field not in vol:
                    self.result.add_error(path, f"Missing required field: {field}")

            if "startDate" in vol:
                self._validate_date(vol["startDate"], f"{path}.startDate")

            if "endDate" in vol:
                self._validate_date(vol["endDate"], f"{path}.endDate")

            if "include_in" in vol:
                self._validate_include_in_tags(vol["include_in"], path)

    def _validate_specialty_skills(self, skills: List):
        """Validate specialty_skills section"""
        if not skills:
            return

        for idx, skill in enumerate(skills):
            path = f"specialty_skills[{idx}]"
            required = ["name", "keywords"]
            for field in required:
                if field not in skill:
                    self.result.add_error(path, f"Missing required field: {field}")

            if "include_in" in skill:
                self._validate_include_in_tags(skill["include_in"], path)

    def _validate_date(self, date_str: str, path: str):
        """Validate date format"""
        if not isinstance(date_str, str):
            self.result.add_error(
                path,
                f"Date must be a string, got {type(date_str).__name__}"
            )
            return

        if not DATE_REGEX.match(date_str):
            self.result.add_error(
                path,
                f"Invalid date format: {date_str}",
                "Use YYYY-MM-DD, YYYY-MM, YYYY, or 'Present'"
            )

    def _validate_include_in_tags(self, tags: Any, path: str):
        """Validate include_in tags"""
        if not isinstance(tags, list):
            self.result.add_error(
                f"{path}.include_in",
                f"include_in must be an array, got {type(tags).__name__}",
                "Use include_in: [all] or include_in: [leadership, technical]"
            )
            return

        if len(tags) == 0:
            self.result.add_error(
                f"{path}.include_in",
                "include_in array cannot be empty",
                "Use include_in: [all] for items that appear in all profiles"
            )
            return

        invalid_tags = [tag for tag in tags if tag not in ALLOWED_INCLUDE_IN_TAGS]
        if invalid_tags:
            self.result.add_error(
                f"{path}.include_in",
                f"Invalid tags: {', '.join(invalid_tags)}",
                f"Allowed tags: {', '.join(ALLOWED_INCLUDE_IN_TAGS)}"
            )

        # Warning if 'all' is mixed with other tags
        if "all" in tags and len(tags) > 1:
            self.result.add_warning(
                f"{path}.include_in",
                "Tag 'all' is present with other tags. The 'all' tag makes other tags redundant.",
                "Consider using just include_in: [all]"
            )


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_colored(text: str, color: str):
    """Print colored text (basic ANSI colors)"""
    colors = {
        "red": "\033[91m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def print_results(result: ValidationResult, verbose: bool = False):
    """Print validation results"""
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    # Print errors
    if result.errors:
        print_colored(f"\n✗ ERRORS ({len(result.errors)}):", "red")
        for error in result.errors:
            print_colored(f"  {error}", "red")

    # Print warnings
    if result.warnings:
        print_colored(f"\n⚠ WARNINGS ({len(result.warnings)}):", "yellow")
        for warning in result.warnings:
            print_colored(f"  {warning}", "yellow")

    # Print info (only in verbose mode)
    if verbose and result.info:
        print_colored(f"\nℹ INFO ({len(result.info)}):", "blue")
        for info in result.info:
            print_colored(f"  {info}", "blue")

    # Print summary
    print("\n" + "=" * 70)
    if not result.has_errors() and not result.has_warnings():
        print_colored("✓ VALIDATION PASSED - No issues found!", "green")
    elif not result.has_errors():
        print_colored("✓ VALIDATION PASSED - With warnings", "yellow")
    else:
        print_colored("✗ VALIDATION FAILED", "red")

    print(f"\nSummary: {result.get_summary()}")
    print("=" * 70 + "\n")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate resume YAML files against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s resume.yaml
  %(prog)s resume.yaml --verbose
  %(prog)s resume.yaml --strict

Exit codes:
  0 - Validation passed
  1 - Validation failed with errors
  2 - Validation passed with warnings (--strict treats warnings as errors)
        """
    )

    parser.add_argument(
        "file",
        help="Path to resume YAML file to validate"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed validation information"
    )

    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    # Validate file
    validator = ResumeValidator(verbose=args.verbose)
    result = validator.validate_file(args.file)

    # Print results
    print_results(result, verbose=args.verbose)

    # Determine exit code
    if result.has_errors():
        sys.exit(1)
    elif args.strict and result.has_warnings():
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
