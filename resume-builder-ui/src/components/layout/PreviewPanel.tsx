import { useMemo } from 'react';
import { X, ExternalLink } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';

export default function PreviewPanel() {
  const { resumeData, getCurrentSelections, getCurrentTextOverrides, setPreviewOpen } =
    useResumeStore();
  const selections = getCurrentSelections();
  const textOverrides = getCurrentTextOverrides();

  const previewHtml = useMemo(() => {
    if (!resumeData || !selections) return '';

    // Build preview HTML based on selections
    let html = `
      <div style="font-family: 'Lato', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">
    `;

    // Basics section
    if (selections.sections.basics) {
      html += `
        <header style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #2563eb; padding-bottom: 20px;">
          <h1 style="font-family: 'Playfair Display', serif; font-size: 2.5em; margin: 0; color: #1e40af;">${resumeData.basics.name}</h1>
          <p style="font-size: 1.2em; color: #4b5563; margin: 8px 0;">${resumeData.basics.label}</p>
          <p style="font-size: 0.9em; color: #6b7280;">
            ${resumeData.basics.email} | ${resumeData.basics.phone} |
            <a href="${resumeData.basics.url}" style="color: #2563eb;">${resumeData.basics.url}</a>
          </p>
        </header>
      `;
    }

    // Work Experience section
    if (selections.sections.work_experience) {
      const hasSelectedWork = Object.entries(selections.workExperience).some(
        ([, data]) => data.selected
      );

      if (hasSelectedWork) {
        html += `<section style="margin-bottom: 25px;">
          <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4em; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 15px;">Work Experience</h2>
        `;

        Object.entries(resumeData.work_experience).forEach(([company, positions]) => {
          const companySelection = selections.workExperience[company];
          if (!companySelection?.selected) return;

          positions.forEach((position, posIndex) => {
            const posSelection = companySelection.positions[posIndex];
            if (!posSelection?.selected) return;

            // Get text overrides for this position
            const posOverrides = textOverrides?.workExperience?.[company]?.[posIndex];
            const jobTitle = posOverrides?.job_title?.value ?? position.job_title;
            const location = posOverrides?.location?.value ?? position.location;
            const startDate = posOverrides?.start_date?.value ?? position.start_date;
            const endDate = posOverrides?.end_date?.value ?? position.end_date;

            const selectedBullets = position.responsibilities
              .map((resp, bulletIdx) => ({
                text:
                  posOverrides?.bullets?.[bulletIdx]?.value ?? resp.description,
                selected: posSelection.bullets[bulletIdx],
              }))
              .filter((b) => b.selected);

            if (selectedBullets.length === 0) return;

            html += `
              <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                  <h3 style="font-size: 1.1em; margin: 0; color: #111827;">${jobTitle}</h3>
                  <span style="font-size: 0.85em; color: #6b7280;">${startDate} - ${endDate}</span>
                </div>
                <p style="font-size: 0.95em; color: #4b5563; margin: 2px 0 8px;">${company} | ${location}</p>
                <ul style="margin: 0; padding-left: 20px; font-size: 0.9em; line-height: 1.6;">
                  ${selectedBullets.map((b) => `<li>${b.text}</li>`).join('')}
                </ul>
              </div>
            `;
          });
        });

        html += `</section>`;
      }
    }

    // Education section
    if (selections.sections.education) {
      const selectedEducation = resumeData.education
        .map((edu, idx) => ({ edu, idx }))
        .filter(({ idx }) => selections.education[idx]);

      if (selectedEducation.length > 0) {
        html += `<section style="margin-bottom: 25px;">
          <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4em; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 15px;">Education</h2>
        `;

        selectedEducation.forEach(({ edu, idx }) => {
          const eduOverrides = textOverrides?.education?.[idx];
          const institution = eduOverrides?.institution?.value ?? edu.institution;
          const area = eduOverrides?.area?.value ?? edu.area;
          const studyType = eduOverrides?.studyType?.value ?? edu.studyType;
          const startDate = eduOverrides?.startDate?.value ?? edu.startDate;
          const endDate = eduOverrides?.endDate?.value ?? edu.endDate;

          html += `
            <div style="margin-bottom: 12px;">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <h3 style="font-size: 1.05em; margin: 0;">${studyType} in ${area}</h3>
                <span style="font-size: 0.85em; color: #6b7280;">${startDate} - ${endDate}</span>
              </div>
              <p style="font-size: 0.9em; color: #4b5563; margin: 2px 0;">${institution}</p>
            </div>
          `;
        });

        html += `</section>`;
      }
    }

    // Certifications section
    if (selections.sections.certifications) {
      const selectedCerts = resumeData.certifications.filter(
        (_, idx) => selections.certifications[idx]
      );

      if (selectedCerts.length > 0) {
        html += `<section style="margin-bottom: 25px;">
          <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4em; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 15px;">Certifications</h2>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        `;

        selectedCerts.forEach((cert) => {
          html += `<span style="background: #eff6ff; color: #1e40af; padding: 4px 12px; border-radius: 4px; font-size: 0.85em;">${cert.acronym}</span>`;
        });

        html += `</div></section>`;
      }
    }

    // Skills section
    if (selections.sections.skills) {
      const selectedSkills = resumeData.specialty_skills
        .map((skill, idx) => ({ skill, idx }))
        .filter(({ idx }) => selections.skills[idx]);

      if (selectedSkills.length > 0) {
        html += `<section style="margin-bottom: 25px;">
          <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4em; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 15px;">Skills</h2>
        `;

        selectedSkills.forEach(({ skill, idx }) => {
          const skillOverrides = textOverrides?.skills?.[idx];
          const skillName = skillOverrides?.name?.value ?? skill.name;
          const keywords = skill.keywords.map((kw, kidx) =>
            skillOverrides?.keywords?.[kidx]?.value ?? kw
          );

          html += `
            <div style="margin-bottom: 10px;">
              <strong style="font-size: 0.95em;">${skillName}:</strong>
              <span style="font-size: 0.9em; color: #4b5563;"> ${keywords.join(' • ')}</span>
            </div>
          `;
        });

        html += `</section>`;
      }
    }

    // Projects section
    if (selections.sections.projects) {
      const hasSelectedProjects = Object.entries(selections.projects).some(
        ([, data]) => data.selected
      );

      if (hasSelectedProjects) {
        html += `<section style="margin-bottom: 25px;">
          <h2 style="font-family: 'Playfair Display', serif; font-size: 1.4em; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 15px;">Projects</h2>
        `;

        resumeData.projects.forEach((project, idx) => {
          const projSelection = selections.projects[idx];
          if (!projSelection?.selected) return;

          // Get text overrides for this project
          const projOverrides = textOverrides?.projects?.[idx];
          const projectName = projOverrides?.name?.value ?? project.name;
          const projectDesc = projOverrides?.description?.value ?? project.description;

          const selectedHighlights = project.highlights
            .map((h, hIdx) => ({
              text: projOverrides?.highlights?.[hIdx]?.value ?? h.description,
              selected: projSelection.highlights[hIdx],
            }))
            .filter((h) => h.selected);

          html += `
            <div style="margin-bottom: 15px;">
              <h3 style="font-size: 1.05em; margin: 0;">${projectName}</h3>
              <p style="font-size: 0.9em; color: #4b5563; margin: 4px 0;">${projectDesc}</p>
              ${
                selectedHighlights.length > 0
                  ? `<ul style="margin: 8px 0 0; padding-left: 20px; font-size: 0.9em; line-height: 1.6;">
                      ${selectedHighlights.map((h) => `<li>${h.text}</li>`).join('')}
                    </ul>`
                  : ''
              }
            </div>
          `;
        });

        html += `</section>`;
      }
    }

    html += `</div>`;
    return html;
  }, [resumeData, selections, textOverrides]);

  return (
    <aside className="w-96 bg-white border-l border-gray-200 flex-shrink-0 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h2 className="font-semibold text-gray-900">Preview</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const newWindow = window.open('', '_blank');
              if (newWindow) {
                newWindow.document.write(`
                  <!DOCTYPE html>
                  <html>
                  <head>
                    <title>Resume Preview</title>
                    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
                  </head>
                  <body style="margin: 0; padding: 20px; background: #f9fafb;">
                    ${previewHtml}
                  </body>
                  </html>
                `);
                newWindow.document.close();
              }
            }}
            className="p-1.5 hover:bg-gray-100 rounded-md text-gray-500"
            title="Open in new tab"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
          <button
            onClick={() => setPreviewOpen(false)}
            className="p-1.5 hover:bg-gray-100 rounded-md text-gray-500"
            title="Close preview"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 overflow-auto p-4 bg-gray-50">
        <div
          className="bg-white shadow-sm rounded-lg p-4 min-h-full"
          dangerouslySetInnerHTML={{ __html: previewHtml }}
        />
      </div>
    </aside>
  );
}
