# Profile Creation Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-21
**Compatible with:** Dynamic YAML-Based Resume System

---

## Table of Contents

1. [Overview](#overview)
2. [What Are Profiles?](#what-are-profiles)
3. [Profile Structure](#profile-structure)
4. [Creating New Profiles](#creating-new-profiles)
5. [Available Options](#available-options)
6. [Example Profiles](#example-profiles)
7. [How Profiles Filter Content](#how-profiles-filter-content)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The profile system allows you to maintain a single master resume (`resume.yaml`) and generate multiple targeted versions by filtering content based on tags. Each profile defines which content to include, how to format it, and where to output it.

**Key Benefits:**
- One master resume, multiple targeted versions
- Consistent formatting across all variations
- Easy to maintain and update
- Automatic filtering based on tags
- Custom output configurations per profile

**Location:**
- Profiles are stored in: `/resume_builder/profiles/`
- Master resume: `/resume_builder/resume.yaml`
- Profile manager: `/resume_builder/profile_manager.py`

---

## What Are Profiles?

A profile is a YAML configuration file that defines:

1. **Profile Metadata** - Name, description, and slug
2. **Filters** - Which content to include (via tags)
3. **Output Settings** - Filename and title modifications

**Use Cases:**
- Generate a leadership-focused resume for management positions
- Create a technical resume emphasizing coding and system design
- Build a consulting resume highlighting client work
- Produce a startup-focused resume showing entrepreneurial experience

---

## Profile Structure

Every profile YAML file has three main sections:

### Basic Structure

```yaml
profile:
  name: "Profile Display Name"
  description: "What this profile emphasizes"
  slug: "profile-identifier"

filters:
  include_tags: [tag1, tag2, all]
  max_bullets_per_job: 4  # Optional

output:
  title_suffix: " - Focus Area"
  filename: "resume-variant"
```

### Section Breakdown

#### 1. Profile Metadata

```yaml
profile:
  name: "Leadership Focused"        # Human-readable name
  description: "Emphasizes people management and team leadership"
  slug: "leadership"                # Used in commands/URLs
```

- **name**: Display name shown in documentation and logs
- **description**: Brief explanation of profile's focus
- **slug**: Short identifier (lowercase, no spaces)

#### 2. Filters

```yaml
filters:
  include_tags: [leadership, management, all]
  max_bullets_per_job: 4
```

- **include_tags**: Array of tags to include from resume content
  - Items with ANY matching tag will be included
  - Always include `all` to get universal content
  - See [Tag System](#available-tags) for valid tags

- **max_bullets_per_job**: (Optional) Limit responsibility bullets
  - Keeps resumes concise (1-2 pages)
  - Applied after tag filtering
  - Omit to include all bullets

#### 3. Output Settings

```yaml
output:
  title_suffix: " - Leadership Focus"
  filename: "resume-leadership"
```

- **title_suffix**: Added to resume title (e.g., "John Doe - Leadership Focus")
- **filename**: Base filename for generated files
  - HTML: `{filename}.html`
  - PDF: `{filename}.pdf`
  - JSON: `{filename}.json`

---

## Creating New Profiles

### Step 1: Choose a Focus Area

Decide what aspect of your experience to emphasize:
- Leadership/Management
- Technical/Development
- Consulting/Advisory
- Startup/Entrepreneurial
- Industry-specific (healthcare, finance, etc.)

### Step 2: Create Profile File

Create a new YAML file in `/resume_builder/profiles/`:

```bash
# Navigate to profiles directory
cd /home/user/colins-resume/resume_builder/profiles/

# Create new profile file
touch consulting.yaml
```

### Step 3: Define Profile Configuration

```yaml
profile:
  name: "Consulting Focused"
  description: "Emphasizes client work and advisory experience"
  slug: "consulting"

filters:
  include_tags: [consulting, all]
  max_bullets_per_job: 3

output:
  title_suffix: " - Consulting Focus"
  filename: "resume-consulting"
```

### Step 4: Validate Profile

Test that the profile loads correctly:

```bash
# Validate profile structure
python resume_builder/profile_manager.py --validate consulting

# Test build with new profile
./build_all.sh --profile consulting
```

### Step 5: Tag Resume Content

Ensure your `resume.yaml` has content tagged appropriately:

```yaml
work_experience:
  "Acme Consulting":
    - job_title: "Senior Consultant"
      # ... other fields ...
      responsibilities:
        - description: "Advised Fortune 500 clients on security strategy"
          include_in: [consulting, leadership, all]

        - description: "Conducted security assessments for healthcare clients"
          include_in: [consulting, all]

      include_in: [consulting, all]
```

---

## Available Options

### Profile Metadata Options

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| name | Yes | String | Human-readable profile name | "Leadership Focused" |
| description | Yes | String | Brief explanation of focus | "Emphasizes team management" |
| slug | Yes | String | Identifier (lowercase, no spaces) | "leadership" |

### Filter Options

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| include_tags | Yes | Array | Tags to include in output | [leadership, all] |
| max_bullets_per_job | No | Integer | Limit bullets per job | 4 |
| exclude_sections | No | Array | Sections to exclude entirely | [volunteer, interests] |
| date_range | No | Object | Filter by date (future feature) | See below |

#### Available Tags

Standard tags available in the system:

- `all` - Universal content (appears in all profiles)
- `leadership` - Leadership and management focus
- `management` - People management emphasis
- `technical` - Technical skills and development
- `development` - Software development emphasis
- `consulting` - Consulting and advisory work
- `startup` - Startup environment experience

**Custom Tags:**
You can define custom tags in your `resume.yaml`, but ensure they're documented and used consistently.

### Output Options

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| title_suffix | No | String | Added to resume title | " - Leadership Focus" |
| filename | Yes | String | Base filename for outputs | "resume-leadership" |
| format | No | Array | Output formats (future) | [html, pdf, json] |

---

## Example Profiles

### Example 1: Default Profile

**File:** `profiles/default.yaml`

```yaml
profile:
  name: "Full Resume"
  description: "Complete resume with all experience"
  slug: "default"

filters:
  include_tags: [all]

output:
  title_suffix: ""
  filename: "resume"
```

**Use Case:** General applications where you want to show everything

**Result:** All content tagged with `[all]` or any other tag combination

---

### Example 2: Leadership Profile

**File:** `profiles/leadership.yaml`

```yaml
profile:
  name: "Leadership Focused"
  description: "Emphasizes people management and team leadership"
  slug: "leadership"

filters:
  include_tags: [leadership, management, all]
  max_bullets_per_job: 4

output:
  title_suffix: " - Leadership Focus"
  filename: "resume-leadership"
```

**Use Case:** Management positions, team lead roles, director positions

**Result:** Shows leadership achievements, team management, strategic planning

**Example Content Included:**
- "Led team of 6 security analysts" ✓
- "Mentored junior developers" ✓
- "Defined strategic roadmap" ✓
- "Built CI/CD pipeline" ✗ (technical-only tag)

---

### Example 3: Technical Profile

**File:** `profiles/technical.yaml`

```yaml
profile:
  name: "Technical Focused"
  description: "Emphasizes technical skills and development"
  slug: "technical"

filters:
  include_tags: [technical, development, all]
  max_bullets_per_job: 4

output:
  title_suffix: " - Technical Focus"
  filename: "resume-technical"
```

**Use Case:** Software engineering roles, architect positions, technical specialist roles

**Result:** Shows technical accomplishments, coding projects, system design

**Example Content Included:**
- "Built microservices architecture" ✓
- "Wrote Python automation framework" ✓
- "Optimized database queries" ✓
- "Managed team of developers" ✗ (leadership-only tag)

---

### Example 4: Consulting Profile

**File:** `profiles/consulting.yaml` (custom)

```yaml
profile:
  name: "Consulting Focused"
  description: "Emphasizes client work and advisory experience"
  slug: "consulting"

filters:
  include_tags: [consulting, leadership, all]
  max_bullets_per_job: 3

output:
  title_suffix: " - Consulting Experience"
  filename: "resume-consulting"
```

**Use Case:** Consulting firm applications, advisory roles, client-facing positions

**Result:** Shows client work, advisory experience, stakeholder management

---

### Example 5: Startup Profile

**File:** `profiles/startup.yaml` (custom)

```yaml
profile:
  name: "Startup Focused"
  description: "Emphasizes startup experience and entrepreneurial skills"
  slug: "startup"

filters:
  include_tags: [startup, technical, leadership, all]
  max_bullets_per_job: 5

output:
  title_suffix: " - Startup Experience"
  filename: "resume-startup"
```

**Use Case:** Startup applications, early-stage companies, entrepreneurial roles

**Result:** Shows versatility, multiple hats, rapid execution, building from scratch

---

## How Profiles Filter Content

### Filtering Logic

The profile manager applies filters in this order:

1. **Tag Matching**
   - Loads profile's `include_tags` array
   - Checks each resume item's `include_in` tags
   - Includes item if ANY tag matches

2. **Bullet Limiting**
   - If `max_bullets_per_job` is set
   - Applies limit to responsibility lists
   - Keeps first N bullets after tag filtering

3. **Output Generation**
   - Applies title_suffix to name
   - Uses filename for output files
   - Generates HTML, PDF, JSON

### Tag Matching Examples

#### Example 1: Simple Match

**Profile tags:** `[leadership, all]`

**Resume item:**
```yaml
- description: "Led team of 5 developers"
  include_in: [leadership]
```

**Result:** ✓ Included (leadership tag matches)

---

#### Example 2: Multiple Tag Match

**Profile tags:** `[leadership, technical, all]`

**Resume item:**
```yaml
- description: "Architected microservices system"
  include_in: [technical, development]
```

**Result:** ✓ Included (technical tag matches)

---

#### Example 3: No Match

**Profile tags:** `[leadership, all]`

**Resume item:**
```yaml
- description: "Wrote Python automation scripts"
  include_in: [technical, development]
```

**Result:** ✗ Excluded (no matching tags)

---

#### Example 4: Universal Content

**Profile tags:** `[leadership, all]`

**Resume item:**
```yaml
- description: "Collaborated with stakeholders"
  include_in: [all]
```

**Result:** ✓ Included (all tag always matches)

---

### Bullet Limiting Example

**Original job (after tag filtering):**
```yaml
responsibilities:
  - "Led team of 6 security analysts"           # 1
  - "Defined strategic roadmap"                 # 2
  - "Managed hiring and performance reviews"    # 3
  - "Presented at executive meetings"           # 4
  - "Built stakeholder relationships"           # 5
  - "Improved team efficiency by 40%"           # 6
```

**With max_bullets_per_job: 4:**
```yaml
responsibilities:
  - "Led team of 6 security analysts"
  - "Defined strategic roadmap"
  - "Managed hiring and performance reviews"
  - "Presented at executive meetings"
```

**Tip:** Order your responsibilities by importance in `resume.yaml`

---

## Best Practices

### Profile Design

1. **Keep It Focused**
   - Each profile should have a clear purpose
   - Don't create too many similar profiles
   - 3-5 profiles is usually sufficient

2. **Use Descriptive Names**
   - Name should indicate profile's focus
   - Description should explain use case
   - Slug should be short but clear

3. **Include 'all' Tag**
   - Always include `all` in your include_tags
   - Ensures universal content appears
   - Example: `[leadership, all]` not just `[leadership]`

4. **Test Your Profiles**
   - Build PDFs and review output
   - Check page length (aim for 1-2 pages)
   - Verify content relevance
   - Compare profiles side-by-side

### Content Tagging

1. **Tag at Appropriate Level**
   - Tag entire jobs if fully relevant
   - Tag individual bullets for mixed roles
   - Use `[all]` for universal content

2. **Use Multiple Tags When Appropriate**
   ```yaml
   - description: "Led technical architecture review meetings"
     include_in: [leadership, technical]  # Relevant to both
   ```

3. **Avoid Over-Tagging**
   - Don't add every possible tag
   - Be selective and intentional
   - Less is more

4. **Document Custom Tags**
   - If creating custom tags, document them
   - Ensure consistent usage
   - Add to this guide

### File Organization

```
resume_builder/
├── profiles/
│   ├── default.yaml        # Standard profiles
│   ├── leadership.yaml
│   ├── technical.yaml
│   ├── consulting.yaml     # Custom profiles
│   └── startup.yaml
├── resume.yaml             # Master resume
└── profile_manager.py      # Filtering logic
```

### Naming Conventions

- **Profile files:** lowercase, descriptive, `.yaml` extension
- **Profile slugs:** lowercase, no spaces, hyphens okay
- **Filenames:** lowercase, hyphens for spaces

Examples:
- `leadership.yaml` → slug: `leadership` → output: `resume-leadership.pdf`
- `technical-deep-dive.yaml` → slug: `technical-deep` → output: `resume-technical-deep.pdf`

---

## Troubleshooting

### Profile Not Found

**Error:**
```
ERROR: Profile 'consulting' not found in profiles/ directory
Available profiles: default, leadership, technical
```

**Solution:**
1. Check profile file exists: `/resume_builder/profiles/consulting.yaml`
2. Verify filename matches slug
3. Check YAML syntax is valid

---

### No Content in Generated Resume

**Problem:** Generated resume is empty or missing content

**Possible Causes:**
1. **No matching tags**
   - Profile's `include_tags` don't match any resume content
   - Solution: Review resume tags or adjust profile tags

2. **Content not tagged**
   - Resume items missing `include_in` field
   - Solution: Add tags to resume content

3. **max_bullets_per_job too restrictive**
   - Set to 0 or very low number
   - Solution: Increase or remove limit

**Debug Steps:**
```bash
# Validate resume
python resume_builder/validate_resume.py resume.yaml --verbose

# Test profile
python resume_builder/profile_manager.py --test leadership
```

---

### Bullet Limit Not Working

**Problem:** More bullets appear than max_bullets_per_job setting

**Possible Causes:**
1. **Limit not set in profile**
   - Omitting `max_bullets_per_job` includes all bullets
   - Solution: Add limit to profile

2. **Multiple jobs in one company**
   - Limit applies per job, not per company
   - Solution: This is expected behavior

3. **Mixed bullet types**
   - String bullets vs object bullets treated differently
   - Solution: Review bullet structure

---

### PDF Too Long/Short

**Problem:** Generated PDF is not the right length

**Solutions:**

**If too long (>2 pages):**
1. Add or decrease `max_bullets_per_job`
   ```yaml
   filters:
     max_bullets_per_job: 3  # Reduce from 4 to 3
   ```

2. Use more specific tags
   ```yaml
   filters:
     include_tags: [leadership]  # Remove 'management' if too broad
   ```

3. Review master resume content
   - Remove less relevant items
   - Combine similar achievements

**If too short (<1 page):**
1. Add more tags
   ```yaml
   filters:
     include_tags: [leadership, management, consulting, all]
   ```

2. Increase bullet limit
   ```yaml
   filters:
     max_bullets_per_job: 6
   ```

3. Add more content to master resume
   - Expand responsibilities
   - Add achievements
   - Include more detail

---

### YAML Syntax Errors

**Error:**
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Common Issues:**
1. **Incorrect indentation**
   - YAML requires consistent spaces (2 or 4)
   - Don't mix tabs and spaces

2. **Missing colons**
   - Each key needs a colon: `key: value`

3. **Unquoted special characters**
   - Use quotes for strings with colons, dashes
   - Example: `name: "Role: Team Lead"`

**Solution:** Use a YAML validator or IDE with YAML support

---

## Advanced Features

### Conditional Formatting (Future)

Future versions may support conditional formatting:

```yaml
filters:
  include_tags: [leadership, all]
  formatting:
    emphasize_keywords: [led, managed, mentored]
    highlight_achievements: true
```

### Date Range Filtering (Future)

Filter experience by date range:

```yaml
filters:
  include_tags: [all]
  date_range:
    start: "2020-01-01"
    end: "Present"
```

### Section Exclusion (Future)

Exclude entire sections:

```yaml
filters:
  include_tags: [all]
  exclude_sections: [volunteer, interests, publications]
```

---

## Integration with Job Branch Workflow

Profiles integrate with the job branch system:

### Creating Job Application Branch

```bash
# Create branch with specific profile
./scripts/new-job-application.sh aws-security-eng leadership

# Creates:
# - Branch: resume/aws-security-eng
# - File: active_profile.txt (contains: "leadership")
# - Uses leadership.yaml for filtering
```

### Workflow

1. Choose appropriate profile for job
2. Create job branch with profile selection
3. Push branch to trigger build
4. GitHub Actions reads profile from active_profile.txt
5. Filters resume using profile
6. Deploys to private URL

See `/docs/job-branch-workflow.md` for complete workflow documentation.

---

## Related Documentation

- **Schema Documentation:** `/resume_builder/SCHEMA_DOCUMENTATION.md`
  - Resume structure and validation
  - Tag system details
  - Content examples

- **Task List:** `/docs/project-planning/TASK_LIST.md`
  - Implementation roadmap
  - Task 1.3: Profile system creation
  - Task 1.4: Profile manager development

- **Job Branch Workflow:** `/docs/job-branch-workflow.md` (future)
  - Complete workflow guide
  - Token system
  - Deployment process

---

## Quick Reference

### Create New Profile

```bash
# 1. Create file
touch resume_builder/profiles/myprofile.yaml

# 2. Add configuration
cat > resume_builder/profiles/myprofile.yaml << EOF
profile:
  name: "My Profile"
  description: "Custom focus area"
  slug: "myprofile"
filters:
  include_tags: [custom, all]
  max_bullets_per_job: 4
output:
  title_suffix: " - Custom Focus"
  filename: "resume-custom"
EOF

# 3. Validate
python resume_builder/profile_manager.py --validate myprofile

# 4. Build
./build_all.sh --profile myprofile
```

### Available Commands

```bash
# List all profiles
python resume_builder/profile_manager.py --list

# Validate profile
python resume_builder/profile_manager.py --validate leadership

# Test profile filtering
python resume_builder/profile_manager.py --test leadership

# Build with profile
./build_all.sh --profile leadership

# Build all profiles
./build_all.sh --all-profiles
```

---

## Support

For issues or questions:

1. Review this documentation
2. Check `/resume_builder/SCHEMA_DOCUMENTATION.md` for tag system details
3. Validate profile YAML syntax
4. Test with `--verbose` flag for detailed output
5. Review Task 1.3 and 1.4 in TASK_LIST.md for implementation details

---

**Version History:**
- v1.0.0 (2025-11-21): Initial profile creation guide

**Maintained by:** Dynamic YAML-Based Resume System
**Project:** colins-resume
