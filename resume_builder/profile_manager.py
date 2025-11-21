#!/usr/bin/env python3
"""
Profile Manager for Resume Builder

This module provides the core filtering logic for applying profile rules to resume data.
It supports:
- Loading profile configurations from YAML files
- Filtering resume items based on include_in tags
- Limiting bullets per job based on profile settings
- Handling edge cases gracefully (missing tags, empty profiles, etc.)
"""

import os
import copy
from pathlib import Path
from typing import Any, Optional, Union

import yaml


class ProfileNotFoundError(Exception):
    """Raised when a profile configuration file is not found."""
    pass


class InvalidProfileError(Exception):
    """Raised when a profile configuration is invalid or malformed."""
    pass


def get_profiles_directory() -> Path:
    """Get the profiles directory path.

    Returns:
        Path to the profiles directory.
    """
    return Path(__file__).parent / "profiles"


def load_profile(profile_name: str, profiles_dir: Optional[Path] = None) -> dict:
    """Load profile configuration from profiles/ directory.

    Args:
        profile_name: Name of the profile to load (without .yaml extension).
        profiles_dir: Optional custom profiles directory path.

    Returns:
        Dictionary containing the profile configuration.

    Raises:
        ProfileNotFoundError: If the profile file does not exist.
        InvalidProfileError: If the profile file is empty or invalid.
    """
    if profiles_dir is None:
        profiles_dir = get_profiles_directory()

    profile_path = profiles_dir / f"{profile_name}.yaml"

    if not profile_path.exists():
        raise ProfileNotFoundError(f"Profile '{profile_name}' not found at {profile_path}")

    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise InvalidProfileError(f"Failed to parse profile '{profile_name}': {e}")

    if profile is None:
        raise InvalidProfileError(f"Profile '{profile_name}' is empty")

    # Validate required structure
    if not isinstance(profile, dict):
        raise InvalidProfileError(f"Profile '{profile_name}' must be a dictionary")

    # Ensure filters section exists with defaults
    if 'filters' not in profile:
        profile['filters'] = {}

    if 'include_tags' not in profile['filters']:
        profile['filters']['include_tags'] = ['all']

    return profile


def list_available_profiles(profiles_dir: Optional[Path] = None) -> list:
    """List all available profile names.

    Args:
        profiles_dir: Optional custom profiles directory path.

    Returns:
        List of profile names (without .yaml extension).
    """
    if profiles_dir is None:
        profiles_dir = get_profiles_directory()

    if not profiles_dir.exists():
        return []

    profiles = []
    for file in profiles_dir.glob("*.yaml"):
        profiles.append(file.stem)

    return sorted(profiles)


def filter_items(items: list, include_tags: list) -> list:
    """Filter list items based on include_in tags.

    An item is included if ANY of its include_in tags matches ANY of the include_tags.
    Items without include_in tags are excluded unless 'all' is in include_tags.

    Args:
        items: List of items to filter. Each item may have an 'include_in' key.
        include_tags: List of tags that should be included.

    Returns:
        Filtered list of items (deep copied to avoid mutations).
    """
    if not items:
        return []

    if not include_tags:
        return []

    # Normalize include_tags to set for O(1) lookup
    include_tags_set = set(include_tags)

    filtered = []
    for item in items:
        if not isinstance(item, dict):
            # Non-dict items (e.g., strings) are included if 'all' is in tags
            if 'all' in include_tags_set:
                filtered.append(copy.deepcopy(item))
            continue

        item_tags = item.get('include_in', [])

        # Handle malformed tags (non-list)
        if not isinstance(item_tags, list):
            if item_tags is None:
                item_tags = []
            else:
                # Convert single value to list
                item_tags = [item_tags]

        # Check if any item tag matches any include tag
        item_tags_set = set(item_tags)

        if item_tags_set & include_tags_set:  # Set intersection
            filtered.append(copy.deepcopy(item))
        elif not item_tags and 'all' in include_tags_set:
            # Items without tags are included when 'all' is specified
            filtered.append(copy.deepcopy(item))

    return filtered


