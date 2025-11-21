#!/usr/bin/env python3
"""
Tests for the JSON Resume to YAML migration script.

These tests verify:
1. Date field consistency (all should use snake_case: start_date, end_date)
2. Data integrity (no data loss during migration)
3. Field name transformations are correct
4. include_in tags are added properly
"""

import json
import pytest
from pathlib import Path
from migrate_json_to_yaml import ResumeMigrator, MigrationStats, DEFAULT_INCLUDE_IN
import logging

# Setup test logger
logging.basicConfig(level=logging.WARNING)
test_logger = logging.getLogger(__name__)


class TestDateFieldConsistency:
    """Tests for consistent date field naming (snake_case)"""

    def test_work_experience_uses_snake_case_dates(self):
        """Work experience should use start_date and end_date"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {
                "name": "Test Company",
                "position": "Developer",
                "startDate": "2023-01-01",
                "endDate": "2024-01-01",
                "highlights": ["Did stuff"]
            }
        ]

        result = migrator._migrate_work_from_json_resume(work_data)

        assert "Test Company" in result
        position = result["Test Company"][0]
        assert "start_date" in position, "Should use snake_case start_date"
        assert "end_date" in position, "Should use snake_case end_date"
        assert "startDate" not in position, "Should NOT have camelCase startDate"
        assert "endDate" not in position, "Should NOT have camelCase endDate"
        assert position["start_date"] == "2023-01-01"
        assert position["end_date"] == "2024-01-01"

    def test_work_experience_missing_end_date_defaults_to_present(self):
        """Work entries without endDate should default to 'Present'"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {
                "name": "Current Company",
                "position": "Lead",
                "startDate": "2024-01-01",
                "highlights": []
            }
        ]

        result = migrator._migrate_work_from_json_resume(work_data)
        position = result["Current Company"][0]

        assert position["end_date"] == "Present"

    def test_education_preserves_camelcase_dates(self):
        """Education should keep camelCase dates (per schema)"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        education_data = [
            {
                "institution": "Test University",
                "area": "Computer Science",
                "studyType": "Bachelor's",
                "startDate": "2020-01-01",
                "endDate": "2024-01-01",
                "score": "3.8"
            }
        ]

        result = migrator._migrate_education(education_data)

        assert len(result) == 1
        entry = result[0]
        # Schema expects camelCase for education dates
        assert "startDate" in entry, "Should keep camelCase startDate"
        assert "endDate" in entry, "Should keep camelCase endDate"
        assert entry["startDate"] == "2020-01-01"
        assert entry["endDate"] == "2024-01-01"

    def test_education_missing_end_date_defaults_to_present(self):
        """Education entries without endDate should default to 'Present'"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        education_data = [
            {
                "institution": "Ongoing University",
                "area": "Cyber Security",
                "studyType": "Master's",
                "startDate": "2023-07-01"
            }
        ]

        result = migrator._migrate_education(education_data)
        entry = result[0]

        # Schema expects camelCase endDate
        assert entry["endDate"] == "Present"

    def test_projects_preserves_camelcase_dates(self):
        """Projects should keep camelCase dates (per schema)"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        projects_data = [
            {
                "name": "Test Project",
                "description": "A test",
                "startDate": "2023-01-01",
                "endDate": "2023-12-01",
                "roles": ["Developer"],
                "type": "application"
            }
        ]

        result = migrator._migrate_projects(projects_data)

        assert len(result) == 1
        project = result[0]
        # Schema expects camelCase for project dates
        assert "startDate" in project, "Should keep camelCase startDate"
        assert "endDate" in project, "Should keep camelCase endDate"
        assert project["startDate"] == "2023-01-01"
        assert project["endDate"] == "2023-12-01"


class TestDataIntegrity:
    """Tests for data integrity during migration"""

    def test_work_highlights_become_responsibilities(self):
        """Work highlights should be mapped to responsibilities"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {
                "name": "Company",
                "position": "Role",
                "startDate": "2023-01-01",
                "highlights": ["Achievement 1", "Achievement 2"]
            }
        ]

        result = migrator._migrate_work_from_json_resume(work_data)
        position = result["Company"][0]

        assert "responsibilities" in position
        # Summary gets prepended, so highlights may not be first
        assert "Achievement 1" in position["responsibilities"]
        assert "Achievement 2" in position["responsibilities"]

    def test_work_summary_prepended_to_responsibilities(self):
        """Work summary should be prepended to responsibilities"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {
                "name": "Company",
                "position": "Role",
                "startDate": "2023-01-01",
                "summary": "Role summary here",
                "highlights": ["Achievement 1"]
            }
        ]

        result = migrator._migrate_work_from_json_resume(work_data)
        position = result["Company"][0]

        assert position["responsibilities"][0] == "Role summary here"
        assert position["responsibilities"][1] == "Achievement 1"

    def test_certificates_mapped_to_certifications(self):
        """JSON Resume 'certificates' should become 'certifications'"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        certs_data = [
            {
                "name": "Test Certification",
                "date": "2023-06-01",
                "url": "https://example.com/cert",
                "issuer": "Test Org"
            }
        ]

        result = migrator._migrate_certifications_from_json_resume(certs_data)

        assert len(result) == 1
        cert = result[0]
        assert cert["title"] == "Test Certification"  # name -> title
        assert cert["date"] == "2023-06-01"
        assert cert["url"] == "https://example.com/cert"
        assert cert["issuer"] == "Test Org"

    def test_skills_mapped_to_specialty_skills(self):
        """JSON Resume 'skills' should become 'specialty_skills'"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        skills_data = [
            {
                "name": "Development",
                "keywords": ["Python", "JavaScript"]
            }
        ]

        result = migrator._migrate_skills_from_json_resume(skills_data)

        assert len(result) == 1
        skill = result[0]
        assert skill["name"] == "Development"
        assert skill["keywords"] == ["Python", "JavaScript"]

    def test_position_mapped_to_job_title(self):
        """JSON Resume 'position' should become 'job_title'"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {
                "name": "Company",
                "position": "Senior Developer",
                "startDate": "2023-01-01"
            }
        ]

        result = migrator._migrate_work_from_json_resume(work_data)
        position = result["Company"][0]

        assert position["job_title"] == "Senior Developer"
        assert "position" not in position


