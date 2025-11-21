# Profile Manager Test Report

## Summary

- **Module**: `resume_builder/profile_manager.py`
- **Test File**: `resume_builder/test_profile_manager.py`
- **Date**: 2025-11-21
- **Status**: PASSED

## Test Results

| Metric | Value |
|--------|-------|
| Total Tests | 45 |
| Passed | 45 |
| Failed | 0 |
| Skipped | 0 |
| Coverage | 90% |
| Execution Time | 0.17s |

## Coverage Report

```
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
profile_manager.py     183     19    90%   37, 55, 73, 77, 80, 95, 201, 216, 221, 238, 304, 326, 330, 385, 420-421, 429, 432, 438
--------------------------------------------------
TOTAL                  183     19    90%
```

## Test Suites

### Test Suite 1: Tag Filtering (7 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_include_in_filtering | PASSED | Verifies items are filtered based on include_in tags |
| test_missing_include_in_tag | PASSED | Handles items without include_in tags correctly |
| test_all_tag_includes_everywhere | PASSED | 'all' tag includes items marked with 'all' |
| test_multiple_tags_on_item | PASSED | Items with multiple tags match any specified tag |
| test_filter_items_empty_input | PASSED | Handles empty inputs gracefully |
| test_filter_items_preserves_order | PASSED | Maintains original order after filtering |
| test_filter_items_deep_copies | PASSED | Returns deep copies to prevent mutations |

### Test Suite 2: Max Bullets Limiting (6 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_max_bullets_per_job | PASSED | Limits responsibilities to max_bullets_per_job |
| test_max_bullets_with_filtering | PASSED | Bullet limiting works with tag filtering |
| test_no_bullet_limit | PASSED | No limit applied when max_bullets_per_job not set |
| test_apply_bullet_limit_edge_cases | PASSED | Handles None, 0, negative limits correctly |
| test_apply_bullet_limit_deep_copies | PASSED | Returns deep copies of bullets |
| test_max_bullets_on_projects | PASSED | Limits project highlights correctly |

### Test Suite 3: Edge Cases (12 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_profile_not_found | PASSED | Raises ProfileNotFoundError for missing profiles |
| test_empty_profile | PASSED | Raises InvalidProfileError for empty profiles |
| test_nested_filtering | PASSED | Filters nested work experience correctly |
| test_malformed_tags | PASSED | Handles malformed include_in tags gracefully |
| test_empty_resume_data | PASSED | Returns empty dict for empty/None resume |
| test_empty_filters_in_profile | PASSED | Defaults to ['all'] when filters missing |
| test_none_profile | PASSED | Returns copy of data when profile is None |
| test_invalid_yaml_profile | PASSED | Raises InvalidProfileError for invalid YAML |
| test_work_experience_not_dict | PASSED | Handles non-dict work_experience |
| test_positions_not_list | PASSED | Handles non-list positions |
| test_non_dict_items_in_list | PASSED | Handles non-dict items in lists |
| test_filter_preserves_unfiltered_sections | PASSED | Preserves interests, languages, meta sections |

### Test Suite 4: Profile Loading (6 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_load_profile_success | PASSED | Successfully loads valid profiles |
| test_load_profile_with_max_bullets | PASSED | Loads max_bullets_per_job setting |
| test_list_available_profiles | PASSED | Lists available profile names |
| test_list_profiles_empty_directory | PASSED | Returns empty list for empty directory |
| test_list_profiles_nonexistent_directory | PASSED | Returns empty list for nonexistent directory |
| test_load_real_profiles | PASSED | Loads actual project profiles |

### Test Suite 5: Profile Validation (6 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_validate_valid_profile | PASSED | Valid profile passes validation |
| test_validate_empty_profile | PASSED | Empty profile fails validation |
| test_validate_none_profile | PASSED | None profile fails validation |
| test_validate_missing_profile_section | PASSED | Missing profile section fails |
| test_validate_invalid_include_tags_type | PASSED | Non-list include_tags fails |
| test_validate_invalid_max_bullets_type | PASSED | Non-integer max_bullets fails |

### Test Suite 6: Profile Info (2 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_get_profile_info | PASSED | Extracts complete profile info |
| test_get_profile_info_defaults | PASSED | Returns defaults for missing sections |

### Test Suite 7: Integration Tests (2 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_filter_with_real_resume_data | PASSED | Filters actual resume.yaml correctly |
| test_all_profiles_filter_correctly | PASSED | All 3 profiles produce valid output |

### Test Suite 8: Performance Tests (2 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_filter_1000_items_performance | PASSED | Filters 1000 items in <100ms |
| test_filter_resume_performance | PASSED | Large resume (100 companies x 10 positions) <1000ms |

### Test Suite 9: JSON Resume Format (2 tests)

| Test | Status | Description |
|------|--------|-------------|
| test_filter_json_resume_work | PASSED | Handles JSON Resume 'work' array format |
| test_filter_json_resume_certificates | PASSED | Handles JSON Resume 'certificates' format |

## Profile Verification

All 3 profiles in the project have been verified to work correctly:

### Default Profile
- **Tags**: ['all']
- **Max Bullets**: None (unlimited)
- **Result**: Includes all items with 'all' tag

### Technical Profile
- **Tags**: ['technical', 'development', 'all']
- **Max Bullets**: 4
- **Result**: Includes technical/development items, limited to 4 bullets

### Leadership Profile
- **Tags**: ['leadership', 'management', 'all']
- **Max Bullets**: 4
- **Result**: Includes leadership/management items, limited to 4 bullets

## Performance Results

| Benchmark | Requirement | Result |
|-----------|-------------|--------|
| Filter 1000 items | <100ms | PASSED |
| Large resume (100 companies x 10 positions) | <1000ms | PASSED |

## Key Functions Implemented

### `load_profile(profile_name: str) -> dict`
Loads profile configuration from `profiles/` directory.
- Raises `ProfileNotFoundError` if profile doesn't exist
- Raises `InvalidProfileError` if profile is empty or invalid
- Defaults `include_tags` to `['all']` if not specified

### `filter_resume_data(resume_data: dict, profile: dict) -> dict`
Applies profile filters to resume data.
- Filters work_experience, education, certifications, skills, projects
- Applies bullet limits to responsibilities and highlights
- Deep copies data to prevent mutations
- Supports both YAML resume format and JSON Resume format

### `filter_items(items: list, include_tags: list) -> list`
Filters list items based on include_in tags.
- Items included if any include_in tag matches any include_tag
- Items without tags included if 'all' in include_tags
- Handles malformed tags gracefully

### `apply_bullet_limit(bullets: list, max_bullets: int) -> list`
Limits number of bullets per job.
- None or 0 means no limit
- Returns deep copy of truncated list

## Acceptance Criteria Status

| Criteria | Status |
|----------|--------|
| All unit tests pass | PASSED (45/45) |
| Code coverage >= 85% | PASSED (90%) |
| Profile manager filters correctly for all 3 profiles | PASSED |
| Edge cases handled gracefully | PASSED |
| Performance: Filter 1000 items in <100ms | PASSED |

## Files

- **Implementation**: `/home/user/colins-resume/resume_builder/profile_manager.py`
- **Tests**: `/home/user/colins-resume/resume_builder/test_profile_manager.py`
- **Profiles**: `/home/user/colins-resume/resume_builder/profiles/`
  - `default.yaml`
  - `technical.yaml`
  - `leadership.yaml`
