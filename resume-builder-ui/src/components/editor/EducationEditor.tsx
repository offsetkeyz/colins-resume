import { useResumeStore } from '../../store/resume-store';

interface EducationEditorProps {
  isReadOnly: boolean;
}

export default function EducationEditor({ isReadOnly }: EducationEditorProps) {
  const { resumeData, getCurrentSelections, toggleEducation } = useResumeStore();
  const selections = getCurrentSelections();

  if (!resumeData || !selections) return null;

  return (
    <div>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Education</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {resumeData.education.map((edu, index) => {
          const isSelected = selections.education[index] ?? true;

          return (
            <div
              key={index}
              className="flex items-start gap-3 px-6 py-4 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleEducation(index)}
                disabled={isReadOnly}
                className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                  isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                }`}
              />
              <div className={`flex-1 ${isSelected ? '' : 'opacity-50'}`}>
                <div className="flex items-baseline justify-between">
                  <h3 className="font-medium text-gray-900">
                    {edu.studyType} in {edu.area}
                  </h3>
                  <span className="text-sm text-gray-500">
                    {edu.startDate} - {edu.endDate}
                  </span>
                </div>
                <p className="text-sm text-gray-600">{edu.institution}</p>
                {edu.score && (
                  <p className="text-sm text-gray-500">GPA: {edu.score}</p>
                )}
                {edu.courses && edu.courses.length > 0 && (
                  <p className="text-xs text-gray-400 mt-1">
                    Courses: {edu.courses.slice(0, 3).join(', ')}
                    {edu.courses.length > 3 && '...'}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
