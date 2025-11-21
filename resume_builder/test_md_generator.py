#!/usr/bin/env python3
"""
Tests for the Markdown Generator module.

This module tests:
- YAML loading functionality
- Profile integration
- Markdown generation for all profiles
- Output quality validation
- Markdown -> HTML -> PDF pipeline readiness
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the resume_builder directory to the path
sys.path.insert(0, str(Path(__file__).parent))

import md_generator as mg
import profile_manager as pm


class TestYAMLLoading(unittest.TestCase):
    """Test YAML loading functionality."""

    def test_read_yaml_file_success(self):
        """Test successful YAML file reading."""
        yaml_path = Path(__file__).parent / 'resume.yaml'
        data = mg.read_yaml_file(yaml_path)

        self.assertIsNotNone(data)
        self.assertIsInstance(data, dict)
        self.assertIn('basics', data)
        self.assertIn('work_experience', data)

    def test_read_yaml_file_not_found(self):
        """Test handling of non-existent file."""
        data = mg.read_yaml_file('/nonexistent/path/file.yaml')
        self.assertIsNone(data)

    def test_read_yaml_file_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [unclosed')
            temp_path = f.name

        try:
            data = mg.read_yaml_file(temp_path)
            self.assertIsNone(data)
        finally:
            os.unlink(temp_path)


class TestLoadResumeData(unittest.TestCase):
    """Test resume data loading with profile filtering."""

    def test_load_with_default_profile(self):
        """Test loading data with default profile."""
        data, profile_info = mg.load_resume_data(profile_name='default')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Full Resume')

    def test_load_with_technical_profile(self):
        """Test loading data with technical profile."""
        data, profile_info = mg.load_resume_data(profile_name='technical')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Technical Focused')

    def test_load_with_leadership_profile(self):
        """Test loading data with leadership profile."""
        data, profile_info = mg.load_resume_data(profile_name='leadership')

        self.assertIsNotNone(data)
        self.assertIsNotNone(profile_info)
        self.assertEqual(profile_info['name'], 'Leadership Focused')

    def test_load_with_invalid_profile(self):
        """Test handling of non-existent profile."""
        data, profile_info = mg.load_resume_data(profile_name='nonexistent')

        self.assertIsNone(data)
        self.assertIsNone(profile_info)


class TestMarkdownGeneration(unittest.TestCase):
    """Test Markdown generation functions."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.resume_data, cls.profile_info = mg.load_resume_data(profile_name='default')

    def test_generate_skills(self):
        """Test skills section generation."""
        specialty_skills = self.resume_data.get('specialty_skills', [])
        skills = mg.generate_skills(None, specialty_skills)

        if specialty_skills:
            self.assertIsNotNone(skills)
            self.assertIn('## Skills', skills)
            self.assertIn('no-break', skills)

    def test_generate_experience(self):
        """Test experience section generation."""
        experience = mg.generate_experience(self.resume_data['work_experience'])

        self.assertIsNotNone(experience)
        self.assertIn('## Experience', experience)
        self.assertIn('Arctic Wolf', experience)

    def test_generate_certifications(self):
        """Test certifications section generation."""
        certs = mg.generate_certifications(self.resume_data.get('certifications'))

        if self.resume_data.get('certifications'):
            self.assertIsNotNone(certs)
            self.assertIn('## Certifications', certs)

    def test_generate_education(self):
        """Test education section generation."""
        edu = mg.generate_education(self.resume_data.get('education'))

        if self.resume_data.get('education'):
            self.assertIsNotNone(edu)
            self.assertIn('## Education', edu)

    def test_generate_awards(self):
        """Test awards section generation."""
        awards = mg.generate_awards(self.resume_data.get('awards'))

        if self.resume_data.get('awards'):
            self.assertIsNotNone(awards)
            self.assertIn('## Awards', awards)

    def test_generate_projects(self):
        """Test projects section generation."""
        projects = mg.generate_projects(self.resume_data.get('projects'))

        if self.resume_data.get('projects'):
            self.assertIsNotNone(projects)
            self.assertIn('## Projects', projects)

    def test_generate_contact_info(self):
        """Test contact info generation."""
        contact_info = self.resume_data['basics'].get('contact_info', [])
        if contact_info:
            result = mg.generate_contact_info(contact_info)
            self.assertIn('######', result)

    def test_generate_keywords(self):
        """Test keywords generation for frontmatter."""
        skills = ['Python', 'JavaScript', 'Security']
        keywords = mg.generate_keywords(skills)

        self.assertIn('- Python', keywords)
        self.assertIn('- JavaScript', keywords)
        self.assertIn('- Security', keywords)

    def test_generate_full_markdown(self):
        """Test complete Markdown generation."""
        markdown = mg.generate_markdown(self.resume_data, self.profile_info)

        self.assertIsNotNone(markdown)
        # Check YAML frontmatter
        self.assertIn('---', markdown)
        self.assertIn('title:', markdown)
        self.assertIn('author:', markdown)
        # Check content sections
        self.assertIn('## Experience', markdown)


