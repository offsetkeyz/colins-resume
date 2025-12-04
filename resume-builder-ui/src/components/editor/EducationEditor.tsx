import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import EditableText from '../shared/EditableText';
import AddEducationModal from '../modals/AddEducationModal';

interface EducationEditorProps {
  isReadOnly: boolean;
}

export default function EducationEditor({ isReadOnly }: EducationEditorProps) {
  const [showAddModal, setShowAddModal] = useState(false);
  const {
    resumeData,
    getCurrentSelections,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
    toggleEducation,
  } = useResumeStore();
  const selections = getCurrentSelections();
  const textOverrides = getCurrentTextOverrides();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <AddEducationModal open={showAddModal} onClose={() => setShowAddModal(false)} />

      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Education</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {resumeData.education.map((edu, index) => {
          const isSelected = selections.education[index] ?? true;

          // Get text overrides
          const eduOverrides = textOverrides?.education?.[index];
          const institution = eduOverrides?.institution?.value ?? edu.institution;
          const area = eduOverrides?.area?.value ?? edu.area;
          const studyType = eduOverrides?.studyType?.value ?? edu.studyType;
          const startDate = eduOverrides?.startDate?.value ?? edu.startDate;
          const endDate = eduOverrides?.endDate?.value ?? edu.endDate;
          const score = eduOverrides?.score?.value ?? edu.score;
          const courses = eduOverrides?.courses?.value ?? (edu.courses?.join(', ') || '');

          return (
            <div
              key={index}
              className="flex items-start gap-3 px-6 py-4 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  e.stopPropagation();
                  toggleEducation(index);
                }}
                onClick={(e) => {
                  e.stopPropagation();
                }}
                disabled={isReadOnly}
                className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                  isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                }`}
              />
              <div className={`flex-1 ${isSelected ? '' : 'opacity-50'}`}>
                <div className="flex items-baseline justify-between">
                  <h3 className="font-medium text-gray-900 flex items-center gap-2">
                    <EditableText
                      value={studyType}
                      onSave={(newValue) =>
                        setTextOverride('education.studyType', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.studyType
                          ? () => removeTextOverride('education.studyType', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.studyType
                          ? () =>
                              pushOverrideToMaster('education.studyType', studyType, {
                                index,
                              })
                          : undefined
                      }
                      isModified={!!eduOverrides?.studyType}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                    />
                    <span> in </span>
                    <EditableText
                      value={area}
                      onSave={(newValue) =>
                        setTextOverride('education.area', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.area
                          ? () => removeTextOverride('education.area', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.area
                          ? () => pushOverrideToMaster('education.area', area, { index })
                          : undefined
                      }
                      isModified={!!eduOverrides?.area}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                    />
                  </h3>
                  <span className="text-sm text-gray-500">
                    <EditableText
                      value={startDate}
                      onSave={(newValue) =>
                        setTextOverride('education.startDate', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.startDate
                          ? () => removeTextOverride('education.startDate', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.startDate
                          ? () =>
                              pushOverrideToMaster('education.startDate', startDate, { index })
                          : undefined
                      }
                      isModified={!!eduOverrides?.startDate}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                    />
                    {' - '}
                    <EditableText
                      value={endDate}
                      onSave={(newValue) =>
                        setTextOverride('education.endDate', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.endDate
                          ? () => removeTextOverride('education.endDate', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.endDate
                          ? () =>
                              pushOverrideToMaster('education.endDate', endDate, { index })
                          : undefined
                      }
                      isModified={!!eduOverrides?.endDate}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                    />
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  <EditableText
                    value={institution}
                    onSave={(newValue) =>
                      setTextOverride('education.institution', newValue, { index })
                    }
                    onRevert={
                      eduOverrides?.institution
                        ? () => removeTextOverride('education.institution', { index })
                        : undefined
                    }
                    onPushToMaster={
                      eduOverrides?.institution
                        ? () =>
                            pushOverrideToMaster('education.institution', institution, {
                              index,
                            })
                        : undefined
                    }
                    isModified={!!eduOverrides?.institution}
                    isReadOnly={isReadOnly}
                    showEditIcon={true}
                  />
                </p>
                {score && (
                  <p className="text-sm text-gray-500">
                    GPA:{' '}
                    <EditableText
                      value={score}
                      onSave={(newValue) =>
                        setTextOverride('education.score', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.score
                          ? () => removeTextOverride('education.score', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.score
                          ? () => pushOverrideToMaster('education.score', score, { index })
                          : undefined
                      }
                      isModified={!!eduOverrides?.score}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                    />
                  </p>
                )}
                {(courses || !isReadOnly) && (
                  <p className="text-xs text-gray-400 mt-1">
                    Courses:{' '}
                    <EditableText
                      value={courses}
                      onSave={(newValue) =>
                        setTextOverride('education.courses', newValue, { index })
                      }
                      onRevert={
                        eduOverrides?.courses
                          ? () => removeTextOverride('education.courses', { index })
                          : undefined
                      }
                      onPushToMaster={
                        eduOverrides?.courses
                          ? () => pushOverrideToMaster('education.courses', courses, { index })
                          : undefined
                      }
                      isModified={!!eduOverrides?.courses}
                      isReadOnly={isReadOnly}
                      showEditIcon={true}
                      placeholder="Add courses (comma-separated)"
                    />
                  </p>
                )}
              </div>
            </div>
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
            Add Education
          </button>
        </div>
      )}
    </div>
  );
}
