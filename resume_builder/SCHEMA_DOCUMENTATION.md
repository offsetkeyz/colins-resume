# Resume YAML Schema & Validation Documentation

This document provides comprehensive guidance on using the YAML-based resume system with profile filtering and validation.

## Table of Contents

1. [Overview](#overview)
2. [Schema Structure](#schema-structure)
3. [Include_in Tag System](#include_in-tag-system)
4. [Validation Tool](#validation-tool)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The YAML resume system allows you to maintain a single master resume that can generate multiple targeted versions using profile-based filtering. This is accomplished through the `include_in` tag system.

**Key Benefits:**
- Single source of truth for all resume content
- Generate multiple resume variations (leadership, technical, etc.)
- Comprehensive validation ensures data integrity
- Human-readable YAML format with comments

**Files:**
- `resume-schema.yaml` - Complete schema definition with documentation
- `validate_resume.py` - Python validation script
- `resume.yaml` - Your master resume file (to be created)

---

## Schema Structure

### Required Root Fields

Every resume must have a `basics` section:

```yaml
basics:
  name: "Your Name"
  email: "your.email@example.com"
```

### Optional Root Sections

All other sections are optional but follow standard resume format:

- `work_experience` - Professional work history
- `education` - Educational background
- `awards` - Awards and recognition
- `certifications` - Professional certifications
- `publications` - Published works
- `skills` - Simple skills list
- `specialty_skills` - Categorized skills with keywords
- `languages` - Spoken languages
- `interests` - Personal interests
- `references` - Professional references
- `projects` - Notable projects
- `volunteer` - Volunteer experience
- `meta` - Resume metadata

---

## Include_in Tag System

### What is include_in?

The `include_in` field allows you to tag resume items for different profiles. This enables one master resume to generate multiple targeted versions.

### Available Tags

- `all` - Include in all resume profiles (default)
- `leadership` - Leadership and management focused resumes
- `management` - People management emphasis
- `technical` - Technical and development focused resumes
- `development` - Software development emphasis
- `consulting` - Consulting-focused resumes
- `startup` - Startup environment resumes

### Usage Examples

#### Simple Usage - Entry Level

Tag an entire job entry:

```yaml
work_experience:
  "Arctic Wolf Networks":
    - job_title: "Team Lead - Security Developer"
      location: "Remote"
      start_date: "2024-03-01"
      end_date: "Present"
      responsibilities:
        - "Led team of 6 security analysts"
        - "Built automation framework"
      include_in: ["all"]  # This entire job appears in all profiles
```

#### Advanced Usage - Responsibility Level

Tag individual responsibilities:

```yaml
work_experience:
  "Arctic Wolf Networks":
    - job_title: "Team Lead - Security Developer"
      location: "Remote"
      start_date: "2024-03-01"
      end_date: "Present"
      responsibilities:
        # Simple string - appears in all profiles
        - "Collaborated with stakeholders on requirements"

        # Object with include_in - appears only in specified profiles
        - description: "Mentored 6 junior developers in Python best practices"
          include_in: ["leadership", "management"]

        - description: "Built automation framework using AWS Lambda and Python"
          include_in: ["technical", "development"]

        - description: "Presented at company-wide engineering meetings"
          include_in: ["leadership", "technical"]

      include_in: ["all"]  # Job itself appears everywhere
```

#### Project Highlights

Projects can have tagged highlights:

```yaml
projects:
  - name: "The Daily Decrypt"
    description: "Cybersecurity news podcast"
    startDate: "2024-01-01"
    endDate: "Present"
    highlights:
      # Simple strings appear in all profiles
      - "Launched podcast reaching 10k monthly listeners"

      # Tagged highlights appear only in specified profiles
      - description: "Built AWS infrastructure with Lightsail and CloudFront"
        include_in: ["technical", "development"]

      - description: "Managed team of 3 content creators"
        include_in: ["leadership", "management"]

    roles:
      - "Host"
      - "Technical Administrator"
    type: "Community Education"
    include_in: ["all"]
```

### Tagging Strategy

**Universal Items (include_in: [all]):**
- Core responsibilities everyone should see
- Fundamental job duties
- Key achievements relevant to all roles
- Basic contact information

**Leadership Items (include_in: [leadership, management]):**
- Team management and mentorship
- Strategic planning and decision making
- Stakeholder communication
- Process improvement and team building
- Hiring and performance management

**Technical Items (include_in: [technical, development]):**
- Software development and coding
- System architecture and design
- Technical problem solving
- Tools and technologies used
- Code review and technical documentation

**Mixed Tags:**
- Use multiple tags when an item is relevant to multiple profile types
- Example: `include_in: ["leadership", "technical"]` for "Led technical architecture review meetings"

---

## Validation Tool

### Installation

The validator requires Python 3.8+ and PyYAML:

```bash
# Install PyYAML if not already installed
pip install pyyaml

# Make validator executable
chmod +x validate_resume.py
```

### Basic Usage

```bash
# Validate a resume file
python validate_resume.py resume.yaml

# Verbose output with detailed information
python validate_resume.py resume.yaml --verbose

# Strict mode (treat warnings as errors)
python validate_resume.py resume.yaml --strict
```

### Exit Codes

- `0` - Validation passed (no errors or warnings)
- `1` - Validation failed with errors
- `2` - Validation passed but has warnings (only in --strict mode)

### What Does the Validator Check?

**Structure Validation:**
- Required fields are present
- Data types are correct (strings, arrays, objects)
- Field names are valid

**include_in Tag Validation:**
- Tags are in array format (not strings)
- Only allowed tags are used
- Arrays are not empty
- Warns if 'all' tag is mixed with other tags (redundant)

**Date Validation:**
- Dates match format: YYYY-MM-DD, YYYY-MM, YYYY, or "Present"
- Date values are logically valid

**Email Validation:**
- Valid email format (user@domain.com)

**URL Validation:**
- Valid HTTP/HTTPS URLs
- Proper format with protocol

**Field Requirements:**
- Each section has required fields
- Example: work experience needs job_title, location, start_date, end_date

### Example Validation Output

**Successful Validation:**
```
======================================================================
VALIDATION RESULTS
======================================================================

======================================================================
✓ VALIDATION PASSED - No issues found!

Summary: Errors: 0, Warnings: 0, Info: 0
======================================================================
```

**Failed Validation:**
```
======================================================================
VALIDATION RESULTS
======================================================================

✗ ERRORS (3):
  [ERROR] basics.email: Invalid email format: invalid-email
    → Suggestion: Use format: user@example.com

  [ERROR] work_experience.Company[0].start_date: Invalid date format: 2024-13-45
    → Suggestion: Use YYYY-MM-DD, YYYY-MM, YYYY, or 'Present'

  [ERROR] work_experience.Company[0].include_in: include_in must be an array, got str
    → Suggestion: Use include_in: [all] or include_in: [leadership, technical]

⚠ WARNINGS (1):
  [WARNING] projects[0].include_in: Tag 'all' is present with other tags
    → Suggestion: Consider using just include_in: [all]

======================================================================
✗ VALIDATION FAILED

Summary: Errors: 3, Warnings: 1, Info: 0
======================================================================
```

---

## Common Patterns

### Pattern 1: Universal Resume Entry

Use when an entire entry should appear in all profiles:

```yaml
education:
  - institution: "Auburn University"
    area: "Computer Science"
    studyType: "Bachelor's"
    startDate: "2020-01-01"
    endDate: "2021-11-01"
    honors: "Summa Cum Laude"
    include_in: ["all"]
```

### Pattern 2: Mixed Responsibilities

Use when you want different bullets for different profiles:

```yaml
work_experience:
  "Company Name":
    - job_title: "Team Lead"
      location: "Remote"
      start_date: "2023-01-01"
      end_date: "Present"
      responsibilities:
        # Everyone sees this
        - "Collaborated with cross-functional teams"

        # Only leadership profiles see this
        - description: "Mentored 5 junior engineers"
          include_in: ["leadership"]

        # Only technical profiles see this
        - description: "Architected microservices using Python and Kubernetes"
          include_in: ["technical"]

        # Both leadership and technical profiles see this
        - description: "Led technical design reviews"
          include_in: ["leadership", "technical"]

      include_in: ["all"]
```

### Pattern 3: Profile-Specific Job

Use when an entire job should only appear in certain profiles:

```yaml
work_experience:
  "Startup Company":
    - job_title: "Founding Engineer"
      location: "San Francisco, CA"
      start_date: "2019-01-01"
      end_date: "2020-12-01"
      responsibilities:
        - "Built MVP from scratch using React and Node.js"
        - "Managed AWS infrastructure"
      include_in: ["technical", "startup"]  # Only show for technical/startup roles
```

### Pattern 4: Projects with Filtered Highlights

Use when a project has both universal and profile-specific highlights:

```yaml
projects:
  - name: "Open Source Security Tool"
    description: "Popular security scanning tool with 5k GitHub stars"
    startDate: "2022-01-01"
    endDate: "Present"
    url: "https://github.com/user/project"
    highlights:
      # Universal highlights (strings)
      - "Maintained active open source project"
      - "Contributed to cybersecurity community"

      # Profile-specific highlights (objects)
      - description: "Wrote 10,000+ lines of Python code"
        include_in: ["technical", "development"]

      - description: "Built community of 50+ contributors"
        include_in: ["leadership", "management"]

    roles:
      - "Creator"
      - "Maintainer"
    type: "application"
    include_in: ["all"]
```

### Pattern 5: Skills by Profile

Categorize specialty skills by profile:

```yaml
specialty_skills:
  - name: "Leadership Skills"
    keywords:
      - "Team Management"
      - "Mentoring"
      - "Strategic Planning"
    include_in: ["leadership", "management"]

  - name: "Technical Skills"
    keywords:
      - "Python"
      - "AWS"
      - "Kubernetes"
    include_in: ["technical", "development"]

  - name: "Core Skills"
    keywords:
      - "Communication"
      - "Problem Solving"
    include_in: ["all"]
```

---

## Troubleshooting

### Common Errors

#### Error: "include_in must be an array, got str"

**Wrong:**
```yaml
include_in: "all"
```

**Correct:**
```yaml
include_in: ["all"]
```

---

#### Error: "include_in array cannot be empty"

**Wrong:**
```yaml
include_in: []
```

**Correct:**
```yaml
include_in: ["all"]
```

---

#### Error: "Invalid tags: custom-tag"

**Wrong:**
```yaml
include_in: ["custom-tag"]
```

**Correct:**
```yaml
include_in: ["leadership"]  # Use predefined tags
```

Available tags: all, leadership, management, technical, development, consulting, startup

---

#### Error: "Invalid date format"

**Wrong:**
```yaml
start_date: "01/15/2024"  # US date format
end_date: "2024-13-01"    # Invalid month
```

**Correct:**
```yaml
start_date: "2024-01-15"  # YYYY-MM-DD
end_date: "2024"          # YYYY (also valid)
endDate: "Present"        # Special value for current positions
```

---

#### Error: "Invalid email format"

**Wrong:**
```yaml
email: "john.doe"
```

**Correct:**
```yaml
email: "john.doe@example.com"
```

---

#### Error: "Invalid URL format"

**Wrong:**
```yaml
url: "github.com/user"
url: "www.example.com"
```

**Correct:**
```yaml
url: "https://github.com/user"
url: "https://www.example.com"
```

---

### Common Warnings

#### Warning: "Tag 'all' is present with other tags"

This is a warning, not an error. Your resume will still validate, but you're told that the 'all' tag makes other tags redundant.

**Current:**
```yaml
include_in: ["all", "leadership", "technical"]
```

**Recommendation:**
```yaml
include_in: ["all"]  # Simpler, same effect
```

**Or if you meant to be more specific:**
```yaml
include_in: ["leadership", "technical"]  # Remove 'all'
```

---

### Debugging Tips

1. **Use --verbose flag:**
   ```bash
   python validate_resume.py resume.yaml --verbose
   ```

2. **Check line numbers:**
   Error messages include the field path to help locate issues:
   ```
   [ERROR] work_experience.Company[0].start_date: Invalid date
   ```
   This means: In work_experience → Company → first position [0] → start_date

3. **Validate early and often:**
   Run validation after making changes, don't wait until you're done

4. **Start simple:**
   Begin with a minimal resume and add sections gradually, validating at each step

5. **Use examples from schema:**
   The `resume-schema.yaml` file contains extensive examples in the comments

---

## Integration with Profile System

### How Profiles Use include_in Tags

When generating a resume with a specific profile (e.g., "leadership"):

1. **Profile loads** and specifies which tags to include
2. **Filter applies** to resume data
3. **Items are included** if they have matching tags
4. **Output is generated** with filtered content

### Profile Configuration Example

```yaml
# profiles/leadership.yaml
profile:
  name: "Leadership Focused"
  slug: "leadership"

filters:
  include_tags: ["leadership", "management", "all"]
  max_bullets_per_job: 4

output:
  title_suffix: " - Leadership Focus"
  filename: "resume-leadership"
```

### What Gets Included

Given the profile above:
- Items tagged with `["all"]` → **Included**
- Items tagged with `["leadership"]` → **Included**
- Items tagged with `["management"]` → **Included**
- Items tagged with `["technical"]` → **Excluded**
- Items tagged with `["leadership", "technical"]` → **Included** (has matching tag)

---

## Best Practices

### 1. Start with 'all'

When migrating, tag everything with `["all"]` first:

```yaml
include_in: ["all"]
```

### 2. Add Specific Tags Gradually

Once the system works, refine tags for specific items:

```yaml
- description: "Mentored team members"
  include_in: ["leadership", "management"]
```

### 3. Keep It Simple

Don't over-complicate tagging. Most items should use:
- `["all"]` - Universal
- `["leadership"]` - Leadership only
- `["technical"]` - Technical only

### 4. Test Your Changes

Always validate after making changes:

```bash
python validate_resume.py resume.yaml
```

### 5. Use Comments

YAML supports comments, use them:

```yaml
responsibilities:
  # Leadership-focused achievements
  - description: "Mentored 5 developers"
    include_in: ["leadership"]

  # Technical achievements
  - description: "Built CI/CD pipeline"
    include_in: ["technical"]
```

### 6. Maintain Consistency

Use the same tag combinations throughout your resume:
- `["leadership", "management"]` for people-focused items
- `["technical", "development"]` for code-focused items

---

## Next Steps

1. **Create resume.yaml** - Convert your existing resume to YAML format
2. **Add include_in tags** - Start with `["all"]` for everything
3. **Validate** - Run `python validate_resume.py resume.yaml`
4. **Refine tags** - Add specific profile tags as needed
5. **Create profiles** - Define leadership, technical, etc. profiles
6. **Generate resumes** - Use profile manager to create targeted versions

---

## Additional Resources

- `resume-schema.yaml` - Complete schema with all field definitions
- `validate_resume.py` - Source code for validator
- Task 1.3 in TASK_LIST.md - Profile system documentation
- Task 1.4 in TASK_LIST.md - Profile manager implementation

---

## Support

For issues or questions:
1. Check this documentation first
2. Review examples in `resume-schema.yaml`
3. Run validator with `--verbose` flag
4. Check TASK_LIST.md for project context

---

**Version:** 1.0.0
**Last Updated:** 2025-11-21
**Compatible with:** Dynamic YAML-Based Resume System
