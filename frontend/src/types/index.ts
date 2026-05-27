export type ExperimentStatus = 'draft' | 'in_progress' | 'completed'

export interface TemplateField {
  label: string
  type: 'text' | 'number' | 'image'
  unit?: string
}

export interface ExperimentTemplate {
  id: number
  name: string
  fields: TemplateField[]
  created_at: string
}

export interface UploadedDocument {
  id: number
  filename: string
  doc_type: 'pdf' | 'docx' | 'url'
  is_handout: boolean
  source_url: string | null
  created_at: string
  has_text: boolean
}

export interface ExperimentListItem {
  id: string
  title: string
  status: ExperimentStatus
  template_id: number | null
  current_step_index: number
  created_at: string
  updated_at: string
  step_count: number
  completed_step_count: number
}

export interface StepRecord {
  id: number
  field_label: string
  field_type: string
  unit: string | null
  text_value: string | null
  number_value: number | null
  image_path: string | null
  updated_at: string
}

export interface ExperimentStep {
  id: number
  order_index: number
  title: string
  instructions: string
  expected_phenomenon: string | null
  phenomenon_source: string | null
  safety_notes: string | null
  field_schema: TemplateField[] | null
  is_completed: boolean
  completed_at: string | null
  records: StepRecord[]
}

export interface ExperimentDetail {
  id: string
  title: string
  status: ExperimentStatus
  template_id: number | null
  purpose: string | null
  reagents_instruments: string[] | null
  global_safety_notes: string[] | null
  parsed_metadata: Record<string, unknown> | null
  current_step_index: number
  created_at: string
  updated_at: string
  steps: ExperimentStep[]
  documents: UploadedDocument[]
}
