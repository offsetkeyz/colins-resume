import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import EditableText from '../shared/EditableText';
import AddSkillModal from '../modals/AddSkillModal';

interface SkillsEditorProps {
  isReadOnly: boolean;
}

export default function SkillsEditor({ isReadOnly }: SkillsEditorProps) {
  const [showAddModal, setShowAddModal] = useState(false);
  const {
    resumeData,
    getCurrentSelections,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
    toggleSkill,
  } = useResumeStore();
  const selections = getCurrentSelections();
  const textOverrides = getCurrentTextOverrides();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <AddSkillModal open={showAddModal} onClose={() => setShowAddModal(false)} />

      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Skills</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {resumeData.specialty_skills.map((skill, index) => {
          const isSelected = selections.skills[index] ?? true;

          // Get text overrides
          const skillOverrides = textOverrides?.skills?.[index];
          const skillName = skillOverrides?.name?.value ?? skill.name;

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
                  toggleSkill(index);
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
                <h3 className="font-medium text-gray-900">
                  <EditableText
                    value={skillName}
                    onSave={(newValue) =>
                      setTextOverride('skills.name', newValue, { index })
                    }
                    onRevert={
                      skillOverrides?.name
                        ? () => removeTextOverride('skills.name', { index })
                        : undefined
                    }
                    onPushToMaster={
                      skillOverrides?.name
                        ? () => pushOverrideToMaster('skills.name', skillName, { index })
                        : undefined
                    }
                    isModified={!!skillOverrides?.name}
                    isReadOnly={isReadOnly}
                    showEditIcon={true}
                  />
                </h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  {skill.keywords.map((keyword, kidx) => {
                    const keywordOverride = skillOverrides?.keywords?.[kidx];
                    const keywordText = keywordOverride?.value ?? keyword;

                    return (
                      <span
                        key={kidx}
                        className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm inline-flex items-center gap-1"
                      >
                        <EditableText
                          value={keywordText}
                          onSave={(newValue) =>
                            setTextOverride('skills.keywords', newValue, {
                              index,
                              subIndex: kidx,
                            })
                          }
                          onRevert={
                            keywordOverride
                              ? () =>
                                  removeTextOverride('skills.keywords', {
                                    index,
                                    subIndex: kidx,
                                  })
                              : undefined
                          }
                          onPushToMaster={
                            keywordOverride
                              ? () =>
                                  pushOverrideToMaster('skills.keywords', keywordText, {
                                    index,
                                    subIndex: kidx,
                                  })
                              : undefined
                          }
                          isModified={!!keywordOverride}
                          isReadOnly={isReadOnly}
                          className="text-sm"
                        />
                      </span>
                    );
                  })}
                </div>
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
            Add Skill
          </button>
        </div>
      )}
    </div>
  );
}
