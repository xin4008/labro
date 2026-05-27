import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

export interface PageContextState {
  title?: string
  onExport?: () => void
  exportDisabled?: boolean
  exportLabel?: string
}

export interface AppOutletContext {
  setPageContext: (ctx: PageContextState) => void
}

export function AppLayout() {
  const [pageContext, setPageContext] = useState<PageContextState>({})

  return (
    <div className="flex h-full min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          title={pageContext.title}
          onExport={pageContext.onExport}
          exportDisabled={pageContext.exportDisabled}
          exportLabel={pageContext.exportLabel}
        />
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet context={{ setPageContext } satisfies AppOutletContext} />
        </main>
      </div>
    </div>
  )
}
