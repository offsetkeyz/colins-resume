import { useState } from 'react';
import {
  FileText,
  Plus,
  Eye,
  EyeOff,
  ChevronDown,
  MoreVertical,
  Trash2,
  Copy,
} from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import CreateVersionModal from '../modals/CreateVersionModal';

export default function TopNav() {
  const {
    versions,
    activeVersionId,
    setActiveVersion,
    previewOpen,
    setPreviewOpen,
    deleteVersion,
    duplicateVersion,
  } = useResumeStore();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const activeVersion = activeVersionId
    ? versions.find((v) => v.id === activeVersionId)
    : null;

  const handleVersionSelect = (id: string | null) => {
    setActiveVersion(id);
    setDropdownOpen(false);
  };

  const handleDelete = () => {
    if (activeVersionId && confirm('Are you sure you want to delete this version?')) {
      deleteVersion(activeVersionId);
    }
    setMenuOpen(false);
  };

  const handleDuplicate = () => {
    if (activeVersionId && activeVersion) {
      duplicateVersion(activeVersionId, `${activeVersion.name} (copy)`);
    }
    setMenuOpen(false);
  };

  return (
    <>
      <nav className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <FileText className="w-6 h-6 text-blue-600" />
          <span className="font-semibold text-gray-900">Resume Builder</span>
        </div>

        {/* Center: Version Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Version:</span>
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-md text-sm font-medium text-gray-700 min-w-[180px] justify-between"
            >
              <span>{activeVersion?.name ?? 'Master'}</span>
              <ChevronDown className="w-4 h-4" />
            </button>

            {dropdownOpen && (
              <div className="absolute top-full left-0 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg z-50">
                <button
                  onClick={() => handleVersionSelect(null)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                    activeVersionId === null ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  Master{' '}
                  <span className="text-gray-400 text-xs">(read-only)</span>
                </button>
                {versions.length > 0 && (
                  <div className="border-t border-gray-100" />
                )}
                {versions.map((version) => (
                  <button
                    key={version.id}
                    onClick={() => handleVersionSelect(version.id)}
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                      activeVersionId === version.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700'
                    }`}
                  >
                    {version.name}
                  </button>
                ))}
                <div className="border-t border-gray-100" />
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    setCreateModalOpen(true);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Create New Version
                </button>
              </div>
            )}
          </div>

          {/* New Version Button */}
          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            New
          </button>

          {/* Version Actions Menu (only for non-master) */}
          {activeVersionId && (
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="p-1.5 hover:bg-gray-100 rounded-md"
              >
                <MoreVertical className="w-4 h-4 text-gray-500" />
              </button>
              {menuOpen && (
                <div className="absolute top-full right-0 mt-1 w-40 bg-white border border-gray-200 rounded-md shadow-lg z-50">
                  <button
                    onClick={handleDuplicate}
                    className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    <Copy className="w-4 h-4" />
                    Duplicate
                  </button>
                  <button
                    onClick={handleDelete}
                    className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Preview Toggle */}
        <button
          onClick={() => setPreviewOpen(!previewOpen)}
          className="flex items-center gap-2 px-3 py-1.5 text-gray-600 hover:bg-gray-100 rounded-md text-sm"
        >
          {previewOpen ? (
            <>
              <EyeOff className="w-4 h-4" />
              Hide Preview
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" />
              Show Preview
            </>
          )}
        </button>
      </nav>

      <CreateVersionModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
      />

      {/* Click outside handler */}
      {(dropdownOpen || menuOpen) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setDropdownOpen(false);
            setMenuOpen(false);
          }}
        />
      )}
    </>
  );
}
