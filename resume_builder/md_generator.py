#!/usr/bin/env python3
"""
Markdown Generator for Resume Builder

This module generates Markdown resume files from YAML data with profile filtering support.
It follows the same patterns as html_generator.py for consistency.

Usage:
    python md_generator.py                    # Generate with default profile
    python md_generator.py -p technical       # Generate with technical profile
    python md_generator.py -l                 # List available profiles
    python md_generator.py --all-profiles     # Generate for all profiles
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

import shared_functions as s
import profile_manager as pm


def read_yaml_file(file_path):
    """Read and parse a YAML file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        Dictionary containing the YAML data, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error decoding YAML. Please ensure the file is a valid YAML format: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# =============================================================================
# DEPRECATED: JSON Loading Function
# =============================================================================
# The following function is deprecated as of 2025-11-21.
# The system now uses YAML exclusively. See resume_builder/resume.yaml
# This code is kept for reference only and may be removed in a future version.
#
# def read_json_file(file_path):
#     """Read and parse a JSON file (DEPRECATED - use read_yaml_file instead).
#
#     Args:
#         file_path: Path to the JSON file.
#
#     Returns:
#         Dictionary containing the JSON data, or None if an error occurs.
#     """
#     import json
#     try:
#         with open(file_path, 'r') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"The file at {file_path} was not found.")
#         return None
#     except json.JSONDecodeError:
#         print("Error decoding JSON. Please ensure the file is a valid JSON format.")
#         return None
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None
# =============================================================================


def load_resume_data(data_path=None, profile_name='default'):
    """Load resume data from YAML and apply profile filtering.

    Args:
        data_path: Path to the YAML data file. Defaults to resume.yaml in same directory.
        profile_name: Name of the profile to apply for filtering.

    Returns:
        Tuple of (filtered_data, profile_info) or (None, None) if an error occurs.
    """
    # Determine the data file path
    if data_path is None:
        script_dir = Path(__file__).parent
        data_path = script_dir / 'resume.yaml'

    # Load the resume data
    resume_data = read_yaml_file(data_path)
    if resume_data is None:
        return None, None

    # Load and apply profile filtering
    try:
        profile = pm.load_profile(profile_name)
        filtered_data = pm.filter_resume_data(resume_data, profile)
        profile_info = pm.get_profile_info(profile)
        return filtered_data, profile_info
    except pm.ProfileNotFoundError as e:
        print(f"Profile error: {e}")
        return None, None
    except pm.InvalidProfileError as e:
        print(f"Invalid profile: {e}")
        return None, None


# Function to generate skills section
def generate_skills(skills=None, specialty_skills=None):
    """Generate the skills section in Markdown format.

    Args:
        skills: List of skill strings.
        specialty_skills: List of specialty skill dictionaries with 'name' and 'keywords'.

    Returns:
        Markdown string for skills section, or None if no skills provided.
    """
    if not skills and not specialty_skills:
        return None

    markdown = "## Skills\n\n"
    markdown += '''<div class="no-break"> \n'''
    if skills:
        for skill in skills:
            markdown += f"```{skill}```\n"
        markdown += "\n"
    if specialty_skills:
        for spskill in specialty_skills:
            name = spskill.get('name', '')
            keywords = spskill.get('keywords', [])
            if name and keywords:
                markdown += f"**{name}**: "
                markdown += ", ".join(keywords)
                markdown += "  \n"
    markdown += "\n  </div>  \n"
    return markdown


# Function to generate experience section
def generate_experience(work_experience):
    """Generate the experience section in Markdown format.

    Args:
        work_experience: Dictionary of company names to list of positions.

    Returns:
        Markdown string for experience section.
    """
    if not work_experience:
        return ""

    markdown = '''<div class="no-break"> \n'''
    markdown += "## Experience\n\n"
    for company, positions in work_experience.items():
        markdown += f"### {company}  \n"
        for position in positions:
            responsibilities = position.get('responsibilities', None)
            skills = position.get('skills', None)
            start_date = position.get('start_date', '')
            end_date = position.get('end_date', '')
            location = position.get('location', '')
            job_title = position.get('job_title', '')

            markdown += f"#### {job_title}  \n"
            markdown += f"{s.get_month_and_year(start_date)} - {s.get_month_and_year(end_date)}"
            if location:
                markdown += f", {location}"
            markdown += "  \n"

            if responsibilities:
                for responsibility in responsibilities:
                    markdown += f"- {responsibility}  \n"
            if skills:
                markdown += f"*Skills*: "
                for skill in skills:
                    markdown += f"```{skill}```"
                    if skill != skills[-1]:
                        markdown += ", "
                markdown += "  \n"
            markdown += "\n  </div>  \n"
    return markdown


