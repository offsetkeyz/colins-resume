#!/usr/bin/env python3
"""
JSON Generator for Resume Builder

This module generates JSON resume files from YAML data with profile filtering support.
It follows the same patterns as md_generator.py for consistency.

Purpose:
- Used for future dynamic website loading
- API endpoint data source
- Alternative output format

Usage:
    python json_generator.py                    # Generate with default profile
    python json_generator.py -p technical       # Generate with technical profile
    python json_generator.py -l                 # List available profiles
    python json_generator.py --all-profiles     # Generate for all profiles
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

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


def clean_resume_data(resume_data):
    """Clean resume data by removing internal fields like include_in tags.

    This prepares the data for JSON export by removing fields that are only
    used for internal profile filtering.

    Args:
        resume_data: Dictionary containing resume data.

    Returns:
        Cleaned dictionary ready for JSON export.
    """
    if resume_data is None:
        return None

    import copy
    cleaned = copy.deepcopy(resume_data)

    def remove_include_in(obj):
        """Recursively remove include_in fields from an object."""
        if isinstance(obj, dict):
            # Remove include_in key if present
            obj.pop('include_in', None)
            # Recursively process nested objects
            for key, value in obj.items():
                remove_include_in(value)
        elif isinstance(obj, list):
            for item in obj:
                remove_include_in(item)

    remove_include_in(cleaned)
    return cleaned


def add_metadata(resume_data, profile_info=None):
    """Add export metadata to the resume data.

    Args:
        resume_data: Dictionary containing resume data.
        profile_info: Optional profile info dictionary.

    Returns:
        Dictionary with added metadata.
    """
    if resume_data is None:
        return None

    import copy
    data_with_meta = copy.deepcopy(resume_data)

    # Create or update export_meta section
    export_meta = {
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'generator': 'resume_builder/json_generator.py',
        'format_version': '1.0'
    }

    if profile_info:
        export_meta['profile'] = {
            'name': profile_info.get('name', 'Unknown'),
            'slug': profile_info.get('slug', ''),
            'description': profile_info.get('description', '')
        }

    data_with_meta['export_meta'] = export_meta

    return data_with_meta


def generate_json(resume_data, profile_info=None, indent=2, include_metadata=True):
    """Generate JSON string from resume data.

    Args:
        resume_data: Dictionary containing resume data.
        profile_info: Optional profile info dictionary for customization.
        indent: Indentation level for JSON output (default: 2).
        include_metadata: Whether to include export metadata (default: True).

    Returns:
        JSON string, or None if no data provided.
    """
    if resume_data is None:
        return None

    # Clean the data (remove internal fields like include_in)
    cleaned_data = clean_resume_data(resume_data)

    # Add metadata if requested
    if include_metadata:
        cleaned_data = add_metadata(cleaned_data, profile_info)

    try:
        return json.dumps(cleaned_data, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        print(f"Error generating JSON: {e}")
        return None


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate JSON resume from YAML data with profile filtering.'
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
        help='Path to output JSON file (default: based on profile name)'
    )
    parser.add_argument(
        '-l', '--list-profiles',
        action='store_true',
        help='List available profiles and exit'
    )
    parser.add_argument(
        '--all-profiles',
        action='store_true',
        help='Generate JSON for all available profiles'
    )
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Exclude export metadata from JSON output'
    )
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Output compact JSON without indentation'
    )
    parser.add_argument(
        '--output-dir',
        default=None,
        help='Output directory for generated JSON files (default: output/)'
    )
    return parser.parse_args()


def get_output_path(profile_info, output_arg=None, output_dir=None):
    """Determine the output path for the JSON file.

    Args:
        profile_info: Profile information dictionary.
        output_arg: Optional output path from command line.
        output_dir: Optional output directory.

    Returns:
        Path object for the output file.
    """
    if output_arg:
        return Path(output_arg)

    # Use output directory (default to 'output' in project root)
    if output_dir:
        base_dir = Path(output_dir)
    else:
        base_dir = Path(__file__).parent.parent / 'output'

    # Ensure output directory exists
    base_dir.mkdir(parents=True, exist_ok=True)

    # Use profile filename if available
    if profile_info and profile_info.get('filename'):
        filename = profile_info['filename']
        return base_dir / f'{filename}.json'
    else:
        return base_dir / 'resume.json'


def generate_for_profile(profile_name, input_path=None, output_path=None,
                         output_dir=None, verbose=True, include_metadata=True,
                         compact=False):
    """Generate JSON for a specific profile.

    Args:
        profile_name: Name of the profile to use.
        input_path: Optional path to input YAML file.
        output_path: Optional path to output JSON file.
        output_dir: Optional output directory.
        verbose: Whether to print status messages.
        include_metadata: Whether to include export metadata.
        compact: Whether to output compact JSON.

    Returns:
        True if successful, False otherwise.
    """
    if verbose:
        print(f"Generating JSON for profile: {profile_name}")

    # Load and filter resume data
    resume_data, profile_info = load_resume_data(input_path, profile_name)
    if resume_data is None:
        print(f"Failed to load resume data for profile: {profile_name}")
        return False

    # Generate JSON
    indent = None if compact else 2
    json_content = generate_json(resume_data, profile_info, indent=indent,
                                  include_metadata=include_metadata)
    if json_content is None:
        print(f"Failed to generate JSON for profile: {profile_name}")
        return False

    # Determine output path
    final_output = get_output_path(profile_info, output_path, output_dir)

    # Write the JSON file
    try:
        with open(final_output, 'w', encoding='utf-8') as f:
            f.write(json_content)
        if verbose:
            print(f"Successfully wrote JSON to: {final_output}")
        return True
    except Exception as e:
        print(f"Error writing JSON file: {e}")
        return False


def get_resume_as_dict(profile_name='default', data_path=None,
                       include_metadata=True, clean_internal_fields=True):
    """Get resume data as a Python dictionary (useful for API integration).

    Args:
        profile_name: Name of the profile to use for filtering.
        data_path: Optional path to input YAML file.
        include_metadata: Whether to include export metadata.
        clean_internal_fields: Whether to remove internal fields like include_in.

    Returns:
        Dictionary containing the resume data, or None if an error occurs.
    """
    resume_data, profile_info = load_resume_data(data_path, profile_name)
    if resume_data is None:
        return None

    if clean_internal_fields:
        resume_data = clean_resume_data(resume_data)

    if include_metadata:
        resume_data = add_metadata(resume_data, profile_info)

    return resume_data


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
            if generate_for_profile(
                profile_name,
                args.input,
                output_dir=args.output_dir,
                include_metadata=not args.no_metadata,
                compact=args.compact
            ):
                success_count += 1
        print(f"\nGenerated {success_count}/{len(profiles)} JSON files successfully.")
        sys.exit(0 if success_count == len(profiles) else 1)

    # Generate for single profile
    success = generate_for_profile(
        args.profile,
        args.input,
        args.output,
        output_dir=args.output_dir,
        include_metadata=not args.no_metadata,
        compact=args.compact
    )
    sys.exit(0 if success else 1)
