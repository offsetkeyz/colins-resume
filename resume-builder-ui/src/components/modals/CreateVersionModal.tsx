import { useState } from 'react';
import { X } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';

interface CreateVersionModalProps {
  open: boolean;
  onClose: () => void;
}

export default function CreateVersionModal({ open, onClose }: CreateVersionModalProps) {
  const { createVersion, versions } = useResumeStore();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [basedOn, setBasedOn] = useState('master');

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    createVersion(
      name.trim(),
      description.trim() || undefined,
      basedOn === 'master' ? 'master' : basedOn
    );

    // Reset form
    setName('');
    setDescription('');
    setBasedOn('master');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Create New Version</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-md text-gray-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Technical Focus"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Description <span className="text-gray-400">(optional)</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Emphasizes technical skills and development experience"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <div>
            <label htmlFor="basedOn" className="block text-sm font-medium text-gray-700 mb-1">
              Based on
            </label>
            <select
              id="basedOn"
              value={basedOn}
              onChange={(e) => setBasedOn(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="master">Master (all items selected)</option>
              {versions.map((version) => (
                <option key={version.id} value={version.id}>
                  {version.name}
                </option>
              ))}
            </select>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Version
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
