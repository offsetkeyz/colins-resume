#!/usr/bin/env python3
"""
Tests for the JSON Generator module.

This module tests:
- YAML loading functionality
- Profile integration
- JSON generation for all profiles
- Output structure validation
- All data fields preserved
- API-ready dict output
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the resume_builder directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import json_generator as jg
import profile_manager as pm


class TestYAMLLoading(unittest.TestCase):
    """Test YAML loading functionality."""

    def test_read_yaml_file_success(self):
        """Test successful YAML file reading."""
        yaml_path = Path(__file__).parent / 'resume.yaml'
        data = jg.read_yaml_file(yaml_path)

        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertIn('basics', data)
        self.assertIn('work_experience', data)

    def test_read_yaml_file_not_found(self):
        """Test handling of non-existent file."""
        data = jg.read_yaml_file('/nonexistent/path/file.yaml')
        self.assertIsNone(data)

    def test_read_yaml_file_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [unclosed')
            temp_path = f.name

        try:
            data = jg.read_yaml_file(temp_path)
            self.assertIsNone(data)
        finally:
            os.unlink(temp_path)


class TestLoadResumeData(unittest.TestCase):
    """Test resume data loading with profile filtering."""

    def test_load_with_default_profile(self):
        """Test loading data with default profile."""
        data, profile_info = jg.load_resume_data(profile_name='default')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Full Resume')

    def test_load_with_technical_profile(self):
        """Test loading data with technical profile."""
        data, profile_info = jg.load_resume_data(profile_name='technical')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Technical Focused')

    def test_load_with_leadership_profile(self):
        """Test loading data with leadership profile."""
        data, profile_info = jg.load_resume_data(profile_name='leadership')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Leadership Focused')

    def test_load_with_invalid_profile(self):
        """Test handling of non-existent profile."""
        data, profile_info = jg.load_resume_data(profile_name='nonexistent')

        self.assertIsNone(data)
        self.assertIsNone(profile_info)


class TestCleanResumeData(unittest.TestCase):
    """Test resume data cleaning functionality."""

    def test_clean_removes_include_in_from_dict(self):
        """Test that include_in is removed from top-level dicts."""
        data = {
            'name': 'Test',
            'include_in': ['all'],
            'nested': {
                'value': 1,
                'include_in': ['technical']
            }
        }
        cleaned = jg.clean_resume_data(data)

        self.assertNotIn('include_in', cleaned)
        self.assertNotIn('include_in', cleaned['nested'])
        self.assertEqual(cleaned['name'], 'Test')
        self.assertEqual(cleaned['nested']['value'], 1)

    def test_clean_removes_include_in_from_lists(self):
        """Test that include_in is removed from items in lists."""
        data = {
            'items': [
                {'name': 'Item 1', 'include_in': ['all']},
                {'name': 'Item 2', 'include_in': ['technical']}
            ]
        }
        cleaned = jg.clean_resume_data(data)

        for item in cleaned['items']:
            self.assertNotIn('include_in', item)
            self.assertIn('name', item)

    def test_clean_handles_none(self):
        """Test that cleaning handles None input."""
        self.assertIsNone(jg.clean_resume_data(None))

    def test_clean_preserves_original_data(self):
        """Test that cleaning does not modify original data."""
        original = {'name': 'Test', 'include_in': ['all']}
        cleaned = jg.clean_resume_data(original)

        self.assertIn('include_in', original)  # Original unchanged
        self.assertNotIn('include_in', cleaned)  # Cleaned has no include_in


class TestAddMetadata(unittest.TestCase):
    """Test metadata addition functionality."""

    def test_add_metadata_includes_export_meta(self):
        """Test that export_meta is added to data."""
        data = {'name': 'Test'}
        with_meta = jg.add_metadata(data)

        self.assertIn('export_meta', with_meta)
        self.assertIn('exported_at', with_meta['export_meta'])
        self.assertIn('generator', with_meta['export_meta'])
        self.assertIn('format_version', with_meta['export_meta'])

    def test_add_metadata_includes_profile_info(self):
        """Test that profile info is included in metadata."""
        data = {'name': 'Test'}
        profile_info = {
            'name': 'Technical Focused',
            'slug': 'technical',
            'description': 'Technical profile'
        }
        with_meta = jg.add_metadata(data, profile_info)

        self.assertIn('profile', with_meta['export_meta'])
        self.assertEqual(with_meta['export_meta']['profile']['name'], 'Technical Focused')
        self.assertEqual(with_meta['export_meta']['profile']['slug'], 'technical')

    def test_add_metadata_handles_none(self):
        """Test that metadata handles None input."""
        self.assertIsNone(jg.add_metadata(None))

    def test_add_metadata_preserves_original(self):
        """Test that adding metadata does not modify original data."""
        original = {'name': 'Test'}
        with_meta = jg.add_metadata(original)

        self.assertNotIn('export_meta', original)
        self.assertIn('export_meta', with_meta)


class TestJSONGeneration(unittest.TestCase):
    """Test JSON generation functions."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.resume_data, cls.profile_info = jg.load_resume_data(profile_name='default')

    def test_generate_json_produces_valid_json(self):
        """Test that generated output is valid JSON."""
        json_str = jg.generate_json(self.resume_data, self.profile_info)

        self.assertIsNotNone(json_str)

        # Should be parseable as JSON
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, dict)

    def test_generate_json_includes_all_sections(self):
        """Test that generated JSON includes all resume sections."""
        json_str = jg.generate_json(self.resume_data, self.profile_info)
        parsed = json.loads(json_str)

        # Check required sections
        self.assertIn('basics', parsed)
        self.assertIn('work_experience', parsed)

        # Check optional sections if present in source data
        if self.resume_data.get('education'):
            self.assertIn('education', parsed)
        if self.resume_data.get('certifications'):
            self.assertIn('certifications', parsed)
        if self.resume_data.get('awards'):
            self.assertIn('awards', parsed)
        if self.resume_data.get('projects'):
            self.assertIn('projects', parsed)
        if self.resume_data.get('specialty_skills'):
            self.assertIn('specialty_skills', parsed)

    def test_generate_json_excludes_include_in(self):
        """Test that include_in fields are removed from output."""
        json_str = jg.generate_json(self.resume_data, self.profile_info)

        # include_in should not appear anywhere in the output
        self.assertNotIn('"include_in"', json_str)

    def test_generate_json_includes_metadata(self):
        """Test that export metadata is included."""
        json_str = jg.generate_json(self.resume_data, self.profile_info, include_metadata=True)
        parsed = json.loads(json_str)

        self.assertIn('export_meta', parsed)
        self.assertIn('exported_at', parsed['export_meta'])
        self.assertIn('profile', parsed['export_meta'])

    def test_generate_json_can_exclude_metadata(self):
        """Test that metadata can be excluded."""
        json_str = jg.generate_json(self.resume_data, self.profile_info, include_metadata=False)
        parsed = json.loads(json_str)

        self.assertNotIn('export_meta', parsed)

    def test_generate_json_with_none_data(self):
        """Test JSON generation with None data."""
        result = jg.generate_json(None)
        self.assertIsNone(result)

    def test_generate_json_compact(self):
        """Test compact JSON output (no indentation)."""
        json_str = jg.generate_json(self.resume_data, self.profile_info, indent=None)

        # Compact JSON should not have newlines (except in string values)
        lines = json_str.split('\n')
        # If compact, most of the content is on one line
        self.assertLess(len(lines), 10)

    def test_generate_json_formatted(self):
        """Test formatted JSON output (with indentation)."""
        json_str = jg.generate_json(self.resume_data, self.profile_info, indent=2)

        # Formatted JSON should have many newlines
        lines = json_str.split('\n')
        self.assertGreater(len(lines), 50)


