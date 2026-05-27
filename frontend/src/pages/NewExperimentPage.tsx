import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useOutletContext } from 'react-router-dom'

import { api } from '@/api/client'
import type { AppOutletContext } from '@/components/layout/AppLayout'
import { DISCIPLINE_LABEL } from '@/constants/discipline'
import type { Discipline, ExperimentTemplate } from '@/types'

export function NewExperimentPage() {
  const navigate = useNavigate()
  const { setPageContext } = useOutletContext<AppOutletContext>()
  const [title, setTitle] = useState('')
  const [discipline, setDiscipline] = useState<Discipline>('chemistry')
  const [templateId, setTemplateId] = useState<number | ''>('')
  const [templates, setTemplates] = useState<ExperimentTemplate[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setPageContext({ title: '新建实验' })
    return () => setPageContext({})
  }, [setPageContext])

  useEffect(() => {
    setTemplateId('')
    void api.listTemplates(discipline).then(setTemplates).catch(() => {
      setError('无法加载数据模板')
    })
  }, [discipline])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      setError('请填写实验标题')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const exp = await api.createExperiment({
        title: title.trim(),
        discipline,
        template_id: templateId === '' ? null : templateId,
      })
      navigate(`/experiments/${exp.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建失败')
    } finally {
      setSubmitting(false)
    }
  }

  const placeholders: Record<Discipline, string> = {
    chemistry: '例如：苯甲酸乙酯的合成',
    physics: '例如：单摆测重力加速度',
    biology: '例如：革兰氏染色与镜检',
  }

  return (
    <div className="mx-auto max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">新建实验项目</h3>

      <div className="mt-4 flex gap-2">
        {(['chemistry', 'physics', 'biology'] as const).map((d) => (
          <button
            key={d}
            type="button"
            onClick={() => setDiscipline(d)}
            className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition ${
              discipline === d
                ? 'border-brand-600 bg-brand-50 text-brand-700'
                : 'border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {DISCIPLINE_LABEL[d]}实验
          </button>
        ))}
      </div>

      <form className="mt-5 space-y-4" onSubmit={(e) => void handleSubmit(e)}>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="title">
            实验标题
          </label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={placeholders[discipline]}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none ring-brand-500 focus:ring-2"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="template">
            数据记录模板（{DISCIPLINE_LABEL[discipline]}）
          </label>
          <select
            id="template"
            value={templateId}
            onChange={(e) =>
              setTemplateId(e.target.value === '' ? '' : Number(e.target.value))
            }
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none ring-brand-500 focus:ring-2"
          >
            <option value="">稍后选择 / 由 AI 推荐</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-brand-600 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {submitting ? '创建中…' : '创建实验'}
        </button>
      </form>
    </div>
  )
}
