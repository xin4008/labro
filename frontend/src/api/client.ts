import type {
  Discipline,
  ExperimentDetail,
  ExperimentListItem,
  ExperimentStatus,
  ExperimentTemplate,
  UploadedDocument,
} from '@/types'

const API_BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {}
  const isFormData = options?.body instanceof FormData
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options?.headers as Record<string, string> | undefined),
    },
  })

  if (!response.ok) {
    let message = `请求失败 (${response.status})`
    try {
      const body = (await response.json()) as { detail?: string | { msg?: string }[] }
      if (typeof body.detail === 'string') {
        message = body.detail
      } else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        message = body.detail[0].msg
      }
    } catch {
      // ignore
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string; phase: string }>('/health'),

  listTemplates: (discipline?: Discipline) =>
    request<ExperimentTemplate[]>(
      discipline ? `/templates?discipline=${discipline}` : '/templates'
    ),

  listExperiments: () => request<ExperimentListItem[]>('/experiments'),

  getExperiment: (id: string) => request<ExperimentDetail>(`/experiments/${id}`),

  createExperiment: (data: {
    title: string
    discipline?: Discipline
    template_id?: number | null
  }) =>
    request<ExperimentDetail>('/experiments', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateExperiment: (
    id: string,
    data: Partial<{
      title: string
      status: ExperimentStatus
      template_id: number | null
      current_step_index: number
    }>
  ) =>
    request<ExperimentDetail>(`/experiments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteExperiment: (id: string) =>
    request<{ ok: boolean }>(`/experiments/${id}`, { method: 'DELETE' }),

  uploadDocument: (experimentId: string, file: File, isHandout: boolean) => {
    const form = new FormData()
    form.append('file', file)
    form.append('is_handout', String(isHandout))
    return request<UploadedDocument[]>(`/experiments/${experimentId}/documents/upload`, {
      method: 'POST',
      body: form,
    })
  },

  addDocumentUrl: (experimentId: string, url: string, isHandout: boolean) =>
    request<UploadedDocument[]>(`/experiments/${experimentId}/documents/url`, {
      method: 'POST',
      body: JSON.stringify({ url, is_handout: isHandout }),
    }),

  deleteDocument: (experimentId: string, documentId: number) =>
    request<{ ok: boolean }>(
      `/experiments/${experimentId}/documents/${documentId}`,
      { method: 'DELETE' }
    ),

  parseLiterature: (experimentId: string) =>
    request<ExperimentDetail>(`/experiments/${experimentId}/parse`, {
      method: 'POST',
    }),

  saveStepRecords: (
    experimentId: string,
    stepId: number,
    records: Array<{
      field_label: string
      field_type: 'text' | 'number' | 'image'
      unit?: string | null
      text_value?: string | null
      number_value?: number | null
    }>
  ) =>
    request<import('@/types').StepRecord[]>(
      `/experiments/${experimentId}/steps/${stepId}/records`,
      { method: 'PUT', body: JSON.stringify({ records }) }
    ),

  uploadStepImage: (experimentId: string, stepId: number, fieldLabel: string, file: File) => {
    const form = new FormData()
    form.append('field_label', fieldLabel)
    form.append('file', file)
    return request<import('@/types').StepRecord>(
      `/experiments/${experimentId}/steps/${stepId}/records/image`,
      { method: 'POST', body: form }
    )
  },

  completeStep: (experimentId: string, stepId: number) =>
    request<ExperimentDetail>(`/experiments/${experimentId}/steps/${stepId}/complete`, {
      method: 'POST',
    }),

  reopenStep: (experimentId: string, stepId: number) =>
    request<ExperimentDetail>(`/experiments/${experimentId}/steps/${stepId}/reopen`, {
      method: 'POST',
    }),

  setCurrentStep: (experimentId: string, stepIndex: number) =>
    request<ExperimentDetail>(`/experiments/${experimentId}/current-step`, {
      method: 'PUT',
      body: JSON.stringify({ step_index: stepIndex }),
    }),

  exportWord: async (experimentId: string, title: string) => {
    const response = await fetch(`${API_BASE}/experiments/${experimentId}/export-word`)
    if (!response.ok) {
      let message = `导出失败 (${response.status})`
      try {
        const body = (await response.json()) as { detail?: string }
        if (body.detail) message = body.detail
      } catch {
        // ignore
      }
      throw new Error(message)
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    const safeTitle = title.replace(/[<>:"/\\|?*]/g, '_').slice(0, 40) || '实验报告'
    a.href = url
    a.download = `${safeTitle}.docx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },
}
