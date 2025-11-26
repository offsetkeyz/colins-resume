import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml
import json
import re

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
# Deprecated JSON Loading Function (kept for backward compatibility)
# =============================================================================
def read_json_file(file_path):
    """Read and parse a JSON file.

    Deprecated in favor of YAML, but retained for compatibility with tests and
    tooling that may still call it.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Dictionary containing the JSON data, or None if an error occurs.
    """
    try:
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON. Please ensure the file is a valid JSON format.")
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
def generate_header(basics, title_suffix='', extra_styles=''):
    f_name = basics['name'].split(' ')[0]
    suffix = title_suffix if title_suffix else ''
    return f'''<head>
    <title>{f_name}\'s Resume{suffix}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{basics.get('name')}\'s Digital Resume{suffix}">
    <meta name="author" content="{basics.get('name')}">
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="stylesheet" href="css/kube.min.css" />
    <link rel="stylesheet" href="css/font-awesome.min.css" />
    <link rel="stylesheet" href="css/custom.min.css" />
    <link rel="shortcut icon" href="img/favicon.ico" />
	<link href='https://fonts.googleapis.com/css?family=Playfair+Display+SC:700' rel='stylesheet' type='text/css'>
	<link href='https://fonts.googleapis.com/css?family=Lato:400,700' rel='stylesheet' type='text/css'>
	<style>
		.intro h1:before {{
			content: "{f_name}";
		}}
	</style>
    {extra_styles}
</head>'''

def generate_navigation(json_data):
	def generate_header_list(json_keys):
		header_list = '''<li class="active"><a href="#about">About</a></li>
  <li><a href="#experiences">Experiences</a></li>
  <li><a href="#education">Education</a></li>'''
		for key in json_keys:
			if key in ['publications','projects']:
				key = key.replace('_', ' ')
				header_list += f'<li><a href=\"#{key}\">{key.title()}</a></li>'
		header_list += '''<li><a href="/resume.pdf" target="_blank">Download Resume</a></li>'''
		return header_list

	f_name = json_data.get('basics').get('name').split(' ')[0]
	return f'''<!-- Navigation -->
	<div class="main-nav">
		<div class="container">
			<header class="group top-nav">
				<div class="navigation-toggle" data-tools="navigation-toggle" data-target="#navbar-1">
				    <span class="logo">{f_name.upper()}</span>
				</div>
			    <nav id="navbar-1" class="navbar item-nav">
				    <ul>
				        {generate_header_list(json_data.keys())}
				    </ul>
				</nav>
			</header>
		</div>
	</div>'''

def generate_introduction(basics):
	markup = f'''<!-- Introduction -->
	<div class="intro section" id="about">
		<div class="container">
			<p>Hi, I’m {basics['name'].split(' ')[0]}</p>
			<div class="units-row units-split wrap">
				<div class="unit-20">
					<img src="{basics.get('image')}" alt="Avatar">
				</div>
			  <div class="unit-80">
					<h1>My passions are<br><span id="typed"></span></h1>
				</div>
			  <p>{basics['summary']}</p>
			</div>
		</div>
	</div>'''
	return markup

def slugify_company(name):
    """Create a filesystem-friendly slug for a company name."""
    if not name:
        return 'company'
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug or 'company'


def get_company_filename(company_slug, profile_info=None):
    """Build the filename for a company detail page."""
    if profile_info:
        profile_slug = profile_info.get('slug')
        if profile_slug and profile_slug != 'default':
            return f"company-{company_slug}-{profile_slug}.html"
    return f"company-{company_slug}.html"


def render_profile_links(profiles):
    """Render social/profile icon links."""
    if not profiles:
        return ''
    links = []
    for profile in profiles:
        icon = profile.get('icon')
        if not icon:
            network = profile.get('network', '').lower()
            icon = f'fa fa-{network}-square' if network else 'fa fa-link'
        links.append(f'''<li><a href="{profile.get('url')}" target="_blank"><i class="{icon}"></i></a></li>''')
    return ''.join(links)


