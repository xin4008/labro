import type { ExperimentStep } from '@/types'

interface Props {
  steps: ExperimentStep[]
}

function highlightUnclear(text: string) {
  const marker = '【文献未明确，建议咨询指导教师】'
  if (!text.includes(marker)) return text
  const parts = text.split(marker)
  return parts.flatMap((part, i) =>
    i < parts.length - 1
      ? [
          part,
          <mark
            key={`m-${i}`}
            className="rounded bg-amber-100 px-1 text-amber-900 not-italic"
          >
            {marker}
          </mark>,
        ]
      : [part]
  )
}

export function StepFlowList({ steps }: Props) {
  if (steps.length === 0) return null

  return (
    <ol className="space-y-4">
      {steps.map((step, index) => (
        <li
          key={step.id}
          className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="flex items-start gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
              {index + 1}
            </span>
            <div className="min-w-0 flex-1">
              <h4 className="text-base font-semibold text-slate-900">{step.title}</h4>
              <div className="mt-2 text-sm leading-relaxed text-slate-700">
                {highlightUnclear(step.instructions)}
              </div>
            </div>
          </div>

          {step.expected_phenomenon && (
            <div className="mt-4 rounded-lg bg-blue-50 px-4 py-3">
              <p className="text-xs font-medium text-brand-700">预期现象</p>
              <p className="mt-1 text-sm text-slate-800">{step.expected_phenomenon}</p>
              {step.phenomenon_source && (
                <p className="mt-1 text-xs text-slate-500">来源：{step.phenomenon_source}</p>
              )}
            </div>
          )}

          {step.safety_notes && (
            <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
              <p className="text-xs font-semibold text-red-800">安全注意</p>
              <p className="mt-1 text-sm font-medium text-red-700">{step.safety_notes}</p>
            </div>
          )}

          {step.field_schema && step.field_schema.length > 0 && (
            <div className="mt-3 border-t border-slate-100 pt-3">
              <p className="text-xs text-slate-500">
                数据记录字段（Phase 3 可录入）：
                {step.field_schema.map((f) => f.label).join('、')}
              </p>
            </div>
          )}
        </li>
      ))}
    </ol>
  )
}
