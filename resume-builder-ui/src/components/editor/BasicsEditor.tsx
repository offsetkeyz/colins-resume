import { useResumeStore } from '../../store/resume-store';
import EditableText from '../shared/EditableText';

interface BasicsEditorProps {
  isReadOnly: boolean;
}

export default function BasicsEditor({ isReadOnly }: BasicsEditorProps) {
  const {
    resumeData,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
  } = useResumeStore();

  const textOverrides = getCurrentTextOverrides();

  if (!resumeData) return null;

  // Get text overrides for basics
  const basicsOverrides = textOverrides?.basics;
  const name = basicsOverrides?.name?.value ?? resumeData.basics.name;
  const label = basicsOverrides?.label?.value ?? resumeData.basics.label;
  const email = basicsOverrides?.email?.value ?? resumeData.basics.email;
  const phone = basicsOverrides?.phone?.value ?? resumeData.basics.phone;
  const url = basicsOverrides?.url?.value ?? resumeData.basics.url;
  const summary = basicsOverrides?.summary?.value ?? resumeData.basics.summary;
  const shortSummary = basicsOverrides?.short_summary?.value ?? resumeData.basics.short_summary;

  return (
    <div>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Basics</h2>
      </div>

      <div className="px-6 py-4 space-y-4">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <EditableText
            value={name}
            onSave={(newValue) => setTextOverride('basics.name', newValue, {})}
            onRevert={
              basicsOverrides?.name
                ? () => removeTextOverride('basics.name', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.name
                ? () => pushOverrideToMaster('basics.name', name, {})
                : undefined
            }
            isModified={!!basicsOverrides?.name}
            isReadOnly={isReadOnly}
            showEditIcon={true}
          />
        </div>

        {/* Title/Label */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <EditableText
            value={label}
            onSave={(newValue) => setTextOverride('basics.label', newValue, {})}
            onRevert={
              basicsOverrides?.label
                ? () => removeTextOverride('basics.label', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.label
                ? () => pushOverrideToMaster('basics.label', label, {})
                : undefined
            }
            isModified={!!basicsOverrides?.label}
            isReadOnly={isReadOnly}
            showEditIcon={true}
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <EditableText
            value={email}
            onSave={(newValue) => setTextOverride('basics.email', newValue, {})}
            onRevert={
              basicsOverrides?.email
                ? () => removeTextOverride('basics.email', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.email
                ? () => pushOverrideToMaster('basics.email', email, {})
                : undefined
            }
            isModified={!!basicsOverrides?.email}
            isReadOnly={isReadOnly}
            showEditIcon={true}
          />
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <EditableText
            value={phone}
            onSave={(newValue) => setTextOverride('basics.phone', newValue, {})}
            onRevert={
              basicsOverrides?.phone
                ? () => removeTextOverride('basics.phone', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.phone
                ? () => pushOverrideToMaster('basics.phone', phone, {})
                : undefined
            }
            isModified={!!basicsOverrides?.phone}
            isReadOnly={isReadOnly}
            showEditIcon={true}
          />
        </div>

        {/* URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
          <EditableText
            value={url}
            onSave={(newValue) => setTextOverride('basics.url', newValue, {})}
            onRevert={
              basicsOverrides?.url
                ? () => removeTextOverride('basics.url', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.url
                ? () => pushOverrideToMaster('basics.url', url, {})
                : undefined
            }
            isModified={!!basicsOverrides?.url}
            isReadOnly={isReadOnly}
            showEditIcon={true}
          />
        </div>

        {/* Summary */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Summary</label>
          <EditableText
            value={summary}
            onSave={(newValue) => setTextOverride('basics.summary', newValue, {})}
            onRevert={
              basicsOverrides?.summary
                ? () => removeTextOverride('basics.summary', {})
                : undefined
            }
            onPushToMaster={
              basicsOverrides?.summary
                ? () => pushOverrideToMaster('basics.summary', summary, {})
                : undefined
            }
            isModified={!!basicsOverrides?.summary}
            isReadOnly={isReadOnly}
            multiline={true}
            showEditIcon={true}
          />
        </div>

        {/* Short Summary (optional) */}
        {(shortSummary || !isReadOnly) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Short Summary <span className="text-xs text-gray-500">(optional)</span>
            </label>
            <EditableText
              value={shortSummary || ''}
              onSave={(newValue) => setTextOverride('basics.short_summary', newValue, {})}
              onRevert={
                basicsOverrides?.short_summary
                  ? () => removeTextOverride('basics.short_summary', {})
                  : undefined
              }
              onPushToMaster={
                basicsOverrides?.short_summary
                  ? () => pushOverrideToMaster('basics.short_summary', shortSummary || '', {})
                  : undefined
              }
              isModified={!!basicsOverrides?.short_summary}
              isReadOnly={isReadOnly}
              multiline={true}
              showEditIcon={true}
              placeholder="Add a brief summary"
            />
          </div>
        )}
      </div>
    </div>
  );
}
