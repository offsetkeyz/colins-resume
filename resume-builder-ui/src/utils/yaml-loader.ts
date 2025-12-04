import yaml from 'js-yaml';
import type { ResumeData, SelectionState } from '../types/resume';

// Load resume YAML from file
export async function loadResumeYaml(): Promise<ResumeData> {
  const response = await fetch('/resume.yaml');
  const text = await response.text();
  return yaml.load(text) as ResumeData;
}

// Create a default selection state with everything selected
export function createDefaultSelections(resume: ResumeData): SelectionState {
  const selections: SelectionState = {
    sections: {
      basics: true,
      work_experience: true,
      education: true,
      awards: true,
      certifications: true,
      skills: true,
      projects: true,
      interests: true,
    },
    workExperience: {},
    education: {},
    awards: {},
    certifications: {},
    skills: {},
    projects: {},
  };

  // Initialize work experience selections
  Object.entries(resume.work_experience).forEach(([company, positions]) => {
    selections.workExperience[company] = {
      selected: true,
      positions: {},
    };
    positions.forEach((position, posIndex) => {
      selections.workExperience[company].positions[posIndex] = {
        selected: true,
        bullets: position.responsibilities.map(() => true),
      };
    });
  });

  // Initialize education selections
  resume.education.forEach((_, index) => {
    selections.education[index] = true;
  });

  // Initialize awards selections
  resume.awards.forEach((_, index) => {
    selections.awards[index] = true;
  });

  // Initialize certifications selections
  resume.certifications.forEach((_, index) => {
    selections.certifications[index] = true;
  });

  // Initialize skills selections
  resume.specialty_skills.forEach((_, index) => {
    selections.skills[index] = true;
  });

  // Initialize projects selections
  resume.projects.forEach((project, index) => {
    selections.projects[index] = {
      selected: true,
      highlights: project.highlights.map(() => true),
    };
  });

  return selections;
}

// Deep clone a selection state
export function cloneSelections(selections: SelectionState): SelectionState {
  return JSON.parse(JSON.stringify(selections));
}

// Generate a unique ID for versions
export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
