#!/usr/bin/env python3
"""
Unit Tests for Profile Manager

These tests verify the profile manager functionality including:
1. Tag filtering logic
2. Max bullets limiting
3. Edge cases handling
4. Profile loading
5. Performance requirements
"""

import copy
import os
import tempfile
import time
from pathlib import Path
import pytest
import yaml

from profile_manager import (
    load_profile,
    filter_resume_data,
    filter_items,
    apply_bullet_limit,
    filter_work_experience,
    filter_projects,
    list_available_profiles,
    validate_profile,
    get_profile_info,
    ProfileNotFoundError,
    InvalidProfileError,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing."""
    return {
        "basics": {
            "name": "Test Person",
            "email": "test@example.com"
        },
        "work_experience": {
            "Company A": [
                {
                    "job_title": "Senior Developer",
                    "start_date": "2023-01-01",
                    "end_date": "Present",
                    "responsibilities": [
                        "Led technical initiatives",
                        "Wrote Python code",
                        "Managed team of 5",
                        "Improved performance by 50%",
                        "Conducted code reviews"
                    ],
                    "include_in": ["technical", "all"]
                },
                {
                    "job_title": "Developer",
                    "start_date": "2021-01-01",
                    "end_date": "2023-01-01",
                    "responsibilities": [
                        "Developed features",
                        "Fixed bugs"
                    ],
                    "include_in": ["technical"]
                }
            ],
            "Company B": [
                {
                    "job_title": "Team Lead",
                    "start_date": "2020-01-01",
                    "end_date": "2021-01-01",
                    "responsibilities": [
                        "Led cross-functional team",
                        "Mentored junior developers",
                        "Strategic planning"
                    ],
                    "include_in": ["leadership", "all"]
                }
            ]
        },
        "education": [
            {
                "institution": "Test University",
                "area": "Computer Science",
                "studyType": "Master's",
                "include_in": ["technical", "all"]
            },
            {
                "institution": "Leadership Academy",
                "area": "Management",
                "studyType": "Certificate",
                "include_in": ["leadership"]
            }
        ],
        "certifications": [
            {
                "title": "AWS Certified",
                "issuer": "AWS",
                "include_in": ["technical", "all"]
            },
            {
                "title": "PMP",
                "issuer": "PMI",
                "include_in": ["leadership"]
            }
        ],
        "projects": [
            {
                "name": "Technical Project",
                "description": "A coding project",
                "highlights": [
                    "Built with Python",
                    "Deployed on AWS",
                    "99.9% uptime",
                    "Handled 1M requests",
                    "Open source"
                ],
                "include_in": ["technical", "all"]
            },
            {
                "name": "Leadership Project",
                "description": "A management initiative",
                "highlights": [
                    "Managed team",
                    "Improved processes"
                ],
                "include_in": ["leadership"]
            }
        ],
        "specialty_skills": [
            {
                "name": "Programming",
                "keywords": ["Python", "JavaScript"],
                "include_in": ["technical"]
            },
            {
                "name": "Leadership",
                "keywords": ["Mentoring", "Strategy"],
                "include_in": ["leadership"]
            }
        ]
    }


@pytest.fixture
def technical_profile():
    """Sample technical profile."""
    return {
        "profile": {
            "name": "Technical Focused",
            "description": "Emphasizes technical skills",
            "slug": "technical"
        },
        "filters": {
            "include_tags": ["technical", "all"],
            "max_bullets_per_job": 3
        },
        "output": {
            "title_suffix": " - Technical",
            "filename": "resume-technical"
        }
    }


@pytest.fixture
def leadership_profile():
    """Sample leadership profile."""
    return {
        "profile": {
            "name": "Leadership Focused",
            "description": "Emphasizes leadership skills",
            "slug": "leadership"
        },
        "filters": {
            "include_tags": ["leadership", "all"],
            "max_bullets_per_job": 4
        },
        "output": {
            "title_suffix": " - Leadership",
            "filename": "resume-leadership"
        }
    }


@pytest.fixture
def default_profile():
    """Sample default profile with 'all' tag."""
    return {
        "profile": {
            "name": "Full Resume",
            "description": "Complete resume",
            "slug": "default"
        },
        "filters": {
            "include_tags": ["all"]
        },
        "output": {
            "title_suffix": "",
            "filename": "resume"
        }
    }


@pytest.fixture
def temp_profiles_dir():
    """Create a temporary profiles directory with test profiles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        profiles_dir = Path(tmpdir)

        # Create default profile
        default = {
            "profile": {
                "name": "Default",
                "description": "Full resume",
                "slug": "default"
            },
            "filters": {
                "include_tags": ["all"]
            }
        }
        with open(profiles_dir / "default.yaml", 'w') as f:
            yaml.dump(default, f)

        # Create technical profile
        technical = {
            "profile": {
                "name": "Technical",
                "description": "Technical focus",
                "slug": "technical"
            },
            "filters": {
                "include_tags": ["technical", "development", "all"],
                "max_bullets_per_job": 4
            }
        }
        with open(profiles_dir / "technical.yaml", 'w') as f:
            yaml.dump(technical, f)

        # Create empty profile (valid YAML but empty content)
        with open(profiles_dir / "empty.yaml", 'w') as f:
            f.write("")

        # Create invalid YAML profile
        with open(profiles_dir / "invalid.yaml", 'w') as f:
            f.write("invalid: yaml: content: [")

        yield profiles_dir


# ============================================================================
# Test Suite 1: Tag Filtering
# ============================================================================

class TestTagFiltering:
    """Test suite for tag-based filtering logic."""

    def test_include_in_filtering(self, sample_resume_data, technical_profile):
        """Test that items are filtered based on include_in tags."""
        result = filter_resume_data(sample_resume_data, technical_profile)

        # Technical profile should include items with 'technical' or 'all' tags
        assert "Company A" in result["work_experience"]
        assert "Company B" in result["work_experience"]  # Has 'all' tag

        # Check education filtering
        assert len(result["education"]) == 1
        assert result["education"][0]["institution"] == "Test University"

        # Check certifications filtering
        assert len(result["certifications"]) == 1
        assert result["certifications"][0]["title"] == "AWS Certified"

    def test_missing_include_in_tag(self):
        """Test handling of items without include_in tags."""
        items = [
            {"name": "Item 1", "include_in": ["all"]},
            {"name": "Item 2"},  # No include_in tag
            {"name": "Item 3", "include_in": ["technical"]}
        ]

        # With 'all' tag, items without include_in should be included
        result = filter_items(items, ["all"])
        names = [item["name"] for item in result]
        assert "Item 1" in names
        assert "Item 2" in names  # Included because 'all' allows untagged items
        assert "Item 3" not in names  # Only has 'technical' tag

        # Without 'all' tag, items without include_in should be excluded
        result = filter_items(items, ["technical"])
        names = [item["name"] for item in result]
        assert "Item 1" not in names
        assert "Item 2" not in names
        assert "Item 3" in names

    def test_all_tag_includes_everywhere(self, sample_resume_data, default_profile):
        """Test that 'all' tag includes items everywhere."""
        result = filter_resume_data(sample_resume_data, default_profile)

        # With 'all' tag, should include items that have 'all' in their include_in
        # or items without specific tags
        work_exp = result["work_experience"]
        assert "Company A" in work_exp
        assert "Company B" in work_exp

        # Check that both positions at Company A are included
        # (one has ['technical', 'all'], one has only ['technical'])
        # Only the one with 'all' should be included when filtering by 'all'
        company_a_positions = work_exp["Company A"]
        assert len(company_a_positions) == 1
        assert company_a_positions[0]["job_title"] == "Senior Developer"

    def test_multiple_tags_on_item(self):
        """Test items with multiple tags in include_in."""
        items = [
            {"name": "Item 1", "include_in": ["technical", "leadership", "all"]},
            {"name": "Item 2", "include_in": ["leadership"]},
            {"name": "Item 3", "include_in": ["technical"]}
        ]

        # Filter by technical
        result = filter_items(items, ["technical"])
        names = [item["name"] for item in result]
        assert "Item 1" in names
        assert "Item 2" not in names
        assert "Item 3" in names

        # Filter by leadership
        result = filter_items(items, ["leadership"])
        names = [item["name"] for item in result]
        assert "Item 1" in names
        assert "Item 2" in names
        assert "Item 3" not in names

        # Filter by multiple tags
        result = filter_items(items, ["technical", "leadership"])
        names = [item["name"] for item in result]
        assert len(result) == 3  # All items match

    def test_filter_items_empty_input(self):
        """Test filter_items with empty input."""
        assert filter_items([], ["all"]) == []
        assert filter_items(None, ["all"]) == []
        assert filter_items([{"name": "test"}], []) == []
        assert filter_items([{"name": "test"}], None) == []

    def test_filter_items_preserves_order(self):
        """Test that filter_items preserves the original order."""
        items = [
            {"name": "C", "include_in": ["all"]},
            {"name": "A", "include_in": ["all"]},
            {"name": "B", "include_in": ["all"]}
        ]

        result = filter_items(items, ["all"])
        names = [item["name"] for item in result]
        assert names == ["C", "A", "B"]

    def test_filter_items_deep_copies(self):
        """Test that filter_items returns deep copies."""
        items = [{"name": "Test", "data": {"nested": "value"}, "include_in": ["all"]}]

        result = filter_items(items, ["all"])

        # Modify the result
        result[0]["name"] = "Modified"
        result[0]["data"]["nested"] = "changed"

        # Original should be unchanged
        assert items[0]["name"] == "Test"
        assert items[0]["data"]["nested"] == "value"


# ============================================================================
# Test Suite 2: Max Bullets Limiting
# ============================================================================

class TestMaxBulletsLimiting:
    """Test suite for max bullets per job limiting."""

    def test_max_bullets_per_job(self, sample_resume_data, technical_profile):
        """Test that max_bullets_per_job limits responsibilities."""
        result = filter_resume_data(sample_resume_data, technical_profile)

        # Technical profile has max_bullets_per_job: 3
        company_a = result["work_experience"]["Company A"]
        senior_position = company_a[0]

        # Original had 5 responsibilities, should be limited to 3
        assert len(senior_position["responsibilities"]) == 3
        assert senior_position["responsibilities"][0] == "Led technical initiatives"
        assert senior_position["responsibilities"][1] == "Wrote Python code"
        assert senior_position["responsibilities"][2] == "Managed team of 5"

    def test_max_bullets_with_filtering(self, sample_resume_data, technical_profile):
        """Test that bullet limiting works together with tag filtering."""
        result = filter_resume_data(sample_resume_data, technical_profile)

        # Projects should also be limited
        tech_project = result["projects"][0]
        assert len(tech_project["highlights"]) == 3  # Limited from 5

    def test_no_bullet_limit(self, sample_resume_data, default_profile):
        """Test that no limit is applied when max_bullets_per_job is not set."""
        result = filter_resume_data(sample_resume_data, default_profile)

        # Default profile has no max_bullets_per_job
        company_a = result["work_experience"]["Company A"]
        senior_position = company_a[0]

        # All 5 responsibilities should be present
        assert len(senior_position["responsibilities"]) == 5

    def test_apply_bullet_limit_edge_cases(self):
        """Test apply_bullet_limit with edge cases."""
        bullets = ["One", "Two", "Three", "Four"]

        # No limit
        assert apply_bullet_limit(bullets, None) == bullets
        assert apply_bullet_limit(bullets, 0) == bullets
        assert apply_bullet_limit(bullets, -1) == bullets

        # Limit larger than list
        assert len(apply_bullet_limit(bullets, 10)) == 4

        # Limit of 1
        assert apply_bullet_limit(bullets, 1) == ["One"]

        # Empty list
        assert apply_bullet_limit([], 5) == []

    def test_apply_bullet_limit_deep_copies(self):
        """Test that apply_bullet_limit returns deep copies."""
        bullets = [{"text": "Original"}]
        result = apply_bullet_limit(bullets, 10)

        result[0]["text"] = "Modified"
        assert bullets[0]["text"] == "Original"

    def test_max_bullets_on_projects(self):
        """Test that max bullets applies to project highlights."""
        projects = [
            {
                "name": "Project",
                "highlights": ["H1", "H2", "H3", "H4", "H5"],
                "include_in": ["all"]
            }
        ]

        result = filter_projects(projects, ["all"], max_bullets=2)

        assert len(result[0]["highlights"]) == 2
        assert result[0]["highlights"] == ["H1", "H2"]


# ============================================================================
# Test Suite 3: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases handling."""

    def test_profile_not_found(self, temp_profiles_dir):
        """Test ProfileNotFoundError when profile doesn't exist."""
        with pytest.raises(ProfileNotFoundError) as exc_info:
            load_profile("nonexistent", temp_profiles_dir)

        assert "nonexistent" in str(exc_info.value)

    def test_empty_profile(self, temp_profiles_dir):
        """Test InvalidProfileError for empty profile files."""
        with pytest.raises(InvalidProfileError) as exc_info:
            load_profile("empty", temp_profiles_dir)

        assert "empty" in str(exc_info.value).lower()

    def test_nested_filtering(self, sample_resume_data, technical_profile):
        """Test filtering of nested structures (work experience by company)."""
        result = filter_resume_data(sample_resume_data, technical_profile)

        # Company A should have 2 positions (both have 'technical' or 'all')
        assert len(result["work_experience"]["Company A"]) == 2

        # Company B should have 1 position (has 'all' tag)
        assert len(result["work_experience"]["Company B"]) == 1

    def test_malformed_tags(self):
        """Test handling of malformed include_in tags."""
        items = [
            {"name": "Item 1", "include_in": "single_string"},  # Should be list
            {"name": "Item 2", "include_in": None},  # None value
            {"name": "Item 3", "include_in": ["all"]},  # Correct format
            {"name": "Item 4", "include_in": 123},  # Invalid type
        ]

        result = filter_items(items, ["all", "single_string"])

        names = [item["name"] for item in result]
        assert "Item 1" in names  # single_string matches
        assert "Item 2" in names  # None with 'all' in tags
        assert "Item 3" in names  # Normal case
        # Item 4 with integer 123 should be converted to ["123"] but won't match

    def test_empty_resume_data(self, technical_profile):
        """Test filtering with empty resume data."""
        result = filter_resume_data({}, technical_profile)
        assert result == {}

        result = filter_resume_data(None, technical_profile)
        assert result == {}

    def test_empty_filters_in_profile(self, sample_resume_data):
        """Test profile with missing filters section."""
        profile = {
            "profile": {"name": "No Filters"}
        }

        result = filter_resume_data(sample_resume_data, profile)

        # Should default to ['all'] tags and no bullet limit
        assert "work_experience" in result

    def test_none_profile(self, sample_resume_data):
        """Test filtering with None profile."""
        result = filter_resume_data(sample_resume_data, None)

        # Should return copy of original data
        assert "work_experience" in result
        assert result is not sample_resume_data

    def test_invalid_yaml_profile(self, temp_profiles_dir):
        """Test InvalidProfileError for invalid YAML syntax."""
        with pytest.raises(InvalidProfileError) as exc_info:
            load_profile("invalid", temp_profiles_dir)

        assert "parse" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_work_experience_not_dict(self):
        """Test handling when work_experience is not a dict."""
        resume = {
            "work_experience": ["invalid", "format"]
        }

        result = filter_work_experience(resume.get("work_experience"), ["all"])
        assert result == {}

    def test_positions_not_list(self):
        """Test handling when company positions is not a list."""
        work = {
            "Company": "invalid format"
        }

        result = filter_work_experience(work, ["all"])
        assert result == {}

    def test_non_dict_items_in_list(self):
        """Test handling non-dict items in lists."""
        items = [
            "string item",
            123,
            {"name": "valid", "include_in": ["all"]},
            None
        ]

        result = filter_items(items, ["all"])

        # Only the dict should be included; strings with 'all' tag are included
        assert any(isinstance(item, dict) and item.get("name") == "valid" for item in result)

    def test_filter_preserves_unfiltered_sections(self, sample_resume_data, technical_profile):
        """Test that sections without include_in logic are preserved."""
        sample_resume_data["interests"] = [{"name": "Coding"}]
        sample_resume_data["languages"] = [{"language": "English"}]
        sample_resume_data["meta"] = {"version": "1.0"}

        result = filter_resume_data(sample_resume_data, technical_profile)

        assert result["interests"] == [{"name": "Coding"}]
        assert result["languages"] == [{"language": "English"}]
        assert result["meta"] == {"version": "1.0"}


# ============================================================================
# Test Profile Loading
# ============================================================================

class TestProfileLoading:
    """Test suite for profile loading functionality."""

    def test_load_profile_success(self, temp_profiles_dir):
        """Test successful profile loading."""
        profile = load_profile("default", temp_profiles_dir)

        assert profile["profile"]["name"] == "Default"
        assert profile["filters"]["include_tags"] == ["all"]

    def test_load_profile_with_max_bullets(self, temp_profiles_dir):
        """Test loading profile with max_bullets_per_job."""
        profile = load_profile("technical", temp_profiles_dir)

        assert profile["filters"]["max_bullets_per_job"] == 4
        assert "technical" in profile["filters"]["include_tags"]

    def test_list_available_profiles(self, temp_profiles_dir):
        """Test listing available profiles."""
        profiles = list_available_profiles(temp_profiles_dir)

        # Should include valid YAML files
        assert "default" in profiles
        assert "technical" in profiles

    def test_list_profiles_empty_directory(self):
        """Test listing profiles in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiles = list_available_profiles(Path(tmpdir))
            assert profiles == []

    def test_list_profiles_nonexistent_directory(self):
        """Test listing profiles when directory doesn't exist."""
        profiles = list_available_profiles(Path("/nonexistent/path"))
        assert profiles == []

    def test_load_real_profiles(self):
        """Test loading actual profiles from the project."""
        profiles_dir = Path(__file__).parent / "profiles"

        if not profiles_dir.exists():
            pytest.skip("Profiles directory not found")

        # Try loading each actual profile
        for profile_file in profiles_dir.glob("*.yaml"):
            profile_name = profile_file.stem
            profile = load_profile(profile_name, profiles_dir)

            assert profile is not None
            assert "filters" in profile


# ============================================================================
# Test Profile Validation
# ============================================================================

class TestProfileValidation:
    """Test suite for profile validation."""

    def test_validate_valid_profile(self, technical_profile):
        """Test validation of a valid profile."""
        is_valid, errors = validate_profile(technical_profile)
        assert is_valid is True
        assert errors == []

    def test_validate_empty_profile(self):
        """Test validation of empty profile."""
        is_valid, errors = validate_profile({})
        assert is_valid is False
        assert any("empty" in e.lower() for e in errors)

    def test_validate_none_profile(self):
        """Test validation of None profile."""
        is_valid, errors = validate_profile(None)
        assert is_valid is False

    def test_validate_missing_profile_section(self):
        """Test validation with missing profile section."""
        profile = {
            "filters": {"include_tags": ["all"]}
        }
        is_valid, errors = validate_profile(profile)
        assert is_valid is False
        assert any("profile" in e.lower() for e in errors)

    def test_validate_invalid_include_tags_type(self):
        """Test validation with invalid include_tags type."""
        profile = {
            "profile": {"name": "Test"},
            "filters": {"include_tags": "not_a_list"}
        }
        is_valid, errors = validate_profile(profile)
        assert is_valid is False
        assert any("include_tags" in e for e in errors)

    def test_validate_invalid_max_bullets_type(self):
        """Test validation with invalid max_bullets_per_job type."""
        profile = {
            "profile": {"name": "Test"},
            "filters": {"max_bullets_per_job": "five"}
        }
        is_valid, errors = validate_profile(profile)
        assert is_valid is False
        assert any("max_bullets" in e for e in errors)


# ============================================================================
# Test Profile Info Extraction
# ============================================================================

class TestProfileInfo:
    """Test suite for profile info extraction."""

    def test_get_profile_info(self, technical_profile):
        """Test extracting profile summary info."""
        info = get_profile_info(technical_profile)

        assert info["name"] == "Technical Focused"
        assert info["description"] == "Emphasizes technical skills"
        assert info["slug"] == "technical"
        assert info["include_tags"] == ["technical", "all"]
        assert info["max_bullets_per_job"] == 3
        assert info["filename"] == "resume-technical"
        assert info["title_suffix"] == " - Technical"

    def test_get_profile_info_defaults(self):
        """Test profile info with missing sections."""
        profile = {}
        info = get_profile_info(profile)

        assert info["name"] == "Unknown"
        assert info["description"] == ""
        assert info["include_tags"] == ["all"]
        assert info["max_bullets_per_job"] is None


# ============================================================================
# Test Integration with Real Data
# ============================================================================

class TestIntegrationWithRealData:
    """Integration tests using actual project data."""

    def test_filter_with_real_resume_data(self):
        """Test filtering with actual resume.yaml data."""
        resume_path = Path(__file__).parent / "resume.yaml"

        if not resume_path.exists():
            pytest.skip("resume.yaml not found")

        with open(resume_path, 'r') as f:
            resume_data = yaml.safe_load(f)

        # Create a test profile
        profile = {
            "profile": {"name": "Test"},
            "filters": {
                "include_tags": ["all"],
                "max_bullets_per_job": 3
            }
        }

        result = filter_resume_data(resume_data, profile)

        # Verify structure is preserved
        assert "basics" in result
        assert "work_experience" in result or "work" in result

    def test_all_profiles_filter_correctly(self):
        """Test that all actual profiles produce valid output."""
        profiles_dir = Path(__file__).parent / "profiles"
        resume_path = Path(__file__).parent / "resume.yaml"

        if not profiles_dir.exists() or not resume_path.exists():
            pytest.skip("Profiles or resume not found")

        with open(resume_path, 'r') as f:
            resume_data = yaml.safe_load(f)

        for profile_file in profiles_dir.glob("*.yaml"):
            profile_name = profile_file.stem
            try:
                profile = load_profile(profile_name, profiles_dir)
                result = filter_resume_data(resume_data, profile)

                # Verify result has expected structure
                assert isinstance(result, dict)
                assert "basics" in result  # basics should always be present

            except (ProfileNotFoundError, InvalidProfileError) as e:
                pytest.fail(f"Failed to process profile {profile_name}: {e}")


# ============================================================================
# Test Performance
# ============================================================================

class TestPerformance:
    """Test suite for performance requirements."""

    def test_filter_1000_items_performance(self):
        """Test that filtering 1000 items completes in <100ms."""
        # Generate 1000 items
        items = []
        for i in range(1000):
            items.append({
                "name": f"Item {i}",
                "description": f"Description for item {i}",
                "include_in": ["all"] if i % 2 == 0 else ["technical"],
                "data": {"key": f"value_{i}", "nested": {"a": 1, "b": 2}}
            })

        include_tags = ["all", "technical"]

        # Time the filtering
        start_time = time.time()
        result = filter_items(items, include_tags)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert len(result) == 1000  # All items should match
        assert elapsed_time < 100, f"Filtering took {elapsed_time:.2f}ms, expected <100ms"

    def test_filter_resume_performance(self):
        """Test that filtering a large resume completes quickly."""
        # Generate a large resume
        resume = {
            "basics": {"name": "Test"},
            "work_experience": {},
            "education": [],
            "certifications": [],
            "projects": [],
            "specialty_skills": []
        }

        # Add 100 companies with 10 positions each
        for i in range(100):
            positions = []
            for j in range(10):
                positions.append({
                    "job_title": f"Position {j}",
                    "responsibilities": [f"Responsibility {k}" for k in range(10)],
                    "include_in": ["all"]
                })
            resume["work_experience"][f"Company {i}"] = positions

        # Add 200 education entries
        for i in range(200):
            resume["education"].append({
                "institution": f"University {i}",
                "include_in": ["all"]
            })

        profile = {
            "profile": {"name": "Test"},
            "filters": {
                "include_tags": ["all"],
                "max_bullets_per_job": 5
            }
        }

        # Time the filtering
        start_time = time.time()
        result = filter_resume_data(resume, profile)
        elapsed_time = (time.time() - start_time) * 1000

        # Verify correctness
        assert len(result["work_experience"]) == 100
        assert len(result["education"]) == 200

        # Verify bullet limiting
        first_company = list(result["work_experience"].values())[0]
        assert len(first_company[0]["responsibilities"]) == 5

        # Performance assertion (generous limit for CI environments)
        assert elapsed_time < 1000, f"Filtering took {elapsed_time:.2f}ms, expected <1000ms"

        # Print actual time for informational purposes
        print(f"\nFiltering large resume took {elapsed_time:.2f}ms")


# ============================================================================
# Test JSON Resume Format Compatibility
# ============================================================================

class TestJSONResumeFormat:
    """Test suite for JSON Resume format compatibility."""

    def test_filter_json_resume_work(self):
        """Test filtering JSON Resume 'work' array format."""
        resume = {
            "work": [
                {
                    "name": "Company A",
                    "position": "Developer",
                    "highlights": ["H1", "H2", "H3", "H4"],
                    "include_in": ["all"]
                },
                {
                    "name": "Company B",
                    "position": "Lead",
                    "highlights": ["L1", "L2"],
                    "include_in": ["leadership"]
                }
            ]
        }

        profile = {
            "profile": {"name": "Test"},
            "filters": {
                "include_tags": ["all"],
                "max_bullets_per_job": 2
            }
        }

        result = filter_resume_data(resume, profile)

        assert len(result["work"]) == 1
        assert result["work"][0]["name"] == "Company A"
        assert len(result["work"][0]["highlights"]) == 2

    def test_filter_json_resume_certificates(self):
        """Test filtering JSON Resume 'certificates' format."""
        resume = {
            "certificates": [
                {"name": "Cert A", "include_in": ["technical"]},
                {"name": "Cert B", "include_in": ["all"]}
            ]
        }

        profile = {
            "profile": {"name": "Test"},
            "filters": {"include_tags": ["all"]}
        }

        result = filter_resume_data(resume, profile)

        assert len(result["certificates"]) == 1
        assert result["certificates"][0]["name"] == "Cert B"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