def generate_work_experience(work_experience, profile_info=None):
    if not work_experience:
        return ''
    markup = '''<!-- Work Experience / Volunteer --><div class="work section second" id="experiences">
 	<div class="container">
		<h1>Work<br>Experiences</h1>'''
    for company, experiences in work_experience.items():
        company_slug = slugify_company(company)
        company_href = get_company_filename(company_slug, profile_info)
        markup += f'''<ul class="work-list">
			<li><a href="{company_href}">{company}</a></li>'''
        for experience in experiences:
            markup += f'<li><a href="{company_href}">{experience.get("job_title")}</a></li>'
        markup += "</ul>"
    markup += "</div></div>"  
    return markup


def format_role_meta(position):
    """Format the date range and location string for a position."""
    start = position.get('start_date') or position.get('startDate')
    end = position.get('end_date') or position.get('endDate')
    start_fmt = s.get_month_and_year(start) if start else ''
    end_fmt = s.get_month_and_year(end) if end else ''

    date_part = f"{start_fmt} - {end_fmt}" if start_fmt or end_fmt else ''
    location = position.get('location', '')

    if date_part and location:
        return f"{date_part} | {location}"
    return date_part or location


def generate_company_detail_page(company, positions, resume_data, profile_info=None, home_href='index.html'):
    """Generate a standalone company detail page."""
    basics = resume_data.get('basics', {})
    detail_title = f" - {company}"
    home_link = home_href
    detail_styles = '''
    <style>
        .experience-card {
            margin-bottom: 40px;
            padding: 25px;
            border: 1px solid #e5e5e5;
            border-radius: 6px;
            background: #fff;
        }
        .experience-card h2 {
            margin-bottom: 6px;
        }
        .experience-meta {
            color: #8c8c8c;
            font-size: 0.95em;
            margin-bottom: 12px;
        }
        .back-link {
            display: inline-block;
            margin-top: 8px;
            font-weight: 700;
        }
    </style>
    '''

    experience_cards = ''
    for position in positions:
        meta = format_role_meta(position)
        responsibilities = position.get('responsibilities', []) or []
        responsibility_items = ''.join(f"<li>{resp}</li>" for resp in responsibilities)
        experience_cards += f'''
            <div class="experience-card">
                <h2>{position.get('job_title')}</h2>
                <div class="experience-meta">{meta}</div>
                <ul>
                    {responsibility_items}
                </ul>
            </div>'''

    return f'''<!DOCTYPE html>
<html>
{generate_header(basics, title_suffix=detail_title, extra_styles=detail_styles)}
<body>
	<div class="main-nav">
		<div class="container">
			<header class="group top-nav">
				<div class="navigation-toggle" data-tools="navigation-toggle" data-target="#navbar-1">
				    <span class="logo">{basics.get('name','').split(' ')[0].upper()}</span>
				</div>
			    <nav id="navbar-1" class="navbar item-nav">
				    <ul>
				        <li><a href="{home_link}#about">Home</a></li>
                        <li class="active"><a href="#">{company}</a></li>
                        <li><a href="{home_link}#experiences">All Experiences</a></li>
				        <li><a href="/resume.pdf" target="_blank">Download Resume</a></li>
				    </ul>
				</nav>
			</header>
		</div>
	</div>

	<div class="intro section" id="about">
		<div class="container">
			<p>Company Spotlight</p>
			<div class="units-row units-split wrap">
			  <div class="unit-100">
					<h1>{company}</h1>
				</div>
			  <p>{basics.get('summary','')}</p>
              <a class="back-link" href="{home_link}#experiences">&larr; Back to main resume</a>
			</div>
		</div>
	</div>

	<div class="work section second" id="experiences">
 	    <div class="container">
		    <h1>Roles &amp; Impact</h1>
            {experience_cards}
        </div>
    </div>

	<footer>
		<div class="container">
			<div class="units-row">
			    <div class="unit-50">
			    	<p>{basics.get('name')}</p>
			    </div>
			    <div class="unit-50">
					<ul class="social list-flat right">''' + render_profile_links(basics.get('profiles', [])) + '''</ul>
			    </div>
			</div>
		</div>
	</footer>

	<script src="js/jquery.min.js"></script>
    <script src="js/kube.min.js"></script>
    <script src="js/site.js"></script>
</body>
</html>'''


def generate_company_pages(resume_data, profile_info=None, home_href='index.html'):
    """Create HTML pages for each company in work_experience."""
    work_experience = resume_data.get('work_experience') if resume_data else None
    if not work_experience:
        return {}

    company_pages = {}
    for company, positions in work_experience.items():
        slug = slugify_company(company)
        filename = get_company_filename(slug, profile_info)
        company_pages[filename] = generate_company_detail_page(
            company,
            positions,
            resume_data,
            profile_info=profile_info,
            home_href=home_href
        )
    return company_pages

