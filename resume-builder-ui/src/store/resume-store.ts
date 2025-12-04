import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ResumeData, ResumeVersion, SelectionState, TextOverride, TextOverrides } from '../types/resume';
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

  // Text override actions
  getCurrentTextOverrides: () => TextOverrides | null;
  setTextOverride: (path: string, value: string, indices: Record<string, string | number>) => void;
  removeTextOverride: (path: string, indices: Record<string, string | number>) => void;
  pushOverrideToMaster: (path: string, value: string, indices: Record<string, string | number>) => void;

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

  // Add new items to master data
  addEducation: (newEducation: Omit<ResumeData['education'][0], 'include_in'>) => void;
  addCompany: (companyName: string) => void;
  addPosition: (company: string, newPosition: Omit<ResumeData['work_experience'][string][0], 'include_in'>) => void;
  addProject: (newProject: Omit<ResumeData['projects'][0], 'include_in'>) => void;
  addSkill: (newSkill: Omit<ResumeData['specialty_skills'][0], 'include_in'>) => void;
  addAward: (newAward: Omit<ResumeData['awards'][0], 'include_in'>) => void;
  addCertification: (newCert: Omit<ResumeData['certifications'][0], 'include_in'>) => void;
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

      // Text override methods
      getCurrentTextOverrides: () => {
        const { versions, activeVersionId } = get();
        if (activeVersionId === null) return null; // Master has no overrides

        const version = versions.find((v) => v.id === activeVersionId);
        return version?.textOverrides ?? null;
      },

      setTextOverride: (path, value, indices) => {
        const { versions, activeVersionId, resumeData } = get();

        // Can't modify Master
        if (activeVersionId === null || !resumeData) return;

        set({
          versions: versions.map((v) => {
            if (v.id === activeVersionId) {
              const newOverrides = { ...v.textOverrides };

              // Build the nested path
              const override: TextOverride = {
                value,
                lastModified: new Date().toISOString(),
              };

              // Parse path and set override (e.g., 'workExperience.bullets')
              const parts = path.split('.');
              const section = parts[0] as keyof TextOverrides;

              if (!newOverrides[section]) {
                newOverrides[section] = {} as any;
              }

              // Handle different section structures
              if (section === 'workExperience') {
                const company = indices.company as string;
                const field = parts[1];

                if (!newOverrides.workExperience![company]) {
                  newOverrides.workExperience![company] = {};
                }

                if (field === 'company_name') {
                  // Special handling for company name override
                  (newOverrides.workExperience![company] as any).company_name = override;
                } else {
                  // Position-level overrides
                  const positionIndex = indices.positionIndex as number;
                  if (!newOverrides.workExperience![company][positionIndex]) {
                    newOverrides.workExperience![company][positionIndex] = {};
                  }

                  if (field === 'bullets') {
                    const bulletIndex = indices.bulletIndex as number;
                    if (!newOverrides.workExperience![company][positionIndex].bullets) {
                      newOverrides.workExperience![company][positionIndex].bullets = {};
                    }
                    newOverrides.workExperience![company][positionIndex].bullets![bulletIndex] = override;
                  } else {
                    (newOverrides.workExperience![company][positionIndex] as any)[field] = override;
                  }
                }
              } else if (section === 'education' || section === 'projects' || section === 'skills' ||
                         section === 'awards' || section === 'certifications') {
                const index = indices.index as number;
                const field = parts[1];

                if (!(newOverrides[section] as any)[index]) {
                  (newOverrides[section] as any)[index] = {};
                }

                if (field === 'highlights' || field === 'bullets' || field === 'keywords') {
                  const subIndex = indices.subIndex as number;
                  if (!(newOverrides[section] as any)[index][field]) {
                    (newOverrides[section] as any)[index][field] = {};
                  }
                  (newOverrides[section] as any)[index][field][subIndex] = override;
                } else {
                  (newOverrides[section] as any)[index][field] = override;
                }
              } else if (section === 'basics') {
                const field = parts[1];
                if (!newOverrides.basics) {
                  newOverrides.basics = {};
                }
                (newOverrides.basics as any)[field] = override;
              }

              return {
                ...v,
                textOverrides: newOverrides,
                updatedAt: new Date().toISOString(),
              };
            }
            return v;
          }),
        });
      },

      removeTextOverride: (path, indices) => {
        const { versions, activeVersionId } = get();

        if (activeVersionId === null) return;

        set({
          versions: versions.map((v) => {
            if (v.id === activeVersionId && v.textOverrides) {
              const newOverrides = { ...v.textOverrides };
              const parts = path.split('.');
              const section = parts[0] as keyof TextOverrides;

              // Remove the override by deleting the property
              if (section === 'workExperience') {
                const company = indices.company as string;
                const field = parts[1];

                if (field === 'company_name') {
                  // Remove company name override
                  delete (newOverrides.workExperience?.[company] as any)?.company_name;
                } else {
                  // Remove position-level overrides
                  const positionIndex = indices.positionIndex as number;
                  if (newOverrides.workExperience?.[company]?.[positionIndex]) {
                    if (field === 'bullets') {
                      const bulletIndex = indices.bulletIndex as number;
                      delete newOverrides.workExperience[company][positionIndex].bullets?.[bulletIndex];
                    } else {
                      delete (newOverrides.workExperience[company][positionIndex] as any)[field];
                    }
                  }
                }
              } else if (section === 'education' || section === 'projects' || section === 'skills' ||
                         section === 'awards' || section === 'certifications') {
                const index = indices.index as number;
                const field = parts[1];

                if ((newOverrides[section] as any)?.[index]) {
                  if (field === 'highlights' || field === 'bullets' || field === 'keywords') {
                    const subIndex = indices.subIndex as number;
                    delete (newOverrides[section] as any)[index][field]?.[subIndex];
                  } else {
                    delete (newOverrides[section] as any)[index][field];
                  }
                }
              } else if (section === 'basics' && newOverrides.basics) {
                const field = parts[1];
                delete (newOverrides.basics as any)[field];
              }

              return {
                ...v,
                textOverrides: newOverrides,
                updatedAt: new Date().toISOString(),
              };
            }
            return v;
          }),
        });
      },

      pushOverrideToMaster: (path, value, indices) => {
        const { resumeData } = get();

        if (!resumeData) return;

        // Update the master data
        const parts = path.split('.');
        const section = parts[0];

        if (section === 'workExperience') {
          const company = indices.company as string;
          const field = parts[1];

          if (field === 'company_name') {
            // Company names are object keys, so we can't rename them in-place
            // This would require complex logic to rename keys in the work_experience object
            // For now, we'll just log a warning
            console.warn('Cannot push company name to master - company names are object keys');
          } else {
            const positionIndex = indices.positionIndex as number;
            if (field === 'bullets') {
              const bulletIndex = indices.bulletIndex as number;
              if (resumeData.work_experience[company]?.[positionIndex]?.responsibilities[bulletIndex]) {
                resumeData.work_experience[company][positionIndex].responsibilities[bulletIndex].description = value;
              }
            } else {
              if (resumeData.work_experience[company]?.[positionIndex]) {
                (resumeData.work_experience[company][positionIndex] as any)[field] = value;
              }
            }
          }
        } else if (section === 'education') {
          const index = indices.index as number;
          const field = parts[1];
          if (resumeData.education[index]) {
            if (field === 'courses') {
              // Convert comma-separated string to array
              resumeData.education[index].courses = value
                .split(',')
                .map((c) => c.trim())
                .filter((c) => c.length > 0);
            } else {
              (resumeData.education[index] as any)[field] = value;
            }
          }
        } else if (section === 'projects') {
          const index = indices.index as number;
          const field = parts[1];

          if (field === 'highlights') {
            const highlightIndex = indices.subIndex as number;
            if (resumeData.projects[index]?.highlights[highlightIndex]) {
              resumeData.projects[index].highlights[highlightIndex].description = value;
            }
          } else {
            if (resumeData.projects[index]) {
              (resumeData.projects[index] as any)[field] = value;
            }
          }
        } else if (section === 'skills') {
          const index = indices.index as number;
          const field = parts[1];

          if (field === 'keywords') {
            const keywordIndex = indices.subIndex as number;
            if (resumeData.specialty_skills[index]?.keywords[keywordIndex] !== undefined) {
              resumeData.specialty_skills[index].keywords[keywordIndex] = value;
            }
          } else {
            if (resumeData.specialty_skills[index]) {
              (resumeData.specialty_skills[index] as any)[field] = value;
            }
          }
        } else if (section === 'awards') {
          const index = indices.index as number;
          const field = parts[1];
          if (resumeData.awards[index]) {
            (resumeData.awards[index] as any)[field] = value;
          }
        } else if (section === 'certifications') {
          const index = indices.index as number;
          const field = parts[1];
          if (resumeData.certifications[index]) {
            (resumeData.certifications[index] as any)[field] = value;
          }
        } else if (section === 'basics') {
          const field = parts[1];
          (resumeData.basics as any)[field] = value;
        }

        set({ resumeData: { ...resumeData } });
      },

      // UI state
      setPreviewOpen: (open) => set({ previewOpen: open }),
      setSelectedSection: (section) => set({ selectedSection: section }),

      // Add new items to master data
      addEducation: (newEducation) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        // Add include_in with all tags
        const educationWithTags = {
          ...newEducation,
          include_in: ['all'] as any,
        };

        // Add to resume data
        const updatedResumeData = {
          ...resumeData,
          education: [...resumeData.education, educationWithTags],
        };

        const newIndex = resumeData.education.length;

        // Update all versions to include the new item
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            education: {
              ...v.selections.education,
              [newIndex]: true,
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addCompany: (companyName) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        // Check if company already exists
        if (resumeData.work_experience[companyName]) {
          console.warn(`Company ${companyName} already exists`);
          return;
        }

        // Add empty company
        const updatedResumeData = {
          ...resumeData,
          work_experience: {
            ...resumeData.work_experience,
            [companyName]: [],
          },
        };

        // Update all versions to include the new company
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            workExperience: {
              ...v.selections.workExperience,
              [companyName]: {
                selected: true,
                positions: {},
              },
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addPosition: (company, newPosition) => {
        const { resumeData, versions } = get();
        if (!resumeData || !resumeData.work_experience[company]) return;

        // Add include_in tags to position and responsibilities
        const positionWithTags = {
          ...newPosition,
          include_in: ['all'] as any,
          responsibilities: newPosition.responsibilities.map((resp) => ({
            description: typeof resp === 'string' ? resp : resp.description,
            include_in: ['all'] as any,
          })),
        };

        const updatedPositions = [
          ...resumeData.work_experience[company],
          positionWithTags,
        ];

        const updatedResumeData = {
          ...resumeData,
          work_experience: {
            ...resumeData.work_experience,
            [company]: updatedPositions,
          },
        };

        const newPositionIndex = resumeData.work_experience[company].length;

        // Update all versions to include the new position
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            workExperience: {
              ...v.selections.workExperience,
              [company]: {
                selected: true,
                positions: {
                  ...v.selections.workExperience[company]?.positions,
                  [newPositionIndex]: {
                    selected: true,
                    bullets: positionWithTags.responsibilities.map(() => true),
                  },
                },
              },
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addProject: (newProject) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        // Add include_in tags
        const projectWithTags = {
          ...newProject,
          include_in: ['all'] as any,
          highlights: newProject.highlights.map((h) => ({
            description: typeof h === 'string' ? h : h.description,
            include_in: ['all'] as any,
          })),
        };

        const updatedResumeData = {
          ...resumeData,
          projects: [...resumeData.projects, projectWithTags],
        };

        const newIndex = resumeData.projects.length;

        // Update all versions to include the new project
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            projects: {
              ...v.selections.projects,
              [newIndex]: {
                selected: true,
                highlights: projectWithTags.highlights.map(() => true),
              },
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addSkill: (newSkill) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        const skillWithTags = {
          ...newSkill,
          include_in: ['all'] as any,
        };

        const updatedResumeData = {
          ...resumeData,
          specialty_skills: [...resumeData.specialty_skills, skillWithTags],
        };

        const newIndex = resumeData.specialty_skills.length;

        // Update all versions to include the new skill
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            skills: {
              ...v.selections.skills,
              [newIndex]: true,
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addAward: (newAward) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        const awardWithTags = {
          ...newAward,
          include_in: ['all'] as any,
        };

        const updatedResumeData = {
          ...resumeData,
          awards: [...resumeData.awards, awardWithTags],
        };

        const newIndex = resumeData.awards.length;

        // Update all versions to include the new award
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            awards: {
              ...v.selections.awards,
              [newIndex]: true,
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },

      addCertification: (newCert) => {
        const { resumeData, versions } = get();
        if (!resumeData) return;

        const certWithTags = {
          ...newCert,
          include_in: ['all'] as any,
        };

        const updatedResumeData = {
          ...resumeData,
          certifications: [...resumeData.certifications, certWithTags],
        };

        const newIndex = resumeData.certifications.length;

        // Update all versions to include the new certification
        const updatedVersions = versions.map((v) => ({
          ...v,
          selections: {
            ...v.selections,
            certifications: {
              ...v.selections.certifications,
              [newIndex]: true,
            },
          },
        }));

        set({
          resumeData: updatedResumeData,
          versions: updatedVersions,
        });
      },
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
