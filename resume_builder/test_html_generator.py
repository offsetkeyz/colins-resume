#!/usr/bin/env python3
"""
Tests for the HTML Generator module.

This module tests:
- YAML loading functionality
- Profile integration
- HTML generation for all profiles
- Output quality validation
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the resume_builder directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import html_generator as hg
import profile_manager as pm


class TestYAMLLoading(unittest.TestCase):
    """Test YAML loading functionality."""

    def test_read_yaml_file_success(self):
        """Test successful YAML file reading."""
        yaml_path = Path(__file__).parent / 'resume.yaml'
        data = hg.read_yaml_file(yaml_path)

        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertIn('basics', data)
        self.assertIn('work_experience', data)

    def test_read_yaml_file_not_found(self):
        """Test handling of non-existent file."""
        data = hg.read_yaml_file('/nonexistent/path/file.yaml')
        self.assertIsNone(data)

    def test_read_yaml_file_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [unclosed')
            temp_path = f.name

        try:
            data = hg.read_yaml_file(temp_path)
            self.assertIsNone(data)
        finally:
            os.unlink(temp_path)


class TestLoadResumeData(unittest.TestCase):
    """Test resume data loading with profile filtering."""

    def test_load_with_default_profile(self):
        """Test loading data with default profile."""
        data, profile_info = hg.load_resume_data(profile_name='default')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Full Resume')

    def test_load_with_technical_profile(self):
        """Test loading data with technical profile."""
        data, profile_info = hg.load_resume_data(profile_name='technical')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Technical Focused')

    def test_load_with_leadership_profile(self):
        """Test loading data with leadership profile."""
        data, profile_info = hg.load_resume_data(profile_name='leadership')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Leadership Focused')

    def test_load_with_invalid_profile(self):
        """Test handling of non-existent profile."""
        data, profile_info = hg.load_resume_data(profile_name='nonexistent')

        self.assertIsNone(data)
        self.assertIsNone(profile_info)


class TestHTMLGeneration(unittest.TestCase):
    """Test HTML generation functions."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.resume_data, cls.profile_info = hg.load_resume_data(profile_name='default')

    def test_generate_header(self):
        """Test header generation."""
        header = hg.generate_header(self.resume_data['basics'])

        self.assertIn('<head>', header)
        self.assertIn('</head>', header)
        self.assertIn('<title>', header)
        self.assertIn('Colin', header)

    def test_generate_navigation(self):
        """Test navigation generation."""
        nav = hg.generate_navigation(self.resume_data)

        self.assertIn('main-nav', nav)
        self.assertIn('About', nav)
        self.assertIn('Experiences', nav)
        self.assertIn('Education', nav)

    def test_generate_introduction(self):
        """Test introduction section generation."""
        intro = hg.generate_introduction(self.resume_data['basics'])

        self.assertIn('intro section', intro)
        self.assertIn('Colin', intro)
        self.assertIn(self.resume_data['basics']['summary'][:50], intro)

    def test_generate_work_experience(self):
        """Test work experience section generation."""
        work = hg.generate_work_experience(self.resume_data['work_experience'])

        self.assertIn('Work', work)
        self.assertIn('Experiences', work)
        self.assertIn('Arctic Wolf', work)

    def test_generate_education_and_certs(self):
        """Test education and certifications section generation."""
        section = hg.generate_education_and_certs(
            self.resume_data.get('education'),
            self.resume_data.get('certifications'),
            self.resume_data.get('awards')
        )

        self.assertIsNotNone(section)
        self.assertIn('Education', section)

    def test_generate_skills(self):
        """Test skills section generation."""
        skills = hg.generate_skills(
            self.resume_data.get('skills'),
            self.resume_data.get('specialty_skills')
        )

        self.assertIn('Technical', skills)
        self.assertIn('Skills', skills)

    def test_generate_projects(self):
        """Test projects section generation."""
        projects = hg.generate_projects(self.resume_data.get('projects'))

        if self.resume_data.get('projects'):
            self.assertIn('Projects', projects)

    def test_generate_footer(self):
        """Test footer generation."""
        footer = hg.generate_footer(self.resume_data)

        self.assertIn('footer', footer)
        self.assertIn('Colin McAllister', footer)

    def test_generate_javascript(self):
        """Test JavaScript section generation."""
        js = hg.generate_javascript(self.resume_data)

        self.assertIn('script', js)
        self.assertIn('typed', js)

    def test_generate_full_html(self):
        """Test complete HTML generation."""
        html = hg.generate_html(self.resume_data, self.profile_info)

        self.assertIsNotNone(html)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('<html>', html)
        self.assertIn('</html>', html)
        self.assertIn('<head>', html)
        self.assertIn('</head>', html)
        self.assertIn('<body>', html)
        self.assertIn('</body>', html)


