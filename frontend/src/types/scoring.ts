import type { GradeInfo } from './character'

/** Score data from /api/score/character */
export interface ScoreData {
  total_score: number
  grade?: string
  phantoms?: PhantomScore[]
  substat_scores?: SubstatScoreBatch[]
  sub_weights?: Record<string, number>
  main_weights?: Record<string, number>
}

export interface PhantomScore {
  score: number
  grade: string
}

/** Per-substat score (one prop within a phantom) */
export interface SubstatScore {
  name_color: string
  num_color: string
  score: number
}

/** Batch substat scores indexed by phantom index then prop index */
export type SubstatScoreBatch = SubstatScore[]

/** Echo grade stored on window._echoGrades */
export interface EchoGradeData {
  grade: string
  score: number
  substat_scores: SubstatScore[]
}
