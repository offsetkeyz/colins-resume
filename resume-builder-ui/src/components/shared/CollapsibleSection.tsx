import { useState, type ReactNode } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface CollapsibleSectionProps {
  title: string | ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  checkbox?: {
    checked: boolean;
    indeterminate?: boolean;
    onChange: () => void;
    disabled?: boolean;
  };
  level?: number;
  metadata?: string | ReactNode;
  id?: string;
}

export default function CollapsibleSection({
  title,
  children,
  defaultOpen = true,
  checkbox,
  level = 0,
  metadata,
  id,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const paddingLeft = level * 16;

  return (
    <div id={id} className="border-b border-gray-100 last:border-b-0">
      <div
        className="flex items-center gap-2 py-2 px-3 hover:bg-gray-50 cursor-pointer"
        style={{ paddingLeft: `${paddingLeft + 12}px` }}
      >
        {/* Expand/Collapse Toggle */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-0.5 hover:bg-gray-200 rounded text-gray-500"
        >
          {isOpen ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </button>

        {/* Checkbox */}
        {checkbox && (
          <input
            type="checkbox"
            checked={checkbox.checked}
            ref={(el) => {
              if (el) {
                el.indeterminate = checkbox.indeterminate ?? false;
              }
            }}
            onChange={(e) => {
              e.stopPropagation();
              checkbox.onChange();
            }}
            onClick={(e) => {
              e.stopPropagation();
            }}
            disabled={checkbox.disabled}
            className={`w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
              checkbox.disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
            }`}
          />
        )}

        {/* Title */}
        <span
          onClick={() => setIsOpen(!isOpen)}
          className={`flex-1 font-medium ${
            checkbox && !checkbox.checked ? 'text-gray-400' : 'text-gray-900'
          } ${level === 0 ? 'text-base' : 'text-sm'}`}
        >
          {title}
        </span>

        {/* Metadata (date, location, etc.) */}
        {metadata && (
          <span className="text-xs text-gray-500">{metadata}</span>
        )}
      </div>

      {/* Children */}
      {isOpen && (
        <div className="pb-2">
          {children}
        </div>
      )}
    </div>
  );
}
