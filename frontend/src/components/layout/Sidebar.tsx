import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { api } from '@/api/client'
import type { ExperimentListItem } from '@/types'

const statusLabel: Record<string, string> = {
  draft: '草稿',
  in_progress: '进行中',
  completed: '已完成',
}

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [experiments, setExperiments] = useState<ExperimentListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setExperiments(await api.listExperiments())
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [location.pathname])

  const handleNew = () => navigate('/experiments/new')

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:w-72">
      <div className="border-b border-slate-200 px-4 py-5">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            Cl
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900">化学实验助手</h1>
            <p className="text-xs text-slate-500">Lab Assistant MVP</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleNew}
          className="mt-4 w-full rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
        >
          + 新建实验
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-3">
        <p className="px-2 pb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
          实验项目
        </p>
        {loading && <p className="px-3 py-2 text-sm text-slate-500">加载中…</p>}
        {error && (
          <div className="mx-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
            <button type="button" className="ml-2 underline" onClick={() => void load()}>
              重试
            </button>
          </div>
        )}
        {!loading && !error && experiments.length === 0 && (
          <p className="px-3 py-2 text-sm text-slate-500">暂无实验，点击上方创建</p>
        )}
        <ul className="space-y-1">
          {experiments.map((exp) => {
            const active = location.pathname === `/experiments/${exp.id}`
            return (
              <li key={exp.id}>
                <Link
                  to={`/experiments/${exp.id}`}
                  className={`block rounded-lg px-3 py-2 transition ${
                    active
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <p className="truncate text-sm font-medium">{exp.title}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {statusLabel[exp.status] ?? exp.status}
                    {exp.step_count > 0 && ` · ${exp.completed_step_count}/${exp.step_count} 步`}
                  </p>
                </Link>
              </li>
            )
          })}
        </ul>
      </div>
    </aside>
  )
}