def generate_certifications(certifications):
    """Generate the certifications section in Markdown format.

    Args:
        certifications: List of certification dictionaries.

    Returns:
        Markdown string for certifications section, or None if no certifications.
    """
    if not certifications:
        return None

    markdown = '''<div class="no-break"> \n'''
    markdown += "## Certifications\n\n"
    for i, certification in enumerate(certifications):
        url = certification.get('url', None)
        acronym = certification.get('acronym', None)
        title = certification.get('title', None)
        name = certification.get('name', title)  # Fall back to title if name not present
        date = certification.get('date', '')

        display_name = acronym if acronym else name

        if display_name and url:
            markdown += f"- **[{display_name}]({url})** | {s.get_month_and_year(date)}"
        elif display_name:
            markdown += f"- **{display_name}** | {s.get_month_and_year(date)}"

        if i < len(certifications) - 1:
            markdown += ", "
    markdown += "\n  </div>  \n"
    return markdown


# Function to generate education section
def generate_education(education):
    """Generate the education section in Markdown format.

    Args:
        education: List of education dictionaries.

    Returns:
        Markdown string for education section, or None if no education.
    """
    if not education:
        return None

    markdown = "## Education  \n\n"
    for edu in education:
        markdown += '''  <div class="no-break">  \n'''
        honors = edu.get('honors', None)
        gpa = edu.get('score', None)
        start_year = s.get_year(edu.get('startDate', ''))
        end_year = s.get_year(edu.get('endDate', ''))
        study_type = edu.get('studyType', '')
        area = edu.get('area', '')
        institution = edu.get('institution', '')

        markdown += f"### {study_type} in {area} @ {institution}\n"
        markdown += f"{start_year} - {end_year}  \n"
        if honors:
            markdown += f"- Honors: *{honors}*  \n"
        if gpa:
            markdown += f"- GPA: *{gpa}*  \n"
        markdown += "\n  </div>  \n"
    return markdown


# Function to generate awards section
def generate_awards(awards):
    """Generate the awards section in Markdown format.

    Args:
        awards: List of award dictionaries.

    Returns:
        Markdown string for awards section, or None if no awards.
    """
    if not awards:
        return None

    markdown = "## Awards & Recognition\n\n"
    for award in awards:
        title = award.get('title', '')
        awarder = award.get('awarder', '')
        date = award.get('date', '')
        markdown += f"- **{title}** | {awarder} ({s.get_month_and_year(date)})  \n"
    return markdown


# Function to generate projects section
def generate_projects(projects):
    """Generate the projects section in Markdown format.

    Args:
        projects: List of project dictionaries.

    Returns:
        Markdown string for projects section, or None if no projects.
    """
    if not projects:
        return None

    markdown = "## Projects\n\n"
    for project in projects:
        project_url = project.get('url', None)
        name = project.get('name', '')
        description = project.get('description', '')
        start_date = project.get('startDate', '')

        if project_url:
            markdown += f"**[{name}]({project_url})**"
        else:
            markdown += f"**{name}**"
        if start_date:
            markdown += f" ({s.get_month_and_year(start_date)})\n"
        else:
            markdown += "\n"
        if description:
            markdown += f"*{description}*  \n"
    return markdown


def generate_keywords(skills):
    """Generate YAML keywords list for markdown frontmatter.

    Args:
        skills: List of skill strings.

    Returns:
        Formatted keywords string.
    """
    if not skills:
        return ""
    keywords = ""
    for skill in skills:
        keywords += f"- {skill}\n"
    return keywords


def generate_contact_info(contact_info):
    """Generate contact info line for markdown.

    Args:
        contact_info: List of contact info dictionaries with 'title' and 'value'.

    Returns:
        Formatted contact info string.
    """
    if not contact_info:
        return ""
    markdown = "###### "
    for contact in contact_info:
        title = contact.get('title', '')
        value = contact.get('value', '')
        markdown += f"{title}: **{value}**"
        if contact != contact_info[-1]:
            markdown += " | "
    return markdown