class TestAllProfiles(unittest.TestCase):
    """Test HTML generation for all available profiles."""

    def test_all_profiles_generate_valid_html(self):
        """Test that all profiles generate valid HTML."""
        profiles = pm.list_available_profiles()

        self.assertGreater(len(profiles), 0, "No profiles found")

        for profile_name in profiles:
            with self.subTest(profile=profile_name):
                data, profile_info = hg.load_resume_data(profile_name=profile_name)

                self.assertIsNotNone(data, f"Failed to load data for profile: {profile_name}")
                self.assertIsNotNone(profile_info, f"Failed to load profile info for: {profile_name}")

                html = hg.generate_html(data, profile_info)

                self.assertIsNotNone(html, f"Failed to generate HTML for profile: {profile_name}")
                self.assertIn('<!DOCTYPE html>', html)
                self.assertIn('<html>', html)
                self.assertIn('</html>', html)

    def test_profile_output_paths(self):
        """Test that profiles generate correct output paths."""
        test_cases = [
            ('default', 'index.html'),
            ('technical', 'resume-technical.html'),
            ('leadership', 'resume-leadership.html'),
        ]

        for profile_name, expected_filename in test_cases:
            with self.subTest(profile=profile_name):
                try:
                    profile = pm.load_profile(profile_name)
                    profile_info = pm.get_profile_info(profile)
                    output_path = hg.get_output_path(profile_info)

                    self.assertEqual(output_path.name, expected_filename)
                except pm.ProfileNotFoundError:
                    self.skipTest(f"Profile {profile_name} not found")


class TestHTMLFileGeneration(unittest.TestCase):
    """Test actual HTML file generation."""

    def test_generate_for_profile_creates_file(self):
        """Test that generate_for_profile creates an HTML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.html'

            success = hg.generate_for_profile(
                'default',
                output_path=str(output_path),
                verbose=False
            )

            self.assertTrue(success)
            self.assertTrue(output_path.exists())

            # Verify file content
            content = output_path.read_text()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('Colin', content)

    def test_generate_for_invalid_profile_fails(self):
        """Test that invalid profile returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.html'

            success = hg.generate_for_profile(
                'nonexistent_profile',
                output_path=str(output_path),
                verbose=False
            )

            self.assertFalse(success)
            self.assertFalse(output_path.exists())


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility features."""

    def test_json_loading_still_works(self):
        """Test that JSON loading function is still available."""
        self.assertTrue(callable(hg.read_json_file))

        # Test with nonexistent file (should return None, not error)
        result = hg.read_json_file('/nonexistent/file.json')
        self.assertIsNone(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_generate_html_with_none_data(self):
        """Test HTML generation with None data."""
        html = hg.generate_html(None)
        self.assertIsNone(html)

    def test_generate_projects_with_none(self):
        """Test projects generation with None."""
        result = hg.generate_projects(None)
        self.assertIsNone(result)

    def test_generate_quote_without_quote(self):
        """Test quote generation when no quote exists."""
        basics_no_quote = {'name': 'Test User'}
        result = hg.generate_quote(basics_no_quote)
        self.assertIsNone(result)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
