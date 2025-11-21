# Intentional Differences: JSON to YAML Migration

**Document Version:** 1.0.0
**Last Updated:** 2025-11-21
**Status:** Approved

---

## Overview

This document catalogs all intentional differences between the original JSON Resume format and the new YAML-based resume system. These changes were made deliberately to improve the system while maintaining data integrity.

---

## Schema Changes

### 1. Work Experience Structure

**JSON (Before):**
```json
"work": [
  {
    "name": "Company Name",
    "position": "Job Title",
    "startDate": "2024-01-01",
    "endDate": "2024-12-01",
    "summary": "Role description",
    "highlights": ["Achievement 1", "Achievement 2"]
  }
]
```

**YAML (After):**
```yaml
work_experience:
  Company Name:
    - job_title: Job Title
      start_date: '2024-01-01'
      end_date: '2024-12-01'
      responsibilities:
        - "Role description"
        - "Achievement 1"
        - "Achievement 2"
      include_in: [all]
```

**Rationale:**
- Grouping by company improves organization
- `job_title` is clearer than `position`
- Snake_case dates consistent with work_experience section
- Merged `summary` and `highlights` into `responsibilities` (summary becomes first item)
- Added `include_in` for profile filtering

---

### 2. Field Name Changes

| JSON Field | YAML Field | Section | Rationale |
|------------|------------|---------|-----------|
| `position` | `job_title` | work_experience | Clearer naming |
| `startDate` | `start_date` | work_experience | Snake_case consistency |
| `endDate` | `end_date` | work_experience | Snake_case consistency |
| `name` (cert) | `title` | certifications | Consistency with awards |
| `skills` | `specialty_skills` | root | Distinguish skill categories from simple lists |
| `certificates` | `certifications` | root | More standard naming |
| `work` | `work_experience` | root | Clearer naming |

---

### 3. Date Format Consistency

**Education & Projects:** Use camelCase (`startDate`, `endDate`)
- Per JSON Resume schema compatibility
- Maintains compatibility with existing tools

**Work Experience:** Use snake_case (`start_date`, `end_date`)
- Consistent with other work_experience fields
- Clear visual distinction between sections

---

### 4. Null Value Handling

**JSON:** Null or missing end dates
```json
"endDate": null
```

**YAML:** Explicit "Present" string
```yaml
end_date: Present
```

**Rationale:**
- Explicit is better than implicit
- Clearer for generators and validators
- Human-readable

---

### 5. Content Merging

**JSON:**
```json
{
  "summary": "Description of role",
  "highlights": ["Point 1", "Point 2"]
}
```

**YAML:**
```yaml
responsibilities:
  - "Description of role"
  - "Point 1"
  - "Point 2"
```

**Rationale:**
- Summary and highlights serve similar purpose
- Single list is easier to manage
- Profile filtering can apply to entire list
- First item is understood to be the summary/overview

---

## New Features Added

### 1. include_in Tags

Every filterable item now has an `include_in` tag:

```yaml
- job_title: Team Lead
  include_in:
    - all
    - leadership
    - management
```

**Purpose:** Enable profile-based resume customization without duplicating data

**Valid Tags:**
- `all` - Include in all profiles (default)
- `leadership` - Leadership-focused profiles
- `management` - Management-focused profiles
- `technical` - Technical-focused profiles
- `development` - Development-focused profiles
- `consulting` - Consulting-focused profiles
- `startup` - Startup-focused profiles

---

### 2. Profile System

New profile configuration files in `profiles/` directory:

- `default.yaml` - Full resume (include_tags: [all])
- `technical.yaml` - Technical focus
- `leadership.yaml` - Leadership focus

---

### 3. YAML-Specific Benefits

| Feature | JSON | YAML |
|---------|------|------|
| Multi-line strings | Escaped newlines | Block literals (|) |
| Comments | Not supported | Supported |
| Anchors/aliases | Not supported | Supported |
| Readability | Good | Better |
| Human editing | Possible | Easier |

---

## Backward Compatibility

### Export Function

A YAML-to-JSON export function is provided for backward compatibility:

```python
from test_migration_validation import yaml_to_json_export

json_data = yaml_to_json_export(Path('resume.yaml'))
```

This reverses all transformations for tools expecting JSON Resume format.

---

### Build Script Compatibility

The existing build scripts (`md_generator.py`, `html_generator.py`) may need updates:

| Script | Required Changes |
|--------|------------------|
| `md_generator.py` | Update to read YAML, use new field names |
| `html_generator.py` | Update to read YAML, use new field names |
| `build_all.sh` | Update file references |

---

## Data Preservation Guarantees

| Guarantee | Status | Verification |
|-----------|--------|--------------|
| All text content preserved | VERIFIED | test_migration_validation.py |
| All URLs preserved | VERIFIED | test_urls_preserved |
| All dates preserved | VERIFIED | test_date_formats |
| No encoding corruption | VERIFIED | test_no_encoding_issues |
| Bidirectional conversion | VERIFIED | yaml_to_json_export |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-21 | Initial documentation |

---

*This document is part of the YAML Resume Migration project (Task 1.5)*
