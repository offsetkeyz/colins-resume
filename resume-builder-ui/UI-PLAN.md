# Resume Builder UI - Detailed Plan

## Overview

A web-based resume builder that adds **version management** (like Git branches) to your existing YAML-based resume system. Users can create custom resume variants by selecting/deselecting content from the master resume.

---

## Core Concepts

### Data Model

```
Master Resume (resume.yaml)
├── Contains ALL content
├── Single source of truth
└── Never modified by the UI (read-only)

Versions (stored in localStorage/JSON)
├── Named variants like "Technical Focus", "Leadership"
├── Store which items are selected/deselected
├── Can have text overrides (future)
└── Based on Master or other versions
```

### Version Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  "Master" = Everything selected (read-only view)            │
│                                                             │
│  User creates "Technical Focus" version from Master         │
│    → Starts with everything selected                        │
│    → User unchecks leadership-focused items                 │
│    → Selections saved to version                            │
│                                                             │
│  User creates "2-Page Resume" from "Technical Focus"        │
│    → Starts with Technical Focus selections                 │
│    → User removes more items to fit 2 pages                 │
└─────────────────────────────────────────────────────────────┘
```

---

## UI Layout (Three-Panel Design)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  📄 Resume Builder    [Version: ▼ Technical Focus ▾]  [+ New]  [👁 Preview]  │
├──────────────┬───────────────────────────────────────┬───────────────────────┤
│              │                                       │                       │
│   SIDEBAR    │         CONTENT EDITOR               │    LIVE PREVIEW       │
│   (200px)    │         (flexible)                   │    (400px, toggle)    │
│              │                                       │                       │
│ ☑ Basics     │  ┌─────────────────────────────────┐ │  ┌─────────────────┐  │
│ ☑ Experience │  │ WORK EXPERIENCE                 │ │  │                 │  │
│ ☑ Education  │  │                                 │ │  │  [Rendered      │  │
│ ☐ Awards     │  │ ▼ Arctic Wolf Networks          │ │  │   Resume]       │  │
│ ☑ Certs      │  │   ☑ Team Lead (2024-Present)    │ │  │                 │  │
│ ☑ Skills     │  │     ☑ Leadership philosophy...  │ │  │                 │  │
│ ☑ Projects   │  │     ☑ Reduced team backlog...   │ │  │                 │  │
│ ☐ Interests  │  │     ☐ Prioritized team...       │ │  │                 │  │
│              │  │   ☐ Security Developer          │ │  │                 │  │
│              │  │                                 │ │  │                 │  │
│              │  │ ▶ CarKey (collapsed)            │ │  │                 │  │
│              │  │ ▶ US Army (collapsed)           │ │  │                 │  │
│              │  └─────────────────────────────────┘ │  └─────────────────┘  │
│              │                                       │                       │
└──────────────┴───────────────────────────────────────┴───────────────────────┘
```

---

## Component Breakdown

### 1. Top Navigation Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📄 Resume Builder                                                          │
│                                                                             │
│  Version: [▼ Technical Focus      ]  [+ New Version]  [⋮ Menu]  [Preview 👁]│
│           └── Dropdown list:                                                │
│               • Master (read-only)                                          │
│               • Technical Focus ← active                                    │
│               • Leadership                                                  │
│               ─────────────────                                             │
│               + Create New Version                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Interactions:**
- Dropdown changes active version
- "Master" shows everything, checkboxes disabled
- "+ New Version" opens creation modal
- Menu (⋮) shows: Rename, Duplicate, Delete, Export
- Preview toggle shows/hides right panel

### 2. Section Sidebar (Left Panel)

```
┌──────────────────┐
│ SECTIONS         │
├──────────────────┤
│ ☑ 👤 Basics      │  ← Click checkbox to toggle entire section
│ ☑ 💼 Experience  │  ← Click label to scroll to section
│ ☑ 🎓 Education   │
│ ☐ 🏆 Awards      │  ← Unchecked = hidden from resume
│ ☑ 📜 Certs       │
│ ☑ 🛠 Skills      │
│ ☑ 📁 Projects    │
│ ☐ ❤️ Interests   │
├──────────────────┤
│ [+ Add Section]  │  ← Future: custom sections
└──────────────────┘
```

**Behaviors:**
- Checkbox toggles entire section visibility
- Label click scrolls content editor to that section
- Visual indicator for "active" section being edited
- Checkboxes disabled when viewing Master