class TestAllProfiles(unittest.TestCase):
    """Test JSON generation for all available profiles."""

    def test_all_profiles_generate_valid_json(self):
        """Test that all profiles generate valid JSON."""
        profiles = pm.list_available_profiles()

        self.assertGreater(len(profiles), 0, "No profiles found")

        for profile_name in profiles:
            with self.subTest(profile=profile_name):
                data, profile_info = jg.load_resume_data(profile_name=profile_name)

                self.assertIsNotNone(data, f"Failed to load data for profile: {profile_name}")
                self.assertIsNotNone(profile_info, f"Failed to load profile info for: {profile_name}")

                json_str = jg.generate_json(data, profile_info)

                self.assertIsNotNone(json_str, f"Failed to generate JSON for profile: {profile_name}")

                # Should be valid JSON
                parsed = json.loads(json_str)
                self.assertIsInstance(parsed, dict)
                self.assertIn('basics', parsed)

    def test_profile_output_paths(self):
        """Test that profiles generate correct output paths."""
        test_cases = [
            ('default', 'resume.json'),
            ('technical', 'resume-technical.json'),
            ('leadership', 'resume-leadership.json'),
        ]

        for profile_name, expected_filename in test_cases:
            with self.subTest(profile=profile_name):
                try:
                    profile = pm.load_profile(profile_name)
                    profile_info = pm.get_profile_info(profile)
                    output_path = jg.get_output_path(profile_info)

                    self.assertEqual(output_path.name, expected_filename)
                except pm.ProfileNotFoundError:
                    self.skipTest(f"Profile {profile_name} not found")


