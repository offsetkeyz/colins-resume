# Resume Builder Checkbox Functionality - Test Guide

## Prerequisites
- Dev server running at http://localhost:5173/
- Browser with JavaScript enabled
- No browser console errors

## Test 1: Verify Master View (Read-Only)

1. Open http://localhost:5173/ in browser
2. Verify "Master" is selected in the version dropdown
3. Check that all checkboxes are **disabled** (grayed out)
4. Try clicking checkboxes - they should NOT change state
5. **Expected**: Master view is read-only, all content visible, checkboxes disabled

## Test 2: Create a New Version

1. Click "+ New" button in the top navigation
2. Enter version name: "Test Version"
3. Leave "Based on" as "Master (all items selected)"
4. Click "Create Version"
5. **Expected**: Version created, automatically switched to "Test Version"

## Test 3: Section-Level Checkboxes (Sidebar)

1. Ensure "Test Version" is active (not Master)
2. In the left sidebar, uncheck "Awards"
3. **Expected**: 
   - Awards section disappears from the content editor
   - Awards section disappears from the preview panel
   - Checkbox state persists

4. Check "Awards" again
5. **Expected**: Awards section reappears in both editor and preview

## Test 4: Company-Level Checkboxes (Work Experience)

1. In Work Experience section, find a company (e.g., "Arctic Wolf Networks")
2. Click the company checkbox to uncheck it
3. **Expected**:
   - Company checkbox unchecks
   - ALL positions under that company uncheck
   - ALL bullets under all positions uncheck
   - Company text becomes grayed out
   - Company disappears from preview

4. Click the company checkbox again to check it
5. **Expected**: Everything under that company re-appears

## Test 5: Position-Level Checkboxes

1. Expand a company with multiple positions
2. Uncheck ONE position (not all)
3. **Expected**:
   - That position's checkbox unchecks
   - ALL bullets under that position uncheck
   - Company checkbox shows INDETERMINATE state (dash/minus sign)
   - Position disappears from preview
   - Other positions still visible

4. Check the position again
5. **Expected**:
   - Position re-appears
   - Company checkbox returns to checked state

## Test 6: Bullet-Level Checkboxes

1. Expand a position with multiple bullets
2. Uncheck ONE bullet (not all)
3. **Expected**:
   - Bullet checkbox unchecks
   - Bullet text becomes grayed out
   - Position checkbox shows INDETERMINATE state
   - Company checkbox shows INDETERMINATE state
   - Bullet disappears from preview
   - Other bullets still visible

4. Uncheck more bullets but leave at least one checked
5. **Expected**: Indeterminate states remain

6. Uncheck ALL bullets in the position
7. **Expected**: Position checkbox automatically unchecks

## Test 7: Education Checkboxes

1. In Education section, uncheck one education item
2. **Expected**:
   - Item becomes grayed out
   - Item disappears from preview
   - Other education items remain

## Test 8: Skills Checkboxes

1. In Skills section, uncheck one skill group
2. **Expected**:
   - Skill group becomes grayed out
   - Skill group disappears from preview

## Test 9: Projects with Highlights

1. In Projects section, expand a project
2. Uncheck one highlight (not all)
3. **Expected**:
   - Highlight unchecks and grays out
   - Project checkbox shows INDETERMINATE state
   - Highlight disappears from preview
   - Project name still shows in preview

4. Uncheck ALL highlights
5. **Expected**: Project checkbox automatically unchecks

## Test 10: Certifications Checkboxes

1. In Certifications section, uncheck a certification
2. **Expected**:
   - Certification unchecks and grays out
   - Certification badge disappears from preview

## Test 11: Live Preview Updates

1. Open preview panel (right side)
2. Perform any checkbox action
3. **Expected**: Preview updates IMMEDIATELY without page refresh

## Test 12: Version Persistence

1. Make several checkbox changes
2. Switch to "Master" version
3. **Expected**: See all content (Master is always full)
4. Switch back to "Test Version"
5. **Expected**: All your checkbox selections are preserved

## Test 13: Indeterminate State Visual Verification

1. Create a partially selected state (some bullets checked, some not)
2. **Expected**: Parent checkbox shows a dash/minus symbol (indeterminate)
3. Click the indeterminate checkbox
4. **Expected**: All children become checked (or all unchecked, depending on implementation)

## Test 14: Preview Open in New Tab

1. Click the "Open in new tab" icon in preview panel
2. **Expected**: New browser tab opens with full-page resume preview
3. Verify only selected content is shown

## Success Criteria

✓ All checkboxes are clickable (except in Master view)
✓ Checkbox changes update immediately in preview
✓ Hierarchical relationships work correctly (parent ↔ child)
✓ Indeterminate states display correctly
✓ Selections persist when switching between versions
✓ Master view remains read-only
✓ No console errors
✓ Preview matches editor selections exactly

## Common Issues to Watch For

❌ Clicking checkbox toggles collapse/expand instead of checking
❌ Checkboxes don't respond to clicks
❌ Preview doesn't update
❌ Indeterminate state doesn't show
❌ Selections don't persist
❌ Master view allows editing
❌ Console errors appear

## If Tests Fail

1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Verify resume.yaml loaded successfully
5. Check that Zustand store is working (use React DevTools)
