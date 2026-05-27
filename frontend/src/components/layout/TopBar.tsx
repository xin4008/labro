interface TopBarProps {
  title?: string
  onExport?: () => void
  exportDisabled?: boolean
  exportLabel?: string
}

export function TopBar({ title, onExport, exportDisabled, exportLabel }: TopBarProps) {
  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white/90 px-4 py-3 backdrop-blur md:px-6">
      <div className="min-w-0 flex-1">
        <h2 className="truncate text-lg font-semibold text-slate-900">
          {title ?? '欢迎使用化学实验助手'}
        </h2>
        <p className="text-xs text-slate-500 md:text-sm">
          {title
            ? '按步骤完成实验并记录数据'
            : '从左侧选择实验，或创建新的实验项目'}
        </p>
      </div>
      {onExport && (
        <button
          type="button"
          disabled={exportDisabled}
          onClick={onExport}
          className="ml-3 shrink-0 rounded-lg border border-brand-600 px-3 py-2 text-sm font-medium text-brand-700 transition hover:bg-brand-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {exportLabel ?? '导出 Word'}
        </button>
      )}
    </header>
  )
}
