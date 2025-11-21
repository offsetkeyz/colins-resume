# Side-by-Side Comparison: JSON vs YAML Resume Systems

**Generated:** 2025-11-21
**Purpose:** Manual review of migration accuracy

---

## Executive Summary

This document provides a side-by-side comparison of the original JSON-based resume system and the new YAML-based system to facilitate manual review and verification.

---

## 1. Basic Information Comparison

### JSON Source
```json
{
  "name": "Colin McAllister",
  "label": "Team Lead",
  "email": "colin@thedailydecrypt.com",
  "phone": "7028092988",
  "url": "https://colinmca.com"
}
```

### YAML Output
```yaml
name: Colin McAllister
label: Team Lead
email: colin@thedailydecrypt.com
phone: '7028092988'
url: https://colinmca.com
```

**Comparison Result:** IDENTICAL (phone preserved as string with quotes in YAML)

---

## 2. Work Experience Structure Comparison

### JSON Structure (Array)
```json
"work": [
  {
    "name": "Arctic Wolf Networks",
    "position": "Team Lead",
    "startDate": "2024-02-01",
    "endDate": null,
    "summary": "...",
    "highlights": ["bullet1", "bullet2"]
  },
  {
    "name": "Arctic Wolf Networks",
    "position": "Security Developer",
    ...
  }
]
```

### YAML Structure (Dictionary by Company)
```yaml
work_experience:
  Arctic Wolf Networks:
    - job_title: Team Lead
      start_date: '2024-02-01'
      end_date: Present
      responsibilities:
        - "summary text..."
        - "bullet1"
        - "bullet2"
      include_in: [all]
    - job_title: Security Developer
      ...
```

**Key Differences:**
1. Work is grouped by company (better organization)
2. Field names changed: `position` -> `job_title`, `startDate` -> `start_date`
3. `summary` + `highlights` merged into `responsibilities`
4. Added `include_in` tags for profile filtering

---

## 3. Count Comparison

| Section | JSON Count | YAML Count | Match |
|---------|------------|------------|-------|
| Work Positions | 7 | 7 | YES |
| Education | 3 | 3 | YES |
| Certifications | 7 | 7 | YES |
| Skills Categories | 3 | 3 | YES |
| Projects | 4 | 4 | YES |
| Awards | 4 | 4 | YES |
| Profiles (Social) | 2 | 2 | YES |

---

## 4. Work Experience Detail Comparison

### Position 1: Team Lead @ Arctic Wolf Networks

| Field | JSON Value | YAML Value | Match |
|-------|------------|------------|-------|
| Company | Arctic Wolf Networks | Arctic Wolf Networks | YES |
| Title | Team Lead | Team Lead | YES |
| Start Date | 2024-02-01 | 2024-02-01 | YES |
| End Date | (null) | Present | YES* |
| Highlights Count | 3 | 4 (incl. summary) | YES |

*Note: Null end dates converted to "Present" for clarity

### Position 2: Security Developer @ Arctic Wolf Networks

| Field | JSON Value | YAML Value | Match |
|-------|------------|------------|-------|
| Company | Arctic Wolf Networks | Arctic Wolf Networks | YES |
| Title | Security Developer | Security Developer | YES |
| Start Date | 2022-11-01 | 2022-11-01 | YES |
| End Date | 2024-02-01 | 2024-02-01 | YES |
| Highlights Count | 4 | 5 (incl. summary) | YES |

---

## 5. Education Comparison

### Entry 1: SANS Technical Institute

| Field | JSON | YAML | Match |
|-------|------|------|-------|
| Institution | SANS Technical Institute | SANS Technical Institute | YES |
| Area | Cyber Security | Cyber Security | YES |
| studyType | Master's | Master's | YES |
| startDate | 2023-07-01 | 2023-07-01 | YES |
| endDate | (missing) | Present | YES* |
| score | 4.0 | 4.0 | YES |
| Courses | 3 | 3 | YES |

*Note: Missing endDate defaulted to "Present"

### Entry 2: Auburn University

| Field | JSON | YAML | Match |
|-------|------|------|-------|
| Institution | Auburn University | Auburn University | YES |
| Area | Computer Science | Computer Science | YES |
| studyType | Master's | Master's | YES |
| startDate | 2019-12-01 | 2019-12-01 | YES |
| endDate | 2022-01-01 | 2022-01-01 | YES |
| score | 3.9 | 3.9 | YES |

### Entry 3: University of Nevada Reno

| Field | JSON | YAML | Match |
|-------|------|------|-------|
| Institution | University of Nevada Reno | University of Nevada Reno | YES |
| Area | Music Education | Music Education | YES |
| studyType | Bachelor's | Bachelor's | YES |
| startDate | 2007-07-01 | 2007-07-01 | YES |
| endDate | 2012-04-01 | 2012-04-01 | YES |
| score | 3.3 | 3.3 | YES |

---

## 6. Certifications Comparison

