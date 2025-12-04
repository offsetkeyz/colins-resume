import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ResumeData, ResumeVersion, SelectionState } from '../types/resume';
import { createDefaultSelections, cloneSelections, generateId } from '../utils/yaml-loader';

interface ResumeStore {
  // Resume data (loaded from YAML)
  resumeData: ResumeData | null;
  isLoading: boolean;
  error: string | null;

  // Versions
  versions: ResumeVersion[];
  activeVersionId: string | null;

  // UI state
  previewOpen: boolean;
  selectedSection: string | null;

  // Actions
  setResumeData: (data: ResumeData) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Version actions
  createVersion: (name: string, description?: string, basedOn?: string) => void;
  deleteVersion: (id: string) => void;
  setActiveVersion: (id: string | null) => void;
  renameVersion: (id: string, name: string) => void;
  duplicateVersion: (id: string, newName: string) => void;

  // Selection actions
  getCurrentSelections: () => SelectionState | null;
  updateSelections: (updater: (selections: SelectionState) => void) => void;

  // Section toggle
  toggleSection: (sectionId: keyof SelectionState['sections']) => void;

  // Work experience toggles
  toggleCompany: (company: string) => void;
  togglePosition: (company: string, positionIndex: number) => void;
  toggleBullet: (company: string, positionIndex: number, bulletIndex: number) => void;

  // Simple item toggles
  toggleEducation: (index: number) => void;
  toggleAward: (index: number) => void;
  toggleCertification: (index: number) => void;
  toggleSkill: (index: number) => void;
  toggleProject: (index: number) => void;
  toggleProjectHighlight: (projectIndex: number, highlightIndex: number) => void;

  // UI actions
  setPreviewOpen: (open: boolean) => void;
  setSelectedSection: (section: string | null) => void;

  // Initialization
  initializeWithData: (data: ResumeData) => void;
}

// Master version is a virtual version that represents all items selected
const MASTER_ID = 'master';