class TestIncludeInTags:
    """Tests for include_in tag addition"""

    def test_work_positions_have_include_in(self):
        """All work positions should have include_in tag"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {"name": "Company", "position": "Role", "startDate": "2023-01-01"}
        ]

        result = migrator._migrate_work_from_json_resume(work_data)
        position = result["Company"][0]

        assert "include_in" in position
        assert position["include_in"] == DEFAULT_INCLUDE_IN

    def test_education_has_include_in(self):
        """All education entries should have include_in tag"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        education_data = [
            {
                "institution": "University",
                "area": "CS",
                "studyType": "BS",
                "startDate": "2020-01-01",
                "endDate": "2024-01-01"
            }
        ]

        result = migrator._migrate_education(education_data)

        assert "include_in" in result[0]
        assert result[0]["include_in"] == DEFAULT_INCLUDE_IN

    def test_certifications_have_include_in(self):
        """All certifications should have include_in tag"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        certs_data = [
            {"name": "Cert", "date": "2023-01-01", "url": "https://example.com"}
        ]

        result = migrator._migrate_certifications_from_json_resume(certs_data)

        assert "include_in" in result[0]
        assert result[0]["include_in"] == DEFAULT_INCLUDE_IN

    def test_projects_have_include_in(self):
        """All projects should have include_in tag"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        projects_data = [
            {
                "name": "Project",
                "description": "Desc",
                "startDate": "2023-01-01",
                "roles": ["Dev"],
                "type": "app"
            }
        ]

        result = migrator._migrate_projects(projects_data)

        assert "include_in" in result[0]
        assert result[0]["include_in"] == DEFAULT_INCLUDE_IN


class TestWorkExperienceGrouping:
    """Tests for work experience grouping by company"""

    def test_multiple_positions_same_company_grouped(self):
        """Multiple positions at same company should be grouped together"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {"name": "Company A", "position": "Senior", "startDate": "2023-01-01"},
            {"name": "Company A", "position": "Junior", "startDate": "2022-01-01", "endDate": "2023-01-01"},
            {"name": "Company B", "position": "Lead", "startDate": "2021-01-01"}
        ]

        result = migrator._migrate_work_from_json_resume(work_data)

        assert len(result) == 2  # Two companies
        assert len(result["Company A"]) == 2  # Two positions
        assert len(result["Company B"]) == 1  # One position

    def test_work_experience_preserves_order(self):
        """Positions should be in the order they appear in the JSON"""
        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)

        work_data = [
            {"name": "Company", "position": "First", "startDate": "2024-01-01"},
            {"name": "Company", "position": "Second", "startDate": "2023-01-01"},
        ]

        result = migrator._migrate_work_from_json_resume(work_data)

        assert result["Company"][0]["job_title"] == "First"
        assert result["Company"][1]["job_title"] == "Second"


class TestFullMigration:
    """Integration tests for full migration"""

    def test_full_migration_with_real_data(self):
        """Test migration with actual json_resume.json file"""
        json_file = Path(__file__).parent / "json_resume.json"

        if not json_file.exists():
            pytest.skip("json_resume.json not found")

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        stats = MigrationStats()
        migrator = ResumeMigrator(test_logger, stats)
        result = migrator.migrate(json_data)

        # Verify structure
        assert "basics" in result
        assert "work_experience" in result
        assert "education" in result

        # Verify work_experience uses snake_case dates (per schema)
        for company, positions in result["work_experience"].items():
            for pos in positions:
                assert "start_date" in pos, f"Missing start_date in {company}"
                assert "end_date" in pos, f"Missing end_date in {company}"

        # Verify education uses camelCase dates (per schema)
        for edu in result["education"]:
            assert "startDate" in edu, f"Missing startDate in education"
            assert "endDate" in edu, f"Missing endDate in education"

        # Verify projects use camelCase dates (per schema)
        for proj in result.get("projects", []):
            assert "startDate" in proj, f"Missing startDate in project"

        # Verify Team Lead label is correct
        assert result["basics"]["label"] == "Team Lead"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