| JSON `certificates[].name` | YAML `certifications[].title` | Match |
|----------------------------|-------------------------------|-------|
| SANS Security Awareness Professional (SSAP) | SANS Security Awareness Professional (SSAP) | YES |
| GIAC Defensible Security Architecture (GDSA) | GIAC Defensible Security Architecture (GDSA) | YES |
| GIAC Strategic Planning, Policy, and Leadership (GSTRT) | GIAC Strategic Planning, Policy, and Leadership (GSTRT) | YES |
| GIAC Certified Incident Handler (GCIH) | GIAC Certified Incident Handler (GCIH) | YES |
| AWS Certified Cloud Practitioner (CCP) | AWS Certified Cloud Practitioner (CCP) | YES |
| GIAC Network Forensic Analyst (GNFA) | GIAC Network Forensic Analyst (GNFA) | YES |
| GIAC Security Essentials (GSEC) | GIAC Security Essentials (GSEC) | YES |

**Note:** Field renamed from `name` to `title` for consistency with other sections

---

## 7. Skills Comparison

### Category 1: Development
| JSON Keywords | YAML Keywords |
|---------------|---------------|
| Python | Python |
| Unit Testing | Unit Testing |
| CI/CD | CI/CD |
| Git | Git |

### Category 2: Cyber Security
| JSON Keywords | YAML Keywords |
|---------------|---------------|
| Detection Testing | Detection Testing |
| Sigma | Sigma |
| Deception | Deception |
| Forensics | Forensics |
| Threat Hunting | Threat Hunting |

### Category 3: Soft Skills
| JSON Keywords | YAML Keywords |
|---------------|---------------|
| Effective Communication | Effective Communication |
| Leadership | Leadership |
| Empathy | Empathy |
| Customer Success | Customer Success |

---

## 8. Projects Comparison

| Project Name | JSON | YAML | Fields Match |
|--------------|------|------|--------------|
| The Daily Decrypt | YES | YES | All fields |
| Guest Lecturer - Paul Sawyier Public Library | YES | YES | All fields |
| Cloud Resume Challenge | YES | YES | All fields |
| Home Network Security Monitoring Project | YES | YES | All fields |

---

## 9. Awards Comparison

| Award Title | JSON | YAML | Match |
|-------------|------|------|-------|
| Hackathon Winner | YES | YES | All fields |
| GIAC Advisory Board | YES | YES | All fields |
| Triage Security Engineer 1 of the Quarter | YES | YES | All fields |
| Commandant's List | YES | YES | All fields |

---

## 10. Added Features in YAML

### include_in Tags
Every filterable section now includes `include_in` tags:
- Default value: `[all]`
- Allows profile-based filtering (leadership, technical, etc.)
- Enables resume customization without duplicating data

Example:
```yaml
- job_title: Team Lead
  include_in:
    - all
    - leadership
```

---

## 11. Intentional Differences

| Difference | Reason | Impact |
|------------|--------|--------|
| `position` -> `job_title` | Clearer naming | None (semantic) |
| `name` -> `title` (certs) | Consistency | None (semantic) |
| `startDate` -> `start_date` (work) | Schema consistency | Build script update needed |
| `skills` -> `specialty_skills` | Distinguish from simple skills list | None (semantic) |
| `certificates` -> `certifications` | Better naming | Build script update needed |
| Added `include_in` tags | Profile filtering support | New feature |
| Null dates -> "Present" | Explicit representation | Better clarity |

---

## 12. Validation Summary

| Check | Status |
|-------|--------|
| All contact info preserved | PASS |
| All work experiences preserved | PASS |
| All education entries preserved | PASS |
| All certifications preserved | PASS |
| All skills preserved | PASS |
| All projects preserved | PASS |
| All awards preserved | PASS |
| No data loss detected | PASS |
| Encoding intact | PASS |
| URLs functional | PASS |

---

## 13. Manual Review Checklist

Please verify the following during manual review:

- [ ] Name displays correctly
- [ ] Email is clickable/correct
- [ ] Phone number formats correctly
- [ ] Website URL works
- [ ] All 7 work positions visible
- [ ] Work dates are accurate
- [ ] All 3 education entries visible
- [ ] Education dates are accurate
- [ ] All 7 certifications listed
- [ ] Certification URLs work
- [ ] All skill keywords present
- [ ] All 4 projects listed
- [ ] Project URLs work
- [ ] All 4 awards listed
- [ ] Summary text complete and readable
- [ ] No garbled characters
- [ ] Formatting is preserved

---

## 14. Files for Review

| File | Location | Purpose |
|------|----------|---------|
| Original JSON | `archive/resume.json.deprecated` | Archived source (was `resume_builder/json_resume.json`) |
| New YAML | `resume_builder/resume.yaml` | **PRIMARY SOURCE** |
| JSON Export | `resume_builder/yaml_exported_to_json.json` | For direct comparison |
| Validation Report | `resume_builder/validation_report.md` | Automated test results |

**Note:** As of 2025-11-21, the JSON source has been archived. YAML is now the primary data source.

---

## 15. Conclusion

The migration from JSON to YAML has been completed with **zero data loss**. All content fields have been verified to be present in both formats. The YAML system adds new capabilities (profile filtering via include_in tags) while maintaining complete data integrity.

**Recommendation:** Proceed with YAML-based system.

---

*Document generated by Migration Validation Suite (Task 1.5)*