class TestAllProfiles(unittest.TestCase):
    """Test Markdown generation for all available profiles."""

    def test_all_profiles_generate_valid_markdown(self):
        """Test that all profiles generate valid Markdown."""
        profiles = pm.list_available_profiles()

        self.assertGreater(len(profiles), 0, "No profiles found")

        for profile_name in profiles:
            with self.subTest(profile=profile_name):
                data, profile_info = mg.load_resume_data(profile_name=profile_name)

                self.assertIsNotNone(data, f"Failed to load data for profile: {profile_name}")
                self.assertIsNotNone(profile_info, f"Failed to load profile info for: {profile_name}")

                markdown = mg.generate_markdown(data, profile_info)

                self.assertIsNotNone(markdown, f"Failed to generate Markdown for profile: {profile_name}")
                self.assertIn('---', markdown)  # Has frontmatter
                self.assertIn('title:', markdown)

    def test_profile_output_paths(self):
        """Test that profiles generate correct output paths."""
        test_cases = [
            ('default', 'resume.md'),
            ('technical', 'resume-technical.md'),
            ('leadership', 'resume-leadership.md'),
        ]

        for profile_name, expected_filename in test_cases:
            with self.subTest(profile=profile_name):
                try:
                    profile = pm.load_profile(profile_name)
                    profile_info = pm.get_profile_info(profile)
                    output_path = mg.get_output_path(profile_info)

                    self.assertEqual(output_path.name, expected_filename)
                except pm.ProfileNotFoundError:
                    self.skipTest(f"Profile {profile_name} not found")


class TestMarkdownFileGeneration(unittest.TestCase):
    """Test actual Markdown file generation."""

    def test_generate_for_profile_creates_file(self):
        """Test that generate_for_profile creates a Markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.md'

            success = mg.generate_for_profile(
                'default',
                output_path=str(output_path),
                verbose=False
            )

            self.assertTrue(success)
            self.assertTrue(output_path.exists())

            # Verify file content
            content = output_path.read_text()
            self.assertIn('---', content)
            self.assertIn('Colin', content)

    def test_generate_for_invalid_profile_fails(self):
        """Test that invalid profile returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / 'test_output.md'

            success = mg.generate_for_profile(
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
        self.assertTrue(callable(mg.read_json_file))

        # Test with nonexistent file (should return None, not error)
        result = mg.read_json_file('/nonexistent/file.json')
        self.assertIsNone(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_generate_markdown_with_none_data(self):
        """Test Markdown generation with None data."""
        markdown = mg.generate_markdown(None)
        self.assertIsNone(markdown)

    def test_generate_projects_with_none(self):
        """Test projects generation with None."""
        result = mg.generate_projects(None)
        self.assertIsNone(result)

    def test_generate_awards_with_none(self):
        """Test awards generation with None."""
        result = mg.generate_awards(None)
        self.assertIsNone(result)

    def test_generate_education_with_none(self):
        """Test education generation with None."""
        result = mg.generate_education(None)
        self.assertIsNone(result)

    def test_generate_certifications_with_none(self):
        """Test certifications generation with None."""
        result = mg.generate_certifications(None)
        self.assertIsNone(result)

    def test_generate_experience_with_empty(self):
        """Test experience generation with empty dict."""
        result = mg.generate_experience({})
        self.assertEqual(result, "")

    def test_generate_skills_with_none(self):
        """Test skills generation with None."""
        result = mg.generate_skills(None, None)
        self.assertIsNone(result)

    def test_generate_contact_info_with_empty(self):
        """Test contact info generation with empty list."""
        result = mg.generate_contact_info([])
        self.assertEqual(result, "")

    def test_generate_keywords_with_empty(self):
        """Test keywords generation with empty list."""
        result = mg.generate_keywords([])
        self.assertEqual(result, "")


class TestMarkdownPipelineReadiness(unittest.TestCase):
    """Test that generated Markdown is ready for HTML/PDF conversion pipeline."""

    def test_markdown_has_valid_frontmatter(self):
        """Test that Markdown has valid YAML frontmatter for Pandoc."""
        data, profile_info = mg.load_resume_data(profile_name='default')
        markdown = mg.generate_markdown(data, profile_info)

        # Check frontmatter structure
        lines = markdown.split('\n')
        self.assertEqual(lines[0], '---')

        # Find closing frontmatter
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line == '---':
                frontmatter_end = i
                break

        self.assertGreater(frontmatter_end, 0, "Frontmatter not properly closed")

        # Verify required frontmatter fields
        frontmatter = '\n'.join(lines[1:frontmatter_end])
        self.assertIn('title:', frontmatter)
        self.assertIn('author:', frontmatter)

    def test_markdown_has_proper_heading_structure(self):
        """Test that Markdown has proper heading hierarchy."""
        data, profile_info = mg.load_resume_data(profile_name='default')
        markdown = mg.generate_markdown(data, profile_info)

        # Should have H2 sections
        self.assertIn('## ', markdown)

        # Verify section headings
        if data.get('work_experience'):
            self.assertIn('## Experience', markdown)
        if data.get('education'):
            self.assertIn('## Education', markdown)

    def test_markdown_links_are_valid(self):
        """Test that Markdown links have proper format."""
        data, profile_info = mg.load_resume_data(profile_name='default')
        markdown = mg.generate_markdown(data, profile_info)

        # Check that links follow Markdown format [text](url)
        import re
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', markdown)

        for text, url in links:
            # Text should not be empty
            self.assertTrue(len(text) > 0, f"Empty link text for URL: {url}")
            # URL should start with http or be a relative path
            self.assertTrue(
                url.startswith('http') or url.startswith('/') or url.startswith('.'),
                f"Invalid URL format: {url}"
            )


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