def generate_education_and_certs(education=None, certifications=None, awards=None):
	if not certifications and not education and not awards:
		return ''
	if certifications:
		markup = '''<!-- Certifications --><div class="certifications section second" id="education">
		<div class="container">
			<h1>CERTIFICATIONS &amp;<br>Education<br></h1>
				<ul class="award-list list-flat"><li>Certifications</li>'''
		for certification in certifications:
			display_name = certification.get('title')  # show full name on website
			if certification.get('url', None):
				title = f'''<a href="{certification.get('url')}" target="_blank">{display_name}</a>'''
			else:
				title = f"{display_name}"
			markup += f"<li>&#8226; {title}</li>"
		markup += '''</ul>'''
	elif education:
		markup = '''<!-- Education --><div class="education section second" id="education">
		<div class="container">
			<h1>Education<br></h1>'''
	markup += '''<ul class="award-list list-flat">
<li>Education</li>'''
	for school in education:
		url = school.get('url', None)
		honors = school.get('honors', None)
		gpa = school.get('score', None)
		markup += f"<li><b>{school.get('studyType')} in {school.get('area')}</b></li>"
		if url:    
			markup += f'''<li><a href={url} target="_blank">{school.get('institution')}</a></li>'''
		else: 
			markup += f"<li><b>{school.get('institution')}</b></li>"
		if honors:
			markup += f"<li>{honors}</li>"
		elif gpa:
			markup += f"<li>GPA: {gpa}</li>"
		markup += f"<li><i>{s.get_month_and_year(school.get('startDate'))} - {s.get_month_and_year(school.get('endDate'))}</i></li>"
		if school != education[-1]:
			markup += "<br>"
	markup += "</ul>"
	if awards:
		markup += '''<ul class="award-list list-flat"><li>Awards</li>'''
		for award in awards:
			markup += f"<li><b>{award.get('title')}</b> | {award.get('awarder')} | <i>{s.get_month_and_year(award.get('date'))}</i></li>"
	markup += "</ul></div></div>"
	return markup

def generate_skills(skills, specialty_skills):
	markup = '''<!-- Technical Skills -->
	<div class="skills section second" id="skills">
		<div class="container">
  			<h1>Technical<br>Skills</h1>'''
	if specialty_skills:		
		for skill in specialty_skills:
			markup += '''<ul class="skill-list list-flat">\n'''
			markup += f"<li>{skill.get('name')}</li>\n"
			markup += f"<li>{' / '.join(skill.get('keywords'))}</li>\n"
			markup += "</ul>\n"
	if skills:
		markup += '''<ul class="skill-list list-flat">\n<li>'''
		for sk in skills:
			markup += f'''<code>{sk}</code>'''
	markup += "</li></ul></div></div>"
	return markup

def generate_projects(projects):
    if not projects:
        return ''
    markup = '''<!-- Projects -->
    <div class="projects section second" id="projects">
 	<div class="container">
  <h1>Projects</h1>'''
    for project in projects:
        project_url = (project.get('url',None))
        markup += (f'''<b><a href="{project_url}" target="_blank">{project['name']}</a></b>''') if project_url else f"<b>{project['name']}</b>" 
        markup += f" ({s.get_month_and_year(project['startDate'])})"
        markup += f'''<br><i>{project.get('description', None)}</i>'''
        markup += '''<ul class="project-list">'''
        for highlight in project.get('highlights', None):
            markup += f"<li>{highlight}</li>"
        markup += '<br></ul>'
    markup += "</div></div>"
    return markup

def generate_quote(basics):
	if not basics.get('quote',None):
		return ''
	return f'''<!-- Quote -->
	<div class="quote">
		<div class="container text-centered">
			<h1>{basics.get('quote')}</h1>
		</div>
	</div>'''

def generate_footer(json_data):
    name = json_data.get('basics').get('name')
    return f'''<footer>
		<div class="container">
			<div class="units-row">
			    <div class="unit-50">
			    	<p>{name}</p>
			    </div>
			    <div class="unit-50">
					<ul class="social list-flat right">{render_profile_links(json_data.get('basics').get('profiles', None))}</ul>
			    </div>
			</div>
		</div>
	</footer>'''
 
