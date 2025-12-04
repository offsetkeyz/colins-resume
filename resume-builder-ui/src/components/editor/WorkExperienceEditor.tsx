import { useResumeStore } from '../../store/resume-store';
import CollapsibleSection from '../shared/CollapsibleSection';

interface WorkExperienceEditorProps {
  isReadOnly: boolean;
}

export default function WorkExperienceEditor({ isReadOnly }: WorkExperienceEditorProps) {
  const {
    resumeData,
    getCurrentSelections,
    toggleCompany,
    togglePosition,
    toggleBullet,
  } = useResumeStore();

  const selections = getCurrentSelections();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Work Experience</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {Object.entries(resumeData.work_experience).map(([company, positions]) => {
          const companySelection = selections.workExperience[company];
          if (!companySelection) return null;

          // Calculate indeterminate state for company
          const allPositionsSelected = Object.values(companySelection.positions).every(
            (p) => p.selected && p.bullets.every((b) => b)
          );
          const somePositionsSelected = Object.values(companySelection.positions).some(
            (p) => p.selected || p.bullets.some((b) => b)
          );
          const companyIndeterminate = somePositionsSelected && !allPositionsSelected;

          return (
            <CollapsibleSection
              key={company}
              title={company}
              defaultOpen={true}
              checkbox={{
                checked: companySelection.selected,
                indeterminate: companyIndeterminate,
                onChange: () => toggleCompany(company),
                disabled: isReadOnly,
              }}
            >
              {positions.map((position, posIndex) => {
                const posSelection = companySelection.positions[posIndex];
                if (!posSelection) return null;

                // Calculate indeterminate state for position
                const allBulletsSelected = posSelection.bullets.every((b) => b);
                const someBulletsSelected = posSelection.bullets.some((b) => b);
                const positionIndeterminate = someBulletsSelected && !allBulletsSelected;

                return (
                  <CollapsibleSection
                    key={`${company}-${posIndex}`}
                    title={position.job_title}
                    metadata={`${position.start_date} - ${position.end_date}`}
                    level={1}
                    defaultOpen={posIndex === 0}
                    checkbox={{
                      checked: posSelection.selected,
                      indeterminate: positionIndeterminate,
                      onChange: () => togglePosition(company, posIndex),
                      disabled: isReadOnly,
                    }}
                  >
                    <div className="ml-12 pr-4 space-y-2">
                      <p className="text-xs text-gray-500 mb-2">
                        📍 {position.location}
                      </p>
                      {position.responsibilities.map((resp, bulletIdx) => (
                        <div
                          key={bulletIdx}
                          className="flex items-start gap-3 py-1"
                        >
                          <input
                            type="checkbox"
                            checked={posSelection.bullets[bulletIdx] ?? false}
                            onChange={(e) => {
                              e.stopPropagation();
                              toggleBullet(company, posIndex, bulletIdx);
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
                              posSelection.bullets[bulletIdx]
                                ? 'text-gray-700'
                                : 'text-gray-400'
                            }`}
                          >
                            {resp.description}
                          </span>
                          {resp.include_in && resp.include_in.length > 0 && (
                            <span className="flex-shrink-0 text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                              {resp.include_in.join(', ')}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </CollapsibleSection>
                );
              })}
            </CollapsibleSection>
          );
        })}
      </div>
    </div>
  );
}
