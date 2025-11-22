# Resume Content Tagging Guide

This guide documents the tagging system used in the master resume (`resume.yaml`) for profile-based filtering.

## Overview

The master resume contains **100+ content items** that can be filtered into different profiles (leadership, technical, default) based on `include_in` tags. This allows a single source of truth to generate multiple targeted resume versions.

## Content Statistics

| Metric | Count |
|--------|-------|
| Total work experience bullets | 78 |
| Total project highlights | 35 |
| Total content items | 113+ |
| Profiles available | 3 (default, technical, leadership) |

## Available Tags

| Tag | Description | Used In Profiles |
|-----|-------------|------------------|
| `all` | Universal content appearing in all profiles | default, technical, leadership |
| `leadership` | Leadership and people management content | leadership |
| `management` | Management and team-building content | leadership |
| `technical` | Technical skills and implementation content | technical |
| `development` | Software development and coding content | technical |

## Tagging Strategy

### Universal Content (`[all]`)
Use for content that should appear in every profile:
- Core achievements with broad appeal
- Key accomplishments that define your career
- Education and awards
- Foundational skills

```yaml
- description: |-
    Reduced team backlog from over 300 tickets to 0, maintaining fewer
    than 10 tickets over the previous quarter.
  include_in: [all]
```

### Leadership Content (`[leadership, management]`)
Use for content emphasizing people and team leadership:
- Team building and mentorship
- 1:1 meetings and career development
- Performance management
- Cross-functional collaboration
- Stakeholder management

```yaml
- description: |-
    Conducted weekly 1:1 meetings with each team member to discuss
    career development, remove blockers, and provide personalized mentorship.
  include_in: [leadership, management]
```

### Technical Content (`[technical, development]`)
Use for content emphasizing technical skills:
- Python/code development
- Automation frameworks
- CI/CD pipelines
- Detection engineering
- Infrastructure and cloud

```yaml
- description: |-
    Architected and implemented Python-based automation framework using
    AWS Lambda and EventBridge, reducing manual alert triage time by 65%.
  include_in: [technical, development]
```

## Profile Filtering Results

When the profile manager filters content:

| Profile | Include Tags | Max Bullets/Job | Typical Output |
|---------|--------------|-----------------|----------------|
| default | `[all]` | unlimited | ~94 items |
| technical | `[technical, development, all]` | 4 | ~48 items |
| leadership | `[leadership, management, all]` | 4 | ~48 items |

## Tagging Guidelines

### DO:
- Tag every responsibility/highlight with at least one tag
- Use `[all]` for items that should appear everywhere
- Use specific tags (`[leadership]`) for profile-only content
- Include measurable results in all bullet points
- Keep bullets concise but impactful

### DON'T:
- Leave items untagged (they won't appear anywhere)
- Use `[all]` with other tags on the same item (redundant)
- Create too many profile-specific items (profiles may feel sparse)
- Mix incompatible tags like `[leadership, technical]` without `all`

## Tag Placement

Tags can be placed at different levels:

### Job Level
Includes/excludes entire job from profile:
```yaml
- job_title: Team Lead
  include_in: [all]
```

### Responsibility Level
Includes/excludes specific bullet points:
```yaml
responsibilities:
  - description: "Technical achievement..."
    include_in: [technical, development]
  - description: "Leadership achievement..."
    include_in: [leadership, management]
```

### Project Highlight Level
Includes/excludes specific project highlights:
```yaml
highlights:
  - description: "Built automation pipeline..."
    include_in: [technical, development]
```

## Content Balance

Aim for this distribution per job:

| Tag Type | Target % | Purpose |
|----------|----------|---------|
| `[all]` | 40-50% | Core achievements |
| `[leadership, management]` | 25-30% | Leadership depth |
| `[technical, development]` | 25-30% | Technical depth |

This ensures each filtered profile has adequate content while avoiding overlap bloat.

## Validation

Always validate after making changes:

```bash
cd resume_builder
python3 validate_resume.py resume.yaml
```

The validator will check:
- All items have `include_in` tags
- Tags are from the allowed list
- No redundant tag combinations
- Proper YAML structure

## Adding New Content

When adding new content:

1. Write the bullet point
2. Determine the target audience:
   - General appeal → `[all]`
   - Leadership focus → `[leadership, management]`
   - Technical focus → `[technical, development]`
3. Place the tag appropriately
4. Run validation
5. Test profile filtering

## Maintenance

### Quarterly Review
- Review all content for relevance
- Update metrics and achievements
- Add new accomplishments
- Archive outdated content

### Before Job Applications
- Verify profiles generate appropriate content
- Check that key achievements are tagged correctly
- Ensure no important content is missing from target profile