export const useResumeStore = create<ResumeStore>()(
  persist(
    (set, get) => ({
      // Initial state
      resumeData: null,
      isLoading: true,
      error: null,
      versions: [],
      activeVersionId: null, // null means "Master"
      previewOpen: true,
      selectedSection: null,

      // Basic setters
      setResumeData: (data) => set({ resumeData: data }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),

      // Initialize store with resume data
      initializeWithData: (data) => {
        set({
          resumeData: data,
          isLoading: false,
          error: null
        });
      },

      // Version management
      createVersion: (name, description, basedOn = MASTER_ID) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        let baseSelections: SelectionState;

        if (basedOn === MASTER_ID) {
          // Start with everything selected
          baseSelections = createDefaultSelections(resumeData);
        } else {
          // Clone from another version
          const baseVersion = versions.find((v) => v.id === basedOn);
          if (baseVersion) {
            baseSelections = cloneSelections(baseVersion.selections);
          } else {
            baseSelections = createDefaultSelections(resumeData);
          }
        }

        const newVersion: ResumeVersion = {
          id: generateId(),
          name,
          description,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          basedOn,
          selections: baseSelections,
        };

        set({
          versions: [...versions, newVersion],
          activeVersionId: newVersion.id,
        });
      },

      deleteVersion: (id) => {
        const { versions, activeVersionId } = get();
        const newVersions = versions.filter((v) => v.id !== id);

        set({
          versions: newVersions,
          activeVersionId: activeVersionId === id ? null : activeVersionId,
        });
      },

      setActiveVersion: (id) => set({ activeVersionId: id }),

      renameVersion: (id, name) => {
        const { versions } = get();
        set({
          versions: versions.map((v) =>
            v.id === id ? { ...v, name, updatedAt: new Date().toISOString() } : v
          ),
        });
      },

      duplicateVersion: (id, newName) => {
        const { versions, resumeData } = get();
        if (!resumeData) return;

        const sourceVersion = versions.find((v) => v.id === id);
        if (!sourceVersion) return;

        const newVersion: ResumeVersion = {
          id: generateId(),
          name: newName,
          description: sourceVersion.description,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          basedOn: sourceVersion.id,
          selections: cloneSelections(sourceVersion.selections),
        };

        set({
          versions: [...versions, newVersion],
          activeVersionId: newVersion.id,
        });
      },

      // Get current selections (Master = all selected, or version selections)
      getCurrentSelections: () => {
        const { resumeData, versions, activeVersionId } = get();
        if (!resumeData) return null;

        if (activeVersionId === null) {
          // Master view - everything selected
          return createDefaultSelections(resumeData);
        }

        const version = versions.find((v) => v.id === activeVersionId);
        return version?.selections ?? createDefaultSelections(resumeData);
      },

      // Update selections for current version
      updateSelections: (updater) => {
        const { versions, activeVersionId, resumeData } = get();

        // Can't modify Master
        if (activeVersionId === null || !resumeData) return;

        set({
          versions: versions.map((v) => {
            if (v.id === activeVersionId) {
              const newSelections = cloneSelections(v.selections);
              updater(newSelections);
              return {
                ...v,
                selections: newSelections,
                updatedAt: new Date().toISOString(),
              };
            }
            return v;
          }),
        });
      },

      // Toggle helpers
      toggleSection: (sectionId) => {
        get().updateSelections((s) => {
          s.sections[sectionId] = !s.sections[sectionId];
        });
      },

      toggleCompany: (company) => {
        get().updateSelections((s) => {
          const current = s.workExperience[company];
          if (!current) return;

          const newSelected = !current.selected;
          current.selected = newSelected;

          // Also update all positions and bullets
          Object.values(current.positions).forEach((pos) => {
            pos.selected = newSelected;
            pos.bullets = pos.bullets.map(() => newSelected);
          });
        });
      },

      togglePosition: (company, positionIndex) => {
        get().updateSelections((s) => {
          const pos = s.workExperience[company]?.positions[positionIndex];
          if (!pos) return;

          const newSelected = !pos.selected;
          pos.selected = newSelected;
          pos.bullets = pos.bullets.map(() => newSelected);

          // Update company selected state based on positions
          const companyData = s.workExperience[company];
          const anyPositionSelected = Object.values(companyData.positions).some(
            (p) => p.selected
          );
          companyData.selected = anyPositionSelected;
        });
      },

      toggleBullet: (company, positionIndex, bulletIndex) => {
        get().updateSelections((s) => {
          const pos = s.workExperience[company]?.positions[positionIndex];
          if (!pos || pos.bullets[bulletIndex] === undefined) return;

          pos.bullets[bulletIndex] = !pos.bullets[bulletIndex];

          // Update position selected state based on bullets
          pos.selected = pos.bullets.some((b) => b);

          // Update company selected state based on positions
          const companyData = s.workExperience[company];
          companyData.selected = Object.values(companyData.positions).some(
            (p) => p.selected
          );
        });
      },

      toggleEducation: (index) => {
        get().updateSelections((s) => {
          s.education[index] = !s.education[index];
        });
      },

      toggleAward: (index) => {
        get().updateSelections((s) => {
          s.awards[index] = !s.awards[index];
        });
      },

      toggleCertification: (index) => {
        get().updateSelections((s) => {
          s.certifications[index] = !s.certifications[index];
        });
      },

      toggleSkill: (index) => {
        get().updateSelections((s) => {
          s.skills[index] = !s.skills[index];
        });
      },

      toggleProject: (index) => {
        get().updateSelections((s) => {
          const project = s.projects[index];
          if (!project) return;

          const newSelected = !project.selected;
          project.selected = newSelected;
          project.highlights = project.highlights.map(() => newSelected);
        });
      },

      toggleProjectHighlight: (projectIndex, highlightIndex) => {
        get().updateSelections((s) => {
          const project = s.projects[projectIndex];
          if (!project || project.highlights[highlightIndex] === undefined) return;

          project.highlights[highlightIndex] = !project.highlights[highlightIndex];
          project.selected = project.highlights.some((h) => h);
        });
      },

      // UI state
      setPreviewOpen: (open) => set({ previewOpen: open }),
      setSelectedSection: (section) => set({ selectedSection: section }),
    }),
    {
      name: 'resume-builder-storage',
      partialize: (state) => ({
        versions: state.versions,
        activeVersionId: state.activeVersionId,
        previewOpen: state.previewOpen,
      }),
    }
  )
);