def generate_markdown(resume_data, profile_info=None):
    """Generate complete Markdown document from resume data.

    Args:
        resume_data: Dictionary containing resume data.
        profile_info: Optional profile info dictionary for customization.

    Returns:
        Complete Markdown document string, or None if no data provided.
    """
    if resume_data is None:
        return None

    basics = resume_data.get('basics', {})
    name = basics.get('name', 'Resume')
    label = basics.get('label', '')
    short_summary = basics.get('short_summary', basics.get('summary', ''))
    contact_info = basics.get('contact_info', [])

    # Generate skills keywords for frontmatter
    skills = resume_data.get('skills', [])
    if isinstance(skills, list) and skills and isinstance(skills[0], dict):
        # Skills are objects with keywords
        skill_keywords = []
        for skill in skills:
            skill_keywords.extend(skill.get('keywords', []))
    else:
        # Skills are simple strings
        skill_keywords = skills if skills else []

    # Build the markdown document with YAML frontmatter
    markdown = f'''---
margin-left: 2cm
margin-right: 2cm
margin-top: 1cm
margin-bottom: 2cm
title: {name}
description-meta: 'Resume of {name} - {label}'
keywords:
{generate_keywords(skill_keywords)}
author:
- {name}
subject: 'Resume'
---
'''

    # Add contact info if available
    if contact_info:
        markdown += generate_contact_info(contact_info)
        markdown += "\n\n"

    # Add short summary
    if short_summary:
        markdown += f"{short_summary}\n\n"

    # Add sections (handle None returns)
    certifications_section = generate_certifications(resume_data.get('certifications', None))
    if certifications_section:
        markdown += certifications_section + "\n"

    education_section = generate_education(resume_data.get('education', None))
    if education_section:
        markdown += education_section + "\n"

    experience_section = generate_experience(resume_data.get('work_experience', {}))
    if experience_section:
        markdown += experience_section + "\n"

    awards_section = generate_awards(resume_data.get('awards', None))
    if awards_section:
        markdown += awards_section + "\n"

    projects_section = generate_projects(resume_data.get('projects', None))
    if projects_section:
        markdown += projects_section + "\n"

    skills_section = generate_skills(
        resume_data.get('skills', None) if not isinstance(resume_data.get('skills', []), list) or not resume_data.get('skills') or not isinstance(resume_data.get('skills', [[]])[0], dict) else None,
        resume_data.get('specialty_skills', None)
    )
    if skills_section:
        markdown += skills_section + "\n"

    return markdown


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate Markdown resume from YAML data with profile filtering.'
    )
    parser.add_argument(
        '-p', '--profile',
        default='default',
        help='Profile name to use for filtering (default: default)'
    )
    parser.add_argument(
        '-i', '--input',
        default=None,
        help='Path to input YAML file (default: resume.yaml)'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Path to output Markdown file (default: resume.md or based on profile)'
    )
    parser.add_argument(
        '-l', '--list-profiles',
        action='store_true',
        help='List available profiles and exit'
    )
    parser.add_argument(
        '--all-profiles',
        action='store_true',
        help='Generate Markdown for all available profiles'
    )
    return parser.parse_args()


def get_output_path(profile_info, output_arg=None):
    """Determine the output path for the Markdown file.

    Args:
        profile_info: Profile information dictionary.
        output_arg: Optional output path from command line.

    Returns:
        Path object for the output file.
    """
    if output_arg:
        return Path(output_arg)

    # Use profile filename if available
    script_dir = Path(__file__).parent
    if profile_info and profile_info.get('filename'):
        filename = profile_info['filename']
        if filename == 'resume':
            return script_dir / 'resume.md'
        else:
            return script_dir / f'{filename}.md'
    else:
        return script_dir / 'resume.md'


def generate_for_profile(profile_name, input_path=None, output_path=None, verbose=True):
    """Generate Markdown for a specific profile.

    Args:
        profile_name: Name of the profile to use.
        input_path: Optional path to input YAML file.
        output_path: Optional path to output Markdown file.
        verbose: Whether to print status messages.

    Returns:
        True if successful, False otherwise.
    """
    if verbose:
        print(f"Generating Markdown for profile: {profile_name}")

    # Load and filter resume data
    resume_data, profile_info = load_resume_data(input_path, profile_name)
    if resume_data is None:
        print(f"Failed to load resume data for profile: {profile_name}")
        return False

    # Generate Markdown
    markdown_content = generate_markdown(resume_data, profile_info)
    if markdown_content is None:
        print(f"Failed to generate Markdown for profile: {profile_name}")
        return False

    # Determine output path
    final_output = get_output_path(profile_info, output_path)

    # Write the Markdown file
    try:
        with open(final_output, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        if verbose:
            print(f"Successfully wrote Markdown to: {final_output}")
        return True
    except Exception as e:
        print(f"Error writing Markdown file: {e}")
        return False


if __name__ == "__main__":
    args = parse_args()

    # List profiles if requested
    if args.list_profiles:
        profiles = pm.list_available_profiles()
        print("Available profiles:")
        for profile_name in profiles:
            try:
                profile = pm.load_profile(profile_name)
                info = pm.get_profile_info(profile)
                print(f"  - {profile_name}: {info.get('description', 'No description')}")
            except Exception as e:
                print(f"  - {profile_name}: (error loading: {e})")
        sys.exit(0)

    # Generate for all profiles if requested
    if args.all_profiles:
        profiles = pm.list_available_profiles()
        success_count = 0
        for profile_name in profiles:
            if generate_for_profile(profile_name, args.input):
                success_count += 1
        print(f"\nGenerated {success_count}/{len(profiles)} Markdown files successfully.")
        sys.exit(0 if success_count == len(profiles) else 1)

    # Generate for single profile
    success = generate_for_profile(args.profile, args.input, args.output)
    sys.exit(0 if success else 1)
