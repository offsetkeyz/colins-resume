import { useState, useRef, useEffect } from 'react';
import { Edit2, Check, X, Upload, RotateCcw } from 'lucide-react';

interface EditableTextProps {
  value: string;
  onSave: (newValue: string) => void;
  onRevert?: () => void;
  onPushToMaster?: () => void;
  isModified?: boolean;
  isReadOnly?: boolean;
  multiline?: boolean;
  className?: string;
  placeholder?: string;
  showEditIcon?: boolean;
}

export default function EditableText({
  value,
  onSave,
  onRevert,
  onPushToMaster,
  isModified = false,
  isReadOnly = false,
  multiline = false,
  className = '',
  placeholder = 'Click to edit...',
  showEditIcon = false,
}: EditableTextProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);
  const [showActions, setShowActions] = useState(false);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  useEffect(() => {
    setEditValue(value);
  }, [value]);

  const handleStartEdit = () => {
    if (isReadOnly) return;
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editValue.trim() !== value.trim() && editValue.trim() !== '') {
      onSave(editValue.trim());
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !multiline) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Enter' && multiline && e.ctrlKey) {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const handleRevert = () => {
    if (onRevert) {
      onRevert();
      setShowActions(false);
    }
  };

  const handlePushToMaster = () => {
    if (onPushToMaster) {
      if (window.confirm('Push this change to the master resume? This will affect all versions.')) {
        onPushToMaster();
        setShowActions(false);
      }
    }
  };

  if (isEditing) {
    const commonProps = {
      ref: inputRef as any,
      value: editValue,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
        setEditValue(e.target.value),
      onKeyDown: handleKeyDown,
      onBlur: handleSave,
      placeholder,
      className: `w-full px-2 py-1 border border-blue-500 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`,
    };

    if (multiline) {
      return (
        <div className="relative">
          <textarea
            {...commonProps}
            rows={3}
            className={`${commonProps.className} resize-none`}
          />
          <div className="flex gap-1 mt-1 text-xs text-gray-500">
            <kbd className="px-1 bg-gray-100 rounded">Ctrl+Enter</kbd> to save,{' '}
            <kbd className="px-1 bg-gray-100 rounded">Esc</kbd> to cancel
          </div>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2">
        <input {...commonProps} type="text" />
        <button
          type="button"
          onClick={handleSave}
          className="p-1 text-green-600 hover:bg-green-50 rounded"
          title="Save"
        >
          <Check className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={handleCancel}
          className="p-1 text-red-600 hover:bg-red-50 rounded"
          title="Cancel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      className={`group relative inline-flex items-center gap-2 ${
        isReadOnly ? 'cursor-default' : 'cursor-pointer hover:bg-gray-50'
      } ${className}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <span
        onClick={handleStartEdit}
        className={`flex-1 ${isModified ? 'text-blue-700 font-medium' : ''}`}
      >
        {value || placeholder}
      </span>

      {isModified && (
        <span
          className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full"
          title="Modified from master"
        />
      )}

      {!isReadOnly && showEditIcon && !isEditing && (
        <button
          type="button"
          onClick={handleStartEdit}
          className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-blue-600 transition-opacity"
          title="Edit"
        >
          <Edit2 className="w-3 h-3" />
        </button>
      )}

      {!isReadOnly && showActions && isModified && (onRevert || onPushToMaster) && (
        <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 p-1 flex gap-1">
          {onRevert && (
            <button
              type="button"
              onClick={handleRevert}
              className="flex items-center gap-1 px-2 py-1 text-xs text-gray-700 hover:bg-gray-100 rounded"
              title="Revert to master"
            >
              <RotateCcw className="w-3 h-3" />
              Revert
            </button>
          )}
          {onPushToMaster && (
            <button
              type="button"
              onClick={handlePushToMaster}
              className="flex items-center gap-1 px-2 py-1 text-xs text-blue-700 hover:bg-blue-50 rounded"
              title="Push to master resume"
            >
              <Upload className="w-3 h-3" />
              Push to Master
            </button>
          )}
        </div>
      )}
    </div>
  );
}
