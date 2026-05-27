import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'

import { api } from '@/api/client'
import { LiteratureImportPanel } from '@/components/literature/LiteratureImportPanel'
import type { AppOutletContext } from '@/components/layout/AppLayout'
import { StepWorkbench } from '@/components/steps/StepWorkbench'
import { DISCIPLINE_LABEL, MATERIALS_LABEL } from '@/constants/discipline'
import type { ExperimentDetail } from '@/types'

export function ExperimentPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { setPageContext } = useOutletContext<AppOutletContext>()
  const [experiment, setExperiment] = useState<ExperimentDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showImport, setShowImport] = useState(false)
  const [exporting, setExporting] = useState(false)

  const loadExperiment = useCallback(async (options?: { silent?: boolean }) => {
    if (!id) return
    if (!options?.silent) setLoading(true)
    try {
      const exp = await api.getExperiment(id)
      setExperiment(exp)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      if (!options?.silent) setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void loadExperiment()
  }, [loadExperiment])

  const handleExport = useCallback(async () => {
    if (!id || !experiment) return
    setExporting(true)
    try {
      await api.exportWord(id, experiment.title)
    } catch (err) {
      alert(err instanceof Error ? err.message : '导出失败')
    } finally {
      setExporting(false)
    }
  }, [id, experiment])

  useEffect(() => {
    setPageContext({
      title: experiment?.title,
      onExport: () => void handleExport(),
      exportDisabled: !experiment || experiment.steps.length === 0 || exporting,
      exportLabel: exporting ? '导出中…' : '导出 Word',
    })
    return () => setPageContext({})
  }, [experiment, exporting, handleExport, setPageContext])

  const handleDelete = async () => {
    if (!id || !experiment) return
    if (!confirm(`确定删除实验「${experiment.title}」？此操作不可恢复。`)) return
    await api.deleteExperiment(id)
    navigate('/')
  }

  if (loading) {
    return <p className="text-sm text-slate-500">加载实验详情…</p>
  }

  if (error || !experiment) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error ?? '实验不存在'}
      </div>
    )
  }

  const documents = experiment.documents ?? []
  const hasSteps = experiment.steps.length > 0

  return (
    <div className="space-y-5">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-brand-600">
              实验工作台
            </p>
            <h3 className="mt-1 text-lg font-semibold text-slate-900">
              {experiment.title}
              <span className="ml-2 rounded bg-brand-100 px-2 py-0.5 text-xs font-medium text-brand-700">
                {DISCIPLINE_LABEL[experiment.discipline]}
              </span>
            </h3>
          </div>
          <button
            type="button"
            onClick={() => void handleDelete()}
            className="text-sm text-red-600 hover:underline"
          >
            删除实验
          </button>
        </div>

        {experiment.purpose && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-slate-800">实验目的</h4>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">{experiment.purpose}</p>
          </div>
        )}

        {experiment.reagents_instruments && experiment.reagents_instruments.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-slate-800">
              {MATERIALS_LABEL[experiment.discipline]}
            </h4>
            <ul className="mt-1 list-inside list-disc text-sm text-slate-600">
              {experiment.reagents_instruments.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {experiment.global_safety_notes && experiment.global_safety_notes.length > 0 && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4">
            <h4 className="text-sm font-semibold text-red-800">安全注意事项</h4>
            <ul className="mt-2 space-y-1 text-sm text-red-700">
              {experiment.global_safety_notes.map((note, i) => (
                <li key={i}>⚠ {note}</li>
              ))}
            </ul>
          </div>
        )}

        <button
          type="button"
          onClick={() => setShowImport((v) => !v)}
          className="mt-4 text-sm text-brand-600 hover:underline"
        >
          {showImport ? '收起文献导入' : '文献导入 / 重新解析'}
        </button>
        {showImport && (
          <div className="mt-3">
            <LiteratureImportPanel
              experimentId={experiment.id}
              documents={documents}
              onUpdated={() => void loadExperiment()}
            />
          </div>
        )}
      </section>

      {hasSteps ? (
        <StepWorkbench
          experiment={experiment}
          onUpdated={() => void loadExperiment({ silent: true })}
        />
      ) : (
        <p className="text-sm text-slate-500">
          展开「文献导入」上传 PDF/DOCX 后，AI 解析即可开始逐步实验记录。
        </p>
      )}
    </div>
  )
}
