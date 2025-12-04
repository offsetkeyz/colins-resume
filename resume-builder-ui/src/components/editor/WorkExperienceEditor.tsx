import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import CollapsibleSection from '../shared/CollapsibleSection';
import EditableText from '../shared/EditableText';
import AddPositionModal from '../modals/AddPositionModal';
import AddCompanyModal from '../modals/AddCompanyModal';

interface WorkExperienceEditorProps {
  isReadOnly: boolean;
}

export default function WorkExperienceEditor({ isReadOnly }: WorkExperienceEditorProps) {
  const [showAddPositionModal, setShowAddPositionModal] = useState(false);
  const [showAddCompanyModal, setShowAddCompanyModal] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const {
    resumeData,
    getCurrentSelections,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
    toggleCompany,
    togglePosition,
    toggleBullet,
  } = useResumeStore();

  const selections = getCurrentSelections();
  const textOverrides = getCurrentTextOverrides();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <AddPositionModal
        open={showAddPositionModal}
        onClose={() => setShowAddPositionModal(false)}
        company={selectedCompany}
      />
      <AddCompanyModal
        open={showAddCompanyModal}
        onClose={() => setShowAddCompanyModal(false)}
      />

      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Work Experience</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {Object.entries(resumeData.work_experience).map(([company, positions]) => {
          const companySelection = selections.workExperience[company];
          if (!companySelection) return null;

          // Get company name override
          const companyOverrides = textOverrides?.workExperience?.[company];
          const companyName = companyOverrides?.company_name?.value ?? company;

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
              title={
                <EditableText
                  value={companyName}
                  onSave={(newValue) =>
                    setTextOverride('workExperience.company_name', newValue, { company })
                  }
                  onRevert={
                    companyOverrides?.company_name
                      ? () => removeTextOverride('workExperience.company_name', { company })
                      : undefined
                  }
                  onPushToMaster={
                    companyOverrides?.company_name
                      ? () =>
                          pushOverrideToMaster('workExperience.company_name', companyName, {
                            company,
                          })
                      : undefined
                  }
                  isModified={!!companyOverrides?.company_name}
                  isReadOnly={isReadOnly}
                  showEditIcon={true}
                />
              }
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

                // Get text overrides for this position
                const posOverrides = textOverrides?.workExperience?.[company]?.[posIndex];
                const jobTitle = posOverrides?.job_title?.value ?? position.job_title;
                const location = posOverrides?.location?.value ?? position.location;
                const startDate = posOverrides?.start_date?.value ?? position.start_date;
                const endDate = posOverrides?.end_date?.value ?? position.end_date;

                return (
                  <CollapsibleSection
                    key={`${company}-${posIndex}`}
                    title={
                      <EditableText
                        value={jobTitle}
                        onSave={(newValue) =>
                          setTextOverride('workExperience.job_title', newValue, {
                            company,
                            positionIndex: posIndex,
                          })
                        }
                        onRevert={
                          posOverrides?.job_title
                            ? () =>
                                removeTextOverride('workExperience.job_title', {
                                  company,
                                  positionIndex: posIndex,
                                })
                            : undefined
                        }
                        onPushToMaster={
                          posOverrides?.job_title
                            ? () =>
                                pushOverrideToMaster('workExperience.job_title', jobTitle, {
                                  company,
                                  positionIndex: posIndex,
                                })
                            : undefined
                        }
                        isModified={!!posOverrides?.job_title}
                        isReadOnly={isReadOnly}
                        showEditIcon={true}
                      />
                    }
                    metadata={
                      <>
                        <EditableText
                          value={startDate}
                          onSave={(newValue) =>
                            setTextOverride('workExperience.start_date', newValue, {
                              company,
                              positionIndex: posIndex,
                            })
                          }
                          onRevert={
                            posOverrides?.start_date
                              ? () =>
                                  removeTextOverride('workExperience.start_date', {
                                    company,
                                    positionIndex: posIndex,
                                  })
                              : undefined
                          }
                          onPushToMaster={
                            posOverrides?.start_date
                              ? () =>
                                  pushOverrideToMaster(
                                    'workExperience.start_date',
                                    startDate,
                                    {
                                      company,
                                      positionIndex: posIndex,
                                    }
                                  )
                              : undefined
                          }
                          isModified={!!posOverrides?.start_date}
                          isReadOnly={isReadOnly}
                          showEditIcon={true}
                        />
                        {' - '}
                        <EditableText
                          value={endDate}
                          onSave={(newValue) =>
                            setTextOverride('workExperience.end_date', newValue, {
                              company,
                              positionIndex: posIndex,
                            })
                          }
                          onRevert={
                            posOverrides?.end_date
                              ? () =>
                                  removeTextOverride('workExperience.end_date', {
                                    company,
                                    positionIndex: posIndex,
                                  })
                              : undefined
                          }
                          onPushToMaster={
                            posOverrides?.end_date
                              ? () =>
                                  pushOverrideToMaster('workExperience.end_date', endDate, {
                                    company,
                                    positionIndex: posIndex,
                                  })
                              : undefined
                          }
                          isModified={!!posOverrides?.end_date}
                          isReadOnly={isReadOnly}
                          showEditIcon={true}
                        />
                      </>
                    }
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
                      <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                        <span>📍</span>
                        <EditableText
                          value={location}
                          onSave={(newValue) =>
                            setTextOverride('workExperience.location', newValue, {
                              company,
                              positionIndex: posIndex,
                            })
                          }
                          onRevert={
                            posOverrides?.location
                              ? () =>
                                  removeTextOverride('workExperience.location', {
                                    company,
                                    positionIndex: posIndex,
                                  })
                              : undefined
                          }
                          onPushToMaster={
                            posOverrides?.location
                              ? () =>
                                  pushOverrideToMaster('workExperience.location', location, {
                                    company,
                                    positionIndex: posIndex,
                                  })
                              : undefined
                          }
                          isModified={!!posOverrides?.location}
                          isReadOnly={isReadOnly}
                          showEditIcon={true}
                          className="text-xs"
                        />
                      </div>

                      {position.responsibilities.map((resp, bulletIdx) => {
                        const bulletOverride = posOverrides?.bullets?.[bulletIdx];
                        const bulletText = bulletOverride?.value ?? resp.description;

                        return (
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
                            <div className="flex-1">
                              <EditableText
                                value={bulletText}
                                onSave={(newValue) =>
                                  setTextOverride('workExperience.bullets', newValue, {
                                    company,
                                    positionIndex: posIndex,
                                    bulletIndex: bulletIdx,
                                  })
                                }
                                onRevert={
                                  bulletOverride
                                    ? () =>
                                        removeTextOverride('workExperience.bullets', {
                                          company,
                                          positionIndex: posIndex,
                                          bulletIndex: bulletIdx,
                                        })
                                    : undefined
                                }
                                onPushToMaster={
                                  bulletOverride
                                    ? () =>
                                        pushOverrideToMaster(
                                          'workExperience.bullets',
                                          bulletText,
                                          {
                                            company,
                                            positionIndex: posIndex,
                                            bulletIndex: bulletIdx,
                                          }
                                        )
                                    : undefined
                                }
                                isModified={!!bulletOverride}
                                isReadOnly={isReadOnly}
                                multiline={true}
                                className={`text-sm leading-relaxed ${
                                  posSelection.bullets[bulletIdx]
                                    ? 'text-gray-700'
                                    : 'text-gray-400'
                                }`}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CollapsibleSection>
                );
              })}

              {!isReadOnly && (
                <div className="ml-12 pr-4 pt-2 pb-2">
                  <button
                    onClick={() => {
                      setSelectedCompany(company);
                      setShowAddPositionModal(true);
                    }}
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    Add Position
                  </button>
                </div>
              )}
            </CollapsibleSection>
          );
        })}
      </div>

      {!isReadOnly && (
        <div className="px-6 py-4 border-t border-gray-200">
          <button
            onClick={() => setShowAddCompanyModal(true)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Company
          </button>
        </div>
      )}
    </div>
  );
}