def generate_javascript(json_data):
    s = '''<!-- Javascript -->
	<script src="js/jquery.min.js"></script>
	<script src="js/typed.min.js"></script>
    <script src="js/kube.min.js"></script>
    <script src="js/site.js"></script>
    <script>
		function newTyped(){}$(function(){$("#typed").typed({
		// Change to edit type effect
		strings: ['''
    for interest in json_data.get('interests', None):
        s += f'''"{interest.get('name')}",'''
    s += '],'
    s += '''typeSpeed:89,backDelay:700,contentType:"html",loop:!0,resetCallback:function(){newTyped()}}),$(".reset").click(function(){$("#typed").typed("reset")})});
    </script>'''
    return s

def generate_html(resume_data, profile_info=None):
    """Generate HTML markup from resume data.

    Args:
        resume_data: Dictionary containing resume data.
        profile_info: Optional profile info dictionary for customization.

    Returns:
        HTML markup string.
    """
    if resume_data is None:
        return None

    markup = f'''<!DOCTYPE html>
<html>
{generate_header(resume_data.get('basics'), title_suffix=profile_info.get('title_suffix', '') if profile_info else '')}
<body>
	{generate_navigation(resume_data)}
	{generate_introduction(resume_data.get('basics'))}
	{generate_work_experience(resume_data.get('work_experience'), profile_info)}
	{generate_education_and_certs(resume_data.get('education', None), resume_data.get('certifications', None), resume_data.get('awards', None))}
	{generate_skills(resume_data.get('skills', None), resume_data.get('specialty_skills', None))}
 	{generate_projects(resume_data.get('projects', None))}
	{generate_quote(resume_data.get('basics'))}
	{generate_footer(resume_data)}
	{generate_javascript(resume_data)}
</body>
</html>
'''
    return markup


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate HTML resume from YAML data with profile filtering.'
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
        help='Path to output HTML file (default: ../index.html or based on profile)'
    )
    parser.add_argument(
        '-l', '--list-profiles',
        action='store_true',
        help='List available profiles and exit'
    )
    parser.add_argument(
        '--all-profiles',
        action='store_true',
        help='Generate HTML for all available profiles'
    )
    return parser.parse_args()


def get_output_path(profile_info, output_arg=None):
    """Determine the output path for the HTML file.

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
            return script_dir.parent / 'index.html'
        else:
            return script_dir.parent / f'{filename}.html'
    else:
        return script_dir.parent / 'index.html'


def generate_for_profile(profile_name, input_path=None, output_path=None, verbose=True):
    """Generate HTML for a specific profile.

    Args:
        profile_name: Name of the profile to use.
        input_path: Optional path to input YAML file.
        output_path: Optional path to output HTML file.
        verbose: Whether to print status messages.

    Returns:
        True if successful, False otherwise.
    """
    if verbose:
        print(f"Generating HTML for profile: {profile_name}")

    # Load and filter resume data
    resume_data, profile_info = load_resume_data(input_path, profile_name)
    if resume_data is None:
        print(f"Failed to load resume data for profile: {profile_name}")
        return False

    # Generate HTML
    html_content = generate_html(resume_data, profile_info)
    if html_content is None:
        print(f"Failed to generate HTML for profile: {profile_name}")
        return False

    # Determine output path
    final_output = get_output_path(profile_info, output_path)

    # Write the HTML file
    try:
        with open(final_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        if verbose:
            print(f"Successfully wrote HTML to: {final_output}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        return False

    # Write per-company detail pages
    home_href = final_output.name
    company_pages = generate_company_pages(resume_data, profile_info, home_href=home_href)
    output_root = final_output.parent

    try:
        for filename, page_html in company_pages.items():
            page_path = output_root / filename
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(page_html)
            if verbose:
                print(f"  - Wrote company page: {page_path.name}")
    except Exception as e:
        print(f"Error writing company page: {e}")
        return False

    return True


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
        print(f"\nGenerated {success_count}/{len(profiles)} HTML files successfully.")
        sys.exit(0 if success_count == len(profiles) else 1)

    # Generate for single profile
    success = generate_for_profile(args.profile, args.input, args.output)
    sys.exit(0 if success else 1)