def apply_bullet_limit(bullets: list, max_bullets: Optional[int]) -> list:
    """Limit number of bullets per job.

    Args:
        bullets: List of bullet points.
        max_bullets: Maximum number of bullets to keep. None or 0 means no limit.

    Returns:
        Truncated list of bullets (deep copied).
    """
    if not bullets:
        return []

    if max_bullets is None or max_bullets <= 0:
        return copy.deepcopy(bullets)

    return copy.deepcopy(bullets[:max_bullets])


def filter_work_experience(work_data: dict, include_tags: list, max_bullets: Optional[int] = None) -> dict:
    """Filter work experience entries based on tags and bullet limits.

    Work experience is structured as:
    {
        "Company Name": [
            {
                "job_title": "...",
                "responsibilities": [...],
                "include_in": [...]
            }
        ]
    }

    Args:
        work_data: Dictionary of company -> list of positions.
        include_tags: List of tags to include.
        max_bullets: Optional maximum bullets per job.

    Returns:
        Filtered work experience dictionary.
    """
    if not work_data:
        return {}

    if not isinstance(work_data, dict):
        return {}

    include_tags_set = set(include_tags)
    filtered_work = {}

    for company, positions in work_data.items():
        if not isinstance(positions, list):
            continue

        filtered_positions = []
        for position in positions:
            if not isinstance(position, dict):
                continue

            # Check include_in tags
            position_tags = position.get('include_in', [])
            if not isinstance(position_tags, list):
                position_tags = [position_tags] if position_tags else []

            position_tags_set = set(position_tags)

            # Include if tags match or if 'all' in include_tags and no specific tags
            if position_tags_set & include_tags_set or (not position_tags and 'all' in include_tags_set):
                new_position = copy.deepcopy(position)

                # Apply bullet limit to responsibilities
                if 'responsibilities' in new_position:
                    new_position['responsibilities'] = apply_bullet_limit(
                        new_position['responsibilities'],
                        max_bullets
                    )

                # Also handle 'highlights' if present (JSON Resume format)
                if 'highlights' in new_position:
                    new_position['highlights'] = apply_bullet_limit(
                        new_position['highlights'],
                        max_bullets
                    )

                filtered_positions.append(new_position)

        if filtered_positions:
            filtered_work[company] = filtered_positions

    return filtered_work


def filter_projects(projects: list, include_tags: list, max_bullets: Optional[int] = None) -> list:
    """Filter projects and apply bullet limits to highlights.

    Args:
        projects: List of project entries.
        include_tags: List of tags to include.
        max_bullets: Optional maximum bullets per project.

    Returns:
        Filtered list of projects.
    """
    filtered = filter_items(projects, include_tags)

    if max_bullets is None or max_bullets <= 0:
        return filtered

    # Apply bullet limit to highlights
    for project in filtered:
        if isinstance(project, dict) and 'highlights' in project:
            project['highlights'] = apply_bullet_limit(
                project['highlights'],
                max_bullets
            )

    return filtered


