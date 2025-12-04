import { useResumeStore } from '../../store/resume-store';

interface SkillsEditorProps {
  isReadOnly: boolean;
}

export default function SkillsEditor({ isReadOnly }: SkillsEditorProps) {
  const { resumeData, getCurrentSelections, toggleSkill } = useResumeStore();
  const selections = getCurrentSelections();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Skills</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {resumeData.specialty_skills.map((skill, index) => {
          const isSelected = selections.skills[index] ?? true;

          return (
            <div
              key={index}
              className="flex items-start gap-3 px-6 py-4 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleSkill(index)}
                disabled={isReadOnly}
                className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                  isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                }`}
              />
              <div className={`flex-1 ${isSelected ? '' : 'opacity-50'}`}>
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-gray-900">{skill.name}</h3>
                  {skill.include_in && skill.include_in.length > 0 && (
                    <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                      {skill.include_in.join(', ')}
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {skill.keywords.map((keyword, kidx) => (
                    <span
                      key={kidx}
                      className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
