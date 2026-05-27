import { useState } from 'react'

import { api } from '@/api/client'
import type { ExperimentDetail, ExperimentStep } from '@/types'

import { StepFieldForm } from './StepFieldForm'

interface Props {
  experiment: ExperimentDetail
  onUpdated: () => void
}

function highlightUnclear(text: string) {
  const marker = '【文献未明确，建议咨询指导教师】'
  if (!text.includes(marker)) return text
  const parts = text.split(marker)
  return parts.flatMap((part, i) =>
    i < parts.length - 1
      ? [
          part,
          <mark key={i} className="rounded bg-amber-100 px-1 text-amber-900">
            {marker}
          </mark>,
        ]
      : [part]
  )
}

export function StepWorkbench({ experiment, onUpdated }: Props) {
  const steps = [...experiment.steps].sort((a, b) => a.order_index - b.order_index)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showOverview, setShowOverview] = useState(false)

  const currentIndex = Math.min(experiment.current_step_index, steps.length - 1)
  const currentStep = steps[currentIndex]

  const goToStep = async (index: number) => {
    setError(null)
    setBusy(true)
    try {
      await api.setCurrentStep(experiment.id, index)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '无法切换步骤')
    } finally {
      setBusy(false)
    }
  }

  const completeStep = async (step: ExperimentStep) => {
    setError(null)
    setBusy(true)
    try {
      await api.completeStep(experiment.id, step.id)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  const reopenStep = async (step: ExperimentStep) => {
    if (!confirm('重新打开此步骤以修改记录？')) return
    setBusy(true)
    try {
      await api.reopenStep(experiment.id, step.id)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  if (!currentStep) return null

  const progress = steps.filter((s) => s.is_completed).length

  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-4 py-3 md:px-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h4 className="text-sm font-semibold text-slate-800">实验进行</h4>
            <p className="text-xs text-slate-500">
              进度 {progress}/{steps.length}
              {experiment.status === 'completed' && ' · 已全部完成'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowOverview((v) => !v)}
            className="text-sm text-brand-600 hover:underline"
          >
            {showOverview ? '收起总览' : '查看全部步骤'}
          </button>
        </div>
        <div className="mt-2 flex gap-1">
          {steps.map((s, i) => {
            const locked =
              i > 0 && !steps[i - 1].is_completed && i > experiment.current_step_index
            return (
              <button
                key={s.id}
                type="button"
                disabled={busy || locked}
                title={locked ? '请先完成上一步' : s.title}
                onClick={() => void goToStep(i)}
                className={`h-2 flex-1 rounded-full transition ${
                  i === currentIndex
                    ? 'bg-brand-600'
                    : s.is_completed
                      ? 'bg-brand-300'
                      : locked
                        ? 'bg-slate-200'
                        : 'bg-slate-300 hover:bg-brand-200'
                }`}
              />
            )
          })}
        </div>
      </div>

      {showOverview && (
        <ul className="border-b border-slate-100 bg-slate-50 px-4 py-2 text-sm md:px-5">
          {steps.map((s, i) => (
            <li key={s.id} className="flex items-center justify-between py-1.5">
              <button
                type="button"
                className="text-left text-slate-700 hover:text-brand-600"
                onClick={() => void goToStep(i)}
              >
                {i + 1}. {s.title}
                {s.is_completed && (
                  <span className="ml-2 text-xs text-green-600">已完成</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="p-4 md:p-5">
        <div className="flex items-start gap-3">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
            {currentIndex + 1}
          </span>
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-semibold text-slate-900">{currentStep.title}</h3>
            <div className="mt-2 text-sm leading-relaxed text-slate-700">
              {highlightUnclear(currentStep.instructions)}
            </div>
          </div>
        </div>

        {currentStep.expected_phenomenon && (
          <div className="mt-4 rounded-lg bg-blue-50 px-4 py-3 text-sm">
            <span className="font-medium text-brand-700">预期现象：</span>
            {currentStep.expected_phenomenon}
            {currentStep.phenomenon_source && (
              <p className="mt-1 text-xs text-slate-500">
                来源：{currentStep.phenomenon_source}
              </p>
            )}
          </div>
        )}

        {currentStep.safety_notes && (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <span className="font-semibold">安全注意：</span>
            {currentStep.safety_notes}
          </div>
        )}

        <StepFieldForm
          experimentId={experiment.id}
          step={currentStep}
          onImageUploaded={onUpdated}
        />

        <div className="mt-6 flex flex-wrap gap-2">
          {currentIndex > 0 && (
            <button
              type="button"
              disabled={busy}
              onClick={() => void goToStep(currentIndex - 1)}
              className="rounded-lg border border-slate-300 px-4 py-2 text-sm hover:bg-slate-50 disabled:opacity-50"
            >
              上一步
            </button>
          )}
          {!currentStep.is_completed ? (
            <button
              type="button"
              disabled={busy}
              onClick={() => void completeStep(currentStep)}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              完成本步
            </button>
          ) : (
            <>
              <span className="flex items-center text-sm text-green-600">本步已完成</span>
              <button
                type="button"
                disabled={busy}
                onClick={() => void reopenStep(currentStep)}
                className="text-sm text-slate-500 hover:underline"
              >
                修改记录
              </button>
              {currentIndex < steps.length - 1 && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => void goToStep(currentIndex + 1)}
                  className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
                >
                  下一步
                </button>
              )}
            </>
          )}
        </div>

        {error && (
          <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}
      </div>
    </section>
  )
}