def filter_resume_data(resume_data: dict, profile: dict) -> dict:
    """Apply profile filters to resume data.

    This is the main filtering function that processes all sections of the resume
    according to the profile configuration.

    Args:
        resume_data: Full resume data dictionary.
        profile: Profile configuration dictionary.

    Returns:
        Filtered resume data (deep copied to avoid mutations).
    """
    if not resume_data:
        return {}

    if not profile:
        return copy.deepcopy(resume_data)

    # Extract filter settings
    filters = profile.get('filters', {})
    include_tags = filters.get('include_tags', ['all'])
    max_bullets = filters.get('max_bullets_per_job')

    # Ensure include_tags is a list
    if not isinstance(include_tags, list):
        include_tags = [include_tags] if include_tags else ['all']

    # Deep copy to avoid mutations
    filtered_data = copy.deepcopy(resume_data)

    # Filter work_experience
    if 'work_experience' in filtered_data:
        filtered_data['work_experience'] = filter_work_experience(
            resume_data.get('work_experience', {}),
            include_tags,
            max_bullets
        )

    # Filter work (JSON Resume format)
    if 'work' in filtered_data:
        # JSON Resume uses 'work' as a list, handle it differently
        work_list = resume_data.get('work', [])
        filtered_work = []
        include_tags_set = set(include_tags)

        for job in work_list:
            if not isinstance(job, dict):
                continue

            job_tags = job.get('include_in', [])
            if not isinstance(job_tags, list):
                job_tags = [job_tags] if job_tags else []

            job_tags_set = set(job_tags)

            if job_tags_set & include_tags_set or (not job_tags and 'all' in include_tags_set):
                new_job = copy.deepcopy(job)

                # Apply bullet limit to highlights
                if 'highlights' in new_job:
                    new_job['highlights'] = apply_bullet_limit(
                        new_job['highlights'],
                        max_bullets
                    )

                filtered_work.append(new_job)

        filtered_data['work'] = filtered_work

    # Filter education
    if 'education' in filtered_data:
        filtered_data['education'] = filter_items(
            resume_data.get('education', []),
            include_tags
        )

    # Filter awards
    if 'awards' in filtered_data:
        filtered_data['awards'] = filter_items(
            resume_data.get('awards', []),
            include_tags
        )

    # Filter certifications
    if 'certifications' in filtered_data:
        filtered_data['certifications'] = filter_items(
            resume_data.get('certifications', []),
            include_tags
        )

    # Filter certificates (JSON Resume format)
    if 'certificates' in filtered_data:
        filtered_data['certificates'] = filter_items(
            resume_data.get('certificates', []),
            include_tags
        )

    # Filter specialty_skills
    if 'specialty_skills' in filtered_data:
        filtered_data['specialty_skills'] = filter_items(
            resume_data.get('specialty_skills', []),
            include_tags
        )

    # Filter skills (JSON Resume format)
    if 'skills' in filtered_data:
        filtered_data['skills'] = filter_items(
            resume_data.get('skills', []),
            include_tags
        )

    # Filter projects with bullet limits
    if 'projects' in filtered_data:
        filtered_data['projects'] = filter_projects(
            resume_data.get('projects', []),
            include_tags,
            max_bullets
        )

    # Keep basics, meta, languages, interests unchanged
    # (these typically don't have include_in tags)

    return filtered_data


def validate_profile(profile: dict) -> tuple[bool, list]:
    """Validate a profile configuration.

    Args:
        profile: Profile configuration dictionary.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []

    if not profile:
        errors.append("Profile is empty or None")
        return False, errors

    if not isinstance(profile, dict):
        errors.append("Profile must be a dictionary")
        return False, errors

    # Check for required sections
    if 'profile' not in profile:
        errors.append("Missing 'profile' section")
    else:
        profile_section = profile['profile']
        if not isinstance(profile_section, dict):
            errors.append("'profile' section must be a dictionary")
        else:
            if 'name' not in profile_section:
                errors.append("Missing 'profile.name'")

    # Check filters section
    if 'filters' in profile:
        filters = profile['filters']
        if not isinstance(filters, dict):
            errors.append("'filters' section must be a dictionary")
        else:
            if 'include_tags' in filters:
                include_tags = filters['include_tags']
                if not isinstance(include_tags, list):
                    errors.append("'filters.include_tags' must be a list")

            if 'max_bullets_per_job' in filters:
                max_bullets = filters['max_bullets_per_job']
                if max_bullets is not None and not isinstance(max_bullets, int):
                    errors.append("'filters.max_bullets_per_job' must be an integer or None")

    return len(errors) == 0, errors


def get_profile_info(profile: dict) -> dict:
    """Extract summary information from a profile.

    Args:
        profile: Profile configuration dictionary.

    Returns:
        Dictionary with profile summary info.
    """
    profile_section = profile.get('profile', {})
    filters = profile.get('filters', {})
    output = profile.get('output', {})

    return {
        'name': profile_section.get('name', 'Unknown'),
        'description': profile_section.get('description', ''),
        'slug': profile_section.get('slug', ''),
        'include_tags': filters.get('include_tags', ['all']),
        'max_bullets_per_job': filters.get('max_bullets_per_job'),
        'filename': output.get('filename', 'resume'),
        'title_suffix': output.get('title_suffix', '')
    }