### 3. Content Editor (Center Panel)

The main editing area with collapsible sections and hierarchical checkboxes.

#### Work Experience Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ WORK EXPERIENCE                                                    [+ Add]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ▼ ☑ Arctic Wolf Networks                                          [⋮]     │
│ ├─────────────────────────────────────────────────────────────────────────┤
│ │  ▼ ☑ Team Lead                                    Feb 2024 - Present    │
│ │  │    📍 Remote                                                         │
│ │  │                                                                      │
│ │  │    ☑ My leadership philosophy is centered on empowering each team    │
│ │  │      member to perform at their best...                              │
│ │  │                                                                      │
│ │  │    ☑ Reduced team backlog from over 300 tickets to 0...              │
│ │  │                                                                      │
│ │  │    ☐ Prioritized team happiness, health, and productivity...         │
│ │  │       └─ [leadership, management] tag                                │
│ │  │                                                                      │
│ │  │    [+ Add Bullet]                                                    │
│ │  └──────────────────────────────────────────────────────────────────────┤
│ │                                                                         │
│ │  ▶ ☐ Security Developer                           Nov 2022 - Feb 2024   │
│ │     └─ (collapsed, unchecked)                                           │
│ │                                                                         │
│ │  ▶ ☑ Business Analyst                             Dec 2021 - Nov 2022   │
│ │                                                                         │
│ └─────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ▶ ☑ CarKey                                                                 │
│ ▶ ☑ US Army                                                                │
│                                                                             │
│ [+ Add Company]                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Checkbox Hierarchy:**
- Company checkbox → toggles all positions & bullets
- Position checkbox → toggles all bullets in position
- Bullet checkbox → toggles individual bullet
- Indeterminate state (—) when partially selected

**Visual Elements:**
- Collapse/expand arrows (▼/▶)
- Include tags shown as subtle badges
- Dates and location displayed
- Hover reveals edit/delete actions

#### Skills Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SKILLS                                                             [+ Add]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ☑ Development                                                               │
│   Python • Unit Testing • CI/CD • Git • REST APIs • AWS Lambda • Docker     │
│                                                                             │
│ ☑ Cyber Security                                                            │
│   Detection Testing • Sigma • Forensics • Threat Hunting • MITRE ATT&CK    │
│                                                                             │
│ ☐ Leadership                                                                │
│   Team Building • Mentorship • Performance Management • Career Development  │
│   └─ [leadership, management] tag                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Projects Section

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PROJECTS                                                           [+ Add]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ▼ ☑ The Daily Decrypt                                                       │
│ │    A cybersecurity news podcast that simplifies complex...                │
│ │    🔗 youtube.com/@DailyDecrypt                                           │
│ │                                                                           │
│ │    Highlights:                                                            │
│ │    ☑ Created the podcast to fill a gap in short-form...                   │
│ │    ☑ Launched the podcast to stay informed about industry news...         │
│ │    ☐ Learned cloud hosting and security by managing...                    │
│ │      └─ [technical, development] tag                                      │
│ │                                                                           │
│ │    [+ Add Highlight]                                                      │
│ └───────────────────────────────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Live Preview (Right Panel)

```
┌────────────────────────────────────────┐
│ PREVIEW                      [🔗] [×]  │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────────────────────────┐  │
│  │                                  │  │
│  │       Colin McAllister           │  │
│  │         Team Lead                │  │
│  │                                  │  │
│  │  WORK EXPERIENCE                 │  │
│  │                                  │  │
│  │  Arctic Wolf Networks            │  │
│  │  Team Lead | 2024 - Present      │  │
│  │  • Leadership philosophy...      │  │
│  │  • Reduced team backlog...       │  │
│  │                                  │  │
│  │  ...                             │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                        │
├────────────────────────────────────────┤
│ Format: [Web ▼]  HTML | PDF | Markdown │
└────────────────────────────────────────┘
```

**Features:**
- Updates in real-time as selections change
- Format dropdown: Web (styled), PDF (print), Markdown
- "🔗" opens in new tab for full view
- "×" collapses panel to maximize editor space
- Scrollable within panel

---

## Modals & Dialogs

### Create Version Modal

```
┌─────────────────────────────────────────────────────────────────┐
│ Create New Version                                         [×]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Name:                                                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Technical Focus                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Description (optional):                                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Emphasizes technical skills and development experience    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Based on:                                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ ▼ Master (all items selected)                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│                                      [Cancel]  [Create Version] │
└─────────────────────────────────────────────────────────────────┘
```

