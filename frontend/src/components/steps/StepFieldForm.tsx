import { useEffect, useMemo, useRef, useState } from 'react'

import { api } from '@/api/client'
import { useDebouncedValue } from '@/hooks/useDebounce'
import { useSpeechInput } from '@/hooks/useSpeechInput'
import type { ExperimentStep, StepRecord, TemplateField } from '@/types'

interface Props {
  experimentId: string
  step: ExperimentStep
  /** 仅图片上传后需要刷新图片 URL 时调用（静默刷新） */
  onImageUploaded?: () => void
}

function recordMap(records: StepRecord[]): Record<string, StepRecord> {
  const m: Record<string, StepRecord> = {}
  for (const r of records) m[r.field_label] = r
  return m
}

function valuesFromStep(fields: TemplateField[], existing: Record<string, StepRecord>) {
  const init: Record<string, string> = {}
  for (const f of fields) {
    const r = existing[f.label]
    if (f.type === 'number') init[f.label] = r?.number_value != null ? String(r.number_value) : ''
    else if (f.type === 'text') init[f.label] = r?.text_value ?? ''
  }
  return init
}

export function StepFieldForm({ experimentId, step, onImageUploaded }: Props) {
  const fields = useMemo<TemplateField[]>(
    () => step.field_schema ?? [{ label: '现象描述', type: 'text' }],
    [step.field_schema]
  )
  const existing = useMemo(() => recordMap(step.records), [step.records])

  const [values, setValues] = useState(() => valuesFromStep(fields, existing))
  const lastSavedJson = useRef(JSON.stringify(values))
  const stepIdRef = useRef(step.id)

  // 仅切换步骤时重置表单，不因自动保存回写 records 而重置（避免闪烁循环）
  useEffect(() => {
    if (stepIdRef.current !== step.id) {
      stepIdRef.current = step.id
      const next = valuesFromStep(fields, existing)
      setValues(next)
      lastSavedJson.current = JSON.stringify(next)
    }
  }, [step.id, fields, existing])

  const [saving, setSaving] = useState(false)
  const [saveHint, setSaveHint] = useState<string | null>(null)
  const debouncedValues = useDebouncedValue(values, 600)

  useEffect(() => {
    const textNumberFields = fields.filter((f) => f.type === 'text' || f.type === 'number')
    if (textNumberFields.length === 0) return

    const serialized = JSON.stringify(debouncedValues)
    if (serialized === lastSavedJson.current) return

    const payload = textNumberFields.map((f) => {
      const raw = debouncedValues[f.label] ?? ''
      if (f.type === 'number') {
        return {
          field_label: f.label,
          field_type: 'number' as const,
          unit: f.unit ?? null,
          number_value: raw === '' ? null : Number(raw),
          text_value: null,
        }
      }
      return {
        field_label: f.label,
        field_type: 'text' as const,
        unit: f.unit ?? null,
        text_value: raw,
        number_value: null,
      }
    })

    let cancelled = false
    setSaving(true)
    void api
      .saveStepRecords(experimentId, step.id, payload)
      .then(() => {
        if (!cancelled) {
          lastSavedJson.current = serialized
          setSaveHint('已自动保存')
          window.setTimeout(() => setSaveHint(null), 2000)
        }
      })
      .catch(() => {
        if (!cancelled) setSaveHint('保存失败')
      })
      .finally(() => {
        if (!cancelled) setSaving(false)
      })

    return () => {
      cancelled = true
    }
  }, [debouncedValues, experimentId, step.id, fields])

  const appendVoiceText = (label: string, spoken: string) => {
    setValues((prev) => ({
      ...prev,
      [label]: prev[label] ? `${prev[label]} ${spoken}` : spoken,
    }))
  }

  const handleImage = async (label: string, file: File | null) => {
    if (!file) return
    setSaving(true)
    try {
      await api.uploadStepImage(experimentId, step.id, label, file)
      setSaveHint('图片已保存')
      onImageUploaded?.()
    } catch {
      setSaveHint('图片上传失败')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mt-4 space-y-4 border-t border-slate-100 pt-4">
      <div className="flex items-center justify-between">
        <h5 className="text-sm font-medium text-slate-800">实验数据记录</h5>
        <span className="text-xs text-slate-400">
          {saving ? '保存中…' : saveHint ?? '修改后自动保存'}
        </span>
      </div>

      {fields.map((field) => (
        <FieldRow
          key={field.label}
          field={field}
          value={values[field.label] ?? ''}
          imagePath={existing[field.label]?.image_path}
          onChange={(v) => setValues((prev) => ({ ...prev, [field.label]: v }))}
          onImage={(f) => void handleImage(field.label, f)}
          onVoice={(t) => appendVoiceText(field.label, t)}
        />
      ))}
    </div>
  )
}

function FieldRow({
  field,
  value,
  imagePath,
  onChange,
  onImage,
  onVoice,
}: {
  field: TemplateField
  value: string
  imagePath?: string | null
  onChange: (v: string) => void
  onImage: (f: File | null) => void
  onVoice: (t: string) => void
}) {
  const speech = useSpeechInput(onVoice)

  if (field.type === 'image') {
    return (
      <div>
        <label className="mb-1 block text-sm text-slate-700">{field.label}</label>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          className="block w-full text-sm"
          onChange={(e) => onImage(e.target.files?.[0] ?? null)}
        />
        {imagePath && (
          <img
            src={imagePath}
            alt={field.label}
            className="mt-2 max-h-48 rounded-lg border border-slate-200 object-contain"
          />
        )}
      </div>
    )
  }

  return (
    <div>
      <label className="mb-1 flex items-center gap-2 text-sm text-slate-700">
        {field.label}
        {field.unit && (
          <span className="text-xs text-slate-400">({field.unit})</span>
        )}
      </label>
      <div className="flex gap-2">
        {field.type === 'number' ? (
          <input
            type="number"
            step="any"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-500"
          />
        ) : (
          <textarea
            value={value}
            rows={2}
            onChange={(e) => onChange(e.target.value)}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-500"
          />
        )}
        {field.type === 'text' && speech.supported && (
          <button
            type="button"
            title="语音输入"
            onClick={() => (speech.listening ? speech.stop() : speech.start())}
            className={`shrink-0 rounded-lg border px-3 py-2 text-sm ${
              speech.listening
                ? 'border-red-300 bg-red-50 text-red-700'
                : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50'
            }`}
          >
            {speech.listening ? '停止' : '🎤'}
          </button>
        )}
      </div>
    </div>
  )
}
