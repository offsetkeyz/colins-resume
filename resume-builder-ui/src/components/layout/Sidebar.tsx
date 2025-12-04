import {
  User,
  Briefcase,
  GraduationCap,
  Award,
  BadgeCheck,
  Wrench,
  FolderGit2,
  Heart,
} from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import type { SelectionState } from '../../types/resume';

const SECTIONS = [
  { id: 'basics' as const, label: 'Basics', Icon: User },
  { id: 'work_experience' as const, label: 'Work Experience', Icon: Briefcase },
  { id: 'education' as const, label: 'Education', Icon: GraduationCap },
  { id: 'awards' as const, label: 'Awards', Icon: Award },
  { id: 'certifications' as const, label: 'Certifications', Icon: BadgeCheck },
  { id: 'skills' as const, label: 'Skills', Icon: Wrench },
  { id: 'projects' as const, label: 'Projects', Icon: FolderGit2 },
  { id: 'interests' as const, label: 'Interests', Icon: Heart },
];

export default function Sidebar() {
  const {
    getCurrentSelections,
    toggleSection,
    activeVersionId,
    selectedSection,
    setSelectedSection,
  } = useResumeStore();

  const selections = getCurrentSelections();
  const isReadOnly = activeVersionId === null;

  const handleCheckboxChange = (sectionId: keyof SelectionState['sections']) => {
    if (isReadOnly) return;
    toggleSection(sectionId);
  };

  const handleLabelClick = (sectionId: string) => {
    setSelectedSection(sectionId);
    // Scroll to section
    const element = document.getElementById(`section-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex-shrink-0 overflow-y-auto">
      <div className="p-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Sections
        </h2>
        <div className="space-y-1">
          {SECTIONS.map(({ id, label, Icon }) => {
            const isSelected = selections?.sections[id] ?? true;
            const isActive = selectedSection === id;

            return (
              <div
                key={id}
                className={`flex items-center gap-3 px-2 py-2 rounded-md cursor-pointer transition-colors ${
                  isActive ? 'bg-blue-50' : 'hover:bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleCheckboxChange(id)}
                  disabled={isReadOnly}
                  className={`w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                    isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                  }`}
                />
                <button
                  onClick={() => handleLabelClick(id)}
                  className={`flex items-center gap-2 flex-1 text-left ${
                    isSelected ? 'text-gray-900' : 'text-gray-400'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              </div>
            );
          })}
        </div>

        {isReadOnly && (
          <p className="mt-4 text-xs text-gray-500 italic">
            Master is read-only. Create a version to customize.
          </p>
        )}
      </div>
    </aside>
  );
}