class TestJSONFileGeneration(unittest.TestCase):
    """Test actual JSON file generation."""

    def test_generate_for_profile_creates_file(self):
        """Test that generate_for_profile creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.json'

            success = jg.generate_for_profile(
                'default',
                output_path=str(output_path),
                verbose=False
            )

            self.assertTrue(success)
            self.assertTrue(output_path.exists())

            # Verify file content is valid JSON
            content = output_path.read_text()
            parsed = json.loads(content)
            self.assertIn('basics', parsed)
            self.assertIn('Colin', parsed['basics']['name'])

    def test_generate_for_invalid_profile_fails(self):
        """Test that invalid profile returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.json'

            success = jg.generate_for_profile(
                'nonexistent_profile',
                output_path=str(output_path),
                verbose=False
            )

            self.assertFalse(success)
            self.assertFalse(output_path.exists())

    def test_generate_with_output_dir(self):
        """Test generation with custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success = jg.generate_for_profile(
                'default',
                output_dir=tmpdir,
                verbose=False
            )

            self.assertTrue(success)

            # Check file was created in output dir
            output_file = Path(tmpdir) / 'resume.json'
            self.assertTrue(output_file.exists())


class TestDataFieldsPreserved(unittest.TestCase):
    """Test that all data fields are preserved in JSON output."""

    @classmethod
    def setUpClass(cls):
        """Load original and generated data."""
        cls.original_data, cls.profile_info = jg.load_resume_data(profile_name='default')
        json_str = jg.generate_json(cls.original_data, cls.profile_info, include_metadata=False)
        cls.parsed_data = json.loads(json_str)

    def test_basics_preserved(self):
        """Test that basics section fields are preserved."""
        original_basics = self.original_data.get('basics', {})
        parsed_basics = self.parsed_data.get('basics', {})

        for key in ['name', 'label', 'email', 'phone', 'url', 'summary']:
            if key in original_basics:
                self.assertIn(key, parsed_basics)
                self.assertEqual(original_basics[key], parsed_basics[key])

    def test_work_experience_preserved(self):
        """Test that work experience fields are preserved."""
        original_work = self.original_data.get('work_experience', {})
        parsed_work = self.parsed_data.get('work_experience', {})

        # Same companies should be present
        for company in original_work:
            self.assertIn(company, parsed_work)

            # Check positions
            for i, position in enumerate(original_work[company]):
                parsed_position = parsed_work[company][i]

                for key in ['job_title', 'location', 'start_date', 'end_date']:
                    if key in position:
                        self.assertIn(key, parsed_position)
                        self.assertEqual(position[key], parsed_position[key])

    def test_education_preserved(self):
        """Test that education fields are preserved."""
        original_edu = self.original_data.get('education', [])
        parsed_edu = self.parsed_data.get('education', [])

        self.assertEqual(len(original_edu), len(parsed_edu))

        for i, edu in enumerate(original_edu):
            for key in ['institution', 'area', 'studyType', 'startDate', 'endDate', 'score']:
                if key in edu:
                    self.assertIn(key, parsed_edu[i])
                    self.assertEqual(edu[key], parsed_edu[i][key])

    def test_certifications_preserved(self):
        """Test that certifications fields are preserved."""
        original_certs = self.original_data.get('certifications', [])
        parsed_certs = self.parsed_data.get('certifications', [])

        self.assertEqual(len(original_certs), len(parsed_certs))

        for i, cert in enumerate(original_certs):
            for key in ['title', 'date', 'url', 'issuer']:
                if key in cert:
                    self.assertIn(key, parsed_certs[i])
                    self.assertEqual(cert[key], parsed_certs[i][key])


class TestAPIIntegration(unittest.TestCase):
    """Test API-ready dictionary output."""

    def test_get_resume_as_dict_returns_dict(self):
        """Test that get_resume_as_dict returns a dictionary."""
        data = jg.get_resume_as_dict('default')

        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertIn('basics', data)

    def test_get_resume_as_dict_with_different_profiles(self):
        """Test get_resume_as_dict with different profiles."""
        profiles = pm.list_available_profiles()

        for profile_name in profiles:
            with self.subTest(profile=profile_name):
                data = jg.get_resume_as_dict(profile_name)

                self.assertIsNotNone(data)
                self.assertIn('basics', data)

    def test_get_resume_as_dict_cleans_internal_fields(self):
        """Test that internal fields are cleaned by default."""
        data = jg.get_resume_as_dict('default', clean_internal_fields=True)

        # Convert to JSON and back to check for include_in
        json_str = json.dumps(data)
        self.assertNotIn('"include_in"', json_str)

    def test_get_resume_as_dict_can_keep_internal_fields(self):
        """Test that internal fields can be preserved if needed."""
        data = jg.get_resume_as_dict('default', clean_internal_fields=False)

        # Should still have include_in fields in original data structure
        # This is useful for debugging or inspection
        self.assertIsNotNone(data)

    def test_get_resume_as_dict_with_invalid_profile(self):
        """Test that invalid profile returns None."""
        data = jg.get_resume_as_dict('nonexistent_profile')
        self.assertIsNone(data)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_resume_data(self):
        """Test handling of empty resume data."""
        json_str = jg.generate_json({})
        self.assertIsNotNone(json_str)

        parsed = json.loads(json_str)
        self.assertIn('export_meta', parsed)

    def test_unicode_handling(self):
        """Test proper handling of unicode characters."""
        data = {
            'basics': {
                'name': 'Test User',
                'summary': 'Testing unicode: cafe'
            }
        }
        json_str = jg.generate_json(data)

        self.assertIn('cafe', json_str)

        # Should be parseable
        parsed = json.loads(json_str)
        self.assertEqual(parsed['basics']['summary'], 'Testing unicode: cafe')

    def test_nested_data_structures(self):
        """Test handling of deeply nested data structures."""
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'value': 'deep',
                        'include_in': ['all']
                    }
                }
            }
        }
        json_str = jg.generate_json(data)
        parsed = json.loads(json_str)

        # Deep value should be preserved
        self.assertEqual(parsed['level1']['level2']['level3']['value'], 'deep')
        # include_in should be removed
        self.assertNotIn('include_in', parsed['level1']['level2']['level3'])


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
