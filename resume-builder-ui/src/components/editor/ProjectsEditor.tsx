import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import CollapsibleSection from '../shared/CollapsibleSection';
import EditableText from '../shared/EditableText';
import AddProjectModal from '../modals/AddProjectModal';

interface ProjectsEditorProps {
  isReadOnly: boolean;
}

export default function ProjectsEditor({ isReadOnly }: ProjectsEditorProps) {
  const [showAddModal, setShowAddModal] = useState(false);
  const {
    resumeData,
    getCurrentSelections,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
    toggleProject,
    toggleProjectHighlight,
  } = useResumeStore();

  const selections = getCurrentSelections();
  const textOverrides = getCurrentTextOverrides();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <AddProjectModal open={showAddModal} onClose={() => setShowAddModal(false)} />

      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Projects</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {resumeData.projects.map((project, index) => {
          const projSelection = selections.projects[index];
          if (!projSelection) return null;

          // Calculate indeterminate state
          const allHighlightsSelected = projSelection.highlights.every((h) => h);
          const someHighlightsSelected = projSelection.highlights.some((h) => h);
          const projectIndeterminate = someHighlightsSelected && !allHighlightsSelected;

          // Get text overrides for this project
          const projOverrides = textOverrides?.projects?.[index];
          const projectName = projOverrides?.name?.value ?? project.name;
          const projectDesc = projOverrides?.description?.value ?? project.description;
          const startDate = projOverrides?.startDate?.value ?? project.startDate;

          return (
            <CollapsibleSection
              key={index}
              title={
                <EditableText
                  value={projectName}
                  onSave={(newValue) =>
                    setTextOverride('projects.name', newValue, { index })
                  }
                  onRevert={
                    projOverrides?.name
                      ? () => removeTextOverride('projects.name', { index })
                      : undefined
                  }
                  onPushToMaster={
                    projOverrides?.name
                      ? () => pushOverrideToMaster('projects.name', projectName, { index })
                      : undefined
                  }
                  isModified={!!projOverrides?.name}
                  isReadOnly={isReadOnly}
                  showEditIcon={true}
                />
              }
              metadata={
                <EditableText
                  value={startDate}
                  onSave={(newValue) =>
                    setTextOverride('projects.startDate', newValue, { index })
                  }
                  onRevert={
                    projOverrides?.startDate
                      ? () => removeTextOverride('projects.startDate', { index })
                      : undefined
                  }
                  onPushToMaster={
                    projOverrides?.startDate
                      ? () => pushOverrideToMaster('projects.startDate', startDate, { index })
                      : undefined
                  }
                  isModified={!!projOverrides?.startDate}
                  isReadOnly={isReadOnly}
                  showEditIcon={true}
                />
              }
              defaultOpen={index === 0}
              checkbox={{
                checked: projSelection.selected,
                indeterminate: projectIndeterminate,
                onChange: () => toggleProject(index),
                disabled: isReadOnly,
              }}
            >
              <div className="ml-12 pr-4">
                <div className="text-sm text-gray-600 mb-3">
                  <EditableText
                    value={projectDesc}
                    onSave={(newValue) =>
                      setTextOverride('projects.description', newValue, { index })
                    }
                    onRevert={
                      projOverrides?.description
                        ? () => removeTextOverride('projects.description', { index })
                        : undefined
                    }
                    onPushToMaster={
                      projOverrides?.description
                        ? () =>
                            pushOverrideToMaster('projects.description', projectDesc, {
                              index,
                            })
                        : undefined
                    }
                    isModified={!!projOverrides?.description}
                    isReadOnly={isReadOnly}
                    multiline={true}
                    showEditIcon={true}
                  />
                </div>

                {project.url && (
                  <a
                    href={project.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline mb-3 inline-block"
                  >
                    🔗 {project.url}
                  </a>
                )}

                {project.keywords && project.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {project.keywords.map((kw, kidx) => (
                      <span
                        key={kidx}
                        className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                )}

                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-500 uppercase">Highlights</p>
                  {project.highlights.map((highlight, hIdx) => {
                    const highlightOverride = projOverrides?.highlights?.[hIdx];
                    const highlightText = highlightOverride?.value ?? highlight.description;

                    return (
                      <div key={hIdx} className="flex items-start gap-3 py-1">
                        <input
                          type="checkbox"
                          checked={projSelection.highlights[hIdx] ?? false}
                          onChange={(e) => {
                            e.stopPropagation();
                            toggleProjectHighlight(index, hIdx);
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                          }}
                          disabled={isReadOnly}
                          className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0 ${
                            isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                          }`}
                        />
                        <div className="flex-1">
                          <EditableText
                            value={highlightText}
                            onSave={(newValue) =>
                              setTextOverride('projects.highlights', newValue, {
                                index,
                                subIndex: hIdx,
                              })
                            }
                            onRevert={
                              highlightOverride
                                ? () =>
                                    removeTextOverride('projects.highlights', {
                                      index,
                                      subIndex: hIdx,
                                    })
                                : undefined
                            }
                            onPushToMaster={
                              highlightOverride
                                ? () =>
                                    pushOverrideToMaster('projects.highlights', highlightText, {
                                      index,
                                      subIndex: hIdx,
                                    })
                                : undefined
                            }
                            isModified={!!highlightOverride}
                            isReadOnly={isReadOnly}
                            multiline={true}
                            className={`text-sm leading-relaxed ${
                              projSelection.highlights[hIdx]
                                ? 'text-gray-700'
                                : 'text-gray-400'
                            }`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CollapsibleSection>
          );
        })}
      </div>

      {!isReadOnly && (
        <div className="px-6 py-4 border-t border-gray-200">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Project
          </button>
        </div>
      )}
    </div>
  );
}
