interface SimpleListItem {
  title: string;
  subtitle?: string;
  description?: string;
}

interface SimpleListEditorProps {
  title: string;
  items: SimpleListItem[];
  selections: { [index: number]: boolean };
  onToggle: (index: number) => void;
  isReadOnly: boolean;
}

export default function SimpleListEditor({
  title,
  items,
  selections,
  onToggle,
  isReadOnly,
}: SimpleListEditorProps) {
  return (
    <div>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {items.map((item, index) => {
          const isSelected = selections[index] ?? true;

          return (
            <div
              key={index}
              className="flex items-start gap-3 px-6 py-4 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggle(index)}
                disabled={isReadOnly}
                className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                  isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                }`}
              />
              <div className={`flex-1 ${isSelected ? '' : 'opacity-50'}`}>
                <h3 className="font-medium text-gray-900">{item.title}</h3>
                {item.subtitle && (
                  <p className="text-sm text-gray-500">{item.subtitle}</p>
                )}
                {item.description && (
                  <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
