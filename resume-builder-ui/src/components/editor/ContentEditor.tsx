import { useResumeStore } from '../../store/resume-store';
import WorkExperienceEditor from './WorkExperienceEditor';
import EducationEditor from './EducationEditor';
import SkillsEditor from './SkillsEditor';
import ProjectsEditor from './ProjectsEditor';
import SimpleListEditor from './SimpleListEditor';

export default function ContentEditor() {
  const { resumeData, getCurrentSelections, activeVersionId } = useResumeStore();
  const selections = getCurrentSelections();

  if (!resumeData || !selections) {
    return (
      <main className="flex-1 overflow-auto p-6">
        <div className="text-gray-500">Loading...</div>
      </main>
    );
  }

  const isReadOnly = activeVersionId === null;

  return (
    <main className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto py-6 px-4 space-y-6">
        {/* Basics (always shown, no checkboxes for individual fields yet) */}
        {selections.sections.basics && (
          <section id="section-basics" className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basics</h2>
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>Name:</strong> {resumeData.basics.name}</p>
              <p><strong>Title:</strong> {resumeData.basics.label}</p>
              <p><strong>Email:</strong> {resumeData.basics.email}</p>
              <p><strong>Summary:</strong> {resumeData.basics.summary.substring(0, 200)}...</p>
            </div>
          </section>
        )}

        {/* Work Experience */}
        {selections.sections.work_experience && (
          <section id="section-work_experience" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <WorkExperienceEditor isReadOnly={isReadOnly} />
          </section>
        )}

        {/* Education */}
        {selections.sections.education && (
          <section id="section-education" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <EducationEditor isReadOnly={isReadOnly} />
          </section>
        )}

        {/* Awards */}
        {selections.sections.awards && (
          <section id="section-awards" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <SimpleListEditor
              title="Awards"
              items={resumeData.awards.map((a) => ({
                title: a.title,
                subtitle: `${a.awarder} - ${a.date}`,
                description: a.summary.substring(0, 150) + '...',
              }))}
              selections={selections.awards}
              onToggle={(index) => useResumeStore.getState().toggleAward(index)}
              isReadOnly={isReadOnly}
            />
          </section>
        )}

        {/* Certifications */}
        {selections.sections.certifications && (
          <section id="section-certifications" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <SimpleListEditor
              title="Certifications"
              items={resumeData.certifications.map((c) => ({
                title: `${c.title} (${c.acronym})`,
                subtitle: `${c.issuer} - ${c.date}`,
              }))}
              selections={selections.certifications}
              onToggle={(index) => useResumeStore.getState().toggleCertification(index)}
              isReadOnly={isReadOnly}
            />
          </section>
        )}

        {/* Skills */}
        {selections.sections.skills && (
          <section id="section-skills" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <SkillsEditor isReadOnly={isReadOnly} />
          </section>
        )}

        {/* Projects */}
        {selections.sections.projects && (
          <section id="section-projects" className="bg-white rounded-lg shadow-sm border border-gray-200">
            <ProjectsEditor isReadOnly={isReadOnly} />
          </section>
        )}

        {/* Interests */}
        {selections.sections.interests && (
          <section id="section-interests" className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Interests</h2>
            <div className="flex flex-wrap gap-2">
              {resumeData.interests.map((interest) => (
                <span
                  key={interest.name}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {interest.name}
                </span>
              ))}
            </div>
          </section>
        )}

        {isReadOnly && (
          <div className="text-center py-8 text-gray-500">
            <p>You're viewing the Master resume (read-only).</p>
            <p className="text-sm">Create a new version to customize content.</p>
          </div>
        )}
      </div>
    </main>
  );
}
