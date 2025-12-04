import { useResumeStore } from '../../store/resume-store';
import CollapsibleSection from '../shared/CollapsibleSection';

interface ProjectsEditorProps {
  isReadOnly: boolean;
}

export default function ProjectsEditor({ isReadOnly }: ProjectsEditorProps) {
  const {
    resumeData,
    getCurrentSelections,
    toggleProject,
    toggleProjectHighlight,
  } = useResumeStore();

  const selections = getCurrentSelections();

  if (!resumeData || !selections) return null;

  return (
    <div>
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

          return (
            <CollapsibleSection
              key={index}
              title={project.name}
              metadata={project.startDate}
              defaultOpen={index === 0}
              checkbox={{
                checked: projSelection.selected,
                indeterminate: projectIndeterminate,
                onChange: () => toggleProject(index),
                disabled: isReadOnly,
              }}
            >
              <div className="ml-12 pr-4">
                <p className="text-sm text-gray-600 mb-3">{project.description}</p>

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
                  {project.highlights.map((highlight, hIdx) => (
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
                      <span
                        className={`text-sm leading-relaxed ${
                          projSelection.highlights[hIdx]
                            ? 'text-gray-700'
                            : 'text-gray-400'
                        }`}
                      >
                        {highlight.description}
                      </span>
                      {highlight.include_in && highlight.include_in.length > 0 && (
                        <span className="flex-shrink-0 text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                          {highlight.include_in.join(', ')}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CollapsibleSection>
          );
        })}
      </div>
    </div>
  );
}
