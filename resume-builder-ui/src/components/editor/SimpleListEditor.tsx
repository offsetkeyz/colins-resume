import { useState } from 'react';
import { Plus } from 'lucide-react';
import { useResumeStore } from '../../store/resume-store';
import EditableText from '../shared/EditableText';
import AddAwardModal from '../modals/AddAwardModal';
import AddCertificationModal from '../modals/AddCertificationModal';

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
  sectionType: 'awards' | 'certifications';
}

export default function SimpleListEditor({
  title,
  items,
  selections,
  onToggle,
  isReadOnly,
  sectionType,
}: SimpleListEditorProps) {
  const [showAddModal, setShowAddModal] = useState(false);
  const {
    resumeData,
    getCurrentTextOverrides,
    setTextOverride,
    removeTextOverride,
    pushOverrideToMaster,
  } = useResumeStore();

  const textOverrides = getCurrentTextOverrides();

  if (!resumeData) return null;

  return (
    <div>
      {sectionType === 'awards' ? (
        <AddAwardModal open={showAddModal} onClose={() => setShowAddModal(false)} />
      ) : (
        <AddCertificationModal open={showAddModal} onClose={() => setShowAddModal(false)} />
      )}

      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      </div>

      <div className="divide-y divide-gray-100">
        {items.map((_item, index) => {
          const isSelected = selections[index] ?? true;

          // Get the actual data item
          const dataItem =
            sectionType === 'awards'
              ? resumeData.awards[index]
              : resumeData.certifications[index];

          // Get text overrides with type guards
          const itemOverrides = textOverrides?.[sectionType]?.[index];

          let itemTitle: string;
          let itemDescription: string | undefined;
          let awarder: string | undefined;
          let issuer: string | undefined;
          let date: string | undefined;
          let acronym: string | undefined;

          if (sectionType === 'awards') {
            const award = dataItem as any;
            const awardOverrides = itemOverrides as any;
            itemTitle = awardOverrides?.title?.value ?? award.title;
            awarder = awardOverrides?.awarder?.value ?? award.awarder;
            date = awardOverrides?.date?.value ?? award.date;
            itemDescription = awardOverrides?.summary?.value ?? award.summary;
          } else {
            const cert = dataItem as any;
            const certOverrides = itemOverrides as any;
            itemTitle = certOverrides?.title?.value ?? cert.title;
            acronym = certOverrides?.acronym?.value ?? cert.acronym;
            issuer = certOverrides?.issuer?.value ?? cert.issuer;
            date = certOverrides?.date?.value ?? cert.date;
          }

          return (
            <div
              key={index}
              className="flex items-start gap-3 px-6 py-4 hover:bg-gray-50"
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  e.stopPropagation();
                  onToggle(index);
                }}
                onClick={(e) => {
                  e.stopPropagation();
                }}
                disabled={isReadOnly}
                className={`mt-1 w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 ${
                  isReadOnly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'
                }`}
              />
              <div className={`flex-1 ${isSelected ? '' : 'opacity-50'}`}>
                <h3 className="font-medium text-gray-900">
                  <EditableText
                    value={itemTitle}
                    onSave={(newValue) =>
                      setTextOverride(`${sectionType}.title`, newValue, { index })
                    }
                    onRevert={
                      itemOverrides?.title
                        ? () => removeTextOverride(`${sectionType}.title`, { index })
                        : undefined
                    }
                    onPushToMaster={
                      itemOverrides?.title
                        ? () =>
                            pushOverrideToMaster(
                              `${sectionType}.title`,
                              itemOverrides.title!.value,
                              { index }
                            )
                        : undefined
                    }
                    isModified={!!itemOverrides?.title}
                    isReadOnly={isReadOnly}
                    showEditIcon={true}
                  />
                  {sectionType === 'certifications' && acronym && (
                    <>
                      {' '}
                      (
                      <EditableText
                        value={acronym}
                        onSave={(newValue) =>
                          setTextOverride(`${sectionType}.acronym`, newValue, { index })
                        }
                        onRevert={
                          (itemOverrides as any)?.acronym
                            ? () => removeTextOverride(`${sectionType}.acronym`, { index })
                            : undefined
                        }
                        onPushToMaster={
                          (itemOverrides as any)?.acronym
                            ? () =>
                                pushOverrideToMaster(
                                  `${sectionType}.acronym`,
                                  acronym,
                                  { index }
                                )
                            : undefined
                        }
                        isModified={!!(itemOverrides as any)?.acronym}
                        isReadOnly={isReadOnly}
                        showEditIcon={true}
                      />
                      )
                    </>
                  )}
                </h3>
                <p className="text-sm text-gray-500">
                  {sectionType === 'awards' ? (
                    <>
                      <EditableText
                        value={awarder || ''}
                        onSave={(newValue) =>
                          setTextOverride(`${sectionType}.awarder`, newValue, { index })
                        }
                        onRevert={
                          (itemOverrides as any)?.awarder
                            ? () => removeTextOverride(`${sectionType}.awarder`, { index })
                            : undefined
                        }
                        onPushToMaster={
                          (itemOverrides as any)?.awarder
                            ? () =>
                                pushOverrideToMaster(
                                  `${sectionType}.awarder`,
                                  awarder || '',
                                  { index }
                                )
                            : undefined
                        }
                        isModified={!!(itemOverrides as any)?.awarder}
                        isReadOnly={isReadOnly}
                        showEditIcon={true}
                      />
                    </>
                  ) : (
                    <>
                      <EditableText
                        value={issuer || ''}
                        onSave={(newValue) =>
                          setTextOverride(`${sectionType}.issuer`, newValue, { index })
                        }
                        onRevert={
                          (itemOverrides as any)?.issuer
                            ? () => removeTextOverride(`${sectionType}.issuer`, { index })
                            : undefined
                        }
                        onPushToMaster={
                          (itemOverrides as any)?.issuer
                            ? () =>
                                pushOverrideToMaster(
                                  `${sectionType}.issuer`,
                                  issuer || '',
                                  { index }
                                )
                            : undefined
                        }
                        isModified={!!(itemOverrides as any)?.issuer}
                        isReadOnly={isReadOnly}
                        showEditIcon={true}
                      />
                    </>
                  )}
                  {' - '}
                  <EditableText
                    value={date || ''}
                    onSave={(newValue) =>
                      setTextOverride(`${sectionType}.date`, newValue, { index })
                    }
                    onRevert={
                      (itemOverrides as any)?.date
                        ? () => removeTextOverride(`${sectionType}.date`, { index })
                        : undefined
                    }
                    onPushToMaster={
                      (itemOverrides as any)?.date
                        ? () =>
                            pushOverrideToMaster(
                              `${sectionType}.date`,
                              date || '',
                              { index }
                            )
                        : undefined
                    }
                    isModified={!!(itemOverrides as any)?.date}
                    isReadOnly={isReadOnly}
                    showEditIcon={true}
                  />
                </p>
                {itemDescription && sectionType === 'awards' && (
                  <div className="text-sm text-gray-600 mt-1">
                    <EditableText
                      value={itemDescription}
                      onSave={(newValue) =>
                        setTextOverride(`${sectionType}.summary`, newValue, { index })
                      }
                      onRevert={
                        (itemOverrides as any)?.summary
                          ? () => removeTextOverride(`${sectionType}.summary`, { index })
                          : undefined
                      }
                      onPushToMaster={
                        (itemOverrides as any)?.summary
                          ? () =>
                              pushOverrideToMaster(
                                `${sectionType}.summary`,
                                (itemOverrides as any).summary.value,
                                { index }
                              )
                          : undefined
                      }
                      isModified={!!(itemOverrides as any)?.summary}
                      isReadOnly={isReadOnly}
                      multiline={true}
                      showEditIcon={true}
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {!isReadOnly && (
        <div className="px-6 py-4 border-t border-gray-200">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            <Plus className="w-4 h-4" />
            Add {sectionType === 'awards' ? 'Award' : 'Certification'}
          </button>
        </div>
      )}
    </div>
  );
}
