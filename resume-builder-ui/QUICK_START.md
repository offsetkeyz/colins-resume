# Resume Builder - Quick Start & Testing Guide

## Current Status

✅ **Checkbox functionality is FULLY IMPLEMENTED and ready to test**

The implementation includes:
- Event propagation fixes (checkboxes won't trigger parent clicks)
- Hierarchical checkbox logic (parent/child relationships)
- Indeterminate states (dash/minus when partially selected)
- Live preview updates
- Version management (Master + custom versions)
- LocalStorage persistence

## Prerequisites

- Node.js 20.19+ (via nvm recommended)
- Modern browser (Chrome, Firefox, Safari)

## Starting the Development Server

```bash
# If you have nvm installed (load it first)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use Node.js 20
nvm use 20

# Start the dev server
npm run dev
```

The server will start at: **http://localhost:5173/**

## Quick Test (2 minutes)

### Step 1: Open the Application
Open http://localhost:5173/ in your browser

### Step 2: Verify Master View
- You should see "Master" selected in the version dropdown
- All checkboxes should be **GRAYED OUT and DISABLED**
- Try clicking a checkbox - it should NOT change
- This is expected behavior (Master is read-only)

### Step 3: Create Your First Version
1. Click the **"+ New"** button in the top navigation
2. Enter a name: **"Test Version"**
3. Leave "Based on" as **"Master (all items selected)"**
4. Click **"Create Version"**
5. You should now see "Test Version" in the dropdown

### Step 4: Test Checkbox Functionality
Now you're in edit mode! Try these:

#### Test Section Checkboxes (Sidebar)
1. Look at the left sidebar
2. **Uncheck "Awards"** - the Awards section should disappear
3. **Check it again** - Awards should reappear
4. Watch the preview panel update immediately

#### Test Work Experience Checkboxes
1. Find "Work Experience" section in the main editor
2. **Expand a company** (e.g., "Arctic Wolf Networks")
3. **Expand a position** (e.g., "Team Lead")
4. Try unchecking:
   - One bullet - position shows dash (indeterminate)
   - All bullets in position - position unchecks automatically
   - The entire position - all bullets uncheck
   - The entire company - everything unchecks

#### Test Other Sections
- Education: Uncheck an education item
- Skills: Uncheck a skill group
- Projects: Uncheck project highlights
- Certifications: Uncheck a certification

### Step 5: Verify Preview Updates
1. Look at the preview panel on the right
2. Every time you toggle a checkbox, the preview should update **IMMEDIATELY**
3. Unchecked items should **DISAPPEAR** from the preview
4. Checked items should **APPEAR** in the preview

### Step 6: Test Version Persistence
1. Make several checkbox changes
2. Switch version dropdown to **"Master"**
   - You should see ALL content (Master is always full)
   - Checkboxes are disabled
3. Switch back to **"Test Version"**
   - Your selections should be **PRESERVED**
   - Checkboxes are enabled again

## What Success Looks Like

### ✅ Working Correctly
- Checkboxes toggle on/off when clicked (in version view)
- Preview updates immediately when you change selections
- Grayed-out items appear dim in the editor
- Indeterminate state shows a dash/minus symbol
- Master view has all checkboxes disabled
- Version selections persist when switching versions
- No console errors in browser DevTools

### ❌ Not Working
- Clicking checkbox also expands/collapses sections
- Checkboxes don't respond to clicks
- Preview doesn't update
- Selections don't persist
- Console shows errors
- Master view allows editing

## Key Files Modified

The following files were updated with event propagation fixes:

```
src/components/shared/CollapsibleSection.tsx
src/components/layout/Sidebar.tsx
src/components/editor/WorkExperienceEditor.tsx
src/components/editor/EducationEditor.tsx
src/components/editor/SkillsEditor.tsx
src/components/editor/ProjectsEditor.tsx
src/components/editor/SimpleListEditor.tsx
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Action                          │
│                    (Click Checkbox)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Event Propagation                         │
│           stopPropagation() prevents bubbling               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Zustand Store                            │
│        - toggleBullet(), togglePosition(), etc.             │
│        - Updates selection state                            │
│        - Saves to localStorage                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Component Re-render                         │
│        - getCurrentSelections() gets new state              │
│        - Components update with new selections              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Preview Update                            │
│        - useMemo recalculates HTML                          │
│        - Only selected items shown                          │
└─────────────────────────────────────────────────────────────┘
```

## Hierarchical Checkbox Behavior

### Work Experience Hierarchy

```
Company Checkbox
├── Position 1 Checkbox
│   ├── Bullet 1 Checkbox
│   ├── Bullet 2 Checkbox
│   └── Bullet 3 Checkbox
└── Position 2 Checkbox
    ├── Bullet 1 Checkbox
    └── Bullet 2 Checkbox
```

**Rules**:
1. Unchecking Company → unchecks all positions and bullets
2. Unchecking Position → unchecks all bullets in that position
3. Unchecking one bullet → position shows indeterminate (dash)
4. Unchecking all bullets → position automatically unchecks
5. If any position has selected bullets → company shows indeterminate
6. If no positions have selected bullets → company automatically unchecks

### Projects Hierarchy

```
Project Checkbox
├── Highlight 1 Checkbox
├── Highlight 2 Checkbox
└── Highlight 3 Checkbox
```

**Rules**:
1. Unchecking Project → unchecks all highlights
2. Unchecking one highlight → project shows indeterminate
3. Unchecking all highlights → project automatically unchecks

## Testing Checklist

- [ ] Dev server is running
- [ ] Application loads without errors
- [ ] Master view shows all content with disabled checkboxes
- [ ] Can create a new version
- [ ] Section checkboxes work (sidebar)
- [ ] Company checkboxes work (work experience)
- [ ] Position checkboxes work (work experience)
- [ ] Bullet checkboxes work (work experience)
- [ ] Education checkboxes work
- [ ] Skills checkboxes work
- [ ] Project checkboxes work
- [ ] Highlight checkboxes work (projects)
- [ ] Awards checkboxes work
- [ ] Certifications checkboxes work
- [ ] Indeterminate states display correctly
- [ ] Preview updates immediately
- [ ] Selections persist when switching versions
- [ ] Master view remains read-only
- [ ] No console errors

## Common Questions

### Q: Why can't I click checkboxes?
**A**: You're probably in Master view. Create a version first (click "+ New" button).

### Q: Why does clicking a checkbox also collapse the section?
**A**: This was the original issue. It's now fixed with `stopPropagation()`.

### Q: What does the dash/minus symbol mean?
**A**: Indeterminate state - some children are selected, but not all.

### Q: Can I edit the Master?
**A**: No, Master is read-only. It's the source of truth. Create versions to customize.

### Q: Where are versions saved?
**A**: In your browser's localStorage. They persist between sessions.

### Q: How do I delete a version?
**A**: Select the version, click the three-dot menu (⋮), then "Delete".

## Troubleshooting

### Issue: Checkboxes don't respond
**Solution**: Make sure you've created a version (not in Master view)

### Issue: Preview doesn't update
**Solution**: Check browser console for errors, try hard refresh (Ctrl+Shift+R)

### Issue: Selections don't persist
**Solution**: Check if localStorage is enabled in your browser

### Issue: Build fails
**Solution**: Run `npm install` and ensure Node.js 20.19+ is active

## Next Steps

1. **Test thoroughly** using the checklist above
2. **Create multiple versions** for different resume variants
3. **Verify preview output** matches your expectations
4. **Report any issues** found during testing

## Support Files

Additional documentation available:
- `/tmp/IMPLEMENTATION_SUMMARY.md` - Detailed technical documentation
- `/tmp/CHECKBOX_TEST_GUIDE.md` - Comprehensive test scenarios
- `/tmp/test-checkbox-ui.html` - Standalone checkbox test page

## Ready to Test!

The application is fully functional and ready for testing. Simply:

1. Open http://localhost:5173/
2. Create a version
3. Start clicking checkboxes
4. Watch the preview update in real-time

**The checkbox functionality is working!** 🎉