### Confirm Delete Dialog

```
┌─────────────────────────────────────────────────────────────────┐
│ Delete Version?                                            [×]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Are you sure you want to delete "Technical Focus"?             │
│                                                                 │
│  This action cannot be undone.                                  │
│                                                                 │
│                                         [Cancel]  [Delete]      │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Management

### Data Flow

```
                    ┌─────────────────┐
                    │  resume.yaml    │ (Read-only, loaded once)
                    │  (Master data)  │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Zustand Store                              │
├─────────────────────────────────────────────────────────────────┤
│  resumeData: ResumeData    ← Loaded from YAML                   │
│  versions: Version[]       ← User-created versions              │
│  activeVersionId: string   ← Currently editing                  │
│                                                                 │
│  getCurrentSelections()    ← Returns active version's selections│
│  updateSelections()        ← Modify active version              │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  localStorage   │ (Persist versions)
                    └─────────────────┘
```

### Selection State Structure

```typescript
SelectionState {
  sections: {
    basics: boolean,
    work_experience: boolean,
    // ...
  },

  workExperience: {
    "Arctic Wolf Networks": {
      selected: boolean,
      positions: {
        0: { selected: boolean, bullets: [true, true, false, ...] },
        1: { selected: boolean, bullets: [...] },
      }
    }
  },

  education: { 0: true, 1: true, 2: false },
  awards: { 0: true, 1: false },
  // ...
}
```

---

## User Interactions Summary

| Action | Result |
|--------|--------|
| Select version from dropdown | Load version's selections, update preview |
| Click "+ New Version" | Open create modal |
| Check/uncheck in sidebar | Toggle entire section |
| Check/uncheck company | Toggle company + all positions/bullets |
| Check/uncheck position | Toggle position + all bullets |
| Check/uncheck bullet | Toggle single bullet, update parent states |
| Click collapse arrow | Expand/collapse section content |
| Click "Preview" button | Toggle preview panel visibility |
| Change preview format | Re-render preview in selected format |

---

## Phase 1 MVP Scope

### Included
- [ ] Version dropdown with Master + saved versions
- [ ] Create new version from Master
- [ ] Three-panel layout (sidebar, editor, preview)
- [ ] Hierarchical checkbox selection for all sections
- [ ] Real-time preview updates
- [ ] Persist versions to localStorage
- [ ] Collapse/expand for nested items

### Deferred to Phase 2
- [ ] Inline text editing
- [ ] Add new items (companies, positions, bullets)
- [ ] Drag-and-drop reordering
- [ ] Export to PDF
- [ ] Version comparison/diff view
- [ ] Merge changes to master YAML
- [ ] Collaborative editing

---

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Framework | React + TypeScript | Type safety, component model |
| Build | Vite | Fast dev server, good DX |
| Styling | Tailwind CSS | Rapid UI development |
| State | Zustand | Simple, lightweight |
| Icons | Lucide React | Clean, consistent icons |
| YAML | js-yaml | Parse resume.yaml |

---

## File Structure

```
resume-builder-ui/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TopNav.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── PreviewPanel.tsx
│   │   ├── editor/
│   │   │   ├── ContentEditor.tsx
│   │   │   ├── WorkExperienceEditor.tsx
│   │   │   ├── EducationEditor.tsx
│   │   │   ├── SkillsEditor.tsx
│   │   │   └── ProjectsEditor.tsx
│   │   ├── shared/
│   │   │   ├── Checkbox.tsx
│   │   │   ├── CheckboxTree.tsx
│   │   │   └── CollapsibleSection.tsx
│   │   └── modals/
│   │       ├── CreateVersionModal.tsx
│   │       └── ConfirmDialog.tsx
│   ├── store/
│   │   └── resume-store.ts
│   ├── types/
│   │   └── resume.ts
│   ├── utils/
│   │   └── yaml-loader.ts
│   ├── App.tsx
│   └── main.tsx
└── public/
    └── resume.yaml (copied or symlinked)
```

---

## Questions for Review

1. **Version storage**: localStorage (simple) vs. JSON files (can commit to git)?
2. **Preview format**: Start with HTML only, or include PDF from day 1?
3. **Edit capabilities**: Read-only selections first, or include editing?
4. **Integration**: Should versions update the actual YAML, or stay separate?
5. **Profiles**: Import existing profiles (technical, leadership) as versions?
