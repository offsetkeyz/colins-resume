// Resume data types matching the YAML structure

export type IncludeInTag = 'all' | 'leadership' | 'management' | 'technical' | 'development' | 'consulting' | 'startup';

export interface Profile {
  network: string;
  username: string;
  url: string;
}

export interface Basics {
  name: string;
  label: string;
  image: string;
  email: string;
  phone: string;
  url: string;
  summary: string;
  short_summary?: string;
  profiles: Profile[];
}

export interface Responsibility {
  description: string;
  include_in: IncludeInTag[];
}

export interface Position {
  job_title: string;
  location: string;
  start_date: string;
  end_date: string;
  responsibilities: Responsibility[];
  include_in: IncludeInTag[];
}

export interface WorkExperience {
  [company: string]: Position[];
}

export interface Education {
  institution: string;
  url?: string;
  area: string;
  studyType: string;
  startDate: string;
  endDate: string;
  score?: string;
  courses?: string[];
  include_in: IncludeInTag[];
}

export interface Award {
  title: string;
  date: string;
  awarder: string;
  summary: string;
  url?: string;
  include_in: IncludeInTag[];
}

export interface Certification {
  title: string;
  acronym: string;
  date: string;
  url: string;
  issuer: string;
  badge_url?: string;
  include_in: IncludeInTag[];
}

export interface Skill {
  name: string;
  keywords: string[];
  include_in: IncludeInTag[];
}

export interface Interest {
  name: string;
  keywords: string[];
}

export interface Language {
  language: string;
  fluency: string;
}

export interface ProjectHighlight {
  description: string;
  include_in: IncludeInTag[];
}

export interface Project {
  name: string;
  description: string;
  url?: string;
  highlights: ProjectHighlight[];
  keywords: string[];
  startDate: string;
  roles: string[];
  include_in?: IncludeInTag[];
}

export interface ResumeData {
  basics: Basics;
  work_experience: WorkExperience;
  education: Education[];
  awards: Award[];
  certifications: Certification[];
  specialty_skills: Skill[];
  languages: Language[];
  interests: Interest[];
  projects: Project[];
}

// Version/selection types
export interface SelectionState {
  // Section-level selections
  sections: {
    basics: boolean;
    work_experience: boolean;
    education: boolean;
    awards: boolean;
    certifications: boolean;
    skills: boolean;
    projects: boolean;
    interests: boolean;
  };

  // Work experience selections: company -> position index -> bullet index -> selected
  workExperience: {
    [company: string]: {
      selected: boolean;
      positions: {
        [positionIndex: number]: {
          selected: boolean;
          bullets: boolean[];
        };
      };
    };
  };

  // Education selections: index -> selected
  education: { [index: number]: boolean };

  // Awards selections: index -> selected
  awards: { [index: number]: boolean };

  // Certifications selections: index -> selected
  certifications: { [index: number]: boolean };

  // Skills selections: index -> selected
  skills: { [index: number]: boolean };

  // Projects selections: index -> { selected, highlights: boolean[] }
  projects: {
    [index: number]: {
      selected: boolean;
      highlights: boolean[];
    };
  };
}

// Text override types for inline editing
export interface TextOverride {
  value: string;
  lastModified: string;
}

export interface TextOverrides {
  // Work experience: company -> positionIndex -> field -> override
  workExperience?: {
    [company: string]: {
      company_name?: TextOverride; // Override for company display name
      [positionIndex: number]: {
        job_title?: TextOverride;
        location?: TextOverride;
        start_date?: TextOverride;
        end_date?: TextOverride;
        bullets?: {
          [bulletIndex: number]: TextOverride;
        };
      };
    };
  };

  // Education: index -> field -> override
  education?: {
    [index: number]: {
      institution?: TextOverride;
      area?: TextOverride;
      studyType?: TextOverride;
      startDate?: TextOverride;
      endDate?: TextOverride;
      score?: TextOverride;
      courses?: TextOverride;
    };
  };

  // Projects: index -> field -> override
  projects?: {
    [index: number]: {
      name?: TextOverride;
      description?: TextOverride;
      url?: TextOverride;
      startDate?: TextOverride;
      highlights?: {
        [highlightIndex: number]: TextOverride;
      };
    };
  };

  // Skills: index -> field -> override
  skills?: {
    [index: number]: {
      name?: TextOverride;
      keywords?: {
        [keywordIndex: number]: TextOverride;
      };
    };
  };

  // Awards: index -> field -> override
  awards?: {
    [index: number]: {
      title?: TextOverride;
      date?: TextOverride;
      awarder?: TextOverride;
      summary?: TextOverride;
    };
  };

  // Certifications: index -> field -> override
  certifications?: {
    [index: number]: {
      title?: TextOverride;
      acronym?: TextOverride;
      date?: TextOverride;
      issuer?: TextOverride;
    };
  };

  // Basics: field -> override
  basics?: {
    name?: TextOverride;
    label?: TextOverride;
    email?: TextOverride;
    phone?: TextOverride;
    url?: TextOverride;
    summary?: TextOverride;
  };
}

export interface ResumeVersion {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  basedOn: string; // 'master' or another version id
  selections: SelectionState;
  textOverrides?: TextOverrides; // Version-specific text edits
}

export interface VersionsData {
  versions: ResumeVersion[];
  activeVersionId: string | null;
}

// Section metadata for UI
export interface SectionMeta {
  id: keyof SelectionState['sections'];
  label: string;
  icon: string;
}

export const SECTION_META: SectionMeta[] = [
  { id: 'basics', label: 'Basics', icon: 'User' },
  { id: 'work_experience', label: 'Work Experience', icon: 'Briefcase' },
  { id: 'education', label: 'Education', icon: 'GraduationCap' },
  { id: 'awards', label: 'Awards', icon: 'Award' },
  { id: 'certifications', label: 'Certifications', icon: 'BadgeCheck' },
  { id: 'skills', label: 'Skills', icon: 'Wrench' },
  { id: 'projects', label: 'Projects', icon: 'FolderGit2' },
  { id: 'interests', label: 'Interests', icon: 'Heart' },
];
