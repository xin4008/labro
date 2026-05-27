export type Discipline = 'chemistry' | 'physics' | 'biology'

export const DISCIPLINE_LABEL: Record<Discipline, string> = {
  chemistry: '化学',
  physics: '物理',
  biology: '生物',
}

export const MATERIALS_LABEL: Record<Discipline, string> = {
  chemistry: '试剂与仪器',
  physics: '器材与材料',
  biology: '材料、试剂与仪器',
}
